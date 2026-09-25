"""Connect the worked disclosure protocol to the existing actor/session interface."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from personasciencebench.adapters.base import check_submission
from personasciencebench.adapters.terminal_bench_science import ODE
from personasciencebench.session import EpisodeSession
from .interaction import InteractionController
from .profiles import profile_record
from .task import write_json


class CollaborativeSession(EpisodeSession):
    """Drop-in session for run_actor; the scientific sealing path is inherited."""

    def __init__(self, episode, profile, output, *, artifact_root, neutral=False):
        if episode.source_task_id != ODE:
            raise ValueError("This worked protocol is bound to ODE; review a new binding for other tasks")
        episode = episode.model_copy(deep=True)
        self.collaboration = InteractionController(profile, neutral=neutral)
        episode.public.context += "\n" + self.collaboration.events[0]["text"]
        episode.public.context += (
            "\nUse topic=workflow, reporting, numerical_help, or stopping when asking a researcher question. "
            "You have six question calls and 40 collaboration actions, plus a reserved final response "
            "only if the controller discloses a request on the last action. "
            "submit_result may return submitted=false with feedback. Continue working and submit again "
            "when that happens. Only submitted=true seals the scientific result.")
        episode.public.researcher_topics = ["workflow", "reporting", "numerical_help", "stopping"]
        view = SimpleNamespace(episode_id=episode.id, persona_metadata=profile_record(profile),
                               disclosed={}, questions=0, history=[], audit=[])
        super().__init__(episode, view, output, artifact_root=artifact_root)
        self._save_collaboration()

    def _save_collaboration(self):
        write_json(self.output / "collaboration_events.private.json", self.collaboration.events)
        write_json(self.output / "disclosures.private.json", self.collaboration.ledger)
        write_json(self.output / "rubric.private.json", self.collaboration.frozen_rubric)
        write_json(self.output / "burden.json", self.collaboration.burden())
        if self.collaboration.closed:
            write_json(self.output / "judge_packet.private.json", self.collaboration.judge_packet())

    def ask_researcher(self, question, topic=None):
        self._open()
        topics = [topic] if topic in self.episode.public.researcher_topics else []
        result = self.collaboration.act({"kind": "question", "text": question, "topics": topics})
        self.researcher.questions = self.collaboration.questions
        self.event("researcher_question", {"question": question, "topic": topic})
        self.event("researcher_reply", {"answer": result["reply"]})
        self._save_collaboration()
        return {"answer": result["reply"], "fact_ids": []}

    def report_progress(self, message):
        self._open()
        result = self.collaboration.act({"kind": "progress", "text": message})
        self.event("shared_progress", {"message": message, "researcher_reply": result["reply"]})
        self._save_collaboration()
        return {"recorded": True, "researcher_reply": result["reply"]}

    def submit_plan(self, plan):
        self._open()
        result = self.collaboration.act({"kind": "plan", "text": plan})
        self.event("plan_submitted", {"plan": plan, "researcher_reply": result["reply"]})
        self._save_collaboration()
        return {"recorded": True, "continue_workflow": True, "researcher_reply": result["reply"]}

    def submit_result(self, submission):
        self._open()
        check_submission(self.episode, submission)
        expected = {"/results/equations.json", "/results/predictions.csv", "/results/report.md"}
        if set(submission.artifacts) != expected:
            raise ValueError("The ODE submission must contain exactly the three native output keys")
        # A dry state transition finds due feedback without closing the real state.
        trial = deepcopy(self.collaboration)
        reply = trial.act({"kind": "final", "text": submission.answer})
        if not reply["sealed"]:
            self.collaboration = trial
            self.event("submission_review", {"researcher_reply": reply["reply"]})
            self._save_collaboration()
            return {"submitted": False, "revision_opportunity": True, "researcher_reply": reply["reply"]}
        # Existing boundary validates paths, checks for concurrent writes, and seals.
        result = super().submit_result(submission)
        report = Path(self.submission.artifacts["/results/report.md"])
        if report.stat().st_size <= 100000:
            try:
                self.collaboration.record_artifact(report, "sealed native report.md")
            except (ValueError, UnicodeError) as error:
                self.event("interaction_evidence_unavailable", {"reason": str(error)})
        else:
            self.event("interaction_evidence_unavailable", {"reason": "Report exceeds the 100 KB judge evidence limit"})
        self.collaboration.act({"kind": "final", "text": submission.answer})
        self._save_collaboration()
        return result
