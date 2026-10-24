#!/usr/bin/env python3
"""Merge independently recorded native grades into a new collection bundle.

The source bundle and raw collection remain untouched. Original collection-only
indices are retained, as are every grading attempt and final judge responses.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


exporter = module('export_collection_bundle')
validator = module('validate_collection_bundle')


def read(path):
    return json.loads(Path(path).read_text())


def key(row):
    return row['source'], row['task_id'], row['arm'], int(row.get('trial', 1)), int(row.get('attempt', row.get('selected_attempt', 0)))


def finite_evidence(value):
    """Make native diagnostic JSON portable, recording every non-finite value."""
    replaced = {}
    def visit(item, pointer):
        if isinstance(item, float) and not math.isfinite(item):
            replaced[pointer] = repr(item)
            return None
        if isinstance(item, dict):
            return {k:visit(v, pointer+'/'+str(k).replace('~','~0').replace('/','~1')) for k,v in item.items()}
        if isinstance(item, list):
            return [visit(v, pointer+'/'+str(i)) for i,v in enumerate(item)]
        return item
    return visit(value, ''), replaced


def native_score(source, grade):
    if grade['status'] == 'missing_submission':
        return 0.0
    if grade['status'] != 'scored':
        return None
    m = grade['evaluation']['metrics']
    field = {'asibench': 'score', 'bixbench': 'correct', 'discoverybench': 'final_score',
             'sciconvbench': 'FRR', 'expbench': 'gated_coverage_mean'}[source]
    return float(m[field])


def validate_grades(bundle):
    base = validator.validate(bundle)
    delivery = read(bundle / 'delivery.json')
    rows = list(csv.DictReader((bundle / 'episodes.csv').open()))
    grades = [json.loads(line) for line in gzip.open(bundle / 'judging/all-attempts.jsonl.gz', 'rt')]
    mapped = {key(g): g for g in grades}
    if len(mapped) != len(grades) or len(grades) != delivery['attempts']:
        raise ValueError('Grading history does not cover every collection attempt exactly once')
    for row in rows:
        grade = mapped[key(row)]
        if not grade['selected'] or row['evaluation_status'] != grade['status']:
            raise ValueError('Selected grade mapping differs from the collection endpoint')
        score = None if row['normalized_score'] == '' else float(row['normalized_score'])
        if score != grade['normalized_score']:
            raise ValueError('Exported score differs from the recorded native grade')
        if grade['status'] in ('grading_error', 'grading_pending', 'execution_error') and score is not None:
            raise ValueError('Unavailable grades cannot be converted to zero')
        if grade['actor_runs_repeated'] or grade['simulator_runs_repeated']:
            raise ValueError('Judging must not rerun actor or simulator')
    calls = [json.loads(line) for line in gzip.open(bundle / 'judging/judgements.jsonl.gz', 'rt')]
    if len(calls) != delivery['judge_calls'] or any(c['role'] != 'judge' for c in calls):
        raise ValueError('Judge usage count/role mismatch')
    counts = Counter(row['evaluation_status'] for row in rows)
    complete = not any(counts[s] for s in ('grading_error', 'grading_pending'))
    if delivery['grading_complete'] != complete:
        raise ValueError('Incorrect grading completeness label')
    return {**base, 'grading_complete': complete, 'judge_responses': len(calls)}


def export(collection, grading, output, secrets):
    collection, grading, output = collection.resolve(), grading.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Refusing to overwrite a bundle')
    validator.validate(collection)
    grades = read(grading / 'results.json')
    original_delivery = read(collection / 'delivery.json')
    if len(grades) != original_delivery['attempts']:
        raise ValueError('Grading run has not accounted for every retained attempt')
    mapped = {key(g): g for g in grades}
    if len(mapped) != len(grades):
        raise ValueError('Duplicate graded attempt')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.graded-export-', dir=output.parent))
    raw_run = Path(read(grading / 'inventory.json')['run_dir'])
    def portable(value):
        if isinstance(value, str):
            return value.replace(str(grading), '@GRADING_RUN').replace(str(raw_run), '@RAW_RUN').replace(str(ROOT), '@SOURCE_REPOSITORY')
        if isinstance(value, dict):
            return {k: portable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [portable(v) for v in value]
        return value
    def save(path, data):
        exporter.write(staging / path, portable(data))
    def gzlines(path, values):
        destination = staging / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as zipped:
            for value in values:
                zipped.write((json.dumps(portable(value), ensure_ascii=False) + '\n').encode())
    try:
        shutil.copytree(collection, staging, dirs_exist_ok=True)
        baseline = staging / 'judging/collection-only'
        for name in ('episodes.csv', 'delivery.json', 'evaluations/metrics.jsonl', 'traces/final-results.json', 'README.md', 'bundle_manifest.json'):
            target = baseline / ('original-manifest.json' if name == 'bundle_manifest.json' else name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(collection / name, target)
        rows = list(csv.DictReader((collection / 'episodes.csv').open()))
        for row in rows:
            grade = mapped[key(row)]
            row['evaluation_status'] = grade['status']
            row['native_score'] = native_score(row['source'], grade)
            row['normalized_score'] = grade['normalized_score']
            row['exclusion_reason'] = {'grading_error': 'Native final grading failed; see judging records',
                                      'grading_pending': 'Final grading has not completed',
                                      'execution_error': 'Actor/simulator execution error; no final grade available'}.get(grade['status'], '')
            if grade.get('retry_skipped'):
                row['exclusion_reason'] = 'Provider policy refusal; skipped at user request; score unavailable'
        with (staging / 'episodes.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        metrics = [json.loads(line) for line in (collection / 'evaluations/metrics.jsonl').read_text().splitlines()]
        for row in metrics:
            grade = mapped[key(row)]
            row.update(disposition=grade['status'], evaluation=grade.get('evaluation', {'status': grade['status'], 'metrics': {}}),
                       judge=grade['judge'], grading_attempt=grade.get('grade_attempt'),
                       grading_record='judging/all-attempts.jsonl.gz')
        (staging / 'evaluations/metrics.jsonl').write_text(''.join(json.dumps(portable(r), ensure_ascii=False) + '\n' for r in metrics))
        final = read(collection / 'traces/final-results.json')
        for row in final:
            grade = mapped[key(row)]
            row['grading_disposition'] = grade['status']
            row['posthoc_grading'] = {'grade_attempt': grade.get('grade_attempt'), 'judge': grade['judge'],
                                     'normalized_score': grade['normalized_score'], 'record': 'judging/all-attempts.jsonl.gz'}
            if grade['status'] in ('scored', 'missing_submission'):
                native = row['native_results'][0]
                native['collection_status'] = native['status']
                native['evaluation'] = grade['evaluation']
                if row['source'] == 'expbench' and grade['status'] == 'scored':
                    native.update(grade['evaluation']['details']['stages'])
                elif grade['status'] == 'scored':
                    native['status'] = 'scored'
        save('traces/final-results.json', final)
        input_receipts = []
        for job in read(grading/'inventory.json')['jobs']:
            mapped_inputs = []
            for original, expected in job['input_hashes'].items():
                source = Path(original)
                if exporter.sha(source) != expected:
                    raise ValueError(f'Grading source changed after evaluation: {job["id"]}/{source.name}')
                record = {'raw_source':portable(original), 'sha256':expected}
                # These native SciConv inputs and artifact manifests supplement
                # the existing snapshot/submission maps without inventing submissions.
                if source.name in ('conversation_log.txt', 'generated_prompt.txt', 'submission_hashes.json'):
                    relative = 'grading_inputs/native/' + job['id'] + '/' + source.name
                    exporter.copy_checked(source, staging/relative)
                    record['bundle_path'] = relative
                mapped_inputs.append(record)
            input_receipts.append({'id':job['id'], 'inputs':mapped_inputs})
        save('judging/verified-inputs.json', input_receipts)
        gzlines('judging/all-attempts.jsonl.gz', grades)
        for name in ('inventory.json', 'runtime.json', 'catalog.json', 'canary-results.json', 'progress.json', 'grade-reuse.json', 'previous-inventory.json', 'discovery-cap-repair-4096.json'):
            if (grading / name).is_file():
                save('judging/provenance/' + name, read(grading / name))
        for directory in ('source', 'runtime-history'):
            for source in sorted((grading / directory).rglob('*')):
                if source.is_file() and source.suffix in ('.py', '.json'):
                    target = staging / 'judging/provenance' / source.relative_to(grading)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if source.suffix == '.json':
                        exporter.write(target, portable(read(source)))
                    else:
                        exporter.copy_checked(source, target)
        for name in ('scripts/export_graded_collection.py', 'scripts/export_collection_bundle.py',
                     'scripts/validate_collection_bundle.py', 'configs/main_run/selection.csv',
                     'tests/test_posthoc_grading.py'):
            target = staging / 'judging/provenance' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            exporter.copy_checked(ROOT / name, target)
        judgements, replays = [], []
        for path in sorted((grading / 'attempts').glob('*/*/*/grade-*')):
            job_id = str(path.parent.relative_to(grading / 'attempts'))
            # Keep native verdicts and grade-attempt history. Large temporary
            # evaluator input copies and private API prompts are not exported.
            for source in sorted(path.rglob('*.json')):
                relative = source.relative_to(path)
                if source.name.endswith('.private.json'):
                    continue
                if 'inputs' in relative.parts and source.name != 'native_score.json':
                    continue
                relative_output = 'judging/attempts/' + str(source.relative_to(grading / 'attempts'))
                value, nonfinite = finite_evidence(read(source))
                save(relative_output, value)
                if source.name == 'native_score.json':
                    save(relative_output + '.export-receipt.json', {
                        'source_sha256':exporter.sha(source), 'nonfinite_values_replaced_with_null':nonfinite,
                        'policy':'Retain non-finite diagnostics explicitly; never convert unavailable scores to zero'})
            api = path / 'api_calls.private.jsonl'
            replay_path = path / 'api_replay.private.jsonl'
            if replay_path.exists():
                for line in replay_path.read_text().splitlines():
                    replays.append({'id': job_id, 'grading_attempt': path.name, **json.loads(line)})
            request = None
            if api.exists():
                for line_number, line in enumerate(api.read_text().splitlines(), 1):
                    call = json.loads(line)
                    if call.get('phase') == 'request':
                        request = call['payload']
                    if 'response' not in call:
                        continue
                    response = call['response']
                    original_request = call.get('request', request)
                    wire_request = response.get('_responses_request', original_request)
                    choice = response.get('choices', [{}])[0]
                    judgements.append({'id': job_id, 'grading_attempt': path.name, 'role': 'judge',
                                       'source_api_sha256': exporter.sha(api), 'source_line': line_number,
                                       'request_sha256': hashlib.sha256(json.dumps(wire_request, sort_keys=True).encode()).hexdigest(),
                                       'response_id': response.get('id'), 'model': response.get('model'), 'usage': response.get('usage', {}),
                                       'finish_reason': choice.get('finish_reason'),
                                       'content': choice.get('message', {}).get('content'),
                                       'effective_settings': {k:v for k,v in (wire_request or {}).items() if k in ('model','max_tokens','max_output_tokens','reasoning_effort','reasoning')},
                                       'requested_native_settings': call.get('requested_native_settings'),
                                       'omitted_native_settings': call.get('omitted_native_settings')})
            # Native ASI bridge uses separate response files. Preserve their visible
            # verdict/usage and effective controller settings without private reasoning.
            seen_ids = {r.get('response_id') for r in judgements if r.get('response_id')}
            for response_path in sorted(path.glob('inputs/*/judge_bridge/*.response.json')):
                wrapper = read(response_path)
                response = wrapper.get('response', {})
                if response.get('id') and response['id'] in seen_ids:
                    continue
                request_path = response_path.with_name(response_path.name.replace('.response.json', '.request.json'))
                request = read(request_path)
                choice = response.get('choices', [{}])[0]
                config = read(response_path.parent/'config.json')
                judgements.append({'id':job_id, 'grading_attempt':path.name, 'role':'judge',
                    'transport':'asi_native_bridge', 'source_api_sha256':exporter.sha(response_path),
                    'source_request_sha256':exporter.sha(request_path),
                    'response_id':response.get('id'), 'model':response.get('model'),
                    'usage':response.get('usage', {}), 'finish_reason':choice.get('finish_reason'),
                    'content':choice.get('message', {}).get('content'), 'error':wrapper.get('error'),
                    'requested_native_settings':{k:v for k,v in request.items() if k != 'messages'},
                    'effective_settings':config})
                save('judging/attempts/' + str(response_path.parent.relative_to(grading/'attempts')) + '/config.json', config)
                adaptations = response_path.parent/'adaptations.jsonl'
                if adaptations.exists():
                    save('judging/attempts/' + str(response_path.parent.relative_to(grading/'attempts')) + '/adaptations.json',
                         [json.loads(line) for line in adaptations.read_text().splitlines()])
        gzlines('judging/judgements.jsonl.gz', judgements)
        gzlines('judging/replays.jsonl.gz', replays)
        counts = dict(Counter(row['evaluation_status'] for row in rows))
        grading_complete = not any(counts.get(s, 0) for s in ('grading_pending', 'grading_error'))
        delivery = {**original_delivery, 'status': 'complete_graded_collection' if grading_complete and not counts.get('execution_error') else 'partial_graded_checkpoint',
                    'selected_statuses': counts, 'judge_calls': len(judgements), 'grading_complete': grading_complete,
                    'unresolved_execution_errors': counts.get('execution_error', 0),
                    'unresolved_grading_errors': counts.get('grading_error', 0),
                    'policy_refusals_skipped': sum(bool(g.get('retry_skipped')) for g in grades if g['selected']),
                    'ready_to_publish': grading_complete and not counts.get('execution_error'),
                    'final_judge': {'model': 'GPT-6 Astra', 'reasoning_effort': 'low'},
                    'collection_only_manifest_sha256': exporter.sha(collection / 'bundle_manifest.json')}
        save('delivery.json', delivery)
        unresolved = []
        for selected in final:
            grade = mapped[key(selected)]
            if grade['status'] not in ('execution_error','grading_error','grading_pending'):
                continue
            native = selected['native_results'][0]
            unresolved.append({k:grade[k] for k in ('source','task_id','arm','trial','attempt','status')} | {
                'retry_skipped':bool(grade.get('retry_skipped')),
                'grading_errors':grade.get('evaluation',{}).get('errors',[]),
                'execution_error':native.get('error') or native.get('actor',{}).get('error'),
                'normalized_score':None})
        save('judging/unresolved-cases.json', unresolved)
        readme = (collection / 'README.md').read_text()
        rest = readme[readme.index('## Commands'):]
        rest = rest.replace('requires pending native evaluation with the preserved task facts.', 'uses the recorded native entity_recovery metric with the preserved task facts.')
        rest = rest.replace('Scores remain null until the receiving team performs native/Astra grading.',
                            'Final native/Astra grades are in `episodes.csv` and `evaluations/metrics.jsonl`. Unavailable scores remain null.')
        header = f'''# {readme.splitlines()[0].lstrip('# ')}

Status: **{delivery['status']}**. All 1,000 frozen slots and all {len(grades)} original/repair attempts are retained.
Selected final dispositions: `{json.dumps(counts)}`. Final grading complete: **{grading_complete}**.

Actor and simulator: **{original_delivery.get('model_label', readme.splitlines()[0].lstrip('# ').split(' — trial')[0])}**. Final judge: **GPT-6 Astra, low effort**.
Exact collection role IDs/settings: `{json.dumps(read(collection/'provenance/run/manifest.json')['role_models'])}`.
Actual posthoc judge routing/settings: `{json.dumps(read(grading/'inventory.json')['judge'])}`.
(The collection judge configuration was deferred; the posthoc route above performed final grading.)
No actor/simulator episodes were rerun for grading. Native rubrics, scoring and EXP integrity gates were retained.
Grading evaluated saved submissions; {counts.get('execution_error', 0)} unresolved execution errors remain unavailable.
Policy refusals skipped at user request: **{delivery['policy_refusals_skipped']}**. Their scores remain unavailable, not zero.

`judging/all-attempts.jsonl.gz` maps every original/repair attempt to its native evaluation.
`judging/judgements.jsonl.gz` retains final judge text and token usage, without private reasoning or API prompt bodies.
`judging/collection-only/` preserves the original ungraded indices and checksum manifest.
The original collection history in `repairs/` is unchanged. Final scores use the same selected attempts, never best-score selection.
Exact judge routing, implementation snapshots and effective settings are recorded under `judging/provenance/`.
All posthoc API calls were judge calls; actor and simulator calls repeated: **0**.
`judging/verified-inputs.json` verifies every original grading input hash;
`grading_inputs/native/` preserves native conversation/specification text and artifact manifests.
Non-finite native diagnostics are represented as null with their original values
and source checksum in adjacent `native_score.json.export-receipt.json` files.

Grading command (using the preserved raw run and the recorded runtime):
```bash
.venv/bin/python scripts/grade_collection.py --run-dir /path/to/raw-run --output /path/to/raw-run/grading/astra-low-v1 --env-file /path/to/.env --workers 4
```

'''
        if (grading/'discovery-cap-repair-4096.json').exists():
            header += '''Grading repair: 15 failed DiscoveryBench cases were retried with the native
250-token judge output cap raised to **4,096**; all 15 now have scores. Previously
successful grades were retained byte-for-byte. The target list, evaluator version
and actual request settings are preserved. This is a documented grading-setting
repair, not a change to scientific rubrics. One ASI metadynamics numerical evaluator
returned a non-finite value; its overall score remains unavailable even though its
model-judge component succeeded. Historical failures are retained.

Exact grading sequence (paths/env/workers as above):
1. Initial: `--output .../grading/astra-low-v1`.
2. Collection-repair grading: `--output .../grading/astra-low-repaired-v2 --reuse-grades-from .../grading/astra-low-v1 --retry-errors`.
3. Failed-case cap repair: `--output .../grading/astra-low-judge-cap4096-v3 --reuse-grades-from .../grading/astra-low-repaired-v2 --repair-discovery-token-cap 4096`.

'''
        unresolved_text = '\n## Unresolved selected cases\n\n'
        unresolved_text += 'Full error messages and selected attempt keys: `judging/unresolved-cases.json`.\n\n'
        unresolved_text += '| Benchmark | Task | Persona | Attempt | Status |\n|---|---|---|---:|---|\n'
        for case in unresolved:
            unresolved_text += f"| {case['source']} | {case['task_id']} | {case['arm']} | {case['attempt']} | {case['status']} |\n"
        skipped = [g['id'] for g in grades if g.get('retry_skipped')]
        if skipped:
            unresolved_text += '\nGrading resume used `--retry-errors` with one `--skip-policy-refusal ID` flag for each recorded skipped attempt:\n\n'
            unresolved_text += '\n'.join('- `' + identifier + '`' for identifier in skipped) + '\n'
        (staging / 'README.md').write_text(header + rest + unresolved_text)
        (staging / 'bundle_manifest.json').unlink()
        files = {}
        for path in sorted(staging.rglob('*')):
            if not path.is_file():
                continue
            relative = str(path.relative_to(staging))
            raw = path.read_bytes()
            exporter.scan_bytes(gzip.decompress(raw) if path.suffix == '.gz' else raw, secrets, relative)
            if len(raw) > 50 * 1024 * 1024:
                raise ValueError(f'File requires splitting: {relative}')
            files[relative] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        exporter.write(staging / 'bundle_manifest.json', {'schema_version': 1, 'files': files})
        result = validate_grades(staging)
        staging.rename(output)
        return result
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate', type=Path, help='Validate an exported graded bundle without model access')
    parser.add_argument('--collection', type=Path)
    parser.add_argument('--grading-dir', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.validate:
        print(json.dumps(validate_grades(args.validate.resolve()), indent=2))
        return
    if not all((args.collection, args.grading_dir, args.output, args.env_file)):
        parser.error('Export requires --collection, --grading-dir, --output, and --env-file')
    from personasciencebench.inference import load_env
    load_env(args.env_file)
    secrets = tuple(v.encode() for k, v in os.environ.items() if k in ('OPENAI_API_KEY', 'NVIDIA_API_KEY', 'OPENROUTER_API_KEY') and v)
    print(json.dumps(export(args.collection, args.grading_dir, args.output, secrets), indent=2))


if __name__ == '__main__':
    main()
