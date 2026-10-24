"""Controlled-comparison regressions using synthetic fixtures, never real runs."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from personasciencebench.persona import Persona
from personasciencebench.researcher import Researcher
from personasciencebench.science_personas.phase1 import (
    Cohort, Design, arm_configs, arm_profiles, make_plan, verify_plan, write_plan,
)
from test_core_boundaries import ScriptedBackend, episode_fixture

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def design():
    return Design.model_validate_json((ROOT / 'examples/science_personas/phase1/design.proposed.json').read_text())


def test_twelve_arms_change_one_dimension_relative_to_reference(design):
    before = design.model_dump()
    arms = arm_profiles(design)
    assert len(arms) == 12 and arms['persona_off'] is None
    base = arms['reference']
    for c in design.contrasts:
        changed = arms[c.id]
        differences = [k for k in base.attributes if base.attributes[k] != changed.attributes[k]]
        assert changed.role == base.role
        if c.dimension == 'field':
            assert changed.domain != base.domain and differences == []
        else:
            assert changed.domain == base.domain and differences == [c.dimension]
    assert design.model_dump() == before


@pytest.mark.parametrize('change', ['unknown', 'unchanged', 'duplicate', 'extra', 'reserved', 'invalid_level'])
def test_invalid_arm_designs_rejected(design, change):
    data = design.model_dump()
    if change == 'unknown': data['contrasts'][0]['dimension'] = 'task_budget'
    elif change == 'unchanged': data['contrasts'][0]['value'] = data['reference']['domain']
    elif change == 'duplicate': data['contrasts'].append(deepcopy(data['contrasts'][0]))
    elif change == 'extra': data['contrasts'][0]['actor_steps'] = 99
    elif change == 'reserved': data['contrasts'][0]['id'] = 'reference'
    else: data['contrasts'][-1]['value'] = 'expert'
    with pytest.raises(ValueError): Design.model_validate(data)


def test_off_keeps_exact_simulator_model_config_and_limits(design):
    config = json.loads((ROOT / 'configs/pilot.json').read_text())
    before = deepcopy(config)
    configs = arm_configs(config, design)
    for attached in configs.values():
        assert {k: v for k, v in attached.items() if k != 'persona'} == {k: v for k, v in config.items() if k != 'persona'}
    assert configs['persona_off']['persona'] == {'enabled': False}
    configs['persona_off']['models']['actor']['max_tokens'] = 1
    assert configs['reference']['models'] == config['models'] and config == before


@pytest.mark.parametrize('mode', ['grounded', 'extractive'])
@pytest.mark.parametrize('topic', ['sample_metadata', 'absent_topic'])
def test_off_and_on_share_policy_facts_and_call_sequence(design, mode, topic):
    requests = []
    for persona in [Persona(enabled=False), Persona(science_profile=design.reference)]:
        backend = ScriptedBackend(*([{'answer':'Unknown from supplied context.', 'fact_ids':[]}, {'supported':True}] if mode=='grounded' else [{'answer':'Unknown','fact_ids':[]}]))
        researcher = Researcher(episode_fixture(), backend, persona=persona, mode=mode, max_questions=1)
        researcher.share_progress('I am checking what is specified.')
        researcher.ask('What is known?', topic=topic)
        assert researcher.ask('Another question')['fallback'] == 'question_limit'
        calls = deepcopy(backend.calls)
        if calls:
            system = json.loads(calls[0][0]['content'])
            assert ('identity' in system) == persona.enabled
            system.pop('identity', None)
            calls[0][0]['content'] = system
        requests.append(calls)
    assert requests[0] == requests[1]
    assert len(requests[0]) == (2 if mode == 'grounded' else int(topic == 'sample_metadata'))


@pytest.fixture
def inputs(tmp_path):
    config_path = tmp_path / 'base.json'
    config_path.write_text((ROOT / 'configs/pilot.json').read_text())
    fixed = {}
    for key in ['task','data','environment','execution','scientific_facts','gold','verifier']:
        path = tmp_path / (key + '.txt')
        path.write_text('synthetic ' + key)
        fixed[key] = [str(path)]
    tasks = []
    for index in range(50):
        episode = episode_fixture()
        episode.id = f'synthetic:{index}'
        episode.source_task_id = str(index)
        episode.benchmark = 'terminal_bench_science'
        episode.review_status = 'reviewed'
        path = tmp_path / f'episode-{index}.json'
        path.write_text(episode.model_dump_json())
        tasks.append({'episode':str(path), 'config':str(config_path), 'fixed_inputs':deepcopy(fixed)})
    return Cohort.model_validate({'tasks':tasks})


def test_fifty_tasks_crossed_with_identical_twelve_arms(design, inputs, tmp_path):
    before = inputs.model_dump()
    plan, configs = make_plan(design, inputs, base=tmp_path)
    assert plan['cohort_size'] == 50 and len(plan['episodes']) == len(configs) == 600
    assert plan['status'] == 'offline_plan_not_executed'
    for index in range(50):
        records = [r for r in plan['episodes'] if r['task_index'] == index]
        assert len(records) == 12
        assert len({r['fixed_inputs_sha256'] for r in records}) == 1
        assert len({r['episode'] for r in records}) == 1
    assert make_plan(design, inputs, base=tmp_path) == (plan, configs)
    assert inputs.model_dump() == before


@pytest.mark.parametrize('size', [0, 49, 51])
def test_incomplete_or_oversized_cohort_rejected(inputs, size):
    data = inputs.model_dump()
    data['tasks'] = (data['tasks'] * 2)[:size]
    with pytest.raises(ValueError): Cohort.model_validate(data)


def test_duplicate_source_task_and_unsupported_runner_rejected(design, inputs, tmp_path):
    tasks = inputs.model_copy(deep=True)
    tasks.tasks[1] = tasks.tasks[0].model_copy(deep=True)
    with pytest.raises(ValueError, match='distinct'): make_plan(design, tasks, base=tmp_path)
    path = Path(inputs.tasks[0].episode)
    episode = json.loads(path.read_text())
    episode['benchmark'] = 'expbench'
    path.write_text(json.dumps(episode))
    with pytest.raises(ValueError, match='separate EXP'): make_plan(design, inputs, base=tmp_path)


def save_plan(tmp_path, design, inputs):
    d, c, output = tmp_path/'design.json', tmp_path/'cohort.json', tmp_path/'plan'
    d.write_text(design.model_dump_json())
    c.write_text(inputs.model_dump_json())
    write_plan(d, c, output)
    return output


@pytest.mark.parametrize('component', ['task','data','environment','execution','scientific_facts','gold','verifier','episode','config','generated_config','manifest'])
def test_frozen_input_or_plan_drift_is_detected(design, inputs, tmp_path, component):
    output = save_plan(tmp_path, design, inputs)
    assert verify_plan(output)['episodes_planned'] == 600
    if component in type(inputs.tasks[0].fixed_inputs).model_fields:
        path = Path(getattr(inputs.tasks[0].fixed_inputs, component)[0])
        path.write_text(path.read_text() + '\nchanged')
    elif component == 'generated_config':
        path = output/'configs/task_000/persona_off.json'
        value = json.loads(path.read_text()); value['actor_steps'] += 1
        path.write_text(json.dumps(value))
    elif component == 'manifest':
        path = output/'plan.private.json'; value = json.loads(path.read_text())
        value['episodes'] = value['episodes'][:-1]; path.write_text(json.dumps(value))
    else:
        path = Path(getattr(inputs.tasks[0], component))
        path.write_text(path.read_text() + '\n')
    with pytest.raises(ValueError, match='changed'): verify_plan(output)


def test_output_never_overwrites_inputs_or_existing_plan(design, inputs, tmp_path):
    output = save_plan(tmp_path, design, inputs)
    with pytest.raises(FileExistsError): write_plan(tmp_path/'design.json', tmp_path/'cohort.json', output)
    inputs.tasks[0].fixed_inputs.data = [str(tmp_path)]
    (tmp_path/'cohort.json').write_text(inputs.model_dump_json())
    with pytest.raises(ValueError, match='separate'): write_plan(tmp_path/'design.json', tmp_path/'cohort.json', tmp_path/'inside-input')


def test_descriptive_observations_preserve_native_scoring_and_zero_questions(tmp_path):
    from personasciencebench.science_personas.observations import summarize
    events = tmp_path/'events.jsonl'; events.write_text('')
    native = tmp_path/'evaluation.json'
    original = {'status':'scored', 'metrics':{'native_score':0.12345, 'passed':False}, 'errors':[]}
    native.write_text(json.dumps(original))
    result = summarize(events, native)
    assert result['question_calls'] == result['unique_disclosed_fact_ids'] == 0
    assert result['native_evaluation']['unchanged_result'] == original
    assert json.loads(native.read_text()) == original
    events.write_text('\n'.join(json.dumps(e) for e in [
        {'sequence':0,'type':'researcher_question','payload':{'question':'What is known?'}},
        {'sequence':1,'type':'researcher_reply','payload':{'answer':'Paired samples','fact_ids':['fact1'],'fallback':None}},
        {'sequence':2,'type':'researcher_question','payload':{'question':'Again?'}},
        {'sequence':3,'type':'researcher_reply','payload':{'answer':'Exhausted','fact_ids':[],'fallback':'question_limit'}},
    ]))
    result = summarize(events)
    assert result['question_calls'] == 2 and result['unique_disclosed_fact_ids'] == 1
    assert result['question_limit_events'] == result['fallback_events'] == 1
    assert result['question_sequences'] == [0,2] and result['native_evaluation'] is None


def test_old_collaboration_episode_is_rejected(design, inputs, tmp_path):
    path = Path(inputs.tasks[0].episode)
    value = json.loads(path.read_text())
    value['conversion']['collaboration_version'] = 'ode-disclosure-1.0'
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='Superseded collaboration'):
        make_plan(design, inputs, base=tmp_path)


def test_exported_phase1_preview_profiles_match_design(design):
    from personasciencebench.science_personas.profiles import SciencePersona
    profiles = arm_profiles(design)
    for name in ['reference', 'coding_fluency_low', 'coding_fluency_high']:
        path = ROOT / 'examples/science_personas/phase1' / (name + '.json')
        assert SciencePersona.model_validate_json(path.read_text()) == profiles[name]
