#!/usr/bin/env python3
"""Build five curated cards from the pinned local EXP-Bench annotations.

Facts below were reviewed against the released task methods, not independently
verified against each source paper. We intentionally do not copy method prose,
outcomes, agent instructions, or hypothetical constraint modifications.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CARDS = [
    {
        "task_id": "neurips2024/97649/0",
        "domain": "multiagent reinforcement learning",
        "question": "How should we compare PPO and Q-learning in JaxMARL's SMAX environments for training time and normalized performance?",
        "context": "SMAX is a cooperative multiagent environment in JaxMARL. Design a fair comparison of the two algorithm families; the researcher can clarify the intended variants and task scope.",
        "facts": [
            ("algorithms", "The intended PPO variant is MAPPO and the intended Q-learning variant is QMIX."),
            ("scope", "The intended scope is nine SMAX maps, excluding maps with more than ten units. The released method does not give a complete unambiguous map list."),
            ("resources", "Comparisons should use the same computational resources. The particular GPU model, GPU count, and wall-time limit are not specified."),
            ("reporting", "The requested outcomes are training time in minutes and scores normalized relative to the best score in each scenario. The project uses mean episode reward and interquartile mean summaries."),
        ],
        "unspecified": ["Exact convergence threshold", "Complete map list", "Seed count", "GPU model and time or money budget"],
        "notes": ["Removed the expected sixfold speedup and predicted winner from actor instructions.", "The map count is retained as a scope fact; the incomplete map list must remain acknowledged."],
    },
    {
        "task_id": "neurips2024/94328/5",
        "domain": "LLM quantization",
        "question": "How should we evaluate the effect of Hadamard versus random orthogonal weight transformations on LLaMA-2 perplexity under 4-bit QuaRot quantization?",
        "context": "QuaRot uses orthogonal transformations in model quantization. We want a controlled comparison of transformation types. Ask the researcher about the existing evaluation setup.",
        "facts": [
            ("models", "The target checkpoints are LLaMA-2 7B, 13B, and 70B."),
            ("data", "The existing evaluation setup uses WikiText-2 with sequence length 2048 tokens and reports perplexity."),
            ("precision", "The intended setup is 4-bit QuaRot-GPTQ weight quantization; inputs and KV caches remain FP16."),
            ("implementation", "The released method constructs a random orthogonal matrix by QR decomposition of a random Gaussian matrix; generation seeds and detailed fusion adjustments are not specified."),
        ],
        "unspecified": ["Hardware allocation", "Wall-time and money budget", "Calibration sample details", "Random seed count"],
        "notes": ["Neutralized the question's suggestion that Hadamard should win.", "Excluded hypothetical performance margins from experiment_constraints."],
    },
    {
        "task_id": "neurips2024/94391/7",
        "domain": "time series forecasting",
        "question": "How should we test the effect of adding residual cycle forecasting (RCF) to Linear and MLP forecasting backbones?",
        "context": "CycleNet combines a forecasting backbone with a residual cycle forecasting component. The goal is to isolate the component's contribution to forecasting accuracy.",
        "facts": [
            ("data", "The target datasets are Electricity and Traffic, using consistent chronological preprocessing and normalization across conditions."),
            ("windows", "The existing setup uses a look-back length of 96 and forecast horizons 96, 192, 336, and 720."),
            ("training", "The source setup uses PyTorch and Adam on one RTX 4090 with 24 GB memory. It uses a 7:1:2 train/validation/test split for these datasets, batch size 64, at most 30 epochs and validation early stopping with patience 5."),
            ("normalization", "The source setup uses RevIN without learnable affine parameters; the MLP hidden width is 512. These settings are part of the existing setup, not measured outcomes."),
            ("reporting", "The project's forecasting reports use MSE and MAE, including relative percentage changes between matched conditions."),
        ],
        "unspecified": ["Overall compute-time and money budget", "Number of independent seeds", "Exact numerical cycle lengths"],
        "notes": ["Unwrapped the source reference without changing its variable groups.", "Omitted unrelated Solar dataset outcomes and hypothetical required improvements.", "Source learning-rate search is omitted from fixed facts; the actor should specify fair tuning across conditions."],
    },
    {
        "task_id": "iclr2024/18447/7",
        "domain": "computer vision",
        "question": "How should we assess the contributions of the Moga and Channel Attention modules to MogaNet's classification performance and feature interactions?",
        "context": "MogaNet is an image classification architecture. The study concerns the contribution of two modules, Moga and Channel Attention, rather than comparisons across unrelated architectures.",
        "facts": [
            ("setup", "The existing backbone is MogaNet-S and the dataset is ImageNet-1K."),
            ("training", "The source training recipe uses 300 epochs, AdamW, base learning rate 0.001, and a cosine learning-rate scheduler."),
            ("reporting", "The project examines both top-1 classification accuracy and distributions of interaction strength J(m). The released annotation does not define the exact J(m) estimator."),
        ],
        "unspecified": ["Module removal implementation", "Exact interaction-strength estimator", "Hardware and time budget", "Seed count and augmentation details"],
        "notes": ["Withheld the step-by-step ablation recipe and any comparison to measured table results.", "J(m) is retained as a measurement requested by the source; its missing definition is explicitly acknowledged."],
    },
    {
        "task_id": "iclr2024/18865/4",
        "domain": "scientific machine learning / fluid dynamics",
        "question": "How should we compare circular and zero padding in SineNet when predicting dynamics with periodic boundary conditions?",
        "context": "SineNet predicts temporal dynamics in physical fields. The question concerns how boundary handling affects prediction, including repeated rollout over time.",
        "facts": [
            ("setup", "The intended model is SineNet-8 and the target dataset is the shallow-water-equations (SWE) dataset with periodic boundary conditions."),
            ("reporting", "The study requests both one-step prediction error percentages and multi-step rollout error percentages; plots of error over time are optional."),
            ("availability", "The released annotation does not specify the exact error formula, rollout horizon, dataset composition, or preprocessing. Those details must be proposed or identified as assumptions."),
        ],
        "unspecified": ["Numerical training hyperparameters", "Exact metric formula and rollout horizon", "Hardware and time budget", "Seed count"],
        "notes": ["Removed the claim that circular padding should improve errors and the reference to measured Table 3 values.", "No numeric results were included in the reference variable inventory."],
    },
]


def main():
    source = ROOT / "data/exp_bench/tasks.jsonl"
    tasks = {t["task_id"]: t for t in map(json.loads, source.read_text().splitlines())}
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    out = ROOT / "data/design_pilot/tasks.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for card in CARDS:
        original = tasks[card["task_id"]]
        assert original["reference_design_schema_valid"]
        cards.append({
            "task_id": card["task_id"], "domain": card["domain"],
            "public": {
                "question": card["question"], "context": card["context"],
                "documents": {"environment.md": (
                    "This is a design-only episode. You can read these supplied context "
                    "documents and ask the researcher questions. Original repositories "
                    "and datasets are not mounted. Compute described by the researcher "
                    "is proposed experimental context, not an allocation you can execute. "
                    "Do not report experiments as performed. State missing details and "
                    "justify any choices you propose."
                )},
            },
            "researcher": {
                "facts": [{"id": f"fact_{i}", "topic": topic, "text": text,
                           "source_field": "method"}
                          for i, (topic, text) in enumerate(card["facts"], 1)],
                "unspecified": card["unspecified"],
            },
            "reference_design": original["reference_design"],
            "provenance": {"source_file": "data/exp_bench/tasks.jsonl",
                           "source_sha256": digest,
                           "source_task_id": card["task_id"],
                           "upstream": original["provenance"],
                           "review": "Reviewed against released annotations; not independently checked against each source paper"},
            "review_notes": card["notes"],
        })
    out.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards))
    print(f"Wrote {len(cards)} curated cards to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
