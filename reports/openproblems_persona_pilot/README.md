# OpenProblems denoising persona pilot

Run 2026-09-30 to 2026-10-01. **125/125 cells have an outcome (124 scored, 1 missing submission)**,
$0.99 at list price. Personas 148, 046 and 155, persona off and `neutral_a`, 5 repeats each, on five
[OpenProblems](https://openproblems.bio/) `task_denoising` datasets. Direct OpenAI `gpt-6-luna`
(reasoning `none`) for actor and researcher; scoring is programmatic (no LLM judge). Same design as the
[DiscoveryBench pilot](../discoverybench_persona_pilot/README.md). [Generated report](REPORT.md) ·
[per-episode results](results.csv) · [screen](screen/REPORT.md) · [configs](configs/) ·
[adapter](../../docs/adapters/openproblems_denoising.md).

**Score:** native molecular-cross-validation metrics (MSE and Poisson loss on held-out molecules), each
scaled so OpenProblems' `no_denoising` control is 0 and `perfect_denoising` is 1, then averaged. Negative
means worse than returning the raw counts. Shown ×100.

**Findings (descriptive):**

1. **No arm differs detectably from persona off.** 148 +5.4 pp (95% CI −9.0 to +20.5, p = 0.53),
   046 +6.1 pp (p = 0.78), 155 +4.9 pp (p = 0.57), `neutral_a` +5.4 pp (p = 0.52). Each persona against
   `neutral_a`: −0.5 to +0.7 pp. All four identity arms sit about 5 pp above persona off, well inside
   the noise.
2. **The task is noisy and hard.** The persona-off run-to-run SD averages 27.5 pp per dataset. In every arm,
   28–48% of episodes scored no better than the raw counts (persona off 10/25, `neutral_a` 8/25,
   148 10/25, 046 12/25, 155 7/25). The actor usually improved MSE but worsened the Poisson loss.
3. **Personas did not change the actor's method.** Every arm mostly chose low-rank (SVD/PCA), kNN
   smoothing or empirical-Bayes shrinkage, in similar proportions (keyword classification of the
   submitted method description).
4. **Language carry-over replicates:** persona 155's researcher wrote Chinese in 13/25 episodes; no
   other arm did. As on DiscoveryBench, this did not change the score.
5. **The DiscoveryBench answer-length effect does not appear here.** Submitted answer length was the
   same with and without an identity (1,587 vs 1,592 characters).

Per-dataset arm means vary in sign (e.g. 046: +48.7 on `mouse_blood_olsson_labelled`, −19.2 on
`immune_cells`), consistent with noise rather than stable persona-by-dataset effects.

## Replication: neutral_b

`neutral_b`, a paraphrase of `neutral_a`, on the same five datasets × 5 repeats with identical settings
([config](configs/neutral_b.json), [report](neutral_b/REPORT.md), [results](neutral_b/results.csv)):
**25/25 scored, $0.17.**

| Contrast | Δ (pp) | 95% CI | Permutation p |
|---|---:|---:|---:|
| neutral_b − persona off | +1.8 | −11.9 to +16.3 | 0.83 |
| neutral_a − persona off | +5.4 | −8.0 to +19.1 | 0.52 |
| neutral_b − neutral_a | −3.6 | −15.9 to +9.0 | 0.62 |

Both neutral texts sit within noise of persona off and of each other. Unlike on DiscoveryBench, where
`neutral_a`'s +21.9 pp failed to replicate, there was no neutral effect here to begin with. Answer length
was similar (1,661 vs 1,808 vs 1,592 characters), and 13/25 `neutral_b` episodes were no better than raw counts.

**Runtime incidents:** the Mac slept twice during this run (on battery), pausing the Docker VM and
dropping its DNS on wake. The scheduler's circuit breaker stopped launching both times; 4 cells failed
before any model call and were relaunched once the network returned (`retry_jobs`: never-started jobs
may retry until they start; episodes that ran retry once). No scored episode was retried or regraded.

## Design and dataset choice

- **Screen** ([report](screen/REPORT.md), 12 episodes, $0.10): persona off × 2 on the six datasets whose
  native evaluation fits an 8 GB Linux VM. Scores were continuous and spanned −1.18 to +0.32, so unlike
  DiscoveryBench no task sat at a floor.
- **Pilot datasets:** `tenx_1k_pbmc`, `mouse_blood_olsson_labelled`, `pancreas`, `tenx_5k_pbmc`,
  `immune_cells`. `cengen` was dropped: it has the highest evaluation memory (6.5 GB peak) and both screen
  runs scored about 0.
- **Information boundary:** the actor sees the task text, file contracts and `train.h5ad`; the researcher
  holds the dataset's metadata (a labelled variant, since the native task gives methods no metadata);
  only the evaluator sees `test.h5ad`.

## What went wrong, and how it was handled

| Event | Effect | Handling |
|---|---|---|
| Docker DNS outage mid-run | 66 jobs failed their free model-list preflight in 0 s (no model calls); 2 running episodes lost their connection | DNS restored; those 68 cells retried once with `--retry-errors` (attempt 2). The scheduler now stops after 3 consecutive fast infrastructure failures |
| Researcher format failures | 155 (once) and 046 (once) returned a decision missing `objectives_open` twice | Counted per persona. The 155 episode was retried; with or without that cell, 155 vs persona off is +4.9 / +4.3 pp |
| Evaluator out of memory | One grading (046, `tenx_5k_pbmc`) was SIGKILLed while another actor ran | Recorded as an evaluator failure (not the actor's), then **regraded from the sealed submission** with no model calls (attempt 3) |
| One genuine missing submission | The actor never handed off a result | Counted as 0 (the pilot convention) |

All original attempts stay in [results.csv](results.csv). The first pass ran at commit `64c2d65`; the
retry pass ran after the scheduler's circuit breaker was added (`scripts/run_persona_pilot.py` only; no
change to adapters, prompts or scoring).

## Limitations

One task family (denoising), five datasets of one data source (`openproblems_v1`) and one model for
actor and researcher. The evaluator environment pins the native scripts' requirements rather than the
`openproblems/base_python:1` image (evaluator version `openproblems-denoising-psb-v1`). Datasets larger than
about 1.5 GB dense could not be evaluated on an 8 GB VM. Uncorrected comparisons.
