# Persona pilot: discoverybench-persona-pilot

Benchmark **discoverybench**, primary metric `final_score` (native, 0–100 here). 125/125 planned episodes finished; statuses {'scored': 124, 'missing_submission': 1}. Code 6e096c091f0f428a2c0848e91152ea9312073651; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona | candidate_046 | 5 | 25.2 | 4.1 pp | -17.8 pp |
| persona | candidate_148 | 5 | 31.4 | 10.3 pp | -11.6 pp |
| persona | candidate_155 | 5 | 23.8 | 2.6 pp | -19.3 pp |
| persona_off | persona_off | 5 | 21.1 | – | – |
| neutral | neutral_a | 5 | 43.0 | 21.9 pp | – |

Persona-off run-to-run SD (mean over 5 tasks with repeats): 21.5 pp. A persona delta smaller than this is indistinguishable from ordinary variation.

## Uncertainty

Task-matched deltas with a 95% percentile bootstrap interval (episodes resampled within arm × task) and a two-sided permutation p (condition labels shuffled within each task). p values are not corrected for the 7 comparisons shown; treat single p < 0.05 results as leads.

| Contrast | Δ (pp) | 95% CI (pp) | Permutation p |
|---|---:|---:|---:|
| candidate_046 - persona_off | +4.1 | [-10.8, +19.4] | 0.635 |
| candidate_148 - persona_off | +10.3 | [-4.7, +25.0] | 0.231 |
| candidate_155 - persona_off | +2.6 | [-11.3, +16.8] | 0.743 |
| neutral_a - persona_off | +21.9 | [+6.2, +36.2] | 0.015 |
| candidate_046 - neutral_a | -17.8 | [-32.6, -2.1] | 0.045 |
| candidate_148 - neutral_a | -11.6 | [-26.3, +3.8] | 0.169 |
| candidate_155 - neutral_a | -19.3 | [-33.0, -4.0] | 0.026 |

## By task

| Task | Domain | candidate_046 | candidate_148 | candidate_155 | persona_off | neutral_a |
|---|---|---:|---:|---:|---:|---:|
| `test/introduction_pathways_non-native_plants/metadata_0.json/0/0` | biology | 40.0 | 52.0 | 32.0 | 52.0 | 73.1 |
| `test/introduction_pathways_non-native_plants/metadata_2.json/0/0` | biology | 49.3 | 62.0 | 49.3 | 28.0 | 76.0 |
| `test/nls_incarceration/metadata_11.json/0/0` | sociology | 27.9 | 28.6 | 34.3 | 25.7 | 31.4 |
| `test/nls_raw/metadata_7.json/0/0` | sociology | 9.0 | 14.7 | 3.3 | 0.0 | 24.7 |
| `train/immigration_offshoring_effect_on_employment/metadata_0.json/0/1` | economics | 0.0 | 0.0 | 0.0 | 0.0 | 10.0 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| biology | neutral | 10 | 74.6 |
| biology | persona | 30 | 47.4 |
| biology | persona_off | 10 | 40.0 |
| economics | neutral | 5 | 10.0 |
| economics | persona | 15 | 0.0 |
| economics | persona_off | 5 | 0.0 |
| sociology | neutral | 10 | 28.0 |
| sociology | persona | 30 | 19.6 |
| sociology | persona_off | 10 | 12.9 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| persona | 75 | 2.31 | 0.00 | 1990 | 14.9 | 112,225 | 0.0065 |
| persona_off | 25 | 2.32 | 0.00 | 1881 | 14.6 | 88,201 | 0.0052 |
| neutral | 25 | 2.12 | 0.00 | 1903 | 15.0 | 88,675 | 0.0058 |

## Failures and retries

None.

Total cost $0.7613 (provider-reported where given, otherwise tokens at list price) over 1857 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
