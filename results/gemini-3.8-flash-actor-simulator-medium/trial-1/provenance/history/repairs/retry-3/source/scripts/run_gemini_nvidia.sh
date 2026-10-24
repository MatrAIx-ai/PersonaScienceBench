#!/usr/bin/env bash
# One frozen Gemini actor/simulator trial. Final Astra grading is deferred.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec .venv/bin/python scripts/run_main.py \
  --run-dir "${RUN_DIR:-runs/main/gemini-3.8-flash-nvidia-medium/trial-1}" \
  --env-file "${ENV_FILE:-.env}" --workers "${WORKERS:-4}" \
  --provider nvidia --model gcp/google/gemini-3.8-flash \
  --reasoning-effort medium --collect-only --require-prepared "$@"
