"""Scripted model responses for SDK/tool integration checks, never real scores."""

import copy
import json
from collections import Counter


class RealisticMock:
    mock = True

    def __init__(self):
        self.counts, self.requests = Counter(), []

    def complete(self, role, payload):
        self.requests.append((role, copy.deepcopy(payload)))
        index = self.counts[role]
        self.counts[role] += 1
        message = {"role": "assistant", "content": None}
        reason = "stop"
        if role == "actor":
            context = json.loads(next(m["content"] for m in payload["messages"] if m["role"] == "user"))
            actions = [("inspect_repository", {"path": "."}),
                       ("execute_check", {"command": "python3 -c 'print(2 + 2)'", "timeout_seconds": 5})]
            if context["researcher_topics"]:
                actions.append(("ask_researcher", {"topic": context["researcher_topics"][0],
                    "question": "What is known about this part of the existing setup?"}))
            actions.append(("submit_plan", {"plan": "Synthetic plan for plumbing verification only. Compare the alternatives in matched conditions, measure outcomes, and report uncertainty and feasibility limits."}))
            if context["continue_after_initial_plan"]:
                actions.extend([
                    ("execute_check", {"command": "python3 -c 'print(3 + 3)'", "timeout_seconds": 5}),
                    ("finish_experiment", {"design": "Synthetic final plan. The small arithmetic check does not implement the scientific experiment.",
                        "conclusion": "Only a smoke test was executed. The research question remains unanswered.",
                        "reproduction_command": "python3 -c 'print(3 + 3)'"})])
            name, arguments = actions[index]
            message["tool_calls"] = [{"id": f"realistic-mock-{index}", "type": "function",
                "function": {"name": name, "arguments": json.dumps(arguments)}}]
            reason = "tool_calls"
        elif role == "researcher":
            system = payload["messages"][0]["content"]
            data = json.loads(system[system.index('{"research_question"'):])
            fact = data["available_fact"]
            message["content"] = json.dumps({"answer": fact["text"], "fact_ids": [fact["id"]]})
        else:
            system = payload["messages"][0]["content"]
            if system.startswith("Inspect the log"):
                output = {"paper_access": False, "git_operations": False,
                          "faked_or_nonexperimental_data": False,
                          "setup_monitor_comprehensive_reason": "Synthetic monitor fixture."}
            else:
                output = {"design_score": 50, "design_evaluation_explanation": "Synthetic fixture.",
                          "design_error_analysis": "No scientific evaluation.", "conclusion_score": "incorrect",
                          "conclusion_evaluation_explanation": "Synthetic fixture.", "conclusion_error_analysis": "No experiment."}
            message["content"] = json.dumps(output)
        return {"id": f"realistic-mock-{role}-{index}", "object": "chat.completion", "created": 0,
                "model": payload["model"], "provider": "offline-mock",
                "choices": [{"index": 0, "message": message, "finish_reason": reason}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "cost": 0.0}}

    def close(self):
        pass
