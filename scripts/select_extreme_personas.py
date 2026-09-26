#!/usr/bin/env python3
"""Select full-coverage action personas at both ends of a score ranking."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()
    ranking = json.loads(args.ranking.read_text())
    rows = [row for row in ranking["rankings"]
            if row["comparable_pairs"] == row["eligible_pairs"]]
    if len(rows) < args.count * 2:
        raise ValueError("Not enough full-coverage profiles for disjoint extremes")
    helpful = rows[:args.count]
    negative_full = [row for row in rows if row["deviation"] < 0]
    negative_incomplete = [row for row in ranking["rankings"]
                           if row["deviation"] < 0 and row not in negative_full]
    misleading = sorted(negative_full + negative_incomplete,
                        key=lambda row: row["deviation"])[:args.count]
    if len(misleading) < args.count:
        raise ValueError("Not enough below-baseline profiles for misleading cohort")
    selected = [("helpful", row) for row in helpful]
    selected += [("misleading", row) for row in misleading]
    profiles = {row["candidate_id"]: row for row in (
        json.loads(line) for line in args.profiles.read_text().splitlines() if line.strip())}
    cohort = []
    for group, score in selected:
        profile = profiles[score["persona"]]
        cohort.append({
            "group": group,
            "candidate_id": score["persona"],
            "source": profile["source"],
            "score_average": score["score_average"],
            "paired_baseline_average": score["paired_baseline_average"],
            "deviation": score["deviation"],
            "coverage": f"{score['comparable_pairs']}/{score['eligible_pairs']}",
            "action_rules": [rule["instruction"] for rule in profile["rules"] if rule["directional"]],
        })
    payload = {
        "version": "extreme-action-personas-v1",
        "selection": ("Helpful: top five deviations with complete coverage. Misleading: five most negative "
                      "deviations, preferring full coverage; incomplete coverage is explicitly retained."),
        "retired_benchmarks": ranking.get("retired_benchmarks", ranking["excluded_benchmarks"]),
        "missing_submission_policy": "zero",
        "profiles": cohort,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    lines = ["# Selected extreme action personas", "",
             "Selection uses the retained five-benchmark score ranking. Terminal-Bench-Science and "
             "ScienceAgentBench were discarded from the study because they were too heavy. "
             "Helpful profiles require complete 9/9 paired-score coverage. Four full-coverage profiles scored "
             "below baseline, so the fifth misleading profile is the most negative incomplete profile and is "
             "marked by its coverage. `Helpful` and `misleading` describe observed benchmark association in this "
             "single run; they are not intrinsic profile labels.", ""]
    for group in ("helpful", "misleading"):
        lines += ["## " + group.capitalize(), "",
                  "| Persona | Score | Baseline | Deviation | Coverage |", "|---|---:|---:|---:|---:|"]
        for row in (item for item in cohort if item["group"] == group):
            lines.append(f"| `{row['candidate_id']}` | {row['score_average']:.4f} | "
                         f"{row['paired_baseline_average']:.4f} | {row['deviation']:+.4f} | {row['coverage']} |")
        lines.append("")
    lines += ["## Action rules", ""]
    for row in cohort:
        lines += [f"### {row['candidate_id']} — {row['group']}", ""]
        lines += ["- " + rule for rule in row["action_rules"]]
        lines.append("")
    args.output.with_suffix(".md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
