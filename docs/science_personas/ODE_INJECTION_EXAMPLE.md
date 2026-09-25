# ODE model task: one fixed task, different private researcher personas

## Existing scientific task

Terminal-Bench-Science's `mathematical-sciences/applied-mathematics/ode-law-discovery`
asks the agent to infer compact symbolic ordinary differential equations from
noisy three-dimensional trajectories, then roll the equations forward from
provided initial conditions. The native outputs are `/results/equations.json`,
`/results/predictions.csv`, and `/results/report.md`. The native verifier checks
output/parser validity, symbolic compactness, hidden and stress rollouts, and
vector-field agreement. Its original numerical gates and pass/fail rule remain
in the task files; this example neither rewrites nor reinterprets them.

Use the team's existing source revision, task package, approved researcher facts,
environment, launch budget and verifier. The [original adapter documentation](../adapters/terminal_bench_science.md)
remains authoritative for preparing and running this task. The actor retains the
full original instruction and visible data. Required information is not hidden
to make the agent consult the researcher.

## Phase 1 change

Use the common reference profile and a `coding_fluency` low/high contrast from
[the proposed design](../../examples/science_personas/phase1/design.proposed.json).
For these three profiles the role, field and all 55 other attribute levels are
identical. The actor is unchanged. Only the private simulator system `identity`
changes. Include persona off with the same simulator, facts, policies, limits and
mode; off omits identity rather than removing researcher access.

No extra go/no-go decision, resource negotiation, revision cycle, hidden preference
requirement or final approval gate is added. Expertise changes expression within
approved context, not access to gold equations, hidden trajectories or new facts.
Question asking remains the actor's choice. Zero questions or no detectable effect
is a valid result and is not a reason to redesign the ODE task.

## Inspect injection offline

Start with a clean Episode from the **unchanged original adapter**. Do not reuse
the superseded `ode-disclosure-1.0` package, `actor/collaboration.md`, or its extra
conversion metadata. The current Phase 1 planner rejects those known old markers.
The archived earlier preview happened to use such metadata; the current evidence
was regenerated directly from the unchanged adapter and supersedes that preview.
No old collaboration file is required or included in this delivery.

Use the same existing base config for all calls below. Replace `EPISODE` with your
normally prepared task directory:

```bash
uv run --locked python examples/science_personas/inspect_injection.py \
  --episode prepared/EPISODE/controller/episode.private.json \
  --config configs/pilot.json \
  --profile examples/science_personas/phase1/reference.json
uv run --locked python examples/science_personas/inspect_injection.py \
  --episode prepared/EPISODE/controller/episode.private.json \
  --config configs/pilot.json \
  --profile examples/science_personas/phase1/coding_fluency_low.json
uv run --locked python examples/science_personas/inspect_injection.py \
  --episode prepared/EPISODE/controller/episode.private.json \
  --config configs/pilot.json --persona-off
```

The preview captures the existing `Researcher.ask` request before inference. It
writes no source Episode, invokes no verifier, and forces no interaction if the
existing settings issue no request. Its output is private operator material.
Compare `public_task_sha256`, `task_eval_sha256`, `non_persona_config_sha256`,
`non_identity_system_sha256`, and `eligible_fact_ids`: all must match for the same
question. `identity` differs by profile and is null for off. The generated profile
ID is absent from the prompt. Do not give this preview to the actor.

## Evidence and limits

The [current ODE check](../../reports/persona_only/ode_injection_comparison.json)
uses a fresh Episode from the unchanged supplied adapter. It verifies that the
original instruction is preserved, checks 20 native source/license files against
the existing source lock, and compares all 12 proposed arms including off. Public
task, TaskEval, non-persona config, eligible facts and non-identity request hashes
are equal across those arms. Native task, data, environment and verifier file
hashes are recorded. These are request-construction and source-integrity checks.

No model was called, no new ODE solution was produced, and the scientific verifier
was not run for this revision. Simulator fidelity and actor/scientific effects
remain empirical questions. Source-file hashes alone cannot certify a future
live container or launcher; retain runtime receipts when running the experiment.

## Reuse for another assigned task

1. Reuse its existing Episode, data, approved facts, launcher and native verifier.
2. Supply the same reference and one-dimension arms selected by the lead.
3. Repeat the private injection check, including persona off.
4. Fill its fixed-input inventory in the common 50-task cohort, following the
   [experiment plan](experiment_plan.md). Include runtime and launch settings
   outside the JSON config; keep them fixed across arms.
5. Run only through the existing benchmark launcher and retain its native result.
   Export descriptive interaction observations separately. Report missing assets,
   unsupported simulator integrations and task defects before including the task.

This is an example of persona integration and controlled comparison, not a new
scientific-task conversion template. See [team handoff](../TEAM_HANDOFF.md).
