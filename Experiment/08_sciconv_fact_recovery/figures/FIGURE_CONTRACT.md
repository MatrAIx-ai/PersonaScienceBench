# Fact-recovery figure contract

Question: Do the five persona settings improve deleted-fact recovery over persona-off across the fixed Astra panel?
Conclusion: Mean recovery is high and persona differences are modest with uncertain paired effects; these exploratory data do not establish a general persona benefit.
Archetype: quantitative grid, two complementary panels.
Panel a establishes absolute performance and ceiling context. Panel b supplies the decisive paired comparison against off; numerical intervals and the zero reference keep uncertainty visible. Preserve condition order and all six absolute/five contrast summaries. No new exclusions or statistical changes.
Backend: existing Python/Matplotlib workflow. Adaptation level: style-only revision of the existing figure.
Data mapping: original/all/arms/recovery_share -> panel a mean and ci95 ×100, units percent; original/all/paired_recovery_vs_off -> panel b mean and ci95 ×100, units percentage points. Counts remain distinct cases and evaluable episodes/matched pairs.
Design: 183 × 100 mm, editable sans-serif text, minimum 5.5 pt; gray baseline and muted teal persona family, no winner highlighting. Lowercase panel labels. Numeric mean/CI labels above uncertainty extents. Shared top/bottom edges and heights; intentional 6:5 widths allocate equal space per condition (six absolute conditions, five contrasts). Record a panel-width exemption; retain 1.5 pt alignment tolerance.
Exports: PDF, SVG, 600-dpi PNG/TIFF. Generic manuscript styling, not a claim of compliance with a particular journal's current submission rules.
Integrity: source summary unchanged; 20 cases and 359 original episodes, with one historical infrastructure failure. No missing-score imputation or new resampling. Pointwise study-cluster bootstrap CIs conditional on observed trials; no corrected significance claim.
QA: source validator, render-time alignment gate, PDF text audit, final PDF collision audit, whole-figure and panel visual inspection. Preserve the original display as an archived comparison. Notebook is the plotting entry point.
