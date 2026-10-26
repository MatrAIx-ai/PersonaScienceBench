# Qwen 3.8 Flash actor / Qwen 3.8 Flash simulator / GPT-6 Astra judge — medium reasoning, trial 1

Delivered scope: one trial, 200 frozen questions × five settings = 1000 episode slots. Runner status: **878 finished**, **122 unresolved execution failures**, 0 other.

`finished` is an execution status, not a correct-answer label; native scores are in `episodes.csv` and `evaluations/metrics.jsonl`. Unresolved slots carry an explicit `failure_class`; they are unavailable, not scientific zeros. Legitimate missing submissions are scored zero per the handoff contract.

## Model roles (as transmitted)

| Role | Model | Reasoning | Output cap (shared / EXP) |
|---|---|---|---|
| actor | `qwen/qwen3.8-flash` | medium | 12288 / 12288 |
| researcher | `qwen/qwen3.8-flash` | medium | 8192 / 8192 |
| judge | `openai/gpt-6-astra` | low | 4096 / 4096 |

Provider label in configs: `openrouter` (see notes below for the actual serving path). Frozen preparation `astra-20260929-v1`; selection sha256 `746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`.

## Counts

| Setting | finished | infrastructure_error |
|---|---:|---:|
| persona_off | 154 | 46 |
| candidate_155 | 177 | 23 |
| candidate_001 | 180 | 20 |
| candidate_003 | 185 | 15 |
| candidate_046 | 182 | 18 |

| Benchmark | finished | infrastructure_error |
|---|---:|---:|
| asibench | 154 | 46 |
| bixbench | 161 | 39 |
| discoverybench | 172 | 28 |
| expbench | 191 | 9 |
| sciconvbench | 200 | 0 |

### Grading disposition

| Disposition | Slots |
|---|---:|
| scored | 698 |
| missing_submission_scored_zero | 180 |
| execution_failed:researcher_output_invalid | 64 |
| execution_failed:gateway_transport | 38 |
| execution_failed:infrastructure_other | 9 |
| execution_failed:infrastructure_no_error_text | 8 |
| execution_failed:actor_http_400 | 2 |
| execution_failed:actor_output_length_cap | 1 |

### Unresolved execution failures by class

| Class | Slots |
|---|---:|
| researcher_output_invalid | 64 |
| gateway_transport | 38 |
| infrastructure_other | 9 |
| infrastructure_no_error_text | 8 |
| actor_http_400 | 2 |
| actor_output_length_cap | 1 |

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
### Qwen 3.8 Flash specifics

- Final cohort: 878 of 1,000 slots finished (698 scored submissions, 180 finished without a submission and scored zero); 122 unresolved execution failures.
- The dominant failure is a simulator protocol fault: the researcher-review protocol requires the simulator to answer with exactly one `researcher_decision` tool call, and Qwen 3.8 Flash frequently returns the decision as plain text (often a JSON-looking block, sometimes in Chinese) instead of a tool call. The runner records this as `Expected exactly one researcher_decision tool call`. It affected 280 slots in the main run and still accounts for 70 of the 122 unresolved slots after four retry passes; the failures concentrate in the `persona_off` setting (46 unresolved slots) where the simulator receives no persona context. This is a property of the model's tool-calling under this protocol, not an infrastructure fault, and it is reported as such.
- Gateway read timeouts (`OpenRouter transport failed (ReadTimeout)`, HTTP 504 "Gateway inference timed out" at the adapter) account for 38 unresolved slots: long actor requests exceeded the gateway's own inference timeout and no client-side timeout setting helps. A few further slots failed with HTTP 400 from the upstream model, one with actor truncation at 12,288 tokens, and 11 ended without an error message.
- Unresolved slots by benchmark: ASIBench 46, BixBench 39, DiscoveryBench 28, EXP-Bench 9.

