# All available Astra personas and trials

**8 personas plus persona-off**, from completed trial jobs, including single-trial personas. All saved results from their completed Astra-low trial jobs on the frozen 200-task panel are eligible; no three-trial requirement. The cancelled initial run is excluded entirely. Sol and the redesigned SciConv campaign are different model/protocol settings and are not pooled.

## Available evidence

| Persona | Trial IDs with scores | Evaluable episodes | Distinct tasks | Scored | Missing submission (zero) | Recorded unscored | Unrecorded slots in started trials |
|---|---|---|---|---|---|---|---|
| 001 | 1,2,3 | 595 | 200 | 578 | 17 | 5 | 0 |
| 003 | 1 | 123 | 123 | 114 | 9 | 77 | 0 |
| 004 | 1 | 177 | 177 | 168 | 9 | 23 | 0 |
| 026 | none | 0 | 0 | 0 | 0 | 0 | 0 |
| 046 | 1 | 185 | 185 | 175 | 10 | 15 | 0 |
| 089 | 1,2,3 | 597 | 200 | 577 | 20 | 3 | 0 |
| 127 | 1,2,3 | 592 | 200 | 576 | 16 | 8 | 0 |
| 148 | 1,2,3 | 572 | 200 | 553 | 19 | 28 | 0 |
| 155 | 1,2,3 | 556 | 199 | 526 | 30 | 44 | 0 |
| 224 | none | 0 | 0 | 0 | 0 | 0 | 0 |
| 262 | none | 0 | 0 | 0 | 0 | 0 | 0 |
| Off | 1,2,3 | 576 | 199 | 549 | 27 | 24 | 0 |

No-result personas remain in the coverage table, without fabricated zero scores. Three selected personas (262/224/026) never completed a trial. Personas 228 and 137 from the cancelled initial job are excluded, as requested. A completed trial job can still contain technical failures; those do not become zero scientific scores.

## Aggregation and uncertainty

Use the latest evaluable endpoint within each task/persona/trial slot. A failed repair falls back to an evaluable original outcome; a scored repair replaces its original regardless of whether its score is higher or lower. Repairs are not extra trials; no partial cancelled-job records are added. Original-only results are retained as a sensitivity. Scientific missing submissions are zero; infrastructure/unscored slots are missing.

First average available trial scores within task, then give tasks equal weight. Pointwise 95% CIs use 20,000 study-cluster bootstrap draws within benchmark, with observed source proportions fixed. CIs condition on available trials; one-trial rows do not estimate run-to-run variation. Fewer than two studies yields an unavailable CI. Singleton source-by-family strata contribute no bootstrap variation. Incomplete tasks, conditional repair selection, unequal trial counts and outcome-selected personas limit comparisons.

Absolute scores use all evaluable outcomes and are descriptive; historical ASI judge versions are mixed. Paired changes require the same task and trial, with corrected ASI judges on both sides and compatible evaluator versions elsewhere. Unavailable matched cells remain explicitly missing. Super-family averages mix native metrics and source composition; these are not pure field effects. No equivalence, multiplicity-adjusted significance or persona ranking is claimed.

## Available performance

![absolute heatmap](figures/all_available/absolute_performance.png)

### By benchmark

| Persona · available trials | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off · 3 | 47.86 [37.53, 58.55]; n=39, e=100 | 30.83 [8.13, 54.35]; n=40, e=119 | 13.14 [6.06, 16.73]; n=40, e=117 | 43.95 [36.66, 51.27]; n=40, e=120 | 85.00 [74.17, 94.17]; n=40, e=120 |
| 148 · 3 | 49.56 [38.97, 60.59]; n=40, e=100 | 30.00 [7.32, 53.85]; n=40, e=118 | 13.66 [9.36, 15.66]; n=40, e=114 | 44.04 [37.12, 51.08]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 · 3 | 52.57 [41.47, 63.55]; n=39, e=99 | 30.83 [8.13, 54.35]; n=40, e=119 | 15.27 [7.74, 21.74]; n=40, e=111 | 43.05 [35.83, 50.29]; n=40, e=107 | 85.00 [75.83, 92.50]; n=40, e=120 |
| 089 · 3 | 50.16 [39.84, 60.75]; n=40, e=118 | 30.83 [8.13, 54.35]; n=40, e=120 | 14.79 [7.96, 20.39]; n=40, e=119 | 45.68 [37.52, 53.93]; n=40, e=120 | 87.50 [77.50, 95.00]; n=40, e=120 |
| 001 · 3 | 51.85 [41.16, 62.85]; n=40, e=117 | 30.83 [8.13, 54.35]; n=40, e=120 | 14.50 [7.09, 22.86]; n=40, e=118 | 44.61 [37.23, 52.25]; n=40, e=120 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 · 3 | 51.30 [40.58, 62.33]; n=40, e=114 | 30.83 [8.13, 54.35]; n=40, e=119 | 14.00 [8.63, 20.09]; n=40, e=119 | 44.10 [36.64, 51.74]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |
| 003 · 1 | 50.62 [28.47, 73.48]; n=11, e=11 | 31.43 [6.90, 56.76]; n=35, e=35 | 17.82 [11.42, 24.04]; n=31, e=31 | 44.22 [37.22, 50.11]; n=6, e=6 | 82.50 [70.00, 92.50]; n=40, e=40 |
| 004 · 1 | 41.76 [30.13, 54.19]; n=27, e=27 | 28.95 [6.25, 53.85]; n=38, e=38 | 13.81 [3.12, 19.20]; n=33, e=33 | 46.28 [38.09, 54.42]; n=39, e=39 | 87.50 [77.50, 97.50]; n=40, e=40 |
| 046 · 1 | 54.08 [41.06, 67.16]; n=28, e=28 | 28.95 [6.25, 53.34]; n=38, e=38 | 17.36 [12.73, 22.17]; n=39, e=39 | 43.57 [35.96, 52.26]; n=40, e=40 | 77.50 [65.00, 90.00]; n=40, e=40 |

### By super-family

| Persona · available trials | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| Off · 3 | 27.61 [9.41, 46.54]; n=50, e=146 | 66.73 [58.70, 74.25]; n=62, e=175 | 50.67 [43.72, 57.35]; n=55, e=161 | 14.97 [8.33, 18.33]; n=32, e=94 |
| 148 · 3 | 26.69 [8.43, 45.81]; n=50, e=144 | 67.26 [59.57, 74.52]; n=63, e=176 | 52.36 [45.29, 59.04]; n=55, e=158 | 14.75 [12.16, 15.81]; n=32, e=94 |
| 155 · 3 | 28.12 [9.85, 47.09]; n=50, e=142 | 67.25 [59.68, 74.42]; n=62, e=175 | 52.21 [45.38, 58.65]; n=55, e=148 | 17.80 [12.10, 24.89]; n=32, e=91 |
| 089 · 3 | 27.68 [9.55, 46.60]; n=50, e=149 | 68.35 [60.63, 75.48]; n=63, e=189 | 53.41 [46.10, 60.52]; n=55, e=164 | 16.59 [10.81, 22.80]; n=32, e=95 |
| 001 · 3 | 27.24 [9.07, 46.10]; n=50, e=147 | 69.71 [62.31, 76.54]; n=63, e=188 | 54.15 [47.30, 60.71]; n=55, e=164 | 16.86 [9.98, 26.52]; n=32, e=96 |
| 127 · 3 | 27.70 [9.55, 46.58]; n=50, e=148 | 68.53 [60.94, 75.55]; n=63, e=186 | 54.54 [47.36, 61.30]; n=55, e=163 | 14.82 [9.63, 21.51]; n=32, e=95 |
| 003 · 1 | 28.23 [7.29, 49.68]; n=41, e=41 | 76.91 [64.40, 87.98]; n=42, e=42 | 57.29 [54.67, 59.50]; n=16, e=16 | 19.60 [13.47, 27.30]; n=24, e=24 |
| 004 · 1 | 27.35 [7.92, 48.71]; n=44, e=44 | 66.95 [58.08, 75.02]; n=56, e=56 | 53.40 [46.03, 60.59]; n=49, e=49 | 14.97 [2.01, 20.71]; n=28, e=28 |
| 046 · 1 | 27.02 [8.50, 47.30]; n=46, e=46 | 66.34 [55.83, 76.16]; n=56, e=56 | 50.76 [43.61, 58.19]; n=51, e=51 | 18.35 [13.00, 24.17]; n=32, e=32 |

## Matched changes from persona-off

![paired heatmap](figures/all_available/paired_performance.png)

### By benchmark

| Persona · available trials | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| 148 · 3 | +0.67 [-5.25, 6.32]; n=30, e=44 | -0.83 [-2.78, 0.00]; n=40, e=117 | +0.72 [-2.71, 6.53]; n=39, e=112 | +0.09 [-2.05, 1.93]; n=40, e=120 | +0.83 [-4.17, 6.67]; n=40, e=120 |
| 155 · 3 | +7.70 [0.30, 16.01]; n=32, e=44 | +0.00 [0.00, 0.00]; n=40, e=118 | +3.03 [-0.89, 8.13]; n=40, e=110 | -0.99 [-2.52, 0.41]; n=40, e=107 | +0.00 [-6.67, 7.50]; n=40, e=120 |
| 089 · 3 | +3.72 [0.59, 7.24]; n=34, e=58 | +0.00 [0.00, 0.00]; n=40, e=119 | +1.52 [-1.29, 5.62]; n=40, e=116 | +1.73 [-0.11, 3.50]; n=40, e=120 | +2.50 [-3.33, 8.33]; n=40, e=120 |
| 001 · 3 | +2.91 [-2.46, 7.53]; n=34, e=58 | +0.00 [0.00, 0.00]; n=40, e=119 | +1.21 [-4.32, 8.09]; n=40, e=115 | +0.66 [-1.39, 2.50]; n=40, e=120 | +5.00 [0.00, 10.83]; n=40, e=120 |
| 127 · 3 | +0.80 [-4.59, 6.13]; n=34, e=57 | +0.00 [0.00, 0.00]; n=40, e=119 | +0.53 [-3.28, 7.61]; n=40, e=116 | +0.15 [-1.73, 1.85]; n=40, e=120 | +4.17 [-2.50, 11.67]; n=40, e=120 |
| 003 · 1 | +24.78 [0.36, 49.20]; n=2, e=2 | +0.00 [0.00, 0.00]; n=35, e=35 | +5.01 [1.49, 9.09]; n=31, e=31 | -6.89 [-13.11, -0.67]; n=6, e=6 | -2.50 [-15.00, 10.00]; n=40, e=40 |
| 004 · 1 | +10.21 [1.94, 20.89]; n=4, e=4 | -2.63 [-8.82, 0.00]; n=38, e=38 | +3.36 [-4.66, 7.64]; n=33, e=33 | +1.68 [-1.57, 4.84]; n=39, e=39 | +2.50 [-5.00, 12.50]; n=40, e=40 |
| 046 · 1 | +19.61 [3.95, 35.26]; n=5, e=5 | -2.63 [-8.82, 0.00]; n=38, e=38 | +6.76 [2.43, 12.64]; n=39, e=39 | -0.47 [-4.08, 4.01]; n=40, e=40 | -7.50 [-20.00, 5.00]; n=40, e=40 |

### By super-family

| Persona · available trials | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| 148 · 3 | -0.86 [-2.49, -0.02]; n=48, e=136 | -0.21 [-4.42, 4.36]; n=58, e=146 | +2.06 [-0.23, 4.65]; n=51, e=138 | -0.00 [-2.95, 5.03]; n=32, e=93 |
| 155 · 3 | +0.64 [-0.20, 2.28]; n=49, e=136 | +1.15 [-4.45, 7.25]; n=59, e=147 | +2.11 [-0.28, 4.84]; n=52, e=126 | +3.72 [-0.83, 9.45]; n=32, e=90 |
| 089 · 3 | +0.21 [-0.38, 1.25]; n=50, e=142 | +2.35 [-1.50, 6.59]; n=60, e=155 | +3.05 [1.15, 5.14]; n=52, e=143 | +1.45 [-1.25, 4.71]; n=32, e=93 |
| 001 · 3 | -0.26 [-0.57, 0.19]; n=50, e=140 | +2.94 [-1.31, 7.43]; n=60, e=155 | +2.97 [0.86, 5.21]; n=52, e=143 | +1.77 [-4.64, 8.40]; n=32, e=94 |
| 127 · 3 | +0.05 [-0.29, 0.50]; n=50, e=142 | +1.10 [-3.61, 6.50]; n=60, e=155 | +3.28 [0.87, 6.04]; n=52, e=142 | -0.57 [-4.01, 3.58]; n=32, e=93 |
| 003 · 1 | -0.02 [-0.02, -0.02]; n=40, e=40 | -4.31 [-18.59, 9.98]; n=35, e=35 | +7.24 [-1.64, 21.56]; n=15, e=15 | +4.44 [2.08, 7.57]; n=24, e=24 |
| 004 · 1 | -2.23 [-7.83, 0.15]; n=42, e=42 | +1.01 [-6.19, 8.28]; n=41, e=41 | +3.77 [-0.70, 9.22]; n=43, e=43 | +3.85 [-6.33, 8.55]; n=28, e=28 |
| 046 · 1 | -1.40 [-6.81, 1.54]; n=44, e=44 | -7.49 [-19.08, 3.25]; n=42, e=42 | +2.56 [-1.95, 8.43]; n=44, e=44 | +6.46 [1.43, 12.50]; n=32, e=32 |

## Original-only sensitivity

| Persona | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 47.55 [37.08, 58.33]; n=38, e=93 | 30.83 [8.13, 54.35]; n=40, e=117 | 13.33 [6.06, 17.14]; n=40, e=115 | 43.95 [36.66, 51.27]; n=40, e=120 | 85.00 [74.17, 94.17]; n=40, e=120 |
| 148 | 49.92 [38.80, 61.26]; n=38, e=91 | 30.00 [7.32, 53.85]; n=40, e=117 | 13.74 [9.66, 15.66]; n=40, e=111 | 44.04 [37.12, 51.08]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 | 52.69 [41.52, 63.72]; n=39, e=96 | 30.83 [8.13, 54.35]; n=40, e=117 | 15.38 [7.74, 21.74]; n=40, e=107 | 43.15 [35.93, 50.38]; n=40, e=105 | 85.00 [75.83, 92.50]; n=40, e=120 |
| 089 | 50.39 [40.15, 60.98]; n=40, e=109 | 31.25 [8.57, 54.76]; n=40, e=117 | 14.72 [7.96, 20.30]; n=40, e=108 | 45.68 [37.52, 53.93]; n=40, e=119 | 87.50 [77.50, 95.00]; n=40, e=119 |
| 001 | 51.61 [40.92, 62.61]; n=40, e=109 | 30.83 [8.13, 54.35]; n=40, e=119 | 14.72 [7.27, 22.86]; n=40, e=115 | 44.45 [37.04, 52.09]; n=40, e=105 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 | 49.68 [38.62, 60.92]; n=38, e=104 | 30.83 [8.13, 54.35]; n=40, e=116 | 13.98 [8.63, 20.03]; n=40, e=113 | 44.10 [36.64, 51.74]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |
| 003 | 61.22 [33.94, 86.92]; n=8, e=8 | 35.71 [9.09, 61.36]; n=28, e=28 | 14.04 [9.14, 20.11]; n=22, e=22 | 44.22 [37.22, 50.11]; n=6, e=6 | 82.50 [70.00, 92.50]; n=40, e=40 |
| 004 | 41.69 [28.73, 55.54]; n=23, e=23 | 28.95 [6.25, 53.85]; n=38, e=38 | 14.25 [3.12, 20.07]; n=32, e=32 | 45.92 [37.32, 54.32]; n=38, e=38 | 87.50 [77.50, 97.50]; n=40, e=40 |
| 046 | 57.73 [42.60, 72.59]; n=23, e=23 | 29.73 [6.67, 54.55]; n=37, e=37 | 18.30 [13.89, 22.77]; n=37, e=37 | 44.68 [37.04, 53.44]; n=39, e=39 | 77.50 [65.00, 90.00]; n=40, e=40 |

| Persona | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| Off | 27.67 [9.47, 46.60]; n=50, e=141 | 66.72 [58.64, 74.17]; n=61, e=172 | 50.76 [43.81, 57.43]; n=55, e=159 | 15.21 [8.33, 18.86]; n=32, e=93 |
| 148 | 26.91 [8.62, 46.01]; n=50, e=139 | 67.94 [59.90, 75.40]; n=61, e=170 | 52.36 [45.29, 59.04]; n=55, e=158 | 14.75 [12.16, 15.81]; n=32, e=92 |
| 155 | 28.10 [9.82, 47.08]; n=50, e=139 | 67.37 [59.79, 74.60]; n=62, e=172 | 52.24 [45.41, 58.70]; n=55, e=147 | 17.94 [12.34, 24.89]; n=32, e=87 |
| 089 | 28.01 [9.88, 46.90]; n=50, e=142 | 68.50 [60.78, 75.56]; n=63, e=184 | 53.41 [46.10, 60.52]; n=55, e=160 | 16.50 [10.81, 22.70]; n=32, e=86 |
| 001 | 27.17 [8.98, 46.04]; n=50, e=145 | 69.62 [62.21, 76.44]; n=63, e=182 | 54.03 [47.19, 60.61]; n=55, e=148 | 17.14 [10.53, 26.52]; n=32, e=93 |
| 127 | 27.68 [9.54, 46.58]; n=50, e=142 | 68.56 [60.98, 75.56]; n=63, e=183 | 53.48 [46.21, 60.46]; n=53, e=157 | 14.80 [9.63, 21.44]; n=32, e=91 |
| 003 | 32.48 [9.18, 54.92]; n=32, e=32 | 77.62 [64.96, 89.05]; n=41, e=41 | 65.38 [62.38, 67.90]; n=14, e=14 | 13.34 [7.26, 19.79]; n=17, e=17 |
| 004 | 27.35 [7.92, 48.71]; n=44, e=44 | 68.85 [59.49, 77.28]; n=52, e=52 | 53.27 [45.55, 60.62]; n=48, e=48 | 15.53 [2.01, 21.22]; n=27, e=27 |
| 046 | 27.79 [7.89, 49.10]; n=43, e=43 | 67.49 [56.75, 77.37]; n=54, e=54 | 52.52 [45.16, 60.22]; n=48, e=48 | 18.94 [13.32, 24.17]; n=31, e=31 |

## Reproduction

[Executed notebook](performance_analysis.ipynb) · [Frozen episode snapshot](data/all_available/snapshot.json) · [Summary and CI source data](data/all_available/summary.csv) · [Paired episodes](data/all_available/paired_episodes.csv)

The previous six-setting report and heatmap remain as historical analyses. The forest-plot alternative has been removed at the user’s request. Rerun `code/analyze_all_available.py` to use the saved snapshot, or add `--refresh` to re-read the saved run files. No new model calls.
