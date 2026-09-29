# Static reference (optional)

## Question

How does the interactive setting compare with task-owned context provided upfront and no simulator?

## Design and shared setting

Use the [shared setting](../shared/setting.json) and [paper plan](../../docs/design/benchmark_paper_plan.md). The current campaign is 200 frozen tasks (40 per source), persona off / 148 / 155, three independent complete episodes, GPT-6 Astra low for actor/researcher/model-based evaluator, and 128 GB / 30 CPUs per trial. The actor comparison and static reference are proposed extensions, not current jobs.

## Status

Optional; not started or submitted.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [ ] Select ten non-image-centric execution/design tasks from the frozen panel; exclude SciConv.
- [ ] Run one actor three times per task with task-owned context upfront, evaluator answers private, and comparable total actor budgets.
- [ ] Compare with the corresponding interactive persona-off and persona-on episodes.

## Implementation

- No static-reference task selection, input-conversion implementation, or launcher is present.
- A reviewed static-context assembly is needed; do not expose references or gold answers.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- No results available.
- If adopted, this adds 30 episodes; it is outside the current 1,800-episode campaign.

## Completion criteria

- [ ] Planned outputs exist with task/trial/condition provenance and denominators.
- [ ] Technical failures and missing submissions are reported separately.
- [ ] Analysis matches the documented experimental unit and uncertainty method.
- [ ] Results and limitations are written back into this plan; manuscript outputs are linked.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.
