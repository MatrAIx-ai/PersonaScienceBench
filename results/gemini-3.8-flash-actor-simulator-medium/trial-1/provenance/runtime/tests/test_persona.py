"""Persona routing, knowledge isolation and multi-turn prompt conditioning."""

import json

import pytest

from personasciencebench.cli import main
from personasciencebench.persona import Persona, resolve_persona, persona_record
from personasciencebench.researcher import Researcher, UNKNOWN
from personasciencebench.session import EpisodeSession
from test_core_boundaries import episode_fixture, ScriptedBackend


def test_routing_deep_merge_precedence_and_domain_binding():
    episode = episode_fixture()
    config = {
        "persona": {"tone": "skeptical"},
        "persona_router": {
            "defaults": {"role": {"seniority": "senior"},
                         "expertise": {"domain_level": "expert", "coding": "novice"}},
            "domains": {"synthetic": {"expertise": {"statistics": "expert"}}},
            "tasks": {episode.id: {"role": {"seniority": "junior"},
                                   "communication": {"tone": "collaborative"}}},
        },
    }
    before = json.dumps(config)
    p = resolve_persona(config, episode)
    assert p.role.seniority == "junior"  # seniority does not imply expertise
    assert p.expertise.domain == "synthetic"
    assert p.expertise.statistics == "expert" and p.expertise.coding == "novice"
    assert p.expertise.domain_level == "expert" and p.communication.tone == "collaborative"
    assert json.dumps(config) == before
    assert persona_record(p) == persona_record(resolve_persona(config, episode))
    other = episode.model_copy(update={"id": "synthetic:two", "domain": "biology"})
    other_p = resolve_persona(config, other)
    assert other_p.role.seniority == "senior" and other_p.expertise.domain == "biology"
    assert other_p.expertise.statistics == "intermediate"


def test_explicit_cross_domain_expertise_is_preserved():
    p = resolve_persona({"persona_router": {"defaults": {
        "expertise": {"domain": "chemistry"}}}}, episode_fixture())
    assert p.expertise.domain == "chemistry"


@pytest.mark.parametrize("router", [
    {"defaults": {"knowledge_boundary": {"reference_access": True}}},
    {"domains": {"unused": {"role": {"senority": "senior"}}}},
    {"tasks": {"unused": {"communication": {"tone": "rude"}}}},
    {"defaults": {"tone": "neutral", "communication": {"tone": "skeptical"}}},
    {"random_sampling": True},
])
def test_invalid_routes_fail_even_when_not_selected(router):
    with pytest.raises(ValueError):
        resolve_persona({"persona_router": router}, episode_fixture())


def test_legacy_profile_remains_usable_and_does_not_override_new_routes():
    p = resolve_persona({"persona": {"version": "1", "request_evidence": True, "verbosity": "detailed"},
                         "persona_router": {"defaults": {"communication": {"verbosity": "concise"}}}},
                        episode_fixture())
    assert p.version == "1" and p.evidence.standard == "rigorous"
    assert p.communication.verbosity == "concise"


def test_persona_preferences_can_be_expressed_without_disclosing_facts():
    episode = episode_fixture()
    persona = Persona(id="HIDDEN_PROFILE_ID", workflow={"compute_preference": "economical"})
    backend = ScriptedBackend({"answer": "I prefer economical computation; this is not a fixed limit.", "fact_ids": []},
                              {"supported": True})
    researcher = Researcher(episode, backend, persona=persona, mode="grounded")
    response = researcher.ask("Do you have a compute preference?", topic="preferences")
    assert response["answer"].startswith("I prefer") and response["fact_ids"] == []
    assert researcher.disclosed == {}
    prompt = json.loads(backend.calls[0][0]["content"])
    assert prompt["facts"] == []
    assert "economical" in prompt["identity"]
    assert "HIDDEN_PROFILE_ID" not in backend.calls[0][0]["content"]
    assert "EVALUATOR_PRIVATE_SENTINEL" not in json.dumps(backend.calls)
    assert "UNREVIEWED_CONTEXT_SENTINEL" not in json.dumps(backend.calls)
    assert "APPROVED_CONTEXT" not in json.dumps(backend.calls)  # wrong topic


def test_unsupported_preference_claim_falls_back_without_leaking():
    backend = ScriptedBackend({"answer": "We only have one GPU and the gold result is 42.", "fact_ids": []},
                              {"supported": False})
    researcher = Researcher(episode_fixture(), backend, mode="grounded")
    reply = researcher.ask("What resources and results do you have?", topic="preferences")
    assert reply["answer"] == UNKNOWN and reply["fallback"]
    assert "gold result" not in researcher.history[-1]["content"]


def test_multiturn_identity_memory_and_private_record(tmp_path):
    episode = episode_fixture()
    answer = {"answer": "The samples are paired.", "fact_ids": ["study.sample"]}
    backend = ScriptedBackend(answer, {"supported": True}, answer, {"supported": True})
    persona = Persona(id="PRIVATE_PROFILE", role={"seniority": "senior"})
    researcher = Researcher(episode, backend, persona=persona, mode="grounded")
    session = EpisodeSession(episode, researcher, tmp_path / "controller")
    session.ask_researcher("What is the sample design?")
    session.report_progress("I am checking the input columns.")
    session.ask_researcher("Remind me of the sample design?")
    assert backend.calls[0][0] == backend.calls[2][0]
    assert any(m["content"] == "The samples are paired." for m in backend.calls[2])
    assert "checking the input columns" in json.dumps(backend.calls[2])
    saved = json.loads((session.output / "persona.private.json").read_text())
    assert saved["profile"]["id"] == "PRIVATE_PROFILE" and saved["sha256"]
    assert "PRIVATE_PROFILE" not in (session.output / "public_input.json").read_text()
    assert "PRIVATE_PROFILE" not in (session.output / "events.jsonl").read_text()
    assert Researcher(episode, ScriptedBackend(), persona=persona).history == []
    assert persona.expertise.domain == "task"  # constructor did not mutate caller


def test_extractive_control_does_not_publish_persona_prose():
    backend = ScriptedBackend({"answer": "I prefer this", "fact_ids": ["study.sample"]})
    researcher = Researcher(episode_fixture(), backend, persona=Persona(), mode="extractive")
    assert researcher.ask("What is the study design?")["answer"] == episode_fixture().researcher.facts[0].text
    assert len(backend.calls) == 1


def test_offline_preview_cli(tmp_path, capsys):
    episode_path, config_path = tmp_path / "episode.json", tmp_path / "config.json"
    episode_path.write_text(episode_fixture().model_dump_json())
    config_path.write_text(json.dumps({"persona_router": {"defaults": {"role": {"seniority": "senior"}}}}))
    assert main(["persona", "--episode", str(episode_path), "--config", str(config_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["profile"]["role"]["seniority"] == "senior"
    assert "EVALUATOR_PRIVATE_SENTINEL" not in json.dumps(output)


@pytest.mark.parametrize("check", ['[]', {"supported": "true"}, {"supported": True, "extra": "unexpected"}])
def test_malformed_grounding_fails_closed(check):
    backend = ScriptedBackend({"answer": "Unvalidated preference", "fact_ids": []}, check)
    researcher = Researcher(episode_fixture(), backend, mode="grounded")
    reply = researcher.ask("What do you prefer?", topic="preferences")
    assert reply["answer"] == UNKNOWN
    assert reply["fallback"] == "invalid_reply_or_grounding_result"
