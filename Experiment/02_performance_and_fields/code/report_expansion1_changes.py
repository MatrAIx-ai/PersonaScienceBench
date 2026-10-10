#!/usr/bin/env python3
"""Offline paired Trial-1 comparisons for 003/004/046; preserve both outcome views."""
from pathlib import Path
import importlib.util,json,hashlib
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Experiment/02_performance_and_fields'
spec=importlib.util.spec_from_file_location('scoring',ROOT/'scripts/report_first_pass_ci.py');scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)
ARMS=['candidate_003','candidate_004','candidate_046'];SOURCES=['asibench','bixbench','discoverybench','expbench','sciconvbench']
B=20000;SEED=20261002

def main():
 rng=np.random.default_rng(SEED);out={'resamples':B,'seed':SEED,'views':{},'provenance':[]}
 for view,file in [('original','original_results_snapshot.json'),('after_repair','results.json')]:
  paths=[ROOT/'runs/repair-1-openai-astra-top2-first-pass'/file,ROOT/'runs/repair-1-openai-astra-top10-trial-1-batch-1'/file]
  for p in paths:out['provenance'].append({'view':view,'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  baseline={(r['source'],r['task_id']):r for r in json.loads(paths[0].read_text()) if r['arm']=='persona_off'};rows=json.loads(paths[1].read_text());arms={}
  for arm in ARMS:
   rr=[r for r in rows if r['arm']==arm];data={}
   for source in SOURCES:
    pairs=[]
    for r in rr:
     if r['source']!=source:continue
     b=baseline[(source,r['task_id'])];a_score=scoring.score(r);b_score=scoring.score(b)
     if a_score is None or b_score is None:continue
     pairs.append({'task_id':r['task_id'],'study_id':r.get('study_id') or r['task_id'],'persona':a_score,'off':b_score,'delta':a_score-b_score})
    clusters=sorted({p['study_id'] for p in pairs})
    sums=np.array([sum(p['delta'] for p in pairs if p['study_id']==c) for c in clusters]);counts=np.array([sum(p['study_id']==c for p in pairs) for c in clusters])
    w=rng.multinomial(len(clusters),np.ones(len(clusters))/len(clusters),size=B);boots=(w@sums)/(w@counts)
    data[source]={'n':len(pairs),'clusters':len(clusters),'persona_mean':float(np.mean([p['persona'] for p in pairs])),'off_mean':float(np.mean([p['off'] for p in pairs])),'delta':float(np.mean([p['delta'] for p in pairs])),'ci95':np.quantile(boots,[.025,.975]).tolist(),'pairs':pairs}
   coverage=Counter('missing_submission' if scoring.native(r).get('status')=='missing_submission' else r['status'] for r in rr)
   arms[arm]={'coverage':dict(coverage),'benchmarks':data}
  out['views'][view]=arms
 dest=BASE/'data/expansion1_changes';dest.mkdir(parents=True,exist_ok=True);(dest/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
 lines=['# Trial 1: performance changes for personas 003, 004 and 046','',
 'One trial only. Each persona is compared with persona-off on exactly the same evaluable tasks within each benchmark. Missing submissions count as zero; infrastructure/unscored outcomes are excluded on both sides. Different personas can have different matched subsets. No global ranking across incompatible native metrics.','',
 'After-repair outcomes are primary here to match the latest available-results request; original-outcome sensitivity is retained below. Repairs are conditional additional attempts, not independent trials. Original successes remain preserved. ASI is descriptive only because historical evaluator configurations differ.','',
 'Intervals are pointwise 95% percentile study-cluster bootstrap CIs (20,000 draws, seed 20261002) of paired task differences. They do not capture repeat-run uncertainty, correct five-benchmark/three-persona multiplicity, or establish significance; sparse clusters can yield degenerate intervals. Values are points on native scores normalized to 0–100.','']
 for view in ['after_repair','original']:
  lines += [f'## {view.replace("_"," ").title()}','', '| Benchmark | 003 Δ [95% CI]; n | 004 Δ [95% CI]; n | 046 Δ [95% CI]; n |','|---|---|---|---|']
  for source in SOURCES:
   cells=[]
   for arm in ARMS:
    s=out['views'][view][arm]['benchmarks'][source];cells.append(f"{s['delta']:+.2f} [{s['ci95'][0]:.2f}, {s['ci95'][1]:.2f}]; n={s['n']}")
   lines.append('| '+source+' | '+' | '.join(cells)+' |')
  lines+=['']
 lines+=['## Coverage after repair','', '| Persona | Scored | Missing submission (zero) | Infrastructure errors |','|---|---:|---:|---:|']
 for arm in ARMS:
  c=out['views']['after_repair'][arm]['coverage'];lines.append(f"| {arm[-3:]} | {c.get('finished',0)} | {c.get('missing_submission',0)} | {c.get('infrastructure_error',0)} |")
 lines+=['','[Numeric results, exact task pairs and source hashes](data/expansion1_changes/summary.json). Reproduce with `code/report_expansion1_changes.py`. No API calls or figures generated.','']
 (BASE/'expansion1_performance_changes.md').write_text('\n'.join(lines));print('\n'.join(lines[8:20]))
if __name__=='__main__':main()
