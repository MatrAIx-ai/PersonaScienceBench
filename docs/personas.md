# Full-profile researcher personas

The current experiment injects the **complete rendered MatrAIx identity into the simulator system prompt**. Actor and judge do not receive the profile. Persona off keeps the same simulator and common protocol but omits the identity. Both conditions can use general knowledge; evaluator references stay private.

## Exact cohort and prompts

The [cohort manifest](../configs/full_persona_v2/cohort.json) records all 30 IDs, source types, selection provenance, pinned renderer version and prompt hashes. [Published profiles](../reports/full_persona_v2/profiles) contain the exact injected identity inside the `text` fence. Run `python3 scripts/restore_full_persona_cohort.py --check` to verify them, or omit `--check` to reconstruct raw prompt files on a fresh checkout.

The original 300-profile sample was rescreened into 180 eligible profiles; a source-balanced, behaviorally diverse 30-profile cohort was selected without model-score selection. All usable fields retained by the pinned upstream renderer were injected, not just the attributes used for selection. Original source records and field-disposition audits remain in the local cohort directory; the handoff identifies transfer paths.

## Configuration

Start from [the recorded shared config](../configs/full_persona_v2/shared.json) or [EXP config](../configs/full_persona_v2/exp.json). Set the top-level persona for each arm:

```python
from pathlib import Path
import json

config = json.loads(Path("configs/full_persona_v2/shared.json").read_text())
config["persona"] = {
    "enabled": True,
    "id": "candidate_148",
    "version": "full-persona-v2",
    "system_prompt": Path("data/persona_case_study/full_persona_v2/prompts/candidate_148.md").read_text(),
}
# Save this operator-side configuration for a fresh run.
```

Use `{"enabled": false}` for persona off. Keep the same `collaboration` switches (`unrestricted_knowledge`, `embody_identity`, `volunteer_information`) in both arms. Do not truncate, summarize or project the identity by task domain. Changing which profiles are selected does not change their prompt contents.

`src/personasciencebench/persona.py` returns a supplied `system_prompt` verbatim. `collaboration.py` places it in the researcher's system identity; SciConv appends it to the native simulated-user system prompt. Episode records retain the resolved persona and full API messages.

## Interpretation

Profile preferences influence communication and decisions; they do not alter native task requirements or authorize fabricated study facts. Some original profiles contain conflicting attributes. Evaluate observable behavior against the actual prompt, not a demographic label or an assumed expertise level. The [case studies](../reports/full_persona_v2/case_studies.md) show supported links and counterexamples.

The optional structured science-persona API and its [compatibility examples](../examples/science_personas/README.md) remain for tests and existing integrations. They were not used for the completed full-profile study or the proposed follow-up. The sole current experiment plan is [the paper plan](design/benchmark_paper_plan.md).
