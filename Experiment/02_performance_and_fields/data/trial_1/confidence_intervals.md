| Benchmark | Tasks | Persona off | Persona 148 | Persona 155 |
|---|---:|---:|---:|---:|
| asibench | 31 | 49.40 [35.69, 63.63] | 49.78 [36.30, 63.58] | 51.99 [38.52, 65.72] |
| bixbench | 40 | 32.50 [17.50, 47.50] | 30.00 [17.50, 45.00] | 32.50 [17.50, 47.50] |
| discoverybench | 34 | 11.87 [4.05, 21.45] | 15.38 [5.72, 26.77] | 14.00 [4.85, 24.93] |
| expbench | 40 | 44.03 [37.60, 50.51] | 42.73 [36.71, 48.84] | 43.73 [37.00, 50.56] |
| sciconvbench | 40 | 85.00 [72.50, 95.00] | 87.50 [77.50, 97.50] | 87.50 [77.50, 97.50] |

| Super-family | Tasks | Persona off | Persona 148 | Persona 155 |
|---|---:|---:|---:|---:|
| life | 46 | 30.34 [18.02, 43.34] | 27.42 [15.66, 40.47] | 30.23 [17.75, 43.27] |
| math_cs | 54 | 49.71 [42.07, 56.99] | 53.83 [46.65, 60.88] | 54.21 [47.31, 60.70] |
| physical_engineering | 57 | 69.23 [59.63, 77.74] | 68.15 [58.82, 76.66] | 67.82 [58.58, 76.24] |
| social_humanities | 28 | 13.22 [4.15, 24.68] | 15.11 [5.02, 27.57] | 16.21 [5.39, 29.50] |

Method: 20000
Method: 20260929
Method: Percentile bootstrap, 2.5th and 97.5th percentiles; paired task resampling across conditions, stratified by benchmark source.
Method: Matched evaluable tasks across all three conditions; missing submissions zero, infrastructure/evaluation errors excluded in all conditions.
Method: Task-weighted mean of native metrics normalized to 0–100. Within-family source counts held fixed in bootstrap; descriptive composite, not a common calibrated scientific measure.
Method: One episode per condition. Intervals reflect task sampling variation, not repeat-run/model randomness. Task bootstrap does not account for dependence among tasks from the same study. Pointwise intervals, not simultaneous intervals or tests of persona differences.
