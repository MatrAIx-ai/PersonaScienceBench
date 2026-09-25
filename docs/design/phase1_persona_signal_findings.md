# Phase 1 persona signal: local evidence, benchmark screen and evaluation options

Status: design note for discussion (2026-09-25). It proposes no change to Phase 1
code, tasks or grading. All runs are local, small and descriptive; raw traces
are kept by the author and not committed.

## Summary

- With the current actor configuration, the actor almost never consults the
  researcher. In 68 local episodes on `openai/gpt-6-luna` it asked **0**
  researcher questions. Persona is injected only into researcher replies, so
  these episodes cannot show a persona effect.
- The actor does ask when information is genuinely held only by the researcher.
  In the team's Luna baseline, EXP-Bench episodes asked 5, 4, 0, 6 and 0
  questions; HiL-Bench (external) reports about 1 to 7 questions per task on
  average, depending on model and domain.
- Two native grading behaviours add noise that can hide small persona effects.
- There are two coherent design logics (below). The one Phase 1 currently
  implies, with no real information gap, needs explicit outcome definitions and
  an interaction trigger to be measurable.

## Local evidence

Model `openai/gpt-6-luna` for actor, researcher and judge; `configs/pilot.json`
settings unless stated. Each condition in the table used three predeclared
repeats per task.

| Run (task) | Condition | Correct | Researcher questions |
| --- | --- | --- | --- |
| `bix-7-q2` | Researcher-only (standard) | 0/3 | 0 |
| `bix-7-q2` | All approved facts in the public brief (standards section 8 control) | 3/3 | 0 |
| `bix-7-q2` | Phase 1 example arms: off, reference, `coding_fluency_low`, `coding_fluency_high` | 0/12 | 0 |
| `bix-7-q2` | Persona off, actor `reasoning_effort` medium | 2/3 | 0 |
| Five BixBench tasks (`bix-19-q1`, `bix-7-q2`, `bix-14-q2`, `bix-52-q7`, `bix-6-q6`) | Researcher-only vs facts-in-brief | 2/15 vs 3/15 | 0 in all 30 |

1. The facts-in-brief control closed the gap for `bix-7-q2`, but more actor
   reasoning also closed it without the researcher. The gap was a reasoning
   gap rather than information only the researcher holds.
2. Across all 68 episodes (eleven BixBench questions, several conditions), the
   researcher question count was 0.

## Native grading behaviours observed

- `str_verifier` requires an exact alphanumeric match. Answers such as
  "337 samples per group." score 0 although the number is correct
  (`bix-19-q1`, `bix-42-q1`).
- In the adapter's native open-ended grader, `range_verifier` questions are
  always graded by an LLM judge rather than a numeric range check. The
  identical value 0.0216 was graded correct in 2 of 6 episodes (`bix-6-q6`).

These graders are frozen for Phase 1. We suggest reporting native answers next
to native grades so grading noise is visible.

## Benchmark screen: does the researcher hold answer-changing information?

Screened offline (repo tracks) or from papers and READMEs (external).

| Benchmark | Researcher-exclusive, answer-changing information | Practical fit |
| --- | --- | --- |
| BixBench, ScienceAgentBench, SciAgentBench, PhySciBench, MLAgentBench, OpenProblems | Essentially none; tasks are self-contained. ScienceAgentBench `domain_knowledge` is mostly background or tool hints (decisive in about 2 to 3 of 102). | ScienceAgentBench: most tasks need packages absent from the actor runtime |
| LABBench2 | Partly, but mostly the answer itself | Light |
| DiscoveryBench, IG-Bench, RExBench, NatureBench | Partly. DiscoveryBench `archaeology` construct definitions (38 queries) are not inferable from data. | DiscoveryBench is LLM-judged; RExBench and NatureBench need GPUs and hours |
| Terminal-Bench-Science, PaperBench | Yes: README Difficulty sections that are not part of the agent's instruction; author-developed rubrics and judge-only addenda | Heavy (hours, Harbor/Docker or GPU) |
| EXP-Bench | Yes, by design: setup facts held by the scoped researcher | Agents ask; not in the Phase 1 planner |
| ASI-Bench | Yes: each task ships guidance levels B1 (full method) to B3 (objective and data only), plus B4 (B3 with distractors); the paper reports 50.91 at B1 vs 26.62 at B3, aggregated over 18 agent-model configurations | Long, token-heavy tasks; the paper describes deterministic gates and scorers |
| HiL-Bench, SciConvBench | Yes; built to test asking | HiL-Bench is SQL/software; SciConvBench grades dialogue only |

Neither HiL-Bench nor SciConvBench conditions its simulator on a persona, and
the other external benchmarks have no user simulator.

## Two design logics

| | A: information asymmetry | B: information symmetry |
| --- | --- | --- |
| Researcher knows | Facts the actor cannot see | Nothing beyond what the actor can see, or nothing that must stay private |
| Persona acts through | How and when information is disclosed | Preferences, stance and interaction style |
| Main outcome | Native score plus question quality (e.g. HiL-Bench Ask-F1) | Needs dedicated outcomes (below); native score rarely changes |
| Examples | EXP-Bench, HiL-Bench, ASI-Bench B3/B1 | Current Phase 1 tasks in practice |

### Evaluating logic B

1. **Preference alignment with crossed scoring.** Give personas optional,
   checkable preferences, such as a required language or package, an
   interpretable model, or effect sizes with confidence intervals. Score each
   output under persona P against both P's rubric and the opposite persona's
   rubric. Adaptation is the diagonal minus the off-diagonal score, which
   controls for what the actor would do anyway.
2. **Robustness to persona pressure.** A persona states a confident but wrong
   prior. The native grader checks whether the scientific answer follows the
   data rather than the persona. This is deterministic wherever the native
   grader is.
3. **Communication fit.** Judge-scored against the rubric-anchored attributes
   and reported separately from correctness.
4. **Process measures.** Questions, steps, cost, and checks consistent with the
   persona (for example robustness checks under a cautious persona).

Logic B also needs interaction to happen. A fixed, persona-independent trigger,
such as a researcher review of the plan at a fixed checkpoint identical in all
arms, fits the standards' documented-trigger allowance. Plan submission is
currently optional, so making it a fixed step would be a registered protocol
change. Without such a trigger, zero-question episodes leave nothing to measure.

## Options for Phase 1

1. Keep existing tasks; make question behaviour a primary outcome and report
   persona effects conditional on interaction. Without HiL-Bench-style blockers,
   an Ask-F1-style measure can be computed against each task's reviewed fact
   pool: the share of questions that retrieve an approved fact, and the share
   of approved facts retrieved.
2. Add existing-benchmark tasks where the researcher holds non-inferable
   information (DiscoveryBench `archaeology` first), confirmed by an offline key
   check and a facts-in-brief control.
3. Consider an ASI-Bench track (actor B3, researcher B1). It is source-backed but
   needs an adapter and is outside the current planner.
4. For logic B: add a fixed plan-review trigger, crossed preference scoring and
   a persona-pressure robustness test.

## Limitations

A single model family and small samples. External benchmark facts come from
papers and READMEs and were not all verified by running them. The local runs
used uncommitted configurations described above. Only `bix-7-q2` was run under
the Phase 1 example arms.
