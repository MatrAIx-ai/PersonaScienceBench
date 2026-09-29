#!/usr/bin/env python3
"""Give every arm's simulated researcher the agent messages of one reference episode.

In a full run each arm's agent takes its own path, so persona-vs-control gaps mostly
measure agent divergence. Replay holds the agent side fixed and compares only what the
researcher says back. SciConv: each arm answers the reference episode's clarification
questions in order, with its own earlier replies as history. Active researcher: at each
reference decision point k, the arm makes one decision from the reference history and
handoff (a one-step counterfactual; points are independent).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import threading
import time

from personasciencebench.arms import CONTROL, NEUTRAL, PERSONA, TWIN, arm_kind
from personasciencebench.collaboration import ActiveResearcher, validate_collaboration
from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.persona import persona_record, render_persona, resolve_persona
from personasciencebench.registry import load_adapter, project_root
from personasciencebench.schema import Episode
from personasciencebench.sciconv_runner import Service, native_class, researcher_system_prompt

ELIGIBLE = (PERSONA, TWIN, NEUTRAL, CONTROL)
DRY_DECISION = {"action": "continue", "interaction": "next_task", "message": "Dry run.", "evidence": "",
                "objectives_open": [], "fact_ids": [], "approve_approach": False}


class BudgetReached(Exception):
    pass


class NotReplayable(Exception):
    pass


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()] if Path(path).exists() else []


def append(path, value):
    with Path(path).open('a') as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + '\n')


def words(text):
    return len(str(text).split())


class Calls:
    """All replay model calls: logged, costed, and refused once the budget is spent."""

    def __init__(self, log, budget_usd, *, price_in=None, price_out=None, send=None, dry_run=False):
        self.log, self.budget, self.send, self.dry_run = log, budget_usd, send, dry_run
        self.prices = (price_in, price_out) if price_in is not None and price_out is not None else None
        self.spent, self.calls, self.prompt_tokens, self.stopped = 0.0, 0, 0, False
        self.lock = threading.Lock()
        self.context = threading.local()

    def check(self):
        with self.lock:
            if not self.dry_run and self.spent >= self.budget:
                self.stopped = True
                raise BudgetReached(f'Replay budget of ${self.budget} reached')

    def record(self, value):
        usage = value.get('usage') or {}
        cost = usage.get('cost')
        if not isinstance(cost, (int, float)) or isinstance(cost, bool):
            cost = None if self.prices is None else (usage.get('prompt_tokens', 0) * self.prices[0]
                                                     + usage.get('completion_tokens', 0) * self.prices[1]) / 1e6
        with self.lock:
            self.calls += 1
            self.prompt_tokens += usage.get('prompt_tokens', 0)
            self.spent += cost or 0.0
            if self.log is not None:
                append(self.log, {**getattr(self.context, 'value', {}), 'time': time.time(),
                                  'cost_usd': cost, **value})
        if cost is None and not self.dry_run:
            raise RuntimeError('Model response has no usage.cost; pass --price-in and --price-out')

    def guard(self, client):
        """Budget-check every request; fakes and dry runs replace only the HTTP call."""
        original = client.completion

        def completion(messages, tools=None, *, json_mode=False, settings=None, tool_choice=None):
            self.check()
            if self.send is None:
                return original(messages, tools, json_mode=json_mode, settings=settings, tool_choice=tool_choice)
            payload = {'model': client.model, 'messages': messages, 'tools': tools,
                       'tool_choice': tool_choice, 'json_mode': json_mode}
            response = self.send(payload)
            self.record({'role': client.role, 'model': client.model, 'request': payload,
                         'response': response, 'usage': response.get('usage', {})})
            return response
        client.completion = completion
        return client


def dry_response(payload):
    tokens = sum(len(m['content']) for m in payload['messages'] if isinstance(m.get('content'), str)) // 4
    message = {'role': 'assistant', 'content': 'Dry run.'}
    if payload.get('tools'):
        message = {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'dry', 'type': 'function', 'function': {
            'name': payload['tools'][0]['function']['name'], 'arguments': json.dumps(DRY_DECISION)}}]}
    return {'choices': [{'message': message, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': tokens, 'completion_tokens': 0, 'cost': 0.0}}


def keyword_names(*functions):
    names = set()
    for function in functions:
        for parameter in inspect.signature(function).parameters.values():
            if parameter.kind in (parameter.KEYWORD_ONLY, parameter.POSITIONAL_OR_KEYWORD):
                names.add(parameter.name)
    return names


def sciconv_options(collaboration):
    """Every researcher_system_prompt switch, read from the arm's collaboration config."""
    parameters = inspect.signature(researcher_system_prompt).parameters
    return {name: collaboration.get(name, p.default) for name, p in parameters.items()
            if name not in ('native', 'persona_text') and p.kind == p.KEYWORD_ONLY}


def service_options(collaboration):
    names = keyword_names(Service.__init__) - {'self', 'client', 'persona_text', 'prompt_options'}
    return {k: v for k, v in collaboration.items() if k in names}


def active_options(collaboration):
    inits = [vars(c)['__init__'] for c in ActiveResearcher.__mro__ if '__init__' in vars(c) and c is not object]
    names = keyword_names(*inits) - {'self', 'episode', 'backend', 'persona'}
    return {k: v for k, v in collaboration.items() if k in names}


def decision_points(history, audit):
    """Reference state before each decision: history prefix, the handoff decide() received, approval."""
    assistant = [i for i, message in enumerate(history) if message['role'] == 'assistant']
    if len(assistant) != len(audit):
        raise ValueError('Reference researcher history and audit are not aligned')
    points, approved = [], False
    for position, entry in zip(assistant, audit):
        if 'decision' not in entry:
            continue
        prefix, handoff = history[:position], None
        if points:
            # decide() appended the handoff itself, so the prefix stops before it.
            try:
                handoff = json.loads(prefix[-1]['content'])['agent_handoff']
            except (IndexError, KeyError, TypeError, ValueError):
                raise ValueError('Reference decision is not preceded by an agent handoff') from None
            prefix = prefix[:-1]
        points.append({'k': len(points), 'prefix': prefix, 'handoff': handoff,
                       'approach_approved': approved, 'reference': entry['decision']})
        approved = approved or bool(entry['decision'].get('approve_approach'))
    return points


def decision_row(k, record):
    return {'k': k, 'phase': record['phase'], 'action': record['action'], 'interaction': record['interaction'],
            'approve_approach': record['approve_approach'], 'fact_ids': record['fact_ids'],
            'message_words': words(record['message'])}


class ReplaySession:
    """What decide() needs from EpisodeSession: an event log and an output directory."""

    def __init__(self, output, episode_id):
        self.output, self.episode_id, self.sequence = output, episode_id, 0

    def event(self, kind, payload):
        append(self.output / 'events.jsonl', {'sequence': self.sequence, 'episode_id': self.episode_id,
                                              'time': time.time(), 'type': kind, 'payload': payload})
        self.sequence += 1


def latest_finished(run):
    latest = {}
    for path in sorted((run / 'finished').glob('*.json')):
        job = read(path)
        if not job.get('result') or not Path(job['result']).exists():
            continue
        key = (job['arm'], job['id'])
        if key not in latest or job.get('attempt', 1) >= latest[key].get('attempt', 1):
            latest[key] = job
    return latest


def load_reference(run, task, job):
    case = Path(job['result']).parent
    reference = {'case': str(case), 'status': job.get('status')}
    if task['kind'] == 'sciconv':
        events = jsonl(case / 'controller/events.jsonl')
        reference.update(kind='sciconv', episode_file=case / 'controller/episode.private.json',
                         questions=[e['payload']['question'] for e in events if e['type'] == 'researcher_question'],
                         replies=[e['payload']['answer'] for e in events if e['type'] == 'researcher_reply'])
    elif task['kind'] == 'python':
        private = case / 'controller'
        reference.update(kind='active', points=decision_points(read(private / 'researcher_history.private.json'),
                                                               read(private / 'researcher_audit.private.json')),
                         episode=read(private / 'episode.private.json'))
    else:
        return None
    return reference


class Replay:
    def __init__(self, run, *, reference='persona_off', arms=None, budget_usd, dry_run=False, workers=4,
                 force=False, price_in=None, price_out=None, send=None, preflight_fn=preflight,
                 sciconv_root=None):
        if not 1 <= workers <= 32:
            raise ValueError('workers must be between 1 and 32')
        if arm_kind(reference) not in ELIGIBLE:
            raise ValueError('The reference arm must be a persona, twin, neutral or control arm')
        self.run, self.reference, self.force, self.dry_run, self.workers = Path(run), reference, force, dry_run, workers
        self.root = self.run / 'replay'
        self.manifest = read(self.run / 'manifest.json')
        known = list(dict.fromkeys(job['arm'] for job in self.manifest['jobs']))
        requested = known if arms is None else list(arms)
        if set(requested) - set(known) or reference not in known:
            raise ValueError('Unknown arm: ' + ', '.join(sorted((set(requested) | {reference}) - set(known))))
        self.skipped = [{'arm': arm, 'reason': f'{arm_kind(arm)} arm is not replayed'}
                        for arm in requested if arm_kind(arm) not in ELIGIBLE]
        self.arms = [reference] + [a for a in requested if a != reference and arm_kind(a) in ELIGIBLE]
        if not dry_run:
            self.root.mkdir(exist_ok=True)
        self.calls = Calls(None if dry_run else self.root / 'api_calls.jsonl', budget_usd, price_in=price_in,
                           price_out=price_out, send=dry_response if dry_run else send, dry_run=dry_run)
        self.preflight_fn, self.sciconv_root = preflight_fn, sciconv_root
        self.catalogs, self.repositories, self.lock = {}, {}, threading.Lock()

    def client(self, spec):
        supported = None
        if not self.dry_run:
            key = json.dumps(spec, sort_keys=True)
            with self.lock:
                if key not in self.catalogs:
                    self.catalogs[key] = self.preflight_fn({'researcher': spec})['researcher']
            supported = self.catalogs[key]['supported_parameters']
        return self.calls.guard(OpenRouterClient(**spec, role='researcher', record=self.calls.record,
                                                 supported_parameters=supported))

    def sciconv_repository(self, task):
        if self.sciconv_root is not None:
            return Path(self.sciconv_root)
        with self.lock:
            if task['prepared'] not in self.repositories:
                m = read(Path(task['prepared']) / 'pilot_manifest.json')
                adapter = load_adapter('sciconvbench', Path(m['source_root']), Path(m['source_manifest']))
                self.repositories[task['prepared']] = adapter.source.repository
            return self.repositories[task['prepared']]

    def replay_sciconv(self, arm, task, reference, out):
        config = read(self.run / 'configs' / arm / 'shared.json')
        collaboration = config.get('collaboration') or {}
        ep = Episode.model_validate(read(reference['episode_file']))
        profile = resolve_persona(config, ep)
        service = Service(self.client(config['models']['researcher']), **service_options(collaboration))
        service.prompt_options = sciconv_options(collaboration)
        if profile.enabled:
            service.persona_text = render_persona(profile)
        controller = out / 'controller'
        controller.mkdir(parents=True)
        shutil.copy2(reference['episode_file'], controller / 'episode.private.json')
        User = native_class(self.sciconv_repository(task), 'llm_user_interface.py', 'LLMUserInterface', service)
        user = User(service, ep.public.question, ep.researcher.facts[0].text, log_file=str(out / 'conversation_log.txt'))
        events = []

        def event(kind, payload):
            data = {'sequence': len(events), 'type': kind, 'time': time.time(), 'payload': payload}
            events.append(data)
            append(controller / 'events.jsonl', data)
        for question in reference['questions']:
            event('researcher_question', {'question': question})
            before = service.stats['total_calls'], service.stats['failed_calls']
            answer = user.answer_clarification_question(question)
            # The native class turns every error into a canned reply, so each answer must be exactly one
            # successful model call; a prompt-edit error raises before the call is counted.
            if service.stats['total_calls'] != before[0] + 1 or service.stats['failed_calls'] != before[1]:
                raise BudgetReached('Replay budget reached') if self.calls.stopped else RuntimeError(
                    'Native researcher answer was not one successful model call')
            event('researcher_reply', {'answer': answer})
        return {'persona': persona_record(profile), 'user_prompt_options': service.prompt_options,
                'questions': len(reference['questions'])}

    def active_researcher(self, arm, task, reference, output):
        config = read(self.run / 'configs' / arm / 'shared.json')
        collaboration = validate_collaboration(config.get('collaboration'))
        if collaboration is None:
            raise NotReplayable('arm config has no active-researcher collaboration')
        ep = Episode.model_validate(reference['episode'])
        profile = resolve_persona(config, ep)
        researcher = ActiveResearcher(ep, self.client(config['models']['researcher']), persona=profile,
                                      **config.get('researcher', {}), **active_options(collaboration))
        return researcher, ReplaySession(output, ep.id), collaboration['max_requests']

    def replay_active(self, arm, task, reference, out):
        rows, persona = [], None
        for point in reference['points']:
            k = point['k']
            output = out / f'k{k}'
            output.mkdir(parents=True)
            researcher, session, limit = self.active_researcher(arm, task, reference, output)
            persona = researcher.persona_metadata
            researcher.history = deepcopy(point['prefix'])
            researcher.approach_approved = point['approach_approved']
            self.calls.context.value = {'arm': arm, 'task': task['id'], 'k': k}
            try:
                decision = researcher.decide(session, deepcopy(point['handoff']), limit - k)
                rows.append(decision_row(k, {**decision.model_dump(mode='json'), 'phase': researcher.audit[-1]['decision']['phase']}))
            except ValueError as error:
                # A protocol or format rejection is this arm's outcome at k, not an infrastructure failure.
                rows.append({'k': k, 'phase': point['reference']['phase'], 'error': f'{type(error).__name__}: {error}'})
        for row in rows:
            append(out / 'decisions.jsonl', row)
        if not rows:
            (out / 'decisions.jsonl').touch()
        return {'persona': persona, 'decision_points': len(rows)}

    def unit(self, arm, task, reference):
        final = self.root / arm / task['slug']
        if final.exists() and not self.force:
            return {'status': 'existing'}
        if self.calls.stopped:
            return {'status': 'budget_stopped'}
        scratch = None
        if self.dry_run:
            scratch = tempfile.TemporaryDirectory(prefix='replay-dry-')
            out = Path(scratch.name) / 'unit'
        else:
            out = final.with_name(task['slug'] + '.partial')
            if out.exists():
                shutil.rmtree(out)
        out.mkdir(parents=True)
        self.calls.context.value = {'arm': arm, 'task': task['id']}
        try:
            info = (self.replay_sciconv if reference['kind'] == 'sciconv' else self.replay_active)(arm, task, reference, out)
        except BudgetReached:
            return {'status': 'budget_stopped'}
        except NotReplayable as error:
            return {'status': 'skipped', 'reason': str(error)}
        except Exception as error:
            return {'status': 'failed', 'error': f'{type(error).__name__}: {error}'}
        finally:
            if scratch is not None:
                scratch.cleanup()
        if self.dry_run:
            return {'status': 'dry_run'}
        write(out / 'replay.json', {'arm': arm, 'arm_kind': arm_kind(arm), 'task': task['id'],
                                    'benchmark': task['benchmark'], 'reference_arm': self.reference,
                                    'reference_case': reference['case'], 'reference_status': reference['status'], **info})
        if final.exists():
            shutil.rmtree(final)
        out.rename(final)
        return {'status': 'completed'}

    def execute(self):
        finished = latest_finished(self.run)
        references, units = {}, []
        for task in self.manifest['tasks']:
            if task['kind'] == 'exp':
                self.skipped.append({'task': task['id'], 'reason': 'not replayed: ExpBench rebuilds its researcher '
                                     'through expbench.collaboration.initialize; not covered'})
                continue
            job = finished.get((self.reference, task['id']))
            if job is None:
                self.skipped.append({'task': task['id'], 'reason': 'no finished reference episode'})
                continue
            reference = load_reference(self.run, task, job)
            if reference is None:
                self.skipped.append({'task': task['id'], 'reason': f"{task['kind']} tasks have no replayable researcher"})
                continue
            references[task['id']] = reference
            units += [(arm, task) for arm in self.arms]
        outcomes = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(self.unit, arm, task, references[task['id']]): (arm, task) for arm, task in units}
            for future in as_completed(futures):
                if future.cancelled():
                    continue
                arm, task = futures[future]
                outcomes.append({'arm': arm, 'task': task['id'], **future.result()})
                if self.calls.stopped:
                    for pending in futures:
                        pending.cancel()
        for future, (arm, task) in futures.items():
            if future.cancelled():
                outcomes.append({'arm': arm, 'task': task['id'], 'status': 'budget_stopped'})
        if self.dry_run:
            return {'dry_run': True, 'units': len(outcomes), 'calls': self.calls.calls,
                    'prompt_tokens_estimate': self.calls.prompt_tokens,
                    'failed': [o for o in outcomes if o['status'] == 'failed'],
                    'note': 'Prompt tokens are characters/4 with placeholder replies; output tokens are not estimated.'}
        summary = summarize(self.root, self.manifest['tasks'], references, self.reference, self.arms)
        summary.update(budget_usd=self.calls.budget, spent_usd=self.calls.spent, calls=self.calls.calls,
                       budget_stopped=self.calls.stopped, skipped=self.skipped,
                       units={s: sum(o['status'] == s for o in outcomes) for s in sorted({o['status'] for o in outcomes})},
                       problems=[o for o in outcomes if o['status'] in ('failed', 'skipped')])
        write(self.root / 'summary.json', summary)
        (self.root / 'REPLAY.md').write_text(markdown(summary))
        return summary


def mean(values):
    return sum(values) / len(values) if values else None


def sciconv_metrics(replies):
    return {'replies': len(replies), 'mean_reply_words': mean([words(r) for r in replies])}


def active_metrics(rows):
    valid = [r for r in rows if 'error' not in r]
    approach = [r for r in valid if r['phase'] == 'approach_review']
    result = [r for r in valid if r['phase'] == 'result_review']
    return {'decisions': len(valid), 'errors': len(rows) - len(valid),
            'mean_reply_words': mean([r['message_words'] for r in valid]),
            'approve_rate_at_approach_review': mean([float(r['approve_approach']) for r in approach]),
            'stop_rate_at_result_review': mean([float(r['action'] == 'stop') for r in result]),
            'mean_fact_ids_per_decision': mean([len(r['fact_ids']) for r in valid])}


def delta(a, b):
    return {k: None if a[k] is None or b[k] is None else a[k] - b[k] for k in a}


def summarize(root, tasks, references, reference_arm, arms):
    benchmarks = {}
    for benchmark in sorted({t['benchmark'] for t in tasks if t['id'] in references}):
        chosen = [t for t in tasks if t['benchmark'] == benchmark and t['id'] in references]
        kind = references[chosen[0]['id']]['kind']

        def observed(arm, task):
            directory = root / arm / task['slug']
            if not (directory / 'replay.json').exists():
                return None
            if kind == 'sciconv':
                return [e['payload']['answer'] for e in jsonl(directory / 'controller/events.jsonl')
                        if e['type'] == 'researcher_reply']
            return jsonl(directory / 'decisions.jsonl')
        metric = sciconv_metrics if kind == 'sciconv' else active_metrics
        data = {arm: {t['id']: observed(arm, t) for t in chosen} for arm in arms}
        data = {arm: {k: v for k, v in rows.items() if v is not None} for arm, rows in data.items()}
        base = data[reference_arm]
        entry = {'kind': kind, 'arms': {}}
        for arm in arms:
            common = sorted(set(data[arm]) & set(base))
            if not common:
                continue
            values = metric([x for t in common for x in data[arm][t]])
            baseline = metric([x for t in common for x in base[t]])
            entry['arms'][arm] = {'arm_kind': arm_kind(arm), 'tasks': len(common), **values,
                                  'delta_vs_reference_replay': delta(values, baseline)}
        if base:
            if kind == 'sciconv':
                original = [r for t in base for r in references[t]['replies']]
            else:
                original = [decision_row(p['k'], p['reference']) for t in base for p in references[t]['points']]
            entry['reference_original'] = metric(original)
            entry['reference_self_replay_minus_original'] = delta(metric([x for t in base for x in base[t]]),
                                                                  entry['reference_original'])
        benchmarks[benchmark] = entry
    return {'reference_arm': reference_arm, 'benchmarks': benchmarks}


def fmt(value):
    return '—' if value is None else f'{value:+.3f}' if isinstance(value, float) else str(value)


def markdown(summary):
    ref = summary['reference_arm']
    lines = ['# Fixed-agent researcher replay', '',
             f'Every arm receives the agent messages of the `{ref}` episode; the agent never reacts to the arm, '
             'so differences are in what the researcher says back, not in the path the agent took.', '',
             '- SciConv: each arm answers the reference questions in order; its own earlier replies form its history.',
             '- Active researcher: each point is a one-step counterfactual with the reference agent\'s messages: the arm '
             'sees the reference history and handoff up to decision k and makes one decision. Points are independent.',
             f'- Differences are arm minus the `{ref}` self-replay on shared tasks. '
             f'`{ref}` self-replay minus its original episode is the sampling-noise baseline.', '',
             f"Spent ${summary['spent_usd']:.4f} of ${summary['budget_usd']} over {summary['calls']} calls"
             + (' (stopped at budget).' if summary['budget_stopped'] else '.'), '']
    for benchmark, entry in summary['benchmarks'].items():
        counts = ['replies'] if entry['kind'] == 'sciconv' else ['decisions', 'errors']
        shown = (['mean_reply_words'] if entry['kind'] == 'sciconv' else
                 ['mean_reply_words', 'approve_rate_at_approach_review', 'stop_rate_at_result_review',
                  'mean_fact_ids_per_decision'])
        keys = counts + shown
        lines += [f'## {benchmark}', '', '| Arm | Kind | Tasks | ' + ' | '.join(keys) + ' | Δ ' + ' | Δ '.join(shown) + ' |',
                  '|' + '---|' * (3 + len(keys) + len(shown))]
        for arm, row in entry['arms'].items():
            lines.append(f"| {arm} | {row['arm_kind']} | {row['tasks']} | " + ' | '.join(fmt(row[k]) for k in keys)
                         + ' | ' + ' | '.join(fmt(row['delta_vs_reference_replay'][k]) for k in shown) + ' |')
        if 'reference_original' in entry:
            noise = entry['reference_self_replay_minus_original']
            lines += ['', f'Noise baseline (`{ref}` self-replay minus original): '
                      + ', '.join(f'{k} {fmt(noise[k])}' for k in shown), '']
        else:
            lines.append('')
    if summary['skipped']:
        lines += ['## Skipped', ''] + [f"- {s.get('arm') or s.get('task')}: {s['reason']}" for s in summary['skipped']]
    if summary['problems']:
        lines += ['', '## Not replayed', ''] + [f"- {p['arm']} / {p['task']}: {p.get('error') or p.get('reason')}"
                                               for p in summary['problems']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True, help='Output directory of run_persona_benchmarks.py')
    parser.add_argument('--reference', default='persona_off')
    parser.add_argument('--arms', nargs='+', help='Default: every persona, twin, neutral and control arm')
    parser.add_argument('--budget-usd', type=float, required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--force', action='store_true', help='Redo arm×task replays that already exist')
    parser.add_argument('--price-in', type=float, help='USD per million prompt tokens when a response lacks usage.cost')
    parser.add_argument('--price-out', type=float, help='USD per million completion tokens when a response lacks usage.cost')
    args = parser.parse_args()
    if not args.dry_run:
        load_env(project_root() / '.env')
    result = Replay(args.run.resolve(), reference=args.reference, arms=args.arms, budget_usd=args.budget_usd,
                    dry_run=args.dry_run, workers=args.workers, force=args.force,
                    price_in=args.price_in, price_out=args.price_out).execute()
    print(json.dumps(result if args.dry_run else {k: result[k] for k in ('spent_usd', 'calls', 'budget_stopped', 'units')}, indent=2))


if __name__ == '__main__':
    main()
