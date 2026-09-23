import json
import socket
from pathlib import Path

import pytest

import importlib.util
try:
    sdk_available = importlib.util.find_spec("openhands.sdk") is not None
except ModuleNotFoundError:
    sdk_available = False
if not sdk_available:
    pytest.skip("EXP-Bench integration tests require the actor extra", allow_module_level=True)
from expbench.paths import ROOT as EXP_ROOT
if not (EXP_ROOT / "data/realistic_pilot/tasks.jsonl").exists():
    pytest.skip("Prepare the pinned EXP-Bench task cards before running its source tests", allow_module_level=True)

from expbench.budget import Budget, Ledger
from expbench.exploration import Sandbox, stage_repository
from expbench.gateway import Gateway, ModelError
from expbench.judge_protocol import query_original
from expbench.original_control import OriginalGrade
from expbench.realistic import RealisticEpisode, run_episode, summarize, main
from expbench.realistic_mock import RealisticMock
from expbench.schema import Config, load_tasks
from expbench.scoped_researcher import ScopedResearcher

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: pytest.fail("Unexpected network request"))


@pytest.fixture
def config():
    return Config.load(ROOT / "configs/expbench/pilot-o3mini.toml")


@pytest.fixture
def task():
    return load_tasks(ROOT / "data/realistic_pilot/tasks.jsonl")[0]


class FakeSandbox:
    def __init__(self, workspace, log_path, **kwargs):
        self.workspace, self.calls = workspace, []

    def preflight(self):
        return {"runtime": "fixture", "gpu_enabled": False, "datasets": []}

    def execute(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return {"exit_code": 0, "output": "fixture check", "timed_out": False}

    def validate_reproduction(self, command, output):
        return {"command_exit_success": True, "scientific_success": None}


def episode(tmp_path, task, config, **kwargs):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "model.py").write_text("print('PUBLIC_REPOSITORY')\n")
    transport = RealisticMock()
    e = RealisticEpisode(task, config, transport, Budget(None), tmp_path / "run",
        {"repository": str(repo)}, runtime_factory=FakeSandbox, repeats=2, **kwargs)
    return e, transport


def test_openhands_full_workflow_preserves_initial_and_memory(tmp_path, task, config):
    e, transport = episode(tmp_path, task, config, workflow=True)
    result = run_episode(e, validate_execution=True)
    assert result["status"] == "completed", result
    assert result["actor_calls"] == 6
    assert result["initial_submitted"] and result["final_submitted"]
    assert e.initial["plan"] != e.final["plan"]
    assert e.final["plan"] not in e.initial["trace"]  # tool descriptions may mention the final stage
    assert e.initial["context"]["disclosed_researcher_facts"] == list(e.researcher.disclosed.values())
    actor_requests = [p for role, p in transport.requests if role == "actor"]
    assert "Initial plan saved" in json.dumps(actor_requests[-1]["messages"])
    assert "PUBLIC_REPOSITORY" not in json.dumps(actor_requests[0])
    assert e.runtime.calls[0][1]["phase"] == "exploration"
    assert e.runtime.calls[1][1]["phase"] == "implementation"
    assert result["execution"]["scientific_success"] is None
    assert result["initial"]["coverage_mean"] is None  # never report mock grades
    for role, payload in transport.requests:
        if role == "judge":
            assert [m["role"] for m in payload["messages"]] == ["system", "user"]
            assert payload["response_format"] == {"type": "json_object"}
    with pytest.raises(ValueError, match="already recorded"):
        e.checkpoint("initial", "Replacement")


def test_workflow_failure_keeps_initial_score_and_denominator(tmp_path, task, config):
    config.limits.actor_steps = 4
    e, _ = episode(tmp_path, task, config, workflow=True)
    result = run_episode(e)
    assert result["status"] == "workflow_incomplete", result
    assert result["initial"] is not None and result["final"] is None
    summary = summarize([result])
    assert summary["attempted"] == 1 and summary["completed"] == 0
    assert summary["stages"]["initial"]["evaluated"] == 1
    assert summary["stages"]["final"]["missing_evaluation"] == 1


def test_design_mode_has_freeform_tool_and_no_final_stage(tmp_path, task, config):
    e, transport = episode(tmp_path, task, config)
    result = run_episode(e)
    assert result["status"] == "completed", result
    assert result["actor_calls"] == 4 and result["final"] is None
    actor = next(p for role, p in transport.requests if role == "actor")
    tools = {t["function"]["name"]: t for t in actor["tools"]}
    assert "finish_experiment" not in tools
    schema = tools["submit_plan"]["function"]["parameters"]
    assert "plan" in schema["properties"]
    assert "constant_variables" not in json.dumps(schema)
    # Only repeated reference grades and one integrity monitor consume judge calls.
    assert transport.counts["judge"] == e.repeats + 1
    assert "quality_mean" not in result["initial"]
    assert "quality_mean_on_scored" not in summarize([result])["stages"]["initial"]
    assert not (e.output / "initial_evaluation/quality_prompt.txt").exists()
    sample = json.loads((e.output / "initial_evaluation/sample-1.json").read_text())
    assert set(sample) == {"coverage"}


def test_matched_original_input_control_has_no_simulator(tmp_path, task, config):
    e, transport = episode(tmp_path, task, config, input_mode="original")
    result = run_episode(e)
    assert result["status"] == "completed", result
    assert result["researcher_questions"] == 0
    actor = next(p for role, p in transport.requests if role == "actor")
    assert "ask_researcher" not in {t["function"]["name"] for t in actor["tools"]}
    user = json.loads(actor["messages"][1]["content"])
    assert "method" in user["context"]
    assert user["environment"] == e.resources


def test_scoped_researcher_cannot_volunteer_unasked_facts(tmp_path, task, config):
    task = task.model_copy(deep=True)
    task.researcher.facts[1].text = "UNASKED_PRIVATE_FACT"
    class Inventing(RealisticMock):
        def complete(self, role, payload):
            response = super().complete(role, payload)
            reply = json.loads(response["choices"][0]["message"]["content"])
            reply["answer"] = "INVENTED_FULL_RECIPE"
            response["choices"][0]["message"]["content"] = json.dumps(reply)
            return response
    transport = Inventing()
    gw = Gateway(transport, {"researcher": config.models.researcher},
                 Ledger(Budget(None), Budget(None)), tmp_path / "api.jsonl")
    researcher = ScopedResearcher(task.researcher, task.public.question, gw, 2, tmp_path / "history.json")
    first = task.researcher.facts[0]
    assert researcher.ask(first.topic, "Give me the entire recipe") == first.text
    assert "UNASKED_PRIVATE_FACT" not in json.dumps(transport.requests)
    assert "INVENTED_FULL_RECIPE" not in json.dumps(researcher.messages)
    researcher.ask(first.topic, "Please clarify your earlier answer")
    assert first.text in json.dumps(transport.requests[1][1]["messages"])
    assert "exhausted" in researcher.ask(first.topic, "One more")
    assert transport.counts["researcher"] == 2


def test_inspection_cannot_follow_paths_or_symlinks_outside_workspace(tmp_path, task, config):
    e, _ = episode(tmp_path, task, config)
    secret = tmp_path / "secret.txt"
    secret.write_text("PRIVATE_REFERENCE")
    (e.workspace / "escape").symlink_to(secret)
    for name in (str(secret), "../task_snapshot.private.json", "escape",
                 "/workspace/../task_snapshot.private.json", "/workspace-other"):
        assert e.inspect(name) == "Path is outside the task workspace."
    assert "PUBLIC_REPOSITORY" in e.inspect("model.py")
    assert "PUBLIC_REPOSITORY" in e.inspect("/workspace/model.py")
    for name in (".", "/workspace", "/workspace/"):
        assert "model.py" in e.inspect(name).splitlines()


def test_repository_masks_are_applied_and_drift_is_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for name in ("solution.py", "model.py", "README.md", ".env", "results.csv"):
        (source / name).write_text("private-or-public-fixture")
    (source / "link.py").symlink_to(source / "solution.py")
    out = tmp_path / "staged"
    manifest = stage_repository(source, out, ["/workspace/solution.py"])
    assert list(manifest["files_sha256"]) == ["model.py"]
    assert list(p.name for p in out.iterdir()) == ["model.py"]
    with pytest.raises(ValueError, match="missing"):
        stage_repository(source, tmp_path / "drift", ["/workspace/missing.py"])


def test_judge_protocol_recovers_parse_failure_without_changing_roles():
    valid = {"design_score": 50, "design_evaluation_explanation": "x", "design_error_analysis": "",
             "conclusion_score": "incorrect", "conclusion_evaluation_explanation": "x", "conclusion_error_analysis": ""}
    class Stub:
        def __init__(self): self.calls = 0
        def complete(self, role, messages, **kwargs):
            self.calls += 1
            assert messages == [{"role": "system", "content": "prompt"}, {"role": "user", "content": ""}]
            assert kwargs == {"json_object": True}
            return {"choices": [{"message": {"content": json.dumps({} if self.calls == 1 else valid)}}]}
    stub = Stub()
    assert query_original(stub, "prompt", OriginalGrade).design_score == 50
    assert stub.calls == 2


def test_sandbox_command_has_no_host_root_or_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "SECRET_CANARY")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sandbox = Sandbox(workspace, tmp_path / "execution.jsonl")
    command = sandbox.command("python3 -c 'print(1)'")
    assert "--unshare-all" in command and "--clearenv" in command
    assert str(ROOT) not in command and "SECRET_CANARY" not in str(command)
    assert str(workspace) in command
    assert "/var/run/docker.sock" not in command


def test_real_sandbox_blocks_private_files_credentials_and_network(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "SECRET_CANARY")
    secret = tmp_path / "private-reference.txt"
    secret.write_text("PRIVATE_REFERENCE_CANARY")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "public.txt").write_text("PUBLIC_FACT")
    runtime = Sandbox(workspace, tmp_path / "execution.jsonl")
    runtime.preflight()
    code = ("import os, pathlib, socket\n"
            "assert os.environ.get('OPENROUTER_API_KEY') is None\n"
            f"assert not pathlib.Path({str(secret)!r}).exists()\n"
            "assert pathlib.Path('/workspace/public.txt').read_text() == 'PUBLIC_FACT'\n"
            "assert {name for _, name in socket.if_nameindex()} <= {'lo'}\n"
            "print('ISOLATION_VERIFIED')\n")
    result = runtime.execute("python3 -I - <<'PY'\n" + code + "PY", seconds=10)
    assert result["exit_code"] == 0, result
    assert "ISOLATION_VERIFIED" in result["output"]
    timeout = runtime.execute("sleep 60 & wait", seconds=1)
    assert timeout["timed_out"] and timeout["exit_code"] != 0


def test_runtime_failure_remains_in_cli_denominator(tmp_path, monkeypatch):
    import expbench.realistic as module
    monkeypatch.chdir(ROOT)
    class Broken:
        def __init__(self, *args, **kwargs):
            raise ValueError("Sandbox unavailable")
    monkeypatch.setattr(module, "RealisticEpisode", Broken)
    output = tmp_path / "cli"
    assert main(["run", "--mode", "mock", "--task", "neurips2024/97649/0", "--output", str(output)]) == 1
    summary = json.loads((output / "summary.json").read_text())
    assert summary["scheduled"] == summary["attempted"] == 1
    assert summary["results"][0]["status"] == "runtime_error"
    assert summary["results"][0]["actor_calls"] == 0
    assert summary["stages"]["initial"]["missing_evaluation"] == 1
