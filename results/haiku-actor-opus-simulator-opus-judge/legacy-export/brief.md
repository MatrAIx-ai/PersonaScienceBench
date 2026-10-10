# Haiku actor / Opus collaborator persona pilot

Run dates: October 2–3, 2026  
Analysis date: October 3, 2026

## Summary

Across 25 frozen scientific tasks repeated three times, the normalized native score was **42.56/100 with persona off** and **38.44/100 with `candidate_155`**, a paired difference of **-4.13 points**. The task-bootstrap 95% interval was **[-10.75, 2.25]**, so this pilot does not establish a reliable overall benefit or harm from this persona.

The persona arm submitted a gradable answer in **63/75 episodes (84.0%)**, versus **64/75 (85.3%)** with persona off. This completion gap is itself an agent-behavior result, especially for a weaker actor model.

Here, **submitted** means that the actor completed the benchmark's required submission contract and produced an answer that its native evaluator could grade. It does not merely mean that the runner process finished. For example, an episode is a non-submission when Haiku reaches its actor-call or wall-time limit without calling the required submission tool, or when required structured artifacts are absent. These outcomes are scored zero because successful protocol completion is part of end-to-end agent performance.

The clearest benchmark-specific observation was DiscoveryBench: `candidate_155` was lower in **7/15** task-trial pairs, tied in the other 8, and was never higher. Its mean difference was **-17.39 points**. This is exploratory evidence to replicate on a larger frozen panel, not yet a benchmark-wide claim.

## Experimental design

- Actor: Haiku 4.5 on Amazon Bedrock.
- Simulated researcher and model-based judge: Opus 4.6 on Amazon Bedrock.
- Conditions: `persona_off` versus the fixed `candidate_155` researcher persona.
- Panel: five frozen tasks from each of ASI-Bench, BixBench, DiscoveryBench, EXP-Bench, and SciConvBench.
- Repeats: three independent trials, producing 150 actor episodes and 75 paired persona contrasts.
- Scores: each benchmark's primary native metric normalized to 0–100. A genuine model non-submission is scored zero.

The persona is applied to the simulated collaborator, not directly to the Haiku actor. `candidate_155` is a bundled stress-test profile rather than one isolated trait, so any difference cannot be attributed to age, language, occupation, or personality separately.

## Results by benchmark

| Benchmark | Off | Persona | Paired Δ | Task-bootstrap 95% CI | Valid submissions off | Valid submissions persona |
|---|---:|---:|---:|---:|---:|---:|
| ASI-Bench | 12.54 | 9.26 | -3.29 | [-12.26, 5.69] | 6/15 | 6/15 |
| BixBench | 46.67 | 40.00 | -6.67 | [-20.00, 0.00] | 13/15 | 13/15 |
| DiscoveryBench | 44.21 | 26.83 | -17.39 | [-32.38, -4.40] | 15/15 | 15/15 |
| EXP-Bench | 56.07 | 56.11 | +0.04 | [-11.93, 11.33] | 15/15 | 14/15 |
| SciConvBench | 53.33 | 60.00 | +6.67 | [-13.33, 26.67] | 15/15 | 15/15 |

The cross-benchmark average is descriptive because these benchmarks measure different scientific capabilities. The per-benchmark rows are the primary result.

## Collaboration behavior

| Benchmark | Actor calls off | Actor calls persona | Researcher interactions off | Researcher interactions persona |
|---|---:|---:|---:|---:|
| ASI-Bench | 54.40 | 51.40 | 4.40 | 3.87 |
| BixBench | 24.27 | 23.60 | 2.60 | 3.00 |
| DiscoveryBench | 18.47 | 17.07 | 2.73 | 2.67 |
| EXP-Bench | 8.67 | 13.60 | 2.73 | 2.93 |
| SciConvBench | 2.47 | 2.53 | 1.47 | 1.53 |

Interaction counts are protocol-specific and should be compared within a benchmark, not pooled across benchmarks. The largest process difference was in EXP-Bench, where the persona arm used more actor calls; the trial-1 wall-time non-submission contributes materially to that mean.

## Repeat stability

Trials 1, 2, and 3 are independent repeats of the same experiment, not different experimental conditions. Each used the same frozen 25-task panel, models, persona arms, prompts, limits, and scoring policy. Every episode began with a fresh conversation and workspace, with no memory, training, or output carried over from an earlier trial.

Their results differ because model generation and multi-step agent trajectories are stochastic. A small difference in an early response can change later tool calls, researcher interactions, analyses, and whether a valid answer is submitted. The variation across repeats therefore measures run-to-run instability under the same configuration.

| Trial | Off | Persona | Paired Δ | Submitted off | Submitted persona |
|---:|---:|---:|---:|---:|---:|
| 1 | 37.07 | 45.66 | +8.59 | 22/25 | 21/25 |
| 2 | 44.53 | 38.34 | -6.19 | 21/25 | 20/25 |
| 3 | 46.10 | 31.32 | -14.77 | 21/25 | 22/25 |

Across the 75 task-trial pairs, `candidate_155` scored higher in **16**, lower in **25**, and tied in **34**.

## Data-quality decisions

- Two DiscoveryBench submissions in trial 1 were originally marked as infrastructure errors because the Opus judge omitted a non-scoring JSON `explanation` field. Evaluator-only regrades preserved the original Haiku submissions and produced scores of 60 and 75.
- One trial-1 EXP-Bench persona episode made 59 actor calls and reached the episode wall-time limit without submitting a design. It is counted as a model non-submission with score zero, not excluded as infrastructure.
- Trials 2 and 3 completed all 50 runner jobs. The same EXP task completed in both later trials, showing that the first outcome was stochastic weak-model failure rather than an impossible task.

The analysis applies **3 audited overlays** and leaves all raw run artifacts unchanged.

## What this contributes to the paper

- It tests persona influence under model-capability pressure: a weaker Haiku actor collaborates with a stronger, fixed Opus researcher.
- It shows why end-to-end persona evaluation should measure completion and protocol adherence, not only the quality of answers that survive to grading.
- It provides a reusable paired design across five existing scientific-agent benchmarks without requiring HiL-Bench adoption.
- The current result is a feasibility and variance estimate, not evidence for a general persona effect.

## Recommended author claim

> In a 150-episode pilot using Haiku as the scientific actor and Opus as the persona-conditioned collaborator and judge, persona conditioning produced measurable task-level and completion differences, but no stable overall performance effect on the selected 25-task panel. The result supports studying persona effects as an interaction between collaborator behavior, actor capability, and task protocol.

## Limitations and next experiment

- Only one complex persona was tested; this cannot identify which persona attribute caused a behavior change.
- Five tasks per benchmark are enough for a pilot, not for a benchmark-wide claim. The bootstrap interval reflects the selected task panel after averaging three repeats.
- The Opus researcher and Opus judge share a model family, which may introduce model-specific coupling.
- Next, test several pre-registered personas that vary one dimension at a time and expand the task panel only after freezing the analysis policy.

## Reproduction and artifacts

Raw trial directories:

- `runs/main/haiku-actor-opus-collab-pilot-20261002-trial-1`
- `runs/main/haiku-actor-opus-collab-pilot-20261002-trial-2`
- `runs/main/haiku-actor-opus-collab-pilot-20261002-trial-3`

Generated analysis artifacts:

- `analysis/haiku_actor_opus_persona_pilot/episodes.csv`
- `analysis/haiku_actor_opus_persona_pilot/pairs.csv`
- `analysis/haiku_actor_opus_persona_pilot/summary.json`
- `analysis/haiku_actor_opus_persona_pilot/audit.json`

Frozen task-selection checksum: `746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`.

Analysis command:

```bash
docker/run.sh .venv/bin/python scripts/report_haiku_opus_persona_pilot.py
```
