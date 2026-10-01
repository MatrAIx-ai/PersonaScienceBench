# PersonaScienceBench paper

`main.tex` retains the supplied AI Frontiers class/style and imports editable sections from `sections/`. Introduction, Related Work, and Section 3.2 (dataset construction) currently contain manuscript prose. Section 3.1 (persona construction) has a red TODO assigned to Divid; the abstract, remaining main sections, and appendix also contain visible red TODO placeholders. The title is provisional; author details are placeholders.

Use [the paper plan](../docs/design/benchmark_paper_plan.md) and [experiment trackers](../Experiment/README.md) when drafting the remaining sections. Earlier unreviewed drafts were cleared; Section 3.2 now documents task conversion and the frozen panel, with a compact benchmark-by-domain table beside generic actor--simulator pseudocode.

Compile from this directory when a LaTeX distribution is available:

```bash
latexmk -pdf main.tex
```

Alternatively, compile with Tectonic:

```bash
tectonic --synctex main.tex
```

The current `main.pdf` and `main.synctex.gz` are rebuilt from the local source using Tectonic 0.17.0. This environment has a temporary compiler at `/tmp/personasciencebench-tex/bin/tectonic`, with its package cache at `/tmp/personasciencebench-tex/cache`.
