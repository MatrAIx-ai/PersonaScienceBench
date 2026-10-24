#!/usr/bin/env bash
# Finish local packaging after the authorized response-repair service stops.
# Never commits, pushes, changes model settings, or reruns scientific episodes.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
: "${ENV_FILE:?Set ENV_FILE to the existing private dotenv path}"
repair_service="${REPAIR_SERVICE:-psb-gemini-trial1-retry2.service}"
export REPAIR_LABEL="${REPAIR_LABEL:-retry-2}"
[[ "$REPAIR_LABEL" =~ ^retry-[0-9]+$ ]] || { echo 'Invalid repair label' >&2; exit 1; }
collection_run="runs/main/gemini-3.8-flash-nvidia-medium/trial-1"
collection_output="results/gemini-3.8-flash-actor-simulator-nvidia-medium/trial-1"
export COLLECTION_STAGING="${collection_output}.${REPAIR_LABEL}"
while systemctl --user is-active --quiet "$repair_service"; do
  sleep 20
done
.venv/bin/python - <<'PY'
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, os
from pathlib import Path
run=Path('runs/main/gemini-3.8-flash-nvidia-medium/trial-1')
rows=[json.loads(p.read_text()) for p in (run/'episodes').glob('*/*/state.json')]
assert len(rows)==1000 and not any(r['status']=='running' for r in rows)
repair_dir=run/'repairs'/os.environ['REPAIR_LABEL']
baseline=repair_dir/'original-all-states.json'
if baseline.exists():
    old={ (r['source'],r['task_id'],r['arm']):r for r in json.loads(baseline.read_text()) }
    selection=json.loads((repair_dir/'retry-selection.json').read_text())['slots']
    selected={(r['source'],r['task_id'],r['arm']) for r in selection}
    for row in rows:
        identity=(row['source'],row['task_id'],row['arm'])
        if identity in selected:
            assert row['attempt']==old[identity]['attempt']+1, identity
        else:
            assert row==old[identity], f'Unselected outcome changed: {identity}'
failures=[]
for row in rows:
    if row['status']!='infrastructure_error':continue
    native=(row.get('native_results') or [{}])[0]
    evidence={'source':row['source'],'task_id':row['task_id'],'arm':row['arm'],'attempt':row['attempt'],'error':native.get('actor',{}).get('error') or native.get('error'),'last_responses':[]}
    case=Path(native['case_directory']) if native.get('case_directory') else None
    api=case/'controller/api_calls.private.jsonl' if case else None
    if api is not None and api.is_file():
        calls=[json.loads(line) for line in api.open() if line.strip()]
        for call in calls[-3:]:
            choice=call['response']['choices'][0]
            evidence['last_responses'].append({'role':call['role'],'request_sha256':hashlib.sha256(json.dumps(call['request'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'max_tokens':call['request'].get('max_tokens'),'finish_reason':choice.get('finish_reason'),'usage':call.get('usage'),'response_repair':call.get('response_repair')})
    failures.append(evidence)
report={'checked_at':datetime.now(timezone.utc).isoformat(),'runner_statuses':dict(Counter(r['status'] for r in rows)),'failures':failures,'disposition':'Unresolved errors remain unavailable; do not relabel them as scientific zeros or bypass provider safety controls.'}
p=repair_dir/'final-failure-audit.json';p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'runner_statuses':report['runner_statuses'],'unresolved':len(failures)}),flush=True)
PY
.venv/bin/python scripts/export_collection_bundle.py \
  --run-dir "$collection_run" --output "$COLLECTION_STAGING" \
  --allow-partial --env-file "$ENV_FILE"
.venv/bin/python scripts/validate_collection_bundle.py "$COLLECTION_STAGING"
.venv/bin/python - <<'PY'
import importlib.util, json, os
from datetime import datetime, timezone
from pathlib import Path
out=Path(os.environ['COLLECTION_STAGING']).resolve()
spec=importlib.util.spec_from_file_location('audit','scripts/audit_result_bundles.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
print(json.dumps(m.audit(out)),flush=True)
delivery=json.loads((out/'delivery.json').read_text())
canonical=Path('results/gemini-3.8-flash-actor-simulator-nvidia-medium/trial-1').resolve()
archive=Path('runs/main/gemini-3.8-flash-nvidia-medium/trial-1/export-archives')/('before-'+os.environ['REPAIR_LABEL'])
archived=False
if canonical.exists():
    assert not archive.exists(), f'Archive already exists: {archive}'
    archive.parent.mkdir(parents=True,exist_ok=True)
    canonical.rename(archive)
    archived=True
try:
    out.rename(canonical)
except BaseException:
    if archived: archive.rename(canonical)
    raise
out=canonical
status={'checked_at':datetime.now(timezone.utc).isoformat(),'output':str(out),'validated':True,'delivery_status':delivery['status'],'unresolved_execution_errors':delivery['unresolved_execution_errors'],'uploaded':False,'commit_created':False}
Path('runs/main/gemini-3.8-flash-nvidia-medium/trial-1/provenance/package-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2),flush=True)
PY
