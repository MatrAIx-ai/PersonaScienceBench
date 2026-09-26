"""Design-only EXP bridge to the shared approach/result review protocol."""

import json
from types import SimpleNamespace
from datetime import datetime, timezone

from expbench.artifacts import append_jsonl
from personasciencebench.collaboration import ActiveResearcher, POLICY
from personasciencebench.persona import Persona
from personasciencebench.schema import (Episode, PublicContext, ResearcherContext,
                                       Fact, Provenance, EvaluatorSpec)


class ResearcherBackend:
    def __init__(self, gateway):
        self.gateway = gateway

    def complete(self, messages, *, json_mode=False):
        response = self.gateway.complete("researcher", messages, json_object=json_mode)
        return response["choices"][0]["message"]["content"]

    def complete_decision(self, messages, schema):
        name = "researcher_decision"
        response = self.gateway.complete("researcher", messages, tools=[{"type":"function", "function":{
            "name":name, "description":"Return one researcher decision for this turn.", "parameters":schema}}],
            tool_choice={"type":"function", "function":{"name":name}})
        calls=response["choices"][0]["message"].get("tool_calls", [])
        if len(calls)!=1 or calls[0]["function"]["name"]!=name:
            raise ValueError("Expected one researcher decision tool call")
        return calls[0]["function"]["arguments"]


def initialize(episode):
    task = episode.task
    # Construct from explicit public/approved fields only; never copy reference_design.
    converted = Episode(
        id=task.task_id, benchmark="expbench", source_task_id=task.task_id,
        study_id=task.task_id, domain=task.domain, source_revision=str(task.provenance.get("source_sha256", "legacy-converted-task")),
        track="design_only",
        public=PublicContext(question=task.public.question, context=task.public.context,
            documents=task.public.documents, environment=episode.resources,
            submission={"deliverable": "Final experiment design with rationale, controls, analysis plan and feasibility; experimental execution is not required."}),
        researcher=ResearcherContext(facts=[Fact(
            id=f.id, topic=f.topic, text=f.text, kind=f.kind, review_status=f.review_status,
            source=Provenance(source_path=f.provenance.get("source_path", f.source_field),
                revision=f.provenance.get("source_revision", str(task.provenance.get("source_sha256", "legacy-converted-task"))),
                locator=f.provenance.get("source_locator", f.source_field), sha256=f.provenance.get("source_sha256")))
            for f in task.researcher.facts], unknowns=task.researcher.unspecified),
        evaluator=EvaluatorSpec(kind="external_design_grader", version="unchanged"))
    episode.researcher = ActiveResearcher(converted, ResearcherBackend(episode.gateway),
                                          persona=episode.config.persona or Persona(enabled=False),
                                          unrestricted_knowledge=episode.config.collaboration.unrestricted_knowledge)
    episode.review_session = SimpleNamespace(output=episode.output, event=lambda kind, value:
        append_jsonl(episode.output / "events.jsonl", {
            "time": datetime.now(timezone.utc).isoformat(), "type": kind,
            "episode_id": task.task_id, "payload": value}))
    episode.turn_reply = None
    episode.collaboration_termination = "not_started"


def drive(episode, conversation):
    researcher = episode.researcher
    limit = episode.config.collaboration.max_requests
    handoff = candidate = None
    for turn in range(limit + 1):
        decision = researcher.decide(episode.review_session, handoff, limit - turn)
        if decision.action == "stop":
            episode.collaboration_termination = "researcher_selected"
            if candidate is not None:
                # EXP design-only evaluates its final accepted design as the native initial checkpoint.
                episode.checkpoint("initial", candidate["answer"])
                episode.design = candidate["answer"]
                episode.review_session.event("design_submission", {"policy": POLICY})
            return
        if turn == limit or episode.actor_calls >= episode.config.limits.actor_steps:
            episode.collaboration_termination = "request_limit" if turn == limit else "actor_call_limit"
            episode.review_session.event("collaboration_budget_exhausted", {"reason": episode.collaboration_termination})
            return
        episode.turn_reply = None
        message = {"researcher_request": decision.message,
                   "required_handoff_stage": "result" if researcher.approach_approved else "plan",
                   "approach_approved": researcher.approach_approved}
        if turn == 0:
            message["public_task"] = episode.actor_input()
        conversation.send_message(json.dumps(message, ensure_ascii=False))
        conversation.max_iteration_per_run = episode.config.limits.actor_steps - episode.actor_calls
        conversation.run()
        if episode.failure:
            raise episode.failure
        handoff = episode.turn_reply
        if handoff is None:
            episode.collaboration_termination = "actor_did_not_handoff"
            return
        if handoff["stage"] == "result":
            candidate = handoff
