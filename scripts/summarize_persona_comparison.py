"""Compare fixed-case Luna runs without combining unlike benchmark scores."""
import json
from datetime import datetime, timezone
from pathlib import Path

from personasciencebench.terminal_scoring import MISSING_SUBMISSION_POLICY, terminal_score_fields

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/luna-cs-novice-five'


def read(path):
    return json.loads(path.read_text())


def main():
    baseline = read(ROOT / 'reports/luna_no_persona_five.json')
    rows = []
    attempts = [RUN, *sorted(RUN.glob('restart-*'))]
    names = {'discoverybench': ('DiscoveryBench', 'final_score'), 'bixbench': ('BixBench', 'grade'),
             'scienceagentbench': ('ScienceAgentBench', 'success_rate')}
    for p in [p for attempt in attempts for kind in ('python', 'sab-grades') for p in sorted((attempt / kind).glob('*/result.json'))]:
        r = read(p)
        name, metric = names[r['benchmark']]
        rows.append({'benchmark': name, 'task': r['source_task_id'], 'status': r['status'],
                     'metric': metric, 'score': r.get('evaluation', {}).get('metrics', {}).get(metric),
                     'questions': r.get('researcher_questions'), 'record': str(p.relative_to(ROOT))})
    for p in [p for attempt in attempts for p in sorted((attempt / 'expbench').glob('*/result.json'))]:
        r = read(p)
        rows.append({'benchmark': 'EXP-Bench', 'task': r['task_id'], 'status': r['status'],
                     'metric': 'reference coverage / 100', 'score': (r.get('initial') or {}).get('coverage_mean'),
                     'questions': r.get('researcher_questions'), 'record': str(p.relative_to(ROOT))})
    for p in [p for attempt in attempts for p in sorted((attempt / 'terminal').glob('*/result.json'))]:
        r = read(p)
        rows.append({'benchmark': 'Terminal-Bench-Science', 'task': r['episode_id'].split(':', 1)[1],
                     'metric': 'reward', **terminal_score_fields(r),
                     'questions': r.get('researcher_questions'), 'record': str(p.relative_to(ROOT))})
    rows = list({(r['benchmark'], r['task']): r for r in rows}.values())
    baseline_by_id = {(r['benchmark'], r['task']): r for r in baseline['cases']}
    for row in rows:
        base = baseline_by_id[(row['benchmark'], row['task'])]
        row['baseline_score'] = base['score']
        row['baseline_status'] = base['status']
        row['baseline_score_source'] = base.get('score_source', 'benchmark_evaluator' if base['score'] is not None else 'unscored')
        row['baseline_native_graded'] = base.get('native_graded')
        row['baseline_questions'] = base['questions']
        row['paired_delta'] = row['score'] - base['score'] if row['score'] is not None and base['score'] is not None else None
    summary = []
    for name in ['DiscoveryBench', 'BixBench', 'ScienceAgentBench', 'EXP-Bench', 'Terminal-Bench-Science']:
        base = [r for r in baseline['cases'] if r['benchmark'] == name]
        selected = [r for r in rows if r['benchmark'] == name]
        scored = [r['score'] for r in selected if r['score'] is not None]
        base_scores = [r['score'] for r in base if r['score'] is not None]
        paired = [r['paired_delta'] for r in selected if r['paired_delta'] is not None]
        graded = [r['score'] for r in selected if r['score'] is not None
                  and r.get('score_source') != 'missing_submission_policy']
        base_graded = [r['score'] for r in base if r['score'] is not None
                       and r.get('score_source') != 'missing_submission_policy']
        paired_graded = [r['paired_delta'] for r in selected if r['paired_delta'] is not None
                         and r.get('score_source') != 'missing_submission_policy'
                         and r.get('baseline_score_source') != 'missing_submission_policy']
        summary.append({'benchmark': name, 'requested': 5, 'persona_finished': len(selected),
                        'baseline_scored': len(base_scores), 'persona_scored': len(scored),
                        'baseline_graded': len(base_graded), 'persona_graded': len(graded),
                        'baseline_native_graded': len(base_graded) if name == 'Terminal-Bench-Science' else None,
                        'persona_native_graded': len(graded) if name == 'Terminal-Bench-Science' else None,
                        'baseline_policy_assigned_zeros': len(base_scores) - len(base_graded),
                        'persona_policy_assigned_zeros': len(scored) - len(graded),
                        'baseline_mean_on_scored': sum(base_scores)/len(base_scores) if base_scores else None,
                        'persona_mean_on_scored': sum(scored)/len(scored) if scored else None,
                        'baseline_mean_on_graded': sum(base_graded)/len(base_graded) if base_graded else None,
                        'persona_mean_on_graded': sum(graded)/len(graded) if graded else None,
                        'paired_scored_cases': len(paired), 'paired_graded_cases': len(paired_graded),
                        'mean_paired_delta': sum(paired)/len(paired) if paired else None,
                        'mean_paired_graded_delta': sum(paired_graded)/len(paired_graded) if paired_graded else None,
                        'baseline_questions': sum(r.get('questions') or 0 for r in base),
                        'persona_questions': sum(r.get('questions') or 0 for r in selected)})
    cost = 0.0
    for p in RUN.glob('**/api_calls.private.jsonl'):
        lines = p.read_text().splitlines()
        for index, line in enumerate(lines):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                if index == len(lines) - 1:
                    continue
                raise
            value = record.get('usage', {}).get('cost')
            if isinstance(value, (int, float)):
                cost += value
    for p in [p for attempt in attempts for p in (attempt / 'expbench').glob('*/result.json')]:
        cost += read(p).get('budget_charge_usd', 0)
    data = {'updated_at': datetime.now(timezone.utc).isoformat(), 'model': 'openai/gpt-6-luna',
            'reasoning_effort': 'none', 'persona': read(ROOT / 'configs/luna-cs-novice-five.json')['persona'],
            'requested_cases': 25, 'finished_cases': len(rows),
            'persona_scored_cases': sum(s['persona_scored'] for s in summary),
            'persona_graded_cases': sum(s['persona_graded'] for s in summary),
            'baseline_scored_cases': sum(s['baseline_scored'] for s in summary),
            'baseline_graded_cases': sum(s['baseline_graded'] for s in summary),
            'terminal_scoring_policy': MISSING_SUBMISSION_POLICY,
            'summary': summary, 'cases': rows,
            'persona_recorded_cost_usd': cost, 'baseline_recorded_cost_usd': baseline['total_recorded_cost_usd'],
            'cross_benchmark_average': None}
    encoded = json.dumps(data, indent=2) + '\n'
    (ROOT / 'reports/luna_cs_novice_comparison.json').write_text(encoded)
    (RUN / 'summary.json').write_text(encoded)
    def score(value):
        return '—' if value is None else f'{value:.4f}'
    lines = ['# Luna: fixed computer-science novice persona', '',
        f"Updated {data['updated_at']}. Persona condition: {len(rows)}/25 cases have final records.", '',
        'The same 25 task IDs, source data, approved study facts, model IDs, reasoning effort,',
        '20 actor iterations, and six-question limit are used in both conditions.',
        'The added persona has computer-science domain knowledge, statistics, and coding',
        'all set to novice. Other persona attributes retain the shared neutral defaults.', '',
        '| Benchmark | Baseline scored | Baseline mean | Persona finished | Persona scored | Persona mean | Paired mean delta (n) |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s in summary:
        lines.append(f"| {s['benchmark']} | {s['baseline_scored']}/5 | {score(s['baseline_mean_on_scored'])} | {s['persona_finished']}/5 | {s['persona_scored']}/5 | {score(s['persona_mean_on_scored'])} | {score(s['mean_paired_delta'])} ({s['paired_scored_cases']}) |")
    lines += ['', 'EXP-Bench scores are reference coverage out of 100; other scores are out of 1.',
              'Means use scored cases; denominators can differ. Paired deltas include only task IDs',
              'scored in both conditions. Terminal no-submission outcomes count as false (`reward=0`)',
              'under `terminal-missing-submission-false-v1`, with `missing_submission` retained.',
              'These policy zeros are separate from native grades. Infrastructure errors remain',
              'unscored, and historical raw attempts are unchanged.', '',
              '| Benchmark | Baseline graded | Baseline policy zeros | Persona graded | Persona policy zeros | Paired graded cases |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for s in summary:
        lines.append(f"| {s['benchmark']} | {s['baseline_graded']}/5 | {s['baseline_policy_assigned_zeros']} | {s['persona_graded']}/5 | {s['persona_policy_assigned_zeros']} | {s['paired_graded_cases']} |")
    lines += ['', 'For Terminal, graded means a native verifier returned a reward. Other benchmarks',
              'use their configured benchmark evaluator.', '',
              '| Benchmark | Task | Baseline | Persona | Persona status | Persona score source | Researcher questions (baseline → persona) |',
              '| --- | --- | ---: | ---: | --- | --- | ---: |']
    for r in rows:
        lines.append(f"| {r['benchmark']} | `{r['task']}` | {score(r['baseline_score'])} | {score(r['score'])} | {r['status']} | {r.get('score_source', 'benchmark_evaluator' if r['score'] is not None else 'unscored')} | {r['baseline_questions']} → {r['questions']} |")
    lines += ['', '## Interpretation and controls', '',
        '- The original 25 cases were launched concurrently. After host interruption, seven unfinished actors were restarted concurrently and two saved SAB submissions were graded without rerunning their actors. Completed cases were retained; replacement results are merged by task ID.',
        '- Recorded charges include logged Python/Terminal attempts and completed EXP-Bench attempts; interrupted EXP-Bench charges may be missing.',
        '- No persona identity is exposed directly to the actor. Its effect can occur through simulator replies; cases where the actor never asks a question do not exercise that channel.',
        '- The persona adds the shared identity prompt with novice expertise and neutral defaults. This is a fixed-profile comparison against no persona, not an isolated causal estimate for each expertise attribute.',
        '- EXP-Bench retains its extractive disclosure rule: persona conditions relevance/fact selection, while published replies remain approved fact text. The other shared adapters use their existing grounded-reply policy.',
        '- SAB 87 uses the same expanded NetCDF environment as its final baseline attempt; the other Python cases retain the original scientific environment.',
        '- Terminal uses the same native actor images and the working separate Docker network-none grader from the final baseline. Native scientific grading scripts are unchanged.',
        '- One run per task and condition does not establish a reliable persona effect. Model sampling, judge variability, and concurrent runtime contention remain possible explanations of differences.',
        '- No additional unit-test suite was run; validation uses the requested live cases.', '',
        f"Recorded persona model charges: ${cost:.6f}; retained baseline charges: ${baseline['total_recorded_cost_usd']:.6f}.", '',
        'Configs: `configs/luna-cs-novice-five.json` and `configs/expbench/luna-cs-novice.toml`.',
        'Full per-case paths are in `reports/luna_cs_novice_comparison.json`.', '']
    (ROOT / 'reports/luna_cs_novice_comparison.md').write_text('\n'.join(lines))
    print(json.dumps({'finished': len(rows), 'summary': summary, 'recorded_cost_usd': cost}, indent=2))


if __name__ == '__main__':
    main()
