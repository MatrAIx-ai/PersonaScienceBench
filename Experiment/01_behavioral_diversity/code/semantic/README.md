# Semantic figure reproduction

The final configuration uses trial 1 only for off/155/001/004/046. Main aggregation gives each super-family 25% weight; the question-weighted result is retained as sensitivity. Raw distances do not subtract rollout randomness. No API judge, summarization, behavior classification or performance plots.

1. Run `analyze.py extract` with the project Python to freeze original generated messages and numeric indexes. Message text stays in ignored `runs/semantic-analysis/`.
2. Run `embed.py --device cuda` with a Python environment containing PyTorch and Transformers. The executed environment used PyTorch 2.13.0+cu130 and Transformers 5.14.1. Model revision and all further runtime provenance are saved. The runner requires the existing local Qwen3-Embedding-0.6B snapshot; it does not download or upload data. No truncation or summaries.
3. Run `audit_controls.py` and inspect missing records/conflicts before interpreting comparisons.
4. Run `analyze.py analyze`, then `build_notebook.py` with project Python. The notebook computes tables, saves its outputs and exports the figure. It never starts embedding automatically.
5. Run the nature-figure source, font and PDF collision checks on `plot.py` and the exported PDF. Alignment is checked within the plotting function.

`config.json` freezes five identities, rollouts, preprocessing, common-round coverage, weighting, bootstrap, case rule and PCA settings. Matched comparison keys are source/question/round/role. The input index is verified against embedding hashes before filtering to the requested trials. Whole questions, including all conditions and rounds, are resampled within benchmark × family. Pairwise distances and PCA use separate roles throughout.

The cached embedding archive can contain additional original trials, but the analysis and each PCA fit filter to configured rollout IDs. `selected_message_index.csv` identifies every analyzed message and its event index. Changed model or preprocessing choices require new embedding provenance. To use excess distances, explicitly set mode to `adjusted` and supply at least two independent rollouts for every configured condition; the implementation rejects missing repeats rather than filling W with zero.

## Current final-response heatmaps

Panel A now uses `final_response.py`, with outputs under `data/semantic_final/`: last generated role response, distinct-question within-family distances, equal family weights, question-blocked pair-label permutations and Holm across 20 tests. `final_report.py` writes the current report. The main notebook loads these outputs by default; set `RECOMPUTE=True` to rerun the 10,000 permutations and 20,000 bootstrap replicates. `test_final_response.py` checks estimator/swap equivalence and bootstrap/Holm arithmetic. The original `analyze.py`/`report.py` retain the earlier round-matched analysis and are not the current Panel A pipeline. Panel B retains frozen reviewed UMAP coordinates and curved connectors without arrows or point indices.
