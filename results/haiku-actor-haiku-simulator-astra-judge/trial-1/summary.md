# Haiku self-collaboration / Astra judge: full persona campaign

Run completed: 2026-10-06T13:54:27.144078+00:00  
Analysis generated: 2026-10-06

## Executive summary

This is the completed **1,000-episode** campaign: 200 frozen scientific tasks evaluated under persona off and four researcher-persona conditions.
Claude Haiku 4.5 served as both the scientific actor and simulated researcher. GPT-6 Astra with low reasoning effort served as the independent model-based judge. All model calls used Amazon Bedrock.

The persona is applied only to the simulated researcher. The actor model, judge, tasks, limits, and native benchmark scoring are fixed across conditions.

| Condition | Mean score /100 | Difference vs off | Paired 95% interval | Valid submissions | Win / tie / loss |
|---|---:|---:|---:|---:|---:|
| `persona_off` | 21.97 | — | — | 189/200 | — |
| `candidate_155` | 19.49 | -2.47 | [-6.49, 1.70] | 178/200 | 27 / 130 / 43 |
| `candidate_001` | 22.04 | +0.08 | [-4.41, 4.58] | 165/200 | 41 / 119 / 40 |
| `candidate_003` | 19.43 | -2.53 | [-7.16, 2.11] | 176/200 | 34 / 121 / 45 |
| `candidate_046` | 17.90 | -4.07 | [-8.91, 0.69] | 172/200 | 26 / 126 / 48 |

The average of the four persona conditions, computed within each task, was **-2.25 points** relative to persona off (95% interval [-5.66, 1.13]).

None of the four overall paired intervals excluded zero.

## Scores by benchmark

| Benchmark | Off | 155 | 001 | 003 | 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 9.54 | 7.28 | 6.24 | 6.50 | 3.87 |
| BixBench | 32.50 | 35.00 | 32.50 | 35.00 | 27.50 |
| DiscoveryBench | 8.37 | 7.28 | 9.72 | 9.96 | 10.77 |
| EXP-Bench | 16.93 | 12.89 | 24.24 | 13.21 | 9.85 |
| SciConvBench | 42.50 | 35.00 | 37.50 | 32.50 | 37.50 |

## Paired differences by benchmark

| Benchmark | 155 vs off | 001 vs off | 003 vs off | 046 vs off |
|---|---:|---:|---:|---:|
| ASI-Bench | -2.25 | -3.29 | -3.04 | -5.67 |
| BixBench | +2.50 | +0.00 | +2.50 | -5.00 |
| DiscoveryBench | -1.08 | +1.35 | +1.59 | +2.40 |
| EXP-Bench | -4.03 | +7.32 | -3.72 | -7.08 |
| SciConvBench | -7.50 | -5.00 | -10.00 | -5.00 |

## Submission behavior

A valid submission means the actor completed the benchmark’s required output contract and produced an answer its native evaluator could grade. It does not merely mean that the process exited. Model non-submissions remain zero-score benchmark outcomes.

| Benchmark | Off | 155 | 001 | 003 | 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 33/40 | 27/40 | 20/40 | 22/40 | 20/40 |
| BixBench | 39/40 | 35/40 | 34/40 | 37/40 | 35/40 |
| DiscoveryBench | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| EXP-Bench | 37/40 | 36/40 | 31/40 | 37/40 | 37/40 |
| SciConvBench | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |

## Completion and repair audit

- Final runner states: **{'finished': 1000}**.
- Final-attempt distribution: **{1: 969, 2: 25, 3: 6}**.
- Episodes completed after attempt 1: **31**.
- Invalid actor-image classifications repaired: **4**.
- Numeric scores changed by those repairs: **0**.
- The malformed actor plots retained zero visual credit. They were changed from evaluator-infrastructure errors to scientific submission defects; actors were not rerun and no additional model calls were made.
- Two genuinely incomplete researcher-format episodes were rerun after non-control bookkeeping omissions became explicitly normalized and audited.

## Interpretation

This run contributes a capability-sensitive condition: a relatively small Haiku model performs the scientific work and also simulates the collaborator, while a stronger independent Astra judge evaluates model-graded components.
It tests whether persona conditioning changes self-collaboration behavior, protocol completion, resource use, and scientific scores.

This is one stochastic trial. The paired intervals describe variation over the frozen task panel but do not estimate run-to-run model variance. The profiles are high-dimensional synthetic bundles, so differences are effects of complete persona conditions—not isolated demographic or personality traits.

## Descriptive ranking

1. `candidate_001`: 22.04/100; 165/200 valid submissions.
2. `persona_off`: 21.97/100; 189/200 valid submissions.
3. `candidate_155`: 19.49/100; 178/200 valid submissions.
4. `candidate_003`: 19.43/100; 176/200 valid submissions.
5. `candidate_046`: 17.90/100; 172/200 valid submissions.

Treat this ordering as descriptive until independently replicated.
