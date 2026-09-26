"""Public repository staging and Bubblewrap execution with no host fallback."""

import json
import os
import signal
import shutil
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath

from expbench.artifacts import append_jsonl, write_json
from expbench.runner import file_digest

CODE_SUFFIXES = {".py", ".sh", ".toml", ".yaml", ".yml", ".json", ".cfg",
                 ".ini", ".c", ".cpp", ".cu", ".h", ".hpp"}


def stage_repository(source, destination, masked_paths):
    """Copy public code/config only; omit history, documents, data and results.

    This stricter staging is a documented adaptation, not the paper's masking.
    Missing target masks are fatal so repository drift cannot silently leak a solution.
    """
    source, destination = Path(source).resolve(), Path(destination)
    if destination.exists():
        raise ValueError("Repository destination already exists")
    masks = []
    for raw in masked_paths:
        relative = PurePosixPath(raw.removeprefix("/workspace/"))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid mask path: {raw}")
        if not (source / str(relative)).is_file():
            raise ValueError(f"Mask target missing in source: {relative}")
        masks.append(str(relative))
    destination.mkdir(parents=True)
    copied = {}
    skip_dirs = {"node_modules", "__pycache__", "results", "outputs", "checkpoints", "wandb"}
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if (path.is_symlink() or not path.is_file() or str(rel) in masks
                or any(p.startswith(".") or p.lower() in skip_dirs for p in rel.parts)):
            continue
        if path.name.lower().startswith("readme"):
            continue
        if path.suffix.lower() not in CODE_SUFFIXES and not (
                path.name.lower().startswith(("license", "requirements")) or path.name == "Makefile"):
            continue
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        target.chmod(0o755 if os.access(path, os.X_OK) else 0o644)
        copied[str(rel)] = file_digest(target)
    if not copied:
        raise ValueError("No public code was staged")
    return {"source": str(source), "masked_paths": masks, "files_sha256": copied,
            "staging_policy": "code-and-config-only-v1; no symlinks, hidden paths, README or results directories"}


def verify_staged(source):
    if not source.get("staging_manifest"):
        raise ValueError("Live runs require a staging manifest; prepare the repository first")
    manifest = json.loads(Path(source["staging_manifest"]).read_text())
    root = Path(source["repository"])
    files = list(root.rglob("*"))
    if any(p.is_symlink() for p in files):
        raise ValueError("Staged repository contains an unapproved symlink")
    actual = {str(p.relative_to(root)): file_digest(p) for p in files if p.is_file()}
    if actual != manifest["files_sha256"]:
        raise ValueError("Staged repository differs from its manifest")
    return file_digest(Path(source["staging_manifest"]))


class Sandbox:
    """Execution sees system libraries, the task workspace and explicit assets only."""

    def __init__(self, workspace, log_path, *, environment=None, datasets=None, gpu=False):
        self.workspace = Path(workspace).resolve()
        self.log_path = Path(log_path)
        self.environment = Path(environment).resolve() if environment else None
        self.datasets = {k: Path(v).resolve() for k, v in (datasets or {}).items()}
        self.gpu = gpu
        self.calls = 0
        self.bwrap = shutil.which(os.environ.get("PERSONASCIENCEBENCH_BWRAP", "bwrap"))
        if not self.bwrap:
            raise ValueError("Bubblewrap is required; host execution is disabled")
        if not self.workspace.is_dir():
            raise ValueError("Task workspace is missing")
        for name, path in self.datasets.items():
            if not name.replace("_", "").replace("-", "").isalnum() or not path.is_dir():
                raise ValueError("Datasets must have simple names and existing directory paths")
        if self.environment and not self.environment.is_dir():
            raise ValueError("Task software environment is missing")
        if gpu and not os.environ.get("CUDA_VISIBLE_DEVICES"):
            raise ValueError("GPU execution requires an allocation with CUDA_VISIBLE_DEVICES set")

    def command(self, shell_command):
        command = [self.bwrap, "--unshare-all", "--die-with-parent", "--new-session", "--clearenv"]
        for directory in ("/usr", "/bin", "/lib", "/lib64"):
            if Path(directory).exists():
                command += ["--ro-bind", directory, directory]
        if Path("/etc/ld.so.cache").exists():
            command += ["--ro-bind", "/etc/ld.so.cache", "/etc/ld.so.cache"]
        command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                    "--dir", "/home/actor", "--bind", str(self.workspace), "/workspace",
                    "--setenv", "HOME", "/home/actor", "--setenv", "LANG", "C.UTF-8",
                    "--setenv", "PATH", "/usr/bin:/bin", "--chdir", "/workspace"]
        if self.environment:
            command += ["--ro-bind", str(self.environment), "/opt/task-env",
                        "--setenv", "PATH", "/opt/task-env/bin:/usr/bin:/bin"]
        for name, path in self.datasets.items():
            command += ["--ro-bind", str(path), "/datasets/" + name]
        if self.gpu:
            for device in sorted(Path("/dev").glob("nvidia*")):
                command += ["--dev-bind", str(device), str(device)]
            command += ["--setenv", "CUDA_VISIBLE_DEVICES", os.environ["CUDA_VISIBLE_DEVICES"]]
        return command + ["/bin/bash", "-c", shell_command]

    def execute(self, shell_command, *, seconds=60, phase="exploration"):
        if not shell_command.strip() or len(shell_command) > 12000:
            raise ValueError("Command must contain 1–12000 characters")
        start = time.monotonic()
        timed_out = False
        with tempfile.TemporaryFile() as stdout:
            process = subprocess.Popen(self.command(shell_command), stdout=stdout,
                                       stderr=subprocess.STDOUT, start_new_session=True,
                                       env={"PATH": "/usr/bin:/bin"})
            try:
                process.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            size = stdout.tell()
            stdout.seek(max(0, size - 24000))
            text = stdout.read().decode(errors="replace")
        self.calls += 1
        result = {"phase": phase, "command": shell_command, "exit_code": process.returncode,
                  "timed_out": timed_out, "elapsed_seconds": round(time.monotonic() - start, 3),
                  "output": text, "output_truncated": size > 24000}
        append_jsonl(self.log_path, result)
        return result

    def preflight(self):
        result = self.execute("python3 -I -c 'print(\"EXPBENCH_SANDBOX_OK\")'", seconds=10,
                              phase="preflight")
        if result["exit_code"] or "EXPBENCH_SANDBOX_OK" not in result["output"]:
            raise ValueError("Isolated runtime preflight failed; inspect execution log")
        description = self.description()
        if self.gpu:
            probe = self.execute("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader",
                                 seconds=10, phase="gpu_preflight")
            if probe["exit_code"] or not probe["output"].strip():
                raise ValueError("GPU visibility check failed inside the isolated runtime")
            description["gpu_inventory"] = probe["output"].strip()
            description["cuda_visible_devices"] = os.environ["CUDA_VISIBLE_DEVICES"]
        return description

    def description(self):
        return {"runtime": "bubblewrap", "network": "disabled",
                "repository": "/workspace", "python": "python3",
                "software_environment": "/opt/task-env" if self.environment else "system Python; project dependencies not preinstalled",
                "datasets": ["/datasets/" + k for k in self.datasets],
                "gpu_enabled": self.gpu,
                "cpu_affinity_count": len(os.sched_getaffinity(0)),
                "note": "Successful exploratory commands are not proof of a completed experiment."}

    def validate_reproduction(self, command, output_dir, seconds=2400):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=False)
        with tempfile.TemporaryDirectory(prefix="expbench-validation-") as temporary:
            workspace = Path(temporary) / "workspace"
            shutil.copytree(self.workspace, workspace, symlinks=True)
            runtime = Sandbox(workspace, output_dir / "execution.jsonl", environment=self.environment,
                              datasets=self.datasets, gpu=self.gpu)
            result = runtime.execute(command, seconds=seconds, phase="reproduction")
        verdict = {"command_exit_success": result["exit_code"] == 0,
                   "scientific_success": None,
                   "scope": "Replay command in a fresh sandbox with a copy of final workspace; no scientific validation implied",
                   **result}
        write_json(output_dir / "result.json", verdict)
        return verdict
