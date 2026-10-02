# Repository coherence audit — 2026-10-01

The main-run contract is [MAIN_RUN.md](MAIN_RUN.md): 200 unique questions,
40 per source, off / 155 / 001 / 003 / 046, and 1,000 episodes per fresh trial.
Three fresh trials mean 3,000 planned episodes, not a statement of completed
historical coverage. Default resources are 30 workers / CPUs and 128 GB RAM;
actor, simulator, and judge use Astra low. The paper's three analysis levels
are performance, semantic diversity, and behavioral diversity.

## Corrections

| Area | Finding and correction |
|---|---|
| Run documentation | Handoff and migration instructions still described the superseded quotas, six-persona proposal, and unimplemented launcher. They now point to the frozen main-run inputs and actual launch scripts. Historical reports and separate IdeaGene/MLAgentBench tracks remain identifiable. |
| Credentials | `.env.example` now includes the main run's `OPENAI_API_KEY`; OpenRouter remains optional. Missing-key errors name the selected provider's variable. |
| Actor setup | New actor environments use the resolved base interpreter, matching the sandbox migration instructions. Setup respects `PERSONASCIENCEBENCH_BWRAP`. Existing environments are not deleted automatically. |
| Frozen inputs | The main launcher accepts only the five shipped settings and verifies the selection checksum, source quotas, uniqueness, and exact persona hashes before API access. Existing run/configuration checks also precede API preflight. CI runs the offline frozen-input checker. |
| Legacy persona metadata | An unused `system_prompt: null` field had changed three legacy metadata/hash fixtures. Legacy serialization now excludes that unused representation; full-profile prompts are unchanged. |
| SciConv provenance | New evaluations use a model-neutral judge label and explicitly save judge model/provider/reasoning. Old hard-coded `+luna-judge` labels require consulting saved configurations/API records. The scoring formula is unchanged. |
| Local analysis tracking | Updated the experiment index, selected-panel status records, and paper-plan overview to distinguish current notebooks from older exports. No notebook, figure, score, or raw trace was regenerated. |
| Local archived links | Repaired four links to bundled archived figures. Labeled 30 unbundled historical paths explicitly instead of substituting current outputs for old evidence. |

## Validation

- Offline suite excluding two optional SDK integration tests: **299 passed,
  31 skipped, 2 deselected**. Source-dependent tests were run with
  `PERSONASCIENCEBENCH_SOURCE_ROOT=/tmp/psb-no-external-sources`; skipped checks
  need source inputs or runtime dependencies. The initial unrestricted suite
  stalled during optional OpenHands SDK import and was interrupted.
- The three legacy failures observed before the serialization fix passed on
  the subsequent run; their golden fixtures were not rewritten.
- Frozen selection and all four persona prompt checksums passed.
- Python syntax checks passed for 91 source/script files; 17 configuration and
  manifest JSON files parsed. Main setup/submission shell syntax passed.
- The local distributable-text/link check passed after archive-link repairs.

The offline suite used the installed environment's packages with automatic
third-party pytest plugin loading disabled. No source download, scientific
episode, job submission, paid API call, or notebook recomputation was performed.
This is not an end-to-end execution certification.

## Version boundaries

The public setup update includes runtime/documentation corrections and scope
notices in the older experiment index and paper plan. Detailed analysis
notebooks, derived data, figures, and local tracking updates remain uncommitted,
as requested. The current notebook figure may differ from a preserved exported
report or plotting script; those snapshots are labeled rather than silently
regenerated. Local analysis inputs and original run artifacts are still needed
to reproduce those analyses.

Historical manifests, recorded prompts, source selections, scores, and trial
outcomes remain unchanged. The original `configs/main_run/provenance.json`
records an earlier snapshot; per-run code receipts record the implementation
used by a new submission. Live scheduler state and model-account access were
not checked.
