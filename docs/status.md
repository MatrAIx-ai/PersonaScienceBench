# Current status

Seven benchmark tracks have automated conversion paths. The current catalog contains 2,280 converted cases and 24 exclusions. See [readiness and exclusions](../reports/conversion_v2/conversion_summary.md).

The latest persona-off GPT-6 Luna trial ran two cases per benchmark concurrently: 13 graded outcomes and one ScienceAgentBench missing submission. See [results](../reports/conversion_v2/README.md). EXP remains design-only; ASI uses local seed31415 grading; SciConv evaluates clarification and specifications.

[Conversion rules and commands](design/conversion_revision_v2.md) document implementation boundaries and remaining runtime requirements. Previous pilot records have been archived outside the repository; current raw records remain local under ignored `runs/`.

The merged science-persona profiles and two reviewed BixBench CHIP questions are available. The Phase 1 planner preserves the configured interaction protocol and source-backed fact eligibility across persona arms.
