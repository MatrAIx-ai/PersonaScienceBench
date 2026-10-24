#!/usr/bin/env python3
"""Restore the shipped 200-task preparation using already-downloaded public assets.

Standard library only. No model calls, task conversion, or sandbox bypass.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT / 'configs/main_run/frozen/astra-20260929-v1'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or relative in ('', '.'):
        raise ValueError(f'Unsafe relative path: {relative!r}')
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes destination: {relative!r}')
    return target


def relocate(value, old_root, old_prepared, root, prepared):
    if isinstance(value, str):
        replacements = {old_prepared: str(prepared), old_root: str(root)}
        pattern = '|'.join(re.escape(p) for p in sorted(replacements, key=len, reverse=True))
        return re.sub(pattern, lambda match: replacements[match.group()], value)
    if isinstance(value, list):
        return [relocate(v, old_root, old_prepared, root, prepared) for v in value]
    if isinstance(value, dict):
        return {k: relocate(v, old_root, old_prepared, root, prepared) for k, v in value.items()}
    return value


def load_bundle(bundle):
    manifest = json.loads((bundle / 'manifest.json').read_text())
    raw = safe_path(bundle, manifest['archive']).read_bytes()
    if len(raw) != manifest['bytes'] or digest(raw) != manifest['sha256']:
        raise ValueError('Frozen preparation archive checksum/size mismatch')
    expanded = gzip.decompress(raw)
    if len(expanded) != manifest['uncompressed_bytes']:
        raise ValueError('Frozen preparation uncompressed size mismatch')
    payload = json.loads(expanded)
    if payload['schema_version'] != 1 or manifest['schema_version'] != 1:
        raise ValueError('Unsupported preparation format')
    if set(payload['files']) != set(manifest['metadata_sha256']):
        raise ValueError('Frozen metadata inventory mismatch')
    for name, text in payload['files'].items():
        safe_path(bundle, name)
        if digest(text.encode()) != manifest['metadata_sha256'][name]:
            raise ValueError(f'Frozen metadata checksum mismatch: {name}')
    if digest(payload['exp_source'].encode()) != manifest['exp_source_sha256']:
        raise ValueError('Frozen EXP source checksum mismatch')
    return manifest, payload


def hash_file(path, cache):
    st = path.stat()
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    if key not in cache:
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
                h.update(block)
        cache[key] = h.hexdigest()
    return cache[key]


def restore(bundle, root, run_dir, *, check_only=False, link_assets=False):
    root, run_dir = root.resolve(), run_dir.resolve()
    prepared = run_dir / 'prepared'
    if prepared.exists() or prepared.is_symlink():
        raise ValueError(f'Refusing to replace existing preparation: {prepared}. Use a fresh run directory.')
    manifest, payload = load_bundle(bundle)
    selection = (root / 'configs/main_run/selection.csv').read_bytes()
    if digest(selection) != manifest['selection_sha256']:
        raise ValueError('Selection differs from the frozen 200-question panel')
    rows = list(csv.DictReader(selection.decode().splitlines()))
    if len(rows) != 200 or len({(r['source'], r['task_id']) for r in rows}) != 200:
        raise ValueError('Selection must contain 200 unique questions')
    if dict(Counter(r['source'] for r in rows)) != manifest['source_counts']:
        raise ValueError('Benchmark counts do not match frozen preparation')
    # Check actual question IDs inside the frozen packages, not only their counts.
    identities = []
    for name, text in payload['files'].items():
        obj = json.loads(text)
        if name.endswith('/pilot_manifest.json'):
            identities.extend((r['benchmark'], r['source_task_id']) for r in obj['cases'])
        elif name.endswith('/tasks.jsonl'):
            identities.append(('expbench', obj['task_id']))
    if len(identities) != 200 or set(identities) != {(r['source'], r['task_id']) for r in rows}:
        raise ValueError('Prepared question IDs differ from the selection')
    sources = json.loads((root / 'manifests/sources.json').read_text())
    for source, frozen in manifest['sources'].items():
        for key, value in frozen.items():
            if sources[source].get(key) != value:
                raise ValueError(f'Source pin mismatch: {source}/{key}')
    for name in payload['files']:
        safe_path(prepared, name)
    cache, problems = {}, []
    for asset in payload['assets']:
        source = safe_path(root, asset['source'])
        safe_path(prepared, asset['destination'])
        if not source.is_file() or source.is_symlink():
            problems.append({'asset': asset['source'], 'error': 'missing or symlink', 'acquisition': asset.get('acquisition')})
        elif hash_file(source, cache) != asset['sha256']:
            problems.append({'asset': asset['source'], 'error': 'SHA-256 differs from original prepared mount'})
    for item in payload['required_external']:
        path = safe_path(root, item['path'])
        exists = path.is_dir() if item['kind'] == 'directory' else path.is_file()
        if not exists:
            problems.append({'asset': item['path'], 'error': 'missing evaluator dependency'})
        elif item.get('sha256') and hash_file(path, cache) != item['sha256']:
            problems.append({'asset': item['path'], 'error': 'evaluator dependency hash mismatch'})
    exp_path = root / 'data/exp_bench/tasks.jsonl'
    if exp_path.exists() and hash_file(exp_path, cache) != manifest['exp_source_sha256']:
        problems.append({'asset': str(exp_path), 'error': 'Existing EXP source differs. Preserve/move it before restoring into this checkout.'})
    if problems:
        raise ValueError('Public assets are not ready. Run scripts/setup_main.sh or acquire the pinned files.\n' + json.dumps(problems, indent=2))
    receipt = {'preparation_id': manifest['preparation_id'], 'bundle_sha256': manifest['sha256'],
               'selection_sha256': manifest['selection_sha256'], 'questions': 200,
               'source_counts': manifest['source_counts'], 'actor_asset_copies': len(payload['assets']),
               'verified_unique_files': len(cache), 'run_directory': str(run_dir),
               'prepared_directory': str(prepared), 'check_only': check_only,
               'inference_performed': False, 'sandbox_tested': False,
               'runtime_protocol': 'Not frozen by this bundle; record the actual runner revision and configuration.',
               'restoration': 'Path rebasing only; task/fact/evaluator content retained.'}
    if check_only:
        print(json.dumps(receipt, indent=2))
        return receipt
    run_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.restoring-prepared-', dir=run_dir))
    try:
        hashes = {}
        for name, text in payload['files'].items():
            obj = relocate(json.loads(text), payload['old_root'], payload['old_prepared'], root, prepared)
            content = json.dumps(obj, ensure_ascii=False, indent=None if name.endswith('/tasks.jsonl') else 2) + '\n'
            path = safe_path(staging, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            hashes[name] = digest(content.encode())
        for asset in payload['assets']:
            source = safe_path(root, asset['source'])
            target = safe_path(staging, asset['destination'])
            target.parent.mkdir(parents=True, exist_ok=True)
            if link_assets:
                target.hardlink_to(source)
            else:
                shutil.copy2(source, target)
            if hash_file(target, cache) != asset['sha256']:
                raise ValueError(f'Restored asset hash mismatch: {asset["destination"]}')
        if not exp_path.exists():
            exp_path.parent.mkdir(parents=True, exist_ok=True)
            with exp_path.open('x') as stream:
                stream.write(payload['exp_source'])
        if prepared.exists() or prepared.is_symlink():
            raise ValueError('Preparation appeared while restoring; refusing overwrite')
        staging.rename(prepared)
        receipt['restored_metadata_sha256'] = hashes
        receipt['asset_mode'] = 'hardlink; keep source assets immutable' if link_assets else 'copy'
        (run_dir / 'preparation_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(json.dumps({k: v for k, v in receipt.items() if k != 'restored_metadata_sha256'}, indent=2))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true', help='Verify inputs/assets without creating a run or making API calls')
    parser.add_argument('--link-assets', action='store_true', help='Hardlink immutable downloaded assets on the same filesystem instead of copying')
    args = parser.parse_args()
    try:
        restore(args.bundle, args.repo_root, args.run_dir, check_only=args.check_only, link_assets=args.link_assets)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
