# Automated conversion for the retained benchmarks

Every conversion produces a public task, source-attributed researcher context, evaluator mapping, provenance, and explicit asset-readiness status. The [standards](../benchmark_standards.md) define the shared rules; [setup](../reproducibility.md) gives acquisition and conversion commands. The [inventory](../../reports/conversion_v2/conversion_summary.md) covers the five retained tracks.

| Benchmark | Automated conversion | Interaction | Preserved evaluation |
|---|---|---|---|
| DiscoveryBench | Join native questions, datasets and references; classify source-exact context/advice; retain input paths | Approach and discovery/evidence review | Native context, variable and relation scoring |
| BixBench | Pinned capsule/member acquisition, data-file filtering and schema extraction; unresolved input roles block readiness | Approach, executed analysis and evidence review | Native open-answer grading and executed-analysis submission requirement |
| EXP-Bench | Cached classification selects exact public setup spans; exclude unresolved question/reference mismatches; generate public-only design workspace | Approach and completed-design review | Reference coverage and separate integrity gate; design only |
| ASI-Bench | Native task catalog and seed31415 instances; B3 public task, eligible B2 method guidance as researcher context; declared inputs, outputs and runtime | Approach, execution and evidence review | Native local gates and weighted scorers, isolated from the actor |
| SciConvBench | Native incomplete/inconsistent request, intended specification and issue annotations; retain source IDs and prompt-length cap | Native clarification dialogue | Native conversation/specification judges; no solver execution |

An empty researcher fact pack is valid. Source extraction is automatically validated and retains locators; it is not described as human review. Current full-profile experiments additionally allow general knowledge in both persona conditions, without exposing evaluator answers or treating suggestions as new requirements.

Bix schema facts are also observable from public data, so the simulator does not necessarily hold exclusive information. EXP extraction receives public question/method spans, not reference designs or expected outcomes; full experimental execution is outside this track. ASI is an explicit B3-plus-B2-guidance collaborative adaptation, rather than native autonomous B3. SciConv's intended specification is user-owned task context; its native annotations and judging are separate from scientific execution.

Related source cases and perturbations stay grouped in analysis. Retain SciConv's native case ratios and upstream aggregate fields separately, because their count definitions differ. Preserve all recorded failures and exclusions; conversion success does not establish runtime readiness or scientific success.

Generated catalogs remain under `data/conversion_catalog/` and `data/design_catalog/`. They are local inputs to task selection. Current preparation defaults cover the retained tracks; compatibility implementations for ScienceAgentBench and Terminal-Bench-Science are not scheduled by the study.
