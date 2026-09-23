#!/usr/bin/env python3
"""Fetch public code snapshots at/before the paper date; never execute their code.

These are reproducible preparation snapshots, not recovered paper run commits.
"""

import io
import json
import tarfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from expbench.exploration import CODE_SUFFIXES

ROOT = Path(__file__).resolve().parents[2]
PINS = json.loads((ROOT / "manifests/expbench_repositories.json").read_text())



def fetch(item):
    tid, pin = item
    repo = pin["url"].removeprefix("https://github.com/")
    sha = pin["revision"]
    dest = ROOT / "data/realistic_pilot/source_repositories" / tid.replace("/", "__")
    metadata = dest.parent / (dest.name + ".json")
    if metadata.exists():
        existing = json.loads(metadata.read_text())
        if existing["revision"] != sha or not dest.is_dir():
            raise ValueError("Existing repository does not match the pinned snapshot")
        existing["repository"] = str(dest.resolve())
        return tid, existing
    if dest.exists():
        raise ValueError(f"Incomplete existing download at {dest}; use a new destination")
    with urllib.request.urlopen(f"https://codeload.github.com/{repo}/tar.gz/{sha}", timeout=120) as response:
        archive = response.read()
    dest.mkdir(parents=True)
    count = 0
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar:
            rel = PurePosixPath(*PurePosixPath(member.name).parts[1:])
            if (not member.isfile() or rel.is_absolute() or ".." in rel.parts
                    or any(p.startswith(".") for p in rel.parts)):
                continue
            if rel.suffix.lower() not in CODE_SUFFIXES and not (
                    rel.name.lower().startswith(("license", "requirements")) or rel.name == "Makefile"):
                continue
            target = dest / str(rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
            target.chmod(0o755 if member.mode & 0o111 else 0o644)
            count += 1
    result = {"repository": str(dest), "url": f"https://github.com/{repo}", "revision": sha,
              "selection": "Latest default-branch commit dated at or before 2025-05-30; not a recovered original run revision",
              "downloaded_code_files": count, "datasets": {}, "gpu": False}
    metadata.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{tid}: {sha[:12]}, {count} code/config files", flush=True)
    return tid, result


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        mappings = dict(pool.map(fetch, PINS.items()))
    output = ROOT / "data/realistic_pilot/source_repositories.json"
    output.write_text(json.dumps(mappings, indent=2) + "\n")
    print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
