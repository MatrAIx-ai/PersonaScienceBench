#!/usr/bin/env python3
"""Create compact, reproducible reports for the completed five-condition campaign."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "runs/main/haiku-actor-opus-five-condition-full-trial-1"
DEFAULT_OUTPUT = ROOT / "haiku_actor_opus_persona_pilot"
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
BENCHMARK_LABELS = {
    "asibench": "ASI-Bench",
    "bixbench": "BixBench",
    "discoverybench": "DiscoveryBench",
    "expbench": "EXP-Bench",
    "sciconvbench": "SciConvBench",
}
ACTOR_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
OPUS_MODEL = "us.anthropic.claude-opus-4-6-v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def confidence_interval(values: list[float]) -> list[float]:
    return [percentile(values, 0.025), percentile(values, 0.975)]


def native_score(benchmark: str, native: dict[str, Any]) -> float:
    status = native.get("status")
    if status in {"missing_submission", "no_submission", "workflow_incomplete"}:
        return 0.0
    evaluation = native.get("evaluation") or {}
    metrics = evaluation.get("metrics") or {}
    if benchmark == "asibench":
        return 100.0 * float(metrics["score"]) / float(metrics["max_score"])
    if benchmark == "bixbench":
        return 100.0 * float(metrics["grade"])
    if benchmark == "discoverybench":
        return 100.0 * float(metrics["final_score"])
    if benchmark == "expbench":
        design = native.get("final") or native.get("initial")
        if design is None:
            raise ValueError("Completed EXP result has no initial or final design")
        return float(design["gated_coverage_mean"])
    if benchmark == "sciconvbench":
        return 100.0 * float(metrics["FRR"])
    raise ValueError(f"Unknown benchmark: {benchmark}")


def submitted(benchmark: str, native: dict[str, Any]) -> bool:
    if benchmark in {"asibench", "bixbench", "discoverybench"}:
        return bool((native.get("actor") or {}).get("submitted"))
    if benchmark == "expbench":
        return bool(native.get("initial_submitted") or native.get("final_submitted"))
    return native.get("status") == "scored"


def actor_calls(native: dict[str, Any]) -> int:
    actor = native.get("actor") or {}
    return int(actor.get("actor_calls", native.get("actor_calls", 0)) or 0)


def researcher_interactions(native: dict[str, Any]) -> int:
    if "researcher_requests" in native:
        return int(native.get("researcher_requests") or 0)
    return int(native.get("researcher_questions") or 0)


def validate_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "arms": list(ARMS),
        "episode_repeats": 1,
        "task_count": 200,
        "episode_count": 1000,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"Unexpected manifest {key}: {manifest.get(key)!r}")
    if set(manifest.get("source_counts") or {}) != set(BENCHMARKS):
        raise ValueError("Manifest does not contain the expected five benchmarks")
    if any(manifest["source_counts"][source] != 40 for source in BENCHMARKS):
        raise ValueError("Expected exactly 40 tasks from each benchmark")
    roles = manifest.get("role_models") or {}
    if (roles.get("actor") or {}).get("model") != ACTOR_MODEL:
        raise ValueError("Unexpected actor model")
    for role in ("researcher", "judge"):
        if (roles.get(role) or {}).get("model") != OPUS_MODEL:
            raise ValueError(f"Unexpected {role} model")


def load_records(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest_path = run_dir / "manifest.json"
    progress_path = run_dir / "progress.json"
    results_path = run_dir / "results.json"
    manifest = json.loads(manifest_path.read_text())
    progress = json.loads(progress_path.read_text())
    validate_manifest(manifest)
    rows = json.loads(results_path.read_text())
    if len(rows) != 1000:
        raise ValueError(f"Expected 1000 results, found {len(rows)}")
    records = []
    for row in rows:
        native_rows = row.get("native_results") or []
        if len(native_rows) != 1:
            raise ValueError(
                f"Expected one native result for {row['source']} {row['task_id']} "
                f"{row['arm']}, found {len(native_rows)}"
            )
        native = native_rows[0]
        benchmark = row["source"]
        score = native_score(benchmark, native)
        actor = native.get("actor") or {}
        collaboration = actor.get("collaboration") or {}
        records.append(
            {
                "benchmark": benchmark,
                "task_id": row["task_id"],
                "task_key": f"{benchmark}:{row['task_id']}",
                "family": row.get("family", ""),
                "subfield": row.get("subfield", ""),
                "study_id": row.get("study_id", ""),
                "arm": row["arm"],
                "attempt": int(row.get("attempt", 1)),
                "runner_status": row.get("status"),
                "native_status": native.get("status"),
                "score_0_100": score,
                "submitted": submitted(benchmark, native),
                "actor_calls": actor_calls(native),
                "execution_calls": int(actor.get("execution_calls", 0) or 0),
                "execution_successes": int(actor.get("execution_successes", 0) or 0),
                "researcher_interactions": researcher_interactions(native),
                "researcher_followups": int(native.get("researcher_followups", 0) or 0),
                "researcher_decisions": int(native.get("researcher_decisions", 0) or 0),
                "termination": collaboration.get("termination", ""),
                "approach_approved": collaboration.get("approach_approved"),
                "elapsed_seconds": native.get("elapsed_seconds"),
            }
        )
    expected_slots = {
        (benchmark, task_id, arm)
        for benchmark, task_id in {
            (record["benchmark"], record["task_id"]) for record in records
        }
        for arm in ARMS
    }
    observed_slots = {
        (record["benchmark"], record["task_id"], record["arm"]) for record in records
    }
    if observed_slots != expected_slots:
        raise ValueError(
            f"Campaign slots are not complete: missing={len(expected_slots - observed_slots)}, "
            f"extra={len(observed_slots - expected_slots)}"
        )
    task_counts = Counter(record["benchmark"] for record in records if record["arm"] == "persona_off")
    if task_counts != Counter({source: 40 for source in BENCHMARKS}):
        raise ValueError(f"Unexpected control task counts: {task_counts}")
    state_paths: dict[tuple[str, str, str], Path] = {}
    for state_path in run_dir.glob("episodes/*/*/state.json"):
        state = json.loads(state_path.read_text())
        state_paths[(state["source"], state["task_id"], state["arm"])] = state_path
    retried_episodes = []
    for record in records:
        if record["attempt"] <= 1:
            continue
        key = (record["benchmark"], record["task_id"], record["arm"])
        state_path = state_paths.get(key)
        if state_path is None:
            raise ValueError(f"Could not find state path for retried episode {key}")
        attempt_one = state_path.parent / "attempt-1"
        native_result_paths = sorted(attempt_one.glob("output/**/result.json"))
        first_statuses = []
        for result_path in native_result_paths:
            result = json.loads(result_path.read_text())
            if isinstance(result, dict) and result.get("status"):
                first_statuses.append(str(result["status"]))
        if any(
            status in {"infrastructure_error", "runtime_error", "error"}
            for status in first_statuses
        ):
            retry_classification = "recorded_infrastructure_or_runtime_failure"
        elif first_statuses:
            retry_classification = "recorded_other_result"
        else:
            retry_classification = "no_native_result_before_resume"
        retried_episodes.append(
            {
                "benchmark": record["benchmark"],
                "task_id": record["task_id"],
                "arm": record["arm"],
                "final_attempt": record["attempt"],
                "first_attempt_native_statuses": first_statuses,
                "retry_classification": retry_classification,
                "final_native_status": record["native_status"],
            }
        )
    retry_counts = Counter(
        item["retry_classification"] for item in retried_episodes
    )
    receipt = {
        "raw_run_directory": str(run_dir.relative_to(ROOT)),
        "manifest": manifest,
        "progress": progress,
        "input_sha256": {
            "manifest.json": sha256(manifest_path),
            "progress.json": sha256(progress_path),
            "results.json": sha256(results_path),
            "selection.csv": sha256(run_dir / "selection.csv"),
        },
        "runner_status_counts": dict(Counter(record["runner_status"] for record in records)),
        "native_status_counts": dict(Counter(record["native_status"] for record in records)),
        "retried_episodes": retried_episodes,
        "retry_classification_counts": dict(retry_counts),
        "analysis_overlays": 0,
        "note": (
            "Attempt-2 rows include recorded infrastructure/runtime failures and slots "
            "whose first attempt produced no native result before a resume. Model "
            "missing/no-submission outcomes were retained as benchmark outcomes and "
            "scored zero."
        ),
    }
    return records, receipt


def paired_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[record["task_key"]][record["arm"]] = record
    pairs = []
    for task_key, arms in sorted(grouped.items()):
        if set(arms) != set(ARMS):
            raise ValueError(f"{task_key} has unexpected arms: {sorted(arms)}")
        control = arms["persona_off"]
        for persona in PERSONAS:
            candidate = arms[persona]
            difference = candidate["score_0_100"] - control["score_0_100"]
            pairs.append(
                {
                    "benchmark": control["benchmark"],
                    "task_id": control["task_id"],
                    "task_key": task_key,
                    "persona": persona,
                    "persona_off": control["score_0_100"],
                    "persona_score": candidate["score_0_100"],
                    "difference": difference,
                    "winner": (
                        persona
                        if difference > 1e-12
                        else "persona_off"
                        if difference < -1e-12
                        else "tie"
                    ),
                    "persona_off_submitted": control["submitted"],
                    "persona_submitted": candidate["submitted"],
                    "actor_calls_difference": (
                        candidate["actor_calls"] - control["actor_calls"]
                    ),
                    "researcher_interactions_difference": (
                        candidate["researcher_interactions"]
                        - control["researcher_interactions"]
                    ),
                }
            )
    if len(pairs) != 800:
        raise ValueError(f"Expected 800 persona/control pairs, found {len(pairs)}")
    return pairs


def bootstrap_comparison(
    pairs: list[dict[str, Any]],
    *,
    persona: str,
    benchmark: str | None,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    selected = [
        row
        for row in pairs
        if row["persona"] == persona
        and (benchmark is None or row["benchmark"] == benchmark)
    ]
    source_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        source_rows[row["benchmark"]].append(row)
    sources = [benchmark] if benchmark else list(BENCHMARKS)
    expected = 40
    for source in sources:
        if len(source_rows[source]) != expected:
            raise ValueError(
                f"{persona}/{source} has {len(source_rows[source])} pairs, expected {expected}"
            )
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        sampled = []
        for source in sources:
            rows = source_rows[source]
            sampled.extend(rng.choice(rows)["difference"] for _ in rows)
        draws.append(mean(sampled))
    differences = [row["difference"] for row in selected]
    return {
        "task_count": len(selected),
        "persona_off_mean": mean(row["persona_off"] for row in selected),
        "persona_mean": mean(row["persona_score"] for row in selected),
        "difference": mean(differences),
        "difference_bootstrap_95_ci": confidence_interval(draws),
        "win_tie_loss": dict(Counter(row["winner"] for row in selected)),
        "bootstrap_samples": samples,
        "bootstrap_unit": (
            "task pair; overall resampling is stratified by benchmark with 40 draws "
            "per benchmark"
        ),
    }


def selected_persona_average_comparison(
    pairs: list[dict[str, Any]],
    *,
    benchmark: str | None,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    selected = [
        row for row in pairs if benchmark is None or row["benchmark"] == benchmark
    ]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_task[row["task_key"]].append(row)
    task_rows = []
    for task_key, rows in by_task.items():
        if {row["persona"] for row in rows} != set(PERSONAS):
            raise ValueError(f"{task_key} does not contain all selected personas")
        task_rows.append(
            {
                "benchmark": rows[0]["benchmark"],
                "persona_off": rows[0]["persona_off"],
                "selected_persona_mean": mean(
                    row["persona_score"] for row in rows
                ),
            }
        )
    for row in task_rows:
        row["difference"] = row["selected_persona_mean"] - row["persona_off"]
    source_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in task_rows:
        source_rows[row["benchmark"]].append(row)
    sources = [benchmark] if benchmark else list(BENCHMARKS)
    for source in sources:
        if len(source_rows[source]) != 40:
            raise ValueError(
                f"Selected-persona average for {source} has "
                f"{len(source_rows[source])} tasks, expected 40"
            )
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        sampled = []
        for source in sources:
            rows = source_rows[source]
            sampled.extend(rng.choice(rows)["difference"] for _ in rows)
        draws.append(mean(sampled))
    return {
        "task_count": len(task_rows),
        "persona_off_mean": mean(row["persona_off"] for row in task_rows),
        "selected_persona_mean": mean(
            row["selected_persona_mean"] for row in task_rows
        ),
        "difference": mean(row["difference"] for row in task_rows),
        "difference_bootstrap_95_ci": confidence_interval(draws),
        "positive_task_count": sum(row["difference"] > 1e-12 for row in task_rows),
        "tie_task_count": sum(abs(row["difference"]) <= 1e-12 for row in task_rows),
        "negative_task_count": sum(row["difference"] < -1e-12 for row in task_rows),
        "bootstrap_samples": samples,
        "bootstrap_unit": (
            "task after averaging the four selected persona scores; overall resampling "
            "is stratified by benchmark"
        ),
    }


def summarize(
    records: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    receipt: dict[str, Any],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    def selected(benchmark: str | None, arm: str) -> list[dict[str, Any]]:
        return [
            row
            for row in records
            if row["arm"] == arm and (benchmark is None or row["benchmark"] == benchmark)
        ]

    def arm_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        elapsed = [
            float(row["elapsed_seconds"])
            for row in rows
            if row["elapsed_seconds"] is not None
        ]
        return {
            "episodes": len(rows),
            "mean_score_0_100": mean(row["score_0_100"] for row in rows),
            "submission_count": sum(row["submitted"] for row in rows),
            "submission_rate": mean(float(row["submitted"]) for row in rows),
            "mean_actor_calls": mean(row["actor_calls"] for row in rows),
            "mean_researcher_interactions": mean(
                row["researcher_interactions"] for row in rows
            ),
            "mean_elapsed_seconds": mean(elapsed) if elapsed else None,
            "native_status_counts": dict(Counter(row["native_status"] for row in rows)),
        }

    overall_arms = {arm: arm_summary(selected(None, arm)) for arm in ARMS}
    comparisons = {}
    for offset, persona in enumerate(PERSONAS, 1):
        comparison = bootstrap_comparison(
            pairs,
            persona=persona,
            benchmark=None,
            samples=samples,
            seed=seed + offset,
        )
        comparison["submission"] = {
            arm: {
                "count": overall_arms[arm]["submission_count"],
                "total": overall_arms[arm]["episodes"],
                "rate": overall_arms[arm]["submission_rate"],
            }
            for arm in ("persona_off", persona)
        }
        comparisons[persona] = comparison
    selected_persona_average = selected_persona_average_comparison(
        pairs,
        benchmark=None,
        samples=samples,
        seed=seed + 50,
    )

    per_benchmark = {}
    for benchmark_index, benchmark in enumerate(BENCHMARKS, 1):
        arms = {arm: arm_summary(selected(benchmark, arm)) for arm in ARMS}
        benchmark_comparisons = {}
        for persona_index, persona in enumerate(PERSONAS, 1):
            benchmark_comparisons[persona] = bootstrap_comparison(
                pairs,
                persona=persona,
                benchmark=benchmark,
                samples=samples,
                seed=seed + 100 * benchmark_index + persona_index,
            )
        per_benchmark[benchmark] = {
            "arms": arms,
            "comparisons_vs_persona_off": benchmark_comparisons,
            "selected_persona_average_vs_persona_off": (
                selected_persona_average_comparison(
                    pairs,
                    benchmark=benchmark,
                    samples=samples,
                    seed=seed + 1000 + benchmark_index,
                )
            ),
        }

    return {
        "analysis": {
            "name": "Haiku actor / Opus collaborator five-condition full campaign",
            "analysis_date": "2026-10-04",
            "trial_count": 1,
            "task_count": 200,
            "tasks_per_benchmark": 40,
            "condition_count": 5,
            "episode_count": 1000,
            "pair_count": 800,
            "score_policy": (
                "Each benchmark's primary native metric is normalized to 0-100; "
                "missing/no-submission model outcomes are scored zero."
            ),
            "uncertainty_policy": (
                "Nonparametric paired task bootstrap. Overall intervals are stratified "
                "by benchmark. Intervals are descriptive and unadjusted for the four "
                "persona comparisons. One trial does not estimate run-to-run variance."
            ),
            "bootstrap_samples": samples,
            "bootstrap_seed": seed,
        },
        "models": receipt["manifest"]["role_models"],
        "overall_by_arm": overall_arms,
        "comparisons_vs_persona_off": comparisons,
        "selected_persona_average_vs_persona_off": selected_persona_average,
        "per_benchmark": per_benchmark,
        "completion": {
            "runner_status_counts": receipt["runner_status_counts"],
            "native_status_counts": receipt["native_status_counts"],
            "retried_episode_count": len(receipt["retried_episodes"]),
            "analysis_overlays": receipt["analysis_overlays"],
        },
        "raw_input_sha256": receipt["input_sha256"],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def interval_text(interval: list[float]) -> str:
    return f"[{interval[0]:.2f}, {interval[1]:.2f}]"


def render_brief(summary: dict[str, Any], receipt: dict[str, Any]) -> str:
    comparisons = summary["comparisons_vs_persona_off"]
    selected_average = summary["selected_persona_average_vs_persona_off"]
    control = summary["overall_by_arm"]["persona_off"]
    ranked = sorted(
        ARMS,
        key=lambda arm: summary["overall_by_arm"][arm]["mean_score_0_100"],
        reverse=True,
    )
    lines = [
        "# Haiku actor / Opus collaborator full campaign",
        "",
        "Run completed: October 4, 2026  ",
        "Analysis date: October 4, 2026",
        "",
        "## Executive summary",
        "",
        "The full campaign completed **all 1,000 planned episodes**: 200 frozen "
        "scientific tasks under persona off and four persona-conditioned collaborator "
        "settings. Haiku 4.5 was the scientific actor; Opus 4.6 was the simulated "
        "researcher and model-based judge.",
        "",
        f"The persona-off control averaged **{control['mean_score_0_100']:.2f}/100**. "
        "The four persona comparisons were:",
        "",
        "| Persona | Mean score | Difference vs off | Paired task-bootstrap 95% CI | "
        "Valid submissions | Win / tie / loss vs off |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for persona in PERSONAS:
        arm = summary["overall_by_arm"][persona]
        comparison = comparisons[persona]
        counts = comparison["win_tie_loss"]
        lines.append(
            f"| `{persona}` | {arm['mean_score_0_100']:.2f} | "
            f"{comparison['difference']:+.2f} | "
            f"{interval_text(comparison['difference_bootstrap_95_ci'])} | "
            f"{arm['submission_count']}/200 | "
            f"{counts.get(persona, 0)} / {counts.get('tie', 0)} / "
            f"{counts.get('persona_off', 0)} |"
        )
    lines += [
        "",
        "These intervals describe variation across this frozen task panel. They are "
        "unadjusted for four persona comparisons, and the single trial does not measure "
        "run-to-run model variance. Accordingly, the campaign is evidence about this "
        "specific model/protocol/task configuration, not a general causal ranking of "
        "human traits.",
        "",
        "## Main findings",
        "",
        "- None of the four overall persona-vs-control intervals excluded zero. The "
        "largest pooled difference was `candidate_003` at "
        f"**{comparisons['candidate_003']['difference']:+.2f} points**, with a 95% "
        f"interval of **{interval_text(comparisons['candidate_003']['difference_bootstrap_95_ci'])}**.",
        "- Averaging the four selected persona conditions within each task produced a "
        f"difference of **{selected_average['difference']:+.2f} points** versus persona "
        f"off, with a 95% interval of "
        f"**{interval_text(selected_average['difference_bootstrap_95_ci'])}**.",
        "- EXP-Bench showed the clearest within-trial pattern: all four persona "
        "conditions were lower than persona off, with differences from **-3.06 to "
        "-10.32 points**. Each unadjusted paired task-bootstrap interval was below zero.",
        "- The pilot's large negative DiscoveryBench result for `candidate_155` did not "
        "replicate on the full 40-task panel: the full-panel difference was "
        f"**{summary['per_benchmark']['discoverybench']['comparisons_vs_persona_off']['candidate_155']['difference']:+.2f} "
        "points** and its interval crossed zero.",
        "- `candidate_046` produced the most valid submissions "
        f"(**{summary['overall_by_arm']['candidate_046']['submission_count']}/200**) "
        "while its mean score was nearly identical to persona off. This separates "
        "protocol completion from answer quality.",
        "",
        "## Experimental design",
        "",
        "- Scientific actor: Claude Haiku 4.5 on Amazon Bedrock.",
        "- Simulated researcher and model-based judge: Claude Opus 4.6 on Bedrock.",
        "- Persona placement: researcher only; the Haiku actor and judge were held fixed.",
        "- Conditions: `persona_off`, `candidate_155`, `candidate_001`, "
        "`candidate_003`, and `candidate_046`.",
        "- Tasks: 40 each from ASI-Bench, BixBench, DiscoveryBench, EXP-Bench, "
        "and SciConvBench.",
        "- Repeats: one trial, yielding 200 episodes per condition and 1,000 total.",
        "- Pairing: every persona result is compared with persona off on the same task.",
        "- Scoring: native benchmark metrics normalized to 0–100; genuine model "
        "non-submissions remain zero.",
        "",
        "A **valid submission** means the actor completed the benchmark's required "
        "submission contract and produced an answer its native evaluator could grade. "
        "It does not merely mean the process exited. Missing submissions caused by actor "
        "step limits, wall-time limits, or absent required artifacts are retained as "
        "zero-score model outcomes.",
        "",
        "## Scores by benchmark",
        "",
        "| Benchmark | Off | 155 | 001 | 003 | 046 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for benchmark in BENCHMARKS:
        arms = summary["per_benchmark"][benchmark]["arms"]
        lines.append(
            f"| {BENCHMARK_LABELS[benchmark]} | "
            + " | ".join(f"{arms[arm]['mean_score_0_100']:.2f}" for arm in ARMS)
            + " |"
        )
    lines += [
        "",
        "## Paired differences by benchmark",
        "",
        "| Benchmark | 155 vs off | 001 vs off | 003 vs off | 046 vs off |",
        "|---|---:|---:|---:|---:|",
    ]
    for benchmark in BENCHMARKS:
        comparisons_by_benchmark = summary["per_benchmark"][benchmark][
            "comparisons_vs_persona_off"
        ]
        lines.append(
            f"| {BENCHMARK_LABELS[benchmark]} | "
            + " | ".join(
                f"{comparisons_by_benchmark[persona]['difference']:+.2f}"
                for persona in PERSONAS
            )
            + " |"
        )
    lines += [
        "",
        "The cross-benchmark average is descriptive because the five benchmark families "
        "measure different scientific capabilities. Benchmark-specific patterns should "
        "be interpreted before the pooled ranking.",
        "",
        "## Submission behavior",
        "",
        "| Benchmark | Off | 155 | 001 | 003 | 046 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for benchmark in BENCHMARKS:
        arms = summary["per_benchmark"][benchmark]["arms"]
        lines.append(
            f"| {BENCHMARK_LABELS[benchmark]} | "
            + " | ".join(
                f"{arms[arm]['submission_count']}/40" for arm in ARMS
            )
            + " |"
        )
    lines += [
        "",
        "Submission differences are part of the measured end-to-end persona effect, "
        "especially with a weaker actor. They should not be filtered out merely because "
        "a successfully submitted answer would have been gradable.",
        "",
        "## Completion and data quality",
        "",
        "- Final accounting: **1,000/1,000 runner jobs finished**.",
        f"- **{len(receipt['retried_episodes'])} slots** completed on attempt 2: "
        f"**{receipt['retry_classification_counts'].get('recorded_infrastructure_or_runtime_failure', 0)}** "
        "had a recorded infrastructure/runtime failure on attempt 1, and "
        f"**{receipt['retry_classification_counts'].get('no_native_result_before_resume', 0)}** "
        "had no native result before the campaign was resumed.",
        "- Model missing/no-submission outcomes were not retried.",
        "- No score was manually changed and no analysis overlay was applied.",
        f"- Raw `results.json` SHA-256: `{receipt['input_sha256']['results.json']}`.",
        "",
        "The attempt-2 slots are listed in `full_campaign_audit.json`. Their first "
        "attempt directories are preserved in the raw run; the compact bundle reports "
        "the completed outcomes.",
        "",
        "## What this contributes to the paper",
        "",
        "- It scales the feasibility pilot to the complete frozen 200-task panel and "
        "four distinct synthetic researcher personas.",
        "- It measures persona effects under capability asymmetry: a weaker Haiku actor "
        "works with a stronger Opus collaborator.",
        "- It treats protocol completion, task score, and collaboration behavior as "
        "joint outcomes rather than analyzing only successful answers.",
        "- It provides paired within-task contrasts across five scientific-agent "
        "benchmarks, reducing task-composition confounding between persona settings.",
        "",
        "## Interpretation boundary",
        "",
        "This is one stochastic trial. The earlier 25-task pilot showed that the same "
        "persona comparison can change direction across fresh repeats. The full campaign "
        "therefore improves task coverage but does not replace replication. The correct "
        "paper framing is a full-panel first trial plus a separate three-repeat variance "
        "pilot—not a definitive population-level persona effect.",
        "",
        "The profiles are high-dimensional synthetic bundles and sometimes contain "
        "internally unusual combinations. A result identifies a condition-level effect; "
        "it cannot isolate age, language, expertise, personality, or any other single "
        "attribute.",
        "",
        "## Condition ranking for this trial",
        "",
    ]
    for index, arm in enumerate(ranked, 1):
        arm_summary = summary["overall_by_arm"][arm]
        suffix = " (control)" if arm == "persona_off" else ""
        lines.append(
            f"{index}. `{arm}`{suffix}: {arm_summary['mean_score_0_100']:.2f}/100, "
            f"{arm_summary['submission_count']}/200 valid submissions."
        )
    lines += [
        "",
        "This ranking is descriptive and should not be read as a stable ordering without "
        "fresh full-panel trials.",
        "",
        "## Files",
        "",
        "- `full_campaign_summary.json`: aggregate statistics and bootstrap intervals.",
        "- `full_campaign_episodes.csv`: one compact row for each of 1,000 episodes.",
        "- `full_campaign_pairs.csv`: 800 same-task persona/control comparisons.",
        "- `full_campaign_audit.json`: raw-input checksums and infrastructure repairs.",
        "- `traces/full-campaign-receipt.json`: compact completion/provenance receipt.",
        "- `report_full_campaign.py`: offline report generator.",
        "- `candidate_*.md`: exact synthetic researcher persona prompts.",
        "",
        "## Reproduce",
        "",
        "From the repository root:",
        "",
        "```bash",
        "docker/run.sh .venv/bin/python "
        "haiku_actor_opus_persona_pilot/report_full_campaign.py",
        "```",
        "",
        "The complete raw run remains at "
        "`runs/main/haiku-actor-opus-five-condition-full-trial-1` and is intentionally "
        "not duplicated in this Git-friendly folder.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20261004)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "traces").mkdir(parents=True, exist_ok=True)

    records, receipt = load_records(run_dir)
    pairs = paired_records(records)
    summary = summarize(
        records,
        pairs,
        receipt,
        samples=args.bootstrap_samples,
        seed=args.seed,
    )

    ordered_records = sorted(
        records,
        key=lambda row: (
            BENCHMARKS.index(row["benchmark"]),
            row["task_id"],
            ARMS.index(row["arm"]),
        ),
    )
    ordered_pairs = sorted(
        pairs,
        key=lambda row: (
            BENCHMARKS.index(row["benchmark"]),
            row["task_id"],
            PERSONAS.index(row["persona"]),
        ),
    )
    write_csv(output_dir / "full_campaign_episodes.csv", ordered_records)
    write_csv(output_dir / "full_campaign_pairs.csv", ordered_pairs)
    (output_dir / "full_campaign_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (output_dir / "full_campaign_audit.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    (output_dir / "full_campaign_brief.md").write_text(
        render_brief(summary, receipt)
    )
    trace_receipt = {
        "campaign": summary["analysis"],
        "manifest": receipt["manifest"],
        "progress": receipt["progress"],
        "input_sha256": receipt["input_sha256"],
        "runner_status_counts": receipt["runner_status_counts"],
        "native_status_counts": receipt["native_status_counts"],
        "retried_episodes": receipt["retried_episodes"],
        "retry_classification_counts": receipt["retry_classification_counts"],
        "compact_outputs_sha256": {},
    }
    for name in (
        "full_campaign_episodes.csv",
        "full_campaign_pairs.csv",
        "full_campaign_summary.json",
        "full_campaign_audit.json",
        "full_campaign_brief.md",
    ):
        trace_receipt["compact_outputs_sha256"][name] = sha256(output_dir / name)
    (output_dir / "traces/full-campaign-receipt.json").write_text(
        json.dumps(trace_receipt, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "output_directory": str(output_dir),
                "episodes": len(records),
                "pairs": len(pairs),
                "runner_status_counts": receipt["runner_status_counts"],
                "retried_episodes": len(receipt["retried_episodes"]),
                "mean_scores": {
                    arm: summary["overall_by_arm"][arm]["mean_score_0_100"]
                    for arm in ARMS
                },
                "differences_vs_persona_off": {
                    persona: summary["comparisons_vs_persona_off"][persona][
                        "difference"
                    ]
                    for persona in PERSONAS
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
