"""Audit this delivery against the supplied repository's fixed task/eval code.

This is a release-integrity check, not a benchmark evaluator or task score.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_scope(root=ROOT):
    baseline = json.loads((root / 'manifests/persona_scope_baseline.json').read_text())
    errors = []
    for relative, expected in baseline['unchanged_files'].items():
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(relative)
    # This correction intentionally changes the common simulator policy. Pin its
    # reviewed bytes separately; never describe it as the old off policy.
    relative = 'src/personasciencebench/researcher.py'
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if actual != baseline['researcher_expected_sha256']:
        errors.append(relative + ': differs from reviewed Phase 1 simulator correction')
    for relative in baseline['removed_extension_paths']:
        path = root / relative
        # Git does not track directories or interpreter caches. A migrated
        # checkout may retain those after all old implementation files vanish.
        files = [path] if path.is_file() else list(path.rglob('*')) if path.is_dir() else []
        if any(p.is_file() and '__pycache__' not in p.parts
               and '.pytest_cache' not in p.parts and p.name != '.DS_Store' for p in files):
            errors.append(relative + ': superseded extension remains')
    for path in (root / 'src').rglob('*.py'):
        relative = path.relative_to(root).as_posix()
        if relative not in baseline['original_source_files'] and not relative.startswith('src/personasciencebench/science_personas/'):
            errors.append(relative + ': unexpected new source module')
    return {'ok': not errors, 'unchanged_files_checked': len(baseline['unchanged_files']),
            'researcher_matches_reviewed_phase1_correction': not any(error.startswith('src/personasciencebench/researcher.py') for error in errors),
            'errors': errors}


if __name__ == '__main__':
    result = check_scope()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['ok'] else 1)
