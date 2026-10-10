# Import validation and final-table mapping

Imported from `actor_metrics(1).zip`. The seven original exported files are
unchanged. The archive is retained outside Git at
`external/imports/haiku_actor_opus/actor_metrics(1).zip`; `import_audit.json`
records its SHA-256 and the extracted file checksums.

Validated 1,000 unique question/condition slots against the merged full campaign:
all attempts, native statuses, submission flags and scores agree. Every episode's
actor API call count equals its recorded actor-call count. Input plus output tokens
equal total tokens; tool-name totals equal exported total tool calls. All five
exported output checksums and three campaign input checksums match. All 1,000
episodes have an API-log checksum; all 800 tool-protocol episodes have an actor
event-log checksum. Only the 200 SciConv episodes lack tool logs, as expected.

For the existing final model table:

- **Actor output (k tokens/episode):** `actor_output_tokens / 1000`, averaging
  the four injected personas equally and benchmarks equally. These are recorded
  completion-token totals, not estimates from visible text. Simulator and judge
  usage are excluded. Do not infer a separate reasoning-token count from this
  aggregate export.
- **Tool calls / episode:** sum `execute_command`, `inspect_repository`, and
  `execute_check` in `tool_name_counts`. Exclude `end_researcher_turn`. Restrict to
  ASI/Bix/Discovery/EXP; SciConv is not applicable and must not enter the mean as
  zero. This matches the Astra extraction's tool-name filter.
- Do **not** use unfiltered `actor_tool_calls` (it includes handoffs), or
  `recorded_execution_calls` (it omits rejected/failed attempts and the earlier
  compact EXP export defaulted that field to zero).
- Recompute the scorecard's study-cluster bootstrap from per-episode rows;
  the supplied summary means do not implement the tool column's source/filter
  contract and are not accompanied by the required table CIs.

This package supplies the previously missing per-episode metrics, including EXP
tool counts. It contains aggregates and provenance, not the private API/action
logs themselves. The original counts cannot be independently re-extracted here
without those source logs; local validation establishes internal consistency and
alignment with the published campaign.

`generate.py` preserves its original upstream checkout layout. Its default paths
and the README's Docker command do not match this repository layout. Rerunning
the generator requires the source run and explicit absolute `--run-dir` and
`--bundle-dir` arguments. The imported CSV can be used directly without that run
directory or any model inference. The final notebook has not yet been regenerated
as part of this archive import.
