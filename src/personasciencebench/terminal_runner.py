"""Concurrent native-image Terminal actors with sealed Harbor verification.

The actor network is disabled as an explicit environment adaptation. Only the
public environment image and a dedicated output workspace enter its container.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import time
from uuid import uuid4

from personasciencebench.actor import run_actor
from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.packaging import write_json, safe_component
from personasciencebench.persona import resolve_persona
from personasciencebench.registry import load_adapter
from personasciencebench.researcher import Researcher
from personasciencebench.schema import Episode
from personasciencebench.session import EpisodeSession
from personasciencebench.terminal_scoring import (
    MISSING_SUBMISSION_POLICY, missing_submission_evaluation, terminal_score_fields,
)


class DockerSandbox:
    def __init__(self, episode, workspace, log):
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=False)
        self.outputs = episode.public.submission['required_artifacts']
        self.container = 'psb-luna-' + uuid4().hex
        self.image = 'psb-science:' + episode.source_task_id.rsplit('/', 1)[-1] + '-f55c14ea'
        self.started = False
        task = Path(episode.evaluator.reference['task_path'])
        with log.open('w') as stream:
            subprocess.run(['docker', 'build', '-t', self.image, str(task / 'environment')],
                           stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=2400)
        resources = episode.public.environment['resources']
        subprocess.run(['docker', 'run', '-d', '--name', self.container,
                        '--network', 'none', '--security-opt', 'no-new-privileges',
                        '--cap-drop', 'ALL', '--cpus', str(resources['cpus']),
                        '--memory', str(resources['memory_mb']) + 'm',
                        '--mount', f'type=bind,src={self.workspace},dst=/workspace',
                        '--entrypoint', '/bin/sh', self.image, '-c', 'sleep infinity'],
                       check=True, capture_output=True, text=True)
        self.started = True
        self.deadline = time.monotonic() + episode.public.environment['agent_timeout_seconds']
        (self.workspace / 'native_artifacts').mkdir()

    def execute(self, command, timeout_seconds=120):
        remaining = int(self.deadline - time.monotonic())
        if remaining <= 0:
            raise RuntimeError('Native actor wall-time budget exhausted')
        seconds = min(timeout_seconds, remaining)
        start = time.monotonic()
        proc = subprocess.run(['docker', 'exec', self.container, 'timeout', '-k', '5',
                               str(seconds), '/bin/sh', '-c', command],
                              capture_output=True, text=True, timeout=seconds + 30)
        # The actor submits local copies under the exact native artifact keys.
        # docker cp never exposes controller files to the actor container.
        for index, source in enumerate(self.outputs):
            target = self.workspace / 'native_artifacts' / f'artifact_{index}'
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise ValueError('Invalid local artifact destination')
            subprocess.run(['docker', 'cp', f'{self.container}:{source}', str(target)],
                           capture_output=True, timeout=30)
        return {'exit_code': proc.returncode, 'stdout': proc.stdout[:65536],
                'stderr': proc.stderr[:65536], 'timeout': proc.returncode in (124, 137),
                'elapsed_seconds': round(time.monotonic() - start, 3)}

    def close(self):
        if self.started:
            subprocess.run(['docker', 'rm', '-f', self.container], capture_output=True, timeout=60)


def run(prepared, output, config, parallel, verifier_backend="harbor"):
    manifest = json.loads((prepared / 'pilot_manifest.json').read_text())
    records = manifest['cases']
    expected = config['pilot_cases_per_benchmark']
    if len(records) != expected or len({r['episode_id'] for r in records}) != expected:
        raise ValueError('Incorrect number of distinct Terminal cases')
    if any(r['benchmark'] != 'terminal_bench_science' or not r['assets_ready'] for r in records):
        raise ValueError('All selected Terminal cases must have ready assets')
    catalog = preflight(config['models'])
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    write_json(output / 'config.json', config)
    write_json(output / 'api_preflight.json', catalog)
    write_json(output / 'runtime_variant.json', {
        'version': 'terminal-native-image-openhands-v1', 'parallel': parallel,
        'actor_network': 'none', 'upstream_actor_network': 'public',
        'actor_steps': config['actor_steps'], 'native_wall_time_limit_preserved': True,
        'grader': 'unchanged native separate verifier', 'verifier_backend': verifier_backend,
        'judge_model_used': False, 'scoring_policy': MISSING_SUBMISSION_POLICY})

    def one(record):
        case = output / safe_component(record['episode_id'])
        case.mkdir(mode=0o700)
        episode = Episode.model_validate_json((Path(record['package']) / 'controller/episode.private.json').read_text())
        adapter = load_adapter('terminal_bench_science', Path(manifest['source_root']), Path(manifest['source_manifest']))
        result = {'episode_id': episode.id, 'status': 'infrastructure_error'}
        sandbox = None
        try:
            sandbox = DockerSandbox(episode, case / 'actor', case / 'image-build.log')
            episode.public.environment['execution'] = 'Native task image; no network; /workspace is a dedicated output directory.'
            episode.public.submission['artifact_copy_paths'] = {
                name: f'native_artifacts/artifact_{i}' for i, name in enumerate(sandbox.outputs)}
            episode.public.context += (
                ' Commands start in the native image working directory. Required files are copied after each '
                'command to /workspace/native_artifacts/artifact_N, in required_artifacts order. '
                'Submit artifact keys as the exact native absolute paths, with values equal to those '
                'workspace-relative copy paths. Do not modify the copies: edit the native target files.')
            def log_api(value):
                with (case / 'api_calls.private.jsonl').open('a') as stream:
                    stream.write(json.dumps(value) + '\n')
            clients = {role: OpenRouterClient(**spec, role=role, record=log_api,
                        supported_parameters=catalog[role]['supported_parameters'])
                       for role, spec in config['models'].items()}
            researcher = Researcher(episode, clients['researcher'], persona=resolve_persona(config, episode), **config['researcher'])
            session = EpisodeSession(episode, researcher, case / 'controller', artifact_root=sandbox.workspace)
            actor_result = run_actor(session, clients['actor'], sandbox, max_steps=config['actor_steps'])
            write_json(case / 'actor_result.json', actor_result)
            result.update(actor=actor_result, researcher_questions=researcher.questions)
            if session.submission is None:
                result['status'] = 'infrastructure_error' if actor_result.get('status') == 'error' else 'missing_submission'
                if result['status'] == 'missing_submission':
                    result['evaluation'] = missing_submission_evaluation()
                    write_json(case / 'evaluation.json', result['evaluation'])
            else:
                sandbox.close()
                sandbox = None
                if verifier_backend == "native-docker":
                    from personasciencebench.terminal_native import evaluate
                    evaluation = evaluate(episode, session.submission, case / 'native-docker')
                else:
                    request = adapter.evaluation_request(episode, session.submission, (case / 'native_receipt.json').resolve())
                    with (case / 'native-verification.log').open('w') as stream:
                        subprocess.run(request.argv, cwd=request.cwd, stdout=stream,
                                       stderr=subprocess.STDOUT, check=True, timeout=7200)
                    evaluation = adapter.evaluate(episode, session.submission)
                result.update(status=evaluation.status, evaluation=evaluation.model_dump(mode='json'))
                write_json(case / 'evaluation.json', evaluation.model_dump(mode='json'))
        except Exception as exc:
            result.update(error_type=type(exc).__name__, error=str(exc))
        finally:
            if sandbox:
                sandbox.close()
        result.update(terminal_score_fields(result))
        write_json(case / 'result.json', result)
        return result

    results = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = [pool.submit(one, record) for record in records]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            write_json(output / 'summary.json', {'requested': expected, 'cases': results, 'cross_benchmark_average': None})
            print(result['episode_id'], result['status'], flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    parser.add_argument('--parallel', type=int, default=5, choices=range(1, 26))
    parser.add_argument('--verifier-backend', choices=['harbor', 'native-docker'], default='harbor')
    args = parser.parse_args()
    load_env(args.env_file)
    results = run(args.prepared, args.output, json.loads(args.config.read_text()), args.parallel,
                  args.verifier_backend)
    return 0 if all(r['score'] is not None for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
