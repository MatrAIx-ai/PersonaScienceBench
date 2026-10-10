"""Offline budget proxy: recorded Astra trial-1 usage, priced at DeepSeek rates."""
import json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
rows=[r for r in json.loads((ROOT/'Experiment/02_performance_and_fields/data/model_scorecard/episodes.json').read_text()) if r['trial']==1 and r.get('api_log')]
pricing=json.loads((ROOT/'runs/deepseek-cost-pilot-20261003/models.json').read_text())
price=next(m['pricing'] for m in pricing if m['id']=='deepseek/deepseek-v4.1-flash:batch')
def one(r):
 p=ROOT/r['api_log'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['api_sha256']
 totals=defaultdict(lambda:dict(prompt_tokens=0,completion_tokens=0,cached_tokens=0,calls=0,missing_usage=0))
 for line in raw.splitlines():
  if not line.strip():continue
  d=json.loads(line)
  if d.get('phase')=='request':continue
  role=d.get('role','unknown');u=d.get('usage') or (d.get('response') or {}).get('usage') or {};t=totals[role]
  if not all(isinstance(u.get(k),(int,float)) for k in ['prompt_tokens','completion_tokens']):t['missing_usage']+=1;continue
  t['calls']+=1;t['prompt_tokens']+=u['prompt_tokens'];t['completion_tokens']+=u['completion_tokens'];t['cached_tokens']+=(u.get('prompt_tokens_details') or {}).get('cached_tokens',0) or 0
 return {k:r[k] for k in ['source','task_id','arm','trial']}|{'roles':dict(totals),'api_log':r['api_log']}
with ThreadPoolExecutor(max_workers=8) as pool:episodes=list(pool.map(one,rows))
groups=defaultdict(list)
for r in episodes:groups[r['source'],r['arm']].append(r)
roles=sorted({role for r in episodes for role in r['roles']})
projection={role:dict(prompt_tokens=0,completion_tokens=0,calls=0,missing_usage=0) for role in roles}
for group,rr in groups.items():
 for role in roles:
  for field in projection[role]:projection[role][field]+=40*sum(r['roles'].get(role,{}).get(field,0) for r in rr)/len(rr)
for role,t in projection.items():t['usd_no_cache']=t['prompt_tokens']*float(price['prompt'])+t['completion_tokens']*float(price['completion'])
result={'model':'deepseek/deepseek-v4.1-flash:batch','prices_per_token':price,'target_episodes':1000,'observed_complete_trial1_episodes':len(episodes),'coverage':{src+' / '+arm:len(rr) for (src,arm),rr in sorted(groups.items())},'projected_roles':projection,'projected_total_usd_no_cache':sum(t['usd_no_cache'] for t in projection.values()),'limitations':['Token and call counts are from Astra, not observed DeepSeek trajectories.','Project each source/persona cell to 40 tasks; failed/incomplete historical episodes excluded.','No cache discount assumed; tokenizer, reasoning, retries and trajectory length can differ.','Only API calls recorded in the episode API logs are included; judge completeness must be checked.']}
(BASE/'historical_projection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
