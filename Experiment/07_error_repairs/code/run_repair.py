#!/usr/bin/env python3
"""Copy a completed trial's state into a separate repair pass, preserving originals."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]

def write(p,data):
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)

def main():
    global ROOT
    campaign = json.loads((ROOT/'Experiment/07_error_repairs/status.json').read_text())
    if campaign.get('runtime'):
        ROOT = Path(campaign['runtime']['root']).resolve()
        if not (ROOT/'runtime_manifest.json').exists():
            raise RuntimeError('Pinned repair runtime is missing')
        sys.path.insert(0, str(ROOT/'src'))
        os.environ['PYTHONPATH'] = str(ROOT/'src')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-run',type=Path,required=True)
    p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--workers',type=int,default=20)
    a=p.parse_args();source=a.source_run.resolve();dest=a.run_dir.resolve()
    if source==dest:raise ValueError('Repairs must use a separate directory')
    os.umask(0o077);dest.mkdir(parents=True,exist_ok=True)
    repair_lock=(dest/'repair.lock').open('a');fcntl.flock(repair_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    manifest=json.loads((source/'manifest.json').read_text())
    if not (dest/'repair_snapshot.json').exists():
        lock=(source/'coordinator.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (dest/'episodes').exists():raise RuntimeError('Partial initialization exists; inspect before retrying')
        for name in ['manifest.json','selection.csv']:shutil.copyfile(source/name,dest/name)
        shutil.copytree(source/'configs',dest/'configs',dirs_exist_ok=True)
        (dest/'prepared').symlink_to((source/'prepared').resolve(),target_is_directory=True)
        from personasciencebench.packaging import safe_component
        import csv
        selection=list(csv.DictReader((source/'selection.csv').open()))
        targets=[];all_states=[]
        def copy(row_arm):
            row,arm=row_arm;key=safe_component(row['source']+':'+row['task_id'])
            old=source/'episodes'/key/arm;new=dest/'episodes'/key/arm;new.mkdir(parents=True)
            p=old/'state.json'
            if p.exists():
                raw=p.read_bytes();state=json.loads(raw);digest=hashlib.sha256(raw).hexdigest()
            else:
                state={**row,'arm':arm,'attempt':0,'status':'infrastructure_error','error':'No episode state in source run'};digest=None
            for attempt in old.glob('attempt-*'):
                if attempt.is_dir():(new/attempt.name).symlink_to(attempt.resolve(),target_is_directory=True)
            (new/'state.json').write_text(json.dumps(state,indent=2)+'\n')
            missing=any(n.get('status')=='missing_submission' for n in state.get('native_results',[]))
            reason='missing_submission' if missing else state['status'] if state['status'] in ('infrastructure_error','running') else None
            info={'source':row['source'],'task_id':row['task_id'],'arm':arm,'original_status':state['status'],'original_attempt':state.get('attempt'),'state_sha256':digest,'repair_reason':reason}
            return state,info
        with ThreadPoolExecutor(max_workers=16) as pool:
            for state,info in pool.map(copy,[(r,arm) for r in selection for arm in manifest['arms']]):
                all_states.append(state)
                if info['repair_reason']:targets.append(info)
        write(dest/'original_results_snapshot.json',all_states)
        write(dest/'repair_snapshot.json',{'source_run':str(source),'captured_at_utc':datetime.now(timezone.utc).isoformat(),'workers':a.workers,'target_count':len(targets),'target_counts':dict(Counter(x['repair_reason'] for x in targets)),'targets':targets,'interpretation':'Conditional repair attempts, not independent trials. Original scores and missing-submission outcomes remain in the source run.'})
        fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
    snapshot=json.loads((dest/'repair_snapshot.json').read_text())
    print('Repair targets:',snapshot['target_count'],snapshot['target_counts'],flush=True)
    cmd=[sys.executable,str(ROOT/'scripts/run_openai_first_pass.py'),'--run-dir',str(dest),'--selection',str(dest/'selection.csv'),'--workers',str(a.workers),'--model',manifest['model'],'--reasoning-effort',manifest['reasoning_effort'],'--retry-infrastructure','--retry-missing','--arms',*manifest['arms']]
    if manifest.get('baseline_run'):cmd+=['--baseline-run',manifest['baseline_run']]
    proc=subprocess.run(cmd,cwd=ROOT)
    result=dest/'results.json'
    report={'job_id':os.environ.get('SLURM_JOB_ID'),'source_run':str(source),'returncode':proc.returncode,'finished_at_utc':datetime.now(timezone.utc).isoformat(),'initial_repair_targets':snapshot['target_count']}
    if result.exists():
        rows=json.loads(result.read_text());ids={(x['source'],x['task_id'],x['arm']) for x in snapshot['targets']}
        repaired=[x for x in rows if (x['source'],x['task_id'],x['arm']) in ids]
        report['target_outcomes']=dict(Counter('missing_submission' if any(n.get('status')=='missing_submission' for n in x.get('native_results',[])) else x['status'] for x in repaired))
    write(dest/'repair_summary.json',report)
    return proc.returncode

if __name__=='__main__':raise SystemExit(main())
