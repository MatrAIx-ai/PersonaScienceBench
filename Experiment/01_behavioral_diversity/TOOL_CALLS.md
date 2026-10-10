# Actor tool-use analysis

Recorded actor execution/inspection actions per complete original episode; not API requests or shell subcommands.

Pair matched source/question/trial first; average matched trial differences within question, then questions within source; equal source weights (four sources). Absolute means use each setting available cases and need not subtract to the paired differences.

20000 source-stratified study-cluster bootstrap resamples; percentile 95% CI; seed 20261004; marginal descriptive intervals, no significance color or stars

SciConv not applicable; missing actor logs excluded, never zero-filled

| Setting | Calls / episode [95% CI] | Questions | Episodes |
|---|---:|---:|---:|
| Off | 6.33 [5.70, 7.11] | 158 | 445 |
| 155 | 6.60 [5.91, 7.42] | 159 | 425 |
| 001 | 6.10 [5.59, 6.73] | 160 | 448 |
| 003 | 5.43 [4.57, 6.63] | 64 | 64 |
| 046 | 5.64 [5.00, 6.48] | 136 | 136 |

| Row − column | Paired difference [95% CI] | Questions | Episode pairs |
|---|---:|---:|---:|
| 155 − Off | +0.27 [-0.14, +0.73] | 158 | 413 |
| 001 − Off | -0.29 [-0.63, +0.02] | 158 | 417 |
| 001 − 155 | -0.54 [-0.89, -0.20] | 159 | 403 |
| 003 − Off | -0.40 [-1.13, +0.20] | 63 | 63 |
| 003 − 155 | -0.16 [-0.64, +0.32] | 63 | 63 |
| 003 − 001 | -0.08 [-0.47, +0.28] | 62 | 62 |
| 046 − Off | -0.19 [-0.58, +0.22] | 130 | 130 |
| 046 − 155 | -0.27 [-0.56, +0.05] | 128 | 128 |
| 046 − 001 | -0.26 [-0.77, +0.22] | 131 | 131 |
| 046 − 003 | +0.28 [-0.23, +0.92] | 61 | 61 |

## Candidate caption

Pairwise differences in recorded actor tool calls under five simulator persona settings. Calls include execute_command (ASI, BixBench, DiscoveryBench), inspect_repository and execute_check (EXP-Bench); researcher handoffs and protocol actions are excluded. Each cell is row minus column, matched on source, question and trial, averaged over trials within question and over questions within source, then equally over the four sources. Color encodes magnitude and direction, not statistical significance. The diagonal is masked. SciConvBench uses a different interaction interface and is excluded rather than assigned zero calls. Marginal 95% study-cluster bootstrap intervals and pair-specific coverage are supplied in the table. More calls do not necessarily imply better scientific performance or greater behavioral diversity. Single-trial settings do not support estimates of rollout variability.

Extracted tool-call IDs are checked for duplicates within each episode. Counts refer to recorded action invocations, not successful execution or distinct shell commands. Coverage and per-episode provenance hashes are saved in data/tool_calls/.
