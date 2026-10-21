# GLM 5.3 Flash actor / GLM 5.3 Flash simulator / GPT-6 Astra judge — medium reasoning, trial 1

Delivered scope: one trial, 200 frozen questions × five settings = 1000 episode slots. Runner status: **947 finished**, **53 unresolved execution failures**, 0 other.

`finished` is an execution status, not a correct-answer label; native scores are in `episodes.csv` and `evaluations/metrics.jsonl`. Unresolved slots carry an explicit `failure_class`; they are unavailable, not scientific zeros. Legitimate missing submissions are scored zero per the handoff contract.

## Model roles (as transmitted)

| Role | Model | Reasoning | Output cap (shared / EXP) |
|---|---|---|---|
| actor | `zai-org/glm-5.3-flash` | medium | 16384 / 16384 |
| researcher | `zai-org/glm-5.3-flash` | medium | 8192 / 8192 |
| judge | `openai/gpt-6-astra` | low | 4096 / 4096 |

Provider label in configs: `openrouter` (see notes below for the actual serving path). Frozen preparation `astra-20260929-v1`; selection sha256 `746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`.

## Counts

| Setting | finished | infrastructure_error |
|---|---:|---:|
| persona_off | 191 | 9 |
| candidate_155 | 189 | 11 |
| candidate_001 | 189 | 11 |
| candidate_003 | 188 | 12 |
| candidate_046 | 190 | 10 |

| Benchmark | finished | infrastructure_error |
|---|---:|---:|
| asibench | 151 | 49 |
| bixbench | 196 | 4 |
| discoverybench | 200 | 0 |
| expbench | 200 | 0 |
| sciconvbench | 200 | 0 |

### Grading disposition

| Disposition | Slots |
|---|---:|
| scored | 893 |
| missing_submission_scored_zero | 54 |
| execution_failed:actor_output_length_cap | 52 |
| execution_failed:researcher_output_invalid | 1 |

### Unresolved execution failures by class

| Class | Slots |
|---|---:|
| actor_output_length_cap | 52 |
| researcher_output_invalid | 1 |

## Bundle layout

- `episodes.csv`: all 1,000 slots, selected attempt, statuses, submitted flag, normalized native score (blank when pending/unavailable), grading disposition, failure class, interaction counts, trace line number, submission directory, state hash.
- `traces/final-results.json`: the full selected `state.json` record per slot (sanitized), with native result dictionaries.
- `traces/shared-events.<benchmark>.jsonl` (five shards) + `shared-events-index.csv`: ordered shared actor/simulator/controller events per slot. Actor tool commands and tool results are private sandbox traffic and are omitted (counts retained). Empty records carry a reason.
- `evaluations/metrics.jsonl`: native metrics (including SciConv `entity_recovery`), evaluator version, judge identity, errors and an explicit disposition for every slot.
- `submissions/<arm>/<task_key>/`: final actor submissions (`submission.json`, `submission_hashes.json`, `submitted_artifacts/`, EXP `initial_design.json`) plus sanitized `actor_result.json`, `evaluation.json`, `result.json`; `submissions/manifest.jsonl` maps every slot to its attempt and files with hashes. Text files (JSON, scripts, logs) are passed through the same sanitizer as every other exported text, so local paths and identifiers are normalized; when that changes a file, the manifest records `sanitized: true` with `sha256_original` next to the exported `sha256`. Binary artifacts are copied verbatim. Files above 25 MiB are hash-listed, not copied.
- `grading_inputs/manifest.json`: frozen preparation id/hashes and the restore route for prepared task packages and evaluator references.
- `provenance/`: run manifest, actual configs, runtime code hashes, preparation receipt, selection and persona hashes, git commit and source diff, lockfile hashes, every attempt per slot (`attempts.csv`), and operator files listed below.
- `bundle_manifest.json`: byte size and SHA-256 of every delivered file.

Reproduce the export offline with `python scripts/export_main_bundle.py --run-dir RUN_DIR --output NEW_DIRECTORY ...`; it makes no model calls and refuses to overwrite an existing export.

## Campaign notes

### Serving path and identifiers

- Actor and simulator (researcher) were served by an internal OpenAI-compatible inference gateway through a local adapter (`provenance/gateway_adapter_nvgw_api.py`) that the benchmark addresses as its `openrouter` provider. The adapter forwards `/chat/completions` unchanged apart from: retry with backoff on 408/429/5xx; a `Respond in JSON.` user-message note when a JSON response format is requested and no user message mentions JSON (the gateway otherwise rejects the request); and, from the third repair pass on, a retry of an intermittent gateway HTTP 400 that rejects `reasoning_effort=medium` for GLM 5.3 Flash (see below). Request logging stays on the operator machine.
- Model identifiers in this export are normalized by stripping the gateway's internal routing prefix. The transmitted settings were `reasoning_effort=medium` for actor and simulator and `low` for the GPT-6 Astra judge. Medium is accepted by the gateway for both target models; see the GLM note below for the intermittent rejection.
- Pricing fields are zero because the gateway does not publish per-token prices; EXP budget charges are therefore uninformative.

### Protocol caps and repair policy

- Protocol defaults: actor 12,288 output tokens, simulator 8,192, judge 4,096, 60 actor steps, 600 s request timeout (client-side timeout raised to 1,900 s via `PSB_LOCAL_CLIENT_TIMEOUT`; the adapter's upstream timeout was 1,800 s).
- Main run (2026-10-19, 50 workers) at protocol caps. Repair pass 1 (`--retry-infrastructure`, same directory) after fixing two operator-side faults: (a) judge requests in JSON mode were rejected by the gateway (`judge HTTP 400`), (b) the sandboxed ASI evaluator could not import `litellm` because the virtual-environment interpreter symlink was dangling inside the sandbox. Neither fault changes model behaviour; both are recorded in `provenance/attempts.csv`.
- After pass 1 the dominant remaining failure was the actor hitting the 12,288-token output cap. On the operator's instruction the actor cap was raised **a little, to 16,384**, for the remaining failed slots only. To keep the protocol-cap run intact, the run directory was copied (episode records hard-linked) into this `cap16k` directory and repair passes 2–3 ran there with `--actor-max-tokens 16384` (a new `scripts/run_main.py` option in this change). Consequently this cohort is **mixed-cap**: every slot that finished before the raise used 12,288 (see `actor_max_tokens` per attempt in `provenance/attempts.csv`); slots recovered in passes 2–3 used 16,384. Simulator and judge caps were never changed. The original protocol-cap configs are included as `provenance/*.original_cap12288_persona_off.*.json`; the protocol-cap run directory remains available on the operator machine.
- **Scientific-outcome repair (disclosed separately).** After pass 3 a large share of finished slots had no actor submission (60-step cap reached, actor stopped without handoff, or the simulator stopped the episode) and were scored zero per the benchmark contract. On the operator's instruction one `--retry-missing` pass (pass 4, 2026-10-21, 50 workers, 16,384 actor cap) re-ran **only** those slots at otherwise unchanged protocol limits; it is a rerun of model behaviour, not an infrastructure fix, and is reported here as such. The rerun itself produced new `infrastructure_error` endpoints (mostly actor truncation at 16,384) for slots whose earlier attempt had finished without a submission; further `--retry-infrastructure` passes (one for GLM 5.3 Flash, two for Qwen 3.8 27B, the second at 25 workers after HTTP 429s) gave those slots a clean completion attempt. Every attempt is retained in `provenance/attempts.csv` with its status; the runner's recorded (latest) attempt is the selected endpoint and nothing was selected by score. Remaining `infrastructure_error` slots whose earlier attempt finished without a submission are reported as execution failures, not as zeros.

### Unresolved slots

Remaining `infrastructure_error` slots are model-behaviour or gateway faults that repeated across passes: actor output still truncated at 16,384 tokens, simulator (researcher) output failing schema validation or citing invalid fact IDs, and a few non-retryable gateway 400s. They are listed with a `failure_class` in `episodes.csv` and left unavailable, not scored.
### GLM 5.3 Flash specifics

- The gateway intermittently answers `model glm-5.3-flash does not support reasoning effort "medium": supported values are max, low, high` with HTTP 400 while the same request succeeds on retry; probes of ten consecutive medium requests all pass. 49 slots failed on that error in repair pass 2 before the adapter was taught to retry it; all cleared in pass 3. The effective setting for every finished slot is therefore `medium`.
- Actor truncation at the output cap is the dominant unresolved failure for this model (118 slots at 12,288 after pass 1; 49 remained at 16,384 after pass 3; 52 remain after the retry-missing repair and its follow-up pass, plus one simulator schema failure).
- Retry-missing pass: 106 slots without a submission were re-run; the final cohort has 893 scored submissions and 54 finished slots without a submission (scored zero), versus 841 and 106 before the repair.

