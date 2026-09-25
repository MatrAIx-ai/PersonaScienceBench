# Persona-only revision

## Resulting scope

The selected science persona is injected into the existing researcher simulator.
Scientific tasks, TaskEval, approved context/disclosure policy, actor tools,
resource limits, and submission lifecycle retain the supplied implementation.

## Added

- `science_personas/`: 56 researcher attribute definitions, complete profile
  validation, deterministic rendering, JSON Schema, explicit one-attribute
  contrasts, and offline validation/render/config-attachment commands.
- Six complete profiles, a simulator-only injection preview, English integration
  and team instructions, and separate researcher-fidelity review material.
- Regression checks for private injection, unchanged task/eval inputs and
  budgets, original first-final acceptance, and exact legacy rendering/records.
- A release scope manifest and audit for the original code/configuration files.

## Minimal existing-code edits

- `persona.py`: an optional `science_profile`, effective-preference payload, and
  versioned private metadata. Existing legacy routing and rendering are retained.
- `researcher.py`: unify on/off common instructions and policy metadata; remove
  the extra profile input from the grounding checker. Identity in the private
  system prompt is the only treatment. Fact filtering, response validation,
  lifecycle, budgets and the per-request call sequence remain unchanged.
- `science_personas/phase1.py` and `observations.py`: controlled-arm planning,
  declared-input checks and descriptive export; no scientific executor or grader.
- `pyproject.toml`: package the new catalog resource. Dependencies/lock unchanged.
- README/persona documentation point to the simulator-only material.

## Removed from the previous delivery

The task-bound collaboration controller, active-attribute projection, mandatory
review/revision loop, collaboration scorer, alternative session/runner, task-card
bindings, copied ODE task package, native-control generator, and task-adaptation
playbook are removed. Their earlier results are not presented as validation of
this revision. The original repository's own task implementations and historical
reports remain unchanged.

The prior offline-CI dependency/test fixes remain. They install Bubblewrap,
exercise the optional SDK separately, and correct offline fixtures/assertions;
they do not alter scientific grading. See the new validation report for results
measured on this revision rather than counts inherited from the old extension.

## Phase 1 correction

The prior persona-only release still changed the off reply policy and supplied
a profile to grounding. Those confounds are corrected here. The new experiment
plan distinguishes whole-profile examples from one-dimension arms, requires the
same 50 tasks, and labels the 12-arm/600-episode allocation as a proposal. The
actual 50-task list and live scientific runs have not been supplied/completed.
