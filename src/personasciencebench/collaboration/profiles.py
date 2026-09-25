"""Science profiles use a closed vocabulary and independently assigned abilities."""

from functools import lru_cache
from importlib.resources import files
import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator

from personasciencebench.schema import Record


@lru_cache(maxsize=1)
def _catalog_bytes() -> bytes:
    return files(__package__).joinpath("catalog.json").read_bytes()


def load_catalog() -> dict:
    # A fresh object prevents caller mutations from changing later profiles.
    return json.loads(_catalog_bytes())


def catalog_sha256() -> str:
    return hashlib.sha256(_catalog_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


class SciencePersona(Record):
    version: Literal["science-persona-1.0"] = "science-persona-1.0"
    id: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    domain: str = Field(min_length=1, max_length=120)
    attributes: dict[str, Literal["low", "medium", "high"]]
    active_attributes: list[str] | None = None

    @model_validator(mode="after")
    def closed_vocabulary(self):
        expected = {a["id"] for a in load_catalog()["attributes"]}
        if set(self.attributes) != expected:
            raise ValueError(f"Exactly 56 attributes required; missing={sorted(expected-set(self.attributes))}, "
                             f"unknown={sorted(set(self.attributes)-expected)}")
        if self.active_attributes is not None:
            active = self.active_attributes
            if not active or len(set(active)) != len(active) or set(active)-expected:
                raise ValueError("active_attributes must be a nonempty, unique catalog subset")
        return self


def render_profile(profile: SciencePersona) -> str:
    catalog = load_catalog()
    active = set(profile.active_attributes or profile.attributes)
    lines = [f"You are a {profile.role} collaborating in {profile.domain}.",
             "Your role does not imply expertise. Apply these independently assigned behavioral anchors:"]
    for attribute in catalog["attributes"]:
        if attribute["id"] in active:
            lines.append(attribute["label"] + ": " + attribute["levels"][profile.attributes[attribute["id"]]])
    lines.extend([
        "Behave according to these anchors only when the conversation creates a relevant opportunity.",
        "Do not recite this profile, its IDs, or the catalog. Do not invent a biography.",
        "Use only the approved public context and disclosed facts. Ability is not access to hidden truth.",
        "Preferences cannot change native objectives, data, methods, allowed models, budgets, or grading.",
        "All levels require honesty, calibrated claims, and respect for scientific constraints.",
        "Express a relevant need before expecting the agent to satisfy it. Do not penalize earlier behavior retroactively."
    ])
    return "\n".join(lines)


def profile_record(profile: SciencePersona) -> dict:
    record = {"profile": profile.model_dump(), "catalog_version": load_catalog()["version"],
              "catalog_sha256": catalog_sha256(),
              "renderer_version": "science-renderer-1.0", "prompt": render_profile(profile)}
    return {**record, "sha256": digest(record)}


def profile_json_schema() -> dict:
    """Export a schema that enforces the exact vocabulary, including external clients."""
    schema = SciencePersona.model_json_schema()
    keys = [a["id"] for a in load_catalog()["attributes"]]
    schema["properties"]["attributes"] = {
        "type": "object", "additionalProperties": False, "required": keys,
        "properties": {key: {"type": "string", "enum": ["low", "medium", "high"]} for key in keys}}
    schema["properties"]["active_attributes"] = {
        "anyOf": [{"type": "array", "items": {"type": "string", "enum": keys},
                   "minItems": 1, "uniqueItems": True}, {"type": "null"}], "default": None}
    return schema
