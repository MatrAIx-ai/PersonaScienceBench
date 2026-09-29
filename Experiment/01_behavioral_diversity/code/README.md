# Implementation

- Current summary fields can be exported with `code/extract_summary_metrics.py`. Missing fields remain missing; they are not zero.
- Detailed message/language extraction, semantic trajectories, and three-trial statistics are not implemented here.
- Existing exploratory implementations: `scripts/report_top_persona_deviations.py` and `scripts/report_full_persona_snapshot.py`; these target older data and require adaptation.

Commands use the repository `.venv/bin/python`. Code in this folder does not submit jobs automatically.

```bash
.venv/bin/python Experiment/01_behavioral_diversity/code/extract_summary_metrics.py --run-dir runs/openai-astra-top2-first-pass --trial 1 --output Experiment/01_behavioral_diversity/data/trial_1_summary_metrics.csv
```
