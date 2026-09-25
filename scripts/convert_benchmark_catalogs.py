#!/usr/bin/env python3
"""Materialize controller-private conversion catalogs for all PSB adapters."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from pathlib import Path

from personasciencebench.adapters.base import sha256
from personasciencebench.registry import ADAPTERS, load_adapter


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "external/sources"
OUTPUT = ROOT / "data/conversion_catalog"


def readiness(episode, digest_cache: dict[str, str]) -> dict:
    missing, changed, unsafe = [], [], []
    for asset in episode.assets:
        path = Path(asset.source_path)
        exists = path.is_file() if asset.kind == "file" else path.is_dir()
        if not exists:
            if asset.required:
                missing.append({"asset_id": asset.id, "visibility": asset.visibility,
                                "path": str(path), "acquisition": asset.acquisition})
            continue
        if path.is_symlink() or (path.is_dir() and any(item.is_symlink() for item in path.rglob("*"))):
            unsafe.append(asset.id)
        if asset.sha256 and path.is_file():
            key = str(path.resolve())
            actual = digest_cache.get(key)
            if actual is None:
                actual = digest_cache[key] = sha256(path)
            if actual != asset.sha256:
                changed.append(asset.id)
    return {"assets_ready": not (missing or changed or unsafe), "missing": missing,
            "hash_mismatches": changed, "symlinks_rejected": unsafe,
            "runtime_tested": False, "model_tested": False}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"schema_version": "1", "source_root": str(SOURCE_ROOT.resolve()),
              "benchmarks": {}, "excluded": []}
    digest_cache: dict[str, str] = {}
    for name in ADAPTERS:
        adapter = load_adapter(name, SOURCE_ROOT, ROOT / "manifests/sources.json")
        tasks = adapter.enumerate_tasks()
        converted = []
        ready = 0
        groups = {}
        for task in tasks:
            groups.setdefault(task.study_id, []).append(task)
        def one_group(group):
            records, errors = [], []
            for task in group:
                try:
                    episode = adapter.convert(task.id)
                    record = episode.model_dump(mode="json")
                    record["catalog_readiness"] = readiness(episode, digest_cache)
                    records.append(record)
                except Exception as exc:
                    errors.append({"benchmark": name, "task_id": task.id,
                                   "reason": f"{type(exc).__name__}: {exc}"})
            return records, errors
        by_id = {}
        with ThreadPoolExecutor(max_workers=4) as pool:
            for future in as_completed([pool.submit(one_group, group) for group in groups.values()]):
                records, errors = future.result()
                by_id.update({r["source_task_id"]: r for r in records})
                report["excluded"].extend(errors)
                print(json.dumps({"benchmark": name, "processed":len(by_id), "source_tasks":len(tasks)}), flush=True)
        partial = OUTPUT / f"{name}.episodes.jsonl.partial"
        with partial.open("w", encoding="utf-8") as stream:
            for task in tasks:
                if task.id not in by_id:
                    continue
                record = by_id[task.id]
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                converted.append(task.id)
                ready += int(record["catalog_readiness"]["assets_ready"])
        partial.replace(OUTPUT / f"{name}.episodes.jsonl")
        report["benchmarks"][name] = {
            "source_tasks": len(tasks), "converted": len(converted),
            "assets_ready": ready, "exceptions": len(tasks) - len(converted),
            "catalog": f"data/conversion_catalog/{name}.episodes.jsonl",
        }
    expbench = json.loads((ROOT / "data/design_catalog/conversion_report.json").read_text())
    report["benchmarks"]["expbench"] = expbench
    report["excluded"].extend({"benchmark": "expbench", **item}
                              for item in expbench.get("excluded", []))
    report["totals"] = {
        "source_tasks": sum(item["source_tasks"] for item in report["benchmarks"].values()),
        "converted": sum(item["converted"] for item in report["benchmarks"].values()),
        "excluded": len(report["excluded"]),
    }
    (OUTPUT / "conversion_report.json.partial").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT / "conversion_report.json.partial").replace(OUTPUT / "conversion_report.json")
    print(json.dumps(report["totals"], sort_keys=True))


if __name__ == "__main__":
    main()
