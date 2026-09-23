# Experiment-design pilot results

All five selected tasks completed: the OpenHands actor consulted a researcher
simulator, submitted a structured experiment design, and stopped. No experiment
code was written or executed. The full local dataset contains 461 tasks; only
the five curated pilot cards were run.

Actor and researcher used `anthropic/claude-sonnet-5`; the judge used
`openai/o3-mini`, through OpenRouter. Runs began on September 22, 2026 UTC.
The actor had a maximum of 20 steps and six researcher questions per task.

## Scores and interaction counts

The final scores use `exp-bench-variable-coverage-design-only-v2`. They are
single LLM judgments against the hidden constant, independent, and dependent
variable reference, interpreted with the approved researcher facts. They are
not measured experiment performance or the original paper's full-task scores.

| Task | Initial score (v1) | Final score (v2) | Actor API calls | Researcher questions | API cost including both grades |
| --- | ---: | ---: | ---: | ---: | ---: |
| JaxMARL | 100 | 95 | 5 | 6 | $0.182134 |
| QuaRot | 100 | 100 | 5 | 5 | $0.133332 |
| CycleNet | 95 | 100 | 5 | 5 | $0.170289 |
| MogaNet | 100 | 100 | 6 | 6 | $0.202661 |
| SineNet | 100 | 100 | 6 | 6 | $0.161001 |

Final mean: **99/100**, completion: **5/5**. Actor API calls are model turns;
a turn can contain multiple tool calls. The actor need not use all 20 steps.

JaxMARL's final judge deducted five points because the design emphasizes
wall-clock time at a fixed environment-step budget. The reference emphasizes
time to a defined convergence criterion; the design includes time-to-threshold
only as a secondary measure. The initial judge accepted that alternative.

## Why there are two grading versions

The initial CycleNet grade questioned the actor's RevIN configuration, although
that configuration was explicitly provided in the approved researcher facts.
The initial judge could not see those facts. Version 2 supplies the approved
researcher context alongside the hidden reference and asks the judge to use it
to resolve source configuration details and unspecified quantities. The three
variable groups remain the scoring basis.

All five saved designs were regraded once, unchanged. Both versions are retained;
the final results do not select the higher score for each task. Because both
the prompt/context and the model sample changed, differences cannot be
attributed solely to the context correction. Judge repeatability has not been
measured.

## Costs and limits

Costs below sum OpenRouter's reported `usage.cost` over successful API responses,
including the response that was truncated in the failed attempt. They exclude
payment fees and hosting, and are not an independently reconciled account bill.

| Invocation | Reported API cost |
| --- | ---: |
| Truncated first authenticated attempt | $0.118050 |
| Completed five-task run, including initial grading | $0.813552 |
| Regrading all five saved designs with v2 | $0.035864 |
| **Total** | **$0.967466** |

The failed authenticated attempt used a 4,096-token actor output allowance and
stopped on a truncated response. The completed run used 12,288 actor output
tokens. The earlier HTTP 401 attempt has no reported inference cost; its old
ledger retains a $0.052752 reservation, which is excluded from spending above.
The current implementation checks authentication before inference and clears
reservations on explicit authentication rejection.

Current configuration has **no run or task dollar caps**, as requested. It
retains 20 actor steps, six researcher questions, and output-token limits.
The completed actor run had already started with the previous $2/task and
$20/run caps; neither cap was reached. Its original manifest is preserved.
The v2 regrading used the uncapped configuration.

## Validation and interpretation

The implementation passed 25 tests, covering the real OpenHands loop with mock
inference, role/history separation, reference isolation, context access,
submission stopping, limits, accounting, API failures, and saved-design grading.
Final artifact checks validate all five designs and grades, confirm unchanged
design hashes for regrading, and check that no further actor request followed
final submission.

Researcher transcripts acknowledge missing facts instead of supplying numerical
outcomes or a full reference design. Fact-ID validation checks citations to the
approved fact bank; it does not establish sentence-level factual support.
The pilot cards were reviewed against the released task annotations, not
independently audited against every source paper.

These scores demonstrate that the pipeline works, but do not establish that the
rubric distinguishes strong and weak scientific designs. Four ceiling scores,
discretionary deductions, and unverified design assumptions are material
limitations. For example, the judge accepted MogaNet's proposed alternative
interaction estimator although the released annotation does not define J(m).
That judgment does not establish equivalence to the original paper's metric.
JaxMARL's provisional map roster and SineNet's dataset and training assumptions
also need scientific review before execution.

Before a larger evaluation, useful validation would include expert review of
designs and references, deliberately incomplete or incorrect design controls,
and repeated grading to measure variability. None of those additional runs has
been performed in this pilot.

## Artifacts

- [Completed actor run and original grades](../../runs/expbench/pilot-live-20260922-attempt3/summary.json)
- [Final v2 grades](../../runs/expbench/pilot-grades-v2-20260922/summary.json)
- [Completed-run manifest](../../runs/expbench/pilot-live-20260922-attempt3/manifest.json)
- [Regrading manifest and design hashes](../../runs/expbench/pilot-grades-v2-20260922/manifest.json)

| Task ID | Submitted design | Final judge explanation |
| --- | --- | --- |
| `neurips2024/97649/0` | [JaxMARL](../../runs/expbench/pilot-live-20260922-attempt3/neurips2024__97649__0/design.json) | [95/100](../../runs/expbench/pilot-grades-v2-20260922/neurips2024__97649__0/grade.json) |
| `neurips2024/94328/5` | [QuaRot](../../runs/expbench/pilot-live-20260922-attempt3/neurips2024__94328__5/design.json) | [100/100](../../runs/expbench/pilot-grades-v2-20260922/neurips2024__94328__5/grade.json) |
| `neurips2024/94391/7` | [CycleNet](../../runs/expbench/pilot-live-20260922-attempt3/neurips2024__94391__7/design.json) | [100/100](../../runs/expbench/pilot-grades-v2-20260922/neurips2024__94391__7/grade.json) |
| `iclr2024/18447/7` | [MogaNet](../../runs/expbench/pilot-live-20260922-attempt3/iclr2024__18447__7/design.json) | [100/100](../../runs/expbench/pilot-grades-v2-20260922/iclr2024__18447__7/grade.json) |
| `iclr2024/18865/4` | [SineNet](../../runs/expbench/pilot-live-20260922-attempt3/iclr2024__18865__4/design.json) | [100/100](../../runs/expbench/pilot-grades-v2-20260922/iclr2024__18865__4/grade.json) |

The actor run directories also contain conversation histories, OpenHands events,
API response and usage records, public task context, and private task snapshots.
These artifacts include hidden references and must not become actor inputs.
