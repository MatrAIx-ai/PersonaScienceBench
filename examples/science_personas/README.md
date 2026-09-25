# Simulator persona examples

- `profiles/`: six full, authored science profiles. The two PI files form a
  one-attribute decision-delegation contrast.
- `persona_overlay.json`: the complete opt-in persona block for an existing
  shared JSON run configuration.
- `profile.schema.json`: the exact 56-field profile contract for external clients.
- `simulator_prompt.example.txt`: the rendered PI identity for operator review.
- `inspect_injection.py`: a capture-only preview through the original simulator;
  requires an already prepared episode and existing run config.
- `simulator_review_template.json`: a separate human researcher-fidelity note.

See the [ODE injection example](../../docs/science_personas/ODE_INJECTION_EXAMPLE.md)
and [team handoff](../../docs/TEAM_HANDOFF.md). These files do not define a new
scientific task, evaluator, disclosure schedule, or actor score. Profiles and
prompt previews are private operator/simulator inputs.
