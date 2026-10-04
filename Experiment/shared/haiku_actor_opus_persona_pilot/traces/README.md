# Compact trace inventory

This folder contains Git-friendly evidence for the three raw pilot trials and
the completed 1,000-episode full campaign.

## Full campaign

- `full-campaign-receipt.json`: the final 1,000/1,000 completion record, fixed
  model/task manifest, raw-input SHA-256 checksums, native status counts, nine
  attempt-2 slots, and checksums of the compact generated reports.
- `full-campaign-manifest.json`: exact final model, arm, task-count, region, and
  selection identity.
- `full-campaign-progress.json`: exact terminal runner accounting.
- `full-campaign-results.json`: exact top-level native results for all 1,000
  episodes. This is the full-campaign counterpart of `trial-N-results.json`.
- `full-campaign-shared-events.jsonl`: actual controller-level shared events
  for every final episode, including researcher decisions, actor/researcher
  handoffs, clarification questions/replies, submissions, and termination.
- `full-campaign-shared-events-index.csv`: one row per episode with its JSONL
  line number, score, status, event counts, source path, and source checksum.

`../full_campaign_episodes.csv` and `../full_campaign_pairs.csv` provide
smaller analysis-ready views of the same campaign.

Raw actor tool commands/results, system prompts, API payloads, and
judge-private records are deliberately excluded from the shared export. The
source event-log checksum on every row preserves provenance.

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
