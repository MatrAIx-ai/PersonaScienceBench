#!/usr/bin/env python3
"""Deterministically choose DiscoveryBench screening candidates across domains and complexity.

Static metadata only: no model calls, answer keys or reference hypotheses are read.
Complexity is a proxy from the native metadata (number of workflow tags and datasets);
DiscoveryBench publishes no per-question difficulty label. Empirical difficulty comes
from the persona-off screen run on these candidates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import statistics

from personasciencebench.registry import load_adapter

ROOT = Path(__file__).resolve().parents[1]
# Raw/processed versions of one study count once (paper plan: "raw/processed versions of the same question count once").
STUDIES = {"meta_regression_raw": "meta_regression", "nls_bmi_raw": "nls_bmi",
           "worldbank_education_gdp_indicators": "worldbank_education_gdp"}
# Studies built on one shared dataset; kept for grouping uncertainty, not for selection.
DATA_FAMILIES = {"nls_raw": "nls", "nls_incarceration": "nls", "nls_ses": "nls", "nls_bmi": "nls", "nls_bmi_raw": "nls"}
# Earlier pilots whose DiscoveryBench tasks are excluded by default so the screen adds new evidence.
EARLIER_PILOTS = [ROOT / "configs/full_persona_v2/selection.json",
                  ROOT / "reports/discoverybench_ecology_persona_pilot/selection.json"]


def earlier_pilot_tasks() -> set[str]:
    tasks = set()
    for path in EARLIER_PILOTS:
        if path.is_file():
            value = json.loads(path.read_text())
            tasks.update(value.get("discoverybench", []) if isinstance(value, dict) else value)
    return tasks


def features(source: Path, task) -> dict:
    split, study, metadata_file, group, qid = task.id.split("/")
    metadata = json.loads((source / "discoverybench/real" / split / study / metadata_file).read_text())
    query = next(q for q in metadata["queries"][int(group)] if str(q["qid"]) == qid)
    tags = [t.strip() for t in str(metadata.get("workflow_tags", "")).split(",") if t.strip()]
    data_bytes = sum((source / "discoverybench/real" / split / study / d["name"]).stat().st_size
                     for d in metadata["datasets"])
    return {"task_id": task.id, "split": split, "study": study, "family": STUDIES.get(study, study),
            "data_family": DATA_FAMILIES.get(study, STUDIES.get(study, study)),
            "domain": task.domain, "question_type": query["question_type"], "question": query["question"],
            "workflow_tags": len(tags), "datasets": len(metadata["datasets"]),
            "data_bytes": data_bytes}


def select(rows: list[dict], domains: list[str], per_domain: int, seed: int, exclude: set[str]) -> list[dict]:
    """Per domain: alternate lower/higher complexity, spreading picks over studies.

    Each pick prefers, in order: a study not yet used in this domain (studies repeat only once
    all are used), the under-represented complexity stratum, converted researcher facts (only
    then does the simulated researcher hold study context), and the test split.
    """
    rng = random.Random(seed)
    chosen = []
    for domain in domains:
        pool = [r for r in rows if r["domain"] == domain and r["task_id"] not in exclude]
        if not pool:
            raise ValueError(f"No eligible DiscoveryBench tasks for domain {domain!r}")
        cut = statistics.median(r["workflow_tags"] for r in pool)
        for r in pool:
            r["complexity"] = "higher" if r["workflow_tags"] > cut else "lower"
        tiebreak = {r["task_id"]: rng.random() for r in pool}
        studies = {r["family"] for r in pool}
        picked = []
        while len(picked) < min(per_domain, len(pool)):
            counts = {c: sum(r["complexity"] == c for r in picked) for c in ("lower", "higher")}
            stratum = "higher" if counts["higher"] < counts["lower"] else "lower"
            used = [r["family"] for r in picked]
            # Reuse a study only after every study in the domain has been used equally often.
            fewest = min(used.count(s) for s in studies)
            options = [r for r in pool if r not in picked]
            options.sort(key=lambda r: (used.count(r["family"]) > fewest, r["complexity"] != stratum,
                                        r["researcher_facts"] == 0, r["split"] != "test",
                                        tiebreak[r["task_id"]]))
            picked.append(options[0])
        chosen.extend(dict(r, domain_rank=i + 1) for i, r in enumerate(picked))
    return chosen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT / "external/sources")
    parser.add_argument("--domains", nargs="+", default=["biology", "humanities", "sociology", "economics"])
    parser.add_argument("--per-domain", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--exclude", nargs="*", default=None,
                        help="Task IDs to leave out (default: DiscoveryBench tasks of earlier recorded pilots)")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    adapter = load_adapter("discoverybench", args.source_root, ROOT / "manifests/sources.json")
    source = args.source_root / "discoverybench"
    rows, unconvertible = [], []
    for task in adapter.enumerate_tasks():
        row = features(source, task)
        try:
            # Offline conversion: the adapter, not raw metadata, decides researcher facts
            # (reviewed tasks carry curated facts) and proves every asset path resolves.
            episode = adapter.convert(task.id)
        except Exception as error:
            unconvertible.append({"task_id": task.id, "reason": f"{type(error).__name__}: {error}"})
            continue
        row["researcher_facts"] = len(episode.researcher.facts)
        row["review_status"] = episode.review_status
        row["assets_ready"] = all(Path(a.source_path).is_file() for a in episode.assets)
        if row["assets_ready"]:
            rows.append(row)
    exclude = earlier_pilot_tasks() if args.exclude is None else set(args.exclude)
    chosen = select(rows, args.domains, args.per_domain, args.seed, exclude)
    record = {
        "schema_version": "1", "benchmark": "discoverybench",
        "source_revision": adapter.source.revision, "seed": args.seed,
        "domains": args.domains, "per_domain": args.per_domain, "excluded": sorted(exclude),
        "method": ("Per domain, rotate over study families (raw/processed versions count once), alternating "
                   "lower/higher complexity around the domain median of native workflow-tag counts; prefer tasks "
                   "with researcher-owned domain knowledge, then the test split. No answer keys or model calls."),
        "difficulty_note": "Complexity is a metadata proxy; empirical difficulty is measured by the persona-off screen.",
        "unconvertible": unconvertible,
        "domain_facts": {d: sum(r["researcher_facts"] > 0 for r in rows if r["domain"] == d) for d in args.domains},
        "catalog_counts": {d: sum(r["domain"] == d for r in rows) for d in sorted({r["domain"] for r in rows})},
        "candidates": chosen,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    for row in chosen:
        print(f"{row['domain']:10} {row['complexity']:6} tags={row['workflow_tags']} facts={row['researcher_facts']:2} "
              f"{row['question_type']:12} {row['task_id']}")


if __name__ == "__main__":
    main()
