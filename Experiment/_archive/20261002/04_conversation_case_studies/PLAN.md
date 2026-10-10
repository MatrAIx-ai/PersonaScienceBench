# Conversation case studies

## Question

What traceable chain connects profile wording, researcher behavior, actor action, and outcome?

## Design and shared setting

Use the [shared setting](../../../shared/setting.json) and [paper plan](../../../../docs/design/benchmark_paper_plan.md). The current campaign is 200 frozen tasks (40 per source), persona off / 148 / 155, three independent complete episodes, GPT-6 Astra low for actor/researcher/model-based evaluator, and 128 GB / 30 CPUs per trial. The actor comparison and static reference are proposed extensions, not current jobs.

## Status

Exploratory pilot cases available; expanded-study cases pending.

See [status.json](status.json) and the [shared run status](../../../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [ ] Select two or three task-matched cases involving 148 or 155 and persona off.
- [ ] Record exact profile evidence, trial/task/condition IDs, event IDs, short excerpts, subsequent actions, and native outcomes.
- [ ] Include helpful, unproductive, or behavior-changing examples; do not infer a mechanism from score alone.
- [ ] Hide outcome scores during semantic annotation where practicable and check a subset with a second judge.

## Implementation

- Existing narrative: `reports/full_persona_v2/case_studies.md`; profiles and recorded transcripts are linked there.
- `data/case_annotation_template.json` defines the evidence record for new cases.
- Expanded-case selection and annotation are not complete; no automatic semantic judge is implemented here.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- Pilot examples include detailed SciConv clarification, approval stalls, and Mandarin language adaptation.
- Persona 046 examples belong to the historical pilot and must not be presented as current-panel evidence.

## Completion criteria

- [ ] Planned outputs exist with task/trial/condition provenance and denominators.
- [ ] Technical failures and missing submissions are reported separately.
- [ ] Analysis matches the documented experimental unit and uncertainty method.
- [ ] Results and limitations are written back into this plan; manuscript outputs are linked.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.

## Top-ten scope update (2026-09-29)

Expand the current collection to the ten largest absolute prior-pilot deviations: 046, 003, 004, 089, 001, 127, 262, 224, 148, 026. Nine new personas add 5,400 episodes across three trials; 148 and the paired persona-off trials already exist in the initial campaign. Keep 155 as an additional condition outside this selected ten. [Job and baseline manifest](../../../shared/top10_expansion.json). This supersedes the two-persona-only scope above; the existing trial-1 results remain unchanged. Multi-batch analysis and updated comparison families are pending.
