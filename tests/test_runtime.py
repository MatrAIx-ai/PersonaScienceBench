"""Runtime construction and process handling checks, without actor/model runs."""

import json
import os
from pathlib import Path
import signal
import sys

import pytest

from personasciencebench.runtime import OUTPUT_LIMIT_BYTES, Sandbox


@pytest.fixture
def sandbox(tmp_path):
    workspace = tmp_path / "actor"
    workspace.mkdir()
    venv = tmp_path / "runtime"
    (venv / "bin").mkdir(parents=True)
    (venv / "bin/python").symlink_to(Path(sys.executable).resolve())
    (venv / "pyvenv.cfg").write_text("include-system-site-packages = false\n")
    return Sandbox(workspace, venv)


def test_mounts_never_expose_parent_home_controller_or_credentials(sandbox, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "DO_NOT_MOUNT_OR_PASS_THIS")
    argv = sandbox._argv("printf synthetic")
    mounts = [(argv[i + 1], argv[i + 2]) for i, value in enumerate(argv)
              if value in {"--bind", "--ro-bind"}]
    assert (str(sandbox.workspace), "/workspace") in mounts
    assert (str(sandbox.python_root), str(sandbox.python_root)) in mounts
    sources = {source for source, target in mounts}
    for forbidden in ("/", "/home", str(Path.home()), str(sandbox.base_prefix),
                      str(sandbox.workspace.parent)):
        assert forbidden not in sources
    assert "/etc" not in sources
    assert "--clearenv" in argv and "--unshare-all" in argv and "--unshare-net" in argv
    assert "--unshare-user" in argv
    assert "--share-net" not in argv
    assert "DO_NOT_MOUNT_OR_PASS_THIS" not in json.dumps(argv)
    assert "--disable-userns" in argv
    assert argv[-5:] == ["/bin/bash", "--noprofile", "--norc", "-c", "printf synthetic"]


def test_runtime_rejects_system_packages_and_workspace_overlap(sandbox):
    with pytest.raises(ValueError, match="separate"):
        Sandbox(sandbox.python_root, sandbox.python_root)
    (sandbox.python_root / "pyvenv.cfg").write_text("include-system-site-packages = true\n")
    with pytest.raises(ValueError, match="system site-packages"):
        Sandbox(sandbox.workspace, sandbox.python_root)


def test_output_is_drained_with_bounded_memory_and_separate_streams(sandbox, monkeypatch):
    # Execute only this fixed infrastructure fixture on the host. The production
    # path has no fallback and always invokes Bubblewrap.
    program = "import sys; print('x'*200000); sys.stderr.write('diagnostic\\n')"
    monkeypatch.setattr(sandbox, "_argv", lambda command: [sys.executable, "-I", "-c", program])
    result = sandbox.execute("synthetic infrastructure fixture", timeout_seconds=5)
    assert result["exit_code"] == 0 and result["timeout"] is False
    assert len(result["stdout"].encode()) == OUTPUT_LIMIT_BYTES
    assert result["stdout_truncated"] is True and result["stdout_bytes"] == 200001
    assert result["stderr"] == "diagnostic\n" and result["stderr_truncated"] is False


def test_timeout_kills_process_group_and_reaps_process(sandbox, monkeypatch):
    program = "import time; print('started', flush=True); time.sleep(30)"
    monkeypatch.setattr(sandbox, "_argv", lambda command: [sys.executable, "-I", "-c", program])
    original = os.killpg
    signals = []
    def killpg(pid, sig):
        signals.append((pid, sig))
        return original(pid, sig)
    monkeypatch.setattr(os, "killpg", killpg)
    result = sandbox.execute("synthetic timeout fixture", timeout_seconds=1)
    assert result["timeout"] is True and result["exit_code"] == -signal.SIGKILL
    assert result["duration"] < 5
    assert result["stdout"] == "started\n"
    assert signals and signals[0][1] == signal.SIGKILL


def test_invalid_commands_and_timeouts_do_not_spawn_processes(sandbox, monkeypatch):
    monkeypatch.setattr(sandbox, "_argv", lambda command: pytest.fail("Must not construct a process"))
    for command, timeout in [("", 1), ("synthetic", 0), ("synthetic", True), ("x" * 64001, 1)]:
        with pytest.raises(ValueError):
            sandbox.execute(command, timeout)


def test_temporary_runtime_mount_survives_isolated_tmpfs(sandbox):
    argv = sandbox._argv("python -V")
    tmpfs = next(i for i, arg in enumerate(argv) if arg == "--tmpfs" and argv[i + 1] == "/tmp")
    runtime = next(i for i, arg in enumerate(argv) if arg == "--ro-bind" and argv[i + 1] == str(sandbox.python_root))
    assert tmpfs < runtime
