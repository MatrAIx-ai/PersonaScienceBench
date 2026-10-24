#!/usr/bin/env python3
"""Audit the downloaded snapshot and join CSV metadata to original annotations.

The output contains hidden references and outcomes. It is an inspection dataset,
not a collection of prompts suitable for sending directly to an evaluated model.
"""

import ast
import csv
import hashlib
import json
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "exp_bench"
VARIABLE_GROUPS = ("constant_variables", "independent_variables", "dependent_variables")
ESCAPES = re.compile(r"\\(?:u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2})|U([0-9a-fA-F]{8}))")
OUTCOME_HINT = re.compile(
    r"\b(?:is|are) expected to\b|\b(?:results|findings) (?:show|indicate|demonstrate)\b"
    r"|\b\d+(?:\.\d+)?\s*(?:x|×|times)\s+faster\b",
    re.IGNORECASE,
)


def decode_text(value):
    """Decode only literal Unicode/hex escapes; preserve LaTeX and other backslashes."""
    return ESCAPES.sub(lambda match: chr(int(next(g for g in match.groups() if g is not None), 16)), value)


def comparable(value, markdown=False):
    value = unicodedata.normalize("NFKC", decode_text(value))
    if markdown:
        value = re.sub(r"(?m)^\s*[-*]\s+", "", value).replace("**", "")
    return " ".join(value.split())


def parse_list(value):
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return decode_text(value), False
    if not isinstance(parsed, list):
        return decode_text(value), False
    return parsed, True


def main():
    manifest = json.loads((DATA / "manifest.json").read_text())
    for item in manifest["files"]:
        path = DATA / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Snapshot checksum mismatch: {path}")

    with (DATA / "raw/huggingface/exp_bench_dataset.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    papers = {}
    source_key_coverage = Counter()
    for path in sorted((DATA / "raw/upstream/tasks").glob("*/*.json")):
        tasks = json.loads(path.read_text())["questions"]
        papers[(path.parent.name, path.stem)] = tasks
        source_key_coverage.update(key for task in tasks for key in task)

    paper_rows = defaultdict(list)
    for row in rows:
        paper_rows[(row["conference"], row["paper_id"])].append(row)
    if set(paper_rows) != set(papers):
        raise ValueError("CSV and annotation paper sets differ")
    for key, group in paper_rows.items():
        if sorted(int(row["task_index"]) for row in group) != list(range(len(papers[key]))):
            raise ValueError(f"CSV task indices do not match annotation records: {key}")
        if len({row["paper_title"] for row in group}) != 1:
            raise ValueError(f"Inconsistent paper titles: {key}")
    if len(rows) != manifest["csv_task_count"]:
        raise ValueError("CSV task count differs from the snapshot manifest")

    records = []
    issues = defaultdict(list)
    differences = []
    hint_examples = []
    field_types = defaultdict(Counter)
    counts_by_type = defaultdict(Counter)
    for row in rows:
        key = (row["conference"], row["paper_id"])
        index = int(row["task_index"])
        task_id = f"{key[0]}/{key[1]}/{index}"
        task = papers[key][index]
        flags = []
        if row["question"] == task["question"]:
            question_match = "exact"
        elif comparable(row["question"]) == comparable(task["question"]):
            question_match = "unicode_or_whitespace"
        elif comparable(row["question"], True) == comparable(task["question"], True):
            question_match = "markdown_formatting"
        else:
            question_match = "text_difference_needs_review"
            flags.append(question_match)
            differences.append({
                "task_id": task_id,
                "csv_question": decode_text(row["question"]),
                "upstream_question": task["question"],
            })

        design = task.get("design_complexity")
        design_path = "design_complexity"
        while isinstance(design, dict) and isinstance(design.get("design_complexity"), dict):
            design = design["design_complexity"]
            design_path += ".design_complexity"
        if design_path != "design_complexity":
            flags.append("unwrapped_nested_design")
        design_valid = isinstance(design, dict) and all(
            isinstance(design.get(group), dict) and bool(design[group]) for group in VARIABLE_GROUPS
        )
        if not design_valid:
            flags.append("missing_reference_variable_groups")
        requirements, requirements_are_list = parse_list(row["impl_requirements"])
        if not requirements_are_list:
            flags.append("csv_requirements_not_parseable_as_list")
        source_files, sources_are_list = parse_list(row["source_files"])
        if not sources_are_list:
            raise ValueError(f"Invalid source file list: {task_id}")
        if ESCAPES.search(row["question"]):
            flags.append("decoded_literal_escapes_in_question")

        hints = []
        for field, value in {
            "question": decode_text(row["question"]),
            "agent_instructions": decode_text(row["agent_instructions"]),
            "reference_design": json.dumps(design, ensure_ascii=False),
        }.items():
            match = OUTCOME_HINT.search(value)
            if match:
                hints.append(f"potential_outcome_hint_in_{field}")
                hint_examples.append({
                    "task_id": task_id,
                    "field": field,
                    "excerpt": value[max(0, match.start() - 100):match.end() + 160],
                })

        record = {
            "task_id": task_id,
            "conference": row["conference"],
            "paper_id": row["paper_id"],
            "paper_title": row["paper_title"],
            "task_index": index,
            "task_type": int(row["task_type"]),
            "subtask_count": int(row["subtask_count"]),
            "question": decode_text(row["question"]),
            "method": task["method"],
            "agent_instructions": decode_text(row["agent_instructions"]),
            "implementation_requirements": requirements,
            "expected_outcome": decode_text(row["expected_outcome"]),
            "source_files": source_files,
            "masked_source": task.get("masked_source"),
            "reference_design": design if design_valid else None,
            "reference_design_schema_valid": design_valid,
            "design_ambiguity": task.get("design_ambiguity"),
            "experiment_constraints": task.get("experiment_constraints"),
            "random_uncertainty": task.get("random_uncertainty"),
            "systematic_uncertainty": task.get("systematic_uncertainty"),
            "implementation_extraction_note": task.get("no_answer"),
            "question_match": question_match,
            "quality_flags": flags,
            "review_hints": hints,
            "provenance": {
                "csv_record_number": len(records) + 1,
                "upstream_file": f"raw/upstream/tasks/{key[0]}/{key[1]}.json",
                "upstream_task_index": index,
                "upstream_design_path": design_path,
            },
        }
        records.append(record)
        for flag in flags + hints:
            issues[flag].append(task_id)
        for field in ("experiment_constraints", "random_uncertainty", "systematic_uncertainty", "design_ambiguity"):
            field_types[field][type(task.get(field)).__name__] += 1
        counts_by_type[row["task_type"]].update({
            "tasks": 1,
            "has_source": int("source" in task),
            "has_masked_source": int("masked_source" in task),
            "has_mode_B": int(task.get("mode") == "B"),
            "has_no_answer": int("no_answer" in task),
            "valid_design_schema": int(design_valid),
        })

    ids = [record["task_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task IDs")
    with (DATA / "tasks.jsonl").open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    questions_to_ids = defaultdict(list)
    for record in records:
        questions_to_ids[comparable(record["question"], True)].append(record["task_id"])
    duplicate_questions = [group for group in questions_to_ids.values() if len(group) > 1]

    paper_summary = []
    for (conference, paper_id), group in sorted(paper_rows.items()):
        types = Counter(row["task_type"] for row in group)
        paper_summary.append({
            "conference": conference, "paper_id": paper_id,
            "paper_title": group[0]["paper_title"], "tasks": len(group),
            "type_1": types["1"], "type_2": types["2"], "type_3": types["3"],
            "subtasks": sum(int(row["subtask_count"]) for row in group),
        })
    with (DATA / "papers.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paper_summary[0]))
        writer.writeheader()
        writer.writerows(paper_summary)

    audit = {
        "task_count": len(records), "paper_count": len(papers),
        "subtask_count": sum(record["subtask_count"] for record in records),
        "conference_task_counts": dict(Counter(row["conference"] for row in rows)),
        "conference_paper_counts": dict(Counter(key[0] for key in papers)),
        "task_type_counts_and_observed_fields": dict(counts_by_type),
        "csv_columns": list(rows[0]),
        "csv_blank_field_counts": {key: sum(not row[key].strip() for row in rows) for key in rows[0]},
        "source_annotation_key_coverage": dict(source_key_coverage),
        "annotation_field_types": dict(field_types),
        "question_match_counts": dict(Counter(record["question_match"] for record in records)),
        "reference_design_schema_valid_count": sum(record["reference_design_schema_valid"] for record in records),
        "duplicate_question_groups": duplicate_questions,
        "text_lengths_characters": {
            field: {
                "min": min(len(record[field]) for record in records),
                "median": statistics.median(len(record[field]) for record in records),
                "max": max(len(record[field]) for record in records),
            }
            for field in ("question", "agent_instructions")
        },
        "quality_flag_and_review_hint_counts": {key: len(value) for key, value in issues.items()},
        "tasks_by_quality_flag_or_review_hint": dict(issues),
        "question_differences_requiring_review": differences,
        "potential_outcome_hint_examples": hint_examples,
        "review_hint_caveat": "Regex hints are inspection candidates, not validated leakage labels or exhaustive detection.",
        "join_caveat": "Joined by conference, paper_id, and task_index. Text-different questions require manual alignment review.",
        "design_caveat": "Schema validity does not establish scientific correctness or suitability for design-only evaluation.",
        "verified_source_file_count": len(manifest["files"]),
    }
    (DATA / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    (DATA / "question_differences.json").write_text(json.dumps(differences, ensure_ascii=False, indent=2) + "\n")
    example_ids = {"neurips2024/97649/0", "iclr2024/18447/0", "neurips2024/94391/4"}
    example_fields = ("task_id", "paper_title", "question", "reference_design", "quality_flags", "review_hints", "provenance")
    examples = [{field: record[field] for field in example_fields} for record in records if record["task_id"] in example_ids]
    (DATA / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: audit[key] for key in (
        "task_count", "paper_count", "subtask_count", "question_match_counts",
        "reference_design_schema_valid_count", "quality_flag_and_review_hint_counts",
    )}, indent=2))
    print(f"Saved tasks.jsonl, papers.csv, audit.json, question_differences.json, examples.json under {DATA}")


if __name__ == "__main__":
    main()
