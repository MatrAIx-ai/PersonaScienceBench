"""Explicit public, researcher, and evaluator boundaries for every adapter."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Provenance(Record):
    source_path: str
    revision: str
    locator: str
    sha256: str | None = None


class Fact(Record):
    id: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    text: str = Field(min_length=1)
    kind: Literal["context", "fixed_requirement", "optional_advice"] = "context"
    source: Provenance
    disclosure: Literal["on_relevant_question", "on_shared_progress"] = "on_relevant_question"
    review_status: Literal["candidate", "reviewed"] = "candidate"


class Asset(Record):
    id: str
    source_path: str
    target_path: str
    kind: Literal["file", "directory"] = "file"
    visibility: Literal["actor", "researcher", "evaluator"] = "actor"
    required: bool = True
    sha256: str | None = None
    acquisition: str | None = None


class PublicContext(Record):
    question: str = Field(min_length=1)
    context: str = ""
    documents: dict[str, str] = Field(default_factory=dict)
    submission: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)
    researcher_topics: list[str] = Field(default_factory=list)


class ResearcherContext(Record):
    facts: list[Fact] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_facts(self):
        if len({f.id for f in self.facts}) != len(self.facts):
            raise ValueError("Researcher fact IDs must be unique")
        return self


class EvaluatorSpec(Record):
    kind: str
    version: str
    reference: dict[str, Any] = Field(default_factory=dict, repr=False)
    config: dict[str, Any] = Field(default_factory=dict)
    entrypoint: str | None = None


class Episode(Record):
    schema_version: str = "0.1"
    id: str
    benchmark: str
    source_task_id: str
    study_id: str
    domain: str
    source_revision: str
    track: Literal["design_only", "full_workflow"] = "full_workflow"
    public: PublicContext
    researcher: ResearcherContext = Field(default_factory=ResearcherContext, repr=False)
    assets: list[Asset] = Field(default_factory=list, repr=False)
    evaluator: EvaluatorSpec = Field(repr=False)
    conversion: dict[str, Any] = Field(default_factory=dict)
    review_status: Literal["candidate", "reviewed"] = "candidate"

    @model_validator(mode="after")
    def unique_assets(self):
        if len({a.id for a in self.assets}) != len(self.assets):
            raise ValueError("Asset IDs must be unique")
        return self

    def actor_input(self) -> dict[str, Any]:
        """Never serialize the complete episode to the actor."""
        return {"episode_id": self.id, "benchmark": self.benchmark,
                "track": self.track, **self.public.model_dump(mode="json")}


class TaskSummary(Record):
    id: str
    study_id: str
    domain: str
    title: str
    source_locator: str


class Submission(Record):
    episode_id: str
    stage: Literal["plan", "final"] = "final"
    answer: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, str] = Field(default_factory=dict)


class EvaluationResult(Record):
    status: Literal["scored", "missing_submission", "blocked", "error"]
    evaluator_version: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class EvaluationRequest(Record):
    """A reviewable native-execution request; constructing it never executes code."""
    argv: list[str]
    cwd: str
    required_paths: list[str] = Field(default_factory=list)
    output_paths: list[str] = Field(default_factory=list)
    environment: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
