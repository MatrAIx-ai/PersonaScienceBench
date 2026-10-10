"""Extract original completed 089 trial-1 messages without replacing the existing archive."""
import json
from analyze import BASE,ROOT,CACHE,key,parse_events,sha,write_json
EXTRA=ROOT/'runs/semantic-analysis-089'
def extract():
 s=json.loads((BASE/'data/behavior_all_personas/snapshot.json').read_text());logs={key(r):r for r in s['event_logs']};rows=[];provenance=[]
 for episode in s['episodes']:
  if episode['arm']!='candidate_089' or episode['trial']!=1 or not episode['eligible']:continue
  log=logs[key(episode)];raw=(ROOT/log['path']).read_bytes();assert sha(raw)==log['sha256']
  rounds,_=parse_events([json.loads(line) for line in raw.splitlines() if line.strip()])
  meta={k:episode[k] for k in ['source','task_id','arm','trial','study_id']}
  meta.update(termination_status=episode['coordinator_status'],native_status=episode.get('native_status'),exclusion=None)
  for r in rounds:
   for role in ['simulator','actor']:
    if r[role]:rows.append(meta|{'role':role,'round':r['round'],'event_index':r[role+'_event_index'],'text':r[role],'text_sha256':sha(r[role].encode())})
  provenance.append(log)
 write_json(EXTRA/'messages.private.json',rows);write_json(EXTRA/'trace_provenance.json',provenance)
 print('Extracted',len(rows),'messages from',len(provenance),'complete 089 episodes',flush=True)
def merge():
 import numpy as np
 extra=json.loads((EXTRA/'messages.private.json').read_text());current=json.loads((CACHE/'messages.private.json').read_text())
 if any(r['arm']=='candidate_089' for r in current):raise ValueError('089 already present; do not append twice')
 old=np.load(CACHE/'embeddings.npz',allow_pickle=False);new=np.load(EXTRA/'embeddings.npz',allow_pickle=False)
 assert list(old['hashes'])==[r['text_sha256'] for r in current];assert list(new['hashes'])==[r['text_sha256'] for r in extra]
 np.savez_compressed(CACHE/'embeddings.npz',embeddings=np.concatenate([old['embeddings'],new['embeddings']]),hashes=np.concatenate([old['hashes'],new['hashes']]))
 write_json(CACHE/'messages.private.json',current+extra)
 write_json(BASE/'data/semantic/persona_089_embedding_provenance.json',{'added_persona':'candidate_089','trial':1,'messages':len(extra),'complete_episodes':len(json.loads((EXTRA/'trace_provenance.json').read_text())),'embedding':json.loads((EXTRA/'embedding_provenance.json').read_text()),'event_logs':json.loads((EXTRA/'trace_provenance.json').read_text())})
 print('Merged 089 messages and embeddings',flush=True)
if __name__=='__main__':extract()
