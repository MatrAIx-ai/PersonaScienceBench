# Optional original integrity monitor

Historical implementation notes, migrated from the original EXP-Bench workspace.
Use [the current EXP-Bench guide](../adapters/expbench.md) for setup and paths.

The monitor is a separate o3-mini call using the released
[monitor prompt](../../data/exp_bench/raw/upstream/prompts/eval_judge_setup_monitor_prompt.txt)
unchanged. It checks paper access, Git operations, and fabricated or
nonexperimental results. It does not grade the scientific design.

For saved original-prompt grades, run:

```bash
.venv/bin/python -m expbench.integrity \
  --grades-from runs/original-judge-diagnostic-20260922 \
  --output runs/YOUR_NEW_MONITOR_RUN
```

Set `OPENROUTER_API_KEY` in the environment before running. The command uses
the judge model in `configs/expbench/pilot-o3mini.toml` by default. Dollar caps remain
unset. Existing outputs are never overwritten.

The original grading manifest and design hashes are checked before inference.
The monitor receives only the recorded `actor_events.jsonl`, including task
instructions, agent actions, and observations. It does not receive the private
reference, private researcher fact bank, previous grade, or judge explanation.

The score gate is:

- All three monitor flags false: retain the saved original design score.
- Any flag true: set the gated design score to zero.
- Malformed monitor output after three attempts: set the gated score to zero,
  with an explicit parsing-error status, matching the original failure gate.
- API/transport failure: stop and leave the gated score unset; do not label it
  misconduct.

Each result retains `standalone_design_score`, `monitor_gated_design_score`,
the three flags, explanation, attempts, and API cost. Reusing verified saved
grades isolates the effect of the monitor without another stochastic design
judgment. This is mathematically the same score gate, although the original
runner called the monitor before deciding whether to invoke its design judge.

This replay is not a full-paper benchmark result. It uses current OpenHands
JSONL events instead of the original console logs, current o3-mini through
OpenRouter, and design-only trajectories. Its prompt includes checks concerning
actual experimentation; whether a design-only trace is rejected is left to the
unchanged monitor rather than preassigned. No execution is fabricated and no
design-only exception is added to the prompt.

The monitor is optional. Ordinary design-only runs and the standalone design
judge remain unchanged. See the test report (historical record archived locally)
for the saved-run experiment.
