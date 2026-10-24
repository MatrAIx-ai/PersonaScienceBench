#!/usr/bin/env bash
# Finish the active repair, then retry only truncations below the raised caps.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
: "${ENV_FILE:?Set the private dotenv path}"
while systemctl --user is-active --quiet psb-minimax-m3-trial1-repair1.service; do
  sleep 20
done
test ! -f runs/main/minimax-m3-adaptive/trial-1/fatal_api.json
.venv/bin/python - <<'PY'
import fcntl, hashlib, importlib.util, json
from datetime import datetime, timezone
from pathlib import Path
spec = importlib.util.spec_from_file_location('runner', 'scripts/run_main.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
run = Path('runs/main/minimax-m3-adaptive/trial-1')
with (run/'coordinator.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    policy = json.loads((run/'generation_limits.json').read_text())
    states = [(p, json.loads(p.read_text())) for p in (run/'episodes').glob('*/*/state.json')]
    assert len(states) == 1000 and not any(s['status'] == 'running' for p, s in states)
    targets = [s for p, s in states if runner.truncated_below_policy(p.parent, s, policy['max_output_tokens'])]
    receipt = {'policy_sha256': hashlib.sha256((run/'generation_limits.json').read_bytes()).hexdigest(),
               'recorded_at': datetime.now(timezone.utc).isoformat(), 'target_count': len(targets),
               'targets': targets, 'previous_states': [s for p, s in states],
               'reason': 'Retry only recorded truncations below the user-authorized higher output caps'}
    path = run/'provenance/token-repair-targets.json'
    with path.open('x') as stream:
        stream.write(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'old_cap_truncations_to_retry': len(targets)}), flush=True)
PY
exec bash scripts/run_minimax_m3.sh --retry-truncations-below-policy
