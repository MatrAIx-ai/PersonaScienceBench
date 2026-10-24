#!/usr/bin/env bash
# Run inside a GPU allocation. No benchmark/client code is changed.
set -euo pipefail
ROOT=${PSB_VLLM_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}
BASE="$ROOT/external/vllm-qwen"
RUN_DIR=${VLLM_RUN_DIR:-$ROOT/runs/vllm-qwen-server}
mkdir -p "$RUN_DIR" "$BASE/cache"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
export VLLM_NO_USAGE_STATS=1 DO_NOT_TRACK=1
export XDG_CACHE_HOME="$BASE/cache" HF_HOME="$BASE/cache/huggingface"
export TRITON_CACHE_DIR="$BASE/cache/triton" TORCHINDUCTOR_CACHE_DIR="$BASE/cache/inductor"
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export VLLM_API_KEY=$(cat "$BASE/api_key")
PORT=${VLLM_PORT:-8000}
HOST=${VLLM_HOST:-0.0.0.0}
TP=${VLLM_TP:-4}
DP=${PSB_VLLM_DP:-1}
MAX_LEN=${VLLM_MAX_MODEL_LEN:-65536}
"$BASE/venv/bin/python" - "$RUN_DIR" "$PORT" "$TP" "$MAX_LEN" "$DP" <<'PY'
import json, os, pathlib, socket, sys
out, port, tp, length, dp = sys.argv[1:]
data = dict(model='Qwen/Qwen3.8-27B', revision='1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0',
    base_url=f"http://{'127.0.0.1' if os.environ.get('VLLM_HOST') == '127.0.0.1' else socket.gethostname()}:{port}/v1", job_id=os.environ.get('SLURM_JOB_ID'),
    tensor_parallel_size=int(tp), data_parallel_size=int(dp), gpu_count=int(tp)*int(dp), max_model_len=int(length), dtype='bfloat16',
    vllm_version='0.30.0', status='starting', key_file='external/vllm-qwen/api_key')
pathlib.Path(out, 'server.json').write_text(json.dumps(data, indent=2)+'\n')
PY
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$RUN_DIR/gpus.csv"
exec "$BASE/venv/bin/vllm" serve "$BASE/model" \
    --served-model-name Qwen/Qwen3.8-27B qwen/qwen3.8-27b qwen/qwen3.8-27b:free \
    --host "$HOST" --port "$PORT" --dtype bfloat16 \
    --tensor-parallel-size "$TP" --data-parallel-size "$DP" \
    --data-parallel-rpc-port "$((PORT + 2))" --max-model-len "$MAX_LEN" \
    --max-num-seqs "${PSB_LOCAL_CONCURRENCY:-32}" --max-num-batched-tokens 8192 \
    --gpu-memory-utilization 0.90 --language-model-only \
    --default-chat-template-kwargs '{"reasoning_effort":"low"}' \
    --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml
