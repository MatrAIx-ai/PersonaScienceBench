#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
BASE="$ROOT/external/vllm-qwen"
export PSB_VLLM_ROOT="$ROOT"
export VLLM_RUN_DIR=${VLLM_RUN_DIR:-$ROOT/runs/vllm-qwen-server}
mkdir -p "$VLLM_RUN_DIR" "$BASE"
if [[ ! -f "$BASE/api_key" ]]; then
    (umask 077; "$ROOT/.venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$BASE/api_key")
fi
[[ -x "$BASE/venv/bin/vllm" && -f "$BASE/model/model.safetensors.index.json" ]] || {
    echo 'Install first: bash scripts/setup_qwen_vllm.sh' >&2; exit 1;
}
"$ROOT/.venv/bin/python" - "$BASE/model" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
index = json.loads((root / 'model.safetensors.index.json').read_text())
missing = [p for p in set(index['weight_map'].values())
           if not (root / p).is_file() or (root / p).stat().st_size == 0]
if missing:
    raise SystemExit(f'Incomplete model download; missing shards: {missing}')
PY
args=(--parsable --job-name=qwen-vllm --partition="${PARTITION:-general}"
    --nodes=1 --ntasks=1 --gres=gpu:h200:4 --cpus-per-task=30 --mem=256G
    --time="${TIME_LIMIT:-12:00:00}" --chdir="$ROOT"
    --output="$VLLM_RUN_DIR/slurm-%j.out" --error="$VLLM_RUN_DIR/slurm-%j.err")
[[ -z ${ACCOUNT:-} ]] || args+=(--account="$ACCOUNT")
[[ -z ${DEPENDENCY:-} ]] || args+=(--dependency="$DEPENDENCY")
job=$(sbatch "${args[@]}" "$ROOT/scripts/serve_qwen_vllm.sh")
printf '%s\n' "$job" | tee "$VLLM_RUN_DIR/job_id.txt"
