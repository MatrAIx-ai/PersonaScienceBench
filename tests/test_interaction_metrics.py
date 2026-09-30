"""Outcome/behavior separation and task-matched post-hoc analysis contracts."""
import json
from pathlib import Path

import pytest

from personasciencebench.interaction_metrics import (
    analysis_score, analyze_case, interaction_counts, paired_summary, read_events,
    visible_messages,
)

ROOT = Path(__file__).resolve().parents[1]
EPISODE = 'discoverybench:test/example/metadata_0.json/0/0'


def event(kind, payload):
    return {'type': kind, 'payload': payload}


def numbered(events):
    return [dict(e, sequence=i, episode_id=EPISODE) for i, e in enumerate(events)]


def decision(phase, action='continue', text='请核查假设。', approved=False):
    return event('researcher_decision', dict(phase=phase, action=action, message=text,
                 approve_approach=approved, evidence='PRIVATE REASONING', interaction='next_task'))


def handoff(stage, text='Shared answer'):
    return event('agent_handoff', dict(stage=stage, answer=text, evidence='Shared evidence',
                 assumptions=['Assumption'], uncertainties=['Uncertainty'],
                 payload={'hypothesis': 'PAYLOAD EXCLUDED'}, artifacts={'code': '/private/path'}))


def transcript():
    return numbered([
        decision('initial_inspection', text='Inspect first'), handoff('plan'),
        decision('approach_review'), handoff('plan'), decision('approach_review', approved=True),
        event('researcher_question', {'question': 'Which unit?'}),
        event('researcher_reply', {'answer': 'A plot.', 'fact_ids': ['hidden']}),
        event('researcher_question', {'question': 'Which unit?'}),
        event('researcher_reply', {'answer': 'A plot.', 'fact_ids': ['hidden']}),
        event('actor_command', {'command': 'bad'}),
        event('actor_command_result', {'exit_code': 1, 'timeout': False, 'stdout': 'TOOL EXCLUDED'}),
        event('actor_command', {'command': 'good'}),
        event('actor_command_result', {'exit_code': 0, 'timeout': False, 'stdout': 'TOOL EXCLUDED'}),
        handoff('result'), decision('result_review'), handoff('result'),
        decision('result_review', action='stop'), event('actor_finished', {}),
    ])


def test_counts_distinguish_required_reviews_revision_requests_and_optional_questions():
    counts = interaction_counts(transcript())
    assert counts['actor_handoffs'] == 4
    assert counts['extra_approach_reviews'] == counts['extra_result_reviews'] == 1
    assert counts['result_revision_requests'] == 1
    assert counts['optional_question_calls'] == 2
    assert counts['optional_question_exact_repeats'] == 1
    assert counts['optional_question_exact_repeat_rate'] == .5
    assert counts['command_attempts'] == 2 and counts['command_failures'] == 1
    assert counts['researcher_reply_characters'] == 4 * len('请核查假设。') + 2 * len('A plot.')
    assert counts['researcher_reply_count'] == 6
    assert counts['initial_request_characters'] == len('Inspect first')
    assert counts['ask_f1'] is None and counts['question_precision'] is None
    assert counts['blocker_recall'] is None


def test_visible_packet_excludes_private_explanations_tools_and_submission_payloads():
    text = json.dumps(visible_messages(transcript()), ensure_ascii=False)
    for marker in ['PRIVATE REASONING', 'TOOL EXCLUDED', 'PAYLOAD EXCLUDED', '/private/path', 'hidden']:
        assert marker not in text
    assert '请核查假设。' in text and 'Shared evidence' in text
    assert 'event_sequence' in text


def test_zero_questions_is_not_perfect_precision_or_zero_measured_usefulness():
    events = numbered([decision('initial_inspection'), handoff('plan'), decision('approach_review', approved=True)])
    counts = interaction_counts(events)
    assert counts['optional_question_calls'] == 0
    assert counts['optional_question_exact_repeat_rate'] is None
    assert counts['question_precision'] is None and counts['ask_f1'] is None
    events.append(dict(event('collaboration_budget_exhausted', {'reason': 'actor_call_limit'}), sequence=3, episode_id=EPISODE))
    counts = interaction_counts(events)
    assert counts['actor_budget_exhausted'] and not counts['dialogue_budget_exhausted']


@pytest.mark.parametrize('mutation', ['empty', 'duplicate', 'gap', 'wrong_episode', 'malformed'])
def test_bad_event_streams_are_not_zero_interaction(tmp_path, mutation):
    events = transcript()
    if mutation == 'empty': events = []
    if mutation == 'duplicate': events[1]['sequence'] = 0
    if mutation == 'gap': events.pop(2)
    if mutation == 'wrong_episode': events[0]['episode_id'] = 'different'
    path = tmp_path / 'events.jsonl'
    path.write_text('not JSON' if mutation == 'malformed' else '\n'.join(json.dumps(e) for e in events))
    with pytest.raises(ValueError): read_events(path, EPISODE)


@pytest.mark.parametrize('value', [True, -1, 1.1, float('nan'), float('inf'), '0.5'])
def test_invalid_native_grades_fail_closed(value):
    with pytest.raises(ValueError):
        analysis_score({'status': 'scored', 'evaluation': {'metrics': {'final_score': value}}})


def test_absent_traces_and_native_grades_remain_absent(tmp_path):
    result = {'episode_id': EPISODE, 'source_task_id': 'test/example/metadata_0.json/0/0',
              'study_id': 'discoverybench:example', 'status': 'missing_submission'}
    (tmp_path / 'result.json').write_text(json.dumps(result))
    row, packet = analyze_case(tmp_path, {'models': {}, 'persona': {'enabled': False}}, condition='off', batch='test')
    assert row['analysis_score'] == 0 and row['native_metrics'] == {}
    assert row['interaction_metrics'] is None and row['interaction_status'] == 'unavailable'
    assert packet is None
    result['status'] = 'infrastructure_error'
    assert analysis_score(result) is None


def row(condition, score, **kwargs):
    return dict(batch='batch', task_id='task', condition=condition, analysis_score=score,
                status='scored', evaluator_version='native-v1', resolved_models=['model-v1'],
                public_input_sha256='same-public', settings_sha256='same-settings', **kwargs)


def test_repeat_means_and_sd_use_shared_baseline_not_best_of_three():
    rows = [row('off', s) for s in [0, .5, 1]] + [row('persona', s) for s in [.1, .2, .3]]
    rows.append({**row('persona', None), 'status': 'infrastructure_error'})
    summary = paired_summary(rows)[0]
    assert summary['condition_n'] == summary['baseline_n'] == 3
    assert summary['condition_mean'] == pytest.approx(.2)
    assert summary['baseline_mean'] == .5 and summary['baseline_sd'] == .5
    assert summary['difference'] == pytest.approx(-.3)
    assert summary['condition_sd'] == pytest.approx(.1)


def test_unmatched_tasks_policies_and_unknown_public_inputs_do_not_pair():
    base = row('off', .5)
    for key in ['task_id', 'public_input_sha256', 'settings_sha256', 'batch']:
        treatment = {**row('persona', .9), key: 'different'}
        assert paired_summary([base, treatment]) == []
    assert paired_summary([{**base, 'public_input_sha256': None}, row('persona', .9)]) == []
    assert paired_summary([row('persona', .9)]) == []
    for key in ['evaluator_version', 'resolved_models']:
        treatment = {**row('persona', .9), key: ['different'] if key == 'resolved_models' else 'different'}
        with pytest.raises(ValueError): paired_summary([base, treatment])




def test_partial_traces_keep_observed_counts_and_are_flagged(tmp_path):
    result = {'episode_id': EPISODE, 'source_task_id': 'test/example/metadata_0.json/0/0',
              'study_id': 'discoverybench:example', 'status': 'infrastructure_error', 'evaluation': None}
    (tmp_path / 'result.json').write_text(json.dumps(result))
    controller = tmp_path / 'controller'
    controller.mkdir()
    events = transcript()[:-1]
    (controller / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events))
    observed, packet = analyze_case(tmp_path, {}, condition='off', batch='partial')
    assert observed['interaction_status'] == 'partial_trace'
    assert observed['interaction_metrics']['actor_handoffs'] == 4
    assert observed['interaction_metrics']['trace_finished'] is False
    assert observed['analysis_score'] is None and packet is not None
    (controller / 'events.jsonl').write_text('[]\n')
    invalid, packet = analyze_case(tmp_path, {}, condition='off', batch='invalid')
    assert invalid['interaction_status'] == 'invalid_trace'
    assert invalid['interaction_metrics'] is None and packet is None


def test_reporter_tracks_repeats_unrun_tasks_and_rejects_duplicate_episode_ids(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('ecology_analysis', ROOT / 'scripts/analyze_discoverybench_interactions.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    batch = tmp_path / 'batch'
    task = 'test/example/metadata_0.json/0/0'
    manifest = {'tasks': [dict(task_id=t, subfield='ecology', analysis_family='association')
                          for t in [task, 'unrun-task']]}
    config = {'models': {'actor': {'model': 'test'}}, 'persona': {'enabled': False}}
    for repeat in [1, 2]:
        condition = batch / 'off' / f'repeat_{repeat:02d}'
        case = condition / 'case'
        controller = case / 'controller'
        controller.mkdir(parents=True)
        result = {'episode_id': EPISODE, 'source_task_id': task, 'study_id': 'example',
                  'status': 'missing_submission'}
        (case / 'result.json').write_text(json.dumps(result))
        (controller / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in transcript()))
        (condition / 'config.json').write_text(json.dumps(config))
        (condition / 'summary.json').write_text(json.dumps({'cases': [{'episode_id': EPISODE}]}))
    report, packets = module.analyze([batch], manifest)
    assert len(report['episodes']) == len(packets) == 2
    assert report['task_tracking'][0]['observed_attempts'] == 2
    assert report['task_tracking'][1]['local_result_tracking'] == 'not_run_in_supplied_batches'
    assert report['task_tracking'][1]['observed_attempts'] == 0
    assert 'analysis_score' not in json.dumps(packets) and 'PRIVATE REASONING' not in json.dumps(packets)
    assert len({r['case_locator'] for r in report['episodes']}) == 2
    module.write_report(tmp_path / 'report', report)
    assert (tmp_path / 'report/episodes.csv').is_file()
    # Two different case directories must not silently collapse under one episode ID.
    duplicate = condition / 'another-case'
    duplicate.mkdir()
    (duplicate / 'result.json').write_text(json.dumps(result))
    with pytest.raises(ValueError, match='Duplicate episode IDs'):
        module.analyze([batch], manifest)
