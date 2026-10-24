import json

from expbench import prompts
from expbench.artifacts import write_json
from expbench.gateway import Gateway, ModelError, parse_structured, response_message
from expbench.schema import ResearcherContext, ResearcherReply


class Researcher:
    def __init__(self, context: ResearcherContext, question: str, gateway: Gateway,
                 limit: int, history_path):
        self.context = context
        self.gateway = gateway
        self.limit = limit
        self.history_path = history_path
        self.questions = 0
        self.messages = [{"role": "system", "content": prompts.RESEARCHER + "\n" + json.dumps({
            "research_question": question,
            "approved_context": context.model_dump(),
        }, ensure_ascii=False)}]
        write_json(self.history_path, self.messages)

    def ask(self, question: str) -> str:
        if self.questions >= self.limit:
            return "The researcher question budget is exhausted. State remaining assumptions and submit your design."
        if not question.strip() or len(question) > 4000:
            return "Ask a nonempty question of at most 4000 characters."
        self.questions += 1
        self.messages.append({"role": "user", "content": question})
        write_json(self.history_path, self.messages)
        response = self.gateway.complete("researcher", self.messages,
                                         schema=ResearcherReply.model_json_schema())
        reply = parse_structured(response, ResearcherReply)
        known = {fact.id for fact in self.context.facts}
        if not set(reply.fact_ids).issubset(known):
            raise ModelError("Researcher cited an unknown fact; answer withheld")
        # Empty evidence is handled in code, not left to an unconstrained model.
        if not reply.fact_ids:
            reply.answer = "That information is not specified in the supplied task facts. State an assumption or propose a justified choice."
        message = response_message(response).copy()
        message["content"] = reply.model_dump_json()
        # Retain provider reasoning metadata if present in the returned message.
        self.messages.append(message)
        write_json(self.history_path, self.messages)
        return reply.answer
