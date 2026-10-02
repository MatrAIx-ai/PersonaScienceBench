# BixBench adapter

The adapter converts 205 questions from the pinned BixBench 1.5 dataset. The initial conversion inventory found 145 asset-ready cases; 60 had unresolved input-file roles. Conversion and runtime readiness are separate. See the [inventory](../../reports/conversion_v2/conversion_summary.md).

## Conversion and collaboration

Preserve the exact question, named methods, variables and native inputs. Automated capsule/member filtering and schema extraction produce public assets and source-attributed simulator context. Native reference notebooks and answer-bearing annotation fields are excluded from actor and simulator inputs. Unresolved input roles block preparation rather than silently exposing a complete archive.

Schema facts can also be discovered by inspecting public data; interaction does not imply exclusive simulator knowledge. The shared protocol reviews an approach, then executed analysis and evidence. Current persona-on and persona-off conditions both permit general knowledge. See [conversion rules](../design/conversion_revision_v2.md) and [the interaction protocol](../interaction_protocol.md).

Capsule identity is retained as provenance. Capsules with byte-identical data can belong to one study: for example, `bix-2`, `bix-7`, `bix-14`, `bix-20` and `bix-47` share exome inputs. Group those together when selecting or splitting tasks. Original CHIP notes retain layout/label explanations; aggregate missingness, cohort counts and join outcomes must be computed by the actor.

Source revisions, archive/member hashes and grader hashes are pinned. Acquisition and preparation are explicit operations; conversion alone does not install scientific packages. Only selected public assets enter the isolated runtime. Use the [setup guide](../reproducibility.md) to acquire data and recreate environments.

## Submission and grading


Submit a final `Submission` with the answer, an `analysis` artifact, and
`payload.executed_analysis=true`. The analysis artifact and execution declaration
are an explicitly labelled PersonaScienceBench submission gate. They preserve
the completed-analysis track; they do not prove successful scientific execution.
Artifact collection and hashes belong to the shared submission/runtime layer.
A plan or missing execution declaration cannot receive a full-workflow score.

`evaluate(episode, submission, judge=...)` invokes the selected native
`OpenEndedGrader` classes through a small facade implementing the upstream
`call_single` response surface. The injected shared judge chooses the actual model
and provider. No API client, credentials, model default, or network call is hidden
inside the adapter.

Only hash-pinned grader classes and literal prompt templates are loaded using an
AST allowlist. This executes native grading logic without importing the upstream
notebook runner, `aviary`, or `lmi`. The adapter deliberately avoids
`GradeAnswer.grade`, whose debug prints include reference answers.

The evaluator ID is `bixbench-1.5-native-openended-49311180-psb-0.1`. This means the
selected native **online open-answer grader**, not a claim to reproduce the
separate paper trajectory-postprocessing/MCQ pipeline. The dataset `eval_mode`
is retained, and native wrapper defaults `partial_match=False`, `llm_match=False`
are explicit.

Important native behaviors are preserved and tested:

- The native `range_verifier` uses an **LLM comparison**, not the
  deterministic numeric-range helper.
- `OpenEndedGrader` passes its generic `OPEN_ENDED_GRADING_PROMPT` in range mode,
  even though the source also defines a dedicated range prompt. We preserve that
  actual call path instead of silently substituting the other template.
- Only a parsed `<grade>correct</grade>` is correct. Refusal and malformed native
  responses become incorrect, and the native `refusal` field remains false.
  This parser behavior is recorded; repairing it would require a new variant.
- The unrelated deterministic range helper has an unassigned local on its
  incorrect branch. This adapter never invokes that helper and does not claim to
  have repaired upstream MCQ grading.

Outputs preserve `grade` (0/1), `correct`, and `refusal`. They also retain
attempted/submitted/evaluated/scored counts, denominator one, template/request
hashes, and evaluator identity. Missing submissions, absent judge configuration,
or provider exceptions remain missing/blocked/error with no invented score.
Raw references and provider exception strings are not included in public errors.
The controller must record the resolved judge model/settings with the run.

## Records and checks

The [completed report](../../reports/full_persona_v2/README.md) contains the historical 30-persona pilot and full traces. `tests/test_bixbench.py` covers source tampering, public/private separation, extraction, grading, missing outcomes and submission gates. Superseded construction pilots remain in Git history, not the current results.
