#!/usr/bin/env python3
"""One frozen SciConv trial, with a shared request budget across every worker and retry."""
import argparse,collections,hashlib,json,os,sys,threading,time
from pathlib import Path

class RequestBudget:
    def __init__(self,limit=850000,window=60.0):
        self.limit=limit;self.window=window;self.entries=collections.deque();self.lock=threading.Condition();self.cooldown_until=0
    @staticmethod
    def reservation(payload):
        # Deliberately conservative: UTF-8 input bytes, output cap, and framing allowance.
        return len(json.dumps(payload.get('input',[]),ensure_ascii=False).encode())+int(payload.get('max_output_tokens',0))+1024
    def acquire(self,amount):
        if amount>self.limit:raise ValueError('One request exceeds the configured local minute budget')
        with self.lock:
            while True:
                now=time.monotonic()
                while self.entries and self.entries[0][0]<=now-self.window:self.entries.popleft()
                used=sum(x[1] for x in self.entries)
                if now>=self.cooldown_until and used+amount<=self.limit:
                    self.entries.append((now,amount));return
                delay=max(.05,self.cooldown_until-now)
                if used+amount>self.limit:delay=max(delay,self.entries[0][0]+self.window-now)
                self.lock.wait(timeout=min(delay,60))
    def cooldown(self,seconds):
        with self.lock:self.cooldown_until=max(self.cooldown_until,time.monotonic()+seconds);self.lock.notify_all()

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-dir',type=Path,required=True);a=p.parse_args();run=a.run_dir.resolve()
    manifest=json.loads((run/'manifest.json').read_text());runtime=Path(manifest['runtime']);repo=Path(manifest['repository'])
    for rel,h in manifest['runtime_hashes'].items():
        if hashlib.sha256((runtime/rel).read_bytes()).hexdigest()!=h:raise RuntimeError('Frozen runtime hash changed: '+rel)
    sys.path.insert(0,str(runtime/'src'))
    from personasciencebench import openai_transport as transport
    from personasciencebench.inference import load_env
    from personasciencebench.sciconv_runner import run as native_run
    load_env(repo/'.env');os.environ['PSB_FATAL_API_FILE']=str(run/'fatal_api.json')
    original_httpx=transport.httpx;budget=RequestBudget(manifest['local_tpm_budget']);log_lock=threading.Lock()
    class GuardedHTTP:
        def __getattr__(self,name):return getattr(original_httpx,name)
        def post(self,url,**kwargs):
            if url!='https://api.openai.com/v1/responses':return original_httpx.post(url,**kwargs)
            reserved=budget.reservation(kwargs.get('json') or {});budget.acquire(reserved)
            response=original_httpx.post(url,**kwargs)
            if response.status_code==429:
                try:delay=float(response.headers.get('retry-after',60))
                except ValueError:delay=60
                budget.cooldown(max(60,delay))
            with log_lock:
                with (run/'request_budget.jsonl').open('a') as f:
                    f.write(json.dumps({'time':time.time(),'reserved':reserved,'http_status':response.status_code})+'\n')
            return response
    transport.httpx=GuardedHTTP()
    config=json.loads((run/'config.json').read_text())
    print('Starting actual trial:',manifest['cases'],'cases,',manifest['workers'],'workers, local budget',manifest['local_tpm_budget'],flush=True)
    native_run(run/'prepared',run/'output',config,manifest['workers'])
    rows=json.loads((run/'output/results.json').read_text())
    summary={'job_id':os.environ.get('SLURM_JOB_ID'),'requested':manifest['cases'],'finished':len(rows),'statuses':dict(collections.Counter(r['status'] for r in rows)),'protocol':manifest['protocol'],'output':str(run/'output')}
    (run/'trial_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
    return int(any(r['status']!='scored' for r in rows))
if __name__=='__main__':raise SystemExit(main())
