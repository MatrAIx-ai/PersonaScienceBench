# Science collaboration extension

This extension adds 56 rubric-anchored science attributes and one runnable ODE task adaptation to the supplied PersonaScienceBench repository. Scientific grading remains with the original executable verifier.

Read in this order:

1. [Design and validity boundaries](DESIGN.md).
2. [Complete 56-attribute catalog](ATTRIBUTE_CATALOG.md).
3. [Worked ODE adaptation and commands](ODE_WORKED_EXAMPLE.md).
4. [Step-by-step guide for adapting other tasks](TASK_ADAPTATION_PLAYBOOK.md).
5. [Copyable task conversion record](TASK_CONVERSION_TEMPLATE.md).
6. [Proposed experiment and human-validation protocol](EXPERIMENT_PROTOCOL.md).
7. [Lessons from the five supplied repositories](REPOSITORY_REVIEW.md).
8. [Executed validation and limitations](../../reports/collaboration/VALIDATION.md).

Code is in `src/personasciencebench/collaboration/`; task assets and six persona profiles are in [the example directory](../../examples/ode_collaboration/README.md).

The main implementation includes strict profile validation, deterministic attribute rendering, frozen task rubrics, prospective disclosure, final-review response opportunities, artifact evidence snapshots, an independent-judge interface, an existing-actor session adapter, and the original native-verifier bridge.

The included scripted demo and oracle verifier controls are software-validation artifacts. A paid model experiment, semantic rubric calibration, and real-researcher validation are not represented as completed.
