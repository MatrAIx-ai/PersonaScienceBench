# Model-level scientific-agent scorecard

| Actor model | Persona-off performance | Mean Persona Performance | Fact recovery (%) | Self-repetition (%) |
|---|---|---|---|---|
| GPT-6 Astra (low) | 47.54 [39.11, 55.46] | 48.82 [40.46, 56.67] | 88.86 [76.96, 97.68] | 12.69 [11.65, 13.73] |

Values are estimates [pointwise 95% study-cluster bootstrap CI]. Persona means average 155/001/003/046 equally; off is a separate reference. Resource metrics are retained as supporting data, outside the main table. For each metric, use questions observed under all five settings, average available trials within question, questions within benchmark, and applicable benchmarks equally. Panels differ by metric; these are historical available-data estimates, not full 200-question coverage. CIs condition on observed trials and do not estimate unseen rollout variation for single-trial settings.

## Definitions and limits

- **Mean Persona Performance:** native score on the existing 0–100 scale; equal weights over five source benchmarks. Original endpoints only, with complete traces and scored outcomes. Historical evaluator versions differ (see summary.json); use this as a provisional retrospective row, not a uniform-judge leaderboard claim.
- **Fact recovery:** mean percentage of required withheld facts recovered, using all eligible SciConv disambiguation runs, without conditioning on success/failure. It is not the failure-conditioned all-facts-complete metric in Experiment 09 panel B.
- **Self-repetition:** Experiment 09's selected 6-word/3-position match definition; messages must have at least 9 word tokens and an episode needs at least two eligible actor messages. Average later-message matched-window fractions. This threshold was selected after exploratory inspection; retain that limitation in the paper. Includes shared actor handoffs/questions, not private reasoning, tool text or final SciConv specifications.
- **Output tokens:** recorded completion tokens summed over all logged actor response records in the entire episode, including reasoning, tool-call generation and final replies. Excludes simulator/judge/input tokens. Missing usage makes the episode unavailable; this differs from Experiment 01's tokens-per-completed-interaction metric.
- **Tool calls:** recorded execute_command, inspect_repository and execute_check invocations; excludes communication/control actions. Applicable to ASI/Bix/Discovery/EXP; SciConv is not assigned zero. Counts do not measure successful execution or the number of shell subcommands.
- **Resource units:** the main table uses absolute means; tokens and their CI endpoints are divided by 1,000 solely for readability. Tool calls remain counts per episode. Persona-off ratios and raw counts are retained only as supporting comparisons; they do not define the primary resource metrics.
- Repetition, tokens and tool counts are descriptive; lower values do not automatically mean better adaptation. Do not combine them into a scalar adaptation score.
- Some settings have only trial 1; repeated settings use all available original trials with equal question/setting weighting. Common questions do not imply matched trial counts. Availability may be outcome-dependent. The closed fixed panel is exploratory and was partly selected using prior effects.
- The Astra metric panels above use historical available data; the full Haiku performance row is appended below. The withdrawn incomplete Sol campaign is excluded. Additional models need the same frozen metric contract and shared question support before ranking; do not reuse these model-specific common panels uncritically.

## Raw resource-use transparency

| Metric | Persona-off mean / episode | Persona mean / episode | Ratio to off | Change from off (%) |
|---|---|---|---|---|
| actor_output_tokens | 4,700.62 | 5,320.35 | 1.132× | +13.18 |
| tool_calls | 5.05 | 5.06 | 1.002× | +0.19 |
## Coverage

| Metric | Common questions | Questions by benchmark | Episodes: off / 155 / 001 / 003 / 046 |
|---|---|---|---|
| performance | 101 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 40} | 300 / 296 / 295 / 101 / 101 |
| fact_recovery | 20 | {"sciconvbench": 20} | 60 / 60 / 60 / 20 / 20 |
| self_repetition | 79 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 19} | 233 / 230 / 227 / 79 / 79 |
| actor_output_tokens | 101 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 40} | 300 / 296 / 295 / 101 / 101 |
| tool_calls | 61 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6} | 180 / 176 / 175 / 61 / 61 |

## Haiku self-collaboration campaign

| Actor model | Persona-off performance | Mean Persona Performance | Fact recovery (%) | Self-repetition (%) |
|---|---|---|---|---|
| GPT-6 Astra (low) | 47.54 [39.11, 55.46] | 48.82 [40.46, 56.67] | 88.86 [76.96, 97.68] | 12.69 [11.65, 13.73] |
| Claude Haiku 4.5 | 21.97 [16.25, 27.71] | 19.72 [15.19, 24.14] | 67.95 [61.77, 74.37] | 21.43 [17.23, 24.53] |

Haiku actor and simulator: Claude Haiku 4.5; judge: GPT-6 Astra. Performance uses 200 questions (40 per benchmark), five settings, one trial, including 120 non-submissions; 95% intervals use the benchmark-stratified study-cluster bootstrap. Haiku fact recovery (67.95%) and self-repetition (21.43%) are collaborator-reported measurements and 95% confidence intervals supplied by the author on 2026-10-07. Their underlying metric records, exact aggregation, sample counts and CI computation method are not available locally; these estimates and intervals have not been independently reproduced. They replace the incorrectly labelled older Opus-simulator values. All non-Off columns represent the four-persona mean; performance weights benchmarks and personas equally.
