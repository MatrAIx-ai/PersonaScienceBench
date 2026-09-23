"""Run ten isolated design episodes, with at most five concurrent processes."""
import argparse
import concurrent.futures
import getpass
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import time

CONDITIONS = ('sonnet5', 'o3mini')


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def cache_source(task, source, root):
    source = dict(source)
    manifest_path = Path(source['staging_manifest'])
    manifest = json.loads(manifest_path.read_text())
    target = root / 'staged' / task.replace('/', '__')
    repository = target / 'repository'
    for relative, digest in manifest['files_sha256'].items():
        rel = Path(relative)
        assert not rel.is_absolute() and '..' not in rel.parts
        src = Path(source['repository']) / rel
        assert not src.is_symlink()
        content = src.read_bytes()
        assert hashlib.sha256(content).hexdigest() == digest
        destination = repository / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        info = src.stat()
        destination.chmod(stat.S_IMODE(info.st_mode))
        os.utime(destination, ns=(info.st_atime_ns, info.st_mtime_ns))
    (target / 'staging.json').write_bytes(manifest_path.read_bytes())
    source.update(repository=str(repository), staging_manifest=str(target / 'staging.json'))
    return task, source


def worker(args):
    from expbench import realistic
    from expbench.gateway import Gateway

    class CompatibleGateway(Gateway):
        def complete(self, role, messages, **kwargs):
            if role == 'judge':
                messages = [dict(m) for m in messages]
                assert [m['role'] for m in messages] == ['system', 'user']
                assert messages[1]['content'] == ''
                messages[1]['content'] = 'Apply the evaluation instructions above.'
            return super().complete(role, messages, **kwargs)

    realistic.Gateway = CompatibleGateway
    out = args.local / 'episodes' / args.condition / args.task.replace('/', '__')
    return realistic.main(['run', '--mode', 'live', '--config',
        f'configs/expbench/sonnet5-actor-{args.condition}-simulator.toml', '--workspace-map',
        str(args.local / 'workspaces.json'), '--task', args.task, '--output', str(out)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', type=Path, default=Path('/tmp/expbench-sonnet5-actor-20260922'))
    parser.add_argument('--output', type=Path, default=Path('runs/expbench/sonnet5-actor-comparison-20260922'))
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--condition', choices=CONDITIONS)
    parser.add_argument('--task')
    args = parser.parse_args()
    if args.worker:
        return worker(args)
    args.local.mkdir(mode=0o700, parents=True, exist_ok=False)
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    mapping = json.loads(Path('data/realistic_pilot/staged/workspaces.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        cached = dict(pool.map(lambda item: cache_source(*item, args.local), mapping.items()))
    save(args.local / 'workspaces.json', cached)
    print('Verified and cached five repositories; ready for ten episodes.', flush=True)
    key = os.environ.get('OPENROUTER_API_KEY') or getpass.getpass('OpenRouter credential: ')
    env = dict(os.environ, OPENROUTER_API_KEY=key,
               PYTHONPYCACHEPREFIX='/tmp/expbench-validation-pycache')
    manifest = {'actor': 'anthropic/claude-sonnet-5', 'judge': 'anthropic/claude-sonnet-5',
        'simulators': list(CONDITIONS), 'task_ids': list(mapping), 'concurrent_processes': 5,
        'actor_steps': 20, 'question_limit': 6, 'judge_repeats': 3, 'workflow': False,
        'judge_user_message': 'Apply the evaluation instructions above.',
        'parser': 'Existing strict JSON parser; no fence repair', 'local_root': str(args.local),
        'note': 'CPU design-only episodes. Same scoped facts, public inputs, repositories and evaluator as previous runs. No validation suite.'}
    save(args.local / 'manifest.json', manifest)
    save(args.output / 'manifest.json', manifest)
    start = time.monotonic()

    def launch(job):
        condition, task = job
        slug = task.replace('/', '__')
        log = args.local / 'logs' / f'{condition}-{slug}.log'
        log.parent.mkdir(exist_ok=True)
        with log.open('w') as stream:
            proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                '--local', str(args.local), '--condition', condition, '--task', task],
                env=env, stdout=stream, stderr=subprocess.STDOUT)
        print(condition, task, 'exit', proc.returncode, flush=True)
        return {'condition': condition, 'task_id': task, 'returncode': proc.returncode}

    jobs = [(condition, task) for task in mapping for condition in CONDITIONS]
    exits = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for future in concurrent.futures.as_completed([pool.submit(launch, job) for job in jobs]):
            exits.append(future.result())
            save(args.local / 'process_status.json', {'finished': len(exits), 'scheduled': 10, 'results': exits})
    save(args.local / 'timing.json', {'episode_wall_seconds': time.monotonic() - start})
    # Keep individual logs/results easy to inspect; archive workspace trees to avoid
    # thousands of shared-filesystem metadata writes.
    for path in args.local.rglob('*'):
        relative = path.relative_to(args.local)
        if 'staged' in relative.parts or 'workspace' in relative.parts:
            continue
        destination = args.output / relative
        if path.is_dir(): destination.mkdir(exist_ok=True, parents=True)
        elif path.is_file(): destination.write_bytes(path.read_bytes())
    archive = args.local / 'workspaces.tar.gz'
    with tarfile.open(archive, 'w:gz') as bundle:
        for workspace in (args.local / 'episodes').glob('*/*/*/workspace'):
            bundle.add(workspace, arcname=str(workspace.relative_to(args.local)))
    (args.output / archive.name).write_bytes(archive.read_bytes())
    (args.output / 'run_driver.py').write_bytes(Path(__file__).read_bytes())
    print('All process attempts finished; artifacts persisted at', args.output, flush=True)
    return 0 if all(r['returncode'] == 0 for r in exits) else 1


if __name__ == '__main__':
    raise SystemExit(main())
