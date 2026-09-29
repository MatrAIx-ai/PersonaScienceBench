#!/usr/bin/env python3
"""Export existing episode-level counters; no inference or transcript judging."""
import argparse
import csv
import json
from pathlib import Path

FIELDS = ['researcher_questions','researcher_requests','researcher_followups','researcher_decisions','actor_calls','plan_reviews','result_reviews','collaboration_termination']
METRICS = ['FRR','CGRR','SRR','clarification_recall','clarification_precision','memory_consistency','intent_capture']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--trial', type=int, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    records = json.loads((a.run_dir/'results.json').read_text())
    rows = []
    for record in records:
        x = next((v for v in record.get('native_results',[]) if v.get('episode_id') or v.get('task_id')), {})
        row = {k:record.get(k) for k in ('source','task_id','family','arm')}
        row.update(trial=a.trial,run_directory=str(a.run_dir),status=x.get('status',record['status']))
        row.update({k:x.get(k) for k in FIELDS})
        row.update({k:(x.get('evaluation') or {}).get('metrics',{}).get(k) for k in METRICS})
        rows.append(row)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['trial','source','task_id','arm'])
        writer.writeheader();writer.writerows(rows)
    print(f'Exported {len(rows)} episode records; absent fields remain blank. Output: {a.output}')

if __name__ == '__main__':
    main()
