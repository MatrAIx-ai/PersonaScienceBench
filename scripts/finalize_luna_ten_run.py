#!/usr/bin/env python3
"""Consolidate the 50-case Luna run and write its readable run report."""

from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path

from personasciencebench.terminal_scoring import terminal_score_fields


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def result_rows(directory: Path) -> list[dict]:
    return [read(path) for path in sorted(directory.glob("*/result.json"))]


def call_stats(files: list[Path]) -> tuple[Counter, float]:
    roles: Counter = Counter()
    cost = 0.0
    for path in files:
        for line in path.read_text(errors="replace").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("phase") == "request":
                continue
            if row.get("phase") not in (None, "response"):
                continue
            roles[row.get("role", "unknown")] += 1
            response = row.get("response") or {}
            usage = row.get("usage") or response.get("usage") or {}
            cost += float(usage.get("cost") or 0)
    return roles, cost


def mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run
    python_dir = run / "python-runtime-fixed"
    exp_dir = run / "expbench-runtime-fixed"
    terminal_dir = run / "terminal"
    ont_retry_dir = run / "terminal-ont-retry"

    recovered = []
    for result_path in sorted(terminal_dir.glob("*/result.json")):
        case = result_path.parent
        evaluation_path = case / "native-docker-retry/evaluation.json"
        if not evaluation_path.is_file():
            continue
        result = read(result_path)
        evaluation = read(evaluation_path)
        if evaluation.get("status") != "scored":
            continue
        result["recovery"] = {
            "initial_status": result.get("status"),
            "initial_error_type": result.get("error_type"),
            "initial_error": result.get("error"),
            "method": "saved-submission-native-regrade",
            "actor_rerun": False,
            "evaluation_path": str(evaluation_path.resolve()),
        }
        result.pop("error_type", None)
        result.pop("error", None)
        result["status"] = evaluation["status"]
        result["evaluation"] = evaluation
        result.update(terminal_score_fields(result, evaluation))
        write(result_path, result)
        recovered.append(result["episode_id"])

    python_rows = result_rows(python_dir)
    exp_rows = result_rows(exp_dir)
    terminal_primary = result_rows(terminal_dir)
    retry_rows = result_rows(ont_retry_dir)
    if len(retry_rows) != 1:
        raise ValueError("Expected exactly one ONT retry result")
    retry = retry_rows[0]
    retry["effective_replacement_for"] = "OpenRouter ReadError in the primary ONT attempt"
    terminal_effective = [retry if row["episode_id"] == retry["episode_id"] else row
                          for row in terminal_primary]
    effective_summary = {
        "requested": 10,
        "cases": terminal_effective,
        "recovered_saved_submissions": recovered,
        "replacement_attempts": [retry["episode_id"]],
        "cross_benchmark_average": None,
    }
    write(terminal_dir / "effective_summary.json", effective_summary)

    discovery = [row for row in python_rows if row["benchmark"] == "discoverybench"]
    bix = [row for row in python_rows if row["benchmark"] == "bixbench"]
    sab = [row for row in python_rows if row["benchmark"] == "scienceagentbench"]
    discovery_score = mean((row.get("evaluation") or {}).get("metrics", {}).get("final_score", 0)
                           for row in discovery)
    bix_correct = sum(bool((row.get("evaluation") or {}).get("metrics", {}).get("correct"))
                      for row in bix)
    sab_success = sum(float((row.get("evaluation") or {}).get("metrics", {}).get("success_rate", 0))
                      for row in sab)
    sab_valid = sum(float((row.get("evaluation") or {}).get("metrics", {}).get("valid_program", 0))
                    for row in sab)
    exp_coverage = mean((row.get("initial") or {}).get("gated_coverage_mean", 0) for row in exp_rows)
    terminal_pass = sum(float((row.get("evaluation") or {}).get("metrics", {}).get("reward", 0))
                        for row in terminal_effective)

    python_calls, python_cost = call_stats(
        list(python_dir.glob("*/controller/api_calls.private.jsonl")))
    exp_calls, exp_cost = call_stats(list(exp_dir.glob("*/api_calls.jsonl")))
    terminal_files = list(terminal_dir.glob("*/api_calls.private.jsonl"))
    terminal_files += list(ont_retry_dir.glob("*/api_calls.private.jsonl"))
    terminal_calls, terminal_cost = call_stats(terminal_files)
    calls = python_calls + exp_calls + terminal_calls
    total_cost = python_cost + exp_cost + terminal_cost

    questions = {
        "DiscoveryBench": sum(row.get("researcher_questions", 0) or 0 for row in discovery),
        "BixBench": sum(row.get("researcher_questions", 0) or 0 for row in bix),
        "ScienceAgentBench": sum(row.get("researcher_questions", 0) or 0 for row in sab),
        "EXP-Bench": sum(row.get("researcher_questions", 0) or 0 for row in exp_rows),
        "Terminal-Bench-Science": (
            sum(row.get("researcher_questions", 0) or 0 for row in terminal_primary)
            + sum(row.get("researcher_questions", 0) or 0 for row in retry_rows)),
    }

    terminal_status = Counter(row["status"] for row in terminal_effective)
    lines = [
        "# GPT-6 Luna persona-off: 50-case run",
        "",
        "Ten cases were attempted for each of five benchmarks. Actor and grounded simulator used `openai/gpt-6-luna` with reasoning `none`; model-based judges also used Luna. ScienceAgentBench and Terminal-Bench-Science retained their native programmatic graders.",
        "",
        "All cases within each runner were scheduled concurrently: shared Python `25`, EXP-Bench `10`, and Terminal `10`. The three runners were launched together. Persona styling was disabled; the simulator remained available for approved study facts.",
        "",
        "## Results",
        "",
        "| Benchmark | Closed cases | Primary metric | Simulator questions |",
        "|---|---:|---:|---:|",
        f"| DiscoveryBench | {len(discovery)}/10 | mean final score `{discovery_score:.4f}` | {questions['DiscoveryBench']} |",
        f"| BixBench | {len(bix)}/10 | accuracy `{bix_correct}/10` | {questions['BixBench']} |",
        f"| ScienceAgentBench | {len(sab)}/10 | success `{sab_success:.0f}/10`; valid programs `{sab_valid:.0f}/10` | {questions['ScienceAgentBench']} |",
        f"| EXP-Bench | {len(exp_rows)}/10 | mean integrity-gated coverage `{exp_coverage:.2f}` | {questions['EXP-Bench']} |",
        f"| Terminal-Bench-Science | {len(terminal_effective)}/10 | native passes `{terminal_pass:.0f}/10`; {terminal_status.get('scored', 0)} graded, {terminal_status.get('missing_submission', 0)} policy-zero missing submissions | {questions['Terminal-Bench-Science']} |",
        "",
        "The reported API usage across completed attempts and the ONT retry is "
        f"`${total_cost:.6f}`: actor `{calls.get('actor', 0)}` calls, simulator `{calls.get('researcher', 0)}` calls, and model judge `{calls.get('judge', 0)}` calls. Native grader executions are not model calls.",
        "",
        "## Readable complete traces",
        "",
        "- [DiscoveryBench, BixBench, and ScienceAgentBench: 30 traces](python-runtime-fixed/TRACE_INDEX.md)",
        "- [EXP-Bench: 10 traces](expbench-runtime-fixed/TRACE_INDEX.md)",
        "- [Terminal-Bench-Science: 10 primary traces](terminal/TRACE_INDEX.md)",
        "- [ONT retry trace](terminal-ont-retry/TRACE_INDEX.md)",
        "",
        "Each case directory retains raw actor events, controller events, simulator history, complete recorded API requests/responses, submissions, and evaluations. The Markdown renderings include recorded prompts and responses but cannot include hidden chain-of-thought that the provider did not return.",
        "",
        "## Recovery record",
        "",
        "- The first 30-case shared attempt and first 10-case EXP attempt stopped before actor inference because Bubblewrap was absent from the process path. Their records remain under `python/` and `expbench/`; the reported batches are `python-runtime-fixed/` and `expbench-runtime-fixed/`.",
        "- The primary ONT attempt ended in an OpenRouter `ReadError` after 18 actor calls. Its single retry completed normally at the 20-step limit with no submission, producing the policy-zero result used above. Both traces are retained.",
        f"- {len(recovered)} submitted Terminal artifacts were graded from their saved immutable submissions after repairing the benchmark-wide artifact lookup. No actor was rerun: " + ", ".join(f"`{item}`" for item in recovered) + ".",
        "- Supplemental `analysis` artifacts from symbolic regression and spin-glass were excluded from native verifier containers and recorded as ignored; every benchmark-required artifact remained hash-checked and unchanged.",
    ]
    (run / "RUN_REPORT.md").write_text("\n".join(lines) + "\n")
    print(f"Finalized {len(python_rows) + len(exp_rows) + len(terminal_effective)} effective cases")
    print(f"API-reported usage: ${total_cost:.6f}; calls={dict(calls)}")


if __name__ == "__main__":
    main()
