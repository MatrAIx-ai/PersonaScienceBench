Run the frozen 200-task sample (40 tasks per benchmark), with the two highest-ranked prior-pilot personas (candidate_148 and candidate_155) and persona off (600 episodes), once per condition. Override with `--arms persona_off candidate_148 candidate_155` or another explicit subset. All roles and EXP source-span conversion use direct OpenAI Responses, `gpt-6-astra`, reasoning `low`.

```bash
bash scripts/submit_openai_first_pass.sh
```

The submission requests one node, 30 CPUs, 128 GB RAM, and 12 hours on `general`. The coordinator prepares only selected tasks and runs at most 30 episode processes concurrently. Scientific BLAS/OpenMP threads are limited to one. Credentials are read from the ignored `.env`; they are not placed in command arguments or run manifests.

Artifacts are under the printed run directory: frozen `selection.csv`, `manifest.json`, per-condition configs, per-submission implementation hashes, Slurm logs, `progress.json`, and individual episode logs/results. Preparation failures remain in `preparation_errors.json`; tasks are never silently replaced. Successful preparation is reused. No pilot or smoke episodes precede this run. Existing runners retain their intrinsic runtime startup checks.

Resume an interrupted run with the same directory:

```bash
RUN_DIR=/absolute/path/to/run bash scripts/submit_openai_first_pass.sh
```

After diagnosing and fixing infrastructure failures, explicitly retry those episodes while retaining earlier attempts:

```bash
RUN_DIR=/absolute/path/to/run bash scripts/submit_openai_first_pass.sh --retry-infrastructure
```

Completed scientific outcomes, including missing submissions, are preserved. A fatal API configuration/authentication error creates `fatal_api.json` and prevents further inference; resolve the issue and archive that marker before resubmitting. HTTP 429 responses receive bounded backoff; ambiguous transport failures are not automatically replayed. Native EXP judge repetitions remain three and are not additional episode repetitions. This is a first pass, not a multi-seed confidence-interval estimate.

To resume trials sequentially, submit trial 2 with `--retry-infrastructure`, then set `DEPENDENCY=afterany:JOB_ID` when submitting trial 3. `afterany` waits for the entire preceding job to terminate, including when episode errors cause a nonzero exit; it does not assert that every episode succeeded. Each job still uses at most 30 concurrent episode processes. Previous attempt directories remain intact.

Persona-only expansion batches may use `--baseline-run /path/to/matching/trial` instead of including persona off in `--arms`. The coordinator checks task-panel and generation/protocol compatibility. This references baseline results for later analysis; it never copies or regenerates them. `scripts/submit_top10_expansion.py --after-job JOB_ID` submits the prepared expansion manifest as sequential 600-episode batches.
