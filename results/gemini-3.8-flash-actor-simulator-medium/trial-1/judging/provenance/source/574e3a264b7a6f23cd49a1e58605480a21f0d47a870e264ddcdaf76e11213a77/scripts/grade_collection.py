#!/usr/bin/env python3
"""Grade saved collection attempts with native evaluators; never invoke actors.

Original collection files remain immutable. Each grading attempt has its own
directory and API logs. Resume retains scored outcomes; --retry-errors retains
failed grading attempts before making a new one. Scientific non-submissions
score zero; interrupted actor/simulator attempts remain unavailable.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.packaging import safe_component
from personasciencebench.registry import load_adapter
from personasciencebench.schema import Episode, Submission

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {'asibench', 'bixbench', 'discoverybench', 'expbench', 'sciconvbench'}
JUDGE = {'model': 'openai/openai/gpt-6-astra', 'provider': 'nvidia',
         'reasoning_effort': 'low', 'max_tokens': 4096, 'timeout': 600,
         'unsupported_parameters': 'omit_and_record'}
# Match the existing direct-OpenAI Astra low grading contract. Native sampling
# settings omitted by this contract are recorded rather than silently changed.
JUDGE_PARAMETERS = ['max_tokens', 'tools', 'reasoning', 'structured_outputs']


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def disposition(native):
    if native.get('status') in ('missing_submission', 'no_submission'):
        return 'missing_submission'
    if native.get('status') in ('grading_pending', 'completed', 'scored'):
        return 'grading_pending'
    return 'execution_error'


def normalized(source, evaluation):
    if evaluation['status'] == 'missing_submission':
        return 0.0
    if evaluation['status'] != 'scored':
        return None
    m = evaluation['metrics']
    if source == 'asibench':
        value = 100 * m['score'] / m['max_score']
    elif source == 'bixbench':
        value = 100 * float(m['correct'])
    elif source == 'discoverybench':
        value = 100 * m['final_score']
    elif source == 'sciconvbench':
        value = 100 * m['FRR']
    elif source == 'expbench':
        value = m['gated_coverage_mean']
    else:
        raise ValueError(source)
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Native grade is not a finite number')
    return value


def inventory(run):
    states = [read(p) for p in sorted((run / 'episodes').glob('*/*/state.json'))]
    if len(states) != 1000 or any(r['status'] == 'running' for r in states):
        raise ValueError('Requires all 1,000 stopped collection slots')
    jobs = []
    for row in states:
        source, task, arm = (row[k] for k in ('source', 'task_id', 'arm'))
        if source not in SOURCES:
            raise ValueError(source)
        key = safe_component(source + ':' + task)
        base = run / 'episodes' / key / arm
        for attempt_dir in sorted(base.glob('attempt-*'), key=lambda p: int(p.name[8:])):
            attempt = int(attempt_dir.name[8:])
            case = attempt_dir / 'output' / (task.replace('/', '__') if source == 'expbench' else key)
            native = read(case / 'result.json')
            status = disposition(native)
            paths = [case / 'result.json']
            if status == 'grading_pending':
                if source == 'expbench':
                    paths += [case / 'task_snapshot.private.json']
                    checkpoints = [case / (s + '_design.json') for s in ('initial', 'final')
                                   if (case / (s + '_design.json')).is_file()]
                    if not checkpoints:
                        raise ValueError(f'Completed EXP attempt lacks a checkpoint: {case}')
                    paths += checkpoints
                else:
                    controller = case / 'controller'
                    paths += [controller / 'episode.private.json', controller / 'submission.json']
                    if source == 'sciconvbench':
                        paths += [case / 'conversation_log.txt', case / 'generated_prompt.txt']
                    else:
                        paths += [controller / 'submission_hashes.json']
                        submitted = read(controller / 'submission.json')
                        hashes = read(controller / 'submission_hashes.json')
                        if set(hashes) != set(submitted['artifacts']):
                            raise ValueError('Sealed artifact inventory changed')
                        for name, path in submitted['artifacts'].items():
                            if digest(path) != hashes[name]:
                                raise ValueError(f'Sealed artifact changed: {case}/{name}')
                            paths.append(Path(path))
            jobs.append({'source': source, 'task_id': task, 'arm': arm, 'trial': 1,
                         'attempt': attempt, 'selected': attempt == row['attempt'],
                         'id': f'{key}/{arm}/attempt-{attempt}', 'case': str(case),
                         'collection_status': status,
                         'input_hashes': {str(p): digest(p) for p in paths}})
    return jobs


def verify_inputs(job):
    for path, expected in job['input_hashes'].items():
        if digest(path) != expected:
            raise ValueError(f'Grading input changed: {path}')


def judge_catalog():
    """Bounded retries only for a transient, read-only model-catalog failure."""
    for attempt in range(3):
        try:
            return preflight({'judge': JUDGE})
        except RuntimeError as exc:
            if attempt == 2 or not any(f'HTTP {code}' in str(exc) for code in (429, 500, 502, 503, 504)):
                raise
            time.sleep(2 ** attempt)


def skip_policy_refusals(jobs, output, identifiers):
    """Skip explicitly selected, recorded refusals; never resend or alter them."""
    by_id = {j['id']: j for j in jobs}
    fatal_path = output / 'fatal_api.json'
    fatal = read(fatal_path) if fatal_path.exists() else None
    matched_fatal = False
    updates = []
    for identifier in identifiers:
        if identifier not in by_id:
            raise ValueError('Skip identifier is outside the frozen inventory')
        verify_inputs(by_id[identifier])
        path = output / 'attempts' / identifier / 'result.json'
        previous = read(path)
        if previous.get('retry_skipped') and previous.get('skip_reason') == 'provider_policy_refusal':
            continue
        if previous['status'] != 'grading_error':
            raise ValueError('Only a failed grade with recorded policy refusal may be skipped')
        evidence = Path(previous['directory']) / 'error.private.json'
        message = read(evidence)['message']
        if 'bio_policy' not in message:
            raise ValueError('Skip requires explicit saved bio_policy refusal evidence')
        if fatal and message == f"OpenAI HTTP {fatal['status']}: {fatal['error']}":
            matched_fatal = True
        updates.append((path, {**previous, 'retry_skipped': True,
                               'skip_reason': 'provider_policy_refusal',
                               'skip_authority': 'explicit_user_instruction',
                               'skip_evidence': str(evidence),
                               'skip_evidence_sha256': digest(evidence)}))
    if fatal and not matched_fatal:
        raise ValueError('Fatal API error does not match the explicitly skipped refusal')
    for path, result in updates:
        write(path, result)
    if fatal:
        # Preserve the original stop marker before allowing unrelated work to resume.
        archive = output / 'skipped-refusals' / (digest(fatal_path) + '.json')
        write(archive, {'fatal_api': fatal, 'skipped_ids': list(identifiers),
                        'authority': 'explicit_user_instruction',
                        'recorded_at': datetime.now(timezone.utc).isoformat()})
        fatal_path.unlink()


def grade_shared(job, destination, judge):
    case = Path(job['case'])
    episode = Episode.model_validate(read(case / 'controller/episode.private.json'))
    submission = Submission.model_validate(read(case / 'controller/submission.json'))
    adapter = load_adapter(job['source'], ROOT / 'external/sources', ROOT / 'manifests/sources.json')
    if job['source'] == 'sciconvbench':
        from personasciencebench.sciconv_runner import Service, grade_saved_dialogue
        for name in ('conversation_log.txt', 'generated_prompt.txt'):
            shutil.copyfile(case / name, destination / name)
        # The native scorer reads these names from its grading directory.
        config = {'models': {'actor': {'model': 'gcp/google/gemini-3.8-flash'}, 'judge': JUDGE}}
        native = read(case / 'result.json')
        evaluation, _ = grade_saved_dialogue(episode, submission.answer, destination, config,
                                            Service(judge), adapter.source.repository,
                                            native.get('question_limit_reached', False))
        return evaluation
    # ASI creates evaluator work alongside the sealed input directory. Copy the
    # sealed artifacts into this grading attempt so it cannot mutate raw runs.
    artifacts = {}
    for index, (name, source) in enumerate(submission.artifacts.items()):
        target = destination / 'inputs' / f'{index:04d}' / Path(source).name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if digest(target) != digest(source):
            raise ValueError('Copied submission changed')
        artifacts[name] = str(target.resolve())
    submission = submission.model_copy(update={'artifacts': artifacts})
    evaluation = adapter.evaluate(episode, submission, judge)
    evaluation.evaluator_version += '+configured-judge-v1'
    evaluation.details.update(judge_model=judge.model, judge_provider=judge.provider,
                              judge_reasoning_effort=judge.reasoning_effort)
    if judge.parameter_adaptations:
        evaluation.details.update(judge_parameter_adaptations=judge.parameter_adaptations,
                                  native_sampling_settings_preserved=False)
        evaluation.evaluator_version += '+provider-defaults-v1'
    if judge.format_adaptations:
        evaluation.details['transport_format_adaptations'] = judge.format_adaptations
        evaluation.evaluator_version += '+json-fence-v1'
    return evaluation.model_dump(mode='json')


def grade_exp(job, destination):
    from expbench.budget import Budget, Ledger
    from expbench.design_evaluation import evaluate_design
    from expbench.gateway import Gateway
    from expbench.schema import ModelSettings
    model = ModelSettings(provider=JUDGE['provider'], model=JUDGE['model'], reasoning_effort='low',
                          max_output_tokens=4096, input_usd_per_million=10, output_usd_per_million=50)
    gateway = Gateway(ResponsesJudgeTransport(), {'judge': model},
                      Ledger(Budget(None), Budget(None)), destination / 'api_calls.private.jsonl')
    stages = {}
    try:
        for stage in ('initial', 'final'):
            path = Path(job['case']) / (stage + '_design.json')
            if path.is_file():
                stages[stage] = evaluate_design(gateway, job['task_id'], read(path),
                                                destination / (stage + '_evaluation'), repeats=3)
        chosen = stages.get('final') or stages['initial']
        return {'status': 'scored', 'evaluator_version': 'released-exp-design-coverage-and-integrity-v1',
                'metrics': {'gated_coverage_mean': chosen['gated_coverage_mean'],
                            'coverage_mean': chosen['coverage_mean']},
                'details': {'stages': stages, 'selected_stage': 'final' if 'final' in stages else 'initial',
                            'judge_model': JUDGE['model'], 'judge_reasoning_effort': 'low',
                            'repeats': 3, 'original_integrity_gate': True}}
    finally:
        write(destination / 'usage.json', gateway.ledger.summary())
        gateway.transport.close()


class ResponsesJudgeTransport:
    """Keep native EXP system-only JSON messages in Responses input, not instructions."""
    mock = False

    def __init__(self):
        from personasciencebench.openai_transport import ResponsesTransport
        from personasciencebench.nvidia_transport import BASE_URL
        self.transport = ResponsesTransport(600, base_url=BASE_URL,
                                            api_key_env='NVIDIA_API_KEY', provider='nvidia')

    def complete(self, role, payload):
        if role != 'judge' or payload['model'] != JUDGE['model']:
            raise ValueError('Only the configured Astra judge may use this transport')
        request = dict(payload)
        effort = request.pop('reasoning_effort', None)
        if effort != 'low':
            raise ValueError('The final judge must use low effort')
        request['reasoning'] = {'effort': effort}
        return self.transport.complete(request)

    def close(self):
        pass


class CompletedJudgePrefix:
    """Reuse an identical successful prefix when repairing a failed grading pass."""
    def __init__(self, transport, source, destination):
        self.transport, self.source, self.destination = transport, source, destination
        self.calls = []
        for line in source.read_text().splitlines():
            call = json.loads(line)
            choice = call.get('response', {}).get('choices', [{}])[0]
            if choice.get('finish_reason') != 'stop' or not isinstance(choice.get('message', {}).get('content'), str):
                break
            self.calls.append(call)
        self.index = 0

    def complete_recorded(self, payload, record, *, role):
        if self.index >= len(self.calls):
            return self.transport.complete_recorded(payload, record, role=role)
        call = self.calls[self.index]
        if role != 'judge' or payload != call['request']:
            raise ValueError('Cached judge request differs; refusing to substitute a judgement')
        with self.destination.open('a') as stream:
            stream.write(json.dumps({'source': str(self.source), 'source_sha256': digest(self.source),
                                     'record_index': self.index, 'request_identical': True,
                                     'additional_model_call': False}) + '\n')
        self.index += 1
        return call['response']


def grade_one(job, output, retry_errors=False, implementation_version=None):
    base = output / 'attempts' / job['id']
    record_path = base / 'result.json'
    if record_path.exists():
        existing = read(record_path)
        if existing.get('retry_skipped') or existing['status'] != 'grading_error' or not retry_errors:
            return existing
    verify_inputs(job)
    disposition_record = {k: job[k] for k in ('source', 'task_id', 'arm', 'trial', 'attempt', 'selected', 'id')}
    disposition_record.update(input_hashes=job['input_hashes'], judge=JUDGE,
                              implementation_version=implementation_version,
                              actor_runs_repeated=0, simulator_runs_repeated=0)
    if job['collection_status'] != 'grading_pending':
        status = job['collection_status']
        result = {**disposition_record, 'status': status, 'evaluation': {'status': status, 'metrics': {}},
                  'normalized_score': 0.0 if status == 'missing_submission' else None, 'judge_calls': 0}
        write(record_path, result)
        return result
    if (output / 'fatal_api.json').exists():
        return {**disposition_record, 'status': 'grading_pending', 'normalized_score': None,
                'reason': 'Stopped after fatal API configuration error'}
    number = 1
    while (base / f'grade-{number}').exists():
        number += 1
    destination = base / f'grade-{number}'
    destination.mkdir(parents=True)
    destination.chmod(0o700)
    def log(call):
        if call['role'] != 'judge':
            raise ValueError('Posthoc grading cannot call actor/simulator')
        with (destination / 'api_calls.private.jsonl').open('a') as stream:
            stream.write(json.dumps(call, ensure_ascii=False) + '\n')
    judge = OpenRouterClient(**JUDGE, role='judge', record=log, supported_parameters=JUDGE_PARAMETERS)
    # The native shared graders may make several calls before a transport or
    # parse error. Retain their completed prefix, rather than rolling it again.
    if retry_errors and record_path.exists() and job['source'] != 'expbench':
        previous = read(record_path)
        cached = Path(previous['directory']) / 'api_calls.private.jsonl'
        if previous['judge'] != JUDGE or previous['input_hashes'] != job['input_hashes']:
            raise ValueError('Cannot reuse grades after judge configuration or inputs change')
        if cached.exists():
            judge.nvidia = CompletedJudgePrefix(judge.nvidia, cached, destination / 'api_replay.private.jsonl')
    result = {**disposition_record, 'grade_attempt': number, 'directory': str(destination),
              'started_at': datetime.now(timezone.utc).isoformat()}
    try:
        evaluation = grade_exp(job, destination) if job['source'] == 'expbench' else grade_shared(job, destination, judge)
        score = normalized(job['source'], evaluation)
        status = evaluation['status'] if evaluation['status'] in ('scored', 'missing_submission') else 'grading_error'
        result.update(status=status, evaluation=evaluation, normalized_score=score)
    except Exception as exc:
        # No API keys/request bodies in summaries; detailed responses stay private.
        result.update(status='grading_error', error_type=type(exc).__name__, normalized_score=None)
        message = str(exc)
        for key in ('OPENAI_API_KEY', 'NVIDIA_API_KEY', 'OPENROUTER_API_KEY'):
            if os.getenv(key):
                message = message.replace(os.environ[key], '[REDACTED]')
        write(destination / 'error.private.json', {'error_type': type(exc).__name__, 'message': message})
    verify_inputs(job)
    calls_path = destination / 'api_calls.private.jsonl'
    calls = [json.loads(line) for line in calls_path.read_text().splitlines()] if calls_path.exists() else []
    result['judge_calls'] = sum('response' in c for c in calls)
    result['finished_at'] = datetime.now(timezone.utc).isoformat()
    write(destination / 'result.json', result)
    write(record_path, result)
    print(json.dumps({k: result[k] for k in ('source', 'task_id', 'arm', 'attempt', 'status', 'normalized_score', 'judge_calls')}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--canary', action='store_true', help='Grade one saved submission per benchmark; resume reuses these grades')
    parser.add_argument('--retry-errors', action='store_true')
    parser.add_argument('--skip-policy-refusal', action='append', default=[], metavar='ATTEMPT_ID',
                        help='Explicitly skip a saved bio_policy refusal and archive its global stop marker')
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error('workers must be between 1 and 16')
    os.umask(0o077)
    load_env(args.env_file)
    run, output = args.run_dir.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ['PSB_FATAL_API_FILE'] = str(output / 'fatal_api.json')
    os.environ['PSB_NVIDIA_EMPTY_LENGTH_RETRIES'] = '0'
    with (output / 'grading.lock').open('a') as lock, (run / 'coordinator.lock').open('a') as collection_lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(collection_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        jobs = inventory(run)
        contract = {'run_dir': str(run), 'judge': JUDGE, 'judge_supported_parameters': JUDGE_PARAMETERS,
                    'policy': 'Grade every submitted original/repair attempt once; latest authorized collection endpoints retained; no best-score selection',
                    'actor_runs_repeated': 0, 'simulator_runs_repeated': 0, 'jobs': jobs}
        path = output / 'inventory.json'
        if path.exists() and read(path) != contract:
            raise ValueError('Frozen grading inventory/configuration changed; use a new output directory')
        if not path.exists():
            write(path, contract)
        print(json.dumps({'attempts': len(jobs), 'selected_slots': sum(j['selected'] for j in jobs),
                          'all_attempt_dispositions': dict(Counter(j['collection_status'] for j in jobs))}), flush=True)
        if args.prepare_only:
            return
        if args.skip_policy_refusal:
            skip_policy_refusals(jobs, output, args.skip_policy_refusal)
        catalog = judge_catalog()
        if catalog['judge']['deployment_model'] != 'openai/gpt-6-astra' or catalog['judge']['accounting_base_model'] != 'gpt-6-astra':
            raise ValueError('Judge route does not identify the intended Astra deployment')
        write(output / 'catalog.json', catalog)
        paths = ['scripts/grade_collection.py'] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'src').rglob('*.py'))
        source_hashes = {name: digest(ROOT / name) for name in paths}
        version = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
        for name in paths:
            target = output / 'source' / version / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and digest(target) != digest(ROOT / name):
                raise ValueError('Grading implementation changed; start a separate grading version')
            if not target.exists():
                shutil.copyfile(ROOT / name, target)
        if (output / 'runtime.json').exists():
            previous = read(output / 'runtime.json')
            write(output / 'runtime-history' / (digest(output / 'runtime.json') + '.json'), previous)
        write(output / 'runtime.json', {'git_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                                       'implementation_version': version, 'sources': source_hashes})
        if args.canary:
            picked = {}
            for job in jobs:
                if job['collection_status'] == 'grading_pending' and job['selected']:
                    picked.setdefault(job['source'], job)
            jobs = list(picked.values())
            if set(picked) != SOURCES:
                raise ValueError('Canary needs one submission from each benchmark')
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = []
            for future in as_completed([pool.submit(grade_one, j, output, args.retry_errors, version) for j in jobs]):
                results.append(future.result())
                write(output / ('canary-progress.json' if args.canary else 'progress.json'),
                      {'finished': len(results), 'requested': len(jobs), 'statuses': dict(Counter(r['status'] for r in results)),
                       'selected_statuses': dict(Counter(r['status'] for r in results if r['selected']))})
        write(output / ('canary-results.json' if args.canary else 'results.json'), sorted(results, key=lambda r: r['id']))
        if any(r['status'] in ('grading_error', 'grading_pending') for r in results):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
