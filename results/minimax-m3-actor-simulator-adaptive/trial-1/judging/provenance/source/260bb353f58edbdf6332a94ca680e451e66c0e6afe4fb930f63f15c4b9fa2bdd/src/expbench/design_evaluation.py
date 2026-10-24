"""Repeated released-prompt reference coverage with the original integrity gate."""

import statistics
from pathlib import Path
from expbench.paths import ROOT

from expbench.artifacts import write_json
from expbench.integrity import PROMPT as MONITOR_PROMPT, evaluate_trace
from expbench.judge_protocol import query_original
from expbench.original_control import OriginalGrade, raw_task
from expbench.runner import file_digest

DESIGN_PROMPT = (ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_prompt.txt")


def evaluate_design(gateway, task_id, checkpoint, output, repeats=3):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    raw, raw_path = raw_task(task_id)
    prompt = DESIGN_PROMPT.read_text().format(design_gt=raw["design_complexity"],
        conclusion_gt=raw["expected_outcome"], design_output=checkpoint["plan"],
        conclusion_output=checkpoint.get("conclusion", ""))
    (output / "coverage_prompt.txt").write_text(prompt)
    samples, conclusions = [], []
    for i in range(repeats):
        grade = query_original(gateway, prompt, OriginalGrade)
        samples.append(grade.design_score)
        conclusions.append(grade.conclusion_score == "correct")
        write_json(output / f"sample-{i + 1}.json", {"coverage": grade.model_dump()})
    mean = statistics.mean(samples)
    monitor = evaluate_trace(gateway, MONITOR_PROMPT.read_text().format(logs=checkpoint["trace"]), mean)
    mock = gateway.transport.mock
    result = {"mock": mock, "repeats": repeats,
        "reference_sha256": file_digest(raw_path),
        "coverage_template_sha256": file_digest(DESIGN_PROMPT),
        "monitor_template_sha256": file_digest(MONITOR_PROMPT),
        "coverage_mean": None if mock else mean,
        "coverage_std": None if mock else statistics.pstdev(samples),
        "conclusion_correct_fraction": (statistics.mean(conclusions)
            if not mock and checkpoint.get("conclusion") else None),
        "monitor_status": monitor["monitor_status"],
        "monitor_passed": None if mock else monitor["monitor_passed"],
        "gated_coverage_mean": None if mock else monitor["monitor_gated_design_score"],
        "note": "Reference coverage with the original integrity gate. Mock sample values are fixtures, not benchmark results."}
    write_json(output / "monitor.json", {"mock": mock, **monitor})
    write_json(output / "summary.json", result)
    return result
