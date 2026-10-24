#!/usr/bin/env bash
# Frozen MiniMax M3 actor/simulator trial with native adaptive thinking.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec .venv/bin/python scripts/run_main.py \
  --run-dir "${RUN_DIR:-runs/main/minimax-m3-adaptive/trial-1}" \
  --env-file "${ENV_FILE:-.env}" --workers "${WORKERS:-4}" \
  --provider nvidia --model nvidia/minimaxai/minimax-m3 \
  --reasoning-effort adaptive --collect-only --require-prepared "$@"
