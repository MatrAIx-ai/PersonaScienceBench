import json
import socket
from pathlib import Path

from expbench.budget import Budget
from expbench.mock import MockTransport, DEMO_DESIGN
from expbench.original_control import make_static_task, raw_task, render_original_judge
from expbench.runner import run_episode
from expbench.schema import Config, Design, load_tasks

ROOT = Path(__file__).resolve().parents[2]


def test_original_fields_preserved_without_reference_leakage():
    task = load_tasks(ROOT / "data/design_pilot/tasks.jsonl")[0]
    raw, _ = raw_task(task.task_id)
    raw["design_complexity"] = {"private": "REFERENCE_CANARY"}
    raw["expected_outcome"] = "OUTCOME_CANARY"
    card = make_static_task(task, raw)
    context = json.loads(card.public.context)
    assert card.public.question == raw["question"]
    assert context == {"method": raw["method"], "agent_instructions": raw["agent_instructions"]}
    assert "REFERENCE_CANARY" not in card.public.model_dump_json()
    assert "OUTCOME_CANARY" not in card.public.model_dump_json()


def test_original_judge_uses_raw_reference_and_exact_template():
    template = (ROOT / "data/exp_bench/raw/upstream/prompts/eval_judge_prompt.txt").read_text()
    raw = {"design_complexity": {"wrapper": {"a": "ORIGINAL_REFERENCE"}},
           "expected_outcome": "ORIGINAL_OUTCOME"}
    design = Design.model_validate(DEMO_DESIGN)
    rendered = render_original_judge(template, raw, design)
    assert rendered == template.format(design_gt=raw["design_complexity"],
        conclusion_gt=raw["expected_outcome"], conclusion_output="",
        design_output=json.dumps(design.model_dump(), ensure_ascii=False))
    assert "approved_researcher_context" not in rendered
    assert "ORIGINAL_REFERENCE" in rendered and "ORIGINAL_OUTCOME" in rendered


def test_static_actor_has_no_researcher_tool_or_calls(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("No network in tests")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    from expbench.actor import _SDK_PERSISTENCE
    from openhands.sdk.llm.llm_profile_store import LLMProfileStore
    assert LLMProfileStore().base_dir.is_relative_to(Path(_SDK_PERSISTENCE.name))
    config = Config.load(ROOT / "configs/expbench/original-input-o3mini.toml")
    task = load_tasks(ROOT / "data/design_pilot/tasks.jsonl")[0]
    raw, _ = raw_task(task.task_id)
    transport = MockTransport()
    result = run_episode(make_static_task(task, raw), config, transport,
                         Budget(None), tmp_path / "run")
    assert result["status"] == "completed"
    assert result["actor_calls"] == 2
    assert result["researcher_questions"] == 0
    assert transport.counts["researcher"] == 0
    actor = [payload for role, payload in transport.requests if role == "actor"]
    for request in actor:
        assert {t["function"]["name"] for t in request["tools"]} == {"read_context", "submit_design"}
        assert "There is no researcher to interview" in request["messages"][0]["content"]
