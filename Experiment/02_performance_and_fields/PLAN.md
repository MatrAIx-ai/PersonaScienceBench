# Performance and field dependence

## Question

Do persona-conditioned researchers change task performance, and does the effect vary with scientific field or expertise?

## Design and shared setting

Use the [shared setting](../shared/setting.json) and [paper plan](../../docs/design/benchmark_paper_plan.md). The current campaign is 200 frozen tasks (40 per source), persona off / 148 / 155, three independent complete episodes, GPT-6 Astra low for actor/researcher/model-based evaluator, and 128 GB / 30 CPUs per trial. The actor comparison and static reference are proposed extensions, not current jobs.

## Status

Trial-1 descriptive and paired analyses complete; three-trial analysis pending.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [ ] Keep the benchmark and super-family tables with task counts, three condition means, and 95% confidence intervals.
- [ ] Report matched-task changes, all-attempt scores, submission rates, technical errors, and conditional-on-submission scores.
- [ ] Annotate direct/adjacent/outside/unknown persona–field relationships separately from statistical or coding familiarity.
- [ ] Aggregate three repeats per task/condition and estimate source-study-aware uncertainty; retain missingness and paired baselines.

## Implementation

- `code/report_first_pass_ci.py` delegates to the existing interim analysis implementation.
- Trial-1 tables, matched scores, and paired-comparison output are copied into `data/trial_1/` with provenance.
- The repeated-run aggregation, study-cluster analysis, and expertise mapping are pending. Do not label interim task-bootstrap intervals as the final repeated analysis.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- Trial 1: 600 processed; 536 scored, 32 missing submissions, 32 technical/evaluation errors.
- 185 tasks were evaluable under all three conditions; missing submissions counted as zero.
- No significant paired difference was detected across 27 benchmark/family contrasts; none reached p < 0.05 before correction. This does not establish equivalence.

## Completion criteria

- [ ] Planned outputs exist with task/trial/condition provenance and denominators.
- [ ] Technical failures and missing submissions are reported separately.
- [ ] Analysis matches the documented experimental unit and uncertainty method.
- [ ] Results and limitations are written back into this plan; manuscript outputs are linked.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.

## Top-ten scope update (2026-09-29)

Expand the current collection to the ten largest absolute prior-pilot deviations: 046, 003, 004, 089, 001, 127, 262, 224, 148, 026. Nine new personas add 5,400 episodes across three trials; 148 and the paired persona-off trials already exist in the initial campaign. Keep 155 as an additional condition outside this selected ten. [Job and baseline manifest](../shared/top10_expansion.json). This supersedes the two-persona-only scope above; the existing trial-1 results remain unchanged. Multi-batch analysis and updated comparison families are pending.

## ASI judge transport repair (2026-09-29)

[Repair record](data/asi_judge_bridge_fix.json): the native text and VLM completion boundary now uses the configured controller-side judge (Astra low in this campaign). Sandbox isolation remains; model keys stay outside the evaluator. Native task-level model/temperature/token defaults are overridden explicitly and recorded, while prompts, rubrics, parsers, and aggregation stay unchanged. Evaluation version is `asi-b3-collaborative-b2-v1+asi-configured-judge-v1`. New episode processes pick up the repair; existing evaluations and potentially in-flight processes still reflect the old version. Historical errors need explicit regrading of sealed submissions before updated comparison tables are published. Offline fixtures passed; no paid test episodes were run.

## Concurrency update (2026-09-29)

At the user’s request, resumed trial 3 and all nine pending expansion batches now use 40 concurrent episode workers and 40 CPUs, retaining 128 GB and the sequential `afterany` chain. Trial 2 continues with 30 workers/CPUs. Frozen tasks, personas, model settings, and scientific budgets are unchanged. Pending submissions were replaced before execution; existing trial-3 outcomes are preserved on resume. [Submission audit](../shared/worker_40_resubmission.json) records old/new job IDs. Rate-limit safety at 40 workers has not yet been established by a completed run.

## Expansion concurrency reduction (2026-09-29)

Following observed rate-limit failures at 40 workers, the user requested 35 workers for the nine pending expansion batches. Those submissions were replaced with 35-worker / 35-CPU jobs, retaining 128 GB and sequential dependencies after running trial 3 (40 workers). This changes operational concurrency only. [Submission audit](../shared/worker_35_resubmission.json) preserves old/new IDs and commands; the earlier 40-worker record remains historical. The performance of 35 workers remains to be measured.

## Repeat priority update

At the user’s request, finish the three trials for expansion group 2 (089, 001, 127) first: current trial 1 job 1966123, then trial 2 job 1966126, then trial 3 job 1966129. The other five pending jobs remain scheduled afterward; none were cancelled. All remain sequential at 35 workers / 35 CPUs / 128 GB. [Dependency-change audit](../shared/expansion_group2_priority.json) records the old and new order.

## Expanded Trial 1 EDA

[Report](trial_1_all_personas_eda.md) covers eight personas plus off, with 20,000-resample 95% task-bootstrap intervals, benchmark and super-family means, coverage counts, matched baseline differences excluding ASI, and an 86-task common-panel sensitivity analysis. One episode remained running at the frozen snapshot; 262/224/026 have no Trial 1 results. Raw ASI scores span two judge setups and are descriptive only. Reproduction code and hashed normalized inputs are under `code/report_all_trial1.py` and `data/trial_1_all_personas/`. This is interim EDA; repeated-trial analysis and failure repairs remain pending.

## Error/missing repair queue

The user requested repairs after the running trial. Five later expansion jobs are held; [repair plan](../07_error_repairs/PLAN.md) and [job manifest](../07_error_repairs/status.json) track seven sequential 20-worker passes in separate directories. Original first-pass outcomes remain unchanged, including missing submissions.
