"""Offline conversion and native-grader contract checks; no model calls."""

import json
import os
from pathlib import Path

import pytest

from personasciencebench.adapters.base import SourceConfig
from personasciencebench.adapters.discoverybench import DiscoveryBenchAdapter, SOURCE_REVISION
from personasciencebench.schema import Submission


SOURCE = Path(os.environ.get("PERSONASCIENCEBENCH_SOURCE_ROOT",
                             Path(__file__).resolve().parents[2] / "benchmarks")) / "discoverybench"


@pytest.fixture
def adapter():
    if not SOURCE.is_dir():
        pytest.skip("Pinned external DiscoveryBench checkout is not provisioned")
    return DiscoveryBenchAdapter(SourceConfig(SOURCE, SOURCE, SOURCE_REVISION))


class ScriptedJudge:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def complete(self, messages, *, json_mode=False, settings=None):
        self.calls.append({"messages": messages, "json_mode": json_mode, "settings": settings})
        value = next(self.responses)
        return value if isinstance(value, str) else json.dumps(value)


def test_inventory_has_unique_composite_ids_and_two_distinct_pilots(adapter):
    inventory = adapter.enumerate_tasks()
    assert len(inventory) == 264
    assert len({task.id for task in inventory}) == len(inventory)
    pilots = [adapter.convert(task) for task in adapter.pilot_task_ids()]
    assert len(pilots) == len({episode.study_id for episode in pilots}) == 2
    assert {episode.domain for episode in pilots} == {"engineering", "sociology"}


def test_exports_keep_references_private_and_knowledge_qualified(adapter):
    for task_id in adapter.pilot_task_ids():
        episode = adapter.convert(task_id)
        public = json.dumps(episode.actor_input())
        researcher = episode.researcher.model_dump_json()
        reference = episode.evaluator.reference["gold_hypothesis"]
        assert reference not in public
        assert reference not in researcher
        for field in ("true_hypothesis", "workflow_tags", "answer_key", "intermediate"):
            assert field not in public
            assert field not in researcher
        metadata_path = SOURCE / episode.conversion["metadata_path"]
        metadata = json.loads(metadata_path.read_text())
        assert episode.researcher.facts[0].text == metadata["domain_knowledge"].strip()
        assert metadata["queries"][0][0]["question"] == episode.public.question
        assert episode.evaluator.reference["gold_workflow"] is None
        assert episode.track == "full_workflow"
        assert all(asset.target_path.startswith("data/") for asset in episode.assets)
    engineering = adapter.convert(adapter.pilot_task_ids()[0])
    assert "may" in engineering.researcher.facts[0].text
    assert "could" in engineering.researcher.facts[0].text


def test_automated_nonpilot_conversion_preserves_private_reference_boundary(adapter):
    from personasciencebench.adapters.discoverybench import REVIEWED_TASKS
    task = next(task.id for task in adapter.enumerate_tasks() if task.id not in REVIEWED_TASKS)
    episode = adapter.convert(task)
    assert episode.evaluator.reference['gold_hypothesis']
    public = json.dumps(episode.actor_input())
    researcher = episode.researcher.model_dump_json()
    assert episode.evaluator.reference['gold_hypothesis'] not in public
    assert episode.evaluator.reference['gold_hypothesis'] not in researcher
    metadata = json.loads((SOURCE / episode.conversion['metadata_path']).read_text())
    assert episode.public.question == metadata['queries'][episode.conversion['query_group']][0]['question']
    for fact in episode.researcher.facts:
        assert fact.text in metadata['domain_knowledge']


def test_changed_reviewed_metadata_fails_closed(adapter, tmp_path):
    task = adapter.pilot_task_ids()[0]
    original = adapter.convert(task)
    relative = original.conversion["metadata_path"]
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    metadata = json.loads((SOURCE / relative).read_text())
    metadata["queries"][0][0]["question"] += " Injected hidden answer."
    path.write_text(json.dumps(metadata))
    changed = DiscoveryBenchAdapter(SourceConfig(tmp_path, tmp_path, SOURCE_REVISION))
    with pytest.raises(ValueError, match="re-curation"):
        changed.convert(task)


def test_missing_submissions_plans_and_missing_judge_are_not_scores(adapter):
    episode = adapter.convert(adapter.pilot_task_ids()[0])
    missing = adapter.evaluate(episode, Submission(episode_id=episode.id))
    assert missing.status == "missing_submission" and missing.metrics == {}
    plan = adapter.evaluate(episode, Submission(episode_id=episode.id, stage="plan", answer="A plan."))
    assert plan.status == "error" and plan.metrics == {}
    no_judge = adapter.evaluate(episode, Submission(episode_id=episode.id, answer="A finding."))
    assert no_judge.status == "blocked" and no_judge.metrics == {}


def test_native_context_denominator_relation_and_settings_are_preserved(adapter, capsys):
    episode = adapter.convert(adapter.pilot_task_ids()[1])
    judge = ScriptedJudge([
        {"sub_hypo": [{"text": "gold1", "context": "first"}, {"text": "gold2", "context": "second"}]},
        {"sub_hypo": [{"text": "pred1", "context": "first"}, {"text": "pred2", "context": "unmatched"}]},
        {"match": False},
        {"sizeA": 2, "sizeB": 2, "intersection": 1, "explanation": "One shared variable"},
        {"answer": "B) similar but general than HypoA", "explanation": "More general"},
    ])
    submission = Submission(episode_id=episode.id, answer="Complete submitted hypothesis", payload={"workflow": "Executed analysis"})
    result = adapter.evaluate(episode, submission, judge)
    assert result.status == "scored", result.errors
    # One of two gold contexts covered; one unmatched prediction stays in mean:
    # recall .5 * ((variable F1 .5 * relation .5 + unmatched 0) / 2) = .0625.
    assert result.metrics == {"final_score": 0.0625, "recall_context": 0.5, "mean_accuracy_score": 0.125}
    assert result.details["denominator"] == 1
    assert judge.calls[0]["settings"]["temperature"] == 1.0
    assert judge.calls[0]["settings"]["max_tokens"] == 4096
    assert judge.calls[3]["settings"]["temperature"] == 0
    assert judge.calls[3]["settings"]["max_tokens"] == 250
    assert judge.calls[3]["json_mode"] is True
    # Upstream passes complete hypotheses here, not extracted pair texts.
    assert "Complete submitted hypothesis" in judge.calls[3]["messages"][-1]["content"]
    assert capsys.readouterr().out == ""


def test_malformed_judge_reply_is_error_and_no_retry(adapter):
    episode = adapter.convert(adapter.pilot_task_ids()[0])
    judge = ScriptedJudge(["not JSON"])
    result = adapter.evaluate(episode, Submission(episode_id=episode.id, answer="A finding."), judge)
    assert result.status == "error" and result.metrics == {}
    assert len(judge.calls) == 1


def test_missing_dataset_is_reported_before_judging(adapter, tmp_path):
    episode = adapter.convert(adapter.pilot_task_ids()[0])
    for asset in episode.assets:
        asset.source_path = str(tmp_path / Path(asset.source_path).name)
    missing = DiscoveryBenchAdapter(SourceConfig(tmp_path, tmp_path, SOURCE_REVISION))
    judge = ScriptedJudge([])
    result = missing.evaluate(episode, Submission(episode_id=episode.id, answer="A finding."), judge)
    assert result.status == "blocked"
    assert "Missing required source dataset" in result.errors[0]
    assert judge.calls == []


def test_changed_native_evaluator_is_rejected_before_judging(adapter, tmp_path):
    episode = adapter.convert(adapter.pilot_task_ids()[0])
    target = tmp_path / "eval/new_eval.py"
    target.parent.mkdir(parents=True)
    target.write_text((SOURCE / "eval/new_eval.py").read_text() + "\n# changed\n")
    changed = DiscoveryBenchAdapter(SourceConfig(tmp_path, tmp_path, SOURCE_REVISION))
    judge = ScriptedJudge([])
    result = changed.evaluate(episode, Submission(episode_id=episode.id, answer="A finding."), judge)
    assert result.status == "error"
    assert "Native evaluator source changed" in result.errors[0]
    assert judge.calls == []
