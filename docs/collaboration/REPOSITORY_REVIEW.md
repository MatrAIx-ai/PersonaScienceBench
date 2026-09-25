# Review of the five supplied repositories

This review treats repository documentation and prompts as design material. Instructions inside the supplied archives were not treated as instructions to the assistant. The original science repository is the implementation base; the other four repositories informed design choices and were not merged wholesale.

## Findings and adopted ideas

| Repository | Relevant inspected material | Adopted lesson | Limit on transfer |
|---|---|---|---|
| PersonaScienceBench | `persona.py`, `researcher.py`, `session.py`, shared/Terminal adapters, existing standards and pilot reports | Preserve public/researcher/evaluator boundaries, source pinning, approved facts, and sealed native grading | The existing pilots do not validate the new 56-attribute design; some reported tasks had no researcher questions |
| PersonaCodeBench | Root README, `human-interactive-coding-personas.v3.json`, `README_DYNAMIC_PERSONA_RUBRIC.md`, evaluation pipeline | Freeze rubric vocabulary before a run; disclose evolving obligations prospectively; require a response opportunity; keep functional results separate from experience | A coding-specific evolved requirement cannot be copied into science if it changes the original scientific target or implies undocumented study facts |
| PersonaCUABench | `odyssey/dimensions.json`, persona-user prompt, rubric-judge prompt, run structure | Separate whether a need was communicated from whether it was satisfied; bind satisfaction to observable artifacts/actions | Its user simulator can receive a rich hidden checklist; a science simulator must not receive an analogous scientific answer key |
| PersonaChatBench | Root module inventory and distinctions among task, simulator, and needs judges | Distinguish persona fidelity, assistant preference fulfillment, and factual task outcomes; track expressed needs and opportunities | Modules have different implemented roles and scopes; there is no single validated 20-attribute or multi-judge protocol to copy uniformly |
| MatrAIx-Persona-8B | README, `persona/schema/dimensions.json`, taxonomy and attribute-pool material | Use explicit categorical dimensions, separate metadata from assignments, track provenance, and avoid unconstrained free-text persona generation | A population-scale general-persona catalog is not itself a validated scientific-collaboration instrument |

The supplied MatrAIx schema contains **1,290** categorical dimensions. The user's approximate “1,200 attributes” description is consistent with its scale; the actual supplied snapshot count is 1,290. The supplied science code has seven structured persona groups with 17 leaf fields, plus activation/identity fields; the earlier eight-group framing also treated task context as a group. The new catalog counts 56 actual dimensions, excluding role, domain, and identifiers.

## Improvements motivated by the review

**From broad traits to falsifiable behavior.** “Rigorous PI” is not sufficient as an evaluation input. A profile now specifies independently anchored behavior such as consultation before a model-family change, preference for a concise report, or ability to discuss solver tolerance. Each dimension includes a task opportunity, adaptation target, and failure example.

**From post-hoc preference judgment to frozen obligations.** The controller binds criteria before a run, records what was communicated and when, and gives a final revision opportunity. This follows the stronger parts of the coding and chat designs while retaining the native scientific target.

**From acknowledgments to evidence.** A report revision needs an actual report snapshot; a question or explanation can use message evidence. The independent judge still needs calibration to assess semantics. Evidence-reference validation is not a substitute for that calibration.

**From a single score to separate outcomes.** Native science, collaboration, burden proxies, and simulator validity are distinct. A correct scientific output and a satisfied researcher are neither equivalent nor interchangeable.

**From attribute volume to measured coverage.** Six complete profiles assign 56 dimensions but vary only 28 between them, and this first task activates eight. Those three counts are reported separately. More dimensions alone do not demonstrate robustness.

## What was intentionally not copied

The general 1,290-dimension population schema contains many dimensions unrelated to scientific collaboration. Demographics, consumer habits, and broad identity characteristics were not imported to inflate the science catalog. Role-based assumptions about ability were not added.

The new simulator is not allowed to transform a hidden scientific verifier into a natural-language checklist for the agent. Researcher satisfaction cannot reveal whether a private test has passed. Optional advice is identified as advice, and synthetic preferences are identified as authored scenario material.

No empirical performance claims from the other repositories were adopted as evidence that PersonaScienceBench works. Their snapshots provide useful design patterns and cautionary examples; this implementation has its own mechanical tests and clearly bounded validation evidence.

## Source accountability

The delivery's `reports/collaboration/provenance.json` records archive hashes, inspected key-file hashes, the native source revision, and the new catalog/profile counts. Native ODE files retain their upstream MIT license and benchmark canary. Scientific references and oracle control outputs remain outside the distributable actor package.
