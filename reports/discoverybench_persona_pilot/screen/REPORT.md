# Persona pilot: discoverybench-screen

Benchmark **discoverybench**, primary metric `final_score` (native, 0–100 here). 24/24 planned episodes finished; statuses {'scored': 23, 'error': 1}. Code f9dc90dc9cb6d44d1996d7729f424ba3c6e6d3f9; models gpt-6-luna.

Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 (full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive pilot results, not significance tests.

## By condition and arm

| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |
|---|---|---:|---:|---:|---:|
| persona_off | persona_off | 12 | 11.4 | – | – |

Persona-off run-to-run SD (mean over 11 tasks with repeats): 14.3 pp. A persona delta smaller than this is indistinguishable from ordinary variation.

## By task

| Task | Domain | persona_off |
|---|---|---:|
| `test/introduction_pathways_non-native_plants/metadata_0.json/0/0` | biology | 40.0 |
| `train/evolution_freshwater_fish/metadata_3.json/0/1` | biology | 0.0 |
| `test/introduction_pathways_non-native_plants/metadata_2.json/0/0` | biology | 50.0 |
| `test/archaeology/metadata_29.json/0/0` | humanities | 0.0 |
| `test/archaeology/metadata_35.json/0/0` | humanities | 0.0 |
| `test/archaeology/metadata_18.json/0/0` | humanities | 0.0 |
| `test/nls_incarceration/metadata_11.json/0/0` | sociology | 14.3 |
| `test/nls_raw/metadata_7.json/0/0` | sociology | 7.1 |
| `test/nls_ses/metadata_6.json/0/0` | sociology | 0.0 |
| `test/worldbank_education_gdp_indicators/metadata_2.json/0/0` | economics | 0.0 |
| `train/immigration_offshoring_effect_on_employment/metadata_0.json/0/1` | economics | 25.0 |
| `test/worldbank_education_gdp/metadata_3.json/0/0` | economics | 0.0 |

## By domain and condition

| Domain | Condition | Episodes | Mean score |
|---|---|---:|---:|
| biology | persona_off | 6 | 30.0 |
| economics | persona_off | 5 | 5.0 |
| humanities | persona_off | 6 | 0.0 |
| sociology | persona_off | 6 | 7.1 |

## Interaction behavior (means per episode)

| Condition | Episodes | Handoffs | Revision requests | Researcher chars | API calls | Tokens | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| persona_off | 24 | 2.12 | 0.00 | 2072 | 15.9 | 121,839 | 0.0074 |

## Failures and retries

- `persona_off-r2-f132fde672bc` (attempt 1): error

Total cost $0.1769 (provider-reported where given, otherwise tokens at list price) over 382 API calls. Raw records: `episodes/`; per-episode rows: `results.csv`.
