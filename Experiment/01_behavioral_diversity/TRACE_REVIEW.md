# Additional trajectory review — UMAP

The previous PCA review plots have been replaced in place with UMAP; raw messages, cached embeddings and the main paper figure are preserved.

Status: generated from existing complete trial-1 traces; no new model calls.

[Open interactive gallery](../../runs/semantic-review/index.html) · [Executed notebook](semantic_trace_review.ipynb) · [Selection manifest](data/semantic_review/manifest.json)

Each case shows the same question under off/155/001/004/046, with separate simulator and actor trajectories. Click a colored node to read its saved exchange. Filter by benchmark or super-family, mark favorites, write notes and **Export selected cases + notes**. Exported JSON preserves question IDs, settings and reasons for selection. Browser storage also retains choices locally; export provides a portable copy.

| Benchmark | Cases with ≥4 exchanges in any setting | All five settings ≥4 |
|---|---:|---:|
| ASI | 0 | 0 |
| Bix | 1 | 0 |
| Discovery | 0 | 0 |
| EXP | 0 | 0 |
| SciConv | 21 | 10 |

Total: **22 questions, 110 persona interaction traces**, including shorter comparison trajectories within selected questions. The two main-figure examples remain excluded. [Bix PDF](../../runs/semantic-review/pdf/bixbench.pdf) · [SciConv PDF](../../runs/semantic-review/pdf/sciconvbench.pdf).

This replaces the prior 131-question review gallery. Obsolete generated plots and PDF books are removed; raw traces, cached embeddings and main manuscript outputs are preserved. Browser review notes retain their original question IDs, but only cases present in the new gallery are displayed/exported.

## Selection and representation

Require complete original trial-1 episodes for all five settings and eligible rounds for both roles. A complete exchange has both a simulator message and a corresponding actor response at the same round index; an unmatched closing message does not count. Retain cases where at least one setting has **four or more complete exchanges**. Rank within benchmark by the number of settings meeting that threshold, then the minimum and total exchange counts across settings (descending), then SHA256(seed|source|question), seed `20261006`. Take up to 30 per source, without filling missing slots with short-only cases. Full lengths and all five settings remain visible.

Selection is deliberately enriched for long interactions. It is an exploratory illustration set, not a representative source or field mixture and not a new aggregate estimator. No performance or semantic-separation ranking is used.

Use the cached frozen Qwen/Qwen3-Embedding-0.6B embeddings (revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`), L2 normalized, 1024 dimensions. Each current generated message is embedded separately, with no prompt/profile metadata or repeated history. Independently for each question and role, fit UMAP to all five settings and all observed trial-1 rounds. Use cosine distance, `n_neighbors=min(15, n_messages−1)`, `min_dist=0.1`, 500 epochs, spectral initialization, `random_state=42`, `transform_seed=42` and `n_jobs=1`. The installed UMAP version and per-map settings are recorded in the manifest and projection JSON. There are no explained-variance percentages for UMAP; distances, cluster gaps and path lengths in the projection are not quantitative effect sizes. Retain actual trajectory lengths, round numbers, arrows and final-node diamonds. UMAP coordinates are local and cannot be compared between plots.

The HTML contains actual saved messages and no generated judgments or summaries. It is self-contained for reviewing plots and messages; the linked PDF/SVG files require the accompanying folders. Raw-text HTML remains in ignored `runs/semantic-review/`; numeric selection manifests, coordinates, scripts and the executed notebook are tracked candidates.

Final manually chosen examples should be described as **manually selected illustrations**. They do not independently establish a population effect. The existing aggregate heatmaps, intervals and manuscript figures remain unchanged.

## Reproduce

From the repository root:

```bash
PYTHONPYCACHEPREFIX=/tmp/psb-umap-pycache MPLCONFIGDIR=/tmp/psb-mpl OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
  .venv/bin/python Experiment/01_behavioral_diversity/code/semantic/gallery.py
.venv/bin/python Experiment/01_behavioral_diversity/code/semantic/build_review_notebook.py
```

The exact numerical package versions used for rendering are recorded in `code/semantic/requirements-umap.txt` and the manifest. A local temporary dependency directory was used to bypass slow shared-filesystem imports; the UMAP implementation and settings are unchanged.

The notebook checks role/persona and trial coverage, node-message counts, finite coordinates, PDF pages, main-artifact hashes and JavaScript syntax. Browser interactions have not been automated. See [validation](data/semantic_review/validation.json).
