# Offline four-metric reporting suite

> Current-version note (2026-10-01): The latest figure is embedded in `metric_suite.ipynb`: actor self-repetition (3/6 positional word matches), failure-conditioned recovery bars, and descriptive cumulative native performance. Exported report/figure snapshots and earlier design notes below are preserved historical versions.

Authorized: extract and recompute from saved traces, native evaluations, cached results only. No new LLM inference, annotations, embeddings, scheduler jobs, or scientific reruns. Preserve existing figures.

Selected settings: off/155/001/003/046. Original endpoints throughout this suite; old repaired-performance reports remain unchanged. This is an integrated analysis of Experiments 01/02/08, not a new collection campaign.

1. Ordered native interaction-pattern repetition. Same-question comparisons, common five-setting trace panel requiring at least two original complete traces for each repeated setting and one for each single-trial setting. Between-persona cells average all cross-rollout pairs within question; within-persona cells average distinct repeat pairs. Average tasks within source, then sources equally for the aggregate. Re-extract native events in original order; remove initial requests and first required handoff per review phase while retaining actual review decision outcomes, optional handoffs and termination. SciConv patterns retain question/reply alternation and termination, so they largely measure trajectory length. Export a same-length sensitivity and denominators. Diagonals for single-trial personas are unavailable, never zero.
2. Native deleted-fact recovery. Read existing disambiguation judge fractions only; source counts verified. Average original repeats within case then cases equally. Include all five selected settings; display means, CIs, paired contrasts and common-case sensitivity. No disclosure/incorporation labels inferred.
3. Native scientific scores. Reuse frozen original endpoint scores, evaluator-aware comparisons. Five-source absolute panel and super-family supplement; original ASI absolute scores remain mixed-evaluator descriptive values. Extract all pairwise compatible contrasts. Missing scientific submissions=0; infrastructure failures missing.
4. Failed-task coverage. Bix correctness and SciConv native FRR only; no thresholds invented for continuous scores. Fixed common questions requiring all three off trials and at least one valid result for each of four personas, with evaluator compatibility. Enumerate off subsets and persona subsets at m=1,2,3; one episode per distinct persona, averaging uniformly over its available trials. This estimates a specified balanced allocation strategy, not best-persona selection. Report unique failed tasks, paired difference, both exclusive sets, marginal gains and intent-preserved SciConv sensitivity. Exclude infrastructure failures; record coverage attrition.

Uncertainty: 20,000 source-stratified study-cluster percentile bootstrap draws retaining all matched comparisons within a sampled study; question-equal means with original source weights (aggregate repetition explicitly equal source weights). Conditional on observed trials/available outcomes, not independent replicate-pair sampling. Sparse strata are disclosed; no CI for one-study-only panels. No significance-based selection or new hypothesis tests.

Deliverables: numeric snapshots and source hashes; metric/coverage CSVs; methods/results report and candidate caption; 240-mm vector main figure and supporting breakdowns, 600-dpi raster exports, executed notebook, meaningful offline tests, alignment/text/collision QA. Visual style: semantic figure's typography, colors and centered panel titles; muted continuous heatmap colors, persona palette off blue/155 gold/001 green/003 magenta/046 vermilion. No causal/persona-realism claim.

## Implementation and results — 2026-10-01

Extraction and analysis complete: 2,200 original episode slots, 1,958 complete traces and 220 saved disambiguation recovery judgments. The repetition panel retains 100 common questions; failure coverage retains 26 Bix and 40 SciConv questions. Exact sequences, exclusions, source hashes, estimates, pointwise intervals and paired differences are exported under `data/`.

[Results and methods](REPORT.md), [executed notebook](metric_suite.ipynb), [main figure](figures/metric_suite.pdf) and [candidate caption](FIGURE_CAPTION.md) are available. Supporting figures show repetition by benchmark and native outcomes by benchmark/super-family with cell CIs. Budget curves contain the requested incremental coverage information; no separate marginal-gain claim is made.

Overall cross-setting structural repetition is 83.56%, versus 85.18% within off; the paired change is −1.62 percentage points (95% CI −5.14 to 2.19). Fact-recovery means range from 84.70% to 91.70%. Three-episode SciConv failure coverage is 29.44% for the mixture and 20.00% for repeated off; the paired difference is 9.44 points (−1.32 to 21.25). Bix coverage is identical between allocations. These estimates do not establish an overall diversity gain; SciConv event structure primarily reflects interaction length.

Six offline tests cover extraction behavior, pairing, allocation arithmetic, task weighting and reproduction of existing results. Final export QA and notebook execution are recorded in [validation](figures/qa/validation.json). Reproduce validation with `.venv/bin/python Experiment/09_offline_metric_suite/code/validate_outputs.py` after building the notebook. Earlier figures are preserved; no API inference or scheduler job was used.

## Figure revision — 2026-10-01

User requested removal of the native performance panel, recovery violins, and SciConv-only failure coverage for each setting. The current main figure contains A/B/D in one aligned row. The prior four-panel figure, notebook and generating source are preserved in `revisions/v1_four_panel/`.

B now displays 20 case means per setting, a Scott-bandwidth violin restricted to the observed range, and the mean with its existing 95% CI. D now averages all size-m subsets of observed trials within each setting; its 40-question panel is fixed. Off/155/001 support m=1–3; 003/046 support m=1 only. New tables are `data/persona_failure_coverage.csv` and `data/persona_failure_questions.csv`; violin inputs are `data/recovery_case_means.csv`. Original mixture analyses remain supplementary. A seventh test checks available budgets, monotonic coverage, fixed denominators, and exact agreement of the off curve with the previous estimator.

## Current A: within-conversation self-repetition — 2026-10-01

User clarified that repetition concerns a model repeating itself while interacting on a single question, rather than similarity between separate runs. Replaced the structural heatmap with the role-separated extraction in `code/self_repetition.py`. It checks original trace hashes and measures exact normalized 40-character window reuse across later versus earlier same-role messages in each episode. Widths 20/80 provide sensitivity checks. No fresh inference or embeddings. The prior structural version is preserved under `revisions/v2_structural_A/`.

The primary simulator panel has 80 questions shared by all five settings; actor results have 76. Average eligible trials within question, questions within source, then sources equally. One eligible conversation is sufficient; fewer than two length-eligible messages is missing, not zero. Pointwise 95% source-study CIs retain matched questions. Long verbatim reuse is rare (simulator source-balanced means 0.09–0.40%); primary paired simulator differences all include zero. This does not demonstrate reduced semantic loops or mode collapse. Language, legitimate factual repetition, and conversation-length effects remain limitations.

[Self-repetition results and methods](SELF_REPETITION.md) supersede earlier structural-A interpretation. Main A shows means/CIs; [role-separated distributions](figures/self_repetition_roles.pdf) show case dots and source-weighted KDEs. B and D remain unchanged. Numeric per-turn, per-episode, per-question, source/family summary and paired-difference CSVs are saved under `data/self_repetition_*`. Nine tests now include known duplicate/novel sequences, absence of within-message self-counting, Unicode preservation, and role separation.

## Current B: complete-fact recovery — 2026-10-01

User requested updating the figure after discussing ceiling effects. B now uses the existing saved numerator/denominator to define complete recovery (all missing facts recovered), averages the binary outcome across available trials within case, and gives each of 20 cases equal weight. The intent gate is not applied. Means are off 78.33%, 155 85.00%, 001 83.33%, 003 80.00%, 046 75.00%. Study-cluster CIs and same-trial paired contrasts are recomputed. The violin shows discrete case-level proportions, with dots and mean/CI. Full source data: `data/complete_recovery_case_means.csv`; partial recovery remains in the report. The prior figure/notebook/source are under `revisions/v3_partial_recovery/`. A and D are unchanged. This changes the displayed endpoint; no new harder task/protocol or inference was run.

## Both roles in A and existing-data stress subset — 2026-10-01

User clarified that work must use current data and actor repetition belongs in the main display. A now shows simulator means/CIs as filled circles and actor means/CIs as hollow squares. Persona colors and all estimators are unchanged. The role-specific panels contain 80 and 76 common questions respectively; this difference is stated in the legend/caption. The simulator-only figure/notebook are archived under `revisions/v4_simulator_only_A/`.

`code/analyze_long_traces.py` adds an exploratory opportunity-to-repeat sensitivity from the saved numeric episode extraction: require at least three or four eligible same-role messages in every included episode and retain questions common across all settings. This selection uses conversation length, not persona effect or baseline repetition. Length can itself depend on persona, and the source mix changes; it is not a causal estimate or a replacement primary panel. Source-balanced means keep equal weights among represented sources (the three-message panel has just one Bix question alongside SciConv, so interpret that aggregate especially cautiously). Source counts, CIs, 20/40/80-character results and paired contrasts are exported in `data/long_trace_repetition.json` and `data/long_trace_repetition.csv` and shown in the executed notebook.

At four eligible messages, the 40-character simulator panel has 13 SciConv questions: off 0.413%, 155 0.300%, 001 0.024%, 003 0.229%, 046 1.331%. The corresponding actor panel has 10 SciConv questions and zero observed long verbatim reuse for every setting. Thus the current traces do not supply a high-off-repetition stress condition by this definition. Main-panel off means remain simulator 0.103% and actor 0.052%; the 20-character sensitivity gives 2.101% and 1.298% on its own eligible panels. No new inference, task setup or trace content was generated.

## Current A: word-based matching — 2026-10-01

At the user's request, A now uses exact four-word windows instead of 40-character windows, separately for simulator and actor. One-/two-/three-word results are exported; unigrams are labeled vocabulary reuse, not repetition-induced stagnation. The window choice was fixed before extracting these results, but this is an exploratory metric revision after viewing the character results. Previous definitions and figures remain under `revisions/v5_character_matching/` and `data/self_repetition_*`.

`code/word_repetition.py` reuses the role/event selector and within-conversation estimator. Unicode NFKC/casefold is applied; punctuation/whitespace delimit word tokens, with internal apostrophes preserved. Chinese Han spans use jieba 0.42.1 dictionary segmentation with HMM disabled; other scripts use Unicode letter/mark/number runs. Code fences/blockquotes are excluded as before. No stopword removal, stemming, synonym matching, translation or model inference. Tokenizer dependencies are pinned in `code/requirements-word-repetition.txt`; dictionary SHA256 and package versions are recorded. Word boundaries and language-specific segmentation remain limitations.

Four-word common panels contain 81 simulator questions (ASI 7, Bix 27, Discovery 21, EXP 6, SciConv 20) and 80 actor questions (ASI 6, Bix 27, Discovery 21, EXP 6, SciConv 20). Equal source weights and 20,000 study-cluster CIs are retained. Point estimates in off/155/001/003/046 order: simulator 2.032/2.544/2.241/2.141/3.211%; actor 1.628/1.894/1.556/0.865/1.986%. Persona effects are mixed. More overlap under a shorter lexical definition is not evidence of more mode collapse, and comparison with character rates also changes eligibility.

[WORD_REPETITION.md](WORD_REPETITION.md) is the current methods/results page; per-turn, episode, question, source/family summary and contrast CSVs are `data/word_repetition_*`. B and D are unchanged. The executed notebook contains current word results and historical character/long-conversation sensitivities. Eleven offline tests include surrounding edits, exact word order, preserved word boundaries, Hindi/Cyrillic handling and Chinese segmentation.

## Current successful-interaction figure

The active interaction-length analysis is `code/plot_successful_interactions.py`, with caption/methods in `SUCCESSFUL_INTERACTIONS.md` and an executed final section in `metric_suite.ipynb`. Panel A shows 0/1/2+ distributions among successes, off versus equally weighted personas. Panel B shows successful-run mean exchanges on the 29 questions with success under all five settings: 3.10 off versus 2.81 mean persona. Overall success on all 40 SciConv questions is retained in the source summary and caption (85.0% versus 83.75%). No causal efficiency or significance claim is made.

Source tables are consolidated under `data/successful_interactions/`; editable PDF/SVG, PNG and QA files are under `figures/successful_interactions/`. The script reads the frozen snapshot directly. Superseded exact-length, continuation, request-rate, standalone distribution and standalone matched-figure scripts, outputs and notebook sections have been removed at the user's request. The repetition/fact-recovery suite and raw snapshot remain intact. Numerical parity with the prior accepted combined figure was verified before removal.

### Extend shared successes across sources
User confirmed successful matches only. Right panel now includes all 40 shared full-credit questions (ASI 1/Bix 10/SciConv 29); Discovery and EXP unavailable. Equal contributing-benchmark means 2.37 off/2.27 mean persona. Left panel remains SciConv successful distribution. Both available-case and full-credit coverage tables retained for audit; only full-credit pairs plotted. Notebook and caption updated and rendered checks passed.

### Align Panel A with Panel B matched set
Both panels now use the same 40 shared full-credit questions and equal benchmark/question/persona weights. Panel A bins count protocol interactions, including initial required handoffs outside SciConv. New bar source tables prefixed `matched_distribution`; prior SciConv-only tables remain supporting data. Notebook/caption updated; key equality, bin arithmetic and rendered QA verified.

Expanded the matched Panel A distribution to 0/1/2/3+ on the same 40 questions, with no weighting changes. Notebook/exports/caption refreshed and checked.

### SciConv-only figure with bar uncertainty
Both panels restricted to the 29 shared-success SciConv questions. Panel A retains 0/1/2/3+ bins and adds pointwise 95% percentile CIs from 20,000 joint whole-question bootstrap draws (seed 20261005). Panel B remains paired successful means 3.10/2.81, no CI. Bootstrap endpoints independently reproduced; notebook/caption/exports updated. Other benchmark raw data retained but excluded from figure.

### M(t) changing-denominator preview
Added completed-by-t mean native score for the same 1,958 all-benchmark episodes as original Panel C, retaining five separate settings and pooled-episode weights. Both numerator and denominator count only completed episodes. Figure, full count table, per-benchmark composition and caption saved; notebook preview executed. Original figures unchanged. See `MT_PREVIEW.md`.

### Split existing main figure
A–B exported together and original cumulative C exported separately under `figures/metric_suite_split/`. C y-label changed to requested “Avg Score before t”; fixed all-run denominator unchanged and defined in caption. Main notebook figure cell executed; all 65 C estimates verified unchanged.

Removed the “C Performance” title from the standalone score figure; axis labels and estimates unchanged. Notebook and exports refreshed.

Standalone score figure made square with larger labels, tick text and legend; estimates unchanged. Notebook and vector/raster exports refreshed.
