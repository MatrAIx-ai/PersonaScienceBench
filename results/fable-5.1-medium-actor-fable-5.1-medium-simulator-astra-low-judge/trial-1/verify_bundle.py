#!/usr/bin/env python3
"""Independent semantic checks for the delivered trial. Offline; no inference."""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import re

from materialize_bundle import Bundle, attempt_key, check, sha, slot


def keyed(rows):
    result = {slot(row): row for row in rows}
    assert len(result) == len(rows) == 1000
    return result


def same_score(left, right):
    if left in ("", None) or right in ("", None):
        assert left in ("", None) and right in ("", None)
    else:
        assert math.isfinite(float(left)) and math.isfinite(float(right))
        assert math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)


def score(source, native, evaluation, status):
    if status == "missing_submission":
        assert native.get("status") == "missing_submission" or evaluation.get("status") == "missing_submission"
        return 0
    if status != "scored":
        return None
    metrics = evaluation.get("metrics", {})
    if source == "expbench":
        assert native["status"] == "completed"
        return (native.get("final") or native.get("initial"))["gated_coverage_mean"]
    assert evaluation["status"] == "scored"
    if source == "asibench":
        return 100 * metrics["score"] / metrics["max_score"]
    metric = {"bixbench": "correct", "discoverybench": "final_score", "sciconvbench": "FRR"}[source]
    return 100 * float(metrics[metric])


def disposition(source, native, evaluation, audit):
    terminal = [stop for stop in audit["unusual"] if stop["role"] != "judge"]
    assert len(terminal) <= 1
    if terminal:
        stop = terminal[0]
        if stop["stop_reason"] == "refusal":
            if stop["role"] == "actor":
                return "actor_refusal"
            assert stop["role"] == "researcher"
            phase = "pre_actor" if stop["prior_actor_responses"] == 0 else "mid_episode"
            assert phase == stop["refusal_phase"]
            return "simulator_refusal_" + phase
        assert stop["role"] == "actor" and stop["stop_reason"] == "max_tokens" and stop["cap"] == 32768
        return "actor_token_limit"
    if native.get("status") == "missing_submission" or evaluation.get("status") == "missing_submission":
        return "missing_submission"
    if source == "expbench":
        assert native["status"] == "completed"
        return "scored" if (native.get("final") or native.get("initial") or {}).get("gated_coverage_mean") is not None else "grading_pending"
    if evaluation.get("status") == "scored":
        return "scored"
    assert evaluation.get("status") == "error"
    assert (native.get("actor") or {}).get("submitted")
    return "grading_pending"


def safe_key(value):
    return (re.sub(r"[^A-Za-z0-9_.-]", "_", value).strip(".")[:100] or "episode") + "-" + sha(value.encode())[:12]


def native_case(run, row):
    prefix = safe_key(row["benchmark"] + ":" + row["task_id"])
    name = row["task_id"].replace("/", "__") if row["benchmark"] == "expbench" else prefix
    return run / "episodes" / prefix / row["arm"] / f'attempt-{row["attempt"]}' / "output" / name


def verify_judge_amendment(bundle, episodes):
    """Check portable evidence; full wire equality is a separate private-log audit."""
    recovery = "provenance/recovery/"
    sources = "provenance/recovery-source/"
    approval_bytes = bundle.raw(recovery + "judge_cap_approval.json")
    approval = json.loads(approval_bytes)
    assert approval["approved"] is True and approval["approver"] == "Robert"
    assert approval["remaining_native_judge_cap"] == 4096
    bindings = {
        "judge_cap_amendment_plan.json": recovery,
        "recover_judges_amended.py": sources,
        "recover_judges_v2.py": sources,
    }
    assert set(approval["approved_file_sha256"]) == set(bindings)
    for name, prefix in bindings.items():
        assert sha(bundle.raw(prefix + name)) == approval["approved_file_sha256"][name]
    bound_approval = {**approval, "approval_file_sha256": sha(approval_bytes)}
    plan = bundle.json(recovery + "judge_recovery_cap4096/plan.json")
    assert plan["approval"] == bound_approval
    assert plan["judge_model"] == "us.openai.gpt-6-astra" and plan["reasoning_effort"] == "low"
    assert plan["native_variable_relation_cap"] == 250 and plan["remaining_variable_relation_cap"] == 4096
    approved = {tuple(k) for k in approval["slots"]}
    assert len(approved) == len(approval["slots"]) == 7
    assert plan["slots"] == approval["slots"]
    outcomes = bundle.json(recovery + "judge_recovery_cap4096/results.json")
    assert len(outcomes) == 7 and {slot(row) for row in outcomes} == approved
    inputs = [
        bundle.json(path) for path in bundle.receipt["files"]
        if path.startswith(recovery + "judge_recovery_cap4096/") and path.endswith("/inputs.json")
    ]
    assert len(inputs) == 7 and {slot(row) for row in inputs} == approved
    for row in outcomes + inputs:
        assert row["budget_amendment"] == bound_approval and row["actor_rerun"] is False
        assert datetime.fromisoformat(row["created_at"]) >= datetime.fromisoformat(approval["received_at"])
        assert row["script_sha256"] == approval["approved_file_sha256"]["recover_judges_v2.py"]
    history = [
        row for row in bundle.jsonl("provenance/judge-recovery-history.jsonl")
        if row["cohort"] == "judge_recovery_cap4096"
    ]
    assert len(history) == 7 and {slot(row) for row in history} == approved
    input_map = {slot(row): row for row in inputs}
    outcome_map = {slot(row): row for row in outcomes}
    reused_count = fresh_count = transport_retries = 0
    for row in history:
        k = slot(row)
        assert row["status"] == outcome_map[k]["status"] == "recovered"
        assert row["evaluation"]["status"] == outcome_map[k]["evaluation"]["status"] == "scored"
        assert row["budget_amendment"] == bound_approval and row["actor_rerun"] is False
        assert row["evaluation"]["details"]["judge_recovery"]["caps_changed"] is True
        for field in ("episode_sha256", "submission_sha256", "artifact_hashes",
                      "original_result_sha256", "source_api_log_sha256", "config_sha256"):
            assert row[field] == input_map[k][field] == outcome_map[k][field]
        receipts = row["replay_receipts"]
        cached = [item for item in receipts if not item["new_model_call"]]
        fresh = [item for item in receipts if item["new_model_call"]]
        calls = row["fresh_native_calls"]
        assert [item["call"] for item in receipts] == list(range(1, len(receipts) + 1))
        assert len(cached) == row["cached_calls"] == row["reused_calls"]
        assert len(fresh) == len(calls) == row["fresh_calls"]
        for receipt, call in zip(fresh, calls):
            assert receipt["native_max_output_tokens"] == 250
            assert receipt["transmitted_max_output_tokens"] == call["cap"] == 4096
            assert receipt["transmitted_request_sha256"] == call["request_sha256"]
            assert call["requested_model"] == call["actual_model"] == "us.openai.gpt-6-astra"
            assert call["reasoning"]["effort"] == "low" and call["status"] == "completed"
            assert isinstance(call["transport_retries"], int) and call["transport_retries"] >= 0
            transport_retries += call["transport_retries"]
        reused_count += len(cached)
        fresh_count += len(fresh)
    assert reused_count == 28 and fresh_count == 14 and transport_retries == 0
    report = bundle.json(recovery + "judge_cap4096_verification.json")
    assert report["verifier_sha256"] == sha(bundle.raw(sources + "verify_judge_amendment.py"))
    assert report["approved_slots"] == report["recovered_slots"] == 7 and report["actor_reruns"] == 0
    assert report["actual_judge_model"] == "us.openai.gpt-6-astra" and report["reasoning_effort"] == "low"
    assert report["original_prefix_calls_reused"] == reused_count and report["fresh_calls"] == fresh_count
    assert report["fresh_call_cap"] == 4096 and report["amended_helper_calls"] == 14
    assert report["transport_retries"] == transport_retries
    for k, row in episodes.items():
        directory = row["judge_recovery"]
        expected = ("approved_helper_cap4096_recovery" if k in approved else
                    "original_cap_recovery" if directory else "native_configuration")
        assert (directory == "judge_recovery_cap4096") == (k in approved)
        assert row["judge_budget_cohort"] == expected
    return {"approved_slots": 7, "recovered_slots": 7,
            "original_prefix_calls_reused": reused_count, "fresh_calls": fresh_count,
            "transport_retries": transport_retries}


def verify(bundle, native_run=None):
    report = bundle.verify()
    episodes = keyed(bundle.csv("episodes.csv"))
    finals = keyed(bundle.json("traces/final-results.json"))
    metrics = keyed(bundle.jsonl("evaluations/metrics.jsonl"))
    canonical = keyed(bundle.jsonl("provenance/canonical_attempts.jsonl"))
    traces = keyed(bundle.jsonl("traces/shared-events.jsonl"))
    tools = keyed(bundle.jsonl("traces/tool-events.jsonl"))
    indexes = keyed(bundle.csv("traces/shared-events-index.csv"))
    inputs = keyed(bundle.jsonl("grading_inputs/manifest.jsonl"))
    audits = keyed(bundle.json("provenance/native-call-audit.json")["slots"])
    attempts = bundle.jsonl("provenance/all-attempts.jsonl")
    submissions = bundle.jsonl("submissions/manifest.jsonl")
    attempts_map = {attempt_key(row): row for row in attempts}
    assert len(attempts_map) == len(attempts) == len(submissions) == 1010
    assert {attempt_key(row) for row in submissions} == set(attempts_map)
    assert Counter(str(row["attempt"]) for row in episodes.values()) == {"1": 990, "2": 10}
    for collection in (finals, metrics, canonical, traces, tools, indexes, inputs, audits):
        assert collection.keys() == episodes.keys()
    for k, row in episodes.items():
        final, metric, selected = finals[k], metrics[k], canonical[k]
        for other in (final, metric, selected, traces[k], tools[k], indexes[k], inputs[k], audits[k]):
            assert attempt_key(other) == attempt_key(row)
        for other in (final, metric, selected):
            assert other["derived_status"] == row["derived_status"]
        evaluation = final["grading_overlay"] or final["native_result"].get("evaluation") or {}
        assert metric["evaluation"] == evaluation
        assert row["derived_status"] == disposition(row["benchmark"], final["native_result"], evaluation, audits[k])
        expected_score = score(row["benchmark"], final["native_result"], evaluation, row["derived_status"])
        for actual in (row["score_0_100"], final["score_0_100"], metric["score_0_100"], selected["score"]):
            same_score(actual, expected_score)
        if expected_score is not None:
            assert not row["null_reason"] and 0 <= expected_score <= 100
        else:
            assert row["null_reason"] == row["derived_status"]
        sensitivity = 0 if row["derived_status"] in ("actor_refusal", "actor_token_limit") else expected_score
        same_score(row["actor_terminal_zero_sensitivity"], sensitivity)
        if row["derived_status"] == "missing_submission":
            assert row["submitted"] == "False"
        submission = submissions[selected["submission_manifest_line"] - 1]
        assert submission["canonical"] and attempt_key(submission) == attempt_key(row)
        attempt = attempts_map[attempt_key(row)]
        assert attempt["canonical"] and attempt["state"] == final["runner_state"]
        assert selected["native_result_sha256"] == attempt["native_result_sha256"]
        if "result.json" in submission["files"]:
            assert selected["native_result_sha256"] == submission["files"]["result.json"]["sha256"]
        assert not audits[k]["mismatches"] and audits[k]["log_present"]
        assert audits[k]["source_api_sha256"] == selected["source_api_sha256"]
        assert len(selected["native_stops"]) <= 1
        assert traces[k]["events"] == attempt["shared_events"]
        assert tools[k]["events"] == attempt["tool_events"]
        assert len(traces[k]["events"]) == int(indexes[k]["event_count"])
        assert (bool(traces[k]["events"]) and not indexes[k]["empty_reason"]) or (
            not traces[k]["events"] and indexes[k]["empty_reason"])
        assert inputs[k]["prepared_key"] == safe_key(row["benchmark"] + ":" + row["task_id"])
        if row["benchmark"] == "sciconvbench" and "/disambiguation/" in row["task_id"] and expected_score is not None:
            assert "entity_recovery" in metric["evaluation"]["metrics"]
    assert not set(report["counts"]) - {
        "scored", "missing_submission", "actor_refusal", "simulator_refusal_pre_actor",
        "simulator_refusal_mid_episode", "actor_token_limit", "grading_pending"}
    overlay_outcomes = {}
    for directory in ("judge_recovery", "judge_recovery_cap4096"):
        path = f"provenance/recovery/{directory}/results.json"
        if path in bundle.receipt["files"]:
            for recovery in bundle.json(path):
                overlay_outcomes[slot(recovery)] = recovery
    for k, recovery in overlay_outcomes.items():
        assert episodes[k]["judge_recovery_status"] == recovery["status"]
        if recovery.get("evaluation") is not None:
            # These native grade records contain paths; compare the numerical/error result fields.
            evaluation = finals[k]["grading_overlay"]
            assert evaluation["status"] == recovery["evaluation"]["status"]
            assert evaluation["metrics"] == recovery["evaluation"]["metrics"]
    amendment = verify_judge_amendment(bundle, episodes)
    ordered_traces = bundle.jsonl("traces/shared-events.jsonl")
    for row in indexes.values():
        assert attempt_key(ordered_traces[int(row["jsonl_line"]) - 1]) == attempt_key(row)
    for row in attempts:
        if not row["canonical"]:
            assert row["native_result"] is None
            assert row.get("startup_failure_log") and row["process_log_sha256"]
            assert not row["shared_events"] and not row["tool_events"]
    frozen = bundle.json("grading_inputs/frozen/manifest.json")
    compressed = bundle.raw("grading_inputs/frozen/preparation.json.gz")
    check(compressed, frozen, "frozen preparation")
    payload = json.loads(gzip.decompress(compressed))
    assert sha(bundle.raw("provenance/selection.csv")) == frozen["selection_sha256"]
    assert set(payload["files"]) == set(frozen["metadata_sha256"])
    for name, text in payload["files"].items():
        assert sha(text.encode()) == frozen["metadata_sha256"][name]
    assert sha(payload["exp_source"].encode()) == frozen["exp_source_sha256"]
    for row in inputs.values():
        assert any(name.startswith(row["prepared_key"] + "/") for name in payload["files"])
    checked_files, checked_artifacts = 0, 0
    if native_run:
        for row in submissions:
            case = native_case(native_run, row)
            for name, metadata in row["files"].items():
                check((case / name).read_bytes(), metadata, name)
                checked_files += 1
            if row["submission"]:
                original = json.loads((case / "controller/submission.json").read_bytes())
                assert set(original.get("artifacts", {})) == set(row["artifacts"])
                for name, metadata in row["artifacts"].items():
                    check(Path(original["artifacts"][name]).read_bytes(), metadata, name)
                    checked_artifacts += 1
            events_path = case / "controller/events.jsonl"
            if not events_path.exists():
                events_path = case / "events.jsonl"
            if events_path.exists():
                original_events = [json.loads(line) for line in events_path.read_bytes().splitlines()]
                exported = attempts_map[attempt_key(row)]
                assert sha(events_path.read_bytes()) == exported["source_event_sha256"]
                shared = [e for e in original_events if e["type"] not in ("actor_command", "actor_command_result")]
                action = [e for e in original_events if e["type"] in ("actor_command", "actor_command_result")]
                assert shared == exported["shared_events"] and action == exported["tool_events"]
        before = keyed(bundle.json("provenance/recovery/all_states.before.json"))
        for k, original in before.items():
            row = episodes[k]
            root = native_case(native_run, row).parents[2]
            current = json.loads((root / "state.json").read_text())
            if current["attempt"] == original["attempt"]:
                assert current == original
            else:
                saved = root / f'attempt-{original["attempt"]}' / "state_snapshot.json"
                assert json.loads(saved.read_text()) == original
    report.update(semantic_verified=True, frozen_metadata_files=len(payload["files"]),
                  native_files_compared=checked_files, native_artifacts_compared=checked_artifacts,
                  original_event_text_verified=bool(native_run),
                  judge_amendment=amendment,
                  metric_contract="Pinned TEAM_HANDOFF section 4 and native final/initial EXP selection.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--native-run", type=Path, help="Optional original run for byte-for-byte source comparisons")
    args = parser.parse_args()
    print(json.dumps(verify(Bundle(args.bundle), args.native_run), indent=2))


if __name__ == "__main__":
    main()
