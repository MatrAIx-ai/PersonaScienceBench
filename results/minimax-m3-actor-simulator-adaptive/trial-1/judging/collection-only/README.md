# MiniMax M3 actor / simulator, adaptive thinking — trial 1

Status: **partial_collection_checkpoint**. All 1,000 frozen slots are indexed. Selected
dispositions: `{"missing_submission": 402, "grading_pending": 559, "execution_error": 39}`. There are 1377 retained
attempts, including originals and explicitly authorized repairs. Judge calls: 0.

Actor and simulator: MiniMax M3 with user-approved **adaptive thinking**, not medium.
Exact API ID: `nvidia/minimaxai/minimax-m3`; resolved deployment:
`dynamo/minimaxai/minimax-m3-sglang`. Requests use
`chat_template_kwargs: {"thinking_mode": "adaptive"}` with no wire `reasoning_effort`.
Final judge: GPT-6 Astra / low, deferred at collection. Actual provider/routing,
capability verification and role configs are in `provenance/`.
One trial: 200 frozen questions × five settings = 1,000 slots.

## Commands and repair provenance

Original: `ENV_FILE=/path/to/.env WORKERS=4 bash scripts/run_minimax_m3.sh`.
Resume: same command with `--resume-unstarted`; technical repair with
`--retry-infrastructure`; targeted old-cap truncation repair with
`--retry-truncations-below-policy`. Preserve the archived target lists and states.
1,377 attempt records include 141 original queue-stop receipts (never executed),
141 resumed executions, 229 technical retries and seven old-cap truncation retries.
All 1,000 selected endpoints executed; none is an unstarted queue entry.
Scientific non-submissions were retained. Latest authorized attempts are selected,
never best scores. Original-only analysis must distinguish unstarted attempt 1
from actual executions; the queue receipts must not be scored as scientific zeros.

Original actor/simulator output caps: **12,288 / 8,192** tokens. Authorized repair
caps: **32,768 / 16,384**. This is a mixed-cap repaired checkpoint, not a uniform
fresh trial. Already-loaded clients kept their old limits; per-call effective
settings and `output_limit_override` receipts identify the actual limits.
See `provenance/run/generation_limits.json`, installation-time states and source
snapshots in `provenance/history/`. No new collection calls occurred during export.

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

## Remaining execution errors

39 selected actor/simulator execution failures remain unavailable. See `episodes.csv` and native error records in `traces/final-results.json`.
