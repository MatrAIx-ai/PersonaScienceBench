#!/usr/bin/env python3
"""Analyze saved DiscoveryBench batches without running actors or judges."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from personasciencebench.interaction_metrics import (
    VERSION, analyze_case, paired_summary, read_json,
)

ROOT = Path(__file__).resolve().parents[1]


def analyze(run_roots: list[Path], manifest: dict) -> tuple[dict, list[dict]]:
    rows, packets, seen = [], [], set()
    tasks = {task["task_id"]: task for task in manifest["tasks"]}
    if len(tasks) != len(manifest["tasks"]):
        raise ValueError("Duplicate task IDs in the study manifest")
    if len({root.name for root in run_roots}) != len(run_roots):
        raise ValueError("Batch directory names must be unique")
    for root in run_roots:
        summaries = sorted(root.glob("**/summary.json"))
        if not summaries:
            raise ValueError(f"No completed condition summaries under {root}")
        for summary_path in summaries:
            relative = summary_path.relative_to(root)
            if len(relative.parts) < 2:
                raise ValueError("A batch must contain condition subdirectories")
            condition = relative.parts[0]
            config = read_json(summary_path.parent / "config.json")
            summary = read_json(summary_path)
            paths = list(summary_path.parent.glob("*/result.json"))
            case_files = {read_json(p)["episode_id"]: p for p in paths}
            if len(paths) != len(case_files):
                raise ValueError("Duplicate episode IDs in case files")
            expected = [r["episode_id"] for r in summary["cases"]]
            if len(expected) != len(set(expected)) or set(expected) != set(case_files):
                raise ValueError("Condition summary and case files disagree")
            for episode_id in sorted(expected):
                path = case_files[episode_id]
                if path.resolve() in seen:
                    raise ValueError("A run was supplied more than once")
                seen.add(path.resolve())
                row, packet = analyze_case(path.parent, config, condition=condition, batch=root.name)
                if row["task_id"] not in tasks:
                    raise ValueError(f"Task outside the declared study panel: {row['task_id']}")
                row["case_locator"] = path.parent.relative_to(root).as_posix()
                row["subfield"] = tasks[row["task_id"]]["subfield"]
                row["analysis_family"] = tasks[row["task_id"]]["analysis_family"]
                rows.append(row)
                if packet is not None:
                    packets.append(packet)
    tracking = []
    for task in manifest["tasks"]:
        selected = [r for r in rows if r["task_id"] == task["task_id"]]
        tracking.append({**task, "observed_attempts": len(selected),
                         "observed_status_counts": dict(Counter(r["status"] for r in selected)),
                         "observed_conditions": sorted({r["condition"] for r in selected}),
                         "local_result_tracking": "observed" if selected else "not_run_in_supplied_batches"})
    report = {"metric_version": VERSION, "benchmark": "discoverybench", "episodes": rows,
              "task_tracking": tracking, "paired_scores": paired_summary(rows),
              "analysis_policy": {"missing_submission": "analysis score zero; no fabricated native grade",
                                  "infrastructure_and_evaluator_errors": "unscored; counted and excluded from paired means",
                                  "repeat_summary": "mean and sample SD; no best-of selection",
                                  "ask_f1": "not applicable: no validated blocker registry",
                                  "semantic_metrics": "pending evidence-backed annotation",
                                  "character_unit": "Unicode code points, including whitespace"}}
    return report, packets


def write_report(output: Path, report: dict):
    output.mkdir(parents=True, exist_ok=False)
    (output / "metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    rows = report["episodes"]
    flat = []
    for row in rows:
        flat.append({**{k: row[k] for k in ("batch", "condition", "case_locator", "task_id", "study_id", "status", "analysis_score", "submitted", "elapsed_seconds", "interaction_status")},
                     "native_final_score": row["native_metrics"].get("final_score"),
                     **(row["interaction_metrics"] or {})})
    fields = list(dict.fromkeys(k for row in flat for k in row))
    with (output / "episodes.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flat)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, action="append", required=True,
                        help="Batch containing CONDITION/config.json, summary.json and episode directories")
    parser.add_argument("--manifest", type=Path, default=ROOT / "configs/discoverybench-ecology-study.json")
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    parser.add_argument("--annotation-output", type=Path, help="New local/private JSON file; contains visible scientific messages")
    args = parser.parse_args()
    report, packets = analyze([p.resolve() for p in args.run_root], read_json(args.manifest))
    if args.output.exists() or (args.annotation_output and args.annotation_output.exists()):
        parser.error("Output already exists; preserve earlier analyses and choose a fresh path")
    write_report(args.output, report)
    if args.annotation_output:
        args.annotation_output.parent.mkdir(parents=True, exist_ok=True)
        args.annotation_output.write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    print(f"Analyzed {len(report['episodes'])} episodes; no model calls. Metrics: {args.output / 'metrics.json'}")


if __name__ == "__main__":
    main()
