"""Offline conversion/boundary/native-grader checks; no model or analysis runs."""

import json
import os
from pathlib import Path
import shutil

import pytest

from personasciencebench.adapters.base import SourceConfig, sha256
from personasciencebench.adapters.bixbench import (
    BixBenchAdapter, CAPSULES, DATASET_REVISION, PILOTS, REPOSITORY_REVISION,
)
from personasciencebench.schema import Submission


SOURCE_ROOT = Path(os.environ.get("PERSONASCIENCEBENCH_SOURCE_ROOT",
                                  Path(__file__).resolve().parents[2] / "benchmarks"))


@pytest.fixture
def adapter():
    source = SourceConfig(
        SOURCE_ROOT / "bixbench", SOURCE_ROOT / "_assets/bixbench",
        REPOSITORY_REVISION, DATASET_REVISION,
    )
    if not (source.assets / "BixBench.jsonl").exists():
        pytest.skip("Pinned external BixBench annotations are not acquired")
    return BixBenchAdapter(source)


class OfflineJudge:
    def __init__(self, response="<grade>correct</grade>"):
        self.response = response
        self.calls = []

    def complete(self, messages, *, json_mode=False, settings=None):
        self.calls.append(messages)
        return self.response


def submission(episode, **updates):
    return Submission(
        episode_id=episode.id, answer="Synthetic candidate for a grader-interface check.",
        payload={"executed_analysis": True}, artifacts={"analysis": "synthetic-analysis.ipynb"},
    ).model_copy(update=updates)


def test_reviewed_inventory_and_information_boundaries(adapter):
    assert len(adapter.enumerate_tasks()) == 205
    episodes = [adapter.convert(task_id) for task_id in adapter.pilot_task_ids()]
    assert len(episodes) == 2
    assert len({episode.study_id for episode in episodes}) == 2
    for episode in episodes:
        # Insert a sentinel only in evaluator-private storage, then exercise the
        # actual shared actor-export path rather than serializing the episode.
        episode.evaluator.reference["target"] = "PRIVATE_SENTINEL_GOLD_87135"
        exported = json.dumps(episode.actor_input())
        assert "PRIVATE_SENTINEL" not in exported
        assert "PRIVATE_SENTINEL" not in episode.researcher.model_dump_json()
        assert "CapsuleNotebook" not in exported
        assert "BixBench.jsonl" not in exported
        assert '"hypothesis":' not in episode.researcher.model_dump_json()
        assert all(fact.review_status == "reviewed" and fact.source.sha256
                   for fact in episode.researcher.facts)
        assert all(asset.visibility == "actor" and not asset.source_path.endswith(".ipynb")
                   for asset in episode.assets)
    with pytest.raises(ValueError, match="two reviewed"):
        adapter.convert("bix-1-q1")


def test_source_tampering_is_rejected(adapter, tmp_path):
    path = tmp_path / "BixBench.jsonl"
    path.write_text((adapter.source.assets / "BixBench.jsonl").read_text() + "\n")
    altered = BixBenchAdapter(SourceConfig(
        adapter.source.repository, tmp_path, REPOSITORY_REVISION, DATASET_REVISION,
    ))
    with pytest.raises(ValueError, match="reviewed dataset"):
        altered.convert("bix-10-q2")


def test_exact_member_extraction_preserves_archive_excludes_notebooks(adapter, tmp_path):
    capsule = PILOTS["bix-8-q2"]
    name = f"CapsuleFolder-{capsule}.zip"
    archive = adapter.source.assets / name
    if not archive.exists():
        pytest.skip("Selected capsule has not been acquired")
    shutil.copyfile(archive, tmp_path / name)
    isolated = BixBenchAdapter(SourceConfig(
        adapter.source.repository, tmp_path, REPOSITORY_REVISION, DATASET_REVISION,
    ))
    paths = isolated.prepare_assets("bix-8-q2")
    assert {path.name for path in paths} == set(CAPSULES[capsule]["files"])
    assert not list((tmp_path / "prepared").rglob("*.ipynb"))
    assert sha256(tmp_path / name) == CAPSULES[capsule]["archive_sha256"]
    for path in paths:
        assert sha256(path) == CAPSULES[capsule]["files"][path.name]
    (tmp_path / name).write_bytes(b"invalid capsule")
    with pytest.raises(ValueError, match="archive hash"):
        isolated.prepare_assets("bix-8-q2")


@pytest.mark.parametrize("response, expected", [
    ("<grade>correct</grade>", 1),
    ("<grade>incorrect</grade>", 0),
    ("<grade>refused</grade>", 0),
    ("malformed native response", 0),
])
def test_native_range_grader_is_llm_based_and_keeps_native_parser(adapter, response, expected):
    episode = adapter.convert("bix-8-q2")
    judge = OfflineJudge(response)
    result = adapter.evaluate(episode, submission(episode), judge)
    assert result.status == "scored"
    assert result.metrics["grade"] == expected
    assert result.metrics["refusal"] is False  # Native parser loses refusal category.
    assert len(judge.calls) == 1
    # Native OpenEndedGrader supplies its generic template even in range mode.
    assert "Target Answer:" in judge.calls[0][0]["content"]
    assert "Target Range:" not in judge.calls[0][0]["content"]
    assert result.details["denominator"] == result.details["scored"] == 1


def test_missing_execution_or_judge_remains_missing_or_blocked(adapter):
    episode = adapter.convert("bix-10-q2")
    judge = OfflineJudge()
    result = adapter.evaluate(episode, submission(episode, answer=""), judge)
    assert result.status == "missing_submission" and result.metrics == {}
    assert result.details["denominator"] == 1 and result.details["scored"] == 0
    result = adapter.evaluate(episode, submission(episode, payload={}), judge)
    assert result.status == "blocked" and result.metrics == {}
    result = adapter.evaluate(episode, submission(episode))
    assert result.status == "blocked" and result.metrics == {}
    assert judge.calls == []
    with pytest.raises(ValueError, match="plan"):
        adapter.evaluate(episode, submission(episode, stage="plan"), judge)


def test_native_dependency_bridge_rejects_modified_grader(adapter, tmp_path):
    source = tmp_path / "bixbench"
    source.mkdir()
    for name in ("graders.py", "prompts.py"):
        shutil.copyfile(adapter.source.repository / "bixbench" / name, source / name)
    with (source / "graders.py").open("a") as stream:
        stream.write("\n# unreviewed mutation\n")
    altered = BixBenchAdapter(SourceConfig(
        tmp_path, adapter.source.assets, REPOSITORY_REVISION, DATASET_REVISION,
    ))
    episode = altered.convert("bix-10-q2")
    judge = OfflineJudge()
    result = altered.evaluate(episode, submission(episode), judge)
    assert result.status == "error" and result.metrics == {}
    assert judge.calls == []


def test_provider_errors_do_not_expose_reference_content(adapter):
    class FailingJudge:
        def complete(self, messages, **kwargs):
            raise ValueError("PRIVATE_REF_OR_PROVIDER_SECRET: " + str(messages))
    episode = adapter.convert("bix-10-q2")
    result = adapter.evaluate(episode, submission(episode), FailingJudge())
    assert result.status == "error" and result.metrics == {}
    assert "PRIVATE_REF_OR_PROVIDER_SECRET" not in result.model_dump_json()
    assert result.details["denominator"] == 1 and result.details["scored"] == 0


def test_missing_inputs_block_scoring_before_any_judge_call(adapter, tmp_path):
    episode = adapter.convert("bix-10-q2")
    episode.assets[0].source_path = str(tmp_path / "not-provisioned.csv")
    judge = OfflineJudge()
    result = adapter.evaluate(episode, submission(episode), judge)
    assert result.status == "blocked" and result.metrics == {}
    assert judge.calls == []
