import argparse
import importlib.metadata
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from expbench.paths import ROOT

from expbench.artifacts import write_json
from expbench.budget import Budget
from expbench.gateway import ModelError, OpenRouterTransport
from expbench.mock import MockTransport
from expbench.runner import file_digest, run_episode
from expbench.schema import Config, Design, load_tasks


def read_key_file(path: Path) -> str:
    """Read only a literal OPENROUTER_API_KEY assignment, without executing shell."""
    keys = []
    for line in path.read_text().splitlines():
        name, sep, value = line.strip().partition("=")
        if sep and name.strip() == "OPENROUTER_API_KEY":
            value = value.strip()
            if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            keys.append(value)
    if len(keys) != 1 or not keys[0] or any(c.isspace() for c in keys[0]):
        raise ValueError("Key file must contain exactly one nonempty literal OPENROUTER_API_KEY assignment")
    return keys[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description="EXP-Bench interactive experiment-design pilot")
    parser.add_argument("command", choices=["list", "validate", "run", "regrade"])
    parser.add_argument("--tasks", type=Path, default=(ROOT / "data/design_pilot/tasks.jsonl"))
    parser.add_argument("--config", type=Path, default=(ROOT / "configs/expbench/pilot.toml"))
    parser.add_argument("--task", help="Run just this task ID; otherwise run all cards")
    parser.add_argument("--designs-from", type=Path, help="Existing run directory for regrade; actor is not rerun")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--env-file", type=Path, help="Explicitly read OPENROUTER_API_KEY from a local file")
    parser.add_argument("--output", type=Path, help="New run directory; existing directories are never overwritten")
    args = parser.parse_args(argv)
    try:
        config, tasks = Config.load(args.config), load_tasks(args.tasks)
        if args.task:
            tasks = [t for t in tasks if t.task_id == args.task]
            if not tasks:
                raise ValueError(f"Task not found: {args.task}")
        if args.command == "list":
            for task in tasks:
                print(f"{task.task_id}\t{task.domain}\t{task.public.question}")
            return 0
        if args.command == "validate":
            print(f"Valid configuration and {len(tasks)} task cards. No API calls made.")
            return 0
        designs = {}
        if args.command == "regrade":
            if args.designs_from is None:
                raise ValueError("regrade requires --designs-from RUN_DIRECTORY")
            for task in tasks:
                path = args.designs_from / task.task_id.replace("/", "__") / "design.json"
                designs[task.task_id] = Design.model_validate_json(path.read_text())
        key = ""
        if args.mode == "live":
            key = read_key_file(args.env_file) if args.env_file else os.environ.get("OPENROUTER_API_KEY", "")
        if args.mode == "live" and not key:
            raise ValueError("Set OPENROUTER_API_KEY before a live run; no requests made")
        output = args.output or (ROOT / "runs/expbench") / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + args.mode)
        output.mkdir(parents=True, exist_ok=False)
        # Private transcripts contain task facts. They are not actor workspace files.
        output.chmod(0o700)
        manifest = {
            "mode": args.mode, "command": args.command, "config": config.model_dump(),
            "tasks_sha256": file_digest(args.tasks), "config_sha256": file_digest(args.config),
            "task_ids": [t.task_id for t in tasks],
            "openhands_sdk": importlib.metadata.version("openhands-sdk"),
            "python": sys.version, "started_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": {str(p.relative_to(Path(__file__).parent)): file_digest(p)
                              for p in sorted(Path(__file__).parent.glob("*.py"))},
        }
        if designs:
            manifest["designs_from"] = str(args.designs_from.resolve())
            manifest["design_sha256"] = {
                task.task_id: file_digest(args.designs_from / task.task_id.replace("/", "__") / "design.json")
                for task in tasks
            }
        write_json(output / "manifest.json", manifest)
        budget, results = Budget(config.limits.run_usd), []
        transport = None
        logging.getLogger("httpx").setLevel(logging.WARNING)
        try:
            if args.mode == "live":
                transport = OpenRouterTransport(key, config.limits.request_timeout_seconds)
                roles = ("judge",) if args.command == "regrade" else ("actor", "researcher", "judge")
                models = {r: getattr(config.models, r) for r in roles}
                bounded = config.limits.run_usd is not None or config.limits.episode_usd is not None
                write_json(output / "model_catalog.json", transport.preflight(models, enforce_price_caps=bounded))
                manifest["config"] = config.model_dump()
                write_json(output / "manifest.json", manifest)
            limit_text = f"run limit ${budget.limit:.2f}" if budget.limit is not None else "no run dollar cap"
            print(f"Mode: {args.mode}; {len(tasks)} tasks; {limit_text}; output: {output}", flush=True)
            for task in tasks:
                if args.mode == "mock":
                    transport = MockTransport()  # independent scripted episode
                result = run_episode(task, config, transport, budget,
                                     output / task.task_id.replace("/", "__"),
                                     saved_design=designs.get(task.task_id))
                results.append(result)
                summary = {"mode": args.mode, "results": results,
                           "budget_charge_usd": round(budget.charged, 6),
                           "mock_scores_are_not_benchmark_results": args.mode == "mock"}
                write_json(output / "summary.json", summary)
                print(f"{task.task_id}: {result['status']}; ${result['budget_charge_usd']:.4f}", flush=True)
                # Don't multiply a configuration or provider failure over the pilot.
                if result["status"] != "completed":
                    break
            return 0 if len(results) == len(tasks) and all(r["status"] == "completed" for r in results) else 1
        except Exception as exc:
            safe = str(exc) if isinstance(exc, (ModelError, ValueError)) else type(exc).__name__
            write_json(output / "run_error.json", {"error": safe, "budget_charge_usd": budget.charged})
            raise ModelError(safe) from None
        finally:
            if transport:
                transport.close()
    except (ValueError, OSError, ModelError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
