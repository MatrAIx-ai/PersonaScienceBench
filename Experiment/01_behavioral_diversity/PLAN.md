# Behavioral diversity

## Question

Do the two profiles produce repeatable collaboration patterns beyond run variation?

## Design and shared setting

Use the [shared setting](../shared/setting.json) and [paper plan](../../docs/design/benchmark_paper_plan.md). The current campaign is 200 frozen tasks (40 per source), persona off / 148 / 155, three independent complete episodes, GPT-6 Astra low for actor/researcher/model-based evaluator, and 128 GB / 30 CPUs per trial. The actor comparison and static reference are proposed extensions, not current jobs.

## Status

Data collection in progress; summary-field extraction implemented; full trace analysis pending.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [ ] Count additional plan reviews, result revisions, collaboration requests, and budget exhaustion separately from required reviews.
- [ ] Analyze SciConv clarification recall/precision, grounding, memory, and questions after the first researcher reply.
- [ ] Extract visible-message characters and language by role; separate them from API token usage.
- [ ] Build role-separated semantic trajectories with a frozen multilingual encoder; compare against baseline repeat variation.

## Implementation

- Current summary fields can be exported with `code/extract_summary_metrics.py`. Missing fields remain missing; they are not zero.
- Detailed message/language extraction, semantic trajectories, and three-trial statistics are not implemented here.
- Existing exploratory implementations: `scripts/report_top_persona_deviations.py` and `scripts/report_full_persona_snapshot.py`; these target older data and require adaptation.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- Exported [600 trial-1 summary records](data/trial_1_summary_metrics.csv); no final behavioral-diversity finding from the expanded three-trial panel yet.
- Original pilot traces motivate the hypotheses but are not expanded-study results.

## Completion criteria

- [ ] Planned outputs exist with task/trial/condition provenance and denominators.
- [ ] Technical failures and missing submissions are reported separately.
- [ ] Analysis matches the documented experimental unit and uncertainty method.
- [ ] Results and limitations are written back into this plan; manuscript outputs are linked.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.

## Top-ten scope update (2026-09-29)

Expand the current collection to the ten largest absolute prior-pilot deviations: 046, 003, 004, 089, 001, 127, 262, 224, 148, 026. Nine new personas add 5,400 episodes across three trials; 148 and the paired persona-off trials already exist in the initial campaign. Keep 155 as an additional condition outside this selected ten. [Job and baseline manifest](../shared/top10_expansion.json). This supersedes the two-persona-only scope above; the existing trial-1 results remain unchanged. Multi-batch analysis and updated comparison families are pending.
