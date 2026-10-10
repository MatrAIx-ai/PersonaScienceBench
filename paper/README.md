# PersonaScienceBench paper

`main.tex` retains the supplied AI Frontiers class/style and imports editable sections from `sections/`. Introduction, Related Work, and Section 3.2 (conversion from static benchmarks to interactive simulations) currently contain manuscript prose. Section 3.1 (persona construction) has a red TODO assigned to Divid; the abstract, remaining main sections, and appendix also contain visible red TODO placeholders. The title is provisional; author details are placeholders.

Use [the paper plan](../docs/design/benchmark_paper_plan.md) and [experiment trackers](../Experiment/README.md) when drafting the remaining sections. Earlier unreviewed drafts were cleared; Section 3.2 now documents conversion from static benchmarks to interactive simulations and the frozen panel, with a compact benchmark-by-domain table beside generic actor--simulator pseudocode.

Results includes a performance table generated from `data/performance_panel.csv` and a semantic figure at half the text width, with its explanatory text wrapping alongside; interpretation remains a TODO. The table source is `tables/performance_panel.tex`, with benchmark and domain tables side by side, two-decimal means and unweighted group-average rows. The two table bodies have equal heights and aligned average rows. Confidence intervals and task/episode counts remain in the source CSV but are omitted from the displayed tables. The semantic figure uses the vector PDF in `figures/semantic.pdf`, copied unchanged from `Experiment/01_behavioral_diversity/figures/semantic/semantic.pdf`. The previous performance PNG is retained as an unused source asset.

Compile from this directory when a LaTeX distribution is available:

```bash
latexmk -xelatex main.tex
```

The original-language interaction appendix uses the bundled OpenType Chinese
font in `fonts/PSBTraceCJK.otf` and requires **XeLaTeX** (or Tectonic).
In Overleaf, select **XeLaTeX** under the project compiler settings and set
`main.tex` as the main document. The included `.latexmkrc` also selects XeLaTeX
for local `latexmk` builds; do not override it with `-pdf` (pdfLaTeX).

Alternatively, compile with Tectonic:

```bash
tectonic --synctex main.tex
```

The current `main.pdf` and `main.synctex.gz` are rebuilt from the local source using Tectonic 0.17.0. This environment has a temporary compiler at `/tmp/personasciencebench-tex/bin/tectonic`, with its package cache at `/tmp/personasciencebench-tex/cache`.

The appendix, “Details on Benchmark Implementation,” reserves five benchmark-specific subsections for technical specifications, each marked with a red TODO.

## Performance values for table construction

[PERFORMANCE_PANEL.md](PERFORMANCE_PANEL.md) lists the five-setting absolute performance panel by benchmark and domain, with 95% CIs, coverage, and a candidate table caption. [Full-precision CSV](data/performance_panel.csv) supplies all 45 cells used in `tables/performance_panel.tex`. Values use the same available-trial inputs as the existing figure; they are not restricted to the trial-1 trace release.

Results also includes the full-width vector figure `figures/metric_suite.pdf`, copied unchanged from `Experiment/09_offline_metric_suite/figures/metric_suite.pdf`. Its caption follows the current notebook definitions for actor self-repetition, failure-conditioned fact recovery, and cumulative performance.

## Updated narrative and section plan

[STRUCTURE.md](STRUCTURE.md) reviews the current manuscript against the model-level scorecard and maps primary versus supporting analyses. The LaTeX currently still leads Results with the older benchmark/domain table; the structural review does not replace or rewrite manuscript prose.

## Page flow

Main sections use `\input` and continue on the current page when space permits. Large `\Needspace` reservations were removed from Results; main figures and the model scorecard use `[!htbp]` instead of fixed `[H]` placement, and the Results wrapped table/figure may float. This lets prose fill available space while keeping figures intact. The explicit appendix page break remains. Rebuilt `main.pdf` after the layout change; Results now begins on the remaining portion of page 5 and subsection 5.3 continues on page 6.
