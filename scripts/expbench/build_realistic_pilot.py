#!/usr/bin/env python3
"""Versioned source-reviewed fact cards; preserve the earlier pilot unchanged."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACTS = {
    "neurips2024/97649/0": [
        ("algorithm_variants", "The requested variants are MAPPO and QMIX."),
        ("map_scope", "The requested scope is nine SMAX maps, excluding maps with more than ten units; the released list is incomplete."),
        ("timing_definition", "Training time means minutes to a defined convergence criterion; the numerical convergence threshold is unspecified."),
        ("score_definition", "Normalize each algorithm score by the best score within that SMAX scenario."),
        ("score_summaries", "The source reports mean episode reward and interquartile mean summaries."),
    ],
    "neurips2024/94328/5": [
        ("model_inventory", "The intended checkpoints are LLaMA-2 7B, 13B and 70B; availability is not established by this fact."),
        ("evaluation_data", "The requested evaluation dataset is WikiText-2."),
        ("context_length", "The existing evaluation configuration uses sequence length 2048 tokens."),
        ("weight_precision", "The requested weight quantization is 4-bit QuaRot-GPTQ."),
        ("other_precision", "The source setup keeps inputs and KV caches in FP16."),
    ],
    "neurips2024/94391/7": [
        ("evaluation_data", "The requested datasets are Electricity and Traffic."),
        ("input_window", "The existing setup uses look-back length 96."),
        ("forecast_horizons", "The requested forecast horizons are 96, 192, 336 and 720."),
        ("normalization", "The existing CycleNet setup uses instance normalization inspired by RevIN, without learnable affine parameters."),
        ("optimizer", "The existing training implementation uses PyTorch and Adam."),
        ("measurements", "The study requests MSE and MAE, with percentage changes between matched conditions."),
    ],
    "iclr2024/18447/7": [
        ("model_inventory", "The existing backbone is MogaNet-S."),
        ("evaluation_data", "The requested classification dataset is ImageNet-1K; access is not established by this fact."),
        ("training_duration", "The existing training recipe uses 300 epochs."),
        ("optimizer", "The existing optimizer is AdamW with initial learning rate 0.001 and a cosine schedule."),
        ("measurements", "The study requests top-1 accuracy and distributions of interaction strength J(m); the released annotation does not define the J(m) estimator."),
    ],
    "iclr2024/18865/4": [
        ("model_inventory", "The intended architecture is SineNet-8."),
        ("evaluation_data", "The intended data are shallow-water-equation dynamics with periodic boundaries."),
        ("measurements", "The study requests one-step and multi-step rollout prediction error percentages."),
        ("metric_details", "The released annotation does not specify the precise error formula or rollout horizon."),
    ],
}


def main():
    previous = ROOT / "data/design_pilot/tasks.jsonl"
    output = ROOT / "data/realistic_pilot/tasks.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for line in previous.read_text().splitlines():
        task = json.loads(line)
        tid = task["task_id"]
        task["public"]["context"] = "Help the researcher decide how to investigate this question. Existing setup details can be clarified by topic. Repository and runtime availability will be supplied separately."
        task["public"]["documents"] = {}
        task["researcher"]["facts"] = [{"id": f"{tid}:{topic}", "topic": topic,
            "text": text, "source_field": "released method / agent_instructions"}
            for topic, text in FACTS[tid]]
        task["provenance"]["adaptation"] = "realistic-researcher-v3"
        task["review_notes"].append("V3: topic-scoped facts; no full method or ablation recipe; actual runtime resources supplied separately. JaxMARL convergence measurement retained.")
        cards.append(task)
    output.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in cards))
    print(f"Wrote {len(cards)} cards to {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
