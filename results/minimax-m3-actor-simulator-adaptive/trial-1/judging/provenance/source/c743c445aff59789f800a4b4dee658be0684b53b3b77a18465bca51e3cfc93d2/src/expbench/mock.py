"""Scripted API responses only; the actor still runs in the real OpenHands SDK.

Synthetic designs and grades deliberately do not use hidden reference designs.
This checks plumbing, not scientific quality or model performance.
"""

import copy
import json
from collections import Counter


DEMO_DESIGN = {
    "objective": "Compare the requested alternatives under controlled experimental conditions.",
    "constant_variables": ["Use consistent data splits and compute conditions."],
    "independent_variables": ["The alternatives named in the public research question."],
    "dependent_variables": ["Measure the outcomes requested in the public research question."],
    "procedure": "This is a synthetic smoke-test design. Establish matched conditions, perform repeated evaluations with documented seeds, and retain all configurations.",
    "analysis_plan": "Compare matched outcomes and report uncertainty across repeated runs.",
    "assumptions": ["Smoke-test output only; not a scientifically validated protocol."],
}


class MockTransport:
    mock = True

    def __init__(self):
        self.counts = Counter()
        self.requests = []

    def complete(self, role, payload):
        self.requests.append((role, copy.deepcopy(payload)))
        index = self.counts[role]
        self.counts[role] += 1
        message = {"role": "assistant", "content": None}
        reason = "stop"
        if role == "actor":
            actions = [
                ("read_context", {"name": "environment.md"}),
                ("ask_researcher", {"question": "What is the intended experimental setup?"}),
                ("ask_researcher", {"question": "Is a wall-time budget specified? Please retain your previous answer."}),
                ("submit_design", {"design": DEMO_DESIGN}),
            ]
            if not any(t["function"]["name"] == "ask_researcher" for t in payload["tools"]):
                actions = [actions[0], actions[-1]]
            if index >= len(actions):
                raise AssertionError("Actor continued after final design submission")
            name, arguments = actions[index]
            message["tool_calls"] = [{"id": f"mock_call_{index}", "type": "function",
                                      "function": {"name": name, "arguments": json.dumps(arguments)}}]
            reason = "tool_calls"
        elif role == "researcher":
            # The system prompt ends in one JSON object; no judge context is used.
            system = payload["messages"][0]["content"]
            context = json.loads(system[system.index('{"research_question"'):])
            fact = context["approved_context"]["facts"][0]
            reply = {"answer": fact["text"], "fact_ids": [fact["id"]]} if index == 0 else {
                "answer": "Not specified.", "fact_ids": [],
            }
            message["content"] = json.dumps(reply)
        else:
            message["content"] = json.dumps({
                "design_score": 50,
                "design_evaluation_explanation": "Synthetic fixture score; NOT a benchmark result.",
                "design_error_analysis": "No scientific evaluation was performed in mock mode.",
            })
        return {"id": f"mock-{role}-{index}", "object": "chat.completion",
                "created": 0, "model": payload["model"], "provider": "offline-mock",
                "choices": [{"index": 0, "message": message, "finish_reason": reason}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "cost": 0.0}}

    def close(self):
        pass
