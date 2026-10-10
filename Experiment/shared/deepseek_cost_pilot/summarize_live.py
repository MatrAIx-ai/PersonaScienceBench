"""Sum provider-reported usage.cost; never substitute price estimates for billing."""
import json
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[3];RUN=ROOT/'runs/deepseek-live-cost-pilot-20261003'
m=json.loads((RUN/'manifest.json').read_text());episodes=[]
for j in m['jobs']:
 original=Path(j['directory']);d=original/'attempt-2' if (original/'attempt-2').exists() else original;role_cost=defaultdict(float);role_tokens=defaultdict(lambda:dict(prompt=0,completion=0,calls=0));missing=0;errors=0;providers=Counter();n=0
 for p in (d/'output').rglob('api_calls*.jsonl'):
  for line in p.read_text().splitlines():
   if not line.strip():continue
   try:r=json.loads(line)
   except json.JSONDecodeError:continue
   if r.get('phase')=='request':continue
   response=r.get('response') or {};u=r.get('usage') or response.get('usage') or {};role=r.get('role','unknown')
   if not u:errors+=1;continue
   n+=1;cost=u.get('cost')
   if not isinstance(cost,(int,float)):missing+=1
   else:role_cost[role]+=cost
   for name,key in [('prompt','prompt_tokens'),('completion','completion_tokens')]:role_tokens[role][name]+=u.get(key,0) or 0
   role_tokens[role]['calls']+=1;providers[response.get('provider') or r.get('provider') or 'unknown']+=1
 exitcode=int((d/'exit_code.txt').read_text()) if (d/'exit_code.txt').exists() else None
 result=[]
 for p in d.glob('output/*/result.json'):
  obj=json.loads(p.read_text());result.append({k:obj.get(k) for k in ['status','metrics','source_task_id','task_id'] if k in obj})
 episodes.append({'selected_attempt':2 if d!=original else 1,**{k:j[k] for k in ['source','task_id','arm']}}|dict(exit_code=exitcode,native_results=result,reported_cost_usd=sum(role_cost.values()),role_cost_usd=dict(role_cost),role_tokens=dict(role_tokens),missing_cost_records=missing,error_records=errors,call_records=n,providers=dict(providers)))
finished=[r for r in episodes if r['exit_code'] is not None];byrole=defaultdict(float)
for r in episodes:
 for role,c in r['role_cost_usd'].items():byrole[role]+=c
complete=len(finished)==25 and all(r['exit_code']==0 and r['native_results'] and all(v.get('status') not in ['error','infrastructure_error','runtime_error'] for v in r['native_results']) for r in finished) and not any(r['missing_cost_records'] for r in episodes)
report={'planned':25,'finished':len(finished),'exit_codes':dict(Counter(r['exit_code'] for r in finished)),'total_reported_cost_usd':sum(r['reported_cost_usd'] for r in episodes),'role_cost_usd':dict(byrole),'missing_cost_records':sum(r['missing_cost_records'] for r in episodes),'ready_for_complete_projection':complete,'projected_1000_episode_usd':40*sum(r['reported_cost_usd'] for r in episodes) if complete else None,'caveat':'One question per benchmark across five settings; projection has substantial task/trajectory uncertainty. Actual usage.cost, excluding probe calls and infrastructure costs. No partial-run cost extrapolation.','episodes':episodes}
# Failed earlier attempts remain billable and are reported separately.
retry_overhead=0.0
for j in m['jobs']:
 d=Path(j['directory'])
 if not (d/'attempt-2').exists():continue
 for path in (d/'output').rglob('api_calls*.jsonl'):
  for line in path.read_text().splitlines():
   try:r=json.loads(line)
   except json.JSONDecodeError:continue
   if r.get('phase')=='request':continue
   cost=(r.get('usage') or (r.get('response') or {}).get('usage') or {}).get('cost')
   if isinstance(cost,(int,float)):retry_overhead+=cost
report['earlier_attempt_cost_usd']=retry_overhead
report['total_spend_including_earlier_attempts_usd']=report['total_reported_cost_usd']+retry_overhead
(RUN/'cost_summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='episodes'},indent=2))
