#!/usr/bin/env bash
# A single persona: API server and benchmark workers share one allocation/node.
set -euo pipefail
ROOT=${PSB_VLLM_ROOT:?Submit using submit_qwen_local_campaign.sh}
ARM=${1:?Missing persona arm}
RUN_DIR=${PSB_LOCAL_RUN_DIR:?Missing run directory}
BASE="$ROOT/external/vllm-qwen"
cd "$ROOT"
LAUNCH="$RUN_DIR/server/${SLURM_JOB_ID}-${SLURM_RESTART_COUNT:-0}-$(date +%s)"
mkdir -p "$LAUNCH"
export VLLM_RUN_DIR="$LAUNCH" VLLM_HOST=127.0.0.1
export PSB_LOCAL_CONCURRENCY=8 PSB_LOCAL_CLIENT_TIMEOUT=1900 VLLM_MAX_MODEL_LEN=131072
export VLLM_TP=2 PSB_VLLM_DP=2
# Shared-storage imports, weight loading and GPU warmup can be very slow.
# Allow the frontend to wait for the engines, and give the outer launcher
# additional time for imports before that internal readiness timer starts.
export VLLM_ENGINE_READY_TIMEOUT_S=${VLLM_ENGINE_READY_TIMEOUT_S:-7200}
export PSB_VLLM_STARTUP_TIMEOUT_S=${PSB_VLLM_STARTUP_TIMEOUT_S:-10800}
export PSB_LOCAL_REQUEST_LOG="$LAUNCH/requests.jsonl"
# Different jobs sharing a node must not compete for ports.
export VLLM_PORT=$((20000 + SLURM_JOB_ID % 10000 * 4))
export PSB_LOCAL_API_PORT=$((VLLM_PORT + 1))
export PSB_LOCAL_API_KEY=$(cat "$BASE/api_key")
export OPENROUTER_API_KEY="$PSB_LOCAL_API_KEY"
export OPENROUTER_BASE_URL="http://127.0.0.1:$PSB_LOCAL_API_PORT/api/v1"
unset PSB_OPENROUTER_RATE_DIR PSB_OPENROUTER_RPM
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
server_pid='' adapter_pid='' benchmark_pid=''
cleanup() {
    for pid in "$benchmark_pid" "$adapter_pid" "$server_pid"; do
        [[ -z "$pid" ]] || kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 143' TERM INT
# Fail before launching 200 episodes if the allocated node cannot initialize CUDA.
"$BASE/venv/bin/python" -c 'import torch; torch.cuda.init(); assert torch.cuda.device_count()==4; print("CUDA ready:", torch.cuda.get_device_name(0))'
bash "$ROOT/scripts/serve_qwen_vllm.sh" > "$LAUNCH/stdout.log" 2> "$LAUNCH/stderr.log" &
server_pid=$!
export PSB_SERVER_PID=$server_pid
"$ROOT/.venv/bin/python" - <<'PY'
import os, time, httpx
started=time.monotonic()
timeout=int(os.environ['PSB_VLLM_STARTUP_TIMEOUT_S'])
deadline=started+timeout
next_report=started
print(f'Waiting up to {timeout}s for vLLM; engine readiness timeout '
      f"{os.environ['VLLM_ENGINE_READY_TIMEOUT_S']}s", flush=True)
while time.monotonic()<deadline:
    try:
        os.kill(int(os.environ['PSB_SERVER_PID']), 0)
    except ProcessLookupError:
        raise SystemExit('vLLM process exited before readiness; inspect server/stderr.log')
    if time.monotonic() >= next_report:
        print(f'vLLM initialization still pending: {time.monotonic()-started:.0f}s elapsed', flush=True)
        next_report=time.monotonic()+300
    try:
        r=httpx.get(f"http://127.0.0.1:{os.environ['VLLM_PORT']}/v1/models",
            headers={'Authorization': 'Bearer '+os.environ['PSB_LOCAL_API_KEY']},
            timeout=5, trust_env=False)
        if r.status_code==200: break
    except httpx.HTTPError: pass
    time.sleep(5)
else: raise SystemExit(f'Local vLLM startup timed out after {timeout}s; benchmark not started')
print(f'vLLM ready after {time.monotonic()-started:.0f}s', flush=True)
PY
"$ROOT/.venv/bin/python" "$ROOT/scripts/check_qwen_vllm.py"
"$BASE/venv/bin/python" "$ROOT/scripts/qwen_local_api.py" > "$LAUNCH/adapter.log" 2>&1 &
adapter_pid=$!
"$ROOT/.venv/bin/python" - <<'PY'
import os, time, httpx
for _ in range(60):
    try:
        r=httpx.get(os.environ['OPENROUTER_BASE_URL']+'/models',
            headers={'Authorization': 'Bearer '+os.environ['PSB_LOCAL_API_KEY']}, timeout=5, trust_env=False)
        if r.status_code==200: break
    except httpx.HTTPError: pass
    time.sleep(1)
else: raise SystemExit('Compatibility API failed to start')
PY
"$ROOT/.venv/bin/python" "$ROOT/scripts/check_qwen_local_load.py"
"$ROOT/.venv/bin/python" - <<'PY'
import json, os
from pathlib import Path
Path(os.environ['VLLM_RUN_DIR'],'repair_settings.json').write_text(json.dumps({
    'workers':8,'tensor_parallel_size':2,'data_parallel_size':2,'context_limit':131072,'client_timeout_seconds':1900,
    'adapter_total_deadline_seconds':1800,'upstream_attempt_timeout_seconds':800,
    'max_attempts':3,'retry_infrastructure':True,'model_reasoning':'low',
    'preserved_original_results':True,
    'engine_ready_timeout_seconds':int(os.environ['VLLM_ENGINE_READY_TIMEOUT_S']),
    'server_startup_timeout_seconds':int(os.environ['PSB_VLLM_STARTUP_TIMEOUT_S'])},indent=2)+'\n')
PY
"$ROOT/.venv/bin/python" "$ROOT/scripts/run_main.py" --run-dir "$RUN_DIR" \
    --workers 8 --arms "$ARM" --standalone-arm --provider openrouter \
    --model qwen/qwen3.8-27b --reasoning-effort low --judge-max-tokens 16384 --require-prepared --retry-infrastructure &
benchmark_pid=$!
# Abort the allocation if either server dies during the campaign.
while kill -0 "$benchmark_pid" 2>/dev/null; do
    kill -0 "$server_pid" 2>/dev/null && kill -0 "$adapter_pid" 2>/dev/null || exit 1
    sleep 5
done
wait "$benchmark_pid"
