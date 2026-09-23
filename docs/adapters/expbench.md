# EXP-Bench: migrated experiment-design track

EXP-Bench is included in this checkout under `src/expbench/`. It preserves the
previous implementation as a separate design-only track, with its own schema,
researcher, OpenHands actor and evaluation commands. It is not one of the four
`personasciencebench.registry` adapters and does not use their domain/task persona
router. It now accepts a fixed shared A–G profile through TOML; the profile
conditions fact selection while published replies remain extractive. Consolidating its interfaces is future work; migration does not change
its scientific task or historical scores.

## What is included

| Path | Contents |
| --- | --- |
| `src/expbench/` | Early pilot, realistic v3.1 workflow, original-input control, scoped researcher, coverage judge, integrity monitor |
| `configs/expbench/` | Historical actor/simulator/judge TOML configurations, including the Sonnet/o3-mini comparison |
| `scripts/expbench/` | Pinned data acquisition, task-card building, repository staging inputs and comparison/report utilities |
| `tests/expbench/` | Migrated offline and isolation checks |
| `manifests/expbench.json` | Pinned upstream annotation/prompt URLs, revisions and 59 file hashes |
| `manifests/expbench_repositories.json` | Five fixed repository snapshot revisions used for preparation |
| `reports/expbench/` | Existing measured comparisons, diagnostics, interaction example and submitted design |
| `data/` | Local-only raw annotations, references, task cards and code snapshots; ignored |
| `runs/expbench/` | Local-only original runs and traces; ignored |

The five reviewed task cards cover JaxMARL, QuaRot, CycleNet, MogaNet and SineNet.
The raw source snapshot contains 461 queries from 51 papers; that is not a claim
that every query has an interactive conversion.

## Setup and rebuild

From this repository's root:

```bash
uv sync --locked --extra test --extra api --extra annotations --extra actor
uv run --locked python scripts/expbench/download_exp_bench.py
uv run --locked python scripts/expbench/examine_exp_bench.py
uv run --locked python scripts/expbench/build_design_pilot.py
uv run --locked python scripts/expbench/build_realistic_pilot.py
uv run --locked expbench validate
uv run --locked expbench list
```

The downloader uses the committed source manifest; it does not resolve upstream
`main` or a latest dataset revision. Existing mismatched files fail verification.
The build steps are offline, do not call models, and write evaluator-private
references into the ignored `data/` tree. Do not mount that tree into an actor.

For isolated repository exploration, acquire the five pinned code snapshots and
prepare masked workspaces:

```bash
uv run --locked python scripts/expbench/fetch_realistic_repositories.py
uv run --locked expbench-realistic prepare \
  --workspace-map data/realistic_pilot/source_repositories.json \
  --output data/realistic_pilot/staged-new
```

The snapshots are the historical preparation commits, not recovered original
paper-run revisions. Only approved code/configuration files are retained, and
source-specified masking happens during staging. Repository download/staging is
not scientific execution. Existing generated maps contain machine-local paths;
regenerate them on a different checkout or machine.

## Offline validation and a design-only run

```bash
uv run --locked python -m pytest tests/expbench -q
uv run --locked expbench-realistic run --mode mock \
  --task neurips2024/97649/0 --output runs/expbench/mock-check
```

The tests require the actor extra and prepared task cards; they skip clearly if
these are missing. The real isolation test and realistic mock run require Linux,
Bubblewrap and permitted namespaces. Mock responses are scripted and are never
reported as benchmark performance.

A live run makes paid model calls:

```bash
uv run --locked expbench-realistic run --mode live \
  --config configs/expbench/pilot-o3mini.toml \
  --workspace-map data/realistic_pilot/staged-new/workspaces.json \
  --env-file .env --output runs/expbench/design-new
```

Review the selected config's model IDs, prices and limits before running it.
These are preserved historical configurations; they do not inherit the new
Luna `configs/pilot.json`. Availability is checked against the provider. The
historical comparison configurations use 20 actor steps and six researcher
questions, with no dollar cap. The default is design-only; `--continue-workflow`
and `--validate-execution` are experimental extensions requiring separately
provisioned task environments/data. This migration is not validation of a full
GPU experiment or the paper's full workflow.

The preserved Sonnet comparison driver can run both five-task conditions after
staging at `data/realistic_pilot/staged/`:

```bash
uv run --locked python scripts/expbench/run_sonnet_actor_comparison.py \
  --local /tmp/expbench-comparison-new --output runs/expbench/comparison-new
```

It uses the historical provider-compatible nonempty judge user message. The
plain realistic runner retains the released empty-user judge protocol, which
some providers reject. These are distinct recorded evaluation conditions; do
not claim identical prompting across them.

## Evaluation and historical results

The current retained realistic track reports **reference coverage**, averaging
three released-prompt judgements of the submitted plan, alongside the original
integrity-monitor gate. It adds no universal design-quality score. A design-only
score does not establish correct code, successful experiment execution or valid
scientific conclusions. Earlier pilot/control commands remain for provenance and
must not be confused with the current reference-coverage condition.

| Simulator | Actor | Judge | Mean reference coverage | Tasks |
| --- | --- | --- | ---: | ---: |
| Sonnet 5 | Sonnet 5 | Sonnet 5 | 79.5/100 | 5 |
| o3-mini | Sonnet 5 | Sonnet 5 | 92.7/100 | 5 |

These are previously measured results, not migration reruns. See the
[comparison report](../../reports/expbench/sonnet5_actor_comparison_20260922.md)
and [report with interaction trace and final design](../../reports/expbench/experiment_design_pilot_summary_20260922.md).
They remain separate from full-workflow scores in the other benchmarks.

The existing local datasets and private runs were moved into this repository's
ignored directories. Public report links were updated; immutable run receipts
retain their historical absolute paths as provenance. Cluster-specific full-run
configs and the old upstream vendor snapshot are retained locally under
`external/expbench-history/`, not distributed as portable setup instructions.
