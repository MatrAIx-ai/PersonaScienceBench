# Question-controlled semantic distances and trajectories

> Archived revision. Links resolve to files preserved with this revision where available. Unbundled historical paths are recorded as text; current outputs are not substituted for historical evidence.

[Executed notebook](semantic_trajectory_analysis.ipynb) · [Figure PDF](semantic.pdf) · [Editable SVG](semantic.svg)

## Scope and interpretation

Settings: Persona off, Persona 155, Persona 001, Persona 004, Persona 046. Original Astra-low completed traces only; no repairs, cancelled initial-run records, Sol episodes, behavioral categories, LLM judges or outcome plots. The selected evaluation manifest contains 40 questions from each of five source benchmarks (200 total); matched coverage after completeness/round requirements appears below.

**Raw-distance figure:** The user selected trial 1 only for all five settings. Consequently every off-diagonal cell uses raw cross-persona cosine distance; no cell subtracts repeat variation. This figure cannot establish excess separation over ordinary rollout randomness. The code supports the requested adjusted estimator but refuses it when configured repeats are insufficient.

The diagonal is masked. No significance stars are shown. The two roles share color limits. Manually selected UMAP examples illustrate observed conversations and are not independent statistical evidence. Distance can reflect linguistic style and is not task or reasoning quality. Persona off is explicitly the no-persona control.

## Shared representation and rounds

Frozen model: `Qwen/Qwen3-Embedding-0.6B` at revision `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`. Local inference, last-token pooling, 1,024 dimensions, L2 normalization; cosine distance before projection. No API calls, summaries, translation or embedding instructions. Full messages are embedded without truncation; inputs over the model context cause an explicit failure.

Strip outer whitespace only; retain generated content; omit metadata, system prompts, injected profiles and transcript history. No summaries, translation or message concatenation.

Round t starts with generated simulator message t, including generated initial inspection requests in review workflows. The next visible actor handoff/question/final specification before the next simulator message is its response. The fixed SciConv input question and pre-first-simulator-reply actor question are excluded. Terminal simulator messages without actor replies remain simulator observations only.

Trial 1 only for all five settings; original coordinator-finished traces. Include a round only when a nonempty role message exists under all five settings. Use this common T_q for all ten persona pairs within each question and role. No truncation to 3–4 rounds, padding, imputation or carry-forward.

Generated initial review requests are included because they are simulator outputs. The fixed SciConv input is excluded because it is benchmark input; its first actor question occurs before the first simulator output and is excluded from the simulator-then-actor pairing. A terminal simulator closing message may have no subsequent actor contribution. Different role coverage is retained explicitly; no response is fabricated.

## Weighting and uncertainty

Equal eligible rounds within each question; equal questions within each super-family; equal 25% weights for life, physical_engineering, math_cs and social_humanities. Whole-question bootstrap within source benchmark × super-family, retaining all settings and messages together.

All configured independent rollout IDs are used: {"persona_off": [1], "candidate_155": [1], "candidate_001": [1], "candidate_004": [1], "candidate_046": [1]}. At each eligible question/round/role, cross-persona distances average all R_i × R_j pairs. Adjusted mode additionally averages distinct within-persona pairs. Round estimates average within question, then questions average within super-family and each of the four families receives 25% weight. Benchmark weights within a family follow retained question counts. Whole questions are resampled within source × super-family 20,000 times (seed 20261005), keeping all their conditions, rounds and rollouts together. Percentile 95% intervals are pointwise, conditional on observed rollouts. No independent resampling of pairwise distances and no multiplicity claim. Questions from a shared source study may be correlated; this figure implements the requested question bootstrap, rather than the study bootstrap used in previous reports.

Later rounds condition on every included trajectory continuing to that round. A question missing any required condition/rollout has no eligible rounds for that role. Counts below and the round-coverage CSV expose these restrictions.

| Role | Source | Matched questions | Eligible question-rounds |
|---|---|---:|---:|
| simulator | ASI-Bench | 12 | 36 |
| simulator | BixBench | 36 | 108 |
| simulator | DiscoveryBench | 29 | 87 |
| simulator | EXP-Bench | 34 | 102 |
| simulator | SciConvBench | 37 | 110 |
| actor | ASI-Bench | 12 | 24 |
| actor | BixBench | 36 | 72 |
| actor | DiscoveryBench | 29 | 58 |
| actor | EXP-Bench | 34 | 68 |
| actor | SciConvBench | 37 | 110 |

The matched panel contains 41 life-science, 42 physical/engineering, 41 math/CS and 24 social/humanities questions. Each family receives 25% aggregate weight. Singleton benchmark-by-family strata have no estimable within-stratum variation in this bootstrap. Balancing controls field composition, not unobserved rollout randomness. Question-weighted sensitivity (original snapshot path: `data/semantic/question_weighted_heatmap_cells.csv`; not bundled in this revision) preserves the original weighting and source-stratified CIs.

## A — exact family-balanced heatmap estimates

| Role | Persona pair | Distance [95% CI] | Questions |
|---|---|---|---:|
| simulator | Persona off / Persona 155 | 0.2337 [0.2260, 0.2416] | 148 |
| simulator | Persona off / Persona 001 | 0.2256 [0.2158, 0.2362] | 148 |
| simulator | Persona off / Persona 004 | 0.1798 [0.1689, 0.1908] | 148 |
| simulator | Persona off / Persona 046 | 0.2553 [0.2452, 0.2657] | 148 |
| simulator | Persona 155 / Persona 001 | 0.2401 [0.2309, 0.2496] | 148 |
| simulator | Persona 155 / Persona 004 | 0.2370 [0.2284, 0.2461] | 148 |
| simulator | Persona 155 / Persona 046 | 0.2588 [0.2493, 0.2684] | 148 |
| simulator | Persona 001 / Persona 004 | 0.2210 [0.2126, 0.2297] | 148 |
| simulator | Persona 001 / Persona 046 | 0.2342 [0.2247, 0.2446] | 148 |
| simulator | Persona 004 / Persona 046 | 0.2477 [0.2372, 0.2589] | 148 |
| actor | Persona off / Persona 155 | 0.2072 [0.1961, 0.2181] | 148 |
| actor | Persona off / Persona 001 | 0.1721 [0.1593, 0.1852] | 148 |
| actor | Persona off / Persona 004 | 0.1378 [0.1260, 0.1493] | 148 |
| actor | Persona off / Persona 046 | 0.2003 [0.1882, 0.2123] | 148 |
| actor | Persona 155 / Persona 001 | 0.2063 [0.1940, 0.2185] | 148 |
| actor | Persona 155 / Persona 004 | 0.2079 [0.1968, 0.2192] | 148 |
| actor | Persona 155 / Persona 046 | 0.2135 [0.2020, 0.2249] | 148 |
| actor | Persona 001 / Persona 004 | 0.1725 [0.1605, 0.1839] | 148 |
| actor | Persona 001 / Persona 046 | 0.1925 [0.1796, 0.2054] | 148 |
| actor | Persona 004 / Persona 046 | 0.1932 [0.1804, 0.2065] | 148 |

## B — case selection and projection

Two examples manually selected by the user after inspecting the length-enriched UMAP gallery: bix-57-q1 and matToolUse/disambiguation/case_236. These are illustrative, not representative or independent aggregate evidence. All five settings are retained with their actual lengths, including one-round trajectories.

Local cosine UMAP jointly fit across all five settings and observed trial-1 messages, separately per question and role. n_neighbors=min(15,N−1), min_dist=0.1, 500 epochs, spectral init, random_state=42, transform_seed=42, n_jobs=1. Frozen coordinates copied exactly from the reviewed gallery; model and software provenance in umap.json and the gallery manifest. Local distances and path lengths are not effect sizes.

| Source | Question | Selection |
|---|---|---|
| BixBench | `bix-57-q1` | Manual exploratory illustration |
| SciConvBench | `matToolUse/disambiguation/case_236` | Manual exploratory illustration |

Every displayed path uses rollout 1. Simulator and actor rows show both sides of those same interactions. Nodes are actual observed messages; round indices remain in source data and are omitted from the plotted points; diamonds mark the final observed node. Gentle quadratic curves connect observed rounds for visual clarity; intermediate positions do not represent observed states. Control points use a perpendicular offset of 0.14 times the chord in axis-normalized coordinates; observed node coordinates are unchanged. Directional arrows and point-index labels are omitted; final nodes remain marked by diamonds. Local UMAP axes have no explained-variance percentages; coordinates cannot be compared across subplots and projected distances are not quantitative effect sizes. The five colors consistently identify conditions. There are no forced common origins or interpolated messages. Curvature is a display choice, not an estimated continuous semantic process.

## Reproducibility

- `code/semantic/config.json`: frozen settings, repeat IDs, availability, weighting and case-selection rules.
- `code/semantic/analyze.py extract`: original trace extraction; private current-message text stays in ignored `runs/semantic-analysis/`.
- `code/semantic/embed.py --device cuda`: offline local embedding; cached vectors keyed by model revision and exact message hash.
- `code/semantic/analyze.py analyze`: pairwise estimates, question bootstrap and the frozen user-selected UMAP coordinates.
- `code/semantic/build_notebook.py`: execute the table-and-figure notebook.

Analyzed 5,093 trial-1 messages from 919 complete episodes out of 1,000 trial-1 slots. Exclusions: `{"incomplete_episode_excluded": 81}`. The reusable embedding archive also contains later trials, which are filtered out before this analysis and every projection fit.

The recorded-question/model/decoding/protocol audit checked 919 complete trial-1 episodes, with 0 mismatched questions and 0 missing records. Initial environment files and unrecorded provider defaults were not reconstructed; see control audit (original snapshot path: `data/semantic/control_audit.json`; not bundled in this revision).

Heatmap source data (original snapshot path: `data/semantic/heatmap_cells.csv`; not bundled in this revision) · Question estimates (original snapshot path: `data/semantic/question_distances.csv`; not bundled in this revision) · Round coverage (original snapshot path: `data/semantic/round_coverage.csv`; not bundled in this revision) · Message/event index (original snapshot path: `data/semantic/selected_message_index.csv`; not bundled in this revision) · Embedding and analysis provenance (original snapshot path: `data/semantic/summary.json`; not bundled in this revision)
