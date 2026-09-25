# Team handoff: Phase 1 researcher persona conditioning

Task owners reuse existing scientific tasks. Their assignment is to verify
simulator persona injection and fixed inputs, not to rewrite task instructions,
data, researcher facts, gold answers, scientific scoring or interaction protocol.

## Read in this order

| Order | File | Purpose |
|---|---|---|
| 1 | [Phase 1 experiment plan](science_personas/experiment_plan.md) | Contract, controls, 50-task cohort, proposed 12 arms, outcomes and limits |
| 2 | [ODE example](science_personas/ODE_INJECTION_EXAMPLE.md) | Apply the contract to one existing scientific task |
| 3 | [Integration guide](science_personas/INTEGRATION_GUIDE.md) | Private-system-only injection; on/off use the same simulator |
| 4 | [Attribute catalog](science_personas/ATTRIBUTE_CATALOG.md) and [selection rules](science_personas/PROFILE_SELECTION.md) | Interpret anchors and vary one dimension |
| 5 | [Simulator QA](science_personas/SIMULATOR_QA.md) | Review researcher fidelity separately from scientific grading |
| 6 | [Validation](../reports/persona_only/VALIDATION.md) | Measured software evidence and remaining operational checks |

## Division of work

| Owner | Deliverable |
|---|---|
| Lead | Registered reference/contrasts, the same 50-task list, outcome definitions and analysis plan |
| Task owner | Existing Episode/config paths; complete fixed-input inventory; actor visibility and launcher checks |
| Persona owner | Shared catalog/profile review, exactly one-field treatment definitions, prompt versions/hashes |
| Simulator reviewer | Independent fidelity/grounding evidence from standalone probes or naturally occurring replies |
| Run owner | Existing-launcher invocations, fresh workspaces, invariant checks, runtime receipts and native results |

## Task-owner checklist

1. Start from the team's existing reviewed task package and native evaluation
   command. Record its source revision; report a defect separately if one exists.
2. Fill [one cohort entry](../examples/science_personas/phase1/task-entry.template.json)
   with the Episode, existing config, task/data/environment/execution/facts/gold/
   verifier paths. Do not make a different package for each persona. Include
   launcher flags and runtime locks that are outside the JSON config.
3. Use the lead's common reference and single-dimension contrasts. The six whole
   profiles are vocabulary examples, not Phase 1 arms. Do not select an easier
   persona for a particular task or use task-dependent routing.
4. Follow the ODE preview for reference, one contrast and persona off. Verify the
   non-identity request, facts, public task, TaskEval and non-persona config match.
   For different naturally arising questions, disclosed facts may differ; the
   approved fact pool and filtering rules must remain fixed.
5. Return the completed cohort entry and injection evidence to the lead. The
   offline planner refuses fewer or more than 50 distinct source tasks. Its
   empty template is not a runnable cohort; do not fill it with placeholder IDs.
6. After cohort registration, use the existing benchmark launcher with generated
   configs. Check effective settings and actual task selection. Reverify declared
   input hashes before/after execution, preserve runtime receipts, and keep
   controller files outside actor mounts. The separate EXP runners need their
   own reviewed integration and are not covered by the new Phase 1 planner.
7. Deliver raw trajectories/events, native evaluation files, descriptive counts,
   and any deviations. Keep zero-question cases and native failures. Never change
   pass/fail criteria or introduce a persona-dependent final review gate.

## Implementation map and checks

- `src/personasciencebench/researcher.py`: shared response policy, private identity,
  fact selection and persona-independent grounding check.
- `src/personasciencebench/science_personas/profiles.py`: 56-attribute schema and
  deterministic renderer; `config.py`: persona-only config copying.
- `src/personasciencebench/science_personas/phase1.py`: offline arm generation,
  50-task manifest and declared-input verification; no execution or scoring.
- `src/personasciencebench/science_personas/observations.py`: read-only descriptive
  counts and unmodified native result export.

```bash
uv run --locked python -m pytest -q tests/test_phase1.py tests/test_science_personas.py tests/test_persona.py tests/test_core_boundaries.py
uv run --locked python scripts/check_persona_scope.py
uv run --locked python scripts/check_repository.py
```

The scope check protects 83 original files, including all task/eval code, and
pins the explicitly reviewed simulator correction. It is a release-integrity
check, not TaskEval. See [CI setup](reproducibility.md) for the Linux and SDK jobs.
