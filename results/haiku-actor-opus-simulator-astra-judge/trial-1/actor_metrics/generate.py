#!/usr/bin/env python3
"""Aggregate actor token usage and tool calls for the completed full campaign."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = ROOT / "runs/main/haiku-actor-opus-five-condition-full-trial-1"
DEFAULT_BUNDLE = ROOT / "haiku_actor_opus_persona_pilot"
ARMS = (
    "persona_off",
    "candidate_155",
    "candidate_001",
    "candidate_003",
    "candidate_046",
)
BENCHMARKS = (
    "asibench",
    "bixbench",
    "discoverybench",
    "expbench",
    "sciconvbench",
)


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def one_log(attempt_dir: Path, names: tuple[str, ...]) -> Path | None:
    candidates = []
    for name in names:
        candidates.extend(attempt_dir.glob(f"**/controller/{name}"))
        candidates.extend(attempt_dir.glob(f"**/{name}"))
    unique = sorted(set(path.resolve() for path in candidates if path.is_file()))
    if len(unique) > 1:
        controller = [path for path in unique if path.parent.name == "controller"]
        if len(controller) == 1:
            return controller[0]
        raise ValueError(f"Found multiple candidate logs under {attempt_dir}: {unique}")
    return unique[0] if unique else None


def retry_count(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("count", "retries", "attempts"):
            if isinstance(value.get(key), int):
                return int(value[key])
    return 0


def actor_usage(path: Path) -> dict[str, int]:
    totals = Counter()
    with path.open(errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("role") != "actor":
                continue
            totals["actor_api_log_rows"] += 1
            usage = row.get("usage") or (row.get("response") or {}).get("usage") or {}
            if not any(
                key in usage
                for key in ("prompt_tokens", "completion_tokens", "total_tokens")
            ):
                continue
            details = usage.get("prompt_tokens_details") or {}
            totals["actor_api_calls"] += 1
            totals["actor_input_tokens"] += int(usage.get("prompt_tokens", 0) or 0)
            totals["actor_output_tokens"] += int(
                usage.get("completion_tokens", 0) or 0
            )
            totals["actor_total_tokens"] += int(
                usage.get(
                    "total_tokens",
                    int(usage.get("prompt_tokens", 0) or 0)
                    + int(usage.get("completion_tokens", 0) or 0),
                )
                or 0
            )
            totals["actor_cache_read_tokens"] += int(
                details.get("cache_read_tokens", 0) or 0
            )
            totals["actor_cache_write_tokens"] += int(
                details.get("cache_write_tokens", 0) or 0
            )
            totals["actor_automatic_retries"] += retry_count(
                row.get("automatic_retries")
            )
    return dict(totals)


def actor_tools(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "actor_tool_calls": 0,
            "execute_command_calls": 0,
            "collaboration_handoff_calls": 0,
            "other_tool_calls": 0,
            "tool_name_counts": {},
        }
    names: Counter[str] = Counter()
    with path.open(errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("kind") != "ActionEvent":
                continue
            tool_name = event.get("tool_name")
            if tool_name:
                names[str(tool_name)] += 1
    known = names["execute_command"] + names["end_researcher_turn"]
    return {
        "actor_tool_calls": sum(names.values()),
        "execute_command_calls": names["execute_command"],
        "collaboration_handoff_calls": names["end_researcher_turn"],
        "other_tool_calls": sum(names.values()) - known,
        "tool_name_counts": dict(names),
    }


def load_episode_metadata(bundle_dir: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    path = bundle_dir / "full_campaign_episodes.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1000:
        raise ValueError(f"Expected 1000 compact episode rows, found {len(rows)}")
    return {
        (row["benchmark"], row["task_id"], row["arm"]): row for row in rows
    }


def aggregate(run_dir: Path, bundle_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata = load_episode_metadata(bundle_dir)
    states = []
    for state_path in run_dir.glob("episodes/*/*/state.json"):
        state = json.loads(state_path.read_text())
        states.append((state, state_path))
    if len(states) != 1000:
        raise ValueError(f"Expected 1000 final state files, found {len(states)}")

    rows = []
    api_sources = Counter()
    actor_event_sources = Counter()
    for state, state_path in states:
        key = (state["source"], state["task_id"], state["arm"])
        meta = metadata.get(key)
        if meta is None:
            raise ValueError(f"State has no compact episode metadata: {key}")
        attempt = int(state["attempt"])
        attempt_dir = state_path.parent / f"attempt-{attempt}" / "output"
        api_path = one_log(
            attempt_dir, ("api_calls.private.jsonl", "api_calls.jsonl")
        )
        if api_path is None:
            raise ValueError(f"No API usage log for final episode {key}")
        actor_event_path = one_log(attempt_dir, ("actor_events.jsonl",))
        usage = actor_usage(api_path)
        tools = actor_tools(actor_event_path)
        api_sources[api_path.name] += 1
        if actor_event_path is None:
            actor_event_sources["none"] += 1
            tool_count_source = "non_tool_sciconv_protocol"
        else:
            actor_event_sources[actor_event_path.name] += 1
            tool_count_source = "openhands_action_events"
        actor_api_calls = int(usage.get("actor_api_calls", 0))
        output_tokens = int(usage.get("actor_output_tokens", 0))
        row = {
            "benchmark": state["source"],
            "task_id": state["task_id"],
            "arm": state["arm"],
            "attempt": attempt,
            "native_status": meta["native_status"],
            "submitted": meta["submitted"],
            "score_0_100": meta["score_0_100"],
            "recorded_actor_calls": int(meta["actor_calls"]),
            "actor_api_log_rows": int(usage.get("actor_api_log_rows", 0)),
            "actor_api_calls": actor_api_calls,
            "actor_input_tokens": int(usage.get("actor_input_tokens", 0)),
            "actor_output_tokens": output_tokens,
            "actor_total_tokens": int(usage.get("actor_total_tokens", 0)),
            "actor_output_tokens_per_model_call": (
                output_tokens / actor_api_calls if actor_api_calls else 0.0
            ),
            "actor_cache_read_tokens": int(
                usage.get("actor_cache_read_tokens", 0)
            ),
            "actor_cache_write_tokens": int(
                usage.get("actor_cache_write_tokens", 0)
            ),
            "actor_automatic_retries": int(
                usage.get("actor_automatic_retries", 0)
            ),
            "actor_tool_calls": tools["actor_tool_calls"],
            "execute_command_calls": tools["execute_command_calls"],
            "collaboration_handoff_calls": tools[
                "collaboration_handoff_calls"
            ],
            "other_tool_calls": tools["other_tool_calls"],
            "recorded_execution_calls": int(meta["execution_calls"]),
            "recorded_execution_successes": int(meta["execution_successes"]),
            "tool_count_source": tool_count_source,
            "tool_name_counts": json.dumps(
                tools["tool_name_counts"], sort_keys=True, separators=(",", ":")
            ),
            "api_usage_log": str(api_path.relative_to(ROOT)),
            "api_usage_log_sha256": sha256(api_path),
            "actor_event_log": (
                str(actor_event_path.relative_to(ROOT))
                if actor_event_path is not None
                else ""
            ),
            "actor_event_log_sha256": (
                sha256(actor_event_path) if actor_event_path is not None else ""
            ),
        }
        rows.append(row)

    observed = {(row["benchmark"], row["task_id"], row["arm"]) for row in rows}
    if observed != set(metadata):
        raise ValueError(
            f"Metric slots differ from episode table: "
            f"missing={len(set(metadata) - observed)}, extra={len(observed - set(metadata))}"
        )
    rows.sort(
        key=lambda row: (
            BENCHMARKS.index(row["benchmark"]),
            row["task_id"],
            ARMS.index(row["arm"]),
        )
    )
    actor_call_mismatches = [
        {
            "benchmark": row["benchmark"],
            "task_id": row["task_id"],
            "arm": row["arm"],
            "recorded_actor_calls": row["recorded_actor_calls"],
            "actor_api_calls": row["actor_api_calls"],
        }
        for row in rows
        if row["recorded_actor_calls"] != row["actor_api_calls"]
    ]
    execution_mismatches = [
        {
            "benchmark": row["benchmark"],
            "task_id": row["task_id"],
            "arm": row["arm"],
            "recorded_execution_calls": row["recorded_execution_calls"],
            "execute_command_attempts": row["execute_command_calls"],
            "difference": (
                row["execute_command_calls"] - row["recorded_execution_calls"]
            ),
        }
        for row in rows
        if row["recorded_execution_calls"] != row["execute_command_calls"]
    ]
    audit = {
        "episodes": len(rows),
        "api_log_sources": dict(api_sources),
        "actor_event_sources": dict(actor_event_sources),
        "actor_call_count_mismatch_count": len(actor_call_mismatches),
        "actor_call_count_mismatch_by_benchmark": dict(
            Counter(row["benchmark"] for row in actor_call_mismatches)
        ),
        "actor_call_count_mismatch_examples": actor_call_mismatches[:20],
        "execute_attempt_vs_recorded_execution_mismatch_count": len(
            execution_mismatches
        ),
        "execute_attempt_vs_recorded_execution_mismatch_by_benchmark": dict(
            Counter(row["benchmark"] for row in execution_mismatches)
        ),
        "execute_attempt_minus_recorded_execution_distribution": dict(
            Counter(row["difference"] for row in execution_mismatches)
        ),
        "execute_attempt_vs_recorded_execution_examples": execution_mismatches[:20],
        "execution_metric_note": (
            "execute_command_calls counts model-issued OpenHands ActionEvents. "
            "recorded_execution_calls counts commands that reached the controller and "
            "returned far enough to be appended to its execution ledger. The former can "
            "therefore exceed the latter when a call is rejected or errors before a "
            "recorded result."
        ),
    }
    return rows, audit


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output = [float(row["actor_output_tokens"]) for row in rows]
    tools = [float(row["actor_tool_calls"]) for row in rows]
    execution = [float(row["execute_command_calls"]) for row in rows]
    recorded_execution = [float(row["recorded_execution_calls"]) for row in rows]
    handoffs = [float(row["collaboration_handoff_calls"]) for row in rows]
    model_calls = [float(row["actor_api_calls"]) for row in rows]
    return {
        "episodes": len(rows),
        "actor_output_tokens_total": int(sum(output)),
        "actor_output_tokens_mean_per_episode": mean(output),
        "actor_output_tokens_median_per_episode": median(output),
        "actor_output_tokens_p25_per_episode": percentile(output, 0.25),
        "actor_output_tokens_p75_per_episode": percentile(output, 0.75),
        "actor_model_calls_mean_per_episode": mean(model_calls),
        "actor_tool_calls_mean_per_episode": mean(tools),
        "actor_tool_calls_median_per_episode": median(tools),
        "execute_command_attempts_mean_per_episode": mean(execution),
        "recorded_execution_calls_mean_per_episode": mean(recorded_execution),
        "collaboration_handoff_calls_mean_per_episode": mean(handoffs),
    }


def summaries(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_arm = []
    for arm in ARMS:
        selected = [row for row in rows if row["arm"] == arm]
        by_arm.append({"arm": arm, **summarize_group(selected)})
    by_benchmark_arm = []
    for benchmark in BENCHMARKS:
        for arm in ARMS:
            selected = [
                row
                for row in rows
                if row["benchmark"] == benchmark and row["arm"] == arm
            ]
            by_benchmark_arm.append(
                {
                    "benchmark": benchmark,
                    "arm": arm,
                    **summarize_group(selected),
                }
            )
    return by_arm, by_benchmark_arm


def tool_name_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for benchmark in ("all", *BENCHMARKS):
        for arm in ARMS:
            selected = [
                row
                for row in rows
                if row["arm"] == arm
                and (benchmark == "all" or row["benchmark"] == benchmark)
            ]
            counts: Counter[str] = Counter()
            for row in selected:
                counts.update(json.loads(row["tool_name_counts"]))
            for tool_name, total in sorted(counts.items()):
                output.append(
                    {
                        "benchmark": benchmark,
                        "arm": arm,
                        "tool_name": tool_name,
                        "calls_total": total,
                        "calls_mean_per_episode": total / len(selected),
                        "episodes": len(selected),
                    }
                )
    return output


def render_readme(summary: dict[str, Any]) -> str:
    lines = [
        "# Actor token and tool-call metrics",
        "",
        "This folder reports actor-only resource usage for the completed "
        "1,000-episode Haiku actor / Opus collaborator campaign.",
        "",
        "## Definitions",
        "",
        "- **Actor output tokens per episode:** sum of Bedrock "
        "`completion_tokens` for API log rows whose role is `actor`. Researcher and "
        "judge tokens are excluded.",
        "- **Actor model calls:** number of final-attempt, usage-bearing API response "
        "records whose role is `actor`. EXP-Bench also logs a request/reservation row "
        "for each call; those rows have no usage and are not double-counted.",
        "- **Actor tool calls:** model-issued OpenHands `ActionEvent` records with a "
        "non-empty `tool_name`.",
        "- **Command attempts:** actor tool calls named `execute_command`.",
        "- **Recorded executions:** commands that reached the controller and returned "
        "far enough to enter its execution ledger. This can be lower than command "
        "attempts when a call is rejected or errors first.",
        "- **Collaboration handoffs:** actor tool calls named "
        "`end_researcher_turn`.",
        "- SciConvBench uses its native non-tool conversational protocol, so its "
        "actor tool-call count is zero and is labeled "
        "`non_tool_sciconv_protocol`.",
        "",
        "Only aggregate usage fields and checksums are exported. The private API "
        "request/response logs are not copied into this folder.",
        "",
        "## Mean metrics by condition",
        "",
        "| Condition | Output tokens / episode | Actor model calls / episode | "
        "Actor tool calls / episode | Command attempts / episode | "
        "Recorded executions / episode |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary["by_condition"]:
        lines.append(
            f"| `{row['arm']}` | "
            f"{row['actor_output_tokens_mean_per_episode']:.1f} | "
            f"{row['actor_model_calls_mean_per_episode']:.2f} | "
            f"{row['actor_tool_calls_mean_per_episode']:.2f} | "
            f"{row['execute_command_attempts_mean_per_episode']:.2f} | "
            f"{row['recorded_execution_calls_mean_per_episode']:.2f} |"
        )
    lines += [
        "",
        "These are descriptive one-trial process metrics. Different benchmark "
        "protocols require very different numbers of model and tool calls, so use "
        "`summary_by_benchmark_condition.csv` for within-benchmark comparisons.",
        "",
        "## Files",
        "",
        "- `per_episode.csv`: actor tokens and tool calls for every episode.",
        "- `summary_by_condition.csv`: five condition-level summaries.",
        "- `summary_by_benchmark_condition.csv`: 25 benchmark/condition summaries.",
        "- `tool_name_counts.csv`: exact tool-name totals and per-episode means.",
        "- `summary.json`: definitions, provenance, aggregate results, and audit.",
        "- `generate.py`: reproducible offline generator.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "docker/run.sh .venv/bin/python "
        "haiku_actor_opus_persona_pilot/actor_metrics/generate.py",
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    bundle_dir = args.bundle_dir.resolve()
    output_dir = bundle_dir / "actor_metrics"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows, audit = aggregate(run_dir, bundle_dir)
    by_condition, by_benchmark_condition = summaries(rows)
    tool_name_counts = tool_name_summaries(rows)
    write_csv(output_dir / "per_episode.csv", rows)
    write_csv(output_dir / "summary_by_condition.csv", by_condition)
    write_csv(
        output_dir / "summary_by_benchmark_condition.csv",
        by_benchmark_condition,
    )
    write_csv(output_dir / "tool_name_counts.csv", tool_name_counts)
    summary = {
        "campaign": {
            "run_directory": str(run_dir.relative_to(ROOT)),
            "episodes": 1000,
            "actor_model": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "researcher_and_judge_model": "us.anthropic.claude-opus-4-6-v1",
        },
        "definitions": {
            "actor_output_tokens": (
                "Sum of provider-reported completion_tokens for role=actor API "
                "records in the final attempt."
            ),
            "actor_tool_calls": (
                "Count of model-issued OpenHands ActionEvent records with non-empty "
                "tool_name; SciConvBench has zero because it uses a native non-tool "
                "protocol."
            ),
            "execute_command_calls": (
                "Attempted subset of actor_tool_calls with "
                "tool_name=execute_command."
            ),
            "recorded_execution_calls": (
                "Commands that reached the controller and returned far enough to enter "
                "its execution ledger."
            ),
            "collaboration_handoff_calls": (
                "Subset of actor_tool_calls with tool_name=end_researcher_turn."
            ),
        },
        "by_condition": by_condition,
        "by_benchmark_condition": by_benchmark_condition,
        "tool_name_counts": tool_name_counts,
        "audit": audit,
        "input_sha256": {
            "full_campaign_episodes.csv": sha256(
                bundle_dir / "full_campaign_episodes.csv"
            ),
            "raw_manifest.json": sha256(run_dir / "manifest.json"),
            "raw_results.json": sha256(run_dir / "results.json"),
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (output_dir / "README.md").write_text(render_readme(summary))
    summary["output_sha256"] = {
        name: sha256(output_dir / name)
        for name in (
            "per_episode.csv",
            "summary_by_condition.csv",
            "summary_by_benchmark_condition.csv",
            "tool_name_counts.csv",
            "README.md",
        )
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "output_directory": str(output_dir),
                "episodes": len(rows),
                "actor_call_count_mismatches": audit[
                    "actor_call_count_mismatch_count"
                ],
                "execution_count_mismatches": audit[
                    "execute_attempt_vs_recorded_execution_mismatch_count"
                ],
                "by_condition": by_condition,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
