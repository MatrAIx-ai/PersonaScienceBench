# BixBench adapter

> The current five-case subset and runtime changes are documented in the
> [current adaptation record](../benchmark_adaptations.md). The two-case
> construction/pilot account below describes the earlier implementation.

Status: two reviewed episodes have completed live isolated analysis and final
Luna grading. Both received native grade zero; neither actor asked the researcher.
See the pilot report (historical record archived locally) and
[reproduction guide](../reproducibility.md).

## Selected episodes

| Native ID | Investigation | Researcher context | Inputs |
| --- | --- | --- | --- |
| `bix-10-q2` | Adjusted ordinal-logistic association between expected patient interaction and COVID-19 severity | Native category labels, shared identifier columns, available severity codes without invented meanings, and CSV encoding | Six original BCG-CORONA CSV/XLSX inputs; capsule `fbe0e950-76f2-4eb7-a216-a2d377970922` |
| `bix-8-q2` | Chi-square association between m6A methylation and differential expression | Worksheet/header names, existing category labels, and distinction between transcript and gene identifiers | Two original XLSX inputs; capsule `48a6b469-9c9d-4bef-b5b4-f29b7d6fa046` |

The questions are preserved verbatim, including all named methods, variables, and
adjustments. Capsule data already contain processed scientific measurements and
annotations; retaining those legitimate native inputs is intentional. Neither
capsule's executed reference notebook is exported. The second capsule's
`Proteomic_data .xlsx` is retained, although the question focuses on the MeRIP
workbook, to preserve the supplied native data inventory.

Both questions are bounded statistical analyses from distinct capsules. The
researcher role is limited to reviewed data interpretation/format clarifications;
the researcher has no gold answer, model coefficient, test statistic, or target
conclusion. Facts can also be discovered through data inspection. Asking questions
is optional, and these two pilots alone do not establish that persona influences
performance.

## Identity and provenance

- Source: `Future-House/BixBench`, revision
  `49311180bdacb324c596f2e07596c126f2004008`.
- Dataset: `futurehouse/BixBench`, revision
  `f8cc3bdcc6357c88b8c3648306522b9c422dc95a`, version 1.5.
- Inventory: 205 questions; only the two explicitly reviewed questions are
  convertible. Capsule UUID is the study-group identifier.
- Annotation, archive, individual input, grader, and prompt hashes are pinned in
  the adapter. Changed sources require renewed review and an adapter version.
- Each fact identifies its ZIP member, dataset revision, file hash, and reviewed
  header/cell/value location. Input metadata supplied every fact; reference
  notebooks and annotation `hypothesis`, `result`, `answer`, `ideal`, and
  `distractors` supplied none.

Source `paper` pointers and native category labels remain controller provenance.
Only the exact question, native canary, public submission requirements, permitted
input paths, and discoverable researcher topics reach the actor.

## Offline provisioning and isolation

The two immutable archives total approximately 2.4 MB and were acquired during
construction at the pinned Hugging Face dataset revision. They remain outside
the development repository in the configured BixBench asset directory.

For a fresh checkout, acquire `BixBench.jsonl` and these archives from
`https://huggingface.co/datasets/futurehouse/BixBench/resolve/<dataset_revision>/`:

```text
CapsuleFolder-fbe0e950-76f2-4eb7-a216-a2d377970922.zip
CapsuleFolder-48a6b469-9c9d-4bef-b5b4-f29b7d6fa046.zip
```

`BixBenchAdapter.prepare_assets(task_id)` is an explicit offline operation. It
checks the archive digest and ZIP paths, then extracts only eight exact reviewed
Data members across both capsules to `assets/prepared/<capsule>/`. It checks each
file hash and leaves the archive intact. It does not glob for data, delete source
notebooks, or extract gold notebook directories. Conversion itself performs no
downloads or extraction.

The shared runtime must copy/mount only the episode's explicit actor assets.
Neither the raw ZIP, source repository, annotation file, controller output,
researcher fact pack, nor evaluator references may be reachable from the actor
or researcher runtime. A filename prefix alone is not an isolation boundary.
Model-backed testing must also restrict network retrieval of the original public
answers/notebooks through the runner's allowed routes.

The actor runtime can use Python or R and may save an executed notebook or script.
Pandas/openpyxl, scipy, and statsmodels are plausible Python dependencies; the
selected Python runtime has completed both pilot analyses. No GPU
is specified for either pilot. Runtime installation is separate from task
conversion and must be recorded when the user selects the testing configuration.

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

- Both pilots have `range_verifier`, which uses an **LLM comparison**, not the
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

## Offline checks completed during construction

`tests/test_bixbench.py` covers public/private separation, source tampering,
allowlisted extraction, immutable archives, native correct/incorrect/refusal and
malformed-response behavior, missing outcomes, full-workflow submission gates,
and private information in provider errors. Judge-interface checks use fixed
offline responses and synthetic predictions; they do not solve either task.

Both selected pilots have now completed execution and grading. The earlier
construction checks remain distinct from their measured scientific scores.
New persona configurations still need controlled live comparisons.
