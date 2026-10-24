"""Controller-side episode lifecycle independent of the actor framework."""

from datetime import datetime, timezone
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from personasciencebench.adapters.base import check_submission, sha256
from personasciencebench.packaging import safe_component, write_json
from personasciencebench.researcher import Researcher
from personasciencebench.schema import Episode, Submission


def _artifact_file(root: Path, source: Path):
    """Open through directory descriptors so path swaps cannot follow symlinks."""
    try:
        parts = source.relative_to(root).parts
        if not parts or ".." in parts:
            raise ValueError("Artifact path is outside the configured actor artifact root")
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in parts[:-1]:
                nested = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                os.close(directory)
                directory = nested
            descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        finally:
            os.close(directory)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            os.close(descriptor)
            raise ValueError("Submission artifact must be a regular file")
        return os.fdopen(descriptor, "rb")
    except OSError:
        raise ValueError("Submission artifact must be a regular file without symlinked path components") from None


class EpisodeSession:
    def __init__(self, episode: Episode, researcher: Researcher, output: Path,
                 *, artifact_root: Path | None = None):
        if researcher.episode_id != episode.id:
            raise ValueError("Researcher belongs to another episode")
        self.artifact_root = artifact_root.resolve() if artifact_root else None
        if self.artifact_root and output.resolve().is_relative_to(self.artifact_root):
            raise ValueError("Controller output cannot be inside the actor artifact root")
        output.mkdir(parents=True, exist_ok=False)
        output.chmod(0o700)
        self.episode, self.researcher, self.output = episode, researcher, output
        self.submission: Submission | None = None
        self.closed = False
        self.sequence = 0
        write_json(output / "episode.private.json", episode.model_dump(mode="json"))
        write_json(output / "public_input.json", episode.actor_input())
        write_json(output / "persona.private.json", researcher.persona_metadata)

    def event(self, kind: str, payload: dict):
        record = {"sequence": self.sequence, "episode_id": self.episode.id,
                  "time": datetime.now(timezone.utc).isoformat(), "type": kind, "payload": payload}
        with (self.output / "events.jsonl").open("a") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.sequence += 1

    def _open(self):
        if self.closed:
            raise ValueError("Episode is already submitted")

    def ask_researcher(self, question: str, topic: str | None = None):
        self._open()
        self.event("researcher_question", {"question": question, "topic": topic})
        response = self.researcher.ask(question, topic)
        self.event("researcher_reply", response)
        write_json(self.output / "researcher_history.private.json", self.researcher.history)
        write_json(self.output / "researcher_audit.private.json", self.researcher.audit)
        return response

    def report_progress(self, message: str):
        self._open()
        self.researcher.share_progress(message)
        write_json(self.output / "researcher_history.private.json", self.researcher.history)
        self.event("shared_progress", {"message": message})
        return {"recorded": True}

    def submit_plan(self, plan: str):
        self._open()
        if not plan.strip():
            raise ValueError("Plan must be nonempty")
        path = self.output / "initial_plan.json"
        checkpoint = {"plan": plan, "trace_sequence": self.sequence,
                      "disclosed_fact_ids": list(self.researcher.disclosed),
                      "time": datetime.now(timezone.utc).isoformat()}
        write_json(path, checkpoint, exclusive=True)
        self.event("plan_submitted", {"path": path.name})
        if self.episode.track == "design_only":
            return self.submit_result(Submission(episode_id=self.episode.id, stage="plan", answer=plan))
        return {"recorded": True, "continue_workflow": True}

    def submit_result(self, submission: Submission):
        self._open()
        check_submission(self.episode, submission)
        if any(key.startswith("controller_") for key in submission.payload):
            raise ValueError("Actor submissions cannot supply controller execution receipts")
        sources = {}
        for name, raw_path in submission.artifacts.items():
            source = Path(raw_path)
            if not source.is_absolute() and self.artifact_root:
                source = self.artifact_root / source
            if self.artifact_root is None or not source.resolve().is_relative_to(self.artifact_root):
                raise ValueError("Artifact path is outside the configured actor artifact root")
            if source.is_symlink() or not source.is_file() or source.stat().st_nlink != 1:
                raise ValueError(f"Submission artifact must be a regular file: {name}")
            sources[name] = source
        sealed = {}
        hashes = {}
        final_dir = self.output / "submitted_artifacts"
        with ExitStack() as stack:
            opened = {name: stack.enter_context(_artifact_file(self.artifact_root, source))
                      for name, source in sources.items()}
            temporary = stack.enter_context(tempfile.TemporaryDirectory(prefix=".submission-", dir=self.output))
            staging = Path(temporary) / "artifacts"
            staging.mkdir()
            for name, incoming in opened.items():
                destination = staging / safe_component(name)
                before = os.fstat(incoming.fileno())
                with destination.open("xb") as target:
                    shutil.copyfileobj(incoming, target)
                after = os.fstat(incoming.fileno())
                if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                    raise ValueError("Artifact changed while it was being submitted")
                destination.chmod(0o400)
                sealed[name] = str((final_dir / destination.name).resolve())
                hashes[name] = sha256(destination)
            staging.rename(final_dir)
        self.submission = submission.model_copy(update={"artifacts": sealed})
        write_json(self.output / "submission.json", self.submission.model_dump(mode="json"), exclusive=True)
        write_json(self.output / "submission_hashes.json", hashes, exclusive=True)
        self.closed = True
        self.event("final_submission" if submission.stage == "final" else "design_submission",
                   {"artifact_hashes": hashes, "stage": submission.stage})
        return {"submitted": True, "episode_id": self.episode.id, "stage": submission.stage}
