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

## CHIP data-coding additions (2026-09-25)

Two questions from the clonal-hematopoiesis (CHIP) capsules are reviewed and
convertible. Both are range-graded, run in the provisioned Python runtime, and
depend on data coding that the input metadata documents.

| Native ID | Investigation | Offline key check | Researcher context | Inputs |
| --- | --- | --- | --- | --- |
| `bix-7-q2` | Mean CHIP variants per sample after removing intronic, intergenic and UTR variants (`range_verifier`, key 40-60) | 52.3 with reference calls removed; 300.9 if reference calls are kept | Workbook layout, Zygosity values including reference calls and blanks, Sequence Ontology terms | 86 exome workbooks in `CHIP_DP10_GQ20_PASS/`, CHIP gene list, trio sheet; capsule `a02b761a-02b6-46b5-9d5e-2964d5a74960` |
| `bix-2-q2` | Percentage of Control Children CHIP variants with VAF 0.3-0.7 (`range_verifier`, key 60-70) | 61.7% on non-reference calls; 13.0% if every row is counted | As for `bix-7-q2` plus trio-sheet codings (Status and BLM status values, `'Mother '` trailing spaces, tab-suffixed IDs, one person without a workbook) and the between-group summary workbook | The same 88 inputs plus `CHIP VAF mean proportions.xlsx`; capsule `30b33e47-92d8-4372-a9f6-da32896493d0` |

Facts come only from input headers, labels and value checks; the capsule
notebooks and annotation `ideal`, `result`, `answer`, `hypothesis` and
`distractors` fields were not used. The summary workbook reports between-group
differences only, not the per-group proportion asked for. `bix-2`, `bix-7`,
`bix-14`, `bix-20` and `bix-47` ship byte-identical exome inputs and are one
study; keep them together in any split although their capsule identifiers differ.

`prepare_assets` now creates native subfolders inside the capsule directory, as
required by `CHIP_DP10_GQ20_PASS/`, and rejects any target that resolves outside it.
Prepare with `--selection configs/bixbench-chip-selection.json`; the default two
cases per benchmark match `configs/pilot.json`.

Measured runs (local, `openai/gpt-6-luna`, reasoning `none`, three repeats per
condition, 0 researcher questions in every episode):

| Condition | `bix-7-q2` | `bix-2-q2` |
| --- | --- | --- |
| Researcher-only (standard) | 0/3 (300.9 each time) | 2/3 (15.8%, 61.6%, 61.6%) |
| All approved facts in the public brief (standards section 8 control) | 3/3 (52.33) | 3/3 (61.7%) |

The control shows the questions are solvable given the reviewed facts; the actor
did not ask for them. Two follow-up local runs on `bix-7-q2` qualify this:

| Follow-up | Result |
| --- | --- |
| Phase 1 example arms (off, reference, `coding_fluency_low`, `coding_fluency_high`), 3 repeats each | 0/12 correct, 0 researcher questions; answers varied within every arm (1.13 to 665.79) |
| Persona off, actor `reasoning_effort` low / medium, 3 repeats each | low: 0/3 (answered in text without submitting); medium: 2/3 correct (52.33) with 0 questions |

With more reasoning the actor infers the reference-call step from the data itself,
so the earlier gap reflects actor reasoning at effort `none` rather than
information that only the researcher holds. These questions are therefore not
evidence of persona sensitivity; they are contributed as reviewed tasks with
source-backed researcher facts. These are small descriptive runs, not a persona
comparison.

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

### CHIP integration boundary

The imported `bix-7-q2` and `bix-2-q2` selections retain native questions, input hashes and graders. Their researcher notes retain layout/label explanations, but omit imported aggregate missingness counts, cohort counts, join outcomes and the claim that no intergenic annotations exist. The actor must compute those properties. Earlier CHIP measurements therefore describe the pre-integration fact pack, not the current one. Both questions were already in the 205-question catalog, so they do not increase its size.
