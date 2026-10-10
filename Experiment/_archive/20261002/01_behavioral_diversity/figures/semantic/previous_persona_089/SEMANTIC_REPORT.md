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
| simulator | Life sciences | 42 | 25% |
| simulator | Physical / engineering | 46 | 25% |
| simulator | Math / CS | 45 | 25% |
| simulator | Social / humanities | 25 | 25% |
| actor | Life sciences | 42 | 25% |
| actor | Physical / engineering | 46 | 25% |
| actor | Math / CS | 45 | 25% |
| actor | Social / humanities | 25 | 25% |

| Source | Questions (same for both roles) |
|---|---:|
| ASI-Bench | 17 |
| BixBench | 37 |
| DiscoveryBench | 31 |
| EXP-Bench | 36 |
| SciConvBench | 37 |

## Overall pairwise results

| Role | Pair | Between | Within i | Within j | Excess [95% CI] | Permutation p | Holm p |
|---|---|---:|---:|---:|---|---:|---:|
| simulator | Persona off / Persona 155 | 0.5640 | 0.5819 | 0.4963 | 0.0249 [0.0227, 0.0270] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 001 | 0.5674 | 0.5819 | 0.5003 | 0.0263 [0.0231, 0.0295] | 0.00010 | 0.00200 |
| simulator | Persona off / Persona 089 | 0.5756 | 0.5819 | 0.5688 | 0.0003 [-0.0008, 0.0013] | 0.19298 | 0.38596 |
| simulator | Persona off / Persona 046 | 0.5997 | 0.5819 | 0.5589 | 0.0293 [0.0261, 0.0326] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 001 | 0.5314 | 0.4963 | 0.5003 | 0.0330 [0.0298, 0.0362] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 089 | 0.5564 | 0.4963 | 0.5688 | 0.0238 [0.0218, 0.0257] | 0.00010 | 0.00200 |
| simulator | Persona 155 / Persona 046 | 0.5684 | 0.4963 | 0.5589 | 0.0408 [0.0374, 0.0441] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 089 | 0.5584 | 0.5003 | 0.5688 | 0.0239 [0.0206, 0.0271] | 0.00010 | 0.00200 |
| simulator | Persona 001 / Persona 046 | 0.5553 | 0.5003 | 0.5589 | 0.0257 [0.0225, 0.0289] | 0.00010 | 0.00200 |
| simulator | Persona 089 / Persona 046 | 0.5915 | 0.5688 | 0.5589 | 0.0277 [0.0246, 0.0307] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 155 | 0.6258 | 0.6323 | 0.5865 | 0.0164 [0.0145, 0.0182] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 001 | 0.6110 | 0.6323 | 0.5712 | 0.0093 [0.0077, 0.0110] | 0.00010 | 0.00200 |
| actor | Persona off / Persona 089 | 0.6362 | 0.6323 | 0.6400 | 0.0001 [-0.0004, 0.0007] | 0.22328 | 0.38596 |
| actor | Persona off / Persona 046 | 0.6280 | 0.6323 | 0.5910 | 0.0163 [0.0146, 0.0180] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 001 | 0.5933 | 0.5865 | 0.5712 | 0.0145 [0.0129, 0.0161] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 089 | 0.6291 | 0.5865 | 0.6400 | 0.0159 [0.0141, 0.0175] | 0.00010 | 0.00200 |
| actor | Persona 155 / Persona 046 | 0.6087 | 0.5865 | 0.5910 | 0.0199 [0.0181, 0.0216] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 089 | 0.6151 | 0.5712 | 0.6400 | 0.0095 [0.0080, 0.0111] | 0.00010 | 0.00200 |
| actor | Persona 001 / Persona 046 | 0.5950 | 0.5712 | 0.5910 | 0.0139 [0.0123, 0.0156] | 0.00010 | 0.00200 |
| actor | Persona 089 / Persona 046 | 0.6318 | 0.6400 | 0.5910 | 0.0162 [0.0146, 0.0178] | 0.00010 | 0.00200 |

## Family-specific descriptive estimates

| Role | Super-family | Pair | Excess [95% CI] | Questions |
|---|---|---|---|---:|
| simulator | Life sciences | Persona off / Persona 155 | 0.0232 [0.0184, 0.0284] | 42 |
| simulator | Physical / engineering | Persona off / Persona 155 | 0.0154 [0.0118, 0.0187] | 46 |
| simulator | Math / CS | Persona off / Persona 155 | 0.0427 [0.0380, 0.0473] | 45 |
| simulator | Social / humanities | Persona off / Persona 155 | 0.0183 [0.0145, 0.0228] | 25 |
| simulator | Life sciences | Persona off / Persona 001 | 0.0303 [0.0225, 0.0390] | 42 |
| simulator | Physical / engineering | Persona off / Persona 001 | 0.0124 [0.0089, 0.0160] | 46 |
| simulator | Math / CS | Persona off / Persona 001 | 0.0335 [0.0282, 0.0383] | 45 |
| simulator | Social / humanities | Persona off / Persona 001 | 0.0288 [0.0221, 0.0375] | 25 |
| simulator | Life sciences | Persona off / Persona 089 | -0.0004 [-0.0022, 0.0017] | 42 |
| simulator | Physical / engineering | Persona off / Persona 089 | -0.0005 [-0.0020, 0.0010] | 46 |
| simulator | Math / CS | Persona off / Persona 089 | 0.0014 [-0.0007, 0.0037] | 45 |
| simulator | Social / humanities | Persona off / Persona 089 | 0.0005 [-0.0020, 0.0033] | 25 |
| simulator | Life sciences | Persona off / Persona 046 | 0.0197 [0.0160, 0.0240] | 42 |
| simulator | Physical / engineering | Persona off / Persona 046 | 0.0170 [0.0134, 0.0204] | 46 |
| simulator | Math / CS | Persona off / Persona 046 | 0.0437 [0.0385, 0.0486] | 45 |
| simulator | Social / humanities | Persona off / Persona 046 | 0.0368 [0.0267, 0.0484] | 25 |
| simulator | Life sciences | Persona 155 / Persona 001 | 0.0281 [0.0228, 0.0345] | 42 |
| simulator | Physical / engineering | Persona 155 / Persona 001 | 0.0204 [0.0158, 0.0253] | 46 |
| simulator | Math / CS | Persona 155 / Persona 001 | 0.0521 [0.0454, 0.0586] | 45 |
| simulator | Social / humanities | Persona 155 / Persona 001 | 0.0315 [0.0241, 0.0396] | 25 |
| simulator | Life sciences | Persona 155 / Persona 089 | 0.0237 [0.0195, 0.0283] | 42 |
| simulator | Physical / engineering | Persona 155 / Persona 089 | 0.0138 [0.0107, 0.0165] | 46 |
| simulator | Math / CS | Persona 155 / Persona 089 | 0.0384 [0.0337, 0.0432] | 45 |
| simulator | Social / humanities | Persona 155 / Persona 089 | 0.0195 [0.0162, 0.0232] | 25 |
| simulator | Life sciences | Persona 155 / Persona 046 | 0.0315 [0.0265, 0.0367] | 42 |
| simulator | Physical / engineering | Persona 155 / Persona 046 | 0.0243 [0.0192, 0.0293] | 46 |
| simulator | Math / CS | Persona 155 / Persona 046 | 0.0662 [0.0599, 0.0715] | 45 |
| simulator | Social / humanities | Persona 155 / Persona 046 | 0.0412 [0.0323, 0.0514] | 25 |
| simulator | Life sciences | Persona 001 / Persona 089 | 0.0306 [0.0219, 0.0408] | 42 |
| simulator | Physical / engineering | Persona 001 / Persona 089 | 0.0113 [0.0080, 0.0148] | 46 |
| simulator | Math / CS | Persona 001 / Persona 089 | 0.0281 [0.0233, 0.0327] | 45 |
| simulator | Social / humanities | Persona 001 / Persona 089 | 0.0254 [0.0194, 0.0328] | 25 |
| simulator | Life sciences | Persona 001 / Persona 046 | 0.0248 [0.0184, 0.0320] | 42 |
| simulator | Physical / engineering | Persona 001 / Persona 046 | 0.0114 [0.0077, 0.0153] | 46 |
| simulator | Math / CS | Persona 001 / Persona 046 | 0.0385 [0.0330, 0.0432] | 45 |
| simulator | Social / humanities | Persona 001 / Persona 046 | 0.0282 [0.0203, 0.0376] | 25 |
| simulator | Life sciences | Persona 089 / Persona 046 | 0.0207 [0.0160, 0.0263] | 42 |
| simulator | Physical / engineering | Persona 089 / Persona 046 | 0.0176 [0.0134, 0.0218] | 46 |
| simulator | Math / CS | Persona 089 / Persona 046 | 0.0374 [0.0324, 0.0420] | 45 |
| simulator | Social / humanities | Persona 089 / Persona 046 | 0.0350 [0.0267, 0.0447] | 25 |
| actor | Life sciences | Persona off / Persona 155 | 0.0102 [0.0065, 0.0141] | 42 |
| actor | Physical / engineering | Persona off / Persona 155 | 0.0203 [0.0172, 0.0235] | 46 |
| actor | Math / CS | Persona off / Persona 155 | 0.0188 [0.0162, 0.0213] | 45 |
| actor | Social / humanities | Persona off / Persona 155 | 0.0163 [0.0115, 0.0213] | 25 |
| actor | Life sciences | Persona off / Persona 001 | 0.0052 [0.0031, 0.0077] | 42 |
| actor | Physical / engineering | Persona off / Persona 001 | 0.0073 [0.0042, 0.0110] | 46 |
| actor | Math / CS | Persona off / Persona 001 | 0.0113 [0.0087, 0.0141] | 45 |
| actor | Social / humanities | Persona off / Persona 001 | 0.0132 [0.0093, 0.0181] | 25 |
| actor | Life sciences | Persona off / Persona 089 | 0.0000 [-0.0012, 0.0014] | 42 |
| actor | Physical / engineering | Persona off / Persona 089 | -0.0002 [-0.0006, 0.0003] | 46 |
| actor | Math / CS | Persona off / Persona 089 | 0.0003 [-0.0003, 0.0010] | 45 |
| actor | Social / humanities | Persona off / Persona 089 | 0.0003 [-0.0011, 0.0019] | 25 |
| actor | Life sciences | Persona off / Persona 046 | 0.0124 [0.0096, 0.0151] | 42 |
| actor | Physical / engineering | Persona off / Persona 046 | 0.0176 [0.0142, 0.0210] | 46 |
| actor | Math / CS | Persona off / Persona 046 | 0.0175 [0.0153, 0.0198] | 45 |
| actor | Social / humanities | Persona off / Persona 046 | 0.0179 [0.0138, 0.0231] | 25 |
| actor | Life sciences | Persona 155 / Persona 001 | 0.0090 [0.0059, 0.0123] | 42 |
| actor | Physical / engineering | Persona 155 / Persona 001 | 0.0131 [0.0111, 0.0153] | 46 |
| actor | Math / CS | Persona 155 / Persona 001 | 0.0211 [0.0186, 0.0235] | 45 |
| actor | Social / humanities | Persona 155 / Persona 001 | 0.0147 [0.0107, 0.0196] | 25 |
| actor | Life sciences | Persona 155 / Persona 089 | 0.0092 [0.0059, 0.0123] | 42 |
| actor | Physical / engineering | Persona 155 / Persona 089 | 0.0208 [0.0179, 0.0239] | 46 |
| actor | Math / CS | Persona 155 / Persona 089 | 0.0182 [0.0156, 0.0208] | 45 |
| actor | Social / humanities | Persona 155 / Persona 089 | 0.0154 [0.0109, 0.0202] | 25 |
| actor | Life sciences | Persona 155 / Persona 046 | 0.0152 [0.0114, 0.0188] | 42 |
| actor | Physical / engineering | Persona 155 / Persona 046 | 0.0193 [0.0164, 0.0223] | 46 |
| actor | Math / CS | Persona 155 / Persona 046 | 0.0251 [0.0227, 0.0273] | 45 |
| actor | Social / humanities | Persona 155 / Persona 046 | 0.0201 [0.0157, 0.0252] | 25 |
| actor | Life sciences | Persona 001 / Persona 089 | 0.0047 [0.0028, 0.0067] | 42 |
| actor | Physical / engineering | Persona 001 / Persona 089 | 0.0074 [0.0042, 0.0112] | 46 |
| actor | Math / CS | Persona 001 / Persona 089 | 0.0117 [0.0091, 0.0146] | 45 |
| actor | Social / humanities | Persona 001 / Persona 089 | 0.0143 [0.0104, 0.0186] | 25 |
| actor | Life sciences | Persona 001 / Persona 046 | 0.0114 [0.0086, 0.0144] | 42 |
| actor | Physical / engineering | Persona 001 / Persona 046 | 0.0110 [0.0084, 0.0139] | 46 |
| actor | Math / CS | Persona 001 / Persona 046 | 0.0147 [0.0124, 0.0170] | 45 |
| actor | Social / humanities | Persona 001 / Persona 046 | 0.0186 [0.0141, 0.0238] | 25 |
| actor | Life sciences | Persona 089 / Persona 046 | 0.0117 [0.0089, 0.0144] | 42 |
| actor | Physical / engineering | Persona 089 / Persona 046 | 0.0178 [0.0141, 0.0214] | 46 |
| actor | Math / CS | Persona 089 / Persona 046 | 0.0179 [0.0155, 0.0203] | 45 |
| actor | Social / humanities | Persona 089 / Persona 046 | 0.0176 [0.0141, 0.0218] | 25 |

## Right-hand examples unchanged

Two examples manually selected by the user after inspecting the length-enriched UMAP gallery: bix-57-q1 and matToolUse/disambiguation/case_236. These are illustrative, not representative or independent aggregate evidence. All five settings are retained with their actual lengths, including one-round trajectories.

Local cosine UMAP jointly refitted after replacing 004 with 089, across all five settings and observed trial-1 messages, separately per question and role. n_neighbors=min(15,N−1), min_dist=0.1, 500 epochs, spectral init, random_state=42, transform_seed=42, n_jobs=1. Case IDs remain user-selected from the earlier 004-panel gallery. Local coordinates and path lengths are not effect sizes.

Cases: `bix-57-q1` and `matToolUse/disambiguation/case_236`, all five settings at trial 1. UMAP is jointly refitted for off/155/001/089/046 after replacing 004; case IDs and projection parameters remain unchanged. No point indices or arrows; diamonds identify final nodes. Curved connections are visual guides, not observed intermediate states. These examples are not independent statistical evidence.

## Reproducibility

`code/semantic/final_response.py` selects the final messages and writes the new statistics under `data/semantic_final/`; `test_final_response.py` checks direct-distance equivalence for all swaps of a small dataset, duplicate-aware bootstrap arithmetic and Holm correction. The notebook can recompute statistics from cached embeddings. No API calls; saved persona 089 messages were newly embedded locally with the same frozen encoder. Earlier round-matched statistics remain under `data/semantic/` and the preceding figure is archived under `figures/semantic/previous_raw_heatmap/`.


## Shared-question sensitivity

The 089 replacement is exploratory and changes complete-case coverage. Restricting the current panel to the 147 questions shared with the previous 004 panel retains nine significant comparisons per role; off versus 089 remains nonsignificant. Sensitivity estimates and p values (original snapshot path: `data/semantic_final/shared_questions_sensitivity/heatmap_cells.csv`; not bundled in this revision). The previous panel is archived in `figures/semantic/previous_persona_004/`. Holm correction applies to the current 20 tests, not all panels explored.
