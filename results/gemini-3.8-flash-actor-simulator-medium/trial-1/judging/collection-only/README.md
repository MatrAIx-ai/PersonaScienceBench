# Gemini 3.8 Flash actor / simulator, medium — trial 1

Status: **partial_collection_checkpoint**. All 1,000 frozen slots are indexed. Selected
dispositions: `{"grading_pending": 809, "missing_submission": 190, "execution_error": 1}`. There are 1035 retained
attempts, including originals and explicitly authorized repairs. Judge calls: 0.

Actor and researcher simulator: Gemini 3.8 Flash, `reasoning_effort=medium`. Final judge: GPT-6 Astra / low, **deferred**.
The gateway's advertised deployment/accounting-model discrepancy is preserved in
`provenance/run/api_access.json`; the requested model ID has not been relabeled.
One trial: 200 questions, 40 per benchmark, off / 155 / 001 / 003 / 046.
Actual protocol/configs and limits are in `provenance/run/configs/`.

## Remaining execution error

The simulator terminated with `content_filter` on DiscoveryBench
`test/nls_raw/metadata_6.json/0/0`, setting `candidate_003`, attempt 4.
This slot remains unavailable, not a scientific zero. The user authorized
delivery of this partial checkpoint with no further retries.

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

Scores remain null until the receiving team performs native/Astra grading.
Scientific non-submissions follow native zero conventions; execution errors are
unavailable, not zeros. The receiving team computes the four separate scorecard
columns and CIs using the repository handoff definitions; no aggregate score is
claimed here. Repetition uses original shared actor text; SciConv fact recovery
requires pending native evaluation with the preserved task facts.

Verify every path/size/SHA-256 in `bundle_manifest.json` and all 1,000 slot keys.
`delivery.json` records any unresolved execution errors. A partial checkpoint
must never be labeled a completed collection. All files are included directly;
`.gz` files are standard gzip streams, not missing external payloads.
