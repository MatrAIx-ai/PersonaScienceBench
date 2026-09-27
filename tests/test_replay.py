"""Fixed-agent replay: every arm sees the reference agent messages; only researcher output varies."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from personasciencebench.schema import Episode, EvaluatorSpec, Fact, Provenance, PublicContext, ResearcherContext
from personasciencebench.sciconv_runner import PERSONA_BOUNDARY

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/replay_fixed_agent.py"
spec = importlib.util.spec_from_file_location("replay_fixed_agent", SCRIPT)
replay = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = replay
spec.loader.exec_module(replay)

# Static text of LLMUserInterface.answer_clarification_question, SciConvBench 8d1528ed8 (context elided).
NATIVE = '''You are a User who knows the COMPLETE requirement for a task.

        The Agent only has an INCOMPLETE version and is asking clarification questions.
        You have access to the COMPLETE requirement and should answer based strictly on that.

        IMPORTANT GUIDELINES:
        1. Answer questions based on the COMPLETE user requirement.
        2. Be specific and provide concrete values if they exist in the COMPLETE requirement.
        3. If the complete requirement doesn't specify something, tell the agent: "Make a reasonable assumption based on best practices."
        4. Be consistent with previous clarifications.

        CONTEXT:
        COMPLETE REQUIREMENT: plate of width 2 m.

        CRITICAL INSTRUCTIONS:
        - Be concise.
        - Do not explain your reasoning.
        - Do not provide information not asked for.
        - Do not make up new constraints that aren't in the complete requirement.
        - Answer like a human user would.
        '''
NATIVE_USER = """
class LLMUserInterface:
    TEMPLATE = {template}
    def __init__(self, llm_service, incomplete_requirement, complete_requirement, log_file="conversation_log.txt"):
        self.llm, self.truth, self.log_file, self.history = llm_service, complete_requirement, log_file, []
    def answer_clarification_question(self, question):
        system = self.TEMPLATE.replace("plate of width 2 m.", self.truth) + " History: " + json.dumps(self.history)
        try:
            answer = self.llm.invoke("The Agent asks: " + question, system)
        except Exception:
            return "I am unable to answer that at this time."
        self.history.append([question, answer])
        with open(self.log_file, "a") as f:
            f.write("Q: " + question + "\\nA: " + answer + "\\n\\n")
        return answer
"""
ARMS = ["persona_off", "p1", "floor_a", "ceiling_a"]
PLAN = {"stage": "plan", "answer": "Plan A.", "evidence": "Inspected.", "assumptions": [], "uncertainties": [],
        "payload": {}, "artifacts": {}}
RESULT = {**PLAN, "stage": "result", "answer": "Result B."}


def episode(benchmark):
    return Episode(id=benchmark + "-task", benchmark=benchmark, source_task_id="t", study_id="s", domain="biology",
        source_revision="f", public=PublicContext(question="Compare conditions."),
        researcher=ResearcherContext(facts=[Fact(id="f1", topic="c", text="Width is 2 m.",
            source=Provenance(source_path="f", revision="f", locator="/c"), review_status="reviewed")]),
        evaluator=EvaluatorSpec(kind="fixture", version="fixture"))


def ref_decision(phase, action="continue", approve=False):
    return {"decision": {"action": action, "interaction": "next_task", "message": f"Ref {phase} words here.",
                         "evidence": "", "objectives_open": [], "fact_ids": [], "approve_approach": approve,
                         "phase": phase}, "policy_version": "x"}


def build_run(tmp_path, native_prompt=NATIVE):
    run = tmp_path / "run"
    tasks = [{"id": "sc", "slug": "sc1", "kind": "sciconv", "benchmark": "sciconvbench", "prepared": "unused"},
             {"id": "bx", "slug": "bx1", "kind": "python", "benchmark": "bixbench", "prepared": "unused"},
             {"id": "tb", "slug": "tb1", "kind": "terminal", "benchmark": "terminal", "prepared": "unused"}]
    jobs = [{**t, "arm": a, "key": a + "-" + t["slug"]} for a in ARMS for t in tasks]
    (run / "finished").mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({"tasks": tasks, "jobs": jobs}))
    for arm in ARMS:
        persona = {"enabled": False} if arm == "persona_off" else {"enabled": True, "id": arm, "system_prompt": f"I am {arm}."}
        (run / "configs" / arm).mkdir(parents=True)
        (run / "configs" / arm / "shared.json").write_text(json.dumps({"models": {"researcher": {"model": "m"}},
            "researcher": {}, "persona": persona, "collaboration": {"protocol": "active_researcher", "max_requests": 12,
                                                                     "volunteer_information": True}}))
    for task, case in (("sc", "sc"), ("bx", "bx"), ("tb", "tb")):
        controller = run / "episodes" / case / "controller"
        controller.mkdir(parents=True)
        (controller.parent / "result.json").write_text("{}")
        (run / "finished" / f"persona_off-{task}1.json").write_text(json.dumps(
            {"arm": "persona_off", "id": task, "result": str(controller.parent / "result.json"), "status": "scored"}))
    sc = run / "episodes/sc/controller"
    (sc / "episode.private.json").write_text(episode("sciconvbench").model_dump_json())
    events = [("researcher_question", {"question": "Q1?"}), ("researcher_reply", {"answer": "orig one"}),
              ("researcher_question", {"question": "Q2?"}), ("researcher_reply", {"answer": "orig two words"})]
    (sc / "events.jsonl").write_text("".join(json.dumps({"sequence": i, "type": t, "time": 0, "payload": p}) + "\n"
                                             for i, (t, p) in enumerate(events)))
    bx = run / "episodes/bx/controller"
    (bx / "episode.private.json").write_text(episode("bixbench").model_dump_json())
    history = [{"role": "assistant", "content": "Ref initial."},
               {"role": "user", "content": json.dumps({"question": "Which width?", "topic": None})},
               {"role": "assistant", "content": "Width is 2 m."},
               {"role": "user", "content": json.dumps({"agent_handoff": PLAN})},
               {"role": "assistant", "content": "Ref approve."},
               {"role": "user", "content": json.dumps({"agent_handoff": RESULT})},
               {"role": "assistant", "content": "Ref stop."}]
    audit = [ref_decision("initial_inspection"), {"question": "Which width?", "answer": "Width is 2 m."},
             ref_decision("approach_review", approve=True), ref_decision("result_review", "stop")]
    (bx / "researcher_history.private.json").write_text(json.dumps(history))
    (bx / "researcher_audit.private.json").write_text(json.dumps(audit))
    native = tmp_path / "native"
    native.mkdir()
    (native / "llm_user_interface.py").write_text(NATIVE_USER.format(template=repr(native_prompt)))
    return run, native, history


class Fake:
    def __init__(self):
        self.payloads = []

    def __call__(self, payload):
        self.payloads.append(payload)
        if payload.get("tools"):
            phase = json.loads(payload["messages"][0]["content"])["phase"]
            decision = {"action": "stop" if phase == "result_review" else "continue", "interaction": "next_task",
                        "message": "Replay decision text.", "evidence": "", "objectives_open": [], "fact_ids": ["f1"],
                        "approve_approach": phase == "approach_review"}
            message = {"content": None, "tool_calls": [{"function": {"name": "researcher_decision",
                                                                     "arguments": json.dumps(decision)}}]}
        else:
            message = {"content": "Reply to " + payload["messages"][1]["content"]}
        return {"choices": [{"message": message, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.01}}


def make(run, native, send, **kw):
    return replay.Replay(run, send=send, sciconv_root=native, **{
        "budget_usd": 10.0, "workers": 1, "preflight_fn": lambda m: {"researcher": {"supported_parameters": []}}, **kw})


def calls(run):
    return [json.loads(l) for l in (run / "replay/api_calls.jsonl").read_text().splitlines()]


def test_sciconv_questions_fixed_prompts_differ_only_by_identity(tmp_path):
    run, native, _ = build_run(tmp_path)
    summary = make(run, native, Fake()).execute()
    for arm in ("persona_off", "p1"):
        events = [json.loads(l) for l in (run / f"replay/{arm}/sc1/controller/events.jsonl").read_text().splitlines()]
        assert [e["payload"]["question"] for e in events if e["type"] == "researcher_question"] == ["Q1?", "Q2?"]
        assert (run / f"replay/{arm}/sc1/controller/episode.private.json").exists()
        assert "Q: Q2?" in (run / f"replay/{arm}/sc1/conversation_log.txt").read_text()
    assert not (run / "replay/floor_a").exists() and not (run / "replay/ceiling_a").exists()
    assert {s.get("arm") for s in summary["skipped"]} >= {"floor_a", "ceiling_a"}
    systems = {}
    for c in calls(run):
        if c["task"] == "sc":
            systems.setdefault(c["arm"], []).append(c["request"]["messages"][0]["content"])
    assert len(systems["persona_off"]) == 2
    assert systems["p1"] == [s + PERSONA_BOUNDARY + "I am p1." for s in systems["persona_off"]]
    arms = summary["benchmarks"]["sciconvbench"]["arms"]
    assert set(arms) == {"persona_off", "p1"} and arms["persona_off"]["delta_vs_reference_replay"]["mean_reply_words"] == 0
    assert summary["benchmarks"]["sciconvbench"]["reference_original"]["replies"] == 2
    assert "one-step counterfactual" in (run / "replay/REPLAY.md").read_text()


def test_active_replay_uses_reference_prefix_handoff_and_approval(tmp_path):
    run, native, history = build_run(tmp_path)
    summary = make(run, native, Fake()).execute()
    for arm in ("persona_off", "p1"):
        requests = [c["request"] for c in calls(run) if c["task"] == "bx" and c["arm"] == arm]
        prefixes = [[], history[:3] + [history[3]], history[:5] + [history[5]]]
        for k, (request, expected) in enumerate(zip(requests, prefixes)):
            system = json.loads(request["messages"][0]["content"])
            assert request["messages"][1:-1] == expected and system["remaining_requests"] == 12 - k
            assert ("identity" in system) == (arm == "p1")
        rows = [json.loads(l) for l in (run / f"replay/{arm}/bx1/decisions.jsonl").read_text().splitlines()]
        assert [(r["k"], r["phase"], r["action"], r["approve_approach"]) for r in rows] == [
            (0, "initial_inspection", "continue", False), (1, "approach_review", "continue", True),
            (2, "result_review", "stop", False)]
        assert (run / f"replay/{arm}/bx1/k2/researcher_history.private.json").exists()
    off = [json.loads(c["request"]["messages"][0]["content"]) for c in calls(run) if c["task"] == "bx" and c["arm"] == "persona_off"]
    p1 = [json.loads(c["request"]["messages"][0]["content"]) for c in calls(run) if c["task"] == "bx" and c["arm"] == "p1"]
    assert [{k: v for k, v in s.items() if k != "identity"} for s in p1] == off
    active = summary["benchmarks"]["bixbench"]
    assert active["arms"]["p1"]["approve_rate_at_approach_review"] == 1.0
    assert active["reference_self_replay_minus_original"]["mean_fact_ids_per_decision"] == 1.0
    assert any(s.get("task") == "tb" for s in summary["skipped"])


def test_budget_stop_then_resume_skips_written_units(tmp_path):
    run, native, _ = build_run(tmp_path)
    fake = Fake()
    first = make(run, native, fake, budget_usd=0.025).execute()
    assert first["budget_stopped"] and len(fake.payloads) == 3 and first["units"]["budget_stopped"] >= 1
    assert not any((run / "replay").glob("*/*.partial/replay.json"))
    done = {p.parent.parent.name + "/" + p.parent.name for p in (run / "replay").glob("*/*/replay.json")}
    second_fake = Fake()
    second = make(run, native, second_fake).execute()
    assert second["units"].get("existing") == len(done) and second["units"]["completed"] == 4 - len(done)
    third_fake = Fake()
    assert make(run, native, third_fake).execute()["units"] == {"existing": 4} and not third_fake.payloads


def test_dry_run_makes_no_calls_and_writes_nothing(tmp_path):
    run, native, _ = build_run(tmp_path)
    def boom(payload):
        raise AssertionError("dry run issued a model call")
    result = make(run, native, boom, dry_run=True, preflight_fn=boom).execute()
    assert result["dry_run"] and result["calls"] == 10 and result["prompt_tokens_estimate"] > 0
    assert not (run / "replay").exists()


def test_missing_cost_fails_without_prices(tmp_path):
    run, native, _ = build_run(tmp_path)
    def no_cost(payload):
        response = Fake()(payload)
        response["usage"].pop("cost")
        return response
    summary = make(run, native, no_cost, arms=["persona_off"]).execute()
    assert summary["units"] == {"failed": 2}
    priced = make(run, native, no_cost, arms=["persona_off"], price_in=1.0, price_out=2.0).execute()
    assert priced["units"] == {"completed": 2} and abs(priced["spent_usd"] - 5 * 2e-5) < 1e-12


def test_failed_prompt_edit_is_a_failed_unit(tmp_path):
    run, native, _ = build_run(tmp_path, NATIVE.replace("- Do not provide information not asked for.", "- Stay on topic."))
    fake = Fake()
    summary = make(run, native, fake, arms=["persona_off"]).execute()
    assert [p["task"] for p in summary["problems"] if p["status"] == "failed"] == ["sc"]
    assert summary["units"] == {"completed": 1, "failed": 1}
    assert not (run / "replay/persona_off/sc1").exists()
    assert not [p for p in fake.payloads if not p.get("tools")]
