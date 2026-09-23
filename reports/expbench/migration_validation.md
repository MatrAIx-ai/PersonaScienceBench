# EXP-Bench migration validation

Date: 2026-09-23. EXP-Bench now lives in PersonaScienceBench, with a separate
`src/expbench` package and design-track commands. This migration preserves the
existing researcher/evaluator semantics; it does not connect the shared A–G
persona router or claim full-experiment reproduction.

Validation completed:

- The combined suite passed **176 tests**, including 47 migrated EXP-Bench tests
  and actual namespace-isolation checks. Dependency warnings remain visible.
- All 59 upstream files passed the pinned snapshot hashes.
- Rebuilding the joined dataset, early design cards and realistic cards produced
  **byte-identical task JSONL files** to the migrated snapshots.
- All five masked repository workspaces passed their existing staging hashes
  after their operator-owned path maps were relocated.
- Both installed commands worked from outside the repository. `expbench validate`
  loaded five task cards, and `expbench-realistic run --mode mock` completed a
  JaxMARL design episode using the real sandbox and scripted model responses.
  Its reported performance values remained null because mock output is not a
  scientific score.
- Documentation links and the distributable-text credential check passed.

No paid model calls or new scientific benchmark runs were made. Existing
Sonnet/o3-mini scores were not re-evaluated. Historical run receipts remain
unchanged, including their original path strings; public report links and
preparation maps were updated for the new layout.

Downloaded annotations, generated references/task cards and previous raw runs
were physically moved into ignored `data/` and `runs/expbench/` directories.
They are not published with the source. Cluster-specific experimental full-run
configuration and the old vendor checkout are retained locally under
`external/expbench-history/`. The committed manifests/scripts let developers
rebuild source inputs inside a fresh checkout.

See [setup and evaluation details](../../docs/adapters/expbench.md).
