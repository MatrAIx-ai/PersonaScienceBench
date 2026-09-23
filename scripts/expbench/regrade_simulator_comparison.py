"""Regrade both saved simulator conditions with a different judge; no actor reruns."""
import argparse
import getpass
import json
import os
import statistics
from pathlib import Path

from expbench.artifacts import write_json
from expbench.budget import Budget, Ledger
from expbench.design_evaluation import evaluate_design
from expbench.gateway import Gateway, OpenRouterTransport
from expbench.integrity import PROMPT as MONITOR_PROMPT
from expbench.runner import file_digest
from expbench.schema import Config


class SonnetJudgeGateway(Gateway):
    def complete(self, role, messages, **kwargs):
        # Claude rejects the released system + empty-user protocol.
        messages = [dict(message) for message in messages]
        assert [m['role'] for m in messages] == ['system', 'user']
        assert messages[1]['content'] == ''
        messages[1]['content'] = 'Apply the evaluation instructions above.'
        return super().complete(role, messages, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comparison', type=Path, default=Path('reports/expbench/o3mini_simulator_comparison_20260922.json'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    previous = json.loads(args.comparison.read_text())
    config = Config.load(Path('configs/expbench/pilot-o3mini.toml'))
    judge = config.models.researcher.model_copy(update={'max_output_tokens': 4096})
    inputs = []
    for row in previous['results']:
        for condition, field in [('sonnet5_simulator', 'baseline_source'), ('o3mini_simulator', 'source')]:
            source = Path(row[field])
            checkpoint_path = source / 'initial_design.json'
            checkpoint = json.loads(checkpoint_path.read_text())
            old_grade = json.loads((source / 'initial_evaluation/summary.json').read_text())
            prior_calls = [json.loads(line) for line in (source / 'api_calls.jsonl').read_text().splitlines()]
            prior_prompts = [c['payload']['messages'][0]['content'] for c in prior_calls
                if c['phase'] == 'request' and c['role'] == 'judge']
            assert (source / 'initial_evaluation/coverage_prompt.txt').read_text() in prior_prompts
            assert MONITOR_PROMPT.read_text().format(logs=checkpoint['trace']) in prior_prompts
            inputs.append({'task_id': row['task_id'], 'name': row['name'], 'condition': condition,
                'source': str(source), 'checkpoint_sha256': file_digest(checkpoint_path),
                'checkpoint': checkpoint, 'old_grade': old_grade})
    key = os.environ.get('OPENROUTER_API_KEY') or getpass.getpass('OpenRouter credential: ')
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    transport = OpenRouterTransport(key, config.limits.request_timeout_seconds)
    budget = Budget(None)
    results = []
    try:
        catalog = transport.preflight({'judge': judge}, enforce_price_caps=False)
        write_json(args.output / 'model_catalog.json', catalog)
        write_json(args.output / 'manifest.json', {'judge': judge.model_dump(), 'repeats': 3,
            'evaluation': 'reference-coverage-only', 'integrity_model': judge.model,
            'source_comparison': str(args.comparison), 'script_sha256': file_digest(Path(__file__)),
            'inputs': [{k:v for k,v in i.items() if k != 'checkpoint'} for i in inputs],
            'note': 'Identical saved plans, traces, system prompts and JSON-object mode. Claude requires a nonempty user message: Apply the evaluation instructions above. Judge and integrity model changed. No actor/simulator calls.'})
        for item in inputs:
            out = args.output / item['condition'] / item['task_id'].replace('/', '__')
            out.mkdir(parents=True)
            ledger = Ledger(budget, Budget(None))
            gateway = SonnetJudgeGateway(transport, {'judge': judge}, ledger, out / 'api_calls.jsonl')
            result = {k:v for k,v in item.items() if k not in ('checkpoint', 'old_grade')}
            result.update(status='error', o3mini=item['old_grade'])
            try:
                grade = evaluate_design(gateway, item['task_id'], item['checkpoint'], out / 'evaluation', repeats=3)
                for field in ('reference_sha256', 'coverage_template_sha256', 'monitor_template_sha256'):
                    assert grade[field] == item['old_grade'][field], field
                assert (out / 'evaluation/coverage_prompt.txt').read_bytes() == (Path(item['source']) / 'initial_evaluation/coverage_prompt.txt').read_bytes()
                result.update(status='completed', sonnet5=grade)
            except Exception as exc:
                result['error_type'] = type(exc).__name__
                raise
            finally:
                usage = ledger.summary()
                write_json(out / 'usage.json', usage)
                result['api_cost_usd'] = sum(r.get('usage', {}).get('cost', 0) for r in usage['records'])
                result['unknown_billing_calls'] = sum('usage' not in r for r in usage['records'])
                write_json(out / 'result.json', result)
                results.append(result)
                write_json(args.output / 'summary.json', {'scheduled': len(inputs),
                    'completed': sum(r['status'] == 'completed' for r in results), 'results': results,
                    'api_cost_usd': sum(r['api_cost_usd'] for r in results)})
            print(item['name'], item['condition'], 'coverage:', grade['coverage_mean'],
                  'monitor:', grade['monitor_status'], flush=True)
    finally:
        transport.close()
    lines = ['# Sonnet 5 judge comparison', '',
        'Ten saved plans, with no actor or simulator reruns. Scores are reference coverage means over three judgments. Both coverage and integrity now use Sonnet 5, with the original system prompts and JSON-object mode. Claude rejected the original empty user message (HTTP 400), so its user message is "Apply the evaluation instructions above." This compatibility change is a protocol difference from the historical o3-mini grades. No additional quality rubric or validation suite was run.', '',
        '| Task | Simulator | o3-mini judge | Sonnet 5 judge | Sonnet integrity |',
        '| --- | --- | ---: | ---: | --- |']
    for r in results:
        lines.append(f"| {r['name']} | {r['condition']} | {r['o3mini']['coverage_mean']:.1f} | {r['sonnet5']['coverage_mean']:.1f} | {r['sonnet5']['monitor_status']} |")
    lines += ['', '## Means', '']
    for condition in ('sonnet5_simulator', 'o3mini_simulator'):
        group = [r for r in results if r['condition'] == condition]
        before = statistics.mean(r['o3mini']['coverage_mean'] for r in group)
        after = statistics.mean(r['sonnet5']['coverage_mean'] for r in group)
        gated = statistics.mean(r['sonnet5']['gated_coverage_mean'] for r in group)
        lines.append(f'- {condition}: o3-mini judge {before:.2f}; Sonnet 5 judge {after:.2f}; Sonnet integrity-gated coverage {gated:.2f}.')
    lines += ['', f"API-reported cost for the completed regrading: ${sum(r['api_cost_usd'] for r in results):.6f}. Two earlier HTTP 400 requests returned no usage accounting; their billing is unconfirmed (see runs/sonnet5-judge-comparison-20260922).", '',
        'These paired grades isolate judge differences on the saved plans. They do not establish which judge is more accurate without human adjudication. The simulator conditions still have different actor trajectories; four of five episodes in each condition did not query a simulator. Sonnet uses a 4,096-output-token allowance without configured reasoning; the historical o3-mini judge used medium reasoning within the same allowance.', '',
        f'Artifacts: [{args.output.name}](../{args.output.as_posix()}/summary.json).']
    Path('reports/expbench/sonnet5_judge_comparison_20260922.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
