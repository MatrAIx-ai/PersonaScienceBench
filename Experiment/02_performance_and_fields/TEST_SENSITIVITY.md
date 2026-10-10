# Performance-test sensitivity analysis

This is a fixed three-method exploratory comparison, not an exhaustive collection of statistical tests or a selection of the most favorable method. All methods use the five settings off/155/001/003/046, identical evaluator-compatible task–trial matches, task-equal means after averaging matched repeats, and independent source-study clusters. Absolute score panels and observed effect sizes are unchanged. There are 90 unique hypotheses (10 persona pairs × 9 groups). Tests are two-sided; Holm correction applies to all 90 within each method, with unavailable tests entered as p=1. Mirrored cells are one test. The separate corrections do not account for selecting a method based on these outputs.

| Method | Statistic and calibration | Assumptions and limitations |
|---|---|---|
| Study-cluster sign flip | Absolute task-weighted mean; flip whole source-study blocks | Independent blocks and joint sign symmetry or valid blockwise label exchangeability; exact enumeration for ≤16 blocks, otherwise 99,999 draws with plus-one correction |
| Cluster-robust t (CR1) | Intercept-only OLS on task differences; sandwich SE with G/(G−1) correction; Student t with G−1 df | Large-cluster-count approximation; few or highly unequal clusters can give unreliable p-values; nonzero effect with degenerate residual variance is unavailable |
| Studentized cluster sign flip | Recompute the absolute CR1 t statistic for each whole-block flip | Same symmetry/exchangeability assumptions as the first method; exact enumeration or 99,999 draws as above; studentization is not a guarantee of greater power |

The minimum number of clusters is two, but two clusters do not establish reliable approximate inference. Per-comparison study counts are exported so sparse comparisons remain visible. All-zero differences have p=1. No model/API calls or changes to scientific scoring were made.

Ordinary episode-level t tests, signed-rank tests and McNemar tests were not applied: the episodes are not independent, scores are not uniformly binary, and rank/direction tests would change the estimand from the plotted task-weighted mean difference. Mixed-effects models require benchmark-specific modeling assumptions beyond this fixed-estimand sensitivity analysis.

## Artifacts and reproduction

- `data/test_sensitivity/overview.json`: counts for every method, in fixed method order.
- `data/test_sensitivity/comparisons.csv`: all raw/adjusted p-values, effect sizes and coverage.
- `figures/test_sensitivity/<method>/pairwise_performance.{pdf,svg,png,tiff}`: complete labeled figures.
- `performance_analysis.ipynb`: executed comparison and figures, preserving the original analysis.
- Recompute: `OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/02_performance_and_fields/code/performance_test_sensitivity.py`, then execute the notebook's sensitivity section.

Interpret as sensitivity evidence conditional on observed trials and evaluable outcomes. Persona selection was exploratory. Method disagreements should be disclosed, not collapsed into whichever p-value is smallest. No false-positive calibration or power simulation was performed in this analysis.

## Method references

- [SciPy paired permutation documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
- [Statsmodels CR1 cluster covariance](https://www.statsmodels.org/v0.14.1/generated/statsmodels.stats.sandwich_covariance.cov_cluster.html).
- [Statsmodels cluster degrees-of-freedom and t inference](https://www.statsmodels.org/dev/generated/statsmodels.regression.linear_model.OLSResults.get_robustcov_results.html).
- [FSL exchangeability blocks](https://fsl.fmrib.ox.ac.uk/fsl/docs/statistics/palm/exchangeability_blocks.html).

## Results

| Method | Raw p < .05 | Holm p < .05 | Unavailable |
|---|---:|---:|---:|
| Study-cluster sign flip | 1 | 0 | 1 |
| Cluster-robust t (CR1) | 1 | 0 | 1 |
| Studentized cluster sign flip | 1 | 0 | 1 |
