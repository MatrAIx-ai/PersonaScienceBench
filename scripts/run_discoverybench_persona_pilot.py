"""Run a matched DiscoveryBench persona pilot with the existing actor and native grader."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import tempfile

from personasciencebench.inference import load_env, model_client, preflight
from personasciencebench.packaging import write_json
from personasciencebench.persona import resolve_persona
from personasciencebench.runner import run_pilots
from personasciencebench.runtime import Sandbox
from personasciencebench.schema import Episode
from personasciencebench.science_personas.config import attach_profile
from personasciencebench.science_personas.observations import summarize as interaction_summary
from personasciencebench.science_personas.profiles import SciencePersona

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('off', 'reference', 'statistics_low', 'statistics_high')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def arm_configs(base, reference):
    """Three complete profiles differ only in statistical_inference; off keeps the simulator."""
    if base.get('persona_router'):
        raise ValueError('Matched pilot requires no persona routing')
    configs = {'off': {**deepcopy(base), 'persona': {'enabled': False}}}
    for arm, level in [('reference', 'medium'), ('statistics_low', 'low'), ('statistics_high', 'high')]:
        profile = deepcopy(reference)
        profile.update(id='discoverybench_' + arm, role='researcher', domain='empirical data analysis')
        profile['attributes'] = {key: 'medium' for key in profile['attributes']}
        profile['attributes']['statistical_inference'] = level
        configs[arm] = attach_profile(base, SciencePersona.model_validate(profile))
    hashes = {digest({k: v for k, v in c.items() if k != 'persona'}) for c in configs.values()}
    if len(hashes) != 1:
        raise ValueError('Non-persona configuration differs between arms')
    return configs


def inventory(prepared, python_root):
    paths = list(prepared.rglob('*')) + list((ROOT / 'src').rglob('*.py'))
    paths += [Path(__file__), ROOT / 'scripts/bwrap_userns_launcher.py', ROOT / 'uv.lock',
              ROOT / 'configs/actor-requirements.lock.txt', python_root / 'pyvenv.cfg']
    paths += list((python_root / 'lib').rglob('*.dist-info/RECORD'))
    return {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def summarize(records):
    """Pair within task and repetition; failures stay missing, never score zero."""
    keyed = {(r['arm'], r['repeat'], r['episode_id']): r for r in records}
    if len(keyed) != len(records):
        raise ValueError('Duplicate arm/repetition/task results')
    summary = []
    for arm in ARMS:
        rows = [r for r in records if r['arm'] == arm]
        scores = [r['score'] for r in rows if r['score'] is not None]
        pairs = [(r, keyed.get(('off', r['repeat'], r['episode_id']))) for r in rows]
        pairs = [(r, c) for r, c in pairs if c is not None and r['score'] is not None and c['score'] is not None]
        deltas = [r['score'] - c['score'] for r, c in pairs]
        summary.append({'arm': arm, 'attempted': len(rows), 'scored': len(scores),
                        'mean_native_score': statistics.mean(scores) if scores else None,
                        'paired_n': len(pairs), 'paired_mean_delta_vs_off': statistics.mean(deltas) if deltas else None,
                        'wins_ties_losses': [sum(d > 1e-9 for d in deltas), sum(abs(d) <= 1e-9 for d in deltas), sum(d < -1e-9 for d in deltas)],
                        'mean_researcher_requests': statistics.mean(r['researcher_requests'] for r in rows) if rows else None,
                        'prompt_tokens': sum(r.get('prompt_tokens', 0) for r in rows),
                        'completion_tokens': sum(r.get('completion_tokens', 0) for r in rows)})
    return {'arms': summary, 'distinct_studies': len({r['study_id'] for r in records}),
            'records': records, 'interpretation': 'Exploratory paired differences only. Repeated trials are not independent studies; this small pilot cannot establish a general persona benefit.',
            'cost_usd': None, 'cost_note': 'Azure usage tokens are recorded; no dollar amount is inferred without Azure billing rates.'}


def collect(run, arm, repeat):
    records = []
    for result in run['cases']:
        case = Path(result['case_directory'])
        events = case / 'controller/events.jsonl'
        observations = interaction_summary(events) if events.exists() else {}
        if observations:
            write_json(case / 'interaction_observations.json', observations)
        api = case / 'controller/api_calls.private.jsonl'
        calls = [json.loads(line) for line in api.read_text().splitlines()] if api.exists() else []
        metrics = result.get('evaluation', {}).get('metrics', {})
        records.append({'arm': arm, 'repeat': repeat, 'episode_id': result['episode_id'],
                        'study_id': result['study_id'], 'status': result['status'],
                        'score': metrics.get('final_score') if result['status'] == 'scored' else None,
                        'researcher_requests': result.get('researcher_requests', 0),
                        'disclosed_facts': result.get('disclosed_facts', 0),
                        'actor_calls': result.get('actor', {}).get('actor_calls'),
                        'observations': observations,
                        'prompt_tokens': sum(c.get('usage', {}).get('prompt_tokens', 0) for c in calls),
                        'completion_tokens': sum(c.get('usage', {}).get('completion_tokens', 0) for c in calls),
                        'resolved_models': sorted({c.get('resolved_model') for c in calls if c.get('resolved_model')}),
                        'case_directory': str(case), 'error': result.get('error')})
    return records


def write_report(output, report):
    write_json(output / 'comparison.json', report)
    lines = ['# DiscoveryBench Azure persona pilot', '', report['interpretation'], '',
             '| Arm | Scored / attempted | Mean native score | Paired change vs off | Pairs | Wins / ties / losses |',
             '| --- | ---: | ---: | ---: | ---: | --- |']
    def number(n):
        return 'unscored' if n is None else f'{n:.4f}'
    for arm in report['arms']:
        lines.append(f"| {arm['arm']} | {arm['scored']} / {arm['attempted']} | {number(arm['mean_native_score'])} | {number(arm['paired_mean_delta_vs_off'])} | {arm['paired_n']} | {' / '.join(map(str, arm['wins_ties_losses']))} |")
    lines += ['', f"Distinct studies: {report['distinct_studies']}. Native metrics and interaction counts remain separate.",
              '', 'Missing or failed evaluations are unscored and excluded from paired differences, with coverage shown explicitly.',
              '', 'Azure costs are unknown here; see token usage in comparison.json and billing in Azure.', '']
    (output / 'comparison.md').write_text('\n'.join(lines))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, default=ROOT / 'prepared/discoverybench-azure')
    p.add_argument('--config', type=Path, default=ROOT / 'configs/discoverybench-azure.json')
    p.add_argument('--actor-python', type=Path, default=ROOT / '.actor-venv')
    p.add_argument('--env-file', type=Path, default=ROOT / '.env')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--repeats', type=int, default=2)
    p.add_argument('--parallel', type=int, default=2, help='Concurrent cases per arm; at most two arms run at once')
    p.add_argument('--order-seed', type=int, default=20260926)
    p.add_argument('--bootstrap-userns', action='store_true', help='Opt in to sudo namespace setup; no host policy changes')
    p.add_argument('--run', action='store_true', help='Execute paid model calls; otherwise write an offline plan only')
    args = p.parse_args(argv)
    if args.repeats < 1 or not 1 <= args.parallel <= 2:
        p.error('repeats must be positive and parallel must be 1 or 2')
    load_env(args.env_file)
    base = json.loads(args.config.read_text())
    deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT')
    if deployment:
        for spec in base['models'].values():
            if spec.get('provider') == 'azure':
                spec['model'] = deployment
    profiles = json.loads((ROOT / 'examples/science_personas/phase1/reference.json').read_text())
    configs = arm_configs(base, profiles)
    prepared = args.prepared.resolve()
    manifest = json.loads((prepared / 'pilot_manifest.json').read_text())
    if len(manifest['cases']) != 2 or any(c['benchmark'] != 'discoverybench' or not c['assets_ready'] for c in manifest['cases']):
        p.error('This pilot requires exactly two ready DiscoveryBench tasks')
    for case in manifest['cases']:
        episode = Episode.model_validate_json((Path(case['package']) / 'controller/episode.private.json').read_text())
        for config in configs.values():
            resolve_persona(config, episode)
    if args.bootstrap_userns:
        os.environ['PERSONASCIENCEBENCH_BWRAP'] = str(ROOT / 'scripts/bwrap_userns_launcher.py')
    frozen = inventory(prepared, args.actor_python.resolve())
    jobs = [(repeat, arm) for repeat in range(1, args.repeats + 1) for arm in ARMS]
    random.Random(args.order_seed).shuffle(jobs)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    for arm, config in configs.items():
        write_json(output / 'configs' / f'{arm}.json', config)
    plan = {'kind': 'discoverybench-matched-persona-pilot-v1', 'source_revision': episode.source_revision,
            'task_ids': [c['episode_id'] for c in manifest['cases']], 'arms': list(ARMS),
            'repeats': args.repeats, 'scheduled_episodes': len(jobs) * 2, 'order_seed': args.order_seed,
            'schedule': jobs, 'non_persona_config_sha256': digest({k: v for k, v in base.items() if k != 'persona'}),
            'frozen_inputs': frozen, 'arm_config_sha256': {arm: digest(c) for arm, c in configs.items()},
            'git_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'git_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
            'bootstrap_userns': args.bootstrap_userns, 'scientific_runs_started': False}
    write_json(output / 'plan.private.json', plan)
    if not args.run:
        print(json.dumps({'output': str(output), 'episodes_planned': len(jobs) * 2, 'model_calls': 0}))
        return 0
    try:
        with tempfile.TemporaryDirectory(prefix='psb-discovery-probe-') as workspace:
            write_json(output / 'runtime_check.json', Sandbox(Path(workspace), args.actor_python).check())
        write_json(output / 'api_preflight.json', preflight(base['models']))
        # Explicit paid compatibility probe; catalog access alone cannot establish deployment readiness.
        for role, spec in base['models'].items():
            def record(value):
                with (output / 'preflight_calls.private.jsonl').open('a') as stream:
                    stream.write(json.dumps(value) + '\n')
            client = model_client(**spec, role=role, record=record)
            messages = [{'role': 'user', 'content': 'Return a JSON object with ready set to true, using the function if supplied.'}]
            if role == 'judge':
                for temperature in (0, 1):
                    client.complete(messages, json_mode=True, settings={'temperature': temperature, 'max_tokens': 250,
                                    'top_p': 1, 'frequency_penalty': 0, 'presence_penalty': 0})
            else:
                client.complete_decision(messages, {'type': 'object', 'properties': {'ready': {'type': 'boolean'}}, 'required': ['ready']})
    except Exception as exc:
        write_json(output / 'blocked.json', {'status': 'preflight_failed', 'error_type': type(exc).__name__, 'error': str(exc), 'scientific_episodes_started': 0})
        raise
    plan['scientific_runs_started'] = True
    write_json(output / 'plan.private.json', plan)
    records = []
    def run_job(job):
        repeat, arm = job
        destination = output / f'repeat-{repeat:02d}' / arm
        return repeat, arm, run_pilots(prepared, ['discoverybench'], destination,
                                      args.actor_python, configs[arm], parallel=args.parallel)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(run_job, job): job for job in jobs}
        for future in as_completed(futures):
            repeat, arm = futures[future]
            try:
                _, _, result = future.result()
                records.extend(collect(result, arm, repeat))
            except Exception as exc:
                for case in manifest['cases']:
                    records.append({'arm': arm, 'repeat': repeat, 'episode_id': case['episode_id'],
                                    'study_id': case['study_id'], 'status': 'infrastructure_error', 'score': None,
                                    'researcher_requests': 0, 'error': f'{type(exc).__name__}: {exc}'})
            write_report(output, summarize(records))
            print(json.dumps({'finished_arm': arm, 'repeat': repeat, 'completed_episodes': len(records),
                              'scored': sum(r['score'] is not None for r in records)}), flush=True)
    intact = inventory(prepared, args.actor_python.resolve()) == frozen
    write_json(output / 'integrity.json', {'frozen_inputs_unchanged': intact,
                'arm_configs_unchanged': all(digest(json.loads((output / 'configs' / f'{arm}.json').read_text())) == plan['arm_config_sha256'][arm] for arm in ARMS)})
    if not intact:
        raise RuntimeError('Inputs or execution code changed during the experiment; comparison is invalid')
    return int(any(r['status'] != 'scored' for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
