"""Attach an explicitly selected persona without changing other run settings."""

from copy import deepcopy

from .profiles import SciencePersona


def attach_profile(config: dict, profile: SciencePersona) -> dict:
    """Replace only the top-level persona block in an unrouted run config.

Nonempty routing is rejected rather than silently changing or overriding it.
Existing manual routing remains supported by the original PersonaRouter.
"""
    from personasciencebench.persona import PersonaRouter

    if not isinstance(config, dict):
        raise ValueError("Run config must be a JSON object")
    router = PersonaRouter.model_validate(config.get("persona_router", {}))
    if router.defaults or router.domains or router.tasks:
        raise ValueError("Single-profile attachment requires empty persona routing; configure existing routes explicitly")
    profile = SciencePersona.model_validate(profile.model_dump())
    result = deepcopy(config)
    result["persona"] = {
        "enabled": True, "id": profile.id, "version": profile.version,
        "science_profile": profile.model_dump(),
    }
    return result
