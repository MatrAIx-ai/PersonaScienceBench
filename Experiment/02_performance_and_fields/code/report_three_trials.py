#!/usr/bin/env python3
"""Reproducible descriptive Astra three-trial tables and annotated figures; no API calls."""
from pathlib import Path
import csv, hashlib, importlib.util, json
from collections import Counter
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/02_performance_and_fields'
OUT=BASE/'data/three_trials'; FIG=BASE/'figures/three_trials'
ARMS=['persona_off','candidate_148','candidate_155','candidate_089','candidate_001','candidate_127']
SOURCES=['asibench','bixbench','discoverybench','expbench','sciconvbench']
FAMILIES=['life','physical_engineering','math_cs','social_humanities']
NAMES=dict(zip(SOURCES,['ASI-Bench*','BixBench','DiscoveryBench','EXP-Bench','SciConvBench']))
NAMES.update(dict(zip(FAMILIES,['Life sciences','Physical sciences & engineering','Math & computer science','Social sciences & humanities'])))
LABELS=['Off','148','155','089','001','127']
COLORS=['#65758B','#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']
B=20000;SEED=20260930
spec=importlib.util.spec_from_file_location('scoring',ROOT/'scripts/report_first_pass_ci.py')
scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)

def main():
 OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
 selection=list(csv.DictReader((ROOT/'Experiment/shared/task_selection.csv').open()))
 lookup={(r['source'],r['task_id']):r for r in selection}
 jobs=json.loads((ROOT/'Experiment/07_error_repairs/status.json').read_text())['jobs'][:6]
 episodes=[]; provenance=[]
 for index,j in enumerate(jobs):
  trial=index%3+1;r=Path(j['run_dir'])
  for view,filename in [('original','original_results_snapshot.json'),('after_repair','results.json')]:
   p=r/filename;raw=p.read_bytes();rows=json.loads(raw)
   provenance.append({'view':view,'trial':trial,'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
   assert len(rows)==600
   for row in rows:
    assert row['arm'] in ARMS
    meta=lookup[(row['source'],row['task_id'])]
    value=scoring.score(row) if row['status']=='finished' else None
    assert value is None or np.isfinite(value) and 0<=value<=100
    n=scoring.native(row)
    status='missing_submission' if n.get('status')=='missing_submission' else 'scored' if value is not None else row['status']
    episodes.append({'view':view,'trial':trial,'source':row['source'],'task_id':row['task_id'],'family':meta['family'],'study_id':meta.get('study_id') or row.get('study_id') or row['task_id'],'arm':row['arm'],'score':value,'status':status,'attempt':row.get('attempt'),'evaluator_version':(n.get('evaluation') or {}).get('evaluator_version')})
 assert len({(e['view'],e['trial'],e['source'],e['task_id'],e['arm']) for e in episodes})==7200
 (OUT/'snapshot.json').write_text(json.dumps({'captured_at_utc':datetime.now(timezone.utc).isoformat(),'provenance':provenance,'episodes':episodes},indent=2)+'\n')
 with (OUT/'episodes.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(episodes[0]));w.writeheader();w.writerows(episodes)
 rng=np.random.default_rng(SEED)
 summaries={};coverage={}
 for view in ['original','after_repair']:
  summaries[view]={};coverage[view]={}
  for arm in ARMS:
   rows=[r for r in episodes if r['view']==view and r['arm']==arm]
   coverage[view][arm]=dict(Counter(r['status'] for r in rows))
   tasks=[]
   for meta in selection:
    rr=[r for r in rows if (r['source'],r['task_id'])==(meta['source'],meta['task_id']) and r['score'] is not None]
    if rr:tasks.append({**rr[0],'score':float(np.mean([r['score'] for r in rr])),'trials_available':len(rr)})
   summaries[view][arm]={}
   for field,groups in [('source',SOURCES),('family',FAMILIES)]:
    summaries[view][arm][field]={}
    for group in groups:
     sub=[t for t in tasks if t[field]==group];assert sub
     boot=np.zeros(B)
     cluster_counts={}
     # Resample studies within each source; preserve observed source weights.
     # All tasks in a sampled study move together; trial means are computed first.
     for source in SOURCES:
      ss=[t for t in sub if t['source']==source]
      if not ss:continue
      clusters=sorted({t['study_id'] for t in ss});cluster_counts[source]=len(clusters)
      sums=np.array([sum(t['score'] for t in ss if t['study_id']==c) for c in clusters])
      counts=np.array([sum(t['study_id']==c for t in ss) for c in clusters])
      weights=rng.multinomial(len(clusters),np.ones(len(clusters))/len(clusters),size=B)
      boot+=(weights@sums)/(weights@counts)*len(ss)/len(sub)
     summaries[view][arm][field][group]={'mean':float(np.mean([t['score'] for t in sub])),'ci95':np.quantile(boot,[.025,.975]).tolist(),'tasks':len(sub),'episodes':sum(t['trials_available'] for t in sub),'tasks_all_three_trials':sum(t['trials_available']==3 for t in sub),'source_counts':dict(Counter(t['source'] for t in sub)),'study_clusters_by_source':cluster_counts}
 method=('Task means average available scores across trials 1–3, then weight each task equally. Missing submissions count as zero; infrastructure and other unscored episodes are excluded. Pointwise 95% percentile CIs use 20,000 study-cluster bootstrap resamples, stratified by benchmark source (seed 20260930), with observed source weights fixed. Trials are not counted as independent tasks. Intervals describe study/task sampling uncertainty conditional on observed trial outcomes; they do not separately estimate trial-to-trial uncertainty or correct for multiple comparisons. Unequal surviving task coverage can bias comparisons.')
 (OUT/'summary.json').write_text(json.dumps({'method':method,'coverage':coverage,'summaries':summaries},indent=2)+'\n')
 for view in summaries:
  for field,groups in [('source',SOURCES),('family',FAMILIES)]:
   with (OUT/f'{view}_{field}.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['persona','group','mean','ci_low','ci_high','tasks','episodes','tasks_all_three_trials']);w.writeheader()
    for arm in ARMS:
     for group in groups:
      s=summaries[view][arm][field][group]
      w.writerow(dict(persona=arm,group=group,mean=s['mean'],ci_low=s['ci95'][0],ci_high=s['ci95'][1],**{k:s[k] for k in ['tasks','episodes','tasks_all_three_trials']}))
 def table(view,field,groups):
  lines=['| Persona | '+' | '.join(NAMES[g] for g in groups)+' |','|---|'+'---|'*len(groups)]
  for arm,label in zip(ARMS,LABELS):
   cells=[]
   for g in groups:
    s=summaries[view][arm][field][g];lo,hi=s['ci95']
    cells.append(f"{s['mean']:.2f} [{lo:.2f}, {hi:.2f}]; n={s['tasks']}, e={s['episodes']}")
   lines.append('| '+label+' | '+' | '.join(cells)+' |')
  return '\n'.join(lines)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
 for field,groups,title,filename in [('source',SOURCES,'Performance by benchmark','benchmark'),('family',FAMILIES,'Performance by scientific super-family','superfamily')]:
  fig,axes=plt.subplots(3 if field=='source' else 2,2,figsize=(18,15 if field=='source' else 11),squeeze=False)
  for ax,g in zip(axes.flat,groups):
   stats=[summaries['after_repair'][arm][field][g] for arm in ARMS]
   means=np.array([s['mean'] for s in stats]);low=np.array([s['ci95'][0] for s in stats]);high=np.array([s['ci95'][1] for s in stats]);x=np.arange(6)
   ax.bar(x,means,color=COLORS,width=.68,zorder=3)
   ax.errorbar(x,means,yerr=np.array([means-low,high-means]).clip(0),fmt='none',ecolor='#17212B',capsize=5,lw=1.5,zorder=4)
   for i,s in enumerate(stats):
    ax.text(i,max(high[i],means[i])+2,f"{means[i]:.1f}\n[{low[i]:.1f}, {high[i]:.1f}]",ha='center',va='bottom',fontsize=9)
   ax.set_xticks(x,[f'{label}\nn={s["tasks"]}, e={s["episodes"]}' for label,s in zip(LABELS,stats)],fontsize=9)
   ax.set_ylim(0,123);ax.set_yticks([0,20,40,60,80,100]);ax.set_title(NAMES[g],fontweight='bold',pad=12)
   ax.set_ylabel('Native score normalized to 0–100');ax.grid(axis='y',alpha=.18,zorder=0);ax.set_axisbelow(True)
  if field=='source':
   axes.flat[-1].axis('off');axes.flat[-1].text(.03,.92,'HOW TO READ\n\nBar: mean of task-level averages across three trials.\nWhisker and bracket: pointwise 95% confidence interval.\nn: distinct evaluable tasks; e: evaluable trial episodes.\nOff: no persona. Missing submissions score zero.\n\nCIs resample studies within each benchmark (20,000 draws).\nRemaining technical errors are excluded.\nScores measure different outcomes across benchmarks.\n\n* ASI evaluator versions differ across historical runs.\nThese results are descriptive, not a clean persona ranking.',transform=axes.flat[-1].transAxes,va='top',fontsize=12,linespacing=1.5)
  fig.suptitle('Astra low · three trials · after one repair pass\n'+title,fontsize=21,fontweight='bold',y=.985)
  footer='Bars: task means across available trials. Labels: mean [95% CI]; n = tasks, e = trial episodes. Study-cluster bootstrap; 20,000 resamples.\nTechnical errors excluded; missing submissions = 0. Unequal coverage and historical ASI evaluator changes limit comparisons.'
  if field=='family':footer+='\nSuper-family scores are task-weighted composites of different native metrics; observed source composition is preserved.'
  fig.text(.5,.015,footer,ha='center',va='bottom',fontsize=10,linespacing=1.5)
  fig.tight_layout(rect=[0,.085,1,.935],h_pad=3,w_pad=3)
  for ext in ['png','pdf','svg']:fig.savefig(FIG/f'{filename}.{ext}',dpi=180,facecolor='white')
  plt.close(fig)
 lines=['# Astra three-trial persona results','', 'Six settings: Off, 148, 155, 089, 001, and 127. All use GPT-6 Astra low for actor, researcher simulator, and judge. Each setting planned 200 tasks × 3 trials = 600 episodes. Personas 046/003/004 have only one trial and are excluded; Sol is a separate model comparison.','', '## Aggregation and confidence intervals','',method,'','Main figures and tables use the latest outcome after the single repair pass, including reused original successes. A repair is a conditional replacement attempt, not a fourth trial or an independent replicate. Original outcomes remain in the sensitivity tables below. Results are provisional: repair selection and technical missingness can bias means. ASI evaluator versions/configuration differ between historical runs and repairs; ASI bars and family composites are descriptive, not clean estimates of persona effects. CI overlap is not a significance test.','', 'Native metrics: ASI score/max × 100; Bix correctness × 100; Discovery final score × 100; EXP final gated coverage (initial fallback); SciConv final resolution with intent preserved × 100. Super-family averages combine these distinct metrics and are not a calibrated common measure.','', 'Each cell: **mean [95% CI]; n=distinct evaluable tasks, e=evaluable trial episodes**. Each task averages its one to three available trial scores before aggregation. Study clusters use source-qualified study IDs; singleton studies remain singleton clusters. Intervals with few independent studies can be unstable.','', '## Table 1 — By benchmark','',table('after_repair','source',SOURCES),'','![Benchmark bars with labeled confidence intervals](figures/three_trials/benchmark.png)','', '**Figure 1.** Performance by benchmark across three Astra trials after one conditional repair pass. Bar labels give mean and pointwise 95% study-cluster bootstrap CI. Error bars show the same CI; task and episode counts appear under each condition. Different surviving task subsets and historical ASI judge configurations prevent a clean ranking.','', '## Table 2 — By super-family','',table('after_repair','family',FAMILIES),'','![Super-family bars with labeled confidence intervals](figures/three_trials/superfamily.png)','', '**Figure 2.** Task-weighted normalized native performance by scientific super-family. Scores first average available trials per task, then average tasks. Bootstrap resampling preserves observed source weights; cross-source metrics remain distinct. Labels and whiskers show mean and pointwise 95% CI. ASI evaluator drift and unequal task coverage also affect these composites.','', '## Coverage after repair','', '| Persona | Scored | Missing submission (zero) | Infrastructure errors | Tasks with all 3 evaluable trials |','|---|---:|---:|---:|---:|']
 for arm,label in zip(ARMS,LABELS):
  c=coverage['after_repair'][arm];n=sum(summaries['after_repair'][arm]['source'][s]['tasks_all_three_trials'] for s in SOURCES)
  lines.append(f"| {label} | {c.get('scored',0)} | {c.get('missing_submission',0)} | {c.get('infrastructure_error',0)} | {n}/200 |")
 lines+=['','## Original outcomes: sensitivity tables','', 'These preserve the original outcomes before this repair pass and use the identical aggregation and bootstrap method. They are not pooled with repair attempts. Original trial resumption history remains part of the existing run provenance.','',table('original','source',SOURCES),'',table('original','family',FAMILIES),'','## Files and reproduction','', '[Summary and all denominators](data/three_trials/summary.json) · [Episode CSV](data/three_trials/episodes.csv) · [Hashed input snapshot](data/three_trials/snapshot.json)','', '[Benchmark PDF](figures/three_trials/benchmark.pdf) · [Benchmark SVG](figures/three_trials/benchmark.svg) · [Super-family PDF](figures/three_trials/superfamily.pdf) · [Super-family SVG](figures/three_trials/superfamily.svg)','', '```bash','.venv/bin/python Experiment/02_performance_and_fields/code/report_three_trials.py','```','']
 (BASE/'three_trial_persona_results.md').write_text('\n'.join(lines))
 print(json.dumps({'report':str(BASE/'three_trial_persona_results.md'),'coverage':coverage['after_repair']},indent=2))
if __name__=='__main__':main()
