"""Offline checks for the post-hoc persona visibility and SciConv per-item scorers."""

import importlib.util
import json
import re
import sys
import threading
from pathlib import Path

import pytest

from personasciencebench import run_io

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vis = load("judge_persona_visibility")
items_mod = load("score_sciconv_items")

PERSONAS = ["cand_a", "cand_b", "cand_c", "cand_d", "cand_e"]
ARMS = ["persona_off", *PERSONAS, "cand_a__reordered", "neutral_a"]
ENTITIES = ["Applied load: P = 30000 N", "Beam length: L = 2 m", "Material: steel"]


class FakeClient:
    def __init__(self, reply, cost=0.01):
        self.reply, self.cost, self.calls = reply, cost, 0
        self.lock = threading.Lock()

    def completion(self, messages):
        with self.lock:
            self.calls += 1
        usage = {"prompt_tokens": 10, "completion_tokens": 5}
        if self.cost is not None:
            usage["cost"] = self.cost
        return {"choices": [{"message": {"content": self.reply(messages)}}], "usage": usage}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def events(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps({"sequence": i, "type": t, "time": 0.0, "payload": p}) + "\n"
                            for i, (t, p) in enumerate(rows)))


def sciconv_events(arm):
    return [("initial_request", {"message": "Simulate a beam."}),
            ("researcher_question", {"question": "What load is applied?"}),
            ("researcher_reply", {"answer": f"{arm} says: the load is P = 30000 N, and the beam is 2 m long."}),
            ("researcher_question", {"question": "Anything else?"}),
            ("researcher_reply", {"answer": f"{arm} says: nothing more."}),
            ("final_specification", {"answer": "Beam, P = 30000 N, steel."})]


def build_run(root, replay_arm="neutral_a"):
    run = root / "run"
    jobs = []
    for arm in ARMS:
        persona = ({"enabled": False} if arm == "persona_off" else
                   {"enabled": True, "id": arm, "system_prompt": f"PROFILE {arm.replace('__reordered', '')}"})
        write(run / "configs" / arm / "shared.json",
              {"persona": persona, "models": {"judge": {"model": "fake/judge", "reasoning_effort": "none"}}})
        for task, benchmark in [("sciconv:t1", "sciconvbench"), ("asi:t2", "asibench")]:
            key = f"{arm}-{benchmark[:6]}"
            jobs.append({"arm": arm, "id": task, "key": key, "kind": "x", "benchmark": benchmark})
            case = run / "episodes" / key / "case"
            reference = {"mode": "disambiguation", "native_row": {"missing_entities": ENTITIES}}
            write(case / "controller/episode.private.json",
                  {"id": task, "benchmark": benchmark, "evaluator": {"reference": reference}})
            replay = arm == replay_arm and benchmark == "sciconvbench"
            if benchmark == "sciconvbench":
                events(case / "controller/events.jsonl", sciconv_events(arm)[:-1] if replay else sciconv_events(arm))
            else:
                decisions = [] if arm == "cand_e" else [
                    ("researcher_decision", {"message": f"{arm} approves the plan."}),
                    ("agent_handoff", {"stage": "plan"}),
                    ("researcher_decision", {"message": f"{arm} wants more tests."})]
                events(case / "controller/events.jsonl", decisions)
            if replay:
                continue
            write(case / "result.json", {"status": "scored"})
            write(case / "llm_judge_disambiguation_score.json",
                  {"score": "2/3", "recovered_entities": [ENTITIES[0], ENTITIES[2]], "still_missing_entities": [ENTITIES[1]]})
            write(run / "finished" / f"{key}.json",
                  {**jobs[-1], "status": "scored", "result": str(case / "result.json")})
    write(run / "manifest.json", {"jobs": jobs})
    return run


def args(module, run, **kw):
    base = ["--run", str(run), "--budget-usd", str(kw.pop("budget", 10)), "--workers", str(kw.pop("workers", 1))]
    return module.parser().parse_args(base + kw.pop("extra", []))


def target_reply(messages, choose="target"):
    user = messages[1]["content"]
    text = user.split("<RESEARCHER_TEXT>\n")[1]
    arm = re.match(r"(\S+) ", text).group(1).replace("__reordered", "")
    label = re.search(rf"^([A-Z]):\nPROFILE {arm}$", user, re.M)
    choice = label.group(1) if label and choose == "target" else "X"
    evidence = text.split(":")[0] if choose != "bad_quote" else "not in the text"
    return f"<FINAL_JSON>{json.dumps({'choice': choice, 'confidence': 2, 'evidence': evidence})}</FINAL_JSON>"


def test_load_run_includes_replay_only_case(tmp_path):
    run = build_run(tmp_path)
    records = {(r["arm"], r["benchmark"]): r for r in run_io.load_run(run)}
    assert len(records) == 2 * len(ARMS)
    replay = records[("neutral_a", "sciconvbench")]
    assert replay["status"] is None and replay["case"].name == "case"
    assert not (replay["case"] / "result.json").exists()
    assert [t["question"] for t in run_io.sciconv_turns(replay["events"])] == ["What load is applied?", "Anything else?"]
    assert run_io.researcher_messages(records[("cand_b", "asibench")]) == ["cand_b approves the plan.", "cand_b wants more tests."]
    assert records[("cand_a__reordered", "asibench")]["kind"] == "twin"
    assert run_io.default_judge(run)["model"] == "fake/judge"


def test_candidates_deterministic_with_target_once():
    profiles = {a: f"PROFILE {a}" for a in PERSONAS}
    record = {"key": "cand_a__reordered-sciconv", "arm": "cand_a__reordered", "kind": "twin"}
    target, options = vis.candidates(record, profiles, 4)
    assert target == "cand_a" and list(options) == ["A", "B", "C", "D"]
    assert list(options.values()).count("cand_a") == 1 and len(set(options.values())) == 4
    assert vis.candidates(record, profiles, 4) == (target, options)
    neutral = vis.candidates({"key": "neutral_a-x", "arm": "neutral_a", "kind": "neutral"}, profiles, 4)
    assert neutral[0] is None and len(set(neutral[1].values())) == 4


def test_binomial_p_known_cases():
    assert vis.binomial_p(2, 4, 0.5) == pytest.approx(11/16)
    assert vis.binomial_p(0, 7, 0.25) == pytest.approx(1.0)
    assert vis.binomial_p(3, 3, 0.25) == pytest.approx(0.25**3)


def test_visibility_hits_x_evidence_and_no_text(tmp_path):
    run = build_run(tmp_path)
    vis.run(args(vis, run), client=FakeClient(target_reply))
    rows = {(r["arm"], r["benchmark"]): r for r in run_io.jsonl(run / "persona_visibility/results.jsonl")}
    assert ("persona_off", "sciconvbench") not in rows
    hit = rows[("cand_a__reordered", "sciconvbench")]
    assert hit["status"] == "judged" and hit["hit"] and hit["evidence_ok"] and hit["chosen_arm"] == "cand_a"
    assert rows[("cand_e", "asibench")]["status"] == "no_text"
    neutral = rows[("neutral_a", "asibench")]
    assert neutral["hit"] is None and neutral["choice"] == "X"
    summary = json.loads((run / "persona_visibility/summary.json").read_text())
    assert summary["persona"]["overall"]["hits"] == 9 and summary["persona"]["overall"]["n"] == 9
    assert summary["neutral"]["x_share"] == 1.0 and (run / "persona_visibility/SUMMARY.md").exists()

    miss = FakeClient(lambda m: target_reply(m, "bad_quote"))
    vis.run(args(vis, run, extra=["--force"]), client=miss)
    rows = run_io.jsonl(run / "persona_visibility/results.jsonl")
    judged = [r for r in rows if r["status"] == "judged"]
    assert judged and not any(r["evidence_ok"] for r in judged)
    x = FakeClient(lambda m: target_reply(m, "X"))
    vis.run(args(vis, run, extra=["--force"]), client=x)
    summary = json.loads((run / "persona_visibility/summary.json").read_text())
    assert summary["persona"]["overall"]["hits"] == 0 and summary["persona"]["overall"]["x_share"] == 1.0


def test_malformed_json_retried_once_then_parse_failure(tmp_path):
    run = build_run(tmp_path)
    client = FakeClient(lambda m: "not json")
    vis.run(args(vis, run), client=client)
    rows = run_io.jsonl(run / "persona_visibility/results.jsonl")
    judged = [r for r in rows if r["status"] not in ("no_text", "no_profile")]
    assert judged and all(r["status"] == "parse_failure" for r in judged)
    assert client.calls == 2 * len(judged)


def test_budget_stops_calls_and_missing_cost_fails(tmp_path):
    run = build_run(tmp_path)
    client = FakeClient(target_reply, cost=0.1)
    report = vis.run(args(vis, run, budget=0.25), client=client)
    assert client.calls == 3 and report["budget_stopped"]
    assert len(run_io.jsonl(run / "judge_persona_visibility/api_calls.jsonl")) == 3
    free = FakeClient(target_reply, cost=None)
    with pytest.raises(RuntimeError, match="no usage cost"):
        vis.run(args(vis, run, extra=["--force"]), client=free)
    assert free.calls == 1
    priced = FakeClient(target_reply, cost=None)
    vis.run(args(vis, run, extra=["--force", "--price-in", "1", "--price-out", "2"]), client=priced)
    assert priced.calls > 1


def test_dry_run_makes_no_calls(tmp_path):
    run = build_run(tmp_path)
    client = FakeClient(target_reply)
    report = vis.run(args(vis, run, extra=["--dry-run"]), client=client)
    assert client.calls == 0 and report["calls"] > 0 and report["estimated_input_tokens"] > 0
    assert not (run / "persona_visibility").exists()
    report = items_mod.run(args(items_mod, run, extra=["--dry-run"]), client=client)
    assert client.calls == 0 and report["calls"] == 2 * len(ARMS)
    assert not list(run.rglob("item_scores.json"))


def attribution_reply(messages):
    user = messages[1]["content"]
    if "What load is applied?" in user:
        value = {"asked": ["E0"], "conveyed": [
            {"card_id": "E0", "level": "full", "evidence": "the load is P = 30000 N"},
            {"card_id": "E1", "level": "full", "evidence": "the beam is 2 m long"}]}
    else:
        value = {"asked": [], "conveyed": []}
    return f"<FINAL_JSON>{json.dumps(value)}</FINAL_JSON>"


def test_item_derivation_two_turn_dialogue(tmp_path):
    run = build_run(tmp_path)
    record = next(r for r in run_io.load_run(run) if r["arm"] == "cand_b" and r["benchmark"] == "sciconvbench")
    caller = run_io.JudgeCaller(run, "score_sciconv_items", {"model": "fake/judge"}, budget_usd=1,
                                client=FakeClient(attribution_reply))
    scores = items_mod.score_episode(record, caller)
    load, length, material = scores["items"]
    assert (load["asked"], load["delivered"], load["unasked_delivered"], load["recovered"], load["grounded"]) == (True, True, False, True, True)
    assert (length["asked"], length["delivered"], length["unasked_delivered"], length["recovered"]) == (False, True, True, False)
    assert (material["delivered"], material["partial"], material["recovered"], material["silent"]) == (False, False, True, True)
    assert scores["recovery"]["item_match_mismatch"] is False and caller.calls == 2

    replay = next(r for r in run_io.load_run(run) if r["arm"] == "neutral_a" and r["benchmark"] == "sciconvbench")
    replay_scores = items_mod.score_episode(replay, caller)
    assert all(i["recovered"] is None and i["silent"] is None for i in replay_scores["items"])


def test_resume_skips_scored_episodes(tmp_path):
    run = build_run(tmp_path)
    client = FakeClient(attribution_reply)
    items_mod.run(args(items_mod, run), client=client)
    assert client.calls == 2 * len(ARMS)
    summary = json.loads((run / "sciconv_items/summary.json").read_text())
    assert summary["scored"] == len(ARMS)
    assert summary["persona_minus_control"]["cand_a"]["delivered"]["mean_delta"] == 0
    again = FakeClient(attribution_reply)
    items_mod.run(args(items_mod, run), client=again)
    assert again.calls == 0

    judge = FakeClient(target_reply)
    vis.run(args(vis, run), client=judge)
    first = len(run_io.jsonl(run / "persona_visibility/results.jsonl"))
    judge_again = FakeClient(target_reply)
    vis.run(args(vis, run), client=judge_again)
    assert judge_again.calls == 0 and len(run_io.jsonl(run / "persona_visibility/results.jsonl")) == first
