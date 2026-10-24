#!/usr/bin/env python3
"""Verify packaged result hashes and unique episode slots; never run inference."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(directory):
    receipt = json.loads((directory / 'bundle_manifest.json').read_text())
    files = receipt['files']
    for name, metadata in files.items():
        path = directory / name
        if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
            raise ValueError(f'Unsafe bundle path: {path}')
        raw = path.read_bytes()
        if len(raw) != metadata['bytes'] or hashlib.sha256(raw).hexdigest() != metadata['sha256']:
            raise ValueError(f'Checksum mismatch: {path}')
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*')
              if p.is_file() and p.name != 'bundle_manifest.json' and '__pycache__' not in p.parts}
    if actual != set(files):
        raise ValueError(f'Unmanifested/missing files in {directory}: {actual ^ set(files)}')
    delivery = json.loads((directory / 'delivery.json').read_text())
    expected = delivery.get('expected_slots')
    if expected:
        source = directory / ('index.csv' if (directory / 'index.csv').exists() else 'episodes.csv')
        rows = list(csv.DictReader(source.open()))
        keys = [(r.get('benchmark', r.get('source')), r['task_id'], r.get('arm', r.get('persona'))) for r in rows]
        if len(rows) != expected or len(set(keys)) != expected:
            raise ValueError(f'Wrong number of unique slots: {source}')
        selected = list(csv.DictReader((ROOT / 'configs/main_run/selection.csv').open()))
        arms = ['persona_off', 'candidate_155', 'candidate_001', 'candidate_003', 'candidate_046']
        expected_keys = {(r['source'], r['task_id'], arm) for r in selected for arm in arms}
        if set(keys) != expected_keys:
            raise ValueError(f'Slot identities differ from the frozen selection: {source}')
    return {'path': str(directory.relative_to(ROOT)), 'files': len(files),
            'status': delivery['status'], 'verified': True}


def main():
    directories = sorted(p.parent for p in (ROOT / 'results').glob('*/*/delivery.json'))
    if not directories:
        raise ValueError('No result bundles found')
    for directory in directories:
        print(json.dumps(audit(directory)), flush=True)


if __name__ == '__main__':
    main()
