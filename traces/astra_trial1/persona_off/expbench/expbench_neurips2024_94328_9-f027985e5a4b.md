# persona_off · expbench · neurips2024/94328/9

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **50/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Please inspect the supplied inputs and any readily available local documentation, then propose an approach for this design-only study; do not produce the full experiment design or run experiments yet. Repositories and compute are not required, so missing local materials need not block planning. The fixed requirements are Phi-3-mini-4k-instruct, QuaRot-RTN versus QuaRot-GPTQ, and INT4/INT6/INT8, comparing perplexity and zero-shot accuracy (source IDs: neurips2024/94328/9:setup_1, neurips2024/94328/9:setup_6, neurips2024/94328/9:setup_8, neurips2024/94328/9:setup_11). Outline your proposed comparison matrix and controls, evaluation and calibration strategy, architecture-compatibility checks for QuaRot, analysis approach, and feasibility assumptions. In particular, identify what bit width would apply to weights, activations, and KV cache, how RTN and GPTQ would be compared fairly, and what evidence a Phi-only study could support about non-LLaMA generalization. Distinguish source-supported details from proposed choices and flag consequential uncertainties, including unavailable resources or implementation details.
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
The brief specifies a design-only comparison on Phi-3-mini-4k-instruct across three integer precisions and two QuaRot quantization methods. No empirical results, datasets, or verified implementation details have been supplied; the environment lacks network access and GPUs.
````

**Objectives Open**

````text
[
  "Inspect available inputs and separate fixed requirements from assumptions.",
  "Review a proposed controlled comparison and evaluation approach before authorizing the full design.",
  "Identify architecture compatibility, quantization-scope, and feasibility uncertainties."
]
````

### Event 2 — Actor

**Answer**

````text
## Proposed approach (for approval; no experiments run)

### Requirements and source status
The fixed study is Phi-3-mini-4k-instruct, QuaRot-RTN versus QuaRot-GPTQ, at INT4/INT6/INT8, reporting perplexity and zero-shot accuracy. The supplied source IDs are neurips2024/94328/9:setup_1, setup_6, setup_8, and setup_11, but their contents are not available locally. I would not attribute specific datasets, quantizer settings, or architecture support to those sources without clarification. The choices below are proposals rather than verified reproductions of the source setup.

### Comparison matrix and controls
- Primary matrix: two weight-quantization methods × three bit widths = six QuaRot conditions on the same checkpoint. Pending source clarification, interpret bit width b as **Wb/Ab/KVb**: eligible linear weights, quantized activations, and both key and value caches use b ∈ {4,6,8}. This makes the advertised precision explicit rather than silently treating INT6/INT8 as weight-only.
- Define GPTQ versus RTN as a change to **weight quantization only**. Both use identical activation/KV quantizers, rotations, quantized module coverage, calibration examples where applicable, evaluation settings, and precision exceptions. GPTQ uses calibration-derived second-order information; RTN does not need it for rounding. Any activation or clipping calibration is shared.
- Include the original floating-point checkpoint and a rotated-but-unquantized checkpoint. Their agreement checks that the rotation implementation preserves the function before attributing losses to quantization. Keep embedding, output-head, normalization, softmax and accumulation precision explicit and identical across conditions; do not imply every tensor is integer.
- Optional, separately labeled diagnostics: matched unrotated quantization to isolate rotation benefit, or weight-only/mixed-precision conditions to localize degradation. These are not substitutes for the six primary conditions.

### Evaluation and calibration strategy
- Proposed perplexity benchmark: a fixed WikiText-2 test preprocessing/window protocol, with an additional corpus such as C4 if feasible or source-required. Pin tokenizer revision, BOS/EOS handling, document boundaries, context length (within the 4k model limit), stride and scored-token counts. Use identical teacher-forced token sequences in every condition; report loss and perplexity.
- Proposed zero-shot suite: a fixed general-language harness suite such as PIQA, HellaSwag, ARC-Easy, ARC-Challenge, WinoGrande and BoolQ, unless the sources specify otherwise. Pin harness version, task versions, prompts, chat-template policy and each task's accuracy variant. Use no demonstrations; report task scores and a predeclared macro-average without mixing raw and length-normalized scoring arbitrarily.
- Propose a fixed, disjoint training-corpus calibration pool (e.g., 128 sequences of length 2048, subject to source confirmation). Fix sampling and exclude evaluation splits. Separate calibration used by GPTQ from evaluation data; shared activation/KV range fitting or clipping must use the same pool for both methods.
- Hold quantization granularity, symmetric/asymmetric convention, group size, clipping policy and integer ranges constant between RTN and GPTQ where meaningful. Predeclare GPTQ-specific damping, ordering and block settings. Do not give GPTQ or RTN unequal evaluation-driven tuning budgets.
- Verify that the perplexity and accuracy evaluation paths actually exercise the intended KV quantization. A cache-disabled forward may otherwise measure weights/activations but not the advertised low-bit cache. If cache-on evaluation is needed, preserve identical causal contexts and token scoring across methods.

### QuaRot compatibility checks before measurement
Inspect the pinned Phi configuration and implementation rather than assuming LLaMA-targeted code ports unchanged. Check normalization and residual-stream rotation algebra, tied embeddings/output head, fused QKV projection slicing and layout, attention head/KV-head dimensions, RoPE placement, fused gate/up projections and MLP nonlinearity, biases if present, and the placement of online transforms and inverse transforms. Verify Hadamard/rotation support for actual dimensions; do not silently pad or change architecture.

Use staged checks: floating-point rotation equivalence in logits and token loss, tensor shapes and QKV layout, cache-on versus cache-off reference agreement, and synthetic quantizer range/rounding tests at all three widths. Inventory every quantized and exempt module. Failure of equivalence is an implementation issue to resolve, not evidence that QuaRot fails on Phi.

### Analysis and interpretation
Report absolute perplexity, excess token negative log-likelihood/perplexity relative to the floating baseline, accuracy and percentage-point loss, and paired GPTQ-minus-RTN contrasts within each bit width. Examine whether the method gap changes with precision. Use paired item resampling for accuracy and document/block resampling for language-model loss rather than treating correlated tokens as independent. Keep evaluation-sampling uncertainty distinct from calibration/rotation-seed variability; matched repeated seeds are desirable if resources permit.

A Phi-only result could support a **case study of transfer to this particular non-LLaMA checkpoint**, including practical compatibility and quality retention under the specified quantizers. It cannot establish generalization to all non-LLaMA architectures or a family-level advantage. Without unrotated quantization controls it also cannot isolate the benefit of rotation; without a matched LLaMA study it cannot quantify a cross-family generalization gap.

### Feasibility and consequential decisions to resolve
Quality-only fake quantization is acceptable if correctly implemented, explicitly labeled, and applied along the real evaluation paths. INT6 especially may lack native kernels; simulated W6/A6/KV6 does not demonstrate packed storage savings, latency, or deployment feasibility. Integer arithmetic/storage claims would require separate validation. Future execution requires checkpoint/tokenizer access, datasets, compatible software and suitable compute, none of which is currently supplied.

Before the full design, the highest-value clarifications are: (1) whether the cited setups mean Wb/Ab/KVb or another precision allocation, including precision exceptions; (2) their benchmark, calibration and quantizer/GPTQ recipes; and (3) any documented Phi adapter and INT6 implementation. Missing answers need not block design: retain explicitly labeled proposed defaults. Please approve or amend this approach before I expand it into the complete protocol.
````

**Stage**

````text
plan
````

**Evidence**

````text
Local inspection found only /workspace/task.json. It contains the research question and the statement 'Design-only task; repositories and compute are not required' as an embedded documents.track.md value; no standalone track.md, repository implementation, source excerpts, checkpoints or evaluation data were found. A small filesystem/Python check confirmed /workspace and Python 3.12.3. The supplied environment states network disabled, no GPU and no preinstalled project dependencies. These are planning observations only: no model was loaded, no compatibility claim was tested, and no quantization/evaluation experiment was run.
````

**Assumptions**

````text
[
  "Unless clarified by source text, INTb is proposed to mean matched b-bit eligible weights, activations and key/value caches, with documented floating-point exceptions.",
  "Datasets, suite, calibration size, precision exceptions and GPTQ hyperparameters remain proposed choices until source alignment or researcher approval.",
  "Later execution may use external resources; their absence locally does not block this design-only task.",
  "A validated simulation backend can support quality comparisons but not claims about native integer performance."
]
````

**Uncertainties**

````text
[
  "The cited source IDs are present in the request but their setup contents are unavailable locally.",
  "Phi-specific rotation compatibility and module coverage require inspection of the eventual pinned checkpoint implementation.",
  "Native INT6 support and genuine low-bit KV handling in the chosen evaluation path are unknown.",
  "Available future compute and datasets will determine feasible replication and secondary controls."
]
````

### Event 3 — Simulator

**Message**

````text
I approve this approach. Develop the final experiment design, not an executed study. The supplied source excerpts establish the model, methods and three precision levels only; no additional source recipe is available. Adopt Wb/Ab/KVb as an explicitly proposed operational definition, not a recovered source requirement. Keep the six primary conditions and floating/rotated-floating controls, and include matched unrotated quantization as a clearly labeled secondary control to isolate rotation benefit. Specify concrete proposed defaults for quantizer granularity, ranges, clipping, exceptions, GPTQ settings, calibration, benchmark scoring and seed replication rather than leaving a menu of choices. Explain how architecture-dependent choices will be resolved at a pre-evaluation implementation gate, including rotation equivalence tolerances and what happens if they fail. Make explicit how quantized keys and values are exercised even in teacher-forced or harness scoring; distinguish cache-storage quantization from attention-operand quantization where relevant. Provide the comparison matrix, rationale, controls, reproducible evaluation protocol, paired statistical analysis, unfilled reporting template, and realistic feasibility/resource assumptions with a minimal and expanded execution plan. Do not claim measurements or native INT6 support. Retain the appropriately limited interpretation: this is a Phi checkpoint transfer case study, not evidence about all non-LLaMA models.
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
The proposed plan covers the required Phi-3-mini-4k-instruct RTN/GPTQ comparison at 4, 6 and 8 bits, with quality metrics, equivalence checks, calibration separation and paired analysis. Reported local inspection found no implementation or datasets, consistent with a design-only deliverable. Precision allocation and recipes are explicitly assumptions; resolving them as proposed defaults is sufficient to proceed.
````

**Objectives Open**

````text
[
  "Complete final experiment design with concrete proposed settings and compatibility gates",
  "Specify controls, quality evaluation and paired analysis/reporting plan",
  "Describe feasibility and interpretation limits without claiming execution"
]
````

### Event 4 — Actor

**Answer**

````text
# Experiment design: QuaRot transfer to Phi-3-mini-4k-instruct

**Status:** design only. No model evaluation, quantization experiment, or measurement has been performed.

## 1. Scope and evidentiary basis

**Fixed, source-supported requirements:** Phi-3-mini-4k-instruct; QuaRot-RTN versus QuaRot-GPTQ; INT4, INT6 and INT8; perplexity and zero-shot accuracy. The researcher confirms that the supplied source excerpts establish these requirements only (source IDs: neurips2024/94328/9:setup_1, setup_6, setup_8, setup_11).

**All detailed settings below are proposed operational choices, not a recovered source recipe.** In particular, define INTb as **Wb/Ab/KVb**, subject to the explicit precision exceptions below. The target inference is quality retention and relative quantizer performance on one non-LLaMA checkpoint—not native integer speed, memory savings, or generalization across all non-LLaMA models.

## 2. Comparison matrix

| Role | Rotation | Weight method | Weights / activations / K,V |
|---|---|---|---|
| Reference | None | None | Floating |
| Equivalence control | QuaRot | None | Floating |
| Primary, three conditions | QuaRot | RTN | 4/4/4, 6/6/6, 8/8/8 |
| Primary, three conditions | QuaRot | GPTQ | 4/4/4, 6/6/6, 8/8/8 |
| Secondary, three conditions | None | RTN | 4/4/4, 6/6/6, 8/8/8 |
| Secondary, three conditions | None | GPTQ | 4/4/4, 6/6/6, 8/8/8 |

The six QuaRot conditions are primary. Matched unrotated conditions are secondary controls that estimate the benefit of the complete rotation procedure at fixed precision and weight method. They do not isolate individual rotation components.

Use one pinned model/tokenizer revision and the same eligible modules, evaluation examples, activation/cache rules and precision exceptions throughout. The unrotated floating reference is shared; rotated floating controls are checked for every rotation seed.

## 3. Proposed quantization specification

### Common numerical conventions

Use a quality-oriented simulated backend, with floating computation after quantize/dequantize (QDQ). For each symmetric quantization group, define qmax = 2^(b−1)−1, scale = max(abs(x))/qmax, and q = clamp(round_to_nearest_even(x/scale), −qmax, qmax). An all-zero group maps to zero with scale 1. This uses a symmetric signed range and deliberately leaves the most-negative two's-complement code unused. Store scales and perform scale computations in FP32.

There is **no percentile clipping, learned clipping or evaluation-based range search**. Ranges come from the group maximum. GPTQ may saturate corrected values to the same frozen weight range. Accumulations and nonlinear operations remain floating point; this is not a claim of an end-to-end integer model.

| Tensor | Proposed granularity and range |
|---|---|
| Eligible linear weights | Per output row, contiguous groups of 128 input-channel elements; final short group permitted; fixed group maximum from that condition's floating weights |
| Linear-input activations | Dynamic symmetric per-token range across the complete input feature vector at each eligible linear boundary |
| Cached keys and values | Separate dynamic symmetric ranges per layer, token and KV head, across that head's feature dimension |

Quantize weights and input activations for attention Q/K/V/output projections and MLP gate/up/down projections. Fused projections retain their fused matrix layout, with documented output slices. If Q/K/V or gate/up share an input, use the same quantized input rather than independently perturbing it. Quantize each boundary once, not twice through nested wrappers.

**Exceptions:** embeddings, language-model output head, biases, normalization parameters and computations, residual additions, positional calculations, attention softmax/probabilities and accumulation, and quantization scales stay floating. Preserve any original weight tying. Query tensors have no additional dedicated quantizer after projection/positional transformation; keys and values receive their additional quantization at the cache boundary. Wb/Ab/KVb therefore denotes specified tensor boundaries, not every tensor in the network.

Primary quality execution uses a consistent FP32 reference/QDQ arithmetic policy where feasible, avoiding accidental BF16-versus-FP32 differences between conditions. Record any implementation-internal casts; do not introduce lower-precision arithmetic selectively to save resources.

### RTN versus GPTQ

RTN rounds each eligible floating weight directly with the shared group quantizer. GPTQ uses the identical grid construction and grouping, but compensates rounding errors using calibration-derived input second moments.

Proposed GPTQ defaults:
- Block size 128; input-column order unchanged; activation ordering disabled.
- Static group boundaries and scales computed before compensation.
- Damping equal to 0.01 times the mean Hessian diagonal.
- Standard treatment of zero-input/dead dimensions, explicitly recorded in code and logs.
- Collect each target layer's inputs from the same **unquantized** condition-specific model: rotated floating for QuaRot, original floating for secondary unrotated controls. Quantize matrices independently from these statistics; do not use progressive quantized-prefix calibration or optional “true sequential” sublayer recalibration.
- FP32 Hessian statistics and numerically checked factorization. If factorization fails, stop and repair the implementation or revise the protocol before evaluation; do not quietly select per-condition damping.

RTN does not use Hessians. Shared dynamic activation/KV quantizers need no fitted calibration ranges. Thus the additional information used by GPTQ is precisely its weight-calibration information, rather than a different clipping or activation recipe. The same calibration sample list is available to every applicable condition; no method receives extra evaluation-driven tuning.

## 4. Pre-evaluation implementation gate

Pin the checkpoint, tokenizer, loading-library version, QuaRot port, GPTQ implementation and evaluation adapter before running benchmark labels. Produce a manifest of architecture dimensions, transformations, quantizer boundaries and exclusions.

### Architecture-dependent resolutions

Inspect actual configuration and module code rather than assuming LLaMA compatibility:
- Normalization type and placement, residual basis changes, biases, embedding/output-head tying and final normalization.
- Fused QKV and gate/up layouts, query/KV-head counts, attention grouping, RoPE dimensions and application point, output-projection layout and MLP activation.
- Hidden, head and intermediate dimensions and their compatibility with the proposed online transforms.

Default to seeded orthogonal sign/Hadamard constructions where dimensions permit. For non-power-of-two sizes, use a verified exact block/factorized orthogonal construction supported by the port, with explicit inverse and accounting for online transforms. Do not pad/change model dimensions silently. If no efficient exact construction is available, a dense orthogonal fallback is allowed only for a transparently labeled quality-only adapter after gate review; do not represent it as deployment-equivalent QuaRot.

Derive and document the basis changes through every affected branch. In particular, do not assume arbitrary rotations commute with RoPE, normalization or nonlinearities. Any attention-space rotation must preserve QK inner products at its actual placement; value rotations require a corresponding compensation downstream. Resolve fused slicing explicitly. Any necessary change to the proposed rotation algorithm or quantization scope is frozen and disclosed **before** benchmark evaluation. If an algebraically correct port cannot be obtained, report a compatibility blocker rather than generate a misleading quantization comparison.

### Gate tests and tolerances

Use a fixed synthetic set and eight calibration sequences held aside for implementation checking, never benchmark labels. Include short sequences, a 2048-token sequence and a 4096-token sequence within supported context, plus incremental-cache and full-prefix paths.

1. Verify orthogonality/inverses, projection shapes, fused-slice reconstruction, tied-weight handling and all quantizer ranges. Check zero groups, saturation, rounding ties and short weight groups for b=4,6,8.
2. On FP32 original versus rotated floating forward passes, require logit normalized RMS error ≤ 1e−5, maximum absolute logit error ≤ 1e−3, and absolute mean token-NLL difference ≤ 1e−4. Normalize RMS error by max(reference RMS, 1e−8).
3. Apply the same tolerances to floating cache-on versus full-prefix scoring. Localize discrepancies layer by layer, with deterministic attention kernels where possible.
4. Compare the quantized explicit-cache path to an independently implemented causal QDQ attention path under identical cache scaling semantics. Check position handling, head sharing, lengths and scale persistence.
5. Assert from instrumentation that every intended boundary executes at the requested width, including K/V reads during both perplexity and harness scoring. Rotated-floating mode must disable QDQ entirely while retaining transforms.

If thresholds fail, stop, diagnose algebra/layout/numerics, and repeat the gate. Do not relax tolerances after seeing benchmark outcomes. If a justified backend requires amended tolerances, document and freeze that amendment before evaluation and report it as a protocol deviation. Gate success is an implementation check, not evidence of benchmark quality.

## 5. KV-cache semantics and actual scoring paths

Apply key QDQ to the **final key representation stored and consumed by attention**, after positional and any compensated attention-space transforms. Apply value QDQ to the representation actually stored after any value-space transform. Persist each token/head scale unchanged: appending a new token must not rescale old cache entries.

The attention implementation must consume these dequantized cached K/V values for **all** causal attention, including the current token's key/value. It must not use original floating K/V for prefill while merely writing quantized copies for later generation.

Distinguish two claims:
- **Cache-storage quantization:** keys/values are represented by quantized codes plus scales and reconstructed on reads. A fake-quantized FP32 tensor can emulate the same numerical error, but does not demonstrate compressed storage.
- **Attention-operand quantization:** here attention uses the reconstructed low-bit K/V values, while Q, QK accumulation, softmax and probability-times-V accumulation stay floating. There is no additional integer attention kernel or quantized softmax claim.

For teacher-forced scoring, prefill a fixed chunk of 128 tokens and continue in chunks of 128 with explicit cache writes/reads and correct causal masks. Within each chunk, attention must also use QDQ K/V. Dynamic per-token scales make these semantics independent of future chunks. Validate against single-token streaming on gate examples.

For harness log-likelihood, route every prompt-plus-candidate sequence through the same cached scorer, including prompt prefill. Score only candidate tokens, using logits shifted by one token. Identical-prefix reuse is optional, but a reused cache must contain the same QDQ values and cannot leak candidate information. Generation-based evaluation is not needed for the chosen suite. These requirements prevent a default cache-disabled harness from silently omitting KV error.

## 6. Calibration, evaluation and replication

### Calibration

Proposed calibration corpus: pinned English C4 training split. For each seed, select 128 distinct documents with at least 2048 tokenizer tokens and sample one contiguous 2048-token span per document. Use the tokenizer without added special tokens. Freeze document IDs/hashes, starts and ordering. Reject exact normalized-document overlaps with evaluation text and log that broader pretraining contamination cannot be ruled out.

The same sample list is used for GPTQ across bit widths and rotation controls within a replicate. Calibration sequences are separate from the implementation-check holdout. Calibration selection, rather than benchmark quality, determines these data.

### Perplexity

Primary dataset: pinned WikiText-2 raw test split. Join the dataset's text rows in order with exactly two newline characters; preserve row contents. Tokenize once with add_special_tokens=False, adding no BOS or EOS. Divide the stream into nonoverlapping windows of 2048 tokens; keep the final window if it contains at least two tokens. Each window starts with an empty cache. Score tokens 2 through the end using the cached teacher-forced scorer above; the first token of each window is unscored. Publish the serialized-text hash, token count, window count and scored-token count.

Report token-weighted mean NLL and perplexity exp(mean NLL). This is a deliberately specified protocol, not necessarily directly comparable to external WikiText-2 numbers using other strides or preprocessing.

Expanded execution adds a fixed C4 validation slice: first 256 eligible documents in a pinned deterministic shard order, one first-2048-token window per document, same scoring rules. Keep this corpus separate from C4 training calibration and report it separately.

### Zero-shot accuracy

Use pinned evaluation-harness definitions for PIQA, HellaSwag, ARC-Easy, ARC-Challenge, WinoGrande and BoolQ; full official harness evaluation splits: PIQA/HellaSwag/WinoGrande/BoolQ validation and ARC-Easy/Challenge test. Use zero demonstrations, harness plain-text prompts and **no chat template** for the primary study. This fixes the scoring policy for the instruct checkpoint rather than tuning it by model condition.

Primary task metrics: length-normalized accuracy (harness acc_norm) for PIQA, HellaSwag and both ARC tasks; raw accuracy (acc) for WinoGrande and BoolQ. Use the pinned harness's exact candidate normalization definition, storing candidate tokenization and scores so it is reproducible. Macro-average these six predeclared task metrics with equal task weight. Also report raw accuracy for the four normalized tasks as supplementary results; never switch the primary metric after viewing outcomes.

Use identical examples, prompt rendering, tokenization and deterministic tie-breaking in every condition. Enforce the 4096-token model limit; log any exclusions, applied identically across all conditions. Do not silently truncate answer choices. Retain per-example scores and correctness.

### Seeds

Expanded replication uses seeds 17, 29 and 43. Each seed determines a rotation and a calibration draw through separately named RNG streams. Share both streams across RTN/GPTQ and bit widths within that seed. Unrotated GPTQ shares the calibration draw. Unrotated RTN and original floating need not be rerun because they have neither random rotation nor GPTQ calibration dependence.

Report each seed and their mean. This measures joint rotation/calibration variability, not a separately identified contribution from each. Evaluation itself is deterministic. Three seeds are modest robustness evidence, not a precise population estimate of seed variability.

## 7. Paired analysis

Predeclare contrasts:
1. Primary: GPTQ minus RTN at each bit width within QuaRot, paired by seed and evaluation unit.
2. Quality retention: each primary condition minus original floating reference; rotated-floating quality should agree as verified at the gate.
3. Secondary rotation effect: rotated minus matched unrotated quantization, separately for method and width.
4. Descriptive precision trends and changes in method gap from 4→6→8; do not assume monotonicity.

For language modeling, report mean NLL, perplexity, ΔNLL and perplexity ratio versus floating. GPTQ−RTN ΔNLL below zero favors GPTQ; show the associated perplexity contrast as well.

For accuracy, report task values, macro-average, and percentage-point differences. GPTQ−RTN above zero favors GPTQ.

Use 10,000 paired bootstrap draws with a fixed analysis seed, resampling the same evaluation units for all compared conditions. For WikiText-2, resample contiguous blocks of four windows to reduce false independence from nearby text; for expanded C4, resample documents. Aggregate losses by scored-token counts and exponentiate only after aggregation. For accuracy, resample examples within each task and recompute the equal-task macro-average. In the expanded study, average paired contrasts across the three fixed seeds within each resample.

Report 95% percentile intervals as evaluation-sampling uncertainty **conditional on those seeds**. Separately show the seed range and standard deviation. These are not confidence intervals over all possible models or calibration sets. Treat intervals as estimation aids; no primary significance claim or post hoc winner selection across many tasks is planned. If formal hypothesis testing is subsequently requested, predeclare multiplicity adjustment before results.

## 8. Unfilled reporting template

| Condition | Seed | Precision / exceptions | PPL | ΔNLL vs FP | PPL ratio vs FP | Zero-shot macro (%) | Δpp vs FP | Gate/deviations |
|---|---|---|---|---|---|---|---|---|
| Original floating | — | FP32 | — | — | — | — | — | — |
| Rotated floating | — | FP32 | — | — | — | — | — | — |
| QuaRot-RTN | — | W4/A4/KV4 | — | — | — | — | — | — |
| QuaRot-GPTQ | — | W4/A4/KV4 | — | — | — | — | — | — |
| QuaRot-RTN | — | W6/A6/KV6 | — | — | — | — | — | — |
| QuaRot-GPTQ | — | W6/A6/KV6 | — | — | — | — | — | — |
| QuaRot-RTN | — | W8/A8/KV8 | — | — | — | — | — | — |
| QuaRot-GPTQ | — | W8/A8/KV8 | — | — | — | — | — | — |
| Unrotated controls, six rows | — | Matched | — | — | — | — | — | — |

Provide a separate six-task table, per-seed tables, and a contrast table with estimate and paired 95% interval for each primary method comparison and secondary rotation comparison. Attach revision hashes, module inventory, calibration/evaluation manifests, gate logs, precision-path assertions and deviations. All cells above are intentionally unfilled.

## 9. Feasibility and execution tiers

**Minimal complete execution:** one seed (17), original floating and rotated-floating controls, all six primary conditions, all six secondary conditions, WikiText-2 and the full six-task suite. This is 14 condition configurations before accounting for reusable artifacts. Gate first; then quantize/evaluate one condition at a time, retaining weights or reconstruction manifests and per-example outputs. Report uncertainty conditional on one seed and make no seed-robustness claim.

**Expanded execution:** all three seeds, the same conditions and tasks, plus C4 validation perplexity. Reuse deterministic references/unrotated RTN outputs rather than pretending reruns are independent replicates. Additional profiling is outside the main quality question and requires separate native-kernel validation.

Future execution needs checkpoint/tokenizer and corpus access, a validated Phi port, evaluation software and suitable compute. A practical target is a GPU with roughly 48–80 GB memory for the conservative FP32 design, plus substantial host RAM and disk. This is a planning estimate, not a verified requirement: layerwise Hessian collection, batch size one, CPU offload and sequential processing may permit smaller devices at higher runtime. Determine actual memory with an implementation-only dry run before scheduling; do not promise a runtime without profiling. Avoid storing every layer's calibration activation simultaneously.

The current offline, CPU-only environment is suitable for planning but not assumed sufficient for timely full evaluation. INT6 QDQ is numerically implementable with ordinary floating/integer operations, but **native INT6 kernels and packed six-bit cache storage are not assumed**. Quality simulation cannot substantiate throughput, bandwidth or memory-savings claims.

## 10. Interpretation rules

A successful gate and acceptable quality retention would support transfer of the specified QuaRot implementation to **this Phi checkpoint**, under the specified precision semantics. The matched controls would reveal whether rotation improves quantized quality here and whether GPTQ's additional calibration improves on RTN at each width. Poor quantized quality after a successful gate is a valid checkpoint-specific finding; a failed gate is an unresolved porting issue, not a quantified failure of QuaRot's statistical generalization.

Neither result establishes behavior on all Phi models, all non-LLaMA architectures, or a relative generalization gap against LLaMA. Those claims require additional checkpoints/families and matched cross-family experiments.
````

**Stage**

````text
result
````

**Evidence**

````text
Repository observations: /workspace contains only task.json. Its embedded documents.track.md text states that this is design-only and repositories/compute are not required; there is no standalone track.md or implementation. A small exploratory filesystem check confirmed these files and Python 3.12.3. No local checkpoint, tokenizer, datasets, source recipe, or QuaRot/GPTQ code was available. The supplied environment reports disabled networking, no GPU and no preinstalled project dependencies. The researcher explicitly approved the proposed approach and clarified that the source excerpts support only model, methods and precision levels. Consequently all granular quantizer, calibration, evaluation and statistical settings are labeled proposed defaults. The controls separate floating transformation error, weight-method effects and rotation benefit; explicit cache-path tests prevent nominal KV settings from being bypassed during scoring. No experimental outcomes or hardware support have been inferred from exploratory commands.
````

**Assumptions**

````text
[
  "Wb/Ab/KVb is an approved proposed operational definition, not a source requirement; floating exceptions and cache boundaries delimit its meaning.",
  "A future implementation can provide an algebraically valid Phi-specific QuaRot port; this remains contingent on the pre-evaluation gate.",
  "Future workers can obtain the pinned checkpoint, tokenizer, C4, WikiText-2 and harness datasets in an execution environment with adequate resources.",
  "Quality-oriented simulated quantization is acceptable; native integer arithmetic, packed INT6 storage and performance measurement are outside this study.",
  "The proposed FP32 execution policy and memory target may require layerwise processing/offload; resource estimates are not measured."
]
````

**Uncertainties**

````text
[
  "Actual Phi module layouts, supported rotation dimensions and any necessary adapter deviations cannot be verified without the model implementation.",
  "Cache and harness integration must be instrumented to establish that quantized K/V affects all scored attention operations.",
  "The size of GPTQ Hessians, FP32 attention workspaces and total evaluation runtime require a future implementation-only resource check.",
  "Three seeds characterize only limited rotation/calibration variability, and one checkpoint cannot support architecture-family generalization claims."
]
````

### Event 5 — Simulator

**Message**

````text
The final design satisfies the requested design-only deliverable. It specifies the six primary Phi comparisons, floating and matched unrotated controls, concrete proposed quantization and calibration settings, architecture and cache-path validation gates, perplexity and zero-shot protocols, paired analysis, reporting templates, and feasible execution tiers. Retain the explicit qualification that Wb/Ab/KVb and detailed recipes are proposed choices, compatibility remains contingent on implementation checks, and no experiments or native INT6 capabilities have been demonstrated. No further revision or experimental execution is required.
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
The reported protocol covers INT4/INT6/INT8 QuaRot-RTN versus QuaRot-GPTQ with shared activation/cache rules and explicit floating exceptions. It includes rotation-equivalence checks, quantized K/V consumption during scoring, disjoint calibration, fixed benchmark metrics, paired uncertainty estimates, and limited checkpoint-specific interpretation. Resource and adapter uncertainties are disclosed rather than presented as verified results. These meet the agreed design-only scope; empirical outcomes remain intentionally unknown.
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
  "event_log": "runs/openai-astra-top2-first-pass/episodes/expbench_neurips2024_94328_9-f027985e5a4b/persona_off/attempt-1/output/neurips2024__94328__9/events.jsonl",
  "event_log_sha256": "6e2a9466fdf4a8f5dbde5400eb38aa40546d56d2bfd202d94cbfd9ab8e626a67",
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
