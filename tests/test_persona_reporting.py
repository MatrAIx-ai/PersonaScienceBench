"""Offline checks for multi-control persona reporting helpers."""

import importlib.util
import json
import py_compile
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


runner = load("run_persona_benchmarks")


@pytest.mark.parametrize("name", ["run_persona_benchmarks", "report_top_persona_deviations", "report_full_persona_snapshot"])
def test_scripts_compile(name):
    py_compile.compile(str(SCRIPTS / f"{name}.py"), doraise=True)


def test_is_control_in_every_script():
    top = load("report_top_persona_deviations")
    snapshot = load("report_full_persona_snapshot")
    for fn in [runner.is_control, top.is_control, snapshot.is_control]:
        assert fn("persona_off") and fn("persona_off_r2") and fn("persona_off_r10")
        assert not fn("candidate_001") and not fn("persona_offline") and not fn("persona_on")


def test_control_summary_mean_and_sd():
    rows = [{"metrics": {"score": 1.0, "flag": True}, "behavior": {"exchanges": 2, "cost": None}},
            {"metrics": {"score": 3.0}, "behavior": {"exchanges": 4}}]
    means, sds = runner.control_summary(rows)
    assert means == {"metrics": {"score": 2.0}, "behavior": {"exchanges": 3.0}}
    assert sds["metrics"]["score"] == pytest.approx(2 ** 0.5)
    assert sds["behavior"]["exchanges"] == pytest.approx(2 ** 0.5)
    means, sds = runner.control_summary(rows[:1])
    assert means["metrics"] == {"score": 1.0} and sds["metrics"] == {"score": None}


def test_report_pairs_persona_with_control_mean(tmp_path):
    jobs = []
    for arm, grade in [("persona_off", 0.0), ("persona_off_r2", 1.0), ("persona_off_r3", 0.5), ("candidate_001", 1.0)]:
        result = tmp_path / "episodes" / arm / "case" / "result.json"
        result.parent.mkdir(parents=True)
        result.write_text(json.dumps({"status": "scored", "evaluation": {"metrics": {"grade": grade}}}))
        job = {"id": "task-a", "kind": "python", "benchmark": "bixbench", "arm": arm, "key": arm,
               "elapsed_seconds": 1.0, "status": "scored", "result": str(result)}
        jobs.append(job)
        (tmp_path / "finished").mkdir(exist_ok=True)
        (tmp_path / "finished" / f"{arm}.json").write_text(json.dumps(job))
    (tmp_path / "manifest.json").write_text(json.dumps({"jobs": jobs}))
    runner.report(tmp_path)
    comparison = json.loads((tmp_path / "comparison.json").read_text())
    [pair] = comparison["paired_differences"]
    assert pair["arm"] == "candidate_001" and pair["n_controls"] == 3
    assert pair["delta"]["metrics"]["grade"] == pytest.approx(0.5)
    assert pair["delta"]["control_sd"]["metrics"]["grade"] == pytest.approx(0.5)
    assert pair["delta"]["behavior"]["result_rejections"] == 0
    assert "3 fresh shared off control run(s) per task" in (tmp_path / "REPORT.md").read_text()


def test_top_deviation_ranking_is_per_benchmark_against_control_mean():
    top = load("report_top_persona_deviations")
    def row(arm, task, benchmark, metrics, status="scored"):
        return {"arm": arm, "task": task, "benchmark": benchmark, "status": status, "metrics": metrics}
    episodes = [row("persona_off", "s1", "sciconvbench", {"FRR": 0.0}), row("persona_off_r2", "s1", "sciconvbench", {"FRR": 1.0}),
                row("a", "s1", "sciconvbench", {"FRR": 1.0}), row("b", "s1", "sciconvbench", {}, "missing_submission"),
                row("persona_off", "e1", "expbench", {"gated_coverage_mean": 40.0}),
                row("a", "e1", "expbench", {"gated_coverage_mean": 50.0}), row("b", "e1", "expbench", {"gated_coverage_mean": 70.0}),
                row("persona_off", "e2", "expbench", {"gated_coverage_mean": 10.0}), row("a", "e2", "expbench", {}, "runtime_error"),
                row("b", "e2", "expbench", {"gated_coverage_mean": 20.0})]
    rankings, _ = top.benchmark_rankings(episodes, ["a", "b"])
    assert rankings["sciconvbench"]["common_tasks"] == ["s1"] and rankings["expbench"]["common_tasks"] == ["e1"]
    sciconv = {r["persona"]: r["deviation"] for r in rankings["sciconvbench"]["rankings"]}
    assert sciconv == {"a": pytest.approx(0.5), "b": pytest.approx(-0.5)}
    assert [r["persona"] for r in rankings["expbench"]["rankings"]] == ["b", "a"]
    assert rankings["expbench"]["rankings"][0]["deviation"] == pytest.approx(0.3)
