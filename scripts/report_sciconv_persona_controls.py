#!/usr/bin/env python3
"""Regenerate the SciConv persona-controls report data from local run directories.

No model calls. Reads each run's finished/ records, native judge outputs, controller events
and API usage; writes results.json, results.csv, summary.json and runtime_config.json.
Permutation tests use fixed seeds, so outputs are deterministic.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
from math import comb
from pathlib import Path
import random
import statistics as st
from collections import Counter, defaultdict

N_PERM = 20000


def read(path):
    return json.loads(Path(path).read_text())


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def episode_rows(study, run):
    run = Path(run)
    manifest = read(run / 'manifest.json')
    retried = set()
    if (run / 'RETRY.json').exists():
        retry = read(run / 'RETRY.json')
        retried |= set(retry.get('jobs', [])) | set(retry.get('second_retry', {}).get('jobs', []))
    rows = []
    for job in manifest['jobs']:
        finished = run / 'finished' / f"{job['key']}.json"
        row = {'study': study, 'arm': job['arm'], 'case': job['slug'].replace('_disambiguation_', '/disambiguation/'),
               'rep': job['rep'], 'retried': job['key'] in retried}
        if not finished.exists():
            rows.append({**row, 'status': 'pending'})
            continue
        record = read(finished)
        row['status'] = record['status']
        if record['status'] == 'scored':
            case = Path(record['result']).parent
            result = read(record['result'])
            native = result['evaluation']['details']['native_case']
            k, n = map(int, read(next(case.glob('llm_judge_disambiguation_score.json')))['score'].split('/'))
            events = jsonl(case / 'controller/events.jsonl')
            usage = [c.get('usage') or {} for c in jsonl(case / 'controller/api_calls.private.jsonl')]
            replies = sum(e['type'] == 'researcher_reply' for e in events)
            row.update({
                'FRR': result['evaluation']['metrics']['FRR'], 'FR': int(bool(native['FR'])), 'IC': int(bool(native['IC'])),
                'facts_recovered': k, 'facts_total': n, 'recovery_share': round(k / n, 6) if n else None,
                'researcher_replies': replies, 'question_limit_hit': int(replies >= 10),
                'prompt_tokens': sum(u.get('prompt_tokens', 0) or 0 for u in usage),
                'completion_tokens': sum(u.get('completion_tokens', 0) or 0 for u in usage),
                'cost_usd': round(sum((u.get('cost') or 0) + ((u.get('cost_details') or {}).get('upstream_inference_cost') or 0)
                                      for u in usage), 6)})
        rows.append(row)
    return rows


def cost_all_attempts(run):
    total = 0.0
    for path in glob.glob(f'{run}/**/api_calls.private.jsonl', recursive=True):
        for call in jsonl(path):
            u = call.get('usage') or {}
            total += (u.get('cost') or 0) + ((u.get('cost_details') or {}).get('upstream_inference_cost') or 0)
    return round(total, 4)


def fisher(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    p = lambda x: comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)
    obs = p(a)
    return sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= obs + 1e-12)


def stratified(values, xs, ys, seed=0):
    """values[case][arm] -> list; mean over cases of (mean xs - mean ys); within-case label permutation."""
    data = {c: ([v for a in xs for v in values[c].get(a, [])], [v for a in ys for v in values[c].get(a, [])]) for c in values}
    data = {c: d for c, d in data.items() if d[0] and d[1]}
    obs = st.mean(st.mean(x) - st.mean(y) for x, y in data.values())
    rng, ge = random.Random(seed), 0
    for _ in range(N_PERM):
        diffs = []
        for x, y in data.values():
            pool = x + y
            rng.shuffle(pool)
            diffs.append(st.mean(pool[:len(x)]) - st.mean(pool[len(x):]))
        ge += abs(st.mean(diffs)) >= abs(obs) - 1e-12
    return {'difference': round(obs, 4), 'p': round((ge + 1) / (N_PERM + 1), 4), 'cases': len(data)}


def rerun_summary(rows, manifest):
    both, neither = manifest['groups']['both_pass_v2'], manifest['groups']['neither_pass_v2_sample']
    group = {a: 'both_pass_v2' for a in both} | {a: 'neither_pass_v2' for a in neither} | {'persona_off': 'persona_off'}
    scored = [r for r in rows if r['status'] == 'scored']
    cells = defaultdict(lambda: [0, 0])
    for r in scored:
        cells[f"{r['case']}|{group[r['arm']]}"][0] += r['FRR']
        cells[f"{r['case']}|{group[r['arm']]}"][1] += 1
    per_persona = {a: st.mean(r['FRR'] for r in scored if r['arm'] == a) for a in both + neither}
    labels = [group[a] for a in per_persona]
    def gap(assign):
        b = [per_persona[a] for a, g in zip(per_persona, assign) if g == 'both_pass_v2']
        n = [per_persona[a] for a, g in zip(per_persona, assign) if g == 'neither_pass_v2']
        return st.mean(b) - st.mean(n)
    obs = gap(labels)
    rng, ge = random.Random(0), 0
    for _ in range(N_PERM):
        ge += abs(gap(rng.sample(labels, len(labels)))) >= abs(obs) - 1e-12
    rng, boots = random.Random(1), []
    b_vals = [per_persona[a] for a in both]
    n_vals = [per_persona[a] for a in neither]
    for _ in range(N_PERM):
        boots.append(st.mean(rng.choices(b_vals, k=len(b_vals))) - st.mean(rng.choices(n_vals, k=len(n_vals))))
    boots.sort()
    foam = [r for r in scored if r['case'].startswith('foam')]
    off_f = [r['FRR'] for r in foam if r['arm'] == 'persona_off']
    on_f = [r['FRR'] for r in foam if r['arm'] != 'persona_off']
    by_group = {g: {'FRR': f"{sum(r['FRR'] for r in scored if group[r['arm']] == g)}/{sum(group[r['arm']] == g for r in scored)}",
                    'question_limit_hits': sum(r['question_limit_hit'] for r in scored if group[r['arm']] == g)}
                for g in ('persona_off', 'both_pass_v2', 'neither_pass_v2')}
    return {'groups': manifest['groups'], 'frr_by_case_and_group': {k: f'{v[0]}/{v[1]}' for k, v in sorted(cells.items())},
            'frr_by_group': by_group,
            'per_persona_frr': {a: round(v, 4) for a, v in per_persona.items()},
            'both_minus_neither': {'difference': round(obs, 4), 'p_persona_permutation': round((ge + 1) / (N_PERM + 1), 4),
                                   'bootstrap_95ci': [round(boots[int(0.025 * N_PERM)], 4), round(boots[int(0.975 * N_PERM)], 4)]},
            'foam_off_vs_any_persona': {'off': f'{sum(off_f)}/{len(off_f)}', 'personas': f'{sum(on_f)}/{len(on_f)}',
                                        'fisher_p': round(fisher(sum(off_f), len(off_f) - sum(off_f), sum(on_f), len(on_f) - sum(on_f)), 4),
                                        'note': 'post hoc'}}


def screen_summary(rows):
    by = defaultdict(list)
    for r in rows:
        if r['status'] == 'scored':
            by[r['case']].append(r)
    frr_band, share_band = Counter(), Counter()
    candidates = []
    for case, rs in by.items():
        solved = sum(r['FRR'] for r in rs)
        frr_band['floor' if solved == 0 else 'ceiling' if solved == len(rs) else 'mid'] += 1
        n, m = rs[0]['facts_total'], st.mean(r['recovery_share'] for r in rs)
        band = 'single_fact' if n == 1 else 'near_ceiling' if m > 0.9 else 'low' if m < 0.3 else 'multi_fact_mid'
        share_band[band] += 1
        if band == 'multi_fact_mid':
            candidates.append({'case': case, 'facts': n, 'mean_recovery': round(m, 4), 'solved': f'{solved}/{len(rs)}'})
    return {'frr_bands': dict(frr_band), 'recovery_share_bands': dict(share_band),
            'question_limit_hits': sum(r.get('question_limit_hit', 0) for r in rows if r['status'] == 'scored'),
            'multi_fact_mid_candidates': sorted(candidates, key=lambda c: c['case'])}


def arm_values(rows, cases):
    values = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r['status'] == 'scored' and r['case'] in cases:
            values[r['case']][r['arm']].append(r['recovery_share'])
    return values


def arm_means(values, arms):
    return {a: {'mean_recovery': round(st.mean(st.mean(values[c][a]) for c in values if values[c].get(a)), 4),
                'episodes': sum(len(values[c].get(a, [])) for c in values)} for a in arms}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rerun', 'screen', 'confirm', 'neutral', 'paraphrase'):
        p.add_argument(f'--{name}', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    studies = {'v2_rerun': a.rerun, 'difficulty_screen': a.screen, 'confirmation': a.confirm,
               'neutral_arms': a.neutral, 'paraphrase_prereg': a.paraphrase}
    rows = [row for study, run in studies.items() for row in episode_rows(study, run)]
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
    columns = []
    for r in rows:
        columns += [c for c in r if c not in columns]
    with (a.output / 'results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

    by_study = defaultdict(list)
    for r in rows:
        by_study[r['study']].append(r)
    screen = screen_summary(by_study['difficulty_screen'])
    cases = {c['case'] for c in screen['multi_fact_mid_candidates']}
    off_rows = [r for r in by_study['difficulty_screen'] + by_study['confirmation'] if r['arm'] == 'persona_off']
    confirm_vals = arm_values(off_rows, cases)
    confirmation = {c: {'runs': len(v['persona_off']), 'mean_recovery': round(st.mean(v['persona_off']), 4),
                        'sd': round(st.pstdev(v['persona_off']), 4), 'kept': 0.25 <= st.mean(v['persona_off']) <= 0.90}
                    for c, v in sorted(confirm_vals.items())}
    confirmed = {c for c, v in confirmation.items() if v['kept']}

    neutral_vals = arm_values(off_rows + by_study['neutral_arms'], confirmed)
    for c in neutral_vals:
        neutral_vals[c]['neutral_pooled'] = neutral_vals[c]['neutral_a'] + neutral_vals[c]['neutral_b']
        neutral_vals[c]['persona_pooled'] = neutral_vals[c]['candidate_148'] + neutral_vals[c]['candidate_155']
    neutral = {'arms': arm_means(neutral_vals, ['persona_off', 'neutral_a', 'neutral_b', 'candidate_148', 'candidate_155']),
               'contrasts': {f'{x} - {y}': stratified(neutral_vals, [x], [y]) for x, y in [
                   ('neutral_pooled', 'persona_off'), ('persona_pooled', 'persona_off'), ('neutral_b', 'neutral_a'),
                   ('persona_pooled', 'neutral_pooled'), ('candidate_148', 'persona_off'), ('candidate_155', 'persona_off'),
                   ('neutral_a', 'persona_off'), ('neutral_b', 'persona_off')]}}

    para_off = off_rows + [r for r in by_study['paraphrase_prereg'] if r['arm'] == 'persona_off']
    para_vals = arm_values(para_off + [r for r in by_study['paraphrase_prereg'] if r['arm'] != 'persona_off'], confirmed)
    paraphrase = {'arms': arm_means(para_vals, ['persona_off', 'neutral_a', 'neutral_a_swap', 'neutral_c', 'neutral_d']),
                  'H1_trait_sentence': stratified(para_vals, ['neutral_a', 'neutral_c'], ['neutral_a_swap', 'neutral_d']),
                  'H2_fresh_neutral_a_vs_off': stratified(para_vals, ['neutral_a'], ['persona_off']),
                  'secondary': {f"{'+'.join(x)} - {'+'.join(y)}": stratified(para_vals, x, y) for x, y in [
                      (['neutral_a'], ['neutral_a_swap']), (['neutral_c'], ['neutral_d']), (['neutral_a_swap'], ['persona_off']),
                      (['neutral_c'], ['persona_off']), (['neutral_d'], ['persona_off']),
                      (['neutral_a', 'neutral_a_swap', 'neutral_c', 'neutral_d'], ['persona_off'])]},
                  'decision_rule': 'each primary test needs p < 0.025 (Bonferroni over two)'}

    # Sensitivity: the native loop drops the 10th answer, so repeat the key contrasts without limit-hit episodes.
    def no_limit(rs):
        return [r for r in rs if r['status'] == 'scored' and not r['question_limit_hit']]
    nv = arm_values(no_limit(off_rows + by_study['neutral_arms']), confirmed)
    for c in nv:
        nv[c]['neutral_pooled'] = nv[c]['neutral_a'] + nv[c]['neutral_b']
        nv[c]['persona_pooled'] = nv[c]['candidate_148'] + nv[c]['candidate_155']
    pv = arm_values(no_limit(para_off + by_study['paraphrase_prereg']), confirmed)
    sensitivity = {
        'question_limit_hits_by_study_and_arm': {s: {arm: f"{sum(r['question_limit_hit'] for r in by_study[s] if r['arm'] == arm and r['status'] == 'scored')}/"
                                                       f"{sum(r['arm'] == arm and r['status'] == 'scored' for r in by_study[s])}"
                                                 for arm in sorted({r['arm'] for r in by_study[s]})} for s in studies},
        'excluding_limit_hits': {
            'neutral_pooled - persona_off': stratified(nv, ['neutral_pooled'], ['persona_off']),
            'persona_pooled - persona_off': stratified(nv, ['persona_pooled'], ['persona_off']),
            'H1_trait_sentence': stratified(pv, ['neutral_a', 'neutral_c'], ['neutral_a_swap', 'neutral_d']),
            'H2_fresh_neutral_a_vs_off': stratified(pv, ['neutral_a'], ['persona_off'])}}

    summary = {
        'sensitivity': sensitivity,
        'status_counts': {s: dict(Counter(r['status'] for r in by_study[s])) for s in studies},
        'retried_episodes': {s: sum(r['retried'] for r in by_study[s]) for s in studies},
        'cost_usd_all_attempts': {s: cost_all_attempts(run) for s, run in studies.items()},
        'v2_rerun': rerun_summary(by_study['v2_rerun'], read(a.rerun / 'manifest.json')),
        'difficulty_screen': screen, 'confirmation': confirmation, 'neutral_arms': neutral, 'paraphrase_prereg': paraphrase}
    (a.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')

    identities = {}
    for run in (a.neutral, a.paraphrase, a.rerun):
        identities |= {k: v for k, v in read(Path(run) / 'manifest.json').get('identity_sha256', {}).items() if v}
    config = {
        'code_revision': '75e3f08 (all runs; before PR #6 fb2d8c1)',
        'config': 'configs/full_persona_v2/shared.json at 75e3f08: unrestricted_knowledge=true (v2 settings); persona replaced per arm',
        'models': read(Path(a.screen) / 'configs/persona_off/shared.json')['models'],
        'identity_sha256': identities,
        'seeds': {s: read(Path(run) / 'manifest.json').get('seed') for s, run in studies.items()},
        'permutations': N_PERM,
        'sources': {'SciConvBench': 'https://github.com/csml-rpi/SciConvBench.git @ 8d1528ed86b54cb4437f8f921e0f396511acd104'},
        'driver_sha256': {s: {k: v for k, v in read(Path(run) / 'manifest.json')['source_sha256'].items() if k.startswith('scripts/')}
                          for s, run in studies.items()},
        'src_tree_sha256': {s: hashlib.sha256(json.dumps({k: v for k, v in read(Path(run) / 'manifest.json')['source_sha256'].items()
                                                          if k.startswith('src/')}, sort_keys=True).encode()).hexdigest()
                            for s, run in studies.items()}}
    (a.output / 'runtime_config.json').write_text(json.dumps(config, indent=2) + '\n')
    print(json.dumps(summary['status_counts']), json.dumps(summary['cost_usd_all_attempts']))


if __name__ == '__main__':
    main()
