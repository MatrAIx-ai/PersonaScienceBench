# Persona pilot: discoverybench-neutral-b

Benchmark **discoverybench**, primary metric `final_score` (native, 0–100 here). 25/25 planned episodes finished; statuses {'scored': 25}. Code a38170f5bd4064a8e3b81163756538312798bd43; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| neutral | neutral_b | 5 | 24.2 | – | – |

Persona-off run-to-run SD (mean over 0 tasks with repeats): –. A persona delta smaller than this is indistinguishable from ordinary variation.

## By task

| Task | Domain | neutral_b |
|---|---|---:|
| `test/introduction_pathways_non-native_plants/metadata_0.json/0/0` | biology | 52.0 |
| `test/introduction_pathways_non-native_plants/metadata_2.json/0/0` | biology | 21.3 |
| `test/nls_incarceration/metadata_11.json/0/0` | sociology | 22.9 |
| `test/nls_raw/metadata_7.json/0/0` | sociology | 11.3 |
| `train/immigration_offshoring_effect_on_employment/metadata_0.json/0/1` | economics | 13.3 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| biology | neutral | 10 | 36.7 |
| economics | neutral | 5 | 13.3 |
| sociology | neutral | 10 | 17.1 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| neutral | 25 | 2.24 | 0.00 | 1868 | 14.2 | 74,768 | 0.0050 |

## Failures and retries

None.

Total cost $0.1253 (provider-reported where given, otherwise tokens at list price) over 355 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
