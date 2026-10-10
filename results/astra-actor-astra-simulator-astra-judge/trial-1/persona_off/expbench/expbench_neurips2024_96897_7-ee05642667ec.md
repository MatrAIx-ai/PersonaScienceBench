# persona_off · expbench · neurips2024/96897/7

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
Please inspect the supplied task inputs and any relevant local documentation, without requiring repository access or compute. Report what is established versus unspecified, and propose an approach for designing a fair BAdam-versus-LoRA comparison when finetuning Llama 3-70B on MathInstruct and evaluating zero-shot math performance. At this stage, provide only inspection findings, a proposed design outline, and consequential assumptions or uncertainties—not the full experiment design. In particular, flag choices about model variant, method configurations, training and tuning budget fairness, benchmark selection and contamination, zero-shot evaluation protocol, variability and statistical comparison, and feasibility. Treat absent source details as unresolved or explicitly proposed assumptions. This is a design-only task: do not run training or claim empirical results.
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
The brief specifies the model family and size, dataset, comparison methods, and zero-shot math objective, but supplies no empirical outcome, resource budget, or detailed setup. The available task note states that repositories and compute are not required.
````

**Objectives Open**

````text
[
  "Inspect available inputs and distinguish established requirements from missing setup details.",
  "Review a proposed comparison approach and consequential assumptions before authorizing the full design.",
  "Ultimately deliver a final experiment design with rationale, controls, analysis plan, and feasibility, without claiming execution."
]
````

### Event 2 — Actor

**Answer**

````text
## Inspection findings
The supplied task establishes only the comparison: BAdam versus LoRA, finetuning Llama 3-70B on MathInstruct, with zero-shot math performance as the outcome. The repeated question is a duplicate, not a second experimental condition. Embedded `track.md` says this is design-only and repositories and compute are not required. No paper, implementation, hyperparameters, dataset revision, benchmark list, or hardware specification for a future experiment is supplied. There is consequently no source-supported basis for predicting which method will win.

## Proposed design outline (pending approval)
1. **Define the target and controls.** Select an exact Llama 3-70B checkpoint and revision shared by both methods, plus the corresponding unfine-tuned checkpoint as a baseline. Provisionally use the original base model rather than Instruct to reduce confounding from prior instruction tuning; this is a proposal, not a supplied requirement. Fix tokenizer, formatting, loss masking, context length, precision, data preprocessing, and evaluation behavior across arms.
2. **Specify method configurations.** Verify the intended BAdam implementation and define block partition, block activation order/switch interval, optimizer settings, and trainable components. Define LoRA rank, scaling, dropout, target modules, and trainable exceptions. Do not silently substitute QLoRA or a different BAdam variant. Record method-specific resource needs rather than treating equal trainable-parameter counts as fairness.
3. **Separate notions of budget fairness.** Propose a primary matched-training-exposure comparison with identical examples/tokens, effective batch size, and data order within paired seeds. Report resource differences. Add a separately labeled matched-resource comparison only if feasible, since equal tokens and equal wall time or compute generally cannot all be imposed simultaneously. Predeclare tuning ranges and use held-out MathInstruct validation, not test benchmarks, for selection. Set explicit per-method tuning allowances; equal trial counts alone need not imply equal tuning compute. Define whether the intended claim concerns tuned methods at equal resources or the best configurations at equal training exposure.
4. **Choose benchmarks and audit overlap first.** Candidate independent endpoints are GSM8K and MATH test performance, contingent on the chosen MathInstruct release and overlap audit. Inspect MathInstruct source provenance and check exact, normalized, and near-duplicate problem overlap across training, validation, and candidate benchmarks. Prespecify how benchmark-derived training sources and detected overlaps are removed or flagged. Preserve benchmark membership where practical and report exclusions; if cleaning alters MathInstruct, limit the claim to that explicitly defined filtered version. Shared pretraining contamination cannot be eliminated by finetuning-data cleaning.
5. **Lock a genuinely zero-shot evaluation protocol.** No demonstrations, benchmark-specific prompt tuning, or benchmark-based checkpoint selection. Use one task instruction format, with any request for reasoning fixed in advance, identical decoding and generation limits, and a versioned answer-extraction/equivalence scorer. Provisionally use deterministic, single-sample accuracy without external tools; distinguish zero-shot reasoning from an answer-only protocol. Address invalid answers and truncation consistently.
6. **Plan variability and inference.** Provisionally target at least three paired training seeds, subject to feasibility, matching data-order seeds across methods where meaningful. Prespecify a primary outcome—such as equally weighted mean benchmark accuracy—alongside per-benchmark accuracy, BAdam-minus-LoRA differences, and uncertainty. Account for both paired evaluation items and independent training runs; do not treat thousands of benchmark questions as substitutes for training replication. Define practical significance and multiplicity handling before testing, and permit an inconclusive result.
7. **Assess feasibility without executing training.** In the full design, estimate weight, gradient, optimizer, activation, and adapter memory separately, then specify candidate hardware, sharding/offload, and throughput checks. BAdam's blockwise updates do not remove the need to accommodate the backbone; LoRA likewise requires the backbone. Future smoke checks would verify correct parameter updates, data formatting, loss behavior, and evaluator correctness before a costly run. No GPU experiment is possible in the supplied environment, and none is necessary for this design stage.

## Consequential unresolved choices
Before elaborating, the most useful clarifications are: (1) base versus Instruct and exact checkpoint; (2) intended BAdam variant/implementation and any mandated LoRA settings; (3) exact MathInstruct release and permitted contamination filtering; (4) primary fairness criterion, future hardware, and tuning/training caps; (5) mandated benchmarks and meaning of zero-shot, including reasoning and tools; and (6) acceptable replication budget and the operational meaning of 'better.' With no supporting sources, these remain decisions to approve, not facts to infer.

This is an outline only. No training, benchmark evaluation, or empirical outcome is claimed; full experiment design awaits explicit approval.
````

**Stage**

````text
plan
````

**Evidence**

````text
Inspected `/workspace` and read `/workspace/task.json`. The directory contained only task.json; a lightweight listing and Python JSON inspection confirmed top-level fields `question`, `context`, and `documents`. `documents` embeds `track.md` with the text: 'Design-only task; repositories and compute are not required.' There is no separate local track.md, source repository, method documentation, or data artifact in the listing. Supplied environment metadata states network disabled, datasets empty, dependencies not preinstalled, and GPU disabled. Exploration was limited to local listing and reading the task specification.
````

**Assumptions**

````text
[
  "Proposed, not fixed: original Llama 3-70B base checkpoint rather than an Instruct checkpoint.",
  "Proposed, not fixed: matched training exposure as the primary comparison, with resource costs reported and an optional distinct resource-matched comparison.",
  "Proposed, not fixed: GSM8K and MATH as candidate endpoints, subject to dataset provenance and contamination review.",
  "Proposed, not fixed: deterministic single-sample, tool-free zero-shot evaluation and at least three paired training seeds.",
  "Fixed task requirements are the BAdam-versus-LoRA comparison, Llama 3-70B, MathInstruct finetuning, zero-shot math outcomes, and design-only work; the proposals above are not source-supported setup details."
]
````

**Uncertainties**

````text
[
  "Exact checkpoint, dataset revisions, implementations, method hyperparameters, and training format are unspecified.",
  "Hardware feasibility, training duration, tuning allowance, and replication affordability cannot be established from supplied inputs.",
  "MathInstruct-to-benchmark overlap and original-model pretraining contamination have not been measured; no clean benchmark claim is warranted.",
  "Primary outcome, fairness estimand, practical superiority threshold, and exact zero-shot protocol require approval."
]
````

### Event 3 — Simulator

**Message**

````text
Proceed with the full design using your proposed approach. Adopt, explicitly as design assumptions rather than source-established facts, Llama 3-70B base, matched training exposure as the primary estimand, GSM8K and MATH subject to an overlap audit, and deterministic single-sample tool-free zero-shot reasoning evaluation. Include the unfine-tuned baseline. The primary claim should concern validation-selected configurations under a predeclared tuning allowance at equal training exposure; report compute differences and keep any resource-matched comparison secondary and conditional on feasibility.

Make the final design operational: propose concrete training and tuning settings or bounded search spaces for both methods, specify the intended BAdam algorithm variant and block schedule without inventing implementation details, and distinguish configurable proposals from implementation checks required before execution. Specify data splits, preprocessing, masking and token accounting, contamination exclusion rules, checkpoint selection, fixed prompts and decoding, scoring and invalid-output handling. Avoid using benchmark outcomes to tune or select configurations. State how filtering limits the claim about MathInstruct.

Prespecify an equally weighted mean of the two benchmark accuracies as the primary endpoint, report each benchmark separately, and give a paired-seed/item uncertainty plan that respects both sources of variability. Target at least three paired seeds, acknowledge the inferential limits of that small replication count, and define a proposed practical-superiority threshold and rules for superior, inconclusive, or worse outcomes without predicting results. Provide approximate memory accounting and a plausible future hardware plan with explicit uncertainty, tuning and replication costs, and go/no-go smoke checks; no execution or fabricated throughput is needed. Deliver a self-contained final experiment design with rationale, controls, analysis plan, feasibility, and remaining uncertainties. Exact revisions and unavailable source details may remain clearly marked prerequisites rather than guessed facts.
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
The reported inspection finds only the task specification and embedded design-only instruction, with no method documentation, data, or compute available. The outline addresses the requested comparison, distinguishes budget fairness, proposes contamination controls and paired evaluation, and appropriately avoids claiming an empirical outcome. Its unresolved setup choices can be adopted as explicit design assumptions, so no further inspection is required before developing the design.
````

**Objectives Open**

````text
[
  "Operational final experiment design and rationale",
  "Concrete method configurations, tuning fairness, and training controls",
  "Contamination-aware zero-shot evaluation and statistical decision plan",
  "Resource feasibility and explicit assumptions or prerequisites"
]
````

### Event 4 — Actor

**Answer**

````text
# Experiment design: BAdam versus LoRA for zero-shot math

## 1. Question and scope of the claim
Compare **validation-selected BAdam and LoRA configurations under a predeclared tuning allowance and equal final training exposure**, starting from the same Llama 3-70B base checkpoint and finetuning on a contamination-filtered version of MathInstruct. Include the unfine-tuned checkpoint as a baseline.

The primary endpoint is the equally weighted mean of GSM8K and MATH test accuracies. Report each benchmark separately. The experiment can answer which selected configuration works better under this particular protocol; it cannot establish that one method is universally superior or optimally tuned.

These are approved **design assumptions**, not recovered source facts: base rather than Instruct model; training-exposure matching; the two candidate benchmarks; deterministic, single-sample, tool-free zero-shot reasoning evaluation. Exact checkpoint, dataset, benchmark, tokenizer, and implementation revisions are prerequisites to execution. The supplied documentation establishes none of them.

## 2. Freeze the experimental artifacts
Before training, archive a manifest containing:
- Exact model/tokenizer identifiers, immutable revisions, weight hashes, license/access status, and tokenizer special-token behavior.
- MathInstruct revision and source-provenance fields; canonical GSM8K and full MATH test releases, not an unannounced reduced subset.
- Training, BAdam, LoRA, distributed-runtime, and evaluator code revisions; dependency lockfile; prompts; search table; seeds; and split/exclusion hashes.
- Hardware, precision, sharding/offload settings, and all departures from this protocol.

Resolve implementation feasibility before opening benchmark performance results. Do not replace the model with Llama 3.1, an Instruct checkpoint, a quantized backbone, or QLoRA while retaining the original comparison label.

## 3. Dataset construction and contamination controls
### Audit before splitting
1. Inventory MathInstruct source datasets and check rights and provenance. Identify known GSM8K- or MATH-derived sources. For this conservative design, exclude **all identifiable MathInstruct records derived from either benchmark family, including their training splits**, not merely matching test questions. This sacrifices training coverage to make the evaluation more interpretable.
2. Check remaining records against both benchmarks' available question sets. Exclude exact question matches after Unicode normalization, whitespace normalization, and consistent representation of simple LaTeX spacing. Do not erase numbers or mathematical operators: superficially similar questions with different quantities are not automatically duplicates.
3. As an operational near-duplicate screen, flag question word-5-gram Jaccard similarity at least 0.80, using candidate retrieval for scale; for short questions use normalized edit similarity at least 0.90. These are proposed screening thresholds, not validated guarantees. Review flags blind to method outputs and exclude confirmed copies, paraphrases of the same mathematical instance, and solution-bearing reproductions. Retain an adjudication log. Inspect solution text for copied benchmark question text as well.
4. Deduplicate within MathInstruct and group remaining near-duplicates into clusters before splitting. Record counts and source distributions at each exclusion stage. Audit a fixed random sample of unflagged records for missed overlap; adjust audit rules only before training and document changes.

Preserve the canonical benchmark test membership when possible by removing training overlaps. If overlap cannot be adequately assessed because of missing provenance, report that limitation and stop short of a clean-transfer claim. If either benchmark must be replaced, amend the protocol before training; do not silently change the primary endpoint afterward. Shared pretraining contamination remains unknown and is not solved by this audit.

### Splits and representation
- After filtering, take a deterministic 95% training / 5% validation split by duplicate cluster, approximately stratified by source and reasoning type where reliable metadata exist. Publish record IDs and hashes. Validation is used only for configuration selection and diagnostics, never as training data.
- Use one representation for both methods: a fixed problem prompt followed by the supplied MathInstruct response. Preserve valid supplied reasoning; exclude empty, malformed, or problem-only records. Record exclusion reasons. Do not generate new teacher answers.
- Training prompt: `Solve the following math problem. Show your reasoning, then give your final answer as \\boxed{answer}.\n\nProblem: {problem}\n\nSolution:\n`.
- Apply exactly one tokenizer-defined beginning-of-sequence token and one end-of-sequence token after the response, according to the verified tokenizer convention. Do not apply an Instruct chat template. Retain original response content rather than rewriting possibly ambiguous answers into boxes.
- Proposed maximum training length: **4,096 tokens including prompt and response**. Exclude overlength records instead of truncating away questions or answer endings. Report the number and source mix removed. Use un-packed, dynamically padded sequences initially; padding labels are ignored. An optimized packing alternative requires verified example isolation and identical behavior in both arms before adoption.
- Mask prompt and padding tokens from the loss; supervise response tokens and response-ending EOS only. Normalize accumulated loss by the total number of supervised tokens, not by unweighted averages of microbatch losses.

Report both nonpadding input tokens and supervised response tokens. An epoch means one pass through the identical retained training records. Filtering and length exclusion mean the final claim concerns **this documented subset of MathInstruct**, not the untouched dataset.

## 4. Shared training controls
Proposed common settings:
- BF16 backbone and computation, with FP32 optimizer moments where supported; no backbone quantization.
- Freeze token embeddings and output head in both methods. Use gradient checkpointing and compatible distributed sharding. Record any other frozen parameters.
- Effective global batch: **64 examples**, microbatch initially one example per device, with accumulation adjusted to hardware. Match global batches and example order within paired seeds. Keep the last partial batch and normalize it correctly.
- Train for **one complete epoch**, with no validation early stopping. Adam-style betas `(0.9, 0.999)`, epsilon `1e-8`, gradient-norm clipping at 1.0, 3% linear warmup followed by cosine decay to 10% of peak learning rate. Clip parameters with gradients, acknowledging that these sets differ by method.
- The final epoch checkpoint is the only eligible checkpoint for tuning selection. Intermediate checkpoints are recovery artifacts, not additional selectable candidates.

A fixed one-epoch exposure is intentionally concrete rather than asserted optimal. If feasibility checks require changing length, batch, or exposure, revise the protocol for both methods before scored tuning begins.

## 5. Method definitions and bounded tuning
### BAdam arm
Use the **blockwise full-parameter-update variant commonly designated BAdam/BlockAdam**, not a sparse-coordinate or block-ratio variant. Partition the trainable transformer backbone into **one transformer layer per block**, including that layer's attention, MLP, and normalization parameters. Only the active block receives updates during a block window; other weights remain fixed during that window but participate in the required forward/backward computation. Keep the final standalone normalization frozen to avoid inventing a special extra block.

Proposed schedule: visit transformer layers in ascending index order, cycle repeatedly, and switch active block every **50 or 100 optimizer steps**. The schedule operates on optimizer updates, not accumulation microsteps. Verify the layer count from the checkpoint; an 80-layer architecture is only the basis of the memory illustration below.

Eight tuning candidates, the full Cartesian product:
- Peak learning rate: `{1e-5, 2e-5}`.
- Block switch interval: `{50, 100}` optimizer steps.
- Decoupled weight decay: `{0, 0.1}`, excluding normalization and bias parameters.

**Required implementation checks, not invented algorithm facts:** establish from the selected release how blocks are constructed, whether it supports the requested cyclic order, how Adam step counters and moments behave when blocks are revisited, where inactive state resides, and whether weight decay or gradient clipping can inadvertently modify inactive blocks. Use the documented native moment lifecycle, record it explicitly, and do not silently reset or retain moments to improve results. If that lifecycle or schedule differs materially from the intended variant, obtain a protocol amendment before execution. Test distributed/sharding compatibility and the frozen embedding/head behavior.

Before tuning, calculate total optimizer steps from the audited dataset. Require enough steps to complete at least **two full block cycles even at the longest candidate interval**, so later layers are not effectively neglected. If this is infeasible, shorten both switch candidates prospectively or revise exposure for both arms; do not proceed with an incomplete-cycle comparison without redefining the claim.

### LoRA arm
Apply standard LoRA to attention Q/K/V/output projections and MLP gate/up/down projections in every transformer layer. Freeze backbone weights and normalizations; train only adapters. No bias or embedding/head training. Use the conventional scaling `alpha/r`, not rank-stabilized scaling, dropout **0.05**, weight decay **0**, and a verified standard initialization whose initial adapter contribution is zero.

Eight tuning candidates, the full Cartesian product:
- Rank: `{16, 64}`.
- Peak learning rate: `{1e-4, 2e-4}`.
- Scaling `alpha/r`: `{1, 2}`.

Verify exact module names, adapter count, initialization, and frozen/trainable tensors before execution. BAdam's normalization updates versus LoRA's frozen normalizations are part of the specified method packages, not an isolated low-rank-only causal comparison. Report trainable parameter counts; do not force artificial equality between them.

### Allowance and selection
Each method receives **eight full-exposure trials**, using the same designated tuning data-order seed, and the same number of validation measurements. Thus each receives eight training epochs' worth of tuning tokens in aggregate, not eight epochs in a single trial. Select the configuration with the lowest aggregate held-out response-token negative log-likelihood at the final checkpoint. Prespecify tie-breaking within `1e-4` nats/token: smaller rank for LoRA or shorter switch interval for BAdam, then lower learning rate, then the remaining search-table order.

No benchmark evaluation informs search expansion, prompt choice, length choice, or checkpoint selection. Selection by validation likelihood is an imperfect proxy for math accuracy but avoids exploiting benchmark labels. Equal trial count and exposure are **not equal GPU-hour tuning budgets**. Report both methods' actual tuning costs, and bound the primary claim to these search spaces. Resource exhaustion must not result in selectively dropping expensive candidates; amend the allowance prospectively or report an incomplete comparison.

## 6. Independent replications and baseline
After locking both selected configurations, train **three new paired seeds**; five or more are preferable if funded. Use the same record permutations and batches within each seed pair. Adapter initialization/dropout randomness is method-specific, so paired seeds control data randomness rather than making the methods stochastic equivalents. Do not recycle the winning tuning trial as an independent replicate. Evaluate all six final models plus the unfine-tuned baseline.

Costs are therefore **16 tuning runs plus 6 final runs = 22 one-epoch training runs**. Three-seed results characterize final-training variability conditional on a single tuning exercise; they do not estimate the variability of rerunning the whole hyperparameter search.

## 7. Locked zero-shot evaluation
Use the identical plain-text problem prompt specified above, with no demonstrations, retrieved context, calculators, code execution, or self-consistency sampling. No benchmark-specific prompt variants. Evaluate the baseline the same way.

Proposed decoding: greedy argmax, `do_sample=false`, one completion per question, maximum **2,048 new tokens**, EOS stopping only, and total prompt-plus-generation length within the verified model context. Do not silently truncate benchmark problems; detect context violations before scoring and resolve them prospectively. Record runtime nondeterminism rather than claiming bitwise reproducibility from greedy decoding alone.

Lock and test answer extraction before evaluating study checkpoints:
1. Parse the final well-formed boxed expression, using balanced delimiters.
2. If no box exists, allow only an explicitly marked final-answer span such as `Final answer:` or `The answer is`, taking the last such span. Do not use a generic last-number fallback or a model judge.
3. GSM8K: require a single finite numeric answer, normalize separators and exact rational/decimal representations, and compare exact numeric value to the canonical target. Handle permitted currency/unit wrappers by a fixed rule.
4. MATH: use a pinned deterministic evaluator with documented normalization and bounded symbolic-equivalence checks, including structured answers where supported. Apply safe parsing and timeouts; never execute generated code. Fix any permitted numeric tolerance in the scorer manifest before evaluation.
5. Unparseable, ambiguous multiple-answer, empty, wrong, evaluator-timeout, and token-limit-truncated completions score incorrect. Report each failure rate separately; do not discard these examples from denominators.

Validate the scorer on a hand-built set of correct/incorrect equivalent forms, fractions, signs, sets, intervals, malformed boxes, and adversarial strings, independently of study outputs. Any manual audit of scored outputs must be blinded to method and cannot become selective rescoring.

## 8. Endpoints and statistical comparison
For method `m`, seed `s`, and benchmark `b`, let `A[m,s,b]` be percent correct on the full fixed test set. Define:

`P[m,s] = (A[m,s,GSM8K] + A[m,s,MATH]) / 2`.

The primary estimated effect is `mean_s(P[BAdam,s] - P[LoRA,s])`, in **percentage points**. Average seeds equally and benchmarks equally, irrespective of benchmark sizes. Also report each seed, each benchmark, baseline accuracy, each method's improvement over baseline, invalid-output rates, and training/resource measurements.

### Uncertainty
- Use **10,000 paired hierarchical bootstrap replicates**: resample seed pairs, then independently resample question IDs within each benchmark. Use the same sampled question IDs for both methods and all sampled seeds; this preserves question difficulty and method pairing. Compute the primary difference in every replicate and report a percentile 95% interval. Report similarly constructed per-benchmark intervals as secondary, descriptive intervals, without claiming multiplicity-controlled benchmark superiority.
- Also report the three paired-seed effects and a paired Student-t 95% interval across seeds for the fixed benchmark sets, with two degrees of freedom. This is a sensitivity analysis with a strong small-sample distributional assumption, not a cure for limited replication.
- Three seeds give weak information about training variability; bootstrap intervals can be unstable, and benchmark items are not substitutes for independent runs. Neither procedure incorporates uncertainty from choosing these benchmark families or rerunning tuning. Stronger generalization requires more seeds and other uncontaminated benchmarks.

Proposed practical margin: **1.0 percentage point** on the primary endpoint, chosen as a design judgment rather than a known meaningful threshold.
- **Practically superior under this protocol:** primary interval lies entirely above `+1.0` point and the paired-seed sensitivity interval also lies above `+1.0`.
- **Practically worse:** both intervals lie entirely below `-1.0` point.
- **Inconclusive for practical superiority/inferiority:** all other cases, including small positive estimates, conflicting uncertainty analyses, or wide intervals.

These conservative decision labels are not an exact-coverage guarantee with three seeds. Report numerical estimates regardless of label; failure to establish superiority is not equivalence. Do not add seeds opportunistically until a preferred result appears; choose three versus a larger fixed count before benchmark scoring.

## 9. Feasibility and resource accounting
### Illustrative memory, not measured utilization
For a 70-billion-parameter BF16 backbone, weights alone are approximately **140 GB decimal (130 GiB)**. Ordinary full Adam would add roughly 280 GB for FP32 gradients, 560 GB for two FP32 moments, and potentially 280 GB for FP32 master weights, before activations; exact layouts differ.

For an illustrative 80-layer backbone, one transformer-layer block is of order **0.85–0.9 billion parameters**. Active-block gradients cost roughly 1.7–3.6 GB depending on precision, two FP32 moments about 7 GB, and an optional master copy about 3.5 GB. BAdam saves GPU optimizer memory only to the extent its actual implementation limits or offloads inactive state. Retaining moments for every layer on GPU could reintroduce hundreds of GB. Full forward activations, necessary backward paths, temporary collectives, and sharding buffers remain additional costs.

For the usual Llama 3-70B projection dimensions, the proposed LoRA targets yield roughly **207 million adapter parameters at rank 16 and 828 million at rank 64**; recompute from the actual checkpoint. Adapter weights, gradients, two moments, and optional master copies are approximately 12–16 bytes per adapter parameter, or roughly **2.5–3.3 GB** and **9.9–13.3 GB**, respectively, in addition to the backbone, activations, and buffers.

### Future hardware proposal
A plausible starting allocation is **one node with eight 80-GB GPUs**, a fast interconnect, at least **1 TB host RAM**, and several TB of fast local storage. Prefer BF16 sharded weights, gradient checkpointing, and microbatch one; verify the chosen BAdam implementation supports the sharding strategy before committing. CPU offload is conditional and must be reported. This is a candidate capacity plan, not proof of fit or speed. Eight GPUs' aggregate capacity is not interchangeable with per-device usable memory.

Use the same node class for both arms. Record accelerator-hours, wall time, energy if available, peak GPU/host memory, processed and supervised tokens, effective batch, and throughput including validation/checkpoint overhead. Different algorithmic compute is allowed in the primary exposure-matched comparison, but not hidden. After future smoke timing, estimate total GPU-hours as the sum of all 22 run estimates plus validation, recovery allowance, and seven full benchmark-suite evaluations. No defensible hour estimate is available now.

Save recovery checkpoints conservatively and retain final artifacts for reproducibility. Selected BAdam models require full-weight artifacts or lossless equivalents; LoRA adapters require the pinned base. Include this storage asymmetry in costs.

### Go/no-go checks before scored tuning
- Verify access, licensing, revision hashes, contamination log, split disjointness, and token counts.
- Exercise a toy model and then a short 70B training smoke test: correct masks/loss normalization, finite loss and gradients, only intended tensors updated, frozen weights unchanged, zero initial LoRA contribution, correct block transitions, and documented state behavior after a revisit and resume.
- Confirm at least two full BAdam cycles at the longest interval for the final audited token budget.
- Check 4,096-token memory fit, communication compatibility, checkpoint save/restore equivalence, and enough time/storage for the complete search and replication plan.
- Validate prompt tokenization, context fit, stopping, baseline generation, and scorer unit tests without using benchmark scores for decisions.

Abort or amend the design prospectively if these fail. Smoke-test examples are for engineering checks, not extra benchmark-guided tuning.

## 10. Optional secondary resource-matched study
Only if the primary comparison is feasible and additional resources are allocated: predeclare equal accelerator-hour training caps on the same hardware, with a fixed maximum step count determined from independent timing pilots. Keep evaluation unchanged and report resulting unequal token exposure. Reusing primary selected configurations answers a conditional resource-capped question, not which method is best under independently resource-optimized tuning. A genuinely resource-optimized comparison needs its own equal tuning-resource allowance. Do not substitute this secondary result for the primary exposure-matched conclusion.

## Remaining prerequisites
Exact artifacts; BAdam variant and native optimizer-state semantics; verified module shapes; contamination outcomes; retained data size and resulting block coverage; scorer revision; distributed compatibility; available budget; and the fixed replication count remain to be established. The design makes no prediction of the winner and reports no executed experiment.
````

**Stage**

````text
result
````

**Evidence**

````text
Local inspection found only `/workspace/task.json`. Its question specifies BAdam versus LoRA on Llama 3-70B finetuned using MathInstruct and evaluated on zero-shot math; the question is duplicated. The context says to design an experiment and not claim one was run. Embedded `documents.track.md` reads: 'Design-only task; repositories and compute are not required.' A directory listing and JSON-read check confirmed there was no source code, separate method documentation, dataset, or implementation configuration to inspect. Supplied environment metadata states network disabled, no datasets, no GPU, and dependencies not preinstalled. The researcher subsequently approved the base-model, exposure-matched, GSM8K/MATH, deterministic zero-shot reasoning assumptions and requested this full design. Numerical hyperparameters, thresholds, search budgets, and hardware are prospective proposals. Memory estimates are arithmetic approximations, not observed usage. Controls address shared starting weights/data/prompts, benchmark-independent selection, separate tuning and final seeds, and unequal resource costs. No training, timing pilot, contamination measurement, or benchmark evaluation was executed.
````

**Assumptions**

````text
[
  "Approved design assumptions, not source facts: original Llama 3-70B base; primary matched training exposure; GSM8K and full MATH subject to audit; tool-free deterministic single-sample zero-shot reasoning; unfine-tuned baseline.",
  "Primary claim is conditional on validation-selected configurations from eight full-exposure candidates per method, not unlimited optimization or compute equality.",
  "Proposed settings include one epoch, 4096-token training limit, global batch 64, BAdam layer blocks and cyclic schedule, specified eight-point searches, three independent final seed pairs, and a one-percentage-point practical margin.",
  "Known benchmark-family MathInstruct sources are excluded conservatively; conclusions therefore apply to the documented filtered and length-limited dataset.",
  "Memory accounting assumes BF16 backbone, approximately 70 billion parameters, illustrative 80-layer dimensions, and optimizer-state layouts that must be verified."
]
````

**Uncertainties**

````text
[
  "No exact model, tokenizer, dataset, benchmark, evaluator, or method-code revisions were supplied.",
  "BAdam block/state lifecycle and distributed compatibility must be verified before execution; changing them may change the intended algorithm and memory needs.",
  "Contamination screening cannot establish absence of paraphrased overlap or pretraining contamination.",
  "Audited dataset size may require revising block switch intervals prospectively to ensure coverage.",
  "Three final seed pairs provide limited inferential reliability and exclude tuning-selection variability; additional fixed replication is preferable if feasible.",
  "GPU fit, throughput, wall time, CPU-offload costs, and total affordability remain unmeasured; eight 80-GB GPUs are a candidate plan rather than a guarantee."
]
````

### Event 5 — Simulator

**Message**

````text
The final design adequately addresses the question and the agreed design-only deliverable. It specifies the comparison and conditional claim, prospective method configurations and tuning allowances, shared controls, contamination handling, locked zero-shot evaluation, paired replication and uncertainty analysis, practical decision rules, and a qualified feasibility plan. Keep the outstanding artifact revisions, BAdam implementation semantics, dataset coverage, and hardware checks as explicit prerequisites to future execution. No empirical winner can be inferred, and no experiment is claimed to have been run. The supplied final design is the final candidate.
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
The reported deliverable includes eight tuning candidates per method, three independent final seed pairs, an unfine-tuned baseline, equal final training exposure, benchmark-independent validation selection, GSM8K/MATH macro-average accuracy, paired seed/item uncertainty, and a proposed one-point practical margin. It also provides approximate memory accounting, a candidate eight-GPU allocation, smoke-test gates, and clearly states limitations of filtering, three-seed inference, unknown implementation details, and unmeasured runtime. These satisfy the requested design, rationale, controls, analysis plan, and feasibility without requiring execution.
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
  "event_log": "runs/openai-astra-top2-first-pass/episodes/expbench_neurips2024_96897_7-ee05642667ec/persona_off/attempt-1/output/neurips2024__96897__7/events.jsonl",
  "event_log_sha256": "e9b0b45bcfc61f521d8006ab8f9192789730588536e15cb1d0f91fcf392b8ee2",
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
