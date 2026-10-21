import copy
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

from expbench.actor import BenchmarkExecutor, ReadContextAction
from expbench.budget import Budget, BudgetExceeded, Ledger
from expbench.gateway import Gateway, ModelError
from expbench.mock import MockTransport, DEMO_DESIGN
from expbench.researcher import Researcher
from expbench.runner import Episode, run_episode
from expbench.schema import Config, Design, Fact, Grade, load_tasks

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Tests must not make network connections")
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def config():
    return Config.load(ROOT / "tests/fixtures/expbench/pilot.toml")


@pytest.fixture
def tasks():
    return load_tasks(ROOT / "data/design_pilot/tasks.jsonl")


def gateway(tmp_path, config, transport=None, cap=20):
    return Gateway(transport or MockTransport(),
                   {r: getattr(config.models, r) for r in ("actor", "researcher", "judge")},
                   Ledger(Budget(cap), Budget(cap)), tmp_path / "calls.jsonl")


def test_real_openhands_five_task_mock_pilot(tmp_path, config, tasks):
    budget = Budget(20)
    for i, task in enumerate(tasks):
        transport = MockTransport()
        out = tmp_path / str(i)
        result = run_episode(task, config, transport, budget, out)
        assert result["status"] == "completed", result
        assert result["actor_calls"] == 4
        assert result["researcher_questions"] == 2
        assert result["design_score"] is None  # never report mock fixture scores as results
        events = [json.loads(line) for line in (out / "actor_events.jsonl").read_text().splitlines()]
        assert not any(e["kind"] == "AgentErrorEvent" for e in events)
        observations = [e for e in events if e["kind"] == "ObservationEvent"]
        assert len(observations) == 4
        assert all(not e["observation"]["is_error"] for e in observations)
        # The second actor turn sees the actual read_context observation.
        actor_requests = [p for role, p in transport.requests if role == "actor"]
        assert "design-only episode" in json.dumps(actor_requests[1]["messages"])
        assert task.researcher.facts[0].text in json.dumps(actor_requests[2]["messages"])
        tools = {t["function"]["name"] for t in actor_requests[0]["tools"]}
        assert tools == {"read_context", "ask_researcher", "submit_design"}
        assert (out / "design.json").is_file() and (out / "grade.json").is_file()
    assert budget.charged == 0


def test_reference_and_unasked_facts_do_not_reach_actor(tmp_path, config, tasks):
    task = tasks[0].model_copy(deep=True)
    task.reference_design.constant_variables["private_test"] = "HIDDEN_REFERENCE_CANARY"
    task.researcher.facts.append(Fact(id="private_test", topic="other", text="UNASKED_FACT_CANARY", source_field="test"))
    transport = MockTransport()
    result = run_episode(task, config, transport, Budget(20), tmp_path / "run")
    assert result["status"] == "completed"
    for role, payload in transport.requests:
        text = json.dumps(payload)
        if role == "actor":
            assert "HIDDEN_REFERENCE_CANARY" not in text
            assert "UNASKED_FACT_CANARY" not in text
        elif role == "researcher":
            assert "HIDDEN_REFERENCE_CANARY" not in text
        else:
            assert "HIDDEN_REFERENCE_CANARY" in text
            assert "UNASKED_FACT_CANARY" in text


def test_researcher_memory_and_reset(tmp_path, config, tasks):
    gw = gateway(tmp_path, config)
    first = Researcher(tasks[0].researcher, "Question A", gw, 3, tmp_path / "history.json")
    answer = first.ask("Initial question")
    first.ask("Follow-up question")
    second_request = gw.transport.requests[1][1]["messages"]
    assert [m["role"] for m in second_request] == ["system", "user", "assistant", "user"]
    assert answer in second_request[2]["content"]
    fresh = Researcher(tasks[1].researcher, "Question B", gw, 3, tmp_path / "fresh.json")
    assert len(fresh.messages) == 1 and fresh.questions == 0
    assert "Initial question" not in json.dumps(fresh.messages)


def test_question_budget_does_not_make_extra_calls(tmp_path, config, tasks):
    gw = gateway(tmp_path, config)
    researcher = Researcher(tasks[0].researcher, "Question", gw, 1, tmp_path / "r.json")
    researcher.ask("First")
    assert "exhausted" in researcher.ask("Second")
    assert gw.transport.counts["researcher"] == 1


def test_arbitrary_paths_are_not_readable(tmp_path, config, tasks):
    secret = tmp_path / "secret.txt"
    secret.write_text("DO_NOT_READ")
    episode = Episode(tasks[0], config, MockTransport(), Budget(20), tmp_path / "run")
    executor = BenchmarkExecutor(episode, "read_context")
    for path in (str(secret), "../../data/exp_bench/tasks.jsonl", "/proc/self/environ"):
        observation = executor(ReadContextAction(name=path))
        assert "DO_NOT_READ" not in observation.model_dump_json()
        assert "Unknown document" in observation.model_dump_json()


def test_step_limit_does_not_invoke_judge(tmp_path, config, tasks):
    config.limits.actor_steps = 1
    transport = MockTransport()
    result = run_episode(tasks[0], config, transport, Budget(20), tmp_path / "run")
    assert result["status"] == "no_submission"
    assert transport.counts["actor"] == 1
    assert transport.counts["judge"] == 0


def test_submission_is_immutable(tmp_path, config, tasks):
    episode = Episode(tasks[0], config, MockTransport(), Budget(20), tmp_path / "run")
    design = Design.model_validate(DEMO_DESIGN)
    episode.submit(design)
    with pytest.raises(ModelError):
        episode.submit(design)
    executor = BenchmarkExecutor(episode, "ask_researcher")
    from expbench.actor import AskResearcherAction
    assert "already" in executor(AskResearcherAction(question="After submission")).model_dump_json()
    assert episode.researcher.questions == 0


class ChargedMock(MockTransport):
    mock = False


def test_reservation_stops_before_network(tmp_path, config):
    transport = ChargedMock()
    gw = gateway(tmp_path, config, transport, cap=0.00001)
    with pytest.raises(BudgetExceeded):
        gw.complete("actor", [{"role": "user", "content": "Hello"}])
    assert not transport.requests
    assert gw.ledger.run.charged == 0


def test_shared_run_budget():
    shared = Budget(0.1)
    first, second = Ledger(shared, Budget(1)), Ledger(shared, Budget(1))
    first.reserve(0.08)
    first.settle(0.08, 0.07, {})
    with pytest.raises(BudgetExceeded):
        second.reserve(0.04)
    assert shared.charged == pytest.approx(0.07)


def test_failed_request_retains_reservation_and_stops(tmp_path, config):
    class Failing(ChargedMock):
        def complete(self, role, payload):
            raise ModelError("Timeout")
    gw = gateway(tmp_path, config, Failing())
    with pytest.raises(ModelError):
        gw.complete("judge", [{"role": "user", "content": "Hello"}])
    assert gw.ledger.run.charged > 0
    assert gw.ledger.records[0]["billing_status"] == "unknown_reserved"
    before = gw.ledger.run.charged
    with pytest.raises(ModelError):
        gw.complete("judge", [])
    assert gw.ledger.run.charged == before


def test_reasoning_is_not_counted_twice(tmp_path, config):
    class Reasoning(ChargedMock):
        def complete(self, role, payload):
            out = super().complete(role, payload)
            out["usage"] = {"prompt_tokens": 100, "completion_tokens": 50,
                            "completion_tokens_details": {"reasoning_tokens": 40}}
            return out
    gw = gateway(tmp_path, config, Reasoning())
    gw.complete("judge", [{"role": "user", "content": "Hello"}])
    assert gw.ledger.run.charged == pytest.approx((100 * 1.1 + 50 * 4.4) / 1e6)


def test_unknown_researcher_fact_id_is_rejected(tmp_path, config, tasks):
    class Hallucination(MockTransport):
        def complete(self, role, payload):
            out = super().complete(role, payload)
            out["choices"][0]["message"]["content"] = json.dumps({"answer": "Invented", "fact_ids": ["nonexistent"]})
            return out
    gw = gateway(tmp_path, config, Hallucination())
    researcher = Researcher(tasks[0].researcher, "Question", gw, 1, tmp_path / "r.json")
    with pytest.raises(ModelError, match="unknown fact"):
        researcher.ask("Question")
    assert not any(m["role"] == "assistant" for m in researcher.messages)


def test_missing_evidence_returns_fixed_unknown(tmp_path, config, tasks):
    class Ungrounded(MockTransport):
        def complete(self, role, payload):
            out = super().complete(role, payload)
            out["choices"][0]["message"]["content"] = json.dumps({"answer": "You have 100 GPUs", "fact_ids": []})
            return out
    researcher = Researcher(tasks[0].researcher, "Question", gateway(tmp_path, config, Ungrounded()),
                            1, tmp_path / "r.json")
    answer = researcher.ask("What hardware do I have?")
    assert "not specified" in answer and "100 GPUs" not in answer


def test_invalid_grades_and_designs_are_rejected():
    for score in (-1, 101, "50", True):
        with pytest.raises(ValueError):
            Grade(design_score=score, design_evaluation_explanation="Test", design_error_analysis="")
    bad = copy.deepcopy(DEMO_DESIGN)
    bad["constant_variables"] = [" "]
    with pytest.raises(ValueError):
        Design.model_validate(bad)


def test_regrade_preserves_design_and_uses_researcher_context(tmp_path, config, tasks):
    transport = MockTransport()
    design = Design.model_validate(DEMO_DESIGN)
    result = run_episode(tasks[2], config, transport, Budget(None), tmp_path / "run", saved_design=design)
    assert result["status"] == "completed" and result["grade_only"]
    assert [role for role, _ in transport.requests] == ["judge"]
    payload = json.loads(transport.requests[0][1]["messages"][1]["content"])
    assert payload["approved_researcher_context"] == tasks[2].researcher.model_dump()
    assert payload["design_output"] == design.model_dump()
    assert json.loads((tmp_path / "run" / "design.json").read_text()) == design.model_dump()
