# Construction and first live pilot

Date: 2026-09-23. The four retained adapters are implemented, with two explicitly
curated episode conversions each. Four data-ready episodes were executed through
OpenHands. At the time of this first pilot, the remaining four had data or native-runtime blockers.
ScienceAgentBench subsequently completed both cases; see [its report](sab_pilot_report.md)
and [current status](../docs/status.md).
The existing EXP-Bench adaptation remains separate.

## Current model configuration

| Role | OpenRouter model | Reasoning effort |
| --- | --- | --- |
| Simulator / researcher | `openai/gpt-6-luna` | `none` |
| Actor | `openai/gpt-6-luna` | `none` |
| Judge | `openai/gpt-6-luna` | `none` |

The judge was changed after the actor runs at the user's request. The final
Luna judge evaluated the original sealed submissions; **no actor was rerun**.
The actor had a maximum of 20 OpenHands iterations. Researcher interaction was
optional, limited to six questions with at most one reviewed fact per reply.
The persona was neutral and the researcher used grounded-prose mode. There was
no dollar cap or automatic inference retry. The saved API usage reports zero
reasoning tokens for all Luna calls.

## Final results: Luna judge

| Benchmark | Case | Actor calls | Shell commands: successful / attempted | Researcher questions | Native score |
| --- | --- | ---: | ---: | ---: | --- |
| DiscoveryBench | Requirements engineering survey | 5 | 4 / 4 | 0 | `final_score = 0.0` |
| DiscoveryBench | Incarceration and wealth | 4 | 2 / 2 | 0 | `final_score = 0.0` |
| BixBench | `bix-10-q2`: BCG/COVID ordinal regression | 6 | 3 / 4 | 0 | Incorrect, `grade = 0` |
| BixBench | `bix-8-q2`: m6A / expression association | 6 | 4 / 4 | 0 | Incorrect, `grade = 0` |

All four actors submitted final answers and analysis files. All four final
Luna evaluations completed without transport or parsing errors. DiscoveryBench's
mean native score is **0.0 over two scored tasks**; BixBench accuracy is **0/2**.
These are different native metrics; no combined benchmark average is reported.

For both DiscoveryBench cases, Luna returned `match: false` at the native
context-matching stage. Consequently, context recall and the final score are
zero; the variable/relation comparisons were not reached. The BixBench judge
explicitly returned an incorrect grade for both answers. These outcomes were
not substituted for missing files, API failures, or incomplete actor runs.

## What this test establishes

Offline verification passed **126 checks**: 117 adapter, transport, protocol,
and runtime checks plus nine actor checks, including a scripted integration
through the actual OpenHands SDK. Those are construction checks, distinct from
the four live scientific episodes and the two researcher conversations.

The conversion, isolated execution, submission capture, and grading paths work
for the four pilot cases. Bubblewrap's actual startup check verified a separate
network namespace, absent controller credentials and home configuration, and
working scientific Python dependencies. The actor saw only staged public data.

**The benchmark runs did not exercise the simulator.** Every actor completed
the task without asking a question. Therefore these scores do not demonstrate
a simulator or persona benefit. The current selected tasks and public briefs
allow independent work; future dialogue-focused selection should identify
consequential, source-grounded researcher context. Do not reinterpret this as a
four-episode evaluation of researcher collaboration or silently force questions.

Two separate researcher-interface checks used the same Luna configuration, two
questions per BixBench context, and an explicit progress update between questions.
Both retained episode-local conversation memory and disclosed only approved
facts. The BCG context produced two accepted grounded replies. In the m6A
context, both proposed replies failed the support check and were replaced with
the exact approved fact text. These fallbacks are recorded. No actor participated
in these checks and they contribute no scientific score.

Reference grading is also judge-sensitive. During setup, the same saved
submissions received different grades under Sonnet 5: the corrected run marked
BCG/COVID correct and assigned nonzero DiscoveryBench scores. The final Luna
results above follow the user's latest selection. This disagreement needs
review before interpreting the numbers as a reliable ranking of scientific
quality; changing the judge did not change the actor's scientific work.

## Explicit adaptations and compatibility repairs

- Each source keeps its own reference, rubric, score formula, and native output
  mapping. There is no added universal design-quality score.
- OpenRouter's selected endpoints do not advertise some native DiscoveryBench
  sampling parameters. The pilot explicitly omits unsupported parameters,
  records the requested and omitted settings, and marks a separate evaluator
  variant using provider defaults. Native sampling settings are not claimed to
  be exactly reproduced.
- The initial Sonnet default-reasoning judgement exhausted a native 250-token
  response on reasoning. That attempt remains an evaluation error. Disabling
  judge reasoning repaired the configuration without changing actor outputs.
- A provider returned complete JSON objects inside Markdown code fences despite
  JSON mode. The transport now removes only a complete, valid JSON-object fence;
  values and the raw response log remain unchanged. It does not repair malformed
  JSON, infer missing answers, or accept surrounding prose. Completed identical
  judge responses were reused during that repair, with only missing downstream
  judgements requested. Final Luna grading was a fresh evaluation because its
  model differs.
- Native answer grading does not independently validate scientific execution or
  the correctness of the analysis code. Command traces and submitted programs
  are retained separately; a successful command is not a scientific correctness
  certificate.

## Cases remaining at the time of this report

| Benchmark | Prepared cases | Why no live scientific run yet |
| --- | ---: | --- |
| ScienceAgentBench | 2 | Matching verified data/evaluator bundle returns HTTP 401; official alternatives do not contain these cases |
| Terminal-Bench-Science | 2 | Local inputs are complete, but Docker daemon access is denied; native Harbor environments/verifiers cannot run here yet |

These cases have no scientific score and are excluded from performance
denominators. See [construction status](../docs/construction_status.md) and
[the eight-case inventory](construction_inventory.json) for exact IDs and paths.

## Recorded artifacts and cost

- [Original actor runs and submissions](../runs/pilot-luna-none-01/summary.json).
  Each episode's `controller/` directory contains `actor_events.jsonl`,
  `events.jsonl`, `submission.json`, `submission_hashes.json`,
  `submitted_artifacts/`, and private API call records. The episode's `actor/`
  directory retains its working files.
- [Final Luna evaluations](../runs/pilot-luna-none-01-luna-judge/summary.json).
- [Separate researcher-interface checks](../runs/researcher-smoke-luna-none/summary.json).
- [Current configuration](../configs/pilot.json).

OpenRouter-reported cost for the 21 actor calls plus eight final Luna judge calls
was **$0.009213395**. The eight separate simulator-check calls cost **$0.0004187**.
Earlier Sonnet grading and compatibility debugging are additional: recorded
pilot/regrade calls total $0.25885. Small API compatibility probes are excluded
from these figures; this is returned usage accounting, not an invoice total.

Raw runs, credentials, and staged datasets are ignored by Git. Links to raw run
files identify local artifacts and are unavailable in a fresh clone. The configuration
file may evolve; saved run/config receipts identify the settings used for these results.
