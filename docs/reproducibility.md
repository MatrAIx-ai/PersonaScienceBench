# Setup and remote migration

Use Linux, Python 3.12, the checked-in lockfiles and Bubblewrap. The repository is a source checkout; `configs/` and `manifests/` are part of the runtime layout.

## Environment

```bash
sudo apt-get update
sudo apt-get install --yes --no-install-recommends bubblewrap
uv sync --locked --extra test --extra api --extra annotations --extra actor --extra conversion --extra scientific-evaluation
uv run --locked python -m venv .actor-venv
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
uv run --locked python -m personasciencebench check-runtime --actor-python .actor-venv
```

The runtime probe checks host isolation support; it does not call a model. There is no unsandboxed fallback. Recreate environments after relocation. The historical batch scheduler hardcodes `external/runtime/bubblewrap-local/usr/bin/bwrap`; resolve that host-specific requirement before using it. The general runner also supports the documented `PERSONASCIENCEBENCH_BWRAP` override.

Create `.env` from `.env.example` and configure `OPENROUTER_API_KEY` on the remote host. Credentials remain ignored. The [frozen configs](../configs/full_persona_v2) record the completed study's model/settings, not a guarantee of future provider availability.

## Existing results and exact personas

All 310 readable traces and final tables are in [the published report](../reports/full_persona_v2/README.md). Verify and reconstruct raw identity files without API calls:

```bash
python3 scripts/restore_full_persona_cohort.py --check
python3 scripts/restore_full_persona_cohort.py
```

The second command requires a new output directory. Raw API/event logs, execution artifacts, source inputs and conversion caches are ignored local files. Transfer the directories listed in the [handoff](TEAM_HANDOFF.md) if those records are needed. A clone alone is sufficient to inspect the published conversations and prompts.

## Source acquisition and conversion

Source revisions and asset hashes live in `manifests/`. Reuse transferred source data or acquire the retained sources:

```bash
uv run --locked python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench bixbench asibench sciconvbench
uv run --locked python scripts/acquire_conversion_assets.py bixbench
uv run --locked python scripts/acquire_conversion_assets.py asibench --tasks astronomy.nbody_close_encounters biology.scrna_seq_analysis materials.relaxation_mode_recovery math.sigma_linear_diophantine
uv run --locked python scripts/expbench/download_exp_bench.py
```

Acquisition downloads pinned data and can be large. Install ASI from its pinned checkout for native evaluation:

```bash
uv pip install --python .venv/bin/python --no-deps -e external/sources/asibench
```

When transferred catalogs are unavailable, rebuild EXP task cards and conversion catalogs:

```bash
uv run --locked python scripts/expbench/build_full_design_catalog.py
uv run --locked python scripts/convert_benchmark_catalogs.py
uv run --locked python scripts/prepare_conversion_runtimes.py --benchmarks asibench
```

EXP context extraction and source advice classification may use model calls and cached annotations. Reuse existing caches to avoid repeating them. The converter defaults to the four retained source adapters; EXP is included from its separately built design catalog. Legacy heavy adapters require explicit selection and are not part of the current study.

## New runs

Read the [paper plan](design/benchmark_paper_plan.md) before scheduling. The 200-task manifest and expanded six-persona, three-repeat launcher are not yet implemented. `scripts/run_persona_benchmarks.py` preserves the prior scheduler and assumes a historical 25-task build; do not mistake it for the planned study.

Prepare new public task workspaces on the destination host, using explicit source task IDs and selections. Recorded `prepared` packages and the old scheduler's input manifests contain absolute paths. The shared runner supports Discovery/Bix/ASI, `personasciencebench.sciconv_runner` handles SciConv, and `expbench.realistic` handles EXP. Keep independent cases parallel, retain complete traces, and use a fresh output directory for every experiment.

## Offline development checks

```bash
uv run --locked python scripts/check_repository.py
uv run --locked python -m pytest -q -rs
```

The repository checker scans distributable files and links without opening ignored credentials. Offline tests do not call paid models. Tests needing downloaded sources or SDK dependencies skip when unavailable; set `PERSONASCIENCEBENCH_SOURCE_ROOT` to include acquired sources. Current CI is defined in [checks.yml](../.github/workflows/checks.yml).
