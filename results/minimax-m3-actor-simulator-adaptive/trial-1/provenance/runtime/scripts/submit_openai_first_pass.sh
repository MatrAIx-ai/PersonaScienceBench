#!/usr/bin/env bash
# Submit actual first-pass episodes. Reuse RUN_DIR to resume an interrupted job.
set -euo pipefail
WORKERS="${WORKERS:-35}"
CPUS_PER_TASK="${CPUS_PER_TASK:-$WORKERS}"
if [[ ! "$WORKERS" =~ ^[1-9][0-9]*$ || ! "$CPUS_PER_TASK" =~ ^[1-9][0-9]*$ ]] || (( WORKERS > CPUS_PER_TASK )); then
    printf 'WORKERS and CPUS_PER_TASK must be positive integers, with workers <= CPUs\n' >&2
    exit 2
fi
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${RUN_DIR:-$ROOT/runs/openai-astra-first-pass-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1
printf -v command '%q ' "$ROOT/.venv/bin/python" "$ROOT/scripts/run_openai_first_pass.py" --run-dir "$RUN_DIR" --workers "$WORKERS" --model gpt-6-astra --reasoning-effort low "$@"
dependency_args=()
if [[ -n "${DEPENDENCY:-}" ]]; then
    if [[ ! "$DEPENDENCY" =~ ^(afterany|afterok):[0-9]+$ ]]; then
        printf 'DEPENDENCY must be afterany:JOB_ID or afterok:JOB_ID\n' >&2
        exit 2
    fi
    dependency_args=("--dependency=$DEPENDENCY")
fi
job_id=$(sbatch "${dependency_args[@]}" --parsable --job-name=psb-astra-first --partition=general --account=general_group \
    --nodes=1 --ntasks=1 --cpus-per-task="$CPUS_PER_TASK" --mem=128G --time=12:00:00 \
    --chdir="$ROOT" --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err" \
    --wrap="$command")
printf '%s\n' "$job_id" > "$RUN_DIR/job_id"
printf 'Submitted job %s\nRun directory: %s\n' "$job_id" "$RUN_DIR"
