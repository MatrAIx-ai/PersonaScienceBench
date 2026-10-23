"""Export the Fable trial without inference or mutation of native run records."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

from audit_native_calls import audit, case_path, safe

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
REPO = BASE / "checkout"
RUN = BASE / "actor32768/run"
DELIVERY_REPO = BASE / "delivery-checkout"
SLUG = "fable-5.1-medium-actor-fable-5.1-medium-simulator-astra-low-judge"
OUT = DELIVERY_REPO / "results" / SLUG / "trial-1"
ARMS = ["persona_off", "candidate_155", "candidate_001", "candidate_003", "candidate_046"]
SOURCES = ["asibench", "bixbench", "discoverybench", "expbench", "sciconvbench"]
SHARED_TYPES = {
    "researcher_decision", "agent_handoff", "actor_finished",
    "collaboration_candidate_selected", "final_submission", "researcher_question",
    "researcher_reply", "initial_request", "final_specification", "design_submission",
    "result_handoff_rejected", "collaboration_missing_submission",
}
PRIVATE_TYPES = {"actor_command", "actor_command_result"}
SECRET = re.compile(rb"(?:sk-(?:proj-|or-v1-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9_]{24,}|github_pat_[A-Za-z0-9_]{24,}|(?:AKIA|ASIA)[A-Z0-9]{16}|Bearer [A-Za-z0-9._-]{20,})")
PRIVATE_KEYS = {"_native_response", "_native_request", "_responses_response", "_responses_request",
                "reasoning_content", "encrypted_content", "thinking_blocks"}
LIMIT = 24 * 1024 * 1024


def read(path):
    return json.loads(path.read_text())


def raw_json(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def key(row):
    return row.get("benchmark", row.get("source")), row["task_id"], row["arm"]


def slot_fields(row, attempt):
    return {"benchmark": row["source"], "task_id": row["task_id"], "arm": row["arm"],
            "trial": 1, "attempt": attempt}


def checked(raw, label):
    if SECRET.search(raw):
        raise ValueError(f"Possible credential in {label}; inspect privately before export")
    return raw


def clean(value):
    """Rebase metadata paths only. Original shared text and artifacts are unchanged."""
    if isinstance(value, dict):
        if PRIVATE_KEYS.intersection(value):
            raise ValueError("Private model payload reached the public export boundary")
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str):
        for old, new in [(str(RUN), "${RUN}"), (str(REPO), "${REPO}"),
                         (str(BASE), "${CAMPAIGN}")]:
            value = value.replace(old, new)
        return value
    return value


def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(checked(raw_json(value), name))


def write_csv(name, rows):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    checked(path.read_bytes(), name)


def write_jsonl(name, rows):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        for row in rows:
            raw = (json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n").encode()
            stream.write(checked(raw, name))


def split_large(path, logical_files):
    if path.stat().st_size <= LIMIT:
        return
    raw = path.read_bytes()
    encoded = gzip.compress(raw, mtime=0) if path.suffix in (".json", ".jsonl") else raw
    encoding = "gzip" if encoded is not raw else "identity"
    parts = []
    for offset in range(0, len(encoded), LIMIT):
        suffix = ".gz" if encoding == "gzip" else ""
        part = path.with_name(path.name + suffix + f".part{offset // LIMIT:03d}")
        block = encoded[offset:offset + LIMIT]
        part.write_bytes(block)
        parts.append({"path": str(part.relative_to(OUT)), "bytes": len(block), "sha256": sha(block)})
    logical_files[str(path.relative_to(OUT))] = {"bytes": len(raw), "sha256": sha(raw),
                                                "encoding": encoding, "encoded_sha256": sha(encoded),
                                                "reconstruction": "Concatenate parts in listed order, then gunzip only when encoding is gzip.", "parts": parts}
    path.unlink()


def native(row):
    entries = row.get("native_results") or []
    return next((n for n in entries if n.get("episode_id") or n.get("task_id")), {})


def native_score(source, result, evaluation):
    metrics = evaluation.get("metrics", {})
    if result.get("status") == "missing_submission" or evaluation.get("status") == "missing_submission":
        return 0.0
    if source == "expbench":
        # TEAM_HANDOFF section 4: already 0–100; final/initial is the native rule.
        return (result.get("final") or result.get("initial") or {}).get("gated_coverage_mean")
    if evaluation.get("status") != "scored":
        return None
    if source == "asibench":
        return 100 * metrics["score"] / metrics["max_score"]
    if source == "bixbench":
        return 100 * float(metrics["correct"])
    if source == "discoverybench":
        return 100 * metrics["final_score"]
    if source == "sciconvbench":
        return 100 * metrics["FRR"]
    raise ValueError(source)


def shared_events(case, *, tools=False):
    path = case / "controller/events.jsonl"
    if not path.exists():
        path = case / "events.jsonl"
    events, original_count = [], 0
    if not path.exists():
        return events, None, 0
    for line in path.open():
        original_count += 1
        event = json.loads(line)
        kind = event["type"]
        if kind not in SHARED_TYPES | PRIVATE_TYPES:
            raise ValueError(f"Unreviewed event type {kind}")
        if (kind in PRIVATE_TYPES) != tools:
            continue
        # Check the schema, but preserve every shared string byte-for-byte.
        clean(event)
        events.append(event)
    return events, sha(path.read_bytes()), original_count


class Artifacts:
    def __init__(self):
        self.archives, self.added = {}, {}
        (OUT / "submissions").mkdir(parents=True, exist_ok=True)

    def add(self, source, raw, member):
        checked(raw, member)
        if source not in self.archives:
            self.archives[source] = tarfile.open(OUT / "submissions" / f"{source}.tar.gz", "w:gz")
            self.added[source] = {}
        digest = sha(raw)
        if member in self.added[source]:
            assert self.added[source][member] == digest
        else:
            info = tarfile.TarInfo(member)
            info.size, info.mode, info.mtime = len(raw), 0o600, 0
            self.archives[source].addfile(info, io.BytesIO(raw))
            self.added[source][member] = digest
        return {"archive": f"submissions/{source}.tar.gz", "member": member,
                "bytes": len(raw), "sha256": digest}

    def close(self):
        for archive in self.archives.values():
            archive.close()


def collect_attempt(row, attempt, artifacts):
    case = case_path(row, attempt)
    slot = slot_fields(row, attempt)
    prefix = f'{safe(row["source"] + ":" + row["task_id"])}/{row["arm"]}/attempt-{attempt}'
    record = {**slot, "submission": None, "artifacts": {}, "files": {}}
    submission = case / "controller/submission.json"
    names = ["result.json", "evaluation.json", "actor_result.json",
             "controller/public_input.json", "public_input.json",
             "controller/submission.json", "controller/submission_hashes.json",
             "initial_design.json", "final_design.json", "generated_prompt.txt",
             "conversation_log.txt", "execution.jsonl", "runtime.json", "usage.json",
             "repository_provenance.json",
             "llm_judge_intent_score.json", "llm_judge_disambiguation_chat_score.json",
             "llm_judge_disambiguation_score.json", "llm_judge_inconsistency_score.json",
             "llm_judge_inconsistency_chat_score.json"]
    for phase in ("initial_evaluation", "final_evaluation"):
        names += [f"{phase}/{name}" for name in
                  ("summary.json", "monitor.json", "sample-1.json", "sample-2.json",
                   "sample-3.json", "coverage_prompt.txt")]
    for name in names:
        path = case / name
        if path.is_file():
            raw = path.read_bytes()
            if name.endswith(".json"):
                clean(json.loads(raw))
            elif name.endswith(".jsonl"):
                for line in raw.splitlines():
                    clean(json.loads(line))
            record["files"][name] = artifacts.add(row["source"], raw, f"{prefix}/{name}")
    if submission.exists():
        data = read(submission)
        record["submission"] = record["files"]["controller/submission.json"]
        expected = read(case / "controller/submission_hashes.json") if (case / "controller/submission_hashes.json").exists() else {}
        assert set(expected) == set(data.get("artifacts", {}))
        for name, original in data.get("artifacts", {}).items():
            path = Path(original)
            if path.is_symlink() or not path.resolve().is_relative_to(case.resolve()):
                raise ValueError("Submission artifact escapes its controller-owned case")
            raw = path.read_bytes()
            assert sha(raw) == expected[name]
            record["artifacts"][name] = artifacts.add(row["source"], raw, "objects/" + sha(raw))
    record["initial_design"] = record["files"].get("initial_design.json")
    record["final_design"] = record["files"].get("final_design.json")
    return record


def export(checkpoint=False):
    OUT.mkdir(parents=True, exist_ok=True)
    # This directory is generated by this exporter; no user-authored files are removed.
    logical_path = OUT / "logical_files.json"
    if logical_path.exists():
        for entry in read(logical_path).values():
            for part in entry["parts"]:
                (OUT / part["path"]).unlink(missing_ok=True)
    originals = read(ROOT / "all_states.before.json")
    assert len(originals) == 1000 and len({key(r) for r in originals}) == 1000
    failures = {key(r): r for r in read(ROOT / "failure_inventory.json")}
    original_audits = {key(r): r for r in read(ROOT / "native_call_audit.json")["slots"]}
    grades, recovery_outcomes = {}, {}
    for directory in ["judge_recovery", "judge_recovery_cap4096"]:
        results_path = ROOT / directory / "results.json"
        if not results_path.exists():
            continue
        outcomes = read(results_path)
        assert len(outcomes) == (9 if directory == "judge_recovery" else 7)
        for grade in outcomes:
            recovery_outcomes[key(grade)] = (directory, grade)
            if grade.get("evaluation") is not None:
                grades[key(grade)] = (directory, grade)
    records, finals, traces, trace_index, metrics, canonical = [], [], [], [], [], []
    tool_traces = []
    all_attempts, submissions, grade_inputs, audits, recovery_records = [], [], [], [], []
    artifacts = Artifacts()
    for original in originals:
        k = key(original)
        slot_base = RUN / "episodes" / safe(original["source"] + ":" + original["task_id"]) / original["arm"]
        current = read(slot_base / "state.json")
        startup = failures.get(k, {}).get("category") == "startup_throttled"
        selected = current if startup else original
        if not startup:
            assert current == original, f"An immutable original state changed: {k}"
        if not checkpoint:
            assert selected["status"] not in ("running", "pending"), f"Still running: {k}"
        attempt = selected["attempt"]
        case = case_path(original, attempt)
        result = native(selected)
        info = audit(selected, attempt) if startup else original_audits[k]
        assert not info["mismatches"], f"Model/config mismatch: {k}"
        audits.append(info)
        status = "infrastructure_unresolved"
        evaluation = result.get("evaluation") or {}
        grade_record = grades.get(k)
        if grade_record:
            directory, grade = grade_record
            assert grade["actor_attempt"] == attempt
            assert sha((case / "controller/submission.json").read_bytes()) == grade["submission_sha256"]
            assert sha((case / "result.json").read_bytes()) == grade["original_result_sha256"]
            evaluation = grade["evaluation"]
            recovery_records.append(clean({"recovery_directory": directory, **grade}))
        # A recorded judge error must not mask a completed actor submission.
        model_stops = [entry for entry in info["unusual"] if entry["role"] != "judge"]
        assert len(model_stops) <= 1, f"Multiple terminal model stops require review: {k}"
        stop = model_stops[0] if model_stops else None
        score = None
        if stop:
            if stop["stop_reason"] == "refusal":
                status = ("actor_refusal" if stop["role"] == "actor"
                          else "simulator_refusal_" + stop["refusal_phase"])
            elif stop["stop_reason"] == "max_tokens" and stop["role"] == "actor":
                status = "actor_token_limit"
            else:
                status = "model_response_error"
        elif selected["status"] == "finished" or grade_record:
            score = native_score(original["source"], result, evaluation)
            if score is not None:
                status = "missing_submission" if (result.get("status") == "missing_submission"
                          or evaluation.get("status") == "missing_submission") else "scored"
            else:
                status = "grading_pending"
        elif (result.get("actor") or {}).get("submitted") and evaluation.get("status") == "error":
            status = "grading_pending"
        if score is not None:
            assert 0 <= score <= 100
        slot = slot_fields(original, attempt)
        selection_rule = ("first native attempt after audited startup throttle" if startup else
                          "first native attempt after original pilot timeout-schema startup repair" if original["attempt"] > 1 else
                          "original campaign canonical attempt, fixed before recovery")
        submission_row = None
        submission_line = None
        for attempt_dir in sorted(slot_base.glob("attempt-*"), key=lambda p: int(p.name.split("-")[1])):
            if not attempt_dir.is_dir():
                continue
            number = int(attempt_dir.name.split("-")[1])
            attempt_record = collect_attempt(original, number, artifacts)
            attempt_record["canonical"] = number == attempt
            submissions.append(attempt_record)
            if number == attempt:
                submission_row = attempt_record
                submission_line = len(submissions)
            native_path = case_path(original, number) / "result.json"
            state_path = attempt_dir / "state_snapshot.json"
            state = (read(state_path) if state_path.exists() else
                     current if number == attempt and startup else
                     original if number == original["attempt"] else None)
            if number < attempt:
                assert not native_path.exists(), f"A discarded scientific attempt exists: {k}"
                earlier = audit(original, number)
                assert not earlier["calls"], f"An earlier attempt reached inference: {k}"
            original_events, event_hash, original_count = shared_events(case_path(original, number))
            original_tools, _, _ = shared_events(case_path(original, number), tools=True)
            all_attempts.append({**slot_fields(original, number), "canonical": number == attempt,
                                 "state": clean(state), "native_result": clean(read(native_path)) if native_path.exists() else None,
                                 "native_result_sha256": sha(native_path.read_bytes()) if native_path.exists() else None,
                                 "shared_events": original_events, "tool_events": original_tools,
                                 "source_event_sha256": event_hash,
                                 "source_event_count": original_count})
            process_log = attempt_dir / "process.log"
            if process_log.exists():
                all_attempts[-1]["process_log_sha256"] = sha(process_log.read_bytes())
                if not native_path.exists() and number < attempt:
                    all_attempts[-1]["startup_failure_log"] = clean(process_log.read_text())
        assert submission_row is not None
        submitted = bool(submission_row["submission"] or submission_row["initial_design"]
                         or submission_row["final_design"] or
                         submission_row["files"].get("generated_prompt.txt"))
        events, event_hash, original_count = shared_events(case)
        tool_events, _, _ = shared_events(case, tools=True)
        tool_traces.append({**slot, "events": tool_events, "source_sha256": event_hash,
                            "note": "Recorded command actions/results only; no private actor reasoning or raw API payloads."})
        empty_reason = "" if events else ("No shared event was recorded before " + status)
        traces.append({**slot, "events": events, "empty_reason": empty_reason,
                       "source_sha256": event_hash, "source_event_count": original_count})
        trace_index.append({**slot, "jsonl_line": len(traces), "event_count": len(events),
                            "source_sha256": event_hash or "", "empty_reason": empty_reason})
        actor = result.get("actor") or {}
        collaboration = actor.get("collaboration") or {}
        null_reason = "" if score is not None else status
        last_recovery = recovery_outcomes.get(k)
        recovery = last_recovery[1] if last_recovery else {}
        row = {**slot, "study_id": original["study_id"], "family": original["family"],
               "subfield": original["subfield"], "task_family_id": original["task_family_id"],
               "runner_status": selected["status"], "native_status": result.get("status", ""),
               "evaluation_status": evaluation.get("status", "native_exp" if original["source"] == "expbench" else ""),
               "derived_status": status, "submitted": submitted, "score_0_100": score,
               "native_score": ((result.get("final") or result.get("initial") or {}).get("gated_coverage_mean")
                                 if original["source"] == "expbench" else
                                 evaluation.get("metrics", {}).get({"asibench": "score", "bixbench": "correct",
                                     "discoverybench": "final_score", "sciconvbench": "FRR"}[original["source"]])),
               "null_reason": null_reason, "actor_terminal_zero_sensitivity": 0 if status in ("actor_refusal", "actor_token_limit") else score,
               "native_stop_reason": stop["stop_reason"] if stop else "",
               "terminal_role": stop["role"] if stop else "",
               "actor_calls": actor.get("actor_calls", result.get("actor_calls", "")),
               "researcher_requests": result.get("researcher_requests", collaboration.get("researcher_requests", "")),
               "termination": collaboration.get("termination", result.get("collaboration_termination", "")),
               "judge_recovery": grade_record[0] if grade_record else "",
               "judge_budget_cohort": ("approved_helper_cap4096_recovery" if grade_record and grade_record[0] == "judge_recovery_cap4096"
                                       else "original_cap_recovery" if grade_record else "native_configuration"),
               "judge_recovery_status": recovery.get("status", ""),
               "judge_reused_calls": recovery.get("reused_calls", ""),
               "judge_fresh_calls": recovery.get("fresh_calls", ""),
               "judge_overlay_rule": "Latest recovery evaluation (may be an error); a later recovery error without an evaluation is retained separately." if last_recovery else "",
               "selection_rule": selection_rule}
        records.append(row)
        metrics.append({**slot, "derived_status": status, "score_0_100": score, "null_reason": null_reason,
                        "evaluation": clean(evaluation),
                        "exp_native_grade": clean(result.get("final") or result.get("initial")) if original["source"] == "expbench" else None})
        native_path = case / "result.json"
        canonical.append({**slot, "canonical_attempt_id": attempt, "selection_rule": selection_rule,
                          "original_status": original["status"], "derived_status": status,
                          "original_canonical_attempt": original["attempt"], "native_stop": stop,
                          "native_stops": model_stops, "judge_stops": [s for s in info["unusual"] if s["role"] == "judge"],
                          "score": score, "score_basis": "native mapping with explicit judge overlay" if score is not None else "pending disposition",
                          "native_result_sha256": sha(native_path.read_bytes()) if native_path.exists() else None,
                          "source_api_sha256": info.get("source_api_sha256"), "submission_manifest_line": submission_line})
        finals.append({**slot, "derived_status": status, "runner_state": clean(selected),
                       "native_result": clean(result), "grading_overlay": clean(evaluation) if grade_record else None,
                       "latest_judge_recovery": clean(recovery) if last_recovery else None,
                       "score_0_100": score, "null_reason": null_reason,
                       "submission_manifest": "submissions/manifest.jsonl",
                       "submission_key": slot, "canonical_manifest": "provenance/canonical_attempts.jsonl"})
        grade_inputs.append({**slot, "prepared_key": safe(original["source"] + ":" + original["task_id"]),
                             "frozen_preparation": "grading_inputs/frozen/preparation.json.gz",
                             "restore_script": "scripts/restore_main_preparation.py in the pinned repository",
                             "submission_key": slot, "source_manifest": "provenance/sources.json",
                             "grader_eligible": submitted, "derived_status": status,
                             "note": "Simulator refusal and actor terminal scoring require maintainer disposition." if stop else ""})
    artifacts.close()
    write_csv("episodes.csv", records)
    write("traces/final-results.json", finals)
    write_jsonl("traces/shared-events.jsonl", traces)
    write_jsonl("traces/tool-events.jsonl", tool_traces)
    write_csv("traces/shared-events-index.csv", trace_index)
    write_jsonl("evaluations/metrics.jsonl", metrics)
    write_jsonl("evaluations/judge-recovery.jsonl", recovery_records)
    write_jsonl("provenance/canonical_attempts.jsonl", canonical)
    write_jsonl("provenance/all-attempts.jsonl", all_attempts)
    write_jsonl("submissions/manifest.jsonl", submissions)
    write_jsonl("grading_inputs/manifest.jsonl", grade_inputs)
    write("provenance/native-call-audit.json", {"slots": audits, "note": "Private content excluded; native wire models, efforts, limits, stops and usage audited."})
    write("provenance/original-states.json", clean(originals))
    counts = Counter(r["derived_status"] for r in records)
    write("delivery.json", {
        "status": "partial_collection_with_terminal_model_outcomes",
        "expected_slots": 1000, "recorded_slots": len(records),
        "configuration_verified": True, "counts": dict(counts),
        "numeric_scores": sum(r["score_0_100"] is not None for r in records),
        "scored_numeric": counts.get("scored", 0),
        "missing_submission_zero": counts.get("missing_submission", 0),
        "additional_actor_zero_sensitivity_slots": counts.get("actor_refusal", 0) + counts.get("actor_token_limit", 0),
        "canonical_attempts": dict(Counter(str(r["attempt"]) for r in records)),
        "attempt_records": len(all_attempts),
        "collection_complete": False,
        "remaining_decisions": ["Actor refusal/cap scoring", "Pre-actor and mid-episode simulator refusals as terminal collection outcomes"] +
                              ([f'{counts["grading_pending"]} judge grades remain pending.'] if counts.get("grading_pending") else []),
        "judge_cap_amendment_state": ("run" if (ROOT / "judge_recovery_cap4096/results.json").exists() else
                                     "approved_not_run" if (ROOT / "judge_cap_approval.json").exists() else "not_approved"),
        "grading_pending": counts.get("grading_pending", 0),
        "infrastructure_unresolved": counts.get("infrastructure_unresolved", 0),
        "checkpoint": checkpoint,
    })
    logical_files = {}
    for path in list(OUT.rglob("*")):
        if path.is_file() and path.name not in ("bundle_manifest.json", "logical_files.json"):
            split_large(path, logical_files)
    write("logical_files.json", logical_files)
    print(json.dumps({"output": str(OUT), "counts": dict(counts), "attempts": len(all_attempts),
                      "logical_files_split": list(logical_files)}, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", action="store_true")
    export(parser.parse_args().checkpoint)
