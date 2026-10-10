# Compact paired behavioral analysis

**Four-panel behavioral comparison.** Cells show row minus column for Off/155/001/003/046. A: simulator episode-total output tokens; B: actor episode-total output tokens. Both include reasoning, are expressed in thousands, and share color limits. C: mean per-episode clarification recall (percentage-point differences). D: actor tool calls per episode. All four panels show lower triangles; gray diagonal denotes self-comparison. All eligible matched episodes are included regardless of final performance. Tool use applies to four execution/design sources; clarification recall applies to SciConv. Match question/trial before averaging, then equally weight questions within benchmarks and available benchmarks. Coverage varies by metric/pair. Revision requests were removed from this display after inspection of nonsignificant results; their ten tests remain in the original 50-comparison Holm correction and source-data tables. Star key: A/B, Holm-adjusted p < 0.20 across 50 comparisons; C, absolute difference > 2 percentage points; D, absolute difference > 0.2 calls/episode. C/D stars highlight user-selected effect-size thresholds, not statistical significance or 95% confidence. Thresholds were selected after inspection.

Stars alongside p values in the tables below indicate Holm-adjusted p < 0.20 only; these statistical flags are distinct from the C/D figure highlights.

## A  Simulator output

| Row − column | Difference [95% CI] | Holm p | Questions | Episode pairs | Questions by source |
|---|---|---|---|---|---|
| 155 − Off | +0.263 [+0.242, +0.287] | 0.0005* | 196 | 525 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 38} |
| 001 − Off | +0.048 [+0.034, +0.061] | 0.0005* | 195 | 528 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 37} |
| 001 − 155 | -0.217 [-0.239, -0.197] | 0.0005* | 196 | 514 | {"asibench": 39, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 37} |
| 003 − Off | +0.236 [+0.217, +0.258] | 0.0005* | 101 | 101 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6, "sciconvbench": 38} |
| 003 − 155 | -0.030 [-0.062, -0.003] | 1 | 101 | 101 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6, "sciconvbench": 38} |
| 003 − 001 | +0.173 [+0.149, +0.200] | 0.0005* | 100 | 100 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 5, "sciconvbench": 38} |
| 046 − Off | +0.032 [+0.005, +0.054] | 0.6844 | 168 | 168 | {"asibench": 18, "bixbench": 37, "discoverybench": 36, "expbench": 39, "sciconvbench": 38} |
| 046 − 155 | -0.218 [-0.245, -0.195] | 0.0005* | 166 | 166 | {"asibench": 18, "bixbench": 37, "discoverybench": 34, "expbench": 39, "sciconvbench": 38} |
| 046 − 001 | -0.047 [-0.089, -0.014] | 0.2827 | 168 | 168 | {"asibench": 22, "bixbench": 37, "discoverybench": 36, "expbench": 36, "sciconvbench": 37} |
| 046 − 003 | -0.189 [-0.212, -0.168] | 0.0005* | 99 | 99 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 38} |

## B  Actor output

| Row − column | Difference [95% CI] | Holm p | Questions | Episode pairs | Questions by source |
|---|---|---|---|---|---|
| 155 − Off | +1.123 [+0.838, +1.451] | 0.0005* | 196 | 525 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 38} |
| 001 − Off | -0.252 [-0.548, -0.002] | 1 | 195 | 528 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 37} |
| 001 − 155 | -1.372 [-1.722, -1.058] | 0.0005* | 196 | 514 | {"asibench": 39, "bixbench": 40, "discoverybench": 40, "expbench": 40, "sciconvbench": 37} |
| 003 − Off | +0.611 [+0.290, +1.022] | 0.03744* | 101 | 101 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6, "sciconvbench": 38} |
| 003 − 155 | -0.455 [-0.745, -0.121] | 0.5065 | 101 | 101 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6, "sciconvbench": 38} |
| 003 − 001 | +0.741 [+0.423, +1.135] | 0.0032* | 100 | 100 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 5, "sciconvbench": 38} |
| 046 − Off | +0.180 [-0.152, +0.510] | 1 | 168 | 168 | {"asibench": 18, "bixbench": 37, "discoverybench": 36, "expbench": 39, "sciconvbench": 38} |
| 046 − 155 | -0.951 [-1.328, -0.598] | 0.0005* | 166 | 166 | {"asibench": 18, "bixbench": 37, "discoverybench": 34, "expbench": 39, "sciconvbench": 38} |
| 046 − 001 | +0.084 [-0.426, +0.550] | 1 | 168 | 168 | {"asibench": 22, "bixbench": 37, "discoverybench": 36, "expbench": 36, "sciconvbench": 37} |
| 046 − 003 | -0.095 [-0.615, +0.407] | 1 | 99 | 99 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 38} |

## C  Clarification recall

| Row − column | Difference [95% CI] | Holm p | Questions | Episode pairs | Questions by source |
|---|---|---|---|---|---|
| 155 − Off | +2.535 [-1.840, +7.674] | 1 | 40 | 120 | {"sciconvbench": 40} |
| 001 − Off | +2.257 [-2.118, +7.500] | 1 | 40 | 120 | {"sciconvbench": 40} |
| 001 − 155 | -0.278 [-4.950, +4.058] | 1 | 40 | 120 | {"sciconvbench": 40} |
| 003 − Off | +0.312 [-6.250, +7.500] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 003 − 155 | +0.714 [-5.089, +7.679] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 003 − 001 | +3.229 [-5.521, +12.396] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 046 − Off | +1.637 [-6.071, +10.387] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 046 − 155 | +2.039 [-5.000, +10.625] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 046 − 001 | +4.554 [-5.238, +14.970] | 1 | 40 | 40 | {"sciconvbench": 40} |
| 046 − 003 | +1.324 [-2.530, +7.188] | 1 | 40 | 40 | {"sciconvbench": 40} |

## D  Actor tool use

| Row − column | Difference [95% CI] | Holm p | Questions | Episode pairs | Questions by source |
|---|---|---|---|---|---|
| 155 − Off | +0.274 [-0.142, +0.729] | 1 | 158 | 413 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40} |
| 001 − Off | -0.288 [-0.632, +0.021] | 1 | 158 | 417 | {"asibench": 38, "bixbench": 40, "discoverybench": 40, "expbench": 40} |
| 001 − 155 | -0.539 [-0.890, -0.199] | 0.08056* | 159 | 403 | {"asibench": 39, "bixbench": 40, "discoverybench": 40, "expbench": 40} |
| 003 − Off | -0.401 [-1.135, +0.200] | 1 | 63 | 63 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6} |
| 003 − 155 | -0.165 [-0.645, +0.317] | 1 | 63 | 63 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 6} |
| 003 − 001 | -0.078 [-0.471, +0.278] | 1 | 62 | 62 | {"asibench": 7, "bixbench": 28, "discoverybench": 22, "expbench": 5} |
| 046 − Off | -0.192 [-0.580, +0.225] | 1 | 130 | 130 | {"asibench": 18, "bixbench": 37, "discoverybench": 36, "expbench": 39} |
| 046 − 155 | -0.266 [-0.561, +0.047] | 1 | 128 | 128 | {"asibench": 18, "bixbench": 37, "discoverybench": 34, "expbench": 39} |
| 046 − 001 | -0.265 [-0.766, +0.220] | 1 | 131 | 131 | {"asibench": 22, "bixbench": 37, "discoverybench": 36, "expbench": 36} |
| 046 − 003 | +0.278 [-0.234, +0.922] | 1 | 61 | 61 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6} |

## Methods

Two-sided paired study-cluster sign flip; exact <=16 study blocks, otherwise 99,999 Monte Carlo draws with plus-one correction. Source-balanced weighted task differences; all tasks in a study share a sign. Requires independent study blocks and blockwise sign symmetry/exchangeability under the null.

Holm across the original 50 metric/persona-pair comparisons (including the undisplayed revision-request comparisons); one star for adjusted p<0.20, none otherwise. CIs are pointwise 95% study bootstrap, not multiplicity-adjusted.

All panels include all eligible matched episodes, without filtering on final performance. Metrics are calculated per episode before averaging; coverage varies by pair and metric.

Match source/question/trial, average repeats within question, then questions within benchmark and benchmarks equally. Pair/metric-specific coverage.

Actor and simulator recorded output separately per whole episode including reasoning, initial simulator decisions and final actor responses; no judge usage. Display in thousands.

Historical selected persona panel, unequal repeats and metric-specific availability; exploratory. The display threshold was changed to 0.20 after inspecting the results. Stars do not establish better adaptation or human realism.

Star key: A/B, Holm-adjusted p < 0.20 across 50 comparisons; C, absolute difference > 2 percentage points; D, absolute difference > 0.2 calls/episode. C/D stars highlight user-selected effect-size thresholds, not statistical significance or 95% confidence. Thresholds were selected after inspection.
