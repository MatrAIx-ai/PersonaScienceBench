"""Controller-side MLAgentBench pilot helpers; neither command calls a model.

`baseline` runs the pristine starter of each prepared MLAgentBench case in the
evaluator sandbox and writes evaluator-private receipts. `summarize` joins a
finished run with those receipts and applies the native strict >10% rule,
reporting attempted/submitted/evaluated/scored counts with explicit
denominators.
"""

import argparse
import json
from pathlib import Path
import sys

from personasciencebench.adapters.base import read_json
from personasciencebench.adapters.mlagentbench import derive_improvement
from personasciencebench.packaging import safe_component, write_json
from personasciencebench.registry import load_adapter
from personasciencebench.schema import Episode


def measure_baselines(prepared: Path, output: Path, *, runs: int = 3,
                      tasks: list[str] | None = None) -> list[dict]:
    manifest = read_json(prepared / "pilot_manifest.json")
    cases = [case for case in manifest["cases"] if case["benchmark"] == "mlagentbench"
             and (not tasks or case["source_task_id"] in tasks)]
    if not cases:
        raise ValueError("No matching prepared MLAgentBench cases")
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    adapter = load_adapter("mlagentbench", Path(manifest["source_root"]),
                           Path(manifest["source_manifest"]))
    summaries = []
    for case in cases:
        episode = Episode.model_validate(
            read_json(Path(case["package"]) / "controller/episode.private.json"))
        receipt = adapter.measure_baseline(episode, output / safe_component(episode.id), runs=runs)
        summaries.append({key: receipt[key] for key in
                          ("episode_id", "runs", "mean", "stdev", "metric", "host")})
    write_json(output / "baselines.json", summaries)
    return summaries


def summarize(run: Path, baselines: Path) -> dict:
    """Denominators follow the native runs-based success rate: every attempted
    episode stays in it, so non-scored episodes count as unsuccessful."""
    receipts = {}
    for path in sorted(baselines.rglob("baseline_receipt.json")):
        receipt = read_json(path)
        if receipt["episode_id"] in receipts:
            raise ValueError(f"Duplicate baseline receipts for {receipt['episode_id']}")
        receipts[receipt["episode_id"]] = receipt
    rows = []
    for path in sorted(run.glob("*/result.json")):
        result = read_json(path)
        if result.get("benchmark") != "mlagentbench":
            continue
        evaluation = result.get("evaluation")
        actor = result.get("actor") or {}
        row = {"episode_id": result["episode_id"], "status": result["status"],
               "submitted": evaluation is not None,
               "evaluated": evaluation is not None and evaluation["status"] in ("scored", "error"),
               "native_score": None, "relative_improvement": None, "success_10pct": None,
               # Process and interaction measures stay separate from the native score.
               "elapsed_seconds": result.get("elapsed_seconds"),
               "actor_calls": actor.get("actor_calls"),
               "execution_calls": actor.get("execution_calls"),
               "researcher_requests": result.get("researcher_requests"),
               "researcher_decisions": result.get("researcher_decisions"),
               "optional_questions": result.get("researcher_questions"),
               "disclosed_facts": result.get("disclosed_facts")}
        if result["status"] == "scored":
            row["native_score"] = evaluation["metrics"]["native_score"]
            receipt = receipts.get(result["episode_id"])
            if receipt is not None:
                row.update(derive_improvement(receipt, row["native_score"]))
            else:
                row["baseline"] = "missing"
        rows.append(row)
    if not rows:
        raise ValueError("The run contains no MLAgentBench case results")
    scored = [row for row in rows if row["status"] == "scored"]
    unresolved = [row["episode_id"] for row in scored if row["success_10pct"] is None]
    successes = sum(row["success_10pct"] is True for row in rows)
    return {
        "counts": {"attempted": len(rows),
                   "submitted": sum(row["submitted"] for row in rows),
                   "evaluated": sum(row["evaluated"] for row in rows),
                   "scored": len(scored)},
        "success_10pct": {"successes": successes, "denominator": len(rows),
                          "rate": None if unresolved else successes / len(rows),
                          "missing_baselines": unresolved},
        "cases": rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    measuring = commands.add_parser("baseline", help="Write evaluator-private baseline receipts")
    measuring.add_argument("--prepared", type=Path, required=True)
    measuring.add_argument("--output", type=Path, required=True)
    measuring.add_argument("--runs", type=int, default=3)
    measuring.add_argument("--tasks", nargs="+", help="Limit to these native task IDs")
    summarizing = commands.add_parser("summarize", help="Join a run with baseline receipts")
    summarizing.add_argument("--run", type=Path, required=True)
    summarizing.add_argument("--baselines", type=Path, required=True)
    summarizing.add_argument("--output", type=Path, help="Also write the summary JSON here")
    args = parser.parse_args(argv)
    try:
        if args.command == "baseline":
            result = measure_baselines(args.prepared, args.output, runs=args.runs, tasks=args.tasks)
        else:
            result = summarize(args.run, args.baselines)
            if args.output:
                write_json(args.output, result, exclusive=True)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
