# Current interaction protocol

The full-persona study uses the same task, budgets and common simulator instructions across persona conditions. Only the simulator identity changes. The actor receives researcher messages, not the hidden profile or evaluator references.

## Execution and design tracks

Discovery, Bix, ASI and EXP use `active_researcher` / `researcher-review-v2`:

1. The researcher requests input inspection and a proposed approach.
2. The actor reports a plan, evidence, assumptions and uncertainties.
3. The researcher approves the approach or requests a focused clarification.
4. The actor performs the analysis or writes the experimental design and submits a result handoff.
5. The researcher requests an identifiable revision or concludes. The controller seals the deliverable and the native evaluator grades it separately.

The saved pilot allows twelve researcher requests and sixty actor calls per episode. EXP is design-only; no experiment execution is required. Execution tracks require the native artifacts and evidence. Missing submissions remain explicit outcomes.

Shared handoffs contain actor-selected evidence; the researcher does not inspect private tool logs automatically. In the current tool interface, plan/result handoffs are mandatory. Extra reviews measure simulator activity; questions or proposals inside actor messages measure actor initiative. Do not label every handoff as spontaneous engagement.

The current controller allows stopping only during result review. An unreadable input can therefore trap a cautious researcher in approach review. Preserve that behavior in historical interpretation; see the [case study](../reports/full_persona_v2/case_studies.md). Any future protocol change needs a new run version.

## SciConv

SciConv keeps its native ambiguous/inconsistent request and intended-specification split. The actor asks clarification questions or returns `[COMPLETE]`, with up to ten question turns and a final attempt. The full identity conditions the simulated user's answers. Its first actor question precedes persona exposure. Native judges assess specification recovery, intent and conversational grounding; no scientific solver is executed.

## Records and boundaries

Save full shared messages, model requests/responses, tool events, submissions, native grades and termination reasons. Task requirements stay source-attributed; general knowledge and suggestions are allowed in the current on/off conditions. References, hidden graders and credentials stay outside actor/simulator access. Legacy optional-question bridge interfaces remain implemented for compatibility and are a different interaction condition.
