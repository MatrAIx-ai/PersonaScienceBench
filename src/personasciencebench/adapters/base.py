"""Shared API for source adapters; no import-time network or execution."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Protocol

from personasciencebench.schema import Episode, EvaluationRequest, EvaluationResult, Submission, TaskSummary


@dataclass(frozen=True)
class SourceConfig:
    repository: Path
    assets: Path
    revision: str
    dataset_revision: str | None = None


class Judge(Protocol):
    def complete(self, messages: list[dict[str, str]], *, json_mode: bool = False,
                 settings: dict | None = None) -> str: ...


class Adapter:
    name: str

    def __init__(self, source: SourceConfig):
        self.source = source

    def enumerate_tasks(self) -> list[TaskSummary]:
        raise NotImplementedError

    def convert(self, task_id: str) -> Episode:
        raise NotImplementedError

    def pilot_task_ids(self) -> list[str]:
        """Two curated candidates; adapters must select explicitly."""
        raise NotImplementedError

    def evaluate(self, episode: Episode, submission: Submission,
                 judge: Judge | None = None) -> EvaluationResult:
        raise NotImplementedError

    def evaluation_request(self, episode: Episode, submission: Submission,
                           output: Path) -> EvaluationRequest:
        raise ValueError(f"{self.name} uses an in-process judge adapter")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_submission(episode: Episode, submission: Submission) -> None:
    if submission.episode_id != episode.id:
        raise ValueError("Submission episode ID does not match")
    if episode.track == "full_workflow" and submission.stage != "final":
        raise ValueError("A plan cannot be scored as a completed scientific task")
