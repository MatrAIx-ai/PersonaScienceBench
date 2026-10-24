#!/usr/bin/env bash
# Finish the authorized judge-only workflow and prepare a validated local export.
# This script never launches actor/simulator episodes or commits/pushes results.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
: "${ENV_FILE:?Set ENV_FILE to the private dotenv file}"
grading_run="runs/main/gemini-3.8-flash-nvidia-medium/trial-1"
grading_output="$grading_run/grading/astra-low-v1"
graded_bundle="${GRADED_BUNDLE:-runs/gemini-upload-staging/astra-graded}"
while systemctl --user is-active --quiet "${GRADING_SERVICE:-psb-gemini-astra-judging.service}"; do
  sleep 20
done
test -f "$grading_output/results.json"
# Retry failed evaluations once; successful/zero grades are retained. Identical
# completed shared-judge prefixes are reused and every failed attempt remains.
if .venv/bin/python scripts/grade_collection.py \
    --run-dir "$grading_run" --output "$grading_output" \
    --env-file "$ENV_FILE" --workers 4 --retry-errors; then
  echo 'Final grading pass completed.'
else
  echo 'Some grades remain unavailable; the export will retain explicit errors.'
fi
.venv/bin/python scripts/export_graded_collection.py \
  --collection /home/sherryj/Desktop/PersonaScienceBench-upload-gemini-medium/results/gemini-3.8-flash-actor-simulator-medium/trial-1 \
  --grading-dir "$grading_output" \
  --output "$graded_bundle" \
  --env-file "$ENV_FILE"
python3 -B scripts/export_graded_collection.py --validate "$graded_bundle"
export GRADED_BUNDLE="$graded_bundle"
python3 - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
bundle = Path(os.environ['GRADED_BUNDLE']).resolve()
d = json.loads((bundle/'delivery.json').read_text())
status = {'checked_at':datetime.now(timezone.utc).isoformat(),'output':str(bundle),
          'validated':True,'grading_complete':d['grading_complete'],
          'selected_statuses':d['selected_statuses'],'judge_calls':d['judge_calls'],
          'uploaded':False,'commit_created':False}
Path('runs/main/gemini-3.8-flash-nvidia-medium/trial-1/grading/astra-low-v1/package-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
PY
