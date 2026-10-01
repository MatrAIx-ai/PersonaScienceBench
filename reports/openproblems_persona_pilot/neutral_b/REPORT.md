# Persona pilot: openproblems-neutral-b

Benchmark **openproblems_denoising**, primary metric `score` (native, 0–100 here). 25/25 planned episodes finished; statuses {'scored': 25}. Code 80ffc1e5026f29c559daceba5e9cd16a53c12473; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| neutral | neutral_b | 5 | 0.5 | – | – |

Persona-off run-to-run SD (mean over 0 tasks with repeats): –. A persona delta smaller than this is indistinguishable from ordinary variation.

## By task

| Task | Domain | neutral_b |
|---|---|---:|
| `openproblems_v1/tenx_1k_pbmc` | openproblems_v1 | -0.1 |
| `openproblems_v1/mouse_blood_olsson_labelled` | openproblems_v1 | -7.1 |
| `openproblems_v1/pancreas` | openproblems_v1 | 10.1 |
| `openproblems_v1/tenx_5k_pbmc` | openproblems_v1 | 0.3 |
| `openproblems_v1/immune_cells` | openproblems_v1 | -0.4 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| openproblems_v1 | neutral | 25 | 0.5 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| neutral | 25 | 2.24 | 0.04 | 2004 | 1661 | 28.0 | 14.8 | 105,667 | 0.0067 |

## Failures and retries

- `neutral_b-r1-7b00206d58ae-retry2` (attempt 2): launch_error
- `neutral_b-r1-7b00206d58ae` (attempt 1): launch_error
- `neutral_b-r3-1bd642898c4f-retry2` (attempt 2): launch_error
- `neutral_b-r3-1bd642898c4f` (attempt 1): launch_error
- `neutral_b-r3-ac9c93d7ccf3` (attempt 1): launch_error
- `neutral_b-r4-ac9c93d7ccf3` (attempt 1): launch_error

Total cost $0.1686 (provider-reported where given, otherwise tokens at list price) over 370 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
