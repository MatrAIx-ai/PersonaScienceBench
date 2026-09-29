# Shared researcher collaboration

Protocol `researcher-review-v2` uses the same loop across DiscoveryBench, BixBench, ASI-Bench, and the current EXP-Bench design-only track:

**Inspect → discuss the approach → execute or develop the design → review evidence → revise or finish.**

The agent first inspects inputs and proposes an approach, exposing consequential choices and uncertainty. The researcher approves that approach or requests clarification. After approval, the agent produces a result or design with evidence; the researcher can accept it or request a revision tied to a specific issue. Additional criticism and revisions are optional. The original scientific objective, fixed methods, constraints, output contract, and native grading remain unchanged.

## Handoffs and review

`end_researcher_turn` has these fields:

| Field | Meaning |
|---|---|
| `stage` | `plan` before approach approval; `result` afterwards |
| `answer` | Proposed approach, progress report, or final deliverable |
| `evidence` | Concrete input observations, result excerpts, diagnostics, or design rationale |
| `assumptions` | Choices not established by the source |
| `uncertainties` | Unresolved issues that could affect the work |
| `payload`, `artifacts` | Existing submission fields in the shared execution runner |

The researcher receives the public task, eligible approved facts and these handoffs. It does not receive hidden references or private actor reasoning. It must distinguish a suggested choice from confirmed study information. Persona expertise affects the review; it does not grant hidden knowledge or require expert-level criticism from novice profiles.

The controller enforces the order of handoffs: a result cannot be accepted before approach approval, and stopping cannot be accepted before a result has been reviewed. Inspection commands remain available before approval; the instruction to defer main analysis is prompt-based, because arbitrary shell commands cannot reliably be classified as inspection versus analysis. Thus the handoff order is enforced, not semantic classification of every command.

A complete candidate is retained through clarification-only replies. The researcher must choose to stop before a candidate is sealed; budget exhaustion without that decision leaves the task incomplete. Artifact validation and grading follow the existing benchmark contract. EXP-Bench reviews a completed design and its rationale, not fabricated experiment results. Its accepted design uses the existing design-only evaluation checkpoint; its approach handoff is not a second native graded submission.

SciConvBench retains its native clarification dialogue and final specification instead of adding approach/result approval turns. It shares information boundaries, persona isolation, native grading, and trace recording.

The researcher now returns one typed `researcher_decision` tool call per request. This prevents accepting a generated multi-turn conversation as a real decision. See the [current conversion rules](../design/conversion_revision_v2.md) for the maintained protocol.

## Enable it

For the current shared Python runner settings, see `configs/full_persona_v2/shared.json`. The relevant configuration is:

```json
"collaboration": {"protocol": "active_researcher", "max_requests": 12}
```

In active mode, `max_requests` controls dialogue; the passive simulator’s `max_questions` and `max_facts_per_reply` settings do not control active reviews. Source-specific facts remain attributed; the current full-profile configs set `unrestricted_knowledge=true` for both persona-on and persona-off conditions, allowing general knowledge and suggestions.

The shipped persona-off configurations use GPT-6 Luna for actor, researcher and LLM judges, with 60 total actor calls per case. Native programmatic graders remain programmatic. Use a fresh output directory and set the selected case count and parallelism through the existing runner options. Omitting `collaboration` preserves the earlier passive simulator behavior for historical configurations.

For the EXP realistic runner, use `configs/full_persona_v2/exp.json` with interactive input and design-only mode. Collaboration deliberately rejects the original-input control and experimental full-workflow mode. The legacy EXP runner is unchanged.

## Interpret the traces

Readable traces show the review phase, approach approval, handoff stage, evidence, assumptions and uncertainty. Raw logs retain all model calls and tool activity. `plan_reviews` and `result_reviews` distinguish the two review points. Request counts include initial requests; follow-up counts include approval and continuation messages and therefore do not measure useful criticism on their own.

Two exchanges are normal for the simplest complete task: inspection/approach, then result/design. Extra rounds should resolve an uncertainty, change a consequential choice, correct a discrepancy, or improve the explanation. Do not interpret a mechanical increase in turns as a demonstrated improvement in collaboration quality.

## Live verification

The [completed 30-persona report](../../reports/full_persona_v2/README.md) contains the current execution record and all 310 published Markdown traces. Original raw logs remain local under ignored `runs/`.
