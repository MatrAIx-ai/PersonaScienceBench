"""Knowledge, style and disclosure switches are independent; contract rejections are visible."""

import json
from types import SimpleNamespace

import pytest

from personasciencebench.actor import _run_collaboration
from personasciencebench.collaboration import ActiveResearcher, CollaborationConfig, replace_once
from personasciencebench.persona import Persona, persona_preferences, persona_record
from personasciencebench.schema import Episode, EvaluatorSpec, Fact, Provenance, PublicContext, ResearcherContext
from personasciencebench.sciconv_runner import PERSONA_BOUNDARY, Service, researcher_system_prompt

# Static text of LLMUserInterface.answer_clarification_question, SciConvBench 8d1528ed8 (context elided).
NATIVE = '''You are a User who knows the COMPLETE requirement for a task.

        The Agent only has an INCOMPLETE version and is asking clarification questions.
        You have access to the COMPLETE requirement and should answer based strictly on that.

        IMPORTANT GUIDELINES:
        1. Answer questions based on the COMPLETE user requirement.
        2. Be specific and provide concrete values if they exist in the COMPLETE requirement.
        3. If the complete requirement doesn't specify something, tell the agent: "Make a reasonable assumption based on best practices."
        4. Be consistent with previous clarifications.

        CONTEXT:
        COMPLETE REQUIREMENT: plate of width 2 m.

        CRITICAL INSTRUCTIONS:
        - Be concise.
        - Do not explain your reasoning.
        - Do not provide information not asked for.
        - Do not make up new constraints that aren't in the complete requirement.
        - Answer like a human user would.
        '''
KNOWLEDGE = ["answer based strictly on that", "Make a reasonable assumption"]
STYLE = ["- Be concise.", "- Do not explain your reasoning."]
DISCLOSURE = ["- Do not provide information not asked for."]


def test_native_sciconv_user_prompt_is_unchanged_by_default():
    assert researcher_system_prompt(NATIVE) == NATIVE


@pytest.mark.parametrize("switch, removed", [("unrestricted_knowledge", KNOWLEDGE), ("embody_identity", STYLE),
                                             ("volunteer_information", DISCLOSURE)])
def test_each_sciconv_switch_edits_only_its_own_rules(switch, removed):
    prompt = researcher_system_prompt(NATIVE, **{switch: True})
    for anchor in KNOWLEDGE + STYLE + DISCLOSURE:
        assert (anchor in prompt) == (anchor not in removed), anchor
    assert "Do not make up new constraints" in prompt


def test_persona_off_and_on_differ_only_by_identity_text():
    options = dict(unrestricted_knowledge=True, embody_identity=True, volunteer_information=True)
    off = researcher_system_prompt(NATIVE, **options)
    on = researcher_system_prompt(NATIVE, **options, persona_text="You are a terse PI.")
    assert on == off + PERSONA_BOUNDARY + "You are a terse PI."
    assert PERSONA_BOUNDARY not in researcher_system_prompt(NATIVE)


def test_persona_alone_keeps_every_native_rule():
    prompt = researcher_system_prompt(NATIVE, persona_text="You are a terse PI.")
    assert prompt.startswith(NATIVE) and all(a in prompt for a in KNOWLEDGE + STYLE + DISCLOSURE)


def test_missing_prompt_anchor_fails_loudly():
    with pytest.raises(ValueError, match="anchor"):
        researcher_system_prompt(NATIVE.replace("- Be concise.", "- Be brief."), embody_identity=True)
    with pytest.raises(ValueError):
        replace_once("a a", "a", "b")


def test_service_sends_the_composed_prompt_once():
    class Client:
        def completion(self, messages):
            self.messages = messages
            return {"choices": [{"message": {"content": "2 m."}}], "usage": {}}
    client = Client()
    service = Service(client, persona_text="You are a terse PI.", prompt_options={"volunteer_information": True})
    service.invoke("What is the width?", NATIVE)
    system = client.messages[0]["content"]
    assert system.count("You are a terse PI.") == 1 and DISCLOSURE[0] not in system and STYLE[0] in system
    untouched = Client()
    Service(untouched).invoke("What is the width?", NATIVE)
    assert untouched.messages[0]["content"] == NATIVE


def test_collaboration_switches_are_independent_and_strict():
    assert CollaborationConfig().model_dump() == {"protocol": "active_researcher", "unrestricted_knowledge": False,
        "embody_identity": False, "volunteer_information": False, "truthful_history": False,
        "researcher_policy": "llm", "max_requests": 12}
    with pytest.raises(ValueError):
        CollaborationConfig(unknown_switch=True)


def test_system_prompt_persona_record_keeps_legacy_hash():
    legacy = Persona(id="p", communication={"tone": "skeptical"})
    assert "system_prompt" not in persona_preferences(legacy)
    assert persona_record(legacy)["profile"] == persona_preferences(legacy)


class DecisionBackend:
    def __init__(self, decisions):
        self.decisions, self.requests = list(decisions), []

    def complete_decision(self, messages, schema):
        self.requests.append(messages)
        return json.dumps(self.decisions.pop(0))


def decision(action="continue", interaction="next_task", approve=False):
    return {"action": action, "interaction": interaction, "message": "Proceed.", "evidence": "Visible progress.",
            "objectives_open": [], "fact_ids": [], "approve_approach": approve}


def episode(benchmark="bixbench"):
    return Episode(id="fixture-task", benchmark=benchmark, source_task_id="native-id", study_id="study",
        domain="biology", source_revision="fixture", public=PublicContext(question="Compare the two conditions."),
        researcher=ResearcherContext(facts=[Fact(id="conditions", topic="conditions", text="Two conditions.",
            source=Provenance(source_path="f", revision="f", locator="/c"), review_status="reviewed")]),
        evaluator=EvaluatorSpec(kind="fixture", version="fixture"))


def instructions(researcher, tmp_path):
    session = SimpleNamespace(event=lambda *a: None, output=tmp_path)
    researcher.decide(session, None, 5)
    return json.loads(researcher.backend.requests[-1][0]["content"])


@pytest.mark.parametrize("enabled", [False, True])
def test_embody_identity_is_separate_from_knowledge_and_keeps_grader_rule(tmp_path, enabled):
    persona = Persona(id="p") if enabled else Persona(enabled=False)
    plain = instructions(ActiveResearcher(episode(), DecisionBackend([decision(interaction="initial_request")]),
                                          persona=persona), tmp_path)
    styled = instructions(ActiveResearcher(episode(), DecisionBackend([decision(interaction="initial_request")]),
                                           persona=persona, embody_identity=True), tmp_path)
    assert "Use ONLY the public project brief" in styled["instructions"] and "approved_facts" in styled
    assert "Embody the supplied identity, if any" in styled["instructions"]
    assert "omniscient grader" in styled["instructions"] and "omniscient grader" in plain["instructions"]
    assert ("identity" in styled) == enabled
    general = instructions(ActiveResearcher(episode(), DecisionBackend([decision(interaction="initial_request")]),
                                            persona=persona, unrestricted_knowledge=True), tmp_path)
    assert "general knowledge" in general["instructions"] and "Use the configured expertise" in general["instructions"]


class ScriptedConversation:
    """Each run() is one actor turn that hands back the next scripted handoff."""
    def __init__(self, controller, handoffs):
        self.controller, self.handoffs, self.sent = controller, list(handoffs), []
        self.max_iteration_per_run = None

    def send_message(self, text):
        self.sent.append(json.loads(text))

    def run(self):
        self.controller.calls += 1
        self.controller.turn_reply = self.handoffs.pop(0)


def handoff(stage, artifacts=None, executed=True):
    return {"stage": stage, "answer": "A finding.", "evidence": "Ran the analysis.", "assumptions": [],
            "uncertainties": [], "payload": {"executed_analysis": executed}, "artifacts": artifacts or {}}


def test_rejected_result_is_shown_to_researcher_and_actor_then_valid_result_is_sealed(tmp_path):
    backend = DecisionBackend([decision(interaction="initial_request"), decision(approve=True),
                               decision(interaction="refine_analysis"), decision("stop", "conclude")])
    researcher = ActiveResearcher(episode(), backend, persona=Persona(enabled=False))
    events, sealed = [], []
    session = SimpleNamespace(researcher=researcher, episode=episode(), output=tmp_path,
                              event=lambda kind, value: events.append((kind, value)))
    controller = SimpleNamespace(session=session, calls=0, failure=None, actor_error=None, termination=None,
                                 turn_reply=None, dispatch=lambda op, value: sealed.append((op, value)))
    conversation = ScriptedConversation(controller, [handoff("plan"), handoff("result", executed=False),
                                                     handoff("result", {"analysis": "analysis.py"})])
    _run_collaboration(conversation, controller, {"max_requests": 6}, max_steps=20)
    rejected = [value for kind, value in events if kind == "result_handoff_rejected"]
    assert rejected == [{"reason": "result does not satisfy the submission contract",
                         "missing": ["artifacts.analysis", "payload.executed_analysis=true"]}]
    seen = json.loads(researcher.history[-2]["content"])["agent_handoff"]
    assert seen["artifacts"] == {"analysis": "analysis.py"} and "controller_contract_check" not in seen["payload"]
    reviewed_rejection = [json.loads(m["content"])["agent_handoff"] for m in researcher.history
                          if m["role"] == "user" and "agent_handoff" in m["content"]][1]
    assert reviewed_rejection["payload"]["controller_contract_check"] == rejected[0]
    assert conversation.sent[2]["previous_result_rejected"] == rejected[0]
    assert "previous_result_rejected" not in conversation.sent[1]
    assert sealed == [("submit_result", {"answer": "A finding.", "payload": {"executed_analysis": True},
                                         "artifacts": {"analysis": "analysis.py"}})]


def test_budget_exhaustion_records_whether_the_approach_was_ever_approved(tmp_path):
    backend = DecisionBackend([decision(interaction="initial_request"), decision(), decision()])
    researcher = ActiveResearcher(episode(), backend, persona=Persona(enabled=False))
    events = []
    session = SimpleNamespace(researcher=researcher, episode=episode(), output=tmp_path,
                              event=lambda kind, value: events.append((kind, value)))
    controller = SimpleNamespace(session=session, calls=0, failure=None, actor_error=None, termination=None,
                                 turn_reply=None, dispatch=lambda *a: None)
    _run_collaboration(ScriptedConversation(controller, [handoff("plan"), handoff("plan")]), controller,
                       {"max_requests": 2}, max_steps=20)
    assert ("collaboration_budget_exhausted", {"reason": "researcher_request_limit", "approach_approved": False}) in events
