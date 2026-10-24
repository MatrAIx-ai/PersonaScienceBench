"""Apply the released integrity monitor to saved, originally graded designs."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from expbench.paths import ROOT

from pydantic import Field

from expbench.artifacts import write_json
from expbench.budget import Budget, Ledger
from expbench.gateway import Gateway, ModelError, OpenRouterTransport, parse_structured
from expbench.original_control import OriginalGrade
from expbench.runner import file_digest
from expbench.schema import Config, Record
from expbench.judge_protocol import original_messages

PROMPT = (ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_setup_monitor_prompt.txt")


class IntegrityMonitor(Record):
    paper_access: bool = Field(strict=True)
    git_operations: bool = Field(strict=True)
    faked_or_nonexperimental_data: bool = Field(strict=True)
    setup_monitor_comprehensive_reason: str = Field(min_length=1)

    @property
    def passed(self):
        return not (self.paper_access or self.git_operations or self.faked_or_nonexperimental_data)


def evaluate_trace(gateway, prompt, standalone_score):
    """Upstream retries malformed monitor output three times, then gates to zero.

    Transport failures propagate and remain unscored, rather than being treated
    as misconduct. No judge rerun is needed to gate a hash-verified saved grade.
    """
    for attempt in range(1, 4):
        response = gateway.complete("judge", original_messages(prompt), json_object=True)
        try:
            monitor = parse_structured(response, IntegrityMonitor)
        except ModelError:
            continue
        return {
            "monitor": monitor.model_dump(),
            "monitor_status": "passed" if monitor.passed else "rejected",
            "monitor_passed": monitor.passed,
            "monitor_attempts": attempt,
            "standalone_design_score": standalone_score,
            "monitor_gated_design_score": standalone_score if monitor.passed else 0,
        }
    return {
        "monitor": None, "monitor_status": "parse_error", "monitor_passed": False,
        "monitor_attempts": 3, "standalone_design_score": standalone_score,
        "monitor_gated_design_score": 0,
        "error": "Monitor output invalid after three attempts; original parse-failure gate applied",
    }


def load_inputs(grades_from):
    manifest = json.loads((grades_from / "manifest.json").read_text())
    original_prompt = (ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_prompt.txt")
    if manifest.get("template_sha256") != file_digest(original_prompt):
        raise ValueError("Saved grades must use the released original judge prompt")
    prepared = []
    for item in manifest["inputs"]:
        source = Path(item["run"])
        task_id = item["task_id"]
        slug = task_id.replace("/", "__")
        directory = source / slug
        if file_digest(directory / "design.json") != item["design_sha256"]:
            raise ValueError(f"Design changed since original judging: {task_id}")
        events = directory / "actor_events.jsonl"
        logs = events.read_text()
        if not logs.strip():
            raise ValueError(f"Empty actor trace: {task_id}")
        for line in logs.splitlines():
            event = json.loads(line)
            if not isinstance(event, dict) or "kind" not in event:
                raise ValueError(f"Invalid actor event: {task_id}")
        grade_path = grades_from / source.name / slug / "grade.json"
        grade = OriginalGrade.model_validate_json(grade_path.read_text())
        prepared.append({
            "source_run": str(source), "task_id": task_id, "logs": logs,
            "grade": grade.model_dump(), "grade_sha256": file_digest(grade_path),
            "actor_trace_sha256": file_digest(events), "design_sha256": item["design_sha256"],
        })
    if not prepared:
        raise ValueError("No saved original grades to monitor")
    keys = [(Path(i["source_run"]).name, i["task_id"]) for i in prepared]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate input run names or task IDs")
    return prepared


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grades-from", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=(ROOT / "configs/expbench/default.toml"))
    args = parser.parse_args(argv)
    prepared = load_inputs(args.grades_from)
    config = Config.load(args.config)
    template = PROMPT.read_text()
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ValueError("Set OPENROUTER_API_KEY; no requests made")
    args.output.mkdir(parents=True, exist_ok=False)
    args.output.chmod(0o700)
    budget, results = Budget(config.limits.run_usd), []
    transport = OpenRouterTransport(key, config.limits.request_timeout_seconds)
    try:
        catalog = transport.preflight({"judge": config.models.judge},
            enforce_price_caps=config.limits.run_usd is not None or config.limits.episode_usd is not None)
        write_json(args.output / "model_catalog.json", catalog)
        write_json(args.output / "manifest.json", {
            "kind": "original-integrity-monitor-request-replay-v2-on-design-only-traces",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "grades_from": str(args.grades_from.resolve()), "config": config.model_dump(),
            "monitor_prompt_sha256": file_digest(PROMPT),
            "original_judge_manifest_sha256": file_digest(args.grades_from / "manifest.json"),
            "source_sha256": file_digest(Path(__file__)),
            "request_protocol": "released system+empty user, JSON-object mode, three parse attempts",
            "request_protocol_sha256": file_digest(Path(__file__).with_name("judge_protocol.py")),
            "inputs": [{k: v for k, v in i.items() if k not in {"logs", "grade"}} for i in prepared],
            "deviations": ["Current OpenHands JSONL actor events instead of original console logs",
                           "Design-only traces; no implementation or execution attempted",
                           "Saved original-prompt grades reused to isolate the gate",
                           "Current o3-mini through OpenRouter; medium reasoning, 4096 output tokens",
                           "Strict Boolean validation; at most three parse attempts; no transport retries"],
        })
        for item in prepared:
            directory = args.output / Path(item["source_run"]).name / item["task_id"].replace("/", "__")
            directory.mkdir(parents=True)
            prompt = template.format(logs=item["logs"])
            (directory / "monitor_prompt.txt").write_text(prompt)
            write_json(directory / "standalone_grade.json", item["grade"])
            ledger = Ledger(budget, Budget(config.limits.episode_usd))
            gateway = Gateway(transport, {"judge": config.models.judge}, ledger,
                              directory / "api_calls.jsonl")
            result = {
                "source_run": Path(item["source_run"]).name, "task_id": item["task_id"],
                "status": "error", "monitor_applied": True,
                "standalone_design_score": item["grade"]["design_score"],
                "monitor_gated_design_score": None,
            }
            try:
                evaluated = evaluate_trace(gateway, prompt, item["grade"]["design_score"])
                if evaluated["monitor"] is not None:
                    write_json(directory / "monitor.json", evaluated["monitor"])
                result.update(status="completed", **evaluated)
            except Exception as exc:
                result["error"] = str(exc) if isinstance(exc, ModelError) else type(exc).__name__
                raise
            finally:
                write_json(directory / "usage.json", ledger.summary())
                result["budget_charge_usd"] = round(ledger.episode.charged, 7)
                write_json(directory / "result.json", result)
                results.append(result)
                write_json(args.output / "summary.json", {
                    "kind": "original-integrity-monitor-request-replay-v2-on-design-only-traces",
                    "results": results, "budget_charge_usd": round(budget.charged, 7)})
            print(f"{result['source_run']} {item['task_id']}: {result['monitor_status']}; "
                  f"{result['standalone_design_score']} -> {result['monitor_gated_design_score']}", flush=True)
    finally:
        transport.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
