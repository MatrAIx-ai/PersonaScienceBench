"""Versioned researcher–actor benchmark; legacy controls remain separately runnable."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.metadata
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from expbench.paths import ROOT

from expbench.artifacts import write_json
from expbench.budget import Budget, Ledger
from expbench.cli import read_key_file
from expbench.design_evaluation import evaluate_design
from expbench.exploration import Sandbox, stage_repository, verify_staged
from expbench.gateway import Gateway, ModelError, OpenRouterTransport
from expbench.original_control import raw_task
from expbench.runner import file_digest
from expbench.schema import Config, load_tasks
from expbench.scoped_researcher import ScopedResearcher
from personasciencebench.persona import Persona, persona_record


class RealisticEpisode:
    def __init__(self, task, config, transport, budget, output, source, *,
                 input_mode="interactive", workflow=False, repeats=3, seconds=2400,
                 runtime_factory=Sandbox):
        if config.collaboration is not None and (workflow or input_mode != "interactive"):
            raise ValueError("Shared collaboration supports the interactive EXP design-only track")
        self.task, self.config, self.output = task, config, Path(output)
        self.input_mode, self.workflow, self.repeats = input_mode, workflow, repeats
        self.output.mkdir(parents=True, exist_ok=False)
        self.output.chmod(0o700)
        self.workspace = self.output / "workspace"
        shutil.copytree(source["repository"], self.workspace, symlinks=True)
        self.runtime = runtime_factory(self.workspace, self.output / "execution.jsonl",
            environment=source.get("environment"), datasets=source.get("datasets"), gpu=source.get("gpu", False))
        self.resources = self.runtime.preflight()
        self.deadline = time.monotonic() + seconds
        self.gateway = Gateway(transport, {r: getattr(config.models, r) for r in ("actor", "researcher", "judge")},
            Ledger(budget, Budget(config.limits.episode_usd)), self.output / "api_calls.jsonl")
        self.researcher = ScopedResearcher(task.researcher, task.public.question, self.gateway,
            config.limits.researcher_questions, self.output / "researcher_history.json",
            persona=config.persona)
        if config.collaboration is not None:
            from expbench.collaboration import initialize
            initialize(self)
        write_json(self.output / "persona.private.json",
                   self.researcher.persona_metadata if config.collaboration is not None
                   else persona_record(config.persona or Persona(enabled=False)))
        self.initial = self.final = self.design = self.failure = self.actor_status = None
        self.actor_calls = 0
        self.reproduction_command = None
        write_json(self.output / "task_snapshot.private.json", task.model_dump())
        write_json(self.output / "runtime.json", self.resources)
        write_json(self.output / "repository_provenance.json", source)
        write_json(self.output / "public_input.json", self.actor_input())

    def actor_input(self):
        if self.input_mode == "original":
            raw, _ = raw_task(self.task.task_id)
            question = raw.get("question", raw.get("hypothesis"))
            context = {"method": raw["method"], "agent_instructions": raw.get("agent_instructions", "")}
        else:
            question, context = self.task.public.question, self.task.public.context
        return {"question": question, "context": context, "environment": self.resources,
                "researcher_topics": list(self.researcher.facts) if self.input_mode == "interactive" else [],
                "question_budget": self.config.limits.researcher_questions if self.input_mode == "interactive" else 0,
                "actor_step_budget": self.config.limits.actor_steps,
                "continue_after_initial_plan": self.workflow}

    def inspect(self, relative):
        if relative == "/workspace":
            relative = "."
        elif relative.startswith("/workspace/"):
            relative = relative[len("/workspace/"):]
        path = (self.workspace / relative).resolve()
        if not path.is_relative_to(self.workspace.resolve()):
            return "Path is outside the task workspace."
        if not path.exists():
            return "Path does not exist."
        if path.is_dir():
            return "\n".join(p.name + ("/" if p.is_dir() else "") for p in sorted(path.iterdir())[:200])
        with path.open("rb") as f:
            content = f.read(24001)
        return content[:24000].decode(errors="replace") + ("\n[truncated]" if len(content) > 24000 else "")

    def execute(self, command, requested_seconds):
        remaining = int(self.deadline - time.monotonic())
        if remaining <= 0:
            raise ModelError("Episode reached its wall-time limit")
        phase = "exploration" if self.initial is None else "implementation"
        seconds = min(requested_seconds, 60 if phase == "exploration" else 600, remaining)
        return self.runtime.execute(command, seconds=seconds, phase=phase)

    def checkpoint(self, stage, plan, conclusion=""):
        if stage not in ("initial", "final") or getattr(self, stage) is not None:
            raise ValueError("Checkpoint is invalid or already recorded")
        if stage == "final" and self.initial is None:
            raise ValueError("Initial checkpoint must precede final checkpoint")
        events = self.output / "actor_events.jsonl"
        checkpoint = {"stage": stage, "plan": plan, "conclusion": conclusion,
            "context": {**self.actor_input(), "disclosed_researcher_facts": list(self.researcher.disclosed.values())},
            "trace": events.read_text() if events.exists() else "No actor events recorded.",
            "actor_calls_at_checkpoint": self.actor_calls,
            "timestamp": datetime.now(timezone.utc).isoformat()}
        setattr(self, stage, checkpoint)
        write_json(self.output / f"{stage}_design.json", checkpoint)


def run_episode(episode, *, validate_execution=False):
    result = {"task_id": episode.task.task_id, "mode": episode.input_mode,
              "workflow_requested": episode.workflow, "mock": episode.gateway.transport.mock,
              "initial": None, "final": None, "execution": None, "error": None}
    try:
        from expbench.realistic_actor import run_actor
        run_actor(episode)
        if episode.failure:
            raise episode.failure
        result["status"] = ("completed" if episode.design is not None else
                            "workflow_incomplete" if episode.initial else "no_submission")
        for stage in ("initial", "final"):
            checkpoint = getattr(episode, stage)
            if checkpoint:
                result[stage] = evaluate_design(episode.gateway, episode.task.task_id, checkpoint,
                                                episode.output / f"{stage}_evaluation", episode.repeats)
        if validate_execution and episode.final and episode.reproduction_command:
            result["execution"] = episode.runtime.validate_reproduction(
                episode.reproduction_command, episode.output / "reproduction")
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc) if isinstance(exc, (ModelError, ValueError)) else type(exc).__name__
    finally:
        result.update(initial_submitted=episode.initial is not None, final_submitted=episode.final is not None,
            actor_calls=episode.actor_calls, researcher_questions=episode.researcher.questions,
            actor_status=episode.actor_status,
            reproduction_command=episode.reproduction_command,
            budget_charge_usd=round(episode.gateway.ledger.episode.charged, 7))
        if episode.config.collaboration is not None:
            from personasciencebench.collaboration import POLICY
            result.update(interaction_protocol=POLICY,
                          researcher_requests=episode.researcher.requests,
                          researcher_followups=max(0, episode.researcher.requests - 1),
                          plan_reviews=episode.researcher.plan_reviews,
                          result_reviews=episode.researcher.result_reviews,
                          collaboration_termination=episode.collaboration_termination)
        write_json(episode.output / "usage.json", episode.gateway.ledger.summary())
        write_json(episode.output / "result.json", result)
    return result


def summarize(results):
    """Explicit denominators; missing judgments remain missing, never disappear."""
    import statistics
    summary = {"attempted": len(results), "completed": sum(r["status"] == "completed" for r in results),
               "mock": any(r["mock"] for r in results), "stages": {}}
    for stage in ("initial", "final"):
        evaluated = [r[stage] for r in results if r.get(stage)]
        scored = [r for r in evaluated if r["coverage_mean"] is not None]
        summary["stages"][stage] = {
            "submitted": sum(r.get(stage + "_submitted", False) for r in results),
            "evaluated": len(evaluated), "numerically_scored": len(scored),
            "missing_evaluation": len(results) - len(evaluated),
            "coverage_mean_on_scored": statistics.mean(r["coverage_mean"] for r in scored) if scored else None,
            "gated_mean_on_scored": statistics.mean(r["gated_coverage_mean"] for r in scored) if scored else None,
            "monitor_pass_fraction_on_scored": statistics.mean(r["monitor_passed"] for r in scored) if scored else None}
    return summary


def prepare(tasks, repositories, output):
    output.mkdir(parents=True, exist_ok=False)
    mappings = {}
    for task in tasks:
        source = repositories[task.task_id]
        raw, _ = raw_task(task.task_id)
        directory = output / task.task_id.replace("/", "__")
        staged = directory / "repository"
        metadata = stage_repository(source["repository"], staged,
                                    raw.get("masked_source", raw.get("source", [])))
        write_json(directory / "staging.json", metadata)
        mappings[task.task_id] = {**source, "repository": str(staged.resolve()),
                                 "staging_manifest": str((directory / "staging.json").resolve())}
    write_json(output / "workspaces.json", mappings)
    return mappings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run"])
    parser.add_argument("--tasks", type=Path, default=(ROOT / "data/realistic_pilot/tasks.jsonl"))
    parser.add_argument("--config", type=Path, default=(ROOT / "configs/expbench/pilot-o3mini.toml"))
    parser.add_argument("--workspace-map", type=Path)
    parser.add_argument("--task")
    parser.add_argument("--parallel", type=int, default=1, help="Concurrent isolated episodes (1–25)")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--input-mode", choices=["interactive", "original"], default="interactive")
    parser.add_argument("--continue-workflow", action="store_true")
    parser.add_argument("--validate-execution", action="store_true")
    parser.add_argument("--judge-repeats", type=int, default=3)
    parser.add_argument("--seconds", type=int, default=2400)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    transport = None
    try:
        if not 1 <= args.parallel <= 25:
            raise ValueError("parallel must be between one and 25")
        if not 1 <= args.judge_repeats <= 10 or args.seconds < 1:
            raise ValueError("Judge repeats must be 1–10 and seconds positive")
        if args.validate_execution and not args.continue_workflow:
            raise ValueError("Execution validation requires --continue-workflow")
        tasks = load_tasks(args.tasks)
        if args.task:
            tasks = [t for t in tasks if t.task_id == args.task]
            if not tasks:
                raise ValueError("Unknown task ID")
        sources = json.loads(args.workspace_map.read_text()) if args.workspace_map else {}
        if args.command == "prepare":
            prepare(tasks, sources, args.output)
            print(f"Prepared {len(tasks)} isolated repository snapshots at {args.output}")
            return 0
        config = Config.load(args.config)
        if args.mode == "live":
            if not sources and not args.continue_workflow and args.input_mode == "interactive":
                prepared = args.output.parent / (args.output.name + "-prepared")
                prepared.mkdir(parents=True, exist_ok=False)
                for task in tasks:
                    directory = prepared / task.task_id.replace("/", "__")
                    workspace = directory / "workspace"
                    workspace.mkdir(parents=True)
                    public_file = workspace / "task.json"
                    write_json(public_file, task.public.model_dump())
                    staging = directory / "staging.json"
                    write_json(staging, {"staging_policy": "automated-public-design-only-v2",
                        "files_sha256": {"task.json": file_digest(public_file)}})
                    sources[task.task_id] = {"repository": str(workspace.resolve()),
                        "staging_manifest": str(staging.resolve()), "design_only": True}
                write_json(prepared / "workspaces.json", sources)
            if any(t.task_id not in sources for t in tasks):
                raise ValueError("Live runs require a prepared workspace mapping for every task")
            for task in tasks:
                sources[task.task_id]["verified_staging_sha256"] = verify_staged(sources[task.task_id])
            key = read_key_file(args.env_file) if args.env_file else os.environ.get("OPENROUTER_API_KEY", "")
            if not key:
                raise ValueError("Set OPENROUTER_API_KEY or supply --env-file; no requests made")
        args.output.mkdir(parents=True, exist_ok=False)
        args.output.chmod(0o700)
        if args.mode == "mock" and not sources:
            fixture = args.output / "fixture_repository"
            fixture.mkdir()
            (fixture / "example.py").write_text("# Synthetic smoke-test fixture, not scientific data.\nprint(2 + 2)\n")
            sources = {t.task_id: {"repository": str(fixture), "fixture": True} for t in tasks}
        manifest = {"version": "realistic-v3.1", "evaluation": "reference-coverage-only", "mode": args.mode, "input_mode": args.input_mode,
            "config": config.model_dump(), "workflow": args.continue_workflow,
            "parallel": args.parallel,
            "persona_enabled": bool(config.persona is not None and config.persona.enabled),
            "judge_repeats": args.judge_repeats, "wall_time_seconds": args.seconds,
            "tasks_sha256": file_digest(args.tasks), "task_ids": [t.task_id for t in tasks],
            "sdk_version": importlib.metadata.version("openhands-sdk"),
            "source_sha256": {p.name: file_digest(p) for p in Path(__file__).parent.glob("*.py")},
            "judge_protocol": "released system+empty user, JSON object, three parse attempts; OpenRouter deployment differs",
            "limitations": ["Modified benchmark, not original paper reproduction",
                "CPU exploration unless GPU and environment provisioned in mapping",
                "Execution replay checks command completion, not scientific validity"]}
        write_json(args.output / "manifest.json", manifest)
        budget, results = Budget(config.limits.run_usd), []
        if args.mode == "live":
            transport = OpenRouterTransport(key, config.limits.request_timeout_seconds)
            roles = ["actor", "judge"] + (["researcher"] if args.input_mode == "interactive" else [])
            catalog = transport.preflight({r: getattr(config.models, r) for r in roles},
                enforce_price_caps=config.limits.run_usd is not None or config.limits.episode_usd is not None)
            write_json(args.output / "model_catalog.json", catalog)
            manifest["config"] = config.model_dump()
            write_json(args.output / "manifest.json", manifest)
        # Register SDK tools once before starting episode threads.
        from expbench.realistic_actor import run_actor

        def one(task):
            episode_transport = transport
            if args.mode == "mock":
                from expbench.realistic_mock import RealisticMock
                episode_transport = RealisticMock()
            task_output = args.output / task.task_id.replace("/", "__")
            try:
                episode = RealisticEpisode(task, config, episode_transport, budget, task_output, sources[task.task_id],
                    input_mode=args.input_mode, workflow=args.continue_workflow,
                    repeats=args.judge_repeats, seconds=args.seconds)
            except (OSError, ValueError, KeyError) as exc:
                result = {"task_id": task.task_id, "status": "runtime_error", "mock": args.mode == "mock",
                    "initial": None, "final": None, "initial_submitted": False, "final_submitted": False,
                    "budget_charge_usd": 0, "error": str(exc), "actor_calls": 0, "researcher_questions": 0}
                task_output.mkdir(parents=True, exist_ok=True)
                write_json(task_output / "result.json", result)
                return result
            return run_episode(episode, validate_execution=args.validate_execution)

        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = [pool.submit(one, task) for task in tasks]
            for future in as_completed(futures):
                if future.cancelled():
                    continue
                result = future.result()
                results.append(result)
                results.sort(key=lambda r: r["task_id"])
                write_json(args.output / "summary.json", {**summarize(results), "scheduled": len(tasks),
                    "parallel": args.parallel, "results": results})
                print(f"{result['task_id']}: {result['status']}; initial={result['initial_submitted']}; final={result['final_submitted']}", flush=True)
                if result["status"] == "error":
                    # Already-running episodes finish; unscheduled inference is stopped.
                    for pending in futures:
                        pending.cancel()
        return 0 if len(results) == len(tasks) and all(r["status"] == "completed" for r in results) else 1
    except (ValueError, OSError, KeyError, ModelError) as exc:
        print(f"Error: {exc}")
        return 1
    finally:
        if transport:
            transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
