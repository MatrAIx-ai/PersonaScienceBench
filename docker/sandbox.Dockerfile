# Linux runtime for PersonaScienceBench on hosts without Bubblewrap (e.g. macOS).
# Follows docs/reproducibility.md: Linux, Python 3.12, the checked-in lockfiles and Bubblewrap.
# The repository is bind-mounted at /repo; its virtual environments live in Docker volumes.
FROM ubuntu:24.04

RUN apt-get update \
 && apt-get install --yes --no-install-recommends bubblewrap git ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /usr/local/bin/

# Keep the trusted base interpreter outside /root and outside the workspace:
# runtime.Sandbox mounts it read-only and refuses interpreters under the actor workspace.
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/opt/uv-cache
RUN uv python install 3.12 && git config --system --add safe.directory '*'

WORKDIR /repo
