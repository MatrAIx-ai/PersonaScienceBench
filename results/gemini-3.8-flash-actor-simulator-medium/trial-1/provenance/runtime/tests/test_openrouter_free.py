from types import SimpleNamespace
import pytest
from expbench.schema import ModelSettings
from personasciencebench import openrouter_pacing as pacing


def test_zero_prices_valid_negative_rejected():
    ModelSettings(model='qwen/qwen3.8-27b:free', max_output_tokens=4096,
                  input_usd_per_million=0, output_usd_per_million=0)
    with pytest.raises(ValueError):
        ModelSettings(model='x', max_output_tokens=4096,
                      input_usd_per_million=-1, output_usd_per_million=0)


def test_paid_requests_not_throttled(monkeypatch):
    monkeypatch.setenv('PSB_OPENROUTER_RATE_DIR', '/unused')
    monkeypatch.setattr(pacing, '_acquire', lambda: pytest.fail('paid path paced'))
    sentinel = object()
    assert pacing.paced_post(lambda: sentinel, {'model':'deepseek/deepseek-v4.1-flash'}) is sentinel


def test_daily_quota_stops_without_retry(monkeypatch, tmp_path):
    monkeypatch.setenv('PSB_OPENROUTER_RATE_DIR', str(tmp_path))
    monkeypatch.setenv('PSB_FATAL_API_FILE', str(tmp_path/'fatal.json'))
    monkeypatch.setattr(pacing, '_acquire', lambda: None)
    calls=[]
    response=SimpleNamespace(status_code=429, headers={},json=lambda:{'error':{'message':'Daily free model limit reached'}})
    def send():calls.append(1);return response
    assert pacing.paced_post(send, {'model':'x:free'}) is response
    assert len(calls)==1 and (tmp_path/'fatal.json').exists()


def test_transient_limit_honors_retry_after(monkeypatch, tmp_path):
    monkeypatch.setenv('PSB_OPENROUTER_RATE_DIR', str(tmp_path))
    monkeypatch.setattr(pacing, '_acquire', lambda: None)
    delays=[];monkeypatch.setattr(pacing, '_cooldown', delays.append)
    replies=iter([SimpleNamespace(status_code=429,headers={'retry-after':'17'},json=lambda:{'error':{'message':'Too many requests'}}),SimpleNamespace(status_code=200)])
    assert pacing.paced_post(lambda:next(replies),{'model':'x:free'}).status_code==200
    assert delays==[17]


def test_zero_price_catalog_preflight_and_charge(tmp_path):
    import httpx
    from expbench.gateway import OpenRouterTransport, Gateway
    from expbench.budget import Budget, Ledger
    spec=ModelSettings(model='qwen/qwen3.8-27b:free',max_output_tokens=4096,
                       input_usd_per_million=0,output_usd_per_million=0)
    def handler(req):
        if req.url.path.endswith('/key'):return httpx.Response(200,json={'data':{}})
        if req.url.path.endswith('/models'):
            return httpx.Response(200,json={'data':[{'id':spec.model,'pricing':{'prompt':'0','completion':'0'},'supported_parameters':['tools','structured_outputs']}]})
        return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':'{}'}}], 'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':0}})
    transport=OpenRouterTransport('nonsecret-test-key',10);transport.client.close()
    transport.client=httpx.Client(base_url='https://openrouter.ai/api/v1',transport=httpx.MockTransport(handler))
    models={r:spec for r in ['actor','researcher','judge']}
    try:
        assert len(transport.preflight(models,enforce_price_caps=False))==3
        ledger=Ledger(Budget(None),Budget(None));gateway=Gateway(transport,models,ledger,tmp_path/'calls.jsonl')
        gateway.complete('judge',[{'role':'user','content':'test'}])
        assert ledger.run.charged==0
    finally:transport.close()
