# Trial 1 EDA: persona performance by benchmark and super-family

Snapshot: **2026-09-30T01:59:29.240140+00:00**. One Trial 1 episode per task/condition; this is an interim descriptive analysis, not the three-trial paper result.

## Scope and principal findings

Available results cover **8 personas plus persona-off**. Personas 262, 224, and 026 have no Trial 1 results yet. Each condition targets the same 200 tasks, with 40 per benchmark. Actor, researcher simulator, and model judge use GPT-6 Astra with low reasoning.

Technical failures cause uneven coverage, especially for persona 003. Raw available-case means must not be interpreted as a fair overall ranking. Pairwise matched comparisons and a common-panel sensitivity analysis appear below. Missing submissions are zero; technical errors, running episodes, and otherwise unscored cases are excluded from score means, not silently treated as incorrect scientific answers.

**ASI comparability warning:** off/148/155 were evaluated with the older ASI judge setup; expansion personas use the repaired configured-judge bridge. The reported ASI means are descriptive snapshots. Judge/model configuration drift prevents a clean cross-batch persona attribution. Paired comparison tables exclude ASI for every persona; the raw super-family tables include it and inherit this caveat.

## Episode coverage

Finished episodes can include missing submissions. Every row below has a planned denominator of 200.

| Persona | Scored | Missing submission (0) | Technical errors | Running | Other unscored | Not started | Evaluable / 200 |
|---|---|---|---|---|---|---|---|
| Off | 178 | 12 | 10 | 0 | 0 | 0 | 190 |
| 148 | 180 | 9 | 11 | 0 | 0 | 0 | 189 |
| 155 | 178 | 11 | 11 | 0 | 0 | 0 | 189 |
| 046 | 165 | 11 | 24 | 0 | 0 | 0 | 176 |
| 003 | 97 | 7 | 96 | 0 | 0 | 0 | 104 |
| 004 | 160 | 11 | 29 | 0 | 0 | 0 | 171 |
| 089 | 184 | 10 | 5 | 1 | 0 | 0 | 194 |
| 001 | 184 | 9 | 7 | 0 | 0 | 0 | 193 |
| 127 | 183 | 8 | 9 | 0 | 0 | 0 | 191 |
| 262 | 0 | 0 | 0 | 0 | 0 | 200 | 0 |
| 224 | 0 | 0 | 0 | 0 | 0 | 200 | 0 |
| 026 | 0 | 0 | 0 | 0 | 0 | 200 | 0 |

## Score definitions and uncertainty

- ASI-Bench: native score / native maximum × 100; only valid scored evaluations.
- BixBench: correctness × 100.
- DiscoveryBench: native final score × 100.
- EXP-Bench: final gated coverage mean, falling back to initial only when no final record exists; already on a 0–100 scale.
- SciConvBench: final resolution with intent preserved (FRR) × 100; this evaluates the specification/conversation, not scientific solver correctness.

Each cell is **mean [pointwise 95% CI]; n=evaluable tasks**. Intervals use 20,000 percentile task-bootstrap resamples (seed 20260929), stratified by benchmark source. Within-source observed sample sizes are fixed. Pairwise differences resample matched task differences. These follow the earlier Trial 1 descriptive CI convention.

These intervals reflect task resampling, not repeat-run uncertainty. They do not account for dependence among tasks from the same study or correct for multiple comparisons; sparse or constant-valued groups may have degenerate intervals. They should not establish statistical significance, equivalence, or a final persona ranking.

## Performance by benchmark

Available-case means use each persona’s own evaluable tasks. Each benchmark has 40 planned tasks per condition. Higher values are better within each benchmark; different native metrics are not calibrated to one another.

| Persona | ASI-Bench* | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 49.40 [35.49, 63.43]; n=31 | 32.50 [17.50, 47.50]; n=40 | 10.35 [3.37, 18.68]; n=39 | 44.03 [37.53, 50.49]; n=40 | 85.00 [72.50, 95.00]; n=40 |
| 148 | 50.31 [37.02, 63.55]; n=32 | 30.00 [17.50, 45.00]; n=40 | 15.04 [6.11, 25.68]; n=37 | 42.73 [36.49, 48.81]; n=40 | 87.50 [77.50, 97.50]; n=40 |
| 155 | 51.55 [38.27, 64.80]; n=32 | 32.50 [17.50, 47.50]; n=40 | 12.86 [4.49, 23.06]; n=37 | 43.73 [36.93, 50.43]; n=40 | 87.50 [77.50, 97.50]; n=40 |
| 046 | 57.73 [42.70, 72.57]; n=23 | 29.73 [16.22, 45.95]; n=37 | 18.30 [9.93, 27.89]; n=37 | 44.68 [37.96, 51.67]; n=39 | 77.50 [65.00, 90.00]; n=40 |
| 003 | 61.22 [33.55, 86.20]; n=8 | 35.71 [17.86, 53.57]; n=28 | 14.04 [6.61, 22.45]; n=22 | 44.22 [37.00, 50.11]; n=6 | 82.50 [70.00, 92.50]; n=40 |
| 004 | 41.69 [28.76, 55.68]; n=23 | 28.95 [15.79, 44.74]; n=38 | 14.25 [6.17, 24.12]; n=32 | 45.92 [38.61, 53.25]; n=38 | 87.50 [77.50, 97.50]; n=40 |
| 089 | 48.28 [36.92, 59.72]; n=38 | 32.50 [17.50, 47.50]; n=40 | 15.25 [7.82, 23.76]; n=36 | 45.52 [38.22, 52.86]; n=40 | 90.00 [80.00, 97.50]; n=40 |
| 001 | 50.41 [38.89, 62.27]; n=37 | 32.50 [17.50, 47.50]; n=40 | 14.18 [6.24, 23.86]; n=39 | 41.98 [34.32, 49.83]; n=37 | 85.00 [72.50, 95.00]; n=40 |
| 127 | 54.91 [43.13, 66.46]; n=34 | 33.33 [17.95, 48.72]; n=39 | 15.21 [6.79, 25.05]; n=38 | 43.92 [36.94, 50.83]; n=40 | 92.50 [82.50, 100.00]; n=40 |
| 262 | — | — | — | — | — |
| 224 | — | — | — | — | — |
| 026 | — | — | — | — | — |

## Performance by scientific super-family

Task-weighted averages of normalized native scores; these are descriptive composites of different metrics. No reweighting to equal source or family weights is applied. The available source composition can differ across personas because failures are excluded.

| Super-family | Planned tasks | ASI | Bix | Discovery | EXP | SciConv |
|---|---|---|---|---|---|---|
| Life sciences | 50 | 5 | 40 | 5 | 0 | 0 |
| Physical sciences & engineering | 63 | 23 | 0 | 0 | 6 | 34 |
| Math & CS | 55 | 12 | 0 | 3 | 34 | 6 |
| Social sciences & humanities | 32 | 0 | 0 | 32 | 0 | 0 |

| Persona | Life sciences | Physical sciences & engineering | Math & CS | Social sciences & humanities |
|---|---|---|---|---|
| Off | 29.08 [17.32, 41.58]; n=48 | 69.23 [59.77, 78.02]; n=57 | 49.71 [42.18, 56.98]; n=54 | 11.94 [3.63, 22.32]; n=31 |
| 148 | 27.42 [15.83, 40.47]; n=46 | 68.15 [58.95, 76.76]; n=57 | 54.07 [47.11, 60.94]; n=55 | 14.72 [5.54, 25.90]; n=31 |
| 155 | 28.97 [16.98, 41.51]; n=48 | 67.82 [58.53, 76.45]; n=57 | 53.91 [47.14, 60.36]; n=55 | 15.65 [5.12, 28.30]; n=29 |
| 046 | 27.79 [15.34, 41.05]; n=43 | 67.49 [56.77, 77.26]; n=54 | 52.52 [45.76, 59.42]; n=48 | 18.94 [9.34, 29.85]; n=31 |
| 003 | 32.48 [16.85, 48.10]; n=32 | 77.62 [64.66, 89.18]; n=41 | 65.38 [59.86, 70.79]; n=14 | 13.34 [4.89, 22.92]; n=17 |
| 004 | 27.35 [15.62, 40.40]; n=44 | 68.85 [59.51, 77.23]; n=52 | 53.27 [46.42, 60.17]; n=48 | 15.53 [6.03, 26.98]; n=27 |
| 089 | 29.34 [17.97, 41.34]; n=50 | 68.57 [60.37, 76.18]; n=63 | 52.87 [45.92, 59.90]; n=53 | 18.42 [9.29, 28.60]; n=28 |
| 001 | 28.58 [16.73, 40.87]; n=49 | 66.65 [57.92, 74.61]; n=61 | 52.40 [44.12, 60.15]; n=52 | 15.50 [5.91, 26.87]; n=31 |
| 127 | 30.65 [18.49, 43.07]; n=47 | 72.34 [64.67, 79.35]; n=61 | 54.67 [47.55, 61.44]; n=52 | 16.31 [6.52, 28.01]; n=31 |
| 262 | — | — | — | — |
| 224 | — | — | — | — |
| 026 | — | — | — | — |

## Matched differences from persona-off: benchmark

**Positive = persona exceeds off on exactly the same evaluable tasks.** Each persona has its own matched subset, so rows can still differ in task coverage. ASI is omitted for all rows because of the evaluator change. The baseline is the existing Trial 1 persona-off run; no baseline episodes were duplicated.

| Persona | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|
| 148 | -2.50 [-7.50, 0.00]; n=40 | +3.32 [-5.85, 14.05]; n=36 | -1.30 [-3.93, 1.28]; n=40 | +2.50 [-5.00, 12.50]; n=40 |
| 155 | +0.00 [0.00, 0.00]; n=40 | +1.96 [-6.75, 11.08]; n=37 | -0.30 [-2.62, 2.05]; n=40 | +2.50 [-7.50, 12.50]; n=40 |
| 046 | +0.00 [0.00, 0.00]; n=37 | +6.90 [-1.59, 15.73]; n=36 | -0.48 [-3.70, 3.09]; n=39 | -7.50 [-20.00, 5.00]; n=40 |
| 003 | +0.00 [0.00, 0.00]; n=28 | +2.80 [-9.03, 13.62]; n=22 | -6.89 [-13.11, -0.67]; n=6 | -2.50 [-15.00, 10.00]; n=40 |
| 004 | -2.63 [-7.89, 0.00]; n=38 | +3.58 [-5.40, 13.47]; n=31 | +1.73 [-0.97, 4.41]; n=38 | +2.50 [-5.00, 10.00]; n=40 |
| 089 | +0.00 [0.00, 0.00]; n=40 | +4.04 [-4.15, 13.05]; n=36 | +1.49 [-1.47, 4.42]; n=40 | +5.00 [0.00, 12.50]; n=40 |
| 001 | +0.00 [0.00, 0.00]; n=40 | +3.93 [-3.81, 13.10]; n=38 | -0.84 [-3.42, 1.73]; n=37 | +0.00 [-10.00, 10.00]; n=40 |
| 127 | +0.00 [0.00, 0.00]; n=39 | +4.44 [-4.78, 14.75]; n=37 | -0.12 [-3.15, 2.83]; n=40 | +7.50 [-2.50, 17.50]; n=40 |
| 262 | — | — | — | — |
| 224 | — | — | — | — |
| 026 | — | — | — | — |

## Matched differences from persona-off: super-family

**ASI excluded for all personas in this table.** These composites therefore target different source mixtures than the raw super-family table. All source counts and study-cluster counts are retained in the machine-readable summary.

| Persona | Life sciences | Physical sciences & engineering | Math & CS | Social sciences & humanities |
|---|---|---|---|---|
| 148 | -3.10 [-8.53, 0.00]; n=43 | +0.62 [-6.82, 8.03]; n=40 | +2.87 [-2.54, 9.36]; n=43 | +1.76 [-7.12, 12.27]; n=30 |
| 155 | -0.25 [-0.74, 0.00]; n=45 | +0.51 [-9.49, 10.51]; n=40 | +1.57 [-2.21, 6.78]; n=43 | +2.88 [-8.23, 14.39]; n=29 |
| 046 | +0.17 [0.00, 0.50]; n=40 | -9.05 [-21.43, 1.33]; n=40 | +2.22 [-2.75, 8.17]; n=42 | +6.39 [-3.33, 16.86]; n=30 |
| 003 | -0.04 [-1.29, 1.16]; n=31 | -5.88 [-20.59, 8.82]; n=34 | +7.76 [-4.00, 23.38]; n=14 | +0.76 [-12.95, 13.07]; n=17 |
| 004 | -2.36 [-7.64, 0.49]; n=41 | +0.35 [-7.21, 8.00]; n=39 | +3.71 [-0.50, 9.23]; n=41 | +4.14 [-6.46, 15.75]; n=26 |
| 089 | +0.00 [0.00, 0.00]; n=45 | +2.86 [-0.08, 8.17]; n=40 | +3.38 [-0.93, 8.84]; n=43 | +5.20 [-5.28, 16.55]; n=28 |
| 001 | -0.25 [-0.74, 0.00]; n=45 | +0.17 [-9.85, 10.20]; n=40 | +0.30 [-2.58, 3.30]; n=40 | +3.68 [-5.54, 14.83]; n=30 |
| 127 | -0.26 [-0.78, 0.00]; n=43 | +5.75 [-3.88, 15.86]; n=40 | +2.68 [-2.01, 8.36]; n=43 | +4.18 [-6.63, 16.28]; n=30 |
| 262 | — | — | — | — |
| 224 | — | — | — | — |
| 026 | — | — | — | — |

## Common-panel sensitivity analysis

The same **86 non-ASI tasks** are evaluable across every available condition (off plus eight personas). This sacrifices coverage and may select easier tasks, but prevents each row from using a different task subset. Source counts: BixBench 26, DiscoveryBench 15, EXP-Bench 5, SciConvBench 40.

| Persona | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|
| Off | 38.46 [19.23, 57.69]; n=26 | 15.24 [3.33, 30.48]; n=15 | 51.33 [42.80, 62.13]; n=5 | 85.00 [72.50, 95.00]; n=40 |
| 148 | 38.46 [19.23, 57.69]; n=26 | 20.48 [5.24, 39.05]; n=15 | 44.80 [35.00, 52.80]; n=5 | 87.50 [77.50, 97.50]; n=40 |
| 155 | 38.46 [19.23, 57.69]; n=26 | 17.28 [2.46, 36.35]; n=15 | 48.60 [35.00, 63.20]; n=5 | 87.50 [77.50, 97.50]; n=40 |
| 046 | 38.46 [19.23, 57.69]; n=26 | 26.94 [12.11, 43.70]; n=15 | 45.73 [36.20, 54.67]; n=5 | 77.50 [65.00, 90.00]; n=40 |
| 003 | 38.46 [19.23, 57.69]; n=26 | 18.31 [8.31, 29.51]; n=15 | 43.87 [35.00, 50.93]; n=5 | 82.50 [70.00, 92.50]; n=40 |
| 004 | 38.46 [19.23, 57.69]; n=26 | 16.97 [5.33, 32.40]; n=15 | 48.60 [36.20, 63.20]; n=5 | 87.50 [77.50, 97.50]; n=40 |
| 089 | 38.46 [19.23, 57.69]; n=26 | 21.90 [7.46, 38.57]; n=15 | 47.60 [35.00, 60.20]; n=5 | 90.00 [80.00, 97.50]; n=40 |
| 001 | 38.46 [19.23, 57.69]; n=26 | 22.72 [7.11, 41.29]; n=15 | 47.60 [36.20, 60.20]; n=5 | 85.00 [72.50, 95.00]; n=40 |
| 127 | 38.46 [19.23, 57.69]; n=26 | 25.29 [9.52, 43.44]; n=15 | 48.60 [36.79, 63.20]; n=5 | 92.50 [82.50, 100.00]; n=40 |

## Observations from this snapshot

- **SciConvBench:** persona 127 has 92.50, versus off at 85.00; its matched difference is +7.50 [-2.50, 17.50]; n=40. Persona 089 has 90.00; persona 046 has 77.50. These are specification-resolution outcomes, not solver success rates.
- **BixBench:** most personas have exactly zero matched difference from off in this snapshot. Apparent differences in raw means can come from different surviving task subsets; the common-panel means are identical across all available conditions.
- **DiscoveryBench:** persona 046 has a matched improvement of +6.90 [-1.59, 15.73]; n=36. Its interval includes zero. The other personas also have positive point estimates in this snapshot; these are exploratory signals.
- **EXP-Bench:** persona 003 has only 6 evaluable tasks. Its negative paired interval should not be promoted to a reliable persona effect given severe missingness, few tasks, shared-study dependence, and multiple comparisons.
- **Super-family composition:** persona 003’s raw Math & CS mean is 65.38 on 14 tasks, compared with off at 49.71 on 54 tasks. That is not an apples-to-apples advantage. On matched non-ASI Math & CS tasks its difference is +7.76 [-4.00, 23.38]; n=14.

## Interpretation and next steps

1. Use the matched-difference tables to inspect possible persona effects; available-case means alone confound performance and which tasks survived technical failures.
2. Repair rate-limit failures and regrade sealed submissions after documenting evaluator settings. ASI comparisons need a common judge configuration before being used as evidence of persona effects.
3. Finish the prioritized independent repeats for 089/001/127 and aggregate at the task/condition level; account for shared-study dependence in the eventual paper analysis.
4. Keep unrun personas visibly absent. Do not select a winning persona or claim a significant improvement from this single, incomplete trial.

## Provenance and reproduction

[Normalized episode snapshot](data/trial_1_all_personas/snapshot.json) records original statuses, task IDs, scores, evaluator versions, and source-file hashes. [Summary](data/trial_1_all_personas/summary.json) stores all CIs, denominators, and source compositions. [Episode CSV](data/trial_1_all_personas/episodes.csv) supports independent inspection.

The input snapshot is taken once; a live run may advance while it is read. Final-result files are used when available, otherwise per-episode state files are snapshotted. Historical failed attempts are not counted as extra trials. Original baseline results include three episodes retained from the initial cancelled first-pass job, as in the existing Trial 1 analysis.

Rebuild exactly from the saved snapshot (no API calls):

```bash
.venv/bin/python Experiment/02_performance_and_fields/code/report_all_trial1.py \
  --snapshot Experiment/02_performance_and_fields/data/trial_1_all_personas/snapshot.json
```
