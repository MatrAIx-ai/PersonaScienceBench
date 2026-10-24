#!/usr/bin/env python3
"""Publish one Astra trial per selected persona from saved shared conversations.

No inference, scheduling, or modification of original run artifacts.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['persona_off', 'candidate_155', 'candidate_001', 'candidate_003', 'candidate_046']
RUNS = ['openai-astra-top2-first-pass', 'openai-astra-top10-trial-1-batch-2',
        'openai-astra-top10-trial-1-batch-1']
SECRET = re.compile(r'(?:sk-(?:proj-|or-v1-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})')
LABELS = {'initial_request': 'Initial task', 'researcher_decision': 'Simulator',
          'agent_handoff': 'Actor', 'researcher_question': 'Actor clarification question',
          'researcher_reply': 'Simulator reply', 'final_specification': 'Actor final specification',
          'collaboration_budget_exhausted': 'Controller termination',
          'collaboration_missing_submission': 'Controller termination',
          'collaboration_stopped': 'Controller termination'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_component(value):
    return (re.sub(r'[^A-Za-z0-9_.-]', '_', value).strip('.')[:100] or 'episode') + '-' + hashlib.sha256(value.encode()).hexdigest()[:12]


def native(row):
    return next((r for r in row.get('native_results', []) if r.get('episode_id') or r.get('task_id')), {})


def score(row):
    """Same native-score definitions as report_first_pass_ci; no numpy required."""
    if row.get('status') != 'finished':
        return None
    n = native(row)
    if n.get('status') == 'missing_submission':
        return 0.0
    evaluation = n.get('evaluation') or {}
    m = evaluation.get('metrics') or {}
    source = row['source']
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
    raise ValueError(source)


def choose_endpoint(original, repaired):
    # Prefer an evaluable repair, never the highest score; retain original fallback.
    if repaired is not None and score(repaired) is not None:
        return repaired, 'original' if repaired == original else 'repaired'
    if score(original) is not None:
        return original, 'original_fallback' if repaired != original else 'original'
    return None, 'unavailable'


def sanitize(text):
    return SECRET.sub('[REDACTED_CREDENTIAL]', text).replace(str(ROOT), '<LOCAL_REPOSITORY>')


def fenced(text):
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False, indent=2)
    text = sanitize(text)
    fence = '````'
    while fence in text:
        fence += '`'
    return f'{fence}text\n{text}\n{fence}'


def conversation(events):
    """Allowlist shared exchanges; exclude tool/private/API/judge payloads."""
    result = []
    for index, event in enumerate(events):
        kind = event.get('type')
        if kind not in LABELS:
            continue
        payload = event.get('payload') or {}
        fields = {key: payload[key] for key in
                  ('message', 'question', 'answer', 'stage', 'interaction', 'phase',
                   'action', 'approve_approach', 'evidence', 'objectives_open',
                   'assumptions', 'uncertainties', 'reason') if key in payload}
        if fields:
            result.append({'event_index': index, 'kind': kind, 'role': LABELS[kind], 'fields': fields})
    return result


def event_path(row, original_run, repair_run, endpoint):
    n = native(row)
    candidates = []
    if n.get('case_directory'):
        case = Path(n['case_directory'])
        if not case.resolve().is_relative_to(ROOT / 'runs'):
            raise ValueError('Recorded case path is outside local run storage')
        candidates.extend([case / 'controller/events.jsonl', case / 'events.jsonl'])
    key = safe_component(row['source'] + ':' + row['task_id'])
    case_key = row['task_id'].replace('/', '__') if row['source'] == 'expbench' else key
    ordered = [repair_run, original_run] if endpoint == 'repaired' else [original_run, repair_run]
    for run in ordered:
        case = run / 'episodes' / key / row['arm'] / f"attempt-{row['attempt']}" / 'output' / case_key
        candidates.extend([case / 'controller/events.jsonl', case / 'events.jsonl'])
    return next((p for p in candidates if p.is_file()), None)


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def export(out):
    if out.exists():
        raise ValueError('Choose a new output directory; existing exports are preserved')
    selection = ROOT / 'configs/main_run/selection.csv'
    with selection.open(newline='') as handle:
        panel = list(csv.DictReader(handle))
    expected = {(r['source'], r['task_id'], arm) for r in panel for arm in ARMS}
    rows, receipts, seen = [], [], set()
    out.mkdir(parents=True)
    # Preserve byte-level receipts and verbatim whitespace in recorded messages.
    (out / ".gitattributes").write_text("* -text\n*.md whitespace=-blank-at-eol\n")
    for name in RUNS:
        original_run, repair_run = ROOT / 'runs' / name, ROOT / 'runs' / ('repair-1-' + name)
        original_file, repair_file = repair_run / 'original_results_snapshot.json', repair_run / 'results.json'
        originals = json.loads(original_file.read_text())
        repairs = {(r['source'], r['task_id'], r['arm']): r for r in json.loads(repair_file.read_text())}
        receipts.extend({'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in (original_file, repair_file))
        manifest = json.loads((repair_run / 'manifest.json').read_text())
        if manifest['selection_sha256'] != sha(selection):
            raise ValueError('Run selection differs from the main panel')
        for original in originals:
            arm = original['arm']
            if arm not in ARMS:
                continue
            key = (original['source'], original['task_id'], arm)
            if key not in expected or key in seen:
                raise ValueError('Unexpected or duplicate trial-1 slot')
            seen.add(key)
            row, endpoint = choose_endpoint(original, repairs.get(key))
            record = dict(persona=arm, trial=1, source=key[0], task_id=key[1],
                          family=original.get('family', ''), original_status=original['status'],
                          endpoint=endpoint, native_status='', native_score_0_100='',
                          transcript='', shared_events=0, event_log='', event_log_sha256='',
                          exclusion_reason='')
            if row is None:
                record['exclusion_reason'] = 'No evaluable original or repaired endpoint'
                rows.append(record)
                continue
            config_file = repair_run / 'configs' / f"{arm}.{'exp' if key[0] == 'expbench' else 'shared'}.json"
            config = json.loads(config_file.read_text())
            models = {role: {k: cfg.get(k) for k in ('model', 'provider', 'reasoning_effort')}
                      for role, cfg in config['models'].items()}
            if any(m['model'] != 'gpt-6-astra' or m['reasoning_effort'] != 'low' for m in models.values()):
                raise ValueError('Non-Astra-low model in selected trace run')
            path = event_path(row, original_run, repair_run, endpoint)
            shared = conversation([json.loads(line) for line in path.read_text().splitlines() if line.strip()]) if path else []
            if not shared:
                record['exclusion_reason'] = 'No shared conversation recorded'
                rows.append(record)
                continue
            n = native(row)
            relative = Path(arm) / key[0] / (safe_component(key[0] + ':' + key[1]) + '.md')
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            record.update(native_status=n.get('status', row['status']), native_score_0_100=score(row),
                          transcript=relative.as_posix(), shared_events=len(shared),
                          event_log=str(path.relative_to(ROOT)), event_log_sha256=sha(path))
            lines = [f'# {arm} · {key[0]} · {key[1]}', '',
                     '[All trial-1 traces](../../README.md)', '',
                     f"- Trial: **1**; endpoint: **{endpoint}**; attempt: **{row['attempt']}**.",
                     f"- Native status: **{record['native_status']}**; normalized native score: **{score(row):.4g}/100**.",
                     f"- Recorded protocol: `{n.get('interaction_protocol', 'not recorded')}`.",
                     '- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.',
                     '- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.',
                     '- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.', '',
                     '## Shared conversation', '']
            for item in shared:
                lines += [f"### Event {item['event_index'] + 1} — {item['role']}", '']
                for field, value in item['fields'].items():
                    lines += [f'**{field.replace("_", " ").title()}**', '', fenced(value), '']
            lines += ['## Provenance', '', fenced({'source_run': str(original_run.relative_to(ROOT)),
                      'repair_run': str(repair_run.relative_to(ROOT)), 'event_log': record['event_log'],
                      'event_log_sha256': record['event_log_sha256'], 'models': models})]
            target.write_text(sanitize('\n'.join(lines)) + '\n')
            rows.append(record)
    if seen != expected:
        raise ValueError(f'Missing planned slots: {len(expected - seen)}')
    rows.sort(key=lambda r: (ARMS.index(r['persona']), r['source'], r['task_id']))
    write_csv(out / 'index.csv', rows)
    counts = {arm: {'planned': sum(r['persona'] == arm for r in rows),
                    'published': sum(r['persona'] == arm and bool(r['transcript']) for r in rows)} for arm in ARMS}
    lines = ['# Astra trial-1 interaction traces', '',
             '**One trial per setting:** persona off, 155, 001, 003, and 046; 200 planned questions each.', '',
             'These are saved historical Astra interactions, not new executions of the current SciConv protocol. All three roles use GPT-6 Astra with low reasoning. Sol and cancelled/aborted campaigns are excluded.', '',
             'For each task/persona, an evaluable repaired endpoint is preferred, with the original retained when a repair is unevaluable. Endpoints are never selected by the highest score. Repairs belong to trial 1. This endpoint policy matches available-performance reporting; original-only behavioral/semantic figures can use different endpoints.', '',
             'Only shared simulator–actor conversations are published. Scientific failures, zero scores, and missing submissions remain where a conversation was recorded; infrastructure-only/unusable slots have no transcript and remain visible in the [1,000-slot index](index.csv). Native scores are benchmark-specific and are not a common calibrated quality measure.', '',
             '| Setting | Planned trial-1 slots | Published conversations | Unavailable |', '|---|---:|---:|---:|']
    for arm, count in counts.items():
        lines.append(f"| [{arm}]({arm}/README.md) | {count['planned']} | {count['published']} | {count['planned']-count['published']} |")
        sub = [r for r in rows if r['persona'] == arm]
        arm_lines = [f'# {arm}: trial 1', '', '[Collection](../README.md)', '',
                     '| Benchmark | Question | Native score /100 | Endpoint | Trace / exclusion |', '|---|---|---:|---|---|']
        for r in sub:
            link = f"[Read]({Path(r['transcript']).relative_to(arm).as_posix()})" if r['transcript'] else r['exclusion_reason']
            arm_lines.append(f"| {r['source']} | {r['task_id']} | {r['native_score_0_100']} | {r['endpoint']} | {link} |")
        (out / arm).mkdir(exist_ok=True)
        (out / arm / 'README.md').write_text('\n'.join(arm_lines) + '\n')
    lines += ['', 'Reproduce offline from original local run artifacts with `python scripts/export_trial1_traces.py --output NEW_DIRECTORY`. The exporter refuses to overwrite an existing export. Known credential patterns are redacted from generated messages; original logs remain local and unchanged. [Export manifest](manifest.json) records input and output checksums.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n')
    files = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
    manifest = dict(trial=1, personas=ARMS, counts=counts, selection_sha256=sha(selection),
                    input_receipts=receipts, files_sha256=files,
                    endpoint_counts=dict(Counter(r['endpoint'] for r in rows if r['transcript'])),
                    excluded_counts=dict(Counter(r['exclusion_reason'] for r in rows if not r['transcript'])),
                    generator_sha256=sha(Path(__file__)), inference_calls=0)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for path in out.rglob('*'):
        if path.is_file() and SECRET.search(path.read_text()):
            raise ValueError(f'Credential-pattern check failed: {path.relative_to(out)}')
    print(json.dumps({'counts': counts, 'endpoints': manifest['endpoint_counts'],
                      'total_bytes': sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/astra-actor-astra-simulator-astra-judge/trial-1')
    export(parser.parse_args().output)
