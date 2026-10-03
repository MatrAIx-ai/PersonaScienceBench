#!/usr/bin/env python3
"""Aggregate the three-trial Haiku actor / Opus collaborator persona pilot."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import random
from statistics import mean
from typing import Any


ARMS = ("persona_off", "candidate_155")
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
DEFAULT_TRIALS = (
    "runs/main/haiku-actor-opus-collab-pilot-20261002-trial-1",
    "runs/main/haiku-actor-opus-collab-pilot-20261002-trial-2",
    "runs/main/haiku-actor-opus-collab-pilot-20261002-trial-3",
)
TIMEOUT_KEY = (1, "expbench", "neurips2024/97609/1", "candidate_155")
ACTOR_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
OPUS_MODEL = "us.anthropic.claude-opus-4-6-v1"


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def confidence_interval(values: list[float]) -> list[float]:
    return [percentile(values, 0.025), percentile(values, 0.975)]


def find_regrades(trial_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    regrades: dict[tuple[str, str], dict[str, Any]] = {}
    for path in trial_dir.glob("episodes/*/*/attempt-1/regrade-v2/results.json"):
        arm = path.parents[2].name
        rows = json.loads(path.read_text())
        if len(rows) != 1:
            raise ValueError(f"Expected one regrade row in {path}, found {len(rows)}")
        row = rows[0]
        evaluation = row.get("evaluation")
        if not evaluation or evaluation.get("status") != "scored":
            raise ValueError(f"Regrade did not score successfully: {path}")
        regrades[(row["source_task_id"], arm)] = evaluation
    return regrades


def timeout_evidence(trial_dir: Path) -> str:
    pattern = (
        "episodes/expbench_neurips2024_97609_1-*/candidate_155/attempt-1/"
        "output/neurips2024__97609__1/actor_events.jsonl"
    )
    paths = list(trial_dir.glob(pattern))
    if len(paths) != 1:
        raise ValueError(f"Expected one timeout event log, found {len(paths)}")
    terminal_detail = "Episode reached its wall-time limit"
    for line in paths[0].read_text().splitlines():
        if terminal_detail in line:
            return str(paths[0])
    raise ValueError(f"Timeout evidence not found in {paths[0]}")


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


def load_records(root: Path, trial_paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    overlays: list[dict[str, Any]] = []
    timeout_log: str | None = None
    selection_hashes: set[str] = set()
    for trial, relative in enumerate(trial_paths, 1):
        trial_dir = root / relative
        manifest = json.loads((trial_dir / "manifest.json").read_text())
        selection_hashes.add(manifest["selection_sha256"])
        if manifest["arms"] != list(ARMS) or manifest["task_count"] != 25:
            raise ValueError(f"Unexpected trial design in {trial_dir / 'manifest.json'}")
        role_models = manifest["role_models"]
        if role_models["actor"]["model"] != ACTOR_MODEL:
            raise ValueError(f"Unexpected actor model in trial {trial}")
        if role_models["researcher"]["model"] != OPUS_MODEL:
            raise ValueError(f"Unexpected researcher model in trial {trial}")
        if role_models["judge"]["model"] != OPUS_MODEL:
            raise ValueError(f"Unexpected judge model in trial {trial}")
        rows = json.loads((trial_dir / "results.json").read_text())
        if len(rows) != 50:
            raise ValueError(f"Trial {trial} has {len(rows)} rows instead of 50")
        regrades = find_regrades(trial_dir)
        for row in rows:
            native_rows = row.get("native_results") or []
            if len(native_rows) != 1:
                raise ValueError(
                    f"Expected one native result for trial {trial} "
                    f"{row['source']} {row['task_id']} {row['arm']}"
                )
            benchmark = row["source"]
            arm = row["arm"]
            task_id = row["task_id"]
            native = dict(native_rows[0])
            raw_native_status = native.get("status")
            normalization = "none"
            regrade = regrades.get((task_id, arm))
            if regrade is not None:
                if benchmark != "discoverybench" or raw_native_status != "error":
                    raise ValueError("Unexpected evaluator-only regrade target")
                native["evaluation"] = regrade
                native["status"] = "scored"
                normalization = "discovery_evaluator_only_regrade_v2"
                overlays.append(
                    {
                        "trial": trial,
                        "benchmark": benchmark,
                        "task_id": task_id,
                        "arm": arm,
                        "raw_status": raw_native_status,
                        "effective_status": "scored",
                        "reason": (
                            "Original actor submission was preserved; the Opus judge returned "
                            "valid scoring counts but omitted a non-scoring explanation field."
                        ),
                    }
                )
            key = (trial, benchmark, task_id, arm)
            if key == TIMEOUT_KEY:
                if raw_native_status != "error" or native.get("initial_submitted"):
                    raise ValueError("Unexpected state for the known EXP wall-time episode")
                timeout_log = timeout_evidence(trial_dir)
                native["status"] = "no_submission"
                native["error"] = "wall_time_limit"
                normalization = "exp_wall_time_model_non_submission"
                overlays.append(
                    {
                        "trial": trial,
                        "benchmark": benchmark,
                        "task_id": task_id,
                        "arm": arm,
                        "raw_status": raw_native_status,
                        "effective_status": "no_submission",
                        "reason": (
                            "Haiku made 59 actor calls but never supplied the required design "
                            "before the episode wall-time limit."
                        ),
                    }
                )
            score = native_score(benchmark, native)
            records.append(
                {
                    "trial": trial,
                    "benchmark": benchmark,
                    "task_id": task_id,
                    "task_key": f"{benchmark}:{task_id}",
                    "arm": arm,
                    "runner_status": row["status"],
                    "raw_native_status": raw_native_status,
                    "effective_status": native["status"],
                    "normalization": normalization,
                    "score_0_100": score,
                    "submitted": submitted(benchmark, native),
                    "actor_calls": actor_calls(native),
                    "researcher_interactions": researcher_interactions(native),
                    "researcher_followups": int(native.get("researcher_followups") or 0),
                    "elapsed_seconds": native.get("elapsed_seconds"),
                }
            )
        unused_regrades = set(regrades) - {
            (record["task_id"], record["arm"])
            for record in records
            if record["trial"] == trial
            and record["normalization"] == "discovery_evaluator_only_regrade_v2"
        }
        if unused_regrades:
            raise ValueError(f"Unused regrades in trial {trial}: {sorted(unused_regrades)}")
    if timeout_log is None:
        raise ValueError("Known EXP wall-time evidence was not processed")
    if len(selection_hashes) != 1:
        raise ValueError(f"Trials used different task selections: {sorted(selection_hashes)}")
    return records, {
        "overlays": overlays,
        "timeout_event_log": timeout_log,
        "selection_sha256": next(iter(selection_hashes)),
    }


def paired_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[(record["trial"], record["task_key"])][record["arm"]] = record
    pairs = []
    for (trial, task_key), arms in sorted(grouped.items()):
        if set(arms) != set(ARMS):
            raise ValueError(f"Pair {trial}/{task_key} has arms {sorted(arms)}")
        off = arms["persona_off"]
        persona = arms["candidate_155"]
        difference = persona["score_0_100"] - off["score_0_100"]
        pairs.append(
            {
                "trial": trial,
                "benchmark": off["benchmark"],
                "task_id": off["task_id"],
                "task_key": task_key,
                "persona_off": off["score_0_100"],
                "candidate_155": persona["score_0_100"],
                "difference": difference,
                "winner": (
                    "candidate_155"
                    if difference > 1e-12
                    else "persona_off"
                    if difference < -1e-12
                    else "tie"
                ),
            }
        )
    return pairs


def bootstrap_task_panel(
    pairs: list[dict[str, Any]],
    *,
    benchmark: str | None,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    selected = [row for row in pairs if benchmark is None or row["benchmark"] == benchmark]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_task[row["task_key"]].append(row)
    task_values: dict[str, tuple[float, float, float]] = {}
    source_tasks: dict[str, list[str]] = defaultdict(list)
    for task_key, rows in by_task.items():
        if len(rows) != 3:
            raise ValueError(f"{task_key} has {len(rows)} trials instead of 3")
        task_values[task_key] = (
            mean(row["persona_off"] for row in rows),
            mean(row["candidate_155"] for row in rows),
            mean(row["difference"] for row in rows),
        )
        source_tasks[rows[0]["benchmark"]].append(task_key)
    expected_sources = [benchmark] if benchmark else list(BENCHMARKS)
    for source in expected_sources:
        if len(source_tasks[source]) != 5:
            raise ValueError(f"{source} has {len(source_tasks[source])} tasks instead of 5")
    rng = random.Random(seed)
    draws = {"persona_off": [], "candidate_155": [], "difference": []}
    for _ in range(samples):
        selected_values = []
        for source in expected_sources:
            tasks = source_tasks[source]
            selected_values.extend(task_values[rng.choice(tasks)] for _ in tasks)
        draws["persona_off"].append(mean(value[0] for value in selected_values))
        draws["candidate_155"].append(mean(value[1] for value in selected_values))
        draws["difference"].append(mean(value[2] for value in selected_values))
    observed = {
        "persona_off": mean(row["persona_off"] for row in selected),
        "candidate_155": mean(row["candidate_155"] for row in selected),
        "difference": mean(row["difference"] for row in selected),
    }
    return {
        "task_count": len(task_values),
        "trial_count": 3,
        "pair_count": len(selected),
        "means": observed,
        "bootstrap_95_ci": {
            key: confidence_interval(values) for key, values in draws.items()
        },
        "bootstrap_samples": samples,
        "bootstrap_unit": (
            "selected task, after averaging the three trials; resampling is stratified "
            "by benchmark for the overall estimate"
        ),
    }


def summarize(
    records: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    def arm_records(benchmark: str | None, arm: str) -> list[dict[str, Any]]:
        return [
            row
            for row in records
            if row["arm"] == arm and (benchmark is None or row["benchmark"] == benchmark)
        ]

    per_benchmark = {}
    for offset, benchmark in enumerate(BENCHMARKS, 1):
        stats = bootstrap_task_panel(
            pairs,
            benchmark=benchmark,
            samples=samples,
            seed=seed + offset,
        )
        stats["submission"] = {
            arm: {
                "count": sum(row["submitted"] for row in arm_records(benchmark, arm)),
                "total": len(arm_records(benchmark, arm)),
                "rate": mean(float(row["submitted"]) for row in arm_records(benchmark, arm)),
            }
            for arm in ARMS
        }
        stats["mean_actor_calls"] = {
            arm: mean(row["actor_calls"] for row in arm_records(benchmark, arm))
            for arm in ARMS
        }
        stats["mean_researcher_interactions"] = {
            arm: mean(row["researcher_interactions"] for row in arm_records(benchmark, arm))
            for arm in ARMS
        }
        source_pairs = [row for row in pairs if row["benchmark"] == benchmark]
        stats["win_tie_loss"] = dict(Counter(row["winner"] for row in source_pairs))
        per_benchmark[benchmark] = stats

    overall = bootstrap_task_panel(
        pairs,
        benchmark=None,
        samples=samples,
        seed=seed,
    )
    overall["submission"] = {
        arm: {
            "count": sum(row["submitted"] for row in arm_records(None, arm)),
            "total": len(arm_records(None, arm)),
            "rate": mean(float(row["submitted"]) for row in arm_records(None, arm)),
        }
        for arm in ARMS
    }
    overall["win_tie_loss"] = dict(Counter(row["winner"] for row in pairs))

    per_trial = {}
    for trial in (1, 2, 3):
        trial_pairs = [row for row in pairs if row["trial"] == trial]
        per_trial[str(trial)] = {
            "persona_off_mean": mean(row["persona_off"] for row in trial_pairs),
            "candidate_155_mean": mean(row["candidate_155"] for row in trial_pairs),
            "difference": mean(row["difference"] for row in trial_pairs),
            "win_tie_loss": dict(Counter(row["winner"] for row in trial_pairs)),
            "submission": {
                arm: {
                    "count": sum(
                        row["submitted"]
                        for row in records
                        if row["trial"] == trial and row["arm"] == arm
                    ),
                    "total": 25,
                }
                for arm in ARMS
            },
        }
    return {
        "overall": overall,
        "per_benchmark": per_benchmark,
        "per_trial": per_trial,
        "effective_status_counts": dict(Counter(row["effective_status"] for row in records)),
        "raw_runner_status_counts": dict(Counter(row["runner_status"] for row in records)),
        "normalization_counts": dict(Counter(row["normalization"] for row in records)),
    }


def fmt(value: float) -> str:
    return f"{value:.2f}"


def interval_text(interval: list[float]) -> str:
    return f"[{interval[0]:.2f}, {interval[1]:.2f}]"


def render_brief(
    summary: dict[str, Any],
    audit: dict[str, Any],
    trial_paths: list[str],
) -> str:
    overall = summary["overall"]
    off = overall["means"]["persona_off"]
    persona = overall["means"]["candidate_155"]
    delta = overall["means"]["difference"]
    delta_ci = overall["bootstrap_95_ci"]["difference"]
    off_submission = overall["submission"]["persona_off"]
    persona_submission = overall["submission"]["candidate_155"]
    lines = [
        "# Haiku actor / Opus collaborator persona pilot",
        "",
        "Run dates: October 2–3, 2026  ",
        "Analysis date: October 3, 2026",
        "",
        "## Summary",
        "",
        f"Across 25 frozen scientific tasks repeated three times, the normalized native "
        f"score was **{off:.2f}/100 with persona off** and **{persona:.2f}/100 with "
        f"`candidate_155`**, a paired difference of **{delta:+.2f} points**. The "
        f"task-bootstrap 95% interval was **{interval_text(delta_ci)}**, so this pilot "
        "does not establish a reliable overall benefit or harm from this persona.",
        "",
        f"The persona arm submitted a gradable answer in **{persona_submission['count']}/"
        f"{persona_submission['total']} episodes ({100 * persona_submission['rate']:.1f}%)**, "
        f"versus **{off_submission['count']}/{off_submission['total']} "
        f"({100 * off_submission['rate']:.1f}%)** with persona off. This completion gap "
        "is itself an agent-behavior result, especially for a weaker actor model.",
        "",
        "Here, **submitted** means that the actor completed the benchmark's required "
        "submission contract and produced an answer that its native evaluator could "
        "grade. It does not merely mean that the runner process finished. For example, "
        "an episode is a non-submission when Haiku reaches its actor-call or wall-time "
        "limit without calling the required submission tool, or when required structured "
        "artifacts are absent. These outcomes are scored zero because successful protocol "
        "completion is part of end-to-end agent performance.",
        "",
        f"The clearest benchmark-specific observation was DiscoveryBench: "
        f"`candidate_155` was lower in "
        f"**{summary['per_benchmark']['discoverybench']['win_tie_loss'].get('persona_off', 0)}/15** "
        "task-trial pairs, tied in the other 8, and was never higher. Its mean difference "
        f"was **{summary['per_benchmark']['discoverybench']['means']['difference']:+.2f} "
        "points**. This is exploratory evidence to replicate on a larger frozen panel, "
        "not yet a benchmark-wide claim.",
        "",
        "## Experimental design",
        "",
        "- Actor: Haiku 4.5 on Amazon Bedrock.",
        "- Simulated researcher and model-based judge: Opus 4.6 on Amazon Bedrock.",
        "- Conditions: `persona_off` versus the fixed `candidate_155` researcher persona.",
        "- Panel: five frozen tasks from each of ASI-Bench, BixBench, DiscoveryBench, "
        "EXP-Bench, and SciConvBench.",
        "- Repeats: three independent trials, producing 150 actor episodes and 75 paired "
        "persona contrasts.",
        "- Scores: each benchmark's primary native metric normalized to 0–100. A genuine "
        "model non-submission is scored zero.",
        "",
        "The persona is applied to the simulated collaborator, not directly to the Haiku "
        "actor. `candidate_155` is a bundled stress-test profile rather than one isolated "
        "trait, so any difference cannot be attributed to age, language, occupation, or "
        "personality separately.",
        "",
        "## Results by benchmark",
        "",
        "| Benchmark | Off | Persona | Paired Δ | Task-bootstrap 95% CI | Valid submissions off | Valid submissions persona |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for benchmark in BENCHMARKS:
        row = summary["per_benchmark"][benchmark]
        lines.append(
            f"| {BENCHMARK_LABELS[benchmark]} | {fmt(row['means']['persona_off'])} | "
            f"{fmt(row['means']['candidate_155'])} | "
            f"{row['means']['difference']:+.2f} | "
            f"{interval_text(row['bootstrap_95_ci']['difference'])} | "
            f"{row['submission']['persona_off']['count']}/15 | "
            f"{row['submission']['candidate_155']['count']}/15 |"
        )
    lines += [
        "",
        "The cross-benchmark average is descriptive because these benchmarks measure "
        "different scientific capabilities. The per-benchmark rows are the primary result.",
        "",
        "## Collaboration behavior",
        "",
        "| Benchmark | Actor calls off | Actor calls persona | Researcher interactions off | Researcher interactions persona |",
        "|---|---:|---:|---:|---:|",
    ]
    for benchmark in BENCHMARKS:
        row = summary["per_benchmark"][benchmark]
        lines.append(
            f"| {BENCHMARK_LABELS[benchmark]} | "
            f"{row['mean_actor_calls']['persona_off']:.2f} | "
            f"{row['mean_actor_calls']['candidate_155']:.2f} | "
            f"{row['mean_researcher_interactions']['persona_off']:.2f} | "
            f"{row['mean_researcher_interactions']['candidate_155']:.2f} |"
        )
    lines += [
        "",
        "Interaction counts are protocol-specific and should be compared within a "
        "benchmark, not pooled across benchmarks. The largest process difference was in "
        "EXP-Bench, where the persona arm used more actor calls; the trial-1 wall-time "
        "non-submission contributes materially to that mean.",
        "",
        "## Repeat stability",
        "",
        "Trials 1, 2, and 3 are independent repeats of the same experiment, not "
        "different experimental conditions. Each used the same frozen 25-task panel, "
        "models, persona arms, prompts, limits, and scoring policy. Every episode began "
        "with a fresh conversation and workspace, with no memory, training, or output "
        "carried over from an earlier trial.",
        "",
        "Their results differ because model generation and multi-step agent trajectories "
        "are stochastic. A small difference in an early response can change later tool "
        "calls, researcher interactions, analyses, and whether a valid answer is "
        "submitted. The variation across repeats therefore measures run-to-run "
        "instability under the same configuration.",
        "",
        "| Trial | Off | Persona | Paired Δ | Submitted off | Submitted persona |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for trial in ("1", "2", "3"):
        row = summary["per_trial"][trial]
        lines.append(
            f"| {trial} | {fmt(row['persona_off_mean'])} | "
            f"{fmt(row['candidate_155_mean'])} | {row['difference']:+.2f} | "
            f"{row['submission']['persona_off']['count']}/25 | "
            f"{row['submission']['candidate_155']['count']}/25 |"
        )
    winner_counts = overall["win_tie_loss"]
    lines += [
        "",
        f"Across the 75 task-trial pairs, `candidate_155` scored higher in "
        f"**{winner_counts.get('candidate_155', 0)}**, lower in "
        f"**{winner_counts.get('persona_off', 0)}**, and tied in "
        f"**{winner_counts.get('tie', 0)}**.",
        "",
        "## Data-quality decisions",
        "",
        "- Two DiscoveryBench submissions in trial 1 were originally marked as "
        "infrastructure errors because the Opus judge omitted a non-scoring JSON "
        "`explanation` field. Evaluator-only regrades preserved the original Haiku "
        "submissions and produced scores of 60 and 75.",
        "- One trial-1 EXP-Bench persona episode made 59 actor calls and reached the "
        "episode wall-time limit without submitting a design. It is counted as a model "
        "non-submission with score zero, not excluded as infrastructure.",
        "- Trials 2 and 3 completed all 50 runner jobs. The same EXP task completed in "
        "both later trials, showing that the first outcome was stochastic weak-model "
        "failure rather than an impossible task.",
        "",
        f"The analysis applies **{len(audit['overlays'])} audited overlays** and leaves "
        "all raw run artifacts unchanged.",
        "",
        "## What this contributes to the paper",
        "",
        "- It tests persona influence under model-capability pressure: a weaker Haiku "
        "actor collaborates with a stronger, fixed Opus researcher.",
        "- It shows why end-to-end persona evaluation should measure completion and "
        "protocol adherence, not only the quality of answers that survive to grading.",
        "- It provides a reusable paired design across five existing scientific-agent "
        "benchmarks without requiring HiL-Bench adoption.",
        "- The current result is a feasibility and variance estimate, not evidence for a "
        "general persona effect.",
        "",
        "## Recommended author claim",
        "",
        "> In a 150-episode pilot using Haiku as the scientific actor and Opus as the "
        "persona-conditioned collaborator and judge, persona conditioning produced "
        "measurable task-level and completion differences, but no stable overall "
        "performance effect on the selected 25-task panel. The result supports studying "
        "persona effects as an interaction between collaborator behavior, actor capability, "
        "and task protocol.",
        "",
        "## Limitations and next experiment",
        "",
        "- Only one complex persona was tested; this cannot identify which persona "
        "attribute caused a behavior change.",
        "- Five tasks per benchmark are enough for a pilot, not for a benchmark-wide "
        "claim. The bootstrap interval reflects the selected task panel after averaging "
        "three repeats.",
        "- The Opus researcher and Opus judge share a model family, which may introduce "
        "model-specific coupling.",
        "- Next, test several pre-registered personas that vary one dimension at a time "
        "and expand the task panel only after freezing the analysis policy.",
        "",
        "## Reproduction and artifacts",
        "",
        "Raw trial directories:",
        "",
    ]
    lines.extend(f"- `{path}`" for path in trial_paths)
    lines += [
        "",
        "Generated analysis artifacts:",
        "",
        "- `analysis/haiku_actor_opus_persona_pilot/episodes.csv`",
        "- `analysis/haiku_actor_opus_persona_pilot/pairs.csv`",
        "- `analysis/haiku_actor_opus_persona_pilot/summary.json`",
        "- `analysis/haiku_actor_opus_persona_pilot/audit.json`",
        "",
        f"Frozen task-selection checksum: `{audit['selection_sha256']}`.",
        "",
        "Analysis command:",
        "",
        "```bash",
        "docker/run.sh .venv/bin/python scripts/report_haiku_opus_persona_pilot.py",
        "```",
        "",
    ]
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_group_writable(paths: list[Path]) -> None:
    """Keep Docker-generated artifacts editable by the host user's shared group."""
    for path in paths:
        path.chmod(path.stat().st_mode | 0o020)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--trials", nargs=3, default=list(DEFAULT_TRIALS))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/haiku_actor_opus_persona_pilot"),
    )
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20261003)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    records, audit = load_records(root, args.trials)
    pairs = paired_records(records)
    if len(records) != 150 or len(pairs) != 75:
        raise ValueError(f"Expected 150 records and 75 pairs, got {len(records)} and {len(pairs)}")
    if Counter(row["benchmark"] for row in records) != Counter(
        {benchmark: 30 for benchmark in BENCHMARKS}
    ):
        raise ValueError("Unexpected benchmark allocation")

    summary = summarize(
        records,
        pairs,
        samples=args.bootstrap_samples,
        seed=args.seed,
    )
    summary["design"] = {
        "actor_model": ACTOR_MODEL,
        "researcher_model": OPUS_MODEL,
        "judge_model": OPUS_MODEL,
        "arms": list(ARMS),
        "benchmarks": list(BENCHMARKS),
        "tasks_per_benchmark": 5,
        "trials": 3,
        "episodes": 150,
        "paired_observations": 75,
        "score_policy": (
            "Primary native benchmark metric normalized to 0-100; genuine model "
            "non-submission scores zero; infrastructure-only failures would be excluded."
        ),
    }
    audit["raw_artifacts_mutated"] = False
    audit["analysis_generated_at"] = "2026-10-03"

    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "episodes.csv", records)
    write_csv(output / "pairs.csv", pairs)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (output / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    brief = render_brief(summary, audit, args.trials)
    (output / "brief.md").write_text(brief)
    docs_path = root / "docs" / "haiku_actor_opus_persona_pilot_brief.md"
    docs_path.write_text(brief)
    make_group_writable([output.parent, output, *output.iterdir(), docs_path])

    print(
        json.dumps(
            {
                "episodes": len(records),
                "pairs": len(pairs),
                "overall": summary["overall"],
                "per_benchmark": {
                    benchmark: {
                        "means": row["means"],
                        "difference_ci": row["bootstrap_95_ci"]["difference"],
                        "submission": row["submission"],
                    }
                    for benchmark, row in summary["per_benchmark"].items()
                },
                "output": str(output),
                "brief": str(docs_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
