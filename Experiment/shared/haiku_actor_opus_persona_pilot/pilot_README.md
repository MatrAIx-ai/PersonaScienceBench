# Earlier 25-task Haiku actor / Opus collaborator persona pilot

## Start here

This experiment asked a simple question:

> Does changing the persona of an AI-simulated research collaborator change how
> well a separate scientific AI agent performs?

The short answer is: **the persona changed some outcomes, but this pilot did not
find a stable overall improvement or decline.** The persona condition averaged
4.13 points lower than persona off, but the uncertainty interval included both
harm and no effect. The largest exploratory difference appeared on
DiscoveryBench, where the persona condition performed worse.

This was a small feasibility study, not a final benchmark result. It shows that
PersonaScienceBench can measure persona-related changes in end-to-end agent
performance using a weaker actor model on Amazon Bedrock.

## Who did what?

Three model roles were involved:

| Role | Model | Job |
|---|---|---|
| Scientific actor | Claude Haiku 4.5 | Solved the task, used tools, analyzed evidence, and submitted the final answer |
| Simulated researcher | Claude Opus 4.6 | Reviewed plans and results and responded to the actor during collaboration |
| Judge | Claude Opus 4.6 | Applied a benchmark's model-based grading procedure when one was required |

The **persona was applied only to the simulated researcher**. Haiku did not
receive the persona as its own identity. The judge and all other settings were
kept the same between conditions.

Using Haiku as the actor was intentional: it tested whether collaborator
persona effects remain visible when the working agent has less capability than
the stronger models commonly used in scientific-agent experiments.

## What were the two conditions?

Every selected task was run under both conditions:

| Condition | Meaning |
|---|---|
| `persona_off` | The Opus researcher collaborated without the synthetic persona profile |
| `candidate_155` | The same Opus researcher was instructed to embody the fixed `candidate_155` profile |

`candidate_155` is a synthetic, bundled stress-test persona. Among many
attributes, it describes a formal Mandarin-speaking, highly conscientious,
orderly, accuracy-oriented, collaborative agronomy practitioner. The complete
profile is in [`candidate_155.md`](candidate_155.md).

Because the profile changes many attributes together, the experiment cannot
tell us whether any observed difference came from language, age, occupation,
personality, communication style, or another individual feature.

## What was run?

The package's frozen main panel contains five scientific benchmark families.
Five tasks were selected from each family:

| Benchmark | What it tests in this experiment |
|---|---|
| ASI-Bench | Multi-step scientific work with required structured artifacts |
| BixBench | Bioinformatics and scientific data-analysis answers |
| DiscoveryBench | Data-supported scientific hypotheses and discoveries |
| EXP-Bench | Experimental-design quality and coverage |
| SciConvBench | Scientific clarification and information recovery through conversation |

The procedure was:

1. Freeze 25 tasks: five from each benchmark family.
2. Run each task once with persona off and once with `candidate_155`.
3. This creates 50 episodes in one trial.
4. Repeat the same 50-episode experiment three times with fresh model calls.
5. Score each episode with its benchmark's original scoring procedure.
6. Normalize the different benchmark scores to a common 0–100 scale for a
   descriptive combined summary.

The final dataset therefore contains:

- 25 unique tasks;
- two persona conditions;
- three independent trials;
- 150 total agent episodes;
- 75 paired comparisons of persona off versus `candidate_155`.

“Paired” means that the two conditions were compared on exactly the same task
within the same trial.

## What does “valid submission” mean?

A valid submission means that Haiku completed the benchmark's required
submission contract and produced an answer that the benchmark could grade.
It does **not** merely mean that the program finished running.

For example, an episode is a non-submission when Haiku:

- reaches its actor-call limit without using the required submission tool;
- reaches the wall-time limit before submitting;
- omits required structured artifacts; or
- produces work but does not place it in the benchmark's required output field.

Non-submissions were scored zero. This is intentional: completing the output
protocol is part of end-to-end agent performance.

Across all three trials:

- persona off produced 64 valid submissions from 75 episodes;
- `candidate_155` produced 63 valid submissions from 75 episodes;
- most missing submissions occurred in ASI-Bench, where both conditions
  submitted successfully in only 6 of 15 episodes.

The similar submission totals mean that the overall score difference was not
simply caused by one condition failing to submit much more often.

## Main results

Across all benchmarks and repeats:

| Condition | Mean normalized score |
|---|---:|
| Persona off | 42.56/100 |
| `candidate_155` | 38.44/100 |
| Paired difference | -4.13 points |

The task-bootstrap 95% interval for the difference was **[-10.75, 2.25]**.
Because this interval crosses zero, the pilot does not establish a reliable
overall benefit or harm from the persona.

Results differed by benchmark:

| Benchmark | Persona off | `candidate_155` | Paired difference | Valid submissions |
|---|---:|---:|---:|---:|
| ASI-Bench | 12.54 | 9.26 | -3.29 | 6/15 in both conditions |
| BixBench | 46.67 | 40.00 | -6.67 | 13/15 in both conditions |
| DiscoveryBench | 44.21 | 26.83 | -17.39 | 15/15 in both conditions |
| EXP-Bench | 56.07 | 56.11 | +0.04 | 15/15 off; 14/15 persona |
| SciConvBench | 53.33 | 60.00 | +6.67 | 15/15 in both conditions |

The combined average should be treated as descriptive because the five
benchmarks measure different abilities. The benchmark-level results are more
informative.

The clearest exploratory observation was DiscoveryBench:
`candidate_155` scored lower in 7 of 15 task-trial comparisons, tied in the
other 8, and was never higher. This should be replicated with more frozen tasks
before being presented as a general result.

## Why are trials 1, 2, and 3 different?

The trials are independent repeats of the **same experiment**, not different
configurations or stages.

Each trial used the same:

- 25 frozen tasks;
- Haiku actor and Opus researcher/judge;
- persona conditions;
- prompts and collaboration protocol;
- call and time limits; and
- scoring policy.

Every episode began with a fresh conversation and workspace. No memory,
training, answer, or other state carried over from one trial to another.

The results differed because model generation and multi-step agent behavior are
stochastic. A small difference in an early response can change later tool
calls, researcher interactions, analysis choices, and whether the agent
eventually submits a valid answer.

| Trial | Persona off | `candidate_155` | Paired difference | Valid submissions |
|---:|---:|---:|---:|---:|
| 1 | 37.07 | 45.66 | +8.59 | 22/25 off; 21/25 persona |
| 2 | 44.53 | 38.34 | -6.19 | 21/25 off; 20/25 persona |
| 3 | 46.10 | 31.32 | -14.77 | 21/25 off; 22/25 persona |

The effect changes direction across trials. This run-to-run instability is the
main reason not to claim a stable overall persona effect from the pilot.

## What happened during data processing?

Three trial-1 records required documented handling:

1. Two DiscoveryBench actor submissions were valid, but the Opus judge omitted
   a non-scoring JSON explanation field. The original Haiku answers were kept
   and graded again after making that optional field tolerant. Their resulting
   scores were 60 and 75.
2. One EXP-Bench persona episode made 59 actor calls but reached its wall-time
   limit without submitting an experiment design. It was classified as a
   genuine model non-submission and scored zero.

No actor answer was regenerated or replaced. The original run artifacts remain
unchanged, and all three decisions are recorded in [`audit.json`](audit.json).

## What can we conclude?

This pilot supports the following statements:

- PersonaScienceBench can run a paired persona experiment across all five
  scientific benchmark families using Bedrock.
- A collaborator persona can coincide with differences in task score,
  interaction behavior, and protocol completion.
- Weak-model evaluation should measure non-submission and run-to-run
  instability, not only the quality of successfully graded answers.
- DiscoveryBench is a useful candidate for a larger follow-up because it showed
  the most consistent difference in this task sample.

This pilot does **not** establish:

- that personas generally improve or harm scientific agents;
- that `candidate_155` is generally harmful;
- which attribute inside `candidate_155` caused a difference;
- that the DiscoveryBench result generalizes beyond these five selected tasks;
  or
- that the normalized cross-benchmark average is a single universal measure of
  scientific ability.

## What should happen next?

The next experiment should use several pre-registered personas that vary one
dimension at a time, retain persona off as the shared control, and expand the
number of frozen tasks. Repeating each condition remains important because this
pilot showed substantial stochastic variation.

## Run the full 200-task campaign

Use [`run_full_campaign.sh`](run_full_campaign.sh) in a tmux session. It keeps
the pilot model configuration—Haiku actor, Opus researcher/judge, and five
workers—but removes the five-tasks-per-benchmark pilot limit and runs all five
package conditions.

```bash
tmux new -s psb-full
./haiku_actor_opus_persona_pilot/run_full_campaign.sh
```

The default run is one trial with 200 tasks × 5 conditions = 1,000 episodes.
The five conditions are `persona_off`, `candidate_155`, `candidate_001`,
`candidate_003`, and `candidate_046`. Thus, this is four enabled personas plus
the shared persona-off control. It is safe to rerun after interruption because
completed episodes are reused.

Before model execution, the script acquires and validates the public assets for
all 40 selected BixBench tasks and all 40 selected ASI-Bench tasks. Downloads
are cached, so later restarts reuse them. The five-condition campaign uses
`runs/main/haiku-actor-opus-five-condition-full-trial-1`; this is deliberately
different from the preserved earlier two-condition attempt.

To retry only genuine infrastructure failures after resolving their cause:

```bash
RETRY_INFRASTRUCTURE=1 \
./haiku_actor_opus_persona_pilot/run_full_campaign.sh
```

Do not enable missing-submission retries. A missing submission is a measured
agent outcome and is scored zero.

## Files in this folder

- [`brief.md`](brief.md): concise author-facing interpretation and recommended
  paper claim.
- [`summary.json`](summary.json): aggregate results and bootstrap intervals.
- [`episodes.csv`](episodes.csv): normalized records for all 150 episodes.
- [`pairs.csv`](pairs.csv): the 75 paired persona comparisons.
- [`audit.json`](audit.json): documented handling of the three trial-1 records.
- [`report.py`](report.py): reproducible analysis and report generator.
- [`run_full_campaign.sh`](run_full_campaign.sh): resumable tmux-friendly full
  experiment runner.
- [`candidate_155.md`](candidate_155.md): complete tested persona.
- [`traces/`](traces/): compact, Git-friendly run evidence.

## Trace policy

The complete raw trials total about 1 GB and are not duplicated here. The
[`traces/`](traces/) folder contains:

- each trial's model and experiment manifest;
- terminal completion counts;
- all 50 top-level native results from each trial;
- the frozen task selection;
- both DiscoveryBench regrades; and
- the EXP-Bench timeout event trace.

This approximately 3 MB bundle is sufficient to inspect and reproduce the
reported numbers without committing complete API logs, private task snapshots,
prepared workspaces, or every intermediate event.

## Reproduce the report

From the repository root:

```bash
docker/run.sh .venv/bin/python haiku_actor_opus_persona_pilot/report.py
```

The script writes analysis artifacts to
`analysis/haiku_actor_opus_persona_pilot` and refreshes the brief under `docs/`.
