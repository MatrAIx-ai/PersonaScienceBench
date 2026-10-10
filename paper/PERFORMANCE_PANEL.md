# Performance panel: table handoff

These are the **absolute performance values from Panel A of the current five-setting performance figure**. Use these values to create manuscript tables; no reanalysis is needed. The existing figures are preserved.

**Machine-readable data:** [performance_panel.csv](data/performance_panel.csv). It contains all 45 cells at full precision, 95% confidence limits, distinct question counts, evaluable episode counts, source-study counts, and actual trial IDs.

## Table-ready values

Values are **mean normalized native score [95% CI]**, on a 0–100 scale, rounded to two decimals. Persona off / 155 / 001 have up to three historical trials; 003 / 046 have one. The trial-1 trace release is a subset and must not replace the available-trial performance data below.

### By benchmark

| Group | Persona off | Persona 155 | Persona 001 | Persona 003 | Persona 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 47.86 [37.53, 58.55] | 52.57 [41.47, 63.55] | 51.85 [41.16, 62.85] | 50.62 [28.47, 73.48] | 54.08 [41.06, 67.16] |
| BixBench | 30.83 [8.13, 54.35] | 30.83 [8.13, 54.35] | 30.83 [8.13, 54.35] | 31.43 [6.90, 56.76] | 28.95 [6.25, 53.34] |
| DiscoveryBench | 13.14 [6.06, 16.73] | 15.27 [7.74, 21.74] | 14.50 [7.09, 22.86] | 17.82 [11.42, 24.04] | 17.36 [12.73, 22.17] |
| EXP-Bench | 43.95 [36.66, 51.27] | 43.05 [35.83, 50.29] | 44.61 [37.23, 52.25] | 44.22 [37.22, 50.11] | 43.57 [35.96, 52.26] |
| SciConvBench | 85.00 [74.17, 94.17] | 85.00 [75.83, 92.50] | 90.00 [80.83, 97.50] | 82.50 [70.00, 92.50] | 77.50 [65.00, 90.00] |

### By scientific super-family

| Group | Persona off | Persona 155 | Persona 001 | Persona 003 | Persona 046 |
|---|---:|---:|---:|---:|---:|
| Life sciences | 27.61 [9.41, 46.54] | 28.12 [9.85, 47.09] | 27.24 [9.07, 46.10] | 28.23 [7.29, 49.68] | 27.02 [8.50, 47.30] |
| Physical sciences & engineering | 66.73 [58.70, 74.25] | 67.25 [59.68, 74.42] | 69.71 [62.31, 76.54] | 76.91 [64.40, 87.98] | 66.34 [55.83, 76.16] |
| Mathematics & computer science | 50.67 [43.72, 57.35] | 52.21 [45.38, 58.65] | 54.15 [47.30, 60.71] | 57.29 [54.67, 59.50] | 50.76 [43.61, 58.19] |
| Social sciences & humanities | 14.97 [8.33, 18.33] | 17.80 [12.10, 24.89] | 16.86 [9.98, 26.52] | 19.60 [13.47, 27.30] | 18.35 [13.00, 24.17] |

## Coverage for table construction

Each entry below is **distinct questions / evaluable trial episodes**. Use the CSV for source-study counts and cell-specific trial IDs. Do not label every cell n = 40 or count repeated episodes as independent questions.

| Benchmark | Persona off | Persona 155 | Persona 001 | Persona 003 | Persona 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 39 / 100 | 39 / 99 | 40 / 117 | 11 / 11 | 28 / 28 |
| BixBench | 40 / 119 | 40 / 119 | 40 / 120 | 35 / 35 | 38 / 38 |
| DiscoveryBench | 40 / 117 | 40 / 111 | 40 / 118 | 31 / 31 | 39 / 39 |
| EXP-Bench | 40 / 120 | 40 / 107 | 40 / 120 | 6 / 6 | 40 / 40 |
| SciConvBench | 40 / 120 | 40 / 120 | 40 / 120 | 40 / 40 | 40 / 40 |

| Super-family | Persona off | Persona 155 | Persona 001 | Persona 003 | Persona 046 |
|---|---:|---:|---:|---:|---:|
| Life sciences | 50 / 146 | 50 / 142 | 50 / 147 | 41 / 41 | 46 / 46 |
| Physical sciences & engineering | 62 / 175 | 62 / 175 | 63 / 188 | 42 / 42 | 56 / 56 |
| Mathematics & computer science | 55 / 161 | 55 / 148 | 55 / 164 | 16 / 16 | 51 / 51 |
| Social sciences & humanities | 32 / 94 | 32 / 91 | 32 / 96 | 24 / 24 | 32 / 32 |

## Candidate table caption

Available scientific-task performance by simulator persona, benchmark, and scientific super-family. Entries show mean normalized native score (0–100) and pointwise 95% confidence intervals. Observed trials are averaged within question, followed by equal weighting of questions within each group. Intervals use 20,000 source-stratified study-cluster bootstrap resamples. Persona off, 155, and 001 have up to three trials; 003 and 046 have one. Evaluable repaired endpoints are preferred, with original fallback when repairs are unevaluable; repairs are not additional independent trials. Scientific missing submissions receive zero, while infrastructure/evaluation failures remain missing. Counts vary by cell. ASI absolute scores mix historical judge versions, and super-family aggregates combine different native metrics.

## Instructions for the next agent

- Preserve persona order: off, 155, 001, 003, 046. Make benchmark and super-family tables or two sections of one table.
- Read the full-precision CSV, then format to two decimals. Use em dashes for missing values; never replace missing values with zero.
- These are absolute available-case means. Do not obtain matched differences by subtracting these cell means: the paired panel uses different eligibility rules and denominators.
- CI overlap is not the pairwise significance test. Do not add significance stars or significance-based bolding from this file.
- The CSV is self-contained; local source provenance is recorded in [performance_panel_provenance.json](data/performance_panel_provenance.json).
