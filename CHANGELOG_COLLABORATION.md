# Collaboration extension change record

## Added

- `src/personasciencebench/collaboration/`: 56-attribute catalog; strict profiles and JSON Schema export; task-bound rubric/disclosure controller; evidence and opportunity validation; independent judge integration; original-actor session adapter; source-locked task preparation; native verification; offline demo/CLI.
- `examples/ode_collaboration/`: six complete profiles, one controlled delegation contrast, unchanged native public inputs, task card, source lock, shared-renderer opt-in config, scripted protocol fixture, live entry point, and controller-only verifier control generator.
- `docs/collaboration/`: design, all attribute anchors, complete worked example, detailed adaptation playbook, copyable task template, proposed experiment protocol, and review of the five supplied repositories.
- `tests/collaboration/`: 31 new regression cases, including parameterized cases.
- `reports/collaboration/`: executed validation, native control receipts, original/enhanced test comparison, and source provenance.

## Existing implementation changes

- `src/personasciencebench/persona.py` accepts an optional `science_profile`. When present and enabled, the new catalog renderer is used. Original profiles retain their renderer and legacy record format; explicit persona-off still emits no persona prompt. Scientific facts and evaluator access are unchanged.
- `pyproject.toml` includes `catalog.json` in built Python packages. Runtime dependencies and original scientific adapters were not replaced.
- Repository README and persona guide point to the new extension while preserving historical implementation/results documentation.

## Boundaries

The original native ODE instruction, data, checker, verifier tests, and grading thresholds are unchanged. The added collaboration procedure is explicit. The example live actor inherits the existing no-network actor runtime and declares its model-step cap; these differ from the original task's public-network condition and are documented.

The new full-suite test run retains the original snapshot's seven failures and six setup errors on this host. No new failing tests were observed. No new paid-model results, human validity results, or semantic-judge agreement results are claimed.
