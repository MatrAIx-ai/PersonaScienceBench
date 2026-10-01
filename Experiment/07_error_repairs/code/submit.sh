#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
: "${SOURCE_RUN:?Set SOURCE_RUN}" "${RUN_DIR:?Set RUN_DIR}" "${DEPENDENCY:?Set DEPENDENCY}"
[[ "$DEPENDENCY" =~ ^afterany:[0-9]+$ ]] || exit 2
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONUNBUFFERED=1
printf -v command '%q ' "$ROOT/.venv/bin/python" "$ROOT/Experiment/07_error_repairs/code/run_repair.py" --source-run "$SOURCE_RUN" --run-dir "$RUN_DIR" --workers 20
job=$(sbatch --parsable --job-name=psb-astra-repair --partition=general --account=general_group \
 --nodes=1 --ntasks=1 --cpus-per-task=30 --mem=128G --time=12:00:00 --dependency="$DEPENDENCY" \
 --chdir="$ROOT" --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err" --wrap="$command")
printf '%s\n' "$job" > "$RUN_DIR/job_id"
printf '%s\n' "$job"
