"""Topic-scoped, extractive researcher with persistent conversation memory."""

import json

from expbench.artifacts import write_json
from expbench.gateway import ModelError, parse_structured
from expbench.realistic_prompts import RESEARCHER
from expbench.schema import ResearcherReply
from personasciencebench.persona import render_persona

UNKNOWN = "That information is not specified. State an assumption or propose a justified choice."


class ScopedResearcher:
    def __init__(self, context, question, gateway, limit, history_path, *, persona=None):
        self.facts = {f.topic: f for f in context.facts}
        if len(self.facts) != len(context.facts):
            raise ValueError("Realistic researcher requires one fact per topic")
        self.question, self.gateway, self.limit = question, gateway, limit
        self.history_path = history_path
        self.persona = persona.model_copy(deep=True) if persona is not None else None
        self.messages, self.disclosed, self.questions = [], {}, 0
        write_json(history_path, self.messages)

    def ask(self, topic, question):
        if self.questions >= self.limit:
            return "The researcher question budget is exhausted. Record remaining uncertainty."
        fact = self.facts.get(topic)
        if fact is None:
            return "Choose an available topic: " + ", ".join(self.facts)
        self.questions += 1
        user = {"role": "user", "content": json.dumps({"topic": topic, "question": question})}
        self.messages.append(user)
        write_json(self.history_path, self.messages)
        policy = RESEARCHER
        if self.persona is not None and self.persona.enabled:
            policy += ("\n" + render_persona(self.persona) +
                       "\nThe identity conditions your interpretation of the question. "
                       "It does not change the approved fact boundary or the required JSON format.")
        messages = [{"role": "system", "content": policy + "\n" + json.dumps({
            "research_question": self.question, "available_fact": fact.model_dump()})}, *self.messages]
        response = self.gateway.complete("researcher", messages, schema=ResearcherReply.model_json_schema())
        reply = parse_structured(response, ResearcherReply)
        if reply.fact_ids not in ([], [fact.id]):
            raise ModelError("Researcher cited a fact outside the requested topic; answer withheld")
        answer = fact.text if reply.fact_ids else UNKNOWN
        if reply.fact_ids:
            self.disclosed[fact.id] = fact.model_dump()
        self.messages.append({"role": "assistant", "content": answer})
        write_json(self.history_path, self.messages)
        return answer
