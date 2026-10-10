#!/usr/bin/env python3
"""Offline, role-separated SciConv token usage from original successful Astra traces."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter,defaultdict
import csv,json,hashlib,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Experiment/01_behavioral_diversity';DATA=BASE/'data/sciconv_tokens'
ARMS=['persona_off','candidate_148','candidate_155','candidate_089','candidate_001','candidate_127'];LABELS=['Off','148','155','089','001','127'];ROLES=['actor','researcher','judge'];B=20000;SEED=20261003

def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def export_csv(p,rows):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def extract(item):
 trial,row=item;n=next((x for x in row.get('native_results',[]) if x.get('benchmark')=='sciconvbench'),{});mode=row['task_id'].split('/')[1]
 meta={'trial':trial,'case':row['task_id'],'mode':mode,'study_id':row.get('study_id') or row['task_id'],'arm':row['arm'],'status':row['status'],'attempt':row.get('attempt')}
 if row['status']!='finished' or n.get('status')!='scored':return meta,[],None
 path=Path(n['case_directory'])/'controller/api_calls.private.jsonl'
 if not path.exists():return {**meta,'status':'trace_missing'},[],None
 raw=path.read_bytes();counts=Counter();calls=[]
 for index,line in enumerate(raw.splitlines()):
  c=json.loads(line);role=c['role'];counts[role]+=1;u=c.get('usage') or {};total=u.get('completion_tokens');reason=(u.get('completion_tokens_details') or {}).get('reasoning_tokens')
  if total is not None:assert isinstance(total,int) and total>=0
  if reason is not None:assert isinstance(reason,int) and 0<=reason<=total
  calls.append({**meta,'call_index':index+1,'role':role,'role_turn':counts[role],'input_tokens':u.get('prompt_tokens'),'output_tokens':total,'reasoning_tokens':reason,'nonreasoning_output_tokens':total-reason if total is not None and reason is not None else None,'cached_input_tokens':(u.get('prompt_tokens_details') or {}).get('cached_tokens')})
 # SciConv has one actor call per question plus final-specification call, and one researcher reply per question.
 for c in calls:c['phase']='judge' if c['role']=='judge' else 'reply' if c['role']=='researcher' else 'final_specification' if c['role_turn']==counts['actor'] else 'question'
 assert counts['actor']==counts['researcher']+1,(row['task_id'],counts)
 return {**meta,'status':'scored','actor_calls':counts['actor'],'researcher_calls':counts['researcher'],'judge_calls':counts['judge']},calls,{'trial':trial,'case':row['task_id'],'arm':row['arm'],'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}

def collect():
 jobs=json.loads((ROOT/'Experiment/07_error_repairs/status.json').read_text())['jobs'][:6];work=[];sources=[]
 for i,j in enumerate(jobs):
  p=Path(j['run_dir'])/'original_results_snapshot.json';raw=p.read_bytes();sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
  work.extend((i%3+1,r) for r in json.loads(raw) if r['source']=='sciconvbench')
 with ThreadPoolExecutor(max_workers=12) as pool:result=list(pool.map(extract,work))
 snap={'source_results':sources,'episodes':[r[0] for r in result],'calls':[c for r in result for c in r[1]],'trace_hashes':[r[2] for r in result if r[2]]}
 assert len(snap['episodes'])==720
 write(DATA/'snapshot.json',snap);export_csv(DATA/'calls.csv',snap['calls']);return snap

def cluster_summary(rows,field,rng):
 # An episode contributes one value; trials average within case before aggregation.
 grouped=defaultdict(list)
 for r in rows:
  if r.get(field) is not None:grouped[(r['case'],r['mode'],r['study_id'])].append(r[field])
 cases=[dict(case=k[0],mode=k[1],study_id=k[2],value=float(np.mean(v))) for k,v in sorted(grouped.items())]
 if not cases:return {'mean':None,'ci95':None,'cases':0,'episodes':0}
 boot=np.zeros(B)
 for mode in sorted({x['mode'] for x in cases}):
  sub=[x for x in cases if x['mode']==mode];clusters=sorted({x['study_id'] for x in sub})
  sums=np.array([sum(x['value'] for x in sub if x['study_id']==c) for c in clusters]);counts=np.array([sum(x['study_id']==c for x in sub) for c in clusters]);w=rng.multinomial(len(clusters),np.ones(len(clusters))/len(clusters),size=B)
  boot+=(w@sums)/(w@counts)*len(sub)/len(cases)
 return {'mean':float(np.mean([x['value'] for x in cases])),'ci95':np.quantile(boot,[.025,.975]).tolist(),'cases':len(cases),'episodes':sum(len(v) for v in grouped.values())}

def analyze(snap):
 rng=np.random.default_rng(SEED);groups=defaultdict(list)
 for c in snap['calls']:groups[(c['trial'],c['case'],c['arm'],c['role'])].append(c)
 episode_meta={(e['trial'],e['case'],e['arm']):e for e in snap['episodes'] if e['status']=='scored'}
 for key in episode_meta:
  for role in ROLES:groups.setdefault((*key,role),[])
 episodes=[]
 for key,calls in groups.items():
  first=calls[0] if calls else {**episode_meta[key[:3]],'role':key[3]};r={k:first[k] for k in ['trial','case','mode','study_id','arm','role']};r['calls']=len(calls)
  for metric in ['output_tokens','reasoning_tokens','nonreasoning_output_tokens']:
   vals=[c[metric] for c in calls];complete=all(x is not None for x in vals)
   r[metric+'_total']=sum(vals) if complete else None;r[metric+'_per_call']=float(np.mean(vals)) if complete and vals else None
  questions=[c['output_tokens'] for c in calls if c['phase']=='question'];r['question_output_mean']=float(np.mean(questions)) if questions and all(v is not None for v in questions) else None
  final=[c['output_tokens'] for c in calls if c['phase']=='final_specification'];r['final_output']=final[0] if final else None
  episodes.append(r)
 export_csv(DATA/'episode_role_tokens.csv',episodes)
 summary={'seed':SEED,'resamples':B,'coverage':{a:dict(Counter(e['status'] for e in snap['episodes'] if e['arm']==a)) for a in ARMS},'missing_reasoning_usage_calls':sum(c['reasoning_tokens'] is None for c in snap['calls']),'roles':{}}
 metrics=['output_tokens_per_call','output_tokens_total','reasoning_tokens_per_call','nonreasoning_output_tokens_per_call','question_output_mean','final_output']
 for role in ROLES:
  summary['roles'][role]={a:{m:cluster_summary([r for r in episodes if r['role']==role and r['arm']==a],m,rng) for m in metrics} for a in ARMS}
 # Per-turn means conditional on reaching that role's call number, with changing denominators explicit.
 turns=[]
 for role in ['actor','researcher']:
  for arm in ARMS:
   for turn in sorted({c['role_turn'] for c in snap['calls'] if c['role']==role}):
    rr=[c for c in snap['calls'] if c['role']==role and c['arm']==arm and c['role_turn']==turn]
    s=cluster_summary(rr,'output_tokens',rng)
    turns.append({'role':role,'persona':arm,'turn':turn,'mean':s['mean'],'ci_low':s['ci95'][0] if s['ci95'] else None,'ci_high':s['ci95'][1] if s['ci95'] else None,'cases':s['cases'],'episodes':s['episodes'],'final_specification_calls':sum(c['phase']=='final_specification' for c in rr)})
 export_csv(DATA/'per_turn_tokens.csv',turns);write(DATA/'summary.json',summary);return summary

def table(s):
 lines=['| Persona | Actor output/call [95% CI] | Simulator output/reply [95% CI] | Actor output/episode | Simulator output/episode |','|---|---|---|---:|---:|']
 for a,label in zip(ARMS,LABELS):
  vals=[]
  for role in ['actor','researcher']:
   v=s['roles'][role][a]['output_tokens_per_call'];vals.append(f"{v['mean']:.1f} [{v['ci95'][0]:.1f}, {v['ci95'][1]:.1f}]")
  totals=[f"{s['roles'][role][a]['output_tokens_total']['mean']:.1f}" for role in ['actor','researcher']]
  lines.append('| '+label+' | '+' | '.join(vals+totals)+' |')
 return '\n'.join(lines)

def report(s):
 text=['# Experiment 01 — SciConv interaction output tokens','', '[Executed notebook](sciconv_tokens.ipynb)','',
 'Original Astra-low trials only: 40 SciConv cases (20 disambiguation, 20 inconsistency), six conditions, three trials = 720 planned episodes. Repairs, Sol and the credit-exhausted new baseline are not pooled. One historical infrastructure failure is excluded; 719 scored episodes contribute. Raw private prompts and replies are not copied into derived data.','',
 'API completion_tokens is total generated output, including reasoning when reported. Non-reasoning output = completion_tokens − reasoning_tokens only when the reasoning field exists; missing reasoning counts remain missing. Counts are tokens, not characters or whitespace words. Input usage includes prompts/history and is separately available in the call CSV. Failed requests have no recorded successful usage and are not assigned zero token cost.','',
 'For each role, average calls within each episode, then trials within each case, then cases equally. Episode totals use the same trial/case weighting. Actor calls include questions and the final specification; question-only and final-output statistics are stored separately. These weights do not equal a pooled mean over all calls.','',
 'Pointwise 95% CIs: 20,000 study-cluster bootstrap draws within SciConv mode, holding observed mode weights fixed; seed 20261003. Intervals condition on observed trials, do not separately estimate trial randomness, and are not multiplicity-corrected comparisons.','',table(s),'','![Output tokens by role](figures/sciconv_tokens/output_tokens.png)','',
 '## Turn alignment and limitations','',
 'Within each episode, role_turn counts API calls in trace order. Actor call 1 precedes the first simulator reply; actor call q is a question paired with simulator reply q until the final actor specification. Actor calls equal researcher calls plus one in all included traces. Actor trajectories by call number mix question and final-specification phases across episodes; the CSV explicitly counts final-specification calls. Later-turn averages are conditional on reaching that turn, with changing case/episode denominators; do not interpret them as within-episode growth.','',
 'Episodes with no simulator call contribute zero to simulator episode totals, but have no per-reply value and are excluded from that conditional mean; the figure reports its reduced denominators. The judge is kept separate in the numeric summaries. Tokenization improves on whitespace length comparisons for Mandarin profiles but does not by itself measure information quality or language-normalized verbosity. No causal claim about personality or disclosure follows from token counts.','',
 '[Per-call numeric data](data/sciconv_tokens/calls.csv) · [Per-turn means/CIs](data/sciconv_tokens/per_turn_tokens.csv) · [Episode-role totals](data/sciconv_tokens/episode_role_tokens.csv) · [Summary](data/sciconv_tokens/summary.json)','',
 'Reproduce: `.venv/bin/python Experiment/01_behavioral_diversity/code/analyze_sciconv_tokens.py`. Use `--refresh` only to extract from saved private traces again. No model calls.','']
 (BASE/'SCICONV_TOKENS.md').write_text('\n'.join(text))

def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');a=p.parse_args();DATA.mkdir(parents=True,exist_ok=True)
 snap=collect() if a.refresh or not (DATA/'snapshot.json').exists() else json.loads((DATA/'snapshot.json').read_text())
 s=analyze(snap);report(s);print(table(s));print('Calls',len(snap['calls']),'coverage',s['coverage'])
if __name__=='__main__':main()
