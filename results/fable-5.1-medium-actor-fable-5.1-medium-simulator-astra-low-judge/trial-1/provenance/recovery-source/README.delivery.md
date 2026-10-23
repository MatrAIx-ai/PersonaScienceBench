# Fable 5.1 medium — trial 1

This delivery covers all **1,000 frozen slots**: 200 questions, five settings (`persona_off`, `candidate_155`, `candidate_001`, `candidate_003`, `candidate_046`), one trial. Each benchmark contributes 40 questions. The full campaign ran on October 22, 2026 with 30 workers, retaining its five qualification episodes; recovery finished on October 23.

**965 slots have numeric primary scores: 917 scored submissions and 48 legitimate non-submission zeros.** Nine Discovery grades come from judge-only recovery: two at the original caps, then seven with an explicitly approved helper-cap increase. The other 35 records are 18 actor refusals, 12 simulator refusals and five actor token-limit stops. All nine startup transport failures have been repaired, and no grades remain pending. No episodes are still running or unstarted.

This is a complete delivery of the collected records, with **partial collection status** pending the receiving team's disposition of terminal model outcomes. It is not a claim of 1,000 successfully completed or graded episodes, and the model-expansion checklist is not marked complete.

| Disposition | Slots | Primary score |
|---|---:|---|
| Scored submission | 917 | Native score mapped to 0–100 |
| Legitimate missing submission | 48 | 0 |
| Actor refusal | 18 | Null, explicit reason |
| Simulator refusal before any actor response | 9 | Null, explicit reason |
| Simulator refusal after actor responses | 3 | Null, explicit reason |
| Actor response hit 32,768 tokens | 5 | Null, explicit reason |
| Completed actor submission; grading pending | 0 | — |

The five actor token-limit outcomes are the five settings of ASI `chemistry.sapt_water_dimer`. These and the refusals were not rerolled. `actor_terminal_zero_sensitivity` adds zeros for the 18 actor refusals and five actor token-limit stops while retaining all existing numeric scores; it leaves simulator failures null. It is a separately labeled sensitivity input, not the primary score.

| Role | Requested / actual model | Settings |
|---|---|---|
| Actor | `us.anthropic.claude-fable-5-1` / `claude-fable-5-1` | Bedrock InvokeModel, adaptive thinking, medium effort, 32,768 response tokens |
| Simulator (`researcher`) | Same Fable model | Bedrock InvokeModel, adaptive thinking, medium effort, 8,192 response tokens |
| Judge | `us.openai.gpt-6-astra` / same returned ID | Bedrock Responses, low reasoning, default 4,096 output tokens; native Discovery variable/relation helpers use 250, increased to 4,096 for 14 fresh calls across seven approved recovery grades |

Region: `us-west-2`. The native call audit verifies all recorded role responses against these model IDs, efforts and actor/simulator caps. Original failed judge calls were not retained by the old logger; their native errors remain in the result records. The recovery transport now preserves incomplete native responses and usage before raising an error. Token totals are observed-log totals, not a complete billing invoice; dollar costs remain null.

Two default-cap qualification responses exhausted the repository's 12,288-token actor response budget before producing usable submissions. Robert explicitly approved **32,768** on October 22. The revised configuration was qualified separately, and its five pilot episodes were retained in this trial. The earlier default-cap pilots are preserved under `provenance/excluded-default-cap-pilots.*` and excluded from the primary slot selection. Increasing the cap changes the response budget and must be disclosed in comparisons; medium reasoning, 60 actor steps, 12 researcher requests, and SciConv's native 10-clarification limit were retained.

Other runtime amendments are recorded in `provenance/original/campaign_amendment.v4.json`: direct Bedrock routing; native structured simulator output because Fable rejects forced tool choice; provider-default sampling where Astra does not support native sampling parameters; a 1,800-second request timeout; and the host execution restrictions. Actors used Bubblewrap with network disabled, JavaScript/TypeScript blocked, bind/listen denied, and no RLScience cluster access. ASI/Bix/Discovery and EXP use the recorded researcher-review protocol; SciConv retains its native clarification protocol and the recorded persona/user-prompt policy. This is a frozen task panel, not an assertion that every historical runtime protocol is identical.

The full launch command, after restoring frozen preparation and applying the recorded runtime source overlay, was:

```bash
python scripts/run_main.py \
  --run-dir "$RUN_DIR" --provider bedrock \
  --model us.openai.gpt-6-astra --reasoning-effort low \
  --actor-model us.anthropic.claude-fable-5-1 --actor-reasoning-effort medium \
  --researcher-model us.anthropic.claude-fable-5-1 --researcher-reasoning-effort medium \
  --require-prepared --workers 30 --actor-max-tokens 32768 --request-timeout 1800
```

`provenance/original/full_launch.json` retains the exact argument vector and launch receipt. Base revision: `d672e19abf0f7bd71cf916dc313953be9b69bd65`. The original and recovery source archives, dirty diffs, per-file hashes, dependency lock, environment inventories, persona files and ten actual role configurations are included. These archived source files are provenance; use the pinned repository and inspect the overlay before any future launch.

Recovery preserved original outcomes and selected the first attempt reaching native inference after a confirmed startup failure. Nine `GetInferenceProfile` throttles were retried once as episodes, with three workers and bounded SDK preflight retries. All nine finished; their first native outcomes were retained as-is, without a score threshold or further rollout. One earlier EXP qualification slot (`neurips2024/97609/1`, `candidate_003`) already used attempt 2 after a timeout-schema failure before inference. Thus the canonical map selects 990 attempt-1 and ten attempt-2 records, and all 1,010 primary-campaign attempt records are retained. No earlier scientific attempt was discarded.

Nine completed Discovery submissions originally had judge failures. Recovery replayed the exact ordered completed original wire-request prefix, verified by full request equality and hashes, then made one fresh invocation for each remaining native call, stopping on failure. Actor submissions, artifacts and original error records were unchanged. Two recovered at the original caps. Seven still hit the native 250-token helper cap: two settings of `test/archaeology/metadata_13.json/0/0` and all five settings of `test/archaeology/metadata_16.json/0/0`.

The judge-only helper-cap increase from **250 to 4,096 tokens was approved and applied** on October 23. All seven remaining grades recovered. This amendment reused 28 completed calls from the original prefixes and made 14 fresh helper calls at 4,096 tokens, with Astra still at low reasoning and zero transport retries. No actors or simulators were rerun. An independent audit against retained private logs checks every fresh transmitted request against its native request, allowing only the cap change, and confirms that all seven original submissions, 28 artifact files, episode inputs, API logs and original error results remain unchanged. The approval binds the seven slot keys and exact recovery-script hashes. The portable bundle verifier checks this authorization, the audit-script hash, cohort membership, call counts, models, reasoning settings, caps, transport retry counts and consistency of recorded transmitted-request hashes; full wire equality requires the retained private logs.

The earlier unsuccessful grading attempts remain in `provenance/judge-recovery-history.jsonl`; the amended grades are explicit overlays. The preparation plan's historical `prepared_not_authorized` status is retained alongside the later approval and execution receipts. `episodes.csv` exposes `judge_budget_cohort` for every slot. These seven grades used a different judge response budget and must be identified in comparisons. In particular, `metadata_13` mixes budgets across arms: `persona_off` and `candidate_155` use the amendment, while its other three arms retain the native helper cap. All five `metadata_16` arms use the amendment.

`episodes.csv`, the canonical attempt map, trace index, grading-input manifest and native metrics share identical slot/attempt keys. Primary scoring follows `docs/TEAM_HANDOFF.md` section 4: ASI `100*score/max_score`; Bix `100*correct`; Discovery `100*final_score`; SciConv `100*FRR`; EXP `gated_coverage_mean`, already 0–100, using the native final/initial rule. SciConv disambiguation `entity_recovery` is preserved separately, before intent gating. No aggregate paper scores or confidence intervals are claimed here.

Every original shared event is retained in order, including unsuccessful episodes and explicit empty-trace reasons. Command actions/results are retained separately in `traces/tool-events.jsonl`; private model reasoning and raw API payloads are excluded. Native files and event text preserve original path strings verbatim. Derived metadata rebases paths to `${REPO}`, `${RUN}` and `${CAMPAIGN}`. The materializer creates separate submission JSON with portable artifact paths and leaves the original bytes intact.

Run these commands from this delivery directory to verify or reconstruct the bundle. They use standard-library Python, make no model calls, execute no submitted code, and start no servers:

```bash
python materialize_bundle.py
python verify_bundle.py
python materialize_bundle.py --output /absolute/path/to/a/new/fable-trial-1
```

`logical_files.json` lists the parts, encoding, byte size and SHA-256 for each compressed or split logical file. All physical files are at most 24 MiB. The materializer concatenates parts, decompresses where specified, checks every archive member, and writes `canonical-submissions.jsonl` in the fresh output directory. For controller submissions, that index points to `submission.rebased.json`; for EXP, it exposes the original design, execution and native evaluation files. SciConv includes the final specification, original conversation log and native judge outputs. Submitted files, including images and analysis scripts, are preserved byte-for-byte and are not executed by verification.

The tracked frozen preparation is included in `grading_inputs/frozen/`, with 1,160 metadata files, original EXP records and pinned external-asset routes/checksums. To reconstruct task/evaluator paths on another host, acquire the pinned public assets described by the repository, then run the pinned `scripts/restore_main_preparation.py --bundle <delivery>/grading_inputs/frozen --run-dir <fresh-run>`. It verifies selection, source pins and recorded asset hashes and rebases paths without preparation inference. The roughly 2.8 GiB of original public benchmark assets remain downloads from those pinned routes. Historical evaluator directories without tree hashes are identified by the frozen manifest and rely on pinned source acquisition. Hidden grading references stay in this private repository and outside actor workspaces.

`bundle_manifest.json` covers every delivered file except itself. Offline transport/inference tests passed (68 tests), and judge recovery request/receipt tests passed (five tests). The semantic verifier checks all 1,000 keys, scores, attempts, shared text, archive references and frozen metadata hashes; the original-run verification receipt also checks native files and submitted artifact bytes. `provenance/recovery/judge_cap4096_verification.json` records the seven-grade amendment audit. Claude Opus 5.5 reviewed the recovery and exporter across several exchanges; actual-model receipts are included. Its advice was checked against the native implementation and handoff, including the EXP score scale and final/initial rule.
