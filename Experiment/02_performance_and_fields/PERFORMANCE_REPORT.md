# Experiment 02 — Consolidated performance and field analysis

[Executed notebook](performance_analysis.ipynb) · [Earlier descriptive report](three_trial_persona_results.md)

Six settings (off/148/155/089/001/127), 200 frozen tasks, three Astra trials. This report preserves the existing benchmark and super-family table structures, and adds same-task/same-trial contrasts, version filtering, completion, conditional scores, and coverage sensitivities. No new inference or regrading.

## Principal observations

- The 108 original/after-repair absolute-score means and task/episode denominators reproduce the earlier report. Intervals are recomputed with this analysis's fixed bootstrap seed; small Monte Carlo endpoint differences are expected.
- Most original benchmark-level paired intervals include zero. The tables retain all directions and magnitudes rather than selecting a winning persona. ASI bridge-only coverage is smaller than the descriptive ASI panel.
- The strict all-six-settings/all-three-trials panel contains 103 original tasks and 116 after-repair tasks. Original ASI has no task satisfying that full bridge-only panel. Results on incomplete pairwise panels should not be presented as a common-panel ranking.
- Several Bix paired intervals are exactly [0,0] because every observed matched difference is zero. This describes the observed panel; it is not an equivalence test or a guarantee about new tasks.
- Super-family patterns are descriptive mixtures of different benchmark metrics. Automatic field-overlap annotations document explicit profile/task relationships but do not establish an expertise-match mechanism.

## How to read the evidence

The first two tables retain latest-after-repair available-case means for continuity. They are descriptive: ASI mixes legacy and corrected evaluator configurations, and conditions have unequal surviving coverage. Original matched contrasts below are the primary persona comparisons. ASI contrasts require the configured-judge bridge on both episodes; all legacy/unknown ASI pairs are excluded. Other native evaluator versions must match except for missing submissions, whose scientific zero does not require grading.

Scientific missing submissions score zero. Infrastructure failures are missing, not zero. “Submitted” means a scored deliverable exists, including incorrect scored answers; for EXP the native initial-design fallback is retained. Conditional scores use only scored submissions. The submitted/planned fraction includes infrastructure failures in the planned denominator and therefore measures operational coverage, not isolated scientific ability.

Means average available trials within task, then tasks equally. Paired changes match task and trial before averaging within task. Pointwise 95% CIs use 20,000 source-stratified study-cluster bootstrap draws with observed source weights fixed. They condition on observed trials and do not separately quantify trial randomness. Different pairwise panels can differ in coverage; no winner or significance claim follows from CI overlap or individual intervals.

## Table 1 — By benchmark

| Persona | ASI-Bench* | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 48.16 [37.86, 58.74]; n=39, e=99 | 32.46 [8.82, 56.25]; n=38, e=104 | 13.14 [6.06, 16.73]; n=40, e=117 | 43.95 [36.66, 51.27]; n=40, e=120 | 85.00 [74.17, 94.17]; n=40, e=120 |
| 148 | 49.56 [38.97, 60.59]; n=40, e=100 | 30.00 [7.32, 53.85]; n=40, e=111 | 13.66 [9.36, 15.66]; n=40, e=114 | 44.04 [37.12, 51.08]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 | 53.67 [42.44, 64.68]; n=39, e=98 | 30.83 [8.13, 54.35]; n=40, e=103 | 15.27 [7.74, 21.74]; n=40, e=110 | 43.05 [35.83, 50.29]; n=40, e=107 | 85.00 [75.83, 92.50]; n=40, e=120 |
| 089 | 50.16 [39.84, 60.75]; n=40, e=118 | 30.83 [8.13, 54.35]; n=40, e=118 | 14.79 [7.96, 20.39]; n=40, e=119 | 45.68 [37.52, 53.93]; n=40, e=120 | 87.50 [77.50, 95.00]; n=40, e=120 |
| 001 | 51.85 [41.16, 62.85]; n=40, e=117 | 30.83 [8.13, 54.35]; n=40, e=119 | 14.50 [7.09, 22.86]; n=40, e=118 | 44.61 [37.23, 52.25]; n=40, e=120 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 | 51.30 [40.58, 62.33]; n=40, e=114 | 30.83 [8.13, 54.35]; n=40, e=118 | 14.00 [8.63, 20.09]; n=40, e=119 | 44.10 [36.64, 51.74]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |

## Table 2 — By super-family

| Persona | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| Off | 28.76 [9.95, 47.61]; n=48, e=131 | 66.91 [58.93, 74.38]; n=62, e=174 | 50.67 [43.72, 57.35]; n=55, e=161 | 14.97 [8.33, 18.33]; n=32, e=94 |
| 148 | 26.69 [8.43, 45.81]; n=50, e=137 | 67.26 [59.57, 74.52]; n=63, e=176 | 52.36 [45.29, 59.04]; n=55, e=158 | 14.75 [12.16, 15.81]; n=32, e=94 |
| 155 | 28.12 [9.85, 47.09]; n=50, e=126 | 67.25 [59.68, 74.42]; n=62, e=175 | 52.99 [46.13, 59.38]; n=55, e=147 | 17.80 [12.10, 24.89]; n=32, e=90 |
| 089 | 27.68 [9.55, 46.60]; n=50, e=147 | 68.35 [60.63, 75.48]; n=63, e=189 | 53.41 [46.10, 60.52]; n=55, e=164 | 16.59 [10.81, 22.80]; n=32, e=95 |
| 001 | 27.24 [9.07, 46.10]; n=50, e=146 | 69.71 [62.31, 76.54]; n=63, e=188 | 54.15 [47.30, 60.71]; n=55, e=164 | 16.86 [9.98, 26.52]; n=32, e=96 |
| 127 | 27.70 [9.55, 46.58]; n=50, e=147 | 68.53 [60.94, 75.55]; n=63, e=186 | 54.54 [47.36, 61.30]; n=55, e=163 | 14.82 [9.63, 21.51]; n=32, e=95 |

*ASI absolute means remain mixed-version descriptive values. Super-families combine distinct native metrics and their source composition, rather than measuring a pure field effect. The existing annotated [benchmark bars](figures/three_trials/benchmark.png) and [super-family bars](figures/three_trials/superfamily.png) remain unchanged.

Sparse-stratum limitation: some source-by-family cells contain only one study. Resampling that study cannot estimate its between-study uncertainty, so the combined interval holds that component fixed and can be very narrow or degenerate. These intervals are conditional descriptive ranges, not evidence of precise population field effects. Study counts by source are recorded in the numeric summary. A source-only result with one study has no estimable study-level CI; the complete-panel table marks it unavailable.

## Task- and trial-matched original contrasts

![Matched performance changes](figures/consolidated/matched_performance.png)

The original six-setting Figure 4 heatmap is preserved. The expanded [all-available-persona report](ALL_AVAILABLE_PERFORMANCE.md) and performance notebook now include every persona with at least one completed trial job.

### Original

| Persona Δ vs off | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| 148 | +2.10 [-3.17, 7.60]; n=28, e=37 | -0.83 [-2.78, 0.00]; n=40, e=114 | +1.51 [-3.62, 12.63]; n=39, e=107 | +0.09 [-2.05, 1.93]; n=40, e=120 | +0.83 [-4.17, 6.67]; n=40, e=120 |
| 155 | +8.19 [0.74, 16.66]; n=31, e=41 | +0.00 [0.00, 0.00]; n=40, e=115 | +3.08 [-0.81, 8.13]; n=40, e=105 | -0.96 [-2.46, 0.41]; n=40, e=105 | +0.00 [-6.67, 7.50]; n=40, e=120 |
| 089 | +2.70 [-0.63, 6.52]; n=29, e=46 | +0.00 [0.00, 0.00]; n=40, e=114 | +1.51 [-1.11, 5.86]; n=40, e=104 | +1.73 [-0.11, 3.50]; n=40, e=119 | +2.50 [-3.33, 8.33]; n=40, e=119 |
| 001 | +2.53 [-2.47, 6.83]; n=30, e=46 | +0.00 [0.00, 0.00]; n=40, e=116 | +0.95 [-4.25, 7.23]; n=40, e=110 | +0.32 [-2.02, 2.39]; n=40, e=105 | +5.00 [0.00, 10.83]; n=40, e=120 |
| 127 | -1.51 [-8.02, 3.70]; n=29, e=46 | +0.00 [0.00, 0.00]; n=40, e=114 | +0.58 [-3.28, 7.59]; n=39, e=108 | +0.15 [-1.73, 1.85]; n=40, e=120 | +4.17 [-2.50, 11.67]; n=40, e=120 |

| Persona Δ vs off | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| 148 | -0.88 [-2.54, -0.04]; n=47, e=128 | +0.45 [-3.54, 4.83]; n=57, e=143 | +3.04 [0.75, 5.63]; n=51, e=137 | -0.56 [-4.74, 5.03]; n=32, e=90 |
| 155 | +0.63 [-0.22, 2.27]; n=49, e=131 | +1.37 [-4.28, 7.51]; n=58, e=145 | +2.07 [-0.33, 4.81]; n=52, e=124 | +3.78 [-0.72, 9.45]; n=32, e=86 |
| 089 | -0.29 [-0.38, -0.21]; n=48, e=130 | +2.10 [-1.91, 6.54]; n=58, e=150 | +3.18 [1.24, 5.29]; n=51, e=138 | +1.18 [-1.05, 3.64]; n=32, e=84 |
| 001 | -0.60 [-1.15, -0.20]; n=50, e=133 | +3.50 [-0.59, 7.99]; n=57, e=149 | +2.01 [-0.18, 4.17]; n=51, e=125 | +1.72 [-4.26, 7.71]; n=32, e=90 |
| 127 | -0.03 [-0.29, 0.26]; n=50, e=132 | +0.94 [-4.18, 6.62]; n=58, e=151 | +2.27 [0.26, 4.50]; n=49, e=137 | -0.41 [-4.01, 4.57]; n=31, e=88 |

### After Repair

| Persona Δ vs off | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| 148 | +0.67 [-5.25, 6.32]; n=30, e=44 | -0.88 [-2.94, 0.00]; n=38, e=98 | +0.72 [-2.71, 6.53]; n=39, e=112 | +0.09 [-2.05, 1.93]; n=40, e=120 | +0.83 [-4.17, 6.67]; n=40, e=120 |
| 155 | +7.70 [0.30, 16.01]; n=32, e=44 | +0.00 [0.00, 0.00]; n=38, e=94 | +2.95 [-1.03, 8.13]; n=40, e=109 | -0.99 [-2.52, 0.41]; n=40, e=107 | +0.00 [-6.67, 7.50]; n=40, e=120 |
| 089 | +3.72 [0.59, 7.24]; n=34, e=58 | +0.00 [0.00, 0.00]; n=38, e=103 | +1.52 [-1.29, 5.62]; n=40, e=116 | +1.73 [-0.11, 3.50]; n=40, e=120 | +2.50 [-3.33, 8.33]; n=40, e=120 |
| 001 | +2.91 [-2.46, 7.53]; n=34, e=58 | +0.00 [0.00, 0.00]; n=38, e=103 | +1.21 [-4.32, 8.09]; n=40, e=115 | +0.66 [-1.39, 2.50]; n=40, e=120 | +5.00 [0.00, 10.83]; n=40, e=120 |
| 127 | +0.80 [-4.59, 6.13]; n=34, e=57 | +0.00 [0.00, 0.00]; n=38, e=104 | +0.53 [-3.28, 7.61]; n=40, e=116 | +0.15 [-1.73, 1.85]; n=40, e=120 | +4.17 [-2.50, 11.67]; n=40, e=120 |

| Persona Δ vs off | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| 148 | -0.90 [-2.60, -0.02]; n=46, e=117 | -0.21 [-4.42, 4.36]; n=58, e=146 | +2.06 [-0.23, 4.65]; n=51, e=138 | -0.00 [-2.95, 5.03]; n=32, e=93 |
| 155 | +0.67 [-0.21, 2.38]; n=47, e=112 | +1.15 [-4.45, 7.25]; n=59, e=147 | +2.11 [-0.28, 4.84]; n=52, e=126 | +3.63 [-1.03, 9.45]; n=32, e=89 |
| 089 | +0.22 [-0.40, 1.30]; n=48, e=126 | +2.35 [-1.50, 6.59]; n=60, e=155 | +3.05 [1.15, 5.14]; n=52, e=143 | +1.45 [-1.25, 4.71]; n=32, e=93 |
| 001 | -0.27 [-0.60, 0.20]; n=48, e=124 | +2.94 [-1.31, 7.43]; n=60, e=155 | +2.97 [0.86, 5.21]; n=52, e=143 | +1.77 [-4.64, 8.40]; n=32, e=94 |
| 127 | +0.06 [-0.31, 0.52]; n=48, e=127 | +1.10 [-3.61, 6.50]; n=60, e=155 | +3.28 [0.87, 6.04]; n=52, e=142 | -0.57 [-4.01, 3.58]; n=32, e=93 |

## Coverage and conditional outcomes

### Original

| Persona | Scored / 600 | Missing submission | Infrastructure / other | Submitted / planned (%) |
|---|---|---|---|---|
| Off | 532 | 33 | 35 | 88.7 |
| 148 | 535 | 24 | 41 | 89.2 |
| 155 | 513 | 32 | 55 | 85.5 |
| 089 | 547 | 25 | 28 | 91.2 |
| 001 | 542 | 26 | 32 | 90.3 |
| 127 | 547 | 26 | 27 | 91.2 |

### After Repair

| Persona | Scored / 600 | Missing submission | Infrastructure / other | Submitted / planned (%) |
|---|---|---|---|---|
| Off | 549 | 11 | 40 | 91.5 |
| 148 | 553 | 12 | 35 | 92.2 |
| 155 | 526 | 12 | 62 | 87.7 |
| 089 | 577 | 18 | 5 | 96.2 |
| 001 | 578 | 16 | 6 | 96.3 |
| 127 | 576 | 15 | 9 | 96.0 |

### Submission among evaluable attempts (%) — original trials

| Persona | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 98.68 [96.05, 100.00]; n=38, e=93 | 73.33 [55.00, 88.24]; n=40, e=117 | 100.00 [100.00, 100.00]; n=40, e=115 | 100.00 [100.00, 100.00]; n=40, e=120 | 100.00 [100.00, 100.00]; n=40, e=120 |
| 148 | 100.00 [100.00, 100.00]; n=38, e=91 | 80.00 [64.96, 91.67]; n=40, e=117 | 100.00 [100.00, 100.00]; n=40, e=111 | 100.00 [100.00, 100.00]; n=40, e=120 | 100.00 [100.00, 100.00]; n=40, e=120 |
| 155 | 98.72 [96.15, 100.00]; n=39, e=96 | 75.00 [57.14, 89.33]; n=40, e=117 | 99.17 [98.25, 100.00]; n=40, e=107 | 100.00 [100.00, 100.00]; n=40, e=105 | 100.00 [100.00, 100.00]; n=40, e=120 |
| 089 | 100.00 [100.00, 100.00]; n=40, e=109 | 79.17 [60.95, 93.16]; n=40, e=117 | 100.00 [100.00, 100.00]; n=40, e=108 | 100.00 [100.00, 100.00]; n=40, e=119 | 100.00 [100.00, 100.00]; n=40, e=119 |
| 001 | 100.00 [100.00, 100.00]; n=40, e=109 | 78.33 [63.57, 90.38]; n=40, e=119 | 100.00 [100.00, 100.00]; n=40, e=115 | 100.00 [100.00, 100.00]; n=40, e=105 | 100.00 [100.00, 100.00]; n=40, e=120 |
| 127 | 100.00 [100.00, 100.00]; n=38, e=104 | 78.33 [60.36, 92.31]; n=40, e=116 | 100.00 [100.00, 100.00]; n=40, e=113 | 100.00 [100.00, 100.00]; n=40, e=120 | 100.00 [100.00, 100.00]; n=40, e=120 |

### Score conditional on submission — original trials

| Persona | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 47.85 [37.46, 58.55]; n=38, e=92 | 37.37 [10.81, 63.06]; n=33, e=85 | 13.33 [6.06, 17.14]; n=40, e=115 | 43.95 [36.66, 51.27]; n=40, e=120 | 85.00 [74.17, 94.17]; n=40, e=120 |
| 148 | 49.92 [38.80, 61.26]; n=38, e=91 | 32.43 [8.11, 57.50]; n=37, e=93 | 13.74 [9.66, 15.66]; n=40, e=111 | 44.04 [37.12, 51.08]; n=40, e=120 | 85.83 [75.83, 94.17]; n=40, e=120 |
| 155 | 53.78 [42.53, 64.87]; n=39, e=95 | 38.54 [11.11, 64.10]; n=32, e=87 | 15.38 [7.74, 21.74]; n=40, e=106 | 43.15 [35.93, 50.38]; n=40, e=105 | 85.00 [75.83, 92.50]; n=40, e=120 |
| 089 | 50.39 [40.15, 60.98]; n=40, e=109 | 36.76 [10.61, 61.63]; n=34, e=92 | 14.72 [7.96, 20.30]; n=40, e=108 | 45.68 [37.52, 53.93]; n=40, e=119 | 87.50 [77.50, 95.00]; n=40, e=119 |
| 001 | 51.61 [40.92, 62.61]; n=40, e=109 | 34.26 [9.26, 59.26]; n=36, e=93 | 14.72 [7.27, 22.86]; n=40, e=115 | 44.45 [37.04, 52.09]; n=40, e=105 | 90.00 [80.83, 97.50]; n=40, e=120 |
| 127 | 49.68 [38.62, 60.92]; n=38, e=104 | 36.27 [10.10, 61.24]; n=34, e=90 | 13.98 [8.63, 20.03]; n=40, e=113 | 44.10 [36.64, 51.74]; n=40, e=120 | 89.17 [80.00, 96.67]; n=40, e=120 |

## Observed run-to-run score variation

For each task with at least two evaluable trials, compute its sample standard deviation, then average those task SDs. CIs resample studies, not the two or three runs. ASI uses corrected-bridge episodes only. This separately describes observed run variation; it is not the uncertainty represented by the score-mean CIs. Tasks with only one valid run are excluded rather than assigned zero SD.

| Persona: mean within-task SD | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 9.47 [1.99, 18.72]; n=18 | 1.44 [0.00, 4.81]; n=40 | 8.40 [2.27, 16.17]; n=39 | 5.25 [3.81, 6.57]; n=40 | 7.22 [1.44, 12.99]; n=40 |
| 148 | 7.25 [1.91, 14.36]; n=15 | 0.00 [0.00, 0.00]; n=40 | 8.41 [5.10, 14.80]; n=39 | 5.48 [4.24, 6.73]; n=40 | 8.66 [2.89, 15.88]; n=40 |
| 155 | 3.15 [0.69, 6.59]; n=18 | 1.44 [0.00, 4.81]; n=40 | 9.20 [4.11, 15.86]; n=40 | 5.08 [3.60, 6.47]; n=40 | 12.99 [5.77, 20.21]; n=40 |
| 089 | 7.15 [3.49, 11.55]; n=39 | 1.77 [0.00, 5.89]; n=40 | 8.82 [4.97, 13.31]; n=40 | 4.95 [3.44, 6.47]; n=40 | 7.22 [1.44, 12.99]; n=40 |
| 001 | 5.17 [2.94, 7.88]; n=40 | 1.44 [0.00, 4.81]; n=40 | 9.83 [6.39, 12.78]; n=40 | 5.06 [3.34, 6.81]; n=37 | 5.77 [1.44, 11.55]; n=40 |
| 127 | 6.86 [3.48, 10.90]; n=36 | 1.44 [0.00, 4.81]; n=40 | 11.30 [6.96, 16.16]; n=40 | 4.28 [2.56, 6.08]; n=40 | 5.77 [1.44, 11.55]; n=40 |

## Shared complete-panel sensitivity

Require all six settings and all three trials to be evaluable, plus the same evaluator-version rule. This is stricter than pairwise matching and can remove difficult or failure-prone tasks. It is a sensitivity, not a replacement target population.

**original: 103 tasks**, source counts {'discoverybench': 19, 'bixbench': 29, 'expbench': 16, 'sciconvbench': 39}.

| Persona Δ vs off | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| 148 | — | +0.00 [0.00, 0.00]; n=29, e=87 | -0.37 [-4.37, 2.63]; n=19, e=57 | +0.66 [-4.04, 5.31]; n=16, e=48 | +0.85 [-4.27, 6.84]; n=39, e=117 |
| 155 | — | +0.00 [0.00, 0.00]; n=29, e=87 | +3.26 [-0.80, 7.30]; n=19, e=57 | -0.49 [-2.59, 1.51]; n=16, e=48 | +0.00 [-6.84, 7.69]; n=39, e=117 |
| 089 | — | +0.00 [0.00, 0.00]; n=29, e=87 | +4.29 [-0.90, 8.98]; n=19, e=57 | +2.93 [0.05, 5.75]; n=16, e=48 | +2.56 [-2.56, 8.55]; n=39, e=117 |
| 001 | — | +0.00 [0.00, 0.00]; n=29, e=87 | +8.02 [-0.60, 14.17]; n=19, e=57 | -0.02 [-3.44, 3.34]; n=16, e=48 | +5.13 [0.00, 11.11]; n=39, e=117 |
| 127 | — | +0.00 [0.00, 0.00]; n=29, e=87 | +3.05 [-0.58, 6.80]; n=19, e=57 | -0.37 [-3.77, 2.74]; n=16, e=48 | +4.27 [-2.56, 11.97]; n=39, e=117 |

**after_repair: 116 tasks**, source counts {'discoverybench': 26, 'bixbench': 22, 'expbench': 27, 'sciconvbench': 40, 'asibench': 1}.

| Persona Δ vs off | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| 148 | +1.23; CI unavailable; n=1, e=3 | -1.52 [-5.88, 0.00]; n=22, e=66 | +1.28 [-3.88, 4.74]; n=26, e=78 | -0.37 [-3.22, 2.09]; n=27, e=81 | +0.83 [-4.17, 6.67]; n=40, e=120 |
| 155 | +1.32; CI unavailable; n=1, e=3 | +0.00 [0.00, 0.00]; n=22, e=66 | +3.26 [1.51, 5.76]; n=26, e=78 | -1.28 [-2.73, 0.30]; n=27, e=81 | +0.00 [-6.67, 7.50]; n=40, e=120 |
| 089 | +2.71; CI unavailable; n=1, e=3 | +0.00 [0.00, 0.00]; n=22, e=66 | +2.52 [-2.02, 8.03]; n=26, e=78 | +1.31 [-0.63, 3.09]; n=27, e=81 | +2.50 [-3.33, 8.33]; n=40, e=120 |
| 001 | -0.27; CI unavailable; n=1, e=3 | +0.00 [0.00, 0.00]; n=22, e=66 | +4.61 [-3.36, 11.89]; n=26, e=78 | -0.42 [-2.62, 1.82]; n=27, e=81 | +5.00 [0.00, 10.83]; n=40, e=120 |
| 127 | +1.96; CI unavailable; n=1, e=3 | +0.00 [0.00, 0.00]; n=22, e=66 | +1.19 [-2.62, 6.08]; n=26, e=78 | -0.73 [-2.98, 1.20]; n=27, e=81 | +4.17 [-2.50, 11.67]; n=40, e=120 |

## Super-family sensitivity without ASI

| Persona Δ vs off | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| 148 | -1.28 [-3.05, -0.52]; n=44, e=124 | +1.33 [-3.67, 7.17]; n=40, e=120 | +1.94 [0.06, 3.56]; n=43, e=127 | -0.56 [-4.74, 5.03]; n=32, e=90 |
| 155 | -0.32 [-0.32, -0.32]; n=45, e=126 | -0.84 [-7.39, 6.23]; n=40, e=118 | +0.28 [-1.49, 2.22]; n=43, e=115 | +3.78 [-0.72, 9.45]; n=32, e=86 |
| 089 | -0.42 [-0.42, -0.42]; n=45, e=126 | +1.97 [-3.31, 7.97]; n=40, e=120 | +3.07 [1.04, 5.28]; n=43, e=126 | +1.18 [-1.05, 3.64]; n=32, e=84 |
| 001 | -0.75 [-0.75, -0.75]; n=45, e=128 | +4.20 [-0.53, 9.99]; n=40, e=119 | +1.43 [-0.96, 3.85]; n=43, e=114 | +1.72 [-4.26, 7.71]; n=32, e=90 |
| 127 | -0.43 [-0.43, -0.43]; n=45, e=126 | +3.86 [-2.18, 11.36]; n=40, e=120 | +1.71 [-0.29, 3.87]; n=43, e=128 | -0.41 [-4.01, 4.57]; n=31, e=88 |

## Documented field overlap and methods familiarity

An exploratory metadata audit maps each persona/task to direct, adjacent, outside, or unknown overlap. Direct requires an explicit specific-topic familiarity at Familiar/Proficient/Expert; adjacent includes broader-topic matches or Aware-level knowledge; outside means no overlap in the explicit familiarity list for a mapped specific topic; unknown covers unmapped/coarse metadata. These labels do not establish actual expertise, absence of knowledge, or a causal expertise-match effect. Broad or incomplete task labels limit this analysis. Statistics/coding/data-analysis skills are recorded separately and do not automatically convert a domain mismatch into a direct match.

[Persona methods/background audit](data/consolidated/persona_expertise.csv) · [All 1,000 task–persona relationships and evidence](data/consolidated/task_field_relationships.csv)

Source-specific effect summaries for each relationship category are included in the JSON and notebook. Do not pool them into an expertise benefit claim: persona selection, coarse metadata, source/field confounding and sparse study clusters remain. Neutral wording and isolated-trait controls were not run.

## Reproduction and scope

[Numeric summary](data/consolidated/summary.json) · [Matched episode differences](data/consolidated/matched_episode_differences.csv) · [Paired tables](data/consolidated/paired_summary.csv) · [Analysis contract](data/consolidated/analysis_contract.json)

Reproduce: `.venv/bin/python Experiment/02_performance_and_fields/code/consolidate_performance.py`; render with `code/plot_matched_performance.py`. The original frozen snapshot is hashed and unchanged. Single-trial 003/004/046 remain in their separate exploratory report. Sol, new-protocol SciConv and semantic trajectories are outside this report.
