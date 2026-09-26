# DiscoveryBench: Azure GPT-5.6 Sol persona pilot

Completed 16 executions across 2 distinct studies, four conditions, and 2 repetitions. 16 received native scores. Both frozen-input and arm-configuration integrity checks passed.

These are exploratory paired observations, not evidence of a general persona benefit. All three model roles used the recorded Azure deployment with reasoning effort `none`.

| Researcher condition | Mean native score | Paired change vs off | Scored / attempted | Wins / ties / losses |
| --- | ---: | ---: | ---: | --- |
| off | 0.5000 | 0.0000 | 4 / 4 | 0 / 4 / 0 |
| reference | 0.2500 | -0.2500 | 4 / 4 | 0 / 3 / 1 |
| statistics_low | 0.5000 | 0.0000 | 4 / 4 | 0 / 4 / 0 |
| statistics_high | 0.8333 | 0.3333 | 4 / 4 | 2 / 2 / 0 |

## By scientific study

| Study | Condition | Repetition scores | Mean |
| --- | --- | --- | ---: |
| nls_incarceration | off | 1.0000, 1.0000 | 1.0000 |
| nls_incarceration | reference | 0.0000, 1.0000 | 0.5000 |
| nls_incarceration | statistics_low | 1.0000, 1.0000 | 1.0000 |
| nls_incarceration | statistics_high | 1.0000, 1.0000 | 1.0000 |
| requirements_engineering_for_ML_enabled_systems | off | 0.0000, 0.0000 | 0.0000 |
| requirements_engineering_for_ML_enabled_systems | reference | 0.0000, 0.0000 | 0.0000 |
| requirements_engineering_for_ML_enabled_systems | statistics_low | 0.0000, 0.0000 | 0.0000 |
| requirements_engineering_for_ML_enabled_systems | statistics_high | 0.6667, 0.6667 | 0.6667 |

## What changed in the work

The high-statistical-expertise condition improved the engineering task in both
repetitions (0.6667 versus 0 for the matched controls). Its researcher feedback
requested a paired role comparison and interpretation of statistical significance;
the resulting analysis supplied that comparison. Across conditions the primary
role proportions were similar. This supports a narrow observation about analysis
coverage and reporting, rather than a claim that persona created new study facts.

The neutral reference profile's lower average needs particular caution. Its first
sociology submission reported the same direction of association as the successful
runs, but the native grader extracted different context scopes and rejected their
match, producing zero context recall. The zero is retained exactly as scored.
This is evidence of grading sensitivity, not a demonstrated reversal of the
scientific finding or proof that the neutral persona harmed the analysis.

All runs used one approach handoff and one result handoff, with three researcher
decisions including the initial request. The sample does not isolate persona
fidelity or quantify grader variability; these should be assessed before scaling.

## Design and limits

- Persona off retained the same simulator, facts, protocol, models, and budgets.
- Enabled profiles held 55 attributes, role, and domain fixed. Only statistical inference differed: medium, low, or high.
- Each persona score was paired with the same study and repetition of the off control. The three contrasts reuse that control and are correlated.
- Missing results remain unscored. Repetitions are not additional independent studies. No hypothesis tests or population-level confidence intervals are claimed.
- Native scores measure LLM-judged reference agreement; successful tool execution is separate evidence and does not independently verify the scientific analysis.
- GPT-5.6 Sol resolved model IDs, interaction counts, execution receipts, and usage tokens are in results.json. Dollar cost requires Azure billing data.

## Reproduction

Follow the [Azure pilot guide](../../docs/discoverybench_azure_pilot.md). The shared implementation and pinned sources are unchanged across the arms. 
Raw records are stored locally under `runs/discoverybench-azure-gpt56-20260926/`; private references, credentials, and raw traces are excluded from this report.

The run used uncommitted implementation files on the working branch. The private plan records their hashes, the base Git revision, runtime inputs, and the shuffled schedule.

## Validation record

The live run's input and arm hashes were unchanged from start to finish. Subsequent
code review corrected an actor-call summary field, the preflight-start status, and
Azure regrade provenance, and isolated Python imports during privileged namespace
setup; it did not rerun or replace any scientific submission or score. The raw run retains its actual execution-source hashes.

Initial implementation checks: **198 tests passed, 19 skipped** because unrelated external benchmark
assets were not acquired; repository link/secret-pattern checks and `git diff
--check` passed. The final namespace launcher passed both the isolation check and
a forced command-timeout check.

The PR scope was subsequently narrowed to keep the sudo namespace bootstrap as
a local host-specific helper for separate review. The pilot now uses the existing
`PERSONASCIENCEBENCH_BWRAP` override and records the selected launcher's hash.
This packaging change does not alter the retained experiment records or scores.

Current PR validation after narrowing the runtime scope: **199 tests passed,
19 skipped**; offline planning, the configured runtime check, repository checks,
and `git diff --check` also passed.
