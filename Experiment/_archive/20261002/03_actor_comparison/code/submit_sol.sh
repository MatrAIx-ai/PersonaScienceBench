#!/usr/bin/env bash
set -euo pipefail
: "${RUN_DIR:?Set RUN_DIR}" "${DEPENDENCY:?Set DEPENDENCY}" "${PYTHONPATH:?Set pinned runtime PYTHONPATH}"
[[ "$DEPENDENCY" =~ ^afterany:[0-9]+$ ]] || exit 2
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
printf -v command '%q ' "$@"
job=$(sbatch --parsable --job-name=psb-gpt56sol --partition=general --account=general_group \
    --nodes=1 --ntasks=1 --cpus-per-task=30 --mem=128G --time=12:00:00 --dependency="$DEPENDENCY" \
    --output="$RUN_DIR/slurm-%j.out" --error="$RUN_DIR/slurm-%j.err" --wrap="$command")
printf '%s\n' "$job" > "$RUN_DIR/job_id"
printf '%s\n' "$job"
