"""Offline recovery tests: synthetic local fixtures, no network or listeners."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import recover_judges_v2 as repair
import recover_judges_amended as amended
from personasciencebench.inference import OpenRouterClient
from personasciencebench.openai_transport import ResponsesTransport
from personasciencebench.schema import EvaluationResult


@pytest.mark.parametrize("incomplete", [False, True])
def test_exact_prefix_and_amended_wire_receipts(tmp_path, monkeypatch, incomplete):
    repo, run, output = tmp_path / "repo", tmp_path / "run", tmp_path / "output"
    case = tmp_path / "case"
    (case / "controller").mkdir(parents=True)
    (run / "configs").mkdir(parents=True)
    monkeypatch.setattr(repair, "REPO", repo)
    monkeypatch.setattr(repair, "RUN", run)
    monkeypatch.setattr(repair, "OUT", output)
    spec = {"provider": "bedrock", "model": "us.openai.gpt-6-astra", "reasoning_effort": "low",
            "max_tokens": 4096, "unsupported_parameters": "omit_and_record"}
    repair.write(run / "configs/persona_off.shared.json", {"models": {"judge": spec}})
    episode = {"id": "discoverybench:synthetic", "benchmark": "discoverybench", "source_task_id": "synthetic",
               "study_id": "synthetic", "domain": "synthetic", "source_revision": "test",
               "public": {"question": "Synthetic question."},
               "evaluator": {"kind": "synthetic", "version": "synthetic-v1",
                             "config": {"native_helper_settings": {
                                 "variable_and_relation": {"max_tokens": 250},
                                 "decomposition_and_context": {"max_tokens": 4096}}}}}
    repair.write(case / "controller/episode.private.json", episode)
    repair.write(case / "controller/submission.json", {"episode_id": episode["id"], "answer": "Synthetic answer."})
    repair.write(case / "controller/submission_hashes.json", {})
    repair.write(case / "result.json", {"status": "error"})
    sent = []

    def make_transport(model, timeout):
        transport = ResponsesTransport(timeout)
        transport.provider = "bedrock"

        def send(request):
            sent.append(request)
            bad = incomplete and len(sent) == 2
            raw = {"id": f"synthetic-{len(sent)}", "model": spec["model"],
                   "status": "incomplete" if bad else "completed",
                   "incomplete_details": {"reason": "max_output_tokens"} if bad else None,
                   "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
                   "usage": {"input_tokens": 10, "output_tokens": 4096 if bad else 2,
                             "output_tokens_details": {"reasoning_tokens": 4090 if bad else 0}}}
            return raw, 0

        transport._send = send
        return transport

    cached_messages = [{"role": "user", "content": "Cached synthetic request."}]

    class Adapter:
        def evaluate(self, episode, submission, judge):
            try:
                assert judge.complete(cached_messages, settings={"max_tokens": 250}) == "ok"
                assert judge.complete([{"role": "user", "content": "Fresh small request."}],
                                      settings={"max_tokens": 250}) == "ok"
                assert judge.complete([{"role": "user", "content": "Fresh large request."}],
                                      settings={"max_tokens": 4096}) == "ok"
            except RuntimeError:
                return EvaluationResult(status="error", evaluator_version="synthetic")
            return EvaluationResult(status="scored", evaluator_version="synthetic", metrics={"final_score": 1})

    monkeypatch.setattr(repair, "load_adapter", lambda *args: Adapter())
    with patch("personasciencebench.bedrock_transport.transport", make_transport):
        cached = []
        client = OpenRouterClient(**spec, role="judge", supported_parameters=["max_tokens"], record=cached.append)
        client.complete(cached_messages, settings={"max_tokens": 250})
        repair.append(case / "controller/api_calls.private.jsonl", cached[0])
        row = {"case_path": str(case), "arm": "persona_off", "source": "discoverybench",
               "task_id": "synthetic", "attempt": 1}
        result = repair.one(row, {"judge": {"supported_parameters": ["max_tokens"]}},
                            {"remaining_native_judge_cap": 4096, "approval_source": "synthetic fixture"})
    destination = output / case.name / "persona_off"
    receipts = [json.loads(s) for s in (destination / "replay_receipts.jsonl").read_text().splitlines()]
    wires = [json.loads(s) for s in (destination / "wire_calls.private.jsonl").read_text().splitlines()]
    logs = [json.loads(s) for s in (destination / "api_calls.private.jsonl").read_text().splitlines()]
    assert result["reused_calls"] == 1
    assert result["fresh_calls"] == (1 if incomplete else 2)
    assert len(sent) == 1 + result["fresh_calls"]
    assert logs[0]["recovery_reused"] and logs[0]["response"]["_responses_request"]["max_output_tokens"] == 250
    for receipt, wire, log in zip(receipts[1:], wires, logs[1:], strict=True):
        assert receipt["transmitted_request_sha256"] == repair.object_hash(wire["request"])
        assert receipt["transmitted_max_output_tokens"] == 4096
        assert wire["request"] == log["response"]["_responses_request"]
    assert logs[1]["request"]["max_tokens"] == 250
    assert logs[1]["judge_budget_amendment"]["transmitted_cap"] == 4096
    assert result["evaluation"]["details"]["judge_recovery"]["caps_changed"]
    if incomplete:
        assert result["status"] == "judge_pending"
        assert wires[0]["response"]["status"] == "incomplete"
        assert logs[1]["usage"]["completion_tokens"] == 4096
    else:
        assert result["status"] == "recovered"
        assert "judge_budget_amendment" not in logs[2]


def test_short_prefix_cannot_be_scored():
    with pytest.raises(ValueError, match="entire cached prefix"):
        repair.assert_consumed(2, 3, "scored")


def test_amendment_does_not_mutate_native_request():
    request = {"max_output_tokens": 250, "reasoning": {"effort": "low"}}
    wire = repair.transmitted_request(request, {"remaining_native_judge_cap": 4096})
    wire["reasoning"]["effort"] = "synthetic"
    assert request == {"max_output_tokens": 250, "reasoning": {"effort": "low"}}


def test_approval_bound_to_exact_slots_and_files(tmp_path, monkeypatch):
    monkeypatch.setattr(amended, "ROOT", tmp_path)
    names = ["judge_cap_amendment_plan.json", "recover_judges_amended.py", "recover_judges_v2.py"]
    for name in names:
        (tmp_path / name).write_text("synthetic fixture")
    keys = {("discoverybench", "synthetic", "persona_off")}
    approval = {"approved": True, "approver": "Robert", "remaining_native_judge_cap": 4096,
                "source": "synthetic approval fixture", "received_at": "synthetic",
                "slots": [list(k) for k in sorted(keys)],
                "approved_file_sha256": {name: repair.digest((tmp_path / name).read_bytes()) for name in names}}
    amended.verify_approval(approval, keys)
    (tmp_path / names[0]).write_text("changed fixture")
    with pytest.raises(AssertionError):
        amended.verify_approval(approval, keys)
