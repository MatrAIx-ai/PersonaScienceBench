# Action-persona case study

This case study asks a narrow question: can simple, rule-based screening find persona profiles whose concrete preferences visibly change a model's requested scientific workflow? Profile selection is entirely static. Model outputs and judge scores do not decide which profiles enter the selected set.

## Selection rules

We sampled 300 records with seed `20260926` from the pinned 999-row public sample of `MatrAIx2026/MatrAIx_Persona_1M` at revision `8b1073ab23d0c0ba0928386a041bac55e5365ddc`. The selector retained a profile when it met all three rules:

1. **Concrete actions:** at least four populated fields can be rendered as instructions, such as a testing, debugging, commenting, or decision preference.
2. **Clear behavioral difference:** at least three instructions specify a direction rather than a neutral or context-dependent preference.
3. **Scientific-work relevance:** the directional instructions span at least two of decision-making, implementation, verification, and communication.

Only action instructions are injected. Demographic and identity attributes are excluded.

The static screen selected **131 of 300 profiles (43.7%)**. Its source composition shows a strong density bias:

| Source in public sample | Sampled | Selected |
|---|---:|---:|
| Synthetic | 121 | 121 |
| Stack Overflow | 38 | 6 |
| Real human survey | 4 | 4 |
| Wiki | 99 | 0 |
| Amazon | 22 | 0 |
| GSS | 15 | 0 |
| Prism | 1 | 0 |

The rules favor records with many populated action fields. Selection rates must therefore not be interpreted as differences in persona quality across sources.

## Controlled diagnostic

Each selected profile was tested on the same scientific coding-review scenario. GPT-6 Luna generated one response with the action instructions and one of three persona-off baseline responses. A blinded GPT-6 Luna judge saw the action rules and randomized response labels. It identified which response reflected the rules and rated whether the difference changed actions, decisions, checks, or workflow rather than wording alone. Generation and judging used `reasoning_effort=none`; 131 comparisons ran with 16 parallel workers.

A comparison qualified when the judge:

- attributed the rules to the conditioned response;
- rated the difference clear or prominent;
- found a behavioral difference rather than wording alone; and
- cited at least one piece of rule-linked evidence.

## Result

**73 of 131 selected profiles qualified (55.7%).** The judge selected the conditioned response in those 73 comparisons, selected neither response in 58, and never selected the persona-off response. Among all pairs, it rated 99 differences prominent, 25 clear, and 7 subtle. Some pairs can differ prominently for reasons unrelated to the supplied rules, so the 99 prominent ratings are not treated as persona effects.

| Stage | Profiles | Share |
|---|---:|---:|
| Initial deterministic sample | 300 | 100.0% |
| Passed static screen | 131 | 43.7% |
| Qualified in controlled diagnostic | 73 | 24.3% of sample; 55.7% of selected |

This establishes a usable pool for deeper experiments; it does not estimate an effect for the full MatrAIx population. The source is a small public viewer sample, the screen heavily favors dense synthetic records, the diagnostic uses one scenario, and the evaluator is model-based. Repeated tasks, models, and independent evaluation are needed before making a general claim about persona effectiveness.

## Reproduce

Download the pinned public sample as `external/persona_case_study/sample.parquet`. The selector verifies SHA-256 `c856d4d2d8e9832f3154d9856e5adbe9bf327328ab036069f8a4873992e03439` before running.

```bash
.venv/bin/python scripts/select_action_personas.py \
  --input external/persona_case_study/sample.parquet \
  --output data/persona_case_study/action_selection_v1 \
  --sample-size 300 \
  --seed 20260926

.venv/bin/python scripts/run_action_persona_case_study.py \
  --selected data/persona_case_study/action_selection_v1/selected.jsonl \
  --output runs/action-persona-case-study-YYYYMMDD \
  --env-file .env \
  --parallel 16
```

The selection artifacts, full responses, judgments, and private API records remain local under ignored `data/` and `runs/` paths. The repository publishes the protocol, aggregate result, and executable scripts without raw source profiles or private traces.
