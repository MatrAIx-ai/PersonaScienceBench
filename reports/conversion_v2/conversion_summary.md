# Retained benchmark conversion inventory

Automated conversion produced **2,108 cases from 2,132 source cases**, with 24 exclusions. [Machine-readable inventory](conversion_summary.json). These are catalog counts, not the size of the completed persona study or the proposed 200-question panel.

| Benchmark | Source cases | Converted | Excluded | Asset-ready at initial conversion |
|---|---:|---:|---:|---:|
| DiscoveryBench | 264 | 264 | 0 | 264 |
| BixBench | 205 | 205 | 0 | 145 |
| EXP-Bench | 461 | 440 | 21 | 440, design only |
| ASI-Bench | 60 | 60 | 0 | 3 |
| SciConvBench | 1,142 | 1,139 | 3 | 1,139 |

The asset column preserves the September 25 conversion snapshot. Five ASI instances now have local data/reference directories, including the four nonvisual cases proposed in the paper plan; this does not establish every dependency or evaluator is runnable. Bix's other 60 cases have unresolved input-file roles. EXP excludes question/reference mismatches and invalid references. SciConv excludes cases missing required native fields and does not apply the original paper's prior-model-success filter.

See [conversion rules](../../docs/design/conversion_revision_v2.md), [completed persona results](../full_persona_v2/README.md), and [future task mixture](../../docs/design/benchmark_paper_plan.md). ScienceAgentBench and Terminal-Bench-Science are retired from the active suite. Earlier conversion trial outcomes and implementation snapshots are recoverable from Git history.
