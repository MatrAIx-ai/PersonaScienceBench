#!/usr/bin/env python3
"""Run paired full-persona episodes through the five retained benchmarks.

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
import statistics
import subprocess
import sys
import time
import tokenize
import tomllib

from personasciencebench.arms import CEILING, CONTROL, FLOOR, PERSONA, TWIN, arm_kind, is_control, twin_of, TWIN_SUFFIX

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


def control_summary(rows):
    """Per-key mean and sample SD (None below two values) over numeric control metrics and behavior."""
    means, sds = {}, {}
    for group in ['metrics', 'behavior']:
        values = defaultdict(list)
        for row in rows:
            for k, v in row[group].items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    values[k].append(v)
        means[group] = {k: sum(v)/len(v) for k, v in values.items()}
        sds[group] = {k: statistics.stdev(v) if len(v) > 1 else None for k, v in values.items()}
    return means, sds


def reorder_bullets(text, seed):
    """Shuffle '- ' bullet lines within each '#' section; headers and all other lines keep their positions."""
    rng = random.Random(seed)
    lines = text.split('\n')
    sections = [[]]
    for i, line in enumerate(lines):
        if line.startswith('#'):
            sections.append([])
        elif line.startswith('- '):
            sections[-1].append(i)
    for positions in sections:
        bullets = [lines[i] for i in positions]
        rng.shuffle(bullets)
        for i, bullet in zip(positions, bullets):
            lines[i] = bullet
    return '\n'.join(lines)


# Scripted researcher policy of each bound arm (CollaborationConfig.researcher_policy).
BOUND_POLICIES = {'floor_mute': 'mute', 'ceiling_oracle': 'oracle'}


def build(output, control_reps=1, twins=0, neutral_arms=False, bound_arms=False, truthful_history=False):
    from personasciencebench.persona import Persona, persona_record
    cohort = ROOT / 'data/persona_case_study/full_persona_v2'
    cohort_manifest = read(cohort / 'manifest.json')
    profiles = {'persona_off': {'enabled': False}}
    for rep in range(2, control_reps+1):
        profiles[f'persona_off_r{rep}'] = {'enabled': False}
    for row in cohort_manifest['profiles']:
        prompt = (cohort / row['prompt']).read_text()
        assert hashlib.sha256(prompt.encode()).hexdigest() == row['prompt_sha256']
        profiles[row['candidate_id']] = {'enabled': True, 'id': row['candidate_id'],
            'version': 'full-persona-v2', 'system_prompt': prompt}
    twin_sources = {}
    for source in random.Random(20260927).sample(sorted(r['candidate_id'] for r in cohort_manifest['profiles']), twins):
        prompt = profiles[source]['system_prompt']
        reordered = reorder_bullets(prompt, source)
        assert sorted(reordered.split('\n')) == sorted(prompt.split('\n')) and reordered != prompt, source
        arm = source + TWIN_SUFFIX
        profiles[arm] = {'enabled': True, 'id': arm, 'version': 'full-persona-v2', 'system_prompt': reordered}
        twin_sources[arm] = source
    if neutral_arms:
        for arm in ['neutral_a', 'neutral_b']:
            profiles[arm] = {'enabled': True, 'id': arm, 'version': 'neutral-v1',
                             'system_prompt': (ROOT / 'configs/persona_controls' / f'{arm}.txt').read_text()}
    if bound_arms:
        for arm in BOUND_POLICIES:
            profiles[arm] = {'enabled': False}
    kinds = Counter(arm_kind(arm) for arm in profiles)
    assert kinds[CONTROL] == control_reps and kinds[PERSONA] == 30
    shared = read(ROOT / 'configs/conversion-v2-two.json')
    shared['pilot_cases_per_benchmark'] = 1
    # full_persona_v2 settings, now as separate switches: general knowledge, persona-set style, volunteering (SciConv).
    shared['collaboration'].update(unrestricted_knowledge=True, embody_identity=True, volunteer_information=True)
    if truthful_history:
        shared['collaboration']['truthful_history'] = True
    shared['notes'] = ['Full MatrAIx profile in simulator system prompt; unrestricted general knowledge for all arms.',
        f'Five fixed tasks per benchmark; 30 personas and {control_reps} fresh shared baseline run(s) per task; native scoring unchanged.']
    shared.pop('actor_python_overrides', None)
    exp = tomllib.loads((ROOT / 'configs/expbench/conversion-v2-two.toml').read_text())
    exp['collaboration'].update(unrestricted_knowledge=True, embody_identity=True)
    if truthful_history:
        exp['collaboration']['truthful_history'] = True
    for config in [shared, exp]:
        for model in config['models'].values():
            assert model['model'] == 'openai/gpt-6-luna' and model['reasoning_effort'] == 'none'
    tasks = []
    prepared_manifest = read(ROOT / 'prepared/full-persona-v2-five/pilot_manifest.json')
    for record in prepared_manifest['cases']:
        assert record['assets_ready'], record['episode_id']
        tid = record['episode_id']
        slug = hashlib.sha256(tid.encode()).hexdigest()[:12]
        prepared = output / 'inputs' / slug
        write(prepared / 'pilot_manifest.json', {**prepared_manifest, 'cases': [record]})
        tasks.append({'id': tid, 'slug': slug, 'kind': 'sciconv' if record['benchmark']=='sciconvbench' else 'python',
                      'benchmark': record['benchmark'], 'prepared': str(prepared)})
    exp_rows = jsonl(ROOT / 'data/design_catalog/tasks.jsonl')
    random.Random(20260926).shuffle(exp_rows)
    papers = set()
    for row in exp_rows:
        tid = row['task_id']
        paper = tid.rsplit('/',1)[0]
        if paper in papers:
            continue
        papers.add(paper)
        tasks.append({'id': 'expbench:' + tid, 'slug': hashlib.sha256(tid.encode()).hexdigest()[:12],
                      'kind': 'exp', 'benchmark': 'expbench', 'task_id': tid})
        if len(papers)==5:
            break
    assert len(tasks) == 25 and len({t['id'] for t in tasks}) == 25
    assert set(Counter(t['benchmark'] for t in tasks).values()) == {5}
    for arm, profile in profiles.items():
        arm_shared = deepcopy(shared)
        if arm in BOUND_POLICIES:
            arm_shared['collaboration']['researcher_policy'] = BOUND_POLICIES[arm]
        write(output / 'configs' / arm / 'shared.json', {**arm_shared, 'persona': profile})
        write(output / 'configs' / arm / 'exp.json', {**deepcopy(exp), 'persona': profile})
        write(output / 'configs' / arm / 'persona.private.json', persona_record(Persona.model_validate(profile)))
    # Baselines start first; randomize the remaining work to interleave profiles.
    jobs = []
    for arm in profiles:
        arm_tasks = [t for t in tasks if not (arm in BOUND_POLICIES and t['kind'] == 'exp')]
        random.Random(arm).shuffle(arm_tasks)
        for task in arm_tasks:
            jobs.append({**task, 'arm': arm, 'key': arm + '-' + task['slug']})
    baseline = [j for j in jobs if is_control(j['arm'])]
    persona_jobs = [j for j in jobs if not is_control(j['arm'])]
    random.Random(20260926).shuffle(persona_jobs)
    jobs = baseline + persona_jobs
    hashes = {}
    for path in [cohort/'manifest.json', Path(__file__), *sorted((ROOT / 'src').rglob('*.py'))]:
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {'version': 'full-persona-benchmark-v2', 'profiles': 30,
        'tasks': tasks, 'jobs': jobs, 'source_sha256': hashes,
        'selection': cohort_manifest['selection'], 'persona_diversity': cohort_manifest['diversity'],
        'task_selection': 'Seed 20260926 shuffle of asset-ready catalogs with distinct studies; ASI three existing ready instances plus astronomy and biology public CPU instances; EXP five distinct papers.',
        'controls': (f'{control_reps} fresh persona-off runs per task; their mean is' if control_reps > 1 else 'One fresh persona-off run per task,')
            + ' shared across all 30 profile comparisons; not independent replicates'
            + ('. Reference arms (reordered twins, neutral identities, floor/ceiling researchers) calibrate noise and are never ranked'
               if len(profiles) > 30 + control_reps else ''),
        'injection': 'Exact full profile in simulator system prompt only; general knowledge allowed in both conditions; evaluator references remain private',
        'models': shared['models']}
    if twins:
        manifest['twins'] = twin_sources
    if bound_arms:
        manifest['bounds_skipped'] = {'expbench': 'ExpBench has no scripted researcher and rejects researcher_policy other than llm; floor/ceiling arms have no EXP jobs'}
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
            '--tasks', str(ROOT / 'data/design_catalog/tasks.jsonl'), '--env-file', str(ROOT / '.env'),
            '--config', str(config.with_name('exp.json')), '--output', str(result), '--parallel', '1']


def execute(output, job):
    started = time.monotonic()
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1', PERSONASCIENCEBENCH_BWRAP=str(ROOT / 'external/runtime/bubblewrap-local/usr/bin/bwrap'))
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


def spread(values):
    return {'mean': sum(values)/len(values), 'min': min(values), 'max': max(values), 'n': len(values)} if values else None


def noise_floor(rows, comparisons, primary):
    """Per benchmark primary metric: control SD, placebo contrasts, bound means and personas outside the placebo band."""
    result = {}
    for benchmark, metric in sorted(primary.items()):
        selected = [r for r in rows if r['benchmark'] == benchmark]
        if not selected:
            continue
        value = {(r['arm'], r['task']): r['metrics'][metric] for r in selected
                 if isinstance(r['metrics'].get(metric), (int, float)) and not isinstance(r['metrics'][metric], bool)}
        tasks = sorted({r['task'] for r in selected})
        arms = sorted({r['arm'] for r in selected})
        def contrast(a, b):
            return [value[a, t] - value[b, t] for t in tasks if (a, t) in value and (b, t) in value]
        sds = []
        for task in tasks:
            reps = [value[a, task] for a in arms if is_control(a) and (a, task) in value]
            if len(reps) > 1:
                sds.append(statistics.stdev(reps))
        twins = {arm: contrast(arm, twin_of(arm)) for arm in arms if arm_kind(arm) == TWIN}
        neutral = contrast('neutral_b', 'neutral_a')
        per_arm = [sum(v)/len(v) for v in [*twins.values(), neutral] if v]
        band = [min(per_arm), max(per_arm)] if per_arm else None
        deltas = defaultdict(list)
        for pair in comparisons:
            if pair['benchmark'] == benchmark and metric in pair['delta']['metrics']:
                deltas[pair['arm']].append(pair['delta']['metrics'][metric])
        means = [sum(v)/len(v) for v in deltas.values()]
        bound = lambda kind: [v for (a, _), v in value.items() if arm_kind(a) == kind]
        result[benchmark] = {'metric': metric,
            'control_sd': sum(sds)/len(sds) if sds else None, 'control_sd_tasks': len(sds),
            'twin_minus_source': spread([d for v in twins.values() for d in v]),
            'neutral_b_minus_a': spread(neutral),
            'floor_mean': spread(bound(FLOOR))['mean'] if bound(FLOOR) else None,
            'ceiling_mean': spread(bound(CEILING))['mean'] if bound(CEILING) else None,
            'placebo_band': band, 'personas': len(means),
            'personas_outside_band': sum(not band[0] <= m <= band[1] for m in means) if band else None}
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
            initial = record.get('initial') or {}
            metrics = {k: v for k, v in initial.items() if k in {'coverage_mean', 'gated_coverage_mean'}}
            if initial.get('monitor_passed') is not None:
                metrics['monitor_passed'] = int(initial['monitor_passed'])
        behavior = {'exchanges': counts['researcher_reply'] if job['kind']=='sciconv' else counts['agent_handoff'],
                    'plan_handoffs': stages['plan'], 'result_handoffs': stages['result'],
                    'revision_requests': sum(d.get('phase')=='result_review' and d.get('action')=='continue' for d in decisions),
                    'researcher_words': sum(len(str(e['payload'].get('answer', '')).split()) for e in events if e['type'] == 'researcher_reply')
                        if job['kind']=='sciconv' else sum(len(str(d.get('message', '')).split()) for d in decisions),
                    'approach_approved': None if job['kind']=='sciconv' else int(any(d.get('approve_approach') for d in decisions)),
                    'result_rejections': None if job['kind']=='sciconv' else counts['result_handoff_rejected'],
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
    controls = defaultdict(list)
    for r in rows:
        if is_control(r['arm']):
            controls[r['task']].append(r)
    summaries = {task: control_summary(group) for task, group in controls.items()}
    comparisons, references = [], []
    for row in rows:
        if is_control(row['arm']) or row['task'] not in controls:
            continue
        base, sd = summaries[row['task']]
        diff = {}
        for group in ['metrics', 'behavior']:
            diff[group] = {k: v-base[group][k] for k, v in row[group].items()
                           if isinstance(v, (int, float)) and not isinstance(v, bool) and k in base[group]}
        diff['control_sd'] = {group: {k: sd[group][k] for k in diff[group]} for group in ['metrics', 'behavior']}
        statuses = [c['status'] for c in controls[row['task']]]
        (comparisons if arm_kind(row['arm']) == PERSONA else references).append({'arm': row['arm'], 'task': row['task'], 'benchmark': row['benchmark'],
                            'persona_status': row['status'], 'n_controls': len(statuses),
                            'control_status': statuses[0] if len(set(statuses)) == 1 else 'mixed',
                            'control_statuses': statuses, 'delta': diff})
    control_counts = sorted(set(len(v) for v in controls.values()))
    control_text = ('no' if not control_counts else str(control_counts[0]) if len(control_counts) == 1
                    else f'{control_counts[0]}–{control_counts[-1]}')
    primary = {'asibench': 'score', 'bixbench': 'grade', 'discoverybench': 'final_score',
               'expbench': 'gated_coverage_mean', 'sciconvbench': 'FRR'}
    noise = noise_floor(rows, comparisons, primary)
    write(output / 'comparison.json', {'episodes': rows, 'paired_differences': comparisons,
                                       'reference_differences': references, 'noise_floor': noise, 'attempts': attempts})
    lines = ['# Persona benchmark comparison', '',
             f"Completed records: {len(rows)} / {len(manifest['jobs'])}. Statuses: {dict(Counter(r['status'] for r in rows))}.", '',
             f'30 source-balanced, behaviorally diverse full profiles; five fixed tasks for each of five benchmarks; {control_text} fresh shared off control run(s) per task; each persona is compared with the per-task control mean.',
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
        lines.append(f"| {benchmark} | {sum(arm_kind(r['arm']) == PERSONA for r in selected)} | {sum(is_control(r['arm']) for r in selected)} | {mean_metrics or 'pending'} | {exchange_text} |")
    lines += ['', '## Native score distributions', '',
              'Each entry is a profile/task contrast with the mean of its shared off control run(s). Higher/lower counts describe observed outcomes, not statistically significant effects.', '',
              '| Benchmark | Metric | Higher / equal / lower | Minimum delta | Maximum delta |', '|---|---|---:|---:|---:|']
    for benchmark, metric in sorted(primary.items()):
        values = [p['delta']['metrics'][metric] for p in comparisons
                  if p['benchmark']==benchmark and metric in p['delta']['metrics']]
        if values:
            counts = f'{sum(v>0 for v in values)} / {sum(v==0 for v in values)} / {sum(v<0 for v in values)}'
            lines.append(f'| {benchmark} | {metric} | {counts} | {min(values):+.4f} | {max(values):+.4f} |')
    lines += ['', '## Noise floor', '',
              'Spread expected without a persona effect, on each benchmark\'s primary metric. Control SD is the per-task SD over control reps, averaged over tasks with two or more. '
              'Twin − source and neutral_b − neutral_a are per-task differences between arms that carry the same content or no distinctive identity. '
              'The placebo band is [min, max] of the per-arm mean twin and neutral contrasts; personas outside it are counted by their mean delta vs control. '
              'The band is descriptive, not a significance test.', '',
              '| Benchmark | Metric | Control SD | Twin − source: mean [min, max] (n) | neutral_b − neutral_a: mean [min, max] (n) | Floor mean | Ceiling mean | Placebo band | Personas outside band |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    number = lambda v: '—' if v is None else f'{v:+.4f}'
    spread_text = lambda d: '—' if d is None else f"{d['mean']:+.4f} [{d['min']:+.4f}, {d['max']:+.4f}] (n={d['n']})"
    for benchmark, floor in noise.items():
        band = floor['placebo_band']
        lines.append(f"| {benchmark} | {floor['metric']} | {number(floor['control_sd'])} | {spread_text(floor['twin_minus_source'])} | "
                     f"{spread_text(floor['neutral_b_minus_a'])} | {number(floor['floor_mean'])} | {number(floor['ceiling_mean'])} | "
                     + ('—' if band is None else f'[{band[0]:+.4f}, {band[1]:+.4f}]')
                     + f" | {'—' if floor['personas_outside_band'] is None else floor['personas_outside_band']} / {floor['personas']} |")
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
        task_rows = [r for r in rows if r['task']==task and arm_kind(r['arm']) == PERSONA]
        task_values = defaultdict(list)
        for pair in comparisons:
            if pair['task']==task:
                for key, value in pair['delta']['metrics'].items():
                    task_values[key].append(value)
        changes = '; '.join(f'{k}: {sum(v)/len(v):+.4f} (n={len(v)})' for k,v in sorted(task_values.items()))
        control_status = ', '.join(c['status'] for c in controls[task]) if task in controls else 'pending'
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
    parser.add_argument('--control-reps', type=int, default=1,
                        help='Persona-off runs per task for a fresh build (persona_off, persona_off_r2, ...)')
    parser.add_argument('--twins', type=int, default=0,
                        help='Cohort profiles that also run as a bullet-reordered twin (<id>__reordered) for a fresh build')
    parser.add_argument('--neutral-arms', action='store_true', help='Add the neutral_a and neutral_b identity arms to a fresh build')
    parser.add_argument('--bound-arms', action='store_true',
                        help='Add floor_mute and ceiling_oracle scripted-researcher arms to a fresh build')
    parser.add_argument('--truthful-history', action='store_true',
                        help='Instruct the simulated researcher in every arm not to claim disclosures that did not happen')
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
    manifest = (read(output/'manifest.json') if (output/'manifest.json').exists()
                else build(output, args.control_reps, args.twins, args.neutral_arms, args.bound_arms, args.truthful_history))
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
