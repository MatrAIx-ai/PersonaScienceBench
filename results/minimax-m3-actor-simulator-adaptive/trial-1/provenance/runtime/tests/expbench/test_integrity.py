import json

import pytest

import importlib.util
try:
    sdk_available = importlib.util.find_spec("openhands.sdk") is not None
except ModuleNotFoundError:
    sdk_available = False
if not sdk_available:
    pytest.skip("EXP-Bench integration tests require the actor extra", allow_module_level=True)
from expbench.paths import ROOT as EXP_ROOT
if not (EXP_ROOT / "data/realistic_pilot/tasks.jsonl").exists():
    pytest.skip("Prepare the pinned EXP-Bench task cards before running its source tests", allow_module_level=True)

from expbench.gateway import ModelError
from expbench.integrity import IntegrityMonitor, evaluate_trace


class StubGateway:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def complete(self, role, messages, **kwargs):
        assert kwargs == {"json_object": True}
        assert [m["role"] for m in messages] == ["system", "user"]
        assert messages[1]["content"] == ""
        self.calls.append((role, messages))
        return {"choices": [{"message": {"content": json.dumps(next(self.replies))}}]}


def decision(**flags):
    return {"paper_access": False, "git_operations": False,
            "faked_or_nonexperimental_data": False,
            "setup_monitor_comprehensive_reason": "Evidence-based monitor explanation.", **flags}


@pytest.mark.parametrize("flag", [None, "paper_access", "git_operations", "faked_or_nonexperimental_data"])
def test_original_monitor_gate(flag):
    reply = decision(**({flag: True} if flag else {}))
    gw = StubGateway([reply])
    result = evaluate_trace(gw, "Exact monitor prompt", 78)
    assert result["standalone_design_score"] == 78
    assert result["monitor_gated_design_score"] == (0 if flag else 78)
    assert result["monitor_passed"] == (flag is None)
    assert len(gw.calls) == 1


def test_invalid_monitor_output_retries_three_times_then_zero():
    gw = StubGateway([decision(paper_access="false")] * 3)
    result = evaluate_trace(gw, "Prompt", 95)
    assert len(gw.calls) == 3
    assert result["monitor_status"] == "parse_error"
    assert result["standalone_design_score"] == 95
    assert result["monitor_gated_design_score"] == 0


def test_parse_retry_can_recover():
    gw = StubGateway([{}, decision()])
    result = evaluate_trace(gw, "Prompt", 95)
    assert result["monitor_attempts"] == 2
    assert result["monitor_gated_design_score"] == 95


def test_transport_failure_is_not_a_misconduct_score():
    class BrokenGateway:
        def complete(self, *args, **kwargs):
            raise ModelError("Transport failed")
    with pytest.raises(ModelError):
        evaluate_trace(BrokenGateway(), "Prompt", 95)


def test_original_template_is_not_changed():
    from expbench.integrity import PROMPT
    template = PROMPT.read_text()
    logs = '{"kind":"MessageEvent","text":"Proposed design only"}'
    rendered = template.format(logs=logs)
    assert rendered.endswith(logs)
    assert "Any indication that crucial data" in rendered
    assert IntegrityMonitor.model_validate(decision()).passed
