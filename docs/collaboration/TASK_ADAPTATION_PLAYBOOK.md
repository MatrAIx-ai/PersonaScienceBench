# Task adaptation playbook

Use this procedure to convert one additional task. The completed example is [ODE_WORKED_EXAMPLE.md](ODE_WORKED_EXAMPLE.md), the design rules are [DESIGN.md](DESIGN.md), and the copyable record is [TASK_CONVERSION_TEMPLATE.md](TASK_CONVERSION_TEMPLATE.md).

## 1. Select a task with a usable original verifier

Choose a task with accessible public inputs, an explicit output contract, and a numeric or executable grader. Favor tasks with at least two authentic collaboration opportunities: a consequential methodological choice, an interpretable uncertainty, a model-selection decision, or a report that can be revised after feedback.

Reject a candidate for this first track if it can only be evaluated by inventing a new scientific judge, if its original private reference cannot be isolated, or if the proposed researcher can contribute only an answer-key hint. A task with little research ambiguity may still be useful as a low-interaction control; do not force a dialogue onto it.

For ODE, the agent chooses a symbolic model and validation strategy under a fixed transparent-model contract. A researcher can influence consultation, search scope, stopping, and reporting without changing the equations that would pass the original tests.

**Output:** a one-paragraph selection rationale and a statement of what this task cannot measure.

## 2. Freeze the scientific contract before authoring a persona

Record the repository commit and dataset revision; hash the instruction, every input file, verifier scripts, reference files, dependency specifications, and relevant container recipe. Keep the task ID, artifact names, allowed methods, metric definitions, thresholds, time limits, and resource allocation.

Separate source availability from reproducibility. A pinned Dockerfile may still use a moving base-image tag. After a successful build, record the actual image ID/digest, platform, Docker version, and build log. A source lock alone does not pin the entire runtime.

Run one known-bad and one known-good controller-only artifact set through the original verifier. A good control can use oracle data solely to test grading infrastructure. Record it as an oracle control, never an agent solution. If a runtime change is necessary, test parity and document it rather than editing grading thresholds until a control passes.

**Output:** `source.lock.json`, native contract table, and two verifier receipts with provenance.

## 3. Build an information-access table

For each field or file, assign exactly one default owner: actor, researcher/controller, or scientific evaluator. Export public inputs from an allowlist. Do not recursively copy the parent repository to the actor.

| Example item | ODE owner | Rationale |
|---|---|---|
| Original instruction and training/validation data | Actor | Already public in the original task |
| Original public parser/checker | Actor | The native task explicitly provides it |
| Researcher delegation and reporting preferences | Controller until disclosed | Authored collaboration scenario |
| Broad public numerical guidance | Researcher and actor | May be explained, but is not secret scientific knowledge |
| Hidden equations and clean evaluation trajectories | Evaluator | Required only for native scientific grading |
| Independent rubric and disclosure ledger | Controller/judge | Actor receives understandable requests, not the private scoring file |

Add a canary to private synthetic unit fixtures and verify it never appears in exported actor or researcher packets. Keep upstream benchmark canaries intact. Test the actual mount layout in an isolated runtime; an `actor/` directory beside private files is not sufficient if the actor can read its parent.

**Output:** a reviewed visibility manifest, an actor-only export, and boundary tests.

## 4. Write a knowledge ledger independently of the persona

Each approved fact needs an ID, exact content, source revision, source path and locator, provenance hash, visibility, allowed trigger, and a known/unknown status. Classify it as native public requirement, optional domain context, authored preference, or unknown. Never present an authored preference as a source fact.

Ask whether disclosing the fact gives away the answer. A measurement unit may be legitimate context; a hidden fitted coefficient is not. Also ask whether the fact is already obvious in public material. If so, do not award the agent a special discovery bonus merely for asking the researcher to repeat it.

Keep all approved facts constant across the default persona comparison. Expertise alone does not alter access. Record unanswerable questions and the permitted response: acknowledge uncertainty, suggest inspecting available data, or request a justified assumption. Do not let a language model fill missing fields with a plausible story.

**Output:** a fact table plus an explicit unknown list and answer-leakage review.

## 5. Bind attributes to actual task affordances

Start from the 56-attribute catalog. Select roughly four to twelve relevant dimensions for the initial task pilot; this is a practical prompt and coverage choice, not a claim that twelve is optimal.

For each selected dimension, fill a binding record:

```json
{
  "attribute_id": "decision_delegation",
  "task_opportunity": "A consequential model-family expansion remains optional.",
  "researcher_need": "Consult before expanding the search, with options and a recommendation.",
  "disclosure_trigger": "workflow question or first plan/progress",
  "required_response_evidence": "A post-disclosure question or decision record tied to the actual expansion.",
  "not_applicable_when": "No consequential expansion occurs."
}
```

Do not activate power-analysis preferences on a task with no experiment-design decision, missing-data preferences on fully observed data, or literature preferences when no literature step is relevant. Do not score inactive dimensions as passed.

Assign profile levels independently of role. Create at least one matched pair differing in exactly one active dimension. Use role bundles for ecological stress tests; use matched contrasts to study a particular attribute.

**Output:** explicit complete profiles, active-attribute list, and one-attribute contrast check.

## 6. Author a disclosure schedule with fallbacks

Specify an opening, allowed question topics, event triggers, fallback disclosures, deadlines, and the final-review behavior. The agent should be able to ask in ordinary language; any topic field is routing metadata, not a substitute for semantic evaluation of question relevance.

If a need can affect a scored action, disclose it before that action or give a real revision opportunity. A researcher asking for a different report format after the episode closes is a scheduler failure. Do not punish the agent retroactively.

The ODE schedule can be copied structurally:

1. Opening: explain the available researcher support and that final review may require one response.
2. Relevant question: disclose the requested approved material.
3. First plan/progress: disclose workflow preferences if not already known.
4. First draft/attempted final: disclose review requests if not already known.
5. Subsequent final: seal the actual scientific artifacts.

Do not copy ODE-specific text or topic names into an unrelated task. Bind them to that task's decisions. Preserve a final response slot, and specify how wall-time or model-step exhaustion is classified.

**Output:** a deterministic state machine and tests for first-final, skipped-plan, no-question, budget-exhaustion, and late-disclosure paths.

## 7. Freeze an evidence rubric before running agents

For every criterion record: ID, construct, bound requirement, 0–3 anchors, activation gate, applicable opportunity, allowed evidence type, and weight. Use scientific invariants as universal constraints; use persona preferences only after they are communicated.

Write at least four discriminating examples per criterion:

- A clearly satisfied case with the correct evidence.
- A clear violation.
- A polished acknowledgment with no implementation.
- A genuinely inapplicable or unobservable case.

For artifact-dependent criteria, add a false-claim case with an unchanged or contradictory artifact. A semantic judge must distinguish it from a successful revision. Do not rely only on keyword matching, an agent's self-report, or a simulator saying it is satisfied.

The implemented scorer checks references and temporal opportunities; it cannot determine whether a paragraph proves a scientific claim. Review semantic decisions with independent annotators and a judge calibration set. Invalid judge output should trigger a bounded repair or a judge-error status, not a default score.

**Output:** versioned rubric JSON, calibration examples, expected judgments, and a documented disagreement process.

## 8. Implement the adapter using existing boundaries

The new `collaboration/session.py` demonstrates how to reuse `EpisodeSession` and the existing actor interface. Questions, plans, and progress enter the disclosure controller. An attempted final can return feedback. Once final review is complete, the original session seals the three native artifacts, and the original native adapter grades them.

For a new task, replace the ODE task check, topic list, public guidance, preference binding, and artifact evidence selection. Do not bypass source integrity checks or reimplement a scientific metric in the interaction scorer. A task using a numeric-answer grader should retain that grader; a task using program replay should retain that replay contract.

Keep state per episode. Save the resolved profile and catalog hashes privately, a frozen rubric, the disclosure ledger, public dialogue, artifact snapshots, native submission receipts, runtime settings, and errors. Do not expose hidden model reasoning to the simulator. If an actor's tool output needs to become researcher-visible, require an explicit shared-progress event or another reviewed disclosure path.

**Output:** an importable adapter, a runnable example command, and a diagram of actual process/mount boundaries.

## 9. Run adversarial and scientific checks

Verify the following behaviors before a model pilot:

| Check | Expected outcome |
|---|---|
| Unknown persona field or invalid level | Validation error |
| Unknown fact or request for gold answer | Grounded unknown response |
| First final before review | Feedback with a response opportunity |
| Criterion added after the run | Digest/manifest mismatch |
| Evidence from before disclosure used as the sole satisfaction proof | Rejected |
| Full artifact credit based only on an acknowledgment | Rejected |
| Missing evidence | Unobservable, not automatic pass |
| Actor artifact modified after sealing | Sealed scientific/evidence snapshot remains fixed |
| Source instruction, data, or verifier changed | Source-integrity error |
| Deliberately wrong scientific artifact | Native reward indicates failure |
| Controller oracle artifact | Native reward indicates success; label as infrastructure control |

Also test a no-question path and a scientifically correct but uncooperative path. A benchmark should not require questions just to accumulate interaction points. Test a cooperative but scientifically wrong path to confirm that good collaboration does not overwrite native failure.

**Output:** machine-readable validation report and reproducible commands, with failures retained.

## 10. Conduct a small human-reviewed pilot

Before a large sweep, have at least one domain reviewer inspect fact provenance and scientific invariance, and a separate reviewer inspect preference applicability and rubric discrimination. These are recommended research quality gates for release; they are not represented as already completed for this implementation.

Run matched persona contrasts under the same actor model, task inputs, native runtime, model-step policy, seeds, and information pool. Randomize condition order. Inspect zero-question trajectories, misleading success claims, late steering, and failures in addition to successful examples. Compare simulator variants before asserting that differences reflect real human behavior.

Advance a task only after the reviewers agree that it is scientifically unchanged in the declared sense, the interaction opportunities are real, and the rubric separates meaningful behavior from prose-only compliance. Mark the task as authored, mechanically validated, domain reviewed, and pilot validated using distinct fields.

**Output:** signed review notes, simulator/rubric calibration results, and a declared task release status.

## 11. Report coverage and preserve comparability

Publish source-task counts separately from independent-study counts and persona assignments. Report native outcomes, interaction scores, score coverage, researcher-effort proxies, simulator validity, and runtime/judge failures. Include the actual number of applicable opportunities for every metric.

For a study-level summary, aggregate across independent tasks or studies rather than treating every turn as an independent observation. Keep information-redistribution conditions, network changes, added step limits, and design-only tasks distinguishable. Do not average incomparable native metrics across benchmark families without a predefined normalization and an explicit justification.

**Output:** the completed task card, exact experiment configuration, public release bundle, and restricted controller artifact policy.
