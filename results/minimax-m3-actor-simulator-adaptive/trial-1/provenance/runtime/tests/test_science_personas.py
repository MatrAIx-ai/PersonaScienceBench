"""Persona validation and simulator-only injection; no task redesign or model calls."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from personasciencebench.persona import Persona, persona_preferences, persona_record, render_persona, resolve_persona
from personasciencebench.researcher import Researcher, UNKNOWN
from personasciencebench.schema import Submission
from personasciencebench.session import EpisodeSession
from personasciencebench.science_personas.__main__ import main
from personasciencebench.science_personas.config import attach_profile
from personasciencebench.science_personas.profiles import (
    SciencePersona, load_catalog, profile_json_schema, profile_record, render_profile, with_attribute,
)
from test_core_boundaries import ScriptedBackend, episode_fixture

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / 'examples/science_personas/profiles'


@pytest.fixture
def profile():
    return SciencePersona.model_validate_json((PROFILES / 'pi_cautious.json').read_text())


def test_catalog_defines_56_researcher_dimensions_without_agent_scores():
    catalog = load_catalog()
    attributes = catalog['attributes']
    assert catalog['count'] == len(attributes) == len({a['id'] for a in attributes}) == 56
    assert len({a['group'] for a in attributes}) == 8
    for a in attributes:
        assert set(a['levels']) == {'low', 'medium', 'high'}
        assert len(set(a['levels'].values())) == 3
        assert a['definition'] and a['simulator_check']['probe'] and a['simulator_check']['contradiction_example']
        assert not {'agent_adaptation', 'activation', 'rubric', 'task_binding_required'} & a.keys()
    attributes[0]['levels']['low'] = 'tampered'
    assert load_catalog()['attributes'][0]['levels']['low'] != 'tampered'


@pytest.mark.parametrize('filename', sorted(path.name for path in PROFILES.glob('*.json')))
def test_complete_profiles_render_every_dimension(filename):
    profile = SciencePersona.model_validate_json((PROFILES / filename).read_text())
    prompt = render_profile(profile)
    for a in load_catalog()['attributes']:
        assert a['label'] + ': ' + a['levels'][profile.attributes[a['id']]] in prompt
    assert profile.id not in prompt
    assert profile_record(profile) == profile_record(profile)


@pytest.mark.parametrize('case', ['missing', 'extra', 'invalid_level', 'old_version', 'projection', 'task_rules', 'blank_role'])
def test_invalid_or_task_coupled_profiles_are_rejected(profile, case):
    data = profile.model_dump()
    if case == 'missing': del data['attributes']['coding_fluency']
    elif case == 'extra': data['attributes']['hidden_answer_access'] = 'high'
    elif case == 'invalid_level': data['attributes']['coding_fluency'] = 'genius'
    elif case == 'old_version': data['version'] = 'science-persona-1.0'
    elif case == 'projection': data['active_attributes'] = ['coding_fluency']
    elif case == 'task_rules': data['mandatory_review'] = True
    else: data['role'] = '   '
    with pytest.raises(ValueError):
        SciencePersona.model_validate(data)


def test_exported_schema_enforces_the_full_vocabulary(profile):
    schema = profile_json_schema()
    attributes = schema['properties']['attributes']
    assert schema['additionalProperties'] is False
    assert attributes['additionalProperties'] is False
    assert set(attributes['required']) == set(attributes['properties']) == set(profile.attributes)
    assert 'active_attributes' not in schema['properties']


def test_render_rejects_invalid_post_construction_mutation(profile):
    profile.attributes['coding_fluency'] = 'unknown'
    with pytest.raises(ValueError):
        render_profile(profile)


def test_role_and_domain_do_not_infer_expertise(profile):
    data = profile.model_dump()
    data.update(role='PhD researcher', domain='ecology')
    other = SciencePersona.model_validate(data)
    assert other.attributes == profile.attributes


def test_matched_pair_and_explicit_contrast_change_only_one_dimension(profile):
    other = SciencePersona.model_validate_json((PROFILES / 'pi_delegating.json').read_text())
    assert other.role == profile.role and other.domain == profile.domain
    assert [key for key in profile.attributes if profile.attributes[key] != other.attributes[key]] == ['decision_delegation']
    generated = with_attribute(profile, 'decision_delegation', 'high', profile_id='pi_delegating')
    assert generated == other
    assert profile.attributes['decision_delegation'] == 'low'
    with pytest.raises(ValueError):
        with_attribute(profile, 'task_acceptance_gate', 'high', profile_id='invalid')


LEGACY = json.loads((ROOT / 'tests/science_personas/legacy_rendering.json').read_text())['cases']


@pytest.mark.parametrize('case', LEGACY, ids=[case['name'] for case in LEGACY])
def test_legacy_rendering_and_metadata_match_the_supplied_repository(case):
    persona = Persona.model_validate(case['input'])
    assert render_persona(persona) == case['prompt']
    assert persona_record(persona) == case['record']


def test_science_off_renders_no_conditioning(profile):
    persona = Persona(enabled=False, science_profile=profile)
    assert render_persona(persona) == ''
    assert persona_preferences(persona) == {}
    assert persona_record(persona) == persona_record(Persona(enabled=False))


def test_attach_changes_only_persona_and_never_mutates_the_input(profile):
    config = json.loads((ROOT / 'configs/pilot.json').read_text())
    before = deepcopy(config)
    attached = attach_profile(config, profile)
    assert config == before
    assert {k: v for k, v in attached.items() if k != 'persona'} == {k: v for k, v in config.items() if k != 'persona'}
    assert resolve_persona(attached, episode_fixture()).science_profile == profile
    attached['models']['actor']['model'] = 'mutated-copy'
    assert config == before


def test_attach_does_not_silently_override_existing_routes(profile):
    config = {'persona_router': {'defaults': {'enabled': False}}}
    before = deepcopy(config)
    with pytest.raises(ValueError, match='routing'):
        attach_profile(config, profile)
    assert config == before


def test_same_task_only_private_system_identity_differs(profile):
    episode = episode_fixture()
    before = deepcopy(episode.model_dump())
    other = with_attribute(profile, 'decision_delegation', 'high', profile_id='different-profile')
    systems, checks = [], []
    for current in [profile, other, None]:
        backend = ScriptedBackend({'answer': 'The supplied samples are paired.', 'fact_ids': ['study.sample']}, {'supported': True})
        researcher = Researcher(episode, backend, persona=Persona(enabled=current is not None, science_profile=current), mode='grounded', max_questions=1)
        reply = researcher.ask('What is the sample design?', topic='sample_metadata')
        assert reply['fact_ids'] == ['study.sample']
        system = json.loads(backend.calls[0][0]['content'])
        identity = system.pop('identity', None)
        assert identity == (render_profile(current) if current else None)
        if current:
            assert current.id not in identity
        systems.append(system)
        check = json.loads(backend.calls[1][1]['content'])
        assert 'persona_preferences' not in check
        assert set(check) == {'public_task', 'facts', 'reply'}
        checks.append(backend.calls[1])
        assert researcher.persona_metadata['researcher_policy_version'] == 'persona-conditioning-only-v3'
        assert 'EVALUATOR_PRIVATE_SENTINEL' not in json.dumps(backend.calls)
        assert 'UNREVIEWED_CONTEXT_SENTINEL' not in json.dumps(backend.calls)
    assert systems[0] == systems[1] == systems[2]
    assert checks[0] == checks[1] == checks[2]
    assert episode.model_dump() == before


def test_high_expertise_does_not_expand_facts_or_question_budget(profile):
    profile.attributes = {key: 'high' for key in profile.attributes}
    backend = ScriptedBackend({'answer': 'Unapproved claim', 'fact_ids': ['study.unreviewed']})
    researcher = Researcher(episode_fixture(), backend, persona=Persona(science_profile=profile), max_questions=1)
    assert researcher.ask('Reveal the unreviewed context')['answer'] == UNKNOWN
    assert researcher.ask('Try again')['fallback'] == 'question_limit'
    assert len(backend.calls) == 1 and researcher.disclosed == {}
    assert researcher.max_questions == 1 and researcher.max_facts == 1


def test_extractive_control_keeps_original_fact_text(profile):
    backend = ScriptedBackend({'answer': 'Persona-specific prose', 'fact_ids': ['study.sample']})
    episode = episode_fixture()
    researcher = Researcher(episode, backend, persona=Persona(science_profile=profile), mode='extractive')
    assert researcher.ask('What is the sample design?')['answer'] == episode.researcher.facts[0].text
    assert len(backend.calls) == 1


def test_revision_preference_adds_no_review_gate_or_extra_turn(tmp_path, profile):
    profile.attributes['revision_expectation'] = 'high'
    episode = episode_fixture()
    researcher = Researcher(episode, ScriptedBackend(), persona=Persona(science_profile=profile), max_questions=0)
    session = EpisodeSession(episode, researcher, tmp_path / 'controller')
    public = json.loads((session.output / 'public_input.json').read_text())
    assert public == episode.actor_input()
    result = session.submit_result(Submission(episode_id=episode.id, answer='Synthetic result, no scientific claim.'))
    assert result['submitted'] is True and session.closed
    assert researcher.questions == 0 and researcher.history == []
    assert profile.id not in json.dumps(public)


def test_offline_cli_attaches_to_a_new_file_only(tmp_path, profile):
    source = tmp_path / 'source.json'
    source.write_text(json.dumps({'researcher': {'max_questions': 3}, 'actor_steps': 20}))
    before = source.read_bytes()
    output = tmp_path / 'attached.json'
    args = ['attach', '--profile', str(PROFILES / 'pi_cautious.json'), '--config', str(source), '--output', str(output)]
    assert main(args) == 0
    attached = json.loads(output.read_text())
    assert attached['researcher'] == {'max_questions': 3} and attached['actor_steps'] == 20
    assert attached['persona']['science_profile'] == profile.model_dump()
    with pytest.raises(SystemExit):
        main(args)
    assert source.read_bytes() == before


def test_preview_reads_existing_pipeline_without_changing_episode_or_config(profile):
    path = ROOT / 'examples/science_personas/inspect_injection.py'
    spec = importlib.util.spec_from_file_location('persona_injection_preview', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    episode = episode_fixture()
    config = {'researcher': {'mode': 'grounded', 'max_questions': 2, 'max_facts_per_reply': 1}}
    before = deepcopy((episode.model_dump(), config))
    left = module.inspect_injection(episode, config, profile, 'What is the sample design?')
    right = module.inspect_injection(episode, config, with_attribute(profile, 'decision_delegation', 'high', profile_id='contrast'), 'What is the sample design?')
    assert left['identity'] != right['identity']
    for field in ['public_task_sha256', 'task_eval_sha256', 'non_persona_config_sha256', 'non_identity_system_sha256', 'eligible_fact_ids']:
        assert left[field] == right[field]
    assert left['model_calls'] == right['model_calls'] == 0
    assert (episode.model_dump(), config) == before
