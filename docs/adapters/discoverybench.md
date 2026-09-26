# DiscoveryBench adapter

Source: [allenai/discoverybench](https://github.com/allenai/discoverybench), revision
`c31fcf011e070f021a5f5b906896d0821f6880e8`. The adapter enumerates and automatically
converts 264 real-data queries. Eight questions have explicit source reviews,
including the three ecology tasks below. Source data remain in an external,
unmodified checkout with their licenses.

The counting unit is a native query, identified by split, study, metadata file,
query-group index and native `qid`. A persona variant reuses that scientific
question; it does not add an independent source task or study.

## Selected episodes

| Native composite ID | Domain | Scientific objective | Researcher context |
| --- | --- | --- | --- |
| `test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | engineering | Estimate the proportions and bootstrapped 95% confidence intervals for Business Analysts and Developers associated with requirements in ML-enabled systems. | The source's qualified statement about negative values and `-99` potentially representing missing responses. |
| `test/nls_incarceration/metadata_1.json/0/0` | sociology | Compare 1996 wealth for respondents with and without incarceration histories. | The source's explanation of residence information as a way to ascertain incarceration. |

The other reviewed questions are `test/meta_regression/metadata_1.json/0/0`,
`test/nls_ses/metadata_1.json/0/0`, and
`test/worldbank_education_gdp_indicators/metadata_1.json/0/0`.
`pilot_task_ids()` retains the two defaults in the table; use an explicit
selection to prepare another set.

## Ecology tasks

[Selection](../../configs/discoverybench-ecology-selection.json): three questions
from `test/introduction_pathways_non-native_plants`. These add source-reviewed
task packages within the existing 264-query catalog. They share **one study**;
keep all questions and persona variants from this study together in any split.

| Native suffix within the study | Investigation | Scientific decisions for researcher review |
| --- | --- | --- |
| `metadata_0.json/0/0` | When gardening overtook agriculture as an introduction pathway | Interpret the supplied historical bins and compare pathway counts without inventing finer time resolution. |
| `metadata_1.json/0/1` | Urban land use and the proportion of gardening-introduced plants | Explain the proportion denominator, choice of spatial scale/year, uncertainty, and association-versus-causation limits. |
| `metadata_2.json/0/0` | Gardening-introduced prevalence across habitats | Distinguish counts from proportions, preserve native habitat labels, and state weighting and comparison assumptions. |

These are opportunities for optional analytical advice and evidence review,
not extra requirements or hints about the reference answer. Native questions,
input inventories and submission rules are unchanged. No dialogue quota or
persona-dependent scientific rubric is introduced.

All three tasks retain four native files:

| File | Format and purpose |
| --- | --- |
| `temporal_trends_contingency_table.csv` | Tab-separated historical periods, pathways and counts |
| `invaded_niche_pathways.csv` | Tab-separated plot counts, habitat and land-use covariates |
| `invasion_success_pathways.csv` | Comma-separated species characteristics and invasion measurements |
| `phylogenetic_tree.txt` | Newick tree supplied by the source |

Each metadata file and every input file has a reviewed SHA-256 lock in
`ECOLOGY_TASKS` / `ECOLOGY_INPUT_SHA256`. Changed inputs require renewed review;
preparation also verifies the staged bytes. All four files remain available even
when a question only requires one table.

The source's `domain_knowledge` fields are empty. The researcher receives three
reviewed input-schema facts, derived solely from the CSV headers and delimiters,
with source revision, file hash and `row=1` provenance. They contain no computed
trend, coefficient, group comparison or expected conclusion. The actor can
inspect exactly the same headers. Public column descriptions stay public;
contradictory or unspecified scientific details remain uncertainties.

The task IDs and study do not overlap the five DiscoveryBench selections in
[the full-persona cohort](../../configs/full-persona-v2-five-selection.json).
Existing persona renderers, approach/result reviews and native grading are reused.
Tasks support both science-profile and full-profile researcher identities;
persona off retains the same researcher and factual context.

### Persona variants

The existing `pi_cautious` and `pi_delegating` profiles provide a ready contrast:
both describe an applied-mathematics PI and assign all 56 attributes; they differ
only in `decision_delegation` (low versus high). Keep those identities unchanged
rather than implying additional ecology expertise. Persona off provides the
third condition. This gives nine task/condition combinations across three
scientific questions, with one shared study identity.

Generate configs with the existing attachment helper, then use each with the
same prepared packages and launch command:

```bash
for profile in pi_cautious pi_delegating; do
  .venv/bin/python -m personasciencebench.science_personas attach \
    --profile "examples/science_personas/profiles/$profile.json" \
    --config configs/discoverybench-azure.json \
    --output "configs/discoverybench-ecology-$profile.local.json"
done
```

Attachment and mock initial-handoff checks run offline. They verify that models,
budgets, source facts, public briefs and grader inputs stay fixed while the
researcher identity changes. They do not establish persona fidelity or an effect
on scientific performance. Full-profile identities use the existing
`persona.system_prompt` path and the same task boundary.

### Prepare and validate

```bash
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench
.venv/bin/python -m personasciencebench --source-root external/sources prepare \
  --benchmarks discoverybench --selection configs/discoverybench-ecology-selection.json \
  --cases-per-benchmark 3 --output prepared/discoverybench-ecology
PERSONASCIENCEBENCH_SOURCE_ROOT=external/sources .venv/bin/python -m pytest -q tests/test_discoverybench.py
```

Preparation performs no model calls. Use the [Azure setup](../azure.md) or the
existing provider configuration to run the packages through the shared CLI.
Configure `pilot_cases_per_benchmark=3` for this selection. Source packages,
credentials and raw traces remain local and ignored.

## Information boundary and conversion

The public package contains the selected question unchanged, the dataset names
and descriptions, raw-column names and descriptions, the submission contract,
and two logical interfaces: staged `data/<filename>.csv` and the researcher
endpoint. No metadata directory, answer-key file, or source repository is mounted
into the actor runtime. Asset hashes are recorded at conversion and checked by
the shared staging layer.

Nonempty `domain_knowledge` fields become source-attributed researcher facts,
with uncertainty qualifiers, stable IDs, revision, metadata hash and character-span
provenance. Reviewed ecology tasks additionally use the input-schema facts above. Persona and conversation state remain
external to this fixed knowledge pack. The data descriptions remain public;
they are not hidden merely to force interaction.

The converter does not copy a full query, metadata object, or paper. It excludes
`hypotheses`, nested `true_hypothesis`, `workflow`, `workflow_tags`, `intermediate`,
and answer keys from actor and researcher exports. The selected test metadata
contain placeholder `hypotheses.main` values; the actual reference must be joined
from `eval/answer_key_real.csv` on dataset, metadata filename suffix, and `qid`.
An ambiguous or missing join is an error. The answer key, reference hypothesis,
and evaluator records are controller/evaluator-only.

Reviewed metadata and the test answer key must match pinned hashes. Ecology inputs
have additional file locks. A changed reviewed file requires re-curation. Other
source queries retain automated conversion status, which is distinct from a
source-specific review or a completed scientific execution.
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

## Validation

`tests/test_discoverybench.py` checks composite identities, public/private
separation, exact query selection (including nonzero `qid`), source/reference
availability, metadata and input tampering, staged file integrity, missing
outcomes, plan rejection, native context denominators and relation scores,
per-call settings, private stdout suppression, and malformed-judge behavior.

### Task-validation measurements

Three persona-off episodes were run on 2026-09-26 through the shared runner,
with Azure `gpt-5.6-sol-2026-07-09` for actor, researcher and judge, reasoning
`none`, 60 actor steps and the standard approach/result review protocol.
General-knowledge expansion was disabled. This is a task execution check;
no live persona contrast was run for these questions.

| Native suffix | Attempted / submitted / evaluated / scored | Native final score | Context recall | Successful commands / attempts |
| --- | --- | ---: | ---: | ---: |
| `metadata_0.json/0/0` | 1 / 1 / 1 / 1 | 0.0 | 0.0 | 2 / 2 |
| `metadata_1.json/0/1` | 1 / 1 / 1 / 1 | 0.0 | 0.0 | 6 / 6 |
| `metadata_2.json/0/0` | 1 / 1 / 1 / 1 | 0.0 | 1.0 | 7 / 8 |

All three reached submission and native grading. Each had one approach review
and one result review, with no optional clarification questions. The habitat
analysis recovered from one failed command within its normal episode budget.
There were 39 API calls, 299,550 prompt tokens and 20,599 completion tokens;
monetary cost was not available. The prepared inputs, configuration, source files,
lockfiles and selected sandbox launcher matched their frozen hashes at run end.

These outcomes establish that the task packages execute and grade, **not that
they were solved correctly or that personas improve performance**. The native
context matcher rejected the temporal and urban-land-use submissions. The
habitat submission matched a context but received zero relation agreement. The
urban-land-use analysis also disagreed with the reference direction; denominator,
zero-count handling, year and spatial-scale choices require explicit assumptions.
The temporal submission used the supplied time bins, illustrating sensitivity to
context granularity. Low scores were retained without rerunning or changing the
native references, prompts or thresholds.

Native DiscoveryBench scoring evaluates reference agreement and does not
independently verify numerical execution. The Azure judge is labelled
`discoverybench-native-prompts-settings-strict-errors-v1+azure-configured-judge-v1`.
Raw receipts and artifacts are retained locally under
`runs/discoverybench-ecology-validation-20260926/`; reproduction uses a fresh
output directory. Offline persona-boundary checks cover all three questions
with persona off, both existing PI profiles and the full-profile representation.
