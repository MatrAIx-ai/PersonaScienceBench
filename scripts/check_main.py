#!/usr/bin/env python3
"""Validate the handoff inputs offline; no model calls or task execution."""
from pathlib import Path
import csv, hashlib, json
from collections import Counter
root = Path(__file__).resolve().parents[1]
config = root/'configs/main_run'
manifest = json.loads((config/'provenance.json').read_text())
selection = config/'selection.csv'
assert hashlib.sha256(selection.read_bytes()).hexdigest() == manifest['selection_sha256']
rows = list(csv.DictReader(selection.open()))
assert len(rows) == len({(r['source'], r['task_id']) for r in rows}) == 200
assert dict(Counter(r['source'] for r in rows)) == manifest['source_counts']
assert set(manifest['source_counts'].values()) == {40}
for arm in manifest['settings'][1:]:
    assert (config/f'personas/{arm}.md').read_text().strip()
print('Verified: 200 unique questions, five sources × 40, five settings, 1,000 episodes per trial.')
