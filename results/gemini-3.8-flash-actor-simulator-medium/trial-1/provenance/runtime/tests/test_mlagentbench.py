"""Offline conversion/boundary/native-grader checks; no model or training runs."""

import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

import pytest

from personasciencebench.adapters.base import SourceConfig, sha256
from personasciencebench.adapters.mlagentbench import (
    CIFAR10_ARCHIVE, EXCLUDED, EVALUATOR_VERSION, MLAgentBenchAdapter, PINNED,
    SOURCE_REVISION, TASKS, derive_improvement,
)
from personasciencebench.schema import (
    Episode, EvaluatorSpec, PublicContext, ResearcherContext, Submission,
)


SOURCE_ROOT = Path(os.environ.get("PERSONASCIENCEBENCH_SOURCE_ROOT",
                                  Path(__file__).resolve().parents[2] / "benchmarks"))
BENCHMARKS = "MLAgentBench/benchmarks"


@pytest.fixture
def adapter():
    source = SourceConfig(SOURCE_ROOT / "mlagentbench", SOURCE_ROOT / "_assets/mlagentbench",
                          SOURCE_REVISION)
    if not (source.repository / BENCHMARKS).is_dir():
        pytest.skip("Pinned external MLAgentBench checkout is not provisioned")
    return MLAgentBenchAdapter(source)


def offline_adapter(repository: Path, assets: Path) -> MLAgentBenchAdapter:
    return MLAgentBenchAdapter(SourceConfig(repository, assets, SOURCE_REVISION))


def synthetic_episode(repository: Path, *, sentinel=1e10) -> Episode:
    eval_file = repository / BENCHMARKS / "vectorization/scripts/eval.py"
    return Episode(
        id="mlagentbench:vectorization", benchmark="mlagentbench",
        source_task_id="vectorization", study_id="mlagentbench:code-improvement",
        domain="numerical computing", source_revision=SOURCE_REVISION,
        public=PublicContext(question="synthetic",
                             submission={"required_artifacts": ["submission.csv"]}),
        researcher=ResearcherContext(unknowns=["synthetic"]),
        evaluator=EvaluatorSpec(kind="native_local_get_score", version=EVALUATOR_VERSION,
                                reference={"eval_script_sha256": sha256(eval_file),
                                           "metric": {"name": "runtime_seconds", "direction": "lower"},
                                           "failure_sentinel": sentinel, "eval_cache": None}))


def synthetic_source(tmp_path: Path) -> Path:
    repository = tmp_path / "repo"
    scripts = repository / BENCHMARKS / "vectorization/scripts"
    scripts.mkdir(parents=True)
    (scripts / "eval.py").write_text(
        "def get_score(submission_folder='../env'):\n"
        "    try:\n"
        "        with open(submission_folder + '/submission.csv') as stream:\n"
        "            return float(stream.read().split(';')[0])\n"
        "    except Exception:\n"
        "        return 1e10\n")
    return repository


@pytest.fixture
def local_driver(monkeypatch):
    """Run the generated driver without Bubblewrap; counts invocations."""
    calls = []

    def run(self, work):
        calls.append(work)
        process = subprocess.run([sys.executable, "evaluate_driver.py"], cwd=work,
                                 capture_output=True, text=True)
        return {"exit_code": process.returncode, "stdout": process.stdout,
                "stderr": process.stderr, "timeout": False, "duration": 0.0}

    monkeypatch.setattr(MLAgentBenchAdapter, "_run_driver", run)
    return calls


def submission(episode, tmp_path, content="0.5"):
    submitted = tmp_path / "submitted_artifacts"
    submitted.mkdir(parents=True, exist_ok=True)
    (submitted / "submission.csv").write_text(content + "\n")
    (submitted / "train.py").write_text("# submitted training script\n")
    return Submission(episode_id=episode.id, answer="synthetic",
                      artifacts={"submission.csv": str(submitted / "submission.csv"),
                                 "train.py": str(submitted / "train.py")})


def test_inventory_pilots_and_exclusions():
    adapter = offline_adapter(Path("/nonexistent"), Path("/nonexistent"))
    tasks = adapter.enumerate_tasks()
    assert len(tasks) == 12 and len({t.id for t in tasks}) == 12
    assert set(EXCLUDED).isdisjoint({t.id for t in tasks})
    pilots = adapter.pilot_task_ids()
    summaries = {t.id: t for t in tasks}
    assert len(pilots) == 2
    assert len({summaries[p].study_id for p in pilots}) == 2
    assert all(p in PINNED for p in pilots)
    # Only vectorization's native grader returns a sentinel; the others raise.
    assert [t for t, spec in TASKS.items() if spec["failure_sentinel"] is not None] == ["vectorization"]
    for task_id in EXCLUDED:
        with pytest.raises(ValueError, match="excluded"):
            adapter.convert(task_id)
    with pytest.raises(ValueError, match="Unknown"):
        adapter.convert("not-a-task")
    with pytest.raises(ValueError, match="revision"):
        MLAgentBenchAdapter(SourceConfig(Path("/nonexistent"), Path("/nonexistent"),
                                         "0" * 40)).convert("vectorization")


def test_pilot_conversion_information_boundaries(adapter):
    episodes = [adapter.convert(task_id) for task_id in adapter.pilot_task_ids()]
    assert len({episode.study_id for episode in episodes}) == 2
    for episode in episodes:
        episode.evaluator.reference["baseline_receipt"] = "PRIVATE_SENTINEL_BASELINE_55671"
        exported = json.dumps(episode.actor_input())
        researcher = episode.researcher.model_dump_json()
        assert "PRIVATE_SENTINEL" not in exported and "PRIVATE_SENTINEL" not in researcher
        # Grader internals stay evaluator-private: the actor sees the output
        # contract in public.submission, never the scoring implementation.
        assert "get_score" not in exported and "get_score" not in researcher
        assert "scripts/eval.py" not in exported
        assert episode.review_status == "reviewed"
        assert episode.public.environment["budget_adaptation"]
        # Reviewed pilots ship non-empty grounded fact packs; regressions to an
        # empty pack must fail here, not pass vacuously.
        assert len(episode.researcher.facts) >= 3
        assert episode.public.researcher_topics
        assert all(fact.review_status == "reviewed" and fact.source.sha256
                   for fact in episode.researcher.facts)
        assert all(asset.visibility == "actor" for asset in episode.assets)
        assert episode.conversion["researcher_exclusive_information"] is False
        assert episode.conversion["fact_pack_sha256"]
    vectorization = next(e for e in episodes if e.source_task_id == "vectorization")
    assert [a.target_path for a in vectorization.assets] == ["train.py"]
    cifar = next(e for e in episodes if e.source_task_id == "cifar10")
    assert {a.target_path for a in cifar.assets} == {"train.py", "data"}
    assert cifar.public.environment["read_only_paths"] == ["data/*"]
    # cifar10 states the starter's CSV layout explicitly as a recorded adaptation;
    # vectorization keeps the native wording only.
    assert "index" in cifar.public.submission["format"]
    [adaptation] = cifar.conversion["public_contract_adaptations"]
    assert adaptation["field"] == "submission.format" and adaptation["sha256"]
    assert adaptation["source_path"].endswith("cifar10/env/train.py")
    assert "format" not in vectorization.public.submission
    assert vectorization.conversion["public_contract_adaptations"] == []
    for episode in episodes:
        exported = json.dumps(episode.actor_input())
        assert "index_col" not in exported and "eval.py" not in exported


def test_unprovisioned_tasks_declare_required_missing_data(adapter):
    for task_id in ("imdb", "babylm", "CLRS", "house-price"):
        episode = adapter.convert(task_id)
        placeholders = [a for a in episode.assets if a.id == "native-data-unprovisioned"]
        assert len(placeholders) == 1 and placeholders[0].required
        assert placeholders[0].acquisition
        assert episode.review_status == "automated"
        assert episode.researcher.facts == []
        assert episode.conversion["context_status"] == "no_permitted_guidance"


def test_source_tampering_fails_conversion_closed(adapter, tmp_path):
    repository = tmp_path / "repo"
    task = Path(BENCHMARKS) / "vectorization"
    shutil.copytree(adapter.source.repository / task, repository / task)
    altered = offline_adapter(repository, tmp_path / "assets")
    altered.convert("vectorization")  # Pristine copy converts.
    problem = repository / task / "scripts/research_problem.txt"
    problem.write_text(problem.read_text() + "\nUnreviewed edit.")
    # The same adapter instance must re-verify pins on every conversion.
    with pytest.raises(ValueError, match="re-curation"):
        altered.convert("vectorization")


def test_evaluate_status_matrix(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    with pytest.raises(ValueError, match="plan"):
        adapter.evaluate(episode, submission(episode, tmp_path / "a").model_copy(
            update={"stage": "plan"}))
    result = adapter.evaluate(episode, Submission(episode_id=episode.id))
    assert result.status == "missing_submission" and result.metrics == {}
    absent = Submission(episode_id=episode.id, artifacts={"train.py": str(tmp_path / "x.py")})
    (tmp_path / "x.py").write_text("pass\n")
    result = adapter.evaluate(episode, absent)
    assert result.status == "missing_submission"
    assert local_driver == []
    result = adapter.evaluate(episode, submission(episode, tmp_path / "good"))
    assert result.status == "scored"
    assert result.metrics == {"native_score": 0.5, "metric_name": "runtime_seconds",
                              "metric_direction": "lower"}
    assert result.details["scored"] == result.details["denominator"] == 1
    result = adapter.evaluate(episode, submission(episode, tmp_path / "bad", content="garbage"))
    assert result.status == "error" and result.metrics == {}
    assert result.details["native_sentinel"] == 1e10


def test_repeat_evaluation_of_one_submission_does_not_collide(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    sealed = submission(episode, tmp_path / "case")
    first = adapter.evaluate(episode, sealed)
    second = adapter.evaluate(episode, sealed)
    assert first.status == second.status == "scored"
    assert first.details["evaluator_directory"] != second.details["evaluator_directory"]


def test_unsafe_artifact_keys_are_rejected_without_side_effects(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    payload = tmp_path / "case/submitted_artifacts"
    payload.mkdir(parents=True)
    (payload / "evil.py").write_text("pass\n")
    for key in ("../evil.py", "/abs/evil.py"):
        with pytest.raises(ValueError, match="Unsafe"):
            adapter.evaluate(episode, Submission(episode_id=episode.id,
                                                 artifacts={key: str(payload / "evil.py")}))
    assert local_driver == []
    assert not list((tmp_path / "case").glob("mlagentbench_native_evaluation*"))


def test_modified_grader_is_rejected_before_execution(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    eval_file = repository / BENCHMARKS / "vectorization/scripts/eval.py"
    eval_file.write_text(eval_file.read_text() + "\n# unreviewed mutation\n")
    result = adapter.evaluate(episode, submission(episode, tmp_path / "case"))
    assert result.status == "error" and result.metrics == {}
    assert "re-curation" in result.errors[0]
    assert local_driver == []


def test_blocked_when_eval_cache_is_not_provisioned(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    episode.evaluator.reference["eval_cache"] = "data"
    result = adapter.evaluate(episode, submission(episode, tmp_path / "case"))
    assert result.status == "blocked" and result.metrics == {}
    assert local_driver == []


def test_sandbox_failures_map_to_error_status(tmp_path, monkeypatch):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    monkeypatch.setattr(MLAgentBenchAdapter, "_run_driver",
                        lambda self, work: {"exit_code": -9, "stdout": "", "stderr": "killed",
                                            "timeout": True, "duration": 1800.0})
    result = adapter.evaluate(episode, submission(episode, tmp_path / "killed"))
    assert result.status == "error"
    assert result.details["execution_receipt"]["timeout"] is True

    def unavailable(self, work):
        raise ValueError("Bubblewrap is required; host execution is disabled")
    monkeypatch.setattr(MLAgentBenchAdapter, "_run_driver", unavailable)
    result = adapter.evaluate(episode, submission(episode, tmp_path / "nobwrap"))
    assert result.status == "error"
    assert "sandbox unavailable" in result.errors[0].lower()


def test_derive_improvement_matches_native_arithmetic():
    lower = {"mean": 6.0, "metric": {"name": "runtime_seconds", "direction": "lower"}}
    exact = derive_improvement(lower, 5.4)
    assert exact["relative_improvement"] == pytest.approx(0.10)
    assert exact["success_10pct"] is False  # Native criterion is strictly greater.
    assert derive_improvement(lower, 5.3)["success_10pct"] is True
    higher = {"mean": 0.5, "metric": {"name": "test_accuracy", "direction": "higher"}}
    assert derive_improvement(higher, 0.56)["success_10pct"] is True
    assert derive_improvement(higher, 0.54)["success_10pct"] is False
    with pytest.raises(ValueError, match="zero baseline"):
        derive_improvement({"mean": 0, "metric": {"name": "x", "direction": "higher"}}, 1)


def test_prepare_assets_is_pinned_and_idempotent(tmp_path, monkeypatch):
    assets = tmp_path / "assets"
    adapter = offline_adapter(tmp_path / "repo", assets)
    root = assets / "cifar10"
    (root / "data/cifar-10-batches-py").mkdir(parents=True)
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda *a, **k: pytest.fail("Verified assets must not be re-downloaded"))
    receipt = {"archive_sha256": CIFAR10_ARCHIVE["sha256"], "url": CIFAR10_ARCHIVE["url"],
               "extracted": CIFAR10_ARCHIVE["extracted"]}
    (root / "acquisition.json").write_text(json.dumps(receipt))
    assert adapter.prepare_assets("cifar10") == [root / "data"]
    (root / "acquisition.json").write_text(json.dumps({**receipt, "archive_sha256": "0" * 64}))
    with pytest.raises(ValueError, match="different archive hash"):
        adapter.prepare_assets("cifar10")
    assert adapter.prepare_assets("vectorization") == []


def test_prepare_assets_rejects_corrupt_or_unsafe_archives(tmp_path, monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda *a, **k: pytest.fail("A present archive must not be re-downloaded"))
    corrupt_assets = tmp_path / "corrupt"
    adapter = offline_adapter(tmp_path / "repo", corrupt_assets)
    root = corrupt_assets / "cifar10"
    root.mkdir(parents=True)
    (root / "cifar-10-python.tar.gz").write_bytes(b"not a cifar archive")
    with pytest.raises(ValueError, match="archive hash mismatch"):
        adapter.prepare_assets("cifar10")
    # Defense in depth: even a hash-accepted archive may not traverse paths.
    unsafe_assets = tmp_path / "unsafe"
    unsafe_adapter = offline_adapter(tmp_path / "repo", unsafe_assets)
    unsafe_root = unsafe_assets / "cifar10"
    unsafe_root.mkdir(parents=True)
    archive = unsafe_root / "cifar-10-python.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        member = tarfile.TarInfo("../escape.txt")
        payload = b"escaped"
        member.size = len(payload)
        bundle.addfile(member, io.BytesIO(payload))
    monkeypatch.setitem(CIFAR10_ARCHIVE, "sha256", sha256(archive))
    with pytest.raises(ValueError, match="Unsafe archive member"):
        unsafe_adapter.prepare_assets("cifar10")
    assert not (unsafe_assets / "escape.txt").exists() and not (tmp_path / "escape.txt").exists()


def sandbox_available() -> bool:
    """Capability probe, not a presence check: honors PERSONASCIENCEBENCH_BWRAP
    and requires the exact Sandbox invocation to succeed on this host."""
    venv = Path(__file__).resolve().parents[1] / ".venv"
    if not (venv / "bin/python").is_file():
        return False
    if subprocess.run([str(venv / "bin/python"), "-c", "import pandas"],
                      capture_output=True).returncode != 0:
        return False
    try:
        from personasciencebench.runtime import Sandbox
        with tempfile.TemporaryDirectory(prefix="psb-mlab-probe-") as workspace:
            return Sandbox(Path(workspace), venv).execute("true", timeout_seconds=30)["exit_code"] == 0
    except Exception:
        return False


@pytest.mark.skipif(not sandbox_available(),
                    reason="A working Bubblewrap sandbox or a pandas-capable .venv is unavailable")
def test_native_oracle_controls_through_real_sandbox(adapter, tmp_path):
    """Infrastructure controls, never agent results: a well-formed submission scores
    its recorded value and a malformed one maps to the native failure sentinel."""
    episode = adapter.convert("vectorization")
    good = adapter.evaluate(episode, submission(episode, tmp_path / "good", content="0.5"))
    assert good.status == "scored" and good.metrics["native_score"] == 0.5
    bad = adapter.evaluate(episode, submission(episode, tmp_path / "bad", content="garbage"))
    assert bad.status == "error" and "sentinel" in bad.errors[0]


def test_measure_baseline_rejects_drifted_grader_before_any_execution(tmp_path, local_driver):
    repository = synthetic_source(tmp_path)
    adapter = offline_adapter(repository, tmp_path / "assets")
    episode = synthetic_episode(repository)
    eval_file = repository / BENCHMARKS / "vectorization/scripts/eval.py"
    eval_file.write_text(eval_file.read_text() + "\n# unreviewed mutation\n")
    with pytest.raises(ValueError, match="re-curation"):
        adapter.measure_baseline(episode, tmp_path / "baseline")
    assert not (tmp_path / "baseline").exists()
    assert local_driver == []


def load_pilot_script():
    import importlib.util
    path = Path(__file__).resolve().parents[1] / "scripts/mlagentbench_pilot.py"
    spec = importlib.util.spec_from_file_location("mlagentbench_pilot", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_summary_keeps_every_attempt_in_the_success_denominator(tmp_path):
    summarize = load_pilot_script().summarize
    run, baselines = tmp_path / "run", tmp_path / "baselines"
    cases = {
        "a": {"episode_id": "mlagentbench:vectorization", "benchmark": "mlagentbench",
              "status": "scored", "evaluation": {"status": "scored", "metrics": {"native_score": 0.5}}},
        "b": {"episode_id": "mlagentbench:cifar10", "benchmark": "mlagentbench",
              "status": "missing_submission"},
        "c": {"episode_id": "bixbench:bix-7-q2", "benchmark": "bixbench", "status": "scored",
              "evaluation": {"status": "scored", "metrics": {"grade": 1}}},
    }
    for name, result in cases.items():
        (run / name).mkdir(parents=True)
        (run / name / "result.json").write_text(json.dumps(result))
    (baselines / "vec").mkdir(parents=True)
    (baselines / "vec/baseline_receipt.json").write_text(json.dumps(
        {"episode_id": "mlagentbench:vectorization", "mean": 1.0,
         "metric": {"name": "runtime_seconds", "direction": "lower"}}))
    summary = summarize(run, baselines)
    assert summary["counts"] == {"attempted": 2, "submitted": 1, "evaluated": 1, "scored": 1}
    assert summary["success_10pct"] == {"successes": 1, "denominator": 2, "rate": 0.5,
                                        "missing_baselines": []}
    scored = next(row for row in summary["cases"] if row["status"] == "scored")
    assert scored["relative_improvement"] == pytest.approx(0.5) and scored["success_10pct"] is True
    (baselines / "vec/baseline_receipt.json").unlink()
    unresolved = summarize(run, baselines)["success_10pct"]
    assert unresolved["rate"] is None
    assert unresolved["missing_baselines"] == ["mlagentbench:vectorization"]
