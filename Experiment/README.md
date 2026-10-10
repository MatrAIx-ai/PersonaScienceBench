# Experiment workspace

> **Run configuration versus analysis snapshots:** the [main-run guide](../docs/MAIN_RUN.md) defines the current five-setting, 200-question campaign (1,000 episodes per fresh trial). The paper distinguishes performance, semantic diversity, and behavioral diversity. Collection totals and job states in experiment plans are dated records, not live scheduler status or proof of three complete trials for every selected persona. The published analysis workspace is a historical snapshot; newer local notebooks/results are not included in the main-run setup update.

This directory tracks the paper's experiments, their implementation, status, and results. The [integrated paper plan](../docs/design/benchmark_paper_plan.md#current-main-run-and-analysis-presentation-2026-10-01) is the current manuscript-level design: performance, semantic diversity, and behavioral diversity, with repeat-based claims limited to settings that have repeats. Human realism evaluation is outside scope. Individual plans retain historical collection notes; their later implementation records and the integration below supersede stale scheduling text.

| Folder | Purpose | Current scope |
|---|---|---|
| [Behavioral diversity](01_behavioral_diversity/PLAN.md) | Experiment 01 | [Expanded nonsemantic report](01_behavioral_diversity/ALL_PERSONAS_BEHAVIOR.md) and [executed notebook](01_behavioral_diversity/behavioral_analysis.ipynb): the current notebook displays off/155/001/003/046 (1,958 complete traces from 2,200 original slots), with actual API output tokens, reviews, clarification, and four pairwise heatmaps. The linked larger-cohort report is a historical snapshot. [Current semantic methods](01_behavioral_diversity/SEMANTIC_FIGURE_CAPTION.md) describe family-balanced final-response separation over 97 common trial-1 questions and local UMAP cases; within-persona distances are across questions, not repeats. |
| [Performance and field dependence](02_performance_and_fields/PLAN.md) | Experiment 02 | [Primary model scorecard](02_performance_and_fields/performance_analysis.ipynb): persona-off performance, Mean Persona Performance, fact recovery and self-repetition; tokens/tool calls are supporting metrics. [Saved table and definitions](02_performance_and_fields/MODEL_SCORECARD.md). Benchmark/super-family breakdowns and earlier heatmaps remain in the [supporting notebook](02_performance_and_fields/supporting/performance_analysis_before_scorecard.ipynb). |
| [SciConv fact recovery](08_sciconv_fact_recovery/PLAN.md) | Experiment 08 | Standalone quantitative experiment with its own recovery figure, result table and notebook. Offline analysis complete; new strict-protocol baseline has zero scored cases. |
| [Integrated offline metrics](09_offline_metric_suite/PLAN.md) | Reanalysis of 01/02/08 | [Metric report](09_offline_metric_suite/REPORT.md) and [executed notebook](09_offline_metric_suite/metric_suite.ipynb) for off/155/001/003/046. Current notebook figure: actor self-repetition (3 matching positions in 6-word windows; 79 common questions), failure-conditioned complete-fact-recovery bars without CIs, and descriptive cumulative native performance. Earlier exported reports/figures use superseded definitions. Original endpoints, source/study-cluster CIs, full source data; no new collection or inference. |

Scientific experiment folders use `PLAN.md` (design, implementation, findings, remaining work), status records, `code/`, and `data/`. Inactive experiments and retired launchers are in [_archive/20261002](_archive/20261002/README.md). Folder 07 retains repair metadata needed by active analyses; its launchers are archived. Existing folder IDs remain stable. Planned code is explicitly marked unimplemented. Existing large runs are referenced, not relocated or duplicated. Historical analyses in Experiments 01 and 02 and archived Experiment 04 reuse the six-setting, three-trial Astra panel (3,600 planned slots with incomplete valid coverage); Experiment 08 reuses its 20-case disambiguation subset. Their episode counts must not be added together. Experiment 02 additionally includes the completed single trials of 003/004/046 (4,200 total eligible slots), with trial counts explicit; they remain exploratory.

The current main-run configuration is in [MAIN_RUN.md](../docs/MAIN_RUN.md) and `configs/main_run/`; it targets three fresh trials of five settings. Historical collection settings are retained below and do not override that launcher.

Shared historical files: [setting](shared/setting.json), [frozen task panel](shared/task_selection.csv), [collection status](shared/run_status.json). The source and prepared inputs remain authoritative.

Refresh progress snapshots without API calls or job submission:

```bash
.venv/bin/python Experiment/refresh_status.py
```

Refresh reads each job's `progress.json`; it does not query Slurm. A partially processed run's running/queued/stopped state is unknown from this file alone. Error counts are preserved and flagged. Update each plan's implementation checklist and findings when work is completed; refreshing status does not mark scientific analysis complete.

## Historical top-ten expansion

The [expansion manifest](shared/top10_expansion.json) records the original nine-batch plan and baseline references: 5,400 additional episodes, 7,200 planned including the original panel and persona 155. This is not completed coverage. The current repeated panel contains off/148/155/089/001/127; 003/004/046 have one trial and 262/224/026 have no results. Original three-condition artifacts remain historical snapshots. `refresh_status.py` currently refreshes the original three trials only; consult source run records for expansion coverage.

## Operational history (outside the paper experiments)

[Rate-limit probe](_archive/20261002/06_cross_model_rate_limits/plan.json) and [repair records](07_error_repairs/PLAN.md) are archived operational documentation, excluded from the scientific experiment list. Original and repaired outcomes remain distinguishable in data provenance.

### Cleanup and active entry points (2026-10-02)

Active scientific folders are **01, 02, 08 and 09**. Shared utilities and Experiment 07 repair records remain dependencies. The [archive inventory](_archive/20261002/cleanup_manifest.json) records 156 preserved historical files moved out of active locations, including inactive experiments 03–06, retired repair/new-protocol launchers, and superseded figure/notebook revisions. Archived scripts are historical source, not runnable entry points from their new locations; restore the recorded original paths before using them. Generated Python/Jupyter caches and a self-referencing symlink were removed. Current notebooks and their outputs were preserved byte-for-byte.

Use the existing notebooks for current figures. Notebook builders and older analysis helpers are retained where current code/documentation depends on them; builders may regenerate older layouts and should not overwrite manually edited notebooks. No raw runs, current analysis data, paper figures or current figure exports were removed.

### Plot tracking

Include a Jupyter notebook with every plotting analysis, as requested by the user. Keep data provenance, aggregation/CI code, tables, plotting code, and saved figure outputs together. Current three-trial analysis: [notebook](02_performance_and_fields/three_trial_persona_analysis.ipynb).

### Experiment 08: SciConv fact recovery

[Plan](08_sciconv_fact_recovery/PLAN.md) · [Results](08_sciconv_fact_recovery/REPORT.md) · [Executed notebook](08_sciconv_fact_recovery/analysis.ipynb). Offline native fact-recovery reanalysis of 20 disambiguation cases, six settings, three Astra trials; paired intervals and cap-hit sensitivity. Original outcomes primary, repair outcomes separate. Neutral-paraphrase/difficulty-confirmation controls remain prospective. A separate new-protocol baseline was submitted but yielded zero scored cases because credits were exhausted; it is not pooled with the historical analysis.

Experiment 01 now includes [SciConv output-token results](01_behavioral_diversity/SCICONV_TOKENS.md) and an [executed notebook](01_behavioral_diversity/sciconv_tokens.ipynb), with role-separated per-call/per-turn data from 719 original Astra episodes.

### Generated figure cleanup (2026-10-02)

Standalone figure exports and generated figure QA artifacts were cleared from active and archived experiment directories. Notebook-embedded figures, plotting code, source tables, cached statistical/projection data, and manuscript assets under `paper/figures/` remain unchanged. Historical links to deleted renders/QA describe previous outputs; rerun the appropriate plotting cell to recreate figures. See [cleanup manifest](shared/figure_cleanup_manifest.json) for removed paths.

### Primary model scorecard

Experiment 02 now ends in a [model-level scorecard](02_performance_and_fields/performance_analysis.ipynb), with an explicit persona-off reference and three persona-averaged outcome/interaction metrics. [Saved table](02_performance_and_fields/data/model_scorecard/model_scorecard.md) · [definitions and coverage](02_performance_and_fields/MODEL_SCORECARD.md). Benchmark and super-family comparisons remain [supporting analysis](02_performance_and_fields/supporting/performance_analysis_before_scorecard.ipynb). Current rows and their limitations are documented in the saved scorecard. Delivered campaign inputs are catalogued in [results](../results/README.md).
