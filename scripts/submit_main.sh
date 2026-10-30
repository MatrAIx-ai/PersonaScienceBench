#!/usr/bin/env bash
# Submit one trial; use DEPENDENCY=afterok:JOB_ID to sequence trials.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TRIAL=${1:?Usage: bash scripts/submit_main.sh TRIAL_NUMBER}
[[ $TRIAL =~ ^[1-9][0-9]*$ ]] || { echo 'Trial must be positive' >&2; exit 2; }
WORKERS=${WORKERS:-30}
[[ $WORKERS =~ ^[1-9][0-9]*$ ]] || exit 2
RUN_DIR=${RUN_DIR:-$ROOT/runs/main/trial-$TRIAL}
mkdir -p "$RUN_DIR"
args=(--parsable --job-name="psb-trial-$TRIAL" --nodes=1 --ntasks=1
      --cpus-per-task="$WORKERS" --mem=128G --time="${TIME_LIMIT:-12:00:00}"
      --chdir="$ROOT" --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err")
[[ -z ${PARTITION:-} ]] || args+=(--partition="$PARTITION")
[[ -z ${ACCOUNT:-} ]] || args+=(--account="$ACCOUNT")
[[ -z ${DEPENDENCY:-} ]] || args+=(--dependency="$DEPENDENCY")
printf -v command '%q ' "$ROOT/.venv/bin/python" "$ROOT/scripts/run_main.py" --run-dir "$RUN_DIR" --workers "$WORKERS" "${@:2}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
job=$(sbatch "${args[@]}" --wrap="$command")
printf '%s\n' "$job" > "$RUN_DIR/job_id.txt"
printf '%s\n' "$job"
