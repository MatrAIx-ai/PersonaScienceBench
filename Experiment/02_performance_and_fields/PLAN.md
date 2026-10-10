# Performance and field dependence

## Question

Do persona-conditioned researchers change task performance, and does the effect vary with scientific field or expertise?

## Design and shared setting

Use the [integrated paper plan](../../docs/design/benchmark_paper_plan.md) and frozen source manifests. Current primary analysis covers off/148/155/089/001/127 across three completed Astra-low trial jobs and 003/004/046 across one completed trial job, on the same 200 tasks (40 per source). Available endpoints and original-only sensitivity are separate. The [shared setting](../shared/setting.json) retains the original three-condition configuration as history. Sol and the new SciConv protocol are separate. Cancelled initial-job records are excluded; 003/004/046 are included with explicit single-trial labels.

## Status

**Current:** [ALL_AVAILABLE_PERFORMANCE.md](ALL_AVAILABLE_PERFORMANCE.md) and the executed performance notebook cover every eligible persona. Heatmaps are retained, and the forest alternative is discarded. The following consolidation describes the preserved earlier six-setting analysis.

The requested offline consolidation is complete: [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md), [performance_analysis.ipynb](performance_analysis.ipynb), and `data/consolidated/`. Existing benchmark/super-family table structures are retained. New analyses add same-task/same-trial contrasts, corrected-version ASI filtering, submission/conditional scores, within-task run SDs, complete-panel and no-ASI sensitivities, and an explicit metadata-overlap audit. Collection missingness still limits scientific conclusions.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [x] Keep the benchmark and super-family table structures with six setting rows, task/episode counts, means and 95% confidence intervals.
- [x] Report matched-task/trial changes, evaluable-attempt scores (scientific missing submissions = zero), submission rates, technical errors, and conditional-on-submission scores. Infrastructure failures remain missing.
- [x] Create direct/adjacent/outside/unknown metadata-overlap records with explicit profile evidence, separate from statistical/coding familiarity. These automatic rules are exploratory and do not establish actual competence or a causal expertise effect.
- [x] Aggregate repeats within task, estimate source-study-aware uncertainty, report observed within-task score SDs, and retain missingness and paired baselines.

## Implementation

- `code/report_first_pass_ci.py` delegates to the existing interim analysis implementation.
- Trial-1 tables, matched scores, and paired-comparison output are copied into `data/trial_1/` with provenance.
- `code/consolidate_performance.py` uses the existing hashed snapshot; `code/plot_matched_performance.py` exports matched benchmark/family figures. All 108 absolute-score means and denominators reproduce the earlier report. New CIs use a fixed reproducible seed.
- Original pairs are primary; repair outcomes, all-six-setting complete panels and ASI-free family summaries are sensitivity analyses. Shared study-cluster routines and executed-notebook builder live in `../shared/`.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- Current three-trial consolidation: most original benchmark-level matched intervals include zero. Strict common coverage is 103 original tasks and 116 after-repair tasks, with no original ASI task meeting the full corrected-version panel. Family effects remain descriptive and conditional on sparse source/study strata. See [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md).
- The following three bullets preserve the earlier, smaller trial-1 analysis:
- Trial 1: 600 processed; 536 scored, 32 missing submissions, 32 technical/evaluation errors.
- 185 tasks were evaluable under all three conditions; missing submissions counted as zero.
- No significant paired difference was detected across 27 benchmark/family contrasts; none reached p < 0.05 before correction. This does not establish equivalence.

## Completion criteria for the current offline consolidation

- [x] Outputs exist with task/trial/condition provenance and denominators.
- [x] Technical failures and missing submissions are reported separately.
- [x] Analysis matches the documented experimental unit and uncertainty method.
- [x] Results and limitations are written back into this plan; reports, notebooks and figures are linked.

Collection limitations remain explicit; completing the analysis does not make the underlying dataset complete. [Figure QA](figures/consolidated/qa/QA_NOTES.md) records the final checks.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.
- 2026-09-30: Completed matched three-trial consolidation, evaluator filtering, coverage and run-variation summaries, field-overlap audit, sensitivities, executed notebook and figure QA. No new model calls or regrading.
- 2026-09-30: Redrew Figure 4 using `ars-codex:academic-research-suite` v3.22.2. The executed performance notebook now includes two forest panels, all 45 printed estimates and 95% CIs, 8 pt minimum text, a full caption and reproducible plotting source. Estimates and denominators are unchanged. Historical ARS QA (discarded when the user removed the forest alternative) record the checks.

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

## Three-trial Astra report and figures

Generated `three_trial_persona_results.md`, two annotated bar figures in `figures/three_trials/` (PNG/PDF/SVG), and normalized data/CSV tables in `data/three_trials/`. Reproduce with `code/report_three_trials.py`. Scope: off/148/155/089/001/127 across three trials, after one repair pass; original-outcome sensitivity tables retained. Each task averages available trial scores, then tasks receive equal weight. Pointwise 95% intervals resample studies within source, preserving observed source weights. Figures include numeric mean/CI annotations and task/episode denominators. Analysis remains provisional because technical errors, conditional retries, and ASI evaluator drift limit comparability; these are not significance tests or pure trial-randomness intervals. Input hashes, unique trial/task/condition keys, summary denominators, and CI bounds were checked; both figures were visually inspected.

## Notebook tracking convention

User preference: every plotting analysis must include a Jupyter notebook documenting data inputs, aggregation, CI computation, tables, plot code, and saved outputs. The three-trial notebook is `three_trial_persona_analysis.ipynb`; it reproduces the existing summary from the frozen snapshot and exports both annotated figures.

## Current scope: completed-trial personas, heatmaps only

The user discarded the forest plot and requested every persona with at least one completed trial. The cancelled initial run is excluded entirely. Include off/148/155/089/001/127 across three trials and 003/004/046 across one trial, without requiring three repeats. All 4,200 planned slots of those completed campaigns are tracked; 3,973 have an evaluable available endpoint. Unscored episodes remain missing.

[All-available report](ALL_AVAILABLE_PERFORMANCE.md), `data/all_available/`, and the executed `performance_analysis.ipynb` are now the primary expanded performance analysis. New absolute and matched-change heatmaps preserve the original design; the previous six-setting heatmap and historical bar figures are retained separately. Repairs are within-trial endpoints, not additional trials. A failed repair falls back to a valid original result; original-only sensitivity remains available. Counts, evaluator compatibility and single-trial uncertainty limits are explicit.

## Model-level scorecard (2026-10-02)

The primary entry point is now `performance_analysis.ipynb`, rewritten around one row per actor model: explicit persona-off performance, Mean Persona Performance, fact recovery, actor self-repetition, absolute actor output in thousands of tokens per episode, and execution/inspection tool calls per episode. Current eligible data support only a historical Astra-low row. Each metric uses a common five-setting question panel, equal setting/source weights and source-stratified study-cluster intervals. Unequal repeats and historical evaluator versions are disclosed. [Report and definitions](MODEL_SCORECARD.md); CSV/Markdown/LaTeX exports in `data/model_scorecard/`. The prior executed notebook, including benchmark/super-family results, is preserved at `supporting/performance_analysis_before_scorecard.ipynb`. No inference or benchmark submission was performed.

### Resource normalization update

Removed worst-persona performance. Resource columns now show the ratio of four-persona mean use to persona-off mean use on the same metric-specific question panel. Numerator and denominator are recomputed jointly in each study-bootstrap draw. A ratio of 1 is equal use; the ratios are not success-adjusted efficiency. Raw means and intervals are retained in `data/model_scorecard/resource_use_raw.csv` and displayed in the notebook.

### Absolute resource units (supersedes ratio columns)

The primary scorecard now reports actor output in k tokens/episode and tool calls/episode. Token estimates and confidence limits are divided by 1,000 only as a unit conversion. No baseline normalization is used in the main table. Raw counts and persona-off ratios remain supporting comparisons.

## Aggregate model leaderboard figure (2026-10-05)

Added a three-panel bar figure to the final section of `performance_analysis.ipynb`: Mean Persona Performance, fact recovery, and actor self-repetition. Model-colored bars average the four injected personas and applicable benchmarks equally with 95% intervals from 20,000 source-stratified study-cluster bootstrap samples; performance includes persona-off point-reference ticks. Per the updated reporting instruction, each model uses its own available eligible questions, retaining all-five-setting eligibility within each model but applying no intersection across models. Astra uses 101 / 20 / 79 questions and Haiku uses 200 / 20 / 137 for performance / fact recovery / repetition. Means and intervals now match the supporting scorecard; Mean Persona Performance is 48.82% for Astra and 33.82% for Haiku. Exact model-specific membership, coverage exclusions, input hashes, values and source CSV are saved under `data/model_leaderboard/`; PDF/SVG/PNG exports are under `figures/model_leaderboard/`. [Methods and candidate caption](MODEL_LEADERBOARD.md) document differing coverage, unequal repeats, historical evaluator differences and the exploratory repetition matcher. These are descriptive summaries of historical configurations, not matched or paired model comparisons. Offline analysis only.
