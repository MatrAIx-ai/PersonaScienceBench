#!/usr/bin/env python3
"""Validate frozen main-run inputs offline; no model calls or task execution."""
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ['persona_off', 'candidate_155', 'candidate_001', 'candidate_003', 'candidate_046']
SOURCES = {'discoverybench', 'bixbench', 'expbench', 'sciconvbench', 'asibench'}


def validate_inputs(root=ROOT, selection=None):
    config = root / 'configs/main_run'
    manifest = json.loads((config / 'provenance.json').read_text())
    selection = selection if selection is not None else config / 'selection.csv'
    if manifest['settings'] != SETTINGS:
        raise ValueError('Main-run settings differ from the selected five-setting panel')
    if hashlib.sha256(selection.read_bytes()).hexdigest() != manifest['selection_sha256']:
        raise ValueError('Selection checksum differs from the frozen main-run panel')
    with selection.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    counts = Counter(r['source'] for r in rows)
    if (len(rows) != 200 or len({(r['source'], r['task_id']) for r in rows}) != 200
            or set(counts) != SOURCES or set(counts.values()) != {40}
            or dict(counts) != manifest['source_counts']):
        raise ValueError('Expected 200 unique questions: 40 from each of the five selected sources')
    cohort = json.loads((root / 'configs/full_persona_v2/cohort.json').read_text())
    hashes = {p['candidate_id']: p['prompt_sha256'] for p in cohort['profiles']}
    for arm in SETTINGS[1:]:
        prompt = config / f'personas/{arm}.md'
        if hashlib.sha256(prompt.read_bytes()).hexdigest() != hashes[arm]:
            raise ValueError(f'Persona prompt checksum mismatch: {arm}')
    return rows


if __name__ == '__main__':
    validate_inputs()
    print('Verified: 200 unique questions, five sources × 40, five settings, exact persona hashes, 1,000 episodes per trial.')
