# Persona pilot: openproblems-screen

Benchmark **openproblems_denoising**, primary metric `score_clipped` (native, 0–100 here). 12/12 planned episodes finished; statuses {'scored': 12}. Code 45dde7d4a63e59ac74577d8a6a1a3cf2776a5fa5; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona_off | persona_off | 6 | 6.7 | – | – |

Persona-off run-to-run SD (mean over 6 tasks with repeats): 5.5 pp. A persona delta smaller than this is indistinguishable from ordinary variation.

## By task

| Task | Domain | persona_off |
|---|---|---:|
| `openproblems_v1/tenx_1k_pbmc` | openproblems_v1 | 5.1 |
| `openproblems_v1/mouse_blood_olsson_labelled` | openproblems_v1 | 1.3 |
| `openproblems_v1/pancreas` | openproblems_v1 | 19.8 |
| `openproblems_v1/tenx_5k_pbmc` | openproblems_v1 | 9.7 |
| `openproblems_v1/immune_cells` | openproblems_v1 | 3.7 |
| `openproblems_v1/cengen` | openproblems_v1 | 0.7 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| openproblems_v1 | persona_off | 12 | 6.7 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| persona_off | 12 | 2.50 | 0.25 | 2272 | 1387 | 23.4 | 14.8 | 101,146 | 0.0068 |

## Failures and retries

None.

Total cost $0.0965 (provider-reported where given, otherwise tokens at list price) over 212 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
