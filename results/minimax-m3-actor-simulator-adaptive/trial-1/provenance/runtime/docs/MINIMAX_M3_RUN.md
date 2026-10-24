# MiniMax M3 adaptive thinking

This trial uses MiniMax M3 for both actor and simulator on the frozen 200-question
panel, under all five persona settings (1,000 episodes). Native adaptive thinking
is a mode, not a medium reasoning-effort level. DeepSeek is on hold.

The exact API model is `nvidia/minimaxai/minimax-m3`, currently resolved to
`dynamo/minimaxai/minimax-m3-sglang`. The transport sends
`chat_template_kwargs: {"thinking_mode": "adaptive"}` and omits
`reasoning_effort` on the wire. The harness configuration uses `adaptive` as the
policy identifier. See the [native API reference](https://docs.api.nvidia.com/nim/reference/minimaxai-minimax-m3-infer).
Catalog capability fields are unspecified on this deployment; the preflight
records that fact and the documentation source separately. Saved live probes
verify named tools, continuation after a tool result, JSON, the actual researcher
decision schema, and EXP structured replies. A changed deployment requires
reverification.

With setup complete, downloaded source assets, working Bubblewrap isolation,
and `NVIDIA_API_KEY` configured privately in the dotenv file:

```bash
.venv/bin/python scripts/check_main.py
.venv/bin/python scripts/restore_main_preparation.py \
  --run-dir runs/main/minimax-m3-adaptive/trial-1
ENV_FILE=/home/sherryj/Desktop/.env WORKERS=4 bash scripts/run_minimax_m3.sh
```

Restore into a fresh run directory only. For resume, run the final command again;
the coordinator retains completed attempts and checks the run identity. Failed
infrastructure attempts require an explicit `--retry-infrastructure` repair pass,
which preserves attempt history. Scientific non-submissions remain recorded.

The launcher collects episodes without final judge calls. Final evaluation uses
the shared Astra/low native graders in a separate judging stage. Configuration,
API capability metadata, preparation receipts, code hashes, attempts, traces,
and submissions are kept under `runs/main/minimax-m3-adaptive/trial-1/`.
Probe records under `provenance/` are private and are not public conversation
exports. Validate and export a complete tracked collection before upload, as
described in the [team handoff](TEAM_HANDOFF.md).

## Authorized output-limit repair

The original trial used actor/simulator output caps of 12,288/8,192 tokens.
During the execution-failure repair pass, the user authorized higher limits:
32,768 for the actor and 16,384 for the simulator. Both caps were accepted by
live probes on the configured deployment. This is an experimental setting
change and must be labeled in repaired results.

`generation_limits.json` is bound to this run's manifest checksum. New
actor/simulator clients load it once; clients already running retain their
loaded limits. Original configs and attempts are retained, and actual API logs
record the effective cap, original cap, policy ID, and policy checksum. EXP
budget reservations use the effective cap. The common judge is unaffected.
Source snapshots and the installation-time episode states are in `provenance/`.

`scripts/finish_minimax_token_repairs.sh` waits for the current execution repair
pass, then runs one further pass only for recorded truncations under the old
limits. Non-submissions, completed episodes, and failures already occurring at
the higher cap are excluded from that follow-up. It archives the selected
targets before starting them. This workflow makes no grading or upload calls.
