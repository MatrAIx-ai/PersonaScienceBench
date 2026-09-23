"""Load a source adapter using the pinned collection manifest."""

import importlib
import json
from pathlib import Path
import subprocess

from personasciencebench.adapters.base import SourceConfig, sha256

ADAPTERS = {
    "discoverybench": ("discoverybench", "DiscoveryBenchAdapter"),
    "bixbench": ("bixbench", "BixBenchAdapter"),
    "scienceagentbench": ("scienceagentbench", "ScienceAgentBenchAdapter"),
    "terminal_bench_science": ("terminal_bench_science", "TerminalBenchScienceAdapter"),
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_manifest(path: Path | None = None) -> dict:
    return json.loads((path or project_root() / "manifests/sources.json").read_text())


def load_adapter(name: str, source_root: Path, manifest: Path | None = None,
                 *, verify: bool = True):
    spec = source_manifest(manifest)[name]
    repository = (source_root / spec["repository_directory"]).resolve()
    assets = (source_root / spec["assets_directory"]).resolve()
    if verify:
        actual = subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.PIPE).strip()
        if actual != spec["revision"]:
            raise ValueError(f"{name}: source revision differs from manifest")
        if subprocess.check_output(["git", "-C", str(repository), "diff", "--name-only", "HEAD"],
                                   text=True, stderr=subprocess.PIPE).strip():
            raise ValueError(f"{name}: tracked source files were modified")
        for annotation in spec.get("annotation_files", []):
            if sha256(assets / annotation["path"]) != annotation["sha256"]:
                raise ValueError(f"{name}: changed annotation {annotation['path']}")
    module, class_name = ADAPTERS[name]
    adapter_class = getattr(importlib.import_module(f"personasciencebench.adapters.{module}"), class_name)
    return adapter_class(SourceConfig(repository, assets, spec["revision"], spec.get("dataset_revision")))
