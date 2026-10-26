# Delivered model campaigns

Running agents store their complete collection exports here and **commit and push them**. Raw `runs/` directories are ignored and are not a deliverable by themselves. Our analysis team handles final grading, metric computation and the paper table.

Use `results/<model-and-role-slug>/trial-<N>/`. Each campaign is 200 frozen questions × five settings (off / 155 / 001 / 003 / 046), or 1,000 episode slots for one trial. Do not mix model configurations or independent trials in one directory.

Required bundle contents:

- `README.md`: actual model roles/providers/settings, run command, counts, errors, grading status, repair policy.
- `episodes.csv`: all 1,000 keyed slots and selected attempts, including scientific failures and non-submissions. Pending grading is explicit, not zero.
- `traces/final-results.json`, `traces/shared-events.jsonl`, and `traces/shared-events-index.csv`: original ordered conversations, results/termination records, and artifact mapping for every slot.
- `submissions/`: actor final answers/files required for native regrading; include image/file outputs if produced.
- `grading_inputs/`: grading-input manifest and portable redistributable inputs. References must be available to the receiving team, not just absolute paths on the runner's machine. Record access routes and hashes for restricted assets.
- `evaluations/metrics.jsonl`: available native metrics and explicit pending/error records.
- `provenance/`: exact configs, selection/persona/input hashes, source revisions, runtime code hashes and source changes needed to reproduce the configuration.
- `bundle_manifest.json`: relative path, byte size and SHA-256 for every delivered file except itself.

Final score tables and `analysis/` outputs are optional for the running agent. Complete traces/submissions are mandatory even if aggregate scores are already available. Keep per-episode token/tool records when available as supporting data.

Shard large JSONL files by benchmark/persona or compress/split large payloads, and document reconstruction and full-file checksums. Include all parts in the commit. Never include credentials, `.env`, environments, or unreviewed private API payloads. Respect source asset visibility; include restricted references only through an authorized team-accessible route.

Before pushing, verify manifest hashes, slot counts, score/trace/attempt alignment and artifact existence. Stage only the intended campaign directory. After pushing, report the **branch, commit hash, repository-relative path, 1,000-slot coverage, pending grading and unresolved errors**, and verify the remote commit. Collection is not complete if actor/simulator execution is missing; clearly label partial checkpoints.

See [the full handoff](../docs/TEAM_HANDOFF.md) for runnable examples, exact schemas, metric definitions, and known launcher limitations. Existing campaigns are catalogued below. These are historical exports, not newly rerun episodes; delivery completeness is explicitly recorded.

## Current inventory

| Campaign | Location | Delivered scope |
|---|---|---|
| Astra actor / Astra simulator / Astra judge | [trial-1](astra-actor-astra-simulator-astra-judge/trial-1/DELIVERY.md) | 1,000-slot index; 898 Markdown conversations; partial historical export |
| Haiku actor / Opus simulator / Opus judge | [legacy-export](haiku-actor-opus-simulator-opus-judge/legacy-export/DELIVERY.md) | Original pilot and full-campaign records; original filenames retained |
| Haiku actor / Opus simulator / Astra judge | [trial-1](haiku-actor-opus-simulator-astra-judge/trial-1/DELIVERY.md) | 1,000 scores, native metrics and conversations; all four metric inputs available; not a complete standalone regrading package |
| Haiku actor / Haiku simulator / Astra judge | [trial-1](haiku-actor-haiku-simulator-astra-judge/trial-1/DELIVERY.md) | 1,000 scores and reported behavioral aggregates; full conversations/submissions missing |
| GLM 5.3 Flash actor / GLM 5.3 Flash simulator / Astra judge (medium) | [trial-1](glm-5.3-flash-actor-glm-5.3-flash-simulator-astra-judge-medium/trial-1/DELIVERY.md) | 1,000 slots; 947 finished with traces, submissions, native metrics and provenance (893 scored, 54 missing-submission zeros); 53 unresolved execution failures; mixed actor cap during repair; one disclosed retry-missing repair pass |
| Qwen 3.8 27B actor / Qwen 3.8 27B simulator / Astra judge (medium) | [trial-1](qwen3.8-27b-actor-qwen3.8-27b-simulator-astra-judge-medium/trial-1/DELIVERY.md) | 1,000 slots; 984 finished with traces, submissions, native metrics and provenance (913 scored, 70 missing-submission zeros, 1 grading pending); 16 unresolved execution failures; mixed actor cap during repair; one disclosed retry-missing repair pass |
| Qwen 3.8 Flash actor / Qwen 3.8 Flash simulator / Astra judge (medium) | [trial-1](qwen3.8-flash-actor-qwen3.8-flash-simulator-astra-judge-medium/trial-1/DELIVERY.md) | 1,000 slots; 878 finished with traces, submissions, native metrics and provenance (698 scored, 180 missing-submission zeros); 122 unresolved execution failures, mostly simulator tool-call protocol faults; protocol caps throughout, no retry-missing pass |
| DeepSeek V4 Flash actor / DeepSeek V4 Flash simulator / Astra judge (medium) | [trial-1](deepseek-v4-flash-actor-deepseek-v4-flash-simulator-astra-judge-medium/trial-1/DELIVERY.md) | 1,000 slots; 961 finished with traces, submissions, native metrics and provenance (838 scored, 123 missing-submission zeros); 39 unresolved execution failures, mostly reasoning-only actor completions; protocol caps throughout, no retry-missing pass |

Qwen runtime outputs remain under ignored `runs/qwen38-local-trial-1/`; they have not been packaged as a complete delivery. Current Slurm state must be queried, not inferred from this inventory. Original transport ZIPs and older duplicate exports were preserved in ignored `.local_archive/20261010/` on the maintainer's machine.

New bundles are produced by `python scripts/export_main_bundle.py --run-dir RUN_DIR --output results/<slug>/trial-<N> ...`. The exporter passes every UTF-8 text file it copies, including submissions and submitted artifacts, through its path/id/credential sanitizer; `submissions/manifest.jsonl` records `sha256_original` next to the exported hash whenever that changed a file. Run `python scripts/audit_result_bundles.py` from the repository root to verify all packaged file hashes and episode-key counts. Each directory has a current `bundle_manifest.json`; original receipts remain unchanged where present. [Migration record](migration_20261010.json) maps old paths to their new locations. Do not use archived exporter scripts bundled as provenance as current launch commands; use `scripts/` and `docs/TEAM_HANDOFF.md`.
