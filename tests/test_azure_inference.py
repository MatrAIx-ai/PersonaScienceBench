"""Azure transport contract checks; no live credentials or model calls."""
import json
from types import SimpleNamespace

import pytest
import httpx

from personasciencebench.inference import AzureOpenAIClient, OpenRouterClient, azure_base_url, load_env, model_client, preflight


@pytest.fixture
def azure(monkeypatch):
    monkeypatch.setenv('AZURE_OPENAI_API_KEY', 'UNIT_TEST_AZURE_KEY')
    monkeypatch.setenv('AZURE_OPENAI_ENDPOINT', 'https://example.services.ai.azure.com/openai/v1/')
    calls = []
    def post(url, **kwargs):
        calls.append({'url': url, **kwargs})
        return SimpleNamespace(status_code=200, json=lambda: {
            'model': 'resolved-deployment', 'usage': {'prompt_tokens': 2, 'completion_tokens': 3},
            'choices': [{'finish_reason': 'stop', 'message': {'content': '{"ready":true}'}}]})
    monkeypatch.setattr(httpx, 'post', post)
    return calls


def test_native_settings_preserved_and_credentials_not_recorded(azure):
    records = []
    client = model_client(provider='azure', model='custom-deployment', role='judge', reasoning_effort='none', record=records.append)
    native = {'temperature': 0, 'max_tokens': 250, 'top_p': 1, 'frequency_penalty': 0, 'presence_penalty': 0}
    client.complete([{'role': 'user', 'content': 'Return JSON.'}], json_mode=True, settings=native)
    request = azure[0]
    assert request['url'].endswith('/openai/v1/chat/completions')
    assert request['headers'] == {'api-key': 'UNIT_TEST_AZURE_KEY'}
    payload = request['json']
    assert payload['model'] == 'custom-deployment'
    assert payload['max_completion_tokens'] == 250
    assert all(payload[k] == v for k, v in native.items() if k != 'max_tokens')
    assert payload['reasoning_effort'] == 'none'
    assert 'provider' not in payload and 'reasoning' not in payload and 'max_tokens' not in payload
    assert records[0]['requested_native_settings'] == native
    assert records[0]['omitted_native_settings'] == {}
    assert records[0]['transport_provider'] == 'Azure OpenAI'
    assert 'UNIT_TEST_AZURE_KEY' not in json.dumps(records)


@pytest.mark.parametrize('endpoint', [
    'https://example.services.ai.azure.com/api/projects/project',
    'http://example.services.ai.azure.com/openai/v1',
    'https://example.com/openai/v1',
    'https://user:password@example.services.ai.azure.com/openai/v1',
])
def test_bad_endpoint_rejected_before_request(azure, monkeypatch, endpoint):
    monkeypatch.setenv('AZURE_OPENAI_ENDPOINT', endpoint)
    with pytest.raises(ValueError, match='AZURE_OPENAI_ENDPOINT'):
        AzureOpenAIClient('deployment', role='actor').complete([])
    assert azure == []


def test_preflight_does_not_confuse_model_catalog_with_deployments(azure, monkeypatch):
    monkeypatch.setattr(httpx, 'get', lambda *a, **k: SimpleNamespace(status_code=200, json=lambda: {'data': [{'id': 'base-model'}]}))
    result = preflight({'actor': {'provider': 'azure', 'model': 'custom-deployment'}})
    assert result['actor']['id'] == 'custom-deployment'
    assert result['actor']['deployment_verified'] is False
    assert result['actor']['supported_parameters'] is None
    assert azure == []


def test_env_allowlist_and_existing_exports(tmp_path, monkeypatch):
    monkeypatch.setenv('AZURE_OPENAI_API_KEY', 'EXPORTED_TEST_KEY')
    monkeypatch.delenv('AZURE_OPENAI_DEPLOYMENT', raising=False)
    monkeypatch.delenv('UNRELATED_TEST_VARIABLE', raising=False)
    path = tmp_path / '.env'
    path.write_text('AZURE_OPENAI_API_KEY=FILE_TEST_KEY\nAZURE_OPENAI_DEPLOYMENT="deployment"\nUNRELATED_TEST_VARIABLE=ignored\n')
    load_env(path)
    import os
    assert os.environ['AZURE_OPENAI_API_KEY'] == 'EXPORTED_TEST_KEY'
    assert os.environ['AZURE_OPENAI_DEPLOYMENT'] == 'deployment'
    assert 'UNRELATED_TEST_VARIABLE' not in os.environ


def test_default_provider_unchanged():
    assert type(model_client(model='model', role='actor')) is OpenRouterClient
    with pytest.raises(ValueError, match='Unknown model provider'):
        model_client(provider='typo', model='model', role='actor')
