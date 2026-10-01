# Persona pilot: openproblems-persona-pilot

Benchmark **openproblems_denoising**, primary metric `score` (native, 0–100 here). 125/125 planned episodes finished; statuses {'missing_submission': 1, 'scored': 124}. Code 64c2d6585631f5d45a1293895de2814a4b69be43; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona | candidate_046 | 5 | 4.8 | 6.1 pp | 0.7 pp |
| persona | candidate_148 | 5 | 4.1 | 5.4 pp | 0.0 pp |
| persona | candidate_155 | 5 | 3.6 | 4.9 pp | -0.5 pp |
| persona_off | persona_off | 5 | -1.3 | – | – |
| neutral | neutral_a | 5 | 4.1 | 5.4 pp | – |

Persona-off run-to-run SD (mean over 5 tasks with repeats): 27.5 pp. A persona delta smaller than this is indistinguishable from ordinary variation.

## Uncertainty

Task-matched deltas with a 95% percentile bootstrap interval (episodes resampled within arm × task) and a two-sided permutation p (condition labels shuffled within each task). p values are not corrected for the 7 comparisons shown; treat single p < 0.05 results as leads.

| Contrast | Δ (pp) | 95% CI (pp) | Permutation p |
|---|---:|---:|---:|
| candidate_046 - persona_off | +6.1 | [-18.5, +34.4] | 0.782 |
| candidate_148 - persona_off | +5.4 | [-9.0, +20.5] | 0.528 |
| candidate_155 - persona_off | +4.9 | [-10.4, +20.0] | 0.574 |
| neutral_a - persona_off | +5.4 | [-8.0, +19.1] | 0.520 |
| candidate_046 - neutral_a | +0.7 | [-23.0, +29.3] | 0.975 |
| candidate_148 - neutral_a | +0.0 | [-12.8, +13.6] | 0.997 |
| candidate_155 - neutral_a | -0.5 | [-14.2, +13.3] | 0.949 |

## By task

| Task | Domain | candidate_046 | candidate_148 | candidate_155 | persona_off | neutral_a |
|---|---|---:|---:|---:|---:|---:|
| `openproblems_v1/tenx_1k_pbmc` | openproblems_v1 | -5.2 | 12.5 | 7.1 | 16.0 | 3.1 |
| `openproblems_v1/mouse_blood_olsson_labelled` | openproblems_v1 | 48.7 | -6.0 | -17.8 | -28.4 | -2.3 |
| `openproblems_v1/pancreas` | openproblems_v1 | -14.1 | 16.7 | 11.3 | -12.0 | 27.2 |
| `openproblems_v1/tenx_5k_pbmc` | openproblems_v1 | 13.7 | 1.0 | 3.9 | 0.8 | -16.1 |
| `openproblems_v1/immune_cells` | openproblems_v1 | -19.2 | -3.5 | 13.7 | 17.3 | 8.7 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| openproblems_v1 | neutral | 25 | 4.1 |
| openproblems_v1 | persona | 75 | 4.2 |
| openproblems_v1 | persona_off | 25 | -1.3 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| persona | 75 | 2.47 | 0.12 | 2028 | 1587 | 32.6 | 16.0 | 137,695 | 0.0082 |
| persona_off | 25 | 2.36 | 0.16 | 2160 | 1592 | 31.0 | 15.5 | 110,064 | 0.0069 |
| neutral | 25 | 2.60 | 0.04 | 2226 | 1808 | 33.8 | 15.0 | 118,105 | 0.0071 |

## Failures and retries

- `candidate_046-r1-124566223954` (attempt 1): launch_error
- `candidate_046-r1-7b00206d58ae` (attempt 1): launch_error
- `candidate_046-r1-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_046-r1-fa4087c369be` (attempt 1): launch_error
- `candidate_046-r2-124566223954` (attempt 1): launch_error
- `candidate_046-r2-1bd642898c4f` (attempt 1): launch_error
- `candidate_046-r2-7b00206d58ae` (attempt 1): launch_error
- `candidate_046-r2-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_046-r2-fa4087c369be` (attempt 1): launch_error
- `candidate_046-r3-124566223954` (attempt 1): launch_error
- `candidate_046-r3-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_046-r3-fa4087c369be` (attempt 1): launch_error
- `candidate_046-r4-1bd642898c4f` (attempt 1): launch_error
- `candidate_046-r4-7b00206d58ae-retry2` (attempt 2): error
- `candidate_046-r4-7b00206d58ae` (attempt 1): launch_error
- `candidate_046-r4-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_046-r4-fa4087c369be` (attempt 1): launch_error
- `candidate_046-r5-124566223954` (attempt 1): launch_error
- `candidate_046-r5-1bd642898c4f` (attempt 1): launch_error
- `candidate_046-r5-7b00206d58ae` (attempt 1): launch_error
- `candidate_046-r5-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_046-r5-fa4087c369be` (attempt 1): launch_error
- `candidate_148-r1-124566223954` (attempt 1): launch_error
- `candidate_148-r1-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_148-r2-7b00206d58ae` (attempt 1): launch_error
- `candidate_148-r2-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_148-r3-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_148-r4-124566223954` (attempt 1): launch_error
- `candidate_148-r4-1bd642898c4f` (attempt 1): launch_error
- `candidate_148-r4-7b00206d58ae` (attempt 1): launch_error
- `candidate_148-r5-124566223954` (attempt 1): launch_error
- `candidate_148-r5-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r1-124566223954` (attempt 1): infrastructure_error
- `candidate_155-r1-1bd642898c4f` (attempt 1): launch_error
- `candidate_155-r1-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r1-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_155-r1-fa4087c369be` (attempt 1): launch_error
- `candidate_155-r2-124566223954` (attempt 1): launch_error
- `candidate_155-r2-1bd642898c4f` (attempt 1): launch_error
- `candidate_155-r2-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r2-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_155-r2-fa4087c369be` (attempt 1): launch_error
- `candidate_155-r3-124566223954` (attempt 1): launch_error
- `candidate_155-r3-1bd642898c4f` (attempt 1): infrastructure_error
- `candidate_155-r3-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r3-ac9c93d7ccf3` (attempt 1): launch_error
- `candidate_155-r3-fa4087c369be` (attempt 1): launch_error
- `candidate_155-r4-124566223954` (attempt 1): launch_error
- `candidate_155-r4-1bd642898c4f` (attempt 1): launch_error
- `candidate_155-r4-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r4-fa4087c369be` (attempt 1): launch_error
- `candidate_155-r5-1bd642898c4f` (attempt 1): launch_error
- `candidate_155-r5-7b00206d58ae` (attempt 1): launch_error
- `candidate_155-r5-fa4087c369be` (attempt 1): launch_error
- `neutral_a-r1-124566223954` (attempt 1): launch_error
- `neutral_a-r1-1bd642898c4f` (attempt 1): launch_error
- `neutral_a-r1-7b00206d58ae` (attempt 1): launch_error
- `neutral_a-r1-ac9c93d7ccf3` (attempt 1): launch_error
- `neutral_a-r1-fa4087c369be` (attempt 1): launch_error
- `neutral_a-r2-124566223954` (attempt 1): launch_error
- `neutral_a-r2-7b00206d58ae` (attempt 1): launch_error
- `neutral_a-r3-124566223954` (attempt 1): launch_error
- `neutral_a-r3-1bd642898c4f` (attempt 1): launch_error
- `neutral_a-r3-7b00206d58ae` (attempt 1): infrastructure_error
- `neutral_a-r4-7b00206d58ae` (attempt 1): launch_error
- `neutral_a-r4-ac9c93d7ccf3` (attempt 1): launch_error
- `neutral_a-r4-fa4087c369be` (attempt 1): launch_error
- `neutral_a-r5-1bd642898c4f` (attempt 1): launch_error
- `neutral_a-r5-7b00206d58ae` (attempt 1): launch_error
- `neutral_a-r5-ac9c93d7ccf3` (attempt 1): launch_error

Total cost $0.9900 (provider-reported where given, otherwise tokens at list price) over 2012 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
