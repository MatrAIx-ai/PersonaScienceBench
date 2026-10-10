# Experiment 01 — SciConv interaction output tokens

[Executed notebook](sciconv_tokens.ipynb)

Original Astra-low trials only: 40 SciConv cases (20 disambiguation, 20 inconsistency), six conditions, three trials = 720 planned episodes. Repairs, Sol and the credit-exhausted new baseline are not pooled. One historical infrastructure failure is excluded; 719 scored episodes contribute. Raw private prompts and replies are not copied into derived data.

API completion_tokens is total generated output, including reasoning when reported. Non-reasoning output = completion_tokens − reasoning_tokens only when the reasoning field exists; missing reasoning counts remain missing. Counts are tokens, not characters or whitespace words. Input usage includes prompts/history and is separately available in the call CSV. Failed requests have no recorded successful usage and are not assigned zero token cost.

For each role, average calls within each episode, then trials within each case, then cases equally. Episode totals use the same trial/case weighting. Actor calls include questions and the final specification; question-only and final-output statistics are stored separately. These weights do not equal a pooled mean over all calls.

Pointwise 95% CIs: 20,000 study-cluster bootstrap draws within SciConv mode, holding observed mode weights fixed; seed 20261003. Intervals condition on observed trials, do not separately estimate trial randomness, and are not multiplicity-corrected comparisons.

| Persona | Actor output/call [95% CI] | Simulator output/reply [95% CI] | Actor output/episode | Simulator output/episode |
|---|---|---|---:|---:|
| Off | 160.0 [134.6, 187.7] | 73.9 [62.6, 85.8] | 613.1 | 243.5 |
| 148 | 167.3 [142.4, 195.1] | 90.4 [78.8, 102.8] | 626.3 | 280.9 |
| 155 | 188.7 [161.4, 218.2] | 113.8 [99.3, 129.0] | 749.1 | 404.1 |
| 089 | 148.6 [129.2, 168.4] | 64.7 [56.6, 73.7] | 629.5 | 225.2 |
| 001 | 176.9 [154.0, 201.7] | 83.2 [70.4, 97.6] | 682.9 | 258.1 |
| 127 | 159.3 [136.2, 184.4] | 82.3 [70.8, 94.9] | 624.4 | 276.9 |

![Output tokens by role](figures/sciconv_tokens/output_tokens.png)

## Turn alignment and limitations

Within each episode, role_turn counts API calls in trace order. Actor call 1 precedes the first simulator reply; actor call q is a question paired with simulator reply q until the final actor specification. Actor calls equal researcher calls plus one in all included traces. Actor trajectories by call number mix question and final-specification phases across episodes; the CSV explicitly counts final-specification calls. Later-turn averages are conditional on reaching that turn, with changing case/episode denominators; do not interpret them as within-episode growth.

Episodes with no simulator call contribute zero to simulator episode totals, but have no per-reply value and are excluded from that conditional mean; the figure reports its reduced denominators. The judge is kept separate in the numeric summaries. Tokenization improves on whitespace length comparisons for Mandarin profiles but does not by itself measure information quality or language-normalized verbosity. No causal claim about personality or disclosure follows from token counts.

[Per-call numeric data](data/sciconv_tokens/calls.csv) · [Per-turn means/CIs](data/sciconv_tokens/per_turn_tokens.csv) · [Episode-role totals](data/sciconv_tokens/episode_role_tokens.csv) · [Summary](data/sciconv_tokens/summary.json)

Reproduce: `.venv/bin/python Experiment/01_behavioral_diversity/code/analyze_sciconv_tokens.py`. Use `--refresh` only to extract from saved private traces again. No model calls.
