"""Synthetic checks of isolation and lifecycle; no scientific/model execution."""

import io
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from personasciencebench import protocol
from personasciencebench.adapters.base import sha256
from personasciencebench.inference import OpenRouterClient
from personasciencebench.packaging import asset_readiness, export_episode
from personasciencebench.researcher import Researcher, UNKNOWN
from personasciencebench.schema import (
    Asset, Episode, EvaluatorSpec, Fact, Provenance, PublicContext,
    ResearcherContext, Submission,
)
from personasciencebench.session import EpisodeSession


class ScriptedBackend:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []

    def complete(self, messages, *, json_mode=False, settings=None):
        self.calls.append(messages)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return json.dumps(response) if isinstance(response, dict) else response


def episode_fixture():
    return Episode(
        id="synthetic:one", benchmark="synthetic", source_task_id="one",
        study_id="study-one", domain="synthetic", source_revision="synthetic-v1",
        public=PublicContext(question="Describe the supplied synthetic data.",
                             researcher_topics=["sample_metadata"]),
        researcher=ResearcherContext(facts=[Fact(
            id="study.sample", topic="sample_metadata", text="APPROVED_CONTEXT: samples are paired.",
            source=Provenance(source_path="curation.txt", revision="v1", locator="line 1"),
            review_status="reviewed",
        ), Fact(
            id="study.unreviewed", topic="sample_metadata", text="UNREVIEWED_CONTEXT_SENTINEL",
            source=Provenance(source_path="curation.txt", revision="v1", locator="line 2"),
            review_status="candidate",
        )]),
        evaluator=EvaluatorSpec(kind="synthetic", version="v1",
                                reference={"answer": "EVALUATOR_PRIVATE_SENTINEL"},
                                entrypoint="never_imported_or_executed:fail"),
    )


def test_constructor_and_export_are_offline_and_public_contains_only_allowed_inputs(tmp_path):
    episode = episode_fixture()
    source = tmp_path / "allowed.csv"
    source.write_text("a,b\n1,2\n")
    private = tmp_path / "reference.txt"
    private.write_text("EVALUATOR_FILE_SENTINEL")
    episode.assets = [
        Asset(id="data", source_path=str(source), target_path="data/input.csv", sha256=sha256(source)),
        Asset(id="gold", source_path=str(private), target_path="reference.txt", visibility="evaluator"),
    ]
    backend = ScriptedBackend()  # Raises StopIteration if construction invokes it.
    researcher = Researcher(episode, backend)
    assert researcher.history == [] and backend.calls == []
    summary = export_episode(episode, tmp_path / "package")
    assert summary["assets_ready"] is True
    assert summary["runtime_tested"] is False and summary["model_tested"] is False
    assert backend.calls == []
    actor_files = list((tmp_path / "package/actor").rglob("*"))
    actor_text = "\n".join(path.read_text() for path in actor_files if path.is_file())
    assert "APPROVED_CONTEXT" not in actor_text
    assert "UNREVIEWED_CONTEXT" not in actor_text
    assert "EVALUATOR_PRIVATE_SENTINEL" not in actor_text
    assert "EVALUATOR_FILE_SENTINEL" not in actor_text
    assert str(source) not in actor_text
    assert "a,b" in actor_text
    saved = json.loads((tmp_path / "package/controller/episode.private.json").read_text())
    assert saved["evaluator"]["reference"]["answer"] == "EVALUATOR_PRIVATE_SENTINEL"


def test_assets_fail_closed_for_hash_changes_and_symlinks(tmp_path):
    episode = episode_fixture()
    source = tmp_path / "data.txt"
    source.write_text("original")
    episode.assets = [Asset(id="data", source_path=str(source), target_path="data.txt", sha256=sha256(source))]
    source.write_text("changed")
    assert asset_readiness(episode)["hash_mismatches"] == ["data"]
    with pytest.raises(ValueError, match="integrity"):
        export_episode(episode, tmp_path / "changed")
    link = tmp_path / "link.txt"
    link.symlink_to(source)
    episode.assets[0].source_path = str(link)
    episode.assets[0].sha256 = None
    assert asset_readiness(episode)["symlinks_rejected"] == ["data"]


def test_duplicate_runtime_mounts_are_rejected(tmp_path):
    episode = episode_fixture()
    source = tmp_path / "data.txt"
    source.write_text("synthetic")
    episode.assets = [
        Asset(id="one", source_path=str(source), target_path="data/input.txt"),
        Asset(id="two", source_path=str(source), target_path="data/input.txt"),
    ]
    with pytest.raises(ValueError):
        export_episode(episode, tmp_path / "ambiguous")


@pytest.mark.parametrize("fact_ids", [["unknown"], ["study.unreviewed"], ["study.sample", "study.sample"]])
def test_unknown_unreviewed_or_duplicate_citations_publish_unknown(fact_ids):
    episode = episode_fixture()
    backend = ScriptedBackend({"answer": "UNSUPPORTED_GENERATED_SENTINEL", "fact_ids": fact_ids})
    researcher = Researcher(episode, backend)
    reply = researcher.ask("What is the sample design?")
    assert reply["answer"] == UNKNOWN and reply["fact_ids"] == []
    assert researcher.disclosed == {}
    history = json.dumps(researcher.history)
    assert "UNSUPPORTED_GENERATED_SENTINEL" not in history
    model_inputs = json.dumps(backend.calls)
    assert "UNREVIEWED_CONTEXT_SENTINEL" not in model_inputs
    assert "EVALUATOR_PRIVATE_SENTINEL" not in model_inputs


def test_grounding_rejection_falls_back_and_memory_contains_published_reply():
    episode = episode_fixture()
    backend = ScriptedBackend(
        {"answer": "UNSUPPORTED_RESULT: the treatment cured every subject.", "fact_ids": ["study.sample"]},
        {"supported": False},
    )
    researcher = Researcher(episode, backend, mode="grounded")
    reply = researcher.ask("What is the sample design?")
    assert reply["answer"] == episode.researcher.facts[0].text
    assert reply["fallback"] == "unsupported_prose_extractive_fallback"
    assert researcher.history[-1]["content"] == reply["answer"]
    assert "UNSUPPORTED_RESULT" not in json.dumps(researcher.history)
    assert set(researcher.disclosed) == {"study.sample"}
    assert len(backend.calls) == 2
    fresh = Researcher(episode, ScriptedBackend())
    assert fresh.history == [] and fresh.disclosed == {}


def test_grounding_transport_failure_remains_explicit_and_discloses_no_reply():
    episode = episode_fixture()
    backend = ScriptedBackend(
        {"answer": "The samples are paired.", "fact_ids": ["study.sample"]},
        RuntimeError("transport failed: PRIVATE_PROVIDER_DETAIL"),
    )
    researcher = Researcher(episode, backend, mode="grounded")
    with pytest.raises(RuntimeError, match="transport failed"):
        researcher.ask("What is the sample design?")
    # Provider outages must remain infrastructure failures, rather than making
    # an apparently successful scientific interaction with an unrecorded outage.
    assert researcher.disclosed == {} and researcher.audit == []
    assert researcher.history[-1]["role"] == "user"
    assert "PRIVATE_PROVIDER_DETAIL" not in json.dumps(researcher.history)


def test_topic_scope_and_question_limit_do_not_trigger_extra_backend_calls():
    episode = episode_fixture()
    backend = ScriptedBackend()
    researcher = Researcher(episode, backend, max_questions=1)
    first = researcher.ask("What is the gold result?", topic="unavailable_topic")
    second = researcher.ask("Try again")
    assert first["answer"] == UNKNOWN and first["fact_ids"] == []
    assert second["fallback"] == "question_limit"
    assert backend.calls == []


def test_artifact_rejection_is_recoverable_and_final_snapshot_is_immutable(tmp_path):
    episode = episode_fixture()
    root = tmp_path / "actor"
    root.mkdir()
    first = root / "first.txt"
    first.write_text("original analysis evidence")
    second = root / "second.txt"
    second.write_text("second evidence")
    forbidden = tmp_path / "controller_secret.txt"
    forbidden.write_text("PRIVATE_CONTROLLER_SENTINEL")
    session = EpisodeSession(episode, Researcher(episode, ScriptedBackend()),
                             tmp_path / "controller", artifact_root=root)
    bad = Submission(episode_id=episode.id, answer="Synthetic answer",
                     artifacts={"first": str(first), "second": str(forbidden)})
    with pytest.raises(ValueError, match="artifact root"):
        session.submit_result(bad)
    assert session.closed is False and session.submission is None
    valid = bad.model_copy(update={"artifacts": {"first": str(first), "second": str(second)}})
    result = session.submit_result(valid)
    assert result["submitted"] is True and session.closed is True
    first.write_text("mutated after submission")
    assert Path(session.submission.artifacts["first"]).read_text() == "original analysis evidence"
    with pytest.raises(ValueError, match="already submitted"):
        session.ask_researcher("Late question")


def test_artifact_symlink_and_controller_mount_are_rejected(tmp_path):
    episode = episode_fixture()
    root = tmp_path / "actor"
    root.mkdir()
    file = root / "data.txt"
    file.write_text("evidence")
    link = root / "link.txt"
    link.symlink_to(file)
    researcher = Researcher(episode, ScriptedBackend())
    with pytest.raises(ValueError, match="Controller output"):
        EpisodeSession(episode, researcher, root / "controller", artifact_root=root)
    session = EpisodeSession(episode, researcher, tmp_path / "controller", artifact_root=root)
    with pytest.raises(ValueError, match="regular file"):
        session.submit_result(Submission(episode_id=episode.id, artifacts={"analysis": str(link)}))


def test_plan_checkpoint_preserves_disclosure_prefix_without_ending_full_workflow(tmp_path):
    episode = episode_fixture()
    backend = ScriptedBackend({"answer": "ignored in extractive mode", "fact_ids": ["study.sample"]})
    session = EpisodeSession(episode, Researcher(episode, backend), tmp_path / "controller")
    result = session.submit_plan("Initial analysis plan")
    assert result["continue_workflow"] is True and session.closed is False
    checkpoint_path = session.output / "initial_plan.json"
    before = checkpoint_path.read_bytes()
    session.ask_researcher("What is the sample design?")
    assert checkpoint_path.read_bytes() == before
    assert json.loads(before)["disclosed_fact_ids"] == []
    assert set(session.researcher.disclosed) == {"study.sample"}


def test_handler_auth_public_context_and_lifecycle_without_network(tmp_path, monkeypatch):
    class DummyServer:
        def __init__(self, address, handler):
            self.address, self.RequestHandlerClass = address, handler
    monkeypatch.setattr(protocol, "ThreadingHTTPServer", DummyServer)
    episode = episode_fixture()
    backend = ScriptedBackend()
    session = EpisodeSession(episode, Researcher(episode, backend), tmp_path / "controller")
    token = "unit-test-only-long-endpoint-token"
    server = protocol.server_for(session, token)

    def request(method, path, body=None, authorized=True):
        handler = object.__new__(server.RequestHandlerClass)
        raw = json.dumps(body).encode() if body is not None else b""
        handler.headers = {"Content-Length": str(len(raw))}
        if authorized:
            handler.headers["Authorization"] = "Bearer " + token
        handler.path, handler.rfile = path, io.BytesIO(raw)
        response = []
        handler.send = lambda code, payload: response.append((code, payload))
        getattr(handler, "do_" + method)()
        return response[0]

    assert request("GET", "/context", authorized=False)[0] == 401
    assert request("POST", "/ask_researcher", {"question": "ignored"}, authorized=False)[0] == 401
    assert backend.calls == [] and session.sequence == 0
    status, public = request("GET", "/context")
    assert status == 200 and public["episode_id"] == episode.id
    assert "PRIVATE_SENTINEL" not in json.dumps(public)
    assert "APPROVED_CONTEXT" not in json.dumps(public)
    assert request("GET", "/evaluator")[0] == 404
    assert request("POST", "/submit_result", {"episode_id": "wrong"})[0] == 400
    assert request("POST", "/submit_result", {"episode_id": episode.id, "answer": "Synthetic final"})[0] == 200
    assert request("POST", "/ask_researcher", {"question": "Too late"})[0] == 400
    assert backend.calls == []


def test_openrouter_transport_is_lazy_and_never_records_authorization(monkeypatch):
    calls, records = [], []
    class TransportError(Exception):
        pass
    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(status_code=200, json=lambda: {
            "model": "resolved-test-model", "provider": "synthetic", "usage": {"total_tokens": 3},
            "choices": [{"finish_reason": "stop", "message": {"content": "synthetic response"}}],
        })
    monkeypatch.setitem(sys.modules, "httpx", SimpleNamespace(post=fake_post, HTTPError=TransportError))
    monkeypatch.setenv("OPENROUTER_API_KEY", "NONSECRET_UNIT_TEST_TOKEN")
    client = OpenRouterClient("synthetic-model", role="researcher", record=records.append)
    assert calls == [] and records == []
    assert client.complete([{"role": "user", "content": "synthetic request"}],
                           settings={"temperature": 0.2}) == "synthetic response"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer NONSECRET_UNIT_TEST_TOKEN"
    assert calls[0][1]["json"]["temperature"] == 0.2
    assert "NONSECRET_UNIT_TEST_TOKEN" not in json.dumps(records)
    assert records[0]["resolved_model"] == "resolved-test-model"


def test_openrouter_incomplete_completions_cannot_be_graded_as_finished(monkeypatch):
    class TransportError(Exception):
        pass
    def fake_post(url, **kwargs):
        return SimpleNamespace(status_code=200, json=lambda: {
            "usage": {"total_tokens": 9},
            "choices": [{"finish_reason": "length", "message": {"content": "<grade>incorrect</grade>"}}],
        })
    monkeypatch.setitem(sys.modules, "httpx", SimpleNamespace(post=fake_post, HTTPError=TransportError))
    monkeypatch.setenv("OPENROUTER_API_KEY", "NONSECRET_UNIT_TEST_TOKEN")
    client = OpenRouterClient("synthetic-model", role="judge")
    with pytest.raises(RuntimeError, match="incomplete"):
        client.complete([{"role": "user", "content": "synthetic request"}])
