"""Calibration arms: reordered twins, neutral identities, floor/ceiling researchers, truthful history, noise floor."""

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from personasciencebench.collaboration import (ActiveResearcher, CollaborationConfig, ScriptedResearcher,
                                               SCRIPTED_REPLY)
from personasciencebench.persona import Persona
from personasciencebench.researcher import Researcher
from personasciencebench.runner import researcher_factory
from personasciencebench.schema import Episode, EvaluatorSpec, Fact, Provenance, PublicContext, ResearcherContext
from personasciencebench.sciconv_runner import MUTE_REPLY, Service, researcher_system_prompt
from test_knowledge_persona_separation import NATIVE, DecisionBackend, decision

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
TRUTH_SCICONV = ("- What you say about this conversation must be true: never claim you already told the agent "
                 "something that is not in the incomplete requirement or in your earlier answers.")
TRUTH_ACTIVE = ("What you say about this collaboration must be true: never claim you already gave the agent "
                "information that is not in the project brief or your earlier messages. ")


def load(name):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


runner = load("run_persona_benchmarks")


def profile_text(i):
    return (f"## Who you are\n\nYou are researcher {i}.\n\n## Habits\n\n- first {i}\n- second {i}\n- third {i}\n"
            f"- fourth {i}\n\n## Style\n\n- terse {i}\n- warm {i}\n")


def make_root(root):
    cohort = root / "data/persona_case_study/full_persona_v2"
    cohort.mkdir(parents=True)
    rows = []
    for i in range(30):
        cid = f"candidate_{i:03d}"
        text = profile_text(i)
        (cohort / f"{cid}.md").write_text(text)
        rows.append({"candidate_id": cid, "prompt": f"{cid}.md", "prompt_sha256": hashlib.sha256(text.encode()).hexdigest()})
    (cohort / "manifest.json").write_text(json.dumps({"profiles": rows, "selection": "fixture", "diversity": "fixture"}))
    (root / "configs/expbench").mkdir(parents=True)
    shutil.copy(REPO / "configs/conversion-v2-two.json", root / "configs/conversion-v2-two.json")
    shutil.copy(REPO / "configs/expbench/conversion-v2-two.toml", root / "configs/expbench/conversion-v2-two.toml")
    shutil.copytree(REPO / "configs/persona_controls", root / "configs/persona_controls")
    prepared = root / "prepared/full-persona-v2-five"
    prepared.mkdir(parents=True)
    cases = [{"episode_id": f"{b}:task{j}", "benchmark": b, "assets_ready": True, "package": "x"}
             for b in ["asibench", "bixbench", "discoverybench", "sciconvbench"] for j in range(5)]
    (prepared / "pilot_manifest.json").write_text(json.dumps({"cases": cases}))
    (root / "data/design_catalog").mkdir(parents=True)
    (root / "data/design_catalog/tasks.jsonl").write_text(
        "".join(json.dumps({"task_id": f"paper{k}/task{m}"}) + "\n" for k in range(6) for m in range(2)))
    (root / "scripts").mkdir()
    (root / "scripts/run_persona_benchmarks.py").write_text("fixture\n")
    (root / "src").mkdir()


@pytest.fixture
def build(tmp_path, monkeypatch):
    root = tmp_path / "root"
    make_root(root)
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "__file__", str(root / "scripts/run_persona_benchmarks.py"))

    def run(**flags):
        output = tmp_path / "out"
        if output.exists():
            shutil.rmtree(output)
        manifest = runner.build(output, **flags)
        config = lambda arm, name: json.loads((output / "configs" / arm / name).read_text())
        return manifest, config, root
    return run


# 1. reorder_bullets

def test_reorder_bullets_permutes_bullets_within_sections_only():
    text = profile_text(1)
    out = runner.reorder_bullets(text, "candidate_001")
    assert out != text and sorted(out.split("\n")) == sorted(text.split("\n"))
    assert out == runner.reorder_bullets(text, "candidate_001")
    before, after = text.split("\n"), out.split("\n")
    for old, new in zip(before, after):
        if not old.startswith("- "):
            assert new == old
    sections = lambda lines: [sorted(l for l in part.split("\n") if l.startswith("- "))
                              for part in "\n".join(lines).split("\n#")]
    assert sections(after) == sections(before)


# 2. build()

def test_default_build_has_only_controls_and_cohort(build):
    manifest, config, _ = build()
    arms = {j["arm"] for j in manifest["jobs"]}
    assert arms == {"persona_off"} | {f"candidate_{i:03d}" for i in range(30)}
    assert "twins" not in manifest and "bounds_skipped" not in manifest
    assert config("candidate_000", "shared.json")["collaboration"].get("truthful_history", False) is False
    manifest, _, _ = build(control_reps=2)
    assert {j["arm"] for j in manifest["jobs"]} == {"persona_off", "persona_off_r2"} | {f"candidate_{i:03d}" for i in range(30)}


def test_twins_are_reordered_copies_of_recorded_sources(build):
    manifest, config, root = build(twins=2)
    twins = sorted(a for a in {j["arm"] for j in manifest["jobs"]} if a.endswith("__reordered"))
    assert len(twins) == 2 and sorted(manifest["twins"]) == twins
    for arm in twins:
        source = manifest["twins"][arm]
        assert arm == source + "__reordered"
        original = (root / "data/persona_case_study/full_persona_v2" / f"{source}.md").read_text()
        prompt = config(arm, "shared.json")["persona"]["system_prompt"]
        assert prompt == runner.reorder_bullets(original, source) and prompt != original
        assert sum(j["arm"] == arm for j in manifest["jobs"]) == 25


def test_neutral_arms_carry_the_neutral_texts(build):
    manifest, config, root = build(neutral_arms=True)
    assert {"neutral_a", "neutral_b"} <= {j["arm"] for j in manifest["jobs"]}
    for arm in ["neutral_a", "neutral_b"]:
        persona = config(arm, "shared.json")["persona"]
        assert persona["enabled"] and persona["system_prompt"] == (root / "configs/persona_controls" / f"{arm}.txt").read_text()
        assert config(arm, "exp.json")["persona"] == persona


def test_bound_arms_set_policy_and_skip_expbench(build):
    manifest, config, _ = build(bound_arms=True)
    for arm, policy in [("floor_mute", "mute"), ("ceiling_oracle", "oracle")]:
        assert config(arm, "shared.json")["collaboration"]["researcher_policy"] == policy
        assert "researcher_policy" not in config(arm, "exp.json")["collaboration"]
        jobs = [j for j in manifest["jobs"] if j["arm"] == arm]
        assert len(jobs) == 20 and not any(j["kind"] == "exp" for j in jobs)
    assert config("candidate_000", "shared.json")["collaboration"].get("researcher_policy", "llm") == "llm"
    assert "expbench" in manifest["bounds_skipped"]


def test_truthful_history_reaches_every_arm(build):
    manifest, config, _ = build(twins=1, neutral_arms=True, bound_arms=True, truthful_history=True)
    arms = {j["arm"] for j in manifest["jobs"]}
    assert len(arms) == 1 + 30 + 1 + 2 + 2
    for arm in arms:
        assert config(arm, "shared.json")["collaboration"]["truthful_history"] is True
        assert config(arm, "exp.json")["collaboration"]["truthful_history"] is True


# 3. ScriptedResearcher

class ForbiddenBackend:
    def complete(self, *a, **k):
        raise AssertionError("scripted researcher called the backend")

    def complete_decision(self, *a, **k):
        raise AssertionError("scripted researcher called the backend")


def fact(key, text):
    return Fact(id=key, topic=key, text=text, source=Provenance(source_path="f", revision="f", locator="/" + key),
                review_status="reviewed")


def episode():
    return Episode(id="fixture-task", benchmark="bixbench", source_task_id="native-id", study_id="study",
        domain="biology", source_revision="fixture", public=PublicContext(question="Compare the two conditions."),
        researcher=ResearcherContext(facts=[fact("conditions", "Two conditions."), fact("units", "Values are in mM.")]),
        evaluator=EvaluatorSpec(kind="fixture", version="fixture"))


def handoff(stage, payload=None):
    return {"stage": stage, "answer": "A finding.", "evidence": "Ran the analysis.", "assumptions": [],
            "uncertainties": [], "payload": payload or {"executed_analysis": True}, "artifacts": {}}


def session(tmp_path):
    return SimpleNamespace(event=lambda *a: None, output=tmp_path)


def scripted(policy):
    return ScriptedResearcher(episode(), ForbiddenBackend(), persona=Persona(enabled=False), policy=policy)


def test_mute_researcher_sequence(tmp_path):
    researcher = scripted("mute")
    first = researcher.decide(session(tmp_path), None, 5)
    assert (first.action, first.interaction, first.fact_ids) == ("continue", "initial_request", [])
    assert "Two conditions." not in first.message and researcher.disclosed == {}
    plan = researcher.decide(session(tmp_path), handoff("plan"), 4)
    assert plan.action == "continue" and plan.approve_approach and researcher.approach_approved
    result = researcher.decide(session(tmp_path), handoff("result"), 3)
    assert (result.action, result.interaction) == ("stop", "conclude")
    assert researcher.disclosed == {}


def test_oracle_initial_request_lists_and_discloses_every_fact(tmp_path):
    researcher = scripted("oracle")
    first = researcher.decide(session(tmp_path), None, 5)
    assert "- Two conditions." in first.message and "- Values are in mM." in first.message
    assert first.fact_ids == ["conditions", "units"] and set(researcher.disclosed) == {"conditions", "units"}


def test_contract_rejection_gets_a_revision_until_one_request_remains(tmp_path):
    rejection = {"reason": "result does not satisfy the submission contract",
                 "missing": ["artifacts.analysis", "payload.executed_analysis=true"]}
    researcher = scripted("mute")
    researcher.decide(session(tmp_path), None, 5)
    researcher.decide(session(tmp_path), handoff("plan"), 4)
    rejected = handoff("result", {"executed_analysis": False, "controller_contract_check": rejection})
    revise = researcher.decide(session(tmp_path), rejected, 3)
    assert (revise.action, revise.interaction) == ("continue", "refine_analysis")
    assert "artifacts.analysis, payload.executed_analysis=true" in revise.message
    last = researcher.decide(session(tmp_path), rejected, 1)
    assert (last.action, last.interaction) == ("stop", "conclude")


@pytest.mark.parametrize("policy", ["mute", "oracle"])
def test_scripted_ask_returns_fixed_reply_and_discloses_nothing(policy):
    researcher = scripted(policy)
    reply = researcher.ask("What units are the values in?", "units")
    assert reply["answer"] == SCRIPTED_REPLY and reply["fact_ids"] == [] and reply["fallback"] == "scripted_" + policy
    assert researcher.disclosed == {} and researcher.questions == 1


def test_scripted_policy_must_be_mute_or_oracle():
    with pytest.raises(ValueError):
        scripted("llm")


# 4. researcher_factory

def test_researcher_factory_per_policy():
    assert researcher_factory(None) == (Researcher, {})
    llm = CollaborationConfig(truthful_history=True).model_dump()
    assert researcher_factory(llm) == (ActiveResearcher, {"unrestricted_knowledge": False, "embody_identity": False,
                                                          "truthful_history": True})
    for policy in ["mute", "oracle"]:
        cls, options = researcher_factory(CollaborationConfig(researcher_policy=policy).model_dump())
        assert cls is ScriptedResearcher and options["policy"] == policy
        assert set(options) == {"unrestricted_knowledge", "embody_identity", "truthful_history", "policy"}


# 5. SciConv

def test_scripted_service_never_calls_the_client():
    class Client:
        def completion(self, messages):
            raise AssertionError("mute service called the client")
    service = Service(Client(), persona_text="You are a terse PI.", prompt_options={"truthful_history": True})
    service.script(MUTE_REPLY)
    assert service.invoke("What is the width?", NATIVE) == MUTE_REPLY
    assert service.invoke("And the height?", NATIVE) == MUTE_REPLY
    assert service.stats["scripted_replies"] == 2 and service.stats["total_calls"] == 0
    assert "scripted_replies" not in Service(Client()).stats


def test_sciconv_truthful_history_line():
    assert TRUTH_SCICONV not in researcher_system_prompt(NATIVE)
    assert TRUTH_SCICONV not in researcher_system_prompt(NATIVE, unrestricted_knowledge=True, embody_identity=True,
                                                         volunteer_information=True)
    for options in [{}, dict(unrestricted_knowledge=True, embody_identity=True, volunteer_information=True)]:
        prompt = researcher_system_prompt(NATIVE, truthful_history=True, persona_text="You are a terse PI.", **options)
        assert prompt.count(TRUTH_SCICONV) == 1 and "- Answer like a human user would." in prompt


# 6. ActiveResearcher truthful_history

@pytest.mark.parametrize("truthful", [False, True])
def test_active_researcher_truth_sentence(tmp_path, truthful):
    backend = DecisionBackend([decision(interaction="initial_request")])
    researcher = ActiveResearcher(episode(), backend, persona=Persona(enabled=False), truthful_history=truthful)
    researcher.decide(session(tmp_path), None, 5)
    instructions = json.loads(backend.requests[-1][0]["content"])["instructions"]
    assert instructions.count(TRUTH_ACTIVE) == (1 if truthful else 0)
    assert researcher.persona_metadata["truthful_history"] is truthful


# 7. ExpBench guard

def test_expbench_rejects_scripted_policy():
    from expbench.collaboration import initialize
    stub = SimpleNamespace(config=SimpleNamespace(collaboration=SimpleNamespace(researcher_policy="mute")))
    with pytest.raises(ValueError, match="researcher_policy must be 'llm'"):
        initialize(stub)


# 8. noise_floor / report

GRADES = {"persona_off": (0, 0), "persona_off_r2": (1, 0), "candidate_001": (1, 1), "candidate_002": (0.5, 0),
          "candidate_001__reordered": (1, 0), "neutral_a": (0, 0), "neutral_b": (1, 0),
          "floor_mute": (0, 0), "ceiling_oracle": (1, 1)}


def test_report_noise_floor_and_reference_split(tmp_path):
    jobs = []
    (tmp_path / "finished").mkdir()
    for arm, grades in GRADES.items():
        for task, grade in zip(["bixbench:t1", "bixbench:t2"], grades):
            key = f"{arm}-{task[-2:]}"
            result = tmp_path / "episodes" / key / "result.json"
            result.parent.mkdir(parents=True)
            result.write_text(json.dumps({"status": "scored", "evaluation": {"metrics": {"grade": grade}}}))
            job = {"id": task, "kind": "python", "benchmark": "bixbench", "arm": arm, "key": key,
                   "elapsed_seconds": 1.0, "status": "scored", "result": str(result)}
            jobs.append(job)
            (tmp_path / "finished" / f"{key}.json").write_text(json.dumps(job))
    (tmp_path / "manifest.json").write_text(json.dumps({"jobs": jobs}))
    runner.report(tmp_path)
    comparison = json.loads((tmp_path / "comparison.json").read_text())
    floor = comparison["noise_floor"]["bixbench"]
    assert floor["metric"] == "grade"
    assert floor["control_sd"] == pytest.approx(0.3536, abs=1e-3) and floor["control_sd_tasks"] == 2
    assert floor["placebo_band"] == pytest.approx([-0.5, 0.5])
    assert floor["personas"] == 2 and floor["personas_outside_band"] == 1
    assert floor["floor_mean"] == 0 and floor["ceiling_mean"] == 1
    assert floor["twin_minus_source"]["mean"] == pytest.approx(-0.5)
    assert floor["neutral_b_minus_a"]["mean"] == pytest.approx(0.5)
    assert {p["arm"] for p in comparison["paired_differences"]} == {"candidate_001", "candidate_002"}
    assert {p["arm"] for p in comparison["reference_differences"]} == {
        "candidate_001__reordered", "neutral_a", "neutral_b", "floor_mute", "ceiling_oracle"}
    assert "## Noise floor" in (tmp_path / "REPORT.md").read_text()


# 9. report_top_persona_deviations

def test_top_deviation_rankings_exclude_reference_arms():
    top = load("report_top_persona_deviations")
    episodes = [{"arm": arm, "task": "s1", "benchmark": "sciconvbench", "status": "scored", "metrics": {"FRR": value}}
                for arm, value in [("persona_off", 0.0), ("a", 1.0), ("a__reordered", 1.0), ("neutral_a", 0.5),
                                   ("floor_mute", 0.0), ("ceiling_oracle", 1.0)]]
    rankings, _ = top.benchmark_rankings(episodes, ["a", "a__reordered", "neutral_a", "floor_mute", "ceiling_oracle"])
    assert [r["persona"] for r in rankings["sciconvbench"]["rankings"]] == ["a"]
