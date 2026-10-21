#!/usr/bin/env python3
"""Export a completed main-run directory into the collection bundle described in
docs/TEAM_HANDOFF.md section 5 (`results/<model-slug>/trial-<N>/`).

Generic `--run-dir` importer: no inference, no modification of run artifacts.
It reads every episode's `state.json`, selects the recorded (latest) attempt,
and writes episodes.csv, traces/, evaluations/, submissions/, grading_inputs/,
provenance/ and bundle_manifest.json. Earlier attempts are listed in
provenance/attempts.csv; nothing is chosen by score.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['persona_off', 'candidate_155', 'candidate_001', 'candidate_003', 'candidate_046']
SOURCES = ['asibench', 'bixbench', 'discoverybench', 'expbench', 'sciconvbench']
SECRET = re.compile(r'(?:sk-(?:proj-|or-v1-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|'
                    r'github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|Bearer [A-Za-z0-9._-]{16,})')
# Tool traffic is private to the actor sandbox; shared conversation events are exported.
PRIVATE_EVENT_TYPES = {'actor_command', 'actor_command_result'}
MAX_ARTIFACT_BYTES = 25 * 1024 * 1024


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def safe_component(value: str) -> str:
    return (re.sub(r'[^A-Za-z0-9_.-]', '_', value).strip('.')[:100] or 'episode') + '-' + hashlib.sha256(value.encode()).hexdigest()[:12]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


class Sanitizer:
    def __init__(self, replacements: list[tuple[str, str]]):
        # Longest patterns first so prefixed ids are rewritten before their suffixes.
        self.replacements = sorted(replacements, key=lambda item: -len(item[0]))

    def text(self, value: str) -> str:
        for old, new in self.replacements:
            value = value.replace(old, new)
        return SECRET.sub('[REDACTED_CREDENTIAL]', value)

    def json(self, value):
        return json.loads(self.text(json.dumps(value, ensure_ascii=False)))


def native(row: dict) -> dict:
    return next((r for r in row.get('native_results', []) if isinstance(r, dict) and (r.get('episode_id') or r.get('task_id'))), {})


def score(row: dict):
    """Native performance mapping from docs/TEAM_HANDOFF.md section 4."""
    if row.get('status') != 'finished':
        return None
    n = native(row)
    if n.get('status') == 'missing_submission':
        return 0.0
    evaluation = n.get('evaluation') or {}
    m = evaluation.get('metrics') or {}
    source = row['source']
    try:
        if source == 'asibench':
            return 100 * m['score'] / m['max_score'] if evaluation.get('status') == 'scored' else None
        if source == 'bixbench':
            return 100 * float(m['correct']) if 'correct' in m else None
        if source == 'discoverybench':
            return 100 * m['final_score'] if 'final_score' in m else None
        if source == 'sciconvbench':
            return 100 * m['FRR'] if 'FRR' in m else None
        if source == 'expbench':
            return (n.get('final') or n.get('initial') or {}).get('gated_coverage_mean')
    except (KeyError, TypeError, ZeroDivisionError):
        return None
    raise ValueError(source)


def case_dir(attempt_dir: Path, row: dict) -> Path:
    key = safe_component(row['source'] + ':' + row['task_id'])
    name = row['task_id'].replace('/', '__') if row['source'] == 'expbench' else key
    return attempt_dir / 'output' / name


def event_log(case: Path) -> Path | None:
    for candidate in (case / 'controller' / 'events.jsonl', case / 'events.jsonl'):
        if candidate.is_file():
            return candidate
    return None


def error_text(row: dict) -> str:
    found = []

    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ('error', 'sdk_error') and isinstance(value, str) and value:
                    found.append(value)
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    walk(row.get('native_results'))
    return ' || '.join(found)


def classify_failure(row: dict) -> str:
    if row.get('status') == 'finished':
        return ''
    text = error_text(row)
    if 'HTTP 400 for judge' in text:
        return 'judge_http_400'
    if '(length)' in text:
        return 'actor_output_length_cap'
    if 'ResearcherDecision' in text or 'invalid fact' in text.lower() or 'researcher_decision tool call' in text:
        return 'researcher_output_invalid'
    if 'HTTP 429' in text:
        return 'gateway_rate_limit'
    if 'ReadTimeout' in text or 'ConnectError' in text or 'transport failed' in text:
        return 'gateway_transport'
    if 'HTTP 400' in text:
        return 'actor_http_400'
    if 'litellm' in text:
        return 'sandbox_dependency'
    if 'File name too long' in text:
        return 'filesystem_name_too_long'
    return 'infrastructure_other' if text else 'infrastructure_no_error_text'


def submitted_flag(row: dict, case: Path) -> bool:
    n = native(row)
    if row['source'] == 'expbench':
        return bool(n.get('initial_submitted') or n.get('final_submitted'))
    if row['source'] == 'sciconvbench':
        return (case / 'controller' / 'submission.json').is_file()
    return bool((n.get('actor') or {}).get('submitted'))


def grading_disposition(row: dict, value) -> str:
    if row['status'] != 'finished':
        return 'execution_failed:' + classify_failure(row)
    n = native(row)
    if n.get('status') == 'missing_submission':
        return 'missing_submission_scored_zero'
    if value is not None:
        return 'scored'
    evaluation = n.get('evaluation') or {}
    if evaluation.get('status') not in (None, 'scored'):
        return 'grading_pending:' + str(evaluation.get('status'))
    return 'grading_pending:no_native_score'


def attempt_summary(attempt_dir: Path, row: dict) -> dict:
    out = {'has_output': (attempt_dir / 'output').exists(), 'status': '', 'error': '', 'actor_max_tokens': ''}
    for cfg_name, getter in (('config.json', lambda d: d['models']['actor'].get('max_tokens')),
                             ('manifest.json', lambda d: d['config']['models']['actor'].get('max_output_tokens'))):
        cfg = attempt_dir / 'output' / cfg_name
        if cfg.is_file():
            try:
                out['actor_max_tokens'] = getter(json.loads(cfg.read_text()))
                break
            except (KeyError, TypeError, ValueError):
                pass
    results = attempt_dir / 'output' / 'results.json'
    summary = attempt_dir / 'output' / 'summary.json'
    try:
        if row['source'] == 'expbench' and summary.is_file():
            data = json.loads(summary.read_text())
            first = (data.get('results') or [{}])[0]
            out['status'] = first.get('status', '')
            out['error'] = str(first.get('error') or '')[:300]
        elif results.is_file():
            data = json.loads(results.read_text())
            first = data[0] if isinstance(data, list) and data else {}
            out['status'] = first.get('status', '')
            out['error'] = error_text({'native_results': [first]})[:300]
    except (ValueError, OSError):
        out['status'] = 'unreadable'
    if not out['status']:
        log = attempt_dir / 'process.log'
        if log.is_file():
            tail = log.read_text(errors='replace')[-400:]
            out['status'] = 'no_result_record'
            out['error'] = re.sub(r'\s+', ' ', tail)[-300:]
    return out


TEXT_SUFFIXES = {'.json', '.jsonl', '.txt', '.md', '.csv', '.tsv', '.py', '.sh', '.log', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.tex', '.html', '.xml', '.rst'}


def copy_sanitized(src: Path, dest: Path, sanitizer: 'Sanitizer') -> dict:
    """Copy a file; UTF-8 text files (any name) are passed through the sanitizer (local paths, ids, credentials).

    Returns the hashes to record: `sha256` is the hash of the exported file, `sha256_original`
    the hash of the untouched source when the two differ.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    original = sha_file(src)
    if src.suffix.lower() in TEXT_SUFFIXES or src.suffix == '' or src.stat().st_size <= MAX_ARTIFACT_BYTES:
        try:
            raw = src.read_bytes()
            raw = None if b'\x00' in raw else raw.decode('utf-8')
        except UnicodeDecodeError:
            raw = None
        if raw is not None:
            cleaned = sanitizer.text(raw)
            dest.write_text(cleaned)
            exported = sha_file(dest)
            entry = {'bytes': dest.stat().st_size, 'sha256': exported, 'exported': True}
            if exported != original:
                entry.update({'sanitized': True, 'sha256_original': original, 'bytes_original': src.stat().st_size})
            return entry
    shutil.copyfile(src, dest)
    return {'bytes': src.stat().st_size, 'sha256': original, 'exported': True}


def copy_tree_limited(source: Path, target: Path, sanitizer: Sanitizer, files: list[dict], label: str) -> None:
    for path in sorted(p for p in source.rglob('*') if p.is_file()):
        rel = path.relative_to(source).as_posix()
        size = path.stat().st_size
        entry = {'kind': label, 'path': rel, 'bytes': size, 'sha256': sha_file(path)}
        if size > MAX_ARTIFACT_BYTES:
            entry['exported'] = False
            entry['reason'] = f'oversize (> {MAX_ARTIFACT_BYTES} bytes); hash recorded, file retained locally'
        else:
            dest = target / rel
            entry.update(copy_sanitized(path, dest, sanitizer))
        files.append(entry)


def export(a: argparse.Namespace) -> None:
    run = a.run_dir.resolve()
    out = a.output.resolve()
    if out.exists():
        raise ValueError('Choose a new output directory; existing exports are preserved')
    replacements = [tuple(item.split('=', 1)) for item in a.replace]
    replacements += [(str(run), '<LOCAL_RUN>'), (str(ROOT), '<LOCAL_REPOSITORY>'), (str(Path.home()), '<HOME>')]
    if a.scrub_home_prefix:
        replacements += [(prefix, '<HOME>') for prefix in a.scrub_home_prefix]
    sanitizer = Sanitizer(replacements)

    manifest = json.loads((run / 'manifest.json').read_text())
    selection = ROOT / 'configs/main_run/selection.csv'
    if manifest['selection_sha256'] != sha_file(selection):
        raise ValueError('Run selection differs from the frozen main panel')
    with selection.open(newline='') as handle:
        panel = list(csv.DictReader(handle))
    expected = {(r['source'], r['task_id'], arm) for r in panel for arm in ARMS}

    out.mkdir(parents=True)
    (out / '.gitattributes').write_text('* -text\n')
    for sub in ('traces', 'evaluations', 'submissions', 'grading_inputs', 'provenance'):
        (out / sub).mkdir()

    episodes, finals, metrics, index_rows, attempts_rows, submission_rows = [], [], [], [], [], []
    seen = set()
    failure_classes = Counter()
    shards = {source: (out / 'traces' / f'shared-events.{source}.jsonl').open('w') for source in SOURCES}
    line_numbers = Counter()
    for state_path in sorted((run / 'episodes').glob('*/*/state.json')):
        row = json.loads(state_path.read_text())
        key = (row['source'], row['task_id'], row['arm'])
        if key not in expected:
            raise ValueError(f'Unexpected slot {key}')
        if key in seen:
            raise ValueError(f'Duplicate slot {key}')
        seen.add(key)
        slot_dir = state_path.parent
        attempt = int(row['attempt'])
        attempt_dir = slot_dir / f'attempt-{attempt}'
        case = case_dir(attempt_dir, row)
        task_key = safe_component(row['source'] + ':' + row['task_id'])
        n = native(row)
        value = score(row)
        evaluation = n.get('evaluation') or {}
        disposition = grading_disposition(row, value)
        failure = classify_failure(row)
        if failure:
            failure_classes[failure] += 1

        # every attempt, never only the selected one
        for att in sorted(slot_dir.glob('attempt-*'), key=lambda p: int(p.name.split('-')[1])):
            number = int(att.name.split('-')[1])
            summary = attempt_summary(att, row)
            attempts_rows.append({'benchmark': key[0], 'task_id': key[1], 'arm': key[2], 'attempt': number,
                                  'selected': number == attempt, 'has_output': summary['has_output'],
                                  'actor_max_tokens': summary['actor_max_tokens'],
                                  'status': summary['status'] if number != attempt else row['status'],
                                  'error': sanitizer.text(summary['error'] if number != attempt else error_text(row)[:300])})

        # shared conversation
        log = event_log(case)
        events, event_type_counts, private_count = [], Counter(), 0
        if log is not None:
            for seq, line in enumerate(log.read_text().splitlines()):
                if not line.strip():
                    continue
                event = json.loads(line)
                event_type_counts[event.get('type')] += 1
                if event.get('type') in PRIVATE_EVENT_TYPES:
                    private_count += 1
                    continue
                events.append({'sequence': event.get('sequence', seq), 'time': event.get('time'),
                               'type': event.get('type'), 'payload': sanitizer.json(event.get('payload') or {})})
        record = {'benchmark': key[0], 'task_id': key[1], 'arm': key[2], 'attempt': attempt,
                  'runner_status': row['status'], 'native_status': n.get('status', ''),
                  'score_0_100': value, 'submitted': submitted_flag(row, case),
                  'source_event_log': sanitizer.text(str(log)) if log else None,
                  'source_event_log_sha256': sha_file(log) if log else None,
                  'event_count': len(events), 'private_tool_events_omitted': private_count,
                  'events': events}
        if not events:
            record['empty_reason'] = 'no shared event log recorded' if log is None else 'event log holds no shared events'
        shards[key[0]].write(json.dumps(record, ensure_ascii=False) + '\n')
        line_numbers[key[0]] += 1
        line_number = line_numbers[key[0]]
        index_rows.append({'shard': f'shared-events.{key[0]}.jsonl', 'line_number': line_number, 'benchmark': key[0], 'task_id': key[1], 'arm': key[2],
                           'attempt': attempt, 'runner_status': row['status'], 'native_status': record['native_status'],
                           'score_0_100': value, 'submitted': record['submitted'], 'shared_event_count': len(events),
                           'event_type_counts': json.dumps(dict(event_type_counts), sort_keys=True),
                           'source_event_log': record['source_event_log'] or '',
                           'source_event_log_sha256': record['source_event_log_sha256'] or ''})

        # submissions for a later judge-only regrade
        sub_files: list[dict] = []
        sub_target = out / 'submissions' / key[2] / task_key
        if case.exists():
            controller = case / 'controller'
            for name in ('submission.json', 'submission_hashes.json'):
                if (controller / name).is_file():
                    sub_files.append({'kind': 'controller', 'path': name,
                                      **copy_sanitized(controller / name, sub_target / name, sanitizer)})
            if (controller / 'submitted_artifacts').is_dir():
                copy_tree_limited(controller / 'submitted_artifacts', sub_target / 'submitted_artifacts', sanitizer, sub_files, 'submitted_artifact')
            if row['source'] == 'expbench':
                for design in sorted(case.glob('*design*.json')):
                    sub_files.append({'kind': 'exp_design', 'path': design.name,
                                      **copy_sanitized(design, sub_target / design.name, sanitizer)})
            for name in ('actor_result.json', 'evaluation.json', 'result.json'):
                if (case / name).is_file():
                    sub_target.mkdir(parents=True, exist_ok=True)
                    (sub_target / name).write_text(sanitizer.text((case / name).read_text()))
                    sub_files.append({'kind': 'record', 'path': name, 'bytes': (case / name).stat().st_size,
                                      'sha256': sha_file(case / name), 'exported': True, 'sanitized': True})
        submission_rows.append({'benchmark': key[0], 'task_id': key[1], 'arm': key[2], 'attempt': attempt,
                                'submitted': record['submitted'],
                                'submission_dir': (Path('submissions') / key[2] / task_key).as_posix() if sub_files else '',
                                'file_count': len(sub_files), 'files': sub_files,
                                'prepared_task_key': task_key,
                                'evaluator_version': evaluation.get('evaluator_version')})

        sanitized_row = sanitizer.json(row)
        finals.append({'benchmark': key[0], 'task_id': key[1], 'arm': key[2], 'trial': 1, 'attempt': attempt,
                       'grading_disposition': disposition, 'score_0_100': value,
                       'source_state_sha256': sha_file(state_path), 'record': sanitized_row})
        metrics.append({'benchmark': key[0], 'task_id': key[1], 'arm': key[2], 'attempt': attempt,
                        'submitted': record['submitted'], 'evaluation_status': evaluation.get('status'),
                        'evaluator_version': evaluation.get('evaluator_version'),
                        'judge': sanitizer.json({k: v for k, v in (evaluation.get('details') or {}).items() if k.startswith('judge')}),
                        'metrics': sanitizer.json(evaluation.get('metrics') or {}),
                        'exp_initial': sanitizer.json(n.get('initial')) if key[0] == 'expbench' else None,
                        'exp_final': sanitizer.json(n.get('final')) if key[0] == 'expbench' else None,
                        'errors': sanitizer.json(evaluation.get('errors') or []),
                        'score_0_100': value, 'grading_disposition': disposition,
                        'source_state_sha256': finals[-1]['source_state_sha256']})
        actor = n.get('actor') or {}
        episodes.append({'benchmark': key[0], 'task_id': key[1], 'task_key': task_key, 'family': row.get('family', ''),
                         'subfield': row.get('subfield', ''), 'study_id': row.get('study_id', ''), 'arm': key[2], 'trial': 1,
                         'selected_attempt': attempt, 'attempts_total': sum(1 for _ in slot_dir.glob('attempt-*')),
                         'runner_status': row['status'], 'native_status': record['native_status'],
                         'evaluation_status': evaluation.get('status', ''), 'submitted': record['submitted'],
                         'score_0_100': '' if value is None else value, 'grading_disposition': disposition,
                         'failure_class': failure,
                         'termination': sanitizer.text(str(n.get('collaboration_termination') or (actor.get('collaboration') or {}).get('termination') or actor.get('status') or n.get('actor_status') or '')),
                         'actor_calls': n.get('actor_calls', actor.get('actor_calls', '')),
                         'researcher_questions': len(n.get('researcher_questions') or []) if isinstance(n.get('researcher_questions'), list) else n.get('researcher_questions', ''),
                         'researcher_requests': n.get('researcher_requests', ''),
                         'elapsed_seconds': n.get('elapsed_seconds', ''),
                         'shared_event_count': len(events), 'events_shard': f'traces/shared-events.{key[0]}.jsonl', 'events_line_number': line_number,
                         'submission_dir': submission_rows[-1]['submission_dir'],
                         'source_state_sha256': finals[-1]['source_state_sha256']})
    for handle in shards.values():
        handle.close()
    if seen != expected:
        raise ValueError(f'Missing planned slots: {len(expected - seen)}')

    order = lambda r: (ARMS.index(r['arm']), SOURCES.index(r['benchmark']), r['task_id'])
    episodes.sort(key=order)
    write_csv(out / 'episodes.csv', episodes)
    write_csv(out / 'traces' / 'shared-events-index.csv', index_rows)
    (out / 'traces' / 'final-results.json').write_text(json.dumps(sorted(finals, key=order), ensure_ascii=False, indent=1) + '\n')
    with (out / 'evaluations' / 'metrics.jsonl').open('w') as handle:
        for item in sorted(metrics, key=order):
            handle.write(json.dumps(item, ensure_ascii=False) + '\n')
    with (out / 'submissions' / 'manifest.jsonl').open('w') as handle:
        for item in sorted(submission_rows, key=order):
            handle.write(json.dumps(item, ensure_ascii=False) + '\n')
    write_csv(out / 'provenance' / 'attempts.csv', sorted(attempts_rows, key=lambda r: (order(r), r['attempt'])))

    # grading inputs: the frozen preparation bundle tracked in Git is the team-accessible route
    receipt = json.loads((run / 'preparation_receipt.json').read_text())
    frozen = ROOT / 'configs/main_run/frozen' / receipt['preparation_id']
    (out / 'grading_inputs' / 'manifest.json').write_text(json.dumps({
        'preparation_id': receipt['preparation_id'], 'bundle_sha256': receipt.get('bundle_sha256'),
        'selection_sha256': receipt['selection_sha256'],
        'frozen_bundle_repository_path': str(frozen.relative_to(ROOT)) if frozen.exists() else None,
        'restore_command': f"python scripts/restore_main_preparation.py --run-dir RUN_DIR --link-assets  # preparation {receipt['preparation_id']}",
        'note': 'Prepared task packages (public brief, simulator facts, evaluator references) are not copied here; '
                'restore them from the tracked frozen bundle, whose checksums are verified by the restore script. '
                'Hidden evaluator references stay out of this public export. Large public datasets are acquired per docs/MAIN_RUN.md.',
        'per_slot_evaluator_versions': dict(Counter(f"{r['benchmark']}:{r['evaluator_version']}" for r in submission_rows)),
        'preparation_receipt': sanitizer.json(receipt),
    }, indent=2) + '\n')

    # provenance
    prov = out / 'provenance'
    (prov / 'configs').mkdir()
    for path in sorted((run / 'configs').glob('*.json')):
        (prov / 'configs' / path.name).write_text(sanitizer.text(path.read_text()))
    for name in ('manifest.json', 'api_access.json', 'preparation_receipt.json', 'progress.json', 'preparation_errors.json'):
        if (run / name).is_file():
            (prov / name).write_text(sanitizer.text((run / name).read_text()))
    for path in sorted(run.glob('code.*.json')):
        shutil.copyfile(path, prov / path.name)
    shutil.copyfile(selection, prov / 'selection.csv')
    (prov / 'persona_prompt_hashes.json').write_text(json.dumps(
        {arm: sha_file(ROOT / 'configs/main_run/personas' / f'{arm}.md') for arm in ARMS if arm != 'persona_off'}, indent=2) + '\n')
    git = lambda *args: subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout
    (prov / 'git_commit.txt').write_text(git('rev-parse', 'HEAD'))
    diff = git('diff', 'HEAD', '--', 'scripts', 'src', 'configs', 'manifests')
    (prov / 'git_diff_scripts_src_configs.patch').write_text(sanitizer.text(diff) if diff else '# clean working tree for scripts/, src/, configs/, manifests/\n')
    (prov / 'lockfile_hashes.json').write_text(json.dumps({name: sha_file(ROOT / name) for name in ('uv.lock', 'pyproject.toml') if (ROOT / name).is_file()}, indent=2) + '\n')
    for extra in a.provenance_file:
        src = Path(extra)
        (prov / src.name).write_text(sanitizer.text(src.read_text(errors='replace')))

    # readme and delivery
    counts = Counter(r['runner_status'] for r in episodes)
    by_arm = {arm: Counter(r['runner_status'] for r in episodes if r['arm'] == arm) for arm in ARMS}
    by_source = {s: Counter(r['runner_status'] for r in episodes if r['benchmark'] == s) for s in SOURCES}
    dispositions = Counter(r['grading_disposition'] for r in episodes)
    models = {role: {k: cfg.get(k) for k in ('model', 'provider', 'reasoning_effort', 'max_tokens', 'max_output_tokens')}
              for role, cfg in json.loads((prov / 'configs' / 'persona_off.shared.json').read_text())['models'].items()}
    exp_models = {role: {k: cfg.get(k) for k in ('model', 'reasoning_effort', 'max_output_tokens')}
                  for role, cfg in json.loads((prov / 'configs' / 'persona_off.exp.json').read_text())['models'].items()}
    notes = Path(a.notes_file).read_text() if a.notes_file else ''
    status = 'complete_execution_with_unresolved_slots' if counts.get('infrastructure_error') else 'complete'
    lines = [f'# {a.title}', '',
             f'Delivered scope: one trial, 200 frozen questions × five settings = {len(episodes)} episode slots. '
             f'Runner status: **{counts.get("finished", 0)} finished**, **{counts.get("infrastructure_error", 0)} unresolved execution failures**, '
             f'{sum(v for k, v in counts.items() if k not in ("finished", "infrastructure_error"))} other.', '',
             '`finished` is an execution status, not a correct-answer label; native scores are in `episodes.csv` and `evaluations/metrics.jsonl`. '
             'Unresolved slots carry an explicit `failure_class`; they are unavailable, not scientific zeros. Legitimate missing submissions are scored zero per the handoff contract.', '',
             '## Model roles (as transmitted)', '', '| Role | Model | Reasoning | Output cap (shared / EXP) |', '|---|---|---|---|']
    for role in ('actor', 'researcher', 'judge'):
        m, e = models.get(role, {}), exp_models.get(role, {})
        lines.append(f"| {role} | `{m.get('model')}` | {m.get('reasoning_effort')} | {m.get('max_tokens')} / {e.get('max_output_tokens')} |")
    lines += ['', f"Provider label in configs: `{models['actor'].get('provider')}` (see notes below for the actual serving path). "
              f"Frozen preparation `{receipt['preparation_id']}`; selection sha256 `{receipt['selection_sha256']}`.", '',
              '## Counts', '', '| Setting | finished | infrastructure_error |', '|---|---:|---:|']
    lines += [f"| {arm} | {by_arm[arm].get('finished', 0)} | {by_arm[arm].get('infrastructure_error', 0)} |" for arm in ARMS]
    lines += ['', '| Benchmark | finished | infrastructure_error |', '|---|---:|---:|']
    lines += [f"| {s} | {by_source[s].get('finished', 0)} | {by_source[s].get('infrastructure_error', 0)} |" for s in SOURCES]
    lines += ['', '### Grading disposition', '', '| Disposition | Slots |', '|---|---:|']
    lines += [f'| {k} | {v} |' for k, v in sorted(dispositions.items(), key=lambda kv: -kv[1])]
    if failure_classes:
        lines += ['', '### Unresolved execution failures by class', '', '| Class | Slots |', '|---|---:|']
        lines += [f'| {k} | {v} |' for k, v in failure_classes.most_common()]
    lines += ['', '## Bundle layout', '',
              '- `episodes.csv`: all 1,000 slots, selected attempt, statuses, submitted flag, normalized native score (blank when pending/unavailable), grading disposition, failure class, interaction counts, trace line number, submission directory, state hash.',
              '- `traces/final-results.json`: the full selected `state.json` record per slot (sanitized), with native result dictionaries.',
              '- `traces/shared-events.<benchmark>.jsonl` (five shards) + `shared-events-index.csv`: ordered shared actor/simulator/controller events per slot. Actor tool commands and tool results are private sandbox traffic and are omitted (counts retained). Empty records carry a reason.',
              '- `evaluations/metrics.jsonl`: native metrics (including SciConv `entity_recovery`), evaluator version, judge identity, errors and an explicit disposition for every slot.',
              '- `submissions/<arm>/<task_key>/`: final actor submissions (`submission.json`, `submission_hashes.json`, `submitted_artifacts/`, EXP `initial_design.json`) plus sanitized `actor_result.json`, `evaluation.json`, `result.json`; `submissions/manifest.jsonl` maps every slot to its attempt and files with hashes. Text files (JSON, scripts, logs) are passed through the same sanitizer as every other exported text, so local paths and identifiers are normalized; when that changes a file, the manifest records `sanitized: true` with `sha256_original` next to the exported `sha256`. Binary artifacts are copied verbatim. Files above 25 MiB are hash-listed, not copied.',
              '- `grading_inputs/manifest.json`: frozen preparation id/hashes and the restore route for prepared task packages and evaluator references.',
              '- `provenance/`: run manifest, actual configs, runtime code hashes, preparation receipt, selection and persona hashes, git commit and source diff, lockfile hashes, every attempt per slot (`attempts.csv`), and operator files listed below.',
              '- `bundle_manifest.json`: byte size and SHA-256 of every delivered file.', '',
              'Reproduce the export offline with `python scripts/export_main_bundle.py --run-dir RUN_DIR --output NEW_DIRECTORY ...`; it makes no model calls and refuses to overwrite an existing export.', '']
    if notes:
        lines += ['## Campaign notes', '', notes.rstrip(), '']
    (out / 'README.md').write_text(sanitizer.text('\n'.join(lines)) + '\n')
    delivery = {'status': status, 'expected_slots': len(expected), 'available_slots': len(episodes),
                'finished_slots': counts.get('finished', 0), 'unresolved_slots': counts.get('infrastructure_error', 0),
                'trial': 1, 'actor': a.actor_label, 'simulator': a.simulator_label, 'judge': a.judge_label,
                'grading': 'inline native evaluation during the run; dispositions per slot in episodes.csv',
                'limitations': a.limitation, 'path': str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else str(out),
                'exported_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'inference_calls': 0}
    (out / 'delivery.json').write_text(json.dumps(delivery, indent=2) + '\n')
    (out / 'DELIVERY.md').write_text('\n'.join(['# Delivery status', '', status, '',
                                                f'Actor: {a.actor_label}; simulator: {a.simulator_label}; judge: {a.judge_label}.', '',
                                                *[f'- {item}' for item in a.limitation], '',
                                                'See `delivery.json`, `README.md` and `bundle_manifest.json`.']) + '\n')

    # final checks and manifest
    for path in out.rglob('*'):
        if path.is_file() and path.suffix in ('.json', '.jsonl', '.csv', '.md', '.txt', '.patch', '.py', '.sh', '.env'):
            text = path.read_text(errors='replace')
            if SECRET.search(text):
                raise ValueError(f'Credential-pattern check failed: {path.relative_to(out)}')
            for forbidden in a.forbid:
                if forbidden in text:
                    raise ValueError(f'Forbidden string {forbidden!r} in {path.relative_to(out)}')
    files = {str(p.relative_to(out)): {'bytes': p.stat().st_size, 'sha256': sha_file(p)}
             for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'bundle_manifest.json'}
    (out / 'bundle_manifest.json').write_text(json.dumps({'generator': 'scripts/export_main_bundle.py',
                                                           'generator_sha256': sha_file(Path(__file__)),
                                                           'run_manifest_selection_sha256': manifest['selection_sha256'],
                                                           'files': files}, indent=1) + '\n')
    print(json.dumps({'slots': len(episodes), 'runner_status': dict(counts), 'dispositions': dict(dispositions),
                      'failure_classes': dict(failure_classes), 'files': len(files),
                      'total_bytes': sum(f['bytes'] for f in files.values())}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--actor-label', required=True)
    parser.add_argument('--simulator-label', required=True)
    parser.add_argument('--judge-label', default='GPT-6 Astra (low)')
    parser.add_argument('--replace', action='append', default=[], metavar='OLD=NEW',
                        help='Literal text replacement applied to every exported text (model id normalization, host redaction)')
    parser.add_argument('--scrub-home-prefix', action='append', default=[], help='Additional absolute path prefixes to replace with <HOME>')
    parser.add_argument('--forbid', action='append', default=[], help='Strings that must not appear in any exported text file')
    parser.add_argument('--provenance-file', action='append', default=[], help='Operator file to copy (sanitized) into provenance/')
    parser.add_argument('--notes-file', help='Markdown appended to README.md as campaign notes')
    parser.add_argument('--limitation', action='append', default=[], help='Limitation line for delivery.json / DELIVERY.md')
    export(parser.parse_args())
