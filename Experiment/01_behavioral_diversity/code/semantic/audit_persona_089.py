"""Check actual recorded simulator requests, not just the campaign configuration."""
import csv,json
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import numpy as np
from analyze import BASE,ROOT,CACHE,write_json

def check(log):
 p=(ROOT/log['path']).parent;profile=json.loads((p/'persona.private.json').read_text());expected=profile['identity_prompt'];calls=0;found=0;missing=0
 api=p/'api_calls.private.jsonl'
 if not api.exists():api=p/'api_calls.jsonl'
 for line in api.open():
  a=json.loads(line)
  if a['role']!='researcher':continue
  request=a.get('request',a.get('payload',{}))
  if 'messages' not in request:continue
  calls+=1;matches=False
  for m in request['messages']:
   if m.get('role')!='system':continue
   if isinstance(m.get('content'),str) and expected in m['content']:
    matches=True;continue
   try:identity=json.loads(m.get('content','')).get('identity')
   except (ValueError,AttributeError,TypeError):continue
   if identity==expected:matches=True
  found+=matches;missing+=not matches
 return {'source':log['source'],'task_id':log['task_id'],'enabled':profile['profile']['enabled'],'persona_id':profile['profile']['id'],'identity_sha256':profile['sha256'],'researcher_calls':calls,'identity_in_actual_requests':found,'missing_identity_calls':missing}

def main():
 logs=json.loads((BASE/'data/semantic/persona_089_embedding_provenance.json').read_text())['event_logs']
 with ThreadPoolExecutor(max_workers=12) as pool:checks=list(pool.map(check,logs))
 rows=json.loads((CACHE/'messages.private.json').read_text());f=np.load(CACHE/'embeddings.npz',allow_pickle=False);z=f['embeddings'];assert list(f['hashes'])==[r['text_sha256'] for r in rows]
 index={(r['source'],r['task_id'],r['arm'],r['role'],r['trial'],r['round']):i for i,r in enumerate(rows)}
 finals=list(csv.DictReader((BASE/'data/semantic_final/final_message_index.csv').open()));result={}
 for role in ['simulator','actor']:
  selected={(r['source'],r['task_id'],r['arm']):r for r in finals if r['role']==role};questions=sorted({(r['source'],r['task_id']) for r in finals});dist=[];identical=0
  for source,task in questions:
   a=selected[source,task,'persona_off'];b=selected[source,task,'candidate_089'];identical+=a['text_sha256']==b['text_sha256']
   ids=[index[(source,task,r['arm'],role,int(r['trial']),int(r['round']))] for r in [a,b]];x=z[ids].astype(float);x/=np.linalg.norm(x,axis=1,keepdims=True);dist.append(float(1-x[0]@x[1]))
  result[role]={'questions':len(questions),'identical_final_text_pairs':identical,'different_final_text_pairs':len(questions)-identical,'mean_same_question_cosine_distance':float(np.mean(dist))}
 output={'complete_089_episodes_audited':len(checks),'enabled_correct_persona':sum(r['enabled'] and r['persona_id']=='candidate_089' for r in checks),'identity_hash_counts':dict(Counter(r['identity_sha256'] for r in checks)),'researcher_calls':sum(r['researcher_calls'] for r in checks),'calls_with_expected_identity':sum(r['identity_in_actual_requests'] for r in checks),'calls_without_expected_identity':sum(r['missing_identity_calls'] for r in checks),'final_response_checks':result,'episodes':checks}
 write_json(BASE/'data/semantic_final/persona_089_injection_audit.json',output)
 print(json.dumps({k:v for k,v in output.items() if k!='episodes'},indent=2))
if __name__=='__main__':main()
