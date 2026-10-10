# Within-conversation self-repetition

This replaces the cross-run structural heatmap in panel A. It uses saved original messages only, separated into simulator and actor roles. No LLM inference or new embeddings. B and D retain their previous values. The prior structural figure and notebook are archived under `revisions/v2_structural_A/`.

## Definition

For each later message of one role in a conversation, form every overlapping window of 40 normalized Unicode characters. Count a window as repeated if exactly the same window appeared in an earlier message of that same role and episode. Divide matched windows by all windows in the current message, then average these fractions across eligible later turns. Repeated windows inside the current message alone do not count. The first eligible message supplies history and is not scored.

Normalization: remove fenced code blocks and Markdown blockquote lines; Unicode NFKC and casefold; retain letters, combining marks and numbers, removing punctuation/whitespace. No word-tokenizer, translation, summaries or semantic judge. Simulator messages omit initial requests/inspection; actor messages are handoffs or SciConv clarification questions, excluding tool logs, transcript history and final SciConv specification. Naturally restated or unmarked quoted material remains part of the observed output.

The primary width of 40 was set before examining outcomes, following the existing 40-character opening analysis. Widths 20 and 80 are sensitivity checks, not alternatives selected by the result. Characters span languages differently; multilingual persona settings and code-heavy messages can affect this metric. It measures long verbatim phrase reuse, not semantic redundancy, unnecessary questioning, lack of progress, or mode collapse. Necessary scientific terms or facts may repeat legitimately.

## Aggregation and missingness

Require at least two messages of the same role with sufficient normalized length. Too-short or single-message conversations are unavailable, never zero. Average eligible original trials within question, retain questions eligible for all five settings, average questions within benchmark and then the five benchmarks equally. Simulator and actor panels are matched separately. Eligibility conditions on conversation length and successful trace completion. Longer conversations have more opportunities for reuse; this is descriptive and does not remove that confounding. Three-trial settings use their available eligible trials; 003/046 use one. Paired contrasts compare question means, not necessarily the same number of trials.

Pointwise 95% percentile CIs use 20,000 source-study cluster bootstrap draws, retaining each sampled study’s matched questions. Trial noise is conditional on saved repeats, not independently re-estimated. No significance stars or multiplicity-adjusted claims.

| Role | Window length | Common questions | Source counts |
|---|---|---|---|
| simulator | 20 | 81 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| simulator | 40 | 80 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 19} |
| simulator | 80 | 78 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 17} |
| actor | 20 | 80 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| actor | 40 | 76 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 16} |
| actor | 80 | 61 | {"asibench": 6, "bixbench": 23, "discoverybench": 21, "expbench": 6, "sciconvbench": 5} |

## Simulator results — 40 characters

| Setting | Repeated windows % [95% CI] | Paired difference vs off (pp) |
|---|---|---|
| Off | 0.10 [0.05, 0.18]; n=80, g=57 | Reference |
| 155 | 0.16 [0.01, 0.38]; n=80, g=57 | 0.05 [-0.11, 0.26]; n=80, g=57 |
| 001 | 0.09 [0.03, 0.16]; n=80, g=57 | -0.01 [-0.11, 0.08]; n=80, g=57 |
| 003 | 0.14 [0.01, 0.34]; n=80, g=57 | 0.04 [-0.09, 0.23]; n=80, g=57 |
| 046 | 0.40 [0.10, 0.82]; n=80, g=57 | 0.29 [-0.00, 0.70]; n=80, g=57 |

## Actor results — 40 characters

| Setting | Repeated windows % [95% CI] | Paired difference vs off (pp) |
|---|---|---|
| Off | 0.05 [0.02, 0.09]; n=76, g=53 | Reference |
| 155 | 0.00 [0.00, 0.00]; n=76, g=53 | -0.05 [-0.09, -0.01]; n=76, g=53 |
| 001 | 0.06 [0.02, 0.14]; n=76, g=53 | 0.01 [-0.06, 0.10]; n=76, g=53 |
| 003 | 0.00 [0.00, 0.01]; n=76, g=53 | -0.05 [-0.08, -0.01]; n=76, g=53 |
| 046 | 0.03 [0.01, 0.06]; n=76, g=53 | -0.02 [-0.07, 0.04]; n=76, g=53 |

## Sensitivity to phrase length

| Role | Window | Off | 155 | 001 | 003 | 046 |
|---|---|---|---|---|---|---|
| simulator | 20 | 2.1012 | 1.3460 | 1.7987 | 2.0522 | 2.8271 |
| simulator | 40 | 0.1031 | 0.1554 | 0.0910 | 0.1429 | 0.3977 |
| simulator | 80 | 0.0074 | 0.0000 | 0.0000 | 0.0000 | 0.0280 |
| actor | 20 | 1.2982 | 0.2135 | 1.0026 | 0.5744 | 1.3197 |
| actor | 40 | 0.0519 | 0.0006 | 0.0634 | 0.0045 | 0.0291 |
| actor | 80 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Sensitivity panels can have different eligible questions; coverage is reported above. The primary simulator contrasts all have CIs including zero. The data do not establish that persona injection reduces within-conversation simulator self-repetition. Low lexical repetition does not rule out semantic or strategic repetition.

## Figure and data

[Main figure](figures/metric_suite.pdf) · [Separate simulator/actor distributions](figures/self_repetition_roles.pdf) · [Executed notebook](metric_suite.ipynb). A shows mean/CI because most case-level values are zero and a few outliers dominate the raw scale. Supporting violins show source-balanced KDEs (Scott bandwidth; observed range; equal maximum width), case dots, source-balanced mean and CI. Density is not uncertainty.

CSV files under data/: `self_repetition_episodes`, `self_repetition_turns`, `self_repetition_cases`, `self_repetition_cells`, `self_repetition_contrasts`. They contain numbers and hashes, not message text. Frozen trace hashes are checked on extraction.

`OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/self_repetition.py` regenerates the extraction, statistics and this report.
