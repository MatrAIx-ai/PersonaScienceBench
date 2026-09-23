#!/usr/bin/env python3
"""Recompute offline evidence for the score-gap audit; never calls a model."""

import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = ["neurips2024/97649/0", "neurips2024/94328/5",
         "neurips2024/94391/7", "iclr2024/18447/7", "iclr2024/18865/4"]
RUNS = ["original-input-o3mini-20260922", "pilot-o3mini-20260922"]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = [json.loads(s) for s in (ROOT / "data/exp_bench/tasks.jsonl").read_text().splitlines()]
    by_id = {r["task_id"]: r for r in rows}
    counts = [sum(len(v) for v in r["reference_design"].values())
              for r in rows if r["reference_design_schema_valid"]]
    evidence = {
        "kind": "offline-score-gap-audit",
        "paid_calls": 0,
        "reference_group_key_count_caveat": "Dictionary keys, not atomic criteria or measured task difficulty",
        "all_valid_references": {"n": len(counts), "mean_keys": statistics.mean(counts),
                                 "median_keys": statistics.median(counts)},
        "tasks": [], "runs": {},
    }
    for tid in TASKS:
        row = by_id[tid]
        c, p, idx = tid.split("/")
        raw_path = ROOT / f"data/exp_bench/raw/upstream/tasks/{c}/{p}.json"
        raw = read(raw_path)["questions"][int(idx)]
        released = ROOT / f"external/expbench-history/vendor/curie-db1b1f5/benchmark/exp_bench/outputs/logs/{c}/{p}/{p}_complete_final.json"
        assert read(released)["questions"][int(idx)] == raw, tid
        evidence["tasks"].append({"task_id": tid, "type": row["task_type"],
            "reference_keys": sum(len(v) for v in row["reference_design"].values()),
            "raw_task_matches_vendored_release": True,
            "raw_source_sha256": digest(raw_path)})
    for run in RUNS:
        entries = []
        for tid in TASKS:
            slug = tid.replace("/", "__")
            directory = ROOT / "runs" / run / slug
            calls = [json.loads(s) for s in (directory / "api_calls.jsonl").read_text().splitlines()]
            requests = [r for r in calls if r.get("phase") == "request" and r.get("role") == "actor"]
            result = read(directory / "result.json")
            assert result["status"] == "completed" and not result["mock"]
            grades = ROOT / "runs/expbench/original-judge-diagnostic-20260922" / run / slug
            grade = read(grades / "grade.json")
            monitor = read(ROOT / "runs/expbench/original-monitor-20260922" / run / slug / "result.json")
            entry = {"task_id": tid, "status": result["status"],
                "actor_calls": len(requests),
                "tools": [t["function"]["name"] for t in requests[0]["payload"]["tools"]],
                "adapted_score": result["design_score"], "original_prompt_score": grade["design_score"],
                "monitor_result": monitor,
                "design_sha256": digest(directory / "design.json"),
                "request_log_sha256": digest(directory / "api_calls.jsonl")}
            if run.startswith("original-input"):
                c, p, idx = tid.split("/")
                raw = read(ROOT / f"data/exp_bench/raw/upstream/tasks/{c}/{p}.json")["questions"][int(idx)]
                first_user = next(m["content"] for m in requests[0]["payload"]["messages"] if m["role"] == "user")
                supplied = json.loads(first_user)
                context = json.loads(supplied["context"])
                assert supplied["question"] == raw.get("question", raw.get("hypothesis"))
                assert context == {"method": raw["method"], "agent_instructions": raw.get("agent_instructions", "")}
                assert set(supplied) == {"question", "context", "documents", "question_budget", "actor_step_budget"}
                assert supplied["question_budget"] == 0
                assert len(requests) == 1
                entry["original_task_fields_verified_in_actual_actor_request"] = True
            judge_calls = [json.loads(s) for s in (grades / "api_calls.jsonl").read_text().splitlines()]
            judge_request = next(r["payload"] for r in judge_calls if r.get("phase") == "request")
            entry["replay_judge_roles"] = [m["role"] for m in judge_request["messages"]]
            entry["replay_response_format"] = judge_request.get("response_format")
            entries.append(entry)
        evidence["runs"][run] = {"tasks": entries,
            "adapted_mean": statistics.mean(e["adapted_score"] for e in entries),
            "original_prompt_mean": statistics.mean(e["original_prompt_score"] for e in entries)}
    output = ROOT / "reports/expbench/score_gap_audit.json"
    output.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Verified {len(TASKS)} source matches, 5 actual static actor inputs, and 10 completed run records.")
    print(f"Wrote {output.relative_to(ROOT)}; no model calls made.")


if __name__ == "__main__":
    main()
