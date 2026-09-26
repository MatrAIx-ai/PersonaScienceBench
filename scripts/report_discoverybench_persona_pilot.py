"""Export a reviewed-metrics-only DiscoveryBench report; never copy evaluator references."""
import argparse
import json
from pathlib import Path
import statistics

from personasciencebench.packaging import write_json


def publish(run: Path, output: Path):
    plan = json.loads((run / 'plan.private.json').read_text())
    integrity = json.loads((run / 'integrity.json').read_text())
    if integrity != {'frozen_inputs_unchanged': True, 'arm_configs_unchanged': True}:
        raise ValueError('Experiment integrity did not pass')
    comparison = json.loads((run / 'comparison.json').read_text())
    if len(comparison['records']) != plan['scheduled_episodes']:
        raise ValueError('The experiment is incomplete')
    rows = []
    for record in comparison['records']:
        case = Path(record['case_directory']) if record.get('case_directory') else None
        result = json.loads((case / 'result.json').read_text()) if case and (case / 'result.json').is_file() else {}
        actor = result.get('actor', {})
        rows.append({key: record.get(key) for key in ('arm', 'repeat', 'episode_id', 'study_id', 'status',
            'score', 'researcher_requests', 'disclosed_facts', 'prompt_tokens', 'completion_tokens', 'resolved_models')} |
            {'actor_calls': actor.get('actor_calls'), 'execution_calls': actor.get('execution_calls'),
             'execution_successes': actor.get('execution_successes'),
             'scientific_execution_verified': actor.get('scientific_execution_verified'),
             'interaction': {k: v for k, v in record.get('observations', {}).items() if k in {'question_calls', 'review_handoffs', 'plan_handoffs', 'result_handoffs', 'researcher_decisions', 'unique_disclosed_fact_ids', 'review_message_characters', 'fallback_events'}}})
    rows.sort(key=lambda r: (r['study_id'], r['repeat'], r['arm']))
    def mean(values):
        values = [v for v in values if v is not None]
        return statistics.mean(values) if values else None
    studies = sorted({r['study_id'] for r in rows})
    by_study = [{'study_id': study, 'arm': arm, 'scores': [r['score'] for r in rows if r['study_id'] == study and r['arm'] == arm],
                 'mean_score': mean(r['score'] for r in rows if r['study_id'] == study and r['arm'] == arm)}
                for study in studies for arm in plan['arms']]
    public = {'kind': 'descriptive_matched_discoverybench_pilot', 'source_revision': plan['source_revision'],
              'configured_models': json.loads((run / 'configs/off.json').read_text())['models'],
              'arms': comparison['arms'], 'distinct_studies': len(studies), 'repeats': plan['repeats'],
              'scheduled_episodes': plan['scheduled_episodes'], 'scored_episodes': sum(r['score'] is not None for r in rows),
              'by_study': by_study, 'trials': rows, 'integrity': integrity,
              'non_persona_config_sha256': plan['non_persona_config_sha256'],
              'interpretation': comparison['interpretation'], 'cost_usd': None,
              'record_locator': run.name, 'raw_records': 'Ignored runs/ directory; not redistributed.'}
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'results.json', public)
    def fmt(n):
        return 'unscored' if n is None else f'{n:.4f}'
    lines = ['# DiscoveryBench: Azure GPT-5.6 Sol persona pilot', '',
             f"Completed {len(rows)} executions across {len(studies)} distinct studies, four conditions, and {plan['repeats']} repetitions. "
             f"{public['scored_episodes']} received native scores. Both frozen-input and arm-configuration integrity checks passed.", '',
             'These are exploratory paired observations, not evidence of a general persona benefit. All three model roles used the recorded Azure deployment with reasoning effort `none`.', '',
             '| Researcher condition | Mean native score | Paired change vs off | Scored / attempted | Wins / ties / losses |',
             '| --- | ---: | ---: | ---: | --- |']
    for arm in comparison['arms']:
        lines.append(f"| {arm['arm']} | {fmt(arm['mean_native_score'])} | {fmt(arm['paired_mean_delta_vs_off'])} | {arm['scored']} / {arm['attempted']} | {' / '.join(map(str,arm['wins_ties_losses']))} |")
    lines += ['', '## By scientific study', '', '| Study | Condition | Repetition scores | Mean |', '| --- | --- | --- | ---: |']
    for row in by_study:
        lines.append(f"| {row['study_id'].removeprefix('discoverybench:')} | {row['arm']} | {', '.join(fmt(x) for x in row['scores'])} | {fmt(row['mean_score'])} |")
    lines += ['', '## Design and limits', '',
              '- Persona off retained the same simulator, facts, protocol, models, and budgets.',
              '- Enabled profiles held 55 attributes, role, and domain fixed. Only statistical inference differed: medium, low, or high.',
              '- Each persona score was paired with the same study and repetition of the off control. The three contrasts reuse that control and are correlated.',
              '- Missing results remain unscored. Repetitions are not additional independent studies. No hypothesis tests or population-level confidence intervals are claimed.',
              '- Native scores measure LLM-judged reference agreement; successful tool execution is separate evidence and does not independently verify the scientific analysis.',
              '- GPT-5.6 Sol resolved model IDs, interaction counts, execution receipts, and usage tokens are in results.json. Dollar cost requires Azure billing data.',
              '', '## Reproduction', '',
              'Follow the [Azure pilot guide](../../docs/discoverybench_azure_pilot.md). The shared implementation and pinned sources are unchanged across the arms.',
              f"Raw records are stored locally under `runs/{run.name}/`; private references, credentials, and raw traces are excluded from this report.",
              '', 'The private plan records source, configuration, and runtime hashes, plus the shuffled execution schedule.', '']
    (output / 'README.md').write_text('\n'.join(lines))
    return {'episodes': len(rows), 'scored': public['scored_episodes'], 'output': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(publish(args.run.resolve(), args.output)))


if __name__ == '__main__':
    main()
