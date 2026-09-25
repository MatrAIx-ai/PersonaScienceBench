"""Offline control contracts, optional source checks, and a scripted SDK smoke test."""

import importlib.util
import json
import socket
from pathlib import Path

import pytest

from expbench.budget import Budget
from expbench.mock import MockTransport, DEMO_DESIGN
from expbench.original_control import make_static_task, raw_task, render_original_judge
from expbench.runner import run_episode
from expbench.schema import Config, Design, Task, load_tasks

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def original_input():
    # Synthetic released-input shape, not a downloaded scientific task/reference.
    return {
        "question": "Does treatment A change the measured response?",
        "method": "Use matched conditions.\nRetain units (µM) and all observations.",
        "agent_instructions": "Report uncertainty; do not invent empirical results.",
        "design_complexity": {"private": {"constant": "REFERENCE_CANARY"}},
        "expected_outcome": "OUTCOME_CANARY",
    }


@pytest.fixture
def task():
    return Task(
        task_id="synthetic/paper/1", domain="synthetic fixture",
        public={"question": "Adapted public question", "context": "Adapted context",
                "documents": {"environment.md": "Synthetic environment; no experiment is run."}},
        researcher={"facts": [], "unspecified": ["wall-time budget"]},
        reference_design={"constant_variables": {"batch": "PRIVATE_CONSTANT"},
                          "independent_variables": {"treatment": "PRIVATE_INDEPENDENT"},
                          "dependent_variables": {"response": "PRIVATE_DEPENDENT"}},
        provenance={"source": "synthetic unit fixture"}, review_notes=["Fixture only."],
    )


def assert_static_fields(task, raw):
    before = task.model_dump()
    card = make_static_task(task, raw)
    assert task.model_dump() == before
    assert card.public.question == raw.get("question", raw.get("hypothesis"))
    assert json.loads(card.public.context) == {
        "method": raw["method"], "agent_instructions": raw.get("agent_instructions", ""),
    }
    assert "REFERENCE_CANARY" not in card.public.model_dump_json()
    assert "OUTCOME_CANARY" not in card.public.model_dump_json()
    assert card.provenance["control"] == "original-input-design-only-no-researcher"
    # Modifying the returned card must not mutate the source task's nested fields.
    card.public.documents.clear()
    card.review_notes.append("Changed copy")
    assert task.model_dump() == before


@pytest.mark.parametrize("question_key", ["question", "hypothesis"])
def test_original_fields_preserved_without_reference_leakage(task, original_input, question_key):
    original_input[question_key] = original_input.pop("question")
    assert_static_fields(task, original_input)


def test_missing_optional_agent_instructions(task, original_input):
    del original_input["agent_instructions"]
    assert_static_fields(task, original_input)


def test_raw_task_selects_exact_question_and_source_path(tmp_path, task, original_input):
    source = tmp_path / "synthetic/paper.json"
    source.parent.mkdir()
    source.write_text(json.dumps({"questions": [{"question": "Other question"}, original_input]}))
    raw, path = raw_task(task.task_id, root=tmp_path)
    assert raw == original_input
    assert path == source


def assert_original_rendering(template, raw):
    design = Design.model_validate(DEMO_DESIGN)
    rendered = render_original_judge(template, raw, design)
    assert rendered == template.format(
        design_gt=raw["design_complexity"], conclusion_gt=raw["expected_outcome"],
        conclusion_output="", design_output=json.dumps(design.model_dump(), ensure_ascii=False),
    )
    assert "approved_researcher_context" not in rendered
    assert "REFERENCE_CANARY" in rendered and "OUTCOME_CANARY" in rendered


def test_original_judge_uses_raw_reference_and_exact_template(original_input):
    template = (
        "Design reference:\n{design_gt}\nConclusion reference:\n{conclusion_gt}\n"
        "Design output:\n{design_output}\nConclusion output:\n{conclusion_output}\n"
        'Literal JSON braces: {{"fixture": true}}\n'
    )
    assert_original_rendering(template, original_input)


@pytest.fixture
def source_original_input():
    path = ROOT / "data/design_pilot/tasks.jsonl"
    if not path.is_file():
        pytest.skip("Source-backed control test requires prepared EXP-Bench design_pilot task cards")
    task = load_tasks(path)[0]
    conference, paper, _ = task.task_id.split("/")
    source = ROOT / "data/exp_bench/raw/upstream/tasks" / conference / (paper + ".json")
    if not source.is_file():
        pytest.skip("Source-backed control test requires the pinned EXP-Bench raw task")
    raw, _ = raw_task(task.task_id)
    raw["design_complexity"] = {"private": "REFERENCE_CANARY"}
    raw["expected_outcome"] = "OUTCOME_CANARY"
    return task, raw


def test_source_original_fields_preserved_without_reference_leakage(source_original_input):
    assert_static_fields(*source_original_input)


def test_source_original_judge_uses_exact_template(original_input):
    path = ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_prompt.txt"
    if not path.is_file():
        pytest.skip("Source-backed judge test requires the pinned EXP-Bench original judge prompt")
    assert_original_rendering(path.read_text(), original_input)


def test_static_actor_has_no_researcher_tool_or_calls(tmp_path, monkeypatch, task, original_input):
    try:
        sdk_available = importlib.util.find_spec("openhands.sdk") is not None
    except ModuleNotFoundError:
        sdk_available = False
    if not sdk_available:
        pytest.skip("EXP-Bench SDK smoke test requires the actor extra (covered by actor-smoke CI)")

    def forbidden(*args, **kwargs):
        raise AssertionError("No network in tests")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    from expbench.actor import _SDK_PERSISTENCE
    from openhands.sdk.llm.llm_profile_store import LLMProfileStore

    assert LLMProfileStore().base_dir.is_relative_to(Path(_SDK_PERSISTENCE.name))
    config = Config.load(ROOT / "configs/expbench/original-input-o3mini.toml")
    transport = MockTransport()
    result = run_episode(make_static_task(task, original_input), config, transport,
                         Budget(None), tmp_path / "run")
    assert result["status"] == "completed", result
    assert result["actor_calls"] == 2
    assert result["researcher_questions"] == 0
    assert transport.counts["researcher"] == 0
    actor = [payload for role, payload in transport.requests if role == "actor"]
    for request in actor:
        assert {t["function"]["name"] for t in request["tools"]} == {"read_context", "submit_design"}
        assert "There is no researcher to interview" in request["messages"][0]["content"]
