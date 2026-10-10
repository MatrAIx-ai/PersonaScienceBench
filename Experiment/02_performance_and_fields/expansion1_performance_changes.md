# Trial 1: performance changes for personas 003, 004 and 046

One trial only. Each persona is compared with persona-off on exactly the same evaluable tasks within each benchmark. Missing submissions count as zero; infrastructure/unscored outcomes are excluded on both sides. Different personas can have different matched subsets. No global ranking across incompatible native metrics.

After-repair outcomes are primary here to match the latest available-results request; original-outcome sensitivity is retained below. Repairs are conditional additional attempts, not independent trials. Original successes remain preserved. ASI is descriptive only because historical evaluator configurations differ.

Intervals are pointwise 95% percentile study-cluster bootstrap CIs (20,000 draws, seed 20261002) of paired task differences. They do not capture repeat-run uncertainty, correct five-benchmark/three-persona multiplicity, or establish significance; sparse clusters can yield degenerate intervals. Values are points on native scores normalized to 0–100.

## After Repair

| Benchmark | 003 Δ [95% CI]; n | 004 Δ [95% CI]; n | 046 Δ [95% CI]; n |
|---|---|---|---|
| asibench | +5.12 [-1.49, 14.95]; n=11 | +2.23 [-11.62, 14.89]; n=25 | +3.06 [-6.45, 10.65]; n=25 |
| bixbench | +0.00 [0.00, 0.00]; n=31 | -3.23 [-11.11, 0.00]; n=31 | -3.23 [-11.11, 0.00]; n=31 |
| discoverybench | +5.01 [1.49, 9.09]; n=31 | +3.36 [-4.45, 7.64]; n=33 | +6.76 [2.43, 12.64]; n=39 |
| expbench | -6.89 [-13.11, -0.67]; n=6 | +1.68 [-1.48, 4.79]; n=39 | -0.47 [-4.01, 3.97]; n=40 |
| sciconvbench | -2.50 [-15.00, 10.00]; n=40 | +2.50 [-5.00, 12.50]; n=40 | -7.50 [-20.00, 5.00]; n=40 |

## Original

| Benchmark | 003 Δ [95% CI]; n | 004 Δ [95% CI]; n | 046 Δ [95% CI]; n |
|---|---|---|---|
| asibench | +1.36 [-2.90, 7.00]; n=7 | +1.88 [-15.65, 18.33]; n=19 | -1.51 [-12.98, 5.95]; n=18 |
| bixbench | +0.00 [0.00, 0.00]; n=28 | -2.63 [-8.82, 0.00]; n=38 | +0.00 [0.00, 0.00]; n=37 |
| discoverybench | +2.80 [-0.73, 10.33]; n=22 | +3.58 [-4.45, 8.42]; n=31 | +6.90 [2.62, 12.48]; n=36 |
| expbench | -6.89 [-13.11, -0.67]; n=6 | +1.73 [-1.57, 4.92]; n=38 | -0.48 [-4.15, 4.04]; n=39 |
| sciconvbench | -2.50 [-15.00, 10.00]; n=40 | +2.50 [-5.00, 12.50]; n=40 | -7.50 [-20.00, 5.00]; n=40 |

## Coverage after repair

| Persona | Scored | Missing submission (zero) | Infrastructure errors |
|---|---:|---:|---:|
| 003 | 114 | 7 | 79 |
| 004 | 168 | 6 | 26 |
| 046 | 175 | 5 | 20 |

[Numeric results, exact task pairs and source hashes](data/expansion1_changes/summary.json). Reproduce with `code/report_expansion1_changes.py`. No API calls or figures generated.
