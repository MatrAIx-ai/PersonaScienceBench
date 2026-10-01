# Persona pilot: discoverybench-counterfactual

Benchmark **discoverybench**, primary metric `final_score` (native, 0–100 here). 300/300 planned episodes finished; statuses {'scored': 298, 'missing_submission': 2}. Code 742b98bb3bc6d4212fa6b6d17eebd92435bb38f3; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona | candidate_046 | 5 | 22.3 | – | – |
| persona | candidate_148 | 5 | 27.0 | – | – |
| persona | candidate_155 | 5 | 33.1 | – | – |
| gender_swap | candidate_046__gender_swap | 5 | 21.1 | – | – |
| gender_swap | candidate_148__gender_swap | 5 | 21.7 | – | – |
| gender_swap | candidate_155__gender_swap | 5 | 19.2 | – | – |
| reordered | candidate_046__reordered | 5 | 18.7 | – | – |
| reordered | candidate_148__reordered | 5 | 27.5 | – | – |
| reordered | candidate_155__reordered | 5 | 22.2 | – | – |
| speed_accuracy_flip | candidate_046__speed_accuracy_flip | 5 | 21.7 | – | – |
| speed_accuracy_flip | candidate_148__speed_accuracy_flip | 5 | 24.4 | – | – |
| speed_accuracy_flip | candidate_155__speed_accuracy_flip | 5 | 13.5 | – | – |

Persona-off run-to-run SD (mean over 0 tasks with repeats): –. A persona delta smaller than this is indistinguishable from ordinary variation.

## Counterfactual variants

Each variant against its own unchanged persona, task-matched; pooled rows stratify by persona × task. Score in pp; hypothesis length in characters. The `reordered` variant changes only line order, so its contrast is the wording-noise reference for the others.

| Contrast | Measure | Δ | 95% CI | Permutation p |
|---|---|---:|---:|---:|
| candidate_046__gender_swap - candidate_046 | score | -1.3 pp | [-14.5, +11.8] | 0.888 |
| candidate_046__gender_swap - candidate_046 | hypothesis chars | -100.6 | [-360.6, +91.3] | 0.599 |
| candidate_046__reordered - candidate_046 | score | -3.7 pp | [-15.6, +8.6] | 0.663 |
| candidate_046__reordered - candidate_046 | hypothesis chars | -83.2 | [-343.2, +122.2] | 0.659 |
| candidate_046__speed_accuracy_flip - candidate_046 | score | -0.6 pp | [-14.9, +13.8] | 0.941 |
| candidate_046__speed_accuracy_flip - candidate_046 | hypothesis chars | -130.9 | [-374.5, +34.5] | 0.375 |
| candidate_148__gender_swap - candidate_148 | score | -5.3 pp | [-20.2, +10.3] | 0.540 |
| candidate_148__gender_swap - candidate_148 | hypothesis chars | -41.2 | [-92.2, +11.0] | 0.163 |
| candidate_148__reordered - candidate_148 | score | +0.5 pp | [-14.7, +16.0] | 0.968 |
| candidate_148__reordered - candidate_148 | hypothesis chars | -10.6 | [-86.2, +73.8] | 0.853 |
| candidate_148__speed_accuracy_flip - candidate_148 | score | -2.7 pp | [-18.2, +12.9] | 0.764 |
| candidate_148__speed_accuracy_flip - candidate_148 | hypothesis chars | -26.6 | [-81.6, +33.5] | 0.405 |
| candidate_155__gender_swap - candidate_155 | score | -13.9 pp | [-27.0, -1.1] | 0.079 |
| candidate_155__gender_swap - candidate_155 | hypothesis chars | +44.9 | [-10.7, +100.1] | 0.153 |
| candidate_155__reordered - candidate_155 | score | -10.9 pp | [-24.0, +2.5] | 0.182 |
| candidate_155__reordered - candidate_155 | hypothesis chars | +145.9 | [-48.0, +466.2] | 0.612 |
| candidate_155__speed_accuracy_flip - candidate_155 | score | -19.6 pp | [-32.6, -6.1] | 0.025 |
| candidate_155__speed_accuracy_flip - candidate_155 | hypothesis chars | +55.7 | [-6.3, +133.2] | 0.215 |
| gender_swap (pooled) - persona | score | -6.8 pp | [-15.1, +1.5] | 0.152 |
| gender_swap (pooled) - persona | hypothesis chars | -32.3 | [-115.1, +37.4] | 0.599 |
| reordered (pooled) - persona | score | -4.7 pp | [-12.7, +3.4] | 0.324 |
| reordered (pooled) - persona | hypothesis chars | +17.4 | [-97.9, +146.3] | 0.800 |
| speed_accuracy_flip (pooled) - persona | score | -7.6 pp | [-16.3, +0.9] | 0.120 |
| speed_accuracy_flip (pooled) - persona | hypothesis chars | -33.9 | [-118.2, +34.0] | 0.583 |

## By task

| Task | Domain | candidate_046 | candidate_148 | candidate_155 | candidate_046__gender_swap | candidate_148__gender_swap | candidate_155__gender_swap | candidate_046__reordered | candidate_148__reordered | candidate_155__reordered | candidate_046__speed_accuracy_flip | candidate_148__speed_accuracy_flip | candidate_155__speed_accuracy_flip |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test/introduction_pathways_non-native_plants/metadata_0.json/0/0` | biology | 17.1 | 52.0 | 88.0 | 40.0 | 22.7 | 32.0 | 32.0 | 68.0 | 49.3 | 52.0 | 36.0 | 16.0 |
| `test/introduction_pathways_non-native_plants/metadata_2.json/0/0` | biology | 68.0 | 46.7 | 45.3 | 16.0 | 38.0 | 32.0 | 5.3 | 36.0 | 24.0 | 36.0 | 55.3 | 32.0 |
| `test/nls_incarceration/metadata_11.json/0/0` | sociology | 18.6 | 28.6 | 18.1 | 31.4 | 27.9 | 28.6 | 31.4 | 28.6 | 37.5 | 17.1 | 17.1 | 11.4 |
| `test/nls_raw/metadata_7.json/0/0` | sociology | 8.0 | 8.0 | 14.0 | 18.0 | 10.0 | 3.3 | 16.7 | 5.0 | 0.0 | 3.3 | 13.3 | 8.0 |
| `train/immigration_offshoring_effect_on_employment/metadata_0.json/0/1` | economics | 0.0 | 0.0 | 0.0 | 0.0 | 10.0 | 0.0 | 8.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| biology | gender_swap | 30 | 30.1 |
| biology | persona | 30 | 52.9 |
| biology | reordered | 30 | 35.8 |
| biology | speed_accuracy_flip | 30 | 37.9 |
| economics | gender_swap | 15 | 3.3 |
| economics | persona | 15 | 0.0 |
| economics | reordered | 15 | 2.7 |
| economics | speed_accuracy_flip | 15 | 0.0 |
| sociology | gender_swap | 30 | 19.9 |
| sociology | persona | 30 | 15.9 |
| sociology | reordered | 30 | 19.9 |
| sociology | speed_accuracy_flip | 30 | 11.7 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| persona | 75 | 2.31 | 0.00 | 1898 | 402 | 5.0 | 14.7 | 99,945 | 0.0060 |
| gender_swap | 75 | 2.28 | 0.00 | 1901 | 371 | 3.7 | 14.7 | 100,584 | 0.0060 |
| reordered | 75 | 2.31 | 0.00 | 1895 | 420 | 5.9 | 14.5 | 98,662 | 0.0058 |
| speed_accuracy_flip | 75 | 2.16 | 0.03 | 1853 | 368 | 3.5 | 15.1 | 103,171 | 0.0060 |

## Failures and retries

None.

Total cost $1.7838 (provider-reported where given, otherwise tokens at list price) over 4425 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
