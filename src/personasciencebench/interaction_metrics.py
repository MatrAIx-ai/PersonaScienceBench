"""Offline measures of the recorded ActiveResearcher protocol.

These measure observable interaction, not question usefulness or scientific quality.
No model calls, reference-answer reads, or changes to native grading occur here.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev


VERSION = "active-researcher-interactions-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def read_events(path: Path, episode_id: str) -> list[dict]:
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for index, event in enumerate(events):
        if (not isinstance(event, dict) or type(event.get("sequence")) is not int or event["sequence"] != index
                or event.get("episode_id") != episode_id
                or not isinstance(event.get("type"), str)
                or not isinstance(event.get("payload"), dict)):
            raise ValueError(f"Invalid or incomplete event sequence at line {index + 1}")
    if not events:
        raise ValueError("Empty event log is not evidence of zero interaction")
    return events


def visible_messages(events: list[dict]) -> list[dict]:
    """Exclude private researcher evidence, tool output, artifacts and payloads."""
    messages = []
    for event in events:
        kind, p = event["type"], event["payload"]
        if kind == "researcher_decision":
            role, stage, text = "researcher", p["phase"], p["message"]
        elif kind == "agent_handoff":
            role, stage = "actor", p["stage"]
            fields = [p["answer"], p["evidence"], *p.get("assumptions", []), *p.get("uncertainties", [])]
            if not all(isinstance(value, str) for value in fields):
                raise ValueError("Invalid visible handoff fields")
            text = "\n".join(fields)
        elif kind == "researcher_question":
            role, stage, text = "actor", "optional_question", p["question"]
        elif kind == "researcher_reply":
            role, stage, text = "researcher", "optional_reply", p["answer"]
        elif kind == "shared_progress":
            role, stage, text = "actor", "shared_progress", p["message"]
        else:
            continue
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Empty or invalid visible message")
        messages.append({"event_sequence": event["sequence"], "role": role, "stage": stage, "text": text})
    return messages


def interaction_counts(events: list[dict]) -> dict:
    messages = visible_messages(events)
    decisions = [e["payload"] for e in events if e["type"] == "researcher_decision"]
    handoffs = [e["payload"] for e in events if e["type"] == "agent_handoff"]
    if not decisions:
        raise ValueError("ActiveResearcher metrics require researcher decision records")
    for d in decisions:
        if d["phase"] not in {"initial_inspection", "approach_review", "result_review"} or d["action"] not in {"continue", "stop"}:
            raise ValueError("Unrecognized researcher phase or action")
    if any(h["stage"] not in {"plan", "result"} for h in handoffs):
        raise ValueError("Unrecognized handoff stage")
    phases = Counter(d["phase"] for d in decisions)
    questions = [e["payload"]["question"] for e in events if e["type"] == "researcher_question"]
    commands = [e["payload"] for e in events if e["type"] == "actor_command_result"]
    for command in commands:
        if type(command.get("exit_code")) is not int or type(command.get("timeout")) is not bool:
            raise ValueError("Invalid command result")
    # A repeated question is an exact text repeat; case and punctuation are significant.
    repeated = len(questions) - len(set(questions))
    actor = [m for m in messages if m["role"] == "actor"]
    replies = [m for m in messages if m["role"] == "researcher" and m["stage"] != "initial_inspection"]
    result = {
        "trace_finished": any(e["type"] == "actor_finished" for e in events),
        "actor_handoffs": len(handoffs),
        "plan_handoffs": sum(h["stage"] == "plan" for h in handoffs),
        "result_handoffs": sum(h["stage"] == "result" for h in handoffs),
        "researcher_decisions": len(decisions),
        "approach_reviews": phases["approach_review"],
        "result_reviews": phases["result_review"],
        "extra_approach_reviews": max(0, phases["approach_review"] - 1),
        "extra_result_reviews": max(0, phases["result_review"] - 1),
        "result_revision_requests": sum(d["phase"] == "result_review" and d["action"] == "continue" for d in decisions),
        "optional_question_calls": len(questions),
        "optional_question_exact_repeats": repeated,
        "optional_question_exact_repeat_rate": repeated / len(questions) if questions else None,
        "actor_visible_characters": sum(len(m["text"]) for m in actor),
        "researcher_reply_characters": sum(len(m["text"]) for m in replies),
        "researcher_reply_count": len(replies),
        "researcher_characters_per_reply": mean(len(m["text"]) for m in replies) if replies else None,
        "initial_request_characters": sum(len(m["text"]) for m in messages if m["stage"] == "initial_inspection"),
        "command_attempts": sum(e["type"] == "actor_command" for e in events),
        "command_results": len(commands),
        "command_failures": sum(c["exit_code"] != 0 or c["timeout"] for c in commands),
        "command_timeouts": sum(c["timeout"] for c in commands),
        "dialogue_budget_exhausted": any(e["type"] == "collaboration_budget_exhausted" and e["payload"]["reason"] == "researcher_request_limit" for e in events),
        "actor_budget_exhausted": any(e["type"] == "collaboration_budget_exhausted" and e["payload"]["reason"] == "actor_call_limit" for e in events),
        "question_precision": None,
        "blocker_recall": None,
        "ask_f1": None,
        "semantic_metrics_status": "not_annotated; ASK-F1 not applicable without a validated blocker registry",
    }
    return result


def analysis_score(result: dict) -> float | None:
    """Keep native grades distinct from the declared missing-submission convention."""
    if result["status"] == "missing_submission":
        return 0.0
    if result["status"] != "scored":
        return None
    value = result["evaluation"]["metrics"]["final_score"]
    if type(value) not in {int, float} or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Invalid native score")
    return float(value)


def analyze_case(case: Path, config: dict, *, condition: str, batch: str) -> tuple[dict, dict | None]:
    result = read_json(case / "result.json")
    controller = case / "controller"
    # Exclude identity only; budgets, all model roles and knowledge settings must match.
    comparison_config = {key: value for key, value in config.items() if key not in {"persona", "persona_router", "notes"}}
    settings_hash = hashlib.sha256(json.dumps(comparison_config, sort_keys=True).encode()).hexdigest()
    native = result.get("evaluation") or {}
    row = {
        "batch": batch, "condition": condition, "episode_id": result["episode_id"],
        "task_id": result["source_task_id"], "study_id": result["study_id"],
        "status": result["status"], "analysis_score": analysis_score(result),
        "native_metrics": native.get("metrics", {}), "evaluator_version": native.get("evaluator_version"),
        "submitted": (controller / "submission.json").is_file(),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "settings_sha256": settings_hash, "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
        "source_hashes": {"result.json": digest(case / "result.json")},
        "interaction_status": "unavailable", "interaction_metrics": None, "usage_by_role": None,
    }
    public = controller / "public_input.json"
    row["public_input_sha256"] = digest(public) if public.is_file() else None
    persona_path = controller / "persona.private.json"
    persona = read_json(persona_path) if persona_path.is_file() else {}
    row["persona_sha256"] = persona.get("sha256")
    row["unrestricted_knowledge"] = persona.get("unrestricted_knowledge")
    event_path = controller / "events.jsonl"
    packet = None
    if event_path.is_file():
        row["source_hashes"]["controller/events.jsonl"] = digest(event_path)
        try:
            events = read_events(event_path, result["episode_id"])
            row["interaction_metrics"] = interaction_counts(events)
            row["interaction_status"] = "measured" if row["interaction_metrics"]["trace_finished"] else "partial_trace"
            packet = {"trace_id": digest(event_path), "messages": visible_messages(events),
                      "annotation_status": "pending", "questions_and_proposals": [],
                      "feedback_uptake": [], "preference_expression": []}
        except (KeyError, TypeError, ValueError) as error:
            row["interaction_status"] = "invalid_trace"
            row["interaction_error"] = str(error)
    api_path = controller / "api_calls.private.jsonl"
    if api_path.is_file():
        calls = [json.loads(line) for line in api_path.read_text().splitlines() if line.strip()]
        usage = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "usage_missing_calls": 0})
        for call in calls:
            u = usage[call["role"]]
            u["calls"] += 1
            receipt = call.get("usage") or {}
            if "prompt_tokens" not in receipt or "completion_tokens" not in receipt:
                u["usage_missing_calls"] += 1
            for key in ("prompt_tokens", "completion_tokens"):
                value = receipt.get(key, 0)
                if type(value) is not int or value < 0:
                    raise ValueError("Invalid token usage receipt")
                u[key] += value
        row["usage_by_role"] = dict(usage)
        row["resolved_models"] = sorted({str(c.get("resolved_model", c.get("response", {}).get("model"))) for c in calls})
        row["source_hashes"]["controller/api_calls.private.jsonl"] = digest(api_path)
    return row, packet


def paired_summary(rows: list[dict], baseline: str = "off") -> list[dict]:
    """Pair only within batch, task, public input, settings and evaluator version.

    Aggregate repeat means; missing submissions are zero, infrastructure/evaluator
    errors are excluded. Retain counts and sample SD; never select a best repeat.
    """
    groups = defaultdict(list)
    for row in rows:
        if row["analysis_score"] is not None and row.get("public_input_sha256") is not None:
            key = (row["batch"], row["task_id"], row["public_input_sha256"], row["settings_sha256"])
            groups[key].append(row)
    output = []
    for key, group in sorted(groups.items()):
        controls = [r for r in group if r["condition"] == baseline]
        if not controls:
            continue
        versions = {r["evaluator_version"] for r in group if r["status"] == "scored"}
        models = {tuple(r.get("resolved_models", [])) for r in group if r.get("resolved_models")}
        if len(versions) > 1 or len(models) > 1:
            raise ValueError("Matched comparison contains different evaluators or resolved models")
        for condition in sorted({r["condition"] for r in group} - {baseline}):
            treatment = [r for r in group if r["condition"] == condition]
            scores = [r["analysis_score"] for r in treatment]
            off = [r["analysis_score"] for r in controls]
            output.append({"batch": key[0], "task_id": key[1], "condition": condition,
                           "condition_n": len(scores), "baseline_n": len(off),
                           "condition_mean": mean(scores), "baseline_mean": mean(off),
                           "difference": mean(scores) - mean(off),
                           "condition_sd": stdev(scores) if len(scores) > 1 else None,
                           "baseline_sd": stdev(off) if len(off) > 1 else None})
    return output
