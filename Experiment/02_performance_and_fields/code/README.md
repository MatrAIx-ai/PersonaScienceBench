# Implementation

- `code/report_first_pass_ci.py` delegates to the existing interim analysis implementation.
- Trial-1 tables, matched scores, and paired-comparison output are copied into `data/trial_1/` with provenance.
- The repeated-run aggregation, study-cluster analysis, and expertise mapping are pending. Do not label interim task-bootstrap intervals as the final repeated analysis.

Commands use the repository `.venv/bin/python`. Code in this folder does not submit jobs automatically.

```bash
.venv/bin/python Experiment/02_performance_and_fields/code/report_first_pass_ci.py --run-dir runs/openai-astra-top2-first-pass
```

This regenerates artifacts in the source run, not the archived snapshot under this experiment. Refresh the copied snapshot and its hashes deliberately after reviewing changed results.
