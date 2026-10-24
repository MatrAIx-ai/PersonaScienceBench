"""Write separate actor and controller packages; never mount raw source trees."""

import json
from pathlib import Path, PurePosixPath
import shutil

from personasciencebench.adapters.base import sha256
from personasciencebench.schema import Episode


def write_json(path: Path, value, *, exclusive: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def safe_component(value: str) -> str:
    """Stable filename without allowing arbitrary path traversal."""
    import hashlib
    import re
    slug = re.sub(r"[^A-Za-z0-9_.-]", "_", value).strip(".")[:100] or "episode"
    return slug + "-" + hashlib.sha256(value.encode()).hexdigest()[:12]


def asset_readiness(episode: Episode) -> dict:
    missing, changed, unsafe = [], [], []
    for asset in episode.assets:
        path = Path(asset.source_path)
        exists = path.is_file() if asset.kind == "file" else path.is_dir()
        if not exists:
            if asset.required:
                missing.append({"asset_id": asset.id, "visibility": asset.visibility,
                                "path": str(path), "acquisition": asset.acquisition})
            continue
        if path.is_symlink() or (path.is_dir() and any(p.is_symlink() for p in path.rglob("*"))):
            unsafe.append(asset.id)
        if asset.sha256 and path.is_file() and sha256(path) != asset.sha256:
            changed.append(asset.id)
    return {"assets_ready": not (missing or changed or unsafe), "missing": missing,
            "hash_mismatches": changed, "symlinks_rejected": unsafe,
            "runtime_tested": False, "model_tested": False}


def export_episode(episode: Episode, output: Path) -> dict:
    """Create a public-only staging directory and separate operator-private records.

    Missing assets do not become fabricated files. Candidate packages remain
    exportable so users can inspect the exact remaining preparation requirements.
    """
    actor_targets = [PurePosixPath(a.target_path) for a in episode.assets if a.visibility == "actor"]
    if len(set(actor_targets)) != len(actor_targets):
        raise ValueError("Actor assets have duplicate target paths")
    for target in actor_targets:
        if ".." in target.parts or "\\" in str(target) or str(target) in (".", "/"):
            raise ValueError("Unsafe asset target path")
    for i, target in enumerate(actor_targets):
        if any(target.is_relative_to(other) or other.is_relative_to(target)
               for other in actor_targets[i + 1:]):
            raise ValueError("Actor asset targets overlap")
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    private = output / "controller"
    public = output / "actor"
    private.mkdir(mode=0o700)
    public.mkdir()
    readiness = asset_readiness(episode)
    if readiness["hash_mismatches"] or readiness["symlinks_rejected"]:
        raise ValueError("Asset integrity failed: " + json.dumps(readiness))
    write_json(private / "episode.private.json", episode.model_dump(mode="json"))
    write_json(private / "researcher.private.json", episode.researcher.model_dump(mode="json"))
    write_json(private / "evaluator.private.json", episode.evaluator.model_dump(mode="json"))
    mounts = []
    for asset in episode.assets:
        if asset.visibility != "actor":
            continue
        target = PurePosixPath(asset.target_path)
        if ".." in target.parts or "\\" in asset.target_path:
            raise ValueError("Unsafe asset target path")
        source = Path(asset.source_path)
        if not source.exists():
            continue
        staged = public / "assets" / safe_component(asset.id)
        staged.parent.mkdir(exist_ok=True)
        if asset.kind == "directory":
            shutil.copytree(source, staged, symlinks=False)
            inventory = {str(p.relative_to(staged)): sha256(p)
                         for p in sorted(staged.rglob("*")) if p.is_file()}
        else:
            shutil.copy2(source, staged)
            inventory = {".": sha256(staged)}
        mounts.append({"asset_id": asset.id, "prepared_path": str(staged.relative_to(output)),
                       "target_path": asset.target_path, "read_only": True,
                       "sha256_inventory": inventory})
    actor_input = episode.actor_input()
    actor_input["input_assets"] = [{"asset_id": m["asset_id"], "target_path": m["target_path"]}
                                   for m in mounts]
    write_json(public / "task.json", actor_input)
    write_json(private / "mounts.json", mounts)
    write_json(private / "readiness.json", readiness)
    return {"episode_id": episode.id, "benchmark": episode.benchmark,
            "source_task_id": episode.source_task_id, "study_id": episode.study_id,
            "package": str(output.resolve()), "review_status": episode.review_status,
            "fact_count": len(episode.researcher.facts), **readiness}
