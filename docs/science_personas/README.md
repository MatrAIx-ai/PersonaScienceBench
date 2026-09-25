# Science personas: Phase 1 simulator conditioning

This release expands the researcher vocabulary to 56 behavior-anchored science
attributes. Phase 1 changes only persona conditioning in the researcher's private
system prompt. The actor sees the researcher's replies. Persona off uses the same
simulator, facts, policy, settings and budget, omitting only conditioning.

The scientific task, data, environment, execution budget, scientific fact pool,
gold/reference and original evaluator/verifier remain fixed across arms. No new
interaction gate or scientific scoring rule is introduced.

## Start here

1. [Experiment plan](experiment_plan.md): controls, one-dimension contrasts, the
   50-task requirement, a clearly proposed 12-arm allocation and analysis limits.
2. [Team handoff](../TEAM_HANDOFF.md): task owners' reading order and deliverables.
3. [ODE injection example](ODE_INJECTION_EXAMPLE.md): use one unchanged task.
4. [Integration guide](INTEGRATION_GUIDE.md): the actual private injection path.
5. [Attribute catalog](ATTRIBUTE_CATALOG.md), [selection](PROFILE_SELECTION.md),
   and [provenance](ATTRIBUTE_PROVENANCE.md): definitions and authored examples.
6. [Simulator QA](SIMULATOR_QA.md): assess fidelity without rewriting tasks.
7. [Current trial](../../reports/conversion_v2/README.md): integration outcomes; full raw traces stay local.

This correction unifies the previously different on/off instructions and removes
the separate profile input from the grounding checker. The legacy optional-question path uses policy version
`persona-conditioning-only-v3`; current approach/result reviews use `researcher-review-v2`. The only direct conditioning surface is the
reply-generating simulator's system `identity` field. Private metadata records
are not model prompts or actor inputs.

The new offline planner checks explicit single-dimension arms, an exact 50-task
cohort, generated configs and declared artifact fingerprints. It does not run
models, alter task selectors or replace benchmark launchers. The supplied cohort
is unfilled; the 600-episode example is not a completed experiment.

All 56 attributes are rendered; a trait need not become visible in every episode.
Zero questions and null effects are retained. Current approach/result review gates are fixed across persona arms; their handoffs are reported separately from optional questions. SciConv retains native clarification. The merged seven-track conversion and interaction protocols remain in place. The planner generates configs for those protocols rather than reverting them to the older optional-question controller. Superseded standalone reports and scope audits are omitted.
