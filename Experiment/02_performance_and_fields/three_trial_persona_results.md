# Astra three-trial persona results

[Executed Jupyter notebook: data, CIs, tables and plot code](three_trial_persona_analysis.ipynb)

Six settings: Off, 148, 155, 089, 001, and 127. All use GPT-6 Astra low for actor, researcher simulator, and judge. Each setting planned 200 tasks × 3 trials = 600 episodes. Personas 046/003/004 have only one trial and are excluded; Sol is a separate model comparison.

## Aggregation and confidence intervals

Task means average available scores across trials 1–3, then weight each task equally. Missing submissions count as zero; infrastructure and other unscored episodes are excluded. Pointwise 95% percentile CIs use 20,000 study-cluster bootstrap resamples, stratified by benchmark source (seed 20260930), with observed source weights fixed. Trials are not counted as independent tasks. Intervals describe study/task sampling uncertainty conditional on observed trial outcomes; they do not separately estimate trial-to-trial uncertainty or correct for multiple comparisons. Unequal surviving task coverage can bias comparisons.

Main figures and tables use the latest outcome after the single repair pass, including reused original successes. A repair is a conditional replacement attempt, not a fourth trial or an independent replicate. Original outcomes remain in the sensitivity tables below. Results are provisional: repair selection and technical missingness can bias means. ASI evaluator versions/configuration differ between historical runs and repairs; ASI bars and family composites are descriptive, not clean estimates of persona effects. CI overlap is not a significance test.

Native metrics: ASI score/max × 100; Bix correctness × 100; Discovery final score × 100; EXP final gated coverage (initial fallback); SciConv final resolution with intent preserved × 100. Super-family averages combine these distinct metrics and are not a calibrated common measure.

Each cell: **mean [95% CI]; n=distinct evaluable tasks, e=evaluable trial episodes**. Each task averages its one to three available trial scores before aggregation. Study clusters use source-qualified study IDs; singleton studies remain singleton clusters. Intervals with few independent studies can be unstable.

## Table 1 — By benchmark

| Persona | ASI-Bench* | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 48.16 [37.76, 58.87]; n=39, e=99 | 32.46 [8.89, 56.10]; n=38, e=104 | 13.14 [6.06, 16.73]; n=40, e=117 | 43.95 [36.55, 51.20]; n=40, e=120 | 85.00 [75.00, 94.17]; n=40, e=120 |
| 148 | 49.56 [38.74, 60.29]; n=40, e=100 | 30.00 [7.32, 54.00]; n=40, e=111 | 13.66 [9.31, 15.66]; n=40, e=114 | 44.04 [36.94, 51.05]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 | 53.67 [42.51, 64.59]; n=39, e=98 | 30.83 [8.33, 54.55]; n=40, e=103 | 15.27 [7.74, 21.77]; n=40, e=110 | 43.05 [35.78, 50.35]; n=40, e=107 | 85.00 [75.83, 93.33]; n=40, e=120 |
| 089 | 50.16 [39.86, 60.46]; n=40, e=118 | 30.83 [8.11, 54.55]; n=40, e=118 | 14.79 [7.96, 20.39]; n=40, e=119 | 45.68 [37.34, 53.99]; n=40, e=120 | 87.50 [78.33, 95.83]; n=40, e=120 |
| 001 | 51.85 [41.21, 62.74]; n=40, e=117 | 30.83 [7.89, 54.17]; n=40, e=119 | 14.50 [7.09, 22.80]; n=40, e=118 | 44.61 [37.16, 52.27]; n=40, e=120 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 | 51.30 [40.50, 62.20]; n=40, e=114 | 30.83 [8.33, 54.05]; n=40, e=118 | 14.00 [8.63, 20.05]; n=40, e=119 | 44.10 [36.41, 51.76]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |

![Benchmark bars with labeled confidence intervals](figures/three_trials/benchmark.png)

**Figure 1.** Performance by benchmark across three Astra trials after one conditional repair pass. Bar labels give mean and pointwise 95% study-cluster bootstrap CI. Error bars show the same CI; task and episode counts appear under each condition. Different surviving task subsets and historical ASI judge configurations prevent a clean ranking.

## Table 2 — By super-family

| Persona | Life sciences | Physical sciences & engineering | Math & computer science | Social sciences & humanities |
|---|---|---|---|---|
| Off | 28.76 [10.06, 47.38]; n=48, e=131 | 66.91 [58.86, 74.38]; n=62, e=174 | 50.67 [43.67, 57.20]; n=55, e=161 | 14.97 [8.33, 18.33]; n=32, e=94 |
| 148 | 26.69 [8.38, 46.01]; n=50, e=137 | 67.26 [59.37, 74.45]; n=63, e=176 | 52.36 [45.24, 59.05]; n=55, e=158 | 14.75 [12.16, 15.81]; n=32, e=94 |
| 155 | 28.12 [10.00, 47.10]; n=50, e=126 | 67.25 [59.63, 74.57]; n=62, e=175 | 52.99 [46.03, 59.39]; n=55, e=147 | 17.80 [12.10, 24.89]; n=32, e=90 |
| 089 | 27.68 [9.52, 46.80]; n=50, e=147 | 68.35 [60.81, 75.35]; n=63, e=189 | 53.41 [46.09, 60.51]; n=55, e=164 | 16.59 [10.81, 22.80]; n=32, e=95 |
| 001 | 27.24 [9.26, 46.49]; n=50, e=146 | 69.71 [62.27, 76.53]; n=63, e=188 | 54.15 [47.34, 60.60]; n=55, e=164 | 16.86 [9.98, 26.52]; n=32, e=96 |
| 127 | 27.70 [9.75, 46.71]; n=50, e=147 | 68.53 [60.96, 75.48]; n=63, e=186 | 54.54 [47.38, 61.32]; n=55, e=163 | 14.82 [9.63, 21.51]; n=32, e=95 |

![Super-family bars with labeled confidence intervals](figures/three_trials/superfamily.png)

**Figure 2.** Task-weighted normalized native performance by scientific super-family. Scores first average available trials per task, then average tasks. Bootstrap resampling preserves observed source weights; cross-source metrics remain distinct. Labels and whiskers show mean and pointwise 95% CI. ASI evaluator drift and unequal task coverage also affect these composites.

## Coverage after repair

| Persona | Scored | Missing submission (zero) | Infrastructure errors | Tasks with all 3 evaluable trials |
|---|---:|---:|---:|---:|
| Off | 549 | 11 | 40 | 170/200 |
| 148 | 553 | 12 | 35 | 169/200 |
| 155 | 526 | 12 | 62 | 147/200 |
| 089 | 577 | 18 | 5 | 195/200 |
| 001 | 578 | 16 | 6 | 194/200 |
| 127 | 576 | 15 | 9 | 191/200 |

## Original outcomes: sensitivity tables

These preserve the original outcomes before this repair pass and use the identical aggregation and bootstrap method. They are not pooled with repair attempts. Original trial resumption history remains part of the existing run provenance.

| Persona | ASI-Bench* | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 47.55 [37.10, 58.33]; n=38, e=93 | 30.83 [8.33, 54.39]; n=40, e=117 | 13.33 [6.06, 17.18]; n=40, e=115 | 43.95 [36.46, 51.19]; n=40, e=120 | 85.00 [74.98, 94.17]; n=40, e=120 |
| 148 | 49.92 [38.70, 61.09]; n=38, e=91 | 30.00 [7.32, 54.00]; n=40, e=117 | 13.74 [9.66, 15.66]; n=40, e=111 | 44.04 [37.07, 51.11]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 | 52.69 [41.67, 63.68]; n=39, e=96 | 30.83 [8.33, 54.49]; n=40, e=117 | 15.38 [7.74, 21.74]; n=40, e=107 | 43.15 [35.75, 50.37]; n=40, e=105 | 85.00 [75.83, 92.50]; n=40, e=120 |
| 089 | 50.39 [40.13, 60.90]; n=40, e=109 | 31.25 [8.57, 54.55]; n=40, e=117 | 14.72 [8.18, 20.19]; n=40, e=108 | 45.68 [37.48, 53.99]; n=40, e=119 | 87.50 [78.33, 95.83]; n=40, e=119 |
| 001 | 51.61 [40.86, 62.29]; n=40, e=109 | 30.83 [8.55, 54.67]; n=40, e=119 | 14.72 [7.27, 22.80]; n=40, e=115 | 44.45 [37.06, 52.13]; n=40, e=105 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 | 49.68 [38.65, 60.86]; n=38, e=104 | 30.83 [8.55, 54.07]; n=40, e=116 | 13.98 [8.63, 20.07]; n=40, e=113 | 44.10 [36.65, 51.84]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |

| Persona | Life sciences | Physical sciences & engineering | Math & computer science | Social sciences & humanities |
|---|---|---|---|---|
| Off | 27.67 [9.57, 46.66]; n=50, e=141 | 66.72 [58.58, 74.23]; n=61, e=172 | 50.76 [43.86, 57.33]; n=55, e=159 | 15.21 [8.33, 18.86]; n=32, e=93 |
| 148 | 26.91 [8.56, 46.05]; n=50, e=139 | 67.94 [59.81, 75.43]; n=61, e=170 | 52.36 [45.22, 59.10]; n=55, e=158 | 14.75 [12.16, 15.81]; n=32, e=92 |
| 155 | 28.10 [9.72, 47.19]; n=50, e=139 | 67.37 [59.69, 74.74]; n=62, e=172 | 52.24 [45.47, 58.74]; n=55, e=147 | 17.94 [12.34, 24.89]; n=32, e=87 |
| 089 | 28.01 [10.07, 46.95]; n=50, e=142 | 68.50 [60.77, 75.58]; n=63, e=184 | 53.41 [46.08, 60.43]; n=55, e=160 | 16.50 [10.81, 22.70]; n=32, e=86 |
| 001 | 27.17 [9.21, 45.81]; n=50, e=145 | 69.62 [62.32, 76.38]; n=63, e=182 | 54.03 [47.26, 60.62]; n=55, e=148 | 17.14 [10.53, 26.52]; n=32, e=93 |
| 127 | 27.68 [9.49, 46.73]; n=50, e=142 | 68.56 [61.01, 75.64]; n=63, e=183 | 53.48 [46.34, 60.44]; n=53, e=157 | 14.80 [9.63, 21.44]; n=32, e=91 |

## Files and reproduction

[Summary and all denominators](data/three_trials/summary.json) · [Episode CSV](data/three_trials/episodes.csv) · [Hashed input snapshot](data/three_trials/snapshot.json)

[Benchmark PDF](figures/three_trials/benchmark.pdf) · [Benchmark SVG](figures/three_trials/benchmark.svg) · [Super-family PDF](figures/three_trials/superfamily.pdf) · [Super-family SVG](figures/three_trials/superfamily.svg)

```bash
.venv/bin/python Experiment/02_performance_and_fields/code/report_three_trials.py
```
