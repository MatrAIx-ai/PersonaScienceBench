# Behavioral diversity

> Current-version note (2026-10-01): The current five-setting behavioral notebook and semantic methods supersede older all-persona/PCA descriptions below. See [workspace overview](../README.md), `behavioral_analysis.ipynb`, and [semantic caption](SEMANTIC_FIGURE_CAPTION.md).

## Question

Does persona conditioning broaden semantic and behavioral coverage beyond repeat variation, and which collaboration patterns change?

## Design and shared setting

Use the [integrated paper plan](../../docs/design/benchmark_paper_plan.md#current-integrated-scope-and-claim-2026-09-30), frozen source manifests and exact injected profiles. The primary panel is 200 frozen tasks (40 per source), off/148/155/089/001/127, three original Astra-low trials, with incomplete valid coverage reported explicitly. The [shared setting](../shared/setting.json) retains the initial three-condition configuration as provenance. Personas 003/004/046 have one trial and cannot support within-persona repeatability estimates. Sol and the new SciConv protocol are separate settings. No human realism evaluation is planned.

## Status

The requested offline behavioral analysis is implemented in [BEHAVIOR_REPORT.md](BEHAVIOR_REPORT.md) and [behavioral_analysis.ipynb](behavioral_analysis.ipynb): 21 automatic/native metrics, paired differences, repeat variation, script/length sensitivity, and lexical opening repetition. It analyzes 3,382 complete original episodes and explicitly excludes 218 incomplete/missing-log slots. The user has now authorized the trial-1 semantic figure described below; repeat-adjusted semantic separation remains unavailable in that one-trial panel. Content-level feedback/volunteering annotation remains outside this automatic analysis.

See [status.json](status.json) and the [shared run status](../shared/run_status.json) for timestamped collection snapshots. Snapshot counts are not live scheduler state. `finished` can include missing submissions; it does not mean scientifically correct or scored.

## Planned work

- [x] Count additional plan reviews, result-revision requests, collaboration exchanges, and budget exhaustion separately from required reviews.
- [x] Analyze SciConv clarification recall/precision, grounding, memory, and questions after the first researcher reply.
- [x] Extract visible-message characters and Unicode script by role; separate them from API token usage. Script agreement is explicitly not full language identification.
- [x] Build role-separated, question-controlled semantic trajectories with a frozen multilingual encoder. The requested trial-1 figure reports raw distances; comparison against repeat variation remains prospective.
- [ ] Compare stage/task/role-matched semantic distances within off, within each persona and between personas with the same estimator and task-balanced weighting. Treat pairwise repeat combinations as dependent.
- [x] Add exploratory exact repeated-question and 40-character opening-collision diagnostics; optional extra-review patterns are hashed in the snapshot. Initial requests and protocol schema are excluded, with task/script matching and fixed prefix length. No semantic-collapse inference is made.
- [x] Assemble behavioral heatmap, all-task reply-length distributions and within/between-persona variation, with original-unit tables, denominators, source-study-aware CIs and an executed Jupyter notebook.
- [x] Figure 3: trial-1 persona-pair heatmaps and question-controlled paths, with equal super-family weighting.

## Relationship to the other experiments

Experiment 01 supplies the core diversity evidence. Experiment 02 reports consequences using native scores and field/source summaries; 04 links profile wording to recorded simulator/actor behavior; 08 is a standalone SciConv fact-recovery experiment with its own quantitative figure and table. Recovery must not be relabeled as observed disclosure. Experiment 03 is a conditional joint-model extension and static reference (05) is optional. This analysis does not depend on a new human study, full per-fact annotation, or new inference.

## Implementation

- `code/analyze_behavior.py` extracts and analyzes saved original event logs; `code/plot_behavior.py` creates three figures. Numeric/hashed snapshots and CSVs live in `data/behavior/`; private transcript text is not exported.
- Shared study-cluster aggregation is in `../shared/analysis_utils.py`. `../shared/build_analysis_notebooks.py` executes real local Jupyter kernels and saves outputs. The separate `code/semantic/` pipeline now implements the requested local embeddings and Figure 3.
- Current summary fields can also be exported with `code/extract_summary_metrics.py`. Missing fields remain missing; they are not zero.
- Existing exploratory implementations: `scripts/report_top_persona_deviations.py` and `scripts/report_full_persona_snapshot.py`; these target older data and require adaptation.

## Data and provenance

[data/artifacts.json](data/artifacts.json) indexes source artifacts. Large private traces, raw inputs, API logs, and workspaces remain under ignored `runs/` and `data/`; this folder contains compact derived artifacts and references. Paths in artifact indexes are repository-relative. No API keys are stored here. The source run remains authoritative.

## Results so far

- Earlier export: [600 trial-1 summary records](data/trial_1_summary_metrics.csv). The three-trial analysis linked above supersedes that interim behavioral summary.
- Original pilot traces motivate the hypotheses but are not expanded-study results.
- The expanded nonsemantic analysis finds substantial reply-length separation, including an English-primary sensitivity, and less exact opening reuse between personas. Extra reviews, revision requests and post-reply question counts show much smaller excess variation. See the report for estimates, CIs, matched panels and limits.

## Completion criteria for the requested nonsemantic analysis

- [x] Outputs exist with task/trial/condition provenance and denominators.
- [x] Technical failures and missing submissions are reported separately.
- [x] Analysis matches the documented experimental unit and uncertainty method.
- [x] Results and limitations are written back into this plan; reports, notebooks and figures are linked.

The full experiment remains open for the deferred semantic work. [Figure QA](figures/behavior/qa/QA_NOTES.md) records the final checks.

## Change log

- 2026-09-29: Created experiment tracker from the updated paper plan and existing implementation.
- 2026-09-30: Completed the requested automatic behavioral analysis, executed its notebook and checked all three figures. No new model calls; semantic trajectories remain deferred.

## Top-ten scope update (2026-09-29)

Expand the current collection to the ten largest absolute prior-pilot deviations: 046, 003, 004, 089, 001, 127, 262, 224, 148, 026. Nine new personas add 5,400 episodes across three trials; 148 and the paired persona-off trials already exist in the initial campaign. Keep 155 as an additional condition outside this selected ten. [Job and baseline manifest](../shared/top10_expansion.json). This supersedes the two-persona-only scope above; the existing trial-1 results remain unchanged. Multi-batch analysis and updated comparison families are pending.

## Implemented: SciConv per-turn output tokens

[Report](SCICONV_TOKENS.md) and [executed notebook](sciconv_tokens.ipynb) now cover six settings (off/148/155/089/001/127), all 40 SciConv cases and three original Astra trials: 719 scored episodes, one infrastructure failure, 7,751 successful API records. `code/analyze_sciconv_tokens.py` extracts numeric per-call output, reasoning and non-reasoning tokens; role-local turn indices; question versus final-specification phases; episode totals and per-turn summaries. Judge usage is separate. Private message text remains in ignored raw traces.

CI summaries use case-equal means and mode-stratified study-cluster bootstrap intervals. Episodes with no simulator reply count zero toward episode totals but do not define a per-reply mean; those denominators remain explicit. Later-turn means condition on reaching each turn. `code/plot_sciconv_tokens.py` exports the role comparison in PNG/PDF/SVG/TIFF with alignment, font and collision QA. Notebook validates unique calls, usage arithmetic, coverage and summary bounds. No API calls. This completes the token-use subanalysis, not semantic trajectories, validated per-fact disclosure labels, or the entire behavioral experiment.

## Implemented: all completed-trial personas

The [expanded behavioral report](ALL_PERSONAS_BEHAVIOR.md) and [executed notebook](behavioral_analysis.ipynb) include off/148/155/089/001/127 (three trials each) and 003/004/046 (one trial each): 3,833 complete traces from 4,200 slots. All 21 automatic metrics and paired effects include the added settings. Original endpoints preserve the prior behavioral method; cancelled initial runs and repaired endpoints are excluded. Thus coverage differs from the repaired performance primary analysis. Within-persona repeat variation, opening collisions and English-primary sensitivity retain the original repeated panel, with exact equality checked against the previous summary. One-trial CIs condition on the observed trial. Previous figures/data remain under `figures/behavior` and `data/behavior`. The separate SciConv API-token report retains its explicitly documented six-setting scope. The trial-1 semantic figure is now implemented below; repeat-adjusted semantic analysis remains prospective.

## Semantic figure: trial 1 with family balancing

The user specified two main panels: A, 5×5 persona-pair heatmaps; B, two question-controlled PCA case studies, in aligned simulator/actor rows. The user then selected **trial 1 only** and requested super-family control. The implemented panel is off/155/001/004/046, using raw cosine distances. Each comparison is matched on question, round and role; questions average within family and the four families receive equal weight. Bootstrap whole questions within benchmark × family. This controls field composition but cannot estimate within-persona rollout randomness from one trial. The adjusted B−(W_i+W_j)/2 estimator is implemented and requires repeats.

The current matched panel contains 148 questions: life 41, physical/engineering 42, math/CS 41, social/humanities 24. Sources: ASI 12, Bix 36, Discovery 29, EXP 34, SciConv 37. The median-case rule selected `bix-43-q5` and `fluids/disambiguation/case_001`; both rows use their actual trial-1 exchanges. Initial generated review requests are retained; the fixed SciConv initial input is excluded. Full lengths, including a 13-message Bix simulator baseline, are shown.

[Semantic report](SEMANTIC_REPORT.md), [notebook](semantic_trajectory_analysis.ipynb), [figure](figures/semantic/semantic.pdf), and `code/semantic/` record the pipeline. The local frozen Qwen3-Embedding-0.6B encoder used no API judge/summarizer. Existing behavioral figures remain intact; question-weighted semantic estimates remain a sensitivity. Fact recovery remains Experiment 08.

## Implemented: additional manual trajectory review

[Review guide](TRACE_REVIEW.md), [interactive gallery](../../runs/semantic-review/index.html) and [executed notebook](semantic_trace_review.ipynb) provide 131 additional complete trial-1 question cases: ASI 12, Bix 30, Discovery 29, EXP 30, SciConv 30. Each contains all five current settings, both roles, full saved message text and local UMAP paths (replacing the review-only PCA gallery at the user’s request). Fixed hash selection excludes the two main-figure cases; insufficient eligible ASI/Discovery cases account for the shortfall from 150. Favorites and notes export as JSON for user selection of illustrative cases. No new inference or changes to aggregate estimates; manually selected examples remain exploratory illustrations. Code and numeric selection provenance are under `code/semantic/gallery*` and `data/semantic_review/`.


### Review selection revised: long interactions

The current UMAP gallery replaces the 131-question sample with 22 questions having at least one setting with ≥4 complete simulator–actor exchanges: Bix 1, SciConv 21. Ten SciConv cases qualify for all five settings. Rank by qualifying-setting count, minimum then total exchanges, with a fixed hash tie-break; retain all five settings and actual lengths. Other sources have no qualifying additional complete cases. This length-enriched set is for manual illustration selection; the aggregate analyses remain unchanged. Obsolete review-only plots are removed and the notebook is regenerated.


### Main semantic figure: user-selected UMAP examples

The main figure and notebook now use `bix-57-q1` and `matToolUse/disambiguation/case_236`, manually selected from the long-interaction review gallery. Panel B reuses the exact reviewed UMAP coordinates for all five settings and both roles; short and single-node trajectories remain visible. Panel A and its confidence intervals are unchanged. The prior median-case PCA figure and notebook are archived under `figures/semantic/previous_median_pca/`. The case-selection record explicitly identifies these as manual exploratory illustrations.


### Final-response, domain-level permutation analysis

User requested a 5×5 comparison of cross-persona versus within-persona semantic distances using final responses, controlling super-family rather than matching question distances. Implementation selects the last generated role message from complete original trial-1 episodes, uses a common five-setting question set and distinct-question pairs within each family, then equal family weights. Question-wise pair-label swaps preserve the repeated collection design without introducing same-question distances into the statistic. Use 10,000 one-sided permutations, Holm across 20 role/pair tests and 20,000 source×family question-bootstrap replicates for pointwise CIs. Outputs live in `data/semantic_final/`; `final_response.py` and `test_final_response.py` implement and check the estimator. Current notebook and report describe this exploratory estimand, not rollout-adjusted variability. Right-hand selected UMAP trajectories remain fixed; prior raw-distance figure archived.

Result: 148 common questions, 1,480 final role messages. Nine of ten pairs have positive excess separation with Holm-adjusted p<0.05 in each role (18/20 total). Persona off versus 004 is not significant in either role. Results are exploratory and conditional on the observed trial and question-wise exchangeability. Full pointwise CIs and permutation p values are in `data/semantic_final/heatmap_cells.csv` and `SEMANTIC_REPORT.md`.


The candidate manuscript caption and detailed methods/interpretation handoff are in [SEMANTIC_FIGURE_CAPTION.md](SEMANTIC_FIGURE_CAPTION.md). Case titles retain benchmark names above short identifiers: BixBench / bix 57 and SciConvBench / case 236.


### Exploratory replacement: persona 089

At user request, current panel is off/155/001/089/046. Complete common coverage is 158 questions (1,580 final messages). 089 trial-1 saved messages were embedded locally with the same frozen Qwen model; no new interaction API calls. Both selected UMAP cases were refitted for all five settings. Nine pairs per role remain significant; off–089 is nonsignificant (Holm p≈0.386). The 147-question shared-coverage sensitivity gives the same decision pattern. Prior 004 panel outputs are archived in `figures/semantic/previous_persona_004/`; this replacement is documented as exploratory, not a search establishing significance.


### Exploratory replacement: persona 003

At user request, panel is now off/155/001/003/046. Persona 003 specifies Russian primary output, intermediate English, blunt/slangy/concrete/detail-oriented style, and an analytical, risk-averse approach. It has 104 complete trial-1 episodes; five-setting common coverage is 97 questions (ASI 7, Bix 27, Discovery 21, EXP 5, SciConv 37). All ten comparisons per role are significant after Holm correction; off–003 excess is 0.041161 simulator and 0.022604 actor (p≈0.002). These are exploratory results and may include language effects; coverage differs substantially from the 089 panel. The earlier panel is archived and a shared-question sensitivity is recorded. No new interaction API calls; only local embedding and projection/statistical recomputation.

## Offline actor tool-use analysis (2026-10-02)

Implemented `code/analyze_tool_calls.py` and appended section 6 to `behavioral_analysis.ipynb`. Counts recorded execution/inspection actions across 1,518 complete original episodes; excludes 440 SciConv episodes as not applicable. Four benchmarks have equal weight; contrasts match question and trial. [Results and caption](TOOL_CALLS.md), per-episode provenance and all ten pairwise CIs in `data/tool_calls/`, PNG/PDF/SVG heatmap in `figures/tool_calls/`. Existing notebook sections and scientific outputs were retained.

## Compact behavioral comparison (2026-10-02)

Updated the final notebook figure to one row of four lower-triangle heatmaps: whole-episode simulator + actor completion tokens, revision requests, clarification recall, and actor tool use. Stars denote two-sided paired study-cluster sign-flip tests with Holm correction across 40 comparisons. Earlier notebook sections remain intact. Definitions, coverage, confidence intervals and adjusted p values are in [COMPACT_BEHAVIOR.md](COMPACT_BEHAVIOR.md); reproducible extraction and plotting are in `code/compact_behavior.py`. Notebook figure and results cells were executed offline. PDF text audit: minimum 8 pt; collision and panel alignment audits passed. The 274 mm master canvas is deliberate for the requested horizontal four-panel layout; PDF/SVG are vector masters and 600-dpi PNG is the preview (TIFF was not requested).

### Split token panel correction

Panel A now uses simulator tokens in its lower triangle and actor tokens in its upper triangle, rather than summing the roles. Both use episode-total recorded completion tokens in thousands, one shared scale, and row-minus-column signs. Panels B–D remain lower-triangle only. Holm correction now covers 50 displayed contrasts. The figure, notebook and companion results table were refreshed.

### Exploratory display threshold

At user request after inspection, stars now denote Holm-adjusted p < 0.10 across the same 50 comparisons. Effect estimates, p values, tests and 95% confidence intervals are unchanged.

### Success-conditioned panels B and C

B and C now restrict paired comparisons to question/trial episodes with full native credit (100) in both settings. B averages revision requests per successful episode; C averages per-episode clarification recall. A and D are unchanged. This descriptive jointly successful subset has pair-specific coverage. Tests and Holm adjustment are recalculated across the same 50 contrasts at adjusted p < 0.10.

### Restore all matched episodes

B and C restored to all eligible matched episodes regardless of outcome. At user request, the exploratory star threshold is now Holm-adjusted p < 0.15 across all 50 contrasts, selected after reviewing prior thresholds and outcome subsets. Keep 95% pointwise CIs; do not interpret the display as a prespecified confirmatory test.

### Display threshold 0.20

At user request, stars now denote Holm-adjusted p < 0.20 across the same 50 comparisons. This is an exploratory threshold chosen after inspection. All-episode coverage, estimates, tests, adjusted p values and 95% confidence intervals remain unchanged.

### Disclosed effect-size highlights

Star key: A/B, Holm-adjusted p < 0.20 across 50 comparisons; C, absolute difference > 2 percentage points; D, absolute difference > 0.2 calls/episode. C/D stars highlight user-selected effect-size thresholds, not statistical significance or 95% confidence. Thresholds were selected after inspection. The definition appears immediately below the notebook figure and in COMPACT_BEHAVIOR.md. Numerical estimates, confidence intervals and p values are unchanged; CSV/JSON retain statistical `star` separately from `figure_star`.

### Separate simulator and actor panels

Final figure now uses A simulator output, B actor output, C clarification recall and D actor tool use, all lower triangles with row-minus-column contrasts. A/B share token color limits. Revision-request panel removed after inspection; its tests remain in the original 50-comparison Holm family and CSV/JSON results. Display annotation rules are unchanged and disclosed in accompanying text.
