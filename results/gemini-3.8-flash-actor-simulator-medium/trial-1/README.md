# Gemini 3.8 Flash actor / simulator, medium — trial 1

Status: **partial_graded_checkpoint**. All 1,000 frozen slots and all 1035 original/repair attempts are retained.
Selected final dispositions: `{"scored": 806, "missing_submission": 190, "grading_error": 3, "execution_error": 1}`. Final grading complete: **False**.

Actor and simulator: **Gemini 3.8 Flash actor / simulator, medium**. Final judge: **GPT-6 Astra, low effort**.
Exact collection role IDs/settings: `{"actor": {"model": "gcp/google/gemini-3.8-flash", "provider": "nvidia", "reasoning_effort": "medium"}, "researcher": {"model": "gcp/google/gemini-3.8-flash", "provider": "nvidia", "reasoning_effort": "medium"}, "judge": {"model": "gpt-6-astra", "provider": "openai", "reasoning_effort": "low"}}`.
Actual posthoc judge routing/settings: `{"model": "openai/openai/gpt-6-astra", "provider": "nvidia", "reasoning_effort": "low", "max_tokens": 4096, "timeout": 600, "unsupported_parameters": "omit_and_record"}`.
(The collection judge configuration was deferred; the posthoc route above performed final grading.)
No actor/simulator episodes were rerun for grading. Native rubrics, scoring and EXP integrity gates were retained.
Grading evaluated saved submissions; 1 unresolved execution errors remain unavailable.
Policy refusals skipped at user request: **2**. Their scores remain unavailable, not zero.

`judging/all-attempts.jsonl.gz` maps every original/repair attempt to its native evaluation.
`judging/judgements.jsonl.gz` retains final judge text and token usage, without private reasoning or API prompt bodies.
`judging/collection-only/` preserves the original ungraded indices and checksum manifest.
The original collection history in `repairs/` is unchanged. Final scores use the same selected attempts, never best-score selection.
Exact judge routing, implementation snapshots and effective settings are recorded under `judging/provenance/`.
All posthoc API calls were judge calls; actor and simulator calls repeated: **0**.
`judging/verified-inputs.json` verifies every original grading input hash;
`grading_inputs/native/` preserves native conversation/specification text and artifact manifests.
Non-finite native diagnostics are represented as null with their original values
and source checksum in adjacent `native_score.json.export-receipt.json` files.

Grading command (using the preserved raw run and the recorded runtime):
```bash
.venv/bin/python scripts/grade_collection.py --run-dir /path/to/raw-run --output /path/to/raw-run/grading/astra-low-v1 --env-file /path/to/.env --workers 4
```

## Commands and provenance

Original: `ENV_FILE=/path/to/.env WORKERS=4 bash scripts/run_gemini_nvidia.sh`.
Repairs: same command plus `--retry-infrastructure`. Retries 2 and 3 additionally set
`PSB_NVIDIA_EMPTY_LENGTH_RETRIES=2`: at most two identical-request replays for
empty actor `length` replies below the requested output cap; every response and
usage is logged. Content filters/refusals are not automatically retried.
See the exact repair selections and source snapshots in `provenance/history/`.
The first repair intentionally included four EXP non-submissions that the
coordinator had labeled infrastructure failures. This scientific-outcome repair
is distinguished from technical repairs; the other missing outcomes were retained.
Original-only paper analysis must read attempt 1 from `repairs/all-attempts.jsonl.gz`;
selected endpoints use the latest authorized attempt, never the highest score.

## Files and paths

`episodes.csv`, `traces/final-results.json`, `traces/shared-events.jsonl`, and its
index map every selected slot to an attempt, original shared exchanges, grading
input, and submitted files. `repairs/all-attempts.jsonl.gz` retains all attempts.
Shared conversations exclude private reasoning, tool output and evaluator keys.
`supporting/` retains token accounting (including failed-response repair calls)
and tool actions. Raw authenticated API request payloads are not published.

All explicit `submission_paths`, `artifacts`, and `grading_input` entries are
relative to this bundle's root. Native provenance strings use `@RAW_RUN` or
`@SOURCE_REPOSITORY`; those are not payload download links. Sealed artifact bytes
are content-addressed under `submissions/files/`. EXP design checkpoints retain
initial/final labels as recorded; a nonexistent final design is not invented.
Their embedded SDK traces omit private reasoning and system-prompt records,
while preserving original scientific actions and observations with source indices.

`grading_inputs/task_snapshots/` contains controller-only facts/evaluator data;
keep it private to the receiving grading team and out of actor mounts. This
bundle is prepared for the existing team repository, not a public dataset release.
The frozen metadata bundle is included in `grading_inputs/frozen/`. Public
source/data dependencies have pinned download routes and hashes in its manifest,
source manifests and acquisition scripts; virtual environments and downloaded
input copies are excluded. On the receiving host, install the recorded runtime
and acquire pinned public assets, then restore the frozen bundle with:

```bash
.venv/bin/python scripts/restore_main_preparation.py --bundle /path/to/this/bundle/grading_inputs/frozen --run-dir /path/to/new/reference-run
```

Replace `@SOURCE_REPOSITORY` in task snapshot path fields with that receiving
checkout root. A native grader should load the listed snapshot and submission,
resolving artifact values relative to this bundle root. Every input/output is
mapped in `grading_inputs/manifest.json`. No actor/simulator rerun is required.
ASI reference directories use pinned acquisition and presence checks where the
historical bundle lacked tree hashes; that source limitation is preserved.

## Grading and validation

Final native/Astra grades are in `episodes.csv` and `evaluations/metrics.jsonl`. Unavailable scores remain null.
Scientific non-submissions follow native zero conventions; execution errors are
unavailable, not zeros. The receiving team computes the four separate scorecard
columns and CIs using the repository handoff definitions; no aggregate score is
claimed here. Repetition uses original shared actor text; SciConv fact recovery
uses the recorded native entity_recovery metric with the preserved task facts.

Verify every path/size/SHA-256 in `bundle_manifest.json` and all 1,000 slot keys.
`delivery.json` records any unresolved execution errors. A partial checkpoint
must never be labeled a completed collection. All files are included directly;
`.gz` files are standard gzip streams, not missing external payloads.

## Unresolved selected cases

Full error messages and selected attempt keys: `judging/unresolved-cases.json`.

| Benchmark | Task | Persona | Attempt | Status |
|---|---|---|---:|---|
| discoverybench | test/archaeology/metadata_16.json/0/0 | candidate_046 | 1 | grading_error |
| discoverybench | test/nls_raw/metadata_6.json/0/0 | candidate_003 | 4 | execution_error |
| expbench | iclr2024/19281/1 | candidate_046 | 1 | grading_error |
| expbench | neurips2024/97431/8 | persona_off | 1 | grading_error |

Grading resume used `--retry-errors` with one `--skip-policy-refusal ID` flag for each recorded skipped attempt:

- `expbench_iclr2024_19281_1-0aedaf6a9390/candidate_046/attempt-1`
- `expbench_neurips2024_97431_8-833eedc8ebc5/persona_off/attempt-1`
