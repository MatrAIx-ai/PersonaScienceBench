# OpenProblems denoising adapter

[OpenProblems](https://openproblems.bio/) `task_denoising`: estimate true expression from sparse
single-cell RNA-seq counts. The source is pinned at
[`openproblems-bio/task_denoising@6233222`](https://github.com/openproblems-bio/task_denoising/tree/6233222758328ceea11651cc6f3aeb11fe3ae396),
and the processed datasets come from the public bucket `s3://openproblems-data/resources/task_denoising/datasets/`
(the `log_cp10k` directories). The hashes of the fetched files are pinned in `manifests/sources.json`.

## Episode

One episode per dataset. **The actor implements and runs a denoising method** on `data/train.h5ad` (raw
counts: the training half of each cell's molecules from the native molecular cross-validation split). It
submits `denoised.h5ad` (`layers["denoised"]`, same cells and genes, plus `uns["dataset_id"]` and
`uns["method_id"]`) together with the executed script as `artifacts["analysis"]`.

| Boundary | Content |
|---|---|
| Actor | Task description; `file_train.yaml`, `file_prediction.yaml`, `comp_method.yaml` from the pinned repo; `train.h5ad`; shape and organism |
| Researcher | Dataset name, summary, description, URL and reference, from `test.h5ad` `uns` |
| Evaluator | `test.h5ad` (held-out molecules, `train_sum`), native metric and control scripts |

**Variant:** the native task gives methods only `train.h5ad`, and its dataset metadata stays with the test
split. Here the simulated researcher holds that metadata, and every episode records this as
`conversion.variant = researcher_holds_dataset_metadata`. The metadata describes the study; it contains no
held-out counts or scores.

## Scoring

`evaluate()` copies the sealed prediction, `train.h5ad`, `test.h5ad` and the pinned native scripts into a
fresh directory, and runs them in a separate Bubblewrap sandbox with the evaluator environment
(`configs/openproblems-evaluator-requirements.lock.txt`). Each script runs unchanged except for its
`## VIASH START … ## VIASH END` parameter block, which the harness fills in as Viash would.

- **Native metrics** `mse` (after normalize_total to 10,000 and log1p) and `poisson` (after rescaling to the
  held-out library size). Both are minimised. Their raw values are reported as `metrics.mse` and
  `metrics.poisson`.
- **Controls** `no_denoising` (negative: returns the training counts) and `perfect_denoising` (positive:
  returns the held-out counts) are computed on the same dataset.
- **Scaled metrics:** each metric scaled to (negative − value) / (negative − positive), so the negative
  control is 0 and the positive control is 1. `score` is the mean of the two; **`score_clipped` clips each
  scaled metric to [0, 1] first and is the headline in pilot reports.** The native Poisson loss is
  unbounded: a prediction on the wrong scale (for example, not on the count scale) can drive it into the
  thousands, or below zero, and then the unclipped `score` is dominated by a few episodes (1 of the
  125 pilot episodes did this).
- A prediction the native metrics cannot read, or with the wrong layer, shape or cell/gene order, is
  reported as `missing_submission` with the contract violation recorded (the pilots count it as 0).
  Evaluator failures are `error`.

The evaluator environment pins the metric scripts' own requirements (`scprep`, `scikit-learn`, `numpy<2`,
plus `anndata`, `scanpy`) instead of the `openproblems/base_python:1` image, so scores are labelled
`openproblems-denoising-psb-v1`, not as official leaderboard values.

## Setup

```bash
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks openproblems_denoising
uv sync --locked --extra openproblems   # h5py, used to read dataset metadata during conversion
base=$(.venv/bin/python -c 'import os, sys; print(os.path.realpath(sys._base_executable))')
"$base" -m venv --clear .openproblems-eval-venv && uv pip sync --python .openproblems-eval-venv/bin/python --require-hashes configs/openproblems-evaluator-requirements.lock.txt
"$base" -m venv --clear .actor-venv-openproblems && uv pip sync --python .actor-venv-openproblems/bin/python --require-hashes configs/actor-requirements-openproblems.lock.txt
```

`fetch-sources` downloads and hash-checks the pinned dataset files. The actor environment adds `anndata`,
`scanpy` and `scikit-learn` to the shared actor packages and is kept separate
(`actor_python: .actor-venv-openproblems` in pilot configs), so other benchmarks' actor environment is
unchanged.

**Memory.** The native `mse` metric densifies the count matrices, so evaluation needs several times the
dense size of a dataset (cells × genes × 8 bytes). Pilots on an 8 GB Docker VM use the smaller datasets and
a few workers; the larger datasets need more memory.
