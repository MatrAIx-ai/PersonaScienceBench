# Benchmark modification standards

Version: development standard 0.2, 2026-09-25.

These rules govern task conversions, researcher simulators, persona variants,
actor integrations, and reporting in PersonaScienceBench. The source-specific
implementation sequence is in
[current conversion implementation](design/conversion_revision_v2.md).

MUST denotes a requirement for a conforming conversion. SHOULD denotes a default
whose departure needs a recorded rationale. MAY denotes an optional extension.
Recording a departure does not require a new user approval step; work within the
authorized scope and label changed experimental conditions accurately.

**1. Preserve a well-defined scientific task**

- A converted episode MUST retain identifiable source task IDs, a scientific
  objective, required deliverables, and an explicit evaluation contract.
- The conversion MUST preserve fixed scientific constraints such as outcome
  definitions, required methods, units, thresholds, data splits, and output schemas.
  An intentional change creates a new task/evaluation variant with a change record.
- Essential access information, actual resources, output formats, and basic task
  scope MUST be public. Additional requirements communicated by the researcher
  MUST be discoverable and available under the configured interaction budget.
- Tasks SHOULD be selected for legitimate researcher context or useful scientific
  decisions. Do not remove arbitrary details or invent missing facts solely to
  make the actor ask questions.
- Several questions MAY share an episode only after reviewing scientific
  coherence, answer dependencies, and scoring. Shared data alone is insufficient.

**2. Separate public, researcher, and evaluator information**

| Boundary | Permitted content | Excluded content |
| --- | --- | --- |
| Actor | Public brief, allowed files/tools, runtime facts, public requirements, shared researcher replies | Private context files, reference answers, hidden tests/results, solution code |
| Researcher | Reviewed knowledge, fixed constraints, persona, shared dialogue/progress, explicitly shared artifacts | Reference answers, hidden grader state, gold solution code, unseen actor reasoning or files |
| Evaluator | Required references, submission, and the permitted evidence needed by its scoring contract | Supplying hidden grading feedback to the actor or researcher during the episode |
| Controller | Source records, versions, access policies, event storage, evaluator configuration | Exposing its private stores or credentials through model-visible mounts/tools |

- Exporters MUST use explicit field/file allowlists. Copying a complete source row,
  paper, notebook, README, or metadata file is not an acceptable default export.
- Reference material MUST remain inaccessible through filesystem mounts, tool
  endpoints, logs, retrieval indexes, and network routes controlled by the runner.
  A `.private` filename alone does not enforce this boundary.
- Legitimate labels and metadata already supplied as native task inputs MAY remain
  visible after review. Context that helps solve a task is not automatically leakage;
  the relevant distinction is whether it belongs to the allowed input contract.
- Offline curation MAY inspect references to identify leakage. Runtime researcher
  knowledge MUST still be justified by permitted source context, not generated
  by reverse-engineering the desired answer.
- Public development checks MAY provide normal execution feedback. Hidden final
  evaluator outputs MUST NOT become an iterative hint channel.

**3. Ground researcher knowledge**

Each approved fact MUST contain at least:

```json
{
  "fact_id": "study-a.sample_pairing",
  "topic": "sample_design",
  "content": "A reviewed, source-supported statement.",
  "kind": "context",
  "provenance": {
    "source_revision": "pinned revision",
    "source_path": "path in the pinned source",
    "source_locator": "JSON pointer, table cell, or text span"
  },
  "disclosure_policy": "on_relevant_question"
}
```

- Distinguish `context`, `fixed_requirement`, and `optional_advice`. State
  uncertainty and unsupported details explicitly; preserve qualifiers in sources.
- Every fact MUST have a stable ID and inspectable provenance. A missing fact
  MUST remain unknown unless a new source-backed revision is curated.
- Researcher responses MUST preserve permitted scientific content. General
  scientific explanation or suggestions must be identified as such and enabled by
  the declared policy; they cannot introduce unsupported task-specific facts.
- Fact IDs alone MUST NOT be treated as proof that every sentence is grounded.
  Implement and record checks for unsupported additions; use approved wording or
  an explicit unknown response when support cannot be established.
- Researcher statements about hardware, installed packages, or file availability
  MUST agree with the actual runtime manifest. A source paper's hardware is not
  evidence of resources available to the actor.

**4. Keep persona separate from knowledge and objectives**

- A persona MUST be a versioned configuration separate from the task fact pack.
  Examples of supported behavior are concision, technical vocabulary, initiative,
  and requesting evidence before accepting an interpretation.
- In a style-only comparison, available knowledge, fixed requirements, and
  disclosure policy MUST remain the same across personas. Actual questions and
  disclosures may differ as interactions evolve; record those differences.
- Changes to expertise access, initiative/disclosure policy, advice permissions,
  or task objectives MUST be labelled separate experimental factors. They cannot
  be attributed solely to communication style.
- Personas MUST NOT change reference answers, fabricate evidence, or override the
  task's required scientific method, scope, thresholds, or submission contract.
- External persona sources MAY be mapped into the common schema. Keep relevant
  researcher behavior explicit; do not infer scientific competence from unrelated
  demographic attributes. Record the mapping/version when using MatrAIx profiles.
- Maintain an extractive or otherwise tightly grounded neutral control alongside
  more expressive persona conditions. Grounding remains required in every mode.

**5. Define conversation and memory behavior**

- Execution/design collaboration MAY require an approach review and a result
  review under the declared protocol. These checkpoints MUST be counted separately
  from optional clarification or revision rounds. No minimum number of additional
  questions or performance reward for longer conversations is permitted.
- A native clarification benchmark MAY retain its original dialogue and final
  specification boundary rather than adding artificial approval exchanges.
- Actor tool calls and researcher–actor messages MUST be recorded as distinct
  event types. Tool use alone does not count as researcher interaction.
- Researcher memory MUST persist within an episode and reset between independent
  episodes. Actor memory follows the same episode boundary. Related questions
  share memory only if explicitly grouped into one episode.
- The researcher MUST see only shared messages/progress and permitted knowledge.
  It MUST NOT automatically receive private actor reasoning, unrelated files,
  other episodes, or evaluator feedback.
- Proactive researcher messages MAY occur under a documented trigger policy,
  such as an explicitly shared progress update. Log the trigger and visible input.
- A plan checkpoint MUST record its time, trace prefix, submission, and disclosed
  context. Later facts or results MUST NOT be added retroactively to that checkpoint.

**6. Use a common contract with independent runtimes**

Each adapter MUST automate catalog conversion without per-case editing. It MUST
produce either a versioned package or a recorded exclusion, and distinguish asset
readiness from successful execution. Exact-source model classification MAY be used
when field/section rules are insufficient; preserve the extraction trace, cache key,
and automated review status. Unknown file roles MUST block readiness.

Every adapter MUST expose these capabilities, though implementation details may
differ:

| Interface | Responsibility |
| --- | --- |
| Enumerate source tasks | Stable native identities, versions, study groups, and availability |
| Export episode | Public context, researcher knowledge, asset mapping, submission contract, evaluator locator |
| Prepare runtime | Actual files, packages/resources, allowed tools, and declared isolation |
| Researcher interaction | Questions, optional shared progress, grounded replies, per-episode memory |
| Submit result | Typed artifact/answer manifest, immutable checkpoint, explicit termination status |
| Evaluate submission | Source-specific metrics, evaluator version, evidence, errors, and denominator |

- Actor execution MUST remain replaceable. No conversion may depend on access to
  a particular model's internal reasoning representation or a proprietary trace.
- OpenHands, notebook agents, terminal agents, and external runners MAY use
  separate environments. The common layer SHOULD support a Python API initially
  and a transport-neutral JSON contract for HTTP/CLI integrations.
- Actor, researcher, and LLM judge configurations MUST be independent. OpenRouter
  is an inference provider, not the required agent execution framework.
- Use a logical asset manifest with paths, hashes, visibility, and mount mappings.
  Do not require workspace-specific absolute paths or mount the raw source collection.
- Asset provisioning failures MUST be reported before interpreting task scores.
  Preserve native resource limits or declare a distinct altered-budget track.
  EXP's current design step limit is not a universal limit for full scientific tasks.
- Costs and resources MUST be recorded. Do not introduce monetary caps implicitly;
  enforce them only when configured for the run.

**7. Keep scoring scientifically interpretable**

- Preserve each source's metric names, scales, references, and aggregation unless
  a documented evaluation variant intentionally changes them.
- Native execution verifiers MUST remain execution verifiers. Do not replace
  them with an LLM score merely to obtain one shared judge across all sources.
- For LLM-scored tracks, retain the selected Sonnet judge configuration unless
  explicitly changed for an experiment. Record the resolved model ID, provider,
  prompt/template hash, generation settings, parser, and any repeated samples.
- A changed judge, prompt, parser behavior, logprob weighting, or aggregation MUST
  produce a new evaluator version. If a deployment lacks a required capability,
  fail explicitly or use a predeclared labelled variant; do not silently fall back.
- `design_only` scores MUST describe designs only. `full_workflow` scores MUST
  apply to the required executed analysis, program, or artifacts. An unexecuted
  plan cannot receive a native completed-analysis score.
- EXP reference coverage and its integrity gate remain distinct recorded results.
  The discarded artificial design-quality rubric MUST NOT be reintroduced as a
  default metric. No universal subjective collaboration score is required.
- A successful process exit, a generated notebook, or a submitted report MUST NOT
  alone be described as scientifically correct. State what the source grader verifies.
- Extra valid discoveries beyond a reference MAY be recorded separately. Do not
  automatically claim the native reference score measures their scientific value.
- Benchmark-specific scores MUST be reported separately. Converting scales to
  0–100 does not make the underlying constructs equivalent. Any aggregate needs
  declared weighting and an explicit interpretation.

**8. Record failures, comparisons, and repeated attempts honestly**

- Every attempted episode MUST remain in the run record, including no submission,
  timeout, execution failure, provider failure, and judge failure.
- Distinguish scientific failure from infrastructure/evaluation failure. A missing
  score remains missing unless a predeclared reporting policy assigns a penalty.
  Preserve the original status even when computing a penalized aggregate.
- Reports MUST state attempted, submitted, evaluated, and numerically scored
  counts, and the denominator for every mean or success rate.
- Retries MUST be explicit and logged. Do not silently replace failed or low-scoring
  episodes with successful reruns or select the best attempt after seeing results.
- Persona comparisons MUST hold tasks, actor configuration, resources, knowledge,
  and evaluator fixed unless a named experimental factor changes one of them.
  Record seeds when supported; a seed is not a guarantee of deterministic APIs.
- Include a neutral interactive condition and an all-approved-context control when
  estimating the effect of researcher interaction. Neither control includes gold
  answers. Do not attribute score differences to the simulator in episodes with
  no researcher interaction or without accounting for actor trajectory variation.
- Keep related papers, datasets, capsules, and overlapping variants grouped for
  splitting and statistical analysis. Report question/task counts separately from
  independent study counts; check cross-source overlap where provenance permits.

**9. Version sources and make conversion changes reviewable**

An episode MUST record the following, split between public and private controller
records according to the information boundaries above:

| Record | Minimum information |
| --- | --- |
| Source | Benchmark, repository/data revisions, native IDs, study group, attribution |
| Conversion | Adapter/schema version, exact field moves/edits, reasons, review status |
| Knowledge | Fact-pack version/hash, source locators, unknowns, disclosure policy |
| Persona | Profile/version, behavior settings, external mapping if used |
| Runtime | Runner/version, assets and hashes, environment/image, actual resource limits |
| Submission | Track/stage, answers/artifact hashes, timestamp, trace/checkpoint reference |
| Evaluation | Evaluator version, metric definitions, reference hashes, judge settings if applicable |
| Result | All role configurations, status/errors, metrics, denominators, resource/cost usage |

- Raw upstream snapshots MUST remain reproducible. Put modifications in our
  adapters and versioned overlays; record any necessary upstream patch explicitly.
- Preserve original taxonomies alongside normalized domain labels. Source counts
  and inventories MUST identify the inspected revision and counting unit.
- Preserve licenses, attribution, canaries, and source redistribution restrictions.
  Publish acquisition instructions instead of restricted gold/data bundles.
- Credentials MUST stay outside source files, task packages, model inputs, and
  recorded authorization headers. Redact secrets from logs without deleting
  scientific evidence needed to interpret the run.

**10. Criteria for accepting a converted task**

Use recorded evidence for the checks below before marking a task ready:

| Check | Required evidence |
| --- | --- |
| Scientific identity | Source IDs, coherent objective, fixed requirements, and native output contract |
| Useful researcher role | Source-backed context/advice and a reason interaction could help; no mandatory dialogue quota |
| Information separation | Public/researcher exports reviewed; reference fields and hidden artifacts excluded from their access |
| Grounding and persona | Facts have provenance; unknowns remain explicit; renderer checks/fallbacks and persona factors documented |
| Runtime readiness | Required assets resolve and the selected runner can produce the required artifact format |
| Scoring compatibility | Correct source split/version, native submission mapping, documented scoring changes, and error handling |
| Reporting | Missing outcomes and denominators preserved; related-study identities available |
| Reproducibility | Source, conversion, knowledge, persona, runtime, and evaluator versions recorded |

Automated checks SHOULD target meaningful failure modes: nested answer fields
escaping an allowlist, malformed question/answer separation, unauthorized fact
disclosure, wrong artifact mapping, and disappearing missing results. Scientific
context review cannot be replaced by schema validation alone.

Use the narrow checks needed for the change. Documentation edits need link and
consistency checks; changed parsers need representative and leakage cases; changed
runtime or grader integrations need appropriate execution checks. Broad or paid
benchmark reruns are not an automatic requirement for every edit. Mark unverified
capabilities and unavailable assets explicitly instead of implying readiness.
