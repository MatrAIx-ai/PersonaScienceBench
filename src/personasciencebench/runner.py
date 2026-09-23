"""A bounded OpenHands pilot runner; source adapters remain framework independent."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path, PurePosixPath
import shutil
import time

from personasciencebench.adapters.base import read_json, sha256
from personasciencebench.inference import OpenRouterClient, ReplayJudge, preflight
from personasciencebench.packaging import safe_component, write_json
from personasciencebench.registry import load_adapter
from personasciencebench.researcher import Researcher
from personasciencebench.persona import resolve_persona
from personasciencebench.schema import Episode, Submission
from personasciencebench.session import EpisodeSession


def stage_workspace(package: Path, workspace: Path):
    """Copy only allowlisted public assets, preserving their native relative paths."""
    workspace.mkdir(parents=True, exist_ok=False)
    for mount in read_json(package / "controller/mounts.json"):
        logical = PurePosixPath(mount["target_path"])
        if logical.is_absolute() or ".." in logical.parts:
            raise ValueError("The portable Python runner supports only relative input paths")
        source = package / mount["prepared_path"]
        if not source.resolve().is_relative_to((package / "actor/assets").resolve()):
            raise ValueError("Prepared asset is outside the public asset directory")
        for relative, digest in mount["sha256_inventory"].items():
            file = source if relative == "." else source / relative
            if file.is_symlink() or sha256(file) != digest:
                raise ValueError("Prepared asset integrity check failed")
        destination = workspace / str(logical)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    shutil.copy2(package / "actor/task.json", workspace / "task.json")


def run_pilots(prepared: Path, benchmarks: list[str], output: Path, python_root: Path,
               config: dict, *, parallel=2) -> dict:
    if not 1 <= parallel <= 4:
        raise ValueError("parallel must be between one and four")
    # ScienceAgentBench uses an explicitly versioned Bubblewrap environment
    # adaptation with unchanged native graders. Terminal still needs Harbor.
    supported = {"discoverybench", "bixbench", "scienceagentbench"}
    if set(benchmarks) - supported:
        raise ValueError("This runner executes DiscoveryBench, BixBench and the ScienceAgentBench sandbox adaptation; other sources need their runtime bridges")
    manifest = read_json(prepared / "pilot_manifest.json")
    selected = [r for r in manifest["cases"] if r["benchmark"] in benchmarks]
    for name in benchmarks:
        if sum(r["benchmark"] == name for r in selected) != 2:
            raise ValueError(f"The pilot must include exactly two prepared {name} cases")
    if any(not r["assets_ready"] for r in selected):
        raise ValueError("A selected episode has missing or unsafe assets")
    # Resolve all profiles before model/API calls or starting any case.
    profiles = {}
    for record in selected:
        episode = Episode.model_validate(read_json(Path(record["package"]) / "controller/episode.private.json"))
        profiles[episode.id] = resolve_persona(config, episode)
    catalog = preflight(config["models"])
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    write_json(output / "config.json", config)
    write_json(output / "api_preflight.json", catalog)
    # Import and register tools once before worker threads start.
    from personasciencebench.actor import run_actor
    from personasciencebench.runtime import Sandbox

    def one(record):
        started = time.monotonic()
        case = output / safe_component(record["episode_id"])
        case.mkdir(mode=0o700)
        package = Path(record["package"])
        if not package.is_absolute():
            package = package.resolve()
        episode = Episode.model_validate(read_json(package / "controller/episode.private.json"))
        adapter = load_adapter(episode.benchmark, Path(manifest["source_root"]), Path(manifest["source_manifest"]))
        result = {"episode_id": episode.id, "benchmark": episode.benchmark,
                  "source_task_id": episode.source_task_id, "study_id": episode.study_id,
                  "status": "infrastructure_error"}
        try:
            workspace = case / "actor"
            stage_workspace(package, workspace)
            sandbox = Sandbox(workspace.resolve(), python_root.resolve())
            probe = sandbox.check()
            write_json(case / "sandbox_check.json", probe)
            if probe.get("exit_code") != 0:
                raise RuntimeError("Isolated scientific execution runtime failed its startup check")
            def record_api(value):
                with (case / "controller/api_calls.private.jsonl").open("a") as stream:
                    stream.write(json.dumps(value, ensure_ascii=False) + "\n")
            clients = {role: OpenRouterClient(**spec, role=role, record=record_api,
                                             supported_parameters=catalog[role]["supported_parameters"])
                       for role, spec in config["models"].items()}
            researcher = Researcher(episode, clients["researcher"],
                                    persona=profiles[episode.id], **config["researcher"])
            session = EpisodeSession(episode, researcher, case / "controller", artifact_root=workspace)
            actor_result = run_actor(session, clients["actor"], sandbox, max_steps=config["actor_steps"])
            write_json(case / "actor_result.json", actor_result)
            result.update(actor=actor_result, researcher_questions=researcher.questions,
                          disclosed_facts=len(researcher.disclosed))
            if session.submission is None:
                result["status"] = "infrastructure_error" if actor_result.get("status") == "error" else "missing_submission"
            else:
                if episode.benchmark == "scienceagentbench":
                    evaluation = adapter.evaluate_in_sandbox(
                        episode, session.submission, python_root.resolve(), case / "controller/native_evaluation")
                    evaluation.details["judge_model"] = None
                    evaluation.details["judge_kind"] = "native_programmatic_verifier"
                else:
                    evaluation = adapter.evaluate(episode, session.submission, clients["judge"])
                    evaluation.details["judge_model"] = clients["judge"].model
                    evaluation.details["judge_reasoning_effort"] = clients["judge"].reasoning_effort
                if clients["judge"].parameter_adaptations:
                    evaluation.evaluator_version += "+openrouter-provider-defaults-v1"
                    evaluation.details["judge_parameter_adaptations"] = clients["judge"].parameter_adaptations
                    evaluation.details["native_sampling_settings_preserved"] = False
                if clients["judge"].format_adaptations:
                    evaluation.evaluator_version += "+json-fence-v1"
                    evaluation.details["transport_format_adaptations"] = clients["judge"].format_adaptations
                result.update(status=evaluation.status, evaluation=evaluation.model_dump(mode="json"))
                write_json(case / "evaluation.json", evaluation.model_dump(mode="json"))
        except Exception as exc:
            result.update(status="infrastructure_error", error_type=type(exc).__name__, error=str(exc))
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        result["case_directory"] = str(case.resolve())
        write_json(case / "result.json", result)
        return result

    results = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = [pool.submit(one, case) for case in selected]
        for future in as_completed(futures):
            results.append(future.result())
            write_json(output / "results.json", results)
    summary = {"cases": sorted(results, key=lambda r: r["episode_id"]),
               "scored": sum(r["status"] == "scored" for r in results), "requested": len(selected),
               "configuration": config["models"], "cross_benchmark_average": None}
    write_json(output / "summary.json", summary)
    return summary


def regrade(run: Path, source_root: Path, manifest: Path, output: Path, config: dict,
            *, replay_from: Path | None = None) -> dict:
    """Grade immutable saved submissions under one recorded judge configuration."""
    spec = config["models"]["judge"]
    if replay_from and read_json(replay_from / "judge_config.json") != spec:
        raise ValueError("Cannot replay judgements from a different model configuration")
    catalog = preflight({"judge": spec})
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    write_json(output / "judge_config.json", spec)
    write_json(output / "api_preflight.json", catalog)
    results = []
    for case in sorted(run.iterdir()):
        submission_path = case / "controller/submission.json"
        if not submission_path.exists():
            continue
        episode = Episode.model_validate(read_json(case / "controller/episode.private.json"))
        submission = Submission.model_validate(read_json(submission_path))
        hashes = read_json(case / "controller/submission_hashes.json")
        if set(hashes) != set(submission.artifacts):
            raise ValueError("Artifact inventory changed after submission")
        for name, path in submission.artifacts.items():
            if sha256(Path(path)) != hashes[name]:
                raise ValueError("A saved submission artifact changed")
        destination = output / case.name
        destination.mkdir(mode=0o700)
        def record_api(value):
            with (destination / "api_calls.private.jsonl").open("a") as stream:
                stream.write(json.dumps(value, ensure_ascii=False) + "\n")
        judge = OpenRouterClient(**spec, role="judge", record=record_api,
                                 supported_parameters=catalog["judge"]["supported_parameters"])
        if replay_from:
            def record_replay(value):
                with (destination / "api_replay.private.jsonl").open("a") as stream:
                    stream.write(json.dumps(value) + "\n")
            judge = ReplayJudge(judge, replay_from / case.name / "api_calls.private.jsonl", record_replay)
        adapter = load_adapter(episode.benchmark, source_root, manifest)
        evaluation = adapter.evaluate(episode, submission, judge)
        evaluation.evaluator_version += "+configured-judge-v1"
        evaluation.details["judge_model"] = spec["model"]
        evaluation.details["judge_reasoning_effort"] = spec.get("reasoning_effort")
        if judge.parameter_adaptations:
            evaluation.evaluator_version += "+openrouter-provider-defaults-v1"
            evaluation.details["judge_parameter_adaptations"] = judge.parameter_adaptations
            evaluation.details["native_sampling_settings_preserved"] = False
        if judge.format_adaptations:
            evaluation.evaluator_version += "+json-fence-v1"
            evaluation.details["transport_format_adaptations"] = judge.format_adaptations
        record = {"episode_id": episode.id, "benchmark": episode.benchmark,
                  "source_task_id": episode.source_task_id, "original_run": str(case.resolve()),
                  "submission_sha256": sha256(submission_path),
                  "evaluation": evaluation.model_dump(mode="json")}
        write_json(destination / "evaluation.json", record)
        results.append(record)
        write_json(output / "results.json", results)
    summary = {"cases": results, "judge_config": spec,
               "scored": sum(r["evaluation"]["status"] == "scored" for r in results),
               "actor_runs_repeated": 0, "cross_benchmark_average": None}
    write_json(output / "summary.json", summary)
    return summary
