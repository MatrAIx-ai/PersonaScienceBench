# Benchmark paper plan

Implementation, per-experiment plans, status snapshots, and derived artifacts are tracked in the [Experiment workspace](../../Experiment/README.md).

## Expansion to the ten largest absolute pilot changes (2026-09-29)

The user selected the ten largest **absolute changes from persona off**, not the ten highest scores. In ranked order these are **046, 003, 004, 089, 001, 127, 262, 224, 148, 026**. This outcome-selected panel includes both positive and negative pilot deviations. Persona 148 already belongs to the original expanded campaign; persona 155 remains an additional comparison outside this top-ten set.

Run the other **nine personas × 200 frozen tasks × three trials = 5,400 new episodes**. Reuse the corresponding trial's persona-off baseline and the existing 148 episodes; no new baseline or 148/155 episodes are scheduled by this expansion. The top-ten-plus-baseline panel therefore contains **6,600 episodes**; including the retained 155 condition gives **7,200 total planned episodes**. This supersedes the two-persona-only scope for the expanded persona panel; sections describing the 1,800-episode campaign remain provenance for its initial phase.

The scientific setting remains GPT-6 Astra low, the same frozen inputs, full profiles, tools, grading, and budgets. New jobs use 128 GB RAM, 30 CPUs, and up to 30 concurrent episodes. To avoid overlapping API load, nine 600-episode batches form an `afterany` chain after resumed trial 3 (job 1964348). Groups are [046, 003, 004], [089, 001, 127], and [262, 224, 026], repeated for trials 1–3. `afterany` enforces non-overlap but does not certify successful completion; errors remain visible for later repair.

The [expansion manifest](../../runs/openai-astra-top10-expansion.json) records jobs, dependencies, exact profile hashes, run directories, and matching baseline references. The [submission entry point](../../scripts/submit_top10_expansion.py) submits prepared batches idempotently; the coordinator's `--baseline-run` verifies task/model/settings compatibility. The first job is 1964501; the final job is 1964513. Additional actor models and the static reference remain unsubmitted.

Extend behavioral and outcome analyses to this named panel without choosing personas again from expanded-study scores. Keep 155 separately labeled, disclose pilot selection and overlap, and predefine the multiple-comparison family for the expanded analysis. Existing three-condition interim tables are unchanged historical results. Expanded multi-batch aggregation is still to be implemented; the current three-arm CI script must not be used as if it covers all ten personas.

## Paper story

**A scientific agent should be evaluated with a range of researchers, not just one default simulated user. Researcher preferences and expertise can change how the agent asks, plans, revises, and ultimately performs.**

A generic LLM simulator can repeatedly express a similar helpful, cooperative style. Our motivation is that this narrow range of behavior leaves important collaboration patterns untested. The paper will measure whether full-profile conditioning creates a wider, repeatable range of interactions, and show what that diversity reveals about scientific agents.

The story has three steps:

1. **One default collaborator misses diversity.** Persona-conditioned researchers express different communication styles, information-sharing patterns, and expectations for proceeding.
2. **Diversity changes the work, in both directions.** The same actor can benefit from one researcher and struggle with another; the relationship can change across scientific fields and task formats.
3. **The conversations explain the difference.** Concrete exchanges show how a profile preference becomes a simulator response, how the actor reacts, and what changes in the deliverable.

The contribution is a benchmark of diverse scientific collaboration: automated task conversion, full-profile researcher simulation, and evaluation of both outcomes and interactions. Construction establishes the benchmark; the experiments supply the main story. Per-benchmark conversion rules and complete persona schemas belong mainly in the appendix and repository. The study evaluates simulated collaborator diversity; it does not require a human experiment.

The [current pilot](../../reports/full_persona_v2/README.md) supplies the starting examples: 30 personas plus persona off, ten scientific questions, and 310 finished episodes. The [trace case studies](../../reports/full_persona_v2/case_studies.md) already show useful clarification, targeted pushback, stalled approval, and language adaptation. The current expanded study tests these patterns on 200 source-balanced tasks with the two highest-scoring profiles from that pilot, 148 and 155, plus persona off. This outcome-selected panel studies promising collaborators; it does not represent the full range of personas or establish that these profiles are optimal on new tasks.

## Experiments that carry the story

| Experiment | Question it answers | Comparison and main result |
|---|---|---|
| **1. Behavioral diversity** | Does a persona create a recognizable collaboration pattern beyond ordinary run variation? | Selected personas versus persona off on the same tasks. Compare communication, extra reviews, useful questions, and semantic trajectories. Run three independent complete episodes for every task/condition to measure variation within each condition. |
| **2. Performance and field dependence** | When does a researcher help or hinder, and does expertise match matter? | Plot each persona's score change from baseline by scientific subfield and task format. Examine domain familiarity and methodological expertise separately. Include behavior changes even when the final score stays the same. |
| **3. Actor comparison** | Which actors remain effective across different collaborators? | Proposed extension: three actor models on the same task/persona panel, with simulator, evaluator, tools, and budgets held fixed. The current campaign runs one actor, GPT-6 Astra. Report mean performance, worst-persona performance, completion, and whether actor ordering changes across personas. |
| **4. Conversation case studies** | What actually happens between the profile and the outcome? | Two or three detailed, task-matched comparisons with short transcript excerpts: profile instruction → simulator response → actor decision → result. Explain useful and unproductive interaction patterns. |

A small **static reference** can place these results beside conventional evaluation: ten nonvisual execution/design questions, one actor, three independent episodes per question, original task context available upfront, and no simulator. Compare it with the matching neutral and persona-conditioned runs. Keep task-owned context available, evaluator answers private, and total actor budgets comparable. This is a reference setting; the main persona comparison is interactive persona off versus interactive persona on. SciConv remains an interaction task rather than being converted into a trivial full-specification copying test.

## Current execution setting

The frozen configuration is **200 tasks × three conditions × three independent complete episodes = 1,800 episodes** for one actor. The conditions are **persona off, candidate_148, and candidate_155**. Actor, researcher simulator, and model-based evaluator all use **direct OpenAI Responses API, `gpt-6-astra`, reasoning effort `low`**. Astra does not support the originally requested `none`; `low` was explicitly selected instead. Native non-model evaluators remain in place.

Keep the exact full persona profiles private to the researcher simulator; neither actor nor evaluator receives them. General knowledge is available to the simulator in all conditions. Execution/design tracks use the existing active-researcher protocol, mandatory approach/result review, a 12-request collaboration limit, and a 60-call actor budget. SciConv retains its native clarification workflow with up to ten dialogue turns. Retain the existing per-role output limits and native grading contracts, including EXP's three judge repetitions; judge repetitions are not independent episode trials.

Each trial requests **128 GB RAM, 30 CPUs, and a 12-hour Slurm allocation**, with up to **30 concurrent episode processes**. Scientific BLAS/OpenMP threads are limited to one. Run actual episodes without a separate smoke-test campaign; intrinsic runtime startup checks remain. Entry points: [run coordinator](../../scripts/run_openai_first_pass.py), [submission script](../../scripts/submit_openai_first_pass.sh), and [run instructions](../../scripts/OPENAI_FIRST_PASS.md).

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

## Two selected personas plus persona off

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
| **Does feedback change the work?** | Specific suggestions adopted, rejected, or unresolved; resulting changes in method, assumptions, or final answer. | Evidence-backed annotation of case studies, linking the simulator message to the actor's later action. |
| **Is the behavior connected to the profile?** | Expression or contradiction of two or three relevant, observable preferences per selected persona. | Read the exact profile alongside trace excerpts; use a short frozen rubric, with “not applicable” where the task offers no opportunity. |

The first four rows give the main quantitative behavioral results; the last two explain them. Broad claims such as “all new scientific advice is correct” or “information gain at every turn” would require costly, uncertain judging and are not core metrics. For semantic annotations, retain event IDs and excerpts, hide outcome scores from the annotator, and check a small subset with a second judge. This uses existing traces rather than a new instrumentation phase.

### What SciConv already tells us about proactivity

There is no single native proactivity score, but the [current runner](../../src/personasciencebench/sciconv_runner.py) already exports:

- **Clarification recall:** missing entities or inconsistencies asked about / total annotated issues.
- **Clarification precision:** relevant question turns / all question turns.
- **FRR:** final resolution with intent preserved; **CGRR:** successful resolution grounded in the conversation; **SRR:** successful resolution without sufficient conversational grounding. FRR = CGRR + SRR.
- **Memory consistency and intent capture:** whether the final specification retains supplied information and the intended task.

Together, these distinguish asking more from asking usefully, and resolving through dialogue from resolving silently. The counts are judge-derived; retain their evidence and flag inconsistent counts when analyzing them. Use the exported coverage/relevance fields rather than treating every upstream `CR`/`CP` alias as the same definition.

The actor's first SciConv question occurs before it receives a persona-conditioned reply, so changes in activity attributable to that reply must be examined afterward. In the other four tracks, the [controller](../../src/personasciencebench/collaboration.py) requires plan/result handoffs: extra review requests measure simulator activity, while questions and proposals inside actor handoffs measure actor initiative. These are separate quantities.

## Figures and tables: purpose and dependencies

Plan **five main figures and three main tables**, with the actor-comparison table conditional on the proposed additional-actor extension. Their order follows construction → behavioral diversity → field-dependent outcomes → actor comparison → explanatory cases. Experiment numbers below refer to the four experiments above.

| Item | What we want to show | Data required | Experiment dependency / what can be prepared now |
|---|---|---|---|
| **Figure 1 — Benchmark overview** | How scientific tasks become collaborations, where the persona enters, and how outcomes and behavior are evaluated. | Conversion rules, public/researcher/evaluator context, simulator–actor workflow, native grading contracts. | Construction only. Draft now; use the frozen 40-per-source, 200-task panel. |
| **Table 1 — Task coverage** | Breadth across scientific subfields and formats, with source-study counts so many questions from one study are visible. | Final task IDs, benchmark, subfield, format, source family, and nonvisual eligibility. | Task selection. Use the frozen manifest and distinguish full-panel counts from matched evaluable counts. |
| **Table 2 — Two simulated researchers and baseline** | The concrete differences represented by the panel: scientific background, methodological familiarity, communication/workflow preferences, and language. | Existing full profiles, two or three relevant attributes per profile, links to exact injected prompts. | Persona construction. Can complete now without new runs. |
| **Figure 2 — Behavioral diversity and repeat variation** | Whether personas produce distinct, recurring patterns of useful questioning, extra reviews, revisions, repetition, and communication. | Event counts, native SciConv metrics, message lengths/languages, all three samples for each condition. | **Experiment 1.** Pilot supports a prototype; the expanded first-actor study supplies broad coverage and within-condition variation. Keep SciConv questioning separate from required-review workflows. |
| **Figure 3 — Conversation trajectories** | When simulator messages diverge and whether that divergence appears in the actor's responses. | Role-separated shared messages, aligned stages, fixed multilingual embeddings, matched baseline runs and repetitions. | **Experiment 1.** Prototype from pilot traces; final averages and repeat-reference distributions use the expanded study. Method below. |
| **Figure 4 — Helpful here, hindering elsewhere** | How each persona's performance change varies across subfields, task formats, and expertise relationships. | Three-sample mean native scores, paired baseline means, field/format tags, persona–field relationships, task and study counts. | **Experiment 2.** Requires expanded first-actor results for the main persona × subfield heatmap; add workflow panels. Pilot provides motivating examples. |
| **Table 3 — Actor performance across researchers** | Which actors maintain performance and completion across the selected collaborators, and whether their ordering changes with persona. | The same 200 tasks × three conditions × three samples for each actor; native benchmark scores, completion, and fixed aggregation weights. | **Experiment 3 (proposed extension).** Current runs cover only GPT-6 Astra; requires two additional actors. Report native scores, balanced overall mean, persona–baseline change, and worst-persona performance with uncertainty. |
| **Figure 5 — Conversations that explain the results** | A visible chain from profile wording to simulator utterance, actor action, and outcome. Include two or three helpful, unproductive, or behavior-changing examples. | Exact profiles, short event-linked excerpts, corresponding baseline, submitted work, and native scores. | **Experiment 4.** Use expanded 148/155 traces for the current panel; earlier 046 examples may appear only as clearly labeled exploratory-pilot evidence. No edited-reply interventions required. |

**Supplementary material:** (1) the full task/source manifest and conversion contracts, derived from task selection; (2) exact profiles/prompts and original 30-persona selection provenance, already available; (3) all three-sample outcomes and behavioral results by task/persona/actor, dependent on Experiments 1–3; (4) metric definitions, semantic annotation rubric and evidence excerpts, dependent on trace analysis; and (5) extended case-study transcripts supporting Figure 5. If the optional static reference is run, include its paired outcome/behavior table here. These support the main story without adding another experiment campaign.

### Figure 3: how conversations diverge from start to finish

Use the same scientific questions as controls and display simulator and actor trajectories separately:

1. Embed shared messages with one fixed multilingual encoder. Exclude persona system prompts, copied task setup, private tool output, and judge text. Use stage-specific text rather than a growing transcript prefix.
2. Align review workflows by initial request, approach, result, and conclusion. Give SciConv its own panel aligned by dialogue progress. Missing stages remain missing, with contributing episode counts shown.
3. For each task, role, and stage, average embeddings over the three runs of each condition. Subtract the corresponding three-run persona-off mean, then average the task-matched differences by persona over a common task set.
4. Project the average paths with one shared PCA. Add a companion distribution of distances in the original embedding space: persona–baseline distances versus distances between independent baseline runs, using the same task, role, and stage. Keep task/source study as the unit for uncertainty rather than treating every pair of runs as independent.

Label language and show within-field and same-language views where possible. Pair trajectories with Figure 2's concrete behavior measures: a semantic change may reflect language, elaboration, or a different plan. The paths show divergence; the transcript excerpts explain its meaning. Embedding distance is not a performance or fidelity score.

## Discussion: show the actual conversations

Use two or three compact case-study panels. Each should contain the relevant **profile wording**, two to four short **actor/simulator excerpts**, the **actor's subsequent action**, and the **task outcome**, alongside the matching baseline.

Historical examples from the exploratory pilot are listed below. Use fresh 148/155 examples for the expanded study where available; any 046 or other out-of-panel comparison must be labeled as pilot evidence:

- **Completeness and task recovery:** 148's “Every detail” preference, its broad SciConv answer, and the actor's incorporation of missing geometry and boundaries. Contrast with an incomplete symbolic deliverable, while distinguishing what the actor asked from what the simulator volunteered.
- **When pushback helps or stalls:** 046's “Step-by-step pair programming” preference and targeted Bix inspection that resolves a column mismatch; contrast with 148 withholding approval on an unreadable workbook. The first produces a usable answer; the second exposes a protocol bottleneck.
- **Language changes the collaboration:** 155's Mandarin instruction, the actor switching language, and the extra question about the final answer's language; 046 supplies a Spanish comparison.

Bring these snippets into the discussion rather than leaving all evidence in the appendix. Include the difficult examples: a high-scoring persona can stall a workflow, and a low-scoring persona can rescue a task. Describe observed mechanisms and profile alignment without requiring edited replies, checkpoint interventions, or a new ablation campaign. Detailed evidence is already linked in the [case-study report](../../reports/full_persona_v2/case_studies.md).

## Analysis and what comes next

1. **Complete the three-trial, first-actor campaign:** 200 questions × three conditions × three independent episodes = **1,800 episodes**: 1,200 persona-on and 600 persona-off episodes. Trial 1 is processed; trials 2 and 3 have been submitted. Preserve error records and diagnose technical failures separately from scientific outcomes.
2. **Analyze behavior as well as performance:** populate the benchmark and super-family score tables, paired differences, completion rates, and within-condition variation. Extract questioning, review/revision counts, visible-message lengths, language adaptation, and role-separated trajectories from the same saved episodes. The current panel supports Experiments 1, 2, and 4.
3. **Prepare the presentation:** update Figure 1 and Tables 1–2 from the frozen configuration; build Figures 2–4 from the repeated trials; choose two or three evidence-linked 148/155 case studies for Figure 5. Keep pilot-only examples explicitly labeled.
4. **Proposed additional-actor extension:** repeat this same panel with two more actor models, changing only the actor and keeping the Astra-low researcher/evaluator, tools, and budgets fixed. This would add **3,600 episodes**, for **5,400 across three actors**, and enable Experiment 3. These additional actors are not part of the currently submitted jobs.

The optional static reference remains ten questions × three episodes × one actor = **30 episodes**. It would bring the current single-actor study to **1,830**, or the proposed three-actor study to **5,430**. All counts refer to complete episodes, not API calls or judge repetitions.

### Reporting scores and uncertainty

Present native per-benchmark scores and task-matched persona differences first. Retain the current table columns: benchmark or super-family, task count, persona off, persona 148, persona 155; report mean and 95% confidence interval in each score cell. Use native scores normalized to 0–100 for display: ASI score/max score, Bix correctness, Discovery final score, EXP integrity-gated reference coverage, and SciConv FRR. A common numerical range does not make these equivalent measures.

Super-family results are **task-weighted descriptive averages** of these normalized metrics, with explicit source composition and fixed source weights within each family's resampling. They are not estimates of pure field effects. Use equal benchmark weights if reporting an overall benchmark-balanced summary. Count scientific missing submissions as zero in all-attempt scores; report technical/evaluation errors separately and use a shared evaluable task set for paired comparisons, with exclusions and denominators shown. Do not silently turn errors into scientific zeros or select the best trial. Report availability across all three repeats rather than hiding incomplete task–condition cells.

The [trial-1 tables](../../runs/openai-astra-top2-first-pass/analysis/confidence_intervals.md) used 20,000 paired task-bootstrap resamples, stratified by source, with pointwise percentile 95% intervals. The [paired comparisons](../../runs/openai-astra-top2-first-pass/analysis/paired_comparisons.json) used 100,000 two-sided paired sign-flip draws and Holm correction across 27 contrasts (three condition pairs over five benchmarks and four families). No contrast reached p < 0.05 even before correction. This is insufficient evidence of a difference, not evidence of equivalence; do not write the paper as if persona performance gains are established.

Those first-pass intervals measure task-sampling variation, not repeat-run uncertainty, and do not adjust for dependence within source studies. For the final repeated analysis, average the three episodes per task/condition, retain paired baselines, report within-condition run variation, and estimate uncertainty at the source-study level with benchmark stratification. Keep the three repeats nested within their task/study; do not treat 1,800 episodes or all pairwise repeat combinations as independent tasks. Report the resampling method, cluster counts, paired-difference intervals, and correction family explicitly; three repeats alone do not guarantee narrow or reliable confidence intervals. Distinguish this final analysis from the already reported task-bootstrap interim results.

Simulator-model swaps, prompt-length sweeps, and full-factorial attribute experiments remain outside the core plan. The paper tests whether **different simulated researchers produce repeatable collaboration patterns, whether those patterns affect outcomes across fields, and—if the additional-actor extension is run—whether actors respond differently**. Behavioral differences and informative null performance results are valid outcomes; every claimed mechanism must be supported by the recorded conversations.

### ASI implementation correction (2026-09-29)

A native evaluator transport path was found to ignore the configured judge: 24 trial-1 ASI errors came from task-level GPT-5.5/temperature defaults. The new `asi-configured-judge-v1` bridge routes both text and diagnostic-image grading through the configured controller-side Astra-low judge, without giving the sandbox credentials or network access. It preserves native prompts, rubrics, and score aggregation and records the effective settings. Apply evaluator-version filtering when combining results. Historical evaluations have not been regraded; existing trial-1 tables remain interim historical artifacts. See the [repair record](../../Experiment/02_performance_and_fields/data/asi_judge_bridge_fix.json).
