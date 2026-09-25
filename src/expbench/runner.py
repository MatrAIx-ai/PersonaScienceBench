import hashlib
import json
from pathlib import Path

from expbench import prompts
from expbench.artifacts import write_json
from expbench.budget import Budget, BudgetExceeded, Ledger
from expbench.gateway import Gateway, ModelError, parse_structured
from expbench.researcher import Researcher
from expbench.schema import Config, Design, Grade, Task


class Episode:
    def __init__(self, task: Task, config: Config, transport, budget: Budget, output: Path):
        if config.collaboration is not None:
            raise ValueError("Use expbench-realistic in interactive design-only mode for shared collaboration")
        self.task, self.config, self.output = task, config, output
        output.mkdir(parents=True, exist_ok=False)
        self.gateway = Gateway(transport, {role: getattr(config.models, role)
                                          for role in ("actor", "researcher", "judge")},
                               Ledger(budget, Budget(config.limits.episode_usd)),
                               output / "api_calls.jsonl")
        self.researcher = Researcher(task.researcher, task.public.question, self.gateway,
                                    config.limits.researcher_questions,
                                    output / "researcher_history.json")
        self.design = None
        self.failure = None
        self.actor_calls = 0
        self.actor_error = None
        self.actor_status = None
        write_json(output / "task_snapshot.private.json", task.model_dump())
        write_json(output / "public_task.json", task.public.model_dump())

    def submit(self, design: Design):
        if self.design is not None:
            raise ModelError("Design already submitted")
        self.design = design
        write_json(self.output / "design.json", design.model_dump())

    def grade(self):
        payload = {"task_context": self.task.public.model_dump(),
                   "approved_researcher_context": self.task.researcher.model_dump(),
                   "design_ground_truth": self.task.reference_design.model_dump(),
                   "design_output": self.design.model_dump()}
        response = self.gateway.complete("judge", [
            {"role": "system", "content": prompts.JUDGE},
            {"role": "user", "content": json.dumps(payload)},
        ], schema=Grade.model_json_schema())
        grade = parse_structured(response, Grade)
        write_json(self.output / "grade.json", {
            "mock": self.gateway.transport.mock,
            "rubric": "exp-bench-variable-coverage-design-only-v2",
            **grade.model_dump(),
        })
        return grade


def run_episode(task, config, transport, budget, output, saved_design=None):
    episode = Episode(task, config, transport, budget, output)
    status, grade, error = "running", None, None
    phase = "actor"
    try:
        if saved_design is None:
            from expbench.actor import run_actor
            run_actor(episode)
        else:
            episode.submit(saved_design)
        if episode.failure:
            raise episode.failure
        if episode.design is None:
            status = "no_submission"
        else:
            phase = "judge"
            grade = episode.grade()
            status = "completed"
    except Exception as exc:
        # SDK may wrap the original exception. Do not log arbitrary exception
        # text, which could contain request internals or secrets.
        exc = episode.failure or exc
        status = "budget_exceeded" if isinstance(exc, BudgetExceeded) else phase + "_error"
        error = str(exc) if isinstance(exc, (ModelError, BudgetExceeded)) else type(exc).__name__
    finally:
        write_json(output / "usage.json", episode.gateway.ledger.summary())
    result = {
        "task_id": task.task_id, "status": status, "mock": transport.mock,
        "grade_only": saved_design is not None,
        "design_submitted": episode.design is not None,
        "design_score": grade.design_score if grade and not transport.mock else None,
        "actor_calls": episode.actor_calls, "researcher_questions": episode.researcher.questions,
        "actor_status": episode.actor_status, "actor_error": episode.actor_error,
        "budget_charge_usd": round(episode.gateway.ledger.episode.charged, 6),
        "error": error,
    }
    write_json(output / "result.json", result)
    return result


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
