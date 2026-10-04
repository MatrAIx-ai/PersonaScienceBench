# Compact trace inventory

This folder contains Git-friendly evidence for the three raw pilot trials and
the completed 1,000-episode full campaign.

## Full campaign

- `full-campaign-receipt.json`: the final 1,000/1,000 completion record, fixed
  model/task manifest, raw-input SHA-256 checksums, native status counts, nine
  attempt-2 slots, and checksums of the compact generated reports.

The full nested `results.json` is about 18 MB and is not duplicated here.
`../full_campaign_episodes.csv` and `../full_campaign_pairs.csv` contain the
compact data needed to inspect and reproduce the reported statistics.

## Pilot per-trial records

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
