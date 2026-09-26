#!/usr/bin/env python3
"""Sample MatrAIx profiles and select concrete, observable research actions."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

import pyarrow.parquet as pq


SOURCE_REVISION = "8b1073ab23d0c0ba0928386a041bac55e5365ddc"
SOURCE_SHA256 = "c856d4d2d8e9832f3154d9856e5adbe9bf327328ab036069f8a4873992e03439"
SEED = 20260926

# Each retained field maps directly to an instruction that can be observed later.
ACTION_FIELDS = {
    "decision_style": ("decision", "When making a scientific decision, use a {value} approach."),
    "debugging_strategy": ("verification", "When debugging, use this strategy: {value}."),
    "code_modularity_preference": ("implementation", "When structuring code, prefer: {value}."),
    "code_type_system_orientation": ("implementation", "When choosing typing, prefer: {value}."),
    "code_comment_style": ("implementation", "When writing code, use: {value}."),
    "code_testing_approach": ("verification", "When validating code, use: {value}."),
    "code_observability_habit": ("verification", "When instrumenting code, use: {value}."),
    "code_performance_priority": ("implementation", "When trading off code qualities, prioritize: {value}."),
    "code_naming_verbosity": ("implementation", "When naming code elements, use: {value}."),
    "code_complexity_tolerance": ("implementation", "When reviewing complexity, tolerate this level: {value}."),
    "code_indentation_style": ("implementation", "When formatting code, use: {value}."),
    "peeve_unexplained_jargon": ("communication", "When explaining scientific work, treat unexplained jargon as: {value}."),
}

# These values describe no stable choice, so they count as present but not directional.
NON_DIRECTIONAL = {
    "null", "not applicable", "context-dependent", "no strong preference",
    "mixed approach", "mixed (context-dependent)", "balanced consideration",
    "inconsistent/mixed", "neutral",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if not text or text.lower() == "null" else text


def assess(row: dict, candidate_id: str) -> dict:
    rules = []
    for field, (context, template) in ACTION_FIELDS.items():
        value = normalized(row.get(field))
        if value is None:
            continue
        rules.append({
            "field": field,
            "value": value,
            "context": context,
            "directional": value.lower() not in NON_DIRECTIONAL,
            "instruction": template.format(value=value),
        })
    directional = [rule for rule in rules if rule["directional"]]
    contexts = sorted({rule["context"] for rule in directional})
    checks = {
        "concrete_actions": len(rules) >= 4,
        "clear_behavioral_difference": len(directional) >= 3,
        "scientific_work_relevance": len(contexts) >= 2,
    }
    return {
        "candidate_id": candidate_id,
        "source": normalized(row.get("source")),
        "source_row_index": row.get("source_row_index"),
        "rules": rules,
        "counts": {
            "concrete_actions": len(rules),
            "directional_actions": len(directional),
            "contexts": contexts,
        },
        "checks": checks,
        "selected": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=300)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    if file_sha256(args.input) != SOURCE_SHA256:
        raise ValueError("Input is not the pinned MatrAIx public sample")
    table = pq.read_table(args.input)
    if args.sample_size < 1 or args.sample_size > table.num_rows:
        raise ValueError("sample-size must be between 1 and the source row count")

    indexes = sorted(random.Random(args.seed).sample(range(table.num_rows), args.sample_size))
    rows = table.take(indexes).to_pylist()
    records = [assess(row, f"candidate_{number:03d}")
               for number, row in enumerate(rows, 1)]
    selected = [record for record in records if record["selected"]]

    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "sampled.jsonl").write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records))
    (args.output / "selected.jsonl").write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in selected))
    report = {
        "version": "action-profile-selection-v1",
        "source": "MatrAIx2026/MatrAIx_Persona_1M sample/sample.parquet",
        "source_revision": SOURCE_REVISION,
        "source_sha256": SOURCE_SHA256,
        "source_rows": table.num_rows,
        "sample_size": len(records),
        "sample_seed": args.seed,
        "selected": len(selected),
        "rules": {
            "concrete_actions": "At least four populated fields render as concrete action instructions.",
            "clear_behavioral_difference": "At least three action values express a directional choice rather than a neutral or context-dependent value.",
            "scientific_work_relevance": "Directional actions cover at least two of decision, implementation, verification, and communication.",
        },
        "sample_sources": dict(sorted(Counter(record["source"] for record in records).items())),
        "selected_sources": dict(sorted(Counter(record["source"] for record in selected).items())),
        "failure_counts": {
            name: sum(not record["checks"][name] for record in records)
            for name in next(iter(records))["checks"]
        },
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
