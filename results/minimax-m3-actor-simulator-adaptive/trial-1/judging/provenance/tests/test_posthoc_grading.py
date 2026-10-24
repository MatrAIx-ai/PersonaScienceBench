"""Posthoc grading preserves failed/zero outcomes and never reruns an actor."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('grade_collection', ROOT / 'scripts/grade_collection.py')
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)


def job(tmp_path, status='grading_pending'):
    source = tmp_path / 'immutable-result.json'
    source.write_text('{"original":true}')
    return {'source': 'bixbench', 'task_id': 'fixture', 'arm': 'persona_off', 'trial': 1,
            'attempt': 1, 'selected': True, 'id': 'fixture/persona_off/attempt-1',
            'collection_status': status, 'input_hashes': {str(source): grade.digest(source)}}


@pytest.mark.parametrize('status,score', [('missing_submission', 0.0), ('execution_error', None), ('not_started', None)])
def test_non_submissions_and_execution_errors_make_no_calls(tmp_path, monkeypatch, status, score):
    def forbidden(*args, **kwargs):
        raise AssertionError('No inference allowed for this outcome')
    monkeypatch.setattr(grade, 'OpenRouterClient', forbidden)
    result = grade.grade_one(job(tmp_path, status), tmp_path / 'grading')
    assert result['normalized_score'] == score
    assert result['status'] == status and result['judge_calls'] == 0


def test_changed_inputs_fail_before_any_model_call(tmp_path, monkeypatch):
    item = job(tmp_path)
    Path(next(iter(item['input_hashes']))).write_text('changed')
    with pytest.raises(ValueError, match='Grading input changed'):
        grade.grade_one(item, tmp_path / 'grading')


def test_inventory_preserves_verified_unstarted_history_only(tmp_path):
    attempt = tmp_path / 'attempt-1'
    attempt.mkdir()
    case = attempt / 'output' / 'fixture'
    row = {'source': 'bixbench', 'task_id': 'fixture', 'arm': 'persona_off', 'attempt': 2}
    with pytest.raises(ValueError, match='Missing native result'):
        grade.attempt_result(case, attempt, row, 1)
    receipt = attempt / 'unstarted-state.json'
    previous = {**row, 'attempt': 1, 'status': 'infrastructure_error',
                'error': 'Fatal API error stopped further episodes'}
    grade.write(receipt, previous)
    assert grade.attempt_result(case, attempt, row, 1) == ('not_started', [receipt])
    with pytest.raises(ValueError, match='Invalid unstarted'):
        grade.attempt_result(case, attempt, {**row, 'attempt': 1}, 1)
    grade.write(receipt, {**previous, 'returncode': 1})
    with pytest.raises(ValueError, match='Invalid unstarted'):
        grade.attempt_result(case, attempt, row, 1)
    grade.write(receipt, previous)
    (attempt / 'process.log').write_text('ran')
    with pytest.raises(ValueError, match='Invalid unstarted'):
        grade.attempt_result(case, attempt, row, 1)


def test_resume_retains_a_zero_grade_without_calling_models(tmp_path, monkeypatch):
    item = job(tmp_path)
    out = tmp_path / 'grading'
    saved = {'status': 'scored', 'normalized_score': 0.0, 'id': item['id']}
    grade.write(out / 'attempts' / item['id'] / 'result.json', saved)
    def forbidden(*args, **kwargs):
        raise AssertionError('A completed zero must not be rerun')
    monkeypatch.setattr(grade, 'OpenRouterClient', forbidden)
    assert grade.grade_one(item, out, retry_errors=True) == saved


def test_error_retry_preserves_prior_grading_attempt(tmp_path, monkeypatch):
    item = job(tmp_path)
    out = tmp_path / 'grading'
    from types import SimpleNamespace
    monkeypatch.setattr(grade, 'OpenRouterClient', lambda **kwargs: SimpleNamespace(nvidia=object()))
    def failed(*args):
        raise RuntimeError('simulated transport error')
    monkeypatch.setattr(grade, 'grade_shared', failed)
    first = grade.grade_one(item, out)
    assert first['status'] == 'grading_error' and first['normalized_score'] is None
    monkeypatch.setattr(grade, 'grade_shared', lambda *args: {'status': 'scored', 'metrics': {'correct': False}})
    assert grade.grade_one(item, out)['status'] == 'grading_error'
    second = grade.grade_one(item, out, retry_errors=True)
    assert second['status'] == 'scored' and second['normalized_score'] == 0
    assert second['grade_attempt'] == 2
    assert grade.read(out / 'attempts' / item['id'] / 'grade-1/result.json') == first


@pytest.mark.parametrize('source,metrics,expected', [
    ('asibench', {'score': 2, 'max_score': 8}, 25),
    ('bixbench', {'correct': True}, 100),
    ('discoverybench', {'final_score': .4}, 40),
    ('sciconvbench', {'FRR': 0, 'entity_recovery': .75}, 0),
    ('expbench', {'gated_coverage_mean': 62}, 62),
])
def test_native_score_mapping_preserves_benchmark_definitions(source, metrics, expected):
    assert grade.normalized(source, {'status': 'scored', 'metrics': metrics}) == expected
    assert grade.normalized(source, {'status': 'error', 'metrics': metrics}) is None


def test_exp_responses_route_preserves_system_prompt_and_json_contract(monkeypatch):
    import httpx
    from types import SimpleNamespace
    captured = {}
    monkeypatch.setenv('NVIDIA_API_KEY', 'TEST_GATEWAY_KEY')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('PSB_FATAL_API_FILE', raising=False)
    def post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return SimpleNamespace(status_code=200, json=lambda: {
            'id': 'fixture', 'model': grade.JUDGE['model'], 'status': 'completed',
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': '{"ok":true}'}]}],
            'usage': {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}})
    monkeypatch.setattr(httpx, 'post', post)
    payload = {'model': grade.JUDGE['model'], 'messages': [
        {'role': 'system', 'content': 'Original native JSON rubric'}, {'role': 'user', 'content': ''}],
        'max_tokens': 4096, 'reasoning_effort': 'low', 'response_format': {'type': 'json_object'}}
    result = grade.ResponsesJudgeTransport().complete('judge', payload)
    assert captured['url'] == 'https://inference-api.nvidia.com/v1/responses'
    assert captured['headers']['Authorization'] == 'Bearer TEST_GATEWAY_KEY'
    assert captured['json']['input'] == [payload['messages'][0]]
    assert 'instructions' not in captured['json']
    assert captured['json']['reasoning'] == {'effort': 'low'}
    assert captured['json']['text']['format'] == {'type': 'json_object'}
    assert result['provider'] == 'nvidia'
    with pytest.raises(ValueError, match='Only the configured Astra judge'):
        grade.ResponsesJudgeTransport().complete('actor', payload)


def test_failed_grading_reuses_only_identical_completed_prefix(tmp_path):
    import json
    source = tmp_path / 'calls.jsonl'
    payload = {'model': grade.JUDGE['model'], 'reasoning_effort': 'low', 'messages': [{'role': 'user', 'content': 'Grade this'}]}
    good = {'request': payload, 'response': {'choices': [{'finish_reason': 'stop', 'message': {'content': 'native verdict'}}]}}
    bad = {'request': payload, 'response': {'choices': [{'finish_reason': 'length', 'message': {'content': 'partial'}}]}}
    source.write_text(json.dumps(good) + '\n' + json.dumps(bad) + '\n')
    class Transport:
        def complete_recorded(self, payload, record, *, role):
            return 'new call'
    replay = grade.CompletedJudgePrefix(Transport(), source, tmp_path / 'replay.jsonl')
    with pytest.raises(ValueError, match='request differs'):
        replay.complete_recorded({**payload, 'reasoning_effort': 'high'}, None, role='judge')
    assert replay.complete_recorded(payload, None, role='judge') == good['response']
    assert replay.complete_recorded(payload, None, role='judge') == 'new call'
    receipt = json.loads((tmp_path / 'replay.jsonl').read_text())
    assert receipt['additional_model_call'] is False and receipt['record_index'] == 0


def refusal_fixture(tmp_path, code='bio_policy'):
    item = job(tmp_path)
    out = tmp_path / 'grading'
    base = out / 'attempts' / item['id']
    destination = base / 'grade-1'
    fatal = {'status': 400, 'error': {'code': code, 'message': 'blocked'}}
    grade.write(out / 'fatal_api.json', fatal)
    grade.write(destination / 'error.private.json', {
        'message': f"OpenAI HTTP 400: {fatal['error']}"})
    previous = {'status': 'grading_error', 'normalized_score': None,
                'directory': str(destination), 'judge_calls': 2}
    grade.write(destination / 'result.json', previous)
    grade.write(base / 'result.json', previous)
    return item, out, destination, previous


@pytest.mark.parametrize('code', ['bio_policy', 'cyber_policy'])
def test_skip_only_authorized_policy_refusal_preserves_history_and_never_retries(tmp_path, monkeypatch, code):
    item, out, destination, previous = refusal_fixture(tmp_path, code)
    grade.skip_policy_refusals([item], out, [item['id']])
    assert not (out / 'fatal_api.json').exists()
    archive = list((out / 'skipped-refusals').glob('*.json'))
    assert len(archive) == 1
    assert grade.read(archive[0])['skipped_ids'] == [item['id']]
    assert grade.read(destination / 'result.json') == previous
    def forbidden(*args, **kwargs):
        pytest.fail('Skipped refusal must never be sent to a model again')
    monkeypatch.setattr(grade, 'OpenRouterClient', forbidden)
    result = grade.grade_one(item, out, retry_errors=True)
    assert result['retry_skipped'] and result['normalized_score'] is None
    grade.skip_policy_refusals([item], out, [item['id']])  # Idempotent resume.


def test_skip_cannot_clear_an_unrelated_fatal_error(tmp_path):
    item, out, destination, previous = refusal_fixture(tmp_path)
    fatal = {'status': 401, 'error': {'code': 'authentication_error'}}
    grade.write(out / 'fatal_api.json', fatal)
    with pytest.raises(ValueError, match='does not match'):
        grade.skip_policy_refusals([item], out, [item['id']])
    assert grade.read(out / 'fatal_api.json') == fatal
    assert grade.read(destination.parent / 'result.json') == previous


def test_skip_requires_recorded_policy_refusal(tmp_path):
    item, out, destination, previous = refusal_fixture(tmp_path)
    grade.write(destination / 'error.private.json', {'message': 'timeout'})
    with pytest.raises(ValueError, match='refusal evidence'):
        grade.skip_policy_refusals([item], out, [item['id']])
    assert (out / 'fatal_api.json').exists()


@pytest.mark.parametrize('code', ['bio_policy', 'cyber_policy', 'invalid_model'])
def test_judge_refusals_do_not_stop_unrelated_work_but_configuration_errors_do(tmp_path, monkeypatch, code):
    import httpx, json
    from types import SimpleNamespace
    from personasciencebench.openai_transport import PolicyRefusalError
    monkeypatch.setenv('NVIDIA_API_KEY', 'TEST_KEY')
    fatal = tmp_path / 'fatal_api.json'
    monkeypatch.setenv('PSB_FATAL_API_FILE', str(fatal))
    calls = []
    def post(*args, **kwargs):
        calls.append(1)
        return SimpleNamespace(status_code=400, json=lambda: {'error': {
            'code': '400', 'message': 'Gateway error: ' + json.dumps({'error': {'code': code}})}})
    monkeypatch.setattr(httpx, 'post', post)
    payload = {'model': grade.JUDGE['model'], 'messages': [{'role': 'user', 'content': 'fixture'}],
               'max_tokens': 4096, 'reasoning_effort': 'low'}
    expected = RuntimeError if code == 'invalid_model' else PolicyRefusalError
    with pytest.raises(expected):
        grade.ResponsesJudgeTransport().complete('judge', payload)
    assert fatal.exists() == (code == 'invalid_model')
    assert len(calls) == 1


def test_new_policy_refusal_is_unavailable_and_excluded_from_all_retries(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from personasciencebench.openai_transport import PolicyRefusalError
    item = job(tmp_path)
    out = tmp_path / 'grading'
    monkeypatch.setattr(grade, 'OpenRouterClient', lambda **kwargs: SimpleNamespace(nvidia=object()))
    def refused(*args):
        raise PolicyRefusalError('provider code cyber_policy')
    monkeypatch.setattr(grade, 'grade_shared', refused)
    first = grade.grade_one(item, out)
    assert first['retry_skipped'] and first['normalized_score'] is None
    assert first['skip_evidence_sha256'] == grade.digest(first['skip_evidence'])
    def forbidden(*args):
        pytest.fail('Policy refused submission must not be retried')
    monkeypatch.setattr(grade, 'grade_shared', forbidden)
    assert grade.grade_one(item, out, retry_errors=True) == first


def test_grade_reuse_preserves_zero_and_history_updates_selection_without_api(tmp_path, monkeypatch):
    item=job(tmp_path);previous=tmp_path/'old';out=tmp_path/'new'
    contract={'run_dir':str(tmp_path),'judge':grade.JUDGE,'judge_supported_parameters':grade.JUDGE_PARAMETERS,
              'policy':'fixture','jobs':[item]}
    grade.write(previous/'inventory.json',contract)
    destination=previous/'attempts'/item['id']/'grade-1'
    result={**item,'judge':grade.JUDGE,'status':'scored','normalized_score':0.0,
            'directory':str(destination),'grade_attempt':1,'judge_calls':1}
    grade.write(destination/'result.json',result)
    grade.write(destination.parent/'result.json',result)
    grade.write(previous/'results.json',[result])
    grade.write(out/'inventory.json',{**contract,'jobs':[{**item,'selected':False}]})
    grade.reuse_previous_grades(previous,out)
    copied=grade.read(out/'attempts'/item['id']/'result.json')
    assert copied['normalized_score']==0.0 and not copied['selected']
    assert (out/'attempts'/item['id']/'grade-1/result.json').read_bytes()==(destination/'result.json').read_bytes()
    def forbidden(*args,**kwargs):pytest.fail('Completed grade must never be rerun')
    monkeypatch.setattr(grade,'OpenRouterClient',forbidden)
    assert grade.grade_one({**item,'selected':False},out,retry_errors=True)==copied
    grade.reuse_previous_grades(previous,out)
    assert grade.read(out/'grade-reuse.json')['additional_judge_calls']==0


def test_grade_reuse_rejects_changed_input_contract_before_copy(tmp_path):
    item=job(tmp_path);previous=tmp_path/'old';out=tmp_path/'new'
    contract={'run_dir':str(tmp_path),'judge':grade.JUDGE,'judge_supported_parameters':grade.JUDGE_PARAMETERS,
              'policy':'fixture','jobs':[item]}
    grade.write(previous/'inventory.json',contract)
    grade.write(previous/'results.json',[])
    grade.write(out/'inventory.json',{**contract,'jobs':[{**item,'input_hashes':{}}]})
    with pytest.raises(ValueError,match='Prior grading inputs changed'):
        grade.reuse_previous_grades(previous,out)
    assert not (out/'attempts').exists()


def test_discovery_repair_changes_only_small_native_call_limit(monkeypatch):
    captured=[]
    def completion(self, messages, tools=None, **kwargs):
        captured.append(kwargs['settings']);return 'fixture'
    monkeypatch.setattr(grade.OpenRouterClient,'completion',completion)
    judge=grade.DiscoveryCapRepairJudge(4096,**grade.JUDGE,role='judge')
    settings={'max_tokens':250,'temperature':0}
    judge.completion([],settings=settings)
    judge.completion([],settings={'max_tokens':4096,'temperature':1})
    assert settings['max_tokens']==250
    assert captured==[{'max_tokens':4096,'temperature':0},{'max_tokens':4096,'temperature':1}]


def test_repair_targets_exclude_successes_other_errors_and_other_benchmarks(tmp_path):
    jobs=[]
    import json
    for i,(source,status,cap,finish,selected) in enumerate([
            ('discoverybench','grading_error',250,'length',True),
            ('discoverybench','scored',250,'length',True),
            ('asibench','grading_error',250,'length',True),
            ('discoverybench','grading_error',4096,'length',True),
            ('discoverybench','grading_error',250,'stop',True),
            ('discoverybench','grading_error',250,'length',False)]):
        item={'id':str(i),'source':source,'selected':selected};jobs.append(item)
        directory=tmp_path/'attempts'/str(i)/'grade-1'
        grade.write(directory.parent/'result.json',{'status':status,'directory':str(directory)})
        directory.mkdir()
        (directory/'api_calls.private.jsonl').write_text(json.dumps({
            'request':{'max_tokens':cap},'response':{'choices':[{'finish_reason':finish}]}})+'\n')
    assert grade.discovery_cap_targets(jobs,tmp_path)==['0']


def test_replay_preserves_prefix_across_multiple_failed_grading_attempts(tmp_path):
    import json
    original=tmp_path/'grade-1';second=tmp_path/'grade-2';original.mkdir();second.mkdir()
    first_request={'model':grade.JUDGE['model'],'max_tokens':4096,'messages':[]}
    small_request={**first_request,'max_tokens':250}
    good={'request':first_request,'response':{'choices':[{'finish_reason':'stop','message':{'content':'saved'}}]}}
    small_good={'request':small_request,'response':{'choices':[{'finish_reason':'stop','message':{'content':'other saved'}}]}}
    source=original/'api_calls.private.jsonl'
    source.write_text(json.dumps(good)+'\n')
    grade.write(second/'unused.json',{})
    (second/'api_replay.private.jsonl').write_text(json.dumps({'source':str(source),'source_sha256':grade.digest(source),'record_index':0})+'\n')
    later=second/'api_calls.private.jsonl';later.write_text(json.dumps(small_good)+'\n')
    class Transport:
        def complete_recorded(self,payload,record,*,role):return 'new call'
    replay=grade.CompletedJudgePrefix(Transport(),later,tmp_path/'replay.jsonl',allowed_cap_change=(250,4096))
    assert replay.complete_recorded(first_request,None,role='judge')==good['response']
    assert replay.complete_recorded(first_request,None,role='judge')=='new call'
    assert replay.complete_recorded(first_request,None,role='judge')=='new call'
    receipt=json.loads((tmp_path/'replay.jsonl').read_text())
    assert receipt['source']==str(source) and receipt['record_index']==0
