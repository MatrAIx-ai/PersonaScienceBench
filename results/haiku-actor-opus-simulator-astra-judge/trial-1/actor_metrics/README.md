# Actor output-token and tool-call metrics

These are the actor-side process metrics for the exact 1,000 frozen Haiku-actor / Opus-researcher trajectories regraded in this bundle. They are inherited byte-for-byte from the source campaign because changing only the judge cannot change actor output tokens, model calls, tool calls, command attempts, or researcher handoffs.

- `per_episode.csv`: actor tokens and tool calls for every episode.
- `summary_by_condition.csv`: five condition-level summaries.
- `summary_by_benchmark_condition.csv`: 25 benchmark/condition summaries.
- `tool_name_counts.csv`: exact actor tool-name totals.
- `summary.json`: definitions, source provenance, and audit.
- `source_README.md`: original source-campaign documentation.

Researcher and judge tokens are excluded from actor token totals. SciConvBench uses a native non-tool conversation protocol, so its actor tool-call count is zero by design.
