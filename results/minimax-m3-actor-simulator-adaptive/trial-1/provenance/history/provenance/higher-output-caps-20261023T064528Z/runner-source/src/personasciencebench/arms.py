"""Arm roles in a persona run. Only PERSONA arms are ranked; the others calibrate the comparison."""

CONTROL = "control"    # persona off (persona_off, persona_off_r2, ...)
PERSONA = "persona"    # a cohort profile
TWIN = "twin"          # a cohort profile with its lines reordered: same content, measures prompt-wording noise
NEUTRAL = "neutral"    # an enabled identity that describes an ordinary researcher (neutral_a, neutral_b)
FLOOR = "floor"        # scripted researcher that gives the agent nothing beyond the public brief
CEILING = "ceiling"    # the agent gets all researcher facts up front
TWIN_SUFFIX = "__reordered"
REFERENCE_KINDS = (TWIN, NEUTRAL, FLOOR, CEILING)


def arm_kind(arm: str) -> str:
    if arm == "persona_off" or arm.startswith("persona_off_r"):
        return CONTROL
    if arm.endswith(TWIN_SUFFIX):
        return TWIN
    for prefix, kind in (("neutral_", NEUTRAL), ("floor_", FLOOR), ("ceiling_", CEILING)):
        if arm.startswith(prefix):
            return kind
    return PERSONA


def is_control(arm: str) -> bool:
    return arm_kind(arm) == CONTROL


def twin_of(arm: str) -> str | None:
    """The persona a twin arm was made from, or None."""
    return arm[:-len(TWIN_SUFFIX)] if arm.endswith(TWIN_SUFFIX) else None
