# Paper structure review — 2026-10-02

This review maps the current LaTeX manuscript to the agreed model-level scorecard and existing experiments. It preserves the current manuscript prose and assets; it does not claim that proposed multi-model results are complete. Literature claims and citations were not independently re-verified in this structural review.

## Central argument

PersonaScienceBench evaluates scientific agents interacting with diverse simulated researchers. It measures scientific effectiveness, information acquisition, conversational redundancy and resource use, then examines how researcher personas change scientific outcomes and semantic and behavioral patterns.

Researcher adaptation is the broad evaluation objective. The metrics are complementary indicators, not a validated scalar adaptation score or a direct test of preference fulfillment. Differences in behavior alone do not establish better adaptation. Human realism is outside the measured scope.

## Recommended section order

| Section | Reader's question | Content and evidence | Current manuscript state |
|---|---|---|---|
| Abstract | What is the benchmark and what does it establish? | Motivation → task/persona construction → model scorecard → strongest verified cross-model findings → bounded implication. Insert numerical findings after the final comparison cohort is fixed. | Placeholder; draft last. |
| 1. Introduction | Why evaluate scientific agents with different collaborators? | Scientific work requires interaction; collaborator variation is an evaluation condition; introduce benchmark and scorecard; explain subsequent diversity analyses; state contributions. | Substantial prose; measurement framing and several evidence claims need updating. |
| 2. Related Work | What gap remains after existing scientific and interactive benchmarks? | Scientific-agent evaluation; interactive/user-simulation benchmarks; persona conditioning and adaptation evaluation. Keep the gap precise and source supported. | Prose exists; currently overstates repeat-based identification for the selected panel. |
| 3. PersonaScienceBench | What reusable benchmark are we releasing? | 3.1 Persona construction and selection; 3.2 task conversion, dataset mixture and interaction protocol; 3.3 evaluation metrics and aggregation. | Persona construction pending; conversion section drafted; metric contract absent. |
| 4. Experimental Setup | What exactly is compared? | Actor models and reasoning settings; fixed simulator/judge roles for controlled comparisons; tools and budgets; off control; question/setting/trial coverage; original versus repaired outcomes; evaluator versions; statistical units. | Placeholder. Distinguish historical Astra evidence from the forthcoming standardized model comparison. |
| 5. Results | What does the benchmark reveal? | Lead with the model scorecard. Follow with persona-dependent performance, semantic variation and behavioral variation. | Old by-benchmark/domain table and two figures exist, but interpretation is mostly missing. |
| 6. Discussion | What do the observations mean for scientific collaboration? | Explain capability, information acquisition and interaction tradeoffs; connect variations to collaborator conditions; distinguish responsiveness from successful requirement fulfillment. | Placeholder, currently combined with case studies. Put case evidence near the corresponding result instead. |
| 7. Limitations and Responsible Use | Where do the conclusions stop? | Synthetic collaborators; exploratory selection; uneven repetitions/missingness; evaluator changes; restricted recovery applicability; language sensitivity; resource comparability; no human-realism validation. | Placeholder. |
| 8. Conclusion | What reusable contribution remains? | Brief benchmark contribution and verified empirical takeaway. No new findings. | Placeholder. |
| Appendix | How can readers reproduce and inspect it? | Five source adapters; prompts/visibility; persona cards and selection; metric formulas and bootstrap; run coverage/version matrices; source/domain breakdowns; sensitivity analyses; full examples. | Currently only the five adapter placeholders. Expand beyond implementation alone. |

## Section 3.3: metric contract

The main model table has exactly these columns:

| Actor model | Persona-off performance | Mean Persona Performance | Fact recovery (%) | Self-repetition (%) | Actor output (k tokens/episode) | Tool calls/episode |
|---|---|---|---|---|---|---|
| One row per evaluated actor model | Reference condition | Equal mean over 155/001/003/046 | SciConv disambiguation subset | Actor 6-word/3-position measure | Recorded whole-episode output including reasoning, divided by 1,000 | Execution/inspection actions on four applicable benchmarks |

Do not reintroduce worst-persona performance or baseline-normalized resource ratios into the main table. Keep off separate from the four-persona average. State that token/tool counts are absolute resource-use measurements and do not independently measure adaptation quality. Show confidence intervals and metric-specific coverage. Persona-off resource comparisons remain supplementary.

Current source: [executed Experiment 02 notebook](../Experiment/02_performance_and_fields/performance_analysis.ipynb); [saved table](../Experiment/02_performance_and_fields/data/model_scorecard/model_scorecard.md); [definitions](../Experiment/02_performance_and_fields/MODEL_SCORECARD.md). The retrospective Astra performance row uses 101 common questions, not all 200 selected questions. Fact recovery uses 20 cases; repetition 79 common questions; tool use 61. These are distinct panels, not one universal denominator.

## Section 5: evidence sequence

### 5.1 Model-level scientific collaboration results

**Role:** primary benchmark result. Present the table above first, one row per actor model under an explicitly stated evaluation configuration. Discuss performance and resource use together; show whether stronger scientific outcomes coexist with information acquisition or lower redundancy. Do not label low cost after early failure as efficient collaboration. Only the Astra retrospective row is currently populated; keep other findings pending rather than manufacturing a leaderboard.

**Artifact:** Experiment 02 model_scorecard.{csv,md,tex}. Its raw LaTeX table will need manuscript-width formatting when integrated; the export is not yet the table imported by main.tex.

### 5.2 Performance variation across researcher personas

**Role:** explain what the persona average hides. Use setting-level effects relative to off and, once available, model-by-persona results. Discuss supported heterogeneity rather than assuming a rank reversal or uniform degradation. Full benchmark and super-family heatmaps are supporting analysis; promote a specific breakdown only if it changes the central conclusion.

**Artifacts:** Experiment 02 preserved supporting notebook and pairwise data. The existing paper/tables/performance_panel.tex uses available-case persona/source means and unweighted displayed group averages. It is not numerically interchangeable with the new common-question, source-balanced model scorecard.

### 5.3 Semantic variation in scientific interactions

**Role:** establish differences in generated content under persona settings and illustrate interaction paths. Use the current role-separated heatmaps and two UMAP examples. Explain that domain-balanced distinct-question distances differ from a question-controlled repeated-rollout statistic. Language and style can contribute. The manually selected cases illustrate the quantitative result; they are not independent statistical evidence.

**Artifact:** Experiment 01 semantic_trajectory_analysis.ipynb and SEMANTIC_FIGURE_CAPTION.md; manuscript figures/semantic.pdf. The current panel has 97 common trial-1 questions, and does not estimate within-persona rollout variability.

### 5.4 Behavioral variation and information acquisition

**Role:** explain operational differences in collaboration. Use actor repetition, observed reviews/clarification, tool use, and task-grounded fact recovery. Select a compact set of contrasts that adds information beyond the scorecard; do not repeat every diagnostic as a main figure.

**Artifacts:** Experiment 01 behavioral_analysis.ipynb (including the tool-use heatmap), Experiment 08 fact-recovery analysis, and Experiment 09 metric_suite.ipynb.

Important distinction: the scorecard's fact recovery is the fraction of required facts recovered across all eligible cases. Experiment 09 panel B is complete-fact recovery conditional on native failure, with different failure subsets per persona. Keep the latter as a separately labeled diagnostic or supplement; it cannot stand in for the main metric.

Experiment 09 panel C is a cumulative final-score contribution by observed completion length across heterogeneous protocols. It is not a within-run improvement curve. Place it in supporting material unless completion timing is a central question, and retain its conditional-denominator explanation.

## Display allocation

| Display | Placement and purpose |
|---|---|
| Task-mixture table and conversion algorithm | Benchmark construction; retain the existing 200-task inventory and source/domain counts. |
| Model scorecard | First main Results display; replace the old persona/source table in the lead position. |
| Semantic heatmap + trajectories | Main explanatory figure; keep simulator and actor roles separate. |
| Compact behavioral figure | Main explanatory evidence; select nonredundant repetition/information/tool-use findings after model comparisons are available. |
| Persona × benchmark/super-family tables and heatmaps | Supporting analysis, with a concise main-text finding only where warranted. |
| Full pairwise CI tables, alternative tests, grid search, coverage/version details | Appendix/source data; exploratory selection and conclusion-changing limitations must still be acknowledged in main text. |
| Full transcripts | Appendix or trace release, with the selected example alongside its relevant Results subsection. |

## Immediate consistency changes needed in the manuscript

1. **Results table:** results.tex still imports tables/performance_panel.tex. It needs the new scorecard in the leading position; preserve the existing table as supplementary rather than relabeling its values.
2. **Introduction measurement paragraph:** replace the old unstructured list of review rounds, message lengths and language adaptation with the agreed primary scorecard, then introduce diversity analyses as explanations.
3. **Repeated-rollout claim:** the Introduction says every task–condition cell is repeated, and Related Work says repeats distinguish profile diversity from run variation. This does not describe the current five-setting panel: 003/046 have one original trial. Scope repeat-based statements to cohorts with repeats.
4. **Attribution claim:** matching tasks does not by itself make all observed differences solely attributable to persona. Unequal valid coverage, historical evaluator changes and stochastic outputs remain relevant; separate the controlled design from what the retrospective evidence identifies.
5. **Protocol wording:** four sources share approach/result review; SciConv uses its native clarification protocol. Avoid describing all five as one identical review procedure.
6. **Adaptation claim:** task effectiveness, fact recovery and resource/behavior metrics characterize adaptation-related outcomes. They do not directly measure satisfaction of expressed researcher requirements or human realism.
7. **Methods versus findings:** the 200-question selection is a benchmark property; 101/97/79/61-question common panels are analysis coverage. Keep those quantities distinct throughout.
8. **Caption versus methods:** avoid putting the only metric definition or exclusion rule in a long Results caption. Define the contract before Results, then use captions for panel-specific interpretation.

## Canonical terminology

- **Actor:** scientific agent under evaluation.
- **Researcher simulator:** persona-conditioned collaborator; the persona is not injected into the actor.
- **Persona-off:** same interaction protocol without the injected persona profile.
- **Mean Persona Performance:** equal mean over the four injected settings; off excluded.
- **Actor output:** whole-episode completion tokens, including reasoning; k tokens = tokens/1,000.
- **Tool calls:** recorded execution/inspection actions, not conversational handoffs or subcommands.
- **Fact recovery:** distinguish fraction recovered (main metric) from all-facts completion conditional on failure (diagnostic).
- **Diversity:** measured semantic/behavioral variation; not equivalent to realism or successful preference adaptation.

## Suggested writing order

Write metric definitions and experimental setup first, then integrate the scorecard and write Results around verified estimates. Update the Introduction/contributions to match those results. Write Discussion, limitations, conclusion and finally the abstract. Keep persona-construction ownership unchanged. No new inference or extra study is needed merely to align the structure; incoming model results can fill the fixed primary table when ready.
