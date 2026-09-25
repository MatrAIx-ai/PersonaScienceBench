"""Pinned ODE task preparation and unchanged native-verifier integration."""

from pathlib import Path
import hashlib
import json
import shutil
import urllib.request

from personasciencebench.adapters.base import SourceConfig
from personasciencebench.adapters.terminal_bench_science import TerminalBenchScienceAdapter, ODE
from personasciencebench.schema import Episode, Submission
from personasciencebench.session import _artifact_file


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def check_sources(source: Path, lock: dict):
    for item in lock["files"]:
        path = source / item["path"]
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or nonregular source: {item['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Pinned source checksum mismatch: {item['path']}")


def fetch_sources(source: Path, lock: dict):
    """Only the fixed repository and exact immutable revision in the lock are used."""
    if lock["repository"] != "https://github.com/harbor-framework/terminal-bench-science":
        raise ValueError("Unexpected source repository")
    revision = lock["revision"]
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("An immutable commit SHA is required")
    for item in lock["files"]:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts or "solution" in relative.parts or "authoring" in relative.parts:
            raise ValueError("Source path is outside the approved fetch scope")
        path = source / relative
        if path.exists():
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError(f"Existing source differs: {relative}")
            continue
        request = urllib.request.Request(
            f"https://raw.githubusercontent.com/harbor-framework/terminal-bench-science/{revision}/{relative.as_posix()}",
            headers={"User-Agent": "PersonaScienceBench-source-preparation"})
        raw = urllib.request.urlopen(request, timeout=60).read()
        if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError(f"Downloaded source differs: {relative}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    check_sources(source, lock)


def prepare(source: Path, output: Path, lock: dict) -> dict:
    """Export only native public files. The full source tree is controller-only."""
    check_sources(source, lock)
    if output.exists():
        raise FileExistsError("Prepare into a fresh output directory")
    source = source.resolve()
    if source.is_relative_to(output.resolve()) or output.resolve().is_relative_to(source):
        raise ValueError("Source and prepared package must use disjoint directory trees")
    adapter = TerminalBenchScienceAdapter(SourceConfig(source, source / "_assets", lock["revision"]))
    episode = adapter.convert(ODE)
    public, controller = output / "actor", output / "controller"
    public.mkdir(parents=True)
    controller.mkdir(mode=0o700)
    task = source / "tasks" / ODE
    shutil.copyfile(task / "instruction.md", public / "instruction.md")
    for asset in episode.assets:
        if asset.visibility != "actor":
            continue
        relative = Path(asset.target_path.lstrip("/"))
        if ".." in relative.parts:
            raise ValueError("Invalid actor asset target")
        destination = public / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset.source_path, destination)
    (public / "collaboration.md").write_text(
        "# Collaboration protocol\n\n"
        "The adjacent instruction.md is the unmodified scientific task. The researcher can discuss "
        "workflow, reporting, numerical_help, and stopping. Questions are optional. "
        "Use the host's ask/report/submit interface; only the host can record artifact evidence. "
        "A first final submission can return review feedback and a response slot before sealing. "
        "The collaboration condition allows six researcher question calls and 40 interaction actions, "
        "with one final response slot added only if a last-action disclosure needs it. "
        "These are interaction limits; the original 28,800-second, 4-CPU, 8-GB scientific allocation "
        "and three required output paths remain unchanged. "
        "Researcher preferences do not alter scientific grading.\n")
    episode.conversion.update(collaboration_version="ode-disclosure-1.0", instruction_change="none",
                              collaboration_addendum="separate actor/collaboration.md",
                              new_collaboration_review_status="authored; external domain review pending")
    write_json(controller / "episode.private.json", episode.model_dump(mode="json"))
    write_json(controller / "source.lock.json", lock)
    record = {
        "source_revision": lock["revision"], "task_id": ODE,
        "native_instruction_sha256": hashlib.sha256((public / "instruction.md").read_bytes()).hexdigest(),
        "native_grader_modified": False, "actor_export": sorted(str(p.relative_to(public)) for p in public.rglob("*") if p.is_file()),
        "deployment_note": "Mount only actor/data at /data, instructions separately, and an empty writable /results. Never mount the source tree, repository, or controller directory into the actor container."
    }
    write_json(controller / "preparation.json", record)
    return record


def native_verify(prepared: Path, artifacts: Path, output: Path):
    """Seal exact files and invoke the existing, unmodified native Docker adapter."""
    from personasciencebench.terminal_native import evaluate
    episode = Episode.model_validate_json((prepared / "controller/episode.private.json").read_text())
    lock = json.loads((prepared / "controller/source.lock.json").read_text())
    task = Path(episode.evaluator.reference["task_path"])
    source = task.parents[len(Path(ODE).parts)]
    check_sources(source, lock)
    if output.exists():
        raise FileExistsError("Verification output must be fresh")
    output.mkdir(parents=True, mode=0o700)
    sealed = output / "sealed"
    sealed.mkdir(mode=0o700)
    mapping = {}
    for name in ["equations.json", "predictions.csv", "report.md"]:
        path = artifacts.resolve() / name
        with _artifact_file(artifacts.resolve(), path) as incoming:
            destination = sealed / name
            with destination.open("xb") as target:
                shutil.copyfileobj(incoming, target)
        destination.chmod(0o400)
        mapping[f"/results/{name}"] = str(destination.resolve())
    submission = Submission(episode_id=episode.id, artifacts=mapping)
    write_json(output / "submission.json", submission.model_dump(mode="json"))
    result = evaluate(episode, submission, output / "native")
    return result.model_dump(mode="json")
