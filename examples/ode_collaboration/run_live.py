"""Run one real actor with the worked controller; requires configured paid inference.

Uses the existing native-image Docker actor. Its no-network actor policy is an
explicit runtime variant; compare all conditions under the same policy.
"""

import argparse
import json
from pathlib import Path

from personasciencebench.actor import run_actor
from personasciencebench.collaboration.profiles import SciencePersona
from personasciencebench.collaboration.session import CollaborativeSession
from personasciencebench.collaboration.task import write_json
from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.schema import Episode
from personasciencebench.terminal_runner import DockerSandbox
from personasciencebench.terminal_native import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["prepared", "persona", "config", "output"]:
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--max-steps", type=int, default=2000)
    parser.add_argument("--neutral", action="store_true")
    args = parser.parse_args()
    if args.max_steps < 2:
        raise ValueError("Reserve enough actor iterations for review and a response")
    load_env(args.env_file)
    config = json.loads(args.config.read_text())
    spec = config["models"]["actor"]
    catalog = preflight({"actor": spec})
    args.output.mkdir(parents=True, exist_ok=False)
    episode = Episode.model_validate_json((args.prepared / "controller/episode.private.json").read_text())
    profile = SciencePersona.model_validate_json(args.persona.read_text())
    write_json(args.output / "runtime_variant.json", {
        "actor_network": "none", "upstream_actor_network": "public", "max_actor_steps": args.max_steps,
        "original_scientific_wall_time_limit": 28800, "researcher_kind": "deterministic_grounded_templates",
        "interaction_actions": 40, "question_calls": 6, "neutral": args.neutral,
        "note": "A model-step cap and network policy are declared experimental adaptations, not native equivalence."})
    sandbox = None
    try:
        sandbox = DockerSandbox(episode, args.output / "actor", args.output / "image-build.log")
        episode.public.submission["artifact_copy_paths"] = {
            name: f"native_artifacts/artifact_{i}" for i, name in enumerate(sandbox.outputs)}
        episode.public.context += (
            "\nCommands run in the native image; files at the three required /results paths are "
            "copied after each command to /workspace/native_artifacts/artifact_0, artifact_1, artifact_2 "
            "in that order. Submit native absolute keys with these workspace-relative paths as values.")
        def log_api(value):
            with (args.output / "api_calls.private.jsonl").open("a") as stream:
                stream.write(json.dumps(value)+"\n")
        client = OpenRouterClient(**spec, role="actor", record=log_api,
                                  supported_parameters=catalog["actor"]["supported_parameters"])
        session = CollaborativeSession(episode, profile, args.output / "controller",
                                       artifact_root=sandbox.workspace, neutral=args.neutral)
        actor_result = run_actor(session, client, sandbox, max_steps=args.max_steps)
        write_json(args.output / "actor_result.json", actor_result)
        sandbox.close(); sandbox = None
        if session.submission is None:
            write_json(args.output / "scientific_result.json", {
                "status": "no_sealed_submission", "native_reward": None,
                "interaction_status": "incomplete", "reason": actor_result.get("status")})
        else:
            result = evaluate(episode, session.submission, args.output / "native")
            write_json(args.output / "scientific_result.json", result.model_dump(mode="json"))
    finally:
        if sandbox is not None:
            sandbox.close()


if __name__ == "__main__":
    main()
