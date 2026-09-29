# PersonaScienceBench paper

`main.tex` retains the supplied AI Frontiers class/style and imports editable sections from `sections/`. Red TODO/CITE markers are drafting instructions, not findings or references. The title is provisional; author details are placeholders.

The outline follows [the paper plan](../docs/design/benchmark_paper_plan.md) and [experiment trackers](../Experiment/README.md). Benchmark allocation is filled from the frozen panel. Score tables intentionally contain dashes until final version-consistent results are inserted. The three-column score layout shows the initial panel; expand or supplement it for the full selected persona panel. No placeholder citations are fabricated.

Compile from this directory when a LaTeX distribution is available:

```bash
latexmk -pdf main.tex
```

`main.pdf` is the original supplied template PDF and has not been regenerated for this outline. This environment currently has neither `latexmk` nor `pdflatex`.
