"""Native Terminal verifier scripts in separate Docker --network none containers.

Explicit adaptation for hosts lacking Harbor's nftables FIB support. Native
Dockerfiles, test.sh, grading code, and submitted artifacts are unchanged.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import tomllib
from uuid import uuid4

from personasciencebench.adapters.base import sha256, check_submission
from personasciencebench.adapters.terminal_bench_science import _task_digest, _regular, PILOTS
from personasciencebench.packaging import write_json
from personasciencebench.schema import Episode, Submission, EvaluationResult

VERSION = 'terminal-native-separate-docker-network-none-v1'


def evaluate(episode, submission, output):
    check_submission(episode, submission)
    if set(submission.artifacts) != set(PILOTS[episode.source_task_id]['outputs']):
        raise ValueError('Native artifact set differs from the reviewed task contract')
    task = Path(episode.evaluator.reference['task_path'])
    if _task_digest(task) != episode.evaluator.reference['task_digest']:
        raise ValueError('Native task changed after preparation')
    config = tomllib.loads((task / 'task.toml').read_text())
    if config['verifier']['environment_mode'] != 'separate' or config['verifier']['environment']['network_mode'] != 'no-network':
        raise ValueError('Requires the native separate, networkless verifier policy')
    hashes = {name: sha256(_regular(Path(path))) for name, path in submission.artifacts.items()}
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    container = 'psb-verifier-' + uuid4().hex
    image = 'psb-native-verifier:' + task.name + '-f55c14ea'
    provenance = {'runtime_variant': VERSION, 'native_task_digest': _task_digest(task),
                  'artifact_sha256': hashes, 'network_mode': 'none',
                  'native_verifier_script_sha256': sha256(task / 'tests/test.sh'),
                  'native_verifier_dockerfile_sha256': sha256(task / 'tests/Dockerfile'),
                  'native_grader_modified': False, 'judge_model_used': False}
    started = False
    try:
        with (output / 'image-build.log').open('w') as log:
            subprocess.run(['docker', 'build', '-t', image, str(task / 'tests')],
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=2400)
        # Keep default Docker SETUID/SETGID capabilities: native verifiers can
        # drop candidate code to their prescribed unprivileged users.
        subprocess.run(['docker', 'run', '-d', '--name', container, '--network', 'none',
                        '--cpus', str(config['environment']['cpus']),
                        '--memory', str(config['environment']['memory_mb']) + 'm',
                        '--entrypoint', '/bin/sh', image, '-c', 'sleep infinity'],
                       capture_output=True, text=True, check=True)
        started = True
        subprocess.run(['docker', 'exec', container, 'mkdir', '-p', '/logs/verifier'], check=True)
        for native, source in submission.artifacts.items():
            subprocess.run(['docker', 'exec', container, 'mkdir', '-p', str(Path(native).parent)], check=True)
            subprocess.run(['docker', 'cp', source, f'{container}:{native}'], check=True)
        timeout = int(config['verifier']['timeout_sec'])
        with (output / 'native-execution.log').open('w') as log:
            proc = subprocess.run(['docker', 'exec', container, 'timeout', '-k', '5', str(timeout),
                                   '/bin/bash', '/tests/test.sh'], stdout=log,
                                  stderr=subprocess.STDOUT, timeout=timeout + 30)
        provenance['native_process_exit_code'] = proc.returncode
        if proc.returncode in (124, 137):
            raise RuntimeError(f'Native verifier process exited {proc.returncode}')
        # Some native scripts deliberately return pytest's failure status after
        # writing reward=0. The native reward file is the grading contract.
        subprocess.run(['docker', 'cp', f'{container}:/logs/verifier/reward.txt', str(output / 'reward.txt')], check=True)
        subprocess.run(['docker', 'cp', f'{container}:/logs/verifier/ctrf.json', str(output / 'ctrf.json')], capture_output=True)
        reward = float((output / 'reward.txt').read_text().strip())
        if reward not in (0, 1):
            raise ValueError('Reviewed native task must return binary reward')
        if hashes != {name: sha256(_regular(Path(path))) for name, path in submission.artifacts.items()}:
            raise ValueError('Sealed artifacts changed during verification')
        result = EvaluationResult(status='scored', evaluator_version=VERSION,
                                  metrics={'reward': reward}, details={**provenance, 'score_denominator': 1})
    except Exception as exc:
        result = EvaluationResult(status='error', evaluator_version=VERSION,
                                  errors=[f'{type(exc).__name__}: {exc}'],
                                  details={**provenance, 'score_denominator': 0})
    finally:
        if started:
            subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=60)
    write_json(output / 'evaluation.json', result.model_dump(mode='json'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--task-id')
    parser.add_argument('--output-name', default='native-docker')
    args = parser.parse_args()
    if Path(args.output_name).name != args.output_name or args.output_name in ('.', '..'):
        raise ValueError('Output name must be a single path component')
    cases = [p.parent.parent for p in args.run.glob('*/controller/submission.json')
             if not (p.parent.parent / args.output_name / 'evaluation.json').exists()]
    def one(case):
        episode = Episode.model_validate_json((case / 'controller/episode.private.json').read_text())
        if args.task_id and episode.source_task_id != args.task_id:
            return
        submission = Submission.model_validate_json((case / 'controller/submission.json').read_text())
        result = evaluate(episode, submission, case / args.output_name)
        print(episode.id, result.status, result.metrics, flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        for future in as_completed([pool.submit(one, case) for case in cases]):
            future.result()


if __name__ == '__main__':
    main()
