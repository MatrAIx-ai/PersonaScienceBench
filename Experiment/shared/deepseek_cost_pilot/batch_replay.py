"""Small fixed-history batch billing pilot; not fresh scientific trajectories."""
import argparse,hashlib,json,os,random,time
from pathlib import Path
from collections import defaultdict
import httpx
from personasciencebench.inference import load_env
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/deepseek-cost-pilot-20261003';MODEL='deepseek/deepseek-v4.1-flash'
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
def write(name,data):
 OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def prepare():
 rows=[r for r in json.loads((ROOT/'Experiment/02_performance_and_fields/data/model_scorecard/episodes.json').read_text()) if r['trial']==1 and r.get('api_log')]
 selected=[];rng=random.Random(20261003)
 for src in sorted({r['source'] for r in rows}):
  ids=[{r['task_id'] for r in rows if r['source']==src and r['arm']==a} for a in ARMS]
  common=sorted(set.intersection(*ids));tid=rng.choice(common)
  selected.extend(next(r for r in rows if r['source']==src and r['task_id']==tid and r['arm']==a) for a in ARMS)
 requests=[];metadata=[]
 for row in selected:
  raw=(ROOT/row['api_log']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['api_sha256'];pending={}
  for line in raw.splitlines():
   if not line.strip():continue
   d=json.loads(line)
   if d.get('phase')=='request':pending[d['call_id']]=d['payload'];continue
   payload=d.get('request') or pending.pop(d.get('call_id'),None)
   if payload is None:raise ValueError('Missing saved request')
   body={k:v for k,v in payload.items() if k not in ['model','provider','stream']};body['reasoning']={'effort':'low'}
   cid=f"replay-{len(requests):04d}";requests.append({'custom_id':cid,'body':body})
   metadata.append({k:row[k] for k in ['source','task_id','arm','trial','api_log','api_sha256']}|{'custom_id':cid,'role':d['role'],'historical_usage':d.get('usage') or (d.get('response') or {}).get('usage') or {}})
 payload={'endpoint':'/v1/chat/completions','model':MODEL,'requests':requests}
 write('replay_request.private.json',payload);write('replay_metadata.json',{'design':'One fixed-seed randomly selected common trial-1 question per benchmark, all five personas, all saved calls. Fixed history replay; outputs are NOT propagated to later calls; no scientific tool execution. Original per-role output caps; DeepSeek reasoning low.','episodes':25,'requests':metadata,'selected_questions':{r['source']:r['task_id'] for r in selected}})
 print(json.dumps({'episodes':25,'requests':len(requests),'payload_bytes':len(json.dumps(payload))}),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','submit','poll']);a=p.parse_args()
 if a.action=='prepare':prepare();return
 load_env(ROOT/'.env');headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']}
 with httpx.Client(timeout=90) as c:
  if a.action=='submit':
   if (OUT/'replay_submission.json').exists():raise RuntimeError('Already submitted; poll instead')
   r=c.post('https://openrouter.ai/api/v1/batches',headers=headers,json=json.loads((OUT/'replay_request.private.json').read_text()));data=r.json();write('replay_submission.json',{'http_status':r.status_code,'response':data,'submitted_at':time.time()});r.raise_for_status()
  else:
   bid=json.loads((OUT/'replay_submission.json').read_text())['response']['id'];r=c.get('https://openrouter.ai/api/v1/batches/'+bid,headers=headers);r.raise_for_status();data=r.json();write('replay_status.json',data)
  print(json.dumps({k:v for k,v in data.items() if k!='results'}),flush=True)
if __name__=='__main__':main()
