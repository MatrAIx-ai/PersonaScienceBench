# PersonaScienceBench

Scientific agents collaborating with diverse simulated researchers.

**Start here:** [remote-agent handoff](docs/TEAM_HANDOFF.md) · [paper and experiment plan](docs/design/benchmark_paper_plan.md) · [completed 30-persona results](reports/full_persona_v2/README.md) · [interaction case studies](reports/full_persona_v2/case_studies.md)

## Current study

The completed experiment contains **30 full personas plus persona off, two questions from each of five benchmarks, and 310 recorded episodes**. Actor, simulator and judge used GPT-6 Luna with reasoning effort `none`. Full profiles enter only the simulator system prompt; both conditions allow general knowledge, while evaluator references remain private.

The [results report](reports/full_persona_v2/README.md) preserves all scores, persona indexes, exact injected profiles, and **310 full Markdown traces**, including failed and missing-submission episodes. [Frozen experiment metadata](reports/full_persona_v2/experiment.json) and [configuration snapshots](configs/full_persona_v2) accompany them. Raw JSON logs and execution artifacts remain local; see the handoff for transfer instructions.

## Five retained benchmarks

| Benchmark | Converted cases | Scientific coverage | Native evaluation |
|---|---:|---|---|
| DiscoveryBench | 264 | Biology, humanities, sociology, economics, engineering, meta-science | Discovery scoring |
| BixBench | 205 | Computational biology | Open-answer grading with executed-analysis submission |
| EXP-Bench | 440 | ML and scientific experiment design | Design coverage and integrity gate; design only |
| ASI-Bench | 60 | Scientific computing across disciplines | Local gates and weighted scores |
| SciConvBench | 1,139 | Fluids, PDEs, materials, solid mechanics | Clarification and specification metrics |

There are **2,108 converted cases**. Conversion does not guarantee that every input or runtime is ready. [Conversion inventory](reports/conversion_v2/conversion_summary.md). ScienceAgentBench and Terminal-Bench-Science were discarded from the active study because of their heavier data/runtime requirements; compatibility code remains for existing interfaces and tests.

Conversion is automated per benchmark. Preserve the scientific question, inputs, deliverables and native grading; separate public context from simulator context and evaluator references; record exclusions and source provenance. Execution/design tasks use approach and result reviews, while SciConv retains native clarification. See the [conversion rules](docs/design/conversion_revision_v2.md) and [benchmark standards](docs/benchmark_standards.md).

## Next experiment

The [paper plan](docs/design/benchmark_paper_plan.md) proposes **200 nonvisual questions, six selected personas plus persona off, and three independent complete episodes per condition**. That is 4,200 episodes per actor or 12,600 for three actors. Task selection and the expanded launcher are still to be implemented; the future batch has not been launched. The plan contains the task mixture, behavioral metrics, and figure/table dependencies.

## Setup and navigation

Follow the [Linux setup and migration guide](docs/reproducibility.md). The [persona guide](docs/personas.md) explains the full-profile injection used in the completed study; the [interaction protocol](docs/interaction_protocol.md) explains the shared review workflow.

| Location | Purpose |
|---|---|
| `reports/full_persona_v2/` | Preserved experiment results, profiles, trace indexes, full traces and case studies |
| `configs/full_persona_v2/` | Frozen cohort, task selection and model/protocol settings |
| `docs/design/benchmark_paper_plan.md` | Authoritative future study and paper plan |
| `docs/persona_pilots.md`, `reports/discoverybench_persona_pilot/` | Config-driven persona pilots (dry-run estimates, TPM-aware parallelism, persona / persona-off / neutral / counterfactual arms) and the DiscoveryBench pilot results |
| `src/`, `scripts/`, `tests/` | Runners, conversion/analysis tools and offline checks |
| `manifests/` | Pinned upstream sources and checksums |
| `data/`, `external/`, `prepared/`, `runs/` | Ignored local inputs and runtime artifacts; transfer or regenerate explicitly |

<!-- FULL_PERSONA_RESULTS_START -->

## Current persona results

Final results: **310/310 episodes finished**. [Benchmark results, all 30 profiles, and interaction traces](reports/full_persona_v2/README.md).

Top deviations below use the same **8 completed questions** for every persona; questions with infrastructure or evaluator errors are excluded for every persona. Differences are normalized score percentage points.

**Shared baseline: 26.01%.** All personas are compared on the same 8 questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.

| Rank | Persona | Score | Change vs off | Traces |
|---:|---|---:|---:|---|
| 1 | [046](reports/full_persona_v2/profiles/candidate_046.md) | 4.54% | **-21.47 pp** | [Read](reports/full_persona_v2/traces/candidate_046.md) |
| 2 | [003](reports/full_persona_v2/profiles/candidate_003.md) | 6.14% | **-19.87 pp** | [Read](reports/full_persona_v2/traces/candidate_003.md) |
| 3 | [004](reports/full_persona_v2/profiles/candidate_004.md) | 9.33% | **-16.68 pp** | [Read](reports/full_persona_v2/traces/candidate_004.md) |
| 4 | [089](reports/full_persona_v2/profiles/candidate_089.md) | 9.79% | **-16.22 pp** | [Read](reports/full_persona_v2/traces/candidate_089.md) |
| 5 | [001](reports/full_persona_v2/profiles/candidate_001.md) | 9.91% | **-16.10 pp** | [Read](reports/full_persona_v2/traces/candidate_001.md) |
| 6 | [127](reports/full_persona_v2/profiles/candidate_127.md) | 10.51% | **-15.50 pp** | [Read](reports/full_persona_v2/traces/candidate_127.md) |
| 7 | [262](reports/full_persona_v2/profiles/candidate_262.md) | 11.33% | **-14.68 pp** | [Read](reports/full_persona_v2/traces/candidate_262.md) |
| 8 | [224](reports/full_persona_v2/profiles/candidate_224.md) | 12.20% | **-13.81 pp** | [Read](reports/full_persona_v2/traces/candidate_224.md) |
| 9 | [148](reports/full_persona_v2/profiles/candidate_148.md) | 39.37% | **+13.36 pp** | [Read](reports/full_persona_v2/traces/candidate_148.md) |
| 10 | [026](reports/full_persona_v2/profiles/candidate_026.md) | 12.66% | **-13.35 pp** | [Read](reports/full_persona_v2/traces/candidate_026.md) |

**Behavior on the same questions**

Each cell shows **persona on / baseline**. Rows follow the performance ranking.

| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |
|---|---:|---:|---:|
| [046](reports/full_persona_v2/profiles/candidate_046.md) | 2.38 / 3.38 | 70.76 / 65.99 | 0.17 / 0.33 |
| [003](reports/full_persona_v2/profiles/candidate_003.md) | 3.88 / 3.38 | 66.73 / 65.99 | 0.00 / 0.33 |
| [004](reports/full_persona_v2/profiles/candidate_004.md) | 3.88 / 3.38 | 69.05 / 65.99 | 0.00 / 0.33 |
| [089](reports/full_persona_v2/profiles/candidate_089.md) | 4.25 / 3.38 | 69.53 / 65.99 | 0.00 / 0.33 |
| [001](reports/full_persona_v2/profiles/candidate_001.md) | 4.25 / 3.38 | 70.60 / 65.99 | 0.00 / 0.33 |
| [127](reports/full_persona_v2/profiles/candidate_127.md) | 4.50 / 3.38 | 70.49 / 65.99 | 0.50 / 0.33 |
| [262](reports/full_persona_v2/profiles/candidate_262.md) | 2.25 / 3.38 | 68.95 / 65.99 | 0.00 / 0.33 |
| [224](reports/full_persona_v2/profiles/candidate_224.md) | 4.38 / 3.38 | 65.12 / 65.99 | 0.00 / 0.33 |
| [148](reports/full_persona_v2/profiles/candidate_148.md) | 3.88 / 3.38 | 72.61 / 65.99 | 0.00 / 0.33 |
| [026](reports/full_persona_v2/profiles/candidate_026.md) | 3.50 / 3.38 | 74.09 / 65.99 | 0.33 / 0.33 |

Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.


<!-- FULL_PERSONA_RESULTS_END -->
