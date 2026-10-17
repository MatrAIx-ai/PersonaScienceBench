#!/usr/bin/env python3
"""Rerun test of the full_persona_v2 SciConv co-pass pattern under the frozen v2 settings.

Arms: persona off, the six personas that passed both SciConv cases in v2, and six
seeded draws from the thirteen that passed neither. Two cases x three fresh episodes.
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
PREPARED = ROOT / 'prepared/sciconv-persona-rerun/pilot_manifest.json'
BOTH_PASS = ['candidate_050', 'candidate_055', 'candidate_148', 'candidate_155', 'candidate_228', 'candidate_259']
REPEATS = 3
SEED = 20260928


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def v2_groups(snapshot):
    frr = {}
    for e in read(snapshot)['episodes']:
        if e['arm'] != 'persona_off' and e['benchmark'] == 'sciconvbench':
            frr.setdefault(e['arm'], {})[e['task'].split(':', 1)[1]] = e['metrics']['FRR']
    both = sorted(a for a, v in frr.items() if v.get('solMech/disambiguation/case_104') == 1
                  and v.get('foam/disambiguation/case_020') == 1)
    neither = sorted(a for a, v in frr.items() if v.get('solMech/disambiguation/case_104') == 0
                     and v.get('foam/disambiguation/case_020') == 0)
    assert both == BOTH_PASS and len(neither) == 13, (both, len(neither))
    return both, random.Random(SEED).sample(neither, 6)


def build(output):
    from personasciencebench.persona import Persona, persona_record
    both, neither = v2_groups(ROOT / 'reports/full_persona_v2/snapshot.json')
    cohort = {r['candidate_id']: r for r in read(ROOT / 'configs/full_persona_v2/cohort.json')['profiles']}
    profiles = {'persona_off': {'enabled': False}}
    for candidate in both + neither:
        row = cohort[candidate]
        prompt = (ROOT / row['published_profile']).read_text().split('```text\n', 1)[1].rsplit('\n```', 1)[0]
        assert hashlib.sha256(prompt.encode()).hexdigest() == row['prompt_sha256'], candidate
        profiles[candidate] = {'enabled': True, 'id': candidate, 'version': 'full-persona-v2', 'system_prompt': prompt}
    shared = read(ROOT / 'configs/full_persona_v2/shared.json')
    assert shared['collaboration'].get('unrestricted_knowledge') is True
    manifest = read(PREPARED)
    tasks = []
    for record in manifest['cases']:
        assert record['assets_ready'], record['episode_id']
        slug = record['episode_id'].split(':', 1)[1].replace('/', '_')
        prepared = output / 'inputs' / slug
        write(prepared / 'pilot_manifest.json', {**manifest, 'cases': [record]})
        tasks.append({'id': record['episode_id'], 'slug': slug, 'prepared': str(prepared)})
    for arm, profile in profiles.items():
        write(output / 'configs' / arm / 'shared.json', {**deepcopy(shared), 'persona': profile})
        write(output / 'configs' / arm / 'persona.private.json', persona_record(Persona.model_validate(profile)))
    jobs = [{**t, 'arm': arm, 'rep': rep, 'key': f"{arm}-{t['slug']}-r{rep}"}
            for arm in profiles for t in tasks for rep in range(1, REPEATS + 1)]
    random.Random(SEED).shuffle(jobs)
    write(output / 'manifest.json', {
        'version': 'sciconv-persona-rerun-v1', 'groups': {'both_pass_v2': both, 'neither_pass_v2_sample': neither},
        'arms': list(profiles), 'tasks': tasks, 'repeats': REPEATS, 'jobs': jobs, 'seed': SEED,
        'config': 'configs/full_persona_v2/shared.json (unrestricted_knowledge=true), persona replaced per arm',
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), PREPARED, *sorted((ROOT / 'src').rglob('*.py'))]}})
    return jobs


def execute(output, job):
    started = time.monotonic()
    result_dir = output / 'episodes' / job['key']
    log = output / 'logs' / (job['key'] + '.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [PYTHON, '-m', 'personasciencebench.sciconv_runner', '--prepared', job['prepared'],
           '--output', str(result_dir), '--config', str(output / 'configs' / job['arm'] / 'shared.json'), '--parallel', '1']
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
    parser.add_argument('--parallel', type=int, default=4)
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
