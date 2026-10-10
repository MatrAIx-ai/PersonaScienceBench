# Haiku self-collaboration / Astra judge persona results

## Start here

This folder is the compact, author-facing export of the completed experiment:

- 200 frozen tasks: 40 each from five scientific-agent benchmarks;
- persona off plus four simulated-researcher personas;
- Haiku 4.5 as both actor and researcher simulator;
- GPT-6 Astra, low reasoning, as model-based judge;
- 1,000/1,000 final runner endpoints completed.

The persona-off mean was **21.97/100**. Read
[`summary.md`](summary.md) for the findings and interpretation.

## Files

- `summary.md`: author-facing findings.
- `summary.json`: complete aggregate statistics and paired bootstrap intervals.
- `episodes.csv`: one compact row per episode.
- `pairs.csv`: 800 same-task persona/control comparisons.
- `audit.json`: completion, retries, checksums, and repair provenance.
- `actor_metrics/`: per-episode actor output tokens, model calls, and tool calls.
- `traces/final-results.json`: exact final top-level result records.
- `traces/shared-events.jsonl`: shared actor/researcher interaction events.
- `traces/shared-events-index.csv`: searchable trace index.
- `provenance/`: exact manifest, selection, configs, code hashes, launcher, and
  Bedrock access receipt.
- `repairs/`: before/after evidence for the four invalid-image classification
  repairs.
- `candidate_*.md`: exact persona prompts.

## What is excluded

The raw run is approximately 21 GB because it contains prepared datasets,
sandbox environments, actor workspaces, generated scientific artifacts, and
private API records. Those are not duplicated here.

The compact shared trace excludes raw actor command output, system prompts,
private researcher state, evaluator references, and API payloads. Source paths
and SHA-256 checksums preserve trace provenance.

## Raw run

`runs/main/haiku-self-astra-judge-five-condition-full-trial-1`

## Reproduce this bundle

```bash
docker/run.sh .venv/bin/python scripts/package_haiku_self_astra_results.py
```

The exporter refuses to overwrite an existing bundle.
