# Final-response semantic separation and illustrative trajectories

> Archived revision. Links resolve to files preserved with this revision where available. Unbundled historical paths are recorded as text; current outputs are not substituted for historical evidence.

[Executed notebook](semantic_trajectory_analysis.ipynb) · [Figure](semantic.pdf) · [Candidate caption and figure handoff](SEMANTIC_FIGURE_CAPTION.md)

## What is tested

Within each scientific super-family, compare final-response distances between personas with distances within each persona across different questions. This is a domain-level comparison of final-response embeddings, not within-persona rollout randomness or a matched-question distance statistic. Both roles share the same complete five-setting question set.

**Endpoint**: Last nonempty generated role message among the saved simulator–actor exchanges in a complete original trial-1 episode. Simulator may be a closing message; actor may be its last handoff/question/specification. Not necessarily a successful task submission. Roles may end at different rounds.

**Question set**: Common complete five-persona question set for BOTH roles. One final message per persona/question/role.

**Statistic**: Within each super-family: mean cosine distance across ordered distinct-question cross-persona pairs minus half the sum of the two within-persona distinct-question means. Exclude same question pairs from both quantities. Average four family effects equally (25% each).

**Permutation**: Independently swap the two persona labels within each question; keep family, benchmark and question identities fixed. This preserves question dependence without using same-question distances. One-sided alternative: cross-persona excess > 0. Monte Carlo p=(1+number of permuted statistics >= observed)/(10000+1).

**Bootstrap**: Resample whole questions within source benchmark × super-family; retain all five persona outputs together. 20000 resamples, percentile pointwise 95% CI. Exclude pairs representing the same original question even if selected twice; multiplicity-weight the remaining pairs and renormalize. Stratum sizes fixed.

**Multiplicity**: Holm correction across all 20 role × persona-pair tests. Family-specific estimates and CIs are descriptive, without additional significance testing.

**Null**: Pairwise persona-label exchangeability within each question. Tests association under this null, not causality or rollout variability.

**Limitations**: Within-persona spread includes question differences. One observed trial; bootstrap conditions on it. Source-study dependence beyond question is not modeled. Final-message functions and lengths vary by source/persona. Persona panel and endpoint were selected during exploratory analysis; results require confirmatory validation.

**Permutations**: 10000

**Bootstrap resamples**: 20000

**Seed**: 20261008

Frozen Qwen/Qwen3-Embedding-0.6B embeddings (revision 97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3), L2 normalized. Current generated messages only, without prompt/persona metadata, summaries or transcript history. Cosine distances are calculated before UMAP.

For family f and personas i,j, let Q contain n complete questions. Define B as the mean d(x_iq,x_js) over ordered q≠s; W_i and W_j are the corresponding within-persona means over q≠s. E_f=B−(W_i+W_j)/2. The overall statistic averages the four E_f values equally. Only the lower triangle is displayed; the diagonal is light gray and the redundant upper triangle is hidden; negative estimates are retained. The statistic is sensitive to shifts in mean normalized embeddings and is not an omnibus detector of every distributional difference.

The permutation preserves each question’s two outputs and changes only which persona label is attached to each output. Thus no same-question distance enters the statistic, but the randomization respects the paired collection design. A star marks Holm-adjusted one-sided p<0.05 across all 20 tests. Bootstrap intervals are pointwise, not simultaneous; their zero-crossing need not agree with Holm decisions.

## Coverage

| Role | Super-family | Questions | Weight |
|---|---|---:|---:|
| simulator | Life sciences | 41 | 25% |
| simulator | Physical / engineering | 42 | 25% |
| simulator | Math / CS | 41 | 25% |
| simulator | Social / humanities | 24 | 25% |
| actor | Life sciences | 41 | 25% |
| actor | Physical / engineering | 42 | 25% |
| actor | Math / CS | 41 | 25% |
| actor | Social / humanities | 24 | 25% |

| Source | Questions (same for both roles) |
|---|---:|
| ASI-Bench | 12 |
| BixBench | 36 |
| DiscoveryBench | 29 |
| EXP-Bench | 34 |
| SciConvBench | 37 |

## Overall pairwise results

| Role | Pair | Between | Within i | Within j | Excess [95% CI] | Permutation p | Holm p |
|---|---|---:|---:|---:|---|---:|---:|
| simulator | Persona off / Persona 155 | 0.5663 | 0.5824 | 0.5005 | 0.0249 [0.0225, 0.0271] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 001 | 0.5671 | 0.5824 | 0.4984 | 0.0267 [0.0233, 0.0302] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 004 | 0.5753 | 0.5824 | 0.5681 | 0.0000 [-0.0011, 0.0013] | 0.43906 | 0.58094 |
| simulator | Persona off / Persona 046 | 0.5985 | 0.5824 | 0.5573 | 0.0286 [0.0255, 0.0316] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 001 | 0.5336 | 0.5005 | 0.4984 | 0.0341 [0.0309, 0.0373] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 004 | 0.5572 | 0.5005 | 0.5681 | 0.0230 [0.0208, 0.0250] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 046 | 0.5695 | 0.5005 | 0.5573 | 0.0406 [0.0371, 0.0438] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 004 | 0.5569 | 0.4984 | 0.5681 | 0.0236 [0.0206, 0.0267] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 046 | 0.5542 | 0.4984 | 0.5573 | 0.0263 [0.0230, 0.0295] | 0.00010 | 0.00200 |
| simulator | Persona 004 / Persona 046 | 0.5892 | 0.5681 | 0.5573 | 0.0266 [0.0230, 0.0301] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 155 | 0.6260 | 0.6319 | 0.5873 | 0.0164 [0.0144, 0.0181] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 001 | 0.6112 | 0.6319 | 0.5718 | 0.0094 [0.0077, 0.0111] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 004 | 0.6337 | 0.6319 | 0.6353 | 0.0001 [-0.0005, 0.0007] | 0.29047 | 0.58094 |
| actor | Persona off / Persona 046 | 0.6278 | 0.6319 | 0.5917 | 0.0160 [0.0143, 0.0176] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 001 | 0.5942 | 0.5873 | 0.5718 | 0.0146 [0.0130, 0.0161] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 004 | 0.6267 | 0.5873 | 0.6353 | 0.0155 [0.0137, 0.0171] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 046 | 0.6093 | 0.5873 | 0.5917 | 0.0197 [0.0178, 0.0216] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 004 | 0.6121 | 0.5718 | 0.6353 | 0.0086 [0.0070, 0.0103] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 046 | 0.5953 | 0.5718 | 0.5917 | 0.0136 [0.0118, 0.0152] | 0.00010 | 0.00200 |
| actor | Persona 004 / Persona 046 | 0.6287 | 0.6353 | 0.5917 | 0.0152 [0.0135, 0.0169] | 0.00010 | 0.00200 |

## Family-specific descriptive estimates

| Role | Super-family | Pair | Excess [95% CI] | Questions |
|---|---|---|---|---:|
| simulator | Life sciences | Persona off / Persona 155 | 0.0236 [0.0187, 0.0291] | 41 |
| simulator | Physical / engineering | Persona off / Persona 155 | 0.0140 [0.0101, 0.0174] | 42 |
| simulator | Math / CS | Persona off / Persona 155 | 0.0436 [0.0385, 0.0487] | 41 |
| simulator | Social / humanities | Persona off / Persona 155 | 0.0184 [0.0143, 0.0230] | 24 |
| simulator | Life sciences | Persona off / Persona 001 | 0.0314 [0.0236, 0.0401] | 41 |
| simulator | Physical / engineering | Persona off / Persona 001 | 0.0112 [0.0075, 0.0153] | 42 |
| simulator | Math / CS | Persona off / Persona 001 | 0.0348 [0.0288, 0.0401] | 41 |
| simulator | Social / humanities | Persona off / Persona 001 | 0.0295 [0.0224, 0.0392] | 24 |
| simulator | Life sciences | Persona off / Persona 004 | -0.0001 [-0.0021, 0.0024] | 41 |
| simulator | Physical / engineering | Persona off / Persona 004 | -0.0006 [-0.0026, 0.0014] | 42 |
| simulator | Math / CS | Persona off / Persona 004 | 0.0002 [-0.0016, 0.0022] | 41 |
| simulator | Social / humanities | Persona off / Persona 004 | 0.0006 [-0.0021, 0.0041] | 24 |
| simulator | Life sciences | Persona off / Persona 046 | 0.0198 [0.0159, 0.0243] | 41 |
| simulator | Physical / engineering | Persona off / Persona 046 | 0.0157 [0.0118, 0.0193] | 42 |
| simulator | Math / CS | Persona off / Persona 046 | 0.0452 [0.0393, 0.0507] | 41 |
| simulator | Social / humanities | Persona off / Persona 046 | 0.0338 [0.0249, 0.0436] | 24 |
| simulator | Life sciences | Persona 155 / Persona 001 | 0.0288 [0.0234, 0.0354] | 41 |
| simulator | Physical / engineering | Persona 155 / Persona 001 | 0.0192 [0.0142, 0.0246] | 42 |
| simulator | Math / CS | Persona 155 / Persona 001 | 0.0547 [0.0473, 0.0619] | 41 |
| simulator | Social / humanities | Persona 155 / Persona 001 | 0.0339 [0.0274, 0.0414] | 24 |
| simulator | Life sciences | Persona 155 / Persona 004 | 0.0219 [0.0177, 0.0270] | 41 |
| simulator | Physical / engineering | Persona 155 / Persona 004 | 0.0126 [0.0090, 0.0158] | 42 |
| simulator | Math / CS | Persona 155 / Persona 004 | 0.0379 [0.0331, 0.0422] | 41 |
| simulator | Social / humanities | Persona 155 / Persona 004 | 0.0194 [0.0157, 0.0235] | 24 |
| simulator | Life sciences | Persona 155 / Persona 046 | 0.0316 [0.0265, 0.0370] | 41 |
| simulator | Physical / engineering | Persona 155 / Persona 046 | 0.0233 [0.0175, 0.0288] | 42 |
| simulator | Math / CS | Persona 155 / Persona 046 | 0.0672 [0.0604, 0.0731] | 41 |
| simulator | Social / humanities | Persona 155 / Persona 046 | 0.0403 [0.0316, 0.0501] | 24 |
| simulator | Life sciences | Persona 001 / Persona 004 | 0.0272 [0.0202, 0.0356] | 41 |
| simulator | Physical / engineering | Persona 001 / Persona 004 | 0.0083 [0.0049, 0.0123] | 42 |
| simulator | Math / CS | Persona 001 / Persona 004 | 0.0315 [0.0258, 0.0367] | 41 |
| simulator | Social / humanities | Persona 001 / Persona 004 | 0.0275 [0.0217, 0.0350] | 24 |
| simulator | Life sciences | Persona 001 / Persona 046 | 0.0254 [0.0189, 0.0329] | 41 |
| simulator | Physical / engineering | Persona 001 / Persona 046 | 0.0100 [0.0062, 0.0145] | 42 |
| simulator | Math / CS | Persona 001 / Persona 046 | 0.0410 [0.0348, 0.0464] | 41 |
| simulator | Social / humanities | Persona 001 / Persona 046 | 0.0289 [0.0211, 0.0378] | 24 |
| simulator | Life sciences | Persona 004 / Persona 046 | 0.0191 [0.0142, 0.0250] | 41 |
| simulator | Physical / engineering | Persona 004 / Persona 046 | 0.0148 [0.0106, 0.0192] | 42 |
| simulator | Math / CS | Persona 004 / Persona 046 | 0.0410 [0.0358, 0.0461] | 41 |
| simulator | Social / humanities | Persona 004 / Persona 046 | 0.0313 [0.0207, 0.0430] | 24 |
| actor | Life sciences | Persona off / Persona 155 | 0.0104 [0.0066, 0.0145] | 41 |
| actor | Physical / engineering | Persona off / Persona 155 | 0.0210 [0.0176, 0.0247] | 42 |
| actor | Math / CS | Persona off / Persona 155 | 0.0189 [0.0164, 0.0214] | 41 |
| actor | Social / humanities | Persona off / Persona 155 | 0.0150 [0.0105, 0.0195] | 24 |
| actor | Life sciences | Persona off / Persona 001 | 0.0055 [0.0034, 0.0080] | 41 |
| actor | Physical / engineering | Persona off / Persona 001 | 0.0073 [0.0038, 0.0114] | 42 |
| actor | Math / CS | Persona off / Persona 001 | 0.0110 [0.0084, 0.0139] | 41 |
| actor | Social / humanities | Persona off / Persona 001 | 0.0137 [0.0097, 0.0186] | 24 |
| actor | Life sciences | Persona off / Persona 004 | 0.0005 [-0.0009, 0.0021] | 41 |
| actor | Physical / engineering | Persona off / Persona 004 | 0.0001 [-0.0004, 0.0006] | 42 |
| actor | Math / CS | Persona off / Persona 004 | -0.0000 [-0.0005, 0.0005] | 41 |
| actor | Social / humanities | Persona off / Persona 004 | -0.0002 [-0.0016, 0.0015] | 24 |
| actor | Life sciences | Persona off / Persona 046 | 0.0124 [0.0095, 0.0153] | 41 |
| actor | Physical / engineering | Persona off / Persona 046 | 0.0174 [0.0139, 0.0211] | 42 |
| actor | Math / CS | Persona off / Persona 046 | 0.0173 [0.0150, 0.0197] | 41 |
| actor | Social / humanities | Persona off / Persona 046 | 0.0169 [0.0132, 0.0214] | 24 |
| actor | Life sciences | Persona 155 / Persona 001 | 0.0088 [0.0057, 0.0122] | 41 |
| actor | Physical / engineering | Persona 155 / Persona 001 | 0.0134 [0.0110, 0.0159] | 42 |
| actor | Math / CS | Persona 155 / Persona 001 | 0.0219 [0.0192, 0.0245] | 41 |
| actor | Social / humanities | Persona 155 / Persona 001 | 0.0143 [0.0107, 0.0185] | 24 |
| actor | Life sciences | Persona 155 / Persona 004 | 0.0098 [0.0062, 0.0135] | 41 |
| actor | Physical / engineering | Persona 155 / Persona 004 | 0.0201 [0.0168, 0.0238] | 42 |
| actor | Math / CS | Persona 155 / Persona 004 | 0.0179 [0.0153, 0.0204] | 41 |
| actor | Social / humanities | Persona 155 / Persona 004 | 0.0140 [0.0102, 0.0179] | 24 |
| actor | Life sciences | Persona 155 / Persona 046 | 0.0151 [0.0113, 0.0189] | 41 |
| actor | Physical / engineering | Persona 155 / Persona 046 | 0.0193 [0.0160, 0.0228] | 42 |
| actor | Math / CS | Persona 155 / Persona 046 | 0.0256 [0.0229, 0.0280] | 41 |
| actor | Social / humanities | Persona 155 / Persona 046 | 0.0190 [0.0144, 0.0240] | 24 |
| actor | Life sciences | Persona 001 / Persona 004 | 0.0054 [0.0032, 0.0079] | 41 |
| actor | Physical / engineering | Persona 001 / Persona 004 | 0.0061 [0.0028, 0.0102] | 42 |
| actor | Math / CS | Persona 001 / Persona 004 | 0.0106 [0.0082, 0.0130] | 41 |
| actor | Social / humanities | Persona 001 / Persona 004 | 0.0123 [0.0080, 0.0171] | 24 |
| actor | Life sciences | Persona 001 / Persona 046 | 0.0113 [0.0084, 0.0144] | 41 |
| actor | Physical / engineering | Persona 001 / Persona 046 | 0.0108 [0.0079, 0.0140] | 42 |
| actor | Math / CS | Persona 001 / Persona 046 | 0.0148 [0.0124, 0.0174] | 41 |
| actor | Social / humanities | Persona 001 / Persona 046 | 0.0174 [0.0128, 0.0222] | 24 |
| actor | Life sciences | Persona 004 / Persona 046 | 0.0119 [0.0091, 0.0147] | 41 |
| actor | Physical / engineering | Persona 004 / Persona 046 | 0.0167 [0.0129, 0.0205] | 42 |
| actor | Math / CS | Persona 004 / Persona 046 | 0.0165 [0.0144, 0.0188] | 41 |
| actor | Social / humanities | Persona 004 / Persona 046 | 0.0158 [0.0117, 0.0204] | 24 |

## Right-hand examples unchanged

Two examples manually selected by the user after inspecting the length-enriched UMAP gallery: bix-57-q1 and matToolUse/disambiguation/case_236. These are illustrative, not representative or independent aggregate evidence. All five settings are retained with their actual lengths, including one-round trajectories.

Local cosine UMAP jointly fit across all five settings and observed trial-1 messages, separately per question and role. n_neighbors=min(15,N−1), min_dist=0.1, 500 epochs, spectral init, random_state=42, transform_seed=42, n_jobs=1. Frozen coordinates copied exactly from the reviewed gallery; model and software provenance in umap.json and the gallery manifest. Local distances and path lengths are not effect sizes.

Cases: `bix-57-q1` and `matToolUse/disambiguation/case_236`, all five settings at trial 1. Exact reviewed UMAP coordinates remain fixed. No point indices or arrows; diamonds identify final nodes. Curved connections are visual guides, not observed intermediate states. These examples are not independent statistical evidence.

## Reproducibility

`code/semantic/final_response.py` selects the final messages and writes the new statistics under `data/semantic_final/`; `test_final_response.py` checks direct-distance equivalence for all swaps of a small dataset, duplicate-aware bootstrap arithmetic and Holm correction. The notebook can recompute statistics from cached embeddings. No API calls or new embeddings. Earlier round-matched statistics remain under `data/semantic/` and the preceding figure is archived under `figures/semantic/previous_raw_heatmap/`.
