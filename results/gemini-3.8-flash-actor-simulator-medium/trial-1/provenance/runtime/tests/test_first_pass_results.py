"""Offline safeguards for cross-actor configuration and harness-only result collection."""
import importlib.util
import json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('first_pass',Path(__file__).resolve().parents[1]/'scripts/run_openai_first_pass.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def test_actor_override_preserves_other_roles():
    models=runner.role_models('gpt-6-astra','low','gpt-5.6-sol','none')
    assert models['actor']=={'model':'gpt-5.6-sol','provider':'openai','reasoning_effort':'none'}
    assert models['researcher']==models['judge']=={'model':'gpt-6-astra','provider':'openai','reasoning_effort':'low'}

def test_all_role_model_setting():
    assert all(x['model']=='gpt-5.6-sol' and x['reasoning_effort']=='low' for x in runner.role_models('gpt-5.6-sol','low').values())

def test_nested_actor_result_is_not_a_harness_result(tmp_path):
    case=tmp_path/'case';artifact=case/'actor/workspace';artifact.mkdir(parents=True)
    (artifact/'result.json').write_text('[1,2,3]')
    row={'source_task_id':'bix-1-q1','status':'scored'}
    (case/'result.json').write_text(json.dumps(row))
    assert runner.load_native_result(tmp_path,'bixbench','bix-1-q1','case')==[row]

def test_wrong_task_result_rejected(tmp_path):
    case=tmp_path/'case';case.mkdir();(case/'result.json').write_text('{"source_task_id":"other"}')
    with pytest.raises(ValueError,match='does not match'):runner.load_native_result(tmp_path,'bixbench','bix-1-q1','case')

def test_exp_native_path_and_missing_result(tmp_path):
    assert runner.load_native_result(tmp_path,'expbench','a/b','ignored')==[]
    case=tmp_path/'a__b';case.mkdir();row={'task_id':'a/b','final':{}}
    (case/'result.json').write_text(json.dumps(row))
    assert runner.load_native_result(tmp_path,'expbench','a/b','ignored')==[row]

def test_actor_and_simulator_override_keeps_judge_fixed():
    models=runner.role_models("gpt-6-astra","low","gpt-5.6-sol","low","gpt-5.6-sol","low")
    assert models["actor"]==models["researcher"]=={"model":"gpt-5.6-sol","provider":"openai","reasoning_effort":"low"}
    assert models["judge"]=={"model":"gpt-6-astra","provider":"openai","reasoning_effort":"low"}
