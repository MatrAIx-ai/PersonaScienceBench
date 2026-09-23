# ScienceAgentBench pilot

Both authorized pilots completed in `runs/sab-luna-none-01`. Native task success
was **1/2 (50%)**, and both programs executed successfully. Each fresh program
replay produced bytes identical to the immutable actor submission.

| Task | Domain | Simulator | Actor | Judge | Native task success |
| --- | --- | --- | --- | --- | --- |
| Verified 22, Papyrus filtering | Computational chemistry | GPT-6 Luna, effort none | GPT-6 Luna, effort none | Unchanged native programmatic evaluator | 0/1 |
| Verified 45, perceived stress scoring | Psychology and cognitive science | GPT-6 Luna, effort none | GPT-6 Luna, effort none | Unchanged native programmatic evaluator | 1/1 |

| Task | Valid program | Actor calls | Successful execution commands | Researcher questions | Reviewed facts disclosed | Provider-reported cost |
| --- | --- | --- | --- | --- | --- | --- |
| 22 | 1/1 | 6 | 4/4 | 0 | 0 | $0.00252034 |
| 45 | 1/1 | 6 | 4/4 | 1 | 0 | $0.001386685 |

Total provider-reported cost was **$0.003907025**. The cases ran in parallel in
approximately nine minutes, mostly waiting for cold OpenHands imports on the
cluster filesystem. There were no inference retries, model fallbacks, judge-model
calls, or actor reruns. OpenRouter recorded `openai/gpt-6-luna` through OpenAI
for all 13 completed calls: 12 actor calls and one researcher call.

Papyrus received native failure because its output table differed from the
reference. A separate private diagnostic confirmed that it selected the same
336 activity IDs, while its 32-column output differed from the 34-column reference
and 930 of 10,752 shared-column cells differed after native rounding/string
conversion. Thus this result does not mean that the selected activity IDs were
wrong. The public instruction's request to preserve column names and the extra
reference columns also expose an output-contract ambiguity. The native score
was retained unchanged; no answer or program was repaired.

The PSS program passed the unchanged native grader. Its single researcher
question asked for confirmation of a scoring convention absent from the approved
context; the researcher correctly reported that it was unspecified. No private
reference answer or reviewed fact was disclosed. This two-task pilot verifies
execution and grading integration, not the effectiveness of the simulator or a
persona intervention.

The OpenHands actor receives a maximum of 20 iterations and may choose whether
to question the grounded researcher. The researcher uses the existing neutral
persona, discloses at most one relevant reviewed fact per reply, and retains the
conversation. There is no dollar cap. No LLM judge is called for these tasks.

The user-provided verified archive resolved the earlier SharePoint access
blocker. Its SHA-256 is
`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
Nine reviewed files were extracted privately. Task contracts match the pinned
verified annotation revision; there was no published upstream archive hash to
independently authenticate the supplied archive. All three public input pickles
and the Papyrus reference pickle loaded inside Bubblewrap using pandas 3.0.2 and
NumPy 2.4.4. Thirteen focused adapter/provisioning checks pass; a separate actual
namespace/read-only-workspace probe also passed. Those are infrastructure checks,
not scientific task successes.

Docker daemon access is denied for this account. Evaluation therefore uses the
recorded `scienceagentbench-verified-split-execution-bubblewrap-v2` adaptation:
fresh execution of the sealed program with public inputs only, followed by a
separate read-only native verifier with the private reference. The controller
retains the actor submission and fresh replay output and reports any byte
mismatch. Program validity and binary native task success are separate metrics;
CodeBERTScore is not computed. This is not an exact replication of the original
Docker environment.

Native grading quirks are preserved: Papyrus checks reference rows without an
explicit extra-row gate; the PSS grader discards the first CSV row despite the
headerless-output instruction and compares CSV strings. These limitations apply
to the reported native scores. No infrastructure failure was assigned a score.

Prepared public/controller packages: `prepared/sab-verified-v1`. Raw model traces,
sealed submissions, execution logs, and native-grader records remain in the
private run directory, which is ignored by Git. The aggregate run receipt is
[summary.json](../runs/sab-luna-none-01/summary.json). Each case's
`controller/actor_events.jsonl` preserves its interaction trace,
`controller/submission.json` identifies the sealed final program/artifact, and
`controller/native_evaluation/` contains replay and grader receipts. This report
contains no private reference answers.

Raw run links above point to private local artifacts, not files distributed in a
fresh clone. These runs predate the configurable A–G persona router.
