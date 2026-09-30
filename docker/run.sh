#!/usr/bin/env bash
# Run a command in the Linux sandbox image with the repository mounted at /repo.
# Linux virtual environments live in Docker volumes so they never replace the host's .venv.
# Bubblewrap needs user namespaces and its own /proc inside the container, hence the
# unconfined seccomp/AppArmor profiles and system paths; the container gets no extra capabilities.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
tty=()
[ -t 0 ] && tty=(-it)
exec docker run --rm "${tty[@]}" \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  -v "$repo":/repo -v psb-venv:/repo/.venv -v psb-actor-venv:/repo/.actor-venv -v psb-uv-cache:/opt/uv-cache \
  -e PERSONASCIENCEBENCH_SOURCE_ROOT=/repo/external/sources \
  psb-sandbox:latest "$@"
