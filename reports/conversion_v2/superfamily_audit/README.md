# Empirical superfamily sampling audit

Seed: **20260929**. Audited **2132 source question records**. No model calls or benchmark executions.

This tests whether the **four proposed reporting superfamilies** are represented when sampling an equal number of questions from each benchmark. It does not discover a unique scientific taxonomy.

## Classification and eligibility

- **Life:** biology and biostatistics; all Bix questions retain their biological application label.
- **Physical / engineering:** physics, chemistry, astronomy, materials, Earth science, electrical engineering, robotics, fluids and mechanics. Molecular-design EXP papers are classified as chemistry.
- **Mathematics / CS:** mathematics, CS, software requirements, and numerical PDE specifications. PsychoBench evaluates LLMs and is classified as CS; that boundary is contestable.
- **Social / humanities:** sociology, economics, archaeology/humanities and meta-science. Native Discovery domain labels are retained, including its health/social survey questions.

The main scenario allows diagnostic plots produced by numerical code, but excludes image-centric tasks, conservative unresolved modality cases, missing declared assets and unresolved Bix input roles. EXP uses explicit paper-objective exclusions plus question-level exceptions for mixed astronomy and aerodynamic datasets. Audio-centric design tasks are outside this text/numerical screen.

**Screened does not mean runtime-certified.** All 200 native evaluators have not been executed. Further scientific-objective review, external-tool checks and resource limits can shrink this frame. Counts must not be described as a finalized runnable panel.

Discovery duplicates are normalized question-text matches. SciConv also groups identical intended specifications or matching explicit native Task IDs across modes. This does not detect every semantic near-duplicate or parameterized variant. Group counts are clustering proxies, not a claim that all groups are independent studies.

## Screened candidate capacities

| Source | Life sciences | Physical / engineering | Mathematics / CS | Social / humanities | Total |
|---|---:|---:|---:|---:|---:|
| discoverybench | 26 | 0 | 15 | 166 | 207 |
| bixbench | 124 | 0 | 0 | 0 | 124 |
| expbench | 0 | 29 | 235 | 0 | 264 |
| sciconvbench | 0 | 788 | 120 | 0 | 908 |
| asibench | 7 | 29 | 18 | 0 | 54 |
| **Total** | 157 | 846 | 388 | 166 | 1557 |

Machine-readable decisions, public questions, classification basis, grouping keys and exclusions: [inventory.jsonl](inventory.jsonl).

## Actual source-stratified random sample

Uniformly selected 40 candidate task families without replacement from each source. Equivalent variants use a frozen seeded representative.

| Source | Life sciences | Physical / engineering | Mathematics / CS | Social / humanities | Total |
|---|---:|---:|---:|---:|---:|
| discoverybench | 5 | 0 | 3 | 32 | 40 |
| bixbench | 40 | 0 | 0 | 0 | 40 |
| expbench | 0 | 6 | 34 | 0 | 40 |
| sciconvbench | 0 | 34 | 6 | 0 | 40 |
| asibench | 5 | 23 | 12 | 0 | 40 |
| **Total** | 50 | 63 | 55 | 32 | 200 |

[Actual sampled task IDs](diagnostic_plots_allowed.random_sample.csv). This is a source-stratified random sample; study sizes are not equalized.

## Repeated sampling experiment

These are repeated offline draws of task IDs, **not model episodes**. The intervals below describe composition across draws, not performance confidence intervals.

| Family | Mean number of questions | 5th–95th percentile across draws |
|---|---:|---:|
| life | 50.295 | 47–54 |
| physical_engineering | 60.536 | 55–66 |
| math_cs | 57.234 | 51–63 |
| social_humanities | 31.935 | 28–35 |

All four families appeared in **100.0% of 1000 draws**. This observed frequency is not a guarantee for every possible draw.

## Optimized family-balance feasibility witness

Integer optimization fixes the same source quotas, minimizes the sum of squared deviations from equal family totals, then maximizes study-group coverage. A seeded random objective breaks remaining ties. There are no hand-entered source–family quotas.

| Source | Life sciences | Physical / engineering | Mathematics / CS | Social / humanities | Total |
|---|---:|---:|---:|---:|---:|
| discoverybench | 0 | 0 | 0 | 40 | 40 |
| bixbench | 40 | 0 | 0 | 0 | 40 |
| expbench | 0 | 6 | 34 | 0 | 40 |
| sciconvbench | 0 | 30 | 10 | 0 | 40 |
| asibench | 7 | 21 | 12 | 0 | 40 |
| **Total** | 47 | 57 | 56 | 40 | 200 |

[Optimized task IDs](diagnostic_plots_allowed.balanced_sample.csv). **This optimizer-selected set is a feasibility witness, not a probability sample.** Its inclusion probabilities are not known.

Certified optimum squared deviation: **194.0**; represented study-group proxies: **154**.

Exact equality is impossible under this mapping: social/humanities is available only through Discovery, whose source quota limits it to 40. The optimized solution uses all Discovery slots for that family and loses Discovery biology/computing coverage. This exposes a tradeoff between balanced margins and within-source breadth; it is not a recommendation to discard that breadth silently.

## Native subfield coverage in the random sample

Superfamily totals do not imply adequate subfield sample sizes. These are native domain labels, not a completed cross-source subfield taxonomy. Bix has overlapping category lists and EXP has paper titles; neither is counted as a mutually exclusive subfield taxonomy here.

| Source | Native domain | Questions |
|---|---|---:|
| discoverybench | biology | 5 |
| discoverybench | economics | 1 |
| discoverybench | engineering | 3 |
| discoverybench | humanities | 9 |
| discoverybench | meta science | 7 |
| discoverybench | sociology | 15 |
| sciconvbench | fluids | 7 |
| sciconvbench | foam | 8 |
| sciconvbench | matSci | 4 |
| sciconvbench | matToolUse | 4 |
| sciconvbench | pde | 6 |
| sciconvbench | solMech | 4 |
| sciconvbench | solToolUse | 7 |
| asibench | astronomy | 2 |
| asibench | biology | 5 |
| asibench | chemistry | 5 |
| asibench | computer_science | 5 |
| asibench | earth_science | 2 |
| asibench | electrical_engineering | 1 |
| asibench | materials | 2 |
| asibench | math | 7 |
| asibench | physics | 7 |
| asibench | robotics | 4 |

| Superfamily | Questions | Source-study group proxies |
|---|---:|---:|
| life | 50 | 31 |
| physical_engineering | 63 | 60 |
| math_cs | 55 | 39 |
| social_humanities | 32 | 4 |

Native subfields with only one or two sampled questions support examples or exploratory descriptions, not precise standalone comparisons. Question counts also overstate independent evidence when several questions share a study.

## Sensitivity and limitations

- Excluding declared figure outputs leaves **22 ASI candidates** after the other screening rules. Forty per benchmark is then infeasible. The initial 26 no-figure ASI records additionally lose two missing-data cases and two perception/spatial-mapping exclusions.
- Moving all SciConv PDE tasks into physical/engineering still represents all four families. The alternate allocations and simulations are in [summary.json](summary.json).
- Purely metadata-driven domain assignments are transparent but are not an independent two-reviewer field audit. Molecular biology/chemistry, LLM psychology, Earth ecology and applied PDEs have plausible alternative labels.
- Acquisition readiness is distinct from scientific or runtime validity. R-based Bix analyses, expensive ASI computations, unresolved source-group dependence and mixed-modality EXP tasks still warrant task-level review.
- The historical pilot outcomes were not read or used to select tasks. The sample can overlap historical tasks by chance; this audit does not implement a holdout split.

## Reproduce

From the repository root, with the downloaded sources and local environments:

```bash
.venv/bin/python scripts/audit_superfamily_sampling.py
```

The script uses only local source data, verifies checkout revisions and records inventory/script hashes. It does not load credentials, call models, alter historical experiment configurations or launch episodes. The frozen native EXP join is created offline if absent.

[Audit script](../../../scripts/audit_superfamily_sampling.py) · [Summary and provenance](summary.json)
