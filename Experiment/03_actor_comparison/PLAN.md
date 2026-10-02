# Actor comparison

> Withdrawn on 2026-10-01 at the user’s request. The incomplete Sol campaign is excluded from current results and public traces; raw runs are retained in `runs/_archive/20261001-incomplete-campaigns/`. Plans and counts below are historical.

## Question

Which actor models remain effective across different researcher profiles?

## Design and shared setting

Use the [shared setting](../shared/setting.json) and [paper plan](../../docs/design/benchmark_paper_plan.md). The current campaign is 200 frozen tasks (40 per source), persona off / 148 / 155, three independent complete episodes, GPT-6 Astra low for actor/researcher/model-based evaluator, and 128 GB / 30 CPUs per trial. The actor comparison and static reference are proposed extensions, not current jobs.

## Status

Proposed extension; not started or submitted.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [ ] Use the same 200 tasks, three conditions, and three complete episodes for each of three actors.
- [ ] Keep the Astra-low researcher and evaluator, task inputs, tools, and budgets fixed; change only the actor.
- [ ] Report per-benchmark means, completion, worst-persona performance, paired changes, and ranking changes.

## Implementation

- Only GPT-6 Astra data currently exist for the expanded panel.
- Select two additional actors and implement actor-only configuration before submission.
- The current coordinator sets the same model for all roles; it must be extended before using it for this comparison. No actor-comparison launcher is implemented here.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- No cross-actor result is available.
- Two additional actors would add 3,600 episodes, giving 5,400 across three actors.

## Completion criteria

- [ ] Planned outputs exist with task/trial/condition provenance and denominators.
- [ ] Technical failures and missing submissions are reported separately.
- [ ] Analysis matches the documented experimental unit and uncertainty method.
- [ ] Results and limitations are written back into this plan; manuscript outputs are linked.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.
