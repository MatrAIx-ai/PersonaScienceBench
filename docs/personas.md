# Researcher personas

## Science attribute extension

The [56-dimension catalog](science_personas/ATTRIBUTE_CATALOG.md) is an opt-in
simulator profile through `persona.science_profile`. All 56 assignments are
required and rendered. There is no task-specific attribute projection or added
interaction controller. Legacy profile rendering is preserved. Persona off now uses the same common
policy and grounding path as persona on, omitting only the private identity.
See the authoritative [Phase 1 contract](science_personas/experiment_plan.md);
historical experiments below are not the new 50-task controlled comparison.

Read the [integration guide](science_personas/INTEGRATION_GUIDE.md),
[profile selection guide](science_personas/PROFILE_SELECTION.md), and
[ODE injection example](science_personas/ODE_INJECTION_EXAMPLE.md). Attribute
anchors describe researcher behavior; they are not agent-scoring criteria.
The supplied persona documentation follows.

Personas condition the researcher simulator through its system message. They do
not require a particular model or change model weights. Both `run` and `serve`
use the same router. The actor receives researcher replies through the existing
interface, not the hidden profile or private identity prompt.

### Action-profile case study

`persona.action_rules` accepts 1–12 concrete preference instructions as an
alternative identity representation. It cannot be combined with `science_profile`.
The action renderer replaces the legacy identity; it does not add its default
expertise or style instructions. The same private renderer is used by shared
reviews, EXP, and native SciConv. Persona off omits it through the
existing `enabled=false` switch. Scientific facts, task requirements, interaction
policy, actor inputs, and native grading remain fixed across comparison arms.

`scripts/run_persona_benchmarks.py` runs 30 profiles sampled with seed `20260930`
from the 73 that qualified in the one-response diagnostic. It uses two fixed
cases from each of five retained benchmarks plus ten shared persona-off controls,
for 310 records. ScienceAgentBench and Terminal-Bench-Science were piloted and
then discarded because their storage and execution requirements were too heavy
for this persona study. This is a separate, exploratory whole-profile study, not
the proposed one-dimension-at-a-time Phase 1 experiment. The 30-profile cohort is
enriched using the earlier diagnostic; conclusions do
not generalize to all 131 statically selected profiles or the source population.
Each off result is reused across its task's 30 contrasts and is not 30 independent
control observations. Full traces and per-task performance and behavioral deltas
are saved locally in the run directory.

## Configuration and persona off

The current [shared config](../configs/conversion-v2-two.json) and [EXP config](../configs/expbench/conversion-v2-two.toml) disable persona while retaining the simulator. To enable a profile, attach its `science_profile` using the [integration guide](science_personas/INTEGRATION_GUIDE.md), or supply a supported legacy `Persona` block.

Top-level `enabled=false` bypasses routing and omits the profile. The configured interaction protocol remains fixed: current reviews use `researcher-review-v2`; legacy optional questions use `persona-conditioning-only-v3`; SciConv uses native clarification. Persona never changes the scientific fact pool, task requirements or grader.

## Configuration

Use `configs/persona_example.json` as a complete runnable configuration. It keeps
the configured Luna model roles and adds a senior researcher example. No model
run is needed to resolve a persona. The existing `configs/pilot.json` remains a
neutral baseline; old flat style fields are accepted and normalized.

The following `persona_router` block can be added to a run configuration:

```json
{
  "persona_router": {
    "version": "1",
    "defaults": {
      "role": {"title": "researcher", "seniority": "senior"},
      "expertise": {
        "domain": "task",
        "domain_level": "expert",
        "statistics": "intermediate",
        "coding": "novice"
      },
      "research_style": {"approach": "hypothesis_driven", "method_preference": "interpretable"},
      "evidence": {"standard": "rigorous", "risk_tolerance": "cautious"},
      "communication": {"verbosity": "concise", "technical_level": "technical", "tone": "collaborative"},
      "workflow": {"priority": "thoroughness", "compute_preference": "economical"},
      "interaction": {"initiative": "proactive", "feedback": "challenging"}
    },
    "domains": {
      "sociology": {"expertise": {"statistics": "expert"}}
    },
    "tasks": {
      "REPLACE_WITH_FULL_EPISODE_ID": {"role": {"seniority": "junior"}}
    }
  }
}
```

Resolution uses recursive field overrides in this order:

1. Built-in neutral defaults and the existing top-level `persona` profile.
2. `persona_router.defaults`.
3. `persona_router.domains[episode.domain]` (exact, case-sensitive match).
4. `persona_router.tasks[episode.id]` (complete ID, including benchmark prefix).

Unspecified fields retain their earlier values. There is no random sampling,
LLM routing, fuzzy domain matching, or implicit seniority-to-expertise mapping.
`domain: "task"` resolves to the episode domain. An explicit different domain is
preserved, allowing an interdisciplinary researcher. Unknown fields, invalid
enums and contradictory legacy/nested style fields within one profile fail
validation, including in routes not selected for the current task. Unmatched
route keys simply do not apply; check the preview to catch misspelled keys.

## Supported aspects

| Aspect | Configuration and values |
| --- | --- |
| A. Role / seniority | `role.title`: short text; `seniority`: junior, mid, senior |
| B. Expertise | `expertise.domain`: task or domain text; domain_level, statistics, coding: novice, intermediate, expert independently |
| C. Research style | approach: balanced, exploratory, hypothesis_driven; method_preference: agnostic, interpretable, predictive |
| D. Evidence / risk | standard: standard, rigorous; risk_tolerance: cautious, balanced, tolerant |
| E. Communication | verbosity: concise, normal, detailed; technical_level: plain, technical; tone: neutral, collaborative, skeptical |
| F. Workflow | priority: balanced, speed, thoroughness; compute_preference: unconstrained, economical |
| G. Interaction | initiative: responsive, proactive; feedback: neutral, supportive, challenging |
| H. Knowledge boundary | Derived from public task context, reviewed facts, topic/disclosure rules and explicit unknowns; not a user-writable persona field |

`unconstrained` adds no compute preference; it does not claim unlimited hardware.
`proactive` means raising a useful clarification within a researcher reply. It
does not add unsolicited turns, rewrite the initial task, or make progress
reporting trigger a reply. The actor still decides when to ask questions. A
zero-question episode cannot establish a persona effect in this version.

## Prompt and disclosure behavior

For every question, the simulator receives the rendered A–G identity, fixed
researcher instructions, public task context, eligible reviewed facts and
unknowns, followed by the episode's shared conversation history. Rendering
turns categorical attributes into behavioral instructions, e.g. a senior
researcher asks for methodological justification when assumptions are unclear.
Researcher memory contains only actor questions, explicit progress reports and
published researcher replies. It is reset for each episode.

In `grounded` mode, a reply may contain supported study information, configured
preferences, uncertainty and clarifying questions. A second call to the same
simulator backend checks that factual assertions are supported and preferences
have not become fabricated constraints or mandatory requirements. This also
allows preference-only replies with no approved facts or fact citations.
Invalid citations and malformed replies fail closed. Rejected prose falls back
to selected fact text or the standard unknown response. The check is
model-based, not a guarantee of truth or persona fidelity.

In `extractive` mode, only selected approved fact text is published; persona
style and preference prose are not expressed. This remains a deterministic
control. Neither mode changes references, native scoring, actual execution
resources, the question limit, or the maximum facts per reply.

H is enforced by the controller's fact filtering, reference separation and
reply validation. Expertise never expands the fact pool. Optional methodological
advice must remain optional. Preferences are not permission to invent a study
history, actual budget, deadline, observed result, or solution.

## Preview and audit

From the project directory, using an environment with the package installed:

```bash
python -m personasciencebench persona \
  --episode prepared/pilot-v1/EPISODE/controller/episode.private.json \
  --config configs/persona_example.json
```

This operator-only command prints the resolved profile, identity prompt,
schema/renderer versions and a deterministic SHA-256 digest. It does not call
an API, load credentials or expose evaluator references. Pass the same config
with `--config configs/persona_example.json` to `run` or `serve`.

Each session saves `controller/persona.private.json` (or `persona.private.json`
under the output directory supplied to `serve`). It records the resolved profile,
identity prompt, digest and researcher policy version even when the actor asks no questions. Run configuration,
private researcher history/audit and API logs retain the context needed to
interpret an experiment. Keep these controller files outside the actor sandbox.

This is an independent implementation of structured persona prompt conditioning.
It does not import the MatrAIx population dataset or its full dimension schema.
Compare personas on the same tasks and model settings; report question counts
and grounding fallbacks along with scientific scores. Legacy configurations remain readable, but the new `persona-conditioning-only-v3`
prompt/checking policy is a distinct simulator condition from earlier runs.
Offline tests verify
routing and isolation; live persona fidelity requires a separate model study.
