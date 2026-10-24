"""Explicit, pinned source acquisition; conversion itself stays offline."""

from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import urllib.request

from personasciencebench.adapters.base import sha256
from personasciencebench.registry import source_manifest


def _inside(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in relative:
        raise ValueError("Source manifest paths must be relative and contained")
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()) or target.is_symlink():
        raise ValueError("Source manifest target escapes its directory")
    return target


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.PIPE).strip()


def _verify_repository(path: Path, revision: str):
    if _git("-C", str(path), "rev-parse", "HEAD") != revision:
        raise ValueError(f"Existing checkout has a different revision: {path}")
    if _git("-C", str(path), "diff", "--name-only", "HEAD"):
        raise ValueError(f"Existing checkout has tracked modifications: {path}")


def _download(root: Path, spec: dict):
    target = _inside(root, spec["path"])
    if target.exists():
        if not target.is_file() or sha256(target) != spec["sha256"]:
            raise ValueError(f"Existing asset differs from manifest: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".download-", dir=target.parent) as temporary:
        staged = Path(temporary) / "asset"
        with urllib.request.urlopen(spec["url"], timeout=120) as source, staged.open("wb") as output:
            shutil.copyfileobj(source, output)
        if sha256(staged) != spec["sha256"]:
            raise ValueError(f"Downloaded asset failed SHA-256 validation: {spec['path']}")
        if "bytes" in spec and staged.stat().st_size != spec["bytes"]:
            raise ValueError(f"Downloaded asset failed size validation: {spec['path']}")
        # Hard-link publication refuses to overwrite a concurrently created file.
        target.hardlink_to(staged)


def fetch_sources(root: Path, benchmarks: list[str], manifest: Path | None = None) -> dict:
    """Acquire repositories/annotations/public pilot archives; never run source code.

    Existing checkouts and assets are verified and never reset or overwritten.
    ScienceAgentBench's access-controlled verified ZIP must be supplied separately.
    """
    specs = source_manifest(manifest)
    if not set(benchmarks) <= specs.keys():
        raise ValueError("Unknown benchmark in source acquisition request")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    records = []
    for name in benchmarks:
        spec = specs[name]
        repository = _inside(root, spec["repository_directory"])
        assets = _inside(root, spec["assets_directory"])
        if not repository.exists():
            repository.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".source-", dir=repository.parent) as temporary:
                stage = Path(temporary) / "repository"
                _git("init", str(stage))
                _git("-C", str(stage), "remote", "add", "origin", spec["repository_url"])
                _git("-C", str(stage), "fetch", "--depth=1", "origin", spec["revision"])
                _git("-C", str(stage), "checkout", "--detach", spec["revision"])
                _verify_repository(stage, spec["revision"])
                stage.rename(repository)
        _verify_repository(repository, spec["revision"])
        for asset in [*spec.get("annotation_files", []), *spec.get("data_files", [])]:
            _download(assets, asset)
        records.append({"benchmark": name, "revision": spec["revision"],
                        "repository": str(repository), "assets": str(assets)})
    return {"sources": records, "model_calls": 0,
            "note": "ScienceAgentBench requires a separately supplied verified ZIP; fetching does not execute benchmarks."}
