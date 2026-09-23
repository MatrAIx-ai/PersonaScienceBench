# DiscoveryBench adapter

Status: two reviewed episodes have completed live actor execution and final
Luna grading. Both received native `final_score=0.0`; neither actor asked the
researcher. See the [pilot report](../../reports/pilot_report.md) for judge
sensitivity and [current status](../status.md) for subsequent changes.

Source: [allenai/discoverybench](https://github.com/allenai/discoverybench), revision
`c31fcf011e070f021a5f5b906896d0821f6880e8`. The upstream checkout is external and
unmodified. The adapter consumes the source's real-data tasks and retains its
domain labels. It enumerates 264 queries using composite IDs; only the two
explicitly reviewed IDs below are exportable in this version.

## Selected episodes

| Native composite ID | Domain | Scientific objective | Researcher context |
| --- | --- | --- | --- |
| `test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | engineering | Estimate the proportions and bootstrapped 95% confidence intervals for Business Analysts and Developers associated with requirements in ML-enabled systems. | The source's qualified statement about negative values and `-99` potentially representing missing responses. |
| `test/nls_incarceration/metadata_1.json/0/0` | sociology | Compare 1996 wealth for respondents with and without incarceration histories. | The source's explanation of residence information as a way to ascertain incarceration. |

The last two ID components are query-group index and native `qid`; the metadata
filename is essential because top-level metadata `id` values are not unique.
Study groups are distinct and must remain intact across future dataset splits.

Both source CSVs are already present in the pinned checkout. They are roughly
507 KB and 343 KB respectively. The incarceration data are already processed
and include `ever_jailed`; the researcher fact is background, not an instruction
to reconstruct that column. Its marginal usefulness is an empirical question.
Neither episode requires asking a question to complete the task.

## Information boundary and conversion

The public package contains the selected question unchanged, the dataset names
and descriptions, raw-column names and descriptions, the submission contract,
and two logical interfaces: staged `data/<filename>.csv` and the researcher
endpoint. No metadata directory, answer-key file, or source repository is mounted
into the actor runtime. Asset hashes are recorded at conversion and checked by
the shared staging layer.

The researcher receives one explicitly reviewed source statement for each task,
with its original uncertainty qualifiers, a stable fact ID, revision, metadata
hash, and `/domain_knowledge` provenance. Persona and conversation state remain
external to this fixed knowledge pack. The data descriptions remain public;
they are not hidden merely to force interaction.

The converter does not copy a full query, metadata object, or paper. It excludes
`hypotheses`, nested `true_hypothesis`, `workflow`, `workflow_tags`, `intermediate`,
and answer keys from actor and researcher exports. The selected test metadata
contain placeholder `hypotheses.main` values; the actual reference must be joined
from `eval/answer_key_real.csv` on dataset, metadata filename suffix, and `qid`.
An ambiguous or missing join is an error. The answer key, reference hypothesis,
and evaluator records are controller/evaluator-only.

The two metadata files and answer key must match reviewed hashes. A changed file
requires re-curation; inventory membership never implies an approved boundary.
The source license and dataset license remain in the upstream checkout. The
adapter links to them rather than redistributing the original corpus.

## Execution and submission

An independent actor can use a terminal or notebook runtime with the staged
CSV. The adapter imposes neither a model choice nor a common monetary cap or
20-step EXP design budget. The runner records actual tools, resources, and
execution evidence.

Submit `Submission(stage="final", answer="...")`, or place the finding in
`payload["hypothesis"]`. An optional `payload["workflow"]` describes the executed
analysis; supporting code/notebook/files can be included in `artifacts`.
A `stage="plan"` submission cannot receive the native completed-analysis score.
Native DiscoveryBench grading measures reference agreement of the finding;
it does **not** independently prove that an analysis was executed correctly.
The run record must keep execution evidence separate from the scientific score.

## Native evaluation bridge

The bridge extracts only eight named function definitions from the pinned
`eval/new_eval.py` AST. It verifies SHA-256
`83406ddbe6894429cc5012b17cb82a209d5397aa7863b0aba1bb51edf1dd6c65` before compilation.
Imports, CLI entrypoints, API client creation, and upstream stdout are excluded.
An explicitly injected `Judge` supplies every response; conversion and
enumeration never invoke one. No role model is selected by this adapter.

It preserves valid-response native behavior:

1. Decompose the reference and submitted hypothesis into contextual sub-hypotheses.
2. Greedily match contexts one-to-one in source order.
3. For each matched context, grade variable overlap F1 and relation agreement
   (`0`, `0.5`, or `1`). The source passes the **full hypotheses** to this step,
   despite looping over matched sub-hypotheses; the bridge preserves that detail.
4. Divide the summed matched accuracy by all predicted contexts, including
   unmatched predictions. Multiply this mean by reference-context recall.

Reported native metrics are `final_score`, `recall_context`, and
`mean_accuracy_score`, each on a 0–1 scale. Each episode has denominator one;
cross-episode attempted/submitted/evaluated/scored counts belong in the common
report. Missing submissions, missing assets, provider errors, and parsing errors
remain explicit unscored statuses.

Native helper generation settings are forwarded per call. Hypothesis
decomposition and semantic context matching use temperature `1.0` and 4096
tokens. Variable/relation grading uses temperature `0` and 250 tokens: the
upstream helper hardcodes 250 despite its caller requesting 512. Both use
`top_p=1`, frequency penalty `0`, and presence penalty `0`. Providers that cannot
support these settings must fail or use a separately declared evaluator variant;
the shared client must not silently discard them.

The evaluator version is
`discoverybench-native-prompts-settings-strict-errors-v1`. Its documented changes
are injected judge/model routing, explicit errors for malformed outputs, no
implicit retries, and suppression of private reference printing. In particular,
strict handling replaces upstream parse-failure paths that can return `None` or
negative scores. Exact prompts, source hash, requested generation settings,
responses, and intermediate grades stay in the private evaluation result.
The configured provider and resolved judge model must accompany a real run.

## Checks and remaining work

`tests/test_discoverybench.py` checks composite identities, both information
boundaries, source/reference availability, changed-source rejection, missing
results, plan rejection, native context denominators and relation scores,
per-call settings, private stdout suppression, and malformed-judge behavior.

Before the requested pilot: select the simulator and actor configurations,
configure a compatible judge, prepare the isolated actor runtime using only the
public export, obtain the user's testing confirmation, and run the two episodes
with immutable interaction and submission records. These checks have not been
replaced by claims of successful scientific execution.
