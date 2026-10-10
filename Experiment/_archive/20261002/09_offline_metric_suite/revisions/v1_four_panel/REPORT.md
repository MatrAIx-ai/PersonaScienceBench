# Four-metric offline suite

> Archived revision. Links resolve to files preserved with this revision where available. Unbundled historical paths are recorded as text; current outputs are not substituted for historical evidence.

[Executed notebook](metric_suite.ipynb) · [Main figure](figures/metric_suite.pdf) · [Candidate caption](FIGURE_CAPTION.md)

Selected settings: off/155/001/003/046. All measurements use original Astra-low endpoints from the historical protocol. Saved traces, native judgments and native scores only; no new LLM inference. Earlier repaired-endpoint performance figures remain separate. This suite is exploratory and does not evaluate human realism.

## Main findings

- Structural repetition within off: 85.18 [78.85, 90.55]%. Across all ten persona pairs: 83.56 [79.14, 87.65]%. Their paired difference is -1.62 [-5.14, 2.19] percentage points. Equal source weights; same 100-question panel (77 source-study clusters).
- Structural matches remain common. In SciConv, every observed same-length comparison matches exactly: this native-event metric captures questioning length/stopping, not semantic templates or different scientific methods.
- Native fact recovery is available for all 20 disambiguation cases in every selected setting. Absolute means and same-trial paired contrasts differ for single-trial settings because off has three trials.
- BixBench has identical equal-budget failed-task coverage for off and the persona mixture. SciConv has a positive coverage point difference at three episodes, but its paired interval includes zero. No significant gain or equivalence conclusion is asserted.

## Coverage

| Setting | Observed trials | Original slots | Evaluable scores | Complete traces | Recovery episodes |
|---|---|---|---|---|---|
| Off | 1,2,3 | 600 | 565 | 565 | 60 |
| 155 | 1,2,3 | 600 | 545 | 545 | 60 |
| 001 | 1,2,3 | 600 | 568 | 568 | 60 |
| 003 | 1 | 200 | 104 | 104 | 20 |
| 046 | 1 | 200 | 176 | 176 | 20 |

Repetition requires ≥2 complete traces for off/155/001 and ≥1 for 003/046 on each included question. It retains 100/200 selected questions: ASI-Bench 7, BixBench 27, DiscoveryBench 21, EXP-Bench 5, SciConvBench 40. No trace subsampling. Within-persona diagonals for 003/046 are unavailable.

![Four metrics](figures/metric_suite.png)

## 1. Interaction-pattern repetition

The canonical sequence retains ordered simulator review decisions, additional actor handoffs and end/limit markers. Initial requests and each phase’s first mandatory actor handoff are omitted; actual decisions on mandatory reviews are retained because their outcomes can vary. All natural-language prose and transport/retry events are ignored. SciConv retains questions, replies, final specification and cap/complete termination. Repeated events are not collapsed. End-state markers are protocol outcomes, not scientific success labels.
For each question, between-persona repetition is the fraction of all cross-trial pairs with identical sequences; within-persona repetition uses only distinct repeat pairs. Average within source then equally over five sources. Replicate pairs are not independent sampling units. The same-length sensitivity conditions on equal exchange counts and has different pair/question coverage. It is exported rather than silently replacing the primary metric.

| Pair (row / column) | Repetition % [95% CI]; questions, studies | Δ from within-off repetition (pp) |
|---|---|---|
| Off / Off | 85.18 [78.85, 90.55]; n=100, g=77 | — |
| 155 / Off | 82.95 [77.91, 87.60]; n=100, g=77 | -2.23 [-5.55, 1.17]; n=100, g=77 |
| 155 / 155 | 77.92 [70.79, 84.54]; n=100, g=77 | — |
| 001 / Off | 83.40 [77.89, 88.10]; n=100, g=77 | -1.77 [-5.23, 1.25]; n=100, g=77 |
| 001 / 155 | 79.79 [74.31, 84.77]; n=100, g=77 | -5.39 [-9.16, -1.61]; n=100, g=77 |
| 001 / 001 | 79.58 [72.56, 85.88]; n=100, g=77 | — |
| 003 / Off | 86.44 [81.86, 90.57]; n=100, g=77 | 1.26 [-2.38, 5.22]; n=100, g=77 |
| 003 / 155 | 82.34 [76.71, 87.54]; n=100, g=77 | -2.83 [-7.25, 1.96]; n=100, g=77 |
| 003 / 001 | 83.27 [78.07, 87.71]; n=100, g=77 | -1.91 [-6.14, 2.23]; n=100, g=77 |
| 003 / 003 | — | — |
| 046 / Off | 86.33 [81.78, 90.76]; n=100, g=77 | 1.15 [-3.00, 5.60]; n=100, g=77 |
| 046 / 155 | 82.29 [76.95, 87.54]; n=100, g=77 | -2.89 [-7.78, 2.57]; n=100, g=77 |
| 046 / 001 | 81.89 [76.40, 87.02]; n=100, g=77 | -3.29 [-8.33, 1.90]; n=100, g=77 |
| 046 / 003 | 86.92 [81.84, 91.74]; n=100, g=77 | 1.74 [-4.21, 8.37]; n=100, g=77 |
| 046 / 046 | — | — |

Source breakdown (original snapshot path: `figures/repetition_by_benchmark.pdf`; not bundled in this revision) · All source/family cells and same-length sensitivity (original snapshot path: `data/repetition.csv`; not bundled in this revision) · Exact canonical sequences (original snapshot path: `data/trace_patterns.csv`; not bundled in this revision)

## 2. Native missing-fact recovery

Disambiguation only. Read the saved native fraction, validate against n_items, average repeats within case then cases equally. This is endpoint fact recovery before the intent gate; not disclosure, incorporation, or per-turn information gain. Reuse original saved judge responses; no regrading. The strict new SciConv protocol has no scored data and is excluded.

| Setting | Recovery % [95% CI]; cases, studies | Matched Δ vs off (pp) |
|---|---|---|
| Off | 84.70 [70.42, 96.37]; n=20, g=20 | Reference |
| 155 | 88.63 [75.30, 99.88]; n=20, g=20 | 3.93 [-0.24, 11.31]; n=20, g=20 |
| 001 | 88.69 [75.71, 99.52]; n=20, g=20 | 3.99 [0.00, 11.07]; n=20, g=20 |
| 003 | 91.70 [80.00, 99.29]; n=20, g=20 | 5.54 [-1.43, 16.79]; n=20, g=20 |
| 046 | 86.43 [71.43, 98.57]; n=20, g=20 | 0.27 [-1.07, 1.88]; n=20, g=20 |

All five settings share 20 cases; the common-case sensitivity equals the available-case recovery means. Off/155/001 have 60 episodes each, 003/046 have 20 each. Paired deltas for single-trial personas use off trial 1 only. Current CIs resample source-study clusters, whereas the older Experiment 08 report stratified by domain; means agree but intervals need not.

## 3. Native scientific outcomes

Native source scores are unchanged: ASI normalized native score; Bix correctness; Discovery final_score; EXP gated_coverage_mean with documented initial fallback; SciConv FRR. Scientific missing submissions are zero; infrastructure failures are missing. Absolute ASI values mix historical judge configurations and are descriptive. All pairwise contrasts enforce native evaluator compatibility, including corrected ASI judges on both sides. Super-families are descriptive mixtures of different native metrics.

### Benchmark

| Setting | ASI-Bench | BixBench | DiscoveryBench | EXP-Bench | SciConvBench |
|---|---|---|---|---|---|
| Off | 47.55 [37.14, 58.14]; n=38, g=38 | 30.83 [8.33, 55.07]; n=40, g=25 | 13.33 [6.06, 17.14]; n=40, g=6 | 43.95 [36.48, 51.40]; n=40, g=23 | 85.00 [75.00, 94.17]; n=40, g=40 |
| 155 | 52.69 [41.52, 63.80]; n=39, g=39 | 30.83 [8.33, 55.07]; n=40, g=25 | 15.38 [7.68, 21.77]; n=40, g=6 | 43.15 [35.84, 50.48]; n=40, g=23 | 85.00 [75.83, 92.50]; n=40, g=40 |
| 001 | 51.61 [40.90, 62.60]; n=40, g=40 | 30.83 [8.33, 55.07]; n=40, g=25 | 14.72 [7.01, 22.89]; n=40, g=6 | 44.45 [36.97, 52.17]; n=40, g=23 | 90.00 [81.67, 97.50]; n=40, g=40 |
| 003 | 61.22 [34.03, 86.76]; n=8, g=8 | 35.71 [10.34, 61.54]; n=28, g=20 | 14.04 [9.14, 20.11]; n=22, g=5 | 44.22 [37.22, 50.11]; n=6, g=6 | 82.50 [70.00, 92.50]; n=40, g=40 |
| 046 | 57.73 [42.77, 72.55]; n=23, g=23 | 29.73 [6.52, 54.76]; n=37, g=25 | 18.30 [13.86, 22.77]; n=37, g=6 | 44.68 [36.96, 53.50]; n=39, g=23 | 77.50 [65.00, 90.00]; n=40, g=40 |

### Super-family

| Setting | Life sciences | Physical / engineering | Math / CS | Social / humanities |
|---|---|---|---|---|
| Off | 27.67 [9.60, 47.06]; n=50, g=31 | 66.72 [58.66, 74.30]; n=61, g=58 | 50.76 [44.03, 57.43]; n=55, g=39 | 15.21 [8.33, 18.86]; n=32, g=4 |
| 155 | 28.10 [9.94, 47.49]; n=50, g=31 | 67.37 [59.65, 74.65]; n=62, g=59 | 52.24 [45.58, 58.75]; n=55, g=39 | 17.94 [12.34, 24.89]; n=32, g=4 |
| 001 | 27.17 [9.09, 46.57]; n=50, g=31 | 69.62 [62.09, 76.46]; n=63, g=60 | 54.03 [47.31, 60.61]; n=55, g=39 | 17.14 [10.53, 26.52]; n=32, g=4 |
| 003 | 32.48 [10.28, 55.08]; n=32, g=22 | 77.62 [64.91, 89.05]; n=41, g=41 | 65.38 [62.38, 67.90]; n=14, g=13 | 13.34 [7.26, 19.79]; n=17, g=3 |
| 046 | 27.79 [7.87, 49.29]; n=43, g=29 | 67.49 [56.91, 77.64]; n=54, g=51 | 52.52 [45.23, 60.40]; n=48, g=33 | 18.94 [13.32, 24.17]; n=31, g=4 |

Native score figure with CIs (original snapshot path: `figures/native_scores_with_ci.pdf`; not bundled in this revision) · All compatible pairwise contrasts (original snapshot path: `data/matched_contrasts.csv`; not bundled in this revision)

## 4. Equal-budget failed-task coverage

Use native binary Bix correctness and SciConv FRR. A scientific failure is score=0, including a scientific missing submission. No threshold is invented for ASI/Discovery/EXP. Fixed common questions require off trials 1–3 and at least one valid original result for each of the four personas, with compatible evaluator versions. This retains 26 Bix and 40 SciConv questions. Exclusion reasons are exported.
At budget m=1,2,3, average every size-m subset of the three observed off trials. For the persona mixture, choose m distinct personas uniformly from the four, and choose one available original trial per chosen persona uniformly. The reported failure coverage is the expected fraction of questions with at least one failure under these empirical allocation policies; it is not an optimized persona selection or an independent new rollout estimate. Different trial availability is part of this conditional policy, not eliminated by matching budgets.

| Benchmark | Episodes/question | Repeated off % | Persona mixture % | Paired Δ (pp) |
|---|---|---|---|---|
| BixBench | 1 | 61.54 [36.36, 88.00]; n=26, g=20 | 61.54 [36.36, 88.00]; n=26, g=20 | 0.00 [0.00, 0.00]; n=26, g=20 |
| BixBench | 2 | 61.54 [36.36, 88.00]; n=26, g=20 | 61.54 [36.36, 88.00]; n=26, g=20 | 0.00 [0.00, 0.00]; n=26, g=20 |
| BixBench | 3 | 61.54 [36.36, 88.00]; n=26, g=20 | 61.54 [36.36, 88.00]; n=26, g=20 | 0.00 [0.00, 0.00]; n=26, g=20 |
| SciConvBench | 1 | 15.00 [5.83, 25.00]; n=40, g=40 | 16.25 [8.54, 25.21]; n=40, g=40 | 1.25 [-5.83, 8.33]; n=40, g=40 |
| SciConvBench | 2 | 19.17 [7.50, 31.67]; n=40, g=40 | 23.94 [13.89, 35.05]; n=40, g=40 | 4.77 [-5.42, 15.28]; n=40, g=40 |
| SciConvBench | 3 | 20.00 [7.50, 32.50]; n=40, g=40 | 29.44 [17.57, 42.01]; n=40, g=40 | 9.44 [-1.32, 21.25]; n=40, g=40 |

The mixture-only and off-only failed-task sets are averaged over independently sampled allocation choices between the two strategies; they are not distinct failure-mechanism counts. Their difference equals the coverage difference. Curves are nested budget summaries on a fixed question panel, not independent observations. Additional budget gains can be obtained by adjacent-budget subtraction; no attribution to an individual persona is claimed.
A supplementary SciConv sensitivity keeps only questions whose saved intent-capture flag is 1 in every included episode. This is outcome-conditioned and not the primary analysis. It checks one native fidelity signal, not full simulator factual correctness. Its denominators are in the CSV.

## Uncertainty and limitations

20,000 percentile bootstrap draws over source-study clusters, carrying all matched outcomes within each study. Average repeats within task first. Source weights are fixed: equal source weights for aggregate repetition, observed task proportions elsewhere. Paired-difference CIs use per-question differences, not subtraction of marginal CI endpoints. CIs are pointwise, conditional on saved trials and valid coverage, with no significance stars or multiplicity-adjusted claims. One-study strata contribute no resampling variation; total-one-study cells have unavailable CIs. Per-cell source/study counts are exported. Original persona selection and the selected five-setting panel were exploratory.
No new semantic labels, human-realism judgments, embeddings, actor/simulator calls, or task executions were generated. Patterns are coarse protocol structure. Unequal repeat counts and incomplete original episodes limit generalization. Larger failure coverage is informative only under valid task-preserving simulation; the saved intent check is incomplete evidence of fidelity.

## Reproduction

`OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/extract.py`

`OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/analyze.py`

`MPLCONFIGDIR=/tmp/psb-mpl OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/build_notebook.py`

The snapshot stores only numeric metadata, protocol action labels and file hashes/paths, not private conversation text. Original files remain authoritative. `code/test_metrics.py` checks canonicalization, distinct-repeat pairing, exhaustive allocation arithmetic, task weighting, and equality to previously saved outcome/recovery means.
