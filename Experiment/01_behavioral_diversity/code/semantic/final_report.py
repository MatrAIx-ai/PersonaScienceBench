import csv,json
from analyze import BASE,NAMES
from final_response import DEST

def main():
 s=json.loads((DEST/'summary.json').read_text());c=s['config'];cells=list(csv.DictReader((DEST/'heatmap_cells.csv').open()));families=list(csv.DictReader((DEST/'family_cells.csv').open()))
 lines=['# Final-response semantic separation and illustrative trajectories','','[Executed notebook](semantic_trajectory_analysis.ipynb) · [Figure](figures/semantic/semantic.pdf) · [Candidate caption and figure handoff](SEMANTIC_FIGURE_CAPTION.md)','','## What is tested','',
 'Within each scientific super-family, compare final-response distances between personas with distances within each persona across different questions. This is a domain-level comparison of final-response embeddings, not within-persona rollout randomness or a matched-question distance statistic. Both roles share the same complete five-setting question set.','']
 for name,value in s['methods'].items():lines+=['**'+name.replace('_',' ').capitalize()+'**: '+str(value),'']
 lines+=['Frozen Qwen/Qwen3-Embedding-0.6B embeddings (revision '+c['model_revision']+'), L2 normalized. Current generated messages only, without prompt/persona metadata, summaries or transcript history. Cosine distances are calculated before UMAP.','',
 'For family f and personas i,j, let Q contain n complete questions. Define B as the mean d(x_iq,x_js) over ordered q≠s; W_i and W_j are the corresponding within-persona means over q≠s. E_f=B−(W_i+W_j)/2. The overall statistic averages the four E_f values equally. Only the lower triangle is displayed; the diagonal is light gray and the redundant upper triangle is hidden; negative estimates are retained. The statistic is sensitive to shifts in mean normalized embeddings and is not an omnibus detector of every distributional difference.','',
 'The permutation preserves each question’s two outputs and changes only which persona label is attached to each output. Thus no same-question distance enters the statistic, but the randomization respects the paired collection design. A star marks Holm-adjusted one-sided p<0.05 across all 20 tests. Bootstrap intervals are pointwise, not simultaneous; their zero-crossing need not agree with Holm decisions.','',
 '## Coverage','','| Role | Super-family | Questions | Weight |','|---|---|---:|---:|']
 for role,v in s['roles'].items():
  for f,n in v['family_counts'].items():lines.append(f'| {role} | {NAMES[f]} | {n} | 25% |')
 lines+=['','| Source | Questions (same for both roles) |','|---|---:|']
 for source,n in s['roles']['simulator']['source_counts'].items():lines.append(f'| {NAMES[source]} | {n} |')
 lines+=['','## Overall pairwise results','','| Role | Pair | Between | Within i | Within j | Excess [95% CI] | Permutation p | Holm p |','|---|---|---:|---:|---:|---|---:|---:|']
 for r in cells:
  lines.append(f"| {r['role']} | {c['labels'][r['persona_i']]} / {c['labels'][r['persona_j']]} | {float(r['between']):.4f} | {float(r['within_i']):.4f} | {float(r['within_j']):.4f} | {float(r['estimate']):.4f} [{float(r['ci_low']):.4f}, {float(r['ci_high']):.4f}] | {float(r['p_permutation']):.5f} | {float(r['p_holm']):.5f} |")
 lines+=['','## Family-specific descriptive estimates','','| Role | Super-family | Pair | Excess [95% CI] | Questions |','|---|---|---|---|---:|']
 for r in families:lines.append(f"| {r['role']} | {NAMES[r['family']]} | {c['labels'][r['persona_i']]} / {c['labels'][r['persona_j']]} | {float(r['estimate']):.4f} [{float(r['ci_low']):.4f}, {float(r['ci_high']):.4f}] | {r['questions']} |")
 lines+=['','## Right-hand examples unchanged','',c['case_rule'],'',c['projection'],'',
 'Cases: `bix-57-q1` and `matToolUse/disambiguation/case_236`, all five settings at trial 1. UMAP is jointly refitted for off/155/001/003/046 after replacing 089; case IDs and projection parameters remain unchanged. No point indices or arrows; hollow circles identify starts, larger solid circles identify ends, and smaller filled dots identify intermediate rounds. A single-node trajectory is shown as a filled dot inside a hollow circle. Curved connections are visual guides, not observed intermediate states. These examples are not independent statistical evidence.','',
 '## Reproducibility','',
 '`code/semantic/final_response.py` selects the final messages and writes the new statistics under `data/semantic_final/`; `test_final_response.py` checks direct-distance equivalence for all swaps of a small dataset, duplicate-aware bootstrap arithmetic and Holm correction. The notebook can recompute statistics from cached embeddings. No API calls; saved persona 003 messages were newly embedded locally with the same frozen encoder. Earlier round-matched statistics remain under `data/semantic/` and the preceding figure is archived under `figures/semantic/previous_raw_heatmap/`.','']
 if (DEST/'shared_questions_sensitivity/summary.json').exists():
  shared=json.loads((DEST/'shared_questions_sensitivity/summary.json').read_text())
  sr=list(csv.DictReader((DEST/'shared_questions_sensitivity/heatmap_cells.csv').open()))
  counts={role:sum(r['role']==role and r['significant_holm_005']=='True' for r in sr) for role in c['roles']}
  lines+=['','## Exploratory 003 replacement and sensitivity','',f"Persona 003 specifies Russian output and blunt, slangy, concrete, detailed communication. Language may contribute to separation. It has only 104 completed original trial-1 episodes; the common panel is smaller than for 089. Restricting the current panel to {shared['roles']['simulator']['questions']} questions shared with the previous 089 panel gives significant-pair counts {counts}. [Sensitivity estimates and p values](data/semantic_final/shared_questions_sensitivity/heatmap_cells.csv). Prior 089 outputs are archived under `figures/semantic/previous_persona_089/`. Holm corrects the current 20 tests, not all panels explored. These post-selection results are exploratory.",'']
 (BASE/'SEMANTIC_REPORT.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
