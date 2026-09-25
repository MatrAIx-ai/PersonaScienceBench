> **Integration update:** This is a proposed experiment, not an executed result. The planner now supports the seven current tracks and source-validated automated conversions. Historical standalone scope-audit claims do not apply to the merged repository.

# Phase 1: researcher persona as the only treatment

## Status and question

This is the corrected Phase 1 protocol. It does not redesign a scientific
benchmark. The question is whether different simulated human researcher personas
change the behavior and native scientific performance of the same agent.
The supplied material contains no finalized 50-task cohort or separately supplied
`experiment_plan` file. The original repository documents 25 converted cases;
that does not establish a ready 50-task cohort. No task IDs have been invented to
fill the gap. No 600-episode experiment has been run for this delivery.

The [12-arm example](../../examples/science_personas/phase1/design.proposed.json)
is a **proposal for allocating 600 episodes**, not a recovered or approved prior
arm matrix. Replace its field labels and reference assignments with the team's
registered choices before execution. Its `status` is deliberately `proposal`.
The [cohort template](../../examples/science_personas/phase1/cohort.template.json)
is deliberately empty and fails the 50-task build check until real tasks are added.

## Treatment and controls

For each existing task, use the same actor model and system prompt, scientific
task/instructions, data bytes, source revision, environment and tool exposure,
execution limits, approved researcher facts, gold/reference material, and native
evaluator/verifier with its original score scale and pass/fail thresholds.
Keep simulator model/settings, common policy, memory lifecycle, disclosure rules,
question limits, grounding checker, and fallback behavior identical across arms.
Keep settings fixed within task; existing task-specific environments may differ
between tasks. Use the same actor and researcher model configuration throughout
the cohort. Reset actor workspace and researcher history for each episode.

Persona is injected only as `identity` in the researcher's **private system
message**. The actor sees no profile, arm name, catalog, prompt preview, or plan;
it can experience persona only through researcher replies. Logs containing
profiles are private controller records, not actor inputs. The grounding checker
receives task context, selected approved facts, and the proposed reply, without
an additional profile or conditioning field. The same generic support policy
applies in every arm; persona fidelity is assessed separately.

`persona_off` keeps the same simulator and approved facts and simply omits
`identity`. It is not a no-researcher condition and does not switch to extractive
mode or a different response policy. Keep the originally selected mode in all
arms. Grounded mode can express style; extractive mode may suppress it. Never
change mode or force a question to create a detectable effect.

The fixed object is the approved fact pool and disclosure policy. The agent's
questions, selected fact IDs, prose, calls used, elapsed time, and resulting
trajectory may differ as outcomes. Actual resource consumption is an outcome;
allocated limits must remain fixed. Model grounding reduces factual errors but
does not prove semantic truth or guarantee that a model will never leak a trait.

## One dimension at a time

Use one common reference persona with all 56 assignments explicit. Each treatment
changes exactly one attribute level or the `domain` field label, keeping role and
all other assignments fixed. IDs are private bookkeeping and are not rendered.
Do not use the six whole-profile examples as Phase 1 treatment arms.

The example maps broad research ideas to narrow operational dimensions:

| Concept | Changed value | Fixed neighboring dimensions |
|---|---|---|
| Field | `SciencePersona.domain` only | All capability and communication anchors |
| Domain expertise | `domain_theory` | Literature familiarity, method, statistics, coding |
| Methodological expertise | `methodological_breadth` | Experimental design, statistics, numerical analysis |
| Computational expertise | `coding_fluency` | Debugging, scientific ML, numerical analysis, compute systems |

These are explicit proxies, not validated measures of each entire broad construct.
For example, changing all computational attributes together would be a bundled
intervention. Study other computational subdimensions as separate contrasts.
Field affiliation does not add external domain facts or automatically change
expertise. Choose field labels before seeing results.

### Proposed allocation

| Arm family | Conditions | Episodes for the same 50 tasks |
|---|---:|---:|
| Persona off | 1 | 50 |
| Common reference persona (all anchors medium) | 1 | 50 |
| Field labels differing from the applied-mathematics reference | 4 | 200 |
| Domain theory low/high | 2 | 100 |
| Methodological breadth low/high | 2 | 100 |
| Coding fluency low/high | 2 | 100 |
| Total | 12 | 600 |

Attribute effects compare a treatment with the common reference, or low vs high
within that same dimension. Do not label a comparison between different treatment
dimensions as a single-variable effect. Off vs reference tests the presence of
conditioning as a whole; it does not identify one attribute's effect. The shared
reference/off observations are reused in analysis, not counted as independent
new observations for each contrast. There is one run per task/arm in this proposal;
additional repetitions increase the episode total and need their own registration.

## Freeze and inspect, without changing task design

1. Select and register the same 50 distinct existing source tasks before any arm
   is run. Record exclusions based on pre-existing readiness/validity criteria,
   not observed persona effects. Do not replace hard tasks only in one arm.
2. Reuse each task's current source-validated Episode or native EXP task card and normal run config. Confirm the
   recorded runner and effective interaction protocol match the intended condition.
   Shared/Terminal/ASI reviews, native SciConv clarification, and EXP design consultation
   remain distinct protocols; hold each fixed across persona arms.
3. Fill one [task-entry template](../../examples/science_personas/phase1/task-entry.template.json)
   per task in the cohort's `tasks` list. Paths resolve relative to the cohort
   file. Include complete native task trees, all data, runtime/container lock
   records, launch commands/flags, model/environment settings, source manifests,
   approved-fact provenance, private references/gold and verifier code. The Episode
   and config are hashed automatically. A category may point to the same file as
   another category if that file actually contains both. If no standalone gold
   file exists, include the original verifier/reference specification; do not
   invent one. Use a reviewed note for truly absent external inputs.
4. Validate the design, build the private plan, and verify it:

```bash
uv run --locked python -m personasciencebench.science_personas.phase1 design-check \
  --design examples/science_personas/phase1/design.proposed.json
uv run --locked python -m personasciencebench.science_personas.phase1 build \
  --design YOUR_REGISTERED_DESIGN.json --cohort YOUR_50_TASK_COHORT.json \
  --output phase1.private
uv run --locked python -m personasciencebench.science_personas.phase1 verify \
  --plan-directory phase1.private
```

The builder requires exactly 50 distinct source tasks. It accepts the six shared Episode-based tracks plus native EXP task cards/catalogs. Both reviewed and automated facts are frozen. Legacy collaboration extensions remain rejected; the current interaction protocol is supplied by the run configuration and held fixed across arms. EXP catalogs require an explicit `task_id`; generated JSON configs can be passed to the native EXP runner. Each plan records the runner and source task ID, but launches no jobs.

5. Inspect injection using the [ODE example](ODE_INJECTION_EXAMPLE.md). Apply the
   same check to each runner family. Verify actor visibility and operator-only
   file placement with the original sandbox rules. Never mount the private plan
   or generated configs into an actor workspace.
6. Use each benchmark's existing launcher, environment setup, execution budget
   and evaluator. Translate each manifest entry into that launcher's existing
   selection mechanism. Confirm the selected task IDs and emitted effective
   config match the manifest; the planner does not rewrite pilot selectors or
   construct a universal launcher. For runners requiring a batch, use the same
   arm config for the registered subset and record actual execution order.
7. Verify frozen inputs immediately before and after a run/batch. Record actual
   container digest, hardware allocation, dependency state, tool versions,
   API/provider model metadata, effective seeds/sampling settings and deviations.
   Keep these settings equal across arms. An order seed only controls the manifest
   order; it is not a model or scientific-data seed. Providers may not offer fully
   deterministic sampling. Do not claim model-version invariance without receipts.
8. Preserve raw outputs and the native evaluator result. Treat infrastructure
   errors and missing results separately under the original benchmark policy;
   no arm-specific retries, extra budget, thresholds or fallback models. Register
   any common retry policy in advance and retain all attempted episodes.

Hashes verify declared local bytes and executable bits. They do not prove that
owners listed every dependency, that a mutable remote resource stayed unchanged,
or that a live launcher actually used the planned settings. Those require the
existing runtime receipts and owner review. Recheck the plan rather than silently
updating its hashes after drift. The plan itself is not a scientific verifier.

## Outcomes and interpretation

Preserve the benchmark's original evaluation JSON and native score/pass criteria.
Do not merge heterogeneous score scales, add persona rewards to scientific scores,
or turn an interaction observation into a submission gate.

Use existing `events.jsonl`, actor trajectory, API receipts and native evaluation:

| Observation | Record | Interpretation limit |
|---|---|---|
| Question asking | Number and position of researcher calls; topics and question text | More questions alone do not imply better questions |
| Response behavior | Agent actions/text following a reply; whether supplied corrections are used | Code from trace evidence, preferably with arm labels hidden |
| Researcher dependence | Consultation counts, repeated queries, facts used, explicit deferral | Counts are proxies; causal dependence is not proved by use |
| Researcher expression | Reply length, factual-support fallbacks, separate fidelity review | A schema-valid persona is not validated human realism |
| Scientific result | Unmodified native evaluation, status, score and pass/fail | Retain original benchmark interpretation |

A read-only helper exports descriptive counts and copies native evaluation JSON
without changing its values:

```bash
uv run --locked python -m personasciencebench.science_personas.observations \
  --events RUN/controller/events.jsonl --evaluation RUN/evaluation.json \
  --output observations.json
```

Omit `--evaluation` when no native evaluation file was produced. Zero questions
and unobservable traits remain valid outcomes, not data to exclude after seeing
results. Do not estimate real human minutes from simulator tokens; report tokens,
calls, and latency as separate measures. Question quality and adaptation require
an explicit, separately reviewed coding rubric and quoted evidence.

Analyze matched within-task differences, stratified by original benchmark where
score scales differ. Register primary contrasts/outcomes and multiplicity handling
before analysis; report uncertainty and effect sizes rather than only significance.
If tasks share a study, account for that dependence. One run per arm does not
isolate sampling noise; label the first sweep exploratory and seek replication
before claiming a stable effect. Unchanged scores are legitimate results.

## Phase 2 boundary

Only after replicated, stable evidence for a dimension should a separately
versioned follow-up consider go/no-go decisions, revision cycles, resource
negotiation or selective escalation. Those interactions are not added, scheduled,
required or scored by this Phase 1 release. A task/evaluator defect belongs to its
benchmark owner, outside the persona treatment patch.
