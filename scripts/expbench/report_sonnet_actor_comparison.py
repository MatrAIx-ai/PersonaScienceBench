"""Summarize saved actor comparison attempts, including unscored failures."""
import json
import re
import statistics
from pathlib import Path

root = Path('runs/expbench/sonnet5-actor-comparison-20260922')
manifest = json.loads((root / 'manifest.json').read_text())
prior = json.loads(Path('runs/expbench/sonnet5-judge-comparison-compatible-20260922/summary.json').read_text())
names = {r['task_id']: r['name'] for r in prior['results']}
rows = []
first_requests = {}
for condition in manifest['simulators']:
    for task in manifest['task_ids']:
        slug = task.replace('/', '__')
        source = root / 'episodes' / condition / slug / slug
        result_path = source / 'result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else {'status': 'process_failed'}
        usage_path = source / 'usage.json'
        records = json.loads(usage_path.read_text())['records'] if usage_path.exists() else []
        grade = result.get('initial')
        calls_path = source / 'api_calls.jsonl'
        if calls_path.exists():
            calls = [json.loads(line) for line in calls_path.read_text().splitlines()]
            request = next(c['payload'] for c in calls if c['phase'] == 'request' and c['role'] == 'actor')
            for message in request['messages']:
                if message['role'] == 'system':
                    message['content'] = re.sub(r'<CURRENT_DATETIME>.*?</CURRENT_DATETIME>', '<CURRENT_DATETIME/>', message['content'], flags=re.S)
            first_requests[(condition, task)] = request
        rows.append({'task_id': task, 'name': names[task], 'simulator': condition,
            'actor': 'anthropic/claude-sonnet-5', 'judge': 'anthropic/claude-sonnet-5',
            'status': result['status'], 'error': result.get('error'),
            'coverage': grade['coverage_mean'] if grade else None,
            'coverage_std': grade['coverage_std'] if grade else None,
            'gated_coverage': grade['gated_coverage_mean'] if grade else None,
            'monitor_status': grade['monitor_status'] if grade else None,
            'actor_calls': result.get('actor_calls'), 'questions': result.get('researcher_questions'),
            'api_cost_usd': sum(r.get('usage', {}).get('cost', 0) for r in records),
            'unknown_billing_calls': sum('usage' not in r for r in records), 'source': str(source)})

aggregates = []
for condition in manifest['simulators']:
    group = [r for r in rows if r['simulator'] == condition]
    scored = [r for r in group if r['coverage'] is not None]
    baseline = [r for r in prior['results'] if r['condition'] == condition + '_simulator']
    aggregates.append({'simulator': condition, 'actor': 'sonnet5', 'judge': 'sonnet5',
        'scheduled': len(group), 'completed': sum(r['status'] == 'completed' for r in group),
        'scored': len(scored), 'coverage_mean_on_scored': statistics.mean(r['coverage'] for r in scored) if scored else None,
        'gated_mean_on_scored': statistics.mean(r['gated_coverage'] for r in scored) if scored else None,
        'prior_o3mini_actor_coverage': statistics.mean(r['sonnet5']['coverage_mean'] for r in baseline),
        'questions': sum(r['questions'] or 0 for r in group),
        'episodes_querying_simulator': sum(bool(r['questions']) for r in group),
        'integrity_passes': sum(r['monitor_status'] == 'passed' for r in group),
        'integrity_parse_errors': sum(r['monitor_status'] == 'parse_error' for r in group)})
output = {'conditions': aggregates, 'results': rows,
    'same_initial_actor_requests_except_timestamp': {task: first_requests.get(('sonnet5', task)) == first_requests.get(('o3mini', task)) for task in manifest['task_ids']},
    'api_cost_usd': sum(r['api_cost_usd'] for r in rows),
    'unknown_billing_calls': sum(r['unknown_billing_calls'] for r in rows),
    'timing': json.loads((root / 'timing.json').read_text())}
report = Path('reports/expbench/sonnet5_actor_comparison_20260922')
report.with_suffix('.json').write_text(json.dumps(output, indent=2) + '\n')
def fmt(x): return f'{x:.1f}' if x is not None else 'Unscored'
lines = ['# Sonnet 5 actor comparison', '',
    'Ten fresh design-only episodes: five tasks per simulator, Sonnet 5 actor and judge, at most five independent processes in parallel. OpenHands, scoped researcher facts, repository masking and CPU sandbox are retained. No GPU training or full experiment execution was requested. No validation suite was run.', '',
    '| Simulator | Actor | Judge | Mean reference coverage /100 | Scored |',
    '| --- | --- | --- | ---: | ---: |']
for a in aggregates:
    lines.append(f"| {a['simulator']} | Sonnet 5 | Sonnet 5 | {fmt(a['coverage_mean_on_scored'])} | {a['scored']}/5 |")
lines += ['', '## Per-task reference coverage', '',
    '| Task | Sonnet 5 simulator | o3-mini simulator |', '| --- | ---: | ---: |']
for task in manifest['task_ids']:
    group = {r['simulator']: r for r in rows if r['task_id'] == task}
    lines.append(f"| {names[task]} | {fmt(group['sonnet5']['coverage'])} | {fmt(group['o3mini']['coverage'])} |")
lines += ['', 'Coverage is the mean of three judgments of each submitted plan. Missing evaluations remain unscored; means use the explicit scored denominator. No added design-quality rubric is used.', '',
    '## Interaction and integrity', '',
    '| Simulator | Total questions | Episodes consulting simulator | Integrity passed | Integrity parse errors | Gated coverage |',
    '| --- | ---: | ---: | ---: | ---: | ---: |']
for a in aggregates:
    lines.append(f"| {a['simulator']} | {a['questions']} | {a['episodes_querying_simulator']}/5 | {a['integrity_passes']}/5 | {a['integrity_parse_errors']} | {fmt(a['gated_mean_on_scored'])} |")
lines += ['', '## Prior actor comparison', '',
    '| Simulator | Prior o3-mini actor | New Sonnet 5 actor |', '| --- | ---: | ---: |']
for a in aggregates:
    lines.append(f"| {a['simulator']} | {a['prior_o3mini_actor_coverage']:.1f} | {fmt(a['coverage_mean_on_scored'])} |")
lines += ['', 'Both columns use Sonnet 5 judging with the same compatibility message. These are separate actor trajectories, one episode per task and condition, not repeated-run estimates or a causal simulator ranking. The simulator publishes approved facts verbatim or an unknown response; it does not provide free-form research advice.', '',
    '## Settings and artifacts', '',
    'Actor limit: 20 steps, six researcher questions, 12,288 output tokens. Sonnet 5 simulator: 1,024 output tokens; o3-mini simulator: 4,096 tokens including medium reasoning. Sonnet 5 judge: 4,096 output tokens. No dollar cap. The original coverage and monitor system prompts are retained, with the nonempty user message "Apply the evaluation instructions above." required by Claude. Strict JSON parsing and original parse-failure gating are unchanged.', '',
    f"API-reported cost: ${output['api_cost_usd']:.6f}; calls with unknown billing: {output['unknown_billing_calls']}. Episode wall time: {output['timing']['episode_wall_seconds'] / 60:.1f} minutes, excluding initial cache preparation and final artifact persistence.", '',
    f'[Run manifest](../{root}/manifest.json), [process results](../{root}/process_status.json), [workspace archive](../{root}/workspaces.tar.gz).', '']
lines += ['Initial actor API requests match between simulator conditions after normalizing the SDK timestamp: ' + str(output['same_initial_actor_requests_except_timestamp']) + '.', '',
    'The JaxMARL episodes differ substantially in researcher usage. Consult the per-episode question counts in the JSON report before attributing the aggregate score gap to simulator capability. Simulator identity is not disclosed to the actor; divergent initial choices precede any researcher response.', '']
for r in rows:
    p = '../' + r['source']
    lines.append(f"- {r['name']} / {r['simulator']}: status `{r['status']}`; [result]({p}/result.json), [plan]({p}/initial_design.json), [conversation]({p}/researcher_history.json), [API trace]({p}/api_calls.jsonl).")
report.with_suffix('.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({k:v for k,v in output.items() if k != 'results'}, indent=2))
