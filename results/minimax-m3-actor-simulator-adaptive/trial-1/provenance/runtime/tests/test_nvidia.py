"""Offline NVIDIA boundary and collection tests; no real API or actor execution."""
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import httpx
import pytest

from personasciencebench.inference import OpenRouterClient, load_env
from personasciencebench.nvidia_transport import (
    ChatTransport, GEMINI_MODEL, MINIMAX_MODEL, MINIMAX_DEPLOYMENT, chat_payload, preflight)


def completion(message=None):
    return {'id':'fixture', 'object':'chat.completion', 'created':0, 'model':GEMINI_MODEL,
            'choices':[{'index':0, 'finish_reason':'stop', 'message':message or {'role':'assistant','content':'ok'}}],
            'usage':{'prompt_tokens':5,'completion_tokens':3,'total_tokens':8}}


@pytest.fixture
def sdk(monkeypatch):
    import openai
    original = openai.OpenAI
    requests = []
    state = {'response':completion(), 'status':200}
    def handler(request):
        requests.append(request)
        return httpx.Response(state['status'], json=state['response'])
    def factory(**kwargs):
        return original(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    monkeypatch.setattr(openai, 'OpenAI', factory)
    monkeypatch.setenv('NVIDIA_API_KEY', 'NVIDIA_TEST_SECRET')
    monkeypatch.delenv('PSB_FATAL_API_FILE', raising=False)
    return state, requests


@pytest.mark.parametrize('model,effort', [(GEMINI_MODEL, 'medium'), (MINIMAX_MODEL, 'adaptive')])
def test_chat_wire_settings_and_secret_free_records(sdk, model, effort):
    state, requests = sdk
    records = []
    client = OpenRouterClient(model, role='actor', provider='nvidia',
                              reasoning_effort=effort, record=records.append)
    assert client.complete([{'role':'user','content':'test'}], json_mode=True) == 'ok'
    request = json.loads(requests[0].content)
    assert requests[0].url == 'https://inference-api.nvidia.com/v1/chat/completions'
    assert requests[0].headers['authorization'] == 'Bearer NVIDIA_TEST_SECRET'
    if model == MINIMAX_MODEL:
        assert request['chat_template_kwargs'] == {'thinking_mode': 'adaptive'}
        assert 'reasoning_effort' not in request and 'extra_body' not in request
    else:
        assert request['reasoning_effort'] == 'medium'
    assert request['response_format'] == {'type':'json_object'}
    assert 'reasoning' not in request and 'provider' not in request
    assert records[0]['request'] == request
    assert records[0]['usage']['total_tokens'] == 8
    assert 'NVIDIA_TEST_SECRET' not in json.dumps(records)


def test_chat_preserves_tool_signature(sdk):
    state, requests = sdk
    tool = {'id':'call_1','type':'function','function':{'name':'echo','arguments':'{}'},
            'extra_content':{'google':{'thought_signature':'signature-fixture'}}}
    state['response'] = completion({'role':'assistant','tool_calls':[tool]})
    client = ChatTransport()
    first = client.complete({'model':GEMINI_MODEL,'messages':[{'role':'user','content':'test'}]})
    message = first['choices'][0]['message']
    assert message['tool_calls'][0]['extra_content'] == tool['extra_content']
    client.complete({'model':GEMINI_MODEL,'messages':[message,{'role':'tool','tool_call_id':'call_1','content':'ok'}]})
    assert json.loads(requests[-1].content)['messages'][0]['tool_calls'][0] == tool


def test_auth_failure_stops_run_without_secret_or_retries(sdk, monkeypatch, tmp_path):
    state, requests = sdk
    state.update(status=401, response={'error':{'message':'NVIDIA_TEST_SECRET','type':'authentication_error'}})
    fatal = tmp_path/'fatal_api.json'
    monkeypatch.setenv('PSB_FATAL_API_FILE', str(fatal))
    with pytest.raises(RuntimeError, match='HTTP 401') as error:
        ChatTransport().complete({'model':GEMINI_MODEL,'messages':[]})
    assert 'NVIDIA_TEST_SECRET' not in str(error.value) + fatal.read_text()
    with pytest.raises(RuntimeError, match='Run stopped'):
        ChatTransport().complete({'model':GEMINI_MODEL,'messages':[]})
    assert len(requests) == 1


def test_preflight_uses_exact_deployment_and_catalog_prices(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY', 'FIXTURE')
    original = httpx.Client
    paths = []
    def handler(request):
        paths.append(request.url.path)
        if request.url.path == '/v1/models':
            return httpx.Response(200, json={'data':[{'id':GEMINI_MODEL}]})
        assert request.url.params['model'] == GEMINI_MODEL
        return httpx.Response(200, json={'data':[{'model_name':GEMINI_MODEL,
            'litellm_params':{'model':'vertex_ai/gemini-3.8-flash','api_key':'HIDDEN_DEPLOYMENT_KEY'},
            'model_info':{'base_model':'vertex_ai/gemini-3.7-flash',
                'input_cost_per_token':0.000001,'output_cost_per_token':0.000002,
                'supports_function_calling':True,'supports_reasoning':True,'supports_response_schema':True}}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(handler)))
    catalog = preflight({'actor':{'model':GEMINI_MODEL,'reasoning_effort':'medium'}})
    assert catalog['actor']['deployment_model'] == 'vertex_ai/gemini-3.8-flash'
    assert catalog['actor']['accounting_base_model'] == 'vertex_ai/gemini-3.7-flash'
    assert catalog['actor']['pricing']['prompt'] == 0.000001
    assert 'HIDDEN_DEPLOYMENT_KEY' not in json.dumps(catalog)
    assert paths == ['/v1/models','/v1/model/info']


def test_dotenv_nvidia_is_literal_and_environment_wins(monkeypatch, tmp_path):
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    file = tmp_path/'.env'
    file.write_text('export NVIDIA_API_KEY="literal-$(do-not-run)"\nUNRELATED_SECRET=hidden\n')
    load_env(file)
    import os
    assert os.environ['NVIDIA_API_KEY'] == 'literal-$(do-not-run)'
    monkeypatch.setenv('NVIDIA_API_KEY', 'inherited')
    load_env(file)
    assert os.environ['NVIDIA_API_KEY'] == 'inherited'


@pytest.mark.parametrize('model,effort', [(GEMINI_MODEL, 'medium'), (MINIMAX_MODEL, 'adaptive')])
def test_exp_gateway_records_actual_wire_request_and_token_cost(sdk, tmp_path, model, effort):
    from expbench.gateway import Gateway, NVIDIATransport
    from expbench.schema import ModelSettings
    from expbench.budget import Ledger, Budget
    spec = ModelSettings(provider='nvidia', model=model, reasoning_effort=effort,
                         max_output_tokens=512, input_usd_per_million=1, output_usd_per_million=2)
    ledger = Ledger(Budget(None), Budget(None))
    log = tmp_path/'api.jsonl'
    gateway = Gateway(NVIDIATransport('fixture',30), {'researcher':spec}, ledger, log)
    gateway.complete('researcher',[{'role':'user','content':'test'}],
                     schema={'type':'object','properties':{'status':{'type':'string'}}})
    wire = json.loads(sdk[1][0].content)
    assert 'provider' not in wire
    if model == MINIMAX_MODEL:
        assert wire['chat_template_kwargs'] == {'thinking_mode': 'adaptive'}
        assert 'reasoning_effort' not in wire
    else:
        assert wire['reasoning_effort'] == 'medium'
    assert wire['response_format']['type'] == 'json_schema'
    assert json.loads(log.read_text().splitlines()[0])['payload'] == wire
    assert ledger.episode.charged == pytest.approx(11/1_000_000)


def test_minimax_native_mapping_idempotent_and_rejects_medium():
    payload = {'model': MINIMAX_MODEL, 'reasoning': {'effort': 'adaptive'}}
    mapped = chat_payload(payload)
    assert chat_payload(mapped) == mapped
    assert payload['reasoning'] == {'effort': 'adaptive'}
    with pytest.raises(ValueError, match='native adaptive'):
        chat_payload({'model': MINIMAX_MODEL, 'reasoning': {'effort': 'medium'}})


def token_policy(tmp_path, monkeypatch):
    import hashlib
    manifest = tmp_path/'manifest.json'
    manifest.write_text('{"model":"minimax"}')
    policy = {'id':'fixture-raised-caps', 'model':MINIMAX_MODEL,
              'authorization':'user_requested_higher_token_limits',
              'run_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
              'max_output_tokens':{'actor':32768, 'researcher':16384}}
    (tmp_path/'generation_limits.json').write_text(json.dumps(policy))
    monkeypatch.setenv('PSB_FATAL_API_FILE', str(tmp_path/'fatal_api.json'))
    return policy


def test_run_bound_cap_override_shared_wire_and_provenance(sdk, tmp_path, monkeypatch):
    policy = token_policy(tmp_path, monkeypatch)
    records=[]
    client=OpenRouterClient(MINIMAX_MODEL, role='actor', provider='nvidia',
                           reasoning_effort='adaptive', max_tokens=12288, record=records.append)
    client.complete([{'role':'user','content':'fixture'}])
    wire=json.loads(sdk[1][0].content)
    assert wire['max_tokens']==32768
    assert records[0]['request']==wire
    assert records[0]['output_limit_override']['configured_max_tokens']==12288
    assert records[0]['output_limit_override']['effective_max_tokens']==32768
    # A loaded client keeps its cap, even if a later policy is installed.
    policy['max_output_tokens']['actor']=65536
    (tmp_path/'generation_limits.json').write_text(json.dumps(policy))
    assert client.max_tokens==32768


def test_cap_override_exp_uses_effective_budget_without_mutating_config(sdk, tmp_path, monkeypatch):
    from expbench.gateway import Gateway, NVIDIATransport
    from expbench.schema import ModelSettings
    from expbench.budget import Ledger, Budget
    token_policy(tmp_path, monkeypatch)
    spec=ModelSettings(provider='nvidia',model=MINIMAX_MODEL,reasoning_effort='adaptive',
                       max_output_tokens=8192,input_usd_per_million=0,output_usd_per_million=1)
    ledger=Ledger(Budget(None),Budget(None));reserved=[]
    original=ledger.reserve
    def reserve(value):
        reserved.append(value); original(value)
    monkeypatch.setattr(ledger,'reserve',reserve)
    log=tmp_path/'api.jsonl'
    gateway=Gateway(NVIDIATransport('fixture',30),{'researcher':spec},ledger,log)
    gateway.complete('researcher',[{'role':'user','content':'fixture'}])
    assert spec.max_output_tokens==8192
    assert json.loads(sdk[1][0].content)['max_tokens']==16384
    assert reserved==[16384/1e6]
    receipt=json.loads(log.read_text().splitlines()[0])
    assert receipt['output_limit_override']['configured_max_tokens']==8192


def test_cap_override_never_changes_judge_other_model_or_wrong_run(tmp_path,monkeypatch):
    from personasciencebench.nvidia_transport import output_limit_override
    token_policy(tmp_path,monkeypatch)
    assert output_limit_override(MINIMAX_MODEL,'judge',4096)==(4096,None)
    assert output_limit_override(GEMINI_MODEL,'actor',12288)==(12288,None)
    (tmp_path/'manifest.json').write_text('changed')
    with pytest.raises(ValueError,match='does not match'):
        output_limit_override(MINIMAX_MODEL,'actor',12288)


@pytest.mark.parametrize('deployment,tools_ok,effort,accepted', [
    (MINIMAX_DEPLOYMENT, None, 'adaptive', True),
    ('unverified/deployment', None, 'adaptive', False),
    (MINIMAX_DEPLOYMENT, False, 'adaptive', False),
    (MINIMAX_DEPLOYMENT, None, 'medium', False),
])
def test_minimax_catalog_requires_verified_deployment(monkeypatch, deployment, tools_ok, effort, accepted):
    monkeypatch.setenv('NVIDIA_API_KEY', 'FIXTURE')
    original = httpx.Client
    def handler(request):
        if request.url.path == '/v1/models':
            return httpx.Response(200, json={'data': [{'id': MINIMAX_MODEL}]})
        return httpx.Response(200, json={'data': [{'model_name': MINIMAX_MODEL,
            'litellm_params': {'model': deployment}, 'model_info': {
                'supports_function_calling': tools_ok,
                'input_cost_per_token': 0, 'output_cost_per_token': 0}}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: original(**kw, transport=httpx.MockTransport(handler)))
    specs = {'actor': {'model': MINIMAX_MODEL, 'reasoning_effort': effort}}
    if not accepted:
        with pytest.raises(ValueError): preflight(specs)
    else:
        meta = preflight(specs)['actor']
        assert meta['native_thinking_mode'] == 'adaptive'
        assert meta['catalog_capabilities']['supports_function_calling'] is None
        assert meta['capability_source'].startswith('https://docs.api.nvidia.com/')


def test_missing_frozen_tasks_stop_before_preflight(monkeypatch, tmp_path):
    import importlib.util
    from personasciencebench import inference, runtime
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('nvidia_main_test',root/'scripts/run_main.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.syspath_prepend(str(root/'scripts'))
    monkeypatch.setattr(runtime,'Sandbox',lambda *a:SimpleNamespace(check=lambda:None))
    monkeypatch.setattr(inference,'preflight',lambda *a,**k:pytest.fail('No API access with missing frozen inputs'))
    run = tmp_path/'run'
    monkeypatch.setattr(sys,'argv',['run_main.py','--run-dir',str(run),'--require-prepared',
                        '--provider','nvidia','--model',GEMINI_MODEL,'--reasoning-effort','medium','--collect-only'])
    monkeypatch.chdir(root)
    with pytest.raises(ValueError,match='Frozen preparation missing for 200 tasks'):
        runner.main()
    assert not run.exists()


def test_resume_unstarted_never_selects_real_failures_or_non_submissions():
    import importlib.util
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('resume_main_test', root/'scripts/run_main.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    queued = {'status':'infrastructure_error', 'error':'Fatal API error stopped further episodes'}
    assert runner.unstarted_after_api_stop(queued)
    assert not runner.unstarted_after_api_stop({**queued, 'returncode':1})
    assert not runner.unstarted_after_api_stop({**queued, 'native_results':[{'status':'error'}]})
    assert not runner.unstarted_after_api_stop({'status':'infrastructure_error', 'native_results':[{'status':'no_submission'}]})
    assert not runner.unstarted_after_api_stop({'status':'finished'})
    assert not runner.unstarted_after_api_stop({'status':'infrastructure_error', 'error':'HTTP 429'})
    assert runner.retry_execution_failure({'status':'infrastructure_error', 'native_results':[{'status':'error'}]})
    assert runner.retry_execution_failure({'status':'infrastructure_error', 'native_results':[{'status':'infrastructure_error'}]})
    for status in ('no_submission', 'missing_submission'):
        state = {'status':'infrastructure_error', 'native_results':[{'status':status}]}
        assert runner.missing_submission(state)
        assert not runner.retry_execution_failure(state)
    assert not runner.retry_execution_failure({'status':'finished', 'native_results':[{'status':'grading_pending'}]})


@pytest.mark.parametrize('exp', [False, True])
def test_raised_cap_retries_only_truncations_below_new_cap(tmp_path, exp):
    import importlib.util
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('raised_caps_main',root/'scripts/run_main.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    base=tmp_path/'slot';folder=base/'attempt-2'/'output';folder.mkdir(parents=True)
    state={'attempt':2,'status':'infrastructure_error','native_results':[{'status':'error'}]}
    caps={'actor':32768,'researcher':16384}
    for cap,finish,expected in [(12288,'length',True),(32768,'length',False),(12288,'stop',False)]:
        request={'max_tokens':cap}
        response={'choices':[{'finish_reason':finish}]}
        rows=([{'phase':'request','call_id':1,'payload':request},
               {'phase':'response','call_id':1,'role':'actor','response':response}] if exp else
              [{'role':'actor','request':request,'response':response}])
        (folder/'api_calls.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in rows))
        assert runner.truncated_below_policy(base,state,caps)==expected
    (folder/'api_calls.jsonl').write_text(json.dumps({'role':'actor','request':{'max_tokens':12288},
        'response':{'choices':[{'finish_reason':'length'}]}})+'\n')
    assert not runner.truncated_below_policy(base,{**state,'status':'finished'},caps)


@pytest.mark.parametrize('actor_error', [False, True])
def test_shared_collection_preserves_submission_without_judge(monkeypatch, tmp_path, actor_error):
    from personasciencebench import runner, actor, runtime
    from personasciencebench.packaging import export_episode, write_json
    from personasciencebench.schema import Episode, PublicContext, EvaluatorSpec, Submission
    episode = Episode(id='discoverybench:fixture', benchmark='discoverybench', source_task_id='fixture',
        study_id='fixture', domain='biology', source_revision='fixture',
        public=PublicContext(question='State a finding.'), evaluator=EvaluatorSpec(kind='fixture',version='fixture'))
    package = tmp_path/'package'
    record = export_episode(episode, package)
    prepared = tmp_path/'prepared'
    write_json(prepared/'pilot_manifest.json', {'cases':[record],'source_root':'unused','source_manifest':'unused'})
    roles = []
    monkeypatch.setattr(runner,'preflight',lambda models: {r:{'supported_parameters':[]} for r in models})
    def client(*, role, **kwargs):
        roles.append(role)
        return SimpleNamespace()
    monkeypatch.setattr(runner, 'OpenRouterClient', client)
    def fail_grade(*args):pytest.fail('Final grader must not run during collection')
    monkeypatch.setattr(runner,'load_adapter',lambda *args: SimpleNamespace(evaluate=fail_grade))
    monkeypatch.setattr(runtime,'Sandbox',lambda *args: SimpleNamespace(check=lambda:{'exit_code':0}))
    def run_actor(session, *args, **kwargs):
        session.submit_result(Submission(episode_id=episode.id,answer='A saved finding'))
        return {'status':'error' if actor_error else 'completed'}
    monkeypatch.setattr(actor,'run_actor',run_actor)
    spec = {'model':GEMINI_MODEL,'provider':'nvidia','reasoning_effort':'medium'}
    config = {'models':{'actor':spec,'researcher':spec,'judge':{'model':'gpt-6-astra','provider':'openai','reasoning_effort':'low'}},
              'collect_only':True,'persona':{'enabled':False},'researcher':{},'actor_steps':2,'pilot_cases_per_benchmark':1}
    result = runner.run_pilots(prepared,['discoverybench'],tmp_path/'output',tmp_path/'python',config,parallel=1)['cases'][0]
    assert roles == ['actor','researcher']
    assert result['status'] == ('infrastructure_error' if actor_error else 'grading_pending'), result
    case = Path(result['case_directory'])
    assert json.loads((case/'controller/submission.json').read_text())['answer'] == 'A saved finding'
    if not actor_error:
        assert result['evaluation']['score'] is None
        assert result['evaluation']['details']['intended_judge']['model'] == 'gpt-6-astra'


def test_exp_collection_keeps_final_design_and_skips_grading(monkeypatch, tmp_path):
    from expbench import realistic
    from expbench.schema import Config
    from expbench.budget import Ledger, Budget
    root = Path(__file__).resolve().parents[1]
    config = Config.load(root/'configs/full_persona_v2/exp.json')
    config.collect_only = True
    config.collaboration = None
    episode = SimpleNamespace(task=SimpleNamespace(task_id='fixture'),config=config,output=tmp_path,
        input_mode='interactive',workflow=False,gateway=SimpleNamespace(transport=SimpleNamespace(mock=False),
            ledger=Ledger(Budget(None),Budget(None))),failure=None,design='saved',initial=None,
        final={'plan':'saved final design'},actor_calls=2,researcher=SimpleNamespace(questions=1),
        actor_status='completed',reproduction_command=None)
    (tmp_path/'final_design.json').write_text(json.dumps(episode.final))
    monkeypatch.setitem(sys.modules,'expbench.realistic_actor',SimpleNamespace(run_actor=lambda e:None))
    monkeypatch.setattr(realistic,'evaluate_design',lambda *a:pytest.fail('No judge during collection'))
    result = realistic.run_episode(episode)
    assert result['status'] == 'completed'
    assert result['final'] is None and result['final_submitted']
    assert result['evaluation']['status'] == 'grading_pending'
    assert (tmp_path/'final_design.json').exists()


def test_sciconv_collection_retains_final_specification_and_never_constructs_judge(monkeypatch, tmp_path):
    from personasciencebench import sciconv_runner as runner
    from personasciencebench.schema import Episode, PublicContext, ResearcherContext, Fact, Provenance, EvaluatorSpec
    from personasciencebench.packaging import export_episode, write_json
    episode = Episode(id='sciconvbench:fixture',benchmark='sciconvbench',source_task_id='fixture',
        study_id='fixture',domain='materials',source_revision='fixture',
        public=PublicContext(question='Public specification'),
        researcher=ResearcherContext(facts=[Fact(id='truth',topic='truth',text='Private full specification',
            source=Provenance(source_path='fixture',revision='fixture',locator='fixture'),review_status='reviewed')]),
        evaluator=EvaluatorSpec(kind='fixture',version='fixture'))
    record = export_episode(episode,tmp_path/'package')
    prepared = tmp_path/'prepared'
    write_json(prepared/'pilot_manifest.json',{'cases':[record],'source_root':'unused','source_manifest':'unused'})
    monkeypatch.setattr(runner,'load_adapter',lambda *a:SimpleNamespace(source=SimpleNamespace(repository=tmp_path)))
    monkeypatch.setattr(runner,'paper_module',lambda *a:SimpleNamespace())
    def preflight(models):
        assert set(models) == {'actor','researcher'}
        return {r:{'supported_parameters':[]} for r in models}
    monkeypatch.setattr(runner,'preflight',preflight)
    monkeypatch.setattr(runner,'OpenRouterClient',lambda **kw:SimpleNamespace())
    class Actor:
        def __init__(self,*a):pass
        def chat(self,current):return '[COMPLETE] Final specification'
    class User:
        def __init__(self,*a,**kw):Path(kw['log_file']).write_text('Saved conversation')
    def native(root,filename,name,service):
        if name == 'ConvAgent':return Actor
        if name == 'LLMUserInterface':return User
        pytest.fail('No native judge should be constructed during collection')
    monkeypatch.setattr(runner,'native_class',native)
    model = {'provider':'nvidia','model':GEMINI_MODEL,'reasoning_effort':'medium'}
    config = {'models':{'actor':model,'researcher':model,'judge':{'model':'gpt-6-astra','provider':'openai','reasoning_effort':'low'}},
              'collect_only':True,'persona':{'enabled':False}}
    output = tmp_path/'output'
    runner.run(prepared,output,config,1)
    result = json.loads((output/'results.json').read_text())[0]
    assert result['status'] == 'grading_pending'
    case = Path(result['case_directory'])
    assert (case/'generated_prompt.txt').read_text() == 'Final specification'
    assert (case/'controller/episode.private.json').is_file()
    assert (case/'controller/submission.json').is_file()
    assert (case/'TRACE.md').is_file()


def test_empty_length_repair_replays_identical_request_and_records_all_usage(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY', 'fixture')
    monkeypatch.setenv('PSB_NVIDIA_EMPTY_LENGTH_RETRIES', '2')
    client = OpenRouterClient(GEMINI_MODEL, role='actor', provider='nvidia', max_tokens=100)
    short = completion({'role':'assistant', 'reasoning_content':'private reasoning'})
    short['choices'][0]['finish_reason'] = 'length'
    received, records = [], []
    responses = iter([short, short, completion()])
    def respond(payload):
        received.append(json.loads(json.dumps(payload)))
        return next(responses)
    monkeypatch.setattr(client.nvidia, 'complete', respond)
    client.record = records.append
    assert client.complete([{'role':'user','content':'fixture'}]) == 'ok'
    assert len(records) == 3 and received[0] == received[1] == received[2]
    assert [r['response_repair']['retry_scheduled'] for r in records] == [True, True, False]
    assert sum(r['usage']['total_tokens'] for r in records) == 24


@pytest.mark.parametrize('finish,content,used,role,refusal', [
    ('content_filter', None, 3, 'actor', None),
    ('length', 'partial answer', 3, 'actor', None),
    ('length', None, 100, 'actor', None),
    ('length', None, 3, 'researcher', None),
    ('length', None, 3, 'actor', 'refused'),
])
def test_empty_length_repair_does_not_retry_other_outcomes(monkeypatch, finish, content, used, role, refusal):
    monkeypatch.setenv('PSB_NVIDIA_EMPTY_LENGTH_RETRIES', '2')
    transport = ChatTransport()
    data = completion({'role':'assistant', 'content':content, 'refusal':refusal})
    data['choices'][0]['finish_reason'] = finish
    data['usage']['completion_tokens'] = used
    calls, records = [], []
    monkeypatch.setattr(transport, 'complete', lambda p: calls.append(p) or data)
    assert transport.complete_recorded({'max_tokens':100}, lambda d,m: records.append((d,m)), role=role) == data
    assert len(calls) == len(records) == 1


def test_empty_length_repair_is_bounded_and_off_by_default(monkeypatch):
    transport = ChatTransport()
    data = completion({'role':'assistant'})
    data['choices'][0]['finish_reason'] = 'length'
    calls = []
    monkeypatch.setattr(transport, 'complete', lambda p: calls.append(p) or data)
    monkeypatch.delenv('PSB_NVIDIA_EMPTY_LENGTH_RETRIES', raising=False)
    transport.complete_recorded({'max_tokens':100}, lambda *a: None, role='actor')
    assert len(calls) == 1
    calls.clear()
    monkeypatch.setenv('PSB_NVIDIA_EMPTY_LENGTH_RETRIES', '2')
    transport.complete_recorded({'max_tokens':100}, lambda *a: None, role='actor')
    assert len(calls) == 3
