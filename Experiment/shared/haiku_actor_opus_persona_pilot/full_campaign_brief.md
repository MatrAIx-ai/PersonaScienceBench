# Haiku actor / Opus collaborator full campaign

Run completed: October 4, 2026  
Analysis date: October 4, 2026

## Executive summary

The full campaign completed **all 1,000 planned episodes**: 200 frozen scientific tasks under persona off and four persona-conditioned collaborator settings. Haiku 4.5 was the scientific actor; Opus 4.6 was the simulated researcher and model-based judge.

The persona-off control averaged **34.60/100**. The four persona comparisons were:

| Persona | Mean score | Difference vs off | Paired task-bootstrap 95% CI | Valid submissions | Win / tie / loss vs off |
|---|---:|---:|---:|---:|---:|
| `candidate_155` | 33.55 | -1.05 | [-6.22, 4.09] | 170/200 | 51 / 97 / 52 |
| `candidate_001` | 34.19 | -0.41 | [-5.11, 4.26] | 173/200 | 44 / 103 / 53 |
| `candidate_003` | 33.04 | -1.56 | [-6.42, 3.36] | 171/200 | 48 / 99 / 53 |
| `candidate_046` | 34.51 | -0.09 | [-5.39, 5.14] | 179/200 | 46 / 99 / 55 |

These intervals describe variation across this frozen task panel. They are unadjusted for four persona comparisons, and the single trial does not measure run-to-run model variance. Accordingly, the campaign is evidence about this specific model/protocol/task configuration, not a general causal ranking of human traits.

## Main findings

- None of the four overall persona-vs-control intervals excluded zero. The largest pooled difference was `candidate_003` at **-1.56 points**, with a 95% interval of **[-6.42, 3.36]**.
- Averaging the four selected persona conditions within each task produced a difference of **-0.78 points** versus persona off, with a 95% interval of **[-5.05, 3.38]**.
- EXP-Bench showed the clearest within-trial pattern: all four persona conditions were lower than persona off, with differences from **-3.06 to -10.32 points**. Each unadjusted paired task-bootstrap interval was below zero.
- The pilot's large negative DiscoveryBench result for `candidate_155` did not replicate on the full 40-task panel: the full-panel difference was **-1.05 points** and its interval crossed zero.
- `candidate_046` produced the most valid submissions (**179/200**) while its mean score was nearly identical to persona off. This separates protocol completion from answer quality.

## Experimental design

- Scientific actor: Claude Haiku 4.5 on Amazon Bedrock.
- Simulated researcher and model-based judge: Claude Opus 4.6 on Bedrock.
- Persona placement: researcher only; the Haiku actor and judge were held fixed.
- Conditions: `persona_off`, `candidate_155`, `candidate_001`, `candidate_003`, and `candidate_046`.
- Tasks: 40 each from ASI-Bench, BixBench, DiscoveryBench, EXP-Bench, and SciConvBench.
- Repeats: one trial, yielding 200 episodes per condition and 1,000 total.
- Pairing: every persona result is compared with persona off on the same task.
- Scoring: native benchmark metrics normalized to 0–100; genuine model non-submissions remain zero.

A **valid submission** means the actor completed the benchmark's required submission contract and produced an answer its native evaluator could grade. It does not merely mean the process exited. Missing submissions caused by actor step limits, wall-time limits, or absent required artifacts are retained as zero-score model outcomes.

## Scores by benchmark

| Benchmark | Off | 155 | 001 | 003 | 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 9.83 | 5.94 | 7.26 | 8.85 | 9.84 |
| BixBench | 27.50 | 32.50 | 32.50 | 27.50 | 35.00 |
| DiscoveryBench | 22.28 | 21.23 | 15.83 | 25.53 | 20.34 |
| EXP-Bench | 58.39 | 48.08 | 55.33 | 53.31 | 52.36 |
| SciConvBench | 55.00 | 60.00 | 60.00 | 50.00 | 55.00 |

## Paired differences by benchmark

| Benchmark | 155 vs off | 001 vs off | 003 vs off | 046 vs off |
|---|---:|---:|---:|---:|
| ASI-Bench | -3.88 | -2.56 | -0.97 | +0.02 |
| BixBench | +5.00 | +5.00 | +0.00 | +7.50 |
| DiscoveryBench | -1.05 | -6.45 | +3.25 | -1.94 |
| EXP-Bench | -10.32 | -3.06 | -5.08 | -6.03 |
| SciConvBench | +5.00 | +5.00 | -5.00 | +0.00 |

The cross-benchmark average is descriptive because the five benchmark families measure different scientific capabilities. Benchmark-specific patterns should be interpreted before the pooled ranking.

## Submission behavior

| Benchmark | Off | 155 | 001 | 003 | 046 |
|---|---:|---:|---:|---:|---:|
| ASI-Bench | 19/40 | 20/40 | 19/40 | 19/40 | 23/40 |
| BixBench | 32/40 | 35/40 | 34/40 | 33/40 | 36/40 |
| DiscoveryBench | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| EXP-Bench | 40/40 | 35/40 | 40/40 | 39/40 | 40/40 |
| SciConvBench | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |

Submission differences are part of the measured end-to-end persona effect, especially with a weaker actor. They should not be filtered out merely because a successfully submitted answer would have been gradable.

## Completion and data quality

- Final accounting: **1,000/1,000 runner jobs finished**.
- **9 slots** completed on attempt 2: **4** had a recorded infrastructure/runtime failure on attempt 1, and **5** had no native result before the campaign was resumed.
- Model missing/no-submission outcomes were not retried.
- No score was manually changed and no analysis overlay was applied.
- Raw `results.json` SHA-256: `f5a6168938a3626bc360c01de22d6b06dc7570785fc25a894296e20fbac6af58`.

The attempt-2 slots are listed in `full_campaign_audit.json`. Their first attempt directories are preserved in the raw run; the compact bundle reports the completed outcomes.

## What this contributes to the paper

- It scales the feasibility pilot to the complete frozen 200-task panel and four distinct synthetic researcher personas.
- It measures persona effects under capability asymmetry: a weaker Haiku actor works with a stronger Opus collaborator.
- It treats protocol completion, task score, and collaboration behavior as joint outcomes rather than analyzing only successful answers.
- It provides paired within-task contrasts across five scientific-agent benchmarks, reducing task-composition confounding between persona settings.

## Interpretation boundary

This is one stochastic trial. The earlier 25-task pilot showed that the same persona comparison can change direction across fresh repeats. The full campaign therefore improves task coverage but does not replace replication. The correct paper framing is a full-panel first trial plus a separate three-repeat variance pilot—not a definitive population-level persona effect.

The profiles are high-dimensional synthetic bundles and sometimes contain internally unusual combinations. A result identifies a condition-level effect; it cannot isolate age, language, expertise, personality, or any other single attribute.

## Condition ranking for this trial

1. `persona_off` (control): 34.60/100, 171/200 valid submissions.
2. `candidate_046`: 34.51/100, 179/200 valid submissions.
3. `candidate_001`: 34.19/100, 173/200 valid submissions.
4. `candidate_155`: 33.55/100, 170/200 valid submissions.
5. `candidate_003`: 33.04/100, 171/200 valid submissions.

This ranking is descriptive and should not be read as a stable ordering without fresh full-panel trials.

## Files

- `full_campaign_summary.json`: aggregate statistics and bootstrap intervals.
- `full_campaign_episodes.csv`: one compact row for each of 1,000 episodes.
- `full_campaign_pairs.csv`: 800 same-task persona/control comparisons.
- `full_campaign_audit.json`: raw-input checksums and infrastructure repairs.
- `traces/full-campaign-receipt.json`: compact completion/provenance receipt.
- `report_full_campaign.py`: offline report generator.
- `candidate_*.md`: exact synthetic researcher persona prompts.

## Reproduce

From the repository root:

```bash
docker/run.sh .venv/bin/python haiku_actor_opus_persona_pilot/report_full_campaign.py
```

The complete raw run remains at `runs/main/haiku-actor-opus-five-condition-full-trial-1` and is intentionally not duplicated in this Git-friendly folder.
