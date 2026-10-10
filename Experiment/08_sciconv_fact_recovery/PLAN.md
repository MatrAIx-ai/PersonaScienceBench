# Experiment 08 — SciConv deleted-fact recovery

> The offline analysis remains active. Failed new-protocol collection launchers were moved to [the dated archive](../_archive/20261002/08_sciconv_fact_recovery/code/) on 2026-10-02; historical submission commands below describe their original locations.

## Question and relationship to existing experiments

Do researcher personas change how much missing scientific specification information the actor recovers, even when binary FRR changes little? This is a separate, exploratory SciConv analysis, not a replacement for Experiment 02's benchmark mixture or FRR endpoint. Existing Astra outcomes have already been inspected, so this analysis is **not preregistered**.

## Dedicated paper presentation

Fact recovery is a standalone experiment, separate from Experiment 04's conversation case studies. In the [integrated paper plan](../../docs/design/benchmark_paper_plan.md#figures-and-tables-purpose-and-dependencies), **Figure 5** has two panels: mean recovered-fact fraction by persona with 95% CIs, and matched differences from persona-off with 95% CIs. The dedicated result table reports recovery %, paired difference in percentage points, FRR %, cases/episodes and cap hits. Existing [report](REPORT.md), [figure](figures/fact_recovery.png) and [executed notebook](analysis.ipynb) supply these artifacts. Original outcomes are primary; repair and cap-exclusion views are sensitivity analyses. Conversation examples appear separately in Figure 6 and can reference this experiment's findings.

## Sources of the design

- [PR #17](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/17): read native saved judgement `score = k/n`; analyze equal-weight case means; include persona-off, fresh replication and neutral paraphrases; check ten-question-limit sensitivity. Its screened panel and Luna results are not pooled into our Astra panel.
- [PR #12](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/12): distinguish recovery from questioning and disclosure; vary persona wording; retain multiple neutral controls; examine response length and persona visibility. Its GLM-5/fork harness results are a separate experiment.
- [Merged PR #6](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/6): separate knowledge, identity style and volunteering controls; future runs must explicitly freeze these switches and the identity boundary. Existing traces retain their original pinned pre-merge protocol.

## Stage A — Offline reanalysis, implemented

- **Panel:** the frozen existing 20 disambiguation cases; six settings (off, 148, 155, 089, 001, 127); three original trials. 360 eligible episode slots. The 20 inconsistency cases are explicitly excluded from deleted-fact scoring.
- **Primary endpoint:** native recovered deleted facts divided by total deleted facts, before the intent gate. Validate integer numerator/denominator, nonzero denominator, bounds, and agreement with the native issue count. Missing/invalid judgements remain missing, never imputed as perfect or zero recovery.
- **Secondary endpoints:** full fact recovery, native FRR (full resolution with intent preserved), question/reply counts, and whitespace-based reply length. Reply length is not a language-normalized token measure. No new per-fact disclosure or volunteering labels are invented.
- **Aggregation:** mean within case across available trials, then equal case weights. Do not pool all facts into a micro-average that overweights cases with more deleted facts. Paired contrasts use the same case and trial before averaging case differences.
- **CIs:** 20,000 percentile study-cluster bootstrap draws, stratified by domain, with observed domain weights fixed; seed 20261001. Dependence among cases with the same study ID is retained. CIs condition on the observed trial outcomes; they do not separately quantify trial-to-trial randomness. Report five exploratory persona-off contrasts with pointwise CIs, not significance claims or an uncorrected winning-persona search.
- **Sensitivities:** original outcomes versus latest repair outcomes; exclude episodes with at least ten researcher replies from both sides of a paired comparison. Repairs are conditional attempts within an original trial, not additional independent replicates.
- **Difficulty screen:** describe baseline recovery per case and single-fact / near-ceiling / low / multi-fact intermediate bands. Do not select the primary panel using observed persona effects. This retrospective screen cannot supply a confirmatory test set.
- **Provenance:** numeric-only snapshot/CSV plus hashes of original result files, native judge outputs, events and frozen model configs. Do not copy reference facts or private conversation/API content into tracked analysis data. Preserve the old evaluator label even where it misleadingly says `+luna-judge`; verified config model names are the source for role identity.
- **Execution:** local analysis only; no API requests, no Slurm inference job, no change to existing runners or task selection.

## Stage B — Prospective controlled follow-up

1. Freeze one simulator protocol and version it explicitly. Audit the tenth-answer handling before collection; any fix requires a new protocol version and a uniformly rerun comparison, not silently combining old and new episodes.
2. Sample fresh disambiguation cases by domain and study. Use independent persona-off screening and confirmation batches for a multi-fact intermediate-difficulty panel. Keep a representative unscreened reference panel so screening does not redefine the main benchmark claim.
3. Include off, the existing full persona identities, and at least three neutral paraphrases with matched factual boundaries. If testing individual traits, use multiple wordings per trait and independently verify persona visibility, as in PR #12.
4. Hold actor, simulator, judge, reasoning effort, budgets and all three simulator switches fixed across conditions. Randomize execution order in balanced case/condition/trial blocks; use coordinated token throttling before any new large run.
5. Freeze contrasts and multiplicity correction before seeing new outcomes. Use held-out confirmation for screened cases, and independent new trials for wording replication. Decide sample size from a declared minimally relevant difference and measured variability, not a favorable pilot difference.
6. Add per-fact asked / fully disclosed / partly disclosed / volunteered / recovered annotations only with a documented rubric and separate annotation provenance. Native recovery alone does not identify whether the persona helped questioning, disclosure, or the actor's own inference. Response length is a possible mediator/confound, not proof of mechanism; a causal test needs an independently controlled length intervention.

Stage A remains an offline reanalysis. The limited case-study baseline below is now authorized and submitted; independent fresh-case screening, neutral-paraphrase controls and replication remain future work.

## Implementation and artifacts

- `code/analyze.py`: extraction, validation, aggregation, paired CIs, sensitivity tables, figures and report. Default reruns from `data/snapshot.json`; `--refresh` re-reads original local files.
- `code/test_analysis.py`: offline checks for fraction validation, trial aggregation and paired effects.
- `analysis.ipynb`: executable data-to-table-to-figure workflow with saved outputs; every plotting update should be tracked here.
- `data/`: normalized snapshot, episode CSV, summary and exploratory difficulty screen.
- `figures/fact_recovery.{png,pdf,svg}`: annotated recovery and paired-difference bars.
- `REPORT.md`: measured results, coverage, method, limitations and links.
- `status.json`: stage implementation/collection status and validation.

## Figure revision with nature-figure

The two-panel fact-recovery figure now uses a 183 × 100 mm Python layout, restrained colors, panel labels, editable text and annotated numeric CIs. Rendering lives in `code/plot_fact_recovery.py` and remains callable from `analysis.ipynb`. Data and inferential methods are unchanged. Alignment, source, PDF text and collision QA records are in `figures/qa/`; source-data CSV and 600-dpi raster exports accompany PDF/SVG.

## Priority case-study baseline — submitted

User authorized one persona-off trial with 35 workers and Astra low, with highest experiment priority. Job **1986876** has no dependency; five legacy expansions remain held. Requests 35 CPUs, 128 GB and 12 hours. The existing 20 disambiguation cases each receive one fresh episode, so at most 20 episode workers can be busy. This is a protocol case study on familiar cases, not held-out confirmation or a difficulty-screened panel.

Post-PR6 settings are explicit: general knowledge on, persona style switch on, volunteering off, identity disabled; actor/researcher/judge all direct OpenAI GPT-6 Astra low. Output budgets remain 12288/8192/4096. Source code/configuration are frozen and hashed in a separate runtime. The native loop is deliberately retained, including the known tenth-reply handling issue; cap-hit sensitivity is required. It is not silently fixed alongside the disclosure intervention.

A thread-shared rolling request reservation budget of 850,000 estimated tokens/minute covers every direct OpenAI HTTP attempt, including retries. Reservation uses conservative UTF-8 input bytes plus output cap and framing allowance; it is not the account's actual tokenizer or a cross-job quota manager. A 429 imposes at least 60 seconds of shared cooldown; bounded transport retries remain. This regulates request throughput while allowing 35 worker slots. No other experiment job was active at submission.

Runner: `code/run_case_study.py`; submission: `code/submit_case_study.sh`; launch record: `data/new_design_trial1_manifest.json`. Outputs, partial native `results.json`, private traces and rate-budget telemetry are under the recorded run directory. Offline budget/prompt/shell checks passed; no paid smoke test was run.

## Superseding configuration correction

User explicitly requested **general knowledge OFF and volunteering OFF**. Job 1986876 was cancelled; its files were removed at the user’s request and are excluded from the intended baseline. Replacement job 1986925 uses a fresh output directory, the same 20 cases, Astra low in all roles, 35 workers/CPUs, 128 GB, and the same rate limiter. Only the knowledge switch changes scientifically relative to the cancelled job; identity remains off and the style switch/native loop remain unchanged. Current manifest: `data/new_design_trial1_manifest.json`; superseded record: `data/superseded_trial1_1986876.json`. This strict task-fact protocol supersedes the general-knowledge-on description above.

Cancelled job 1986876 run directory removed at user request after confirming cancellation and checking replacement inputs for dependencies. A small audit record remains; Slurm accounting history is unchanged.

### Baseline outcome

Job 1986925 ended FAILED after 00:08:57. All 20 episodes failed with API `insufficient_quota` / `credit_balance_exhausted`; 120 HTTP attempts, zero scored results. These are infrastructure failures, not incorrect scientific answers. Additional credits are required before rerunning. No replacement job was submitted.

## Proposed difficulty revision — 2026-10-01 (not collected)

User requested a harder fact-recovery evaluation after observing the ceiling. In the current selected-panel original data, off fully recovers every missing fact in 47/60 episodes (78.3%). Nine of the 20 cases have only one or two annotated missing facts. These are diagnostics, not evidence that missing-fact count alone explains difficulty. The strict post-PR6 condition still has zero scored cases, so its difficulty is unknown.

Keep recovered/total annotated facts as the primary outcome; change and version the task/protocol difficulty prospectively. Preserve all current results and do not retroactively redefine the measured endpoint.

1. **First establish the strict factual boundary:** general knowledge OFF and volunteering OFF, as already requested. The simulator retains the full specification and answers relevant clarification requests faithfully; it should not hide requested information simply to induce failures. Apply the same boundary to every persona, with persona identity otherwise unchanged. Audit/fix the known tenth-reply issue before a new uniformly versioned comparison.
2. **Controlled interaction budget:** a three-question primary condition, with one- and five-question sensitivity conditions. These are proposed design levels motivated by the typical short interaction horizon, not tuned from observed persona effects. Require a final specification after the last simulator reply; use the same budgets for all settings. This measures efficient information recovery. Existing final scores cannot stand in for truncated-run scores; fresh conversations and endpoint evaluation are needed.
3. **Task-based challenge stratum:** prefer multiple independently relevant, task-specific missing requirements (initial proposal: four to eight), such as numerical constraints, intended objectives, material choices, or boundary conditions that are not uniquely inferable from general scientific knowledge. Do not equate more missing items with harder tasks; inspect whether a single broad question reveals them all. Preserve scientific coherence and the benchmark's original full/incomplete request and annotation provenance. If new omissions are created, mark these as a new task variant and validate the annotated reference independently.
4. **Calibration and confirmation:** screen difficulty using only an independent off pilot on separate development cases, then freeze the challenge selection/protocol before comparing personas on held-out cases. Retain the representative original panel as a reference and report the challenge stratum separately. Do not select cases based on favorable persona differences.

The already available full-fact-recovery indicator (recovered count equals total count) can be reported as a stricter complementary endpoint without new inference. On the current selected settings it is off 78.3%, 155 85.0%, 001 83.3%, 003 80.0%, 046 75.0% of original episodes; these descriptive rates are not a newly harder benchmark. Trials per case are equal within each setting, so episode and equal-case means coincide here. Do not confuse this indicator with intent-gated native FRR.

Status: design recorded only; no runner settings changed, task data regenerated, model requests made, or jobs submitted. New difficulty conditions require a separately authorized inference campaign once API access is restored.
