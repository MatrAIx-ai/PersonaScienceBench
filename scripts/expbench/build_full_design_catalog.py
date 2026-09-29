#!/usr/bin/env python3
"""Convert every structurally valid EXP-Bench row into a design-only task card."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from expbench.schema import Task


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/exp_bench/tasks.jsonl"
OUTPUT = ROOT / "data/design_catalog/tasks.jsonl"
REPORT = ROOT / "data/design_catalog/conversion_report.json"

SETUP_TERMS = re.compile(
    r"\b(dataset|data set|model|architecture|environment|metric|optimizer|baseline|"
    r"input|checkpoint|sequence length|epoch|task|benchmark|split|precision|loss)\b", re.I)
OUTCOME_TERMS = re.compile(
    r"\b(outperform|improv(?:e|es|ed|ement)|achiev(?:e|es|ed)|result(?:s)?|"
    r"speedup|faster|slower|better|worse|increase[ds]?|decrease[ds]?)\b", re.I)
NUMBERED_OUTCOME = re.compile(r"(?:\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?\s*[x×]\b)", re.I)


from expbench.context_conversion import extract, POLICY
from personasciencebench.inference import load_env
from concurrent.futures import ThreadPoolExecutor

def setup_facts(row):
    return extract(row, ROOT)


def build_card(row, facts, source_hash):
    flags = list(row.get("quality_flags") or [])
    if row.get("question_match") not in (None, "exact", "normalized_equal", "markdown_only"):
        flags.append("question_reference_alignment_requires_analysis")
    card = {
        "task_id": row["task_id"],
        "domain": f"{row['conference']} / {row['paper_title']}",
        "public": {
            "question": row["question"],
            "context": ("Design an experiment that answers the question. The researcher can clarify "
                        "source-supported setup details by topic. Do not claim that an experiment was run."),
            "documents": {"track.md": "Design-only task; repositories and compute are not required."},
        },
        "researcher": {
            "facts": facts,
            "unspecified": ["Expected empirical outcome", "Unstated resources and runtime budget",
                            "Any setup detail not present in the available topics"],
        },
        "reference_design": row["reference_design"],
        "provenance": {
            "source_file": "data/exp_bench/tasks.jsonl", "source_sha256": source_hash,
            "source_task_id": row["task_id"], "upstream": row["provenance"],
            "validation_method": POLICY,
        },
        "review_notes": [
            "Context uses exact source spans classified as background or question-established requirements. Automated classification does not guarantee absence of leakage.",
            "Automatically extracted setup facts are source-attributed but not human reviewed.",
            *( ["Source audit flags: " + ", ".join(map(str, flags))] if flags else []),
        ],
    }
    Task.model_validate(card)
    return card


def main() -> None:
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line.strip()]
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    cards, excluded = [], []
    load_env(ROOT / ".env")
    allowed_matches = {"exact", "unicode_or_whitespace", "markdown_formatting"}
    eligible = [r for r in rows if r.get("reference_design_schema_valid") and r.get("question_match") in allowed_matches]
    def one(row):
        try:
            return row["task_id"], setup_facts(row), None
        except Exception as error:
            return row["task_id"], [], f"context_extraction_failed:{type(error).__name__}"
    with ThreadPoolExecutor(max_workers=8) as pool:
        extracted = {tid:(facts,error) for tid,facts,error in pool.map(one, eligible)}
    for row in rows:
        if not row.get("reference_design_schema_valid"):
            excluded.append({"task_id": row["task_id"],
                             "reason": "invalid_or_missing_reference_design"})
            continue
        if row["task_id"] not in extracted:
            excluded.append({"task_id":row["task_id"], "reason":"unresolved_question_reference_alignment"})
            continue
        facts, error = extracted[row["task_id"]]
        if error:
            excluded.append({"task_id":row["task_id"], "reason":error})
            continue
        card = build_card(row, facts, source_hash)
        cards.append(card)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(card, ensure_ascii=False) + "\n" for card in cards))
    REPORT.write_text(json.dumps({
        "source_tasks": len(rows), "converted": len(cards), "excluded": excluded,
        "with_researcher_facts": sum(bool(card["researcher"]["facts"]) for card in cards),
        "without_researcher_facts": sum(not card["researcher"]["facts"] for card in cards),
        "track": "design_only", "runtime_repositories_required": False,
    }, indent=2) + "\n")
    print(f"Converted {len(cards)}/{len(rows)} EXP-Bench tasks; {len(excluded)} excluded")


if __name__ == "__main__":
    main()
