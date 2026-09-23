# Benchmark candidates

Candidate benchmarks for PersonaScienceBench: existing science-agent benchmarks that could be adapted so that a simulated researcher steers an evolving, multi-turn collaboration with the agent.

All benchmarks below support scientific execution or analysis over multiple steps. None of their standard evaluations include an adaptive researcher simulator. Their existing agent-tool interactions (the agent calling code, notebooks or a terminal) should be kept separate from user-agent conversation (the researcher talking to the agent).

## Summary

| Benchmark | Domain | Recommendation | Main limitation |
|---|---|---|---|
| [BixBench](#bixbench) | Computational biology | Very high: best first pilot | Check that each capsule's questions form one coherent investigation |
| [BixBench3](#bixbench3) | Computational biology | Very high: strongest full-project fit | About 8 hours per run on average; heavy setup |
| [sc-HeurekaBench](#sc-heurekabench) | Single-cell biology | Very high: good for analysis-interpretation dialogue | Reference-insight scoring misses valid alternative directions |
| [AstaBench: E2E-Bench / E2E-Bench-Hard](#astabench-e2e-bench--e2e-bench-hard) | Computational research | Very high conceptually: ambitious target | More implementation and evaluation work than a bounded pilot |
| [DiscoveryBench](#discoverybench) | Biology, social sciences, economics, other | High: exploratory collaboration across domains | Grading must be extended if the conversation goes beyond the reference finding |
| [PaperBench](#paperbench) | Machine learning research | High: sustained research collaboration | Reproduction is narrower than open-ended discovery; can be expensive |
| [MLRC-Bench](#mlrc-bench) | Machine learning research | High: iterative experiment design | Final performance must be supplemented with reasoning and collaboration assessment |
| [Terminal-Bench-Science](#terminal-bench-science) | Life, physical, Earth, mathematical, engineering sciences | High for selected tasks; medium overall | Some tasks would become artificially prolonged conversations |
| [ScienceAgentBench](#scienceagentbench) | Bioinformatics, chemistry, GIS, psychology/neuroscience | Medium to high | Many instances are bounded implementation tasks |
| [SciAgentArena](#sciagentarena) | Biomedical research | Medium to high, pending task-level selection | Diverse tasks do not automatically form connected project trajectories |

Each entry below has four parts:

- **Existing task and unit to adapt**: what the benchmark asks today, and which piece of it becomes one collaboration.
- **How the researcher could steer**: an example path the simulated researcher could take.
- **Evaluation to reuse**: grading that already exists, and what must be added.
- **Recommendation and main limitation**.

---

## BixBench

**Domain:** computational biology

**Existing task and unit to adapt:** Analyze biological datasets using notebooks. Adapt a whole capsule with its related questions, not an isolated question. Current repository: 60 capsules, 205 questions.

**How the researcher could steer:** Start with data inspection. Request an analysis. Examine the resulting plot. Ask for an explanation, a subgroup comparison or a robustness check. Synthesize conclusions.

**Evaluation to reuse:** Existing question-level answers and graders. Saved notebooks provide evidence of execution. Add project-level and interaction assessment.

**Recommendation:** Very high: best first pilot. Shared data and related questions provide a natural project foundation.

**Main limitation:** Check that each selected capsule's questions actually form a coherent investigation.

## BixBench3

**Domain:** computational biology

**Existing task and unit to adapt:** Reproduce research-scale analyses from raw data; 20 study-scale tasks. Adapt one study.

**How the researcher could steer:** Progress through preprocessing, quality control, analysis, interpretation and artifact production. Let observed results decide whether to revise methods or proceed.

**Evaluation to reuse:** Deterministic grading of structured artifacts, plus process assessment.

**Recommendation:** Very high: strongest full-project fit.

**Main limitation:** Substantial execution cost and setup. The supplied runner reports about eight hours per run on average.

## sc-HeurekaBench

**Domain:** single-cell biology

**Existing task and unit to adapt:** Answer exploratory research questions grounded in published studies, datasets and code. Adapt one open-ended investigation, optionally grouping related questions from the same study.

**How the researcher could steer:** Interpret cell populations. Investigate an unexpected pattern. Discuss competing biological explanations. Choose and execute a follow-up analysis.

**Evaluation to reuse:** Reference scientific insights and existing answer-quality grading. Add checks that claims follow from executed analyses.

**Recommendation:** Very high, especially good for analysis-interpretation dialogue.

**Main limitation:** Reference-insight scoring alone does not fully evaluate scientifically valid alternative directions.

## AstaBench: E2E-Bench / E2E-Bench-Hard

**Domain:** computational research

**Existing task and unit to adapt:** Design and run software experiments, analyze results and write up findings. Adapt one end-to-end research task.

**How the researcher could steer:** Brainstorm an approach. Choose an experiment. Review outcomes. Request another experiment or a methodological revision. Develop the final report.

**Evaluation to reuse:** Existing task evaluation and execution infrastructure. Supplementary dialogue assessment is needed.

**Recommendation:** Very high conceptually: a strong ambitious target. Select the E2E components specifically; do not treat all AstaBench tasks alike.

**Main limitation:** More implementation and evaluation work than a bounded analysis pilot.

## DiscoveryBench

**Domain:** biology, social sciences, economics and other domains

**Existing task and unit to adapt:** Discover relationships in data through loading, transformation, statistical analysis and modeling. Adapt one dataset-centered investigation.

**How the researcher could steer:** Explore variables. Propose explanations. Choose a statistical test. Discuss confounding. Refine a hypothesis after seeing results.

**Evaluation to reuse:** Existing hypothesis / reference-finding evaluation.

**Recommendation:** High: strong for exploratory collaboration across domains.

**Main limitation:** Preserve a core objective, or extend grading when the conversation pursues findings beyond the reference.

## PaperBench

**Domain:** machine learning research ([link](https://openai.com/index/paperbench/))

**Existing task and unit to adapt:** Reproduce a research paper from its description. Adapt one paper or one coherent experimental section.

**How the researcher could steer:** Discuss the method. Implement a baseline. Inspect reproduction discrepancies. Prioritize debugging or ablations. Consolidate results.

**Evaluation to reuse:** Detailed hierarchical reproduction rubrics.

**Recommendation:** High for sustained research collaboration. Excellent project structure.

**Main limitation:** Reproduction is narrower than open-ended discovery and can be expensive.

## MLRC-Bench

**Domain:** machine learning research

**Existing task and unit to adapt:** Develop and implement methods for research challenges. Adapt one challenge.

**How the researcher could steer:** Brainstorm methods. Select a baseline. Inspect performance. Propose changes. Run ablations. Explain what the experiments support.

**Evaluation to reuse:** Challenge-specific performance metrics and baseline comparisons.

**Recommendation:** High for iterative experiment design.

**Main limitation:** Final performance needs to be supplemented with assessment of scientific reasoning and collaboration.

## Terminal-Bench-Science

**Domain:** life, physical, Earth, mathematical and engineering sciences

**Existing task and unit to adapt:** Execute scientific tasks in terminal environments. Adapt selected substantial analysis or simulation workflows.

**How the researcher could steer:** Establish assumptions. Run an initial computation. Explain an anomaly. Revise parameters or methods. Produce the required scientific artifacts.

**Evaluation to reuse:** Task-specific artifact verifiers and execution environments.

**Recommendation:** High for selected tasks; medium for the collection overall.

**Main limitation:** Some tasks offer rich project structure; others would become artificially prolonged conversations.

## ScienceAgentBench

**Domain:** bioinformatics, chemistry, GIS, psychology/neuroscience

**Existing task and unit to adapt:** Produce working scientific analysis programs. Adapt a substantial workflow, or scientifically connected tasks that share data and objectives.

**How the researcher could steer:** Inspect inputs. Agree on an analysis. Implement it. Review outputs. Refine assumptions or visualizations. Interpret findings.

**Evaluation to reuse:** Existing program/output checks, with task-dependent evaluation.

**Recommendation:** Medium to high: useful, but lower than the earlier recommendation.

**Main limitation:** Many instances are bounded implementation tasks. They need extra project framing to support meaningful researcher steering.

## SciAgentArena

**Domain:** biomedical research

**Existing task and unit to adapt:** Biomedical analysis, optimization and discovery across several domains. Adapt a selected complex task or an expert-curated group of related tasks.

**How the researcher could steer:** Review data quality. Select an analysis. Discuss biological interpretation. Request validation or an alternative analysis.

**Evaluation to reuse:** Domain-specific metrics and verification.

**Recommendation:** Medium to high, pending task-level selection.

**Main limitation:** A diverse collection of tasks does not automatically provide connected project trajectories.
