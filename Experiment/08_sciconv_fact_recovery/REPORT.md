# Experiment 08 — SciConv fact recovery

[Executed analysis notebook](analysis.ipynb) · [Plan](PLAN.md)

Exploratory reanalysis of saved Astra-low judgements: 20 disambiguation cases × 6 persona settings × 3 original trials = 360 eligible episode slots. The other 20 SciConv inconsistency cases per condition/trial are excluded: inconsistency resolution is not a deleted-fact count. No new model calls or regrading.

Primary metric: recovered deleted facts / total deleted facts, from native `llm_judge_disambiguation_score.json`, validated against the native issue count. Recovery is not intent-gated; FRR remains a separate outcome. We average trial scores within each case, then give each case equal weight, rather than giving cases with more facts more weight.

Original outcomes are primary; the after-repair view is a sensitivity check. A retry is never an independent trial. Five persona-minus-off contrasts pair the same case and trial before averaging within cases. Pointwise 95% percentile intervals use 20,000 study-cluster bootstrap draws within domains, preserving observed domain weights (seed 20261001). They condition on the observed trials, do not separately estimate repeat-run uncertainty, and are not multiplicity-corrected significance tests. Sparse study/domain strata can produce unstable or degenerate intervals.

## Original three-trial results

| Persona | Recovery % [95% CI] | Paired Δ vs off (pp) [95% CI] | FRR % | Cases / episodes | Cap hits (all) |
|---|---|---|---:|---:|---:|
| Off | 84.7 [71.8, 96.0] | reference | 78.3 | 20 / 60 | 8 |
| 148 | 87.1 [75.1, 97.1] | 2.4 [-2.9, 8.5] | 83.3 | 20 / 60 | 5 |
| 155 | 88.6 [77.1, 99.8] | 3.9 [-0.1, 10.0] | 80.0 | 20 / 60 | 8 |
| 089 | 90.9 [80.9, 98.5] | 6.2 [-0.7, 13.1] | 81.7 | 20 / 59 | 9 |
| 001 | 88.7 [77.5, 98.6] | 4.0 [0.2, 10.5] | 81.7 | 20 / 60 | 7 |
| 127 | 88.3 [76.7, 100.0] | 3.6 [-0.5, 10.0] | 83.3 | 20 / 60 | 7 |

![Fact recovery and paired differences](figures/fact_recovery.png)

**Figure.** Native deleted-fact recovery and matched changes relative to persona-off. Bars and printed brackets show means and pointwise 95% CIs; n counts cases and e counts episodes (matched pairs for differences). No inference of a personality mechanism is warranted without neutral-wording and response-length controls.

## Observations

Usable original disambiguation judgements: **359/360**. Baseline difficulty bands: {'near_ceiling': 12, 'multi_fact_mid': 4, 'single_fact': 3, 'low': 1}. The fixed panel is largely near ceiling; it is not a confirmed intermediate-difficulty panel.

All five persona point estimates exceed off, but most paired intervals include zero. Persona 001 has a lower primary pointwise CI bound just above zero; its cap-exclusion interval reaches zero. These five exploratory comparisons are not multiplicity-corrected, and no neutral-wording or response-length intervention was run. Do not interpret this as a confirmed persona benefit.

## Excluding episodes reaching the ten-question limit

A limit hit is inferred from at least ten researcher-reply events, following PR #17. Apply the exclusion to both members of a paired comparison. This is a proxy for the known last-answer handling issue, not a correction or rerun. The cap-hits column retains counts from the full panel.

| Persona | Recovery % [95% CI] | Paired Δ vs off (pp) [95% CI] | FRR % | Cases / episodes | Cap hits (all) |
|---|---|---|---:|---:|---:|
| Off | 87.0 [74.1, 100.0] | reference | 87.0 | 18 / 52 | 8 |
| 148 | 89.5 [77.2, 98.2] | 2.0 [-3.9, 9.8] | 89.5 | 19 / 55 | 5 |
| 155 | 91.1 [80.5, 99.9] | 3.8 [-0.3, 11.6] | 85.1 | 19 / 52 | 8 |
| 089 | 94.1 [82.4, 100.0] | 7.8 [0.0, 15.7] | 92.2 | 17 / 50 | 9 |
| 001 | 90.7 [79.6, 100.0] | 3.7 [0.0, 11.1] | 88.9 | 18 / 53 | 7 |
| 127 | 90.8 [80.3, 100.0] | 3.2 [-0.9, 10.6] | 89.5 | 19 / 53 | 7 |

## Provenance and scope

Original versus repair views differ in recovery share in **1** episode slots. The full sensitivity results are stored in `data/summary.json`. The snapshot includes 1,440 records: two outcome views of all 720 SciConv episode slots, with inconsistency exclusions explicit.

The old runner labels its evaluator version `+luna-judge` even though the frozen configs specify Astra low. This stale label is retained in the snapshot; actual per-role configuration hashes and model names are recorded separately. The campaign uses the pinned pre-PR-6 persona protocol, not current main defaults.

Whitespace-separated reply length and question counts are descriptive only. They are not language-normalized token counts. Saved conversation judges do not supply all PR #12 per-fact delivered/volunteered labels, so those mechanisms are not inferred here.

The persona-off difficulty screen is exploratory and does not select the cases used above. See `data/difficulty_screen.csv`; fresh confirmation and held-out evaluation are required before adopting a screened panel.

[Snapshot with input hashes](data/snapshot.json) · [Numeric episode CSV](data/episodes.csv) · [Summary](data/summary.json) · [PDF](figures/fact_recovery.pdf) · [SVG](figures/fact_recovery.svg)

Reproduce offline: `.venv/bin/python Experiment/08_sciconv_fact_recovery/code/analyze.py`. Add `--refresh` only to re-extract the snapshot from raw saved judgements. No command in this script invokes a model.
