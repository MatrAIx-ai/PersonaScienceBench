"""Direct OpenAI Responses API with a Chat-shaped boundary for existing runners."""
import os
import time
import random
from pathlib import Path
import json
import httpx


def preflight(models, timeout=45):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_API_KEY is not configured')
    for spec in models.values():
        if spec['model'].startswith('gpt-6-astra') and spec.get('reasoning_effort') == 'none':
            raise ValueError('GPT-6 Astra requires at least low reasoning')
    response = httpx.get('https://api.openai.com/v1/models', headers={'Authorization': 'Bearer '+key}, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f'OpenAI model access HTTP {response.status_code}')
    ids = {m['id'] for m in response.json()['data']}
    result = {}
    for role, spec in models.items():
        if spec['model'] not in ids:
            raise ValueError(f"Exact {role} model unavailable: {spec['model']}")
        result[role] = {'id': spec['model'], 'provider': 'openai', 'pricing': None,
                        'reasoning_effort': spec.get('reasoning_effort'),
                        'supported_parameters': ['max_tokens', 'tools', 'reasoning', 'structured_outputs']}
    return result


def response_content(content):
    """Translate native Chat text/image parts to Responses input parts."""
    if not isinstance(content, list):
        return content
    parts = []
    for part in content:
        if part.get('type') == 'text':
            parts.append({'type':'input_text', 'text':part['text']})
        elif part.get('type') == 'image_url':
            image = part['image_url']
            item = {'type':'input_image', 'image_url':image['url']}
            if image.get('detail') is not None:
                item['detail'] = image['detail']
            parts.append(item)
        else:
            raise ValueError('Unsupported Chat content part for Responses')
    return parts


class ResponsesTransport:
    def __init__(self, timeout=600):
        self.timeout = timeout
        self.history = {}

    def complete(self, payload):
        inputs = []
        restored = set()
        for m in payload['messages']:
            role = m['role']
            calls = m.get('tool_calls') or []
            if role == 'tool':
                inputs.append({'type': 'function_call_output', 'call_id': m['tool_call_id'], 'output': m.get('content') or ''})
            elif calls:
                key = calls[0]['id']
                if key in self.history:
                    if key not in restored:
                        inputs.extend(self.history[key]); restored.add(key)
                else:
                    if m.get('content'):
                        inputs.append({'role': role, 'content': response_content(m['content'])})
                    inputs.extend({'type': 'function_call', 'call_id': c['id'], 'name': c['function']['name'], 'arguments': c['function']['arguments']} for c in calls)
            elif m.get('content'):
                inputs.append({'role': role, 'content': response_content(m['content'])})
        request = {'model': payload['model'], 'input': inputs, 'store': False,
                   'include': ['reasoning.encrypted_content'], 'max_output_tokens': payload['max_tokens']}
        if payload.get('reasoning'):
            request['reasoning'] = payload['reasoning']
        if payload.get('tools'):
            request['tools'] = [{'type': 'function', **t['function'], 'strict': False} for t in payload['tools']]
        choice = payload.get('tool_choice')
        if choice is not None:
            request['tool_choice'] = {'type': 'function', 'name': choice['function']['name']} if isinstance(choice, dict) else choice
        fmt = payload.get('response_format')
        if fmt:
            request['text'] = {'format': ({'type': 'json_schema', **fmt['json_schema']} if fmt['type'] == 'json_schema' else fmt)}
        for name in ('temperature', 'top_p'):
            if name in payload:
                request[name] = payload[name]
        key = os.environ.get('OPENAI_API_KEY')
        if not key:
            raise ValueError('OPENAI_API_KEY is not configured')
        fatal = os.environ.get('PSB_FATAL_API_FILE')
        if fatal and Path(fatal).exists():
            raise RuntimeError('Run stopped after a fatal API configuration error; see fatal_api.json')
        for retry in range(6):
            response = httpx.post('https://api.openai.com/v1/responses', headers={'Authorization': 'Bearer '+key}, json=request, timeout=self.timeout)
            if response.status_code != 429 or retry == 5:
                break
            time.sleep(min(60, float(response.headers.get('retry-after', 2**retry))) + random.random())
        if response.status_code != 200:
            try:
                error = response.json().get('error', {})
                detail = {k: error.get(k) for k in ('type', 'code', 'param', 'message')}
            except ValueError:
                detail = {'message': 'Non-JSON API error'}
            # The request body and headers, especially credentials, never enter errors.
            detail = json.loads(json.dumps(detail).replace(key, '[REDACTED]'))
            if fatal and response.status_code in (400, 401, 403, 404):
                Path(fatal).write_text(json.dumps({'status': response.status_code, 'error': detail}, indent=2))
            raise RuntimeError(f'OpenAI HTTP {response.status_code}: {detail}')
        raw = response.json()
        if raw.get('status') != 'completed':
            raise RuntimeError(f"OpenAI response {raw.get('status')}: {raw.get('incomplete_details') or raw.get('error')}")
        output = raw.get('output', [])
        calls = [{'id': o['call_id'], 'type': 'function', 'function': {'name': o['name'], 'arguments': o['arguments']}} for o in output if o['type'] == 'function_call']
        content = ''.join(c.get('text', '') for o in output if o['type'] == 'message' for c in o['content'] if c['type'] == 'output_text')
        if calls:
            self.history[calls[0]['id']] = output
        u = raw.get('usage', {})
        usage = {'prompt_tokens': u.get('input_tokens', 0), 'completion_tokens': u.get('output_tokens', 0), 'total_tokens': u.get('total_tokens', 0), 'prompt_tokens_details': u.get('input_tokens_details', {}), 'completion_tokens_details': u.get('output_tokens_details', {})}
        message = {'role': 'assistant', 'content': content or None}
        if calls:
            message['tool_calls'] = calls
        return {'id': raw['id'], 'object': 'chat.completion', 'model': raw['model'], 'provider': 'openai',
                'choices': [{'index': 0, 'finish_reason': 'tool_calls' if calls else 'stop', 'message': message}],
                'usage': usage, '_responses_request': request, '_responses_response': raw, '_rate_limit_retries': retry}
