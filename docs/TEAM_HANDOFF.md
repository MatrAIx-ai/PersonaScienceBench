# Remote-agent handoff

## New-model campaign → paper main table (updated 2026-10-10)

This is the handoff contract for another agent evaluating a new model. Run **one fresh trial of 200 questions × five settings = 1,000 episodes** unless additional independent trials are explicitly requested. **The running agent must save the complete collection bundle under `results/<model-slug>/trial-<N>/`, commit it, and push it to the repository. Our analysis team handles final grading, metric extraction, CIs and paper-table updates afterward.** Deliver the underlying records, not just four aggregate numbers; computing the main table is not a prerequisite for delivery. The main table has **Persona-off performance, Mean Persona Performance, Fact recovery (%), and Self-repetition (%)**, each with a 95% CI when reproducible. Tokens/tool calls are supporting data, not main-table columns.

## Model expansion TODO — medium reasoning (2026-10-10)

**20 requested target models.** For this expansion, use the target model for both actor and simulator, requesting **medium reasoning for both**. Keep the common final judge as **GPT-6 Astra / low**, consistent with the existing grading contract; our team can grade after collection. This checklist does not modify existing low-effort jobs, historical results, or CLI defaults.

Names below are requested planning labels, not verified API IDs. Before launching, resolve the exact provider ID/version/variant and verify that the provider supports the requested medium setting (or a documented equivalent). Record the actual transmitted setting and any equivalent token budget. If medium is unsupported, flag the entry rather than silently ignoring it or substituting low. Do not count a similarly named model/version as completed.

Count against the current paper table: **2 exact-name overlaps** (Opus 5.5 and Astra), plus **1 possible overlap** (Gemini 3.7, if the intended variant is Flash). Thus **18 lack an exact-name paper row, or 17 if Gemini 3.7 means Gemini 3.7 Flash**. A paper row alone does not establish reproducible medium-effort coverage. **2 of these 20 (GLM 5.3 Flash, Qwen 3.8 27B) now have medium-effort collection bundles in `results/`, each with a small number of unresolved execution slots documented in the bundle; the other 18 remain unchecked** until the configuration and delivery are verified. Some entries may be completed by obtaining and verifying existing collaborators' bundles rather than rerunning them.

Each verified campaign requires 200 frozen questions × five settings × one trial = **1,000 episodes**. The full 20-model target is **20,000 episodes**, before any separately tracked repairs/additional trials. This is a target inventory, not a claim that 20,000 new episodes must be rerun.

| Done | Target actor + simulator | Required effort | Existing evidence / next action |
|---|---|---|---|
| [ ] | Claude Opus 5.5 | Medium | Paper row exists; medium configuration and full result bundle need verification. |
| [ ] | Claude Fable 5.1 | Medium | No matching paper row or delivered campaign. |
| [ ] | Claude Sonnet 5.5 | Medium | No matching paper row or delivered campaign. |
| [ ] | Claude Haiku 5.5 | Medium | No matching campaign; existing Haiku 4.5 is a different version. |
| [ ] | GPT-6 Astra | Medium | Paper row and historical traces exist at low effort; medium campaign still required. |
| [ ] | GPT-6 Luna | Medium | Historical rate-limit probe only; no full matching paper row. |
| [ ] | GPT-6 Sol | Medium | No matching campaign; historical GPT-5.6 Sol is a different version. |
| [ ] | GPT-5.6 Terra | Medium | No matching paper row or delivered campaign. |
| [ ] | GPT-5.5 | Medium | No matching paper row or delivered campaign; GPT-5 mini/nano do not count. |
| [ ] | Muse Glimmer 30B | Medium | No matching paper row or delivered campaign. |
| [ ] | Muse Spark 1.3 | Medium | No matching paper row or delivered campaign. |
| [ ] | Gemini 3.8 Flash | Medium | No matching campaign; Gemini 3.7 Flash is a different version. |
| [ ] | Gemini 3.7 | Medium | Gemini 3.7 Flash has a paper row; confirm whether Flash is the intended variant, then verify effort and bundle. |
| [ ] | Kimi-K3 | Medium | No matching paper row or delivered campaign. |
| [x] | GLM 5.3 Flash | Medium | Collected 2026-10-19/21 via an OpenAI-compatible gateway (`zai-org/glm-5.3-flash`, medium for actor and simulator, Astra low judge): [results/glm-5.3-flash-actor-glm-5.3-flash-simulator-astra-judge-medium/trial-1](../results/glm-5.3-flash-actor-glm-5.3-flash-simulator-astra-judge-medium/trial-1/README.md), branch `results/qwen3.8-27b-glm-5.3-flash-medium`. 947/1,000 finished (893 scored submissions, 54 finished without a submission and scored zero); 53 unresolved execution failures; mixed actor cap 12,288→16,384 during repair and one disclosed `--retry-missing` scientific-outcome repair pass (see bundle README). |
| [ ] | Grok 4.6 | Medium | No matching paper row or delivered campaign. |
| [x] | Qwen 3.8 27B | Medium | Collected 2026-10-19/21 via an OpenAI-compatible gateway (`qwen/qwen3.8-27b`, medium for actor and simulator, Astra low judge): [results/qwen3.8-27b-actor-qwen3.8-27b-simulator-astra-judge-medium/trial-1](../results/qwen3.8-27b-actor-qwen3.8-27b-simulator-astra-judge-medium/trial-1/README.md), branch `results/qwen3.8-27b-glm-5.3-flash-medium`. 984/1,000 finished (913 scored submissions, 70 finished without a submission and scored zero, 1 grading pending); 16 unresolved execution failures; mixed actor cap 12,288→16,384 during repair and one disclosed `--retry-missing` scientific-outcome repair pass (see bundle README). The earlier local low-effort vLLM campaign is separate. |
| [ ] | Qwen 3.8 Flash | Medium | No matching paper row or delivered campaign; separate from Qwen 3.8 27B. |
| [ ] | DeepSeek V4.1 | Medium | Historical Flash cost pilot only; resolve the requested variant and collect a full medium campaign. |
| [ ] | MiniMax M3 | Medium | No matching paper row or delivered campaign. |

For each entry, the running agent should:

- [ ] Resolve model/provider ID and medium support; record actor/simulator settings and judge disposition.
- [ ] Confirm the frozen 200-question panel and five exact persona prompts.
- [ ] Collect all 1,000 episode slots and repair execution failures without selecting favorable outcomes.
- [ ] Save complete traces, final submissions, grading inputs and provenance to `results/<model-and-role-slug>-medium/trial-1/`.
- [ ] Verify hashes/coverage, commit and push the bundle, then add its path, branch and commit to the model row above.

Only mark a model done when its complete collection bundle is available in the pushed repository and the requested configuration is verified. Final scoring/CIs may remain pending with our team.

### 1. Freeze inputs and identify the model roles

- Use `configs/main_run/selection.csv`: exactly 40 questions each from ASI, BixBench, DiscoveryBench, EXP, and SciConvBench. Do not sample a new panel or replace difficult tasks.
- Run `persona_off`, `candidate_155`, `candidate_001`, `candidate_003`, `candidate_046`. Use the exact files in `configs/main_run/personas/`; inject them into the simulator only. IDs remain the authoritative keys even if figures use descriptive aliases.
- Final paper comparison configuration: **actor = target model; researcher/simulator = target model; judge = GPT-6 Astra, low reasoning**. The model-expansion checklist above requests **medium** effort for actor and simulator. The common Astra judge applies wherever the native evaluator uses a model; deterministic evaluation remains deterministic. Record exact provider model IDs and resolved settings for every role; the actor name alone is insufficient. Final Astra grading may be performed by our team after collection. Preserve all submissions and evaluator inputs needed for that pass; mark provisional scores and pending grading explicitly.
- Pin the repository/runtime version, source revisions, prepared inputs, persona hashes, reasoning/decoding settings, token limits and interaction limits. Use a distinct run directory for every model/configuration/trial. Current SciConv is not interchangeable with earlier protocol versions.
- Restore the tracked [frozen preparation bundle](../configs/main_run/frozen/astra-20260929-v1/README.md) after downloading the pinned public assets. It includes all 200 prepared tasks and the final EXP cards; no EXP extraction cache or new preparation inference is needed. `scripts/restore_main_preparation.py` verifies asset checksums, rebases machine-specific paths and writes `preparation_receipt.json`. Include that receipt in the delivered provenance. The bundle freezes inputs, not runtime code; record the actual protocol revision separately.
- Reusing only the EXP cache does **not** guarantee identical preparation across models: its key includes model settings. Use validated frozen prepared packages and `--require-prepared` for a comparable new-model run. Do not silently regenerate missing packages with the target model.

### 2. Install and run

From the repository root:

```bash
bash scripts/setup_main.sh
.venv/bin/python scripts/check_main.py
.venv/bin/python scripts/run_main.py --help
```

Setup requires Linux, Python 3.12+, `uv`, Bubblewrap and access to the pinned benchmark assets. It makes no LLM calls. Configure credentials privately in `.env` or the process environment; never put them in commands saved to reports or result archives. Install the analysis dependencies separately if computing the table locally: `Experiment/shared/requirements-notebooks.txt`.

**Important launcher semantics:** `--model` supplies the default for **all three roles**, including the judge. `--actor-model` and `--researcher-model` override those two roles only. `--provider` is currently shared by all roles; there is no CLI flag for a separate judge provider. Do not assume `--model TARGET` preserves Astra judging.

The existing Sol/Astra launcher pattern below shows explicit medium overrides for actor/simulator (verify model support before execution). Sol 5.6 is an example of the existing route, not completion of the requested GPT-6 Sol entry:

```bash
RUN_DIR="$PWD/runs/main/sol-self-astra-trial-1"
python scripts/restore_main_preparation.py --run-dir "$RUN_DIR"
.venv/bin/python scripts/run_main.py \
  --run-dir "$RUN_DIR" --workers 30 --provider openai \
  --model gpt-6-astra --reasoning-effort low \
  --actor-model gpt-5.6-sol --actor-reasoning-effort medium \
  --researcher-model gpt-5.6-sol --researcher-reasoning-effort medium \
  --require-prepared
```

For SLURM, use the **same flags**, with `RUN_DIR` exported to the submission script:

```bash
RUN_DIR="$PWD/runs/main/sol-self-astra-trial-1" WORKERS=30 \
bash scripts/submit_main.sh 1 \
  --provider openai --model gpt-6-astra --reasoning-effort low \
  --actor-model gpt-5.6-sol --actor-reasoning-effort medium \
  --researcher-model gpt-5.6-sol --researcher-reasoning-effort medium \
  --require-prepared
```

Use either local execution or SLURM, not both for the same directory. This submits 30 CPUs and 128 GB host RAM; account/partition/time limit are environment overrides. These commands run paid episodes, not a smoke test. Check the generated `configs/*.json` for all role identities and budgets.

For another target model:

- Verify its supported reasoning and API/tool/structured-output settings; do not relabel an unsupported mode as `low`.
- OpenRouter is supported by `--provider openrouter`, using `OPENROUTER_API_KEY` and provider catalog IDs. It applies to the judge too. Use a valid Astra route on that provider only if actually available. Otherwise mixed-provider role support or a documented Astra judge-only regrade must be implemented before claiming the common-judge row. No generic regrade command is supplied by `run_main.py`.
- The OpenAI EXP accounting code currently recognizes only Astra and Sol prices. A different OpenAI target needs verified accounting support; do not bypass the guard or substitute a different model's price.
- The local Qwen launcher in [qwen_vllm.md](qwen_vllm.md) currently runs **Qwen in all three roles**. Its scores require Astra regrading for the paper's common-judge configuration. It is not a drop-in common-judge main-table run.

### 3. Resume, repair, and define collection completion

Rerun the exact command/run directory to resume. Add `--retry-infrastructure` for technical failures. `--actor-max-tokens` (default 12,288, the protocol cap) changes only the actor output cap; because the runner refuses configuration changes inside an existing run directory, a raised cap needs a copy of the run directory and must be reported as a mixed-cap repair (per-attempt caps are recorded by `scripts/export_main_bundle.py`). Finished outcomes, including legitimate scientific failures/non-submissions, are retained. `--retry-missing` deliberately reruns missing submissions; do not use it as the default completion policy or select the highest-scoring attempt. Preserve every attempt and report any scientific-outcome repair separately. A new independent trial requires a new directory, not a repair pass.

Check `progress.json`, `preparation_errors.json`, each episode's `state.json`, and native result/evaluation status. A stale `results.json` or a Slurm exit code alone is not sufficient. There must be:

- 1,000 unique `(benchmark, task_id, persona, trial)` slots; 200 per setting, 40 per benchmark per setting.
- No missing preparation, unstarted, interrupted actor/simulator runs, or unresolved actor/simulator infrastructure-error slots in a completed collection. A grading-only failure can be delivered as `grading_pending` if the full actor/simulator episode and all grading inputs are intact; identify it separately from execution failure.
- An execution/termination record and explicit grading disposition for every slot; include native results if already produced. Pending scores are null with a reason, not fabricated zeros. `finished` does not mean correct. Preserve zero scores and legitimate missing submissions; technical/evaluation errors are unavailable until repaired, not scientific zeros.
- An explicit endpoint/attempt map linking every exported score to the corresponding conversation and final submission. Never silently mix attempts or choose the best score.

On quota/authentication failure, resolve the cause before archiving `fatal_api.json` and resuming. For separate one-persona jobs, use `--arms ARM --standalone-arm`, separate run directories, and the same validated prepared inputs; merge by keys, not row order.

### 4. Metric contract for our receiving analysis team (not a runner deliverable)

| Main-table column | Episode value and aggregation |
|---|---|
| Persona-off performance | Native score on 0–100 for `persona_off`; average trials within question, questions within benchmark, then benchmarks equally. |
| Mean Persona Performance | Same score and weighting, calculated separately for each of the four injected personas, then average the four equally. Excludes off. |
| Fact recovery (%) | `100 × evaluation.metrics.entity_recovery` on eligible **SciConv disambiguation** episodes, before intent gating. Include successes and failures; do not substitute all-facts-complete rate, task success, or a failure-conditioned subset. Average eligible repeats and questions, then the four injected personas equally. |
| Self-repetition (%) | Actor-only lexical repetition within one conversation, using the six-word / three-aligned-position matcher below. Average eligible later messages per episode, trials per question, questions per benchmark, represented benchmarks equally, and four personas equally. |

Native performance mapping is implemented in `scripts/export_trial1_traces.py:score`: ASI = `100*score/max_score`; Bix = `100*correct`; Discovery = `100*final_score`; SciConv = `100*FRR`; EXP = `gated_coverage_mean` (already 0–100, with the existing final/initial selection rule). A legitimate `missing_submission` is zero. Preserve evaluator version and native metrics so mappings can be audited.

Self-repetition details:

1. Use the role-specific shared messages selected by `Experiment/09_offline_metric_suite/code/self_repetition.py:messages`: actor `agent_handoff.payload.answer` for non-SciConv; `researcher_question.payload.question` for SciConv. Exclude private reasoning, simulator text, tool output, system/persona prompts, and final SciConv specification.
2. Use `word_repetition.py:tokenize`: strip fenced code and blockquote lines, NFKC/casefold; Han dictionary segmentation with jieba (`HMM=False`), Unicode word runs otherwise. Preserve the same dependency/dictionary versions.
3. Retain messages with at least **nine word tokens**, and require at least **two** such actor messages. Otherwise the metric is unavailable, not zero.
4. Slide **six-word** windows. A current window is a match if any six-word window in an earlier eligible actor message matches at least **three of the six corresponding positions**. This is not unordered word overlap, semantic similarity, or the older exact four-word definition.
5. For each later message compute matched windows / all windows × 100, then average those message rates. Use `max_aligned_matches` and `best_matches` from the recorded Experiment 09 notebook, as loaded by `model_scorecard.py`. Do not run `word_repetition.py`'s default four-word analysis as a substitute. This six/three definition was selected exploratorily in the original analysis; keep it fixed across new models.

For each metric, use that model's **own available questions observed under all five settings**; do not intersect questions across different models. Do not discard a question because its native score is zero. Record metric-specific exclusions and support; the full 200-task inventory does not imply 200 questions for repetition or fact recovery. The frozen panel has 20 SciConv disambiguation questions (100 condition episodes); verify coverage by IDs rather than assuming every SciConv task is eligible.

95% CIs: use 20,000 percentile bootstrap draws, resampling whole **study clusters within each benchmark**, keeping every question/persona/trial record of a sampled cluster together. Recompute the complete aggregation in each draw; use the 2.5th/97.5th percentiles. Reuse `Experiment/shared/analysis_utils.py:bootstrap_weights` (seed `20261004`) and `Experiment/02_performance_and_fields/code/model_scorecard.py:panel`. Intervals condition on available trials; one trial does not estimate unseen rollout variability. Do not bootstrap individual turns as independent samples or average CI endpoints.

### 5. Collect and upload a complete result bundle

Retain the complete raw run locally. Export a compact machine-readable bundle **inside the repository at `results/<model-slug>/trial-<N>/` and push it**. Use a model/configuration slug that distinguishes actor and simulator choices. Do not stop after saving ignored `runs/` files, attaching an external ZIP, or posting aggregate scores. Filenames below define the handoff format; the runner does not create this export, but `scripts/export_main_bundle.py --run-dir RUN_DIR --output results/<model-slug>/trial-<N> ...` produces it from any completed main-run directory (generic importer; no inference).

| File/directory | Required contents |
|---|---|
| `README.md` | Exact commands, trial count, actual actor/simulator/judge/provider IDs, reasoning, protocol/version, repair policy, counts, unresolved issues and metric definitions. |
| `provenance/` | Git commit **and dirty diff/source snapshot** if applicable; runtime `code.*.json`, dependency locks, source revisions, actual `configs/`, selection/persona hashes, model-access metadata without credentials, prepared-input content hashes. |
| `episodes.csv` | All 1,000 unique slots with benchmark, task/study/family, arm, trial, selected attempt, runner/native/evaluation status, submitted flag, native score and normalized score when available (null with `grading_pending` otherwise), exclusion reason, termination and interaction counts. |
| `traces/final-results.json` | One selected execution/result record per slot, including available native metric dictionaries, final-submission references and attempt identities. Preserve grading errors/pending status. A score-only CSV is not enough. |
| `traces/shared-events.jsonl` | One record per slot containing ordered original shared events, their types/payload text and sequence/round information. Include empty records with a reason when no messages were produced; never silently drop unsuccessful episodes. |
| `traces/shared-events-index.csv` | All slot keys, selected attempts, JSONL line numbers, event counts and source hashes. |
| `evaluations/metrics.jsonl` | Available native metrics, especially SciConv `entity_recovery`, plus judge/evaluator identity and score disposition for every slot. If not yet graded, retain an explicit pending record and the task facts/evaluator references required to compute it later. |
| `submissions/` | Final actor artifacts needed for a future judge-only regrade, mapped to slot/attempt. Include the actor-produced files/text and a grading-input manifest mapping each slot to its exact prepared task, expected-output/reference assets, evaluator version and hashes. Include portable, redistributable grading inputs under `grading_inputs/`; for restricted assets record a pinned retrieval route or confirmed team-accessible location. An inaccessible absolute path or a final scalar score is insufficient. Do not expose hidden references in public exports. |
| `analysis/metric_episodes.csv` (optional; our team produces this) | Derived per-episode performance/recovery/repetition, eligibility and missingness, plus the extractor source and version. |
| `analysis/model_scorecard.{csv,md,tex}` (optional; our team produces this) | Four means with CI endpoints, plus coverage tables and aggregation/bootstrap metadata. Do not upload these without their inputs. |
| `bundle_manifest.json` | Relative path, byte count and SHA-256 of every delivered file except the manifest itself. |

Also retain actor token-usage and tool-action records as optional supporting data; they are not required columns in the main table. Include them if already logged. Preserve source event text needed for repetition without adding LLM summaries. Raw API logs can contain private context or credentials: exclude credentials and authorize the destination; the public conversation export should omit private evaluator references. Never archive `.env`, API keys, virtual environments, or credentials. Keep any redaction log and hashes linking the export to raw local files.

### 5a. Commit, push, and verify delivery

Use the tracked `results/` directory described in [results/README.md](../results/README.md). Keep readable metadata/indexes there and use per-benchmark/per-persona trace shards if necessary. For large artifacts, compress and split into manageable parts (for example 25 MiB), storing all parts plus reconstruction instructions and original-file SHA-256 in the same result directory. Do not leave a missing payload behind a local path or publish only a Git LFS pointer without uploading its object. Preserve every delivered file in `bundle_manifest.json`.

The agent should finish with a scoped commit and push, for example:

```bash
# Replace the branch/model names with this campaign's names.
git switch -c results/model-slug-trial-1
# Populate and verify this directory before staging.
git add -- results/model-slug/trial-1
# Confirm staged paths contain only this campaign's reviewed export.
git diff --cached --stat
git commit -m "Add model-slug five-setting trial-1 results"
git push -u origin results/model-slug-trial-1
git rev-parse HEAD
git ls-remote origin refs/heads/results/model-slug-trial-1
```

Use an existing assigned results branch if one is provided. Do not force-push or stage unrelated workspace files. Before committing, verify unique slot keys, artifact paths, manifest hashes, and absence of credentials. Ensure the destination's visibility is appropriate for the included task assets/references. If access is blocked, report the exact blocker and retained local paths; do not claim delivery complete.

After pushing, confirm the remote branch points to the delivered commit. Report the repository-relative results path, branch, commit hash, collection counts, pending-grading count, and any missing artifacts. A fresh checkout of that commit must recover every submitted trace/artifact (including any compressed parts). The receiving agent checks manifest hashes and all 1,000 mappings. The prior truncated self-Haiku ZIP is why archive/file verification is mandatory. A plain push of ignored `runs/` directories does not upload their contents; the tracked `results/` export is required.

### 6. Reproduce the table on the receiving side

Our team first validates the pushed bundle, performs any pending native/Astra grading using the preserved submissions (without rerunning actor/simulator), then extracts metrics offline and adapt its per-episode rows to `model_scorecard.panel` (`source`, `task_id`, `study_id`, `arm`, `trial`, numeric metric or `None`). Preserve the definitions above and save the derived rows, coverage and provenance before exporting the row to the notebook/paper.

**Current implementation limitation:** `model_scorecard.py` is wired to historical Astra files and the recovered self-Haiku score CSV, with Haiku behavioral means/CIs read from `haiku_self_reported_metrics.json`. It is **not a generic `--run-dir` importer**. Running it unchanged will regenerate those existing rows, not analyze a new model. `scripts/export_trial1_traces.py` likewise hardcodes historical Astra campaigns. The receiving analysis agent must add a bundle-specific loader (or a general importer), reuse the existing metric functions, and verify key/coverage parity. Do not overwrite or relabel another campaign's cached metrics as the new model.

The current Haiku–Haiku behavioral values are collaborator-reported aggregates; their raw records have not been locally reproduced. They are not a template for omitting traces from future deliveries. The running agent’s handoff is complete when the collection bundle has been pushed and verified, with enough data for our team to grade and compute all four columns and CIs without new actor/simulator inference. Grading calls may still be required; the running agent need not compute the final table. Fresh stochastic runs need not match historical paper numbers exactly, even under the same protocol.

---


## Current run and reading order

1. [Main-run guide](MAIN_RUN.md): the authoritative fresh-run configuration and commands.
2. [Root README](../README.md): main-run overview and the three analysis levels—performance, semantic diversity, and behavioral diversity.
3. [Setup and migration](reproducibility.md), [interaction protocol](interaction_protocol.md), and [persona injection](personas.md).
4. [Paper plan](design/benchmark_paper_plan.md) and [Experiment workspace](../Experiment/README.md): evolving analysis plans and historical collection records, not launcher defaults.
5. [Historical pilot report](../reports/full_persona_v2/README.md) and [case studies](../reports/full_persona_v2/case_studies.md): preserved selection provenance.

The main run is **200 questions (40 each from five benchmarks) × five settings (off / 155 / 001 / 003 / 046)**: **1,000 episodes per trial**, or **3,000 across three fresh trials**. Actor, simulator, and judge default to OpenAI GPT-6 Astra with low reasoning. The SLURM launcher defaults to 30 workers / 30 CPUs and 128 GB RAM. These are planned fresh-run totals, not completed-result counts.

## Historical 30-persona pilot: preserve these records

`reports/full_persona_v2/` contains 310 recorded traces: 30 personas × ten questions, plus ten persona-off baselines. The folder also contains exact injected profiles, indexes, a machine-readable snapshot, and frozen experiment metadata. The original report, scores, and traces were not regenerated during cleanup.

`configs/full_persona_v2/` contains the cohort/prompt hashes, ten source-task IDs and exact persona-off model/protocol configs. Recover all 30 raw identity blocks with:

```bash
python3 scripts/restore_full_persona_cohort.py --check
python3 scripts/restore_full_persona_cohort.py
```

The second command creates the ignored cohort directory on a fresh checkout and refuses to overwrite an existing directory. It extracts the published identity blocks verbatim and checks every original prompt hash. It makes no model calls.

The completed run has 265 scored/completed episodes, 43 missing submissions and two technical/evaluator errors. Its published ranking uses eight common questions and a fixed baseline of 26.01%. Keep the original missing-submission convention and tables. New experiments get new run directories and reports.

Important reading notes: some frozen trace headers incorrectly say persona disabled; the recorded API system messages contain the actual identity. Raw-log links inside frozen traces are relative to their original local run directories; they do not resolve on GitHub. Whitespace word counts undercount Chinese replies. Some EXP judge/monitor decisions are inconsistent. The case-study report identifies exact examples; these are analysis concerns, not reasons to edit historical records.

## Running or handing off the main experiment

- Use `configs/main_run/selection.csv` and the four exact profiles in `configs/main_run/personas/`. Do not resample questions or restore the superseded 70/50/40/36/4 allocation.
- Run `scripts/setup_main.sh`, configure `OPENAI_API_KEY`, and validate inputs with `scripts/check_main.py`. Launch with `scripts/run_main.py` or the separate `scripts/submit_main.sh`.
- Give each independent trial its own run directory. Preserve the EXP extraction cache across sequential trials. The guide documents `afterok` dependencies, resume behavior, and repair flags.
- Keep historical protocols, original outcomes, and repair attempts distinct. Current SciConv behavior is not interchangeable with pre-change traces. Inspect saved manifests/configurations when analyzing past runs.
- The main runner does not require analysis notebooks. Existing analysis has uneven trial coverage; the five displayed settings do not imply that every setting has three completed historical trials.
- Treat job IDs and statuses in old plans as dated snapshots. No live scheduler state is asserted by this document.

## MLAgentBench track

The [MLAgentBench adapter](adapters/mlagentbench.md) converts 12 tasks (3 excluded for lacking a native verifier) with two hand-reviewed CPU pilots, `vectorization` and `cifar10`, a native `get_score` evaluator, a hashed CPU runtime lock and a baseline/summary script. Only local smoke runs with a non-team model and transport exist so far. It is not part of the frozen 200-question main run. The [IdeaGene track](adapters/ideagene.md) is also separate; adding an adapter does not add questions to the main-run selection.

## Historical cleanup validation (2026-09-27)

All 375 pre-existing report/profile/trace files were checked byte-for-byte, and the README results tables and future paper plan are unchanged. All 30 prompt hashes and restoration overwrite protection passed; the distributable-file/link check passed.

At that cleanup snapshot, the offline suite produced 171 passes, 26 skips, three legacy persona metadata-fixture failures, and six runtime setup errors because Bubblewrap was not on the system path. All six runtime tests passed when rerun with the existing local Bubblewrap through `PERSONASCIENCEBENCH_BWRAP`. The three failures are `test_legacy_rendering_and_metadata_match_the_supplied_repository` (enabled legacy profiles); their expected metadata/hashes disagree with current records. Their code and fixtures were not changed by cleanup. Source-dependent tests skipped at their expected fixture paths. No paid benchmark runs were launched.

## Local assets to transfer separately

A Git clone includes all published Markdown traces and the exact injected prompts. It does **not** include these ignored assets from the current machine:

| Local path | Why transfer it? |
|---|---|
| `runs/full-persona-v2-two-20260926/` | Original API/event JSON, configurations, submitted code/results and evaluator records; about 2.1 GiB |
| `data/conversion_catalog/`, `data/design_catalog/`, `data/exp_bench/` | Converted task cards, source provenance and cached EXP extraction |
| `data/persona_case_study/full_persona_v2/`, `full_profile_selection_v2/`, `action_selection_v1/` | Original profiles, field audits and selection provenance; the last directory is an input to rescreening the original 300, not an active experiment |
| `external/persona_case_study/` | Original sample and pinned MatrAIx renderer, if rebuilding the selection |
| `external/sources/` | Pinned sources and benchmark assets; Bix data account for most local disk use |

Use an approved file-transfer channel for those directories. Configure credentials independently on the new host. Recreate virtual environments. Prepared packages have machine-specific paths: for a comparable campaign, transfer/rebase the frozen packages as described above; regenerating task content defines a new preparation version. Copy the raw completed run as historical evidence, not as a portable resume queue.

Superseded local outputs were moved to the sibling folder `siyangwu_branch.cleanup-archive-20260927/`, with a restore manifest. They are outside the checkout and unnecessary for the next study. Removed tracked drafts remain recoverable in Git history at commit `0c54c13`. Current datasets, runtime environments, original sampling provenance and the completed run remain intact locally.
