# Persona pilot: discoverybench-gender-reverse

Benchmark **discoverybench**, primary metric `final_score` (native, 0–100 here). 225/225 planned episodes finished; statuses {'scored': 220, 'missing_submission': 5}. Code 92a22ca49c48fa5942cd035c8c70201ffe7c6c5b; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona | candidate_026 | 5 | 27.6 | – | – |
| persona | candidate_089 | 5 | 17.6 | – | – |
| persona | candidate_147 | 5 | 12.7 | – | – |
| gender_swap | candidate_026__gender_swap | 5 | 20.1 | – | – |
| gender_swap | candidate_089__gender_swap | 5 | 28.2 | – | – |
| gender_swap | candidate_147__gender_swap | 5 | 20.1 | – | – |
| reordered | candidate_026__reordered | 5 | 27.0 | – | – |
| reordered | candidate_089__reordered | 5 | 26.6 | – | – |
| reordered | candidate_147__reordered | 5 | 38.0 | – | – |

Persona-off run-to-run SD (mean over 0 tasks with repeats): –. A persona delta smaller than this is indistinguishable from ordinary variation.

## Counterfactual variants

Each variant against its own unchanged persona, task-matched; pooled rows stratify by persona × task. Score in pp; hypothesis length in characters. The `reordered` variant changes only line order, so its contrast is the wording-noise reference for the others.

| Contrast | Measure | Δ | 95% CI | Permutation p |
|---|---|---:|---:|---:|
| candidate_026__gender_swap - candidate_026 | score | -7.5 pp | [-21.7, +8.0] | 0.383 |
| candidate_026__gender_swap - candidate_026 | hypothesis chars | +55.5 | [-80.7, +205.2] | 0.500 |
| candidate_026__reordered - candidate_026 | score | -0.6 pp | [-15.5, +15.1] | 0.948 |
| candidate_026__reordered - candidate_026 | hypothesis chars | -20.5 | [-120.6, +81.1] | 0.741 |
| candidate_089__gender_swap - candidate_089 | score | +10.6 pp | [-4.5, +25.5] | 0.221 |
| candidate_089__gender_swap - candidate_089 | hypothesis chars | +267.9 | [-128.0, +719.7] | 0.274 |
| candidate_089__reordered - candidate_089 | score | +9.0 pp | [-5.8, +22.8] | 0.263 |
| candidate_089__reordered - candidate_089 | hypothesis chars | +57.9 | [-211.9, +315.0] | 0.632 |
| candidate_147__gender_swap - candidate_147 | score | +7.4 pp | [-6.2, +21.1] | 0.352 |
| candidate_147__gender_swap - candidate_147 | hypothesis chars | +394.0 | [+121.6, +617.0] | 0.025 |
| candidate_147__reordered - candidate_147 | score | +25.3 pp | [+12.5, +37.3] | 0.002 |
| candidate_147__reordered - candidate_147 | hypothesis chars | -47.9 | [-111.2, +12.5] | 0.214 |
| gender_swap (pooled) - persona | score | +3.5 pp | [-5.2, +11.8] | 0.465 |
| gender_swap (pooled) - persona | hypothesis chars | +239.2 | [+75.9, +415.2] | 0.017 |
| reordered (pooled) - persona | score | +11.3 pp | [+2.9, +19.3] | 0.017 |
| reordered (pooled) - persona | hypothesis chars | -3.5 | [-101.7, +91.3] | 0.947 |

## By task

| Task | Domain | candidate_026 | candidate_089 | candidate_147 | candidate_026__gender_swap | candidate_089__gender_swap | candidate_147__gender_swap | candidate_026__reordered | candidate_089__reordered | candidate_147__reordered |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test/introduction_pathways_non-native_plants/metadata_0.json/0/0` | biology | 56.0 | 32.0 | 0.0 | 16.0 | 68.0 | 36.0 | 32.0 | 48.0 | 57.3 |
| `test/introduction_pathways_non-native_plants/metadata_2.json/0/0` | biology | 46.0 | 36.0 | 20.0 | 48.0 | 41.3 | 36.0 | 63.3 | 60.0 | 72.0 |
| `test/nls_incarceration/metadata_11.json/0/0` | sociology | 20.0 | 20.0 | 30.7 | 24.3 | 15.7 | 28.6 | 25.7 | 20.0 | 37.1 |
| `test/nls_raw/metadata_7.json/0/0` | sociology | 16.0 | 0.0 | 13.0 | 12.4 | 16.0 | 0.0 | 14.0 | 5.2 | 23.7 |
| `train/immigration_offshoring_effect_on_employment/metadata_0.json/0/1` | economics | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| biology | gender_swap | 30 | 40.9 |
| biology | persona | 30 | 31.7 |
| biology | reordered | 30 | 55.4 |
| economics | gender_swap | 15 | 0.0 |
| economics | persona | 15 | 0.0 |
| economics | reordered | 15 | 0.0 |
| sociology | gender_swap | 30 | 16.2 |
| sociology | persona | 30 | 16.6 |
| sociology | reordered | 30 | 21.0 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| persona | 75 | 2.75 | 0.01 | 2076 | 408 | 4.1 | 16.3 | 126,414 | 0.0067 |
| gender_swap | 75 | 2.75 | 0.03 | 2092 | 617 | 8.8 | 16.4 | 126,420 | 0.0070 |
| reordered | 75 | 2.52 | 0.01 | 2010 | 397 | 5.3 | 15.8 | 114,664 | 0.0066 |

## Failures and retries

- `candidate_026-r2-f4139736a666` (attempt 1): infrastructure_error
- `candidate_089__reordered-r2-8693a2cd77ae` (attempt 1): infrastructure_error
- `candidate_089__reordered-r5-8693a2cd77ae` (attempt 1): error
- `candidate_147__reordered-r5-f132fde672bc` (attempt 1): infrastructure_error

Total cost $1.5368 (provider-reported where given, otherwise tokens at list price) over 3665 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
