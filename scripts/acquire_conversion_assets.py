#!/usr/bin/env python3
"""Acquire pinned Bix capsules and ASI instances; fail on incomplete acquisition."""
import argparse
import csv
import json
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from personasciencebench.adapters.base import sha256
from personasciencebench.adapters.bixbench import DATASET_REVISION
from personasciencebench.registry import load_adapter

ROOT = Path(__file__).resolve().parents[1]


def selected_tasks(selection, benchmark):
    with Path(selection).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    tasks = sorted({r['task_id'] for r in rows if r['source'] == benchmark})
    if not tasks:
        raise ValueError(f'No {benchmark} questions in selection: {selection}')
    return tasks


def bixbench(tasks=None):
    adapter = load_adapter('bixbench', ROOT / 'external/sources', ROOT / 'manifests/sources.json')
    rows = adapter._rows()
    if tasks is not None:
        missing = set(tasks) - {r['question_id'] for r in rows}
        if missing:
            raise ValueError(f'Unknown BixBench questions: {sorted(missing)}')
        rows = [r for r in rows if r['question_id'] in set(tasks)]
    # Questions in the same capsule share their scientific inputs.
    capsules = {r['capsule_uuid']: r['question_id'] for r in rows}
    from huggingface_hub import HfApi
    info = HfApi().dataset_info('futurehouse/BixBench', revision=DATASET_REVISION, files_metadata=True)
    files = {s.rfilename: s for s in info.siblings}
    out = ROOT / 'data/conversion_catalog'
    out.mkdir(parents=True, exist_ok=True)
    adapter.source.assets.mkdir(parents=True, exist_ok=True)

    def one(item):
        capsule, task = item
        name = f'CapsuleFolder-{capsule}.zip'
        target = adapter.source.assets / name
        result = {'capsule': capsule, 'archive': name, 'revision': DATASET_REVISION}
        try:
            meta = files[name]
            expected = meta.lfs.sha256 if meta.lfs else None
            if not expected:
                raise ValueError('Pinned capsule metadata has no SHA-256 digest')
            result['expected_sha256'] = expected
            if not target.exists():
                partial = target.with_suffix('.zip.download')
                with urllib.request.urlopen(
                    f'https://huggingface.co/datasets/futurehouse/BixBench/resolve/{DATASET_REVISION}/{name}',
                    timeout=180,
                ) as response, partial.open('wb') as stream:
                    shutil.copyfileobj(response, stream, 1024 * 1024)
                if sha256(partial) != expected:
                    raise ValueError('Downloaded capsule hash mismatch')
                partial.replace(target)
            if sha256(target) != expected:
                raise ValueError('Acquired capsule hash mismatch')
            result['archive_sha256'] = sha256(target)
            result['input_files'] = len(adapter.prepare_assets(task))
            result['status'] = 'prepared'
        except Exception as error:
            result.update(status='blocked', error_type=type(error).__name__, error=str(error))
        return result

    results = []
    report = out / 'bixbench_acquisition.json'
    with ThreadPoolExecutor(max_workers=6) as pool:
        for future in as_completed([pool.submit(one, item) for item in capsules.items()]):
            results.append(future.result())
            report.write_text(json.dumps(results, indent=2) + '\n')
            print(results[-1]['capsule'], results[-1]['status'], flush=True)
    failed = [r for r in results if r['status'] != 'prepared']
    print(json.dumps({'capsules': len(results), 'prepared': len(results) - len(failed)}))
    if failed:
        raise RuntimeError(f'{len(failed)} BixBench capsules failed; inspect {report} and rerun acquisition')
    return results


def asibench(tasks=None):
    from ai4sci_bench.hf.pull import pull_instances
    manifest = json.loads((ROOT / 'manifests/sources.json').read_text())['asibench']
    destination = ROOT / 'external/sources/_assets/asibench/instances'
    result = pull_instances('seed31415', output_dir=destination, tasks=tasks, revision=manifest['dataset_revision'])
    present = set(result.instance_ids) | set(result.skipped)
    requested = tasks if tasks is not None else sorted({i.split('__', 1)[0] for i in present})
    if not requested:
        raise RuntimeError('ASI-Bench acquisition returned no instances')
    missing = []
    for task in requested:
        instance = destination / (task + '__seed31415')
        if not (instance / 'prompt_b3.md').is_file() or not (instance / 'data').is_dir() or not (instance / 'reference').is_dir():
            missing.append(task)
    if missing:
        raise RuntimeError(f'Incomplete ASI-Bench instances (prompt/data/reference missing): {missing}')
    print(json.dumps({'acquired': result.instance_ids, 'cached': result.skipped, 'verified_tasks': len(requested)}))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('benchmark', choices=['bixbench', 'asibench'])
    subset = parser.add_mutually_exclusive_group()
    subset.add_argument('--tasks', nargs='+', help='Only acquire these source task IDs')
    subset.add_argument('--selection', type=Path, help='Only acquire this benchmark’s questions from a selection CSV')
    args = parser.parse_args()
    tasks = selected_tasks(args.selection, args.benchmark) if args.selection else args.tasks
    (bixbench if args.benchmark == 'bixbench' else asibench)(tasks)


if __name__ == '__main__':
    main()
