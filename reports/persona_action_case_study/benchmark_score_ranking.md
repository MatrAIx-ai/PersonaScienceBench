# Persona benchmark score ranking

This table ranks the 30 action personas by their mean task-paired deviation from persona off. Each benchmark's primary native metric is normalized to 0–1 before averaging. A persona-side missing submission is scored as zero because it produced no gradable answer. Infrastructure, launch, and transport failures are excluded and reduce coverage.

Retired benchmarks absent from this comparison: ScienceAgentBench and Terminal-Bench-Science. Additional analysis exclusions: none.

The common persona-off average is **0.4685** across **9 of 10 included tasks**. Control tasks without a native score and excluded from paired scoring: `bixbench:bix-54-q2`. Persona-specific baseline averages can differ when an infrastructure failure excludes another task.

Primary metrics: ASI score/max score; Bix grade; Discovery final score; EXP gated coverage/100; SciConv FRR.

| Rank | Persona | Score average | Paired off average | Deviation | Coverage | Missing→0 | Infra excluded |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `candidate_009` | 0.7239 | 0.5117 | +0.2122 | 6/9 | 0 | 3 |
| 2 | `candidate_259` | 0.6595 | 0.4685 | +0.1911 | 9/9 | 0 | 0 |
| 3 | `candidate_069` | 0.6292 | 0.4685 | +0.1607 | 9/9 | 0 | 0 |
| 4 | `candidate_095` | 0.6218 | 0.4685 | +0.1533 | 9/9 | 0 | 0 |
| 5 | `candidate_077` | 0.6182 | 0.4685 | +0.1497 | 9/9 | 0 | 0 |
| 6 | `candidate_011` | 0.6007 | 0.4685 | +0.1322 | 9/9 | 0 | 0 |
| 7 | `candidate_090` | 0.5959 | 0.4685 | +0.1274 | 9/9 | 0 | 0 |
| 8 | `candidate_096` | 0.5814 | 0.4685 | +0.1129 | 9/9 | 0 | 0 |
| 9 | `candidate_053` | 0.5718 | 0.4685 | +0.1033 | 9/9 | 0 | 0 |
| 10 | `candidate_066` | 0.5714 | 0.4685 | +0.1029 | 9/9 | 0 | 0 |
| 11 | `candidate_003` | 0.5664 | 0.4685 | +0.0979 | 9/9 | 0 | 0 |
| 12 | `candidate_036` | 0.6083 | 0.5117 | +0.0967 | 6/9 | 0 | 3 |
| 13 | `candidate_100` | 0.5628 | 0.4854 | +0.0775 | 8/9 | 0 | 1 |
| 14 | `candidate_043` | 0.4600 | 0.4020 | +0.0580 | 8/9 | 0 | 1 |
| 15 | `candidate_108` | 0.5125 | 0.4685 | +0.0441 | 9/9 | 0 | 0 |
| 16 | `candidate_107` | 0.5103 | 0.4685 | +0.0418 | 9/9 | 0 | 0 |
| 17 | `candidate_122` | 0.5059 | 0.4685 | +0.0374 | 9/9 | 0 | 0 |
| 18 | `candidate_059` | 0.5044 | 0.4685 | +0.0360 | 9/9 | 0 | 0 |
| 19 | `candidate_232` | 0.5018 | 0.4685 | +0.0334 | 9/9 | 0 | 0 |
| 20 | `candidate_063` | 0.4996 | 0.4685 | +0.0311 | 9/9 | 0 | 0 |
| 21 | `candidate_054` | 0.4970 | 0.4685 | +0.0285 | 9/9 | 0 | 0 |
| 22 | `candidate_120` | 0.4892 | 0.4685 | +0.0207 | 9/9 | 0 | 0 |
| 23 | `candidate_007` | 0.5250 | 0.5088 | +0.0162 | 8/9 | 0 | 1 |
| 24 | `candidate_105` | 0.4787 | 0.4685 | +0.0102 | 9/9 | 0 | 0 |
| 25 | `candidate_097` | 0.4723 | 0.4685 | +0.0038 | 9/9 | 0 | 0 |
| 26 | `candidate_064` | 0.4591 | 0.4685 | -0.0093 | 9/9 | 1 | 0 |
| 27 | `candidate_048` | 0.4448 | 0.4685 | -0.0237 | 9/9 | 0 | 0 |
| 28 | `candidate_038` | 0.4495 | 0.4971 | -0.0476 | 7/9 | 0 | 2 |
| 29 | `candidate_005` | 0.4144 | 0.4685 | -0.0541 | 9/9 | 0 | 0 |
| 30 | `candidate_019` | 0.3253 | 0.4685 | -0.1432 | 9/9 | 0 | 0 |

## Reading the ranking

24 of 30 personas have full 9-task coverage. Rows with lower coverage are less comparable: for example, a high average based on six or eight tasks may reflect which tasks survived rather than a stronger persona. These are descriptive single-run differences against shared controls; they are not uncertainty-adjusted effect estimates.
