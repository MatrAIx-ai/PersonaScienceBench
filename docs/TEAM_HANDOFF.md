# Remote-agent handoff

## Current run and reading order

1. [Main-run guide](MAIN_RUN.md): the authoritative fresh-run configuration and commands.
2. [Root README](../README.md): main-run overview and the three analysis levels—performance, semantic diversity, and behavioral diversity.
3. [Setup and migration](reproducibility.md), [interaction protocol](interaction_protocol.md), and [persona injection](personas.md).
4. [Paper plan](design/benchmark_paper_plan.md) and [Experiment workspace](../Experiment/README.md): evolving analysis plans and historical collection records, not launcher defaults.
5. [Historical pilot report](../reports/full_persona_v2/README.md) and [case studies](../reports/full_persona_v2/case_studies.md): preserved selection provenance.

The main run is **200 questions (40 each from five benchmarks) × five settings (off / 155 / 001 / 003 / 046)**: **1,000 episodes per trial**, or **3,000 across three fresh trials**. Actor, simulator, and judge default to OpenAI GPT-6 Astra with low reasoning. The SLURM launcher defaults to 30 workers / 30 CPUs and 128 GB RAM. These are planned fresh-run totals, not completed-result counts.

## Historical 30-persona pilot: preserve these records

`reports/full_persona_v2/` contains 310 recorded traces: 30 personas × ten questions, plus ten persona-off baselines. The folder also contains exact injected profiles, indexes, a machine-readable snapshot, and frozen experiment metadata. The original report, scores, and traces were not regenerated during cleanup.

`configs/full_persona_v2/` contains the cohort/prompt hashes, ten source-task IDs and exact persona-off model/protocol configs. Recover all 30 raw identity blocks with:

```bash
python3 scripts/restore_full_persona_cohort.py --check
python3 scripts/restore_full_persona_cohort.py
```

The second command creates the ignored cohort directory on a fresh checkout and refuses to overwrite an existing directory. It extracts the published identity blocks verbatim and checks every original prompt hash. It makes no model calls.

The completed run has 265 scored/completed episodes, 43 missing submissions and two technical/evaluator errors. Its published ranking uses eight common questions and a fixed baseline of 26.01%. Keep the original missing-submission convention and tables. New experiments get new run directories and reports.

Important reading notes: some frozen trace headers incorrectly say persona disabled; the recorded API system messages contain the actual identity. Raw-log links inside frozen traces are relative to their original local run directories; they do not resolve on GitHub. Whitespace word counts undercount Chinese replies. Some EXP judge/monitor decisions are inconsistent. The case-study report identifies exact examples; these are analysis concerns, not reasons to edit historical records.

## Running or handing off the main experiment

- Use `configs/main_run/selection.csv` and the four exact profiles in `configs/main_run/personas/`. Do not resample questions or restore the superseded 70/50/40/36/4 allocation.
- Run `scripts/setup_main.sh`, configure `OPENAI_API_KEY`, and validate inputs with `scripts/check_main.py`. Launch with `scripts/run_main.py` or the separate `scripts/submit_main.sh`.
- Give each independent trial its own run directory. Preserve the EXP extraction cache across sequential trials. The guide documents `afterok` dependencies, resume behavior, and repair flags.
- Keep historical protocols, original outcomes, and repair attempts distinct. Current SciConv behavior is not interchangeable with pre-change traces. Inspect saved manifests/configurations when analyzing past runs.
- The main runner does not require analysis notebooks. Existing analysis has uneven trial coverage; the five displayed settings do not imply that every setting has three completed historical trials.
- Treat job IDs and statuses in old plans as dated snapshots. No live scheduler state is asserted by this document.

## MLAgentBench track

The [MLAgentBench adapter](adapters/mlagentbench.md) converts 12 tasks (3 excluded for lacking a native verifier) with two hand-reviewed CPU pilots, `vectorization` and `cifar10`, a native `get_score` evaluator, a hashed CPU runtime lock and a baseline/summary script. Only local smoke runs with a non-team model and transport exist so far. It is not part of the frozen 200-question main run. The [IdeaGene track](adapters/ideagene.md) is also separate; adding an adapter does not add questions to the main-run selection.

## Historical cleanup validation (2026-09-27)

All 375 pre-existing report/profile/trace files were checked byte-for-byte, and the README results tables and future paper plan are unchanged. All 30 prompt hashes and restoration overwrite protection passed; the distributable-file/link check passed.

At that cleanup snapshot, the offline suite produced 171 passes, 26 skips, three legacy persona metadata-fixture failures, and six runtime setup errors because Bubblewrap was not on the system path. All six runtime tests passed when rerun with the existing local Bubblewrap through `PERSONASCIENCEBENCH_BWRAP`. The three failures are `test_legacy_rendering_and_metadata_match_the_supplied_repository` (enabled legacy profiles); their expected metadata/hashes disagree with current records. Their code and fixtures were not changed by cleanup. Source-dependent tests skipped at their expected fixture paths. No paid benchmark runs were launched.

## Local assets to transfer separately

A Git clone includes all published Markdown traces and the exact injected prompts. It does **not** include these ignored assets from the current machine:

| Local path | Why transfer it? |
|---|---|
| `runs/full-persona-v2-two-20260926/` | Original API/event JSON, configurations, submitted code/results and evaluator records; about 2.1 GiB |
| `data/conversion_catalog/`, `data/design_catalog/`, `data/exp_bench/` | Converted task cards, source provenance and cached EXP extraction |
| `data/persona_case_study/full_persona_v2/`, `full_profile_selection_v2/`, `action_selection_v1/` | Original profiles, field audits and selection provenance; the last directory is an input to rescreening the original 300, not an active experiment |
| `external/persona_case_study/` | Original sample and pinned MatrAIx renderer, if rebuilding the selection |
| `external/sources/` | Pinned sources and benchmark assets; Bix data account for most local disk use |

Use an approved file-transfer channel for those directories. Configure credentials independently on the new host. Recreate virtual environments and regenerate prepared task packages: their paths are machine-specific. Copy the raw completed run as historical evidence, not as a portable resume queue.

Superseded local outputs were moved to the sibling folder `siyangwu_branch.cleanup-archive-20260927/`, with a restore manifest. They are outside the checkout and unnecessary for the next study. Removed tracked drafts remain recoverable in Git history at commit `0c54c13`. Current datasets, runtime environments, original sampling provenance and the completed run remain intact locally.
