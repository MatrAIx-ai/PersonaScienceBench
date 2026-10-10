# Benchmark paper plan

> **Current run (2026-10-01):** [MAIN_RUN.md](../MAIN_RUN.md) defines 200 frozen questions (40 per benchmark), off / 155 / 001 / 003 / 046, and 1,000 episodes per fresh trial (3,000 for three). Default resources are 30 workers / CPUs and 128 GB; all roles use Astra low. The paper has three analysis levels: performance, semantic diversity, and behavioral diversity. Earlier scheduling, cohort, and collection-status statements below are historical planning records; they do not override the main-run guide or establish live job status. Detailed local analysis updates are maintained separately.

Implementation, per-experiment plans, status snapshots, and derived artifacts are tracked in the [Experiment workspace](../../Experiment/README.md).

## Current main run and analysis presentation (2026-10-01)

The runnable campaign is defined by [MAIN_RUN.md](../MAIN_RUN.md): **200 frozen questions, 40 per source, under off / 155 / 001 / 003 / 046**. Three fresh trials would produce **3,000 episodes**. This is distinct from historical collection coverage: off/155/001 have three original trials, while 003/046 have one. Historical six- and nine-setting reports remain supporting analyses; their counts must not be described as the current five-setting cohort.

The paper organizes evidence into **performance, semantic diversity, and behavioral diversity**. Diversity does not establish human realism. Latest selected-panel displays are:

- **Performance (02):** absolute native scores with intervals and compatible question–trial paired differences, by benchmark and super-family. The notebook retains the larger historical cohort and a separate five-setting section.
- **Semantic diversity (01):** role-separated final-response distances, equal super-family weighting, and question-wise label-swap tests; current within-persona distances compare different questions, not repeat rollouts. The five-setting intersection contains 97 questions. Two manually selected question trajectories use local UMAP. See the [current caption/methods](../../Experiment/01_behavioral_diversity/SEMANTIC_FIGURE_CAPTION.md); earlier PCA/004/raw-distance descriptions below are superseded.
- **Behavioral diversity (01/09):** four pairwise heatmaps for simulator total output tokens, actor total output tokens, revision requests, and clarification recall. Token totals include reasoning. Experiment 09 contains actor self-repetition (at least three corresponding matches in six-word windows) and complete-fact recovery conditional on SciConv failure. Current figure definitions live in the executed notebooks; older exported reports are preserved snapshots.

This section supersedes conflicting display/cohort statements below. It changes no observations, analysis outputs, or historical run receipts. No new inference is authorized by this plan.

## Earlier integrated scope and claim (2026-09-30)

The empirical question is: **does persona conditioning broaden semantic and behavioral coverage beyond repeated sampling of a persona-off simulator, and what does that variation reveal about scientific collaboration?** Heterogeneity in scientific collaboration motivates the study. Human realism is not an evaluated endpoint; no human realism study is required. Repeated templates or narrow semantic coverage in persona-off are hypotheses to measure, not established findings. Diversity alone does not establish fidelity to real researchers.

The paper includes Experiments 01–05 and 08; operational folders 06 and 07 are excluded from the experiment list. Fact recovery (08) is a standalone scientific experiment, separate from conversation case studies (04). This integration supersedes historical scope, submission, and display descriptions below where they conflict. It changes the paper/analysis plan only; it does not authorize new inference, resubmission, or changes to frozen data.

- **Primary repeated panel:** persona-off and 148/155/089/001/127, 200 frozen tasks, three original Astra trials. These are 3,600 planned episode slots, not 3,600 valid observations. Keep task/study counts, surviving trials, scientific missing submissions, and infrastructure failures explicit.
- **Exploratory breadth:** 003/004/046 have one original trial each. They can extend descriptive coverage, but cannot establish within-persona repeatability. The other selected personas 262/224/026 have no collected results. Preserve the original 30-persona pilot as selection provenance, not additional independent confirmation.
- **Existing evidence:** Experiment 01 now has the [nonsemantic behavioral report](../../Experiment/01_behavioral_diversity/ALL_PERSONAS_BEHAVIOR.md) and executed notebook covering 3,833 complete original episodes across eight personas plus off (003/004/046: one trial; other settings: three; repeat-variation panel unchanged), plus its separate SciConv token analysis. Experiment 02 has the [consolidated performance report](../../Experiment/02_performance_and_fields/PERFORMANCE_REPORT.md), retained score tables, matched/version-filtered contrasts, run variation and coverage sensitivities. Experiment 08 has native fact recovery (359/360 original eligible episodes). The requested trial-1 semantic figure now uses family-balanced raw distances and question-controlled PCA paths; repeat-adjusted semantic separation and expanded annotated conversation case studies remain pending.
- **Model comparison (withdrawn 2026-10-01):** The user excluded the incomplete Sol campaign from the current study and trace publication; raw runs are archived locally. The following collection description is historical. Experiment 03 changes actor and simulator together, holding the Astra judge fixed. Saved progress files show all six Sol batches processed: 690 episodes marked finished (including missing submissions) and 2,910 infrastructure failures. This is incomplete scientific coverage, not a completed comparative result. Do not describe it as an isolated actor effect or infer model ranking from surviving episodes alone.
- **Protocol separation:** existing Astra analyses use the historical protocol. The post-PR6 strict SciConv persona-off attempt produced zero scored cases after credit exhaustion and provides no comparative evidence. Future controls in Experiment 08 remain prospective.

The core evidence chain is **behavioral diversity (01) → semantic divergence beyond repeat variation (01) → heterogeneous scientific outcomes (02) → SciConv fact recovery (08) → trace-grounded explanation (04)**. Experiment 03 is a conditional cross-model extension; 05 is an optional static reference.

## Historical expansion to the ten largest absolute pilot changes (2026-09-29)

The user selected the ten largest **absolute changes from persona off**, not the ten highest scores. In ranked order these are **046, 003, 004, 089, 001, 127, 262, 224, 148, 026**. This outcome-selected panel includes both positive and negative pilot deviations. Persona 148 already belongs to the original expanded campaign; persona 155 remains an additional comparison outside this top-ten set.

Run the other **nine personas × 200 frozen tasks × three trials = 5,400 new episodes**. Reuse the corresponding trial's persona-off baseline and the existing 148 episodes; no new baseline or 148/155 episodes are scheduled by this expansion. The top-ten-plus-baseline panel therefore contains **6,600 episodes**; including the retained 155 condition gives **7,200 total planned episodes**. This supersedes the two-persona-only scope for the expanded persona panel; sections describing the 1,800-episode campaign remain provenance for its initial phase.

The scientific setting remains GPT-6 Astra low, the same frozen inputs, full profiles, tools, grading, and budgets. Following the 2026-09-29 concurrency update, trial 3 uses 128 GB RAM, 40 CPUs, and up to 40 concurrent episodes. The nine pending expansion batches were subsequently reduced to 35 workers / 35 CPUs after rate-limit failures at 40; memory remains 128 GB. Earlier trials retain their original 30-worker allocation. To avoid overlapping API load, nine 600-episode batches form an `afterany` chain after resumed trial 3 (replacement job 1965844). Groups are [046, 003, 004], [089, 001, 127], and [262, 224, 026], repeated for trials 1–3. `afterany` enforces non-overlap but does not certify successful completion; errors remain visible for later repair.

The [expansion manifest](../../runs/openai-astra-top10-expansion.json) records jobs, dependencies, exact profile hashes, run directories, and matching baseline references. The [submission entry point](../../scripts/submit_top10_expansion.py) submits prepared batches idempotently; the coordinator's `--baseline-run` verifies task/model/settings compatibility. The first job is 1964501; the final job is 1964513. Additional actor models and the static reference remain unsubmitted.

Extend behavioral and outcome analyses to this named panel without choosing personas again from expanded-study scores. Keep 155 separately labeled, disclose pilot selection and overlap, and predefine the multiple-comparison family for the expanded analysis. Existing three-condition interim tables are unchanged historical results. Expanded multi-batch aggregation is still to be implemented; the current three-arm CI script must not be used as if it covers all ten personas.

## Paper story

**A scientific agent should be evaluated with a range of researchers, not just one default simulated user. Researcher preferences and expertise can change how the agent asks, plans, revises, and ultimately performs.**

A generic LLM simulator may repeatedly express a similar helpful, cooperative style. We will measure baseline repetition and semantic concentration, then ask whether full-profile conditioning creates a wider, repeatable range of interactions and what that diversity reveals about scientific agents. We do not assume that more textual variation means better scientific performance or greater human realism.

The story has three steps:

1. **Measure diversity beyond run variation.** Compare communication, information-sharing, and workflow patterns between personas and within repeated runs of each condition.
2. **Measure consequences in both directions.** Compare native outcomes and completion on matched tasks across benchmarks and scientific families. Behavioral changes with little outcome change are also informative.
3. **Explain observed differences with conversations.** Link profile wording, simulator responses, actor actions, and deliverables. Use SciConv fact recovery as a quantitative view of information recovered, without treating recovery alone as a disclosure mechanism.

The contribution is a benchmark of diverse scientific collaboration: automated task conversion, full-profile researcher simulation, and evaluation of both outcomes and interactions. Construction establishes the benchmark; the experiments supply the main story. Per-benchmark conversion rules and complete persona schemas belong mainly in the appendix and repository. The study evaluates simulated collaborator diversity; it does not require a human experiment.

The [pilot](../../reports/full_persona_v2/README.md) supplies the starting examples: 30 personas plus persona off, ten scientific questions, and 310 finished episodes. The [trace case studies](../../reports/full_persona_v2/case_studies.md) show useful clarification, targeted pushback, stalled approval, and language adaptation. The expanded repeated panel now contains five personas plus off, with three further personas available for single-trial exploration. Selection used prior performance changes, not a representative sample of researchers. Disclose selection and task overlap; do not generalize the measured diversity to all personas or human populations.

## Experiments that carry the story

| Experiment | Question it answers | Comparison and main result |
|---|---|---|
| **01. Behavioral diversity** | Does persona conditioning broaden behavior and meaning beyond repeat variation? | Role-separated communication length/language, extra reviews and revisions, clarification quality, repeated questions, template concentration, and stage-aligned semantic distances. Compare within-persona and between-persona variation on matched tasks. Main Figures 2–3. |
| **02. Performance and field dependence** | What scientific consequences accompany the different interactions? | Native benchmark scores, paired changes from off, submission rates, and super-family heterogeneity. Expertise relationships require explicit profile-based annotation. Main Figure 4 and the existing two performance tables. |
| **03. Joint actor/simulator comparison** | Do patterns persist with a different collaborating model pair? | Astra/Astra versus Sol/Sol, with Astra judging and matched scientific settings. Report behavioral patterns, performance, and coverage together. Conditional comparison table only after an adequate matched analysis; current Sol missingness limits conclusions. |
| **04. Conversation case studies** | What traceable sequence connects profile, behavior, action, and outcome? | Two or three task-matched examples, including behavior changes without score changes and unproductive interactions. Exact excerpts and event IDs support descriptive explanations, not isolated trait causality. Main Figure 6. |
| **05. Static reference** | What differs when task-owned context is supplied upfront? | Optional ten-task execution/design reference, three trials, no simulator, comparable actor budgets. Exclude SciConv and private evaluator answers. Supplementary if run; currently unimplemented. |
| **08. SciConv fact recovery** | Do personas change how much missing scientific information the actor recovers, even when binary success changes little? | Standalone experiment on the existing 20 disambiguation cases: recovered/total deleted facts, paired change from off, FRR, and cap-hit sensitivity. Main Figure 5 and a dedicated recovery table. Per-fact disclosure labels and new protocol controls remain prospective. |

A small **static reference** can place these results beside conventional evaluation: ten nonvisual execution/design questions, one actor, three independent episodes per question, original task context available upfront, and no simulator. Compare it with the matching neutral and persona-conditioned runs. Keep task-owned context available, evaluator answers private, and total actor budgets comparable. This is a reference setting; the main persona comparison is interactive persona off versus interactive persona on. SciConv remains an interaction task rather than being converted into a trivial full-specification copying test.

## Historical initial execution setting

The frozen configuration is **200 tasks × three conditions × three independent complete episodes = 1,800 episodes** for one actor. The conditions are **persona off, candidate_148, and candidate_155**. Actor, researcher simulator, and model-based evaluator all use **direct OpenAI Responses API, `gpt-6-astra`, reasoning effort `low`**. Astra does not support the originally requested `none`; `low` was explicitly selected instead. Native non-model evaluators remain in place.

Keep the exact full persona profiles private to the researcher simulator; neither actor nor evaluator receives them. General knowledge is available to the simulator in all conditions. Execution/design tracks use the existing active-researcher protocol, mandatory approach/result review, a 12-request collaboration limit, and a 60-call actor budget. SciConv retains its native clarification workflow with up to ten dialogue turns. Retain the existing per-role output limits and native grading contracts, including EXP's three judge repetitions; judge repetitions are not independent episode trials.

The original trials requested **128 GB RAM, 30 CPUs, and a 12-hour Slurm allocation**, with up to **30 concurrent episode processes**. Pending trial 3 and the nine expansion batches were subsequently changed to **40 CPUs / 40 concurrent episodes**, keeping memory, time, and sequential execution unchanged. The nine expansion batches were subsequently reduced to **35 CPUs / 35 concurrent episodes** ([35-worker audit](../../Experiment/shared/worker_35_resubmission.json)); trial 3 continues at 40. For the earlier change see [submission audit](../../Experiment/shared/worker_40_resubmission.json). Scientific BLAS/OpenMP threads are limited to one. Run actual episodes without a separate smoke-test campaign; intrinsic runtime startup checks remain. Entry points: [run coordinator](../../scripts/run_openai_first_pass.py), [submission script](../../scripts/submit_openai_first_pass.sh), and [run instructions](../../scripts/OPENAI_FIRST_PASS.md).

| Trial | Episodes | Slurm job | Recorded state / provenance |
|---|---:|---|---|
| 1 | 600 | 1957983 | Processed in 3 h 21 min 22 s: 536 scored, 32 missing submissions, 32 errors. Three completed episodes were retained from the interrupted initial campaign. |
| 2 | 600 fresh | 1962301 | Submitted with identical task inputs and settings; no episode results reused. |
| 3 | 600 fresh | 1962305 | Submitted with identical task inputs and settings; no episode results reused. |

Submission records are in the [three-trial manifest](../../runs/openai-astra-top2-three-trials.json). Trial 1 is [here](../../runs/openai-astra-top2-first-pass/manifest.json); trials [2](../../runs/openai-astra-top2-trial-2/trial.json) and [3](../../runs/openai-astra-top2-trial-3/trial.json) reuse frozen prepared inputs, with fresh conversations and outputs. The earlier seven-condition job (1957850) was cancelled; it is not an additional trial. These are recorded submission facts, not a live job-status display.

## Benchmark mixture: 200 questions, 40 per source

Use the **frozen random sample**, seed **20260929**, with **40 distinct questions from each benchmark**. This replaces the earlier 70/50/40/36/4 proposal and the four-case ASI allocation. The [selected manifest](../../runs/openai-astra-top2-first-pass/selection.csv) is copied from the [empirical sampling audit](../../reports/conversion_v2/superfamily_audit/diagnostic_plots_allowed.random_sample.csv); its SHA-256 is `746191312aa95b39a1b041b14e0a92dd97d7cb68f6d39d719d6bc6fd20b06533`. Use this identical panel for every condition and trial; do not resample tasks between trials.

The selected policy allows diagnostic plots and numerical scientific workflows, while excluding image-centric objectives such as image interpretation, microscopy/image analysis, reconstruction, computer vision, video, and visual generation. Screen scientific objectives and required outputs as well as file types. Preserve each task's native deliverable and grading contract. Eligibility screening and successful input preparation do not guarantee successful execution or grading.

| Benchmark | Questions | Life sciences | Physical sciences & engineering | Mathematics & computer science | Social sciences & humanities | Task and answer formats |
|---|---:|---:|---:|---:|---:|---|
| **DiscoveryBench** | **40** | 5 | 0 | 3 | 32 | Data analysis and evidence-backed hypothesis synthesis. |
| **BixBench** | **40** | 40 | 0 | 0 | 0 | Biological data analysis, numerical estimates, comparisons, counts, and model interpretation. |
| **EXP-Bench** | **40** | 0 | 6 | 34 | 0 | Experimental design and controlled comparisons; design only. |
| **SciConvBench** | **40** | 0 | 34 | 6 | 0 | Recover requirements or resolve contradictory scientific specifications. |
| **ASI-Bench** | **40** | 5 | 23 | 12 | 0 | Scientific implementation and execution with numerical artifacts. |
| **Total** | **200** | **50** | **63** | **55** | **32** | 80 empirical analyses, 40 designs, 40 specification dialogues, and 40 scientific implementations. |

Equal source quotas define the design; the super-family counts above are the empirical distribution of the frozen sample, not equal field quotas or a post-outcome optimization. Family and benchmark remain partly confounded: all selected social/humanities questions come from Discovery, and Bix dominates life sciences. Retain the subfield, source study, and task-family tags in the manifest. Different questions from one study may appear; do not treat them as independent studies. The [audit](../../reports/conversion_v2/superfamily_audit/) records screening and candidate coverage. Report any pilot overlap explicitly rather than assuming the expanded sample is fully held out.

All 200 inputs were prepared successfully for trial 1. Its matched evaluable analysis retained **185 tasks** after excluding any task with a technical/evaluation error in one or more conditions: 31 ASI, 40 Bix, 34 Discovery, 40 EXP, and 40 SciConv. Their family counts were 46 life, 57 physical/engineering, 54 math/CS, and 28 social/humanities. These are analysis counts, not replacement sampling quotas; later trials may have different failure patterns.

### Three samples per task and condition

Interpret the three samples as **three independent complete episodes for each task × persona condition × actor**, each starting from the original task with a fresh conversation. Both actor and simulator generate a new trajectory. Score all three outputs and report their mean and within-condition variation; do not select the best answer or generate three endings from one shared conversation.

The three conditions are two full personas plus persona off. Run the baseline three times per task and actor, then reuse that same baseline mean for both paired persona–baseline comparisons. Retain all trial outcomes and errors; never substitute a successful rerun silently for a failed trial. The 200 questions remain the task panel; the three samples measure repeat variation rather than adding new questions. This replaces the earlier proposal to repeat only a ten-question subset.

## Historical initial selection: two personas plus off

Use the two highest-scoring profiles in the original 30-persona pilot. Preserve the exact full injected profiles across all tasks and trials.

| Persona | Background and collaboration traits | Selection evidence |
|---|---|---|
| [148](../../reports/full_persona_v2/profiles/candidate_148.md) | Senior medical researcher; medicine/statistics expertise, English communication, extensive detail, accuracy-first work, and demanding approval behavior. | Highest prior-pilot mean: 39.37%, versus 26.01% for persona off. |
| [155](../../reports/full_persona_v2/profiles/candidate_155.md) | Agriculture/agronomy and management background; Mandarin communication, concrete detailed guidance, structured teamwork, and preference for familiar methods. | Second-highest prior-pilot mean: 38.60%, versus 26.01% for persona off. |
| Persona off | Same interactive researcher workflow and general-knowledge access, without an injected persona identity. | Shared baseline for both persona comparisons. |

This replaces the proposed six-profile expanded panel (148, 046, 155, 228, 137, 089). Retain the original 30-persona study as the exploratory screen, including negative and behaviorally contrasting profiles. Selection was based on prior-pilot scores, not the expanded run's outcomes. Disclose this selection and any task overlap when interpreting transfer to the expanded panel. Full profiles contain many attributes, sometimes inconsistent; these experiments do not isolate individual traits or demographic effects.

### Does expertise help in its own field?

For every persona–task pair, record **direct / adjacent / outside / unknown field relationship**, supported by the actual injected profile, plus separate methodological familiarity such as statistics or coding. A domain label alone does not establish expertise: 148's cardiology and statistics background is not automatically computational-biology expertise, and 155's agronomy background does not establish expertise across all life-science tasks.

For each persona, compare its **task-matched score change from persona off** in related and unrelated fields, alongside changes in questioning and supervision. Compare personas on identical tasks, and compare field effects within the same benchmark/format where coverage permits. For example: does 148's statistical guidance transfer across fields, and does 155's practical agronomy background align with any selected tasks? Show a persona × subfield heatmap with sample counts, then separate panels by workflow. Where field and format coincide, report that combination; do not fit a large factorial model to two profiles.

## Interaction metrics: useful and obtainable

Most measures come from saved event logs and native evaluations. Keep expensive semantic judgments concentrated on the case-study traces.

| What we want to know | Measures | How to obtain them |
|---|---|---|
| **Does the work succeed?** | Native score, submission rate, paired score change, and score conditional on submission. | Already recorded. Report native results per benchmark; count missing submissions as zero in the all-attempt score. |
| **How much collaboration is needed?** | Total exchanges, additional approach-review rounds, result revisions, and exhausted dialogue budgets. | Automatic event counts. Separate required first reviews from extra exchanges. |
| **Does the actor become more active and useful?** | SciConv questions after the first simulator reply, issue coverage, relevant-question fraction, and exact repeated-question rate. Outside SciConv: actor-raised questions or new proposals inside handoffs. | SciConv counts and native judge outputs already exist. Questions/proposals inside other handoffs need a small content-labeling pass on selected traces. |
| **How does communication change?** | Visible reply characters by role, language choice, actor language matching, and API token usage. | Text extraction and light language labeling. API tokens measure model-call usage; visible-message length is a separate quantity. Avoid whitespace word count as the main multilingual comparison. |
| **Does conditioning broaden semantic coverage?** | Stage-matched semantic distances within off, within each persona, and between different personas; baseline-centered trajectories. | Fixed multilingual encoder on shared messages only. Match tasks, roles, stages, and weighting; report distances in the original embedding space alongside illustrative PCA paths. Trial-1 raw distances and question-controlled paths are implemented in Experiment 01; repeat-adjusted comparisons remain prospective. |
| **How concentrated are conversational templates?** | Exact repeated-question rate and frequency of recurring response openings or optional dialogue patterns, with a frozen normalization rule. | Add as an exploratory diagnostic in Experiment 01. Remove protocol-required boilerplate, control language/length and sample size, and show common examples. Repeated mandatory approvals alone do not establish semantic collapse. |
| **Does feedback change the work?** | Specific suggestions adopted, rejected, or unresolved; resulting changes in method, assumptions, or final answer. | Evidence-backed annotation of case studies, linking the simulator message to the actor's later action. |
| **Is the behavior connected to the profile?** | Expression or contradiction of two or three relevant, observable preferences per selected persona. | Read the exact profile alongside trace excerpts; use a short frozen rubric, with “not applicable” where the task offers no opportunity. |

The automatic/native measures and semantic comparisons supply the quantitative results; feedback adoption and profile alignment explain selected cases. No human realism scores are planned. Broad claims such as “all new scientific advice is correct” or “information gain at every turn” are not core metrics. Per-fact asked/disclosed/volunteered labels belong to Experiment 08's prospective annotation plan, not existing measured outputs. For any content annotation, retain event IDs and excerpts, document the rubric and validation, and hide outcome scores where practicable.

### What SciConv already tells us about proactivity

There is no single native proactivity score, but the [current runner](../../src/personasciencebench/sciconv_runner.py) already exports:

- **Clarification recall:** missing entities or inconsistencies asked about / total annotated issues.
- **Clarification precision:** relevant question turns / all question turns.
- **FRR:** final resolution with intent preserved; **CGRR:** successful resolution grounded in the conversation; **SRR:** successful resolution without sufficient conversational grounding. FRR = CGRR + SRR.
- **Memory consistency and intent capture:** whether the final specification retains supplied information and the intended task.

Together, these distinguish asking more from asking usefully, and resolving through dialogue from resolving silently. The counts are judge-derived; retain their evidence and flag inconsistent counts when analyzing them. Use the exported coverage/relevance fields rather than treating every upstream `CR`/`CP` alias as the same definition.

The actor's first SciConv question occurs before it receives a persona-conditioned reply, so changes in activity attributable to that reply must be examined afterward. In the other four tracks, the [controller](../../src/personasciencebench/collaboration.py) requires plan/result handoffs: extra review requests measure simulator activity, while questions and proposals inside actor handoffs measure actor initiative. These are separate quantities.

## Figures and tables: purpose and dependencies

Plan **six main figures**, giving SciConv fact recovery its own quantitative figure and keeping conversation case studies separate. Retain the task/profile tables, the two existing performance tables, and the dedicated fact-recovery table; a joint-model comparison table is conditional. Final main-versus-supplement placement of tables depends on space, not on which results are favorable. The sequence is construction → behavioral diversity → semantic divergence → scientific consequences → fact recovery → explanatory cases.

| Item | What we want to show | Data required | Experiment dependency / what can be prepared now |
|---|---|---|---|
| **Figure 1 — Benchmark overview** | How scientific tasks become collaborations, where the persona enters, and how outcomes and behavior are evaluated. | Conversion rules, public/researcher/evaluator context, simulator–actor workflow, native grading contracts. | Construction only. Draft now; use the frozen 40-per-source, 200-task panel. |
| **Table 1 — Task coverage** | Breadth across scientific subfields and formats, with source-study counts so many questions from one study are visible. | Final task IDs, benchmark, subfield, format, source family, and nonvisual eligibility. | Task selection. Use the frozen manifest and distinguish full-panel counts from matched evaluable counts. |
| **Table 2 — Selected personas and baseline** | The concrete differences represented by all five repeated-panel personas: scientific background, methodological familiarity, communication/workflow preferences, and language. | Exact injected profiles and two or three observable attributes per profile. | Persona construction. Label 003/004/046 separately if included for exploratory breadth; disclose pilot selection. |
| **Figure 2 — Behavioral diversity and repeat variation** | Whether personas produce distinct patterns of questioning, extra reviews, revisions, repetition, and communication. | Persona × behavior heatmap of matched differences; all-task reply-length distribution and within/between-condition variation. Keep original-unit summaries available. | **Experiment 01.** Automatic/native behavioral analysis and notebook are implemented; semantic work deferred. Separate simulator behavior from actor adaptation, and SciConv from required-review workflows. |
| **Figure 3 — Question-controlled semantic distances and trajectories** | Persona-associated content differences, with matched questions and balanced super-families. | A: role-separated 5×5 heatmaps; B: two shared questions with local PCA paths, in simulator/actor rows. | **Experiment 01.** Trial 1 only for off/155/001/004/046; raw cosine distance, equal family weights, benchmark × family question bootstrap. Repeat-adjusted separation is deferred until repeats are included. |
| **Figure 4 — Outcomes across benchmarks and fields** | How each persona's task-matched performance change varies across sources and scientific families, including small or null changes. | Preserved heatmap design expanded to eight eligible personas plus off; absolute and paired scores, 95% CIs and trial coverage. | **Experiment 02.** Implemented in `performance_analysis.ipynb`; includes single-trial 003/004/046 and preserves the older six-setting heatmap. Cancelled initial-run records are excluded; the forest alternative is discarded. ASI uses corrected-version pairs; source-confounded families remain descriptive. Existing absolute-score bars remain available. |
| **Performance tables — benchmark and super-family** | Exact outcomes and uncertainty underlying Figure 4. | Existing six-setting tables, means and 95% CIs, task/episode counts, paired contrasts and coverage. | **Experiment 02.** Both table structures are preserved; version-aware matched analysis and coverage sensitivities are implemented. Super-families remain descriptive source mixtures. |
| **Conditional model-comparison table** | Whether diversity and outcome patterns extend to another collaborating model pair. | Matched Astra/Astra and Sol/Sol observations, behavior, native outcomes, completion, and exclusions. | **Experiment 03.** Both collaborating roles change; current missingness prevents treating this as completed model-generalization evidence. |
| **Figure 5 — SciConv fact recovery** | Show partial recovery of missing scientific facts and paired changes from persona-off. | Two quantitative panels: mean recovery fraction by persona with 95% CIs, and matched persona-minus-off differences with 95% CIs. | **Experiment 08.** Existing figure and executed notebook available for 20 disambiguation cases, six settings and three trials. Recovery is distinct from FRR and from volunteered information. |
| **Fact-recovery table** | Exact recovery estimates and binary success alongside coverage. | Recovery %, paired change in percentage points, FRR %, cases/episodes and cap hits; CIs for recovery and paired differences. | **Experiment 08.** Existing report table available. Original outcomes primary; repair and cap-exclusion sensitivities supplementary. |
| **Figure 6 — Conversation case studies** | Connect profile wording, simulator utterances, actor actions and outcomes. | Two or three compact task-matched trace examples with exact excerpts and event IDs. | **Experiment 04.** Expanded trace panels remain pending. Include unproductive or score-neutral changes; use Experiment 08 results where relevant without merging the two experiments. |

**Supplementary material:** (1) the full task/source manifest and conversion contracts, derived from task selection; (2) exact profiles/prompts and original 30-persona selection provenance, already available; (3) all three-sample outcomes and behavioral results by task/persona/actor, dependent on Experiments 1–3; (4) metric definitions, semantic annotation rubric and evidence excerpts, dependent on trace analysis; (5) extended case-study transcripts supporting Figure 6; and (6) fact-recovery repair and cap-hit sensitivities supporting Figure 5. If the optional static reference is run, include its paired outcome/behavior table here. These support the main story without adding another experiment campaign.

### Figure 3: question-controlled semantic distances and trajectories

Latest user specification: exactly two main panels, with simulator and actor rows. Panel A occupies one-third of the width and contains symmetric 5×5 heatmaps. Panel B occupies two-thirds and contains two question-specific local PCA plots per role. Use off/155/001/004/046, **trial 1 only**, and balance the four scientific super-families equally after matching every distance on exact question, round and role.

Embed only the current generated message separately by role, using a frozen multilingual encoder and L2-normalized cosine distance. Retain generated initial review requests; omit fixed input, system/profile metadata and transcript history. Do not concatenate roles, summarize with an LLM, or add behavior/performance panels. No message fabrication, duplicated endpoints or forced PCA origins.

Use a common eligible round set across all five conditions for each question/role, then average rounds within question, questions within super-family, and the four families equally. Resample whole questions within benchmark × family for pointwise 95% CIs. With one rollout per condition, label cells **raw cosine distance**; the requested excess-distance estimator requires at least two independent rollouts for every condition. Super-family balancing controls composition, not repeat randomness.

Choose two source-distinct median-separation cases by a documented rule. Show rollout 1 for all five settings and both roles, preserving every observed round and marking the final node. Fit a single local PCA per question/role to all included trial-1 messages. Report local explained variance and do not compare coordinates across plots. These examples illustrate the aggregate and are not independent evidence. Full source/family/round coverage, preprocessing, model revision, CI tables and the question-weighted sensitivity belong in the executed notebook and report. Fact recovery stays in Figure 5.


Freeze the encoder, normalization and comparison definitions before computing the expanded analysis; these choices are retrospective analysis decisions, not preregistration. Check length and language sensitivity, remove identity/task boilerplate, and preserve actor versus simulator roles. Three repeats give limited within-task variation estimates, so aggregate with task/study-aware uncertainty. Report per-metric effects instead of an arbitrarily weighted universal diversity score.

## Discussion: show the actual conversations

Use two or three compact case-study panels. Each should contain the relevant **profile wording**, two to four short **actor/simulator excerpts**, the **actor's subsequent action**, and the **task outcome**, alongside the matching baseline.

Historical examples from the exploratory pilot are listed below. Select current examples from the six-setting repeated panel where available. Identify historical pilot traces as pilot evidence; 003/004/046 expansion traces are separate single-trial evidence, not pilot traces or three-trial confirmation:

- **Completeness and task recovery:** 148's “Every detail” preference, its broad SciConv answer, and the actor's incorporation of missing geometry and boundaries. Contrast with an incomplete symbolic deliverable, while distinguishing what the actor asked from what the simulator volunteered.
- **When pushback helps or stalls:** 046's “Step-by-step pair programming” preference and targeted Bix inspection that resolves a column mismatch; contrast with 148 withholding approval on an unreadable workbook. The first produces a usable answer; the second exposes a protocol bottleneck.
- **Language changes the collaboration:** 155's Mandarin instruction, the actor switching language, and the extra question about the final answer's language; 046 supplies a Spanish comparison.

Bring these snippets into the discussion rather than leaving all evidence in the appendix. Include the difficult examples: a high-scoring persona can stall a workflow, and a low-scoring persona can rescue a task. Describe observed mechanisms and profile alignment without requiring edited replies, checkpoint interventions, or a new ablation campaign. Detailed evidence is already linked in the [case-study report](../../reports/full_persona_v2/case_studies.md).

## Analysis and what comes next

1. **Complete the offline behavioral analysis (01):** use the six-setting repeated Astra panel to extract additional reviews/revisions, clarification metrics, visible-message lengths, language matching and budget exhaustion. Then compute semantic variation and exploratory template concentration. Separate role, task format, trial and protocol version.
2. **Consolidate scientific consequences (02):** retain the existing benchmark/super-family tables and figures, add version-consistent matched contrasts and coverage, and report original versus repaired results explicitly. Expertise mapping remains exploratory and requires profile evidence.
3. **Present fact recovery independently (08):** retain the existing two-panel recovery figure, exact result table and executed notebook. Report the 20-case scope, paired differences, FRR and sensitivity checks. New per-fact disclosure trajectories require annotation and are not prerequisites for the existing recovery result.
4. **Explain patterns with conversations (04):** select exact question/reply/action evidence, including behavior changes with unchanged scores. Link to recovery findings where relevant while keeping the qualitative cases separate from the quantitative recovery experiment.
5. **Prepare the six-figure narrative:** benchmark construction, behavioral patterns, semantic divergence, outcome heterogeneity, fact recovery, and conversation examples. Every plotting analysis must include a Jupyter notebook, saved outputs and source data.
6. **Keep extensions conditional:** audit matched coverage before interpreting the joint Sol comparison. Static reference, neutral paraphrases, individual-trait ablations, fresh difficulty confirmation and any new inference remain future work. The new strict SciConv baseline has no scored data.

Experiments 01, 02 and 04 reuse the same episodes, and Experiment 08 reuses a SciConv subset; do not add their counts as independent collections. The optional static reference would add 30 new episodes only if run. Operational probes and repair attempts are not independent scientific trials.

### Reporting scores and uncertainty

Present native per-benchmark scores and task-matched persona differences first. Retain the existing three-trial report's two table structures: six setting rows (off/148/155/089/001/127), benchmark or super-family columns, and mean [95% CI] with task/episode counts in each cell. Use native scores normalized to 0–100 for display: ASI score/max score, Bix correctness, Discovery final score, EXP integrity-gated reference coverage, and SciConv FRR. A common numerical range does not make these equivalent measures.

Super-family results are **task-weighted descriptive averages** of these normalized metrics, with explicit source composition and fixed source weights within each family's resampling. They are not estimates of pure field effects. Use equal benchmark weights if reporting an overall benchmark-balanced summary. Count scientific missing submissions as zero in all-attempt scores; report technical/evaluation errors separately and use a shared evaluable task set for paired comparisons, with exclusions and denominators shown. Do not silently turn errors into scientific zeros or select the best trial. Report availability across all three repeats rather than hiding incomplete task–condition cells.

The [trial-1 tables](../../runs/openai-astra-top2-first-pass/analysis/confidence_intervals.md) used 20,000 paired task-bootstrap resamples, stratified by source, with pointwise percentile 95% intervals. The [paired comparisons](../../runs/openai-astra-top2-first-pass/analysis/paired_comparisons.json) used 100,000 two-sided paired sign-flip draws and Holm correction across 27 contrasts (three condition pairs over five benchmarks and four families). No contrast reached p < 0.05 even before correction. This is insufficient evidence of a difference, not evidence of equivalence; do not write the paper as if persona performance gains are established.

Those first-pass intervals measure task-sampling variation, not repeat-run uncertainty, and do not adjust for dependence within source studies. For the final repeated analysis, average the three episodes per task/condition, retain paired baselines, report within-condition run variation, and estimate uncertainty at the source-study level with benchmark stratification. Keep the three repeats nested within their task/study; do not treat 1,800 episodes or all pairwise repeat combinations as independent tasks. Report the resampling method, cluster counts, paired-difference intervals, and correction family explicitly; three repeats alone do not guarantee narrow or reliable confidence intervals. Distinguish this final analysis from the already reported task-bootstrap interim results.

Isolated simulator-model swaps, prompt-length sweeps, and full-factorial attribute experiments remain outside the core plan. The existing Sol campaign is a joint actor/simulator extension. The paper tests whether **different simulated researchers produce repeatable collaboration patterns and whether those patterns accompany different scientific outcomes**. Behavioral differences and informative null performance results are valid outcomes. Trace evidence can support descriptive explanations; isolated trait or causal mediation claims require further controls.

### ASI implementation correction (2026-09-29)

A native evaluator transport path was found to ignore the configured judge: 24 trial-1 ASI errors came from task-level GPT-5.5/temperature defaults. The new `asi-configured-judge-v1` bridge routes both text and diagnostic-image grading through the configured controller-side Astra-low judge, without giving the sandbox credentials or network access. It preserves native prompts, rubrics, and score aggregation and records the effective settings. Apply evaluator-version filtering when combining results. Historical evaluations have not been regraded; existing trial-1 tables remain interim historical artifacts. See the [repair record](../../Experiment/02_performance_and_fields/data/asi_judge_bridge_fix.json).

## GPT-5.6 Sol comparison update (2026-09-30)

The user selected a joint actor-and-simulator comparison: GPT-5.6 Sol low for both collaborating roles, Astra low for judging. The same 200 tasks and six conditions (off, 148, 155, 089, 001, 127) have three planned trials, totaling 3,600 episodes. Saved progress now records all six batches processed, with 690 marked finished and 2,910 infrastructure failures; finished can include missing submissions. Comparative analysis is not implemented. This is not an isolated actor-model effect. See [plan](../../Experiment/_archive/20261002/03_actor_comparison/PLAN.md) and [campaign manifest](../../Experiment/_archive/20261002/03_actor_comparison/data/gpt56sol-actor-simulator-low-prioritized.json).

## Experiment 08 — SciConv fact recovery (exploratory addition)

See [experiment plan](../../Experiment/08_sciconv_fact_recovery/PLAN.md), [report](../../Experiment/08_sciconv_fact_recovery/REPORT.md), and [notebook](../../Experiment/08_sciconv_fact_recovery/analysis.ipynb). Native recovered/total deleted facts and FRR have been analyzed on the existing 20 disambiguation cases, six settings and three Astra trials. This post-hoc reanalysis retains original outcomes as primary, reports paired case/trial differences and pointwise study-cluster CIs, and includes repair and ten-question-limit sensitivities. It does not change the five-benchmark mixture or retrospectively select a favorable panel. Independent difficulty screening/confirmation, neutral paraphrases and fresh replication remain prospective. A limited post-PR6 strict persona-off baseline was attempted separately; all 20 cases failed from exhausted credits, so it contributes no scored results.
