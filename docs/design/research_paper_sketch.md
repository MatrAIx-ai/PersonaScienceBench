# PersonaScienceBench: Research Paper Sketch

Draft for review · 2026-09-24 · No human experiments

**Working title:** *PersonaScienceBench: Evaluating Scientific Agents with Expertise-Conditioned Researcher Simulation*

## Positioning
Comments: I would like the whole paper to be more like agentic llm paper. Somehow more technical.
An LLM benchmark paper about scientific collaboration across domains and researcher expertise levels.

**Central hypothesis:** Grounded researcher simulation exposes collaboration capabilities and failures that static scientific benchmarks leave unmeasured.

Simulation represents explicit collaboration constraints: obtaining context, interpreting answers, and adapting to different researcher profiles. Without human experiments, we do not claim that the simulator reproduces human behavior or predicts real-world outcomes.

## Contributions

- A standard for converting scientific tasks into interactive evaluations while preserving objectives, essential instructions, information boundaries, and grading. (Comments: I do not think this is a contribution but we can say that a selected compilation of comprehensive task across scientific domain, task format, and agent workflow for LLM agent doing science.)
- Controlled researcher profiles with identical approved study facts and independently configurable domain, coding, and statistics expertise.
- A comparison of LLM agents across scientific performance, collaboration behavior, and sensitivity to researcher profiles.

## Experiments

| Experiment | Design | Main question |
| --- | --- | --- |
| Model comparison | Multiple actor models; neutral, novice, intermediate, and expert researchers; fixed tools and budgets; repeated runs. | Which agents perform consistently across tasks and researcher expertise? (comment: I think this is too broad, and overlapped ths 3 in this table. I think this can just be persona-off test models' perf across the tasks.) |
| Value of interaction | Original static task; all approved facts upfront; structured fact oracle; neutral simulator; expertise-conditioned simulator. | What comes from extra information, interactive information gathering, and collaborator behavior? (comments: I think this is good, Inverstigating the connection between persona and behavior level  of LLMs. there should be some quantities that support the "behavior".  Like number of interactions and number of questions beeing asked lenght of questions and etc this sounds more like a case study level answering what are the persona's connections to llms agent when doing scientific tasks.)|
| Expertise ablations | Vary domain expertise while holding coding, statistics, facts, and other attributes fixed; separately test style, behavioral rules, and domain mismatch. | Which aspects of researcher variation affect performance? (comments: this is good this is more like a connection between different persona vs performance level on agentic tasks) |
| Simulator robustness | Repeat a representative subset with a second simulator model, equivalent profile wording, and independent judging where applicable. | Do score differences and model comparisons survive implementation changes? |
| Simulator audit | Check factual support, private-reference leakage, profile adherence, and response constraints. | Is the evaluation internally consistent and grounded? (comments: fine but not interesting and very trivial and hard to measure)|

Include fully specified tasks as controls. Questions remain optional; do not hide essential requirements to manufacture interaction. **Persona off still includes the simulator.**

Define expertise through explicit response rules, such as terminology, explanation depth, and clarification behavior. These are experimental assumptions, not validated human profiles. A novice can know their own study's facts.

## Evaluation

- **Primary:** native scientific task scores, reported separately by benchmark.
- **Secondary:** valid submissions, relevant facts obtained, unsupported assumptions, use of researcher answers, unnecessary questions, and interaction/compute cost.
- Report uncertainty and paired comparisons, accounting for tasks that share a source study. Repeated runs are not independent tasks.
- Keep infrastructure failures distinct from scientific failures and missing submissions.

Fewer questions alone does not establish better collaboration. Hidden persona cannot affect behavior before the first simulator reply; distinguish initial question decisions from subsequent adaptation.

## Scope and Next Steps

Current setup: five benchmark tracks, 25 converted cases, and a single actor-model pilot. EXP-Bench remains design-only; the 1,102 source units are not all converted.

1. Target roughly 100 reviewed cases across the five tracks, stratified by domain and source study.
2. Pilot neutral and task-domain-matched expertise profiles; audit simulator behavior and estimate run cost and variability.
3. Evaluate 4–6 actor models with repeated runs, then run information-access controls and robustness ablations. Final scale depends on pilot evidence and budget.

**Paper order:** motivation → benchmark construction → simulation protocol → main model results → interaction and expertise ablations → robustness and limitations.

**Success criterion:** reproducible differences in scientific collaboration that static scores do not reveal. Realism remains a motivation and an unvalidated property, not an empirical conclusion.

Comments: I think in general it is good, but still kind of in the air. A key designing is missing but very crucial is that how the current tasks's domain can be partitioned/segemented and how the persona profiles can be segemented to cleanly 
support our experiment. 