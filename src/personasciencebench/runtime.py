"""Networkless Bubblewrap execution for independently controlled actor commands.

There is no host-execution fallback. Mount only a reviewed actor workspace, a
dedicated virtual environment, trusted Python runtime files, and system tools.
The controller owns model calls, secrets, trace files, and evaluation references.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import selectors
import shlex
import shutil
import signal
import subprocess
import sys
import time


OUTPUT_LIMIT_BYTES = 65536
COMMAND_LIMIT_CHARS = 64000


class Sandbox:
    def __init__(self, workspace: Path, python_root: Path):
        self.workspace = Path(workspace).resolve()
        self.python_root = Path(python_root).resolve()
        self.base_prefix = Path(sys.base_prefix).resolve()
        configured_bwrap = os.environ.get("PERSONASCIENCEBENCH_BWRAP")
        self.bwrap = (shutil.which(configured_bwrap) if configured_bwrap
                      else shutil.which("bwrap", path="/usr/bin:/bin"))
        if not self.bwrap:
            raise ValueError("Bubblewrap is required; host execution is disabled")
        if not self.workspace.is_dir() or not self.python_root.is_dir():
            raise ValueError("Actor workspace and dedicated Python environment must exist")
        if (self.workspace == Path("/") or self.workspace == Path.home().resolve()
                or self.python_root.is_relative_to(self.workspace)
                or self.workspace.is_relative_to(self.python_root)):
            raise ValueError("Workspace and Python runtime must be separate dedicated directories")
        config = self.python_root / "pyvenv.cfg"
        if not config.is_file():
            raise ValueError("python_root must be a dedicated virtual environment")
        values = {}
        for line in config.read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key.strip().lower()] = value.strip()
        if values.get("include-system-site-packages", "").lower() != "false":
            raise ValueError("Actor environment must not include system site-packages")
        python = self.python_root / "bin/python"
        if not python.is_file():
            raise ValueError("Dedicated environment has no Python executable")
        self.interpreter = python.resolve()
        # The controller's interpreter is trusted software, unlike actor files.
        # Do not discover arbitrary runtime roots by executing actor-controlled
        # code or mounting whichever path a pyvenv.cfg happens to name.
        if not self.interpreter.is_relative_to(self.base_prefix / "bin"):
            raise ValueError("Actor venv must use the controller's trusted base Python")
        self.python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        self.stdlib = self.base_prefix / "lib" / self.python_version
        if not self.stdlib.is_dir():
            raise ValueError("Trusted Python standard library is unavailable")

    def _argv(self, command: str) -> list[str]:
        args = [self.bwrap, "--unshare-all", "--unshare-user", "--unshare-net", "--die-with-parent",
                "--new-session", "--clearenv", "--disable-userns", "--cap-drop", "ALL"]
        for directory in ("/usr", "/bin", "/lib", "/lib64"):
            if Path(directory).exists():
                args.extend(("--ro-bind", directory, directory))
        cache = Path("/etc/ld.so.cache")
        if cache.is_file():
            args.extend(("--ro-bind", str(cache), str(cache)))
        # Create isolated temporary storage before mounting runtime files. A
        # developer's venv may itself live under /tmp; mounting tmpfs afterward
        # would hide that read-only venv and make Python disappear.
        args.extend(("--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"))
        # A virtual environment may contain absolute interpreter symlinks. Keep
        # its exact path, but expose only the base interpreter aliases, stdlib,
        # and direct shared libraries, never the user's home or conda prefix.
        args.extend(("--ro-bind", str(self.python_root), str(self.python_root)))
        aliases = {self.interpreter, self.base_prefix / "bin/python",
                   self.base_prefix / "bin/python3", self.base_prefix / "bin" / self.python_version}
        for alias in sorted(aliases):
            if alias.is_file() and alias.resolve() == self.interpreter:
                args.extend(("--ro-bind", str(self.interpreter), str(alias)))
        args.extend(("--ro-bind", str(self.stdlib), str(self.stdlib)))
        # Hide unrelated base Python packages and editable installation pointers.
        # Actor dependencies must come from the dedicated environment instead.
        for packages in (self.stdlib / "site-packages", self.stdlib / "dist-packages",
                         self.base_prefix / "lib/python3/dist-packages"):
            if packages.is_dir():
                args.extend(("--tmpfs", str(packages)))
        base_lib = self.base_prefix / "lib"
        for library in sorted(base_lib.glob("*.so*")):
            if library.is_file():
                resolved = library.resolve()
                if not any(resolved.is_relative_to(root) for root in
                           (base_lib.resolve(), Path("/usr/lib"), Path("/lib"), Path("/lib64"))):
                    raise ValueError("A base Python library resolves outside trusted runtime directories")
                args.extend(("--ro-bind", str(resolved), str(library)))
        standard_zip = base_lib / f"python{sys.version_info.major}{sys.version_info.minor}.zip"
        if standard_zip.is_file():
            args.extend(("--ro-bind", str(standard_zip), str(standard_zip)))
        args.extend(("--dir", "/home/actor", "--bind", str(self.workspace), "/workspace",
                     "--chdir", "/workspace"))
        environment = {
            "HOME": "/home/actor", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "PATH": f"{self.python_root}/bin:/usr/bin:/bin",
            "LD_LIBRARY_PATH": str(base_lib), "VIRTUAL_ENV": str(self.python_root),
            "PYTHONNOUSERSITE": "1", "PYTHONUNBUFFERED": "1",
            "XDG_CACHE_HOME": "/tmp/cache", "MPLBACKEND": "Agg",
        }
        for key, value in environment.items():
            args.extend(("--setenv", key, value))
        return args + ["/bin/bash", "--noprofile", "--norc", "-c", command]

    @staticmethod
    def _kill_group(process: subprocess.Popen):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def execute(self, command: str, timeout_seconds: int = 120) -> dict:
        if not isinstance(command, str) or not command.strip() or len(command) > COMMAND_LIMIT_CHARS:
            raise ValueError(f"Actor command must contain 1–{COMMAND_LIMIT_CHARS} characters")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds < 1:
            raise ValueError("Command timeout must be a positive integer number of seconds")
        started = time.monotonic()
        deadline = started + timeout_seconds
        captured = {"stdout": bytearray(), "stderr": bytearray()}
        sizes = {"stdout": 0, "stderr": 0}
        timed_out = False
        # Neither shell expansion nor actor-controlled environment variables are
        # evaluated by the controller. Shell interpretation occurs only inside
        # Bubblewrap after namespace and mount setup succeeds.
        process = subprocess.Popen(
            self._argv(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True, close_fds=True,
            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        )
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, "stdout")
                selector.register(process.stderr, selectors.EVENT_READ, "stderr")
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        timed_out = True
                        self._kill_group(process)
                        break
                    for key, _ in selector.select(min(remaining, 0.1)):
                        data = os.read(key.fileobj.fileno(), 65536)
                        if not data:
                            selector.unregister(key.fileobj)
                            continue
                        stream = key.data
                        sizes[stream] += len(data)
                        # Drain and discard excess output rather than buffering
                        # unbounded data in RAM or controller temporary files.
                        room = OUTPUT_LIMIT_BYTES - len(captured[stream])
                        if room > 0:
                            captured[stream].extend(data[:room])
            remaining = max(0.0, deadline - time.monotonic())
            try:
                process.wait(timeout=remaining if not timed_out else 5)
            except subprocess.TimeoutExpired:
                timed_out = True
                self._kill_group(process)
                process.wait(timeout=5)
        finally:
            if process.poll() is None:
                self._kill_group(process)
                process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
        return {
            "exit_code": process.returncode,
            "stdout": captured["stdout"].decode("utf-8", errors="replace"),
            "stderr": captured["stderr"].decode("utf-8", errors="replace"),
            "timeout": timed_out,
            "duration": round(time.monotonic() - started, 3),
            "stdout_truncated": sizes["stdout"] > OUTPUT_LIMIT_BYTES,
            "stderr_truncated": sizes["stderr"] > OUTPUT_LIMIT_BYTES,
            "stdout_bytes": sizes["stdout"], "stderr_bytes": sizes["stderr"],
        }

    def check(self) -> dict:
        """Run a harmless namespace/environment probe; never a scientific task."""
        namespace = os.readlink("/proc/self/ns/net")
        private_ssh = str(Path.home().resolve() / ".ssh")
        private_codex = str(Path.home().resolve() / ".codex")
        script = (
            "import json, os, pathlib, sys; "
            "assert os.getcwd() == '/workspace'; "
            "assert os.environ.get('HOME') == '/home/actor'; "
            "assert 'OPENROUTER_API_KEY' not in os.environ; "
            "assert 'GITHUB_TOKEN' not in os.environ; "
            f"assert os.readlink('/proc/self/ns/net') != {namespace!r}; "
            f"assert not pathlib.Path({private_ssh!r}).exists(); "
            f"assert not pathlib.Path({private_codex!r}).exists(); "
            "print(json.dumps({'isolation_ok': True, 'python': sys.version.split()[0], "
            "'workspace': os.getcwd(), 'network': 'separate namespace', "
            "'scientific_execution': False}))"
        )
        result = self.execute("python -I -c " + shlex.quote(script), timeout_seconds=20)
        if result["exit_code"] != 0 or '"isolation_ok": true' not in result["stdout"]:
            raise RuntimeError("Isolated runtime check failed: " + result["stderr"][-2000:])
        return {**result, "isolation_ok": True, "runtime": "bubblewrap",
                "scientific_execution": False}
