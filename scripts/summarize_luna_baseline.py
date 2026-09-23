"""Summarize this explicit five-case batch without reading private prompt text."""
import json
from pathlib import Path
from datetime import datetime, timezone

from personasciencebench.terminal_scoring import MISSING_SUBMISSION_POLICY, terminal_score_fields

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/luna-no-persona-five'


def load(path):
    return json.loads(path.read_text())


def main():
    rows = []
    exp = RUN / 'expbench/summary.json'
    if exp.exists():
        for r in load(exp)['results']:
            initial = r.get('initial') or {}
            rows.append({'benchmark': 'EXP-Bench', 'task': r['task_id'], 'status': r['status'],
                         'metric': 'reference coverage / 100', 'score': initial.get('coverage_mean'),
                         'questions': r.get('researcher_questions'),
                         'record': str((exp.parent / r['task_id'].replace('/', '__') / 'result.json').relative_to(ROOT))})
    names = {'discoverybench': ('DiscoveryBench', 'final_score'), 'bixbench': ('BixBench', 'grade'),
             'scienceagentbench': ('ScienceAgentBench', 'success_rate')}
    python_results = {}
    for directory in ['python-runtime-fixed', 'sab-netcdf-retry']:
        for p in sorted((RUN / directory).glob('*/result.json')):
            r = load(p)
            python_results[r['episode_id']] = (r, p)
    for r, p in python_results.values():
        name, metric = names[r['benchmark']]
        rows.append({'benchmark': name, 'task': r['source_task_id'], 'status': r['status'],
                     'metric': metric, 'score': r.get('evaluation', {}).get('metrics', {}).get(metric),
                     'questions': r.get('researcher_questions'), 'record': str(p.relative_to(ROOT))})
    for p in sorted((RUN / 'terminal').glob('*/result.json')):
        r = load(p)
        replacement = p.parent / 'evaluation-compose-fixed.json'
        if (p.parent / 'native-docker/evaluation.json').exists():
            replacement = p.parent / 'native-docker/evaluation.json'
        if (p.parent / 'native-docker-verdict-fixed/evaluation.json').exists():
            replacement = p.parent / 'native-docker-verdict-fixed/evaluation.json'
        evaluation = load(replacement) if replacement.exists() else r.get('evaluation', {})
        rows.append({'benchmark': 'Terminal-Bench-Science', 'task': r['episode_id'].split(':', 1)[1],
                     'metric': 'reward', **terminal_score_fields(r, evaluation),
                     'questions': r.get('researcher_questions'), 'record': str(p.relative_to(ROOT)),
                     'replacement_evaluation': str(replacement.relative_to(ROOT)) if replacement.exists() else None})
    costs = {}
    for p in RUN.glob('**/api_calls.private.jsonl'):
        for line in p.read_text().splitlines():
            r = json.loads(line)
            cost = r.get('usage', {}).get('cost')
            if isinstance(cost, (int, float)):
                role = r.get('role', 'unknown')
                costs[role] = costs.get(role, 0) + cost
    exp_cost = sum(r.get('budget_charge_usd', 0) for r in load(exp).get('results', [])) if exp.exists() else 0
    summary = []
    for name in ['DiscoveryBench', 'BixBench', 'ScienceAgentBench', 'EXP-Bench', 'Terminal-Bench-Science']:
        selected = [r for r in rows if r['benchmark'] == name]
        scored = [r['score'] for r in selected if r['score'] is not None]
        graded = [r['score'] for r in selected if r['score'] is not None
                  and r.get('score_source') != 'missing_submission_policy']
        policy_zeros = sum(r.get('score_source') == 'missing_submission_policy' for r in selected)
        summary.append({'benchmark': name, 'requested': 5, 'finished': len(selected),
                        'scored': len(scored), 'graded': len(graded),
                        'native_graded': len(graded) if name == 'Terminal-Bench-Science' else None,
                        'policy_assigned_zeros': policy_zeros,
                        'mean_on_graded': sum(graded)/len(graded) if graded else None,
                        'mean_on_scored': sum(scored)/len(scored) if scored else None,
                        'statuses': {status: sum(r['status'] == status for r in selected)
                                     for status in sorted({r['status'] for r in selected})}})
    data = {'updated_at': datetime.now(timezone.utc).isoformat(), 'model': 'openai/gpt-6-luna',
            'reasoning_effort': 'none', 'persona_enabled': False, 'simulator_enabled': True,
            'requested_cases': 25, 'finished_cases': len(rows),
            'scored_cases': sum(s['scored'] for s in summary),
            'graded_cases': sum(s['graded'] for s in summary),
            'terminal_scoring_policy': MISSING_SUBMISSION_POLICY,
            'summary': summary, 'cases': rows,
            'python_and_terminal_reported_cost_by_role_usd': costs,
            'expbench_budget_charge_usd': exp_cost,
            'total_recorded_cost_usd': sum(costs.values()) + exp_cost,
            'cross_benchmark_average': None}
    (ROOT / 'reports/luna_no_persona_five.json').write_text(json.dumps(data, indent=2) + '\n')
    (RUN / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
    lines = ['# Five-case Luna baseline', '', f"Updated {data['updated_at']}. {len(rows)}/25 cases have final run records.", '',
        'All model roles use `openai/gpt-6-luna`, reasoning effort `none`. The simulator',
        'is enabled with approved study knowledge and no persona styling. Native',
        'programmatic graders are retained for ScienceAgentBench and Terminal.', '',
        '| Benchmark | Finished | Graded | Policy zeros | Scored | Mean on scored cases |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for s in summary:
        score = f"{s['mean_on_scored']:.4f}" if s['mean_on_scored'] is not None else '—'
        lines.append(f"| {s['benchmark']} | {s['finished']}/5 | {s['graded']}/5 | {s['policy_assigned_zeros']} | {s['scored']}/5 | {score} |")
    lines += ['', 'EXP-Bench reports reference coverage on a 0–100 scale for design-only submissions.',
              'Other scores are on a 0–1 scale and retain benchmark-specific meaning.',
              'Terminal no-submission outcomes count as false (`reward=0`) under the explicit',
              '`terminal-missing-submission-false-v1` policy. Their `missing_submission` status',
              'is retained. Policy zeros count as scored, not native graded; infrastructure',
              'errors remain unscored. Historical raw attempts are unchanged.',
              'There is no cross-benchmark average.', '',
              '| Benchmark | Task | Status | Score | Score source | Researcher questions |',
              '| --- | --- | --- | ---: | --- | ---: |']
    for r in rows:
        score = f"{r['score']:.4f}" if r['score'] is not None else '—'
        lines.append(f"| {r['benchmark']} | `{r['task']}` | {r['status']} | {score} | {r.get('score_source', 'benchmark_evaluator' if r['score'] is not None else 'unscored')} | {r['questions']} |")
    lines += ['', '## Execution and limitations', '',
        '- Cases were scheduled concurrently: 15 Python cases, five EXP-Bench cases, and five Terminal cases. Batch launches were staggered as prerequisites became ready.',
        '- Each actor had 20 OpenHands iterations and up to six researcher questions. Terminal retains its native wall-time ceiling, with an additional 20-iteration limit and disabled actor network; these are environment adaptations.',
        '- The initial Python batch failed sandbox startup before actor inference because a Debian standard-library directory was absent. Its records remain under `runs/luna-no-persona-five/python/`; the corrected batch is under `python-runtime-fixed/`.',
        '- SAB 87 exhausted its first actor budget because the initial runtime lacked a NetCDF reader. A separate environment supplied the missing dependency, and only that case was rerun under `sab-netcdf-retry/`. Both attempts and their costs are retained.',
        '- Harbor grading first lacked Docker Compose, then its network sidecar failed because the host kernel lacks nftables FIB support. Saved submissions are graded in separate Docker containers with `--network none` using unchanged native images and verifier scripts. Original errors and intermediate attempts are retained; replacement grades are under `native-docker/evaluation.json`.',
        '- Current case selection is a small, manually reviewed sample, not a random or representative benchmark sample. These runs do not measure a persona effect.',
        '- No additional test suite was run after the user requested validation through actual case execution.', '',
        f"Recorded model charges, including retained infrastructure-affected actor attempts: ${data['total_recorded_cost_usd']:.6f}.", '',
        'Per-case run paths and machine-readable scores are in `reports/luna_no_persona_five.json`.',
        'Private transcripts, references, and submissions remain in the ignored `runs/` tree.',
        'Reproduction and configurations: [Luna baseline](../docs/luna_baseline.md).', '']
    (ROOT / 'reports/luna_no_persona_five.md').write_text('\n'.join(lines))
    print(json.dumps({'finished': len(rows), 'summary': summary, 'recorded_cost_usd': data['total_recorded_cost_usd']}, indent=2))


if __name__ == '__main__':
    main()
