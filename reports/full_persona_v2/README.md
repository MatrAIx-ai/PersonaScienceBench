# Full-persona experiment: final results

Snapshot: 2026-09-26T21:43:22+00:00. **310/310 episodes finished**. The batch is complete.

30 source-balanced, behaviorally diverse profiles; two fixed questions per benchmark; one fresh shared persona-off baseline per question. Actor, simulator and judge use GPT-6 Luna with reasoning effort `none`. Full persona text is injected only into the simulator system prompt. Both conditions can use general knowledge; evaluator references remain private.

Scores use ASI score/max score, Bix grade, Discovery final score, EXP gated coverage/100 and SciConv FRR. **Missing submissions count as zero for both persona and baseline** in this report (an explicit analysis convention, not a fabricated native grade). Infrastructure failures and pending episodes are excluded. All comparisons are task-matched; these single-run descriptive results do not establish causality or statistical significance.

| Benchmark | Finished / 62 | Missing submissions: on / off | Infrastructure failures | Paired cases | Persona mean | Matched off mean | Difference |
|---|---:|---:|---:|---:|---:|---:|---:|
| asibench | 62/62 | 3 / 0 | 0 | 60 | 6.76% | 7.37% | -0.61 pp |
| bixbench | 62/62 | 36 / 2 | 1 | 59 | 18.64% | 0.00% | +18.64 pp |
| discoverybench | 62/62 | 2 / 0 | 1 | 59 | 0.79% | 0.00% | +0.79 pp |
| expbench | 62/62 | 0 / 0 | 0 | 60 | 37.49% | 46.67% | -9.18 pp |
| sciconvbench | 62/62 | 0 / 0 | 0 | 60 | 38.33% | 50.00% | -11.67 pp |

Benchmark means use available comparable outcomes; infrastructure failures are excluded. Matched off means can differ by task mix; no baseline is regenerated. BixBench comparisons use the explicit missing-submission convention because both baseline runs produced no submission.

## Ten largest absolute persona deviations

Ranking uses **the same 8 questions for all 30 profiles**, with complete comparable outcomes: `discoverybench:test/archaeology/metadata_21.json/0/0`, `bixbench:bix-30-q3`, `asibench:materials.relaxation_mode_recovery`, `asibench:math.nnls_modulus_deblur`, `sciconvbench:solMech/disambiguation/case_104`, `sciconvbench:foam/disambiguation/case_020`, `expbench:iclr2024/17776/4`, `expbench:neurips2024/98318/6`. Questions with an infrastructure or evaluator error in any arm are excluded from this common-task ranking. Missing submissions remain zero in both arms. No candidate is excluded by identity. Ties use candidate ID.

Turns are actor–simulator handoffs (native clarification Q&A for SciConv), excluding tool calls. Words/reply uses visible simulator replies, excluding initial requests and private evidence, averaged per task. Revisions count result-review requests for more work; SciConv has no such stage and is omitted. All behavioral columns use the same ranked questions and show persona on / matched off.

**Shared baseline: 26.01%.** All personas are compared on the same 8 questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.

| Rank | Persona | Score | Change vs off | Traces |
|---:|---|---:|---:|---|
| 1 | [046](profiles/candidate_046.md) | 4.54% | **-21.47 pp** | [Read](traces/candidate_046.md) |
| 2 | [003](profiles/candidate_003.md) | 6.14% | **-19.87 pp** | [Read](traces/candidate_003.md) |
| 3 | [004](profiles/candidate_004.md) | 9.33% | **-16.68 pp** | [Read](traces/candidate_004.md) |
| 4 | [089](profiles/candidate_089.md) | 9.79% | **-16.22 pp** | [Read](traces/candidate_089.md) |
| 5 | [001](profiles/candidate_001.md) | 9.91% | **-16.10 pp** | [Read](traces/candidate_001.md) |
| 6 | [127](profiles/candidate_127.md) | 10.51% | **-15.50 pp** | [Read](traces/candidate_127.md) |
| 7 | [262](profiles/candidate_262.md) | 11.33% | **-14.68 pp** | [Read](traces/candidate_262.md) |
| 8 | [224](profiles/candidate_224.md) | 12.20% | **-13.81 pp** | [Read](traces/candidate_224.md) |
| 9 | [148](profiles/candidate_148.md) | 39.37% | **+13.36 pp** | [Read](traces/candidate_148.md) |
| 10 | [026](profiles/candidate_026.md) | 12.66% | **-13.35 pp** | [Read](traces/candidate_026.md) |

**Behavior on the same questions**

Each cell shows **persona on / baseline**. Rows follow the performance ranking.

| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |
|---|---:|---:|---:|
| [046](profiles/candidate_046.md) | 2.38 / 3.38 | 70.76 / 65.99 | 0.17 / 0.33 |
| [003](profiles/candidate_003.md) | 3.88 / 3.38 | 66.73 / 65.99 | 0.00 / 0.33 |
| [004](profiles/candidate_004.md) | 3.88 / 3.38 | 69.05 / 65.99 | 0.00 / 0.33 |
| [089](profiles/candidate_089.md) | 4.25 / 3.38 | 69.53 / 65.99 | 0.00 / 0.33 |
| [001](profiles/candidate_001.md) | 4.25 / 3.38 | 70.60 / 65.99 | 0.00 / 0.33 |
| [127](profiles/candidate_127.md) | 4.50 / 3.38 | 70.49 / 65.99 | 0.50 / 0.33 |
| [262](profiles/candidate_262.md) | 2.25 / 3.38 | 68.95 / 65.99 | 0.00 / 0.33 |
| [224](profiles/candidate_224.md) | 4.38 / 3.38 | 65.12 / 65.99 | 0.00 / 0.33 |
| [148](profiles/candidate_148.md) | 3.88 / 3.38 | 72.61 / 65.99 | 0.00 / 0.33 |
| [026](profiles/candidate_026.md) | 3.50 / 3.38 | 74.09 / 65.99 | 0.33 / 0.33 |

Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.


## All 30 profiles on the common questions

| Persona | Persona mean | Fixed baseline mean | Difference |
|---|---:|---:|---:|
| [candidate_148](profiles/candidate_148.md) | 39.37% | 26.01% | +13.36 pp |
| [candidate_155](profiles/candidate_155.md) | 38.60% | 26.01% | +12.60 pp |
| [candidate_055](profiles/candidate_055.md) | 37.38% | 26.01% | +11.37 pp |
| [candidate_050](profiles/candidate_050.md) | 36.43% | 26.01% | +10.42 pp |
| [candidate_137](profiles/candidate_137.md) | 36.33% | 26.01% | +10.32 pp |
| [candidate_259](profiles/candidate_259.md) | 34.95% | 26.01% | +8.94 pp |
| [candidate_228](profiles/candidate_228.md) | 34.20% | 26.01% | +8.19 pp |
| [candidate_147](profiles/candidate_147.md) | 33.61% | 26.01% | +7.60 pp |
| [candidate_251](profiles/candidate_251.md) | 25.58% | 26.01% | -0.43 pp |
| [candidate_138](profiles/candidate_138.md) | 23.20% | 26.01% | -2.81 pp |
| [candidate_072](profiles/candidate_072.md) | 23.02% | 26.01% | -2.99 pp |
| [candidate_237](profiles/candidate_237.md) | 22.53% | 26.01% | -3.47 pp |
| [candidate_132](profiles/candidate_132.md) | 22.53% | 26.01% | -3.48 pp |
| [candidate_232](profiles/candidate_232.md) | 22.50% | 26.01% | -3.51 pp |
| [candidate_244](profiles/candidate_244.md) | 22.25% | 26.01% | -3.76 pp |
| [candidate_002](profiles/candidate_002.md) | 22.24% | 26.01% | -3.77 pp |
| [candidate_231](profiles/candidate_231.md) | 20.96% | 26.01% | -5.05 pp |
| [candidate_060](profiles/candidate_060.md) | 20.95% | 26.01% | -5.06 pp |
| [candidate_271](profiles/candidate_271.md) | 15.06% | 26.01% | -10.94 pp |
| [candidate_039](profiles/candidate_039.md) | 13.28% | 26.01% | -12.72 pp |
| [candidate_140](profiles/candidate_140.md) | 12.95% | 26.01% | -13.06 pp |
| [candidate_026](profiles/candidate_026.md) | 12.66% | 26.01% | -13.35 pp |
| [candidate_224](profiles/candidate_224.md) | 12.20% | 26.01% | -13.81 pp |
| [candidate_262](profiles/candidate_262.md) | 11.33% | 26.01% | -14.68 pp |
| [candidate_127](profiles/candidate_127.md) | 10.51% | 26.01% | -15.50 pp |
| [candidate_001](profiles/candidate_001.md) | 9.91% | 26.01% | -16.10 pp |
| [candidate_089](profiles/candidate_089.md) | 9.79% | 26.01% | -16.22 pp |
| [candidate_004](profiles/candidate_004.md) | 9.33% | 26.01% | -16.68 pp |
| [candidate_003](profiles/candidate_003.md) | 6.14% | 26.01% | -19.87 pp |
| [candidate_046](profiles/candidate_046.md) | 4.54% | 26.01% | -21.47 pp |
