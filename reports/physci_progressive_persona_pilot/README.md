# Five-persona progressive-disclosure pilot on PhySciBench

This small pilot tests whether different researcher personas change how an actor obtains a task and completes a lightweight scientific calculation. We ran **five tasks × five personas × one attempt = 25 model episodes** on September 27, 2026. **24/25 passed the adapted numerical checks**, all 25 submitted scripts replayed successfully, and every episode obtained all approved information cards before submission.

Final-answer performance showed little separation in this sample. Once the requirements were available, the actor usually completed these small tasks independently. This is consistent with limited room for researcher persona to affect the final answer in this setting; it does **not** establish that the actor is optimally efficient or that personas have no effect. Token use and elapsed time expose more variation, including self-debugging and avoidable computation.

## Persona design

These are **five newly authored research personas**, not demographic profiles or extracts from candidates 046/148/155 in `full_persona_v2`. No age or demographic condition was varied. All personas have the same source facts; differences concern presentation, interpretation, guidance, and workflow preferences. An unfamiliar method may be quoted faithfully from the records without claiming expertise in explaining it.

| Persona | Role and expertise | Research style; evidence/risk preference | Communication and interaction | Resource/workflow preference; knowledge boundary |
|---|---|---|---|---|
| Experimental researcher | Experienced hands-on researcher; strong in experimental conditions, acquisition, and data meaning | Start from phenomena/data; value observations and physical interpretation | Concrete language; typically provide one or two related information units and respond to direct questions | Inspect records/data first; quote model records but defer unfamiliar derivations or algorithm choices |
| Computational researcher | Experienced computational researcher; strong in equations, algorithms, and numerical methods | Start from models/assumptions; value consistency, convergence, and reproducibility | Technical, concise language; group related model conditions | Build a minimal calculation first; quote experimental records without inventing measurement mechanisms |
| Methodological reviewer | Senior methods/quality reviewer; strong in assumptions, errors, and validation | Clarify definitions/boundaries; be cautious toward unvalidated claims | Precise language separating facts and assumptions; focus on relevant issues and question assumptions when progress is shared | Validate on a small scale first; do not claim knowledge of every domain mechanism |
| Exploratory junior researcher | Graduate student new to the area; basic subject knowledge and limited cross-domain experience | Build understanding through discussion; seek help assessing evidence | Concrete, less organized, low-jargon explanations; typically one or two units, with clarification when needed | Prefer small steps and feedback; provide all records even when unable to synthesize an explanation |
| Delivery-focused project lead | Lead responsible for delivery/resources; strong in goals and application context, moderate technical depth | Start from deliverables; accept justified approximations within explicit accuracy requirements | Short, structured, decision-oriented replies; batch related conditions | Prioritize a minimal viable solution and resource efficiency; consult supplied records for technical details |

This table groups the eight implemented attributes: role/seniority, expertise, research style, evidence/risk preference, communication, resource/workflow preference, interaction, and knowledge boundary. The exact injected profile configurations are in [profiles.json](profiles.json); their original Chinese display labels are retained for fidelity. Each persona changes several attributes together, so this is not a single-attribute experiment.

## Tasks and protocol

| PhySciBench task | Calculation | Scale |
|---|---|---|
| 068 | Exciton dynamics with a thermal phonon bath | Small density-matrix/rate-equation calculation |
| 070 | Damped coupled pendulums | 20 ODE variables, two coupling strengths |
| 071 | One-dimensional Gray–Scott reaction–diffusion | 24 variables, 100 Euler steps |
| 076 | Heat conduction in an insulated rod | 10 variables, 1,000 Euler steps |
| 080 | Gaussian-pulse-driven two-level system | Small density-matrix integration |

All five are text/code tasks, require no image interpretation, and need no GPU. Some actors nevertheless chose unnecessarily expensive calculations.

- The **researcher** receives the persona. The actor starts with the same generic request to assist a researcher, without the scientific question, task ID, conditions, data, or reference answer.
- The first researcher response discloses only the goal. Later responses select relevant fact cards according to the question and persona. The common ceiling is **eight new cards per response** and 16 consultations; persona-specific amounts are soft preferences. Actors can request all remaining information.
- The controller appends the selected canonical facts verbatim. A separate model call checks supporting prose when present. Invalid plans fall back to the profile's default disclosure order; unsupported prose is removed. These interventions are logged.
- Both actor and researcher use **`openai/gpt-6-luna`, reasoning effort `none`**, through the local OpenHands-based runner. The actor has an 80-step ceiling. Calculations use network-disabled Docker with two CPUs and 2 GB memory per container; two episodes run concurrently.
- There is one attempt per task/persona, without score-based reruns. Debugging or recovery inside an episode is part of that same attempt. The initial infrastructure-check episode is included among the 25, not an extra repeat. The runtime and inputs stayed unchanged across the batch.

Five ScienceAgentBench tasks were also planned (016, 029, 085, 087, 092). Their verified annotations were available, but the official complete input/evaluator archive returned HTTP 401. **Those 25 combinations were not run and are not counted as scientific failures.** No conclusions about ScienceAgentBench follow from this pilot.

## Results

Means below are per episode across the **same five tasks**, including the failed numerical result and recovery costs. A consultation is one actor question and researcher reply, not one model API call.

| Persona | Numerical pass | Mean consultations | Mean actor tokens | Mean researcher tokens | Mean total tokens | Mean elapsed time (s) |
|---|---:|---:|---:|---:|---:|---:|
| Experimental researcher | 5/5 | 2.6 | 13,149 | 5,599 | 18,749 | 66.9 |
| Computational researcher | 5/5 | 2.6 | 17,779 | 5,944 | 23,723 | 78.1 |
| Methodological reviewer | 5/5 | 2.6 | 12,324 | 5,908 | 18,232 | 60.2 |
| Exploratory junior researcher | 4/5 | 2.8 | 17,622 | 6,260 | 23,883 | 107.9 |
| Delivery-focused project lead | 5/5 | 2.6 | 14,318 | 5,631 | 19,949 | 68.2 |

Tokens include input and output, including repeatedly sent history. Researcher tokens include disclosure planning and the additional support check; those phases are separated in [results.json](results.json). Columns are rounded independently. Total usage was **522,674 tokens**; the API reported **$0.057585065** in cost across the 25 episodes. Elapsed time includes setup/preflight, API waits, controller work, and calculation; it is not pure model latency. Offline script replay is outside these episode totals and incurs no model tokens.

## What can we learn about persona?

**1. Accuracy is close to a ceiling on these small adapted tasks.** Four groups passed all five numerical checks; the junior group passed four. The failed Gray–Scott script constructed both neighbor arrays as copies of the unshifted array, making its diffusion term zero. All required information had already been disclosed. This is a concrete implementation error, not evidence that a junior persona caused the error. The one-attempt design provides no estimate of within-condition variability.

**2. Efficiency measures distinguish the observed trajectories better than final correctness.** The methodological-reviewer condition had the lowest observed mean tokens and time; the computational and junior conditions consumed about 30% more tokens. These are descriptive differences, not a reliable persona ranking. For example:

- In the computational/exciton episode, the actor debugged an operator/basis inconsistency and revised its calculation without asking the researcher again.
- In the junior/pulse episode, the actor initially solved the same dynamics separately for 501 observation cutoffs, hit a 120-second timeout, and then replaced this with one integration and prefix maxima. That timeout alone adds approximately 24 seconds to the five-episode group mean.

Thus token and time differences can arise from actor implementation choices and recovery, even when consultation counts are identical. Separate communication overhead, scientific computation, and debugging before attributing an efficiency difference to persona.

**3. A small information-packaging difference is visible.** On the heat-conduction task, the junior condition used four consultations instead of three: boundary conventions were answered separately, followed by another request for the remaining output requirements. It still passed. This is compatible with incremental disclosure, but a single instance cannot isolate the persona from differences in the actor's questions or sampling variation.

**4. The protocol still measures initial task elicitation more than ongoing collaboration.** All 25 episodes reached 100% fact-card coverage; **none asked the researcher after scientific calculation began** (verified against command positions, not merely the first Python invocation). In **24/25 episodes**, the number of consultations exactly matched the minimum needed to disclose all cards under the common cap. Asking for all remaining details tends to compress soft persona differences into a similar two- or three-exchange workflow.

**5. Rendering/format handling limits persona fidelity.** Of 66 researcher replies, **38 triggered invalid-plan fallback** and another **14 had unsupported prose removed**. All 38 invalid-plan outputs contained an embedded JSON object; extra text outside it prevented strict parsing. In five of those replies, fallback changed the selected fact set; even when the set stayed the same, the intended prose was discarded. Consequently, this batch cannot cleanly estimate the effect of the intended persona expression. The protocol was not changed or rerun mid-batch; these limitations remain part of the recorded results.

A useful next step is to fix structured-response handling and test the same actor handoff against different researcher profiles. Tasks with genuine decisions after an intermediate result would better probe whether a persona changes validation requests, interpretation, or subsequent computation. This pilot has **no persona-off/all-context control** and does not establish causal improvements in correctness or efficiency.

## Evaluation scope and supporting files

“Numerical pass” checks declared outputs against precomputed references and tolerances for the **adapted tasks**, not an official PhySciBench leaderboard score. Supplementary script replay checks executability: all 25 scripts ran successfully, including the numerically incorrect reaction–diffusion script. Replay alone does not certify scientific correctness or full compliance with the original rubric.

The adapters explicitly added missing conventions from reference implementations: energy/unit handling (068), boundary conditions and a converged numerical reference (070), synchronous Euler/endpoint conventions (071), endpoint/index/coefficient interpretation (076), and initial/equilibrium state plus inversion conventions (080). Structured numerical submission fields were also added. In particular, the 070 target uses a refined solution rather than the original default-tolerance output. These qualifications matter when interpreting the high pass rate.

- [results.csv](results.csv): all 25 completed episodes, with usage, timing, coverage, command failures, and consultations after calculation.
- [results.json](results.json): detailed numeric outputs/errors/tolerances, role/phase usage, fallbacks, replay checks, and submitted-artifact hashes.
- [summary.json](summary.json): exact aggregates, excluded tasks, source revisions, and local execution-file hashes.
- [profiles.json](profiles.json) and [runtime_config.json](runtime_config.json): the persona/runtime configurations used.
- [case_evidence.json](case_evidence.json): selected consultation questions, disclosed-card IDs, and execution results supporting the case analysis. These are excerpts, not full replayable transcripts.

Raw API dumps, credentials, local absolute paths, original benchmark archives, and full local transcripts are not included. The local runner and task-card packages are not shipped in this report-only PR; their hashes provide provenance, not an independently runnable reproduction package.

Sources: [PhySciBench](https://huggingface.co/datasets/yigengx/PhySciBench) at `54fdfe63b723b83f3dbfc61f18a402c560e2b24c`; [ScienceAgentBench verified annotations](https://huggingface.co/datasets/osunlp/ScienceAgentBench) at `9c6e96c9e74572e979b0930ee735041cef528cb7`. These adapted-task results are separate from the repository's existing [`full_persona_v2`](../full_persona_v2/README.md) experiment.
