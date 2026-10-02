# Remote-agent handoff

## Read in this order

1. [Paper plan](design/benchmark_paper_plan.md): agreed story, 200 nonvisual questions, six proposed personas, three repetitions, three actors, and figure/table dependencies.
2. [Completed report](../reports/full_persona_v2/README.md): the 30-persona study and its original table structure.
3. [Case studies](../reports/full_persona_v2/case_studies.md): profile-to-behavior evidence and known interpretation issues.
4. [Setup](reproducibility.md), [conversion](design/conversion_revision_v2.md), and [persona injection](personas.md).

## Completed experiment: preserve these records

`reports/full_persona_v2/` contains 310 recorded traces: 30 personas × ten questions, plus ten persona-off baselines. The folder also contains exact injected profiles, indexes, a machine-readable snapshot, and frozen experiment metadata. The original report, scores, and traces were not regenerated during cleanup.

`configs/full_persona_v2/` contains the cohort/prompt hashes, ten source-task IDs and exact persona-off model/protocol configs. Recover all 30 raw identity blocks with:

```bash
python3 scripts/restore_full_persona_cohort.py --check
python3 scripts/restore_full_persona_cohort.py
```

The second command creates the ignored cohort directory on a fresh checkout and refuses to overwrite an existing directory. It extracts the published identity blocks verbatim and checks every original prompt hash. It makes no model calls.

The completed run has 265 scored/completed episodes, 43 missing submissions and two technical/evaluator errors. Its published ranking uses eight common questions and a fixed baseline of 26.01%. Keep the original missing-submission convention and tables. New experiments get new run directories and reports.

Important reading notes: some frozen trace headers incorrectly say persona disabled; the recorded API system messages contain the actual identity. Raw-log links inside frozen traces are relative to their original local run directories; they do not resolve on GitHub. Whitespace word counts undercount Chinese replies. Some EXP judge/monitor decisions are inconsistent. The case-study report identifies exact examples; these are analysis concerns, not reasons to edit historical records.

## What the next agent should do

- Select the 200 nonvisual questions with subfield, format and source-study tags: Discovery 70, Bix 50, EXP 40, SciConv 36, ASI 4. The quotas are a plan, not a finalized task manifest.
- Use the proposed six-profile panel: 148, 046, 155, 228, 137, 089, plus persona off. Preserve full identity text and allow general knowledge; do not revert to short action-rule or 56-attribute personas.
- Build the expanded scheduler around explicit task IDs, selected persona IDs, actor configuration and three independent complete episodes per cell. The existing `scripts/run_persona_benchmarks.py` is the historical scheduler: its build path assumes 25 tasks and all 30 personas. It is not the 200-question launcher.
- Account for its host-specific Bubblewrap path, `external/runtime/bubblewrap-local/usr/bin/bwrap`, before using that scheduler on a different machine. The scientific runtime requires Bubblewrap isolation and has no host-execution fallback. Cleanup did not change sandbox behavior.
- Start by preparing the paper diagrams/tables and analyzing existing traces. The expanded experiment is 4,200 episodes per actor, 12,600 across three actors, plus 30 if the optional static reference is run. No expanded jobs are running.

- DiscoveryBench persona pilots ([guide](persona_pilots.md), [results](../reports/discoverybench_persona_pilot/README.md)): 699 recorded episodes plus two one-episode smoke runs, $4.39 at list price: a 24-episode task screen, the 125-episode pilot, a 25-episode neutral replication, 300 woman -> man / opposite-attribute counterfactual episodes and 225 man -> woman episodes. No persona, neutral, gender-swap or single-attribute effect on score exceeded wording noise; any identity shortened the submitted hypothesis, and a woman label possibly lengthened it (exploratory).
- OpenProblems `task_denoising` ([adapter](adapters/openproblems_denoising.md), [results](../reports/openproblems_persona_pilot/README.md)): pinned task repo and 13 hash-checked datasets; native MCV metrics scaled by the native controls. A 12-episode screen, the 125-episode persona pilot and a 25-episode neutral_b replication ($1.26): no persona or neutral effect on the clipped score (within ±3 pp of persona off); persona 155's researcher writes Chinese. Native evaluation needs about 5-6x a dataset's dense size in memory, so an 8 GB host runs only the smaller datasets. Pilot headlines use the clipped score (the native Poisson loss is unbounded). Counterfactual (gender / opposite-attribute) runs on this benchmark are not part of this report.

## Cleanup validation

All 375 pre-existing report/profile/trace files were checked byte-for-byte, and the README results tables and future paper plan are unchanged. All 30 prompt hashes and restoration overwrite protection passed; the distributable-file/link check passed.

The existing offline suite produced 171 passes, 26 skips, three legacy persona metadata-fixture failures, and six runtime setup errors because Bubblewrap was not on the system path. All six runtime tests passed when rerun with the existing local Bubblewrap through `PERSONASCIENCEBENCH_BWRAP`. The three failures are `test_legacy_rendering_and_metadata_match_the_supplied_repository` (enabled legacy profiles); their expected metadata/hashes disagree with current records. Their code and fixtures were not changed by cleanup. Source-dependent tests skipped at their expected fixture paths. No paid benchmark runs were launched.

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
