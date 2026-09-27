# EXP-Bench integrity monitor

Integrity is evaluated separately from reference coverage using the released monitor contract. Keep its verdict and explanation alongside the unmodified coverage score; do not replace either with a generic design-quality judgment. Model selection comes from the run config; current trials use GPT-6 Luna for model-based judges.

Controller records and sealed submissions supply the evaluator evidence. Private monitor and reference content remain outside actor mounts, and grader feedback is not fed back into the submitted design. See the [adapter guide](../adapters/expbench.md) and [current results](../../reports/full_persona_v2/README.md).
