#!/usr/bin/env python3
"""Rank action personas by task-paired normalized native benchmark score."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


PRIMARY = {
    "asibench": "score",
    "bixbench": "grade",
    "discoverybench": "final_score",
    "expbench": "gated_coverage_mean",
    "sciconvbench": "FRR",
}
RETIRED = {"scienceagentbench", "terminal_bench_science"}


def normalized(row: dict) -> float | None:
    metric = PRIMARY[row["benchmark"]]
    metrics = row.get("metrics", {})
    if metric not in metrics:
        return None
    value = float(metrics[metric])
    if row["benchmark"] == "asibench":
        return value / float(metrics["max_score"])
    if row["benchmark"] == "expbench":
        return value / 100.0
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exclude-benchmarks", nargs="*", default=[])
    args = parser.parse_args()
    data = json.loads(args.comparison.read_text())
    excluded_benchmarks = set(args.exclude_benchmarks)
    unknown = excluded_benchmarks - (PRIMARY.keys() | RETIRED)
    if unknown:
        raise ValueError(f"Unknown excluded benchmarks: {sorted(unknown)}")
    episodes = [row for row in data["episodes"] if row["benchmark"] not in excluded_benchmarks]
    controls = {row["task"]: row for row in episodes if row["arm"] == "persona_off"}
    eligible = {task for task, row in controls.items() if normalized(row) is not None}
    arms = sorted({row["arm"] for row in episodes} - {"persona_off"})
    rankings = []
    for arm in arms:
        pairs, missing, failures = [], 0, 0
        for row in (r for r in episodes if r["arm"] == arm and r["task"] in eligible):
            baseline = normalized(controls[row["task"]])
            score = normalized(row)
            if score is None and row["status"] == "missing_submission":
                score, missing = 0.0, missing + 1
            elif score is None:
                failures += 1
                continue
            pairs.append((score, baseline))
        if not pairs:
            continue
        persona_mean = sum(score for score, _ in pairs) / len(pairs)
        baseline_mean = sum(score for _, score in pairs) / len(pairs)
        rankings.append({
            "persona": arm,
            "score_average": persona_mean,
            "paired_baseline_average": baseline_mean,
            "deviation": persona_mean - baseline_mean,
            "comparable_pairs": len(pairs),
            "eligible_pairs": len(eligible),
            "missing_submissions_scored_zero": missing,
            "infrastructure_pairs_excluded": failures,
        })
    rankings.sort(key=lambda row: (-row["deviation"], row["persona"]))

    baseline_values = [normalized(controls[task]) for task in eligible]
    common_baseline = sum(baseline_values) / len(baseline_values)
    excluded_control_tasks = sorted(set(controls) - eligible)
    lines = [
        "# Persona benchmark score ranking", "",
        "This table ranks the 30 action personas by their mean task-paired deviation from persona off. "
        "Each benchmark's primary native metric is normalized to 0–1 before averaging. A persona-side "
        "missing submission is scored as zero because it produced no gradable answer. Infrastructure, "
        "launch, and transport failures are excluded and reduce coverage.", "",
        "Retired benchmarks absent from this comparison: ScienceAgentBench and Terminal-Bench-Science. "
        "Additional analysis exclusions: " + (", ".join(sorted(excluded_benchmarks - RETIRED)) or "none") + ".", "",
        f"The common persona-off average is **{common_baseline:.4f}** across **{len(eligible)} of {len(controls)} included tasks**. "
        f"Control tasks without a native score and excluded from paired scoring: "
        f"{', '.join(f'`{task}`' for task in excluded_control_tasks) or 'none'}. Persona-specific baseline "
        "averages can differ when an infrastructure failure excludes another task.", "",
        "Primary metrics: ASI score/max score; Bix grade; Discovery final score; EXP gated coverage/100; "
        "SciConv FRR.", "",
        "| Rank | Persona | Score average | Paired off average | Deviation | Coverage | Missing→0 | Infra excluded |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(rankings, 1):
        lines.append(
            f"| {rank} | `{row['persona']}` | {row['score_average']:.4f} | "
            f"{row['paired_baseline_average']:.4f} | {row['deviation']:+.4f} | "
            f"{row['comparable_pairs']}/{row['eligible_pairs']} | "
            f"{row['missing_submissions_scored_zero']} | {row['infrastructure_pairs_excluded']} |"
        )
    full = [row for row in rankings if row["comparable_pairs"] == len(eligible)]
    lines += ["", "## Reading the ranking", "",
              f"{len(full)} of 30 personas have full {len(eligible)}-task coverage. "
              "Rows with lower coverage are less comparable: for example, a high average based on six or "
              "eight tasks may reflect which tasks survived rather than a stronger persona. These are "
              "descriptive single-run differences against shared controls; they are not uncertainty-adjusted "
              "effect estimates.", ""]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines))
    machine = args.output.with_suffix(".json")
    machine.write_text(json.dumps({
        "policy": "task-paired normalized primary metrics; missing submission=0; infrastructure excluded",
        "excluded_benchmarks": sorted(excluded_benchmarks | RETIRED),
        "retired_benchmarks": sorted(RETIRED),
        "common_persona_off_average": common_baseline,
        "eligible_tasks": sorted(eligible),
        "excluded_control_tasks": excluded_control_tasks,
        "rankings": rankings,
        "status_counts": dict(Counter(row["status"] for row in episodes)),
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
