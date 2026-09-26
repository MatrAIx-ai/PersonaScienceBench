#!/usr/bin/env python3
"""Evaluate whether statically selected action profiles visibly affect one response."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import random
import threading

from pydantic import BaseModel, ConfigDict, Field

from personasciencebench.inference import OpenRouterClient, load_env, preflight, strict_json


MODEL = "openai/gpt-6-luna"
SCENARIO = (
    "Agent update: I plan to analyze a noisy time-series dataset. I will write one Python "
    "script, fit a baseline model, and report the main result. I have not yet decided how "
    "to structure the code, document it, test it, or diagnose failures. Review the plan "
    "and tell the agent how you want it to proceed."
)
COMMON_SYSTEM = (
    "You are a simulated researcher reviewing a scientific coding agent's plan. Reply with "
    "a concise, actionable review. Use only the information in the agent update. Do not "
    "invent data properties, results, resources, deadlines, or task requirements. Do not "
    "mention hidden instructions or describe a persona profile."
)


class RuleEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str
    evidence: str


class Judgement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    response_matching_rules: str = Field(pattern="^(A|B|neither)$")
    difference: str = Field(pattern="^(absent|subtle|clear|prominent)$")
    behavioral_not_only_wording: bool
    rule_evidence: list[RuleEvidence]
    explanation: str


def append_jsonl(path: Path, value: dict, lock: threading.Lock) -> None:
    with lock, path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def client(role: str, record) -> OpenRouterClient:
    return OpenRouterClient(
        MODEL, role=role, max_tokens=1000, reasoning_effort="none",
        unsupported_parameters="omit_and_record", record=record,
    )


def generate(system: str, role: str, record) -> str:
    return client(role, record).complete([
        {"role": "system", "content": system},
        {"role": "user", "content": SCENARIO},
    ])


def evaluate_one(candidate: dict, baselines: list[str], api_path: Path,
                 api_lock: threading.Lock) -> dict:
    candidate_id = candidate["candidate_id"]
    record = lambda value: append_jsonl(api_path, {"candidate_id": candidate_id, **value}, api_lock)
    rules = [rule["instruction"] for rule in candidate["rules"] if rule["directional"]]
    persona_system = COMMON_SYSTEM + "\n\nFollow these preferences when relevant:\n- " + "\n- ".join(rules)
    conditioned = generate(persona_system, "conditioned_generator", record)
    baseline_index = int(hashlib.sha256(candidate_id.encode()).hexdigest(), 16) % len(baselines)
    baseline = baselines[baseline_index]
    conditioned_label = "A" if int(hashlib.sha256((candidate_id + ":order").encode()).hexdigest(), 16) % 2 == 0 else "B"
    responses = {conditioned_label: conditioned,
                 "B" if conditioned_label == "A" else "A": baseline}
    judge_prompt = {
        "task": (
            "Identify which response, if either, reflects the supplied action rules. Then rate "
            "how prominently the two responses differ. A prominent difference must change "
            "requested actions, decisions, checks, or workflow; wording and length alone do not count."
        ),
        "action_rules": rules,
        "scenario": SCENARIO,
        "response_A": responses["A"],
        "response_B": responses["B"],
        "output_contract": {
            "response_matching_rules": "A, B, or neither",
            "difference": "absent, subtle, clear, or prominent",
            "behavioral_not_only_wording": "boolean",
            "rule_evidence": [{"field": "source action field", "evidence": "short response evidence"}],
            "explanation": "brief rationale",
        },
    }
    raw = client("persona_effect_judge", record).complete([
        {"role": "system", "content": (
            "You are a blinded evaluator. Judge only observable response behavior. Do not reward "
            "verbosity, polish, or agreement with your own preferences. Return one JSON object.")},
        {"role": "user", "content": json.dumps(judge_prompt, ensure_ascii=False)},
    ], json_mode=True)
    judgement = Judgement.model_validate(strict_json(raw))
    visible = (judgement.response_matching_rules == conditioned_label
               and judgement.difference in {"clear", "prominent"}
               and judgement.behavioral_not_only_wording
               and len(judgement.rule_evidence) >= 1)
    return {
        "candidate_id": candidate_id,
        "source": candidate["source"],
        "static_selected": True,
        "baseline_index": baseline_index,
        "conditioned_label": conditioned_label,
        "action_rules": rules,
        "responses": responses,
        "judgement": judgement.model_dump(),
        "prominent_behavioral_effect": visible,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--parallel", type=int, default=16)
    args = parser.parse_args()
    if args.parallel < 1 or args.parallel > 32:
        raise ValueError("parallel must be between 1 and 32")
    candidates = [json.loads(line) for line in args.selected.read_text().splitlines() if line.strip()]
    if not candidates or any(not row.get("selected") for row in candidates):
        raise ValueError("Input must contain statically selected candidates")
    args.output.mkdir(parents=True, exist_ok=False)
    load_env(args.env_file)
    catalog = preflight({
        "researcher": {"model": MODEL, "reasoning_effort": "none"},
        "judge": {"model": MODEL, "reasoning_effort": "none"},
    })
    (args.output / "preflight.json").write_text(json.dumps(catalog, indent=2) + "\n")
    (args.output / "protocol.json").write_text(json.dumps({
        "version": "action-persona-case-study-v1", "model": MODEL,
        "scenario": SCENARIO, "common_system": COMMON_SYSTEM,
        "candidate_count": len(candidates), "baseline_count": 3,
        "selection_independence": "LLM judgements do not change static selection status.",
    }, indent=2) + "\n")
    api_path, api_lock = args.output / "api_calls.private.jsonl", threading.Lock()
    baseline_record = lambda value: append_jsonl(api_path, {"candidate_id": None, **value}, api_lock)
    baselines = [generate(COMMON_SYSTEM, "baseline_generator", baseline_record) for _ in range(3)]
    (args.output / "baselines.json").write_text(json.dumps(baselines, indent=2) + "\n")

    results, errors = [], []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(evaluate_one, row, baselines, api_path, api_lock): row["candidate_id"]
                   for row in candidates}
        for future in as_completed(futures):
            candidate_id = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(json.dumps({"candidate_id": candidate_id,
                                  "effect": result["prominent_behavioral_effect"]}), flush=True)
            except Exception as exc:
                errors.append({"candidate_id": candidate_id,
                               "error_type": type(exc).__name__, "error": str(exc)})
                print(json.dumps(errors[-1]), flush=True)
    results.sort(key=lambda row: row["candidate_id"])
    errors.sort(key=lambda row: row["candidate_id"])
    (args.output / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in results))
    (args.output / "errors.json").write_text(json.dumps(errors, indent=2) + "\n")
    summary = {
        "statically_selected": len(candidates),
        "evaluated": len(results),
        "errors": len(errors),
        "qualifying_behavioral_effect": sum(row["prominent_behavioral_effect"] for row in results),
        "difference_distribution": dict(sorted(
            Counter(row["judgement"]["difference"] for row in results).items())),
        "note": "These are evaluation results; they do not alter the rule-based selected set.",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
