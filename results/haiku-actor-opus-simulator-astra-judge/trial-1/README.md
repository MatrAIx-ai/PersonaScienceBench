# Haiku actor / Opus researcher / Astra judge results

This folder contains the compact, author-facing export of the judge-only
Astra regrade of the completed Haiku-actor / Opus-researcher campaign.

## Start here

- `summary.md`: findings and researcher-model ablation.
- `summary.json`: complete aggregate statistics and bootstrap intervals.
- `episodes.csv`: all 1,000 matched episode results.
- `persona_pairs.csv`: same-task persona-versus-control comparisons.
- `actor_metrics/`: actor output tokens, model calls, and tool calls for every
  frozen source episode.
- `traces/shared-events.jsonl`: sanitized Opus-simulator/Haiku-actor
  interaction traces for every frozen source episode.
- `traces/shared-events-index.csv`: searchable interaction-trace index.
- `judge_metrics/`: per-episode and aggregate judge-call counts.
- `evaluations/metrics.jsonl`: compact native evaluation metrics without API
  prompts or responses.
- `provenance/`: exact run receipts, code hashes, launchers, and source hashes.
- `candidate_*.md`: exact persona prompts.

## Scope

- Frozen source trajectories: 1,000.
- Actor or researcher reruns: 0.
- Astra calls: 2,587.
- Submitted endpoints scored deterministically with zero Astra calls:
  133.
- Original non-submissions retained as zero: 
  136.

`finished` means the native evaluator completed. It does not imply that an
Astra call was required. Model-based judging uses Astra wherever the native
benchmark requests it; deterministic native components remain unchanged.

## Excluded

The raw regrade is approximately 729 MB because ASI evaluation sandboxes copy
scientific assets. This compact bundle excludes those copies, private API
request/response logs, hidden evaluator references, and temporary workspaces.
Their source files are retained in the raw run and referenced by checksums.

Raw regrade:
`runs/rejudge/haiku-actor-opus-researcher-astra-judge-trial-1`

The actor metrics and interaction traces are inherited byte-for-byte from the
frozen source campaign. Judge-only regrading cannot change actor tokens, actor
tools, or actor–researcher conversation events.
