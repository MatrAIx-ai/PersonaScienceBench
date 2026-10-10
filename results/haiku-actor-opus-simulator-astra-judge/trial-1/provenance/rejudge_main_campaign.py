#!/usr/bin/env python3
"""Regrade a completed main campaign without rerunning actors or researchers."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import dataclasses
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "runs/main/haiku-actor-opus-five-condition-full-trial-1"
DEFAULT_OUTPUT = ROOT / "runs/rejudge/haiku-actor-opus-researcher-astra-judge-trial-1"
SOURCES = (
    "asibench",
    "bixbench",
    "discoverybench",
    "expbench",
    "sciconvbench",
)
ARMS = (
    "persona_off",
    "candidate_155",
    "candidate_001",
    "candidate_003",
    "candidate_046",
)
HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
OPUS = "us.anthropic.claude-opus-4-6-v1"
ASTRA = "us.openai.gpt-6-astra"
MODEL_OUTCOMES = {
    "missing_submission",
    "no_submission",
    "workflow_incomplete",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def source_case(state_path: Path, state: dict[str, Any]) -> Path:
    attempt_output = (
        state_path.parent / f"attempt-{int(state['attempt'])}" / "output"
    )
    key = state_path.parent.parent.name
    if state["source"] == "expbench":
        return attempt_output / state["task_id"].replace("/", "__")
    return attempt_output / key


def source_result_path(case: Path) -> Path:
    return case / "result.json"


def validate_source_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "arms": list(ARMS),
        "episode_repeats": 1,
        "task_count": 200,
        "episode_count": 1000,
        "source_counts": {source: 40 for source in SOURCES},
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(
                f"Source campaign has unexpected {key}: {manifest.get(key)!r}"
            )
    roles = manifest.get("role_models") or {}
    role_expectations = {
        "actor": HAIKU,
        "researcher": OPUS,
        "judge": OPUS,
    }
    for role, model in role_expectations.items():
        spec = roles.get(role) or {}
        if spec.get("provider") != "bedrock" or spec.get("model") != model:
            raise ValueError(f"Unexpected source {role} configuration: {spec}")


def load_source_states(source_run: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows = []
    for path in source_run.glob("episodes/*/*/state.json"):
        state = read_json(path)
        rows.append((path, state))
    if len(rows) != 1000:
        raise ValueError(f"Expected 1,000 source states, found {len(rows)}")
    keys = {
        (state["source"], state["task_id"], state["arm"])
        for _, state in rows
    }
    if len(keys) != 1000:
        raise ValueError("Source campaign contains duplicate task/condition states")
    statuses = Counter(state["status"] for _, state in rows)
    if statuses != {"finished": 1000}:
        raise ValueError(f"Source campaign is not complete: {dict(statuses)}")
    if Counter(state["source"] for _, state in rows) != {
        source: 200 for source in SOURCES
    }:
        raise ValueError("Source campaign does not contain 200 states per benchmark")
    if Counter(state["arm"] for _, state in rows) != {
        arm: 200 for arm in ARMS
    }:
        raise ValueError("Source campaign does not contain 200 states per condition")
    return sorted(
        rows,
        key=lambda item: (
            SOURCES.index(item[1]["source"]),
            item[1]["task_id"],
            ARMS.index(item[1]["arm"]),
        ),
    )


def source_native_result(state: dict[str, Any]) -> dict[str, Any]:
    values = state.get("native_results") or []
    if len(values) != 1:
        raise ValueError(
            f"Expected one source native result for "
            f"{state['source']} {state['task_id']} {state['arm']}"
        )
    if not isinstance(values[0], dict):
        raise ValueError("Source native result is not an object")
    return values[0]


def source_outcome(state: dict[str, Any]) -> str:
    result = source_native_result(state)
    return str(result.get("status") or "")


def has_saved_submission(
    state_path: Path, state: dict[str, Any]
) -> tuple[bool, str]:
    case = source_case(state_path, state)
    source = state["source"]
    if source == "expbench":
        found = any((case / f"{stage}_design.json").is_file()
                    for stage in ("initial", "final"))
        return found, "saved_design" if found else source_outcome(state)
    if source == "sciconvbench":
        required = (
            case / "controller/submission.json",
            case / "controller/episode.private.json",
            case / "generated_prompt.txt",
            case / "conversation_log.txt",
        )
        found = all(path.is_file() for path in required)
        return found, "saved_conversation" if found else source_outcome(state)
    submission = case / "controller/submission.json"
    return submission.is_file(), "saved_submission" if submission.is_file() else source_outcome(state)


def inventory(
    source_rows: list[tuple[Path, dict[str, Any]]]
) -> dict[str, Any]:
    by_source = {}
    for source in SOURCES:
        selected = [
            (path, state)
            for path, state in source_rows
            if state["source"] == source
        ]
        availability = Counter(
            has_saved_submission(path, state)[1]
            for path, state in selected
        )
        by_source[source] = {
            "states": len(selected),
            "rejudgeable": sum(
                has_saved_submission(path, state)[0]
                for path, state in selected
            ),
            "availability": dict(availability),
        }
    return {
        "states": len(source_rows),
        "by_source": by_source,
        "rejudgeable": sum(
            has_saved_submission(path, state)[0]
            for path, state in source_rows
        ),
        "retained_model_outcomes": sum(
            not has_saved_submission(path, state)[0]
            for path, state in source_rows
        ),
    }


def judge_spec(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "model": args.model,
        "provider": "bedrock",
        "reasoning_effort": "low",
        "max_tokens": 4096,
        "timeout": 600,
        "unsupported_parameters": "omit_and_record",
        "aws_profile": args.aws_profile,
        "aws_region": args.aws_region,
    }


def output_identity(
    args: argparse.Namespace,
    source_run: Path,
    source_manifest: dict[str, Any],
    source_inventory: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "judge-only-main-campaign-regrade",
        "source_run": relative(source_run),
        "source_manifest_sha256": sha256(source_run / "manifest.json"),
        "source_results_sha256": sha256(source_run / "results.json"),
        "source_selection_sha256": source_manifest["selection_sha256"],
        "source_actor": source_manifest["role_models"]["actor"],
        "source_researcher": source_manifest["role_models"]["researcher"],
        "source_judge": source_manifest["role_models"]["judge"],
        "new_judge": judge_spec(args),
        "task_count": 200,
        "episode_count": 1000,
        "arms": list(ARMS),
        "source_counts": {source: 40 for source in SOURCES},
        "source_inventory": source_inventory,
        "actor_runs_repeated": 0,
        "researcher_runs_repeated": 0,
    }


def next_attempt(base: Path) -> int:
    attempt = 1
    while (base / f"attempt-{attempt}").exists():
        attempt += 1
    return attempt


def count_api_calls(path: Path) -> int:
    if not path.is_file():
        return 0
    count = 0
    with path.open(errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("phase") == "request":
                count += 1
            elif row.get("role") == "judge" and row.get("usage"):
                count += 1
    return count


def normalized_score(
    source: str, evaluation: dict[str, Any] | None
) -> float:
    if not evaluation or evaluation.get("status") != "scored":
        return 0.0
    metrics = evaluation.get("metrics") or {}
    if source == "asibench":
        return 100.0 * float(metrics["score"]) / float(metrics["max_score"])
    if source == "bixbench":
        return 100.0 * float(metrics.get("grade", metrics.get("correct")))
    if source == "discoverybench":
        return 100.0 * float(metrics["final_score"])
    if source == "expbench":
        return float(metrics["gated_coverage_mean"])
    if source == "sciconvbench":
        return 100.0 * float(metrics["FRR"])
    raise ValueError(f"Unknown benchmark: {source}")


def copy_and_verify_submission(
    case: Path, destination: Path
):
    from personasciencebench.schema import Submission

    submission_path = case / "controller/submission.json"
    hashes_path = case / "controller/submission_hashes.json"
    submission_data = read_json(submission_path)
    source_submission = Submission.model_validate(submission_data)
    expected_hashes = read_json(hashes_path)
    if set(expected_hashes) != set(source_submission.artifacts):
        raise ValueError("Saved submission artifact inventory changed")
    sealed = destination / "sealed_submission"
    sealed.mkdir()
    local_artifacts = {}
    for index, (name, raw_path) in enumerate(
        sorted(source_submission.artifacts.items()), 1
    ):
        source = Path(raw_path)
        if not source.is_file():
            raise ValueError(f"Saved submission artifact is missing: {name}")
        observed = sha256(source)
        if observed != expected_hashes[name]:
            raise ValueError(f"Saved submission artifact changed: {name}")
        suffix = hashlib.sha256(name.encode()).hexdigest()[:12]
        target = sealed / f"{index:03d}-{suffix}-{source.name}"
        shutil.copyfile(source, target)
        if sha256(target) != observed:
            raise ValueError(f"Copied submission artifact changed: {name}")
        local_artifacts[name] = str(target.resolve())
    local_data = {**submission_data, "artifacts": local_artifacts}
    write_json(destination / "source_submission.json", submission_data)
    write_json(destination / "submission_hashes.json", expected_hashes)
    write_json(destination / "submission.json", local_data)
    return Submission.model_validate(local_data), sha256(submission_path)


def configured_evaluation(
    evaluation,
    client,
    spec: dict[str, Any],
) -> dict[str, Any]:
    evaluation.evaluator_version += "+configured-judge-v1"
    evaluation.details["judge_model"] = spec["model"]
    evaluation.details["judge_provider"] = spec["provider"]
    evaluation.details["judge_reasoning_effort"] = spec["reasoning_effort"]
    if client.parameter_adaptations:
        evaluation.evaluator_version += "+provider-defaults-v1"
        evaluation.details["judge_parameter_adaptations"] = (
            client.parameter_adaptations
        )
        evaluation.details["native_sampling_settings_preserved"] = False
    if client.format_adaptations:
        evaluation.evaluator_version += "+json-fence-v1"
        evaluation.details["transport_format_adaptations"] = (
            client.format_adaptations
        )
    return evaluation.model_dump(mode="json")


def rejudge_standard(
    source: str,
    case: Path,
    destination: Path,
    spec: dict[str, Any],
    supported_parameters: list[str],
) -> tuple[dict[str, Any], str]:
    from personasciencebench.inference import OpenRouterClient
    from personasciencebench.registry import load_adapter
    from personasciencebench.schema import Episode

    episode_path = case / "controller/episode.private.json"
    episode = Episode.model_validate(read_json(episode_path))
    submission, submission_hash = copy_and_verify_submission(case, destination)
    api_log = destination / "api_calls.private.jsonl"

    def record(value: dict[str, Any]) -> None:
        with api_log.open("a") as handle:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")

    client = OpenRouterClient(
        **spec,
        role="judge",
        record=record,
        supported_parameters=supported_parameters,
    )
    adapter = load_adapter(
        source, ROOT / "external/sources", ROOT / "manifests/sources.json"
    )
    evaluation = adapter.evaluate(episode, submission, client)
    return configured_evaluation(evaluation, client, spec), submission_hash


def exp_gateway(
    destination: Path,
    spec: dict[str, Any],
):
    from expbench.budget import Budget, Ledger
    from expbench.gateway import BedrockTransport, Gateway
    from expbench.schema import ModelSettings

    settings = ModelSettings.model_validate({
        "provider": "bedrock",
        "model": spec["model"],
        "aws_profile": spec["aws_profile"],
        "aws_region": spec["aws_region"],
        "max_output_tokens": spec["max_tokens"],
        "input_usd_per_million": 11,
        "output_usd_per_million": 55,
        "reasoning_effort": spec["reasoning_effort"],
    })
    transport = BedrockTransport({"judge": settings}, timeout=spec["timeout"])
    ledger = Ledger(Budget(None), Budget(None))
    gateway = Gateway(
        transport,
        {"judge": settings},
        ledger,
        destination / "api_calls.private.jsonl",
    )
    return gateway, transport, ledger


def rejudge_exp(
    case: Path,
    destination: Path,
    task_id: str,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    from expbench.design_evaluation import evaluate_design

    gateway, transport, ledger = exp_gateway(destination, spec)
    evaluated: dict[str, Any] = {}
    checkpoint_hashes = {}
    try:
        for stage in ("initial", "final"):
            checkpoint_path = case / f"{stage}_design.json"
            if not checkpoint_path.is_file():
                continue
            checkpoint = read_json(checkpoint_path)
            checkpoint_hashes[stage] = sha256(checkpoint_path)
            copy = destination / f"{stage}_design.json"
            shutil.copyfile(checkpoint_path, copy)
            if sha256(copy) != checkpoint_hashes[stage]:
                raise ValueError(f"Saved EXP {stage} checkpoint changed while copying")
            evaluated[stage] = evaluate_design(
                gateway,
                task_id,
                checkpoint,
                destination / f"{stage}_evaluation",
                repeats=3,
            )
    finally:
        transport.close()
        write_json(destination / "usage.json", ledger.summary())
    selected = evaluated.get("final") or evaluated.get("initial")
    if selected is None:
        raise ValueError("Saved EXP result has no design checkpoint")
    evaluation = {
        "status": "scored",
        "evaluator_version": "expbench-design-evaluation+configured-judge-v1",
        "metrics": {
            **selected,
            "selected_stage": "final" if evaluated.get("final") else "initial",
        },
        "details": {
            "judge_model": spec["model"],
            "judge_provider": spec["provider"],
            "judge_reasoning_effort": spec["reasoning_effort"],
            "checkpoint_hashes": checkpoint_hashes,
            "all_stages": evaluated,
        },
    }
    return evaluation, hashlib.sha256(
        json.dumps(checkpoint_hashes, sort_keys=True).encode()
    ).hexdigest()


def rejudge_sciconv(
    case: Path,
    destination: Path,
    source_manifest: dict[str, Any],
    spec: dict[str, Any],
    supported_parameters: list[str],
) -> tuple[dict[str, Any], str]:
    from personasciencebench.adapters.sciconvbench import POLICY
    from personasciencebench.inference import OpenRouterClient
    from personasciencebench.registry import load_adapter
    from personasciencebench.schema import Episode
    from personasciencebench.sciconv_runner import (
        Service,
        native_class,
        paper_module,
    )

    episode_path = case / "controller/episode.private.json"
    final_path = case / "generated_prompt.txt"
    conversation_path = case / "conversation_log.txt"
    episode = Episode.model_validate(read_json(episode_path))
    final = final_path.read_text()
    conversation = conversation_path.read_text()
    source_hash = hashlib.sha256()
    for path in (episode_path, final_path, conversation_path):
        source_hash.update(sha256(path).encode())
    shutil.copyfile(final_path, destination / "generated_prompt.txt")
    shutil.copyfile(conversation_path, destination / "conversation_log.txt")
    api_log = destination / "api_calls.private.jsonl"

    def record(value: dict[str, Any]) -> None:
        with api_log.open("a") as handle:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")

    client = OpenRouterClient(
        **spec,
        role="judge",
        record=record,
        supported_parameters=supported_parameters,
    )
    service = Service(client)
    adapter = load_adapter(
        "sciconvbench",
        ROOT / "external/sources",
        ROOT / "manifests/sources.json",
    )
    native = paper_module(adapter.source.repository)
    row = episode.evaluator.reference["native_row"]
    mode = episode.evaluator.reference["mode"]
    domain = episode.evaluator.reference["domain"]
    truth = episode.researcher.facts[0].text
    issues = row[
        "missing_entities" if mode == "disambiguation" else "inconsistencies"
    ]
    name = "Disambiguation" if mode == "disambiguation" else "Inconsistency"
    judge_class = native_class(
        adapter.source.repository,
        f"llm_judge_{mode}.py",
        "LLMJudge" + name,
        service,
    )
    judge = judge_class()
    if mode == "disambiguation":
        grading = judge.evaluate(truth, final, issues)
    else:
        grading = judge.evaluate(final, issues, episode.public.question, truth)
    recovered = None
    if mode == "disambiguation":
        numerator, denominator = map(int, grading["score"].split("/"))
        grading["strict_score"] = (
            "1/1" if numerator == denominator and denominator > 0 else "0/1"
        )
        grading["partial_score"] = f"{numerator}/{denominator}"
        recovered = numerator / denominator if denominator else None
    else:
        grading["strict_score"] = grading.get("score", "0/1")
    chat_class = native_class(
        adapter.source.repository,
        f"llm_judge_{mode}_chat.py",
        "LLMJudge" + name + "Chat",
        service,
    )
    chat = chat_class()
    parsed = chat.parse_conversation_log(conversation)
    chat_result = chat.evaluate(parsed, issues, final)
    chat_result["total_questions_asked_in_chat"] = len(parsed)
    issue_key = (
        "total_missing_entities"
        if mode == "disambiguation"
        else "total_planted_inconsistencies"
    )
    chat_result[issue_key] = len(issues)
    intent = native_class(
        adapter.source.repository,
        "llm_judge_intent.py",
        "LLMJudgeIntent",
        service,
    )().evaluate(final, truth)
    suffix_values = (
        (mode, grading),
        (mode + "_chat", chat_result),
        ("intent", intent),
    )
    for suffix, value in suffix_values:
        write_json(destination / f"llm_judge_{suffix}_score.json", value)
    if any(
        "parsing failed" in json.dumps(value).lower()
        or "could not parse" in json.dumps(value).lower()
        for _, value in suffix_values
    ):
        raise ValueError("Native SciConv judge output parsing failed")
    scorer = (
        native._score_disambiguation
        if mode == "disambiguation"
        else native._score_inconsistency
    )
    native_case = scorer(
        destination,
        len(episode.public.question),
        domain,
        source_manifest["role_models"]["actor"]["model"],
        row["id"],
        row,
    )
    fact_recovery = int(native_case.FR and native_case.IC)
    grounded = int(native_case.grounded and native_case.IC)
    original_result = read_json(case / "result.json")
    original_metrics = (original_result.get("evaluation") or {}).get("metrics") or {}
    relevant_key = (
        "questions_about_missing_entities"
        if mode == "disambiguation"
        else "questions_about_inconsistencies"
    )
    metrics = {
        "FRR": fact_recovery,
        "FR": int(native_case.FR),
        "entity_recovery": recovered,
        "question_limit_reached": int(
            original_metrics.get("question_limit_reached", 0)
        ),
        "CGRR": fact_recovery * grounded,
        "SRR": fact_recovery * (1 - grounded),
        "intent_capture": native_case.IC,
        "clarification_recall": (
            chat_result.get(relevant_key, {}).get("count", 0) / len(issues)
        ),
        "clarification_precision": (
            chat_result.get("relevant_questions", {}).get("count", 0)
            / len(parsed)
            if parsed
            else 0.0
        ),
        "native_paper_CR": native_case.CR,
        "native_paper_CP": native_case.CP,
        "memory_consistency": native_case.MC,
    }
    evaluation = {
        "status": "scored",
        "evaluator_version": POLICY + "+native-judge+configured-judge-v1",
        "metrics": metrics,
        "details": {
            "judge_model": spec["model"],
            "judge_provider": spec["provider"],
            "judge_reasoning_effort": spec["reasoning_effort"],
            "native_case": dataclasses.asdict(native_case),
            "native_silent_resolution_correction": True,
            "score_scope": (
                "specification and conversation; no scientific solver execution"
            ),
            "source_conversation_sha256": sha256(conversation_path),
            "source_final_specification_sha256": sha256(final_path),
            "judge_parameter_adaptations": client.parameter_adaptations,
            "judge_format_adaptations": client.format_adaptations,
        },
    }
    return evaluation, source_hash.hexdigest()


def retained_outcome(
    state: dict[str, Any], case: Path
) -> tuple[dict[str, Any], str]:
    source_result = source_native_result(state)
    status = source_result.get("status")
    if status not in MODEL_OUTCOMES:
        raise ValueError(
            f"No saved submission exists, but source outcome is {status!r}"
        )
    source_path = source_result_path(case)
    source_hash = sha256(source_path)
    evaluation = source_result.get("evaluation")
    if not isinstance(evaluation, dict):
        evaluation = {
            "status": status,
            "evaluator_version": "source-model-outcome-retained",
            "metrics": {},
            "details": {},
        }
    return evaluation, source_hash


def one_regrade(
    state_path: Path,
    source_state: dict[str, Any],
    output_dir: Path,
    source_manifest: dict[str, Any],
    spec: dict[str, Any],
    supported_parameters: list[str],
    retry_infrastructure: bool,
) -> dict[str, Any]:
    key = state_path.parent.parent.name
    arm = source_state["arm"]
    base = output_dir / "episodes" / key / arm
    state_file = base / "state.json"
    if state_file.is_file():
        old = read_json(state_file)
        if old.get("status") == "finished":
            return old
        if old.get("status") == "infrastructure_error" and not retry_infrastructure:
            return old
    base.mkdir(parents=True, exist_ok=True)
    attempt = next_attempt(base)
    destination = base / f"attempt-{attempt}"
    destination.mkdir()
    result = {
        "source": source_state["source"],
        "task_id": source_state["task_id"],
        "arm": arm,
        "attempt": attempt,
        "status": "running",
        "started_at": time.time(),
        "source_attempt": int(source_state["attempt"]),
        "source_state": relative(state_path),
        "source_state_sha256": sha256(state_path),
        "actor_rerun": False,
        "researcher_rerun": False,
        "judge_model": spec["model"],
        "judge_provider": spec["provider"],
        "judge_reasoning_effort": spec["reasoning_effort"],
    }
    write_json(state_file, result)
    case = source_case(state_path, source_state)
    result["source_case"] = relative(case)
    try:
        available, availability = has_saved_submission(state_path, source_state)
        result["source_availability"] = availability
        if not available:
            evaluation, submission_hash = retained_outcome(source_state, case)
            result["judge_calls"] = 0
            result["regrade_disposition"] = "model_outcome_retained_without_call"
        elif source_state["source"] in {
            "asibench", "bixbench", "discoverybench"
        }:
            evaluation, submission_hash = rejudge_standard(
                source_state["source"],
                case,
                destination,
                spec,
                supported_parameters,
            )
            result["regrade_disposition"] = "saved_submission_rejudged"
        elif source_state["source"] == "expbench":
            evaluation, submission_hash = rejudge_exp(
                case,
                destination,
                source_state["task_id"],
                spec,
            )
            result["regrade_disposition"] = "saved_design_rejudged"
        elif source_state["source"] == "sciconvbench":
            evaluation, submission_hash = rejudge_sciconv(
                case,
                destination,
                source_manifest,
                spec,
                supported_parameters,
            )
            result["regrade_disposition"] = "saved_conversation_rejudged"
        else:
            raise ValueError(f"Unsupported source: {source_state['source']}")
        write_json(destination / "evaluation.json", evaluation)
        result.update({
            "evaluation": evaluation,
            "submission_or_trace_sha256": submission_hash,
            "submitted": available,
            "score_0_100": normalized_score(
                source_state["source"], evaluation
            ),
        })
        result["judge_calls"] = count_api_calls(
            destination / "api_calls.private.jsonl"
        )
        if evaluation.get("status") == "error":
            result["status"] = "infrastructure_error"
            result["error"] = "Judge evaluation returned status=error"
        elif evaluation.get("status") == "blocked":
            result["status"] = "infrastructure_error"
            result["error"] = "Judge evaluation returned status=blocked"
        else:
            result["status"] = "finished"
    except Exception as exc:
        result.update({
            "status": "infrastructure_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "judge_calls": count_api_calls(
                destination / "api_calls.private.jsonl"
            ),
        })
    result["finished_at"] = time.time()
    write_json(state_file, result)
    return result


def aggregate_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    finished = [row for row in results if row["status"] == "finished"]
    summary: dict[str, Any] = {
        "episodes": len(results),
        "statuses": dict(Counter(row["status"] for row in results)),
        "judge_calls": sum(int(row.get("judge_calls", 0)) for row in results),
        "actor_runs_repeated": 0,
        "researcher_runs_repeated": 0,
        "by_condition": {},
        "by_benchmark_condition": {},
    }
    for arm in ARMS:
        rows = [row for row in finished if row["arm"] == arm]
        summary["by_condition"][arm] = {
            "finished": len(rows),
            "submitted": sum(bool(row.get("submitted")) for row in rows),
            "mean_score_0_100": (
                sum(float(row["score_0_100"]) for row in rows) / len(rows)
                if rows else None
            ),
            "judge_calls": sum(int(row.get("judge_calls", 0)) for row in rows),
        }
    for source in SOURCES:
        summary["by_benchmark_condition"][source] = {}
        for arm in ARMS:
            rows = [
                row for row in finished
                if row["source"] == source and row["arm"] == arm
            ]
            summary["by_benchmark_condition"][source][arm] = {
                "finished": len(rows),
                "submitted": sum(bool(row.get("submitted")) for row in rows),
                "mean_score_0_100": (
                    sum(float(row["score_0_100"]) for row in rows) / len(rows)
                    if rows else None
                ),
                "judge_calls": sum(
                    int(row.get("judge_calls", 0)) for row in rows
                ),
            }
    return summary


def all_output_states(output_dir: Path) -> list[dict[str, Any]]:
    rows = [
        read_json(path)
        for path in output_dir.glob("episodes/*/*/state.json")
    ]
    return sorted(
        rows,
        key=lambda row: (
            SOURCES.index(row["source"]),
            row["task_id"],
            ARMS.index(row["arm"]),
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=ASTRA)
    parser.add_argument("--aws-profile", default="default")
    parser.add_argument("--aws-region", default="us-west-2")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--retry-infrastructure", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.model != ASTRA:
        raise ValueError(f"This regrade is pinned to {ASTRA}")
    if not 1 <= args.workers <= (os.cpu_count() or 1):
        raise ValueError("Workers must be between 1 and the available CPU count")
    source_run = args.source_run.resolve()
    output_dir = args.output_dir.resolve()
    if source_run == output_dir or source_run in output_dir.parents:
        raise ValueError("Regrade output must be separate from the source campaign")
    source_manifest = read_json(source_run / "manifest.json")
    validate_source_manifest(source_manifest)
    source_rows = load_source_states(source_run)
    source_inventory = inventory(source_rows)
    identity = output_identity(
        args, source_run, source_manifest, source_inventory
    )
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "source_run": relative(source_run),
            "output_dir": relative(output_dir),
            "judge": judge_spec(args),
            "workers": args.workers,
            "inventory": source_inventory,
            "actor_runs_repeated": 0,
            "researcher_runs_repeated": 0,
        }, indent=2))
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    lock = (output_dir / "coordinator.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise RuntimeError(f"Another regrade is active in {output_dir}") from None
    manifest_path = output_dir / "manifest.json"
    if manifest_path.is_file():
        if read_json(manifest_path) != identity:
            raise ValueError("Regrade identity changed; use a new output directory")
    else:
        write_json(manifest_path, identity)
    from personasciencebench.inference import preflight
    spec = judge_spec(args)
    catalog = preflight({"judge": spec})
    write_json(output_dir / "api_access.json", catalog)
    write_json(
        output_dir / f"code.{time.time_ns()}.json",
        {
            str(path.relative_to(ROOT)): sha256(path)
            for folder in ("src", "scripts")
            for path in (ROOT / folder).rglob("*.py")
        },
    )
    supported_parameters = catalog["judge"]["supported_parameters"]
    print(
        f"Validated {len(source_rows)}/1000 frozen source trajectories; "
        f"{source_inventory['rejudgeable']} have saved submissions/designs and "
        f"{source_inventory['retained_model_outcomes']} model outcomes require no call",
        flush=True,
    )
    jobs = []
    for state_path, state in source_rows:
        destination_state = (
            output_dir / "episodes" / state_path.parent.parent.name
            / state["arm"] / "state.json"
        )
        if destination_state.is_file():
            previous = read_json(destination_state)
            if previous.get("status") == "finished":
                continue
            if (
                previous.get("status") == "infrastructure_error"
                and not args.retry_infrastructure
            ):
                continue
        jobs.append((state_path, state))
    print(
        f"Starting {len(jobs)} judge-only endpoint(s) with {args.workers} workers",
        flush=True,
    )
    processed = 0
    status_counter: Counter[str] = Counter()
    progress_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                one_regrade,
                state_path,
                state,
                output_dir,
                source_manifest,
                spec,
                supported_parameters,
                args.retry_infrastructure,
            ): (state_path, state)
            for state_path, state in jobs
        }
        for future in as_completed(futures):
            result = future.result()
            processed += 1
            status_counter[result["status"]] += 1
            with progress_lock:
                current = all_output_states(output_dir)
                write_json(output_dir / "progress.json", {
                    "planned": 1000,
                    "states_present": len(current),
                    "processed_this_invocation": processed,
                    "statuses_this_invocation": dict(status_counter),
                    "statuses_all": dict(
                        Counter(row["status"] for row in current)
                    ),
                    "updated_at": time.time(),
                })
            print(
                f"{result['source']} {result['task_id']} {result['arm']}: "
                f"{result['status']} ({result.get('judge_calls', 0)} judge calls)",
                flush=True,
            )
    results = all_output_states(output_dir)
    write_json(output_dir / "results.json", results)
    summary = aggregate_summary(results)
    summary["generated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(output_dir / "summary.json", summary)
    if len(results) != 1000:
        print(
            f"Regrade incomplete: {len(results)}/1000 states exist. "
            "Rerun the same command to resume.",
            file=sys.stderr,
        )
        return 1
    if summary["statuses"] != {"finished": 1000}:
        print(
            f"Regrade has non-finished endpoints: {summary['statuses']}. "
            "After fixing infrastructure, rerun with --retry-infrastructure.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
