# Actor token and tool-call metrics

This folder reports actor-only resource usage for the completed 1,000-episode Haiku actor / Opus collaborator campaign.

## Definitions

- **Actor output tokens per episode:** sum of Bedrock `completion_tokens` for API log rows whose role is `actor`. Researcher and judge tokens are excluded.
- **Actor model calls:** number of final-attempt, usage-bearing API response records whose role is `actor`. EXP-Bench also logs a request/reservation row for each call; those rows have no usage and are not double-counted.
- **Actor tool calls:** model-issued OpenHands `ActionEvent` records with a non-empty `tool_name`.
- **Command attempts:** actor tool calls named `execute_command`.
- **Recorded executions:** commands that reached the controller and returned far enough to enter its execution ledger. This can be lower than command attempts when a call is rejected or errors first.
- **Collaboration handoffs:** actor tool calls named `end_researcher_turn`.
- SciConvBench uses its native non-tool conversational protocol, so its actor tool-call count is zero and is labeled `non_tool_sciconv_protocol`.

Only aggregate usage fields and checksums are exported. The private API request/response logs are not copied into this folder.

## Mean metrics by condition

| Condition | Output tokens / episode | Actor model calls / episode | Actor tool calls / episode | Command attempts / episode | Recorded executions / episode |
|---|---:|---:|---:|---:|---:|
| `persona_off` | 35305.6 | 22.05 | 22.41 | 17.42 | 16.25 |
| `candidate_155` | 45523.7 | 23.82 | 24.31 | 17.50 | 16.43 |
| `candidate_001` | 35352.0 | 21.92 | 21.97 | 17.23 | 16.16 |
| `candidate_003` | 35793.7 | 21.54 | 21.52 | 16.90 | 15.69 |
| `candidate_046` | 41755.9 | 21.91 | 22.37 | 17.04 | 15.97 |

These are descriptive one-trial process metrics. Different benchmark protocols require very different numbers of model and tool calls, so use `summary_by_benchmark_condition.csv` for within-benchmark comparisons.

## Files

- `per_episode.csv`: actor tokens and tool calls for every episode.
- `summary_by_condition.csv`: five condition-level summaries.
- `summary_by_benchmark_condition.csv`: 25 benchmark/condition summaries.
- `tool_name_counts.csv`: exact tool-name totals and per-episode means.
- `summary.json`: definitions, provenance, aggregate results, and audit.
- `generate.py`: reproducible offline generator.

## Reproduce

```bash
docker/run.sh .venv/bin/python haiku_actor_opus_persona_pilot/actor_metrics/generate.py
```
