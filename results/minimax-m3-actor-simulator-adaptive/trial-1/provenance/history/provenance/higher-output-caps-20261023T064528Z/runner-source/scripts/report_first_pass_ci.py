#!/usr/bin/env python3
"""Matched-task descriptive means and paired, source-stratified bootstrap CIs."""
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np

ARMS = ['persona_off', 'candidate_148', 'candidate_155']
SOURCES = ['asibench', 'bixbench', 'discoverybench', 'expbench', 'sciconvbench']
FAMILIES = ['life_sciences', 'physical_sciences', 'math_cs', 'social_humanities']


def native(row):
    return next((x for x in row.get('native_results', []) if x.get('episode_id') or x.get('task_id')), {})


def score(row):
    x = native(row)
    if row['status'] == 'infrastructure_error':
        return None
    if x.get('status') == 'missing_submission':
        return 0.0
    evaluation = x.get('evaluation') or {}
    m = evaluation.get('metrics', {})
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
        return (x.get('final') or x.get('initial') or {}).get('gated_coverage_mean')
    raise ValueError(source)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--resamples', type=int, default=20000)
    p.add_argument('--seed', type=int, default=20260929)
    a = p.parse_args()
    rows = json.loads((a.run_dir/'results.json').read_text())
    by_task = {}
    for row in rows:
        key = (row['source'], row['task_id'])
        item = by_task.setdefault(key, {'source': row['source'], 'task_id': row['task_id'], 'family': row['family'], 'scores': {}})
        if row['arm'] in item['scores']:
            raise ValueError('Duplicate condition for task')
        item['scores'][row['arm']] = score(row)
    matched = [v for v in by_task.values() if all(v['scores'].get(arm) is not None for arm in ARMS)]
    rng = np.random.default_rng(a.seed)

    def summarize(group):
        means = np.mean([[r['scores'][arm] for arm in ARMS] for r in group], axis=0)
        boot = np.zeros((a.resamples, len(ARMS)))
        # Fixed observed source weights within each family; same indices for all arms.
        for source in SOURCES:
            sub = [r for r in group if r['source'] == source]
            if not sub:
                continue
            values = np.array([[r['scores'][arm] for arm in ARMS] for r in sub])
            indices = rng.integers(0, len(sub), size=(a.resamples, len(sub)))
            boot += values[indices].sum(axis=1) / len(group)
        limits = np.quantile(boot, [0.025, 0.975], axis=0)
        return {'tasks': len(group), 'source_counts': dict(Counter(r['source'] for r in group)),
                'arms': {arm: {'mean': float(means[i]), 'ci95': limits[:,i].tolist()} for i, arm in enumerate(ARMS)}}

    output = {'method': {'resamples': a.resamples, 'seed': a.seed,
        'interval': 'Percentile bootstrap, 2.5th and 97.5th percentiles; paired task resampling across conditions, stratified by benchmark source.',
        'population': 'Matched evaluable tasks across all three conditions; missing submissions zero, infrastructure/evaluation errors excluded in all conditions.',
        'family_aggregation': 'Task-weighted mean of native metrics normalized to 0–100. Within-family source counts held fixed in bootstrap; descriptive composite, not a common calibrated scientific measure.',
        'limitations': 'One episode per condition. Intervals reflect task sampling variation, not repeat-run/model randomness. Task bootstrap does not account for dependence among tasks from the same study. Pointwise intervals, not simultaneous intervals or tests of persona differences.'},
        'matched_tasks': len(matched),
        'benchmarks': {s: summarize([r for r in matched if r['source']==s]) for s in SOURCES},
        'superfamilies': {f: summarize([r for r in matched if r['family']==f]) for f in sorted({r['family'] for r in matched})}}
    out = a.run_dir/'analysis';out.mkdir(exist_ok=True)
    (out/'confidence_intervals.json').write_text(json.dumps(output, indent=2)+'\n')
    (out/'matched_task_scores.json').write_text(json.dumps(matched, indent=2)+'\n')
    lines=[]
    for title, group in [('Benchmark',output['benchmarks']),('Super-family',output['superfamilies'])]:
        lines += [f'| {title} | Tasks | Persona off | Persona 148 | Persona 155 |', '|---|---:|---:|---:|---:|']
        for name,v in group.items():
            cells=[f"{v['arms'][arm]['mean']:.2f} [{v['arms'][arm]['ci95'][0]:.2f}, {v['arms'][arm]['ci95'][1]:.2f}]" for arm in ARMS]
            lines.append('| '+name+' | '+str(v['tasks'])+' | '+' | '.join(cells)+' |')
        lines.append('')
    lines += [f"Method: {v}" for v in output['method'].values()]
    (out/'confidence_intervals.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
