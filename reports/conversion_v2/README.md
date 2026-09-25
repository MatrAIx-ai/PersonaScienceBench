# Automated conversion revision: two cases per benchmark

Persona off; actor, researcher and LLM judges use GPT-6 Luna. Native programmatic graders remain programmatic. Independent cases ran concurrently. These are integration trials, not a controlled estimate of persona or collaboration effects.

Full population: [conversion counts and readiness](conversion_summary.md). Conversion rules: [per-benchmark revision](../../docs/design/conversion_revision_v2.md).

| Case | Status | Native outcome | Exchanges / handoffs | Local trace (not in Git) |
|---|---|---|---:|---|
| `asibench:materials.relaxation_mode_recovery` | scored | Score: 14.62/100 | 3 | `runs/conversion-v2-recovery-asi-typed-20260925/asibench_materials.relaxation_mode_recovery-ad80481c261e/trace.md` |
| `asibench:math.nnls_modulus_deblur` | scored | Score: 0.00/100 | 3 | `runs/conversion-v2-two-asi-ready-20260925/asibench_math.nnls_modulus_deblur-bdb8b6dd4a8c/trace.md` |
| `bixbench:bix-51-q2` | scored | Correct: 1/1 | 2 | `runs/conversion-v2-two-python-20260925/bixbench_bix-51-q2-a165bfd122b4/trace.md` |
| `bixbench:bix-54-q2` | scored | Correct: 1/1 | 3 | `runs/conversion-v2-two-python-20260925/bixbench_bix-54-q2-98d4739139b6/trace.md` |
| `discoverybench:test/nls_incarceration/metadata_1.json/0/0` | scored | Score: 0.000/1 | 2 | `runs/conversion-v2-recovery-discovery-turnfix-20260925/discoverybench_test_nls_incarceration_metadata_1.json_0_0-aa7f4fde34ab/trace.md` |
| `discoverybench:test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | scored | Score: 0.000/1 | 2 | `runs/conversion-v2-two-python-20260925/discoverybench_test_requirements_engineering_for_ML_enabled_systems_metadata_1.json_0_0-062fae8225b5/trace.md` |
| `expbench:neurips2024/94328/5` | completed | Coverage: 79.33/100; gated: 79.33 | 2 | `runs/conversion-v2-two-exp-fixed-20260925/neurips2024__94328__5/trace.md` |
| `expbench:neurips2024/97649/0` | completed | Coverage: 30.00/100; gated: 30.00 | 3 | `runs/conversion-v2-two-exp-fixed-20260925/neurips2024__97649__0/trace.md` |
| `sciconvbench:fluids/disambiguation/case_001` | scored | FRR: 1; CGRR: 1 | 4 | `runs/conversion-v2-two-sciconv-ready-20260925/sciconvbench_fluids_disambiguation_case_001-861d13d6ddfb/trace.md` |
| `sciconvbench:pde/inconsistency/case_001` | scored | FRR: 1; CGRR: 1 | 1 | `runs/conversion-v2-two-sciconv-ready-20260925/sciconvbench_pde_inconsistency_case_001-13f30a39d006/trace.md` |
| `scienceagentbench:verified:22` | missing_submission | No sealed submission | 3 | `runs/conversion-v2-two-python-20260925/scienceagentbench_verified_22-ec9721cd2158/trace.md` |
| `scienceagentbench:verified:45` | scored | Success: 1/1 | 2 | `runs/conversion-v2-two-python-20260925/scienceagentbench_verified_45-f3563c8e60fe/trace.md` |
| `terminal_bench_science:mathematical-sciences/applied-mathematics/ode-law-discovery` | scored | Reward: 0/1 | 3 | `runs/conversion-v2-two-terminal-20260925/terminal_bench_science_mathematical-sciences_applied-mathematics_ode-law-discovery-5cf81479ba65/trace.md` |
| `terminal_bench_science:mathematical-sciences/statistics/symbolic-regression` | scored | Reward: 1/1 | 2 | `runs/conversion-v2-recovery-terminal-turnfix-20260925/terminal_bench_science_mathematical-sciences_statistics_symbolic-regression-58c7f2e65d03/trace.md` |

## Interpretation

- Execution/design tracks count agent-to-researcher handoffs, including required approach and result reviews. SciConvBench counts clarification question/answer pairs. These counts are not interchangeable measures of useful collaboration.
- EXP-Bench remains design-only. ASI scores are local seed31415 scores for a B3-plus-B2-guidance adaptation, not official autonomous B3 scores. SciConvBench evaluates specifications and dialogue, not solver execution.
- ScienceAgentBench instance 22 reached researcher-selected stopping after review but had no sealed submission; it remains unscored and is not replaced by an easier case.
- Missing submissions remain missing unless the benchmark has a declared penalty policy. Infrastructure failures are separately recorded; scientific zeros are retained.
- Early researcher responses sometimes generated multiple imagined decisions or were truncated. Recovery requests introduced an explicit current-turn boundary, then a typed single-decision tool. Exact request versions and token caps are recorded per attempt; successful runs were not repeated to homogenize configuration.
- EXP’s first attempts failed before actor calls because repeated fact topics violated the legacy interface. Unique source-span topics fixed preparation.
- SciConvBench retains the native paper metric calculations and silent-resolution correction. Its clarification ratios use the native case-script count definitions; the paper aggregator ratios are also retained because its recall can exceed one.

## All attempts and recoveries

| Case | Batch | Status | Local trace (not in Git) |
|---|---|---|---|
| `asibench:materials.relaxation_mode_recovery` | `conversion-v2-recovery-asi-turnfix-20260925` | infrastructure_error | `runs/conversion-v2-recovery-asi-turnfix-20260925/asibench_materials.relaxation_mode_recovery-ad80481c261e/trace.md` |
| `asibench:materials.relaxation_mode_recovery` | `conversion-v2-recovery-asi-typed-20260925` | scored | `runs/conversion-v2-recovery-asi-typed-20260925/asibench_materials.relaxation_mode_recovery-ad80481c261e/trace.md` |
| `discoverybench:test/nls_incarceration/metadata_1.json/0/0` | `conversion-v2-recovery-discovery-20260925` | infrastructure_error | `runs/conversion-v2-recovery-discovery-20260925/discoverybench_test_nls_incarceration_metadata_1.json_0_0-aa7f4fde34ab/trace.md` |
| `discoverybench:test/nls_incarceration/metadata_1.json/0/0` | `conversion-v2-recovery-discovery-turnfix-20260925` | scored | `runs/conversion-v2-recovery-discovery-turnfix-20260925/discoverybench_test_nls_incarceration_metadata_1.json_0_0-aa7f4fde34ab/trace.md` |
| `terminal_bench_science:mathematical-sciences/statistics/symbolic-regression` | `conversion-v2-recovery-terminal-20260925` | infrastructure_error | `runs/conversion-v2-recovery-terminal-20260925/terminal_bench_science_mathematical-sciences_statistics_symbolic-regression-58c7f2e65d03/trace.md` |
| `terminal_bench_science:mathematical-sciences/statistics/symbolic-regression` | `conversion-v2-recovery-terminal-turnfix-20260925` | scored | `runs/conversion-v2-recovery-terminal-turnfix-20260925/terminal_bench_science_mathematical-sciences_statistics_symbolic-regression-58c7f2e65d03/trace.md` |
| `asibench:materials.relaxation_mode_recovery` | `conversion-v2-two-asi-ready-20260925` | infrastructure_error | `runs/conversion-v2-two-asi-ready-20260925/asibench_materials.relaxation_mode_recovery-ad80481c261e/trace.md` |
| `asibench:math.nnls_modulus_deblur` | `conversion-v2-two-asi-ready-20260925` | scored | `runs/conversion-v2-two-asi-ready-20260925/asibench_math.nnls_modulus_deblur-bdb8b6dd4a8c/trace.md` |
| `expbench:neurips2024/94328/5` | `conversion-v2-two-exp-20260925` | runtime_error | `runs/conversion-v2-two-exp-20260925/neurips2024__94328__5/trace.md` |
| `expbench:neurips2024/97649/0` | `conversion-v2-two-exp-20260925` | runtime_error | `runs/conversion-v2-two-exp-20260925/neurips2024__97649__0/trace.md` |
| `expbench:neurips2024/94328/5` | `conversion-v2-two-exp-fixed-20260925` | completed | `runs/conversion-v2-two-exp-fixed-20260925/neurips2024__94328__5/trace.md` |
| `expbench:neurips2024/97649/0` | `conversion-v2-two-exp-fixed-20260925` | completed | `runs/conversion-v2-two-exp-fixed-20260925/neurips2024__97649__0/trace.md` |
| `bixbench:bix-51-q2` | `conversion-v2-two-python-20260925` | scored | `runs/conversion-v2-two-python-20260925/bixbench_bix-51-q2-a165bfd122b4/trace.md` |
| `bixbench:bix-54-q2` | `conversion-v2-two-python-20260925` | scored | `runs/conversion-v2-two-python-20260925/bixbench_bix-54-q2-98d4739139b6/trace.md` |
| `discoverybench:test/nls_incarceration/metadata_1.json/0/0` | `conversion-v2-two-python-20260925` | infrastructure_error | `runs/conversion-v2-two-python-20260925/discoverybench_test_nls_incarceration_metadata_1.json_0_0-aa7f4fde34ab/trace.md` |
| `discoverybench:test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | `conversion-v2-two-python-20260925` | scored | `runs/conversion-v2-two-python-20260925/discoverybench_test_requirements_engineering_for_ML_enabled_systems_metadata_1.json_0_0-062fae8225b5/trace.md` |
| `scienceagentbench:verified:22` | `conversion-v2-two-python-20260925` | missing_submission | `runs/conversion-v2-two-python-20260925/scienceagentbench_verified_22-ec9721cd2158/trace.md` |
| `scienceagentbench:verified:45` | `conversion-v2-two-python-20260925` | scored | `runs/conversion-v2-two-python-20260925/scienceagentbench_verified_45-f3563c8e60fe/trace.md` |
| `sciconvbench:fluids/disambiguation/case_001` | `conversion-v2-two-sciconv-ready-20260925` | scored | `runs/conversion-v2-two-sciconv-ready-20260925/sciconvbench_fluids_disambiguation_case_001-861d13d6ddfb/trace.md` |
| `sciconvbench:pde/inconsistency/case_001` | `conversion-v2-two-sciconv-ready-20260925` | scored | `runs/conversion-v2-two-sciconv-ready-20260925/sciconvbench_pde_inconsistency_case_001-13f30a39d006/trace.md` |
| `terminal_bench_science:mathematical-sciences/applied-mathematics/ode-law-discovery` | `conversion-v2-two-terminal-20260925` | scored | `runs/conversion-v2-two-terminal-20260925/terminal_bench_science_mathematical-sciences_applied-mathematics_ode-law-discovery-5cf81479ba65/trace.md` |
| `terminal_bench_science:mathematical-sciences/statistics/symbolic-regression` | `conversion-v2-two-terminal-20260925` | infrastructure_error | `runs/conversion-v2-two-terminal-20260925/terminal_bench_science_mathematical-sciences_statistics_symbolic-regression-58c7f2e65d03/trace.md` |

Trace paths above are local locators under ignored `runs/`, not GitHub links. Full raw model calls, shared dialogue, tool activity, sealed submissions and grader outputs remain locally beside each readable trace. No additional benchmark cases were run as a separate test suite.
