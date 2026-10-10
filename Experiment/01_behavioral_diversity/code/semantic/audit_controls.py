"""Audit recorded question text and generation settings, without exporting prompts."""
import json
from collections import defaultdict
from pathlib import Path
from analyze import ROOT,OUT,sha,write_json,config

def main():
    p=json.loads((OUT/'provenance.json').read_text());by=defaultdict(list);missing=[];selected=config()
    for log in p['event_logs']:
        if log['arm'] not in selected['arms'] or log['trial'] not in selected['rollouts'][log['arm']]:continue
        event=ROOT/log['path'];controller=event.parent
        configs=[controller.parent.parent/'config.json',controller.parent/'config.json',controller.parent/'manifest.json']
        cp=next((x for x in configs if x.exists()),None)
        public=controller/'public_input.json'
        if cp is None or not public.exists():
            missing.append({k:log[k] for k in ['source','task_id','arm','trial']}|{'config_available':cp is not None,'public_input_available':public.exists()});continue
        c=json.loads(cp.read_text());c=c.get('config',c);inp=json.loads(public.read_text())
        settings={'models':{r:{k:v for k,v in c['models'][r].items() if k in ['model','provider','reasoning_effort','max_tokens','max_output_tokens','temperature','top_p']} for r in ['actor','researcher']},'actor_steps':c.get('actor_steps',c.get('limits',{}).get('actor_steps')),'collaboration':c.get('collaboration')}
        by[(log['source'],log['task_id'])].append({'arm':log['arm'],'trial':log['trial'],'question_sha256':sha(json.dumps(inp.get('question',inp),sort_keys=True).encode()),'settings_sha256':sha(json.dumps(settings,sort_keys=True).encode())})
    conflicts=[]
    for key,rows in by.items():
        if len({r['question_sha256'] for r in rows})>1 or len({r['settings_sha256'] for r in rows})>1:conflicts.append({'source':key[0],'task_id':key[1],'records':rows})
    result={'questions_checked':len(by),'episodes_checked':sum(map(len,by.values())),'missing_record_count':len(missing),'missing_records':missing,'conflicts':conflicts,'scope':'Recorded question text plus actor/researcher model, provider, reasoning, output cap, explicit decoding settings, actor_steps and collaboration config. No claim to reconstruct environment files or unrecorded provider defaults.'}
    write_json(OUT/'control_audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['missing_records','conflicts']}));print('conflicts',len(conflicts))

if __name__=='__main__':main()
