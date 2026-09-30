#!/usr/bin/env python3
"""Persona-off difficulty screen of SciConv disambiguation cases under the frozen v2 settings.

Each case gets three fresh persona-off episodes; cases solved 30-70% of the time are
candidates for persona tests. No persona text is injected in this screen.
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
PREPARED = ROOT / 'prepared/sciconv-difficulty-screen/pilot_manifest.json'
REPEATS = 3
SEED = 20260929


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def build(output):
    shared = read(ROOT / 'configs/full_persona_v2/shared.json')
    assert shared['collaboration'].get('unrestricted_knowledge') is True and shared['persona'] == {'enabled': False}
    write(output / 'configs' / 'persona_off' / 'shared.json', deepcopy(shared))
    manifest = read(PREPARED)
    tasks = []
    for record in manifest['cases']:
        assert record['assets_ready'], record['episode_id']
        slug = record['episode_id'].split(':', 1)[1].replace('/', '_')
        write(output / 'inputs' / slug / 'pilot_manifest.json', {**manifest, 'cases': [record]})
        tasks.append({'id': record['episode_id'], 'slug': slug, 'prepared': str(output / 'inputs' / slug)})
    jobs = [{**t, 'arm': 'persona_off', 'rep': rep, 'key': f"persona_off-{t['slug']}-r{rep}"}
            for t in tasks for rep in range(1, REPEATS + 1)]
    random.Random(SEED).shuffle(jobs)
    write(output / 'manifest.json', {
        'version': 'sciconv-difficulty-screen-v1', 'tasks': tasks, 'repeats': REPEATS, 'jobs': jobs, 'seed': SEED,
        'config': 'configs/full_persona_v2/shared.json (unrestricted_knowledge=true), persona off',
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), PREPARED, *sorted((ROOT / 'src').rglob('*.py'))]}})
    return jobs


def execute(output, job):
    started = time.monotonic()
    result_dir = output / 'episodes' / job['key']
    log = output / 'logs' / (job['key'] + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [PYTHON, '-m', 'personasciencebench.sciconv_runner', '--prepared', job['prepared'], '--output', str(result_dir),
           '--config', str(output / 'configs' / job['arm'] / 'shared.json'), '--parallel', '1']
    with log.open('w') as stream:
        proc = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ), stdout=stream, stderr=subprocess.STDOUT)
    records = list(result_dir.glob('*/result.json'))
    record = read(records[0]) if len(records) == 1 else {'status': 'launch_error'}
    result = {**job, 'returncode': proc.returncode, 'elapsed_seconds': round(time.monotonic() - started, 1),
              'status': record['status'], 'result': str(records[0]) if records else None}
    write(output / 'finished' / (job['key'] + '.json'), result)
    print(f"{job['key']}: {record['status']} ({result['elapsed_seconds']}s)", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--parallel', type=int, default=2)
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    output = args.output.resolve()
    jobs = read(output / 'manifest.json')['jobs'] if (output / 'manifest.json').exists() else build(output)
    pending = [j for j in jobs if not (output / 'finished' / (j['key'] + '.json')).exists()]
    print(f'{len(jobs)} jobs, {len(pending)} pending', flush=True)
    if args.build_only:
        return
    pending = pending[:args.limit] if args.limit else pending
    with ThreadPoolExecutor(args.parallel) as pool:
        list(pool.map(lambda j: execute(output, j), pending))


if __name__ == '__main__':
    main()
