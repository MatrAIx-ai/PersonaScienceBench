# PersonaScienceBench

Scientific agents collaborating with diverse simulated researchers. PersonaScienceBench evaluates **scientific effectiveness, information acquisition, interaction behavior, and resource use** under different researcher personas. Model-level benchmark results come first; performance, semantic, and behavioral analyses then explain how collaborator personas shape the interaction. Personas condition the researcher simulator, while the scientific actor encounters their effects through conversation.

## Main experiment

For agents evaluating another model, use the [run-to-table handoff](docs/TEAM_HANDOFF.md#new-model-campaign--paper-main-table-updated-2026-10-10): exact commands, model-role configuration, and the required tracked export to `results/<model-slug>/trial-<N>/`. The running agent commits and pushes the complete traces/submissions; our team handles final grading and table computation.

Run the same frozen **200 questions** under **five simulator settings**. Persona profiles are injected into the simulator; the actor and judge use the shared configuration.

| Run setting | Configuration |
|---|---|
| Simulator personas | Persona off, 155, 001, 003, 046 |
| Questions | 40 each from ASI-Bench, BixBench, DiscoveryBench, EXP-Bench, and SciConvBench |
| Models | GPT-6 Astra, reasoning effort `low`, for actor, simulator, and judge |
| Episodes | 1,000 per trial; 3,000 for three fresh trials |
| SLURM resources | 30 CPUs, 30 workers, 128 GB RAM per job |
| Frozen inputs | [Question selection](configs/main_run/selection.csv), [persona prompts](configs/main_run/personas/), and [portable preparation bundle](configs/main_run/frozen/astra-20260929-v1/README.md) |

These settings describe the fresh-run configuration. Historical runs have different coverage and protocol versions. The current SciConv protocol applies to new runs. See the [complete run guide](docs/MAIN_RUN.md) for shared controls and provenance.

Existing delivered campaigns are indexed in [results/README.md](results/README.md), with explicit completeness labels and per-file checksum manifests. Active raw runs remain local under `runs/`.

## Primary benchmark scorecard

The main results table has **one row per evaluated actor model**, using the same frozen task/persona panel and documented interaction settings. Persona off is a separate reference; persona means average **155 / 001 / 003 / 046** equally.

| Column | What it reports |
|---|---|
| **Persona-off performance** | Native scientific score with no injected simulator persona. |
| **Mean Persona Performance** | Native scientific score averaged across the four injected personas and source benchmarks. |
| **Fact recovery (%)** | Fraction of required withheld facts recovered across eligible SciConv disambiguation runs, without conditioning on success or failure. |
| **Self-repetition (%)** | Actor reuse of earlier messages, measured with the selected six-word / three-matching-position definition. |

Use equal question weights within each benchmark and equal benchmark weights, averaging available repeats within question first. Report 95% confidence intervals and metric-specific coverage. Actor output tokens and tool calls are retained in supporting resource tables, using absolute units; they are not main-table columns. Fewer tokens or tool calls alone do not establish better adaptation. The metrics remain separate rather than being combined into one adaptation score.

The [Experiment 02 notebook](Experiment/02_performance_and_fields/performance_analysis.ipynb) produces the [saved scorecard](Experiment/02_performance_and_fields/data/model_scorecard/model_scorecard.md), [CSV](Experiment/02_performance_and_fields/data/model_scorecard/model_scorecard.csv), and [LaTeX table](Experiment/02_performance_and_fields/data/model_scorecard/model_scorecard.tex). The saved scorecard includes historical Astra low (101 common questions for performance, 20 for fact recovery, 79 for repetition) and Haiku–Haiku (200 questions for performance; behavioral means/CIs are collaborator-reported pending complete trace delivery). Each model uses its own available common-five-setting panel. These counts are analysis coverage, not a replacement for the 200-question benchmark inventory. Additional-model evaluation is being expanded; completed results will populate the same scorecard after coverage and protocol compatibility are checked.

## Three levels of explanatory analysis

The same scientific questions are evaluated across researcher settings, with persona off as a reference. These analyses explain the model-level results rather than define three separate leaderboard scores.

| Level | Research question | Measurements |
|---|---|---|
| **Performance** | How do scientific outcomes vary across researcher personas? | Persona-specific native scores and matched differences. Benchmark and super-family breakdowns are supporting analyses. |
| **Semantic diversity** | Do personas change generated content and conversation paths? | Role-separated embedding distances and question-specific trajectory illustrations. |
| **Behavioral diversity** | How does the collaboration change? | Recorded token and tool use, review/revision behavior, clarification, actor repetition, and fact recovery. |

These measurements characterize adaptation-related outcomes and persona-associated variation. Semantic separation is not a quality score; behavioral change alone does not establish successful fulfillment of a researcher's needs. Diversity motivates broader collaborator coverage, without claiming measured human realism.

## Paper structure and discussion cases

The paper follows **benchmark construction → evaluation metrics and setup → model-level results → explanatory analyses → discussion**:

1. **Introduction and related work:** motivate scientific collaboration and the need to evaluate agents across different researchers.
2. **PersonaScienceBench:** define persona construction, task conversion, role visibility, the 200-question mixture, interaction protocols, and the metric contract.
3. **Experimental setup and main results:** specify the actor/simulator/judge configuration and controls, then report the model-level scorecard.
4. **Performance, semantic, and behavioral analyses:** explain persona-dependent outcomes and interaction differences; keep detailed benchmark/domain tables and sensitivity analyses as supporting material.
5. **Discussion with conversation snippets:** use selected, trace-linked excerpts to explain **why evaluating scientific agents with persona-conditioned collaborators matters**. Show the researcher's request or response, the actor's subsequent action, and the observed scientific consequence where available. Cases can illustrate clarification, disclosure, approval, revision, or persistent misunderstanding; their inclusion depends on the recorded evidence.
6. **Limitations, conclusion, and appendix:** state what simulated collaborators and the measured outcomes establish, and provide implementation details, coverage, full comparisons, and extended traces.

Discussion snippets should compare the same question across persona settings where possible, identify the benchmark, question, persona and trial, and link to the full conversation. Include helpful, unproductive, and mixed interactions when supported. Their purpose is to make the quantitative findings concrete and motivate collaborator diversity in scientific-agent evaluation; selected cases do not establish prevalence, causal mechanisms, a universal performance benefit from personas, or human realism. Relevant examples can also appear beside the Results they illustrate, with Discussion drawing the broader argument.

See the [paper structure review](paper/STRUCTURE.md) and [paper workspace](paper/README.md). This describes the intended manuscript organization; the current LaTeX draft still contains placeholders and older displays awaiting integration.

## From saved runs to final figures

All three levels start from the frozen question selection, saved native evaluations, and recorded interactions. Join records by **benchmark, question, persona, and trial**; retain scientific super-family and source-study identifiers for grouping and uncertainty estimates. Keep original and repaired endpoints distinguishable. The selected display panel is **off / 155 / 001 / 003 / 046**. Historical coverage is three original trials for off/155/001 and one for 003/046; the fresh three-trial run above is a separate collection target.

### 1. Primary scorecard and supporting performance comparisons

- **Extract:** the primary scorecard uses saved original native scores, complete traces, and recorded API usage. Scientific missing submissions follow the native zero-score rules; infrastructure/evaluation failures remain missing. Keep original and repaired endpoints distinguishable; repairs are not additional trials.
- **Aggregate:** for each metric, retain questions with observations under all five settings. Average available trials within question, questions within source, sources equally, and the four injected personas equally. Keep persona off separate. Bootstrap whole studies within source, retaining the settings together, for pointwise 95% CIs. Existing trial counts and evaluator versions vary and are disclosed.
- **Display:** save one model row in the primary table, with the definitions and coverage above. Actor output is episode-total k tokens and tool use is actions per episode; no baseline normalization is applied.
- **Supporting analysis:** retain available-endpoint persona comparisons, benchmark/super-family breakdowns and difference heatmaps in the [previous executed notebook](Experiment/02_performance_and_fields/supporting/performance_analysis_before_scorecard.ipynb). That analysis may prefer evaluable repairs with original fallback and uses matched question/trial contrasts with evaluator-compatibility filters. Its different inclusion rules mean those values need not reproduce the original-only primary scorecard.

Working notebook: [performance_analysis.ipynb](Experiment/02_performance_and_fields/performance_analysis.ipynb). [Definitions and limitations](Experiment/02_performance_and_fields/MODEL_SCORECARD.md) distinguish the metric-specific panels. Native scores retain different meanings across sources; source/domain breakdowns provide supporting context.

### 2. Semantic diversity: final messages → embeddings → separation heatmaps and trajectories

- **Extract and embed:** use the final simulator message and final actor response from original trial 1, keeping roles separate. The current complete five-setting intersection has **97 questions**. Exclude system prompts, injected persona text, and repeated history. Encode generated messages offline with the fixed **Qwen3-Embedding-0.6B** model, L2-normalize, and calculate cosine distances before projection.
- **Compare:** within each super-family, calculate cross-persona distance minus the average within-persona distance, using **different-question pairs** in both terms; give the four families equal weight. Question-wise persona-label swaps provide permutation tests, with Holm correction across 20 role/pair comparisons. Question bootstraps within benchmark × family provide CIs. This controls family composition; it does not estimate same-question rollout variability or eliminate question-level variation.
- **Display:** lower-triangle, role-separated 5 × 5 separation heatmaps alongside local UMAP trajectories for the selected BixBench `bix-57-q1` and SciConvBench `matToolUse/disambiguation/case_236` examples. Each question/role projection is fitted jointly across the five settings. Curved connectors are visual guides between observed messages; the manually selected cases illustrate interactions and are not independent quantitative evidence.

Working notebook: `Experiment/01_behavioral_diversity/semantic_trajectory_analysis.ipynb`. Detailed methods and the candidate caption are maintained in `SEMANTIC_FIGURE_CAPTION.md` in the same folder. Semantic distance describes generated content and may include language/style effects; it is not a quality or realism score.

### 3. Behavioral diversity: saved events and API usage → interaction metrics → pairwise profiles

- **Extract:** use complete original traces and actual recorded API output-token counts, including reasoning. Simulator tokens are measured per noninitial decision/reply; actor tokens are measured per completed interaction, including intervening tool generation. SciConv actor counts use clarification-question calls. Also extract revision requests from result-review decisions and clarification recall from saved native SciConv evaluations. No new LLM judge or estimated character-to-token conversion is used.
- **Compare and display:** match question and original trial, average paired differences within question, and weight represented benchmarks equally. Four 5 × 5 heatmaps show simulator tokens, actor tokens, revision requests, and clarification recall. Cells are **row minus column**; colors show raw differences, not significance. Pointwise 95% study-cluster bootstrap CIs and pair-specific coverage accompany the figure.
- **Complementary behavior panels:** actor self-repetition measures overlap with earlier actor messages in the same conversation (at least three corresponding word matches in six-word windows; the current common panel has 79 questions). The setting was selected in an exploratory window grid. Complete-fact-recovery bars use SciConv disambiguation episodes ending in native failure, average within case and then across eligible cases, and show no CIs. Eligibility can differ by persona; these are conditional descriptive summaries.

The behavioral notebook also includes a five-setting tool-call difference heatmap. Its per-interaction token summaries differ from the primary table's whole-episode token totals. Experiment 09's failure-conditioned complete-fact recovery is a separate diagnostic from the primary scorecard's unconditional fraction of facts recovered; do not interchange their denominators or labels.

Working notebooks: `Experiment/01_behavioral_diversity/behavioral_analysis.ipynb` and `Experiment/09_offline_metric_suite/metric_suite.ipynb`. Token use, revisions, clarification, repetition, and recovery describe different behaviors; they are not combined into a single universally desirable score.

The notebooks retain extraction/aggregation code, coverage tables, figure code, and embedded outputs. Current notebook figures supersede older exported report/figure snapshots where labeled. These notebook paths identify the local analysis workspaces; the setup/trace release does not yet include the newer analysis notebooks and derived results. All analyses reuse saved runs; local embedding extraction does not generate new scientific interactions. Persona and display choices are exploratory, and diversity alone does not establish human realism.

## Recorded interaction traces

Browse [Astra trial-1 conversations](results/astra-actor-astra-simulator-astra-judge/trial-1/README.md) for **off / 155 / 001 / 003 / 046**. The index accounts for all 200 questions per setting and links available shared conversations. Repaired endpoints are labeled; completed zero-scoring outcomes are retained. Sol and infrastructure-only slots are excluded from transcript publication. These are historical interactions with recorded protocol provenance, not new runs of the current launcher.

## Quick start

### Install and prepare

Requires Linux, Python 3.12+, `uv`, and Bubblewrap (`bwrap`).

```bash
git clone --single-branch --branch main https://github.com/MatrAIx-ai/PersonaScienceBench.git
cd PersonaScienceBench
bash scripts/setup_main.sh
cp .env.example .env
# Set OPENAI_API_KEY in .env.
python scripts/check_main.py
```

Setup installs dependencies and downloads source/data assets without LLM inference. Downloaded assets and environments remain local. Analysis notebooks and paper files are not needed to run the experiment.

### Run a trial

Run locally:

```bash
.venv/bin/python scripts/run_main.py --run-dir runs/main/trial-1 --workers 30
```

Or submit to SLURM, supplying your cluster account and partition:

```bash
export ACCOUNT=your_account PARTITION=your_partition
bash scripts/submit_main.sh 1
```

To submit three sequential trials:

```bash
j1=$(bash scripts/submit_main.sh 1)
j2=$(DEPENDENCY=afterok:${j1%%;*} bash scripts/submit_main.sh 2)
DEPENDENCY=afterok:${j2%%;*} bash scripts/submit_main.sh 3
```

Choose either the single-trial submission or the three-trial sequence. Run commands make paid API calls. Each independent trial needs a separate run directory; rerunning the same directory resumes that trial. Preserve the EXP extraction cache across trials to keep prepared inputs fixed. A failed job blocks its dependent jobs until repaired and dependencies updated.

Results and traces are written to `runs/main/trial-N/`. See the [run guide](docs/MAIN_RUN.md#monitor-resume-and-deliver-results) for monitoring, repair flags, and result delivery. Run artifacts and API credentials are excluded from Git.

## Benchmarks in the main run

| Benchmark | Selected questions | Source scientific coverage | Native evaluation |
|---|---:|---|---|
| DiscoveryBench | 40 | Biology, humanities, sociology, economics, engineering, meta-science | Discovery scoring |
| BixBench | 40 | Computational biology | Open-answer grading with executed-analysis submission |
| EXP-Bench | 40 | ML and scientific experiment design | Design coverage and integrity gate; design only |
| ASI-Bench | 40 | Scientific computing across disciplines | Local gates and weighted scores |
| SciConvBench | 40 | Fluids, PDEs, materials, solid mechanics | Clarification and specification metrics |
| **Total** | **200** | | |

The main run uses **200 unique questions**, with **40 from each benchmark**, fixed in the [selection file](configs/main_run/selection.csv). Every question is evaluated under all five settings: **1,000 episodes per trial**, or **3,000 episodes across three trials**. The broader converted source pools are documented separately in the [conversion inventory](reports/conversion_v2/conversion_summary.md).

Conversion is automated per benchmark. Preserve the scientific question, inputs, deliverables and native grading; separate public context from simulator context and evaluator references; record exclusions and source provenance. Execution/design tasks use approach and result reviews, while SciConv retains native clarification. See the [conversion rules](docs/design/conversion_revision_v2.md) and [benchmark standards](docs/benchmark_standards.md).

## Setup and navigation

Follow the [Linux setup and migration guide](docs/reproducibility.md). The [persona guide](docs/personas.md) explains the full-profile injection used in the completed study; the [interaction protocol](docs/interaction_protocol.md) explains the shared review workflow.

| Location | Purpose |
|---|---|
| `reports/full_persona_v2/` | Preserved experiment results, profiles, trace indexes, full traces and case studies |
| `configs/full_persona_v2/` | Frozen cohort, task selection and model/protocol settings |
| `docs/MAIN_RUN.md` | Selected five-setting campaign: setup, run, resume, and result delivery |
| `docs/REPOSITORY_AUDIT.md` | Coherence fixes, offline validation, and remaining reproduction limits |
| `docs/design/benchmark_paper_plan.md` | Broader paper and experiment planning |
| `docs/persona_controls.md` | Noise-measuring arms: repeated persona-off, reordered profiles, neutral identities, mute and oracle researchers |
| `src/`, `scripts/`, `tests/` | Runners, conversion/analysis tools and offline checks |
| `manifests/` | Pinned upstream sources and checksums |
| `data/`, `external/`, `prepared/`, `runs/` | Ignored local inputs and runtime artifacts; transfer or regenerate explicitly |

## Historical pilot

<details>
<summary>Earlier 30-persona pilot: setup and recorded results</summary>

The completed experiment contains **30 full personas plus persona off, two questions from each of five benchmarks, and 310 recorded episodes**. Actor, simulator and judge used GPT-6 Luna with reasoning effort `none`. Full profiles enter only the simulator system prompt; both conditions allow general knowledge, while evaluator references remain private.

The [results report](reports/full_persona_v2/README.md) preserves all scores, persona indexes, exact injected profiles, and **310 full Markdown traces**, including failed and missing-submission episodes. [Frozen experiment metadata](reports/full_persona_v2/experiment.json) and [configuration snapshots](configs/full_persona_v2) accompany them. Raw JSON logs and execution artifacts remain local; see the handoff for transfer instructions.

<!-- FULL_PERSONA_RESULTS_START -->

## Historical pilot persona results

Final results: **310/310 episodes finished**. [Benchmark results, all 30 profiles, and interaction traces](reports/full_persona_v2/README.md).

Top deviations below use the same **8 completed questions** for every persona; questions with infrastructure or evaluator errors are excluded for every persona. Differences are normalized score percentage points.

**Shared baseline: 26.01%.** All personas are compared on the same 8 questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.

| Rank | Persona | Score | Change vs off | Traces |
|---:|---|---:|---:|---|
| 1 | [046](reports/full_persona_v2/profiles/candidate_046.md) | 4.54% | **-21.47 pp** | [Read](reports/full_persona_v2/traces/candidate_046.md) |
| 2 | [003](reports/full_persona_v2/profiles/candidate_003.md) | 6.14% | **-19.87 pp** | [Read](reports/full_persona_v2/traces/candidate_003.md) |
| 3 | [004](reports/full_persona_v2/profiles/candidate_004.md) | 9.33% | **-16.68 pp** | [Read](reports/full_persona_v2/traces/candidate_004.md) |
| 4 | [089](reports/full_persona_v2/profiles/candidate_089.md) | 9.79% | **-16.22 pp** | [Read](reports/full_persona_v2/traces/candidate_089.md) |
| 5 | [001](reports/full_persona_v2/profiles/candidate_001.md) | 9.91% | **-16.10 pp** | [Read](reports/full_persona_v2/traces/candidate_001.md) |
| 6 | [127](reports/full_persona_v2/profiles/candidate_127.md) | 10.51% | **-15.50 pp** | [Read](reports/full_persona_v2/traces/candidate_127.md) |
| 7 | [262](reports/full_persona_v2/profiles/candidate_262.md) | 11.33% | **-14.68 pp** | [Read](reports/full_persona_v2/traces/candidate_262.md) |
| 8 | [224](reports/full_persona_v2/profiles/candidate_224.md) | 12.20% | **-13.81 pp** | [Read](reports/full_persona_v2/traces/candidate_224.md) |
| 9 | [148](reports/full_persona_v2/profiles/candidate_148.md) | 39.37% | **+13.36 pp** | [Read](reports/full_persona_v2/traces/candidate_148.md) |
| 10 | [026](reports/full_persona_v2/profiles/candidate_026.md) | 12.66% | **-13.35 pp** | [Read](reports/full_persona_v2/traces/candidate_026.md) |

**Behavior on the same questions**

Each cell shows **persona on / baseline**. Rows follow the performance ranking.

| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |
|---|---:|---:|---:|
| [046](reports/full_persona_v2/profiles/candidate_046.md) | 2.38 / 3.38 | 70.76 / 65.99 | 0.17 / 0.33 |
| [003](reports/full_persona_v2/profiles/candidate_003.md) | 3.88 / 3.38 | 66.73 / 65.99 | 0.00 / 0.33 |
| [004](reports/full_persona_v2/profiles/candidate_004.md) | 3.88 / 3.38 | 69.05 / 65.99 | 0.00 / 0.33 |
| [089](reports/full_persona_v2/profiles/candidate_089.md) | 4.25 / 3.38 | 69.53 / 65.99 | 0.00 / 0.33 |
| [001](reports/full_persona_v2/profiles/candidate_001.md) | 4.25 / 3.38 | 70.60 / 65.99 | 0.00 / 0.33 |
| [127](reports/full_persona_v2/profiles/candidate_127.md) | 4.50 / 3.38 | 70.49 / 65.99 | 0.50 / 0.33 |
| [262](reports/full_persona_v2/profiles/candidate_262.md) | 2.25 / 3.38 | 68.95 / 65.99 | 0.00 / 0.33 |
| [224](reports/full_persona_v2/profiles/candidate_224.md) | 4.38 / 3.38 | 65.12 / 65.99 | 0.00 / 0.33 |
| [148](reports/full_persona_v2/profiles/candidate_148.md) | 3.88 / 3.38 | 72.61 / 65.99 | 0.00 / 0.33 |
| [026](reports/full_persona_v2/profiles/candidate_026.md) | 3.50 / 3.38 | 74.09 / 65.99 | 0.33 / 0.33 |

Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.


<!-- FULL_PERSONA_RESULTS_END -->

</details>
