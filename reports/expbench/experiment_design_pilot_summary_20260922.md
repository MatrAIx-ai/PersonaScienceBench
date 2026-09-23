# Experiment-design pilot: setup, grading and results

EXP-Bench originally evaluates complete research experiments across 461 tasks from 51 papers. Its workflow is **research question + high-level method + partially masked code repository → experimental design → implementation → execution → conclusion**. Hidden references contain the design variables/procedures, implementation changes and expected conclusion. Evaluation checks integrity and assesses design, implementation, execution and conclusions; the paper allows a 40-minute task budget. [Original paper, Sections 3–4](https://arxiv.org/html/2505.24785v1).

We converted this into an **interactive, design-only pilot** on five tasks: JaxMARL, QuaRot, CycleNet, MogaNet and SineNet. The actor receives a question, brief context, actual environment information and researcher-topic names. It can inspect the masked repository, run small CPU checks and ask the researcher simulator questions before submitting a natural-language plan. Each episode allows 20 actor steps and six researcher questions. The simulator retains conversation history, but receives only the selected topic's approved fact plus prior conversation; the controller returns that fact verbatim or an unknown response. It does not freely invent research advice. The episode ends at plan submission, without evaluating full implementation, training or conclusions.

The implementation uses OpenHands SDK 1.49.3, OpenRouter inference and a CPU Bubblewrap sandbox. Repository snapshots are reconstructed and filtered more strictly than the paper's masking, rather than recovered original experiment revisions. We compare o3-mini and Sonnet 5 actors/simulators, keeping the reported judge fixed to Sonnet 5. Simulator output allowances differ: Sonnet 5 has 1,024 tokens; o3-mini has 4,096 including medium reasoning. This is an adaptation, not a reproduction of the original paper's scores.

**Grading is reference-based.** Sonnet 5 receives the submitted plan and the original hidden design reference, including constant, independent and dependent variables. The released prompt asks it to judge matching items and return a 0–100 percentage with an explanation. This is an LLM-assessed match, not a deterministic item-count calculation or a general scientific-quality score. We average three grades per plan, then average the five task scores. The added design-quality rubric was removed. The original integrity monitor is retained separately; raw coverage below is reported before gating. Claude requires a neutral nonempty user message, so we add “Apply the evaluation instructions above” while preserving the original system prompts.

| Simulator | Actor | Judge | Mean reference coverage |
| --- | --- | --- | ---: |
| Sonnet 5 | o3-mini | Sonnet 5 | 47.5/100 |
| o3-mini | o3-mini | Sonnet 5 | 54.0/100 |
| Sonnet 5 | Sonnet 5 | Sonnet 5 | 79.5/100 |
| o3-mini | Sonnet 5 | Sonnet 5 | 92.7/100 |

These represent one actor episode per task/condition, not three actor reruns. All ten new Sonnet-actor episodes passed integrity; two earlier o3-mini-actor monitor evaluations had JSON-format failures, preserved separately from coverage. Sonnet actors obtained higher coverage in this sample. The simulator ranking remains uncertain: most of the latest gap comes from JaxMARL, where the actor asked zero questions with Sonnet as simulator versus six with o3-mini. Different actor trajectories and only five tasks prevent attributing the difference to simulator capability. High coverage does not demonstrate a successfully executed experiment.

[Sonnet-actor results and traces](sonnet5_actor_comparison_20260922.md) · [Earlier plans regraded by Sonnet](sonnet5_judge_comparison_20260922.md) · [Implementation details](../../docs/expbench/realistic-benchmark.md).

**Example interaction trace — QuaRot, Sonnet 5 actor and Sonnet 5 simulator.** This is an observed run, not a constructed example. Questions and repository actions below are shortened for readability; simulator replies are verbatim published responses, selected through the fact controller.

The actor's task was: “How should we evaluate the effect of Hadamard versus random orthogonal weight transformations on LLaMA-2 perplexity under 4-bit QuaRot quantization?” It first inspected the repository, including rotation, Hadamard, argument and evaluation code, and ran small file/code searches in the sandbox.

| Exchange | Actor question, condensed | Simulator reply, verbatim |
| --- | --- | --- |
| 1 — model inventory | Which LLaMA-2 checkpoints are available locally, and can they run on CPU? | The intended checkpoints are LLaMA-2 7B, 13B and 70B; availability is not established by this fact. |
| 2 — evaluation data | Which perplexity datasets are locally available, and in what format? | The requested evaluation dataset is WikiText-2. |
| 3 — context length | What sequence length and evaluation batch size should be used? | The existing evaluation configuration uses sequence length 2048 tokens. |
| 4 — weight precision | Should 4-bit weights use GPTQ or round-to-nearest, and symmetric or asymmetric quantization? | The requested weight quantization is 4-bit QuaRot-GPTQ. |
| 5 — other precision | Are activations and KV caches also 4-bit, or is this weight-only quantization? | The source setup keeps inputs and KV caches in FP16. |

Between exchanges 2 and 3, the actor searched for model weights and data and checked Python dependencies. After exchange 5, it inspected quantization code again and submitted its plan. The simulator's answers did not establish local availability or settle every subquestion; those gaps remained for the actor to investigate or state as assumptions.

The submitted plan proposed comparing Hadamard and random orthogonal rotations with weight-only 4-bit GPTQ, measuring WikiText-2 perplexity at sequence length 2048, keeping inputs/KV caches in FP16, and repeating both rotation conditions across seeds while fixing calibration settings. It prioritized LLaMA-2 7B, with 13B/70B conditional on resources, and explicitly stated that real perplexity experiments could not be performed in the current environment. This is a summary of the actor's proposal, not independent confirmation of its technical claims.

The episode used **11 actor API calls and five researcher questions**. Sonnet 5 judged the submitted plan at **93.3/100 mean reference coverage** across three grades; integrity passed. No full quantization experiment was executed.

Raw artifacts: [researcher conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/researcher_history.json), [actor actions and observations](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/actor_events.jsonl), [full submitted plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/initial_design.json).

**Full submitted design — verbatim actor output.** This is the final deliverable of the design-only episode, stored as its initial-design checkpoint; it is a proposed experiment, not an execution result.

````text

OBJECTIVE
Determine whether QuaRot's structured (randomized) Hadamard rotation and a generic random orthogonal rotation give statistically different WikiText-2 perplexity when used as the incoherence-processing step ahead of 4-bit weight-only GPTQ quantization of LLaMA-2 models, using the repo's existing `--rotate_mode {hadamard,random}` switch (fake_quant/rotation_utils.py, fake_quant/hadamard_utils.py).

WHAT THE REPO ALREADY GIVES US (confirmed by inspection)
- `rotation_utils.get_orthogonal_matrix(size, mode)` returns either `random_hadamard_matrix` (a structured Walsh-Hadamard transform composed with a random ±1 diagonal, i.e. "randomized Hadamard transform") or `random_orthogonal_matrix` (QR of a Gaussian matrix). Both are therefore stochastic and depend on a seed (`--rotation_seed`), so BOTH conditions need multi-seed replication, not just the random-orthogonal one.
- `rotate_model()` applies the same global rotation Q to embeddings, lm_head, attention Q/K/V-in, attention-out, MLP-in, and MLP-out for every transformer layer, for either mode identically — this is the factor being varied.
- Independently of `rotate_mode`, `rotate_mlp_output` and `rotate_ov_proj` always additionally apply an exact CUDA Walsh–Hadamard fold (`apply_exact_had_to_linear`, via `fast_hadamard_transform`) to the down_proj and v_proj/o_proj weights. This local folding is unconditional and identical in both arms — the experiment isolates the effect of the *global* rotation matrix choice, not of Hadamard structure everywhere.
- GPTQ weight quantization (`gptq_utils.py`) and RTN weight quantization are independent of `rotate_mode`; only the pre-rotated weights differ.
- Perplexity evaluation (`eval_utils.evaluator`) is dataset/seqlen driven and independent of rotation.
- There is currently no top-level driver script (`main.py`) in `fake_quant/`; only the library modules (`utils.py` argparse, `rotation_utils.py`, `gptq_utils.py`, `quant_utils.py`, `eval_utils.py`, `model_utils.py`, `data_utils.py`) exist. A driver script wiring these together (load model → fuse_layer_norms → rotate_model → GPTQ-quantize weights to 4 bits → evaluate perplexity) needs to be written for this study; I will not reconstruct any previously-removed original solution file, only assemble a minimal script from the documented public functions, scoped narrowly to this ablation (rotate_mode × seed) with everything else fixed.

FACTORS AND FIXED SETTINGS
- Independent variable: `rotate_mode` ∈ {hadamard, random}.
- Nuisance/random variable to replicate over: `rotation_seed` (e.g. 5 values, same seed list used for both modes) — needed because both matrices are stochastic.
- Fixed calibration seed (`--seed`, default 0) and fixed GPTQ calibration set (wikitext2 train, `nsamples=128`, default `percdamp=0.01`, `act_order=False`, per-channel groupsize `-1`) so calibration-sampling noise does not confound the rotation comparison. (act_order on/off and groupsize could be a secondary robustness check, run only for the primary model size.)
- Quantization config: weight-only 4-bit QuaRot-GPTQ as specified — `w_bits=4`, GPTQ (`w_rtn=False`), symmetric weights (repo default, `w_asym` off) unless researcher prefers asymmetric (flag both ways only as a secondary check), `a_bits=16`, `k_bits=16`, `v_bits=16` (activations and KV cache stay FP16, confirmed by researcher). `--rotate` enabled for both arms; `fp32_had` fixed to one value (e.g. True) identically in both arms since it is a numerical-precision detail, not the factor under test.
- Evaluation: WikiText-2 test perplexity, seqlen = 2048 (repo's `model.seqlen`), batch size chosen to fit available GPU memory (repo default 32, may need reducing for 70B).
- Primary model: LLaMA-2-7B (cheapest, most repeats feasible). Secondary/extension if compute allows: LLaMA-2-13B and LLaMA-2-70B (use `--distribute` for 70B), run with fewer seeds (e.g. 3) due to cost, to see whether any Hadamard-vs-random gap changes with model scale.

PROCEDURE
1. For each model size in {7B, (13B, 70B if resources allow)}:
   a. For each rotate_mode in {hadamard, random}:
      For each seed in the fixed seed list:
        - Load the FP16 checkpoint fresh each run (rotation mutates weights in place).
        - `fuse_layer_norms(model)`.
        - `rotate_model(model, args)` with the given `rotate_mode`/`rotation_seed`.
        - Apply GPTQ 4-bit weight quantization with the fixed calibration settings above.
        - Run `evaluator(...)` on WikiText-2 test, seqlen 2048, record perplexity.
2. Collect a 2 (mode) × N (seeds) [× model sizes] table of perplexities.
3. Optionally add a no-rotation 4-bit GPTQ baseline (`--rotate` off) as a sanity anchor to confirm both rotation modes improve over no rotation, validating that the harness is wired correctly before trusting the Hadamard-vs-random comparison.
4. Optional secondary diagnostics (not required for the headline comparison but useful to explain any gap): per-layer weight quantization MSE / max-abs error before vs after rotation for each mode (can be captured via `capture_layer_io` or by directly comparing quantized vs original rotated weights), and a measure of weight "incoherence" (e.g. max_ij|W_ij| / ||W||_F row-normalized) pre/post rotation for a sample of layers, comparing the two modes' empirical spread across seeds.

ANALYSIS
- Report mean ± std WikiText-2 perplexity per mode (and per model size), with the seed as the unit of replication.
- Since seeds are matched (same seed index used to draw both the Hadamard sign-diagonal and the random-orthogonal matrix), treat runs as paired by seed and use a paired difference (mean Δppl = ppl_random − ppl_hadamard) with a paired t-test or Wilcoxon signed-rank test (small N, so also report the raw paired differences and a bootstrap CI over seeds rather than relying solely on a p-value).
- Flag whether the observed difference is within run-to-run noise (seed variance within one mode) versus a systematic mode effect; if the between-mode gap is smaller than the within-mode seed spread, conclude no meaningful difference.
- If multiple model sizes are run, check whether any Hadamard-vs-random gap trends with scale.
- If secondary act_order/w_asym/groupsize sweeps are run, treat them as robustness checks on the primary 7B result, not full factorial replication.

FEASIBILITY / ENVIRONMENT CAVEATS (established by direct inspection, not assumption)
- This sandbox has no GPU (`gpu_enabled: false`), no network access, `torch`/`transformers` are not installed, and there are no cached LLaMA-2 weights or WikiText-2 data anywhere on disk. The repo's Hadamard machinery (`fast_hadamard_transform`, and `apply_exact_had_to_linear`'s hardcoded `.cuda()` calls) requires a GPU for both rotate_mode arms, so the experiment as designed is not executable here.
- Consequently, I cannot run or claim any perplexity numbers in this episode. Before requesting GPU/network resources, I recommend a cheap smoke test in this sandbox (once torch is installable) using a tiny synthetic Llama-config model with random weights and 1–2 layers to verify that `rotate_model` under both modes, GPTQ quantization, and `evaluator` all execute end-to-end without shape/device errors — this only validates code wiring, it produces no evidence about the real research question.
- Real runs need: a GPU host (single 40GB+ GPU is plausible for 7B/13B; 70B needs multi-GPU via `--distribute` or very slow CPU offload), internet or pre-downloaded LLaMA-2 HF weights (license-gated), a cached WikiText-2 dataset, and the project's Python dependencies (`requirements.txt`, plus `fast_hadamard_transform`) installed.
- Because a driver script combining these modules does not currently exist in the repo, someone must write one; I have scoped exactly which existing functions it must call and in what order (Section "Procedure") so this is a well-defined, bounded piece of engineering rather than a research uncertainty.

OPEN UNCERTAINTIES TO FLAG TO THE RESEARCHER
- Exact number of seeds affordable given GPU budget (5 recommended per mode per model size for 7B; fewer for larger models).
- Whether asymmetric weight quantization (`w_asym`) or non-default `act_order`/groupsize should also be swept, or fixed at repo defaults as assumed here.
- Whether `fp32_had` should be True or False; I fixed it identically across arms but did not get an explicit preference.
- Whether WikiText-2 calibration set should also be swept/varied jointly with rotation seed, or held fixed as planned (held fixed here to avoid confounding).

````
