# Researcher persona QA

The rubric-based part of this extension is the attribute definition: a concrete
low/medium/high researcher behavior, a diagnostic question, and a contradiction
example. QA concerns whether the simulator realizes that behavior. It does not
score the evaluated agent or modify TaskEval.

## Separate simulator checks

Use a permitted context and a question that could reveal the chosen trait in a
standalone simulator check. Each catalog entry provides one possible probe.
Do not insert these probes into scientific episodes, conceal scientific criteria,
or create extra turns to make all 56 traits observable.

For each reviewed reply, record:

- Profile ID/version, catalog and prompt hashes, and the selected attribute level.
- The permitted context, question, relevant researcher reply, and turn identifiers.
- `observed_consistent`, `observed_inconsistent`, or `not_observed`, with quoted
  researcher evidence and an explanation tied to the level anchor.
- Any knowledge-boundary violation, invented resource/requirement, or conflict
  with the existing simulator protocol, independently of apparent style fidelity.

Use the [review template](../../examples/science_personas/simulator_review_template.json).
It contains no agent score, aggregate performance number, or submission gate.
A lack of evidence remains `not_observed`. A fluent but unsupported answer cannot
establish a valid researcher simulation.

## Examples of the distinction

| Attribute | Evidence about the researcher | Not evidence of simulator fidelity |
|---|---|---|
| Explanation depth | The reply is concise or detailed in the manner specified | The agent submitted a long report |
| Decision delegation | The researcher expresses the configured preference when asked | The agent happened not to ask any questions |
| Numerical analysis | The researcher requests appropriate explanation or discusses permitted numerical assumptions | The agent passed the scientific verifier |
| Revision expectation | Optional feedback expresses the chosen refinement preference | A controller forcibly rejected the first final submission |

## Calibration limits

Mechanical tests verify schema constraints, deterministic rendering, unchanged
knowledge boundaries, and integration with the existing simulator. They cannot
establish that a language model consistently realizes all trait levels.

Before making fidelity or realism claims, collect independent reviewer judgments
on repeated replies, relevant follow-up turns, and matched low/high profiles;
inspect disagreements and profile drift. Keep context and model settings fixed
where a single trait is being compared. Record model-based support-check fallbacks,
because they can erase visible persona expression. Use human domain review for
claims requiring domain understanding.

Do not interpret correlated traits as independent validated constructs. Related
pairs such as robustness demand/sensitivity scope and reproducibility detail/
artifact auditability need discriminant review. The catalog is an operational
starting point, not a validated psychometric instrument or a population model.
No human calibration or new model experiment was performed for this delivery.
