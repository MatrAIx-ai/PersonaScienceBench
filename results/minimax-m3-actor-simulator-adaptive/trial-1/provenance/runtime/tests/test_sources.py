"""Acquisition checks use local Git and file URLs; no network or model calls."""

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from personasciencebench.sources import fetch_sources


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True, stderr=subprocess.PIPE).strip()


@pytest.fixture
def source(tmp_path):
    upstream = tmp_path / "upstream"
    git("init", upstream)
    (upstream / "README.md").write_text("Synthetic source\n")
    git("-C", upstream, "add", "README.md")
    git("-C", upstream, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "fixture")
    asset = tmp_path / "annotation.json"
    asset.write_text('{"synthetic": true}\n')
    spec = {"fixture": {"repository_url": str(upstream), "revision": git("-C", upstream, "rev-parse", "HEAD"),
                        "repository_directory": "fixture", "assets_directory": "_assets/fixture",
                        "annotation_files": [{"path": "annotation.json", "url": asset.as_uri(),
                                              "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
                                              "bytes": asset.stat().st_size}]}}
    manifest = tmp_path / "sources.json"
    manifest.write_text(json.dumps(spec))
    return tmp_path / "downloaded", manifest, spec


def test_acquisition_is_pinned_repeatable_and_non_destructive(source):
    root, manifest, spec = source
    first = fetch_sources(root, ["fixture"], manifest)
    assert first == fetch_sources(root, ["fixture"], manifest)
    assert git("-C", root / "fixture", "rev-parse", "HEAD") == spec["fixture"]["revision"]
    assert (root / "_assets/fixture/annotation.json").is_file()
    (root / "fixture/README.md").write_text("Keep my change")
    with pytest.raises(ValueError, match="tracked modifications"):
        fetch_sources(root, ["fixture"], manifest)
    assert (root / "fixture/README.md").read_text() == "Keep my change"


def test_changed_assets_are_not_overwritten(source):
    root, manifest, _ = source
    fetch_sources(root, ["fixture"], manifest)
    target = root / "_assets/fixture/annotation.json"
    target.write_text("keep existing")
    with pytest.raises(ValueError, match="Existing asset differs"):
        fetch_sources(root, ["fixture"], manifest)
    assert target.read_text() == "keep existing"


def test_failed_download_checksum_leaves_no_published_asset(source):
    root, manifest, spec = source
    spec["fixture"]["annotation_files"][0]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match="SHA-256"):
        fetch_sources(root, ["fixture"], manifest)
    assert not (root / "_assets/fixture/annotation.json").exists()


def test_unsafe_manifest_path_is_rejected(source):
    root, manifest, spec = source
    spec["fixture"]["repository_directory"] = "../outside"
    manifest.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match="contained"):
        fetch_sources(root, ["fixture"], manifest)
    assert not (root.parent / "outside").exists()
