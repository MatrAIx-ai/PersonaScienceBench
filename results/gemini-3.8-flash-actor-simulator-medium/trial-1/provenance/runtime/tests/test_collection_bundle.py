"""Export correctness and privacy tests; no model calls."""
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('collection_export',ROOT/'scripts/export_collection_bundle.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_shared_events_keep_order_and_text_but_exclude_private_fields():
    events=[{'type':'actor_command_result','payload':{'stdout':'private command result'}},
            {'type':'researcher_decision','sequence':4,'time':123,'payload':{'message':'verbatim\n科学','fact_ids':['private-key'],'phase':'plan'}},
            {'type':'agent_handoff','sequence':5,'payload':{'answer':'answer','artifacts':{'private':'path'},'payload':{'hidden':'not public'}}}]
    result=module.shared_events(events)
    assert len(result)==2
    assert result[0]=={'type':'researcher_decision','sequence':4,'time':123,'source_event_index':1,'payload':{'message':'verbatim\n科学','phase':'plan'}}
    assert result[1]['payload']=={'answer':'answer'}


def test_missing_submission_not_misclassified_as_infrastructure():
    assert module.disposition({'status':'no_submission'},'infrastructure_error')[0]=='missing_submission'
    assert module.disposition({'status':'infrastructure_error'},'infrastructure_error')[0]=='execution_error'
    assert module.disposition({'status':'grading_pending'},'finished')[1] is None


def test_secret_scan_does_not_disclose_secret():
    secret=b'fixture-secret-value'
    with pytest.raises(ValueError) as exc:
        module.scan_bytes(b'prefix'+secret+b'suffix',(secret,),'file.json')
    assert secret.decode() not in str(exc.value)


def test_export_rejects_existing_destination_and_incomplete_inventory(tmp_path):
    out=tmp_path/'bundle';out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):
        module.export(tmp_path/'run',out)
    out.rmdir()
    with pytest.raises(ValueError,match='1,000'):
        module.export(tmp_path/'run',out)
    assert not out.exists()


def test_copy_rejects_symlinks(tmp_path):
    target=tmp_path/'file';target.write_text('original')
    link=tmp_path/'link';link.symlink_to(target)
    with pytest.raises(ValueError,match='non-symlink'):
        module.copy_checked(link,tmp_path/'out')


def test_validator_rejects_corrupted_and_unmanifested_payloads(tmp_path):
    spec=importlib.util.spec_from_file_location('collection_validate',ROOT/'scripts/validate_collection_bundle.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    artifact=tmp_path/'artifact.bin';artifact.write_bytes(b'original')
    (tmp_path/'bundle_manifest.json').write_text(json.dumps({'files':{'artifact.bin':{'bytes':8,'sha256':module.sha(artifact)}}}))
    artifact.write_bytes(b'corrupt!')
    with pytest.raises(ValueError,match='checksum/size'):
        validator.validate(tmp_path)
    artifact.write_bytes(b'original')
    (tmp_path/'unexpected.txt').write_text('unexpected')
    with pytest.raises(ValueError,match='every exported file'):
        validator.validate(tmp_path)


def test_exp_checkpoint_excludes_sdk_private_reasoning_without_rewriting_actions():
    trace='\n'.join(json.dumps(r) for r in [
        {'kind':'SystemPromptEvent','system_prompt':'private system'},
        {'kind':'ActionEvent','thought':'private thought','reasoning_content':'private reasoning','thinking_blocks':[{'thinking':'private thinking'}], 'action':{'command':'print("scientific result")','reasoning':'literal scientific parameter'}},
        {'kind':'MessageEvent','llm_message':{'role':'assistant','reasoning_content':'private reasoning','content':[{'type':'thinking','text':'hidden'},{'type':'text','text':'visible answer'}]}},
        {'kind':'ObservationEvent','observation':{'content':'original output'}}])
    records=[json.loads(line) for line in module.public_sdk_trace(trace).splitlines()]
    assert len(records)==3
    assert records[0]['source_event_index']==1
    assert records[0]['action']=={'command':'print("scientific result")','reasoning':'literal scientific parameter'}
    assert 'thought' not in records[0] and 'thinking_blocks' not in records[0]
    assert records[1]['llm_message']=={'role':'assistant','content':[{'type':'text','text':'visible answer'}]}
    assert records[2]['observation']['content']=='original output'
