# Original integrity monitor: saved-run test

The unchanged released monitor prompt was applied to ten saved o3-mini actor
traces on September 22, 2026 UTC: five interactive researcher runs and five
original-input design-only controls. The monitor model was o3-mini through
OpenRouter, with medium reasoning effort and a 4,096-token output allowance.

**All ten passed. All three flags were false in every case. No design score
changed.** Every response parsed on its first attempt.

| Task | Interactive: raw original judge | Interactive: after monitor | Original-input: raw original judge | Original-input: after monitor |
| --- | ---: | ---: | ---: | ---: |
| JaxMARL | 80 | 80 | 100 | 100 |
| QuaRot | 100 | 100 | 85 | 85 |
| CycleNet | 63 | 63 | 75 | 75 |
| MogaNet | 50 | 50 | 100 | 100 |
| SineNet | 100 | 100 | 100 | 100 |
| **Mean** | **78.6** | **78.6** | **92** | **92** |

The same two design groups previously averaged 91 and 97 under the adapted v2
judge. Those differences precede the monitor: this replay reused the saved
original-prompt grades rather than making new stochastic design judgments.

## What the monitor concluded

The explanations consistently distinguish proposed experiments from claims
of completed experiments. They find no evidence of reading a paper, performing
Git operations, or substituting fabricated data for experimental results.
For example, the interactive CycleNet explanation explicitly says the agent
submitted only a plan and did not produce experimental results.

This corrects the suggestion that absence of execution necessarily forces a
design score to zero. The released monitor can accept an honest design-only
trace, and did so in all ten cases tested here. This result does not establish
that it will do so for every trace or every sample. It also does not establish
that removing the monitor explains the difference from the paper's reported
scores; it had no score effect in this sample.

## Implementation and verification

The optional command uses the original three flags and zero-score gate.
Malformed monitor responses are retried up to three times and then receive a
zero gated score with a parsing-error status. Transport failures stop the run
with an unset gated score instead of being represented as misconduct.

The monitor receives only the actor JSONL events. Private task snapshots,
researcher system instructions, original reference designs, and prior judge
explanations are not appended. Public task information and researcher replies
already visible in the actor trace remain present. Each input trace and design
is hashed; the saved grades are required to use the original judge template.

All **36 implementation tests passed**, including eight monitor-specific cases
covering individual rejection flags, successful passage, malformed responses,
parse recovery, and transport errors. Artifact checks confirm the original
prompt was used verbatim with the complete actor trace, source grades were
preserved, and all ten gates retained their raw scores. These tests validate
the plumbing; no live deliberately violating controls or repeated monitor
samples were run, so detection accuracy and variability remain unmeasured.

Reported OpenRouter cost for the ten monitor calls: **$0.0671836**. This excludes
earlier actor and judge calls, payment fees, and hosting. No actor was rerun and
no experiments were executed for this monitor test.

## Scope

Follow-up [score-gap audit](score_gap_audit.md): all-pass design-only traces do
not establish that monitor attrition is unimportant in the paper's full-workflow
average. Figure 14 plots a much lower monitor metric for original OpenHands +
o3-mini runs. Also, these replays preserve prompt text but use a user message,
whereas the released client sends the prompt as a system message and enables
JSON-object output mode. The effect of that request difference is unmeasured.

These are monitor-gated scores for design-only traces, not a reproduction of
the full-paper benchmark averages. We used current OpenHands SDK JSONL events,
not the original runner's console logs; the actor had no repository execution
tools and no empirical conclusion. Current OpenRouter model routing also
differs from the paper's original deployments. The five tasks are a selected
pilot, not the full 461-task evaluation.

## Artifacts and usage

- [Monitor summary](../../runs/expbench/original-monitor-20260922/summary.json)
- [Monitor manifest and input hashes](../../runs/expbench/original-monitor-20260922/manifest.json)
- [Original design-judge results](../../runs/expbench/original-judge-diagnostic-20260922/summary.json)
- [Example: interactive CycleNet monitor](../../runs/expbench/original-monitor-20260922/pilot-o3mini-20260922/neurips2024__94391__7/monitor.json)
- [Usage and gate semantics](../../docs/expbench/integrity-monitor.md)

Each output directory preserves the monitor prompt, API response, parsed flags
and explanation, standalone grade, gated result, and token/cost usage. Earlier
actor and grading artifacts remain unchanged.
