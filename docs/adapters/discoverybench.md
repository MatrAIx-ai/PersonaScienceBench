# DiscoveryBench adapter

The adapter converts all 264 native real-data questions from the pinned `allenai/discoverybench` source. Composite IDs include the metadata path, query-group index and native question ID. Keep related source-study questions together in dataset splits.

## Conversion and collaboration

Public packages retain the question, dataset/column descriptions, staged inputs and submission contract. Automated extraction retains source-attributed context and distinguishes explanatory context from methodological advice. The private answer-key join uses dataset, metadata suffix and question ID; missing or ambiguous references block conversion. Reference hypotheses, workflows and evaluator records remain private.

The current protocol reviews the proposed approach and the resulting discovery/evidence. Full persona identity enters the simulator system prompt. Knowledge policy is configuration-dependent: the full-persona study permits general knowledge in both arms, while the Azure task-validation config retains grounded knowledge. See [conversion rules](../design/conversion_revision_v2.md) and [the interaction protocol](../interaction_protocol.md).

## Reviewed ecology selection

Six source-reviewed questions from `test/introduction_pathways_non-native_plants`
cover distinct analysis families within **one study**. They reuse the existing
264-query converter. The [original selection](../../configs/discoverybench-ecology-selection.json)
retains the first three; the [expanded selection](../../configs/discoverybench-ecology-expanded-selection.json)
and [task tags](../../configs/discoverybench-ecology-study.json) cover all six.

| Native suffix | Analysis family | Persona-off validation score |
|---|---|---:|
| `metadata_0.json/0/0` | Temporal pathway transition | 0.00 |
| `metadata_1.json/0/1` | Urban land use and gardening share | 0.00 |
| `metadata_2.json/0/0` | Habitat comparison | 0.00 |
| `metadata_3.json/0/0` | Interacting covariates | 0.00 |
| `metadata_4.json/0/0` | Residence time and invasion success | 0.00 |
| `metadata_5.json/0/2` | Urban effects across pathways | 0.75 |

All six completed submission and native grading with Azure
`gpt-5.6-sol-2026-07-09`, reasoning effort `none`, 60 actor steps and grounded
researcher knowledge. The first three were validated in the original batch;
the added three in a separate pre-scale batch. These are single-run execution
checks, not estimated task difficulty or proof of scientific correctness.

Metadata and all four inputs are hash-locked. Three CSV header/format facts
provide source-attributed researcher context; no computed finding is supplied.
Native questions, column descriptions, submission and grading stay unchanged.
Retain source ambiguities: `mrt` is described as mean residence time while its
question says minimum, and some buffer descriptions conflict with column names.
The two pathway-count tables are tab-delimited; the species-success table is
comma-delimited, and the fourth input is a Newick tree. Keep all four available.

Preparation makes no model calls:

```bash
.venv/bin/python -m personasciencebench --source-root external/sources prepare \
  --benchmarks discoverybench --selection configs/discoverybench-ecology-expanded-selection.json \
  --cases-per-benchmark 6 --output prepared/discoverybench-ecology
```

The example [Azure config](../../configs/discoverybench-azure.json) selects three
cases. Set `pilot_cases_per_benchmark=6` in an ignored local copy for the expanded
package, then use the shared runner described in [Azure setup](../azure.md).

The six-condition attribute pilot and its six-episode reproduction on the urban
question both scored zero; sensitivity-low covered two urban year/buffer definitions
versus nine for high and both controls. A separate seven-condition full-profile
pre-scale pilot (148, 046, 155, 228, 137, 089 and off; general knowledge enabled in
all arms) also scored zero throughout. All ten pre-scale episodes, including the
three added-task baselines, completed grading. Profile 155 used Mandarin while
046 used English despite its Spanish preference; profile 046 retained inline
execution receipts but attached no standalone files. These are descriptive
findings from one episode per condition, with no demonstrated score improvement.

All 42 task/profile boundary checks passed. Actual identities, shared inputs and
all attached artifact hashes passed the ten-episode audit; no frozen execution
input changed. Detailed research records remain contributor-local. The planned
three-repeat experiment has not run. Use the [offline interaction utility](../interaction_metrics.md)
to export saved-run measurements without new inference, keeping required reviews,
actor proposals and optional questions distinct.

## Submission

Submit `Submission(stage="final", answer="...")` or provide the finding through `payload["hypothesis"]`. Supporting workflow/code artifacts remain separate execution evidence. A plan alone cannot receive the completed-analysis score. Native grading measures reference agreement; it does not prove that the analysis was executed correctly.

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

## Records and checks

The [completed report](../../reports/full_persona_v2/README.md) contains current study results and traces. `tests/test_discoverybench.py` covers identities, source/private boundaries, missing results, plan rejection, native scoring, settings and malformed judge responses. Use the [setup guide](../reproducibility.md) to prepare a new host.
