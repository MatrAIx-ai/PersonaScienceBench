#!/usr/bin/env python3
"""Run the BixBench CHIP persona pilot: five published full profiles plus persona off.

Two reviewed CHIP questions (bix-7-q2, bix-2-q2) x six arms x three independent
episodes. The researcher answers from reviewed facts only (the repository default;
`unrestricted_knowledge` is not set). Each episode runs in its own subprocess with
the shared `personasciencebench run` entry point and unchanged native grading.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / '.venv/bin/python')
PREPARED = ROOT / 'prepared/bixbench-chip-persona/pilot_manifest.json'
TASKS = ['bixbench:bix-7-q2', 'bixbench:bix-2-q2']
# Chosen from the full_persona_v2 eight-question ranking for diversity of observed
# single-run outcome; these labels are selection aids, not established effects.
PERSONAS = {
    'candidate_148': 'positive (+13.36 pp)',
    'candidate_155': 'positive (+12.60 pp)',
    'candidate_251': 'no impact (-0.43 pp)',
    'candidate_089': 'negative (-16.22 pp)',
    'candidate_003': 'negative (-19.87 pp)',
}
REPEATS = 3


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def published_prompt(row):
    text = (ROOT / row['published_profile']).read_text()
    prompt = text.split('```text\n', 1)[1].rsplit('\n```', 1)[0]
    if hashlib.sha256(prompt.encode()).hexdigest() != row['prompt_sha256']:
        raise ValueError(f"Published identity hash mismatch: {row['candidate_id']}")
    return prompt


def build(output):
    from personasciencebench.persona import Persona, persona_record
    cohort = {row['candidate_id']: row for row in read(ROOT / 'configs/full_persona_v2/cohort.json')['profiles']}
    profiles = {'persona_off': {'enabled': False}}
    for candidate in PERSONAS:
        row = cohort[candidate]
        profiles[candidate] = {'enabled': True, 'id': candidate, 'version': 'full-persona-v2',
                               'system_prompt': published_prompt(row)}
    shared = read(ROOT / 'configs/conversion-v2-two.json')
    shared['pilot_cases_per_benchmark'] = 1
    assert 'unrestricted_knowledge' not in shared['collaboration']
    shared['notes'] = ['BixBench CHIP persona pilot: full published MatrAIx profile in the researcher system prompt only.',
                       'Researcher answers from reviewed facts only (unrestricted_knowledge unset); native grading unchanged.']
    for model in shared['models'].values():
        assert model['model'] == 'openai/gpt-6-luna' and model['reasoning_effort'] == 'none'
    manifest = read(PREPARED)
    tasks = []
    for record in manifest['cases']:
        assert record['assets_ready'], record['episode_id']
        slug = record['episode_id'].split(':', 1)[1]
        prepared = output / 'inputs' / slug
        write(prepared / 'pilot_manifest.json', {**manifest, 'cases': [record]})
        tasks.append({'id': record['episode_id'], 'slug': slug, 'prepared': str(prepared)})
    assert sorted(t['id'] for t in tasks) == sorted(TASKS)
    for arm, profile in profiles.items():
        write(output / 'configs' / arm / 'shared.json', {**deepcopy(shared), 'persona': profile})
        write(output / 'configs' / arm / 'persona.private.json', persona_record(Persona.model_validate(profile)))
    jobs = [{**task, 'arm': arm, 'rep': rep, 'key': f'{arm}-{task["slug"]}-r{rep}'}
            for arm in profiles for task in tasks for rep in range(1, REPEATS + 1)]
    random.Random(20260928).shuffle(jobs)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [Path(__file__), PREPARED, *sorted((ROOT / 'src').rglob('*.py'))]}
    write(output / 'manifest.json', {
        'version': 'bixbench-chip-persona-pilot-v1', 'tasks': tasks, 'arms': list(profiles),
        'persona_selection': PERSONAS, 'repeats': REPEATS, 'jobs': jobs, 'source_sha256': hashes,
        'models': shared['models'], 'knowledge': 'reviewed facts only (unrestricted_knowledge unset)',
        'injection': 'Exact published full profile in researcher system prompt only; actor and judge never receive it'})
    return jobs


def execute(output, job, env_file, actor_python):
    started = time.monotonic()
    result_dir = output / 'episodes' / job['key']
    config = output / 'configs' / job['arm'] / 'shared.json'
    log = output / 'logs' / (job['key'] + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    cmd = [PYTHON, '-m', 'personasciencebench', 'run', '--prepared', job['prepared'], '--benchmarks', 'bixbench',
           '--actor-python', str(actor_python), '--output', str(result_dir), '--config', str(config),
           '--env-file', str(env_file), '--parallel', '1']
    with log.open('w') as stream:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    records = list(result_dir.glob('*/result.json'))
    record = read(records[0]) if len(records) == 1 else {'status': 'launch_error'}
    if records:
        with log.open('a') as stream:
            subprocess.run([PYTHON, str(ROOT / 'scripts/render_run_traces.py'), str(result_dir)],
                           cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    result = {**job, 'returncode': proc.returncode, 'elapsed_seconds': round(time.monotonic() - started, 1),
              'status': record['status'], 'result': str(records[0]) if records else None}
    write(output / 'finished' / (job['key'] + '.json'), result)
    print(f"{job['key']}: {record['status']} ({result['elapsed_seconds']}s)", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--actor-python', type=Path, default=ROOT / '.actor-venv')
    parser.add_argument('--parallel', type=int, default=4)
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--limit', type=int, help='Run at most this many pending jobs (smoke test)')
    args = parser.parse_args()
    output = args.output.resolve()
    jobs = read(output / 'manifest.json')['jobs'] if (output / 'manifest.json').exists() else build(output)
    pending = [j for j in jobs if not (output / 'finished' / (j['key'] + '.json')).exists()]
    print(f'{len(jobs)} jobs, {len(pending)} pending', flush=True)
    if args.build_only:
        return
    if args.limit:
        pending = pending[:args.limit]
    with ThreadPoolExecutor(args.parallel) as pool:
        list(pool.map(lambda j: execute(output, j, args.env_file.resolve(), args.actor_python.resolve()), pending))


if __name__ == '__main__':
    main()
