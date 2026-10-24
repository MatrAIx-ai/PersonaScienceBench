#!/usr/bin/env python3
"""Submit prepared additional-persona batches as one sequential Slurm chain."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--after-job', required=True, type=int)
    p.add_argument('--manifest', type=Path, default=ROOT/'runs/openai-astra-top10-expansion.json')
    a = p.parse_args()
    data = json.loads(a.manifest.read_text())
    previous = str(a.after_job)
    for batch in data['batches']:
        if batch.get('job_id'):
            previous = batch['job_id']
            continue
        run = Path(batch['run_dir'])
        if (run/'job_id').exists():
            raise RuntimeError(f'Unrecorded submission in {run}; reconcile before continuing')
        env = dict(os.environ, RUN_DIR=str(run), DEPENDENCY='afterany:'+previous)
        cmd = ['bash',str(ROOT/'scripts/submit_openai_first_pass.sh'),
               '--selection',str(run/'selection.csv'),'--baseline-run',batch['baseline_run'],
               '--arms',*batch['arms']]
        subprocess.run(cmd,env=env,cwd=ROOT,check=True)
        job = (run/'job_id').read_text().strip()
        batch.update(job_id=job,dependency='afterany:'+previous,
                     submitted_at_utc=datetime.now(timezone.utc).isoformat())
        tmp = a.manifest.with_suffix('.tmp')
        tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(a.manifest)
        previous = job
    print('Final job in chain:',previous)

if __name__ == '__main__':
    main()
