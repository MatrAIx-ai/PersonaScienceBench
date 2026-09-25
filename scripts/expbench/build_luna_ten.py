#!/usr/bin/env python3
"""Select ten converted EXP-Bench tasks from the five locally pinned papers."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_IDS = [
    "neurips2024/97649/0", "neurips2024/97649/3",
    "neurips2024/94328/5", "neurips2024/94328/1",
    "neurips2024/94391/7", "neurips2024/94391/2",
    "iclr2024/18447/7", "iclr2024/18447/0",
    "iclr2024/18865/4", "iclr2024/18865/0",
]


def main() -> None:
    catalog = {row["task_id"]: row for row in map(json.loads,
               (ROOT / "data/design_catalog/tasks.jsonl").read_text().splitlines())}
    original_sources = json.loads((ROOT / "data/realistic_pilot/source_repositories.json").read_text())
    by_paper = {task_id.split("/")[1]: value for task_id, value in original_sources.items()}
    output = ROOT / "data/luna_ten_expbench"
    output.mkdir(parents=True, exist_ok=True)
    (output / "tasks.jsonl").write_text(
        "".join(json.dumps(catalog[task_id], ensure_ascii=False) + "\n" for task_id in TASK_IDS))
    sources = {task_id: dict(by_paper[task_id.split("/")[1]]) for task_id in TASK_IDS}
    (output / "source_repositories.json").write_text(json.dumps(sources, indent=2) + "\n")
    print(f"Selected {len(TASK_IDS)} EXP-Bench tasks")


if __name__ == "__main__":
    main()
