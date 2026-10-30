"""Original-input design control and original-prompt judge diagnostic.

Neither mode reproduces the full-experiment runtime or its monitor-gated score.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from expbench.paths import ROOT
from typing import Literal

from pydantic import Field

from expbench.artifacts import write_json
from expbench.budget import Budget, Ledger
from expbench.gateway import Gateway, ModelError, OpenRouterTransport, parse_structured
from expbench.runner import file_digest
from expbench.schema import Config, Design, Record, load_tasks
from expbench.judge_protocol import query_original


class OriginalGrade(Record):
    design_evaluation_explanation: str
    design_score: int = Field(ge=0, le=100, strict=True)
    design_error_analysis: str
    conclusion_evaluation_explanation: str
    conclusion_score: Literal["correct", "incorrect"]
    conclusion_error_analysis: str


def raw_task(task_id, root=(ROOT / "data/exp_bench/raw/upstream/tasks")):
    conference, paper, index = task_id.split("/")
    path = root / conference / (paper + ".json")
    return json.loads(path.read_text())["questions"][int(index)], path


def make_static_task(task, raw):
    control = task.model_copy(deep=True)
    control.public.question = raw.get("question", raw.get("hypothesis"))
    control.public.context = json.dumps({
        "method": raw["method"],
        "agent_instructions": raw.get("agent_instructions", ""),
    }, ensure_ascii=False)
    control.provenance["control"] = "original-input-design-only-no-researcher"
    control.review_notes.append(
        "Original method and agent_instructions preserved verbatim as string values; "
        "may contain expected-result hints present in the released inputs. "
        "No repository, experiment execution, or original integrity monitor."
    )
    return control


def render_original_judge(template, raw, design):
    # Upstream helper.load_system_prompt uses str.format, including Python's
    # dictionary representation for the unmodified design_complexity object.
    # Preserve every design field as a string, one of the original accepted forms.
    return template.format(
        design_gt=raw["design_complexity"],
        conclusion_gt=raw["expected_outcome"],
        design_output=json.dumps(design.model_dump(), ensure_ascii=False),
        conclusion_output="",  # No empirical conclusion exists; never fabricate one.
    )


def prepare(tasks, output):
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    cards = []
    sources = {}
    for task in tasks:
        raw, path = raw_task(task.task_id)
        control = make_static_task(task, raw)
        cards.append(control.model_dump())
        sources[str(path)] = file_digest(path)
        directory = output / task.task_id.replace("/", "__")
        write_json(directory / "actor_input.json", {
            "question": control.public.question,
            "method": raw["method"],
            "agent_instructions": raw.get("agent_instructions", ""),
        })
    (output / "tasks.jsonl").write_text(
        "".join(json.dumps(card, ensure_ascii=False) + "\n" for card in cards))
    write_json(output / "manifest.json", {
        "kind": "original-input-design-only-control",
        "sources_sha256": sources,
        "tasks_sha256": file_digest(output / "tasks.jsonl"),
        "limitations": ["No original repository access", "No experiment execution",
                        "No original integrity monitor", "Current OpenHands SDK"],
    })
    print(f"Prepared {len(cards)} original-input cards at {output}")


def judge_saved(tasks, designs_from, config, output):
    template_path = (ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_prompt.txt")
    template = template_path.read_text()
    prepared = []
    for source in designs_from:
        for task in tasks:
            raw, raw_path = raw_task(task.task_id)
            path = source / task.task_id.replace("/", "__") / "design.json"
            design = Design.model_validate_json(path.read_text())
            prepared.append((source, task.task_id, path, raw_path,
                             render_original_judge(template, raw, design)))
    if len({p.name for p in designs_from}) != len(designs_from):
        raise ValueError("Input run directories must have distinct names")
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ValueError("Set OPENROUTER_API_KEY before judging; no requests made")
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    budget = Budget(config.limits.run_usd)
    results = []
    transport = OpenRouterTransport(key, config.limits.request_timeout_seconds)
    try:
        catalog = transport.preflight({"judge": config.models.judge},
            enforce_price_caps=config.limits.run_usd is not None or config.limits.episode_usd is not None)
        write_json(output / "model_catalog.json", catalog)
        write_json(output / "manifest.json", {
            "kind": "original-request-judge-replay-v2-not-full-benchmark",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "config": config.model_dump(),
            "template_sha256": file_digest(template_path),
            "script_sha256": file_digest(Path(__file__)),
            "request_protocol_sha256": file_digest(Path(__file__).with_name("judge_protocol.py")),
            "inputs": [{"run": str(s.resolve()), "task_id": tid,
                        "design_sha256": file_digest(p), "raw_task_sha256": file_digest(r)}
                       for s, tid, p, r, _ in prepared],
            "deviations": ["Saved design-only outputs, serialized as JSON strings",
                           "Empty empirical conclusion", "No integrity monitor gate",
                           "OpenRouter transport, current o3-mini alias, medium reasoning",
                           "Configured output cap; original system/user roles and JSON-object mode; three parse attempts"],
        })
        for source, task_id, _, _, prompt in prepared:
            directory = output / source.name / task_id.replace("/", "__")
            directory.mkdir(parents=True)
            (directory / "original_judge_prompt.txt").write_text(prompt)
            ledger = Ledger(budget, Budget(config.limits.episode_usd))
            gateway = Gateway(transport, {"judge": config.models.judge}, ledger,
                              directory / "api_calls.jsonl")
            result = {"source_run": source.name, "task_id": task_id,
                      "status": "error", "design_score": None,
                      "monitor_applied": False, "benchmark_score": None}
            try:
                grade = query_original(gateway, prompt, OriginalGrade)
                write_json(directory / "grade.json", grade.model_dump())
                result.update(status="completed", design_score=grade.design_score)
            except Exception as exc:
                result["error"] = str(exc) if isinstance(exc, ModelError) else type(exc).__name__
                raise
            finally:
                write_json(directory / "usage.json", ledger.summary())
                result["budget_charge_usd"] = round(ledger.episode.charged, 7)
                write_json(directory / "result.json", result)
                results.append(result)
                write_json(output / "summary.json", {
                    "kind": "original-request-judge-replay-v2-not-full-benchmark",
                    "results": results, "budget_charge_usd": round(budget.charged, 7)})
            print(f"{source.name} {task_id}: {grade.design_score}/100", flush=True)
    finally:
        transport.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "judge-saved"])
    parser.add_argument("--tasks", type=Path, default=(ROOT / "data/conversion-v2-exp/tasks.jsonl"))
    parser.add_argument("--config", type=Path, default=(ROOT / "configs/expbench/default.toml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--designs-from", type=Path, nargs="+")
    args = parser.parse_args(argv)
    tasks = load_tasks(args.tasks)
    if args.command == "prepare":
        prepare(tasks, args.output)
    else:
        if not args.designs_from:
            parser.error("judge-saved requires --designs-from")
        judge_saved(tasks, args.designs_from, Config.load(args.config), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
