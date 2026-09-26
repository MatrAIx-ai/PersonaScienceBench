# Full-persona experiment: partial results

Snapshot: 2026-09-26T19:59:38+00:00. **225/310 episodes finished**. The batch continues; this report is a fixed snapshot, not a live counter.

30 source-balanced, behaviorally diverse profiles; two fixed questions per benchmark; one fresh shared persona-off baseline per question. Actor, simulator and judge use GPT-6 Luna with reasoning effort `none`. Full persona text is injected only into the simulator system prompt. Both conditions can use general knowledge; evaluator references remain private.

Scores use ASI score/max score, Bix grade, Discovery final score, EXP gated coverage/100 and SciConv FRR. **Missing submissions count as zero for both persona and baseline** in this report (an explicit analysis convention, not a fabricated native grade). Infrastructure failures and pending episodes are excluded. All comparisons are task-matched; these single-run descriptive results do not establish causality or statistical significance.

| Benchmark | Finished / 62 | Missing submissions: on / off | Infrastructure failures | Paired cases | Persona mean | Matched off mean | Difference |
|---|---:|---:|---:|---:|---:|---:|---:|
| asibench | 34/62 | 0 / 0 | 0 | 32 | 8.43% | 7.83% | +0.60 pp |
| bixbench | 30/62 | 19 / 2 | 1 | 27 | 14.81% | 0.00% | +14.81 pp |
| discoverybench | 37/62 | 2 / 0 | 0 | 35 | 0.71% | 0.00% | +0.71 pp |
| expbench | 62/62 | 0 / 0 | 0 | 60 | 37.49% | 46.67% | -9.18 pp |
| sciconvbench | 62/62 | 0 / 0 | 0 | 60 | 38.33% | 50.00% | -11.67 pp |

Partial benchmark means reflect the profiles that finished so far. Matched off means can differ by task mix; no baseline is regenerated. BixBench comparisons use the explicit missing-submission convention because both baseline runs produced no submission.

## Ten largest absolute persona deviations

Ranking uses **the same 4 questions for all 30 profiles**, with complete comparable outcomes: `sciconvbench:solMech/disambiguation/case_104`, `sciconvbench:foam/disambiguation/case_020`, `expbench:iclr2024/17776/4`, `expbench:neurips2024/98318/6`. Other benchmarks are excluded from this ranking until comparable coverage is available. No candidate is excluded by identity. Ties use candidate ID.

Turns are actor–simulator handoffs (native clarification Q&A for SciConv), excluding tool calls. Words/reply uses visible simulator replies, excluding initial requests and private evidence, averaged per task. Revisions count result-review requests for more work; SciConv has no such stage and is omitted. All behavioral columns use the same ranked questions and show persona on / matched off.

**Shared baseline: 48.33%.** All personas are compared on the same 4 questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.

| Rank | Persona | Score | Change vs off | Traces |
|---:|---|---:|---:|---|
| 1 | [046](profiles/candidate_046.md) | 5.42% | **-42.92 pp** | [Read](traces/candidate_046.md) |
| 2 | [003](profiles/candidate_003.md) | 10.83% | **-37.50 pp** | [Read](traces/candidate_003.md) |
| 3 | [001](profiles/candidate_001.md) | 16.17% | **-32.17 pp** | [Read](traces/candidate_001.md) |
| 4 | [132](profiles/candidate_132.md) | 16.42% | **-31.92 pp** | [Read](traces/candidate_132.md) |
| 5 | [004](profiles/candidate_004.md) | 16.92% | **-31.42 pp** | [Read](traces/candidate_004.md) |
| 6 | [127](profiles/candidate_127.md) | 17.33% | **-31.00 pp** | [Read](traces/candidate_127.md) |
| 7 | [262](profiles/candidate_262.md) | 19.00% | **-29.33 pp** | [Read](traces/candidate_262.md) |
| 8 | [089](profiles/candidate_089.md) | 19.58% | **-28.75 pp** | [Read](traces/candidate_089.md) |
| 9 | [155](profiles/candidate_155.md) | 76.00% | **+27.67 pp** | [Read](traces/candidate_155.md) |
| 10 | [224](profiles/candidate_224.md) | 20.75% | **-27.58 pp** | [Read](traces/candidate_224.md) |

**Behavior on the same questions**

Each cell shows **persona on / baseline**. Rows follow the performance ranking.

| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |
|---|---:|---:|---:|
| [046](profiles/candidate_046.md) | 2.50 / 4.00 | 45.90 / 40.02 | 0.00 / 0.00 |
| [003](profiles/candidate_003.md) | 3.25 / 4.00 | 45.91 / 40.02 | 0.00 / 0.00 |
| [001](profiles/candidate_001.md) | 4.00 / 4.00 | 50.48 / 40.02 | 0.00 / 0.00 |
| [132](profiles/candidate_132.md) | 3.75 / 4.00 | 53.98 / 40.02 | 0.00 / 0.00 |
| [004](profiles/candidate_004.md) | 3.25 / 4.00 | 51.25 / 40.02 | 0.00 / 0.00 |
| [127](profiles/candidate_127.md) | 3.75 / 4.00 | 46.38 / 40.02 | 0.00 / 0.00 |
| [262](profiles/candidate_262.md) | 1.75 / 4.00 | 44.25 / 40.02 | 0.00 / 0.00 |
| [089](profiles/candidate_089.md) | 4.00 / 4.00 | 54.33 / 40.02 | 0.00 / 0.00 |
| [155](profiles/candidate_155.md) | 3.50 / 4.00 | 20.77 / 40.02 | 0.00 / 0.00 |
| [224](profiles/candidate_224.md) | 4.25 / 4.00 | 51.53 / 40.02 | 0.00 / 0.00 |

Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.


## All 30 profiles on the common questions

| Persona | Persona mean | Fixed baseline mean | Difference |
|---|---:|---:|---:|
| [candidate_155](profiles/candidate_155.md) | 76.00% | 48.33% | +27.67 pp |
| [candidate_148](profiles/candidate_148.md) | 75.17% | 48.33% | +26.83 pp |
| [candidate_050](profiles/candidate_050.md) | 71.08% | 48.33% | +22.75 pp |
| [candidate_055](profiles/candidate_055.md) | 71.08% | 48.33% | +22.75 pp |
| [candidate_259](profiles/candidate_259.md) | 66.25% | 48.33% | +17.92 pp |
| [candidate_228](profiles/candidate_228.md) | 64.75% | 48.33% | +16.42 pp |
| [candidate_251](profiles/candidate_251.md) | 47.50% | 48.33% | -0.83 pp |
| [candidate_232](profiles/candidate_232.md) | 45.00% | 48.33% | -3.33 pp |
| [candidate_138](profiles/candidate_138.md) | 44.92% | 48.33% | -3.42 pp |
| [candidate_072](profiles/candidate_072.md) | 44.58% | 48.33% | -3.75 pp |
| [candidate_137](profiles/candidate_137.md) | 44.00% | 48.33% | -4.33 pp |
| [candidate_147](profiles/candidate_147.md) | 43.50% | 48.33% | -4.83 pp |
| [candidate_244](profiles/candidate_244.md) | 42.75% | 48.33% | -5.58 pp |
| [candidate_231](profiles/candidate_231.md) | 41.92% | 48.33% | -6.42 pp |
| [candidate_237](profiles/candidate_237.md) | 41.42% | 48.33% | -6.92 pp |
| [candidate_002](profiles/candidate_002.md) | 40.83% | 48.33% | -7.50 pp |
| [candidate_060](profiles/candidate_060.md) | 40.67% | 48.33% | -7.67 pp |
| [candidate_271](profiles/candidate_271.md) | 26.67% | 48.33% | -21.67 pp |
| [candidate_039](profiles/candidate_039.md) | 22.92% | 48.33% | -25.42 pp |
| [candidate_140](profiles/candidate_140.md) | 22.25% | 48.33% | -26.08 pp |
| [candidate_026](profiles/candidate_026.md) | 21.67% | 48.33% | -26.67 pp |
| [candidate_224](profiles/candidate_224.md) | 20.75% | 48.33% | -27.58 pp |
| [candidate_089](profiles/candidate_089.md) | 19.58% | 48.33% | -28.75 pp |
| [candidate_262](profiles/candidate_262.md) | 19.00% | 48.33% | -29.33 pp |
| [candidate_127](profiles/candidate_127.md) | 17.33% | 48.33% | -31.00 pp |
| [candidate_004](profiles/candidate_004.md) | 16.92% | 48.33% | -31.42 pp |
| [candidate_132](profiles/candidate_132.md) | 16.42% | 48.33% | -31.92 pp |
| [candidate_001](profiles/candidate_001.md) | 16.17% | 48.33% | -32.17 pp |
| [candidate_003](profiles/candidate_003.md) | 10.83% | 48.33% | -37.50 pp |
| [candidate_046](profiles/candidate_046.md) | 5.42% | 48.33% | -42.92 pp |
