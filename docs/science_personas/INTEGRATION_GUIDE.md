# Integrating a science persona into the existing simulator

## Fixed interface

The shared pipeline already calls:

```python
persona = resolve_persona(config, episode)
researcher = Researcher(episode, backend, persona=persona, **config["researcher"])
```

During an existing researcher reply, `Researcher.ask()` puts
`render_persona(persona)` in the private system message's `identity` field.
A science profile replaces only that identity rendering. The grounding checker
receives no persona profile or preferences field. Its common policy checks factual
support in the task and selected approved facts and permits optional preferences
without treating them as task requirements. It is not a persona-fidelity judge.
Legacy profiles keep their rendering and records.

No new simulator, session class, task adapter, callback, actor tool, evaluator,
question budget, review state, or interaction score is required. The profile
never enters the public task or the actor's initial system prompt. The actor can
experience it through researcher replies produced by the existing simulator.

## Validate and preview a profile

From the repository root, after the normal environment setup:

```bash
uv run --locked python -m personasciencebench.science_personas validate \
  --profile examples/science_personas/profiles/pi_cautious.json
uv run --locked python -m personasciencebench.science_personas render \
  --profile examples/science_personas/profiles/pi_cautious.json
```

These commands are offline and need no episode, scientific data, evaluator,
credentials, or model. The render output includes the complete profile, catalog
hash, renderer version, prompt, and a deterministic record hash. It is an
operator/private artifact; do not copy it into actor-visible files.

## Attach to a copy of your existing run configuration

Use your current run config as the input. The supplied pilot config is only an
example; this operation does not select models or change their settings.

```bash
uv run --locked python -m personasciencebench.science_personas attach \
  --profile examples/science_personas/profiles/pi_cautious.json \
  --config configs/pilot.json \
  --output configs/persona.pi_cautious.local.json
```

The new file differs from the input only in its top-level `persona` value.
`models`, `researcher`, `actor_steps`, source locations, budgets, and every other
key retain their input values. The input is not modified; an existing output
file is not overwritten. Continue using your original launch command with the
new config path. The tool does not launch any scientific run.

The attachment helper accepts empty existing routing. If `persona_router` has
nonempty defaults/domain/task entries, it fails with a clear error rather than
rewriting those routes or silently allowing them to override your selection.
Phase 1 uses explicit common arms with empty routing, so every task receives the
same intervention. The legacy router remains available for other experiments but
is rejected by the controlled-comparison planner.

The [example persona block](../../examples/science_personas/persona_overlay.json)
shows the complete opt-in structure. `science_profile.version` is
`science-persona-2.0`; all 56 attributes must be present. `active_attributes` and
task-control fields are rejected. Old task-projected science profiles must be
replaced with a complete v2 profile. Legacy profiles without `science_profile`
remain valid.

## Existing modes and disabled persona

Keep the mode already selected for your experiment. In the existing `grounded`
mode, supported researcher prose can express persona. Its existing support check
still rejects unsupported factual assertions. In `extractive` mode the original
approved fact text is returned, so style differences may not be visible. This
extension does not silently switch modes to make an effect appear.

Set `persona.enabled=false` for persona off. Top-level disable bypasses routing
and omits only identity conditioning. The simulator model, approved facts, common
instructions, grounding checker, mode, limits and call sequence remain the same.
On/off policy metadata both use `persona-conditioning-only-v3`. This corrects the
previous implementation, which used a distinct off-only instruction string. A run with no researcher interaction may reveal no persona effect;
do not add questions or reward conditions to manufacture one.

The shared and Terminal runners use this injection route. Separate EXP simulator
policies have not been audited or corrected to this Phase 1 contract; the new
planner rejects those runner families. Do not claim that renderer reuse alone
makes an EXP experiment compliant. The attachment CLI handles shared JSON run configs only;
it does not rewrite EXP TOML files or their experiments.

Use the [Phase 1 planner](experiment_plan.md) to generate and freeze the complete
controlled comparison. An attachment or preview alone is not runtime verification.
