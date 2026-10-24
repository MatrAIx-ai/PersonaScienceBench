"""Offline actor boundary and scripted OpenHands integration checks."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from personasciencebench.actor import ActorController, run_actor
from personasciencebench.researcher import Researcher
from personasciencebench.schema import Episode, EvaluatorSpec, PublicContext, ResearcherContext, Fact, Provenance
from personasciencebench.session import EpisodeSession


class ResearcherBackend:
    def __init__(self):
        self.requests = []

    def complete(self, messages, *, json_mode=False, settings=None):
        self.requests.append(messages)
        return json.dumps({"answer": "The study has two conditions.", "fact_ids": ["conditions"]})


class FakeSandbox:
    def __init__(self, workspace):
        self.workspace = workspace
        self.calls = []

    def execute(self, command, timeout_seconds):
        self.calls.append((command, timeout_seconds))
        # No subprocess and no execution of actor-supplied command text.
        (self.workspace / "analysis.py").write_text("print('scripted offline fixture')\n")
        return {"exit_code": 0, "output": "scripted fixture output", "timed_out": False}


@pytest.fixture
def setup(tmp_path):
    workspace = tmp_path / "actor-workspace"
    workspace.mkdir()
    episode = Episode(
        id="fixture-task", benchmark="bixbench", source_task_id="native-id",
        study_id="study-one", domain="biology", source_revision="fixture",
        public=PublicContext(question="Compare the two conditions.", researcher_topics=["conditions"]),
        researcher=ResearcherContext(facts=[Fact(id="conditions", topic="conditions", text="The study has two conditions.",
            source=Provenance(source_path="fixture", revision="fixture", locator="/conditions"), review_status="reviewed")]),
        evaluator=EvaluatorSpec(kind="fixture", version="fixture", reference={"answer": "EVALUATOR_SECRET_SENTINEL"}),
    )
    backend = ResearcherBackend()
    researcher = Researcher(episode, backend)
    session = EpisodeSession(episode, researcher, tmp_path / "private-controller", artifact_root=workspace)
    sandbox = FakeSandbox(workspace)
    client = SimpleNamespace(model="openai/gpt-6-luna", max_tokens=1024)
    return session, sandbox, client, backend


def test_dispatch_records_commands_and_shared_memory_without_sdk(setup):
    session, sandbox, client, backend = setup
    controller = ActorController(session, client, sandbox)
    result = controller.dispatch("execute_command", {"command": "python analysis.py", "timeout_seconds": 17})
    assert result["exit_code"] == 0
    assert sandbox.calls == [("python analysis.py", 17)]
    assert session.researcher.history == []
    controller.dispatch("report_progress", {"message": "I inspected the input format."})
    response = controller.dispatch("ask_researcher", {"question": "What are the conditions?", "topic": "conditions"})
    assert response["fact_ids"] == ["conditions"]
    assert "EVALUATOR_SECRET_SENTINEL" not in json.dumps(backend.requests)
    assert "shared_progress" in backend.requests[0][1]["content"]


def test_bix_final_requires_actual_nonempty_artifact_and_execution_declaration(setup):
    session, sandbox, client, _ = setup
    controller = ActorController(session, client, sandbox)
    with pytest.raises(ValueError, match="BixBench requires"):
        controller.dispatch("submit_result", {"answer": "A finding"})
    with pytest.raises(ValueError, match="regular"):
        controller.dispatch("submit_result", {"answer": "A finding", "payload": {"executed_analysis": True},
                                               "artifacts": {"analysis": "missing.py"}})
    (sandbox.workspace / "analysis.py").touch()
    with pytest.raises(ValueError, match="cannot be empty"):
        controller.dispatch("submit_result", {"answer": "A finding", "payload": {"executed_analysis": True},
                                               "artifacts": {"analysis": "analysis.py"}})
    controller.dispatch("execute_command", {"command": "python analysis.py"})
    accepted = controller.dispatch("submit_result", {"answer": "A finding", "payload": {"executed_analysis": True},
                                                       "artifacts": {"analysis": "analysis.py"}})
    assert accepted["submitted"] is True
    assert session.closed
    sealed = Path(session.submission.artifacts["analysis"])
    (sandbox.workspace / "analysis.py").write_text("changed after submission")
    assert "scripted offline fixture" in sealed.read_text()
    assert "already been submitted" in controller.dispatch("execute_command", {"command": "anything"})["error"]


@pytest.mark.parametrize("raw_path", ["/etc/passwd", "../private-controller/episode.private.json", "/workspace/analysis.py", "..\\private-controller\\x"])
def test_submission_rejects_nonrelative_or_traversal_artifact_paths(setup, raw_path):
    session, sandbox, client, _ = setup
    controller = ActorController(session, client, sandbox)
    with pytest.raises(ValueError, match="relative"):
        controller.dispatch("submit_result", {"answer": "A finding", "artifacts": {"analysis": raw_path}})
    assert not session.closed


def test_submission_rejects_symlinked_artifact_and_wrong_root(setup, tmp_path):
    session, sandbox, client, _ = setup
    secret = tmp_path / "secret.py"
    secret.write_text("private")
    (sandbox.workspace / "link.py").symlink_to(secret)
    with pytest.raises(ValueError):
        ActorController(session, client, sandbox).dispatch("submit_result", {"answer": "A finding", "artifacts": {"analysis": "link.py"}})
    other = FakeSandbox(tmp_path)
    with pytest.raises(ValueError, match="artifact_root"):
        ActorController(session, client, other)


def test_plan_checkpoint_does_not_finish_full_workflow(setup):
    session, sandbox, client, _ = setup
    controller = ActorController(session, client, sandbox)
    result = controller.dispatch("submit_plan", {"plan": "Analyze the provided data."})
    assert result["continue_workflow"] is True
    assert session.submission is None and not session.closed
    with pytest.raises(FileExistsError):
        controller.dispatch("submit_plan", {"plan": "Replace the initial plan."})


def test_scienceagent_missing_native_artifact_is_correctable_before_closure(setup):
    session, sandbox, client, _ = setup
    session.episode.benchmark = "scienceagentbench"
    session.episode.public.submission = {"program": "solution.py", "required_artifacts": ["pred_results/result.csv"]}
    (sandbox.workspace / "solution.py").write_text("print('fixture')\n")
    controller = ActorController(session, client, sandbox)
    with pytest.raises(ValueError, match="pred_results/result.csv"):
        controller.dispatch("submit_result", {"answer": "Computed", "artifacts": {"solution.py": "solution.py"}})
    assert not session.closed
    (sandbox.workspace / "output.csv").write_text("1,2\n")
    result = controller.dispatch("submit_result", {"answer": "Computed", "artifacts": {
        "solution.py": "solution.py", "pred_results/result.csv": "output.csv"}})
    assert result["submitted"] is True
    assert set(session.submission.artifacts) == {"solution.py", "pred_results/result.csv"}


class ScriptedActorClient:
    model = "openai/gpt-6-luna"
    max_tokens = 1024

    def __init__(self, actions):
        self.actions = iter(actions)
        self.requests = []

    def completion(self, messages, tools=None):
        self.requests.append({"messages": messages, "tools": tools})
        name, arguments = next(self.actions)
        return {
            "id": f"fake-{len(self.requests)}", "object": "chat.completion", "created": 0,
            "model": self.model, "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None, "tool_calls": [{
                    "id": f"call-{len(self.requests)}", "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }],
            }}],
        }


def test_openhands_loop_uses_only_public_input_and_controller_tools(setup):
    try:
        available = importlib.util.find_spec("openhands.sdk") is not None
    except ModuleNotFoundError:
        available = False
    if not available:
        pytest.skip("Optional OpenHands SDK is not installed")
    session, sandbox, _, backend = setup
    client = ScriptedActorClient([
        ("execute_command", {"command": "python analysis.py", "timeout_seconds": 10}),
        ("ask_researcher", {"question": "What are the conditions?", "topic": "conditions"}),
        ("report_progress", {"message": "The fixture analysis completed."}),
        ("submit_plan", {"plan": "Document the completed comparison."}),
        ("submit_result", {"answer": "The fixture finding.", "payload": {"executed_analysis": True}, "artifacts": {"analysis": "analysis.py"}}),
    ])
    result = run_actor(session, client, sandbox, max_steps=7)
    assert result["status"] == "submitted", result
    assert result["actor_calls"] == 5
    assert result["execution_calls"] == 1
    assert result["scientific_execution_verified"] is False
    assert "EVALUATOR_SECRET_SENTINEL" not in json.dumps(client.requests)
    names = {tool["function"]["name"] for tool in client.requests[0]["tools"]}
    assert names == {"execute_command", "ask_researcher", "report_progress", "submit_plan", "submit_result"}
    events = [json.loads(line) for line in (session.output / "actor_events.jsonl").read_text().splitlines()]
    assert events
    assert "EVALUATOR_SECRET_SENTINEL" not in json.dumps(events)
    assert session.researcher.questions == 1
    assert len(backend.requests) == 1
