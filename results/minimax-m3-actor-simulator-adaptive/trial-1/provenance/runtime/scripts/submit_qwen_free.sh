#!/usr/bin/env bash
# Resume after a daily quota reset by clearing the reviewed fatal_api.json and passing --retry-infrastructure.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export RUN_DIR="$ROOT/runs/qwen38-27b-free-trial-1"
export WORKERS=30 CPUS_PER_TASK=30 PARTITION=general TIME_LIMIT=12:00:00
export PSB_OPENROUTER_RATE_DIR="$RUN_DIR/rate_state" PSB_OPENROUTER_RPM=18
bash "$ROOT/scripts/submit_main.sh" 1 --provider openrouter --model qwen/qwen3.8-27b:free --reasoning-effort low --judge-max-tokens 16384 --require-prepared "$@"
