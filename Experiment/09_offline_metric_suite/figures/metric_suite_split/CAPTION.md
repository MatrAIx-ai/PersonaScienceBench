# Split metric-suite figure

A–B retain the existing actor self-repetition (six-word windows, at least three matching corresponding words; study-cluster 95% CIs) and case-averaged complete-fact recovery among unsuccessful SciConv disambiguation runs (no CI). The repetition setting originated from the documented exploratory grid search.

C retains the existing cumulative native score: sum final scores of runs ending by t, divided by all evaluable runs for that setting. The requested y-label is “Avg Score before t”; “before” includes t (≤ t), and the denominator is fixed. It is not mean score conditional on completion by t. All 1,958 original evaluable runs across five benchmarks remain included; partial credit retained. This is not a causal interaction-budget experiment. Curves and estimates are unchanged.

Reproduce with `code/plot_metric_suite_split.py` or the main figure cell in `metric_suite.ipynb`. PDF, SVG, PNG and panel source data are saved here.
