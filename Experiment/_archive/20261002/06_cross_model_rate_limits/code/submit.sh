#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_DIR="${RUN_DIR:-$ROOT/runs/luna-rate-probe-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
printf -v command '%q ' "$ROOT/.venv/bin/python" "$ROOT/Experiment/06_cross_model_rate_limits/code/probe.py" --output "$RUN_DIR"
job=$(sbatch --parsable --job-name=psb-luna-limit-probe --partition=general --account=general_group \
    --nodes=1 --ntasks=1 --cpus-per-task=30 --mem=128G --time=00:30:00 \
    --chdir="$ROOT" --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err" --wrap="$command")
printf '%s\n' "$job" > "$RUN_DIR/job_id"
printf 'Job: %s\nRun: %s\n' "$job" "$RUN_DIR"
