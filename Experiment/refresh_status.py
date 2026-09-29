#!/usr/bin/env python3
"""Refresh collection snapshots from local artifacts; no network, inference, or submission."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'Experiment'


def main():
    source = ROOT/'runs/openai-astra-top2-three-trials.json'
    trials = json.loads(source.read_text())['trials']
    output = {'snapshot_utc': datetime.now(timezone.utc).isoformat(),
              'source': str(source.relative_to(ROOT)), 'scheduler_state_checked': False, 'trials': []}
    for trial in trials:
        run = Path(trial['run_dir'])
        path = run/'progress.json'
        progress = json.loads(path.read_text()) if path.exists() else None
        item = {'trial': trial['trial'], 'job_id': trial.get('job_id'),
                'run_directory': str(run.relative_to(ROOT)), 'progress': progress,
                'final_results_present': (run/'results.json').exists(),
                'collection_status': 'not_observed', 'needs_error_investigation': False}
        if progress:
            errors = progress.get('statuses',{}).get('infrastructure_error',0)
            item['needs_error_investigation'] = errors > 0
            item['collection_status'] = ('all_processed_with_errors' if errors else 'all_processed') if progress['processed'] == progress['planned'] else 'partial_scheduler_state_unknown'
        output['trials'].append(item)
    (BASE/'shared/run_status.json').write_text(json.dumps(output,indent=2)+'\n')
    for path in BASE.glob('*/status.json'):
        data = json.loads(path.read_text())
        data['collection_snapshot_utc'] = output['snapshot_utc']
        data['shared_trials_have_errors'] = any(t['needs_error_investigation'] for t in output['trials'])
        path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__ == '__main__':
    main()
