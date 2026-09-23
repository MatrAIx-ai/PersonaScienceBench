# Why our design-only scores are higher

This audit compares arXiv:2505.24785 **v1**, the pinned Curie release (`db1b1f56159b591515f77e03c55bf473d5c1c201`), our actor requests, and ten saved o3-mini designs and grades. It does not establish an exact numerical decomposition of the gap. No new paid model calls or experiments were run.

**The strongest explanation is that the two scores measure different operating conditions.** Our design-only task supplies considerable design information and reliably saves a structured plan. The paper evaluates design as part of an attempted full experiment, with an integrity gate that can set design to zero. Reusing the judge text does not remove this distinction.

## 1. The monitor matters through the workflow's pass rate

[Figure 14, page 45 of the original paper](https://arxiv.org/pdf/2505.24785v1#page=45) plots the OpenHands + o3-mini monitor metric M at approximately **21%**. Our ten design-only traces all passed. The released [judge.py](../../external/expbench-history/vendor/curie-db1b1f5/benchmark/exp_bench/evaluation/judge.py) sets design, implementation, and conclusion scores to zero when any monitor flag is true or a monitor response remains unparseable, and skips the design judge for those runs.

Consequently, for a common denominator and zero scores on monitor failure:

`mean gated design = monitor pass fraction × mean design among monitor-passing runs`

For illustration, a 20% pass fraction combined with a 92/100 mean among passes gives an overall score of 18.4/100. **Those are illustrative factors, not recovered paper per-run statistics.** The paper reports o3-mini D = 18.4 in Table 1. Its low overall D therefore need not imply that valid submitted designs usually score only 18.4.

There is a publication consistency caveat: Figure 14's approximate Sonnet M bar is below its Table 1 D value (roughly 14 versus 16), as is Haiku's (roughly 16 versus 20.6). Under the simple zero-gate identity and an identical sample this cannot happen. The exact aggregation data/code or clarification from the authors is needed before calculating a definitive conditional design mean. The figure is strong motivation to investigate gating, not sufficient to establish exact attrition counts.

The earlier observation that adding the monitor did not change our scores is correct. **It does not rule out monitor attrition as an explanation for the paper gap.** Our actor has no shell, web, or repository tools, is explicitly told not to execute or claim results, and submits only a plan. Those conditions avoid many opportunities for the violations the monitor examines. A full-workflow trace is a different monitor input distribution.

Saved visual evidence: [paper page 45](assets/expbench-v1-page45.png).

## 2. Our actor is explicitly optimized to produce a graded design

This difference goes beyond using a newer OpenHands version:

| Component | Released full workflow | Our no-simulator control |
| --- | --- | --- |
| Task contract | Design, implement, execute, analyze, conclude | Stop after design; do not execute |
| Tools | Repository and execution environment | Only `read_context` and `submit_design` |
| Design output | Free-text string or list in a final JSON file | Required nonempty constant/independent/dependent groups, procedure, analysis, assumptions |
| Submission | Agent writes output at the specified file path | Host saves a validated tool argument immediately |
| Observed control actor calls | Original matching traces unavailable | Exactly one call for each of five tasks |

The original generation prompt does suggest listing variables, so that guidance itself is not new. Our mandatory schema, extensive design-only instructions, and immediate saving impose substantially stronger scaffolding. The original judge replay receives **all** our design fields, including procedure and assumptions, as its `design_output` string.

Evidence: [our actor prompt](../../src/expbench/prompts.py), [actor adapter](../../src/expbench/actor.py), [output schema](../../src/expbench/schema.py), [released generation prompt](../../external/expbench-history/vendor/curie-db1b1f5/benchmark/exp_bench/evaluation/prompts/eval_gen_prompt.txt).

## 3. Final-file failure can lose credit for a good initial plan

In released `evaluation/eval.py::_query_agent`, after the actor runs, the harness checks a particular JSON file and requires exactly the keys `design` and `conclusion`. Its outer output-validation attempt count is one; this is separate from the 30 OpenHands iterations. Missing files or wrong keys produce a `no_answer` artifact. There is no recovery of a good initial plan from the conversation in this path.

In `judge.py::generate_task_prompt`, a `no_answer` value becomes both the design and conclusion inputs. This gives the design grader no substantive design to credit. If monitor rejection occurs first, the score is explicitly zero. The precise treatment of every timeout, infrastructure failure, invalid task, or missing grade in the paper's aggregate cannot be established without its aggregation script/data; do not silently assert all such cases were included as zeros.

Our validated submission tool removes this final-file failure path. The ten audited runs all completed; we did not discard failed tasks within these two five-task o3-mini runs to calculate their means. Earlier failed Sonnet attempts are separately preserved and do not belong in the o3-mini denominator.

## 4. Original inputs already supply much of the reference design

We verified the five raw task records against the vendored release and checked the exact original question/method/instruction values in the actual no-simulator API requests. No private reference-design field was included in those user payloads. Nevertheless, much of the information being graded is already public in the original method:

| Task | Design information already supplied | Reference dictionary keys |
| --- | --- | ---: |
| JaxMARL | MAPPO/QMIX, nine-map scope, fixed compute, convergence timing and normalized-score definition | 5 |
| QuaRot | Three model sizes, both transformations, 4-bit GPTQ, FP16 components, WikiText-2, 2048 tokens and perplexity | 7 |
| CycleNet | Backbones, RCF conditions, datasets, horizons, normalization and training settings, MSE/MAE | 8 |
| MogaNet | ImageNet-1K, MogaNet-S, 300 epochs, optimizer/LR/schedule, specified module removals, top-1 and J(m) | 4 |
| SineNet | Padding alternatives, fixed training configuration, one-step and rollout errors | 3 |

These counts describe reference structure, not atomic scoring weights. The pilot average is 5.4 dictionary keys versus approximately 6.69 across 460 structurally valid references. Five manually chosen tasks cannot establish overall benchmark difficulty. Four pilot tasks are type 1, one is type 3; the full dataset includes 123 type 2 tasks, none of which is represented here.

In particular, MogaNet's method is already a compact ablation plan. A design-only actor can reorganize it into the requested schema without solving the full experimental task. This is inherited from the released input, so it is not solely simulator leakage. Some inputs also contain expected-result hints, such as JaxMARL's expected sixfold speedup, although those are not independently scored design criteria.

## 5. The original judge is not a deterministic item scorer

The released prompt does not define atomic criteria, a precise denominator, or a consistent penalty for placing the correct value in the wrong variable group. Our saved judgments demonstrate inconsistent treatment:

- Interactive QuaRot: **100**, although the explanation acknowledges that model sizes were put under constants rather than independent variables. Its submitted independent list also includes a random seed described as fixed.
- No-simulator QuaRot: **85**, with the explanation penalizing model-size placement and extra items. These are different designs, so this is evidence of inconsistent reasoning about a shared error, not a controlled estimate of judge variance.
- No-simulator CycleNet: **75**, with an explanation claiming fixed training configurations are missing, despite constants and assumptions that describe fixed settings. The design also allows some tuning and normalization exceptions, so disagreement about this criterion is plausible; the categorical omission explanation is insufficiently precise.

The adapted judge was more permissive on these saved outputs:

| Actor input mode | Adapted judge | Released prompt replay | After monitor |
| --- | ---: | ---: | ---: |
| No simulator | 97 | 92 | 92 |
| Interactive simulator | 91 | 78.6 | 78.6 |

These are single judgments. The observed differences are not a clean estimate of the causal prompt effect without repeated grading.

Evidence: saved [original-prompt grades](../../runs/expbench/original-judge-diagnostic-20260922/summary.json) and [monitor results](../../runs/expbench/original-monitor-20260922/summary.json).

## 6. We copied the judge text, not its complete request configuration

The released `query_plain` uses `llm_query_plain("", task_prompt, ...)`. Its Azure client sends the judge prompt as a **system message**, followed by an empty user message, and requests `response_format={"type":"json_object"}`. It retries malformed outputs up to three times.

Our saved design and monitor replays instead send the entire prompt as a **user message**. Design replay has no response-format parameter and no parse retry, and sets a 4096-token output allowance and medium reasoning. It supplies our serialized design and an empty conclusion. The model provider and deployment also differ. The monitor replay retries parsing but shares the role/format differences.

This is a concrete fidelity gap missed by checking the prompt hash alone. Its score effect is unknown; all ten responses parsed, so parse failure did not cause the observed high scores. Historical outputs are preserved. We should describe these as **released-prompt replays**, not exact reproductions of the original judge invocation.

Evidence: [released model client](../../external/expbench-history/vendor/curie-db1b1f5/benchmark/exp_bench/model.py), [our design replay](../../src/expbench/original_control.py), [our monitor replay](../../src/expbench/integrity.py).

## What would isolate the causes

1. Replay fixed saved designs with the released message roles and JSON mode, recording deployment differences and repeating grades. This requires no GPUs.
2. Grade an input-only baseline that copies the original method/instructions directly into the design field; compare it with our generated designs. This measures how much credit is available by restating supplied information. Include empty, generic, missing-variable and miscategorized-variable controls.
3. For full workflows, record initial design, final submitted design, valid-file rate, monitor pass rate and gated design mean separately. Apply the same judge to both saved designs. This distinguishes design quality from workflow survival and submission failures.
4. Compare identical task IDs and original per-run artifacts where available. Treat paper-wide averages as context until the evaluation sample and aggregation rules are matched.

No single identified factor has been experimentally shown to account for the entire gap. The current evidence makes full-workflow attrition, explicit design scaffolding and already-detailed inputs stronger explanations than a simulator-only bug.

## Offline verification

`python scripts/audit_score_gap.py` verifies five raw-source matches, five actual static actor inputs, and ten completed non-mock run records, and recomputes the score means. It writes [machine-readable evidence](score_gap_audit.json) with artifact hashes. This audit does not change prompts, task cards, historical scores, or runtime behavior.
