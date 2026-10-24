#!/usr/bin/env python3
"""Verify published persona prompts or restore their exact raw identity files."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validated_cohort():
    manifest = json.loads((ROOT / "configs/full_persona_v2/cohort.json").read_text())
    prompts = {}
    for row in manifest["profiles"]:
        published = ROOT / row["published_profile"]
        text = published.read_text()
        prompt = text.split("```text\n", 1)[1].rsplit("\n```", 1)[0]
        if hashlib.sha256(prompt.encode()).hexdigest() != row["prompt_sha256"]:
            raise ValueError(f"Published identity hash mismatch: {row['candidate_id']}")
        if row["candidate_id"] in prompts:
            raise ValueError("Duplicate persona ID")
        prompts[row["candidate_id"]] = prompt
    if len(prompts) != manifest["cohort_size"] or len(prompts) != 30:
        raise ValueError("Expected the frozen 30-profile cohort")
    return manifest, prompts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify only; write nothing")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data/persona_case_study/full_persona_v2")
    args = parser.parse_args()
    manifest, prompts = validated_cohort()
    if args.check:
        print("Verified all 30 published identity hashes; no files written.")
        return
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "prompts").mkdir()
    restored = deepcopy(manifest)
    for row in restored["profiles"]:
        row["prompt"] = f"prompts/{row['candidate_id']}.md"
        (output / row["prompt"]).write_text(prompts[row["candidate_id"]])
    restored["restoration_note"] = (
        "Exact identity files restored from the published study. Original source JSON "
        "records and field audits require separate transfer; they are not reconstructed.")
    (output / "manifest.json").write_text(json.dumps(restored, indent=2) + "\n")
    print(f"Restored 30 exact identities and manifest to {output}")


if __name__ == "__main__":
    main()
