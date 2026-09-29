# Experiment workspace

This directory tracks the paper's experiments, their implementation, status, and results. The [paper plan](../docs/design/benchmark_paper_plan.md) remains the manuscript-level design.

| Folder | Purpose | Current scope |
|---|---|---|
| [Behavioral diversity](01_behavioral_diversity/PLAN.md) | Experiment 01 | Data collection in progress; summary-field extraction implemented; full trace analysis pending. |
| [Performance and field dependence](02_performance_and_fields/PLAN.md) | Experiment 02 | Trial-1 descriptive and paired analyses complete; three-trial analysis pending. |
| [Actor comparison](03_actor_comparison/PLAN.md) | Experiment 03 | Proposed extension; not started or submitted. |
| [Conversation case studies](04_conversation_case_studies/PLAN.md) | Experiment 04 | Exploratory pilot cases available; expanded-study cases pending. |
| [Static reference (optional)](05_static_reference/PLAN.md) | Experiment 05 | Optional; not started or submitted. |

Each experiment has `PLAN.md` (design, implementation, findings, remaining work), `status.json`, `code/`, and `data/`. Planned code is explicitly marked unimplemented. Existing large runs are referenced, not relocated or duplicated. Experiments 1, 2, and 4 analyze the same 1,800-episode campaign; their episode counts must not be added together.

Shared files: [setting](shared/setting.json), [frozen task panel](shared/task_selection.csv), [collection status](shared/run_status.json). The source and prepared inputs remain authoritative.

Refresh progress snapshots without API calls or job submission:

```bash
.venv/bin/python Experiment/refresh_status.py
```

Refresh reads each job's `progress.json`; it does not query Slurm. A partially processed run's running/queued/stopped state is unknown from this file alone. Error counts are preserved and flagged. Update each plan's implementation checklist and findings when work is completed; refreshing status does not mark scientific analysis complete.

## Top-ten expansion

Nine additional personas from the ten largest absolute pilot changes are now queued sequentially after the existing trials. See [expansion manifest](shared/top10_expansion.json) for all nine jobs and baseline references. This adds 5,400 episodes; the combined collection including persona 155 totals 7,200. Experiments 1, 2, and 4 should analyze the top-ten panel, keeping 155 labeled as an additional condition. Their original three-condition artifacts remain interim snapshots. `refresh_status.py` currently refreshes the original three trials only; consult the expansion manifest/run progress for new batches.
