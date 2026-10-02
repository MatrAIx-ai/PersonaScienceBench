# Main experiment: collaborator run guide

This guide is the entry point for running the selected five-setting campaign. Only `src/`, the run/setup scripts, `configs/`, and `manifests/` are needed; `Experiment/`, analysis notebooks, figures, and paper files are not inputs to this run. Historical studies elsewhere in the repository use different cohorts.

## Fixed design

| Setting | Injected simulator persona |
|---|---|
| `persona_off` | Disabled |
| `candidate_155` | Exact prompt in `configs/main_run/personas/candidate_155.md` |
| `candidate_001` | Exact prompt in `configs/main_run/personas/candidate_001.md` |
| `candidate_003` | Exact prompt in `configs/main_run/personas/candidate_003.md` |
| `candidate_046` | Exact prompt in `configs/main_run/personas/candidate_046.md` |

The same **200 unique questions** run under every setting: **40 each** from ASI-Bench, BixBench, DiscoveryBench, EXP-Bench, and SciConvBench. `configs/main_run/selection.csv` fixes question IDs and scientific-family labels. Family counts follow this frozen selection; they are not additionally equalized.

One trial is **1,000 episodes**. Three fresh trials are **3,000 episodes**. Each trial needs a distinct run directory; rerunning the same directory resumes it rather than creating an independent repeat. Historical persona coverage was uneven and is not included here.

Default actor, simulator (`researcher`), and judge: **`gpt-6-astra`, reasoning `low`**, via OpenAI. Model access must exist in the collaborator's account. Defaults are recorded in the launcher; role-specific overrides are available through `--help`. Persona injection affects the simulator. Shared controls come from `configs/full_persona_v2/{shared,exp}.json`: active-researcher protocol, 60 actor steps, 6 researcher questions, 12 collaboration requests, and unrestricted knowledge / identity embodiment enabled. Shared configuration also enables volunteered information. Do not change these across arms.

This is a snapshot of the current runtime, including the current SciConv protocol. It is not a promise to reproduce historical traces produced before protocol changes. `configs/main_run/provenance.json` records the parent commit and hashes of runtime files as copied, before the handoff-specific launcher edits. Each launched run additionally records the actual code hashes and resolved configuration.

## Install and acquire inputs

Use Linux, Python 3.12+, `uv`, and Bubblewrap (`bwrap`). Compute nodes need network access to OpenAI. Source/data downloads require network access and potentially substantial disk space. Install Bubblewrap using your system administrator/package manager.

```bash
git clone --single-branch --branch main https://github.com/MatrAIx-ai/PersonaScienceBench.git
cd PersonaScienceBench
bash scripts/setup_main.sh
cp .env.example .env
# Edit .env and set your own OPENAI_API_KEY. Never commit it.
```

Setup installs locked Python environments, fetches pinned source repositories, downloads BixBench/selected ASI assets and the EXP snapshot, builds local EXP task records, and checks sandbox readiness. It does not run scientific episodes or invoke an LLM. Downloaded data and environments are ignored by Git. Source licenses and access conditions remain applicable. Some scientific tasks may need additional native libraries or tools; preparation errors must be resolved without replacing questions.

Offline input check (standard-library Python only):

```bash
python scripts/check_main.py
```

## Run one trial locally

```bash
.venv/bin/python scripts/run_main.py \
  --run-dir runs/main/trial-1 --workers 30
```

**This command makes paid API calls.** The runner first checks model access, creates per-setting configurations, and prepares selected tasks. EXP preparation can invoke the model to extract the simulator context; its extraction cache is stored under `data/design_catalog/extraction_cache`. Preserve that cache across trials to hold converted inputs fixed. Do not launch initial preparation concurrently in multiple trials. All five settings within a trial share the same prepared task inputs. The runner stops before episodes if any of the 200 tasks fails preparation.

## Submit to SLURM

The separate submission script requests **128 GB RAM and 30 CPUs / workers** by default. Set your site's account, partition, and time limit as needed. It submits one trial per call:

```bash
export ACCOUNT=your_account PARTITION=your_partition
bash scripts/submit_main.sh 1
```

For three sequential trials, require the prior trial to finish successfully:

```bash
j1=$(bash scripts/submit_main.sh 1)
j2=$(DEPENDENCY=afterok:${j1%%;*} bash scripts/submit_main.sh 2)
DEPENDENCY=afterok:${j2%%;*} bash scripts/submit_main.sh 3
```

A failed job blocks downstream `afterok` jobs; repair the failed trial and update their dependencies or resubmit them. This deliberately avoids silently advancing past infrastructure failures. To change parallelism, set `WORKERS`; the submission script requests the same number of CPUs. The local launcher caps workers at `SLURM_CPUS_PER_TASK`, or 30 outside SLURM. Worker count does not guarantee a specific token throughput.

## Monitor, resume, and deliver results

Each `runs/main/trial-N/` contains:

- `manifest.json`, `selection.csv`, `configs/`, `code.*.json`: run identity and provenance.
- `preparation_errors.json`, `progress.json`, `results.json`: preparation and completion accounting.
- `episodes/`: per-task/per-setting state, attempt logs, native results, and interaction artifacts.
- `slurm-*.out`, `slurm-*.err`, `job_id.txt`: submission logs when using SLURM.

A complete trial must account for all **1,000** planned episodes. `finished` is an infrastructure status, not a correct-answer label; use native scores for scientific outcomes. Inspect missing submissions separately.

Resume with the same command and run directory. For a repair pass, use `--retry-infrastructure`; add `--retry-missing` only when intentionally repairing missing scientific submissions. Earlier attempts are retained. After quota/authentication failures, inspect `fatal_api.json`, resolve the cause, then archive/remove that marker before resuming. Do not blindly retry an exhausted account. API retry/backoff is implemented in the runtime, but cannot repair missing funding or permissions.

Return all three run directories plus the EXP extraction cache, source manifests, and the Git commit ID to the analyst through the agreed storage channel. Keep `.env` and API keys out of any archive. Runs/data are ignored by Git; pushing this branch does not upload results.

## Handoff validation

The handoff is checked offline for the selection checksum, question/source counts, persona prompts, Python syntax, CLI loading, and submission-script syntax. No paid episode or cluster job was launched while preparing it. End-to-end execution on the collaborator's machine still requires downloaded assets, sandbox support, model access, and a funded API account.
