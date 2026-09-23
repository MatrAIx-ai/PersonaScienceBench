"""Deterministic A–G persona routing; H comes exclusively from task context."""

from copy import deepcopy
import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator

from personasciencebench.schema import Episode, Record

Level = Literal["novice", "intermediate", "expert"]


class Role(Record):
    title: str = Field(default="researcher", min_length=1, max_length=120)
    seniority: Literal["junior", "mid", "senior"] = "mid"


class Expertise(Record):
    domain: str = Field(default="task", min_length=1, max_length=120)
    domain_level: Level = "intermediate"
    statistics: Level = "intermediate"
    coding: Level = "intermediate"


class ResearchStyle(Record):
    approach: Literal["balanced", "exploratory", "hypothesis_driven"] = "balanced"
    method_preference: Literal["agnostic", "interpretable", "predictive"] = "agnostic"


class Evidence(Record):
    standard: Literal["standard", "rigorous"] = "standard"
    risk_tolerance: Literal["cautious", "balanced", "tolerant"] = "balanced"


class Communication(Record):
    verbosity: Literal["concise", "normal", "detailed"] = "normal"
    technical_level: Literal["plain", "technical"] = "technical"
    tone: Literal["neutral", "collaborative", "skeptical"] = "neutral"


class Workflow(Record):
    priority: Literal["balanced", "speed", "thoroughness"] = "balanced"
    compute_preference: Literal["unconstrained", "economical"] = "unconstrained"


class Interaction(Record):
    initiative: Literal["responsive", "proactive"] = "responsive"
    feedback: Literal["neutral", "supportive", "challenging"] = "neutral"


class Persona(Record):
    id: str = Field(default="neutral", min_length=1)
    version: str = Field(default="2", min_length=1)
    role: Role = Field(default_factory=Role)
    expertise: Expertise = Field(default_factory=Expertise)
    research_style: ResearchStyle = Field(default_factory=ResearchStyle)
    evidence: Evidence = Field(default_factory=Evidence)
    communication: Communication = Field(default_factory=Communication)
    workflow: Workflow = Field(default_factory=Workflow)
    interaction: Interaction = Field(default_factory=Interaction)

    @model_validator(mode="before")
    @classmethod
    def legacy_style(cls, value):
        if not isinstance(value, dict):
            return value
        value = deepcopy(value)
        for key in ("verbosity", "technical_level", "tone"):
            if key in value:
                nested = value.setdefault("communication", {})
                old = value.pop(key)
                if key in nested and nested[key] != old:
                    raise ValueError(f"Conflicting legacy and nested {key}")
                nested[key] = old
        if "request_evidence" in value:
            old = value.pop("request_evidence")
            if not isinstance(old, bool):
                raise ValueError("request_evidence must be boolean")
            standard = "rigorous" if old else "standard"
            nested = value.setdefault("evidence", {})
            if "standard" in nested and nested["standard"] != standard:
                raise ValueError("Conflicting evidence preferences")
            nested["standard"] = standard
        return value


def _merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)
    for key, value in override.items():
        result[key] = (_merge(result[key], value)
                       if isinstance(value, dict) and isinstance(result.get(key), dict)
                       else deepcopy(value))
    return result


class PersonaRouter(Record):
    version: Literal["1"] = "1"
    defaults: dict = Field(default_factory=dict)
    domains: dict[str, dict] = Field(default_factory=dict)
    tasks: dict[str, dict] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_profiles(self):
        # Validate even unused routes so typos do not lie dormant until a later run.
        self.defaults = Persona.model_validate(self.defaults).model_dump(exclude_unset=True)
        for routes in (self.domains, self.tasks):
            for key, patch in routes.items():
                if not key.strip():
                    raise ValueError("Route keys cannot be empty")
                routes[key] = Persona.model_validate(patch).model_dump(exclude_unset=True)
        return self


def resolve_persona(config: dict, episode: Episode) -> Persona:
    """Existing persona < router defaults < exact domain < full episode ID."""
    profile = Persona.model_validate(config.get("persona", {})).model_dump()
    router = PersonaRouter.model_validate(config.get("persona_router", {}))
    for patch in (router.defaults, router.domains.get(episode.domain, {}),
                  router.tasks.get(episode.id, {})):
        profile = _merge(profile, patch)
    if profile["expertise"]["domain"] == "task":
        profile["expertise"]["domain"] = episode.domain
    return Persona.model_validate(profile)


def render_persona(persona: Persona) -> str:
    """Versioned behavioral rendering, with no reference data or generated biography."""
    p = persona
    seniority = {"junior": "Ask for explanations when a methodological choice is unclear.",
                 "mid": "Discuss methodological choices and ask for their rationale when needed.",
                 "senior": "Ask for methodological justification when assumptions are unclear."}
    approach = {"balanced": "Balance exploration with explicit hypotheses.",
                "exploratory": "Prefer examining patterns and alternative explanations before committing to a hypothesis.",
                "hypothesis_driven": "Prefer stating a hypothesis and comparison before analysis."}
    methods = {"agnostic": "Consider methods on their merits.",
               "interpretable": "Prefer interpretable methods when scientifically suitable.",
               "predictive": "Prefer assessing predictive performance when relevant to the task."}
    evidence = {"standard": "Ask for evidence proportional to the claim.",
                "rigorous": "Ask for uncertainty, controls and robustness checks where relevant."}
    risk = {"cautious": "Favor conservative interpretations and explicitly flag uncertainty.",
            "balanced": "Weigh uncertainty against the value of exploring a direction.",
            "tolerant": "Be open to speculative directions, but label them as speculative."}
    priority = {"balanced": "Balance effort and analytical completeness.",
                "speed": "Prefer a useful initial analysis followed by refinement.",
                "thoroughness": "Prefer careful checks before concluding."}
    initiative = {"responsive": "Focus on answering the current question.",
                  "proactive": "During your reply, raise one relevant clarification or next-step question when useful."}
    feedback = {"neutral": "Give direct, even-handed feedback.",
                "supportive": "Acknowledge useful progress and offer constructive suggestions.",
                "challenging": "Probe weak assumptions and request justification respectfully."}
    levels = {"novice": "Ask for explanations; do not claim specialist mastery.",
              "intermediate": "Discuss standard concepts and acknowledge limits on advanced details.",
              "expert": "Use precise terminology and probe assumptions, without claiming unprovided study knowledge."}
    return "\n".join([
        f"You are a {p.role.seniority} {p.role.title} collaborating on research.",
        seniority[p.role.seniority],
        f"Your domain is {p.expertise.domain}.",
        *[f"{label} expertise: {level}. {levels[level]}" for label, level in
          (("Domain", p.expertise.domain_level), ("Statistics", p.expertise.statistics), ("Coding", p.expertise.coding))],
        approach[p.research_style.approach], methods[p.research_style.method_preference],
        evidence[p.evidence.standard], risk[p.evidence.risk_tolerance],
        f"Use {p.communication.verbosity} replies, {p.communication.technical_level} language, "
        f"and a {p.communication.tone} tone.",
        priority[p.workflow.priority],
        "Prefer economical computation." if p.workflow.compute_preference == "economical" else "Express no additional compute preference.",
        initiative[p.interaction.initiative], feedback[p.interaction.feedback],
        "These are preferences, not new task requirements. Never invent budgets, deadlines, access, credentials, "
        "personal history or scientific findings. Expertise changes how you communicate, not which study facts you know.",
    ])


def persona_record(persona: Persona) -> dict:
    prompt = render_persona(persona)
    payload = {"schema_version": "2", "renderer_version": "1", "profile": persona.model_dump(),
               "identity_prompt": prompt}
    payload["sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return payload
