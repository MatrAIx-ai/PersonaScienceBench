# PersonaChatBench, PersonaCodeBench and PersonaCUABench versus PersonaScienceBench

Inspection date: 2026-10-02. Authenticated reads of private repositories; main branches and open PRs are distinguished. This is a repository-evidence assessment, not an independent replication or a measure of unpublished collaborator progress. No peer code, benchmark jobs or new LLM inference was run.

**Assessment:** our concern is justified: the peers generally define persona-aware evaluation targets more explicitly than our current performance/semantic/behavioral analyses. CodeBench has the strongest checked-in cross-model evidence. ChatBench has the clearest shared definition of publicly expressed needs and evaluation opportunities. CUABench has an explicit uniform cross-model execution contract, but completed full-grid results were not established by this inspection. ScienceBench has substantial existing matched scientific-task data and detailed offline analyses; its main gap is a frozen cross-model benchmark scorecard, not another diversity visualization.

| Dimension | ChatBench | CodeBench | CUABench | ScienceBench, current local state |
|---|---|---|---|---|
| Main question | Can assistants solve tasks while meeting observable user needs? | Can coding agents satisfy original tests and persona-dependent interaction/acceptance requirements? | Can browser agents complete tasks for different users, at what experience and cost? | How do simulator personas change scientific outcomes and interactions? |
| Scope | Eight conversational domains with domain-specific protocols | SWE-bench/DeepSWE, Terminal-Bench, plus ongoing adapters | 74 web tasks: 38 Odysseys and 36 REAL | 200 selected questions, 40 from each of five scientific sources |
| Persona-aware outcome | Public need fulfillment, critical-need pass, opportunity coverage | Independent personalization fulfillment; executable persona requirements in newer construction work | Asked-for completion, P1–P5 experience, simulator fidelity | Native scores, fact recovery, descriptive interaction and semantic measurements |
| Cross-model evidence | Some domains compare configurations; not a uniform named-model leaderboard | Checked-in six-agent-stack comparison; newer PR checkpoints are separate | Eleven backbones configured; completed full sweep not demonstrated | Main analyzed campaign uses Astra; incomplete Sol comparison withdrawn |
| Our relative position | Behind on the common metric contract | Behind on cross-model outcome evidence | Behind on multi-model harness preparation; full evaluation completion unclear | Stronger than a small pilot in data depth, but not yet a validated multi-model benchmark |

## 1. ChatBench: separate task success, needs fulfillment and simulator validity

The shared protocol distinguishes three questions: whether the assistant accomplished the task; whether it addressed a publicly expressed user need; and whether the simulated user preserved facts/persona without answer leakage. The third is interaction quality control, not an assistant score.

Needs receive 0/0.5/1 only after applicability, disclosure and an assistant response opportunity are established. Unexpressed, unobservable and unanswered needs retain separate statuses. Criticality is assigned before seeing the answer. Joint task/persona pass is allowed only when the original task defines a pass threshold. This prevents scoring compliance with private attributes that the assistant never had a chance to learn.

Sources: [shared protocol](https://github.com/MatrAIx-ai/PersonaChatBench/blob/a5a335031584986d5f59bf891a411793e38dcb71/standard/README.md), [domain overview](https://github.com/MatrAIx-ai/PersonaChatBench/blob/a5a335031584986d5f59bf891a411793e38dcb71/README.md).

Evidence of execution is substantial but uneven. Math reports 929 tasks, 1,858 planned conversations, 1,856 generated and 1,854 fully evaluated. Health reports 120 conversations across two anonymous doctor configurations; exact model settings are withheld, so its own report disclaims a reproducible named-model ranking. Only 29/50 and 31/50 persona episodes have scorable needs, and reported satisfaction is near ceiling. Travel's reviewed pilot is 30 dialogues, not a large model comparison. These are different cohorts and should not be summed into a single comparable experiment.

Sources: [Math](https://github.com/MatrAIx-ai/PersonaChatBench/blob/a5a335031584986d5f59bf891a411793e38dcb71/math-benchmark/README.md), [Health results](https://github.com/MatrAIx-ai/PersonaChatBench/blob/a5a335031584986d5f59bf891a411793e38dcb71/healthbench-benchmark/examples/RESULTS.md), [Travel](https://github.com/MatrAIx-ai/PersonaChatBench/blob/a5a335031584986d5f59bf891a411793e38dcb71/travel-benchmark/README.md).

Open [PR #27](https://github.com/MatrAIx-ai/PersonaChatBench/pull/27) is especially relevant: task completion, mutually exclusive failure categories, matched effects against neutral, task-by-needs outcomes, simulator validity and reliability. Its expanded task set and revised ending rule are PR changes, not inspected main-branch results. [PR #25](https://github.com/MatrAIx-ai/PersonaChatBench/pull/25) says finance persona selection is still pending human review. The repository itself documents protocol differences across domains, including Law evaluating the client rather than the assistant.

**What to borrow:** explicit opportunities and denominators, separate simulator validity, and outcome-specific failure reporting. Do not import new judge-based scores into our current dataset without acknowledging that they require additional scoring and validation.

## 2. CodeBench: strongest existing comparative evaluation, with distinct development tracks

A checked-in cross-benchmark report compares six model+harness stacks on 81 common valid SWE-bench task–persona pairs and 37 common valid DeepSWE pairs. It reports objective correctness separately from independent personalization fulfillment and examines changes in ranking by persona group. This is already closer to a benchmark leaderboard than our current one-model persona-effect campaign.

The report's primary personalization comparison conditions on each agent's own verifier-passing subset. Matching valid tasks before conditioning does **not** make those successful subsets identical. Its own text acknowledges this and supplies additional paired analyses where available. These are agent-stack comparisons (Codex/Copilot/Claude Code plus models), not isolated base-model effects. Two downloaded per-run summary JSONs independently support the older DeepSWE table's coverage: Codex+Sol 65/66 valid and Claude Code+Opus 5 42/66 valid. I did not regrade their outcomes.

Sources: [six-stack cross-benchmark report](https://github.com/MatrAIx-ai/PersonaCodeBench/blob/fb16951076579a0b0314170a4613d70bb9a6aef4/personalized_coding_agent_interactive_eval/paper_material/swebench_deepswe_cross_benchmark_personalization_results_20260901.md), [earlier five-stack table and linked summaries](https://github.com/MatrAIx-ai/PersonaCodeBench/blob/fb16951076579a0b0314170a4613d70bb9a6aef4/personalized_coding_agent_interactive_eval/paper_material/deepswe66_model_results_table_20260821.md).

A separate, newer construction track introduces vague openings, staged disclosure and executable additional persona requirements while preserving original tests. The root README reports an equal-budget Terminal-Bench screen with 89 baseline attempts, 68 baseline passes, 67 persona attempts and 57 persona passes—but zero qualified timeout contrasts. It also notes verifier problems and persona-check ceilings. Some linked TB2/TB3 development directories are absent from the inspected main tree; those detailed results are therefore README-reported, not fully verified from the linked local artifacts here.

Source: [current root README](https://github.com/MatrAIx-ai/PersonaCodeBench/blob/fb16951076579a0b0314170a4613d70bb9a6aef4/README.md).

Open branches contain more work, not a consolidated release: [PR #8](https://github.com/MatrAIx-ai/PersonaCodeBench/pull/8) reports 774 collected task–persona pairs over 78 tasks, with 61 original-task passes and incomplete collection; [PR #10](https://github.com/MatrAIx-ai/PersonaCodeBench/pull/10) accounts for 100 completed DeepSWE pairs, 98 valid, while distinguishing its older 95-record review pack; [PR #12](https://github.com/MatrAIx-ai/PersonaCodeBench/pull/12) adds an optional runtime integration and limited live diagnostics. These counts are not interchangeable or additive.

**What to borrow:** a model-by-persona score table, controlled comparisons, fixed evaluation contracts, and—once multiple models are available—uncertainty-aware ranking stability across personas. Their construction target changes requirements, whereas our current intervention changes collaborator persona; these answer different questions.

## 3. CUABench: explicit cross-model contract, incomplete evidence of full rollout

Main specifies 74 runnable tasks, 44 domain-conditioned personas, four persona roles plus control for each task, and 370 cells per model per replicate. Eleven execution backbones share the same Chrome harness and nine tools; persona and judge roles are fixed separately. The interface is DOM/text based; saved screenshots do not make it a vision-agent benchmark.

Scoring separates all task rubric items from communicated-only items. REAL tasks use final-state checks; other tasks use rubric judging. Experience dimensions are P1 asked-for fulfillment, P2 readability for the user, P3 actionability, P4 handling gaps and P5 overall experience. The implementation supports separate judge channels and reports agreement when both exist; a second judge can be absent. Tokens, latency, retries, cost and action behavior have explicit reporting code. Configuration support is not proof of successful runs for every model.

Sources: [README](https://github.com/MatrAIx-ai/PersonaCUABench/blob/38812808fd1e117dd3f22080608556acfd175da9/README.md), [experience scorer](https://github.com/MatrAIx-ai/PersonaCUABench/blob/38812808fd1e117dd3f22080608556acfd175da9/src/experience_judge.py), [report implementation](https://github.com/MatrAIx-ai/PersonaCUABench/blob/38812808fd1e117dd3f22080608556acfd175da9/src/report.py).

The main branch does not ship a full-grid results table in the inspected tree. Open [science/education PR #12](https://github.com/MatrAIx-ai/PersonaCUABench/pull/12) reports six tasks × five settings × three replicates = 90 scored cells using Terra, with 89 retained after environment audit. It explicitly says the other backbone grids were not run because credits ran out. No episode used ask_user, so this subset establishes opening-persona effects rather than repeated clarification behavior. Other open PRs contain small domain pilots and scoring audits; they do not establish the current 74-task × 11-model sweep.

**What to borrow:** a frozen model–task–persona matrix, identical tools/budgets across models, and explicit separation of requested requirements, actual task completion and cost. Treat their experience scores as model-judged assessments, not human realism evidence.

## 4. Implications for our paper

1. **Freeze what the benchmark evaluates.** For our existing design, the actor is evaluated under diverse simulated scientific collaborators. Keep simulator, judge, task panel and protocol fixed when changing the actor model. A joint actor/simulator change is a separate system experiment.
2. **Specify one primary outcome and compact supporting columns.** Retain native scientific performance; report off, persona-averaged and worst-setting performance, matched change from off, eligible coverage and resource use. Keep source-specific results visible because native scores have different semantics.
3. **Make collaboration effectiveness more concrete.** Fact recovery already supplies a task-grounded measure where withheld facts are defined. Broader user-need fulfillment is a possible future experiment, not a quantity we can infer from token counts, embeddings or repetition. Do not retrofit hidden preferences as if they were publicly expressed requirements.
4. **Keep the three existing analysis levels as explanatory evidence.** Semantic separation, repetition, reviews and tool-use differences explain model behavior; they are not inherently desirable scores. They can support a benchmark without becoming its leaderboard objective.
5. **Prioritize additional matched actor-model evaluations over more persona variants or plots.** That enables the most consequential question: do collaborator personas change which scientific agent performs best? Report uncertainty and shared coverage before calling a ranking change meaningful.
6. **Separate data quality from capability.** Simulator validity, infrastructure failure, missing submissions, judged task failure and unavailable preference opportunities should not collapse into one outcome. Much of this operational accounting already exists locally; semantic persona-fidelity validation would require an additional audit.

Current ScienceBench evidence remains useful: 200 selected questions across five sources; 1,958 eligible original traces for the selected five-setting behavioral analysis; detailed paired analyses and recorded tool actions across 1,518 applicable episodes. However, repeat coverage is uneven and the Sol comparison was withdrawn. Existing broad personas were partly selected using observed effects, so this panel is exploratory evidence rather than an outcome-independent sampling design.

**Priority judgment:** CodeBench is ahead in demonstrated cross-model results; ChatBench is ahead in persona-aware metric definitions; CUABench is ahead in cross-model harness preparation but not demonstrably finished with its sweep. Our next milestone should be a frozen, reproducible scientific-agent scorecard and matched additional models, while retaining the current analyses as explanations.
