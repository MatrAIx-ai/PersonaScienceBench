# Expertise pilot: experiment setting and motivation

**Proposed initial run:** 50 tasks—10 each from DiscoveryBench,
ScienceAgentBench, BixBench, Terminal-Bench-Science and EXP-Bench.

## Experiment setting

| Setting | Values / clarification |
| --- | --- |
| **Scientific field** | Five researcher-background groups: Computing, engineering & industry; Science, health & agriculture; Society, education & institutions; Business, finance & services; Arts, humanities & media. These are five supergroups merged from the 16 fields in the original persona setup. |
| **Domain-expertise level** | **Novice / Expert** — subject knowledge within the researcher's field. Intermediate is omitted from this pilot. |
| **Methodological-expertise level** | **Novice / Expert** — understanding of research methods, experimental design and statistical analysis. Intermediate is omitted from this pilot. |
| **Computational-expertise level** | **Novice / Expert** — programming, computational tools and implementation skills. Intermediate is omitted from this pilot. |
| **Experimental design** | Test each dimension in parallel rather than combining all dimensions. Vary one dimension at a time and hold the other dimensions at fixed reference values. |
| **Baseline** | **Persona-off:** retain the simulator and the same approved task facts, without persona conditioning. |
| **Models** | Use the same low-cost, fast model across all pilot conditions. |
| **Total executions** | **600 episodes** before reusing any identical reference conditions. |

## Parallel experiment arms

| Experiment | Varied dimension | Fixed dimensions | Executions |
| --- | --- | --- | ---: |
| Scientific field | Five field groups | All expertise levels fixed | **50 × 5 = 250** |
| Domain expertise | Novice / Expert | Field task-matched; methodological and computational expertise fixed | **50 × 2 = 100** |
| Methodological expertise | Novice / Expert | Field task-matched; domain and computational expertise fixed | **50 × 2 = 100** |
| Computational expertise | Novice / Expert | Field task-matched; domain and methodological expertise fixed | **50 × 2 = 100** |
| Persona-off baseline | Persona disabled | Simulator and approved task facts retained | **50 × 1 = 50** |
| **Total** |  |  | **600** |

Use the same 50 tasks across all arms. Keep task inputs, simulator facts, model
configuration and execution budgets fixed. Select the reference values before
running the pilot and use them consistently. Identical reference configurations
may be reused across comparisons, reducing the number of unique executions.
Record whether the researcher's scientific field matches the task's field.

## Motivation

Doing this, we can achieve:

1. **Identify which persona dimensions matter.** Estimate the main effect of
   scientific field and each expertise dimension without confounding it with
   every other dimension.
2. **Understand how researcher expertise changes agent behavior.** Compare
   behaviors such as response length and question asking across persona
   configurations.
3. **Measure whether behavioral changes affect task performance.** Compare
   benchmark scores across persona settings and identify where an agent depends
   on knowledgeable collaborators.
 
**Next step:** Add interactions only for dimensions that produce meaningful
effects, and discard settings that do not produce measurable changes.
