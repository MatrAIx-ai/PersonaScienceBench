"""Local OpenRouter-shaped compatibility layer that forwards to the NVIDIA inference gateway.

Derived from scripts/qwen_local_api.py in PersonaScienceBench (which only forwarded to a
localhost vLLM). Differences: upstream is the OpenAI-compatible gateway, upstream auth uses
GATEWAY_API_KEY, 429/5xx are retried with backoff honouring Retry-After, the catalog
served to /models is restricted to the configured role models with zero catalog prices
(the gateway publishes no per-token prices; cost accounting is therefore unavailable, not
zero-cost), and every request/response is logged without credentials.
"""
from contextlib import asynccontextmanager
import hmac
import os
import asyncio
import json
import time
import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

KEY = os.environ['PSB_LOCAL_API_KEY']                 # client-side key the benchmark presents
UPSTREAM_KEY = os.environ['GATEWAY_API_KEY']      # gateway key, never returned to clients
UPSTREAM = os.environ.get('NVGW_BASE_URL', '<OPENAI_COMPATIBLE_GATEWAY>').rstrip('/')
MODELS = [m for m in os.environ.get('NVGW_MODELS', '').split(',') if m]
PARAMETERS = ['tools', 'tool_choice', 'reasoning', 'structured_outputs',
              'response_format', 'temperature', 'top_p', 'max_tokens', 'seed',
              'stop', 'presence_penalty', 'frequency_penalty']
RETRY_STATUS = (408, 429, 500, 502, 503, 504)
ATTEMPTS = int(os.environ.get('NVGW_ATTEMPTS', '6'))
TOTAL_DEADLINE = float(os.environ.get('NVGW_TOTAL_DEADLINE', '3000'))


@asynccontextmanager
async def lifespan(app):
    app.state.slots = asyncio.Semaphore(int(os.environ.get('PSB_LOCAL_CONCURRENCY', '32')))
    async with httpx.AsyncClient(base_url=UPSTREAM, timeout=httpx.Timeout(float(os.environ.get('NVGW_UPSTREAM_TIMEOUT', '1800')), connect=15, pool=60),
            trust_env=False, headers={'Authorization': f'Bearer {UPSTREAM_KEY}'},
            limits=httpx.Limits(max_connections=128, max_keepalive_connections=64)) as client:
        app.state.upstream = client
        yield


app = FastAPI(lifespan=lifespan)


def record(data):
    if path := os.environ.get('PSB_LOCAL_REQUEST_LOG'):
        with Path(path).open('a') as f:
            f.write(json.dumps(data) + '\n')


def scrub(text):
    return (text or '').replace(UPSTREAM_KEY, '[REDACTED]')


async def forward(request, payload, request_id):
    json_note = payload.pop('_json_note_added', False)
    async with request.app.state.slots:
        for attempt in range(ATTEMPTS):
            start = time.monotonic()
            retry_after = None
            try:
                response = await request.app.state.upstream.post('/chat/completions', json=payload)
                try:
                    data = response.json()
                except ValueError:
                    data = {'error': {'message': scrub(response.text[:2000]), 'type': 'invalid_upstream_response'}}
                status = response.status_code
                retry_after = response.headers.get('retry-after')
            except httpx.TimeoutException:
                status, data = 504, {'error': {'message': 'Gateway inference timed out', 'type': 'upstream_timeout'}}
            except httpx.TransportError as exc:
                status, data = 502, {'error': {'message': type(exc).__name__, 'type': 'upstream_transport'}}
            err = data.get('error') if isinstance(data, dict) else None
            if isinstance(err, dict) and 'message' in err:
                err = {**err, 'message': scrub(str(err['message']))[:500]}
            record({'request_id': request_id, 'attempt': attempt + 1, 'status': status, 'model': payload.get('model'),
                    'elapsed_seconds': time.monotonic() - start, 'error': err,
                    'usage': data.get('usage') if isinstance(data, dict) else None, 'max_tokens': payload.get('max_tokens'), 'json_note_added': json_note})
            # Some GLM backend replicas intermittently reject reasoning_effort=medium with HTTP 400;
            # the same request succeeds on another replica, so treat that specific 400 as transient.
            transient_400 = status == 400 and isinstance(err, dict) and 'does not support reasoning effort' in str(err.get('message', ''))
            if (status not in RETRY_STATUS and not transient_400) or attempt == ATTEMPTS - 1:
                if status == 200:
                    data['provider'] = 'nvidia-inference-gateway'
                    data.setdefault('usage', {})
                    data['local_transport'] = {'request_id': request_id, 'retries': attempt}
                return JSONResponse(data, status_code=status)
            try:
                delay = float(retry_after) if retry_after else 0.0
            except ValueError:
                delay = 0.0
            await asyncio.sleep(max(delay, min(90, float(os.environ.get('PSB_LOCAL_RETRY_BACKOFF', '3')) * 2 ** attempt)))


async def wait_disconnect(request):
    while True:
        if (await request.receive())['type'] == 'http.disconnect':
            return


@app.middleware('http')
async def authenticate(request: Request, call_next):
    if not hmac.compare_digest(request.headers.get('authorization', ''), f'Bearer {KEY}'):
        return JSONResponse({'error': 'Unauthorized'}, status_code=401)
    return await call_next(request)


@app.get('/api/v1/key')
async def key_info():
    return {'data': {'label': 'nvidia-inference-gateway', 'is_free_tier': False, 'limit': None}}


@app.get('/api/v1/models')
async def models(request: Request):
    response = await request.app.state.upstream.get('/models')
    if response.status_code != 200:
        return JSONResponse({'error': 'Gateway catalog unavailable'}, status_code=503)
    data = response.json()
    entries = [m for m in data['data'] if not MODELS or m['id'] in MODELS]
    for model in entries:
        model.update(pricing={'prompt': '0', 'completion': '0'},
                     supported_parameters=PARAMETERS, deployment='nvidia-inference-gateway')
    return {'data': entries}


@app.post('/api/v1/chat/completions')
async def completion(request: Request):
    payload = await request.json()
    if payload.get('stream'):
        raise HTTPException(400, 'This compatibility endpoint supports non-streaming calls only')
    payload.pop('provider', None)          # OpenRouter routing/price constraints do not apply
    reasoning = payload.pop('reasoning', None)
    if reasoning:
        effort = reasoning.get('effort')
        if effort not in ('low', 'medium', 'high', 'xhigh'):
            raise HTTPException(400, 'Supported reasoning efforts: low, medium, high, xhigh')
        payload['reasoning_effort'] = effort
    if isinstance(payload.get('tool_choice'), dict):
        payload['parallel_tool_calls'] = False
    # Gateway compatibility: OpenAI-style JSON mode requires the literal word "json" somewhere in the
    # input messages; the benchmark's judge prompt omits it, so the gateway returned HTTP 400 for every
    # judge call. Append a neutral instruction only when JSON mode is requested and the word is absent.
    fmt = payload.get('response_format') or {}
    if isinstance(fmt, dict) and fmt.get('type') in ('json_object', 'json_schema'):
        msgs = payload.get('messages') or []
        def _text(c):
            if isinstance(c, str): return c
            if isinstance(c, list): return ' '.join(str(x.get('text', '')) for x in c if isinstance(x, dict))
            return ''
        # Only user-role messages count: the gateway maps system messages to Responses-API instructions.
        if not any('json' in _text(m.get('content')).lower() for m in msgs if isinstance(m, dict) and m.get('role') == 'user'):
            note = 'Respond in JSON.'
            # The gateway maps system messages to Responses-API instructions, which the check ignores,
            # so the note must go on the last user message.
            for m in reversed(msgs):
                if isinstance(m, dict) and m.get('role') == 'user':
                    if isinstance(m.get('content'), str): m['content'] = m['content'].rstrip() + '\n\n' + note
                    elif isinstance(m.get('content'), list): m['content'].append({'type': 'text', 'text': note})
                    break
            else:
                msgs.append({'role': 'user', 'content': note})
            payload['messages'] = msgs
            payload['_json_note_added'] = True
    request_id = uuid.uuid4().hex
    task = asyncio.create_task(forward(request, payload, request_id))
    disconnect = asyncio.create_task(wait_disconnect(request))
    try:
        done, _ = await asyncio.wait([task, disconnect], timeout=TOTAL_DEADLINE, return_when=asyncio.FIRST_COMPLETED)
        if task in done:
            return task.result()
        status = 499 if disconnect in done else 504
        record({'request_id': request_id, 'status': status, 'error': 'client_disconnected' if status == 499 else 'total_deadline'})
        return JSONResponse({'error': {'message': 'Client disconnected' if status == 499 else 'Request exceeded total deadline'}}, status_code=status)
    finally:
        task.cancel()
        disconnect.cancel()
        await asyncio.gather(task, disconnect, return_exceptions=True)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=int(os.environ.get('PSB_LOCAL_API_PORT', '8011')), log_level='warning')
