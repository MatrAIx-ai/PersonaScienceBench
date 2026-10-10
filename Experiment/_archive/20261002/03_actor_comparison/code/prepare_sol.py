#!/usr/bin/env python3
"""Prepare (and optionally submit) an isolated GPT-5.6 Sol three-trial campaign."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]

def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--role-scope',required=True,choices=['actor','actor-simulator','all'])
    p.add_argument('--panel',required=True,choices=['prioritized','group2','all-started'])
    p.add_argument('--reasoning-effort',required=True,choices=['none','low','medium','high','xhigh','max'])
    p.add_argument('--after-job',type=int,help='Required for submission: preserve sequential API workload')
    p.add_argument('--submit',action='store_true')
    a=p.parse_args()
    if a.submit and not a.after_job:p.error('--submit requires --after-job')
    base=ROOT/'Experiment/03_actor_comparison'
    campaign=f'gpt56sol-{a.role_scope}-{a.reasoning_effort}-{a.panel}'
    path=base/'data'/f'{campaign}.json'
    if path.exists():
        plan=json.loads(path.read_text())
    else:
        prior=json.loads((ROOT/'Experiment/07_error_repairs/status.json').read_text())['runtime']
        runtime=ROOT/'runs'/f'{campaign}-runtime';runtime.mkdir(exist_ok=False)
        source=Path(prior['root'])
        for name in ['src','scripts','configs','manifests']:shutil.copytree(source/name,runtime/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copyfile(ROOT/'scripts/run_openai_first_pass.py',runtime/'scripts/run_openai_first_pass.py')
        for name in ['.venv','.actor-venv','.env','data','external']:(runtime/name).symlink_to(ROOT/name,target_is_directory=(ROOT/name).is_dir())
        selection=ROOT/'Experiment/shared/task_selection.csv'
        prepared=(ROOT/'runs/openai-astra-top2-first-pass/prepared').resolve()
        from personasciencebench.packaging import safe_component
        rows=list(csv.DictReader(selection.open()))
        for row in rows:
            required=prepared/safe_component(row['source']+':'+row['task_id'])/('tasks.jsonl' if row['source']=='expbench' else 'pilot_manifest.json')
            if not required.exists():raise ValueError(f'Missing frozen input {required}')
        hashes={str(f.relative_to(runtime)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['src','scripts','configs','manifests'] for f in (runtime/folder).rglob('*') if f.is_file()}
        write(runtime/'runtime_manifest.json',{'scientific_code_commit':prior['scientific_code_commit'],'transport_overlay_commit':prior['transport_overlay_commit'],'coordinator_sha256':hashes['scripts/run_openai_first_pass.py'],'sha256':hashes})
        groups=[['persona_off','candidate_148','candidate_155'],['candidate_089','candidate_001','candidate_127']]
        if a.panel=='group2':groups=[['persona_off','candidate_089','candidate_001'],['candidate_127']]
        if a.panel=='all-started':groups.append(['candidate_046','candidate_003','candidate_004'])
        plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'status':'prepared','campaign':campaign,'role_scope':a.role_scope,'reasoning_effort':a.reasoning_effort,'model':'gpt-5.6-sol','panel':a.panel,'trials':3,'planned_episodes':sum(map(len,groups))*600,'workers':30,'cpus':30,'memory_gb':128,'runtime':str(runtime),'runtime_manifest_sha256':hashlib.sha256((runtime/'runtime_manifest.json').read_bytes()).hexdigest(),'selection_sha256':hashlib.sha256(selection.read_bytes()).hexdigest(),'jobs':[]}
        for trial in [1,2,3]:
            baseline=ROOT/'runs'/f'{campaign}-trial-{trial}-batch-1'
            for batch,arms in enumerate(groups,1):
                run=ROOT/'runs'/f'{campaign}-trial-{trial}-batch-{batch}';run.mkdir(exist_ok=False)
                shutil.copyfile(selection,run/'selection.csv');(run/'prepared').symlink_to(prepared,target_is_directory=True)
                cmd=[str(ROOT/'.venv/bin/python'),str(runtime/'scripts/run_openai_first_pass.py'),'--run-dir',str(run),'--selection',str(run/'selection.csv'),'--workers','30','--require-prepared','--model','gpt-6-astra' if a.role_scope!='all' else 'gpt-5.6-sol','--reasoning-effort','low' if a.role_scope!='all' else a.reasoning_effort]
                if a.role_scope!='all':cmd+=['--actor-model','gpt-5.6-sol','--actor-reasoning-effort',a.reasoning_effort]
                if a.role_scope=='actor-simulator':cmd+=['--researcher-model','gpt-5.6-sol','--researcher-reasoning-effort',a.reasoning_effort]
                if batch>1:cmd+=['--baseline-run',str(baseline)]
                cmd+=['--arms',*arms]
                plan['jobs'].append({'trial':trial,'batch':batch,'arms':arms,'run_dir':str(run),'command':cmd})
        write(path,plan)
    if a.submit:
        previous=str(a.after_job)
        for job in plan['jobs']:
            if job.get('job_id'):previous=job['job_id'];continue
            run=Path(job['run_dir'])
            if (run/'job_id').exists():raise RuntimeError('Unrecorded existing job; reconcile before submitting')
            env=dict(os.environ,RUN_DIR=str(run),DEPENDENCY='afterany:'+previous,PYTHONPATH=str(Path(plan['runtime'])/'src'))
            jobid=subprocess.check_output(['bash',str(base/'code/submit_sol.sh'),*job['command']],env=env,text=True).strip()
            if not jobid.isdigit():raise RuntimeError('Invalid submission response')
            job.update(job_id=jobid,dependency='afterany:'+previous);write(path,plan);previous=jobid
        plan['status']='submitted_sequentially';write(path,plan)
    print(json.dumps({'manifest':str(path),'status':plan['status'],'episodes':plan['planned_episodes'],'jobs':[j.get('job_id') for j in plan['jobs']]},indent=2))

if __name__=='__main__':main()
