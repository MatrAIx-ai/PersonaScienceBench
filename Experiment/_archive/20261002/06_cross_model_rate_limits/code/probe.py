#!/usr/bin/env python3
"""Bounded live cross-model capacity probe; never retries or changes benchmark jobs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import httpx
from personasciencebench.inference import load_env

ROOT = Path(__file__).resolve().parents[3]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    os.umask(0o077)
    a.output.mkdir(parents=True, exist_ok=True)
    load_env(ROOT / '.env')
    key = os.environ['OPENAI_API_KEY']
    records = []
    # Synthetic data: bounded input load, no scientific benchmark results.
    context = '\n'.join(f'Observation {i}: sample mass 12 temperature 23 pressure 101.' for i in range(1000))
    def call(model, phase, index, large=False):
        effort = 'none' if model == 'gpt-6-luna' else 'low'
        payload = {'model':model, 'reasoning':{'effort':effort}, 'store':False,
                   'max_output_tokens':128, 'input':f'Probe {phase} {index}. Reply only OK.\n' + (context if large else '')}
        start = time.time()
        rec = {'model':model, 'reasoning_effort':effort, 'phase':phase, 'index':index,
               'started_at':start, 'request_characters':len(payload['input'])}
        try:
            with httpx.Client(timeout=90) as client:
                response = client.post('https://api.openai.com/v1/responses',
                    headers={'Authorization':'Bearer '+key}, json=payload)
            rec.update(http_status=response.status_code,
                       rate_headers={k:v for k,v in response.headers.items() if k.startswith('x-ratelimit-') or k in ('retry-after','retry-after-ms')})
            try:
                data = response.json()
            except ValueError:
                data = {}
            rec.update(response_status=data.get('status'), usage=data.get('usage'),
                       resolved_model=data.get('model'), incomplete_details=data.get('incomplete_details'))
            if response.status_code != 200:
                err=data.get('error') or {}
                rec['error']={k:err.get(k) for k in ('type','code','param')}
                # Retain numeric limit evidence without account identifiers or full messages.
                import re
                rec['error_limit_details']=re.findall(r'(?:Limit|Used|Requested)\s+\d+',str(err.get('message','')))
        except httpx.HTTPError as exc:
            rec['transport_error']=type(exc).__name__
        rec.update(finished_at=time.time(),elapsed_seconds=round(time.time()-start,3))
        return rec
    def save(new):
        records.extend(new)
        with (a.output/'requests.jsonl').open('a') as f:
            for row in new:f.write(json.dumps(row)+'\n')
        print(json.dumps(new),flush=True)
    # First confirm exact requested model/effort access before sending the bounded load.
    save([call('gpt-6-luna','compatibility',0)])
    if records[-1].get('http_status')!=200:
        (a.output/'summary.json').write_text(json.dumps({'status':'compatibility_failed','requests':records},indent=2)+'\n')
        return 1
    for cycle in range(3):
        save([call('gpt-6-astra','astra_before',cycle)])
        with ThreadPoolExecutor(max_workers=3) as pool:
            save(list(pool.map(lambda i:call('gpt-6-luna',f'luna_cycle_{cycle}',i,True),range(3))))
        save([call('gpt-6-astra','astra_after',cycle)])
        if any(x.get('http_status') in (400,401,403,404,429) for x in records[-5:]):break
        if cycle<2:time.sleep(10)
    summary={'status':'complete','finished_at_utc':datetime.now(timezone.utc).isoformat(),
             'job_id':os.environ.get('SLURM_JOB_ID'), 'requests':len(records), 'models':{},
             'interpretation':'Different reported limits or simultaneous success are evidence of available model capacity, not proof of fully independent quotas; background Astra traffic confounds counter changes. No saturation sweep or account limit increase was performed.'}
    for model in ('gpt-6-luna','gpt-6-astra'):
        rows=[r for r in records if r['model']==model]
        summary['models'][model]={'requests':len(rows),'http_200':sum(r.get('http_status')==200 for r in rows),
            'completed':sum(r.get('response_status')=='completed' for r in rows),
            'http_429':sum(r.get('http_status')==429 for r in rows),
            'input_tokens':sum((r.get('usage') or {}).get('input_tokens',0) for r in rows),
            'output_tokens':sum((r.get('usage') or {}).get('output_tokens',0) for r in rows),
            'reported_token_limits':sorted({r['rate_headers']['x-ratelimit-limit-tokens'] for r in rows if 'x-ratelimit-limit-tokens' in r.get('rate_headers',{})})}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
