# MiniMax M3 actor / simulator, adaptive thinking — trial 1

Status: **partial_graded_checkpoint**. All 1,000 frozen slots and all 1377 original/repair attempts are retained.
Selected final dispositions: `{"missing_submission": 402, "scored": 558, "execution_error": 39, "grading_error": 1}`. Final grading complete: **False**.

Actor and simulator: **MiniMax M3 actor / simulator, adaptive thinking**. Final judge: **GPT-6 Astra, low effort**.
Exact collection role IDs/settings: `{"actor": {"model": "nvidia/minimaxai/minimax-m3", "provider": "nvidia", "reasoning_effort": "adaptive"}, "researcher": {"model": "nvidia/minimaxai/minimax-m3", "provider": "nvidia", "reasoning_effort": "adaptive"}, "judge": {"model": "gpt-6-astra", "provider": "openai", "reasoning_effort": "low"}}`.
Actual posthoc judge routing/settings: `{"model": "openai/openai/gpt-6-astra", "provider": "nvidia", "reasoning_effort": "low", "max_tokens": 4096, "timeout": 600, "unsupported_parameters": "omit_and_record"}`.
(The collection judge configuration was deferred; the posthoc route above performed final grading.)
No actor/simulator episodes were rerun for grading. Native rubrics, scoring and EXP integrity gates were retained.
Grading evaluated saved submissions; 39 unresolved execution errors remain unavailable.
Policy refusals skipped at user request: **0**. Their scores remain unavailable, not zero.

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

Grading repair: 15 failed DiscoveryBench cases were retried with the native
250-token judge output cap raised to **4,096**; all 15 now have scores. Previously
successful grades were retained byte-for-byte. The target list, evaluator version
and actual request settings are preserved. This is a documented grading-setting
repair, not a change to scientific rubrics. One ASI metadynamics numerical evaluator
returned a non-finite value; its overall score remains unavailable even though its
model-judge component succeeded. Historical failures are retained.

Exact grading sequence (paths/env/workers as above):
1. Initial: `--output .../grading/astra-low-v1`.
2. Collection-repair grading: `--output .../grading/astra-low-repaired-v2 --reuse-grades-from .../grading/astra-low-v1 --retry-errors`.
3. Failed-case cap repair: `--output .../grading/astra-low-judge-cap4096-v3 --reuse-grades-from .../grading/astra-low-repaired-v2 --repair-discovery-token-cap 4096`.

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

## Remaining execution errors

39 selected actor/simulator execution failures remain unavailable. See `episodes.csv` and native error records in `traces/final-results.json`.

## Unresolved selected cases

Full error messages and selected attempt keys: `judging/unresolved-cases.json`.

| Benchmark | Task | Persona | Attempt | Status |
|---|---|---|---:|---|
| asibench | biology.protein_folding_go_model | candidate_155 | 3 | execution_error |
| asibench | chemistry.implicit_solvent_pb_gb | candidate_155 | 2 | execution_error |
| asibench | chemistry.implicit_solvent_pb_gb | persona_off | 2 | execution_error |
| asibench | chemistry.marcus_et_reorganization_energy | candidate_046 | 3 | execution_error |
| asibench | chemistry.metadynamics_for_dipeptide_in_vacuum | candidate_046 | 1 | grading_error |
| asibench | computer_science.causal_attention | candidate_046 | 2 | execution_error |
| asibench | computer_science.deployment_prediction_sets | candidate_155 | 2 | execution_error |
| asibench | earth_science.farquhar_ballberry_photosynthesis | candidate_003 | 2 | execution_error |
| asibench | earth_science.snow_3layer_compaction | candidate_155 | 2 | execution_error |
| asibench | earth_science.snow_3layer_compaction | persona_off | 2 | execution_error |
| asibench | materials.ising_domain_growth | candidate_155 | 2 | execution_error |
| asibench | math.manifold_pde_meshfree | candidate_003 | 3 | execution_error |
| asibench | math.manifold_pde_meshfree | candidate_155 | 2 | execution_error |
| asibench | math.multiply_connected_conformal_mapping | candidate_155 | 2 | execution_error |
| asibench | math.sigma_linear_diophantine | candidate_001 | 2 | execution_error |
| asibench | math.ucb_q_learning_regret | candidate_046 | 2 | execution_error |
| asibench | physics.dp_contact_process | candidate_155 | 2 | execution_error |
| asibench | physics.kt_phase_transition_2d_xy_model | candidate_003 | 2 | execution_error |
| asibench | physics.kt_phase_transition_2d_xy_model | candidate_046 | 2 | execution_error |
| asibench | physics.lbm_square_wake | candidate_001 | 2 | execution_error |
| asibench | physics.lbm_square_wake | candidate_003 | 3 | execution_error |
| asibench | physics.lbm_square_wake | candidate_046 | 3 | execution_error |
| asibench | physics.paired_nanorod_negative_index_retrieval | candidate_155 | 2 | execution_error |
| asibench | physics.vpfm_leapfrog | candidate_001 | 2 | execution_error |
| asibench | physics.vpfm_leapfrog | candidate_003 | 2 | execution_error |
| asibench | physics.vpfm_leapfrog | candidate_046 | 2 | execution_error |
| asibench | robotics.lidar_imu_time_offset_yaw_calibration | candidate_046 | 2 | execution_error |
| asibench | robotics.lidar_imu_time_offset_yaw_calibration | candidate_155 | 2 | execution_error |
| asibench | robotics.particle_filter | candidate_046 | 2 | execution_error |
| asibench | robotics.rnea_inverse_dynamics_dh | candidate_001 | 2 | execution_error |
| asibench | robotics.rnea_inverse_dynamics_dh | candidate_003 | 2 | execution_error |
| asibench | robotics.rnea_inverse_dynamics_dh | candidate_155 | 3 | execution_error |
| asibench | robotics.rnea_inverse_dynamics_dh | persona_off | 2 | execution_error |
| asibench | robotics.robust_pose_graph_false_loops | candidate_155 | 2 | execution_error |
| bixbench | bix-26-q4 | candidate_003 | 3 | execution_error |
| bixbench | bix-30-q1 | persona_off | 2 | execution_error |
| expbench | iclr2024/19388/10 | candidate_155 | 2 | execution_error |
| expbench | neurips2024/93022/0 | candidate_046 | 3 | execution_error |
| expbench | neurips2024/93022/4 | candidate_155 | 2 | execution_error |
| expbench | neurips2024/97431/8 | candidate_046 | 3 | execution_error |
