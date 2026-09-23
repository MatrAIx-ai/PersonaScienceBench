# Researcher and actor interface

`Episode` is an operator-private record. `Episode.actor_input()` is the only
default model-visible projection. Do not mount this repository, its source
checkouts, complete episode JSON, private logs, evaluator, or model credentials
inside an actor environment.

## Lifecycle

1. Verify source pins and file hashes; stage only allowlisted public inputs.
2. Create a fresh researcher and actor conversation for the episode. Choose a
   versioned persona and disclosure mode before the first turn.
3. Let the actor inspect data and decide whether clarification is useful.
4. Optionally save an initial plan. In the full-workflow track this does not
   finish the episode or constitute a scientific result.
5. Continue implementation and execution. Only explicit progress messages are
   sent to researcher memory; actor shell activity is not automatically shared.
6. Submit the final answer and artifacts. The controller snapshots artifacts,
   hashes them, and closes the episode against further researcher questions.
7. Evaluate the sealed submission in a separate trusted context. Preserve the
   source's metric and label evaluator adaptations explicitly.

Question limits and actor iteration limits are explicit run configuration.
Neither the protocol nor the actor prompt forces a clarification question.
A run with zero questions is valid; report that count when interpreting the
effect of simulator models or personas.

## Researcher behavior

Only `reviewed` facts are eligible for disclosure. Facts carry provenance,
topic, and one of `context`, `fixed_requirement`, or `optional_advice`.
The simulator cannot turn advice into a new benchmark requirement. It returns
an answer plus fact IDs; unknown IDs, excess disclosure, malformed replies,
and unsupported prose trigger a recorded fallback. Unknown questions receive
an explicit unknown response rather than invented context.

`extractive` mode publishes the selected reviewed text verbatim. `grounded`
mode permits persona expression and checks study assertions against the public
task and selected facts. Configured preferences and clarifying questions may
also be expressed without inventing requirements or resource limits. That
model-based check reduces unsupported content but is not a proof of entailment.
Provider outages are recorded as infrastructure failures. Persona does not alter
the fact pool, reference answer, task requirements, or grade.

The [persona router](personas.md) supports A–G attributes with global, domain and
task overrides. H (knowledge boundary) is derived exclusively from episode
context and controller disclosure rules. Each session saves a private resolved
profile and rendered identity prompt. Injection uses system-message text;
model weights and MatrAIx population datasets are not integrated.

## HTTP bridge

Set an unguessable `PERSONASCIENCEBENCH_SESSION_TOKEN` of at least 24 characters
and start the controller outside the actor sandbox:

```bash
python -m personasciencebench serve \
  --episode prepared/pilot-v1/EPISODE/controller/episode.private.json \
  --artifact-root /path/to/actor/workspace \
  --output runs/independent-controller
```

Use a localhost tunnel when the actor runs elsewhere. Every request requires
`Authorization: Bearer <session token>`. This token authorizes interaction only;
the actor never receives the OpenRouter API key.

| Endpoint | Body / result |
| --- | --- |
| `GET /context` | Public question, documents, environment, expected submission, researcher topics |
| `GET /tools` | Interaction tool descriptions |
| `POST /ask_researcher` | `{"question":"...","topic":"optional exact topic"}` → approved reply |
| `POST /report_progress` | `{"message":"..."}` → record in shared memory |
| `POST /submit_plan` | `{"plan":"..."}` → immutable initial checkpoint |
| `POST /submit_result` | `{"episode_id":"...","stage":"final","answer":"...","payload":{},"artifacts":{"analysis":"analysis.py"}}` → sealed submission |

The actor-side CLI `python -m personasciencebench.bridge OPERATION --payload -`
reads JSON from stdin and uses `PERSONASCIENCEBENCH_ENDPOINT` plus the session
token. Relative artifact paths are resolved against the configured artifact
root. The independent runner must synchronize or quiesce actor processes before
final submission. Controller execution receipts are operator-owned and cannot
be supplied through an actor submission payload.

## Evidence and scoring

Save each actor's final answer, analysis artifacts, observable tool execution,
researcher messages, and native evaluator outputs. Keep API payloads and private
researcher/evaluator records outside actor access. A command exit code or an
actor's `executed_analysis` declaration is not proof of scientific correctness.
Reference-answer graders measure reference agreement; they are not independent
execution verifiers. Native verifier failures and missing assets remain distinct
from scored scientific failures. Do not average unlike metrics across sources.
