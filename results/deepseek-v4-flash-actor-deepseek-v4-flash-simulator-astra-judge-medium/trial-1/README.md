# DeepSeek V4 Flash actor / DeepSeek V4 Flash simulator / GPT-6 Astra judge — medium reasoning, trial 1

Delivered scope: one trial, 200 frozen questions × five settings = 1000 episode slots. Runner status: **961 finished**, **39 unresolved execution failures**, 0 other.

`finished` is an execution status, not a correct-answer label; native scores are in `episodes.csv` and `evaluations/metrics.jsonl`. Unresolved slots carry an explicit `failure_class`; they are unavailable, not scientific zeros. Legitimate missing submissions are scored zero per the handoff contract.

## Model roles (as transmitted)

| Role | Model | Reasoning | Output cap (shared / EXP) |
|---|---|---|---|
| actor | `deepseek-ai/deepseek-v4-flash` | medium | 12288 / 12288 |
| researcher | `deepseek-ai/deepseek-v4-flash` | medium | 8192 / 8192 |
| judge | `openai/gpt-6-astra` | low | 4096 / 4096 |

Provider label in configs: `openrouter` (see notes below for the actual serving path). Frozen preparation `astra-20260929-v1`; selection sha256 `746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`.

## Counts

| Setting | finished | infrastructure_error |
|---|---:|---:|
| persona_off | 198 | 2 |
| candidate_155 | 192 | 8 |
| candidate_001 | 190 | 10 |
| candidate_003 | 189 | 11 |
| candidate_046 | 192 | 8 |

| Benchmark | finished | infrastructure_error |
|---|---:|---:|
| asibench | 170 | 30 |
| bixbench | 192 | 8 |
| discoverybench | 199 | 1 |
| expbench | 200 | 0 |
| sciconvbench | 200 | 0 |

### Grading disposition

| Disposition | Slots |
|---|---:|
| scored | 838 |
| missing_submission_scored_zero | 123 |
| execution_failed:infrastructure_other | 28 |
| execution_failed:researcher_output_invalid | 5 |
| execution_failed:actor_output_length_cap | 3 |
| execution_failed:actor_http_400 | 2 |
| execution_failed:infrastructure_no_error_text | 1 |

### Unresolved execution failures by class

| Class | Slots |
|---|---:|
| infrastructure_other | 28 |
| researcher_output_invalid | 5 |
| actor_output_length_cap | 3 |
| actor_http_400 | 2 |
| infrastructure_no_error_text | 1 |

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

- Actor and simulator (researcher) were served by an internal OpenAI-compatible inference gateway through a local adapter (`provenance/gateway_adapter_nvgw_api.py`) that the benchmark addresses as its `openrouter` provider. The adapter forwards `/chat/completions` unchanged apart from: retry with backoff on 408/429/5xx; a `Respond in JSON.` user-message note when a JSON response format is requested and no user message mentions JSON (the gateway otherwise rejects the request); and a retry of an intermittent gateway HTTP 400 that rejects `reasoning_effort=medium` on some replicas. Request logging stays on the operator machine.
- Model identifiers in this export are normalized by stripping the gateway's internal routing prefix. The transmitted settings were `reasoning_effort=medium` for actor and simulator and `low` for the GPT-6 Astra judge.
- Pricing fields are zero because the gateway does not publish per-token prices; EXP budget charges are therefore uninformative.

### Protocol caps and repair policy

- Protocol defaults throughout: actor 12,288 output tokens, simulator 8,192, judge 4,096, 60 actor steps, 600 s request timeout (client-side timeout raised to 1,900 s via `PSB_LOCAL_CLIENT_TIMEOUT`; the adapter's upstream timeout was 1,800 s). Unlike the GLM 5.3 Flash and Qwen 3.8 27B cohorts, **no actor-cap raise and no `--retry-missing` scientific-outcome rerun** were applied here: every slot ran at protocol caps, and slots that finished without a submission are scored zero per the benchmark contract and left as they are.
- Main run on 2026-10-22 at 80 workers, followed by four `--retry-infrastructure` passes at 40 workers (2026-10-22 to 2026-10-25) in the same run directory. A retry pass re-runs only slots whose latest attempt ended in `infrastructure_error`; it never touches finished slots. Two of the passes (2026-10-22 evening and 2026-10-23) were cut short when the operator's scratch volume filled up (`ENOSPC` in the runner); the attempts in flight at that moment have no result files, are listed in `provenance/attempts.csv`, and were re-run by the next pass. Passes 3 and 4 ran to completion. Every attempt is retained with its status; the runner's recorded (latest) attempt is the selected endpoint and nothing was selected by score.

### Unresolved slots

Remaining `infrastructure_error` slots are model-behaviour or gateway faults that repeated across all passes. They are listed with a `failure_class` in `episodes.csv` and left unavailable, not scored. The model-specific notes below give the breakdown.
### DeepSeek V4 Flash specifics

- The requested model was "DeepSeek V4.1 Flash"; the gateway catalog has no such entry, so the campaign ran on DeepSeek V4 Flash (`deepseek-ai/deepseek-v4-flash`), the only DeepSeek Flash variant available.
- Final cohort: 961 of 1,000 slots finished (838 scored submissions, 123 finished without a submission and scored zero); 39 unresolved execution failures.
- The dominant failure is an actor completion that carries reasoning content but no message text and no tool calls (`finish_reason=stop`), which the runner rejects as `completion must contain text`. It occurred on roughly one percent of actor calls in the main run, independent of the output cap, and because a long episode makes many calls it hit 135 slots in the main run; retries cleared most of them, and 28 unresolved slots remain. It is reported as a model-behaviour fault.
- Other unresolved slots: 4 simulator decisions citing invalid fact IDs, 3 actor truncations at 12,288 tokens, 1 simulator decision failing schema validation (missing `evidence`), 1 non-retryable gateway HTTP 400, and 2 without an error message.
- Unresolved slots by benchmark: ASIBench 30, BixBench 8, DiscoveryBench 1.

