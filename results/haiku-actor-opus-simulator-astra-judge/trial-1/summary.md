# Astra regrade of the Haiku-actor / Opus-researcher campaign

## What was done

The completed 1,000-episode Haiku-actor / Opus-researcher campaign was re-evaluated with GPT-6 Astra at low reasoning effort. The actor and researcher trajectories were frozen and were not rerun.

The native evaluators made **2,587 Astra calls** across **731 endpoints**. Another **133 submitted endpoints** used deterministic native scoring, and **136 original non-submissions** remained zero without a call.

## Astra-regraded scores

| Condition | Astra mean | Difference vs off | Paired 95% interval | Submitted | Astra calls |
|---|---:|---:|---:|---:|---:|
| `persona_off` | 26.29 | — | — | 171/200 | 530 |
| `candidate_155` | 26.50 | +0.21 | [-4.73, 5.27] | 170/200 | 510 |
| `candidate_001` | 27.16 | +0.87 | [-4.33, 6.07] | 173/200 | 495 |
| `candidate_003` | 27.36 | +1.07 | [-4.20, 6.30] | 171/200 | 528 |
| `candidate_046` | 27.13 | +0.84 | [-4.35, 6.12] | 179/200 | 524 |

Averaging the four persona conditions within each task produced a pooled effect of **+0.75 points** versus persona off (95% interval [-3.45, 4.91]).

## Researcher-model ablation

Both sides below use Haiku as actor and Astra as judge. The comparison changes the simulated researcher from Haiku to Opus.

| Condition | Opus researcher | Haiku researcher | Difference | Paired 95% interval |
|---|---:|---:|---:|---:|
| `persona_off` | 26.29 | 21.97 | +4.32 | [-0.63, 9.39] |
| `candidate_155` | 26.50 | 19.49 | +7.01 | [2.10, 12.03] |
| `candidate_001` | 27.16 | 22.04 | +5.12 | [0.12, 10.19] |
| `candidate_003` | 27.36 | 19.43 | +7.93 | [2.83, 13.12] |
| `candidate_046` | 27.13 | 17.90 | +9.23 | [3.61, 14.94] |

## Does researcher capability change the persona effect?

| Persona | Effect with Opus researcher | Effect with Haiku researcher | Difference-in-differences | Paired 95% interval |
|---|---:|---:|---:|---:|
| `candidate_155` | +0.21 | -2.47 | +2.68 | [-3.79, 9.09] |
| `candidate_001` | +0.87 | +0.08 | +0.80 | [-5.53, 7.22] |
| `candidate_003` | +1.07 | -2.53 | +3.60 | [-2.90, 10.31] |
| `candidate_046` | +0.84 | -4.07 | +4.91 | [-1.47, 11.23] |

The pooled persona effect was **+0.75** with the Opus researcher and **-2.25** with the Haiku researcher. Their difference-in-differences was **+3.00 points** (95% interval [-1.87, 7.98]).

## Interpretation boundary

This is a useful researcher-capability ablation because actor, task panel, conditions, and active Astra evaluator are aligned. However, it compares one independently sampled trajectory trial for each researcher model. The task-bootstrap intervals do not capture run-to-run model variance, and the two campaigns were executed at different times. Treat the researcher comparison as strong exploratory evidence until replicated.

The original Opus-judge scores are retained in `episodes.csv` for calibration analysis. Differences between those scores and the Astra regrade can also include active evaluator-version changes, not only judge model calibration.
