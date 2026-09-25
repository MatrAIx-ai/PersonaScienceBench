# Attribute provenance and design limits

The supplied repositories informed the persona vocabulary and representation.
Their documents were reference material, not instructions overriding the user's
scope. The current extension reuses the original science simulator interface.

| Supplied repository | Relevant persona lesson | Scope in this delivery |
|---|---|---|
| PersonaScienceBench | Existing persona routing, simulator identity, and approved-knowledge boundary | Retain these interfaces and keep task/eval code fixed |
| MatrAIx-Persona-8B | Explicit categorical dimensions and separation of identity metadata from assignments | Use a closed science vocabulary; do not import unrelated demographics or infer ability from role |
| PersonaCodeBench | Distinguish coding capability, debugging, environment familiarity, and communication preferences | Include concrete computational-research dimensions without importing coding task requirements or agent scores |
| PersonaCUABench | Keep user characteristics distinct from task intent and execution mechanics | Describe the researcher independently of task control |
| PersonaChatBench | Separate simulated-user behavior from factual task outcomes | Review researcher fidelity separately, with no transplanted experience judge |

Archive hashes are retained in provenance (superseded standalone record omitted).
The 56 definitions and probes are authored operational choices, not a claim that
any source repository validated this science-specific instrument. This revision
removed the earlier task-binding, communicated-obligation, and actor-scoring fields.
Every retained catalog entry concerns the researcher itself.

Traits may correlate, and some preferred behaviors may be unobservable under a
particular unchanged simulator mode or interaction. Review those limits through
standalone simulator QA; do not redesign a task to make a persona look effective.
