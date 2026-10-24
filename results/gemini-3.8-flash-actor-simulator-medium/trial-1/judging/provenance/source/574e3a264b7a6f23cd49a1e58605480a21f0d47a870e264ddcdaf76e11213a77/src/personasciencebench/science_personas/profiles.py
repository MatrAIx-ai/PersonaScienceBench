"""Closed science attributes, independent role metadata, and stable rendering.

This module does not read tasks, construct episodes, control turns, or grade work.
"""

from functools import lru_cache
from importlib.resources import files
import hashlib
import json
from typing import Literal

from pydantic import Field, field_validator, model_validator

from personasciencebench.schema import Record

Level = Literal["low", "medium", "high"]


@lru_cache(maxsize=1)
def _catalog_bytes() -> bytes:
    return files(__package__).joinpath("catalog.json").read_bytes()


def load_catalog() -> dict:
    """Return a fresh copy so a caller cannot mutate subsequent renders."""
    return json.loads(_catalog_bytes())


def catalog_sha256() -> str:
    return hashlib.sha256(_catalog_bytes()).hexdigest()


class SciencePersona(Record):
    version: Literal["science-persona-2.0"] = "science-persona-2.0"
    id: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    domain: str = Field(min_length=1, max_length=120)
    attributes: dict[str, Level]

    @field_validator("id", "role", "domain")
    @classmethod
    def nonblank_metadata(cls, value):
        if not value.strip():
            raise ValueError("Persona metadata cannot be blank")
        return value

    @model_validator(mode="after")
    def closed_vocabulary(self):
        expected = {attribute["id"] for attribute in load_catalog()["attributes"]}
        actual = set(self.attributes)
        if actual != expected:
            raise ValueError(
                f"Exactly {len(expected)} science attributes are required; "
                f"missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
            )
        return self


def render_profile(profile: SciencePersona) -> str:
    # Revalidate nested mappings in case a caller mutated an existing model.
    profile = SciencePersona.model_validate(profile.model_dump())
    lines = [
        f"You are a simulated {profile.role} working in {profile.domain}.",
        "Your role and domain labels do not determine your abilities or grant study knowledge.",
        "The following independently assigned anchors define your researcher persona:",
    ]
    for attribute in load_catalog()["attributes"]:
        lines.append(f"{attribute['label']}: {attribute['levels'][profile.attributes[attribute['id']]]}")
    lines.extend([
        "Express relevant traits naturally during an existing researcher reply; do not recite this profile or its identifiers.",
        "Use only knowledge and factual claims permitted by the existing simulator policy. Expertise does not grant hidden facts, references, results, or solutions.",
        "Low expertise means acknowledging limits and requesting explanation, not fabricating findings. High expertise never overrides the knowledge boundary.",
        "Preferences, suggestions, and review comments remain optional. Do not turn them into task requirements, approval gates, or conditions for accepting a submission.",
        "The existing task, fact-disclosure rules, response format, tools, turn and resource limits, and evaluation remain authoritative.",
        "Do not initiate extra turns, require a revision cycle, withhold eligible facts to force consultation, or invent budgets, access, deadlines, or biographical events.",
        "When an attribute is irrelevant or conflicts with the fixed protocol, follow the protocol without forcing that trait into the conversation.",
        "All levels require honesty and calibrated claims. These anchors describe the researcher; they do not score the agent.",
    ])
    return "\n".join(lines)


def profile_record(profile: SciencePersona) -> dict:
    record = {
        "profile": profile.model_dump(), "catalog_version": load_catalog()["version"],
        "catalog_sha256": catalog_sha256(), "renderer_version": "science-renderer-2.0",
        "prompt": render_profile(profile),
    }
    record["sha256"] = hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return record


def with_attribute(profile: SciencePersona, attribute: str, level: Level, *, profile_id: str) -> SciencePersona:
    """Create an explicit one-attribute contrast without inferring anything from a task."""
    data = profile.model_dump()
    data["id"] = profile_id
    data["attributes"][attribute] = level
    return SciencePersona.model_validate(data)


def profile_json_schema() -> dict:
    """Expose the same exact attribute vocabulary to non-Python clients."""
    schema = SciencePersona.model_json_schema()
    keys = [attribute["id"] for attribute in load_catalog()["attributes"]]
    schema["properties"]["attributes"] = {
        "type": "object", "additionalProperties": False, "required": keys,
        "properties": {key: {"type": "string", "enum": ["low", "medium", "high"]} for key in keys},
    }
    return schema
