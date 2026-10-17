#!/usr/bin/env python3
"""Run SciConv episodes for named arms under the frozen v2 settings (Luna).

Arms: persona_off; neutral_a / neutral_b (PR #8 / #16 neutral identity texts, hash-recorded);
candidate_NNN (published full_persona_v2 profiles, hash-checked). Usage example:
  --arms persona_off=5 neutral_a=6 neutral_b=6 candidate_148=3 candidate_155=3
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
SEED = 20260929


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def profile(arm, neutral_dir):
    if arm == 'persona_off':
        return {'enabled': False}, None
    if arm.startswith('neutral_'):
        text = (neutral_dir / f'{arm}.txt').read_text()
        return {'enabled': True, 'id': arm, 'version': 'neutral-v1', 'system_prompt': text}, hashlib.sha256(text.encode()).hexdigest()
    row = {r['candidate_id']: r for r in read(ROOT / 'configs/full_persona_v2/cohort.json')['profiles']}[arm]
    text = (ROOT / row['published_profile']).read_text().split('```text\n', 1)[1].rsplit('\n```', 1)[0]
    digest = hashlib.sha256(text.encode()).hexdigest()
    assert digest == row['prompt_sha256'], arm
    return {'enabled': True, 'id': arm, 'version': 'full-persona-v2', 'system_prompt': text}, digest


def build(output, prepared, arms, neutral_dir):
    from personasciencebench.persona import Persona, persona_record
    shared = read(ROOT / 'configs/full_persona_v2/shared.json')
    assert shared['collaboration'].get('unrestricted_knowledge') is True
    hashes = {}
    for arm in arms:
        persona, hashes[arm] = profile(arm, neutral_dir)
        write(output / 'configs' / arm / 'shared.json', {**deepcopy(shared), 'persona': persona})
        write(output / 'configs' / arm / 'persona.private.json', persona_record(Persona.model_validate(persona)))
    manifest = read(prepared)
    tasks = []
    for record in manifest['cases']:
        assert record['assets_ready'], record['episode_id']
        slug = record['episode_id'].split(':', 1)[1].replace('/', '_')
        write(output / 'inputs' / slug / 'pilot_manifest.json', {**manifest, 'cases': [record]})
        tasks.append({'id': record['episode_id'], 'slug': slug, 'prepared': str(output / 'inputs' / slug)})
    jobs = [{**t, 'arm': arm, 'rep': rep, 'key': f"{arm}-{t['slug']}-r{rep}"}
            for arm, reps in arms.items() for t in tasks for rep in range(1, reps + 1)]
    random.Random(SEED).shuffle(jobs)
    write(output / 'manifest.json', {
        'version': 'sciconv-arms-v1', 'arms': arms, 'identity_sha256': hashes, 'tasks': tasks, 'jobs': jobs, 'seed': SEED,
        'config': 'configs/full_persona_v2/shared.json (unrestricted_knowledge=true), persona replaced per arm',
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), Path(prepared), *sorted((ROOT / 'src').rglob('*.py'))]}})
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
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--arms', nargs='+', required=True, help='arm=repeats')
    parser.add_argument('--neutral-dir', type=Path, required=True)
    parser.add_argument('--parallel', type=int, default=2)
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    arms = {a.split('=')[0]: int(a.split('=')[1]) for a in args.arms}
    jobs = (read(output / 'manifest.json')['jobs'] if (output / 'manifest.json').exists()
            else build(output, args.prepared.resolve(), arms, args.neutral_dir.resolve()))
    pending = [j for j in jobs if not (output / 'finished' / (j['key'] + '.json')).exists()]
    print(f'{len(jobs)} jobs, {len(pending)} pending', flush=True)
    if args.build_only:
        return
    with ThreadPoolExecutor(args.parallel) as pool:
        list(pool.map(lambda j: execute(output, j), pending))


if __name__ == '__main__':
    main()
