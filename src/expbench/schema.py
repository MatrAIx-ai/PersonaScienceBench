"""Validated configuration and explicit public/private task contracts."""

import json
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator
from personasciencebench.persona import Persona
from personasciencebench.collaboration import CollaborationConfig


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ModelSettings(Record):
    model: str = Field(min_length=1)
    max_output_tokens: int = Field(ge=256, le=32768)
    input_usd_per_million: float = Field(gt=0)
    output_usd_per_million: float = Field(gt=0)
    reasoning_effort: str | None = None


class Models(Record):
    actor: ModelSettings
    researcher: ModelSettings
    judge: ModelSettings


class Limits(Record):
    actor_steps: int = Field(ge=1, le=100)
    researcher_questions: int = Field(ge=0, le=30)
    episode_usd: float | None = Field(default=None, gt=0)
    run_usd: float | None = Field(default=None, gt=0)
    request_timeout_seconds: int = Field(ge=1, le=600)


class Config(Record):
    models: Models
    limits: Limits
    persona: Persona | None = None
    collaboration: CollaborationConfig | None = None

    @classmethod
    def load(cls, path: Path):
        data = json.loads(path.read_text()) if path.suffix == ".json" else tomllib.loads(path.read_text())
        return cls.model_validate(data)


class PublicTask(Record):
    question: str = Field(min_length=1)
    context: str = Field(min_length=1)
    documents: dict[str, str]


class Fact(Record):
    id: str
    topic: str
    text: str
    source_field: str
    kind: str = "context"
    review_status: str = "reviewed"
    provenance: dict = Field(default_factory=dict)


class ResearcherContext(Record):
    facts: list[Fact]
    unspecified: list[str]

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [f.id for f in self.facts]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate researcher fact IDs")
        return self


class ReferenceDesign(Record):
    constant_variables: dict
    independent_variables: dict
    dependent_variables: dict

    @model_validator(mode="after")
    def nonempty_groups(self):
        if not all(self.model_dump().values()):
            raise ValueError("Every reference variable group must be nonempty")
        return self


class Task(Record):
    task_id: str
    domain: str
    public: PublicTask
    researcher: ResearcherContext
    reference_design: ReferenceDesign
    provenance: dict
    review_notes: list[str]


class Design(Record):
    objective: str = Field(min_length=10, max_length=8000)
    constant_variables: list[str] = Field(min_length=1, max_length=40)
    independent_variables: list[str] = Field(min_length=1, max_length=40)
    dependent_variables: list[str] = Field(min_length=1, max_length=40)
    procedure: str = Field(min_length=20, max_length=24000)
    analysis_plan: str = Field(min_length=10, max_length=12000)
    assumptions: list[str] = Field(max_length=40)

    @model_validator(mode="after")
    def valid_items(self):
        for group in (self.constant_variables, self.independent_variables,
                      self.dependent_variables, self.assumptions):
            if any(not item.strip() or len(item) > 4000 for item in group):
                raise ValueError("Design list entries must be nonempty and <=4000 characters")
        return self


class ResearcherReply(Record):
    answer: str = Field(min_length=1, max_length=8000)
    fact_ids: list[str]


class Grade(Record):
    design_score: int = Field(ge=0, le=100, strict=True)
    design_evaluation_explanation: str = Field(min_length=1)
    design_error_analysis: str


def load_tasks(path: Path) -> list[Task]:
    tasks = [Task.model_validate(json.loads(line))
             for line in path.read_text().splitlines() if line.strip()]
    if not tasks or len({t.task_id for t in tasks}) != len(tasks):
        raise ValueError("Task file must contain nonempty, unique tasks")
    return tasks
