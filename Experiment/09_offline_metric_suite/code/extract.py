"""Offline, content-free extraction from frozen original results and saved traces."""
from pathlib import Path
import json,hashlib,csv,re,sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Experiment/09_offline_metric_suite';DATA=BASE/'data'
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
SOURCES=['asibench','bixbench','discoverybench','expbench','sciconvbench']
FAMILIES=['life','physical_engineering','math_cs','social_humanities']
LABELS=['Off','155','001','003','046']
def sha(b):return hashlib.sha256(b).hexdigest()
def key(r):return (r['source'],r['task_id'],r['arm'],int(r['trial']))
def write_json(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def write_csv(p,rows):
 if not rows:return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def pattern(events,source,termination=None):
 seq=[];handoffs=Counter();replies=0;actor=0
 for pos,e in enumerate(events):
  typ=e['type'];p=e.get('payload') or {}
  if source=='sciconvbench':
   if typ=='researcher_question':seq.append('actor:question');actor+=1
   elif typ=='researcher_reply':seq.append('simulator:reply');replies+=1
   elif typ=='final_specification':seq.append('actor:final_specification')
  else:
   if typ=='researcher_decision' and p.get('phase')!='initial_inspection' and p.get('interaction')!='initial_request':
    seq.append(':'.join(['simulator',str(p.get('phase','unknown')),str(p.get('action','unknown')),str(p.get('interaction','unknown'))]))
   elif typ=='agent_handoff':
    actor+=1
    nxt=next((x.get('payload') or {} for x in events[pos+1:] if x['type']=='researcher_decision'),{})
    phase=nxt.get('phase','unreviewed');handoffs[phase]+=1
    if handoffs[phase]>1 or phase=='unreviewed':seq.append('actor:additional_handoff:'+phase)
   elif typ=='collaboration_budget_exhausted':seq.append('limit:'+str(p.get('reason','unknown')))
 if source=='sciconvbench':seq.append('end:cap' if replies>=10 else 'end:complete')
 else:seq.append('end:'+str(termination or 'complete'))
 return seq,replies if source=='sciconvbench' else actor

def main():
 DATA.mkdir(exist_ok=True)
 paths=[ROOT/'Experiment/01_behavioral_diversity/data/behavior_all_personas/snapshot.json',ROOT/'Experiment/02_performance_and_fields/data/all_available/snapshot.json']
 raw=[p.read_bytes() for p in paths];beh,perf=map(json.loads,raw)
 provenance=[dict(path=str(p.relative_to(ROOT)),sha256=sha(b)) for p,b in zip(paths,raw)]
 scores=[r for r in perf['episodes'] if r['view']=='original' and r['arm'] in ARMS]
 bindex={key(r):r for r in beh['episodes'] if r['arm'] in ARMS};logs=[r for r in beh['event_logs'] if r['arm'] in ARMS]
 def one(log):
  meta=bindex[key(log)];base={k:meta.get(k) for k in ['source','task_id','arm','trial','study_id','family','coordinator_status','eligible','termination','native_status']}
  base['trace_path']=log['path'];base['sha256']=log['sha256']
  if not meta['eligible']:return base|dict(exclusion='incomplete_original_episode')
  p=ROOT/log['path'];raw=p.read_bytes()
  if sha(raw)!=log['sha256']:raise ValueError('Frozen event hash changed: '+log['path'])
  ev=[json.loads(line) for line in raw.splitlines() if line.strip()];seq,length=pattern(ev,meta['source'],meta.get('termination'))
  return base|dict(exclusion=None,sequence=seq,pattern_hash=sha(json.dumps(seq).encode()),interaction_length=length,extra_plan_reviews=meta.get('extra_plan_reviews'),extra_result_reviews=meta.get('extra_result_reviews'),revision_requests=meta.get('revision_requests'),repeat_question_rate=meta.get('repeat_question_rate'))
 with ThreadPoolExecutor(max_workers=12) as pool:traces=list(pool.map(one,logs))
 recorded={key(r) for r in traces}
 for k,m in bindex.items():
  if k not in recorded:traces.append({x:m.get(x) for x in ['source','task_id','arm','trial','study_id','family']}|dict(exclusion='no_saved_event_log'))
 recover=[]
 for ref in beh['source_results']:
  p=ROOT/ref['path'];raw=p.read_bytes()
  if sha(raw)!=ref['sha256']:raise ValueError('Frozen result hash changed: '+str(p))
  provenance.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(raw)))
  for row in json.loads(raw):
   if row['arm'] not in ARMS or row['source']!='sciconvbench':continue
   n=next((x for x in row.get('native_results',[]) if x.get('benchmark')=='sciconvbench'),{})
   ev=n.get('evaluation') or {};m=ev.get('metrics') or {}
   r={k:row.get(k) for k in ['source','task_id','arm','study_id','family']};r.update(trial=ref['trial'],mode=row['task_id'].split('/')[1],evaluator_version=ev.get('evaluator_version'),status=row['status'],FRR=m.get('FRR'),intent_capture=m.get('intent_capture'),clarification_recall=m.get('clarification_recall'),clarification_precision=m.get('clarification_precision'))
   r['recovery']=None;r['exclusion']='inconsistency_mode' if r['mode']!='disambiguation' else 'not_scored'
   if r['mode']=='disambiguation' and row['status']=='finished' and n.get('status')=='scored':
    p=Path(n['case_directory'])/'llm_judge_disambiguation_score.json'
    raw=p.read_bytes();jud=json.loads(raw);match=re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*',str(jud.get('score','')))
    if not match:raise ValueError('Malformed recovery score '+str(p))
    num,den=map(int,match.groups());assert 0<=num<=den and den>0
    assert den==ev['details']['native_case']['n_items']
    r.update(recovery=100*num/den,facts_recovered=num,facts_total=den,exclusion=None,judge_path=str(p.resolve().relative_to(ROOT.resolve())),judge_sha256=sha(raw))
   recover.append(r)
 for seq in [scores,traces,recover]:assert len({key(r) for r in seq})==len(seq)
 snap=dict(arms=ARMS,labels=LABELS,policy='Original endpoints only; no new LLM inference; existing native judgments reused.',provenance=provenance,scores=scores,traces=traces,recovery=recover)
 write_json(DATA/'snapshot.json',snap)
 write_csv(DATA/'trace_patterns.csv',[{k:json.dumps(v) if k=='sequence' else v for k,v in r.items()} for r in traces]);write_csv(DATA/'recovery_episodes.csv',recover);write_csv(DATA/'score_episodes.csv',scores)
 print(json.dumps({'scores':len(scores),'traces':len(traces),'complete_traces':sum(r.get('exclusion') is None for r in traces),'recovery':sum(r['recovery'] is not None for r in recover)},indent=2),flush=True)
 return snap
if __name__=='__main__':main()
