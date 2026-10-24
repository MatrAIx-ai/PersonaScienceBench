#!/usr/bin/env python3
"""Package frozen task metadata, without rerunning any conversion or inference."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('asibench', 'bixbench', 'discoverybench', 'expbench', 'sciconvbench')
DEFAULT = ROOT / 'configs/main_run/frozen/astra-20260929-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def component(value):
    return (re.sub(r'[^A-Za-z0-9_.-]', '_', value).strip('.')[:100] or 'episode') + '-' + sha(value.encode())[:12]


def build(prepared, output):
    rows = list(csv.DictReader((ROOT / 'configs/main_run/selection.csv').open()))
    files, assets, required = {}, [], []
    old_root = old_prepared = None
    for index, row in enumerate(rows):
        key = component(row['source'] + ':' + row['task_id'])
        task = prepared / key
        if row['source'] == 'expbench':
            files[key + '/tasks.jsonl'] = (task / 'tasks.jsonl').read_text()
            assert json.loads(files[key + '/tasks.jsonl'])['task_id'] == row['task_id']
            continue
        manifest = json.loads((task / 'pilot_manifest.json').read_text())
        assert len(manifest['cases']) == 1
        record = manifest['cases'][0]
        assert record['benchmark'] == row['source'] and record['source_task_id'] == row['task_id']
        assert record['assets_ready']
        original_package = Path(record['package'])
        this_root = str(Path(manifest['source_root']).parent.parent)
        this_prepared = str(original_package.parent.parent)
        if old_root is None:
            old_root, old_prepared = this_root, this_prepared
        assert (old_root, old_prepared) == (this_root, this_prepared)
        package = task / original_package.name
        package_rel = Path(key) / original_package.name
        files[key + '/pilot_manifest.json'] = (task / 'pilot_manifest.json').read_text()
        for name in ['actor/task.json', 'controller/episode.private.json',
                     'controller/researcher.private.json', 'controller/evaluator.private.json',
                     'controller/mounts.json', 'controller/readiness.json']:
            files[(package_rel / name).as_posix()] = (package / name).read_text()
        episode = json.loads(files[(package_rel / 'controller/episode.private.json').as_posix()])
        by_id = {a['id']: a for a in episode['assets']}
        for mount in json.loads(files[(package_rel / 'controller/mounts.json').as_posix()]):
            asset = by_id[mount['asset_id']]
            source = Path(asset['source_path']).relative_to(old_root)
            for relative, digest in mount['sha256_inventory'].items():
                suffix = Path() if relative == '.' else Path(relative)
                assets.append({'destination': (package_rel / mount['prepared_path'] / suffix).as_posix(),
                               'source': (source / suffix).as_posix(), 'sha256': digest,
                               'acquisition': asset.get('acquisition')})
        for asset in episode['assets']:
            if asset['visibility'] != 'actor' and asset.get('required', True):
                required.append({'path': Path(asset['source_path']).relative_to(old_root).as_posix(),
                                 'kind': asset['kind'], 'sha256': asset.get('sha256')})
        instance = episode.get('evaluator', {}).get('reference', {}).get('instance_dir')
        if instance:
            required.append({'path': Path(instance).relative_to(old_root).as_posix(), 'kind': 'directory', 'sha256': None})
        if (index + 1) % 40 == 0:
            print(f'Collected {index + 1}/200 selected tasks', flush=True)
    assert len(rows) == 200
    raw_exp = (ROOT / 'data/exp_bench/tasks.jsonl').read_bytes()
    for path, value in files.items():
        if path.endswith('/tasks.jsonl'):
            assert json.loads(value)['provenance']['source_sha256'] == sha(raw_exp)
    payload = {'schema_version': 1, 'old_root': old_root, 'old_prepared': old_prepared,
               'files': files, 'assets': assets,
               'required_external': list({r['path']: r for r in required}.values()),
               'exp_source': raw_exp.decode(),
               'reference_code_hashes': json.loads((prepared.parent / 'code.1957850.json').read_text())}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    # Controller-private task labels are intentional; credentials are not.
    assert not re.search(rb'(?:ghp_[A-Za-z0-9]{20,}|sk-(?:proj-|or-v1-)[A-Za-z0-9_-]{20,}|-----BEGIN .*PRIVATE KEY-----)', data)
    compressed = gzip.compress(data, compresslevel=9, mtime=0)
    sources = json.loads((ROOT / 'manifests/sources.json').read_text())
    selection = (ROOT / 'configs/main_run/selection.csv').read_bytes()
    manifest = {'schema_version': 1, 'preparation_id': 'astra-20260929-v1',
                'archive': 'preparation.json.gz', 'sha256': sha(compressed),
                'bytes': len(compressed), 'uncompressed_bytes': len(data),
                'questions': 200, 'source_counts': {s: sum(r['source'] == s for r in rows) for s in SOURCES},
                'selection_sha256': sha(selection), 'metadata_files': len(files),
                'actor_asset_copies': len(assets), 'unique_actor_assets': len({a['sha256'] for a in assets}),
                'exp_source_sha256': sha(raw_exp),
                'metadata_sha256': {p: sha(text.encode()) for p, text in files.items()},
                'sources': {s: {k: sources[s].get(k) for k in ['repository_url', 'revision', 'dataset_revision']} for s in SOURCES if s != 'expbench'}}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'preparation.json.gz').write_bytes(compressed)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ['metadata_sha256', 'sources']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    build(args.prepared, args.output)
