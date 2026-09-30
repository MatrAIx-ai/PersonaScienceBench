"""Direct OpenAI transport retries: bounded, recorded, identical requests; no live calls."""
from types import SimpleNamespace

import httpx
import pytest

from personasciencebench import openai_transport
from personasciencebench.openai_transport import ResponsesTransport

COMPLETED = {'id': 'resp_1', 'model': 'gpt-6-luna', 'status': 'completed',
             'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'done'}]}],
             'usage': {'input_tokens': 3, 'output_tokens': 1, 'total_tokens': 4}}
PAYLOAD = {'model': 'gpt-6-luna', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 16}


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'UNIT_TEST_KEY')
    monkeypatch.delenv('PSB_FATAL_API_FILE', raising=False)
    state = SimpleNamespace(statuses=[], requests=[], sleeps=[])
    monkeypatch.setattr(openai_transport.time, 'sleep', state.sleeps.append)

    def post(url, **kwargs):
        state.requests.append(kwargs['json'])
        status = state.statuses.pop(0)
        return SimpleNamespace(status_code=status, headers={'retry-after': '3'},
                               json=lambda: COMPLETED if status == 200 else {'error': {'type': 'server_error'}})
    monkeypatch.setattr(httpx, 'post', post)
    return state


@pytest.mark.parametrize('status', [429, 500, 502, 503, 504])
def test_transient_failures_are_retried_with_the_identical_request(provider, status):
    provider.statuses.extend([status, 200])
    result = ResponsesTransport().complete(PAYLOAD)
    assert result['choices'][0]['message']['content'] == 'done'
    assert result['_rate_limit_retries'] == 1 and len(provider.sleeps) == 1
    assert provider.requests[0] == provider.requests[1]


@pytest.mark.parametrize('status', [400, 401, 403, 404, 422])
def test_client_errors_fail_immediately(provider, status):
    provider.statuses.extend([status])
    with pytest.raises(RuntimeError, match=f'OpenAI HTTP {status}'):
        ResponsesTransport().complete(PAYLOAD)
    assert provider.sleeps == []


def test_retries_are_bounded(provider):
    provider.statuses.extend([503] * 6)
    with pytest.raises(RuntimeError, match='OpenAI HTTP 503'):
        ResponsesTransport().complete(PAYLOAD)
    assert len(provider.requests) == 6 and len(provider.sleeps) == 5
