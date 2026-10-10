# Final-response semantic separation and illustrative trajectories

[Executed notebook](semantic_trajectory_analysis.ipynb) · [Figure](figures/semantic/semantic.pdf) · [Candidate caption and figure handoff](SEMANTIC_FIGURE_CAPTION.md)

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
| simulator | Life sciences | 30 | 25% |
| simulator | Physical / engineering | 37 | 25% |
| simulator | Math / CS | 13 | 25% |
| simulator | Social / humanities | 17 | 25% |
| actor | Life sciences | 30 | 25% |
| actor | Physical / engineering | 37 | 25% |
| actor | Math / CS | 13 | 25% |
| actor | Social / humanities | 17 | 25% |

| Source | Questions (same for both roles) |
|---|---:|
| ASI-Bench | 7 |
| BixBench | 27 |
| DiscoveryBench | 21 |
| EXP-Bench | 5 |
| SciConvBench | 37 |

## Overall pairwise results

| Role | Pair | Between | Within i | Within j | Excess [95% CI] | Permutation p | Holm p |
|---|---|---:|---:|---:|---|---:|---:|
| simulator | Persona off / Persona 155 | 0.5879 | 0.6067 | 0.5230 | 0.0231 [0.0196, 0.0260] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 001 | 0.5946 | 0.6067 | 0.5357 | 0.0234 [0.0192, 0.0269] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 003 | 0.6167 | 0.6067 | 0.5445 | 0.0412 [0.0352, 0.0470] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 046 | 0.6215 | 0.6067 | 0.5887 | 0.0238 [0.0199, 0.0274] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 001 | 0.5558 | 0.5230 | 0.5357 | 0.0264 [0.0222, 0.0299] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 003 | 0.5767 | 0.5230 | 0.5445 | 0.0430 [0.0377, 0.0483] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 046 | 0.5910 | 0.5230 | 0.5887 | 0.0352 [0.0297, 0.0399] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 003 | 0.5803 | 0.5357 | 0.5445 | 0.0402 [0.0354, 0.0444] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 046 | 0.5837 | 0.5357 | 0.5887 | 0.0214 [0.0171, 0.0255] | 0.00010 | 0.00200 |
| simulator | Persona 003 / Persona 046 | 0.6138 | 0.5445 | 0.5887 | 0.0472 [0.0398, 0.0544] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 155 | 0.6385 | 0.6485 | 0.5970 | 0.0157 [0.0130, 0.0183] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 001 | 0.6379 | 0.6485 | 0.6118 | 0.0077 [0.0057, 0.0100] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 003 | 0.6487 | 0.6485 | 0.6036 | 0.0226 [0.0188, 0.0263] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 046 | 0.6456 | 0.6485 | 0.6156 | 0.0136 [0.0114, 0.0156] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 001 | 0.6161 | 0.5970 | 0.6118 | 0.0117 [0.0094, 0.0136] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 003 | 0.6254 | 0.5970 | 0.6036 | 0.0250 [0.0213, 0.0282] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 046 | 0.6230 | 0.5970 | 0.6156 | 0.0167 [0.0140, 0.0190] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 003 | 0.6276 | 0.6118 | 0.6036 | 0.0199 [0.0164, 0.0233] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 046 | 0.6237 | 0.6118 | 0.6156 | 0.0100 [0.0079, 0.0122] | 0.00010 | 0.00200 |
| actor | Persona 003 / Persona 046 | 0.6331 | 0.6036 | 0.6156 | 0.0235 [0.0203, 0.0265] | 0.00010 | 0.00200 |

## Family-specific descriptive estimates

| Role | Super-family | Pair | Excess [95% CI] | Questions |
|---|---|---|---|---:|
| simulator | Life sciences | Persona off / Persona 155 | 0.0280 [0.0217, 0.0349] | 30 |
| simulator | Physical / engineering | Persona off / Persona 155 | 0.0137 [0.0096, 0.0180] | 37 |
| simulator | Math / CS | Persona off / Persona 155 | 0.0299 [0.0209, 0.0365] | 13 |
| simulator | Social / humanities | Persona off / Persona 155 | 0.0208 [0.0137, 0.0275] | 17 |
| simulator | Life sciences | Persona off / Persona 001 | 0.0342 [0.0261, 0.0436] | 30 |
| simulator | Physical / engineering | Persona off / Persona 001 | 0.0106 [0.0064, 0.0153] | 37 |
| simulator | Math / CS | Persona off / Persona 001 | 0.0200 [0.0116, 0.0235] | 13 |
| simulator | Social / humanities | Persona off / Persona 001 | 0.0287 [0.0200, 0.0406] | 17 |
| simulator | Life sciences | Persona off / Persona 003 | 0.0315 [0.0244, 0.0400] | 30 |
| simulator | Physical / engineering | Persona off / Persona 003 | 0.0283 [0.0223, 0.0343] | 37 |
| simulator | Math / CS | Persona off / Persona 003 | 0.0441 [0.0319, 0.0535] | 13 |
| simulator | Social / humanities | Persona off / Persona 003 | 0.0608 [0.0447, 0.0804] | 17 |
| simulator | Life sciences | Persona off / Persona 046 | 0.0172 [0.0132, 0.0213] | 30 |
| simulator | Physical / engineering | Persona off / Persona 046 | 0.0147 [0.0109, 0.0184] | 37 |
| simulator | Math / CS | Persona off / Persona 046 | 0.0285 [0.0200, 0.0336] | 13 |
| simulator | Social / humanities | Persona off / Persona 046 | 0.0348 [0.0240, 0.0483] | 17 |
| simulator | Life sciences | Persona 155 / Persona 001 | 0.0259 [0.0207, 0.0320] | 30 |
| simulator | Physical / engineering | Persona 155 / Persona 001 | 0.0181 [0.0126, 0.0242] | 37 |
| simulator | Math / CS | Persona 155 / Persona 001 | 0.0312 [0.0217, 0.0364] | 13 |
| simulator | Social / humanities | Persona 155 / Persona 001 | 0.0305 [0.0206, 0.0425] | 17 |
| simulator | Life sciences | Persona 155 / Persona 003 | 0.0351 [0.0292, 0.0424] | 30 |
| simulator | Physical / engineering | Persona 155 / Persona 003 | 0.0368 [0.0309, 0.0426] | 37 |
| simulator | Math / CS | Persona 155 / Persona 003 | 0.0434 [0.0352, 0.0493] | 13 |
| simulator | Social / humanities | Persona 155 / Persona 003 | 0.0566 [0.0405, 0.0761] | 17 |
| simulator | Life sciences | Persona 155 / Persona 046 | 0.0322 [0.0261, 0.0388] | 30 |
| simulator | Physical / engineering | Persona 155 / Persona 046 | 0.0213 [0.0155, 0.0275] | 37 |
| simulator | Math / CS | Persona 155 / Persona 046 | 0.0456 [0.0328, 0.0552] | 13 |
| simulator | Social / humanities | Persona 155 / Persona 046 | 0.0416 [0.0284, 0.0570] | 17 |
| simulator | Life sciences | Persona 001 / Persona 003 | 0.0303 [0.0252, 0.0359] | 30 |
| simulator | Physical / engineering | Persona 001 / Persona 003 | 0.0359 [0.0293, 0.0432] | 37 |
| simulator | Math / CS | Persona 001 / Persona 003 | 0.0390 [0.0312, 0.0443] | 13 |
| simulator | Social / humanities | Persona 001 / Persona 003 | 0.0555 [0.0420, 0.0704] | 17 |
| simulator | Life sciences | Persona 001 / Persona 046 | 0.0253 [0.0175, 0.0348] | 30 |
| simulator | Physical / engineering | Persona 001 / Persona 046 | 0.0089 [0.0045, 0.0140] | 37 |
| simulator | Math / CS | Persona 001 / Persona 046 | 0.0231 [0.0149, 0.0274] | 13 |
| simulator | Social / humanities | Persona 001 / Persona 046 | 0.0284 [0.0181, 0.0423] | 17 |
| simulator | Life sciences | Persona 003 / Persona 046 | 0.0355 [0.0277, 0.0453] | 30 |
| simulator | Physical / engineering | Persona 003 / Persona 046 | 0.0365 [0.0313, 0.0417] | 37 |
| simulator | Math / CS | Persona 003 / Persona 046 | 0.0464 [0.0367, 0.0533] | 13 |
| simulator | Social / humanities | Persona 003 / Persona 046 | 0.0702 [0.0460, 0.0978] | 17 |
| actor | Life sciences | Persona off / Persona 155 | 0.0089 [0.0051, 0.0127] | 30 |
| actor | Physical / engineering | Persona off / Persona 155 | 0.0225 [0.0186, 0.0268] | 37 |
| actor | Math / CS | Persona off / Persona 155 | 0.0131 [0.0069, 0.0192] | 13 |
| actor | Social / humanities | Persona off / Persona 155 | 0.0185 [0.0125, 0.0253] | 17 |
| actor | Life sciences | Persona off / Persona 001 | 0.0053 [0.0029, 0.0080] | 30 |
| actor | Physical / engineering | Persona off / Persona 001 | 0.0067 [0.0030, 0.0114] | 37 |
| actor | Math / CS | Persona off / Persona 001 | 0.0053 [0.0021, 0.0096] | 13 |
| actor | Social / humanities | Persona off / Persona 001 | 0.0134 [0.0086, 0.0206] | 17 |
| actor | Life sciences | Persona off / Persona 003 | 0.0199 [0.0135, 0.0263] | 30 |
| actor | Physical / engineering | Persona off / Persona 003 | 0.0242 [0.0178, 0.0306] | 37 |
| actor | Math / CS | Persona off / Persona 003 | 0.0120 [0.0074, 0.0176] | 13 |
| actor | Social / humanities | Persona off / Persona 003 | 0.0343 [0.0238, 0.0450] | 17 |
| actor | Life sciences | Persona off / Persona 046 | 0.0116 [0.0083, 0.0149] | 30 |
| actor | Physical / engineering | Persona off / Persona 046 | 0.0171 [0.0131, 0.0213] | 37 |
| actor | Math / CS | Persona off / Persona 046 | 0.0070 [0.0037, 0.0100] | 13 |
| actor | Social / humanities | Persona off / Persona 046 | 0.0187 [0.0133, 0.0249] | 17 |
| actor | Life sciences | Persona 155 / Persona 001 | 0.0075 [0.0040, 0.0113] | 30 |
| actor | Physical / engineering | Persona 155 / Persona 001 | 0.0137 [0.0108, 0.0172] | 37 |
| actor | Math / CS | Persona 155 / Persona 001 | 0.0104 [0.0049, 0.0146] | 13 |
| actor | Social / humanities | Persona 155 / Persona 001 | 0.0152 [0.0108, 0.0204] | 17 |
| actor | Life sciences | Persona 155 / Persona 003 | 0.0210 [0.0147, 0.0275] | 30 |
| actor | Physical / engineering | Persona 155 / Persona 003 | 0.0276 [0.0224, 0.0329] | 37 |
| actor | Math / CS | Persona 155 / Persona 003 | 0.0159 [0.0094, 0.0215] | 13 |
| actor | Social / humanities | Persona 155 / Persona 003 | 0.0356 [0.0260, 0.0441] | 17 |
| actor | Life sciences | Persona 155 / Persona 046 | 0.0140 [0.0094, 0.0183] | 30 |
| actor | Physical / engineering | Persona 155 / Persona 046 | 0.0185 [0.0150, 0.0225] | 37 |
| actor | Math / CS | Persona 155 / Persona 046 | 0.0131 [0.0074, 0.0178] | 13 |
| actor | Social / humanities | Persona 155 / Persona 046 | 0.0211 [0.0153, 0.0282] | 17 |
| actor | Life sciences | Persona 001 / Persona 003 | 0.0195 [0.0128, 0.0266] | 30 |
| actor | Physical / engineering | Persona 001 / Persona 003 | 0.0218 [0.0160, 0.0277] | 37 |
| actor | Math / CS | Persona 001 / Persona 003 | 0.0090 [0.0043, 0.0135] | 13 |
| actor | Social / humanities | Persona 001 / Persona 003 | 0.0293 [0.0200, 0.0388] | 17 |
| actor | Life sciences | Persona 001 / Persona 046 | 0.0092 [0.0065, 0.0123] | 30 |
| actor | Physical / engineering | Persona 001 / Persona 046 | 0.0104 [0.0071, 0.0142] | 37 |
| actor | Math / CS | Persona 001 / Persona 046 | 0.0052 [0.0020, 0.0086] | 13 |
| actor | Social / humanities | Persona 001 / Persona 046 | 0.0153 [0.0092, 0.0221] | 17 |
| actor | Life sciences | Persona 003 / Persona 046 | 0.0253 [0.0185, 0.0323] | 30 |
| actor | Physical / engineering | Persona 003 / Persona 046 | 0.0199 [0.0157, 0.0239] | 37 |
| actor | Math / CS | Persona 003 / Persona 046 | 0.0130 [0.0081, 0.0181] | 13 |
| actor | Social / humanities | Persona 003 / Persona 046 | 0.0359 [0.0275, 0.0437] | 17 |

## Right-hand examples unchanged

Two examples manually selected by the user after inspecting the length-enriched UMAP gallery: bix-57-q1 and matToolUse/disambiguation/case_236. These are illustrative, not representative or independent aggregate evidence. All five settings are retained with their actual lengths, including one-round trajectories.

Local cosine UMAP jointly refitted after replacing 089 with 003, across all five settings and observed trial-1 messages, separately per question and role. n_neighbors=min(15,N−1), min_dist=0.1, 500 epochs, spectral init, random_state=42, transform_seed=42, n_jobs=1. Case IDs remain user-selected from the earlier 004-panel gallery. Local coordinates and path lengths are not effect sizes.

Cases: `bix-57-q1` and `matToolUse/disambiguation/case_236`, all five settings at trial 1. UMAP is jointly refitted for off/155/001/003/046 after replacing 089; case IDs and projection parameters remain unchanged. No point indices or arrows; hollow circles identify starts, larger solid circles identify ends, and smaller filled dots identify intermediate rounds. A single-node trajectory is shown as a filled dot inside a hollow circle. Curved connections are visual guides, not observed intermediate states. These examples are not independent statistical evidence.

## Reproducibility

`code/semantic/final_response.py` selects the final messages and writes the new statistics under `data/semantic_final/`; `test_final_response.py` checks direct-distance equivalence for all swaps of a small dataset, duplicate-aware bootstrap arithmetic and Holm correction. The notebook can recompute statistics from cached embeddings. No API calls; saved persona 003 messages were newly embedded locally with the same frozen encoder. Earlier round-matched statistics remain under `data/semantic/` and the preceding figure is archived under `figures/semantic/previous_raw_heatmap/`.


## Exploratory 003 replacement and sensitivity

Persona 003 specifies Russian output and blunt, slangy, concrete, detailed communication. Language may contribute to separation. It has only 104 completed original trial-1 episodes; the common panel is smaller than for 089. Restricting the current panel to 95 questions shared with the previous 089 panel gives significant-pair counts {'simulator': 10, 'actor': 10}. [Sensitivity estimates and p values](data/semantic_final/shared_questions_sensitivity/heatmap_cells.csv). Prior 089 outputs are archived under `figures/semantic/previous_persona_089/`. Holm corrects the current 20 tests, not all panels explored. These post-selection results are exploratory.
