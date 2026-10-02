#!/usr/bin/env bash
# Install Python dependencies and fetch pinned public sources/assets. No LLM calls.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
command -v uv >/dev/null
command -v bwrap >/dev/null || { echo 'Install bubblewrap on Linux first.' >&2; exit 1; }
uv sync --locked --extra api --extra annotations --extra actor --extra conversion --extra scientific-evaluation
if [[ ! -f .actor-venv/pyvenv.cfg ]]; then
  uv venv --python .venv/bin/python .actor-venv
fi
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
.venv/bin/python scripts/check_main.py
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench bixbench asibench sciconvbench
uv pip install --python .venv/bin/python --no-deps -e external/sources/asibench
.venv/bin/python scripts/acquire_conversion_assets.py bixbench
mapfile -t asi_tasks < <(.venv/bin/python -c "import csv; print('\n'.join(sorted({r['task_id'] for r in csv.DictReader(open('configs/main_run/selection.csv')) if r['source']=='asibench'})))")
.venv/bin/python scripts/acquire_conversion_assets.py asibench --tasks "${asi_tasks[@]}"
.venv/bin/python scripts/expbench/download_exp_bench.py
.venv/bin/python scripts/expbench/examine_exp_bench.py
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
