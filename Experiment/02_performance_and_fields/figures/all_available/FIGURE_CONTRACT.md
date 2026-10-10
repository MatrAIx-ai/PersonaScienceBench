# All eligible personas — heatmap contract

Include Astra-low personas with at least one completed trial job on the frozen 200-task panel. Off/148/155/089/001/127 have three trials; 003/004/046 have one. The cancelled initial run is excluded, as are personas with no completed trial. A completed trial job may contain technical failures.

Retain the previous two-panel heatmap design: benchmark columns above, super-family columns below, fixed persona order, means and 95% CIs printed in each cell. Row labels disclose the available trial count. Absolute scores include off; paired effects compare eight personas with off. Store exact task, episode and study denominators in source CSVs. Preserve the prior six-setting heatmap separately.

Use all evaluable endpoints from eligible trial slots, preferring a scored repaired endpoint and falling back to an evaluable original if repair failed. Do not maximize scores or count repairs as independent repeats. Average available repeats within task, then tasks equally; resample study clusters within source. Sparse single-study cells have no estimable CI. Absolute ASI scores are mixed-version descriptive values; paired ASI requires corrected judge versions on both sides. Family composites mix native metrics and preserve source composition. No ranking, equivalence or significance claim.

Export PDF/SVG/PNG/TIFF from the executed notebook, with fixed 183 mm width, original heatmap aesthetics, at least 5.5 pt text and 600 dpi raster resolution. No new inference jobs. No forest-plot alternative.

## Combined performance view
`combined_performance` places available scores and 95% CIs on the left and matched changes and 95% CIs on the right, with benchmark and super-family rows. The five selected settings (off/155/001/003/046) share row positions; off is a gray reference for differences. Frozen estimates and inference are unchanged. Coverage differs between panels; absolute ASI scores remain mixed-judge descriptive values. Export: 260 × 165 mm, editable PDF/SVG and 600-dpi PNG/TIFF. Earlier figures are retained.

## All-pairs selected-persona view
`pairwise_performance` is the notebook’s final figure. Left: available absolute heatmaps and CIs. Right: nine full 5×5 row-minus-column matrices with categorical significance colors. 310 × 215 mm, PDF/SVG and 600-dpi raster exports. Two left heatmaps and the right 3×3 grid are independently aligned; their distinct inferential roles use intentionally different grid structures. Earlier combined and separate exports remain preserved. See `../../PAIRWISE_PERFORMANCE_CAPTION.md`.
