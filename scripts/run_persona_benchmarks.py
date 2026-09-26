#!/usr/bin/env python3
"""Run paired action-persona episodes through the five retained benchmarks.

One task per subprocess preserves SDK/global-state isolation. Resource slots
limit concurrency without changing any task's execution budget or protocol.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import tokenize
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / '.venv/bin/python')


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def build(output):
    from personasciencebench.persona import Persona, persona_record
    selections = ROOT / 'data/persona_case_study/action_selection_v1/selected.jsonl'
    diagnostic = ROOT / 'runs/action-persona-case-study-20260926/results.jsonl'
    qualified = sorted(r['candidate_id'] for r in jsonl(diagnostic) if r['prominent_behavioral_effect'])
    included = set(random.Random(20260930).sample(qualified, 30))
    profiles = {'persona_off': {'enabled': False}}
    for row in jsonl(selections):
        if row['candidate_id'] in included:
            profiles[row['candidate_id']] = {'enabled': True, 'id': row['candidate_id'],
                'version': 'action-persona-1.0', 'action_rules': [r['instruction'] for r in row['rules'] if r['directional']]}
    if len(profiles) != 31:
        raise ValueError('Expected 30 diagnostic-qualified profiles and one off control')
    shared = read(ROOT / 'configs/conversion-v2-two.json')
    shared['pilot_cases_per_benchmark'] = 1
    exp = tomllib.loads((ROOT / 'configs/expbench/conversion-v2-two.toml').read_text())
    tasks = []
    for folder, kind in [('conversion-v2-two-python', 'python'),
                         ('conversion-v2-two-asi-ready', 'python'),
                         ('conversion-v2-two-sciconv-ready', 'sciconv')]:
        manifest = read(ROOT / 'prepared' / folder / 'pilot_manifest.json')
        for record in manifest['cases']:
            if record['benchmark'] in {'scienceagentbench', 'terminal_bench_science'}:
                continue
            tid = record['episode_id']
            slug = hashlib.sha256(tid.encode()).hexdigest()[:12]
            prepared = output / 'inputs' / slug
            write(prepared / 'pilot_manifest.json', {**manifest, 'cases': [record]})
            tasks.append({'id': tid, 'slug': slug, 'kind': kind,
                          'benchmark': record['benchmark'], 'prepared': str(prepared)})
    for tid in ['neurips2024/94328/5', 'neurips2024/97649/0']:
        tasks.append({'id': 'expbench:' + tid, 'slug': hashlib.sha256(tid.encode()).hexdigest()[:12],
                      'kind': 'exp', 'benchmark': 'expbench', 'task_id': tid})
    assert len(tasks) == 10 and len({t['id'] for t in tasks}) == 10
    for arm, profile in profiles.items():
        write(output / 'configs' / arm / 'shared.json', {**deepcopy(shared), 'persona': profile})
        write(output / 'configs' / arm / 'exp.json', {**deepcopy(exp), 'persona': profile})
        write(output / 'configs' / arm / 'persona.private.json', persona_record(Persona.model_validate(profile)))
    jobs = []
    for arm in profiles:
        arm_tasks = list(tasks)
        random.Random(arm).shuffle(arm_tasks)
        for task in arm_tasks:
            jobs.append({**task, 'arm': arm, 'key': arm + '-' + task['slug']})
    hashes = {}
    for path in [selections, diagnostic, *sorted((ROOT / 'src').rglob('*.py'))]:
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {'version': 'action-persona-benchmark-v1', 'profiles': len(profiles)-1,
        'tasks': tasks, 'jobs': jobs, 'source_sha256': hashes,
        'selection': '30 profiles sampled with seed 20260930 from the 73 diagnostic-qualified profiles; exploratory enriched cohort, not population estimate',
        'controls': 'One fresh persona-off run per task, reused across profile contrasts; not independent replicates',
        'resources': {'logical_cpus': os.cpu_count(), 'parallel': 6, 'python_slots': 2},
        'discarded_benchmarks': {
            'scienceagentbench': 'retired from persona experiments because assets and evaluator workspaces are too heavy',
            'terminal_bench_science': 'retired from persona experiments because Docker execution and retained traces are too heavy',
        },
        'injection': 'Only private simulator identity; existing facts, actor inputs, review policy and graders unchanged'}
    write(output / 'manifest.json', manifest)
    return manifest


def command(output, job):
    result = output / 'episodes' / job['key']
    config = output / 'configs' / job['arm'] / 'shared.json'
    common = ['--output', str(result), '--config', str(config), '--parallel', '1']
    if job['kind'] == 'python':
        return [PYTHON, '-m', 'personasciencebench', 'run', '--prepared', job['prepared'],
                '--benchmarks', job['benchmark'], '--actor-python', str(ROOT / '.actor-venv'), *common]
    if job['kind'] == 'terminal':
        return [PYTHON, '-m', 'personasciencebench.terminal_runner', '--prepared', job['prepared'],
                '--verifier-backend', 'native-docker', *common]
    if job['kind'] == 'sciconv':
        return [PYTHON, '-m', 'personasciencebench.sciconv_runner', '--prepared', job['prepared'], *common]
    return [PYTHON, '-m', 'expbench.realistic', 'run', '--mode', 'live', '--task', job['task_id'],
            '--tasks', str(ROOT / 'data/conversion-v2-exp/tasks.jsonl'), '--env-file', str(ROOT / '.env'),
            '--config', str(config.with_name('exp.json')), '--output', str(result), '--parallel', '1']


def execute(output, job):
    started = time.monotonic()
    env = dict(os.environ, PERSONASCIENCEBENCH_BWRAP=str(ROOT / 'external/runtime/bubblewrap-local/usr/bin/bwrap'))
    log = output / 'logs' / (job['key'] + '.log')
    log.parent.mkdir(exist_ok=True)
    with log.open('w') as stream:
        proc = subprocess.run(command(output, job), cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    result_dir = output / 'episodes' / job['key']
    records = list(result_dir.glob('*/result.json'))
    record = read(records[0]) if len(records) == 1 else {'status': 'launch_error'}
    result = {**job, 'returncode': proc.returncode, 'elapsed_seconds': time.monotonic()-started,
              'status': record['status'], 'result': str(records[0]) if len(records) == 1 else None}
    # Render existing complete traces; preserve raw controller/API records.
    if records:
        with log.open('a') as stream:
            rendering = subprocess.run([PYTHON, str(ROOT / 'scripts/render_run_traces.py'), str(result_dir)],
                                      cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        result['trace_render_returncode'] = rendering.returncode
    write(output / 'finished' / (job['key'] + '.json'), result)
    return result


def code_behavior(case, events):
    """Measure sealed Python deliverables only; never execute generated code."""
    submission = case / 'controller/submission.json'
    if not submission.exists():
        return {}
    sources = {}
    for event in events:
        if event['type'] == 'agent_handoff':
            sources.update(event['payload'].get('artifacts', {}))
    counts = Counter()
    for name, raw in read(submission).get('artifacts', {}).items():
        if not str(sources.get(name, '')).endswith('.py'):
            continue
        path = Path(raw)
        if not path.resolve().is_relative_to((case/'controller/submitted_artifacts').resolve()):
            continue
        if path.stat().st_size > 1_000_000:
            continue
        try:
            source = path.read_text()
            tree = ast.parse(source)
            comments = [t for t in tokenize.generate_tokens(io.StringIO(source).readline)
                        if t.type == tokenize.COMMENT]
        except (SyntaxError, UnicodeError, tokenize.TokenError):
            continue
        counts['submitted_python_files'] += 1
        counts['code_nonblank_lines'] += sum(bool(line.strip()) for line in source.splitlines())
        counts['code_comment_lines'] += len(comments)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                counts['code_functions'] += 1
                counts['code_test_functions'] += node.name.startswith('test_')
                counts['code_typed_functions'] += bool(node.returns or any(a.annotation for a in node.args.args))
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                counts['code_docstrings'] += bool(ast.get_docstring(node))
            counts['code_assertions'] += isinstance(node, ast.Assert)
    if not counts['submitted_python_files']:
        return {}
    fields = ['submitted_python_files', 'code_nonblank_lines', 'code_comment_lines',
              'code_functions', 'code_test_functions', 'code_typed_functions', 'code_docstrings', 'code_assertions']
    return {key: counts[key] for key in fields}


def report(output):
    manifest = read(output / 'manifest.json')
    results = [read(p) for p in sorted((output / 'finished').glob('*.json'))]
    attempts = list(results)
    latest = {}
    for result in sorted(results, key=lambda r: r.get('attempt', 1)):
        latest[(result['arm'], result['id'])] = result
    results = list(latest.values())
    rows = []
    for job in results:
        record = read(job['result']) if job['result'] and Path(job['result']).exists() else {}
        case = Path(job['result']).parent if job['result'] else None
        events = []
        if case:
            event_path = case / 'controller/events.jsonl'
            events = jsonl(event_path if event_path.exists() else case / 'events.jsonl')
        counts = Counter(e['type'] for e in events)
        stages = Counter(e['payload'].get('stage') for e in events if e['type'] == 'agent_handoff')
        decisions = [e['payload'] for e in events if e['type'] == 'researcher_decision']
        metrics = record.get('evaluation', {}).get('metrics', {})
        if job['kind'] == 'exp':
            metrics = {k: v for k, v in (record.get('initial') or {}).items()
                       if k in {'coverage_mean', 'gated_coverage_mean'}}
        behavior = {'exchanges': counts['researcher_reply'] if job['kind']=='sciconv' else counts['agent_handoff'],
                    'plan_handoffs': stages['plan'], 'result_handoffs': stages['result'],
                    'revision_requests': sum(d.get('phase')=='result_review' and d.get('action')=='continue' for d in decisions),
                    'researcher_words': sum(len(str(d.get('message', '')).split()) for d in decisions),
                    'actor_calls': record.get('actor_calls', record.get('actor', {}).get('actor_calls')),
                    'execution_calls': record.get('actor', {}).get('execution_calls'),
                    'execution_successes': record.get('actor', {}).get('execution_successes'),
                    'researcher_format_errors': counts['researcher_format_error'],
                    'elapsed_seconds': job['elapsed_seconds']}
        api = []
        if case:
            api = (jsonl(case / 'controller/api_calls.private.jsonl')
                   or jsonl(case / 'api_calls.private.jsonl') or jsonl(case / 'api_calls.jsonl'))
        usages = [a.get('usage') or a.get('response', {}).get('usage', {}) for a in api]
        behavior['prompt_tokens'] = sum(u.get('prompt_tokens', 0) for u in usages)
        behavior['completion_tokens'] = sum(u.get('completion_tokens', 0) for u in usages)
        costs = [u['cost'] for u in usages if isinstance(u.get('cost'), (int, float))]
        behavior['reported_cost_usd'] = sum(costs) if costs else record.get('budget_charge_usd')
        submitted = record.get('actor', {}).get('submitted', record.get('initial_submitted'))
        if job['kind'] == 'sciconv' and record.get('status') == 'scored':
            submitted = True
        behavior['submission_produced'] = int(submitted) if isinstance(submitted, bool) else None
        if case:
            behavior.update(code_behavior(case, events))
        rows.append({'arm': job['arm'], 'task': job['id'], 'benchmark': job['benchmark'],
                     'status': job['status'], 'metrics': metrics, 'behavior': behavior,
                     'trace': str(case / 'trace.md') if case else None})
    controls = {r['task']: r for r in rows if r['arm']=='persona_off'}
    comparisons = []
    for row in rows:
        if row['arm']=='persona_off' or row['task'] not in controls:
            continue
        base = controls[row['task']]
        diff = {}
        for group in ['metrics', 'behavior']:
            diff[group] = {k: v-base[group][k] for k, v in row[group].items()
                           if isinstance(v, (int, float)) and not isinstance(v, bool)
                           and isinstance(base[group].get(k), (int, float))}
        comparisons.append({'arm': row['arm'], 'task': row['task'], 'benchmark': row['benchmark'],
                            'persona_status': row['status'], 'control_status': base['status'], 'delta': diff})
    write(output / 'comparison.json', {'episodes': rows, 'paired_differences': comparisons, 'attempts': attempts})
    lines = ['# Persona benchmark comparison', '',
             f"Completed records: {len(rows)} / {len(manifest['jobs'])}. Statuses: {dict(Counter(r['status'] for r in rows))}.", '',
             '30 diagnostically enriched profiles; two fixed tasks for each of five retained benchmarks; one shared off control per task.',
             'ScienceAgentBench and Terminal-Bench-Science were discarded after pilot execution because their storage and execution requirements were too heavy for this persona study.',
             'Paired differences are descriptive. Shared controls and repeated tasks are not independent observations.', '',
             'Concurrency was adjusted to observed host capacity while per-episode limits stayed fixed. Elapsed time is an operational diagnostic, not an isolated persona effect.', '',
             '| Benchmark | Persona records | Off records | Paired mean metric changes | Mean exchange change |',
             '|---|---:|---:|---|---:|']
    for benchmark in sorted({r['benchmark'] for r in rows}):
        selected = [r for r in rows if r['benchmark']==benchmark]
        pairs = [p for p in comparisons if p['benchmark']==benchmark]
        metric_values = defaultdict(list)
        for pair in pairs:
            for key, value in pair['delta']['metrics'].items():
                metric_values[key].append(value)
        mean_metrics = '; '.join(f'{k}: {sum(v)/len(v):+.4f} (n={len(v)})' for k,v in sorted(metric_values.items()))
        exchanges = [p['delta']['behavior']['exchanges'] for p in pairs
                     if p['persona_status'] in {'scored','completed','missing_submission'}
                     and p['control_status'] in {'scored','completed','missing_submission'}]
        exchange_text = f'{sum(exchanges)/len(exchanges):+.2f}' if exchanges else 'pending'
        lines.append(f"| {benchmark} | {sum(r['arm']!='persona_off' for r in selected)} | {sum(r['arm']=='persona_off' for r in selected)} | {mean_metrics or 'pending'} | {exchange_text} |")
    primary = {'asibench': 'score', 'bixbench': 'grade', 'discoverybench': 'final_score',
               'expbench': 'gated_coverage_mean', 'sciconvbench': 'FRR'}
    lines += ['', '## Native score distributions', '',
              'Each entry is a profile/task contrast with its shared off control. Higher/lower counts describe observed outcomes, not statistically significant effects.', '',
              '| Benchmark | Metric | Higher / equal / lower | Minimum delta | Maximum delta |', '|---|---|---:|---:|---:|']
    for benchmark, metric in sorted(primary.items()):
        values = [p['delta']['metrics'][metric] for p in comparisons
                  if p['benchmark']==benchmark and metric in p['delta']['metrics']]
        if values:
            counts = f'{sum(v>0 for v in values)} / {sum(v==0 for v in values)} / {sum(v<0 for v in values)}'
            lines.append(f'| {benchmark} | {metric} | {counts} | {min(values):+.4f} | {max(values):+.4f} |')
    lines += ['', '## Behavioral differences', '',
              'Mean persona-minus-control changes among completed pairs. Code measures cover only sealed Python deliverables present in both arms; they are descriptive proxies, not persona-fidelity scores.', '',
              '| Benchmark | Measure | Mean change | Paired observations |', '|---|---|---:|---:|']
    behavior_groups = defaultdict(list)
    for pair in comparisons:
        if pair['persona_status'] not in {'scored', 'completed', 'missing_submission'} or pair['control_status'] not in {'scored', 'completed', 'missing_submission'}:
            continue
        for key, value in pair['delta']['behavior'].items():
            behavior_groups[(pair['benchmark'], key)].append(value)
    for (benchmark, key), values in sorted(behavior_groups.items()):
        lines.append(f'| {benchmark} | {key} | {sum(values)/len(values):+.4f} | {len(values)} |')
    lines += ['', '## Results by task', '',
              'Missing submissions and infrastructure errors remain explicit. Native score changes are computed only where both arms have a score; no missing result is imputed as zero unless the native runner already applies that policy.', '',
              '| Task | Control status | Persona status counts | Native score changes |', '|---|---|---|---|']
    for task in sorted({r['task'] for r in rows}):
        task_rows = [r for r in rows if r['task']==task and r['arm']!='persona_off']
        task_values = defaultdict(list)
        for pair in comparisons:
            if pair['task']==task:
                for key, value in pair['delta']['metrics'].items():
                    task_values[key].append(value)
        changes = '; '.join(f'{k}: {sum(v)/len(v):+.4f} (n={len(v)})' for k,v in sorted(task_values.items()))
        control_status = controls.get(task, {}).get('status', 'pending')
        lines.append(f"| {task} | {control_status} | {dict(Counter(r['status'] for r in task_rows))} | {changes or 'unavailable'} |")
    lines += ['', '## Individual episodes', '', '| Profile | Task | Status | Trace |', '|---|---|---|---|']
    for row in rows:
        trace = os.path.relpath(row['trace'], output) if row['trace'] else None
        lines.append(f"| {row['arm']} | {row['task']} | {row['status']} | " + (f'[trace]({trace})' if trace else 'unavailable') + ' |')
    (output / 'REPORT.md').write_text('\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report-only', action='store_true')
    parser.add_argument('--retry-errors', action='store_true',
                        help='Retry completed infrastructure failures once; retain every original attempt')
    parser.add_argument('--parallel', type=int, default=6)
    parser.add_argument('--python-slots', type=int, default=2)
    parser.add_argument('--terminal-slots', type=int, default=1)
    parser.add_argument('--after-pid', type=int, help='Wait for an earlier draining scheduler before resuming')
    args = parser.parse_args()
    if args.after_pid:
        previous = Path('/proc') / str(args.after_pid) / 'cmdline'
        while previous.exists():
            try:
                if b'run_persona_benchmarks.py' not in previous.read_bytes():
                    break
            except FileNotFoundError:
                break
            time.sleep(2)
    if not 1 <= args.parallel <= 12 or not 1 <= args.python_slots <= 6 or not 1 <= args.terminal_slots <= 6:
        raise ValueError('Limits: 1–12 total, 1–6 Python, 1–6 Terminal workers')
    output = args.output.resolve()
    if args.report_only:
        report(output)
        return
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(0o700)
    manifest = read(output/'manifest.json') if (output/'manifest.json').exists() else build(output)
    pending = [j for j in manifest['jobs'] if not (output/'finished'/(j['key']+'.json')).exists()]
    completed_original = len(manifest['jobs']) - len(pending)
    if args.retry_errors:
        retries = []
        for job in manifest['jobs']:
            if not (output/'finished'/(job['key']+'.json')).exists():
                continue
            prior = read(output/'finished'/(job['key']+'.json'))
            if prior['status'] not in {'infrastructure_error', 'runtime_error', 'launch_error'}:
                continue
            retry = {**job, 'key': job['key']+'-retry2', 'attempt': 2}
            if not (output/'finished'/(retry['key']+'.json')).exists():
                retries.append(retry)
        pending = retries + pending
        write(output/('recovery_manifest-'+str(time.time_ns())+'.json'), {'jobs': retries, 'reason': 'Infrastructure failures only; scientific outcomes never trigger retry',
            'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((ROOT/'src').rglob('*.py'))}})
    for job in pending:
        if (output/'episodes'/job['key']).exists():
            abandoned = output / 'aborted-after-restart'
            abandoned.mkdir(exist_ok=True)
            source = output / 'episodes' / job['key']
            target = abandoned / job['key']
            if target.exists():
                target = abandoned / (job['key'] + '-' + str(time.time_ns()))
            source.rename(target)
    active = {}
    write(output / ('scheduler-'+str(time.time_ns())+'.json'),
          {'parallel': args.parallel, 'python_slots': args.python_slots, 'terminal_slots': args.terminal_slots,
           'minimum_available_memory_gib': 4, 'jobs_pending': len(pending)})
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        while pending or active:
            control = output / 'scheduler.private.json'
            slots = read(control) if control.exists() else {}
            python_slots = slots.get('python_slots', args.python_slots)
            terminal_slots = slots.get('terminal_slots', args.terminal_slots)
            if not 1 <= python_slots <= 6 or not 1 <= terminal_slots <= 6:
                raise ValueError('Live worker limits must be between one and six')
            counts = Counter(j['kind'] for j in active.values())
            for job in list(pending):
                if len(active)>=args.parallel:
                    break
                available = next(int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()
                                 if line.startswith('MemAvailable:'))
                if available < 4*1024*1024:
                    break
                if job['kind']=='python' and counts['python']>=python_slots:
                    continue
                if job['kind']=='terminal' and counts['terminal']>=terminal_slots:
                    continue
                pending.remove(job)
                active[pool.submit(execute, output, job)] = job
                counts[job['kind']] += 1
            done, _ = wait(active, timeout=30, return_when=FIRST_COMPLETED)
            if not active and pending:
                time.sleep(5)
            for future in done:
                future.result()
                if active[future].get('attempt', 1) == 1:
                    completed_original += 1
                del active[future]
            write(output/'progress.json', {'pending': len(pending), 'active': list(active.values()),
                   'completed': completed_original, 'updated_unix': time.time(),
                   'python_slots': python_slots, 'terminal_slots': terminal_slots})
    report(output)


if __name__ == '__main__':
    main()
