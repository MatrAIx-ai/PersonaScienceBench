# Five-case Luna baseline

Updated 2026-09-23T21:49:47.762342+00:00. 25/25 cases have final run records.

All model roles use `openai/gpt-6-luna`, reasoning effort `none`. The simulator
is enabled with approved study knowledge and no persona styling. Native
programmatic graders are retained for ScienceAgentBench and Terminal.

| Benchmark | Finished | Graded | Policy zeros | Scored | Mean on scored cases |
| --- | ---: | ---: | ---: | ---: | ---: |
| DiscoveryBench | 5/5 | 5/5 | 0 | 5/5 | 0.2556 |
| BixBench | 5/5 | 5/5 | 0 | 5/5 | 0.6000 |
| ScienceAgentBench | 5/5 | 5/5 | 0 | 5/5 | 0.4000 |
| EXP-Bench | 5/5 | 5/5 | 0 | 5/5 | 63.7333 |
| Terminal-Bench-Science | 5/5 | 2/5 | 3 | 5/5 | 0.0000 |

EXP-Bench reports reference coverage on a 0–100 scale for design-only submissions.
Other scores are on a 0–1 scale and retain benchmark-specific meaning.
Terminal no-submission outcomes count as false (`reward=0`) under the explicit
`terminal-missing-submission-false-v1` policy. Their `missing_submission` status
is retained. Policy zeros count as scored, not native graded; infrastructure
errors remain unscored. Historical raw attempts are unchanged.
There is no cross-benchmark average.

| Benchmark | Task | Status | Score | Score source | Researcher questions |
| --- | --- | --- | ---: | --- | ---: |
| EXP-Bench | `iclr2024/18447/7` | completed | 100.0000 | benchmark_evaluator | 5 |
| EXP-Bench | `iclr2024/18865/4` | completed | 100.0000 | benchmark_evaluator | 4 |
| EXP-Bench | `neurips2024/94328/5` | completed | 18.6667 | benchmark_evaluator | 0 |
| EXP-Bench | `neurips2024/94391/7` | completed | 100.0000 | benchmark_evaluator | 6 |
| EXP-Bench | `neurips2024/97649/0` | completed | 0.0000 | benchmark_evaluator | 0 |
| BixBench | `bix-10-q2` | scored | 1.0000 | benchmark_evaluator | 0 |
| BixBench | `bix-13-q1` | scored | 0.0000 | benchmark_evaluator | 0 |
| BixBench | `bix-51-q1` | scored | 1.0000 | benchmark_evaluator | 0 |
| BixBench | `bix-54-q1` | scored | 0.0000 | benchmark_evaluator | 0 |
| BixBench | `bix-8-q2` | scored | 1.0000 | benchmark_evaluator | 0 |
| DiscoveryBench | `test/meta_regression/metadata_1.json/0/0` | scored | 0.5000 | benchmark_evaluator | 0 |
| DiscoveryBench | `test/nls_incarceration/metadata_1.json/0/0` | scored | 0.0000 | benchmark_evaluator | 0 |
| DiscoveryBench | `test/nls_ses/metadata_1.json/0/0` | scored | 0.4444 | benchmark_evaluator | 0 |
| DiscoveryBench | `test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | scored | 0.3333 | benchmark_evaluator | 0 |
| DiscoveryBench | `test/worldbank_education_gdp_indicators/metadata_1.json/0/0` | scored | 0.0000 | benchmark_evaluator | 0 |
| ScienceAgentBench | `22` | scored | 0.0000 | benchmark_evaluator | 0 |
| ScienceAgentBench | `45` | scored | 1.0000 | benchmark_evaluator | 0 |
| ScienceAgentBench | `67` | scored | 0.0000 | benchmark_evaluator | 0 |
| ScienceAgentBench | `87` | scored | 0.0000 | benchmark_evaluator | 0 |
| ScienceAgentBench | `92` | scored | 1.0000 | benchmark_evaluator | 0 |
| Terminal-Bench-Science | `earth-sciences/geosciences/hbv-calibration-1` | missing_submission | 0.0000 | missing_submission_policy | 0 |
| Terminal-Bench-Science | `mathematical-sciences/applied-mathematics/ode-law-discovery` | missing_submission | 0.0000 | missing_submission_policy | 0 |
| Terminal-Bench-Science | `mathematical-sciences/applied-mathematics/traffic-flux-inversion` | scored | 0.0000 | native_verifier | 0 |
| Terminal-Bench-Science | `mathematical-sciences/statistics/symbolic-regression` | scored | 0.0000 | native_verifier | 0 |
| Terminal-Bench-Science | `physical-sciences/physics/spin-glass-groundstate` | missing_submission | 0.0000 | missing_submission_policy | 0 |

## Execution and limitations

- Cases were scheduled concurrently: 15 Python cases, five EXP-Bench cases, and five Terminal cases. Batch launches were staggered as prerequisites became ready.
- Each actor had 20 OpenHands iterations and up to six researcher questions. Terminal retains its native wall-time ceiling, with an additional 20-iteration limit and disabled actor network; these are environment adaptations.
- The initial Python batch failed sandbox startup before actor inference because a Debian standard-library directory was absent. Its records remain under `runs/luna-no-persona-five/python/`; the corrected batch is under `python-runtime-fixed/`.
- SAB 87 exhausted its first actor budget because the initial runtime lacked a NetCDF reader. A separate environment supplied the missing dependency, and only that case was rerun under `sab-netcdf-retry/`. Both attempts and their costs are retained.
- Harbor grading first lacked Docker Compose, then its network sidecar failed because the host kernel lacks nftables FIB support. Saved submissions are graded in separate Docker containers with `--network none` using unchanged native images and verifier scripts. Original errors and intermediate attempts are retained; replacement grades are under `native-docker/evaluation.json`.
- Current case selection is a small, manually reviewed sample, not a random or representative benchmark sample. These runs do not measure a persona effect.
- No additional test suite was run after the user requested validation through actual case execution.

Recorded model charges, including retained infrastructure-affected actor attempts: $0.097774.

Per-case run paths and machine-readable scores are in `reports/luna_no_persona_five.json`.
Private transcripts, references, and submissions remain in the ignored `runs/` tree.
Reproduction and configurations: [Luna baseline](../docs/luna_baseline.md).
