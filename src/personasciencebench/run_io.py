"""Read finished (or replayed) persona runs and make budgeted, logged post-hoc judge calls."""

import json
from pathlib import Path
import re
import threading
import time

from personasciencebench.arms import arm_kind


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def jsonl(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def case_events(case):
    path = case / 'controller/events.jsonl'
    return sorted(jsonl(path if path.exists() else case / 'events.jsonl'), key=lambda e: e['sequence'])


def find_case(run, job, finished):
    """The case directory of a job: from its finished record, else the one replayed case under episodes/<key>/."""
    if finished and finished.get('result'):
        return Path(finished['result']).parent
    found = sorted((run / 'episodes' / job['key']).glob('*/controller/events.jsonl'))
    return found[0].parent.parent if len(found) == 1 else None


def load_run(run):
    """One record per (arm, task), latest attempt, as the benchmark report counts them.

    Replay-only case dirs (controller/events.jsonl and controller/episode.private.json) load the same way;
    fields they lack are None.
    """
    run = Path(run)
    manifest = read_json(run / 'manifest.json')
    latest = {}
    for job in manifest['jobs']:
        finished = {}
        for path in sorted((run / 'finished').glob(job['key'] + '*.json')):
            record = read_json(path)
            if record.get('arm') == job['arm'] and record.get('id') == job['id'] \
                    and record.get('attempt', 1) >= finished.get('attempt', 1):
                finished = record
        case = find_case(run, job, finished)
        if case is None or not (case / 'controller/episode.private.json').exists():
            continue
        episode = read_json(case / 'controller/episode.private.json')
        result = case / 'result.json'
        latest[(job['arm'], job['id'])] = {
            'key': job['key'], 'arm': job['arm'], 'kind': arm_kind(job['arm']), 'task': job['id'],
            'benchmark': job.get('benchmark') or episode.get('benchmark'), 'case': case,
            'status': finished.get('status') or (read_json(result)['status'] if result.exists() else None),
            'episode': episode, 'events': case_events(case)}
    return list(latest.values())


def researcher_messages(record):
    """Everything the simulated researcher wrote, in order; nothing from the agent."""
    if record['benchmark'] == 'sciconvbench':
        texts = [e['payload'].get('answer') for e in record['events'] if e['type'] == 'researcher_reply']
    else:
        texts = [e['payload'].get('message') for e in record['events'] if e['type'] == 'researcher_decision']
    return [t for t in texts if isinstance(t, str) and t.strip()]


def sciconv_turns(events):
    """(question, reply) pairs; a question left without a reply is not a turn."""
    turns, question = [], None
    for e in events:
        if e['type'] == 'researcher_question':
            question = e['payload'].get('question') or ''
        elif e['type'] == 'researcher_reply' and question is not None:
            turns.append({'question': question, 'answer': e['payload'].get('answer') or ''})
            question = None
    return turns


def final_specification(events):
    finals = [e['payload'].get('answer') for e in events if e['type'] == 'final_specification']
    return finals[-1] if finals else None


def arm_config(run, arm):
    path = Path(run) / 'configs' / arm / 'shared.json'
    return read_json(path) if path.exists() else None


def profile_text(run, arm):
    config = arm_config(run, arm)
    persona = (config or {}).get('persona') or {}
    return persona.get('system_prompt') if persona.get('enabled') else None


def default_judge(run):
    config = arm_config(run, 'persona_off')
    return dict(config['models']['judge']) if config else None


def model_spec(run, model):
    """The run's judge settings, with only the model name replaced when one is given."""
    spec = default_judge(run) or {}
    if model:
        spec['model'] = model
    if not spec.get('model'):
        raise ValueError('No judge model in configs/persona_off/shared.json; pass --model')
    return spec


def norm_ws(text):
    return ' '.join((text or '').split())


def is_verbatim(quote, text):
    q = norm_ws(quote)
    return bool(q) and q in norm_ws(text)


def parse_final_json(text):
    """Last <FINAL_JSON> block, else the outermost braces; None when that is not a JSON object."""
    if not isinstance(text, str):
        return None
    matches = re.findall(r'<FINAL_JSON>(.*?)</FINAL_JSON>', text, re.DOTALL)
    if matches:
        body = matches[-1].strip()
    else:
        cleaned = re.sub(r'```(?:json)?\s*', '', text)
        start, end = cleaned.find('{'), cleaned.rfind('}')
        if start == -1 or end <= start:
            return None
        body = cleaned[start:end + 1]
    try:
        value = json.loads(body)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


class BudgetExhausted(Exception):
    pass


class JudgeCaller:
    """Every call is logged; calls stop once the summed reported cost reaches the budget.

    With concurrent workers, calls already in flight when the budget is reached still complete,
    so spend can exceed the budget by at most workers - 1 calls.
    """

    def __init__(self, run, script, spec, *, budget_usd, dry_run=False, price_in=None, price_out=None, client=None):
        self.log_path = Path(run) / script / 'api_calls.jsonl'
        self.spec, self.budget, self.dry_run = spec, budget_usd, dry_run
        self.prices = (price_in, price_out) if price_in is not None and price_out is not None else None
        self.spent, self.calls, self.estimated_tokens = 0.0, 0, 0
        self.lock = threading.Lock()
        self.halted = None
        self.client = client
        if client is None and not dry_run:
            from personasciencebench.inference import OpenRouterClient, load_env, preflight
            from personasciencebench.registry import project_root
            load_env(project_root() / '.env')
            catalog = preflight({'judge': spec})
            self.client = OpenRouterClient(**spec, role='judge',
                                           supported_parameters=catalog['judge']['supported_parameters'])

    def cost(self, usage):
        if isinstance(usage.get('cost'), (int, float)):
            return float(usage['cost'])
        if self.prices is None:
            raise RuntimeError('Response has no usage cost; pass --price-in and --price-out to budget by tokens')
        return (usage.get('prompt_tokens', 0) * self.prices[0] + usage.get('completion_tokens', 0) * self.prices[1]) / 1e6

    def call(self, messages, tag):
        """The completion text, or None in a dry run (counted, tokens estimated as chars/4)."""
        with self.lock:
            if self.dry_run:
                self.calls += 1
                self.estimated_tokens += sum(len(m['content']) for m in messages) // 4
                return None
            if self.halted:
                raise RuntimeError(self.halted)
            if self.spent >= self.budget:
                raise BudgetExhausted(f'Spent ${self.spent:.4f} of ${self.budget:.4f}')
            self.calls += 1
        started = time.time()
        response = self.client.completion(messages)
        usage = response.get('usage') or {}
        entry = {'tag': tag, 'model': self.spec.get('model'), 'time': started, 'seconds': time.time() - started,
                 'request': {'messages': messages}, 'response': response, 'usage': usage}
        with self.lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open('a') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            try:
                self.spent += self.cost(usage)
            except RuntimeError as exc:
                self.halted = str(exc)
                raise
        return response['choices'][0]['message']['content']

    def call_json(self, messages, tag, valid):
        """Parsed judge JSON that passes `valid`, retried once; (value or None, attempts)."""
        for attempt in (1, 2):
            text = self.call(messages, f'{tag}#{attempt}')
            if text is None:
                return None, 0
            value = parse_final_json(text)
            if value is not None and valid(value):
                return value, attempt
        return None, 2

    def report(self):
        return {'dry_run': self.dry_run, 'calls': self.calls, 'spent_usd': self.spent, 'budget_usd': self.budget,
                'model': self.spec.get('model'),
                **({'estimated_input_tokens': self.estimated_tokens} if self.dry_run else {})}
