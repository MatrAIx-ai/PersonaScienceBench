# EXP-Bench design track

The current track evaluates experimental designs rather than executing full experiments. It preserves native reference-coverage judging and a separate integrity monitor. Gold designs and evaluator prompts remain private.

## Conversion

Fetch the pinned public release with `scripts/expbench/download_exp_bench.py` and inspect it with `scripts/expbench/examine_exp_bench.py`. The [source manifest](../../manifests/expbench.json) records revisions and hashes.

```bash
.venv/bin/python scripts/expbench/build_full_design_catalog.py
```

This classifies exact public setup spans into researcher context and caches the model extraction. References and expected outcomes are not classifier inputs. Invalid references and unresolved question/reference mismatches are excluded. The catalog contains 440 design task cards; see [counts and readiness](../../reports/conversion_v2/conversion_summary.md).

## Current execution

Use a selected JSONL task file and a fresh output directory. The runner creates a public-only design workspace automatically when no repository map is supplied.

```bash
.venv/bin/python -m expbench.realistic run \
  --tasks data/design_catalog/tasks.jsonl --task SELECTED_TASK_ID \
  --config configs/full_persona_v2/exp.json \
  --env-file .env --parallel 2 --output runs/expbench-new
```

Use an explicit source task ID for each new episode. `configs/full_persona_v2/exp.json` uses Luna and the common approach/result review protocol. Persona off retains the simulator. Both TOML and planner-generated JSON configs are supported. Only the top-level persona block changes across matched persona arms.

The legacy standalone runner remains available with `configs/expbench/default.toml`; it is a separate optional-question condition. Do not pool its interactions with review handoffs. Full-workflow continuation is outside the validated design track.

## Records and interpretation

Each run retains task/config snapshots, actor and simulator messages, tool calls, sealed designs and grader outputs locally under ignored `runs/`. Report reference coverage and integrity results separately. Coverage is a design score, not evidence of successful execution or valid scientific conclusions.

The [completed full-persona report](../../reports/full_persona_v2/README.md) retains the historical 30-persona pilot and its traces.
