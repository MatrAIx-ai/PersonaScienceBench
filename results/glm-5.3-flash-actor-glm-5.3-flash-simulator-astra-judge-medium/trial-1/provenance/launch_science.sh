#!/bin/bash
# Usage: launch_science.sh <tag> <actor-model-id> [extra run_main args...]
# Runs the frozen 200-question × 5-setting main run with actor = researcher = target (medium),
# judge = GPT-6 Astra (low) through the NVIDIA inference gateway via the local adapter.
set -euo pipefail
TAG=$1; MODEL=$2; shift 2
R=<HOME>/PersonaScienceBench
S=<HOME>/nvgw-campaign/science
set -a; . $S/adapter.env; set +a
export OPENROUTER_BASE_URL="http://127.0.0.1:${PSB_LOCAL_API_PORT}/api/v1"
export PSB_LOCAL_CLIENT_TIMEOUT=1900
cd $R
RUN_DIR="$R/runs/main/${TAG}-self-astra-${RUN_SUFFIX:-trial-1}"
exec .venv/bin/python scripts/run_main.py \
  --run-dir "$RUN_DIR" --workers "${WORKERS:-30}" --provider openrouter \
  --model openai/gpt-6-astra --reasoning-effort low \
  --actor-model "$MODEL" --actor-reasoning-effort medium \
  --researcher-model "$MODEL" --researcher-reasoning-effort medium \
  --require-prepared "$@"
