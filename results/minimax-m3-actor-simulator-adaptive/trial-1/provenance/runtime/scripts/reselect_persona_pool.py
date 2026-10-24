#!/usr/bin/env python3
"""Rescreen the original 300 candidates for broad, observable persona behavior."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import random

import pyarrow.parquet as pq

from build_full_persona_cohort import HASHES, METADATA, REVISION, digest, write_json


# Explicit fields: no inferred habits from demographic labels or broad traits.
AREAS = {
    "communication": [
        "cog_verbosity", "cog_formality", "cog_directness", "cog_humor",
        "cog_emotional_expressiveness", "cog_precision_of_language", "cog_use_of_jargon",
        "cog_emoji_use", "cog_politeness", "cog_storytelling", "cog_empathy_expression",
        "pref_detail_brief_vs_full", "pref_text_vs_call", "peeve_unexplained_jargon",
        "peeve_condescension", "peeve_being_interrupted", "peeve_forced_small_talk",
    ],
    "interaction": [
        "cog_question_asking", "cog_feedback_receptiveness", "cog_conflict_approach",
        "cog_assertiveness", "pref_team_vs_solo", "pref_lead_vs_follow",
        "pref_big_group_vs_one_on_one", "pref_competition_vs_collab",
        "developer_help_seeking_preference", "stackoverflow_participation_style",
        "pr_collaboration_style", "issue_engagement_style",
    ],
    "decisions": [
        "decision_style", "cog_decision_speed", "cog_risk_framing",
        "pref_logic_vs_intuition", "pref_speed_vs_accuracy", "pref_quality_vs_quantity",
        "pref_novelty_vs_familiarity", "pref_stability_vs_change",
    ],
    "workflow": [
        "pref_plan_vs_spontaneous", "pref_routine_vs_variety", "cog_multitasking",
        "cog_reading_vs_watching", "cog_visual_vs_verbal", "cog_big_picture_vs_detail",
        "habit_to_do_lists", "habit_goal_setting", "habit_daily_reflection",
        "habit_re_reading_texts_before_sending", "habit_inbox_zero_discipline",
        "habit_backing_up_files", "debugging_strategy", "codebase_onboarding_style",
        "bug_fix_scope_preference", "bug_fix_test_behavior",
        "code_modularity_preference", "code_type_system_orientation", "code_comment_style",
        "code_testing_approach", "code_observability_habit", "code_performance_priority",
        "code_naming_verbosity", "code_complexity_tolerance", "code_indentation_style",
    ],
    "tool_collaboration": [
        "coding_agent_autonomy_preference", "coding_agent_control_expectation",
        "coding_agent_explanation_preference", "coding_agent_context_sharing_comfort",
        "coding_agent_memory_preference", "coding_agent_failure_tolerance",
        "human_help_boundary_for_ai_coding", "coding_ai_output_trust",
    ],
}
NON_DIRECTIONAL = {
    "neutral", "balanced", "moderate", "average", "sometimes", "medium",
    "context-dependent", "no strong preference", "mixed approach",
    "mixed (context-dependent)", "balanced consideration", "inconsistent/mixed",
    "depends on context", "depends on task", "not sure", "fine",
}
RULES = {
    "concrete_behavior": "At least four retained attributes in the explicit behavioral field map.",
    "directional_behavior": "At least three mapped values outside the explicit neutral/context-dependent value set.",
    "behavioral_breadth": "Directional evidence spans at least two behavioral areas.",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/persona_case_study/full_profile_selection_v2"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    old = root / "data/persona_case_study/action_selection_v1"
    info = json.loads((old / "report.json").read_text())
    previous = {json.loads(s)["candidate_id"] for s in (old / "selected.jsonl").read_text().splitlines() if s.strip()}
    old_sample = {r["candidate_id"]: r for r in (json.loads(s) for s in (old / "sampled.jsonl").read_text().splitlines() if s.strip())}
    source = root / "external/persona_case_study/sample.parquet"
    assert digest(source) == info["source_sha256"]
    ref = root / "external/persona_case_study/rendering_reference"
    for name, expected in HASHES.items():
        assert digest(ref / name) == expected
    spec = importlib.util.spec_from_file_location("pinned_matraix_renderer", ref / "persona_dimension_catalog.py")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    catalog_path = str(ref / "dimensions.json")
    catalog = renderer.load_dimension_catalog(catalog_path)["by_id"]
    fields = [f for values in AREAS.values() for f in values]
    assert len(fields) == len(set(fields)) and all(f in catalog for f in fields)
    table = pq.read_table(source)
    indexes = sorted(random.Random(info["sample_seed"]).sample(range(table.num_rows), info["sample_size"]))
    records = []
    for number, index in enumerate(indexes, 1):
        candidate = f"candidate_{number:03d}"
        row = table.slice(index, 1).to_pylist()[0]
        assert row["source_row_index"] == old_sample[candidate]["source_row_index"]
        dimensions = {k: v for k, v in row.items() if k not in METADATA}
        grouped = renderer.collect_dimension_items(dimensions, catalog_path=catalog_path)
        retained = {key for items in grouped.values() for key, _, _ in items}
        evidence = []
        filtered = []
        for area, keys in AREAS.items():
            for key in keys:
                value = row.get(key)
                if key not in retained:
                    if value is not None:
                        filtered.append({"field": key, "value": value,
                                         "reason": "Not retained by pinned upstream rendering (default, placeholder, or source-field filter)"})
                    continue
                directional = str(value).strip().lower() not in NON_DIRECTIONAL
                evidence.append({"field": key, "value": value, "area": area, "directional": directional})
        directional = [e for e in evidence if e["directional"]]
        areas = sorted({e["area"] for e in directional})
        checks = {"concrete_behavior": len(evidence) >= 4,
                  "directional_behavior": len(directional) >= 3,
                  "behavioral_breadth": len(areas) >= 2}
        records.append({"candidate_id": candidate, "source": row["source"],
                        "parquet_row_index": index, "source_row_index": row["source_row_index"],
                        "selected": all(checks.values()), "checks": checks,
                        "failed_rules": [k for k, v in checks.items() if not v],
                        "counts": {"concrete_behavior": len(evidence), "directional_behavior": len(directional),
                                   "areas": areas, "full_profile_retained_attributes": len(retained)},
                        "evidence": evidence, "render_filtered_behavior_fields": filtered})
    selected = [r for r in records if r["selected"]]
    current = {r["candidate_id"] for r in selected}
    report = {"version": "full-profile-selection-v2", "rules": RULES, "behavioral_fields": AREAS,
              "non_directional_values": sorted(NON_DIRECTIONAL), "source": info["source"],
              "source_revision": info["source_revision"], "source_sha256": info["source_sha256"],
              "sample_seed": info["sample_seed"], "source_rows": table.num_rows, "sample_size": len(records),
              "renderer_revision": REVISION, "renderer_file_sha256": HASHES,
              "selection_script_sha256": digest(Path(__file__)),
              "selected": len(selected), "rejected": len(records) - len(selected),
              "sample_sources": dict(Counter(r["source"] for r in records)),
              "selected_sources": dict(Counter(r["source"] for r in selected)),
              "failure_counts": {k: sum(not r['checks'][k] for r in records) for k in RULES},
              "comparison_with_v1": {"added": sorted(current - previous), "removed": sorted(previous - current),
                                     "retained": sorted(previous & current)},
              "policy": "No domain restriction, model judging, or empirical outcome selection. Eligibility evidence is not the injection: broad profile rendering remains separate.",
              "status": "Eligible pool only; a replacement 30-persona cohort has not been sampled"}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name, rows in [("sampled.jsonl", records), ("selected.jsonl", selected)]:
        (out / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    write_json(out / "report.json", report)
    lines = ["# Full-profile eligibility pool v2", "",
             "Rescreened the same original 300 profiles with stable candidate IDs. No new sampling, "
             "domain filter, model calls, or outcome-based selection. A replacement 30 has not been chosen.", "",
             "## Three screening rules", ""]
    lines += [f"{n}. {text}" for n, text in enumerate(RULES.values(), 1)]
    lines += ["", "The five areas are communication, interaction, decisions, workflow, and tool collaboration. "
              "Coding preferences may contribute but are not required. Demographics and general traits alone "
              "do not establish concrete behavior. Fixed field/value rules are proxies for usable persona "
              "information, not evidence that these profiles will change model behavior.", "",
              "Evidence uses fields that survive the pinned MatrAIx renderer. Its default/placeholder "
              "filter can remove meaningful preferences; filtered fields are recorded explicitly. "
              "The eligibility criteria never limit injection to the matching fields: full-profile rendering "
              "retains all other usable attributes, without a domain or knowledge-boundary restriction.", "",
              f"**Eligible: {len(selected)}/300; excluded: {300-len(selected)}.**", "",
              "| Source | Sampled | Previously eligible | Now eligible |", "|---|---:|---:|---:|"]
    for source_name, count in sorted(report["sample_sources"].items()):
        prior = sum(r['candidate_id'] in previous and r['source'] == source_name for r in records)
        lines.append(f"| {source_name} | {count} | {prior} | {report['selected_sources'].get(source_name, 0)} |")
    lines += ["", f"Compared with the previous 131: {len(current-previous)} added, {len(previous-current)} removed, "
              f"{len(current & previous)} retained. No target pool size was imposed. Field-rich synthetic "
              "profiles can still be favored; this is an eligibility screen, not a representative population sample.", "",
              "[Exact rules and pool changes](report.json) · [Eligible records and evidence](selected.jsonl) · "
              "[All 300 decisions, original values and filtered fields](sampled.jsonl)", "",
              "## Every candidate", "",
              "| Candidate | Source | Eligible | Concrete fields | Directional fields | Areas | Failed rules |",
              "|---|---|---|---:|---:|---|---|"]
    for r in records:
        c = r['counts']
        lines.append(f"| {r['candidate_id']} | {r['source']} | {'Yes' if r['selected'] else 'No'} | "
                     f"{c['concrete_behavior']} | {c['directional_behavior']} | {', '.join(c['areas']) or '—'} | "
                     f"{', '.join(r['failed_rules']) or '—'} |")
    (out / "README.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: report[k] for k in ['selected','rejected','selected_sources','failure_counts']}, indent=2))
    print('Added:', ', '.join(sorted(current - previous)))
    print('Removed:', ', '.join(sorted(previous - current)))


if __name__ == "__main__":
    main()
