# DiscoveryBench adapter

The adapter converts all 264 native real-data questions from the pinned `allenai/discoverybench` source. Composite IDs include the metadata path, query-group index and native question ID. Keep related source-study questions together in dataset splits.

## Conversion and collaboration

Public packages retain the question, dataset/column descriptions, staged inputs and submission contract. Automated extraction retains source-attributed context and distinguishes explanatory context from methodological advice. The private answer-key join uses dataset, metadata suffix and question ID; missing or ambiguous references block conversion. Reference hypotheses, workflows and evaluator records remain private.

The current protocol reviews the proposed approach and the resulting discovery/evidence. Full persona identity enters the simulator system prompt; both persona-on and persona-off conditions permit general knowledge. See [conversion rules](../design/conversion_revision_v2.md) and [the interaction protocol](../interaction_protocol.md).

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
