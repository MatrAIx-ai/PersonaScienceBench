"""Validate the local API, including a forced tool call, without a benchmark run."""
import json
import os
from pathlib import Path
import time

import httpx

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(os.environ.get('VLLM_RUN_DIR', ROOT / 'runs/vllm-qwen-server'))
meta = json.loads((RUN / 'server.json').read_text())
key = (ROOT / meta['key_file']).read_text().strip()
with httpx.Client(base_url=meta['base_url'], headers={'Authorization': f'Bearer {key}'},
                  timeout=180, trust_env=False) as client:
    response = client.get('/models')
    response.raise_for_status()
    assert meta['model'] in [m['id'] for m in response.json()['data']]
    records = []
    for tool_mode in (False, True):
        payload = dict(model=meta['model'], messages=[{'role': 'user', 'content':
            'Call record_result with value 42.' if tool_mode else 'Reply with the word ready.'}],
            max_tokens=1024, temperature=0, reasoning_effort='low')
        if tool_mode:
            payload.update(tools=[{'type': 'function', 'function': {'name': 'record_result',
                'description': 'Record a numeric result.', 'parameters': {'type': 'object',
                'properties': {'value': {'type': 'integer'}}, 'required': ['value'],
                'additionalProperties': False}}}],
                tool_choice={'type': 'function', 'function': {'name': 'record_result'}})
        start = time.monotonic()
        response = client.post('/chat/completions', json=payload)
        response.raise_for_status()
        body = response.json()
        message = body['choices'][0]['message']
        assert body['choices'][0]['finish_reason'] not in ('length', 'error'), body
        if tool_mode:
            call = message['tool_calls'][0]['function']
            assert call['name'] == 'record_result' and json.loads(call['arguments'])['value'] == 42
        else:
            assert message.get('content'), body
        records.append(dict(tool_mode=tool_mode, elapsed_seconds=time.monotonic()-start, response=body))
    start = time.monotonic()
    response = client.post('/chat/completions', json=dict(
        model=meta['model'], messages=[{'role': 'user', 'content': 'Return ready as true.'}],
        max_tokens=1024, temperature=0, reasoning_effort='low',
        response_format={'type': 'json_schema', 'json_schema': {'name': 'readiness',
            'strict': True, 'schema': {'type': 'object', 'properties': {'ready': {'type': 'boolean'}},
                                     'required': ['ready'], 'additionalProperties': False}}}))
    response.raise_for_status()
    body = response.json()
    assert json.loads(body['choices'][0]['message']['content']) == {'ready': True}, body
    records.append(dict(structured_output=True, elapsed_seconds=time.monotonic()-start, response=body))
(RUN / 'api_check.json').write_text(json.dumps(records, indent=2)+'\n')
meta['status'] = 'api_verified'
(RUN / 'server.json').write_text(json.dumps(meta, indent=2)+'\n')
print('Text, tool-call and JSON-schema API checks passed:', meta['base_url'])
