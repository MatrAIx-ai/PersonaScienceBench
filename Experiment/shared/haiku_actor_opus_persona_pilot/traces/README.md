# Compact trace inventory

This folder contains the Git-friendly evidence retained from the three raw
pilot trials.

## Per-trial records

- `trial-N-manifest.json`: models, arms, task count, AWS region, and selection
  checksum.
- `trial-N-progress.json`: terminal runner-state counts.
- `trial-N-results.json`: all 50 top-level episode outcomes and native benchmark
  results for that trial.

## Shared selection

- `pilot_selection.json`: the frozen 25-task panel.
- `selection.csv`: the corresponding selection table.

All three manifests record the same selection checksum:
`746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`.

## Audited normalization traces

- `trial-1-discovery-meta-regression-regrade.json`
- `trial-1-discovery-requirements-regrade.json`
- `trial-1-exp-timeout-actor-events.jsonl`

The two DiscoveryBench files are evaluator-only regrades of preserved Haiku
submissions. The EXP file records the 59-call episode that reached its wall-time
limit without submitting a design.

## Deliberately excluded

The bundle excludes complete per-call API logs, private task snapshots,
researcher-private histories, model caches, prepared workspaces, and scientific
execution environments. Those make the original trials about 1 GB and are not
needed to verify the aggregate report.
