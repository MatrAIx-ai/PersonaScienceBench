# Luna: fixed computer-science novice persona

Updated 2026-09-23T21:49:50.396562+00:00. Persona condition: 25/25 cases have final records.

The same 25 task IDs, source data, approved study facts, model IDs, reasoning effort,
20 actor iterations, and six-question limit are used in both conditions.
The added persona has computer-science domain knowledge, statistics, and coding
all set to novice. Other persona attributes retain the shared neutral defaults.

| Benchmark | Baseline scored | Baseline mean | Persona finished | Persona scored | Persona mean | Paired mean delta (n) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DiscoveryBench | 5/5 | 0.2556 | 5/5 | 5/5 | 0.2500 | -0.0056 (5) |
| BixBench | 5/5 | 0.6000 | 5/5 | 5/5 | 0.6000 | 0.0000 (5) |
| ScienceAgentBench | 5/5 | 0.4000 | 5/5 | 5/5 | 0.4000 | 0.0000 (5) |
| EXP-Bench | 5/5 | 63.7333 | 5/5 | 5/5 | 67.6000 | 3.8667 (5) |
| Terminal-Bench-Science | 5/5 | 0.0000 | 5/5 | 4/5 | 0.0000 | 0.0000 (4) |

EXP-Bench scores are reference coverage out of 100; other scores are out of 1.
Means use scored cases; denominators can differ. Paired deltas include only task IDs
scored in both conditions. Terminal no-submission outcomes count as false (`reward=0`)
under `terminal-missing-submission-false-v1`, with `missing_submission` retained.
These policy zeros are separate from native grades. Infrastructure errors remain
unscored, and historical raw attempts are unchanged.

| Benchmark | Baseline graded | Baseline policy zeros | Persona graded | Persona policy zeros | Paired graded cases |
| --- | ---: | ---: | ---: | ---: | ---: |
| DiscoveryBench | 5/5 | 0 | 5/5 | 0 | 5 |
| BixBench | 5/5 | 0 | 5/5 | 0 | 5 |
| ScienceAgentBench | 5/5 | 0 | 5/5 | 0 | 5 |
| EXP-Bench | 5/5 | 0 | 5/5 | 0 | 5 |
| Terminal-Bench-Science | 2/5 | 3 | 2/5 | 2 | 1 |

For Terminal, graded means a native verifier returned a reward. Other benchmarks
use their configured benchmark evaluator.

| Benchmark | Task | Baseline | Persona | Persona status | Persona score source | Researcher questions (baseline → persona) |
| --- | --- | ---: | ---: | --- | --- | ---: |
| BixBench | `bix-10-q2` | 1.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| BixBench | `bix-51-q1` | 1.0000 | 1.0000 | scored | benchmark_evaluator | 0 → 0 |
| BixBench | `bix-54-q1` | 0.0000 | 1.0000 | scored | benchmark_evaluator | 0 → 0 |
| BixBench | `bix-8-q2` | 1.0000 | 1.0000 | scored | benchmark_evaluator | 0 → 0 |
| DiscoveryBench | `test/meta_regression/metadata_1.json/0/0` | 0.5000 | 0.2500 | scored | benchmark_evaluator | 0 → 0 |
| DiscoveryBench | `test/nls_incarceration/metadata_1.json/0/0` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| DiscoveryBench | `test/nls_ses/metadata_1.json/0/0` | 0.4444 | 1.0000 | scored | benchmark_evaluator | 0 → 0 |
| DiscoveryBench | `test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | 0.3333 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| DiscoveryBench | `test/worldbank_education_gdp_indicators/metadata_1.json/0/0` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| ScienceAgentBench | `22` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| ScienceAgentBench | `45` | 1.0000 | 1.0000 | scored | benchmark_evaluator | 0 → 1 |
| ScienceAgentBench | `67` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 1 |
| ScienceAgentBench | `87` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| ScienceAgentBench | `92` | 1.0000 | 1.0000 | scored | benchmark_evaluator | 0 → 0 |
| BixBench | `bix-13-q1` | 0.0000 | 0.0000 | scored | benchmark_evaluator | 0 → 0 |
| EXP-Bench | `iclr2024/18447/7` | 100.0000 | 61.3333 | completed | benchmark_evaluator | 5 → 0 |
| EXP-Bench | `neurips2024/94328/5` | 18.6667 | 100.0000 | completed | benchmark_evaluator | 0 → 5 |
| EXP-Bench | `neurips2024/94391/7` | 100.0000 | 26.6667 | completed | benchmark_evaluator | 6 → 0 |
| EXP-Bench | `neurips2024/97649/0` | 0.0000 | 50.0000 | completed | benchmark_evaluator | 0 → 0 |
| EXP-Bench | `iclr2024/18865/4` | 100.0000 | 100.0000 | completed | benchmark_evaluator | 4 → 4 |
| Terminal-Bench-Science | `earth-sciences/geosciences/hbv-calibration-1` | 0.0000 | 0.0000 | missing_submission | missing_submission_policy | 0 → 0 |
| Terminal-Bench-Science | `mathematical-sciences/applied-mathematics/ode-law-discovery` | 0.0000 | 0.0000 | scored | native_verifier | 0 → 0 |
| Terminal-Bench-Science | `mathematical-sciences/applied-mathematics/traffic-flux-inversion` | 0.0000 | — | infrastructure_error | unscored | 0 → 0 |
| Terminal-Bench-Science | `mathematical-sciences/statistics/symbolic-regression` | 0.0000 | 0.0000 | scored | native_verifier | 0 → 0 |
| Terminal-Bench-Science | `physical-sciences/physics/spin-glass-groundstate` | 0.0000 | 0.0000 | missing_submission | missing_submission_policy | 0 → 0 |

## Interpretation and controls

- The original 25 cases were launched concurrently. After host interruption, seven unfinished actors were restarted concurrently and two saved SAB submissions were graded without rerunning their actors. Completed cases were retained; replacement results are merged by task ID.
- Recorded charges include logged Python/Terminal attempts and completed EXP-Bench attempts; interrupted EXP-Bench charges may be missing.
- No persona identity is exposed directly to the actor. Its effect can occur through simulator replies; cases where the actor never asks a question do not exercise that channel.
- The persona adds the shared identity prompt with novice expertise and neutral defaults. This is a fixed-profile comparison against no persona, not an isolated causal estimate for each expertise attribute.
- EXP-Bench retains its extractive disclosure rule: persona conditions relevance/fact selection, while published replies remain approved fact text. The other shared adapters use their existing grounded-reply policy.
- SAB 87 uses the same expanded NetCDF environment as its final baseline attempt; the other Python cases retain the original scientific environment.
- Terminal uses the same native actor images and the working separate Docker network-none grader from the final baseline. Native scientific grading scripts are unchanged.
- One run per task and condition does not establish a reliable persona effect. Model sampling, judge variability, and concurrent runtime contention remain possible explanations of differences.
- No additional unit-test suite was run; validation uses the requested live cases.

Recorded persona model charges: $0.103371; retained baseline charges: $0.097774.

Configs: `configs/luna-cs-novice-five.json` and `configs/expbench/luna-cs-novice.toml`.
Full per-case paths are in `reports/luna_cs_novice_comparison.json`.
