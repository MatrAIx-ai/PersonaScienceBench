# ScienceAgentBench adapter

This adapter targets the **verified** split, pinned to annotation revision
`9c6e96c9e74572e979b0930ee735041cef528cb7` and repository revision
`c26e151ed601ba109dc4d35e057ff8e73fec469d`. It does not run the legacy validation
split. Construction and offline checks do not start an actor, researcher model,
benchmark program, Docker build, or paid judge.

## Two selected pilot episodes

| Verified ID | Investigation | Native deliverable | Researcher context |
| --- | --- | --- | --- |
| `22` | Filter Papyrus activity records by quality, protein class, activity type, and organism | A standalone Python program producing `pred_results/papyrus_filtered.pkl`, retaining column names | Reviewed explanation of the protein-class hierarchy and its `->` representation |
| `45` | Score perceived stress questionnaires | A standalone Python program producing the specified headerless `pred_results/questionnaire_pred.csv` | Reviewed explanation of the construct and recall period; BioPsyKit recommendation labelled optional advice |

These are separate source repositories/datasets and CPU-oriented tabular tasks.
Both native graders and their reference dependencies have been inspected from
the supplied verified bundle. They are bounded analyses, not open-ended projects.
Neither episode requires a minimum number of researcher questions. All filtering
criteria, output names, column requirements, and task instructions stay public.

## Information boundaries

- Public: `task_inst`, reviewed `dataset_preview`, native domain/category labels,
  exact allowlisted dataset paths, and standalone-program/artifact requirements.
- Researcher: exact reviewed excerpts of `domain_knowledge`, each carrying its
  annotation revision, instance locator, topic, and context/advice label. It does
  not receive a complete source row, original solution notebook, or grader.
- Controller/evaluator: native program/evaluator names, source-solution location,
  gold program, evaluator implementation, and grading reference files.
- A generic task inventory is supported, but only the two reviewed IDs can be
  exported as interactive episodes. Other rows require explicit curation first.

The native data tree is not blindly copied. Task 22 permits only two Papyrus
pickle files; task 45 permits only the questionnaire pickle. Source pickle data
must be loaded within the actor environment, not by the conversion process.

## Native evaluation and the split-execution adaptation

Upstream `compute_scores.py` executes a submitted program, checks its output,
then calls the selected evaluator module's `eval()` function. Its Docker harness
mounts the full benchmark, including reference code, into that same environment.
The upstream image also embeds API credentials in Dockerfile environment lines.
This adapter does not invoke that path unchanged.

The adapter keeps native task-success evaluation behind an explicitly versioned
**split-execution bridge**: an independent actor runtime executes `solution.py`
with only approved inputs, and the controller seals its artifacts and execution
receipt. A separate evaluator environment invokes the original task evaluator's
`eval()` on those artifacts. The actor program must never execute with evaluator
references mounted. The evaluator environment itself must be isolated from
credentials and the controller because pickle artifacts may execute code when
read by native Python graders.

Native program filename mapping is retained in controller records. Execution
validity and `success_rate` are separate; CodeBERTScore remains optional and must
not be invented or silently reported as zero. Any CodeBERT scorer runs separately
with private gold code and records its model/version. The native task evaluator
uses the unchanged `eval()` functions from the verified bundle. Task 22 requires
pandas and its private reference pickle; task 45 uses standard-library CSV and
its private reference CSV. No model judge is used for either selected task.

Missing artifacts, missing evaluator results, invalid result shapes, and
infrastructure failures remain explicit missing/error outcomes. The adapter does
not use the upstream routine that fills unevaluated rows with zero-valued scores,
nor the best-of-multiple-runs aggregation.

## Asset provisioning

The annotation parquet is present at
`../benchmarks/_assets/scienceagentbench/data/verified-00000-of-00001.parquet`,
SHA-256 `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`.

The user supplied **`benchmark_verified.zip`**, retained outside the repository
under `../benchmarks/_assets/scienceagentbench/`. Its SHA-256 is
`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
The archive has the expected `benchmark/` layout and native task filenames match
the pinned verified annotations. No published upstream archive digest was
available; this is recorded as user-supplied provenance, not independently
authenticated release identity.

`scienceagentbench_provision.provision_archive()` rejects unsafe ZIP paths,
duplicate entries, and symlinks; streams only the nine selected files into the
private `benchmark_verified/` directory; and records each digest in
`provisioning.json`. Those files are three public inputs, two native evaluators,
two private grading outputs, and two private gold programs. Gold programs are
retained for provenance but never staged into either pilot sandbox. All three
input pickles and the task-22 reference pickle loaded successfully as DataFrames
inside networkless Bubblewrap with pandas 3.0.2 and NumPy 2.4.4. Conversion and
provisioning never deserialize pickle files on the controller host.

The earlier SharePoint HTTP 401 acquisition blocker was resolved by the supplied
archive. Docker access remains unavailable for this account; the live pilot uses
the explicitly versioned Bubblewrap adaptation described below.

## Portable isolated evaluation

`evaluate_in_sandbox()` uses evaluator version
`scienceagentbench-verified-split-execution-bubblewrap-v2`. After the conversation
closes, it copies the sealed `solution.py` and freshly verified public inputs
into a new workspace and executes the program with a 900-second timeout. It
then places only the generated output, unchanged native evaluator, and its
allowlisted reference into a separate, read-only, networkless verifier workspace.
That second workspace contains neither candidate code nor public datasets and
uses a 300-second verifier timeout. Both environments hide controller secrets
and have no host-execution fallback.

The native score applies to the fresh program output. The originally submitted
artifact remains immutable; SHA-256 equality or an explicit byte mismatch is
recorded, so nondeterministic or inconsistent replay cannot be hidden. Namespace
startup/dependency failures have no scientific score. A program that actually
runs and fails, times out, or omits its required output receives native program
validity zero and task success zero. A valid program's native evaluation failure
receives validity one and success zero. CodeBERTScore is not computed.

Two upstream grading quirks are preserved and must inform interpretation:

- Task 22 compares reference rows but has no explicit extra-output-row gate.
- Task 45 discards the first CSV row even though its public instruction requests
  a headerless file. Its comparison uses CSV strings, including numeric formatting.

This is an environment adaptation, not a claim of byte-identical upstream Docker
replication. Dedicated Python package versions, native-source hashes, source-data
hashes, replay receipts, and private evaluator logs remain in controller records.

## Optional Docker bridge contract

This inspectable alternative is retained for a host with a provisioned, pinned
Docker evaluator image. The portable pilot uses `evaluate_in_sandbox()` above
and creates its own controller receipt through fresh program execution.

The controller submits `solution.py` and the exact native output as entries in
`Submission.artifacts`. It supplies a private JSON execution-receipt path in
`Submission.payload.controller_execution_receipt`. That receipt contains
`episode_id`, `stage: "final"`, `status: "completed"`, `exit_code: 0`,
`program_sha256`, and an `artifacts` mapping from native output path to SHA-256.
The receipt comes from the independent runner/controller, never from an actor's
self-reported success. A nonzero exit or missing artifact is not a successful
completed-program submission.

`evaluation_request()` constructs a reviewable controller command without
executing it and registers its private result location. The `grade` command
checks the execution receipt, verified provenance, and evaluator-file hash, then
starts a read-only, network-disabled Docker evaluator. No actor program or
credentials are mounted there. `evaluate()` only accepts the result registered
by that controller request; it rejects wrong episode/version, changed submitted
artifacts, malformed scores, and actor-supplied score fields. It records native
task success separately from the execution receipt's program validity.

Example `benchmark_verified/provisioning.json` structure (replace placeholders
with measured hashes and the configured image; this is not a provisioned runtime):

```json
{
  "split": "verified",
  "dataset_revision": "9c6e96c9e74572e979b0930ee735041cef528cb7",
  "archive_sha256": "<64 hex characters>",
  "evaluator_image": "<image>@sha256:<64 hex characters>",
  "reviewed_evaluators": {
    "22": {"script_sha256": "<64 hex characters>", "dependencies": {}},
    "45": {"script_sha256": "<64 hex characters>", "dependencies": {}}
  }
}
```

Dependency keys are explicit paths relative to the private bundle and values are
their SHA-256 digests. Inspect the actual native evaluator before populating this
mapping, including any reference files and imports. The evaluator image must
provide those native Python dependencies. CodeBERTScore is **not implemented** in
this bridge; enabling it later requires its own pinned scorer and result field.
