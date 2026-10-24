#!/usr/bin/env bash
# One-time online installation. Serving subsequently uses local files only.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
BASE="$ROOT/external/vllm-qwen"
export UV_CACHE_DIR="$BASE/uv-cache"
mkdir -p "$BASE"
uv venv --allow-existing --python "$ROOT/.venv/bin/python" "$BASE/venv"
uv pip install --python "$BASE/venv/bin/python" 'vllm==0.30.0'
"$BASE/venv/bin/python" - "$BASE/model" <<'PY'
import sys
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen3.8-27B',
    revision='1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0',
    local_dir=sys.argv[1], max_workers=8)
PY
uv pip freeze --python "$BASE/venv/bin/python" > "$BASE/installed-requirements.txt"
