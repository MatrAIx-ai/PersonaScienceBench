# persona_off · expbench · iclr2024/18013/1

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **60/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Inspect the supplied inputs and any readily available setup documentation, then propose an approach for a design-only comparison of FuseLLM versus Llama-2 on zero-shot Common Sense (CS) benchmarks. Repository inspection is optional and only useful if relevant documentation exists; compute and experimental execution are not required. Do not produce the full experiment design yet. Identify what is source-supported versus assumed, especially model variants/checkpoints, the meaning and task composition of CS, zero-shot prompting and scoring, and comparison metrics. Outline the proposed controls, analysis strategy, and feasibility considerations, and flag consequential uncertainties without inventing missing setup details or expected results.
````

**Interaction**

````text
initial_request
````

**Phase**

````text
initial_inspection
````

**Action**

````text
continue
````

**Approve Approach**

````text
false
````

**Evidence**

````text
The brief requires an experiment design, not execution, and fixes only the FuseLLM versus Llama-2 zero-shot CS comparison. Benchmark composition, checkpoints, resources, and empirical outcome are not specified.
````

**Objectives Open**

````text
[
  "Inspect available setup information and distinguish supported details from assumptions.",
  "Review a proposed comparison approach and consequential uncertainties before authorizing the full design."
]
````

### Event 2 — Actor

**Answer**

````text
Proposed approach (design only; not the full experiment design)

Source-supported scope: compare FuseLLM against Llama-2 on zero-shot commonsense (CS) benchmarks. The supplied task explicitly requests a design, not execution. Neither the local input nor available documentation specifies model sizes/checkpoints, CS task membership, prompts, scoring, or metrics. Consequently, no claim about which model will win is justified.

1. Resolve the reference setup before specifying the protocol. Please use the supplied source topics, iclr2024/18013/1:setup_2 and iclr2024/18013/1:setup_9, to clarify:
   • Which exact FuseLLM and Llama-2 variants/checkpoints are intended, including size, base versus instruction/chat tuning, and model revisions? Is the intended Llama-2 comparator the corresponding unfused base model?
   • What does CS denote in that setup: the exact benchmark/configuration list, evaluated splits, and any exclusions or preprocessing?
   • What source-supported evaluation harness/version, prompt templates, zero-shot definition, answer scoring/normalization, per-task metrics, and CS aggregation rule were used?
   These are consequential unknowns, not details to fill in from general convention. If the sources are silent, we should explicitly agree on defaults rather than label them as reproductions.

2. Proposed controls, pending those clarifications. Evaluate both checkpoints on identical benchmark examples and splits with the same zero-demonstration templates, option ordering, preprocessing, truncation policy, and harness implementation. Retain model-native tokenizers and disclose tokenization differences. Match numerical precision and relevant inference settings where feasible, document any necessary model-specific formatting, and avoid asymmetric prompt optimization. Prefer a matched size/base-or-chat comparison if the question permits; otherwise describe it as a checkpoint comparison rather than isolating a fusion effect.

3. Proposed scoring and analysis. Use each task's source-defined scoring and metric, explicitly distinguishing raw option likelihood, length-normalized likelihood, and generated-answer extraction; do not silently substitute one for another. Predefine a primary CS summary and report all per-task results and paired FuseLLM-minus-Llama-2 differences. If the reference has a CS aggregation rule, preserve it. Otherwise, an equal-task macro-average of compatible accuracy metrics is a candidate assumption requiring approval, not an established fact. Plan paired uncertainty estimates using shared examples within each task, with an aggregate interval that respects task boundaries. Distinguish a higher point estimate from statistically supported improvement, and distinguish suite-average improvement from winning every task. Treat per-task significance claims as secondary and address multiplicity if such claims are desired. Report practical magnitude and uncertainty, not only significance; intervals over examples do not establish generalization to all commonsense tasks.

4. Feasibility and validity. This stage requires no downloads, compute allocation, or experiment execution. A later protocol should include checks for checkpoint identity, dataset/configuration versions, prompt rendering, absence of demonstrations, answer-token alignment, scoring normalization, truncation, and deterministic behavior where applicable. Record training-data contamination information if available and acknowledge that an observational checkpoint comparison cannot by itself attribute gains specifically to fusion. The supplied environment has no datasets, GPU, network access, or preinstalled project dependencies, so actual model evaluation would require a separate provisioned environment; resource estimates should wait for checkpoint and suite identification.

I propose resolving the three setup groups above, then seeking explicit approval before expanding this into the complete design. No expected result is assumed.
````

**Stage**

````text
plan
````

**Evidence**

````text
Repository inspection listed only task.json. Reading it confirmed the question and design-only context; its embedded documents entry says: 'track.md': 'Design-only task; repositories and compute are not required.' A successful exploratory `find . -maxdepth 2 -type f -print` returned only ./task.json, so no local model card, evaluation script, benchmark manifest, or standalone setup documentation was available. The source-topic identifiers and runtime constraints come from the researcher-supplied request, not from inspected source excerpts. No models or benchmarks were run.
````

**Assumptions**

````text
[
  "Identical evaluation examples and a paired comparison are proposed methodological choices, not reported source procedures.",
  "A matched-size, matched-tuning checkpoint pair is preferred if compatible with the source-defined comparison; its availability is unconfirmed.",
  "An equal-task macro-average is only a fallback candidate if compatible task metrics exist and no reference aggregation is specified.",
  "Uncertainty estimates would describe finite evaluation-sample variation conditional on the chosen models and tasks, not training-run variation."
]
````

**Uncertainties**

````text
[
  "Exact FuseLLM and Llama-2 checkpoint identities, sizes, tuning status, and training relationship are unspecified.",
  "CS benchmark membership, configurations, splits, and aggregate definition are unspecified.",
  "Zero-shot templates, harness/version, scoring normalization, and task-specific metrics are unspecified.",
  "Source-topic contents were not supplied locally and require researcher clarification.",
  "Dataset access, checkpoint availability, contamination information, and evaluation resource needs remain unverified."
]
````

### Event 3 — Simulator

**Message**

````text
Approved: proceed to the final design-only experiment protocol. The available source excerpts provide only these facts: iclr2024/18013/1:setup_2 calls for evaluating whether FuseLLM outperforms Llama-2 in zero-shot CS evaluation, and iclr2024/18013/1:setup_9 names FuseLLM. They do not resolve the requested setup details, and no further source clarification is available. Do not present assumed choices as the original paper's setup.

Use your proposed matched-checkpoint controls and paired analysis. To make the design operational rather than leaving all choices open, specify a concrete proposed CS task suite, dataset configurations/splits, zero-demonstration templates, scoring rules, and a compatible evaluation implementation, explicitly labeled as prospective defaults rather than source-supported reproduction details. A matched-size base-model comparison is the preferred default, conditional on verifying checkpoint availability and identity; list exact checkpoint resolution and version pinning as pre-execution gates if identities cannot be verified. Approve equal-task macro-average accuracy as the primary summary if no source aggregation is available, with task-appropriate scoring defined in advance. Specify the paired, within-task bootstrap aggregation, confidence interval and decision criterion, and distinguish inconclusive evidence from evidence of no meaningful difference. Per-task results should be secondary, with multiplicity addressed if inferential claims are made.

Include rationale, controls, validity limits (including contamination and inability to attribute differences solely to fusion), reproducibility checks, and a realistic conditional feasibility plan for a separately provisioned environment. No execution, downloads, or fabricated results are needed. Conclude with how eventual observations would answer the question, not a prediction of which model wins.
````

**Interaction**

````text
next_task
````

**Phase**

````text
approach_review
````

**Action**

````text
continue
````

**Approve Approach**

````text
true
````

**Evidence**

````text
The reported inspection found only task.json and no evaluation setup documentation. The proposed controls and paired analysis fit the design-only objective; unresolved model and suite identities require explicitly prospective choices and pre-execution verification, not further unsupported source claims.
````

**Objectives Open**

````text
[
  "Deliver a complete operational experiment design with explicitly labeled defaults and unresolved identity/version gates.",
  "Specify primary metric, paired uncertainty analysis, decision rule, controls, rationale, and feasibility without claiming execution."
]
````

### Event 4 — Actor

**Answer**

````text
# Design-only protocol: FuseLLM versus Llama-2 on zero-shot CS

## 1. Scope and provenance

**Question:** Does the selected FuseLLM checkpoint outperform the selected Llama-2 checkpoint on a prespecified zero-shot commonsense benchmark suite?

**Source-supported facts:** The supplied task and source excerpt for `iclr2024/18013/1:setup_2` request the zero-shot CS comparison; `iclr2024/18013/1:setup_9` names FuseLLM. They do not identify checkpoints, CS tasks, prompts, metrics, or evaluation software.

**Everything operational below is a prospective protocol, not a reconstruction of the paper's setup.** No evaluation has been executed, and no outcome is predicted.

## 2. Models and pre-execution gates

Prefer a **matched-size base-model comparison**, provisionally at the Llama-2 7B scale. A candidate baseline is `meta-llama/Llama-2-7b-hf`, subject to access and identity verification. No verified FuseLLM repository identifier is available from the supplied evidence, so do not invent one.

Before any benchmark scoring:

1. Locate an authoritative FuseLLM release and verify its provenance, architecture, parameter scale, base versus instruction/chat status, tokenizer, and available training description. Select a released base checkpoint matched to the Llama-2 scale; verify whether the baseline is its actual unfused ancestor rather than assuming this.
2. Record exact repository IDs, immutable commit revisions, weight/config/tokenizer hashes, licenses, and access conditions for both models. If a matched base pair is unavailable, stop and amend the comparison explicitly before looking at scores. Do not silently substitute a chat model or unrelated fusion release.
3. Resolve and pin all dataset revisions/configurations and software versions. Validate the dataset schemas and availability of labels for the splits below. Unavailable or changed data requires a documented pre-scoring amendment, not a post hoc task substitution.
4. Freeze the protocol, evaluation code, analysis seed, manifests, and numerical settings before scoring either model.

The estimand is the performance difference between these two fixed checkpoints. It is not the average effect of fusion across independently trained models.

## 3. Proposed CS suite and primary metric

Use all labeled examples in these seven task/configuration/split combinations. Repository names below are proposed resolution targets, not locally verified resources; pin immutable dataset revisions at the gate above.

| Task | Proposed Hugging Face dataset / configuration | Split | Metric / scoring |
|---|---|---|---|
| BoolQ | `google/boolq`, `default` | validation | Accuracy; raw answer log-likelihood |
| PIQA | `ybisk/piqa`, `plain_text` | validation | Accuracy; token-normalized option log-likelihood |
| HellaSwag | `Rowan/hellaswag`, `default` | validation | Accuracy; token-normalized ending log-likelihood |
| WinoGrande | `allenai/winogrande`, `winogrande_xl` | validation | Accuracy; raw suffix log-likelihood after substitution |
| ARC-Easy | `allenai/ai2_arc`, `ARC-Easy` | test | Accuracy; token-normalized option log-likelihood |
| ARC-Challenge | `allenai/ai2_arc`, `ARC-Challenge` | test | Accuracy; token-normalized option log-likelihood |
| OpenBookQA | `allenai/openbookqa`, `main` | test | Accuracy; token-normalized option log-likelihood |

These tasks cover everyday plausibility, physical reasoning, pronoun resolution, yes/no reading, and elementary science reasoning. This is a pragmatic mixed CS suite, not a claim that all seven measure pure commonsense or that they match the source's undefined CS composition. Labeled validation splits are selected where public test labels may be unavailable. Do not use any evaluation split to choose prompts, checkpoints, or hyperparameters.

**Primary summary:** the unweighted mean of the seven task accuracies. Report it and all differences in percentage points. Do not pool examples across tasks for the primary score: that would disproportionately weight large tasks.

## 4. Frozen zero-demonstration prompts and scoring

Use plain text, no system/chat wrapper, no few-shot demonstrations, no chain-of-thought request, retrieval, tools, calibration examples, or supplied external facts. Evaluate options by teacher-forced likelihood, not sampled generation. Do not score option letters.

Templates below use `\n` for a literal newline. `{...}` denotes a dataset field. Each candidate continuation begins with one ASCII space.

- **BoolQ:** context `{passage}\nQuestion: {question}\nAnswer:`; continuations ` yes` and ` no`, mapped to the Boolean label. Sum continuation-token log-probabilities; do not normalize.
- **PIQA:** context `Goal: {goal}\nSolution:`; continuations ` {sol1}` and ` {sol2}`.
- **HellaSwag:** context `Context: {ctx}\nContinuation:`; continuations ` {ending_i}` for all four supplied endings. Use the dataset's `ctx` field directly rather than reconstructing or additionally prefixing its activity label.
- **ARC-Easy / ARC-Challenge / OpenBookQA:** context `Question: {question}\nAnswer:`; continuations ` {choice_text_i}` in dataset order. Map gold answer keys through the supplied choice labels, including numeric labels where present. For OpenBookQA, do not include the provided supporting fact.
- **WinoGrande:** split the sentence at its single underscore into prefix `p` and suffix `s`. For option `o_i`, use `p + o_i` as context and the unchanged `s` as continuation. Score only the suffix's summed log-probability, conditioning on the substituted option. This tests which referent best supports the rest of the sentence, without including the option's own prior likelihood in the score. Require exactly one blank and a nonempty suffix; a schema violation blocks scoring until resolved prospectively.

For PIQA, HellaSwag, ARC, and OpenBookQA, divide the summed continuation log-likelihood by the number of continuation tokens, excluding BOS/EOS/padding. This mitigates the direct penalty to longer options but is a substantive scoring choice. Different native tokenizers may still change normalization behavior.

For ordinary fields, strip outer whitespace but preserve internal text, punctuation, and case; do not apply unrecorded HellaSwag bracket removal or other task-specific cleanup. WinoGrande retains the raw sentence spacing around its blank. Freeze these transformations in code.

**Tokenization contract:** use each checkpoint's native tokenizer with automatic special-token insertion disabled; encode context and continuation separately, concatenate their token IDs, and prepend one native BOS token if defined. Add no EOS. Score only continuation IDs using correctly shifted causal logits. This explicitly defines boundary behavior rather than relying on tokenizer-dependent whole-string merging. It is a prospective convention and may differ from established harness defaults; audit and record rendered strings and token IDs. Require a nonempty context and continuation. Do not truncate or drop overlength examples silently: check both models against the smaller supported context limit and amend the protocol before scoring if any example exceeds it.

Choose the highest score, with exact ties resolved by original option order; report tie counts. Compute one binary correctness outcome per model per example.

## 5. Compatible implementation and reproducibility checks

Implement a small, version-controlled evaluator using Hugging Face `transformers` causal-language-model inference, `datasets` for loading pinned data, PyTorch for teacher-forced logits, and NumPy for the paired analysis. This supports the explicit templates and WinoGrande suffix rule without relying on an unidentified harness preset. Pin package versions, Python, PyTorch/CUDA, GPU type, tokenizer behavior, and attention implementation in an environment lock and run manifest. An lm-evaluation-harness wrapper is acceptable only if custom task definitions reproduce this contract exactly; default task names alone are insufficient evidence of compatibility.

Before full evaluation, use synthetic fixtures to check:

- Prompt strings contain no demonstrations, gold labels, or unintended dataset fields.
- Choice-label mappings, variable choice counts, and Boolean labels are correct.
- Continuation masks and causal shifting exclude prompt/padding tokens.
- Raw and normalized scores match a small independent arithmetic calculation.
- WinoGrande scores only the suffix, not the inserted option.
- Batched versus single-example scores agree within declared numerical tolerance; option permutations preserve mapped predictions except exact ties.
- Both models receive the same example IDs and strings; no examples are duplicated, omitted, or silently truncated.
- Eval mode disables dropout; repeated fixture scoring checks stability. Report any prediction-changing numerical instability rather than ignoring it.

Use a common supported precision, preferably BF16 with log-softmax/score accumulation in FP32, and no quantization by default. If either model cannot support this reliably, choose a common alternative and document it before evaluation. Native tokenizers are retained rather than forcing one model to use another's vocabulary. Adaptive batching is permissible only after confirming batching invariance.

Save per-example task/ID, gold label, both predictions, option scores, continuation lengths, correctness, and relevant hashes; retain rendering/tokenization audit artifacts subject to dataset licensing. Do not tune against benchmark scores.

## 6. Paired statistical analysis and decisions

For each task `t`, compute model accuracies and the paired difference `d_t = accuracy_FuseLLM - accuracy_Llama2`. The primary difference is `D = (1/7) sum_t d_t`.

**Bootstrap:** use 10,000 replicates with a fixed proposed seed of 20260929. In each replicate, independently resample `n_t` example indices with replacement inside each task. Apply exactly the same sampled indices to both models. Calculate each resampled task difference and then their equal-task mean. Do not resample tasks or concatenate them into a single example pool. The 2.5th and 97.5th percentiles form the primary two-sided 95% interval. This estimates evaluation-example uncertainty conditional on the fixed suite and checkpoints.

**Primary decision:** support higher suite-average performance if the lower bound of the 95% interval for `D` is above zero. Support lower performance if its upper bound is below zero. Otherwise the direction is inconclusive; a nonsignificant difference is not evidence of equality.

**Practical importance:** prespecify a prospective meaningful-difference margin of 1.0 macro-accuracy percentage point. If the interval lies wholly inside [-1.0, +1.0] points, describe this as evidence of practical equivalence under that chosen margin and confidence rule. If the lower bound exceeds +1.0, support a meaningfully positive improvement; analogously for a wholly negative interval below -1.0. Other intervals may leave meaningful differences unresolved. A small positive effect can be directionally supported and practically equivalent at the same time. The one-point margin is a policy choice, not a source-derived property.

**Secondary results:** provide both accuracies, paired differences, and the two discordant counts per task. The primary conclusion concerns the macro-average, not a claim of winning every task. Per-task intervals may be descriptive; if making directional inferential claims across tasks, use paired exact McNemar tests on discordant predictions with Holm correction across the seven tasks at familywise alpha 0.05. Label unadjusted intervals as such and do not use them to bypass this correction. Any later scoring sensitivity is exploratory and cannot replace the preregistered primary result.

## 7. Controls, limitations, and feasibility

Hold dataset versions, examples, prompt text, answer ordering, scoring code, common precision, and context-limit policy fixed. Do not select the best checkpoint or scoring variant after viewing results. Report parameter counts and training differences rather than implying equal parameter scale means equal training budget.

Document available training-data provenance and benchmark overlap disclosures for both models. Where corpora are accessible, consider overlap audits, while acknowledging that unavailable corpora prevent certification of no contamination. Zero-shot refers to absence of inference-time demonstrations, not guaranteed absence of benchmark exposure during training. Training duration, data mixture, distillation, architecture, and tokenizer differences can confound any attribution specifically to fusion. A causal fusion claim would require additional matched-training ablations outside this two-checkpoint protocol.

Bootstrap intervals assume the examples within each task are suitable sampling units. Inspect metadata for shared passages or other clusters before locking the analysis; substantial known clustering calls for a prespecified paired cluster-bootstrap amendment. Neither the default bootstrap nor per-task tests capture training-seed variation, benchmark contamination bias, or uncertainty about all possible commonsense tasks.

The present workspace has no datasets, network, GPU, or installed project stack, so execution belongs in a separately provisioned environment. Secure model access and licensed data first. For a confirmed approximately 7B pair, BF16 weights alone are roughly 14 GB per model; sequential evaluation avoids needing both models resident simultaneously. A 24 GB GPU might suffice with small batches and suitable sequence lengths, but a 40–80 GB GPU provides more headroom; this is conditional guidance, not measured feasibility. Larger released variants require revised provisioning. Budget disk for both weights, data, caches, and audit outputs. Estimate runtime only after pinned model/token-length inventories and an infrastructure smoke test; there is no basis for a runtime claim now. Insufficient compute is not grounds for unreported quantization, smaller test subsets, or changing the suite.

## 8. How observations would answer the question

The eventual report will present a seven-task table and the primary macro-average difference with its paired interval. It will conclude whether this verified FuseLLM checkpoint has supported higher, lower, or unresolved suite-average zero-shot performance relative to the matched Llama-2 checkpoint, and separately whether differences exceed or fall within the prespecified practical margin. Task heterogeneity and validity limits will qualify that conclusion. Until such observations exist, the protocol supplies a testable answer procedure—not a prediction that FuseLLM will win.
````

**Stage**

````text
result
````

**Evidence**

````text
Local inspection found only task.json; its embedded documentation states 'Design-only task; repositories and compute are not required.' A successful exploratory `find . -maxdepth 2 -type f -print` returned only ./task.json. No evaluation code, model manifest, dataset files, or source setup documents were locally available. The researcher subsequently clarified that setup_2 only requests the zero-shot CS comparison and setup_9 names FuseLLM; neither resolves the setup. The researcher approved matched-checkpoint controls, paired analysis, prospective operational defaults, and equal-task macro-average accuracy. The explicit templates, seven-task suite, implementation contract, bootstrap, and decision rules are therefore proposed design choices, not observed paper methods. Paired resampling uses the shared examples to account for correlated model outcomes; task-stratified aggregation preserves equal task weighting. No model inference, dataset download, or experimental result is claimed.
````

**Assumptions**

````text
[
  "The proposed seven-task suite is an acceptable operational definition of CS, not the source-defined suite.",
  "A verified matched-size base FuseLLM/Llama-2 pair can be obtained; the 7B baseline repository is a candidate pending verification, and the FuseLLM identifier remains a mandatory gate.",
  "Proposed dataset repositories, configurations, splits, and schemas will be verified and pinned before scoring.",
  "Plain zero-demonstration text, the specified task scoring, separate context/continuation tokenization, and common nonquantized precision are prospective defaults.",
  "A 1.0 percentage-point macro-accuracy margin is the prospective threshold for practical importance.",
  "Within-task example resampling is appropriate unless a pre-scoring metadata audit identifies dependence requiring clustered sampling."
]
````

**Uncertainties**

````text
[
  "Authoritative FuseLLM checkpoint identity, availability, scale, tuning status, and relationship to the baseline remain unverified.",
  "Model and dataset access permissions, immutable revisions, software compatibility, and maximum sequence lengths require pre-execution validation.",
  "Contamination cannot generally be excluded without adequate training-corpus access.",
  "Feasible memory, throughput, and numerical stability depend on the verified artifacts and separately provisioned hardware.",
  "The result would apply to the selected checkpoint pair and proposed suite, not establish a causal fusion effect or reproduce unspecified source methods."
]
````

### Event 5 — Simulator

**Message**

````text
The final protocol satisfies the design-only deliverable: it provides an operational prospective CS comparison, rationale, matched evaluation controls, explicit scoring and paired analysis, decision rules, and conditional feasibility. It appropriately distinguishes source-supported scope from proposed defaults and leaves unverifiable checkpoint identities and artifact versions as mandatory pre-execution gates. No experimental execution or empirical outcome is claimed. Retain this protocol as the final experiment design; the question of which checkpoint actually performs better remains unanswered pending evaluation.
````

**Interaction**

````text
conclude
````

**Phase**

````text
result_review
````

**Action**

````text
stop
````

**Approve Approach**

````text
false
````

**Evidence**

````text
The reported design specifies seven tasks and splits, zero-demonstration templates, likelihood scoring, equal-task macro-accuracy, a paired within-task bootstrap with confidence-based decisions, practical-equivalence criteria, and multiplicity handling for secondary task claims. It includes reproducibility checks, contamination and attribution limitations, and resource guidance conditional on verified models. These cover the agreed approach and submission contract without requiring execution.
````

**Objectives Open**

````text
[]
````

## Provenance

````text
{
  "source_run": "runs/openai-astra-top2-first-pass",
  "repair_run": "runs/repair-1-openai-astra-top2-first-pass",
  "event_log": "runs/openai-astra-top2-first-pass/episodes/expbench_iclr2024_18013_1-eccde6bbbb33/persona_off/attempt-1/output/iclr2024__18013__1/events.jsonl",
  "event_log_sha256": "780a480eace9936fa872ea15016a8d033717f7e00fabe4a6bc9a8405f7fc3e92",
  "models": {
    "actor": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "researcher": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "judge": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    }
  }
}
````
