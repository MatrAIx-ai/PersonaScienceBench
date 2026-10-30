"""Prepare source adapters, serve interactions, and run explicitly selected pilots."""

import argparse
import json
import os
from pathlib import Path
import sys

from personasciencebench.adapters.base import read_json
from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.packaging import export_episode, safe_component, write_json
from personasciencebench.registry import ADAPTERS, load_adapter, project_root
from personasciencebench.researcher import Researcher
from personasciencebench.persona import resolve_persona, persona_record
from personasciencebench.schema import Episode, Submission

# Adding an opt-in design track must not broaden existing acquisition/pilot defaults.
DEFAULT_BENCHMARKS = [name for name in ADAPTERS if name != "ideagene"]


def prepare(args):
    selection = read_json(args.selection) if getattr(args, "selection", None) else None
    expected = getattr(args, "cases_per_benchmark", 2)
    if expected < 1:
        raise ValueError("cases_per_benchmark must be positive")
    if selection is not None and set(selection) != set(args.benchmarks):
        raise ValueError("Selection must contain exactly the requested benchmarks")
    args.output.mkdir(parents=True, exist_ok=False)
    args.output.chmod(0o700)
    records = []
    for name in args.benchmarks:
        adapter = load_adapter(name, args.source_root, args.manifest)
        tasks = selection[name] if selection is not None else adapter.pilot_task_ids()
        if not isinstance(tasks, list) or len(tasks) != expected or len(set(tasks)) != expected:
            raise ValueError(f"{name} must supply exactly {expected} distinct reviewed candidates")
        for task_id in tasks:
            if hasattr(adapter, "prepare_assets"):
                adapter.prepare_assets(task_id)
            episode = adapter.convert(task_id)
            records.append(export_episode(episode, args.output / safe_component(episode.id)))
    manifest = {"schema_version": "0.1", "source_root": str(args.source_root.resolve()),
                "source_manifest": str(args.manifest.resolve()), "cases": records,
                "cases_per_benchmark": expected,
                "scientific_runs_started": False, "runtime_tested": False}
    write_json(args.output / "pilot_manifest.json", manifest)
    return {"manifest": str(args.output / "pilot_manifest.json"), "cases": len(records),
            "assets_ready": sum(r["assets_ready"] for r in records),
            "scientific_runs_started": False}


def serve(args):
    from personasciencebench.protocol import server_for
    from personasciencebench.session import EpisodeSession
    episode = Episode.model_validate(read_json(args.episode))
    config = read_json(args.config)
    load_env(args.env_file)
    token = os.environ.get("PERSONASCIENCEBENCH_SESSION_TOKEN", "")
    if len(token) < 24:
        raise ValueError("Set PERSONASCIENCEBENCH_SESSION_TOKEN to an unguessable value of at least 24 characters")
    client = OpenRouterClient(**config["models"]["researcher"], role="researcher")
    researcher = Researcher(episode, client, persona=resolve_persona(config, episode),
                            **config["researcher"])
    session = EpisodeSession(episode, researcher, args.output, artifact_root=args.artifact_root)
    def record(value):
        with (session.output / "api_calls.private.jsonl").open("a") as stream:
            stream.write(json.dumps(value) + "\n")
    client.record = record
    with server_for(session, token, host=args.host, port=args.port) as server:
        print(json.dumps({"endpoint": f"http://{args.host}:{server.server_address[1]}",
                          "episode_id": episode.id}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return {"closed": session.closed}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=project_root() / "external/sources")
    parser.add_argument("--manifest", type=Path, default=project_root() / "manifests/sources.json")
    commands = parser.add_subparsers(dest="command", required=True)
    fetching = commands.add_parser("fetch-sources", help="Download and verify pinned sources and public pilot assets")
    fetching.add_argument("--benchmarks", nargs="+", choices=ADAPTERS, default=DEFAULT_BENCHMARKS)
    provisioning = commands.add_parser("provision-sab", help="Extract reviewed files from a supplied verified ZIP")
    provisioning.add_argument("--archive", type=Path, required=True)
    checking = commands.add_parser("check-runtime", help="Probe the isolated scientific runtime without models")
    checking.add_argument("--actor-python", type=Path, required=True)
    preview = commands.add_parser("persona", help="Preview resolved private persona and prompt offline")
    preview.add_argument("--episode", type=Path, required=True)
    preview.add_argument("--config", type=Path, required=True, help="Explicit model/interaction configuration JSON")
    catalog = commands.add_parser("catalog", help="Enumerate metadata without running tasks or models")
    catalog.add_argument("--benchmarks", nargs="+", choices=ADAPTERS, default=DEFAULT_BENCHMARKS)
    preparation = commands.add_parser("prepare", help="Export explicitly selected reviewed candidates")
    preparation.add_argument("--selection", type=Path, help="JSON mapping benchmark names to reviewed task IDs")
    preparation.add_argument("--cases-per-benchmark", type=int, default=2)
    preparation.add_argument("--benchmarks", nargs="+", choices=ADAPTERS, default=DEFAULT_BENCHMARKS)
    preparation.add_argument("--output", type=Path, required=True)
    serving = commands.add_parser("serve", help="Start a researcher interface for an independent actor")
    serving.add_argument("--episode", type=Path, required=True)
    serving.add_argument("--output", type=Path, required=True)
    serving.add_argument("--artifact-root", type=Path, required=True)
    serving.add_argument("--config", type=Path, required=True, help="Explicit model/interaction configuration JSON")
    serving.add_argument("--env-file", type=Path, default=project_root() / ".env")
    serving.add_argument("--host", default="127.0.0.1")
    serving.add_argument("--port", type=int, default=8765)
    running = commands.add_parser("run", help="Execute selected ready pilots using OpenHands")
    running.add_argument("--prepared", type=Path, required=True)
    running.add_argument("--benchmarks", nargs="+", choices=ADAPTERS, required=True)
    running.add_argument("--output", type=Path, required=True)
    running.add_argument("--actor-python", type=Path, required=True, help="Dedicated actor virtualenv directory")
    running.add_argument("--config", type=Path, required=True, help="Explicit model/interaction configuration JSON")
    running.add_argument("--env-file", type=Path, default=project_root() / ".env")
    running.add_argument("--parallel", type=int, default=2)
    regrading = commands.add_parser("regrade", help="Grade saved submissions without rerunning actors")
    regrading.add_argument("--run", type=Path, required=True)
    regrading.add_argument("--output", type=Path, required=True)
    regrading.add_argument("--replay-from", type=Path, help="Reuse identical completed judgements from this earlier regrade")
    regrading.add_argument("--config", type=Path, required=True, help="Explicit model/interaction configuration JSON")
    regrading.add_argument("--env-file", type=Path, default=project_root() / ".env")
    evaluation = commands.add_parser("evaluate", help="Grade a submitted episode; native requests are never auto-executed")
    evaluation.add_argument("--episode", type=Path, required=True)
    evaluation.add_argument("--submission", type=Path, required=True)
    evaluation.add_argument("--output", type=Path, required=True)
    evaluation.add_argument("--judge-model")
    evaluation.add_argument("--env-file", type=Path, default=project_root() / ".env")
    evaluation.add_argument("--native-request", action="store_true", help="Write a native execution request, without running it")
    ideagene = commands.add_parser("run-ideagene", help="Opt-in text-only IG-Arena review pilot")
    ideagene.add_argument("--config", type=Path, required=True, help="Explicit IdeaGene pilot configuration JSON")
    ideagene.add_argument("--output", type=Path, required=True)
    ideagene.add_argument("--dry-run", action="store_true", help="Verify tasks/profiles and emit plan; no inference")
    ideagene.add_argument("--evaluate-native", action="store_true", help="Run native PES after each sealed submission")
    ideagene.add_argument("--native-python", type=Path, help="Python executable with upstream evaluator dependencies")
    ideagene.add_argument("--env-file", type=Path, default=project_root() / ".env")
    args = parser.parse_args(argv)
    try:
        if args.command == "run-ideagene":
            from personasciencebench.ideagene_runner import pilot_plan, run_pilot
            config = read_json(args.config)
            if args.dry_run:
                adapter = load_adapter("ideagene", args.source_root, args.manifest)
                result = pilot_plan(adapter, config)
                args.output.mkdir(parents=True, exist_ok=False)
                write_json(args.output / "plan.json", result, exclusive=True)
            else:
                load_env(args.env_file)
                result = run_pilot(args.source_root, args.manifest, config, args.output,
                                   evaluate_native=args.evaluate_native, native_python=args.native_python)
        elif args.command == "fetch-sources":
            from personasciencebench.sources import fetch_sources
            result = fetch_sources(args.source_root, args.benchmarks, args.manifest)
        elif args.command == "provision-sab":
            from personasciencebench.registry import source_manifest
            from personasciencebench.scienceagentbench_provision import provision_archive
            spec = source_manifest(args.manifest)["scienceagentbench"]
            assets = args.source_root / spec["assets_directory"]
            result = provision_archive(args.archive, assets / "benchmark_verified",
                                       assets / "data/verified-00000-of-00001.parquet")
        elif args.command == "check-runtime":
            import tempfile
            from personasciencebench.runtime import Sandbox
            with tempfile.TemporaryDirectory(prefix="psb-runtime-check-") as workspace:
                result = Sandbox(Path(workspace), args.actor_python).check()
        elif args.command == "persona":
            episode = Episode.model_validate(read_json(args.episode))
            result = persona_record(resolve_persona(read_json(args.config), episode))
        elif args.command == "catalog":
            result = {}
            for name in args.benchmarks:
                adapter = load_adapter(name, args.source_root, args.manifest)
                result[name] = {"inventory_count": len(adapter.enumerate_tasks()),
                                "pilot_ids": adapter.pilot_task_ids()}
        elif args.command == "prepare":
            result = prepare(args)
        elif args.command == "serve":
            result = serve(args)
        elif args.command == "run":
            from personasciencebench.runner import run_pilots
            load_env(args.env_file)
            result = run_pilots(args.prepared, args.benchmarks, args.output, args.actor_python,
                                read_json(args.config), parallel=args.parallel)
        elif args.command == "regrade":
            from personasciencebench.runner import regrade
            load_env(args.env_file)
            result = regrade(args.run, args.source_root, args.manifest, args.output, read_json(args.config),
                             replay_from=args.replay_from)
        else:
            episode = Episode.model_validate(read_json(args.episode))
            submission = Submission.model_validate(read_json(args.submission))
            adapter = load_adapter(episode.benchmark, args.source_root, args.manifest)
            if args.native_request:
                request = adapter.evaluation_request(episode, submission, args.output.with_suffix(".receipt.json"))
                result = request.model_dump(mode="json")
            else:
                load_env(args.env_file)
                judge = OpenRouterClient(args.judge_model, role="judge") if args.judge_model else None
                result = adapter.evaluate(episode, submission, judge).model_dump(mode="json")
            write_json(args.output, result, exclusive=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        # Transport exceptions are sanitized by the inference boundary.
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
