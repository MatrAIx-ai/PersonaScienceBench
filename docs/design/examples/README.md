# MatrAIx profile example

[matraix_persona_0157.yaml](matraix_persona_0157.yaml) is a complete, unchanged upstream development-sample profile with 1,290 dimensions.

- [Pinned source](https://raw.githubusercontent.com/MatrAIx-ai/MatrAIx-Persona-8B/3633d8dab149a9482a71b024418a49ae828cc941/persona/datasets/matraix-persona-dev-sample/persona_0157.yaml)
- Source revision: `3633d8dab149a9482a71b024418a49ae828cc941`
- SHA-256: `d1db5d05d309bf378c2d6f69e93525dff311b632f7ac599f8bdc2e0e88d984a5`
- Retrieved: 2026-09-24
- Upstream source label: `real_human_survey`

This is the official repository's development example, not a record newly extracted from the current full-release Parquet. Its provenance refers to the parent persona pool. Source labels and attributed expertise are not independent verification of competence.

## Field versus level

The source stores a primary field in `domain`, a specialty in `subject_specialty`, and separate proficiency values in `fam_*`, `skill_*`, and `tool_*` dimensions. For this actual record:

| Field | Original value |
| --- | --- |
| domain | Social Sciences |
| subject_specialty | Electrical work |
| academic_field | Interdisciplinary |
| fam_statistics | Aware |
| fam_sociology | None |
| skill_mathematics | Intermediate |
| skill_statistical_modeling | Beginner |
| skill_coding | None |
| tool_python | Never used |

These combinations are preserved exactly. The broad domain does not establish expert proficiency. Mathematics is represented by `skill_mathematics`; it is not a value in the source's 16-category `domain` list. The proposed domain/methodological/computational summary levels are not native fields in this example.

See the [source schema](https://github.com/MatrAIx-ai/MatrAIx-Persona-8B/blob/3633d8dab149a9482a71b024418a49ae828cc941/persona/schema/dimensions.json) and [dataset provenance and terms](https://huggingface.co/datasets/MatrAIx2026/MatrAIx_Persona_1M).
