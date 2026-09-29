# Benchmark paper plan

## Paper story

**A scientific agent should be evaluated with a range of researchers, not just one default simulated user. Researcher preferences and expertise can change how the agent asks, plans, revises, and ultimately performs.**

A generic LLM simulator can repeatedly express a similar helpful, cooperative style. Our motivation is that this narrow range of behavior leaves important collaboration patterns untested. The paper will measure whether full-profile conditioning creates a wider, repeatable range of interactions, and show what that diversity reveals about scientific agents.

The story has three steps:

1. **One default collaborator misses diversity.** Persona-conditioned researchers express different communication styles, information-sharing patterns, and expectations for proceeding.
2. **Diversity changes the work, in both directions.** The same actor can benefit from one researcher and struggle with another; the relationship can change across scientific fields and task formats.
3. **The conversations explain the difference.** Concrete exchanges show how a profile preference becomes a simulator response, how the actor reacts, and what changes in the deliverable.

The contribution is a benchmark of diverse scientific collaboration: automated task conversion, full-profile researcher simulation, and evaluation of both outcomes and interactions. Construction establishes the benchmark; the experiments supply the main story. Per-benchmark conversion rules and complete persona schemas belong mainly in the appendix and repository. The study evaluates simulated collaborator diversity; it does not require a human experiment.

The [current pilot](../../reports/full_persona_v2/README.md) supplies the starting examples: 30 personas plus persona off, ten scientific questions, and 310 finished episodes. The [trace case studies](../../reports/full_persona_v2/case_studies.md) already show useful clarification, targeted pushback, stalled approval, and language adaptation. The next study tests these patterns on a broader task panel with fewer, more informative personas.

## Experiments that carry the story

| Experiment | Question it answers | Comparison and main result |
|---|---|---|
| **1. Behavioral diversity** | Does a persona create a recognizable collaboration pattern beyond ordinary run variation? | Selected personas versus persona off on the same tasks. Compare communication, extra reviews, useful questions, and semantic trajectories. Run three independent complete episodes for every task/condition to measure variation within each condition. |
| **2. Performance and field dependence** | When does a researcher help or hinder, and does expertise match matter? | Plot each persona's score change from baseline by scientific subfield and task format. Examine domain familiarity and methodological expertise separately. Include behavior changes even when the final score stays the same. |
| **3. Actor comparison** | Which actors remain effective across different collaborators? | Three actor models on the same task/persona panel, with simulator, evaluator, tools, and budgets held fixed. Report mean performance, worst-persona performance, completion, and whether actor ordering changes across personas. |
| **4. Conversation case studies** | What actually happens between the profile and the outcome? | Two or three detailed, task-matched comparisons with short transcript excerpts: profile instruction → simulator response → actor decision → result. Explain useful and unproductive interaction patterns. |

A small **static reference** can place these results beside conventional evaluation: ten nonvisual execution/design questions, one actor, three independent episodes per question, original task context available upfront, and no simulator. Compare it with the matching neutral and persona-conditioned runs. Keep task-owned context available, evaluator answers private, and total actor budgets comparable. This is a reference setting; the main persona comparison is interactive persona off versus interactive persona on. SciConv remains an interaction task rather than being converted into a trivial full-specification copying test.

## Benchmark mixture: 200 nonvisual questions

Use **200 distinct questions**, chosen jointly by scientific subfield and the work the actor must do. Include tasks based on text, code, equations, tables, and numerical data. Exclude image interpretation, microscopy/image analysis, image reconstruction, computer vision, video, and visual-generation tasks, including experiment-design questions centered on those applications. Screen the scientific objective and required outputs as well as input-file types; an image stored as a numerical array is still an imaging task. Preserve each selected task's native deliverable and grading contract.

| Benchmark | Questions | Scientific coverage | Task and answer formats |
|---|---:|---|---|
| **DiscoveryBench** | **70** | Archaeology 12; plant ecology 10; fish evolution 8; meta-science 12; NLS health/social research 12; software requirements 8; education–GDP 4; immigration–employment 4. | Trends, associations, multivariate analysis, and evidence-backed hypothesis synthesis. |
| **BixBench** | **50** | Transcriptomics/differential expression 26; genomics/variants/phylogenetics 12; epigenomics 8; single-cell analysis 2; proteomics 2. | Numerical estimates, group comparisons, counts/rankings, and fitted-model interpretation. |
| **EXP-Bench** | **40** | LLM/code 16; RL/decision-making 8; optimization/causal methods 6; time-series 6; molecular dynamics/generation 4. | Controlled-comparison design, ablation/parameter effects, and efficiency–quality tradeoffs; design only. |
| **SciConvBench** | **36** | Nine each from fluids, PDEs, materials, and solid mechanics. | Eighteen incomplete requests and eighteen inconsistent requests; recover requirements or resolve contradictions. |
| **ASI-Bench** | **4** | Astronomy uncertainty inference, single-cell analysis, materials mode recovery, and mathematical Diophantine computation. | Implement and execute a scientific method, producing numerical artifacts. |
| **Total** | **200** | Multiple subfields, with overlap across benchmarks. | 120 empirical analyses, 40 designs, 36 specification dialogues, 4 numerical implementations. |

Discovery supplies broad field coverage; Bix adds depth in biological analysis; EXP connects methodological choices to research design; SciConv tests active clarification. ASI stays at four cases with local data and references rather than scaling up its heavier track. Replace the previous ASI image-deblurring choice with `math.sigma_linear_diophantine`. Biology appears in analysis and implementation, while physical science appears in specification, design, and implementation.

Sampling uses four task tags: **scientific subfield, operation/answer format, source study, and runtime requirements**. Spread selection across source studies, then choose different operations within each. Multiple questions from a study are allowed at this scale, but raw/processed versions of the same question count once. Assign each question one primary subfield for quota counting, with secondary tags retained. For SciConv, avoid selecting several perturbations of the same underlying case. Prefer questions outside the completed pilot; label any retained pilot anchors, such as ASI materials recovery, and show expanded-task results separately from those anchors.

These are allocation targets, not a finalized task manifest. Discovery has 207 distinct question strings across about eight source families. Bix has 124 asset-present candidates across 36 capsules after excluding the 21 Imaging-tagged cases; normalize overlapping category tags before filling quotas. EXP has sufficient nonvisual LLM, RL, optimization, time-series, and molecular-design candidates, with image-related and explicit visual-interpretation questions excluded. All four proposed ASI instances have local data/reference directories. Use the existing catalogs and readiness information to select the panel. Sources: [conversion catalogs](../../data/conversion_catalog), [EXP design catalog](../../data/design_catalog/tasks.jsonl).

### Three samples per task and condition

Interpret the three samples as **three independent complete episodes for each task × persona condition × actor**, each starting from the original task with a fresh conversation. Both actor and simulator generate a new trajectory. Score all three outputs and report their mean and within-condition variation; do not select the best answer or generate three endings from one shared conversation.

The seven conditions are six full personas plus persona off. Run the baseline three times per task and actor, then reuse that same baseline mean for all six paired persona comparisons. The 200 questions remain the task panel; the three samples measure repeat variation rather than adding new questions. This replaces the earlier proposal to repeat only a ten-question subset.

## A smaller, informative persona panel

Use **six full profiles plus persona off** for the expanded study. A proposed panel from the existing runs is:

| Persona | Why include it? |
|---|---|
| [148](../../reports/full_persona_v2/profiles/candidate_148.md) | Strong positive pilot result; medicine/statistics expertise, detail preference, and demanding approval behavior. |
| [046](../../reports/full_persona_v2/profiles/candidate_046.md) | Strong negative aggregate result but a successful Bix recovery; stepwise supervision and Spanish-language behavior. |
| [155](../../reports/full_persona_v2/profiles/candidate_155.md) | Positive result with Mandarin communication, actor language adaptation, and an agronomy background. |
| [228](../../reports/full_persona_v2/profiles/candidate_228.md) | Software/ML expertise and a speed-first preference; useful for comparing ML tasks with other scientific applications. |
| [137](../../reports/full_persona_v2/profiles/candidate_137.md) | Humanities/history expertise and a positive result; broadens the field comparison beyond computing and biomedicine. |
| [089](../../reports/full_persona_v2/profiles/candidate_089.md) | Negative result, engineering/operations background, and a “Just the gist” preference contrasting with 148's detail orientation. |

This is a purposeful panel of interesting collaborators discovered in the pilot. Retain the original 30-persona results as the broader exploratory screen. For the new panel, keep each full injected profile unchanged across tasks; actor and evaluator do not receive it. General knowledge remains available to the simulator, without persona-based domain restrictions.

### Does expertise help in its own field?

For every persona–task pair, record **direct / adjacent / outside / unknown field relationship**, supported by the actual injected profile, plus separate methodological familiarity such as statistics or coding. A domain label alone does not establish expertise: 148's cardiology and statistics background is not automatically computational-biology expertise, and 089's engineering label does not imply expertise in every mechanics problem.

For each persona, compare its **task-matched score change from persona off** in related and unrelated fields, alongside changes in questioning and supervision. Compare personas on identical tasks, and compare field effects within the same benchmark/format where coverage permits. For example: does 228 help more on ML design than on biomedical analysis, and does 148's statistical guidance transfer across fields? Show a persona × subfield heatmap with sample counts, then separate panels by workflow. Where field and format coincide, report that combination; do not fit a large factorial model to six profiles.

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

Plan **five main figures and three main tables**. Their order follows construction → behavioral diversity → field-dependent outcomes → actor comparison → explanatory cases. Experiment numbers below refer to the four experiments above.

| Item | What we want to show | Data required | Experiment dependency / what can be prepared now |
|---|---|---|---|
| **Figure 1 — Benchmark overview** | How scientific tasks become collaborations, where the persona enters, and how outcomes and behavior are evaluated. | Conversion rules, public/researcher/evaluator context, simulator–actor workflow, native grading contracts. | Construction only. Draft now; update counts for the selected 200-task panel. |
| **Table 1 — Task coverage** | Breadth across scientific subfields and formats, with source-study counts so many questions from one study are visible. | Final task IDs, benchmark, subfield, format, source family, and nonvisual eligibility. | Task selection. The allocation above is the draft; final counts require the 200-question manifest. |
| **Table 2 — Six simulated researchers** | The concrete differences represented by the panel: scientific background, methodological familiarity, communication/workflow preferences, and language. | Existing full profiles, two or three relevant attributes per profile, links to exact injected prompts. | Persona construction. Can complete now without new runs. |
| **Figure 2 — Behavioral diversity and repeat variation** | Whether personas produce distinct, recurring patterns of useful questioning, extra reviews, revisions, repetition, and communication. | Event counts, native SciConv metrics, message lengths/languages, all three samples for each condition. | **Experiment 1.** Pilot supports a prototype; the expanded first-actor study supplies broad coverage and within-condition variation. Keep SciConv questioning separate from required-review workflows. |
| **Figure 3 — Conversation trajectories** | When simulator messages diverge and whether that divergence appears in the actor's responses. | Role-separated shared messages, aligned stages, fixed multilingual embeddings, matched baseline runs and repetitions. | **Experiment 1.** Prototype from pilot traces; final averages and repeat-reference distributions use the expanded study. Method below. |
| **Figure 4 — Helpful here, hindering elsewhere** | How each persona's performance change varies across subfields, task formats, and expertise relationships. | Three-sample mean native scores, paired baseline means, field/format tags, persona–field relationships, task and study counts. | **Experiment 2.** Requires expanded first-actor results for the main persona × subfield heatmap; add workflow panels. Pilot provides motivating examples. |
| **Table 3 — Actor performance across researchers** | Which actors maintain performance and completion across the selected collaborators, and whether their ordering changes with persona. | The same 200 tasks × seven conditions × three samples for all three actors; native benchmark scores, completion, and fixed aggregation weights. | **Experiment 3.** Requires the additional actors. Report native scores, balanced overall mean, persona–baseline change, and worst-persona performance with uncertainty. |
| **Figure 5 — Conversations that explain the results** | A visible chain from profile wording to simulator utterance, actor action, and outcome. Include two or three helpful, unproductive, or behavior-changing examples. | Exact profiles, short event-linked excerpts, corresponding baseline, submitted work, and native scores. | **Experiment 4.** Can draft now from the case-study report; expanded runs can supply further instances. No edited-reply interventions required. |

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

Promising examples from the current traces are:

- **Completeness and task recovery:** 148's “Every detail” preference, its broad SciConv answer, and the actor's incorporation of missing geometry and boundaries. Contrast with an incomplete symbolic deliverable, while distinguishing what the actor asked from what the simulator volunteered.
- **When pushback helps or stalls:** 046's “Step-by-step pair programming” preference and targeted Bix inspection that resolves a column mismatch; contrast with 148 withholding approval on an unreadable workbook. The first produces a usable answer; the second exposes a protocol bottleneck.
- **Language changes the collaboration:** 155's Mandarin instruction, the actor switching language, and the extra question about the final answer's language; 046 supplies a Spanish comparison.

Bring these snippets into the discussion rather than leaving all evidence in the appendix. Include the difficult examples: a high-scoring persona can stall a workflow, and a low-scoring persona can rescue a task. Describe observed mechanisms and profile alignment without requiring edited replies, checkpoint interventions, or a new ablation campaign. Detailed evidence is already linked in the [case-study report](../../reports/full_persona_v2/case_studies.md).

## What comes next

1. **Prepare the presentation from existing material:** draft Figure 1, Table 2, and Figure 5; prototype the behavioral and trajectory figures from pilot traces. Complete Table 1 as the 200 nonvisual questions are selected.
2. **Run all three samples of the first actor's panel:** 200 questions × seven conditions × three independent episodes = **4,200 episodes**. This includes 3,600 persona-on episodes and 600 baseline episodes. Keep the full-profile injection and run independent episodes in parallel.
3. **Repeat the same panel with two additional actors:** **8,400 additional episodes**, giving **12,600 main-study episodes** across three actors. Populate the actor-comparison table from this shared panel. No separate repeat-subset phase is needed.

The optional static reference adds ten questions × three episodes × one actor = **30 episodes**, for **12,630 total** if included. These are full interaction episodes, not individual API calls or judge samples.

Present per-benchmark outcomes and task-matched differences first; use equal benchmark weights for an overall summary. Estimate uncertainty at the source-study level, retain paired baselines, and separate technical failures from scientific outcomes. Simulator-model swaps, prompt-length sweeps, and full-factorial attribute experiments are not part of the core plan.

The paper's main sequence is **diverse simulated researchers → different collaboration patterns → field-dependent help and hindrance → actors that handle this diversity differently**. Every experiment and figure should advance that sequence.
