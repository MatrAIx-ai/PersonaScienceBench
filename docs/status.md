# Implementation status

Updated 2026-09-23. This page is the current status; `docs/design/` contains
historical proposals and `reports/construction_inventory.json` is a historical
asset/conversion audit, not a live leaderboard.

| Component | Implemented | Validated / remaining |
| --- | --- | --- |
| Episode schema and adapters | Public/researcher/evaluator split; source pins; two reviewed conversions per adapter | Four adapters, eight task conversions; broader source inventories are not fully converted |
| Actor | OpenHands loop, isolated commands, optional researcher questions, plan checkpoints, sealed submission | Six live episodes across DiscoveryBench, BixBench and ScienceAgentBench |
| Researcher | Episode-local memory, reviewed-fact limits, extractive and checked grounded replies | Separate live interface probes; one question in SAB pilot; grounding remains model-based |
| Persona router | A–G defaults/domain/task overrides, behavioral rendering, private digest; task-derived H | Offline routing, memory and boundary tests; live persona comparisons pending |
| Native evaluation | Source-specific judge bridges; SAB fresh program replay + isolated native evaluation | Discovery/Bix judge-sensitive; SAB 1/2 native successes; no cross-source average |
| Terminal bridge | Two source-preserving conversions; sealed-submission Harbor verification | No live run; development host lacks Docker access |
| Reproduction | Controller/scientific dependency locks, pinned source fetch, SAB provisioning, runtime probe | Fresh controller/scientific installs and source preparation verified; [176 tests pass](../reports/expbench/migration_validation.md); external access/OS prerequisites remain |
| EXP-Bench | Migrated `src/expbench`, configs, preparation scripts, tests and reports | Five design tasks; separate legacy researcher/evaluation interfaces; [setup](adapters/expbench.md) |

## Live pilot evidence

| Benchmark | Completed | Evaluation result | Researcher questions |
| --- | ---: | --- | --- |
| DiscoveryBench | 2 | Final Luna `final_score=0.0` for both | 0, 0 |
| BixBench | 2 | Final Luna `grade=0` for both | 0, 0 |
| ScienceAgentBench | 2 | Valid programs 2/2; native success 1/2 | 0, 1 |
| Terminal-Bench-Science | 0 | No score | Not run |

DiscoveryBench/BixBench scoring uses the preserved source-specific LLM judge
paths with explicitly recorded provider parameter adaptations. Different judges
gave different scores for identical submissions. ScienceAgentBench uses unchanged
programmatic graders inside an adapted execution environment. Papyrus selected
the same 336 activity IDs as the reference but failed exact table comparison;
its zero is not evidence of incorrect activity selection.

Read the [first pilot report](../reports/pilot_report.md) and
[SAB report](../reports/sab_pilot_report.md) for measured costs, traces and caveats.
These runs predate the configurable persona router. No result currently establishes
that a particular persona improves scientific performance.

## Next research work

1. Run controlled persona comparisons on the same task/model settings and report
   question counts, disclosure and grounding fallbacks alongside native scores.
2. Review judge sensitivity and source output-contract ambiguities without
   silently repairing native evaluation or altering existing results.
3. Validate Terminal's Harbor bridge on a Docker-capable host.
4. Extend reviewed task coverage, keeping study groups and references isolated.

EXP-Bench uses its preserved scoped researcher; the shared A–G persona router is
not yet connected to that legacy track. Its historical comparison reports 79.5
and 92.7/100 coverage with Sonnet 5 and o3-mini simulators respectively, both
using Sonnet 5 actor/judge. Those are design scores, not full-experiment results.

There is no implementation of demographic population sampling, LLM persona routing,
automatic conversation initiation or a universal scientific-quality grader.
