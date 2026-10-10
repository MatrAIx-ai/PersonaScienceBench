"""Offline repeated-panel analysis; no inference or scheduler operations."""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ARMS = ['persona_off', 'candidate_148', 'candidate_155', 'candidate_089', 'candidate_001', 'candidate_127']
SOURCES = ['asibench', 'bixbench', 'discoverybench', 'expbench', 'sciconvbench']
FAMILIES = ['life', 'physical_engineering', 'math_cs', 'social_humanities']
NAMES = dict(zip(SOURCES, ['ASI-Bench', 'BixBench', 'DiscoveryBench', 'EXP-Bench', 'SciConvBench']))
NAMES.update(dict(zip(FAMILIES, ['Life sciences', 'Physical / engineering', 'Math / CS', 'Social / humanities'])))
B = 20000
SEED = 20261004

def label(arm):
    return 'Off' if arm == 'persona_off' else arm.removeprefix('candidate_')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')

def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def selection():
    return list(csv.DictReader((ROOT / 'Experiment/shared/task_selection.csv').open()))

def native(row):
    return next((x for x in row.get('native_results', []) if x.get('episode_id') or x.get('task_id')), {})

def safe_component(value):
    return (re.sub(r'[^A-Za-z0-9_.-]', '_', value).strip('.')[:100] or 'episode') + '-' + sha(value.encode())[:12]

def original_work():
    jobs = json.loads((ROOT / 'Experiment/07_error_repairs/status.json').read_text())['jobs'][:6]
    work, provenance = [], []
    for i, job in enumerate(jobs):
        path = Path(job['run_dir']) / 'original_results_snapshot.json'
        raw = path.read_bytes()
        provenance.append({'path': str(path.resolve().relative_to(ROOT)), 'sha256': sha(raw), 'trial': i % 3 + 1})
        work.extend((i % 3 + 1, job['source_run'], row) for row in json.loads(raw))
    assert len(work) == 3600
    assert len({(t, r['source'], r['task_id'], r['arm']) for t, _, r in work}) == 3600
    return work, provenance

@lru_cache(maxsize=48)
def bootstrap_weights(source, clusters):
    seed = SEED + int(sha(json.dumps([source, clusters]).encode())[:8], 16)
    rng = np.random.default_rng(seed)
    n = len(clusters)
    return rng.multinomial(n, np.full(n, 1 / n), size=B).astype(np.int16)

def summarize(rows, field='value', balanced=False):
    """Average repetitions within task; bootstrap studies within source.

    Input rows must describe one condition or one paired contrast. Paired rows
    are constructed before this function. Intervals condition on observed runs.
    """
    grouped = defaultdict(list)
    for r in rows:
        if r.get(field) is not None:
            assert np.isfinite(r[field]), (field, r[field])
            grouped[(r['source'], r['task_id'], r['study_id'])].append(float(r[field]))
    tasks = [dict(source=k[0], task_id=k[1], study_id=k[2], value=float(np.mean(v)), repeats=len(v)) for k, v in sorted(grouped.items())]
    if not tasks:
        return dict(mean=None, ci95=None, tasks=0, episodes=0, studies=0, source_counts={}, task_sd=None)
    sources = sorted({r['source'] for r in tasks})
    mean = 0.
    boot = np.zeros(B)
    counts, studies = {}, {}
    for source in sources:
        sub = [r for r in tasks if r['source'] == source]
        clusters = tuple(sorted({r['study_id'] for r in sub}))
        sums = np.array([sum(r['value'] for r in sub if r['study_id'] == c) for c in clusters])
        ns = np.array([sum(r['study_id'] == c for r in sub) for c in clusters])
        weight = 1 / len(sources) if balanced else len(sub) / len(tasks)
        counts[source] = len(sub)
        studies[source] = len(clusters)
        mean += np.mean([r['value'] for r in sub]) * weight
        w = bootstrap_weights(source, clusters)
        boot += (w @ sums) / (w @ ns) * weight
    vals = [r['value'] for r in tasks]
    return dict(mean=float(mean), ci95=np.quantile(boot, [.025, .975]).tolist(), tasks=len(tasks),
                episodes=sum(r['repeats'] for r in tasks), studies=sum(studies.values()),
                studies_by_source=studies, source_counts=counts,
                task_sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else None)

def paired(rows, field, arm, predicate=None):
    off = {(r['trial'], r['source'], r['task_id']): r for r in rows if r['arm'] == 'persona_off'}
    out = []
    for r in rows:
        if r['arm'] != arm or r.get(field) is None:
            continue
        b = off.get((r['trial'], r['source'], r['task_id']))
        if b is None or b.get(field) is None or (predicate and not predicate(r, b)):
            continue
        out.append({**r, 'value': r[field] - b[field], 'baseline': b[field], 'persona_value': r[field]})
    return out

def cell(s, signed=False, counts=True):
    if s['mean'] is None:
        return '—'
    fmt = '+.2f' if signed else '.2f'
    text = f"{s['mean']:{fmt}} [{s['ci95'][0]:.2f}, {s['ci95'][1]:.2f}]"
    return text + (f"; n={s['tasks']}, e={s['episodes']}" if counts else '')

def markdown_table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers),
                      *['| ' + ' | '.join(map(str, row)) + ' |' for row in rows]])
