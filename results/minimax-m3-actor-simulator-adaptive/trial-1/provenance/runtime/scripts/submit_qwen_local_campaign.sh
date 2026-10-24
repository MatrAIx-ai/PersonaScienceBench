#!/usr/bin/env bash
# Submit one independent combined GPU/server/benchmark job per persona.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PSB_VLLM_ROOT="$ROOT"
BASE="$ROOT/external/vllm-qwen"
CAMPAIGN=${CAMPAIGN_DIR:-$ROOT/runs/qwen38-local-trial-1}
PREPARED=${PREPARED_DIR:-$ROOT/runs/qwen38-27b-free-trial-1/prepared}
mkdir -p "$CAMPAIGN"
[[ -x "$BASE/venv/bin/vllm" && -f "$BASE/model/model.safetensors.index.json" ]] || exit 1
if [[ ! -f "$BASE/api_key" ]]; then
    (umask 077; "$ROOT/.venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$BASE/api_key")
fi
arms=("${@}")
[[ ${#arms[@]} -gt 0 ]] || arms=(persona_off candidate_155 candidate_001 candidate_003 candidate_046)
for arm in "${arms[@]}"; do
    case "$arm" in persona_off|candidate_155|candidate_001|candidate_003|candidate_046) ;; *) exit 2;; esac
    export PSB_LOCAL_RUN_DIR="$CAMPAIGN/$arm"
    mkdir -p "$PSB_LOCAL_RUN_DIR"
    [[ -e "$PSB_LOCAL_RUN_DIR/prepared" ]] || ln -s "$PREPARED" "$PSB_LOCAL_RUN_DIR/prepared"
    # r001 reproduced CUDA cuInit error 3; o001 passed. Exclude the failing node.
    args=(--parsable --job-name="qwen-$arm" --partition="${PARTITION:-general}"
        --nodes=1 --ntasks=1 --gres=gpu:4 --constraint="${GPU_CONSTRAINT:-h200|h100|a100}" --cpus-per-task="${CPUS_PER_TASK:-32}" --mem=384G
        --time="${TIME_LIMIT:-12:00:00}" --exclude="${EXCLUDE_NODES:-r001}" --chdir="$ROOT"
        --output="$PSB_LOCAL_RUN_DIR/slurm-%j.out" --error="$PSB_LOCAL_RUN_DIR/slurm-%j.err")
    [[ -z ${ACCOUNT:-} ]] || args+=(--account="$ACCOUNT")
    job=$(sbatch "${args[@]}" "$ROOT/scripts/run_qwen_local_job.sh" "$arm")
    printf '%s\n' "$job" > "$PSB_LOCAL_RUN_DIR/job_id.txt"
    printf '%s\t%s\n' "$arm" "$job" | tee -a "$CAMPAIGN/submissions.tsv"
done
