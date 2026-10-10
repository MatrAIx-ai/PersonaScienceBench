#!/usr/bin/env python3
"""Package the Haiku-actor/Opus-researcher Astra regrade for authors."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGRADE = (
    ROOT / "runs/rejudge/haiku-actor-opus-researcher-astra-judge-trial-1"
)
DEFAULT_OUTPUT = ROOT / "haiku_actor_opus_astra_rejudge_results"
ORIGINAL_BUNDLE = ROOT / "haiku_actor_opus_persona_pilot"
SELF_ASTRA_BUNDLE = ROOT / "haiku_self_astra_persona_results"
ARMS = (
    "persona_off",
    "candidate_155",
    "candidate_001",
    "candidate_003",
    "candidate_046",
)
PERSONAS = ARMS[1:]
BENCHMARKS = (
    "asibench",
    "bixbench",
    "discoverybench",
    "expbench",
    "sciconvbench",
)
LABELS = {
    "asibench": "ASI-Bench",
    "bixbench": "BixBench",
    "discoverybench": "DiscoveryBench",
    "expbench": "EXP-Bench",
    "sciconvbench": "SciConvBench",
}
SECRET_PATTERN = re.compile(
    r"(?:sk-(?:proj-|or-v1-)?[A-Za-z0-9_-]{20,}|"
    r"gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[A-Z0-9]{16})"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def copy_verified(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    digest = sha256(source)
    if sha256(target) != digest:
        raise ValueError(f"Copy checksum mismatch: {source} -> {target}")
    return digest


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("benchmark", row.get("source"))),
        str(row["task_id"]),
        str(row["arm"]),
    )


def bootstrap_interval(
    values: list[float], samples: int, seed: int
) -> list[float]:
    if not values:
        raise ValueError("Cannot bootstrap an empty comparison")
    generator = random.Random(seed)
    size = len(values)
    estimates = sorted(
        mean(values[generator.randrange(size)] for _ in range(size))
        for _ in range(samples)
    )
    lower = estimates[int(0.025 * (samples - 1))]
    upper = estimates[int(0.975 * (samples - 1))]
    return [lower, upper]


def comparison(
    values: list[float], samples: int, seed: int
) -> dict[str, Any]:
    return {
        "n": len(values),
        "mean_difference": mean(values),
        "paired_task_bootstrap_95_ci": bootstrap_interval(
            values, samples, seed
        ),
        "positive": sum(value > 0 for value in values),
        "tie": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
    }


def validate_regrade(
    manifest: dict[str, Any], results: list[dict[str, Any]]
) -> None:
    if manifest.get("kind") != "judge-only-main-campaign-regrade":
        raise ValueError("Unexpected regrade manifest kind")
    if manifest.get("episode_count") != 1000:
        raise ValueError("Expected a 1,000-episode regrade")
    if manifest.get("arms") != list(ARMS):
        raise ValueError("Unexpected regrade conditions")
    judge = manifest.get("new_judge") or {}
    if (
        judge.get("provider") != "bedrock"
        or judge.get("model") != "us.openai.gpt-6-astra"
        or judge.get("reasoning_effort") != "low"
    ):
        raise ValueError(f"Unexpected regrade judge: {judge}")
    if len(results) != 1000:
        raise ValueError(f"Expected 1,000 regrade results, found {len(results)}")
    if Counter(row["status"] for row in results) != {"finished": 1000}:
        raise ValueError("The Astra regrade is not complete")
    if len({key(row) for row in results}) != 1000:
        raise ValueError("The Astra regrade contains duplicate result slots")


def load_inputs(
    regrade_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[tuple[str, str, str], dict[str, str]],
    dict[tuple[str, str, str], dict[str, str]],
    dict[str, Any],
]:
    regrade_results = json.loads((regrade_dir / "results.json").read_text())
    manifest = json.loads((regrade_dir / "manifest.json").read_text())
    validate_regrade(manifest, regrade_results)
    original_rows = read_csv(ORIGINAL_BUNDLE / "full_campaign_episodes.csv")
    self_rows = read_csv(SELF_ASTRA_BUNDLE / "episodes.csv")
    original = {key(row): row for row in original_rows}
    self_astra = {key(row): row for row in self_rows}
    regrade_keys = {key(row) for row in regrade_results}
    if len(original) != 1000 or set(original) != regrade_keys:
        raise ValueError("Original Opus-judge rows do not match the regrade panel")
    if len(self_astra) != 1000 or set(self_astra) != regrade_keys:
        raise ValueError("Self-Haiku Astra rows do not match the regrade panel")
    return regrade_results, original, self_astra, manifest


def compact_rows(
    regrade_results: list[dict[str, Any]],
    original: dict[tuple[str, str, str], dict[str, str]],
    self_astra: dict[tuple[str, str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    rows = []
    for result in regrade_results:
        slot = key(result)
        old = original[slot]
        self_row = self_astra[slot]
        new_score = float(result["score_0_100"])
        old_score = float(old["score_0_100"])
        self_score = float(self_row["score_0_100"])
        evaluation = result.get("evaluation") or {}
        rows.append({
            "benchmark": result["source"],
            "task_id": result["task_id"],
            "task_key": old.get("task_key", ""),
            "family": old.get("family", ""),
            "subfield": old.get("subfield", ""),
            "study_id": old.get("study_id", ""),
            "arm": result["arm"],
            "source_attempt": result["source_attempt"],
            "regrade_attempt": result["attempt"],
            "regrade_status": result["status"],
            "regrade_disposition": result["regrade_disposition"],
            "submitted": result["submitted"],
            "astra_evaluation_status": evaluation.get("status"),
            "astra_score_0_100": new_score,
            "original_opus_judge_score_0_100": old_score,
            "astra_minus_original_opus_judge": new_score - old_score,
            "self_haiku_astra_score_0_100": self_score,
            "opus_researcher_minus_self_haiku_researcher": (
                new_score - self_score
            ),
            "judge_calls": int(result.get("judge_calls", 0)),
            "evaluator_version": evaluation.get("evaluator_version", ""),
            "submission_or_trace_sha256": result.get(
                "submission_or_trace_sha256", ""
            ),
            "source_state_sha256": result["source_state_sha256"],
        })
    return sorted(
        rows,
        key=lambda row: (
            BENCHMARKS.index(row["benchmark"]),
            row["task_id"],
            ARMS.index(row["arm"]),
        ),
    )


def summarize(
    rows: list[dict[str, Any]], samples: int, seed: int
) -> dict[str, Any]:
    by_key = {
        (row["benchmark"], row["task_id"], row["arm"]): row
        for row in rows
    }
    tasks = sorted({(row["benchmark"], row["task_id"]) for row in rows})
    by_condition = {}
    by_benchmark_condition = {}
    for arm in ARMS:
        selected = [row for row in rows if row["arm"] == arm]
        by_condition[arm] = {
            "episodes": len(selected),
            "submitted": sum(bool_value(row["submitted"]) for row in selected),
            "astra_mean_score_0_100": mean(
                row["astra_score_0_100"] for row in selected
            ),
            "original_opus_judge_mean_score_0_100": mean(
                row["original_opus_judge_score_0_100"] for row in selected
            ),
            "self_haiku_astra_mean_score_0_100": mean(
                row["self_haiku_astra_score_0_100"] for row in selected
            ),
            "judge_calls": sum(row["judge_calls"] for row in selected),
            "judge_call_endpoints": sum(
                row["judge_calls"] > 0 for row in selected
            ),
        }
    for benchmark in BENCHMARKS:
        by_benchmark_condition[benchmark] = {}
        for arm in ARMS:
            selected = [
                row for row in rows
                if row["benchmark"] == benchmark and row["arm"] == arm
            ]
            by_benchmark_condition[benchmark][arm] = {
                "episodes": len(selected),
                "submitted": sum(
                    bool_value(row["submitted"]) for row in selected
                ),
                "astra_mean_score_0_100": mean(
                    row["astra_score_0_100"] for row in selected
                ),
                "judge_calls": sum(row["judge_calls"] for row in selected),
                "judge_call_endpoints": sum(
                    row["judge_calls"] > 0 for row in selected
                ),
            }
    judge_change = {}
    researcher_direct = {}
    for index, arm in enumerate(ARMS):
        selected = [row for row in rows if row["arm"] == arm]
        judge_change[arm] = comparison(
            [
                row["astra_minus_original_opus_judge"]
                for row in selected
            ],
            samples,
            seed + index,
        )
        researcher_direct[arm] = comparison(
            [
                row["opus_researcher_minus_self_haiku_researcher"]
                for row in selected
            ],
            samples,
            seed + 100 + index,
        )
    persona_effects = {
        "opus_researcher_astra": {},
        "self_haiku_researcher_astra": {},
        "difference_in_differences": {},
    }
    for index, arm in enumerate(PERSONAS):
        opus_deltas = []
        self_deltas = []
        did = []
        for benchmark, task_id in tasks:
            opus_persona = by_key[(benchmark, task_id, arm)][
                "astra_score_0_100"
            ]
            opus_off = by_key[(benchmark, task_id, "persona_off")][
                "astra_score_0_100"
            ]
            self_persona = by_key[(benchmark, task_id, arm)][
                "self_haiku_astra_score_0_100"
            ]
            self_off = by_key[(benchmark, task_id, "persona_off")][
                "self_haiku_astra_score_0_100"
            ]
            opus_delta = opus_persona - opus_off
            self_delta = self_persona - self_off
            opus_deltas.append(opus_delta)
            self_deltas.append(self_delta)
            did.append(opus_delta - self_delta)
        persona_effects["opus_researcher_astra"][arm] = comparison(
            opus_deltas, samples, seed + 200 + index
        )
        persona_effects["self_haiku_researcher_astra"][arm] = comparison(
            self_deltas, samples, seed + 300 + index
        )
        persona_effects["difference_in_differences"][arm] = comparison(
            did, samples, seed + 400 + index
        )
    pooled_opus = []
    pooled_self = []
    pooled_did = []
    for benchmark, task_id in tasks:
        opus_off = by_key[(benchmark, task_id, "persona_off")][
            "astra_score_0_100"
        ]
        self_off = by_key[(benchmark, task_id, "persona_off")][
            "self_haiku_astra_score_0_100"
        ]
        opus_value = mean(
            by_key[(benchmark, task_id, arm)]["astra_score_0_100"]
            for arm in PERSONAS
        ) - opus_off
        self_value = mean(
            by_key[(benchmark, task_id, arm)][
                "self_haiku_astra_score_0_100"
            ]
            for arm in PERSONAS
        ) - self_off
        pooled_opus.append(opus_value)
        pooled_self.append(self_value)
        pooled_did.append(opus_value - self_value)
    persona_effects["pooled"] = {
        "opus_researcher_astra": comparison(
            pooled_opus, samples, seed + 500
        ),
        "self_haiku_researcher_astra": comparison(
            pooled_self, samples, seed + 501
        ),
        "difference_in_differences": comparison(
            pooled_did, samples, seed + 502
        ),
    }
    return {
        "analysis": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "episodes": 1000,
            "tasks": 200,
            "conditions": list(ARMS),
            "bootstrap_samples": samples,
            "bootstrap_unit": "task",
            "actor": "Bedrock Claude Haiku 4.5",
            "researcher": "Bedrock Claude Opus 4.6",
            "regrade_judge": "Bedrock GPT-6 Astra, low reasoning",
            "original_judge": "Bedrock Claude Opus 4.6",
        },
        "by_condition": by_condition,
        "by_benchmark_condition": by_benchmark_condition,
        "judge_regrade_change": judge_change,
        "researcher_direct_comparison": researcher_direct,
        "persona_effects": persona_effects,
        "judge_call_audit": {
            "total_calls": sum(row["judge_calls"] for row in rows),
            "endpoints_with_calls": sum(row["judge_calls"] > 0 for row in rows),
            "submitted_zero_call_endpoints": sum(
                bool_value(row["submitted"]) and row["judge_calls"] == 0
                for row in rows
            ),
            "retained_non_submission_endpoints": sum(
                not bool_value(row["submitted"]) for row in rows
            ),
            "call_distribution": dict(
                sorted(Counter(row["judge_calls"] for row in rows).items())
            ),
        },
    }


def interval(value: dict[str, Any]) -> str:
    low, high = value["paired_task_bootstrap_95_ci"]
    return f"[{low:.2f}, {high:.2f}]"


def render_summary(summary: dict[str, Any]) -> str:
    condition = summary["by_condition"]
    effects = summary["persona_effects"]
    calls = summary["judge_call_audit"]
    lines = [
        "# Astra regrade of the Haiku-actor / Opus-researcher campaign",
        "",
        "## What was done",
        "",
        "The completed 1,000-episode Haiku-actor / Opus-researcher campaign "
        "was re-evaluated with GPT-6 Astra at low reasoning effort. The actor "
        "and researcher trajectories were frozen and were not rerun.",
        "",
        f"The native evaluators made **{calls['total_calls']:,} Astra calls** "
        f"across **{calls['endpoints_with_calls']} endpoints**. "
        f"Another **{calls['submitted_zero_call_endpoints']} submitted endpoints** "
        "used deterministic native scoring, and "
        f"**{calls['retained_non_submission_endpoints']} original "
        "non-submissions** remained zero without a call.",
        "",
        "## Astra-regraded scores",
        "",
        "| Condition | Astra mean | Difference vs off | Paired 95% interval | "
        "Submitted | Astra calls |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        row = condition[arm]
        if arm == "persona_off":
            lines.append(
                f"| `{arm}` | {row['astra_mean_score_0_100']:.2f} | — | — | "
                f"{row['submitted']}/200 | {row['judge_calls']} |"
            )
        else:
            value = effects["opus_researcher_astra"][arm]
            lines.append(
                f"| `{arm}` | {row['astra_mean_score_0_100']:.2f} | "
                f"{value['mean_difference']:+.2f} | {interval(value)} | "
                f"{row['submitted']}/200 | {row['judge_calls']} |"
            )
    pooled = effects["pooled"]["opus_researcher_astra"]
    lines += [
        "",
        "Averaging the four persona conditions within each task produced a "
        f"pooled effect of **{pooled['mean_difference']:+.2f} points** versus "
        f"persona off (95% interval {interval(pooled)}).",
        "",
        "## Researcher-model ablation",
        "",
        "Both sides below use Haiku as actor and Astra as judge. The comparison "
        "changes the simulated researcher from Haiku to Opus.",
        "",
        "| Condition | Opus researcher | Haiku researcher | Difference | "
        "Paired 95% interval |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        row = condition[arm]
        value = summary["researcher_direct_comparison"][arm]
        lines.append(
            f"| `{arm}` | {row['astra_mean_score_0_100']:.2f} | "
            f"{row['self_haiku_astra_mean_score_0_100']:.2f} | "
            f"{value['mean_difference']:+.2f} | {interval(value)} |"
        )
    lines += [
        "",
        "## Does researcher capability change the persona effect?",
        "",
        "| Persona | Effect with Opus researcher | Effect with Haiku researcher | "
        "Difference-in-differences | Paired 95% interval |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in PERSONAS:
        opus = effects["opus_researcher_astra"][arm]
        self_value = effects["self_haiku_researcher_astra"][arm]
        did = effects["difference_in_differences"][arm]
        lines.append(
            f"| `{arm}` | {opus['mean_difference']:+.2f} | "
            f"{self_value['mean_difference']:+.2f} | "
            f"{did['mean_difference']:+.2f} | {interval(did)} |"
        )
    pooled_self = effects["pooled"]["self_haiku_researcher_astra"]
    pooled_did = effects["pooled"]["difference_in_differences"]
    lines += [
        "",
        "The pooled persona effect was "
        f"**{pooled['mean_difference']:+.2f}** with the Opus researcher and "
        f"**{pooled_self['mean_difference']:+.2f}** with the Haiku researcher. "
        "Their difference-in-differences was "
        f"**{pooled_did['mean_difference']:+.2f} points** "
        f"(95% interval {interval(pooled_did)}).",
        "",
        "## Interpretation boundary",
        "",
        "This is a useful researcher-capability ablation because actor, task panel, "
        "conditions, and active Astra evaluator are aligned. However, it compares "
        "one independently sampled trajectory trial for each researcher model. "
        "The task-bootstrap intervals do not capture run-to-run model variance, "
        "and the two campaigns were executed at different times. Treat the "
        "researcher comparison as strong exploratory evidence until replicated.",
        "",
        "The original Opus-judge scores are retained in `episodes.csv` for "
        "calibration analysis. Differences between those scores and the Astra "
        "regrade can also include active evaluator-version changes, not only judge "
        "model calibration.",
    ]
    return "\n".join(lines) + "\n"


def render_readme(summary: dict[str, Any]) -> str:
    audit = summary["judge_call_audit"]
    return f"""# Haiku actor / Opus researcher / Astra judge results

This folder contains the compact, author-facing export of the judge-only
Astra regrade of the completed Haiku-actor / Opus-researcher campaign.

## Start here

- `summary.md`: findings and researcher-model ablation.
- `summary.json`: complete aggregate statistics and bootstrap intervals.
- `episodes.csv`: all 1,000 matched episode results.
- `persona_pairs.csv`: same-task persona-versus-control comparisons.
- `actor_metrics/`: actor output tokens, model calls, and tool calls for every
  frozen source episode.
- `traces/shared-events.jsonl`: sanitized Opus-simulator/Haiku-actor
  interaction traces for every frozen source episode.
- `traces/shared-events-index.csv`: searchable interaction-trace index.
- `judge_metrics/`: per-episode and aggregate judge-call counts.
- `evaluations/metrics.jsonl`: compact native evaluation metrics without API
  prompts or responses.
- `provenance/`: exact run receipts, code hashes, launchers, and source hashes.
- `candidate_*.md`: exact persona prompts.

## Scope

- Frozen source trajectories: 1,000.
- Actor or researcher reruns: 0.
- Astra calls: {audit['total_calls']:,}.
- Submitted endpoints scored deterministically with zero Astra calls:
  {audit['submitted_zero_call_endpoints']}.
- Original non-submissions retained as zero: 
  {audit['retained_non_submission_endpoints']}.

`finished` means the native evaluator completed. It does not imply that an
Astra call was required. Model-based judging uses Astra wherever the native
benchmark requests it; deterministic native components remain unchanged.

## Excluded

The raw regrade is approximately 729 MB because ASI evaluation sandboxes copy
scientific assets. This compact bundle excludes those copies, private API
request/response logs, hidden evaluator references, and temporary workspaces.
Their source files are retained in the raw run and referenced by checksums.

Raw regrade:
`runs/rejudge/haiku-actor-opus-researcher-astra-judge-trial-1`

The actor metrics and interaction traces are inherited byte-for-byte from the
frozen source campaign. Judge-only regrading cannot change actor tokens, actor
tools, or actor–researcher conversation events.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regrade-dir", type=Path, default=DEFAULT_REGRADE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()
    regrade_dir = args.regrade_dir.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing bundle: {output_dir}")
    output_dir.mkdir(parents=True)
    for name in (
        "actor_metrics",
        "judge_metrics",
        "evaluations",
        "provenance/code_hashes",
        "traces",
    ):
        (output_dir / name).mkdir(parents=True)
    regrade_results, original, self_astra, manifest = load_inputs(regrade_dir)
    rows = compact_rows(regrade_results, original, self_astra)
    summary = summarize(rows, args.bootstrap_samples, args.seed)
    write_csv(output_dir / "episodes.csv", rows)
    write_json(output_dir / "summary.json", summary)
    (output_dir / "summary.md").write_text(render_summary(summary))
    (output_dir / "README.md").write_text(render_readme(summary))

    by_key = {
        (row["benchmark"], row["task_id"], row["arm"]): row for row in rows
    }
    tasks = sorted({(row["benchmark"], row["task_id"]) for row in rows})
    pair_rows = []
    for benchmark, task_id in tasks:
        off = by_key[(benchmark, task_id, "persona_off")]
        for arm in PERSONAS:
            persona = by_key[(benchmark, task_id, arm)]
            pair_rows.append({
                "benchmark": benchmark,
                "task_id": task_id,
                "persona": arm,
                "persona_astra_score_0_100": persona["astra_score_0_100"],
                "off_astra_score_0_100": off["astra_score_0_100"],
                "persona_minus_off": (
                    persona["astra_score_0_100"]
                    - off["astra_score_0_100"]
                ),
                "persona_submitted": persona["submitted"],
                "off_submitted": off["submitted"],
                "persona_judge_calls": persona["judge_calls"],
                "off_judge_calls": off["judge_calls"],
            })
    write_csv(output_dir / "persona_pairs.csv", pair_rows)

    metric_rows = [{
        "benchmark": row["benchmark"],
        "task_id": row["task_id"],
        "arm": row["arm"],
        "submitted": row["submitted"],
        "judge_calls": row["judge_calls"],
        "regrade_disposition": row["regrade_disposition"],
        "astra_score_0_100": row["astra_score_0_100"],
    } for row in rows]
    write_csv(output_dir / "judge_metrics/per_episode.csv", metric_rows)
    condition_rows = []
    for arm in ARMS:
        value = summary["by_condition"][arm]
        condition_rows.append({"arm": arm, **value})
    write_csv(
        output_dir / "judge_metrics/summary_by_condition.csv",
        condition_rows,
    )
    benchmark_rows = []
    for benchmark in BENCHMARKS:
        for arm in ARMS:
            benchmark_rows.append({
                "benchmark": benchmark,
                "arm": arm,
                **summary["by_benchmark_condition"][benchmark][arm],
            })
    write_csv(
        output_dir / "judge_metrics/summary_by_benchmark_condition.csv",
        benchmark_rows,
    )
    write_json(
        output_dir / "judge_metrics/call_audit.json",
        summary["judge_call_audit"],
    )

    actor_metrics = output_dir / "actor_metrics"
    source_actor_metrics = ORIGINAL_BUNDLE / "actor_metrics"
    for name in (
        "per_episode.csv",
        "summary.json",
        "summary_by_condition.csv",
        "summary_by_benchmark_condition.csv",
        "tool_name_counts.csv",
        "generate.py",
    ):
        copy_verified(source_actor_metrics / name, actor_metrics / name)
    copy_verified(
        source_actor_metrics / "README.md",
        actor_metrics / "source_README.md",
    )
    (actor_metrics / "README.md").write_text(
        "# Actor output-token and tool-call metrics\n\n"
        "These are the actor-side process metrics for the exact 1,000 frozen "
        "Haiku-actor / Opus-researcher trajectories regraded in this bundle. "
        "They are inherited byte-for-byte from the source campaign because "
        "changing only the judge cannot change actor output tokens, model calls, "
        "tool calls, command attempts, or researcher handoffs.\n\n"
        "- `per_episode.csv`: actor tokens and tool calls for every episode.\n"
        "- `summary_by_condition.csv`: five condition-level summaries.\n"
        "- `summary_by_benchmark_condition.csv`: 25 benchmark/condition summaries.\n"
        "- `tool_name_counts.csv`: exact actor tool-name totals.\n"
        "- `summary.json`: definitions, source provenance, and audit.\n"
        "- `source_README.md`: original source-campaign documentation.\n\n"
        "Researcher and judge tokens are excluded from actor token totals. "
        "SciConvBench uses a native non-tool conversation protocol, so its actor "
        "tool-call count is zero by design.\n"
    )

    traces = output_dir / "traces"
    source_traces = ORIGINAL_BUNDLE / "traces"
    copy_verified(
        source_traces / "full-campaign-shared-events.jsonl",
        traces / "shared-events.jsonl",
    )
    copy_verified(
        source_traces / "full-campaign-shared-events-index.csv",
        traces / "shared-events-index.csv",
    )
    copy_verified(
        source_traces / "full-campaign-receipt.json",
        traces / "source-campaign-receipt.json",
    )
    copy_verified(
        source_traces / "full-campaign-manifest.json",
        traces / "source-campaign-manifest.json",
    )
    copy_verified(
        source_traces / "README.md",
        traces / "source_README.md",
    )
    (traces / "README.md").write_text(
        "# Haiku actor / Opus simulator interaction traces\n\n"
        "`shared-events.jsonl` contains one sanitized controller-level shared "
        "conversation record for each of the 1,000 frozen source episodes. It "
        "includes researcher decisions, actor handoffs, clarification exchanges, "
        "submissions, and termination events. `shared-events-index.csv` maps each "
        "task/persona slot to its JSONL line and source checksum.\n\n"
        "These traces are inherited unchanged from the original campaign. The "
        "Astra regrade happened after submission and did not rerun or modify the "
        "Haiku actor or Opus researcher simulator. Raw actor command output, system "
        "prompts, private researcher state, evaluator references, and API payloads "
        "remain excluded.\n"
    )

    metrics_path = output_dir / "evaluations/metrics.jsonl"
    with metrics_path.open("w") as handle:
        for result in sorted(
            regrade_results,
            key=lambda row: (
                BENCHMARKS.index(row["source"]),
                row["task_id"],
                ARMS.index(row["arm"]),
            ),
        ):
            evaluation = result.get("evaluation") or {}
            handle.write(json.dumps({
                "benchmark": result["source"],
                "task_id": result["task_id"],
                "arm": result["arm"],
                "submitted": result["submitted"],
                "score_0_100": result["score_0_100"],
                "judge_calls": result["judge_calls"],
                "regrade_disposition": result["regrade_disposition"],
                "evaluation_status": evaluation.get("status"),
                "evaluator_version": evaluation.get("evaluator_version"),
                "metrics": evaluation.get("metrics") or {},
                "submission_or_trace_sha256": result.get(
                    "submission_or_trace_sha256"
                ),
                "source_state_sha256": result["source_state_sha256"],
            }, ensure_ascii=False, separators=(",", ":")) + "\n")
    (output_dir / "evaluations/README.md").write_text(
        "# Compact evaluations\n\n"
        "`metrics.jsonl` contains one result per episode with scores, native "
        "metrics, judge-call counts, and immutable input hashes. Private judge "
        "prompts/responses and evaluator references are excluded.\n"
    )

    provenance = output_dir / "provenance"
    for name in ("manifest.json", "progress.json", "summary.json", "api_access.json"):
        copy_verified(regrade_dir / name, provenance / f"raw-regrade-{name}")
    for path in sorted(regrade_dir.glob("code.*.json")):
        copy_verified(path, provenance / "code_hashes" / path.name)
    copy_verified(
        ROOT / "scripts/rejudge_main_campaign.py",
        provenance / "rejudge_main_campaign.py",
    )
    copy_verified(
        ROOT / "scripts/run_haiku_opus_astra_rejudge.sh",
        provenance / "run_haiku_opus_astra_rejudge.sh",
    )
    copy_verified(
        Path(__file__),
        provenance / "package_haiku_opus_astra_rejudge_results.py",
    )
    copy_verified(
        ORIGINAL_BUNDLE / "full_campaign_summary.json",
        provenance / "original-opus-judge-summary.json",
    )
    copy_verified(
        SELF_ASTRA_BUNDLE / "summary.json",
        provenance / "self-haiku-astra-summary.json",
    )
    source_run = ROOT / manifest["source_run"]
    copy_verified(
        source_run / "manifest.json",
        provenance / "source-opus-researcher-manifest.json",
    )
    write_json(provenance / "input_receipt.json", {
        "raw_regrade_results": {
            "path": str((regrade_dir / "results.json").relative_to(ROOT)),
            "sha256": sha256(regrade_dir / "results.json"),
            "bytes": (regrade_dir / "results.json").stat().st_size,
        },
        "original_opus_judge_episodes": {
            "path": str(
                (ORIGINAL_BUNDLE / "full_campaign_episodes.csv").relative_to(ROOT)
            ),
            "sha256": sha256(
                ORIGINAL_BUNDLE / "full_campaign_episodes.csv"
            ),
        },
        "self_haiku_astra_episodes": {
            "path": str(
                (SELF_ASTRA_BUNDLE / "episodes.csv").relative_to(ROOT)
            ),
            "sha256": sha256(SELF_ASTRA_BUNDLE / "episodes.csv"),
        },
        "inherited_actor_metrics": {
            "source": str(source_actor_metrics.relative_to(ROOT)),
            "per_episode_sha256": sha256(
                source_actor_metrics / "per_episode.csv"
            ),
        },
        "inherited_interaction_traces": {
            "source": str(
                (
                    source_traces
                    / "full-campaign-shared-events.jsonl"
                ).relative_to(ROOT)
            ),
            "shared_events_sha256": sha256(
                source_traces / "full-campaign-shared-events.jsonl"
            ),
            "shared_events_index_sha256": sha256(
                source_traces
                / "full-campaign-shared-events-index.csv"
            ),
        },
        "raw_regrade_directory_bytes": sum(
            path.stat().st_size
            for path in regrade_dir.rglob("*")
            if path.is_file()
        ),
    })
    for arm in PERSONAS:
        copy_verified(
            ROOT / f"configs/main_run/personas/{arm}.md",
            output_dir / f"{arm}.md",
        )

    files = {
        str(path.relative_to(output_dir)): {
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(output_dir.rglob("*"))
        if path.is_file()
    }
    write_json(output_dir / "bundle_manifest.json", {
        "schema_version": 1,
        "bundle": output_dir.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "episodes": 1000,
        "persona_pairs": 800,
        "files": files,
        "total_bytes_excluding_manifest": sum(
            value["bytes"] for value in files.values()
        ),
    })
    for path in output_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".md", ".json", ".jsonl", ".csv", ".sh", ".py"
        }:
            continue
        if SECRET_PATTERN.search(path.read_text(errors="replace")):
            raise ValueError(f"Credential pattern remained in bundle: {path}")
    print(json.dumps({
        "output_directory": str(output_dir),
        "episodes": len(rows),
        "persona_pairs": len(pair_rows),
        "astra_calls": summary["judge_call_audit"]["total_calls"],
        "total_bytes": sum(
            path.stat().st_size
            for path in output_dir.rglob("*")
            if path.is_file()
        ),
        "astra_means": {
            arm: summary["by_condition"][arm]["astra_mean_score_0_100"]
            for arm in ARMS
        },
        "pooled_persona_effect": summary["persona_effects"]["pooled"][
            "opus_researcher_astra"
        ],
        "pooled_researcher_difference_in_differences": (
            summary["persona_effects"]["pooled"]["difference_in_differences"]
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
