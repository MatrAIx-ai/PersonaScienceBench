#!/usr/bin/env python3
"""Select a source-balanced, behaviorally diverse cohort and render full personas.

Static selection only; no model calls or outcome selection. Original records,
selection decisions and complete field inclusion audits accompany prompts.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random

import pyarrow.parquet as pq


REVISION = "3633d8dab149a9482a71b024418a49ae828cc941"
HASHES = {
    "persona_dimension_catalog.py": "b1f777b4b9fc43992ca831855d68645850453fe84688adbc30eb84f8bcd58d86",
    "dimensions.json": "cbf4db9d887dec057431aff409e1d28d83f345e7a31e29a4275a607212ecfca5",
}
METADATA = {"source_row_index", "source", "source_record_id", "populated_attribute_count"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def diverse_selection(pool, seed):
    """Greedy diminishing-return coverage under balanced source quotas."""
    sources = Counter(r["source"] for r in pool)
    quotas = dict.fromkeys(sorted(sources), 0)
    while sum(quotas.values()) < 30:
        for source in quotas:
            if quotas[source] < sources[source] and sum(quotas.values()) < 30:
                quotas[source] += 1
    # Equal total possible coverage per area and per field within each area.
    values, area_fields = {}, {}
    features = {}
    for row in pool:
        fs = set()
        for e in row["evidence"]:
            if not e["directional"]:
                continue
            key = (e["area"], e["field"], str(e["value"]).strip().casefold())
            fs.add(key)
            values.setdefault(key[:2], set()).add(key[2])
            area_fields.setdefault(key[0], set()).add(key[1])
        features[row["candidate_id"]] = fs
    weights = {k: 1 / (len(area_fields[k[0]]) * len(values[k[:2]]))
               for fs in features.values() for k in fs}
    rng = random.Random(seed)
    tie = {r["candidate_id"]: rng.random() for r in sorted(pool, key=lambda r: r["candidate_id"])}
    chosen, steps, seen, used = [], [], Counter(), Counter()
    remaining = list(pool)
    while len(chosen) < 30:
        candidates = [r for r in remaining if used[r["source"]] < quotas[r["source"]]]
        def gain(row):
            return sum(weights[k] / (1 + seen[k]) for k in sorted(features[row["candidate_id"]]))
        row = max(candidates, key=lambda r: (gain(r), tie[r["candidate_id"]]))
        steps.append({"candidate_id": row["candidate_id"], "source": row["source"],
                      "marginal_coverage_gain": gain(row)})
        chosen.append(row)
        remaining.remove(row)
        used[row["source"]] += 1
        seen.update(features[row["candidate_id"]])
    coverage = {area: {"selected_field_values": sum(k[0] == area for k in seen),
                       "eligible_field_values": sum(k[0] == area for k in weights)}
                for area in sorted(area_fields)}
    return sorted(chosen, key=lambda r: r["candidate_id"]), {
        "method": "Source quotas filled round-robin up to availability; greedy diminishing-return coverage of directional field/value pairs, equal weight per behavioral area and field. Seed breaks ties only.",
        "limitations": "Heuristic diversity, not a global optimum or population-representative sample. Exact categorical values, not semantic distances; missing attributes earn no coverage. No demographic or domain quotas.",
        "source_quotas": quotas, "coverage": coverage, "selection_order": steps}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260927)
    parser.add_argument("--output", type=Path, default=Path("data/persona_case_study/full_persona_v2"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    selection = root / "data/persona_case_study/full_profile_selection_v2"
    info = json.loads((selection / "report.json").read_text())
    source = root / "external/persona_case_study/sample.parquet"
    assert digest(source) == info["source_sha256"], "Source sample mismatch"
    reference = root / "external/persona_case_study/rendering_reference"
    for name, expected in HASHES.items():
        assert digest(reference / name) == expected, f"Renderer reference mismatch: {name}"
    spec = importlib.util.spec_from_file_location("pinned_matraix_renderer", reference / "persona_dimension_catalog.py")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    catalog_path = str(reference / "dimensions.json")
    catalog = renderer.load_dimension_catalog(catalog_path)["by_id"]
    pool = [json.loads(line) for line in (selection / "selected.jsonl").read_text().splitlines() if line.strip()]
    assert len(pool) == info["selected"] and len(pool) >= 30 and all(r["selected"] for r in pool)
    chosen, diversity = diverse_selection(pool, args.seed)
    table = pq.read_table(source)
    indexes = sorted(random.Random(info["sample_seed"]).sample(range(table.num_rows), info["sample_size"]))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "profiles").mkdir()
    (output / "prompts").mkdir()
    (output / "audits").mkdir()
    records = []
    for selected in chosen:
        candidate = selected["candidate_id"]
        index = indexes[int(candidate.split("_")[1]) - 1]
        original = table.slice(index, 1).to_pylist()[0]
        assert original["source_row_index"] == selected["source_row_index"]
        for rule in selected["evidence"]:
            assert str(original[rule["field"]]).strip() == str(rule["value"]).strip()
        dimensions = {k: v for k, v in original.items() if k not in METADATA}
        grouped = renderer.collect_dimension_items(dimensions, catalog_path=catalog_path)
        included = {key for items in grouped.values() for key, _, _ in items}
        audit = []
        for key, value in original.items():
            meta = catalog.get(key)
            if key in included:
                reason = "included"
            elif key in METADATA:
                reason = "source_metadata"
            elif renderer._should_skip_dim(key, meta):
                reason = "upstream_external_source_field"
            elif renderer._dim_value(dimensions, key) is None:
                reason = "upstream_null_empty_or_placeholder"
            else:
                assert meta and (renderer._is_default(value, meta.get("defaultValue")) or
                                 renderer._is_default(renderer._dim_value(dimensions, key), meta.get("defaultValue")))
                reason = "upstream_schema_default"
            audit.append({"field": key, "value": value, "disposition": reason})
        # Explicit zero overrides any environment variable: upstream treats it as unlimited.
        blocks = renderer.build_dimension_narrative(dimensions, catalog_path=catalog_path, max_chars=0)
        prompt = "## Who you are\n\n" + "\n\n".join(blocks) + "\n"
        assert included and "attributes omitted to fit" not in prompt
        prompt_path = output / "prompts" / f"{candidate}.md"
        prompt_path.write_text(prompt)
        write_json(output / "profiles" / f"{candidate}.json", original)
        write_json(output / "audits" / f"{candidate}.json", audit)
        records.append({"candidate_id": candidate, "source": original["source"],
                        "parquet_row_index": index, "source_row_index": original["source_row_index"],
                        "included_attributes": len(included), "prompt_characters": len(prompt),
                        "prompt_sha256": digest(prompt_path),
                        "dispositions": dict(Counter(a["disposition"] for a in audit)),
                        "profile": f"profiles/{candidate}.json", "prompt": f"prompts/{candidate}.md",
                        "audit": f"audits/{candidate}.json"})
    manifest = {"version": "full-persona-v2", "seed": args.seed, "cohort_size": 30,
                "selection": f"Diverse selection from {len(pool)} eligible candidates; no model outcomes used",
                "diversity": diversity, "builder_sha256": digest(Path(__file__)),
                "source": info["source"], "source_revision": info["source_revision"],
                "source_sha256": info["source_sha256"], "original_sample_seed": info["sample_seed"],
                "selection_file_sha256": digest(selection / "selected.jsonl"),
                "renderer_revision": REVISION, "renderer_file_sha256": HASHES,
                "policy": "MatrAIx dimension identity; all retained fields; no truncation, task/domain filtering, approved-facts restriction, or mandatory review workflow added",
                "status": "Prompt artifacts only; not connected to benchmark runners; no experiment launched",
                "source_counts": dict(Counter(r["source"] for r in records)), "profiles": records}
    write_json(output / "manifest.json", manifest)
    lines = ["# Fresh 30-persona cohort and system prompts", "",
             f"Selected from **{len(pool)} eligible profiles**, with balanced source quotas and greedy coverage of directional behavioral preferences. "
             f"Seed `{args.seed}` breaks ties only. No model judging or performance results were used.", "",
             diversity["method"], "", diversity["limitations"], "",
             "This replaces the superseded full_persona_v1 cohort. The full profile is rendered; diversity features only determine selection.", "",
             "Source counts: " + ", ".join(f"{k}: {v}" for k, v in manifest["source_counts"].items()) + ".", "",
             f"Uses the [MatrAIx renderer](https://github.com/MatrAIx-ai/MatrAIx-Persona-8B/blob/{REVISION}/src/matraix/persona_dimension_catalog.py). "
             "The prompt is the dimension-based identity block used by its system template, with no invented name. "
             "There is no task/domain filtering, knowledge-boundary instruction, character cap, or mandatory review workflow. "
             "All retained persona attributes are rendered; this is not limited to action rules. Upstream filtering "
             "removes null/empty/placeholders, schema-default values and designated external/source-dump fields. "
             "Source metadata is kept outside the prompt. Every input field is accounted for in the audit.", "",
             "These files are ready-to-inspect persona system prompts. Task context and the conversation driver "
             "will be designed separately. Existing benchmark runners have not been changed or launched.", "",
             "| Candidate | Source | Attributes injected | Prompt characters | Exact system prompt | Original record | Field audit |",
             "|---|---|---:|---:|---|---|---|"]
    for r in records:
        lines.append(f"| {r['candidate_id']} | {r['source']} | {r['included_attributes']} | {r['prompt_characters']} | "
                     f"[Prompt]({r['prompt']}) | [Full profile]({r['profile']}) | [Audit]({r['audit']}) |")
    (output / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(output), "profiles": len(records), "sources": manifest["source_counts"],
                      "attribute_range": [min(r['included_attributes'] for r in records), max(r['included_attributes'] for r in records)]}))


if __name__ == "__main__":
    main()
