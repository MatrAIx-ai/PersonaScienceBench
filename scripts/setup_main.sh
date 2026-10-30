#!/usr/bin/env bash
# Install Python dependencies and fetch pinned public sources/assets. No LLM calls.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ${1:-} == --help || ${1:-} == -h ]]; then
  echo 'Usage: bash scripts/setup_main.sh'
  echo 'Requires Linux, uv, Git and Bubblewrap. Installs Python 3.12 environments and selected public assets; makes no model calls.'
  exit 0
fi
if [[ $# -ne 0 ]]; then
  echo 'Unknown argument. Use bash scripts/setup_main.sh --help.' >&2
  exit 2
fi
trap 'echo "Setup stopped at line $LINENO. Fix the error above and rerun the same command; verified downloads are reused." >&2' ERR
[[ $(uname -s) == Linux ]] || { echo 'Evaluation requires Linux with Bubblewrap isolation.' >&2; exit 1; }
command -v uv >/dev/null || { echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' >&2; exit 1; }
command -v git >/dev/null || { echo 'Install Git before fetching benchmark sources.' >&2; exit 1; }
command -v "${PERSONASCIENCEBENCH_BWRAP:-bwrap}" >/dev/null || { echo 'Install Bubblewrap or set PERSONASCIENCEBENCH_BWRAP to its executable.' >&2; exit 1; }
# Runtime intentionally searches only system paths unless an explicit path is set.
export PERSONASCIENCEBENCH_BWRAP
PERSONASCIENCEBENCH_BWRAP=$(command -v "${PERSONASCIENCEBENCH_BWRAP:-bwrap}")

echo '[1/6] Installing the locked controller environment (Python 3.12)...'
uv sync --locked --python 3.12 --extra api --extra annotations --extra actor --extra conversion --extra scientific-evaluation
if [[ ! -f .actor-venv/pyvenv.cfg ]]; then
  # Resolve uv's interpreter symlinks before creating the sandbox environment.
  actor_base=$(.venv/bin/python -c 'import os, sys; print(os.path.realpath(sys._base_executable))')
  "$actor_base" -m venv .actor-venv
fi
# Test the actual isolation and interpreter before large dependency/asset downloads.
echo '[2/6] Checking Bubblewrap isolation and the actor interpreter...'
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
.venv/bin/python scripts/check_main.py

echo '[3/6] Fetching pinned benchmark sources...'
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench bixbench asibench sciconvbench
uv pip install --python .venv/bin/python --no-deps -e external/sources/asibench

echo '[4/6] Acquiring selected BixBench capsules and ASI-Bench instances...'
.venv/bin/python scripts/acquire_conversion_assets.py bixbench --selection configs/main_run/selection.csv
.venv/bin/python scripts/acquire_conversion_assets.py asibench --selection configs/main_run/selection.csv

echo '[5/6] Restoring the pinned EXP-Bench source assets...'
.venv/bin/python scripts/expbench/download_exp_bench.py
.venv/bin/python scripts/expbench/examine_exp_bench.py

echo '[6/6] Verifying the installed runtime...'
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
echo 'Setup complete. Configure .env and restore the frozen tasks as described in README.md.'
echo "For subsequent commands, keep PERSONASCIENCEBENCH_BWRAP set if using a non-system executable: $PERSONASCIENCEBENCH_BWRAP"
