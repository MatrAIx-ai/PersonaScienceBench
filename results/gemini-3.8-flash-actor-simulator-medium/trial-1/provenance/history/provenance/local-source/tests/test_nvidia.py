"""Offline NVIDIA boundary and collection tests; no real API or actor execution."""
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import httpx
import pytest

from personasciencebench.inference import OpenRouterClient, load_env
from personasciencebench.nvidia_transport import ChatTransport, GEMINI_MODEL, preflight


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


def test_chat_wire_settings_and_secret_free_records(sdk):
    state, requests = sdk
    records = []
    client = OpenRouterClient(GEMINI_MODEL, role='actor', provider='nvidia',
                              reasoning_effort='medium', record=records.append)
    assert client.complete([{'role':'user','content':'test'}], json_mode=True) == 'ok'
    request = json.loads(requests[0].content)
    assert requests[0].url == 'https://inference-api.nvidia.com/v1/chat/completions'
    assert requests[0].headers['authorization'] == 'Bearer NVIDIA_TEST_SECRET'
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


def test_exp_gateway_records_actual_wire_request_and_token_cost(sdk, tmp_path):
    from expbench.gateway import Gateway, NVIDIATransport
    from expbench.schema import ModelSettings
    from expbench.budget import Ledger, Budget
    spec = ModelSettings(provider='nvidia', model=GEMINI_MODEL, reasoning_effort='medium',
                         max_output_tokens=512, input_usd_per_million=1, output_usd_per_million=2)
    ledger = Ledger(Budget(None), Budget(None))
    log = tmp_path/'api.jsonl'
    gateway = Gateway(NVIDIATransport('fixture',30), {'researcher':spec}, ledger, log)
    gateway.complete('researcher',[{'role':'user','content':'test'}],
                     schema={'type':'object','properties':{'status':{'type':'string'}}})
    wire = json.loads(sdk[1][0].content)
    assert wire['reasoning_effort'] == 'medium' and 'provider' not in wire
    assert wire['response_format']['type'] == 'json_schema'
    assert json.loads(log.read_text().splitlines()[0])['payload'] == wire
    assert ledger.episode.charged == pytest.approx(11/1_000_000)


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
