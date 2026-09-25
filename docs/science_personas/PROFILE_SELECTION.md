# Selecting science personas

Selection is independent of task and evaluator design. For Phase 1, register a
common reference and change exactly one dimension per contrast, then attach the
result to the same existing simulator. There is no task-to-attribute
classifier, automatic role-to-ability mapping, latent biography generator, or
population sampler in this delivery.

## Whole-profile vocabulary examples (not Phase 1 arms)

| File in `examples/science_personas/profiles/` | Role | Domain label | Purpose |
|---|---|---|---|
| `pi_cautious.json` | PI | Applied mathematics | A cautious, consultation-preferring example with low coding fluency |
| `pi_delegating.json` | PI | Applied mathematics | Exactly the same assignments except higher decision delegation |
| `phd_learning.json` | PhD researcher | Nonlinear dynamics | A learning-oriented example |
| `computational_scientist.json` | Computational scientist | Scientific computing | A computationally experienced example |
| `experimentalist.json` | Experimental scientist | Physical measurement | A measurement-oriented example |
| `theorist_exploratory.json` | Theory researcher | Dynamical systems | A theoretically oriented exploratory example |

These are authored examples, not empirical distributions or claims about people
with those roles. Every file assigns all 56 dimensions independently. Role and
domain labels do not grant additional facts or specialist ability. Inspect the
actual assignments before selecting a profile.

The six examples vary 28 of the 56 dimensions. All 56 are rendered, but this set
does not span all combinations or demonstrate fidelity across all dimensions.
A dimension held constant across examples can still be varied explicitly.

## One-variable contrasts

Use a matched contrast when investigating one trait; changing a role, expertise,
communication style, and risk preference together is a whole-profile comparison.
The two PI files differ in `decision_delegation` only, apart from profile ID.

```python
from pathlib import Path
from personasciencebench.science_personas.profiles import SciencePersona, with_attribute

profile_path = Path("examples/science_personas/profiles/pi_cautious.json")
base = SciencePersona.model_validate_json(profile_path.read_text())
contrast = with_attribute(base, "explanation_depth", "high", profile_id="detailed-contrast")
```

This returns a new validated profile and leaves the original unchanged. Unknown
attributes and levels fail validation. It neither reads nor edits a task.

For a comparison, hold the prepared task, evaluator, source revision, actor and
simulator models, mode, budgets, and run settings fixed. Record the changed
persona and its hash. This is experimental bookkeeping around an existing
benchmark; it does not require changing the benchmark's design or score.

## Authoring rules

- Use `low`, `medium`, or `high` according to each dimension's own anchors.
  They are intensity/capability settings, not a universal good-to-bad scale.
- Keep expertise separate from preferences: someone can understand a detailed
  derivation while preferring a concise answer, or want rigorous checks while
  needing their rationale explained.
- Distinguish related traits: delegation concerns involvement in decisions;
  consultation threshold concerns when questions are welcome. Progress cadence
  concerns conversational updates; checkpoint frequency concerns saving work.
- All combinations remain subject to the original simulator policy. A strong
  revision preference is optional feedback during an available turn, never a
  new review gate. A compute preference never invents a hardware limit.
- Validate before use and review the rendered prompt. Run simulator QA for the
  traits your comparison intends to study. Do not infer fidelity from a profile
  file being valid or a prompt containing the desired words.

## Phase 1 selection

Use [the experiment plan](experiment_plan.md) and its proposed explicit design.
The lead fixes the arms for the full cohort before runs. Do not select profiles
per task. Off vs reference estimates conditioning as a whole; dimension effects
come from contrasts against the same reference or low/high within one dimension.
The six examples above are not a factorial or one-variable experimental matrix.
