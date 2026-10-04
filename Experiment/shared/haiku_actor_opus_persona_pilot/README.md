# Haiku actor / Opus collaborator persona experiments

## Start here

This folder contains a completed experiment on whether the persona of an
AI-simulated research collaborator changes a scientific agent's performance.

The final campaign ran:

- 200 frozen scientific tasks;
- five collaborator settings: persona off plus four synthetic personas;
- one episode for every task/setting combination;
- **1,000 total episodes, all completed**.

Claude Haiku 4.5 was the scientific actor. Claude Opus 4.6 was the simulated
researcher and model-based judge. All calls used Amazon Bedrock. The persona
was applied only to the Opus researcher; the Haiku actor, judge, tasks, limits,
and scoring policy were held fixed.

Read [`full_campaign_brief.md`](full_campaign_brief.md) for the author-facing
result. The compact CSV and JSON files in this folder reproduce its numbers
without copying the large raw run.

## Main result

The persona-off control averaged **34.60/100**. None of the four personas had a
reliably different overall score in the paired task bootstrap:

| Setting | Mean score | Difference vs persona off | 95% interval | Valid submissions |
|---|---:|---:|---:|---:|
| `persona_off` | 34.60 | — | — | 171/200 |
| `candidate_155` | 33.55 | -1.05 | [-6.22, 4.09] | 170/200 |
| `candidate_001` | 34.19 | -0.41 | [-5.11, 4.26] | 173/200 |
| `candidate_003` | 33.04 | -1.56 | [-6.42, 3.36] | 171/200 |
| `candidate_046` | 34.51 | -0.09 | [-5.39, 5.14] | 179/200 |

Averaging the four selected persona conditions within each task gave a
**-0.78-point** difference from persona off; its 95% interval also crossed
zero.

The clearest exploratory benchmark-specific pattern was EXP-Bench: all four
persona conditions were lower than persona off by 3.06–10.32 points, and each
unadjusted paired task-bootstrap interval was below zero. This needs a fresh
trial before it is treated as a stable finding.

The earlier pilot's large negative DiscoveryBench result for `candidate_155`
did not replicate on the full 40-task DiscoveryBench panel. Its full-panel
difference was -1.05 points with an interval that crossed zero.

## What was compared?

Every condition used the same 40 tasks from each benchmark:

| Benchmark | What it tests here |
|---|---|
| ASI-Bench | Multi-step scientific work with required structured artifacts |
| BixBench | Bioinformatics and scientific data-analysis answers |
| DiscoveryBench | Data-supported scientific hypotheses and discoveries |
| EXP-Bench | Experimental-design quality and coverage |
| SciConvBench | Scientific clarification and information recovery |

The five collaborator settings were:

| Setting | Meaning |
|---|---|
| `persona_off` | The Opus researcher collaborated without a synthetic persona |
| `candidate_155` | Opus embodied the exact profile in `candidate_155.md` |
| `candidate_001` | Opus embodied the exact profile in `candidate_001.md` |
| `candidate_003` | Opus embodied the exact profile in `candidate_003.md` |
| `candidate_046` | Opus embodied the exact profile in `candidate_046.md` |

These profiles vary many attributes simultaneously. The experiment estimates
condition-level effects; it cannot identify age, language, occupation,
personality, or another single attribute as the cause.

## What does “submitted” mean?

A valid submission means Haiku completed the benchmark's required output
contract and produced an answer its native evaluator could grade. It does not
merely mean that the process finished.

An episode is a non-submission when, for example, Haiku reaches its step or
wall-time limit without using the required submission mechanism or omits
required structured artifacts. These outcomes remain in the analysis with a
score of zero because protocol completion is part of end-to-end agent
performance.

## How to interpret the result

The full campaign improves task coverage, but it contains only **one stochastic
trial**. It therefore does not measure run-to-run model variance.

The earlier pilot repeated 25 tasks three times and found that the
`candidate_155` effect changed direction across trials. The scientifically
appropriate framing is:

> The complete 200-task first trial found no stable overall score difference
> for any of four persona-conditioned collaborators. It did reveal
> benchmark-specific and submission-behavior differences worth replication,
> especially the common negative pattern on EXP-Bench.

Do not describe the descriptive condition ranking as a stable ranking of
personas or human traits.

## Data quality and retries

- Final runner accounting is 1,000/1,000 finished.
- Nine slots ended on attempt 2.
- Four had a recorded infrastructure/runtime failure on attempt 1.
- Five had no native result before the campaign was resumed.
- Model missing/no-submission outcomes were not intentionally retried.
- No score was manually changed and no analysis overlay was applied.

Exact slots and raw-input checksums are in
[`full_campaign_audit.json`](full_campaign_audit.json).

## Files

Full 1,000-episode campaign:

- [`full_campaign_brief.md`](full_campaign_brief.md): concise findings and
  paper interpretation.
- [`full_campaign_summary.json`](full_campaign_summary.json): aggregate
  statistics and paired bootstrap intervals.
- [`full_campaign_episodes.csv`](full_campaign_episodes.csv): one compact row
  per episode.
- [`full_campaign_pairs.csv`](full_campaign_pairs.csv): 800 same-task
  persona/control comparisons.
- [`full_campaign_audit.json`](full_campaign_audit.json): completion,
  checksums, and retry provenance.
- [`report_full_campaign.py`](report_full_campaign.py): reproducible offline
  report generator.
- [`traces/full-campaign-receipt.json`](traces/full-campaign-receipt.json):
  compact completion and provenance receipt.

Earlier 25-task, three-repeat pilot:

- [`brief.md`](brief.md): pilot findings.
- [`summary.json`](summary.json): pilot aggregate results.
- [`episodes.csv`](episodes.csv): 150 pilot episodes.
- [`pairs.csv`](pairs.csv): 75 pilot comparisons.
- [`audit.json`](audit.json): pilot data-quality decisions.
- [`report.py`](report.py): pilot report generator.
- [`pilot_README.md`](pilot_README.md): detailed explanation of the pilot.
- [`traces/`](traces/): compact pilot evidence plus the full-campaign receipt.

Experiment inputs:

- `candidate_001.md`, `candidate_003.md`, `candidate_046.md`, and
  `candidate_155.md`: exact researcher persona prompts.
- [`run_full_campaign.sh`](run_full_campaign.sh): resumable campaign launcher.

## Reproduce the full report

The raw run is intentionally not duplicated in this Git-friendly folder. It
remains at:

```text
runs/main/haiku-actor-opus-five-condition-full-trial-1
```

From the repository root:

```bash
docker/run.sh .venv/bin/python \
  haiku_actor_opus_persona_pilot/report_full_campaign.py
```

The report generator verifies the 1,000 expected slots, fixed model roles,
task selection, benchmark counts, and raw input hashes before writing the
compact artifacts.
