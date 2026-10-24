"""Opt-in shared request pacing for free OpenRouter models; no paid fallback."""
import fcntl
import json
import os
from pathlib import Path
import time


def _paths():
    root = Path(os.environ['PSB_OPENROUTER_RATE_DIR'])
    root.mkdir(parents=True, exist_ok=True)
    return root / 'rate.json', root / 'rate.lock'


def _state_update(update):
    path, lock = _paths()
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        state = json.loads(path.read_text()) if path.exists() else {}
        result = update(state)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state))
        tmp.replace(path)
        return result


def _check_stop():
    fatal = os.environ.get('PSB_FATAL_API_FILE')
    if fatal and Path(fatal).exists():
        raise RuntimeError('Free-model campaign stopped: inspect fatal_api.json before resuming')


def _acquire():
    interval = 60 / float(os.environ.get('PSB_OPENROUTER_RPM', '18'))
    while True:
        _check_stop()
        def reserve(state):
            now = time.time()
            wait = max(state.get('next', 0), state.get('cooldown', 0)) - now
            if wait <= 0:
                state['next'] = now + interval
                return 0
            return wait
        wait = _state_update(reserve)
        if wait <= 0:
            return
        time.sleep(min(wait, 5))


def _cooldown(delay):
    def update(state):
        state['cooldown'] = max(state.get('cooldown', 0), time.time() + delay)
    _state_update(update)


def _quota_stop():
    path = os.environ.get('PSB_FATAL_API_FILE')
    if path:
        p = Path(path)
        # Single atomic creation: do not overwrite an existing stop reason.
        try:
            with p.open('x') as f:
                json.dump({'reason': 'OpenRouter free-model daily quota exhausted',
                           'time': time.time(), 'action': 'Preserve attempts; resume after quota reset with --retry-infrastructure.'}, f)
        except FileExistsError:
            pass


def paced_post(send, payload):
    if not os.environ.get('PSB_OPENROUTER_RATE_DIR') or not payload.get('model', '').endswith(':free'):
        return send()
    for attempt in range(7):
        _acquire()
        response = send()
        response._psb_rate_limit_retries = attempt
        if response.status_code != 429:
            return response
        def record_limit(state):
            state['rate_limit_responses'] = state.get('rate_limit_responses', 0) + 1
            state['last_rate_limit_at'] = time.time()
        _state_update(record_limit)
        headers = response.headers
        try:
            error = response.json().get('error', {})
            message = str(error.get('message', '')).lower()
        except (ValueError, AttributeError):
            message = ''
        try:
            reset = float(headers.get('x-ratelimit-reset', '0'))
            if reset > 1e12:
                reset /= 1000
            reset_wait = max(0, reset - time.time())
        except ValueError:
            reset_wait = 0
        if 'daily' in message or 'per day' in message or 'per-day' in message or reset_wait > 3600:
            _quota_stop()
            return response
        try:
            delay = float(headers.get('retry-after', '0'))
        except ValueError:
            delay = 0
        _cooldown(max(delay, reset_wait, min(60, 2 ** (attempt + 1))))
        if attempt == 6:
            return response
