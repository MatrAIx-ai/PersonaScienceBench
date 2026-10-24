#!/usr/bin/env python3
"""Download the immutable EXP-Bench snapshot recorded in the committed manifest."""

import json
from pathlib import Path

from personasciencebench.sources import _download

ROOT = Path(__file__).resolve().parents[2]


def main():
    manifest = json.loads((ROOT / "manifests/expbench.json").read_text())
    destination = ROOT / "data/exp_bench"
    destination.mkdir(parents=True, exist_ok=True)
    saved = destination / "manifest.json"
    if saved.exists() and json.loads(saved.read_text()) != manifest:
        raise ValueError("Existing EXP-Bench snapshot differs from the committed manifest")
    for entry in manifest["files"]:
        _download(destination, entry)
    saved.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Verified {len(manifest['files'])} pinned EXP-Bench files; no model calls.")


if __name__ == "__main__":
    main()
