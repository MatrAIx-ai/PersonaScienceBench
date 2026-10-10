#!/usr/bin/env bash
set -euo pipefail
: "${RUN_DIR:?Set the prepared run directory}"
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
printf -v command '%q ' "$ROOT/.venv/bin/python" "$RUN_DIR/runtime/run_case_study.py" --run-dir "$RUN_DIR"
job=$(sbatch --parsable --job-name=psb-sciconv-new-off --partition=general --account=general_group \
 --nodes=1 --ntasks=1 --cpus-per-task=35 --mem=128G --time=12:00:00 \
 --chdir="$ROOT" --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err" --wrap="$command")
printf '%s\n' "$job" > "$RUN_DIR/job_id"
printf '%s\n' "$job"
