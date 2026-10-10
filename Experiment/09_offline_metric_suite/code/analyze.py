"""Four frozen-data metrics. Study-cluster uncertainty, no model inference."""
import json,itertools,hashlib,sys
from collections import defaultdict,Counter
from functools import lru_cache
import numpy as np
from extract import ROOT,BASE,DATA,ARMS,SOURCES,FAMILIES,LABELS,key,write_json,write_csv
sys.path.insert(0,str(ROOT/'Experiment/02_performance_and_fields/code'))
from consolidate_performance import compatible
B=20000;SEED=20261001

def task_values(rows,field):
 out=defaultdict(list);meta={}
 for r in rows:
  if r.get(field) is None:continue
  k=(r['source'],r['task_id']);out[k].append(float(r[field]));meta[k]=r
 return [dict(source=k[0],task_id=k[1],study_id=meta[k]['study_id'],family=meta[k]['family'],value=float(np.mean(v)),episodes=len(v)) for k,v in sorted(out.items())]

@lru_cache(None)
def weights(source,clusters):
 rng=np.random.default_rng(SEED+int(hashlib.sha256(json.dumps([source,clusters]).encode()).hexdigest()[:8],16));g=len(clusters)
 return rng.multinomial(g,np.full(g,1/g),size=B)

def summary(rows,equal_source=False):
 if not rows:return dict(mean=None,ci95=None,tasks=0,episodes=0,studies=0,source_counts={},studies_by_source={},singleton_sources=[])
 assert len({(r['source'],r['task_id']) for r in rows})==len(rows)
 sources=sorted({r['source'] for r in rows});boot=np.zeros(B);mean=0.;counts={};gs={}
 for source in sources:
  sub=[r for r in rows if r['source']==source];clusters=tuple(sorted({r['study_id'] for r in sub}));w=weights(source,clusters)
  sums=np.array([sum(r['value'] for r in sub if r['study_id']==g) for g in clusters]);n=np.array([sum(r['study_id']==g for r in sub) for g in clusters])
  factor=1/len(sources) if equal_source else len(sub)/len(rows)
  mean+=factor*np.mean([r['value'] for r in sub]);boot+=factor*(w@sums)/(w@n);counts[source]=len(sub);gs[source]=len(clusters)
 return dict(mean=float(mean),ci95=np.quantile(boot,[.025,.975]).tolist() if sum(gs.values())>=2 else None,tasks=len(rows),episodes=sum(r.get('episodes',1) for r in rows),studies=sum(gs.values()),source_counts=counts,studies_by_source=gs,singleton_sources=[s for s,g in gs.items() if g==1])

def group_summaries(rows,equal_all=False):
 yield 'all','all',summary(rows,equal_all)
 for field,groups in [('source',SOURCES),('family',FAMILIES)]:
  for group in groups:yield field,group,summary([r for r in rows if r[field]==group])

def repetition(a,b,same=False,length=False):
 pairs=list(itertools.combinations(a,2)) if same else list(itertools.product(a,b))
 if length:pairs=[(x,y) for x,y in pairs if x['interaction_length']==y['interaction_length']]
 return (100*np.mean([x['pattern_hash']==y['pattern_hash'] for x,y in pairs]),len(pairs)) if pairs else (None,0)

def repetition_analysis(snap):
 tasks=defaultdict(lambda:defaultdict(list))
 for r in snap['traces']:
  if r.get('exclusion') is None:tasks[(r['source'],r['task_id'])][r['arm']].append(r)
 panel={k:v for k,v in tasks.items() if all(len(v[a])>=(2 if a in ARMS[:3] else 1) for a in ARMS)}
 records=[];cells=[];deltas=[]
 for i,a in enumerate(ARMS):
  for j,b in enumerate(ARMS[:i+1]):
   for variant in ['primary','same_length']:
    rows=[];delta=[]
    for k,v in sorted(panel.items()):
     m,n=repetition(v[a],v[b],i==j,variant=='same_length');off,_=repetition(v[ARMS[0]],v[ARMS[0]],True,variant=='same_length')
     if m is None:continue
     meta=v[a][0];r=dict(source=k[0],task_id=k[1],study_id=meta['study_id'],family=meta['family'],value=float(m),episodes=n)
     rows.append(r);records.append(r|dict(persona_i=a,persona_j=b,variant=variant))
     if off is not None:delta.append(r|dict(value=m-off))
    for level,g,s in group_summaries(rows,True):cells.append(dict(persona_i=a,persona_j=b,variant=variant,level=level,group=g,**s))
    if i!=j:
     for level,g,s in group_summaries(delta,True):deltas.append(dict(persona_i=a,persona_j=b,variant=variant,level=level,group=g,**s))
 coverage=[dict(source=k[0],task_id=k[1],family=v[ARMS[0]][0]['family'],study_id=v[ARMS[0]][0]['study_id'],**{a:len(v[a]) for a in ARMS}) for k,v in sorted(panel.items())]
 return cells,deltas,records,coverage

def outcome_analysis(snap):
 scores=snap['scores'];cells=[];contrasts=[]
 for a in ARMS:
  tasks=task_values([r for r in scores if r['arm']==a],'score')
  for level,g,s in group_summaries(tasks):cells.append(dict(metric='native_score',arm=a,level=level,group=g,**s))
 recovery=[r|dict(full_recovery=100*int(r['facts_recovered']==r['facts_total'])) for r in snap['recovery'] if r['recovery'] is not None]
 for a in ARMS:
  tasks=task_values([r for r in recovery if r['arm']==a],'recovery')
  for level,g,s in group_summaries(tasks):cells.append(dict(metric='fact_recovery',arm=a,level=level,group=g,**s))
  tasks=task_values([r for r in recovery if r['arm']==a],'full_recovery')
  for level,g,s in group_summaries(tasks):cells.append(dict(metric='complete_fact_recovery',arm=a,level=level,group=g,**s))
 for name,rr,field in [('native_score',scores,'score'),('fact_recovery',recovery,'recovery'),('complete_fact_recovery',recovery,'full_recovery')]:
  index={key(r):r for r in rr}
  for i,a in enumerate(ARMS):
   for b in ARMS[:i]:
    pp=[]
    for r in rr:
     if r['arm']!=a or r.get(field) is None:continue
     ref=index.get((r['source'],r['task_id'],b,r['trial']))
     if ref is None or ref.get(field) is None or not compatible(r,ref):continue
     pp.append(r|dict(value=r[field]-ref[field]))
    for level,g,s in group_summaries(task_values(pp,'value')):contrasts.append(dict(metric=name,persona_i=a,persona_j=b,level=level,group=g,**s))
 # Common five-setting fact panel, no invented repeat values.
 bytask=defaultdict(set)
 for r in recovery:bytask[(r['source'],r['task_id'])].add(r['arm'])
 common={k for k,v in bytask.items() if set(ARMS)<=v}
 for a in ARMS:
  s=summary(task_values([r for r in recovery if r['arm']==a and (r['source'],r['task_id']) in common],'recovery'))
  cells.append(dict(metric='fact_recovery_common',arm=a,level='all',group='all',**s))
 return cells,contrasts

def failure_probabilities(off,personas,m):
 # Empirical allocation expectation, exhaustive subsets; no outcome-selected combination.
 off_failure=float(np.mean([1-np.prod(c) for c in itertools.combinations(off,m)]))
 means=[np.mean(v) for v in personas]
 mix_failure=float(np.mean([1-np.prod(c) for c in itertools.combinations(means,m)]))
 return off_failure,mix_failure

def failure_analysis(snap):
 tasks=defaultdict(lambda:defaultdict(list));intent={key(r):r.get('intent_capture') for r in snap['recovery']}
 for r in snap['scores']:
  if r['source'] in ['bixbench','sciconvbench'] and r['score'] is not None:tasks[(r['source'],r['task_id'])][r['arm']].append(r)
 perq=[];coverage=[];exclusions=[]
 for k,v in sorted(tasks.items()):
  allrows=[r for a in ARMS for r in v[a]]
  reason=None
  if {r['trial'] for r in v[ARMS[0]]}!={1,2,3}:reason='requires_three_evaluable_off_trials'
  elif any(not v[a] for a in ARMS[1:]):reason='requires_evaluable_result_for_each_persona'
  elif not all(compatible(a,b) for a,b in itertools.combinations(allrows,2)):reason='incompatible_evaluator_versions'
  if reason:exclusions.append(dict(source=k[0],task_id=k[1],reason=reason));continue
  assert all(r['score'] in [0,100] for r in allrows)
  meta=v[ARMS[0]][0];entry=dict(source=k[0],task_id=k[1],study_id=meta['study_id'],family=meta['family'],**{a:len(v[a]) for a in ARMS})
  allintent=k[0]!='sciconvbench' or all(intent.get(key(r))==1 for r in allrows)
  coverage.append(entry|dict(all_intent_preserved=allintent))
  off=[r['score']/100 for r in v[ARMS[0]]];personas=[[r['score']/100 for r in v[a]] for a in ARMS[1:]]
  for m in [1,2,3]:
   fo,fm=failure_probabilities(off,personas,m)
   values={'off':100*fo,'mixture':100*fm,'difference':100*(fm-fo),'mixture_only':100*fm*(1-fo),'off_only':100*fo*(1-fm)}
   for variant in ['primary']+(['intent_preserved'] if allintent else []):
    for strategy,value in values.items():perq.append(dict(source=k[0],task_id=k[1],study_id=meta['study_id'],family=meta['family'],budget=m,strategy=strategy,variant=variant,value=value,episodes=m))
 cells=[]
 for variant in ['primary','intent_preserved']:
  for m in [1,2,3]:
   for strategy in ['off','mixture','difference','mixture_only','off_only']:
    rr=[r for r in perq if r['budget']==m and r['strategy']==strategy and r['variant']==variant]
    for level,g,s in group_summaries(rr):cells.append(dict(variant=variant,budget=m,strategy=strategy,level=level,group=g,**s))
 return cells,perq,coverage,exclusions

def flatten(rows):
 return [{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows]

def persona_failure_analysis(snap,coverage):
 # Same fixed SciConv questions at every budget; sample without replacement
 # within each setting's observed trials. Single-trial arms stop at m=1.
 panel=[r for r in coverage if r['source']=='sciconvbench']
 idx=defaultdict(list)
 for r in snap['scores']:
  if r['source']=='sciconvbench' and r['score'] is not None:
   idx[(r['task_id'],r['arm'])].append(r['score']/100)
 cells=[];perq=[]
 for arm in ARMS:
  max_m=min(len(idx[(q['task_id'],arm)]) for q in panel)
  for m in range(1,min(3,max_m)+1):
   rows=[]
   for q in panel:
    values=idx[(q['task_id'],arm)]
    assert all(v in [0,1] for v in values)
    value=100*float(np.mean([1-np.prod(c) for c in itertools.combinations(values,m)]))
    row={k:q[k] for k in ['source','task_id','study_id','family']}
    rows.append(row|dict(value=value,episodes=m))
   perq.extend([r|dict(arm=arm,budget=m) for r in rows])
   cells.append(dict(arm=arm,budget=m,**summary(rows)))
 return cells,perq

def main():
 snap=json.loads((DATA/'snapshot.json').read_text());reps,repdelta,repq,repcover=repetition_analysis(snap)
 outcomes,contrasts=outcome_analysis(snap);failures,failq,failcover,failex=failure_analysis(snap)
 pooled=defaultdict(list);meta={}
 for r in repq:
  if r['variant']=='primary' and r['persona_i']!=r['persona_j']:
   k=(r['source'],r['task_id']);pooled[k].append(r['value']);meta[k]=r
 within={(r['source'],r['task_id']):r['value'] for r in repq if r['variant']=='primary' and r['persona_i']==r['persona_j']==ARMS[0]}
 rr=[meta[k]|dict(value=float(np.mean(v)),episodes=len(v)) for k,v in pooled.items()]
 repetition_overview={'between_all_pairs':summary(rr,True),'between_minus_within_off':summary([r|dict(value=r['value']-within[(r['source'],r['task_id'])]) for r in rr],True)}
 individual,individualq=persona_failure_analysis(snap,failcover)
 result=dict(arms=ARMS,labels=LABELS,repetition_overview=repetition_overview,repetition=reps,repetition_delta_vs_off=repdelta,outcomes=outcomes,contrasts=contrasts,failure_coverage=failures,persona_failure_coverage=individual,repetition_coverage=repcover,failure_panel=failcover,failure_exclusions=failex,bootstrap=dict(draws=B,seed=SEED,unit='source-study clusters, all observations for a study kept together; fixed source weights',interval='pointwise percentile; conditional on available trials',single_study='CI unavailable if total study count <2; singleton source strata otherwise fixed'),snapshot_sha256=hashlib.sha256((DATA/'snapshot.json').read_bytes()).hexdigest())
 write_json(DATA/'summary.json',result)
 for name,rows in [('repetition',reps),('repetition_delta_vs_off',repdelta),('repetition_questions',repq),('repetition_coverage',repcover),('outcomes',outcomes),('matched_contrasts',contrasts),('failure_coverage',failures),('failure_questions',failq),('failure_panel',failcover),('failure_exclusions',failex),('persona_failure_coverage',individual),('persona_failure_questions',individualq)]:write_csv(DATA/(name+'.csv'),flatten(rows))
 print(json.dumps({'repetition_common_questions':len(repcover),'repetition_sources':dict(Counter(x['source'] for x in repcover)),'failure_sources':dict(Counter(x['source'] for x in failcover))},indent=2),flush=True)
 return result
if __name__=='__main__':main()
