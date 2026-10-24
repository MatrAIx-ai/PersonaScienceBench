"""Local server-side compatibility layer for existing OpenRouter-shaped calls.

Only localhost vLLM is reachable upstream. No external-provider forwarding.
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

KEY = os.environ['PSB_LOCAL_API_KEY']
UPSTREAM = f"http://127.0.0.1:{int(os.environ.get('VLLM_PORT', '8000'))}/v1"
PARAMETERS = ['tools', 'tool_choice', 'reasoning', 'structured_outputs',
              'response_format', 'temperature', 'top_p', 'max_tokens', 'seed',
              'stop', 'presence_penalty', 'frequency_penalty']


@asynccontextmanager
async def lifespan(app):
    app.state.slots = asyncio.Semaphore(int(os.environ.get('PSB_LOCAL_CONCURRENCY', '8')))
    async with httpx.AsyncClient(base_url=UPSTREAM, timeout=httpx.Timeout(800, connect=10, pool=30), trust_env=False,
            headers={'Authorization': f'Bearer {KEY}'},
            limits=httpx.Limits(max_connections=64, max_keepalive_connections=32)) as client:
        app.state.upstream = client
        yield


app = FastAPI(lifespan=lifespan)


def record(data):
    if path := os.environ.get('PSB_LOCAL_REQUEST_LOG'):
        with Path(path).open('a') as f:
            f.write(json.dumps(data) + '\n')


async def forward(request, payload, request_id):
    """Bound queue + retries; do not retry invalid requests or model outcomes."""
    async with request.app.state.slots:
        for attempt in range(3):
            start = time.monotonic()
            try:
                response = await request.app.state.upstream.post('/chat/completions', json=payload)
                try:
                    data = response.json()
                except ValueError:
                    data = {'error': {'message': response.text[:2000], 'type': 'invalid_upstream_response'}}
                status = response.status_code
            except httpx.TimeoutException:
                status, data = 504, {'error': {'message': 'Local inference timed out', 'type': 'upstream_timeout'}}
            except httpx.TransportError as exc:
                status, data = 502, {'error': {'message': type(exc).__name__, 'type': 'upstream_transport'}}
            record({'request_id': request_id, 'attempt': attempt+1, 'status': status,
                    'elapsed_seconds': time.monotonic()-start, 'error': data.get('error'),
                    'usage': data.get('usage'), 'max_tokens': payload.get('max_tokens')})
            if status not in (408, 429, 500, 502, 503, 504) or attempt == 2:
                if status == 200:
                    data['provider'] = 'local-vllm'
                    data.setdefault('usage', {})['cost'] = 0
                    data['local_transport'] = {'request_id': request_id, 'retries': attempt}
                return JSONResponse(data, status_code=status)
            await asyncio.sleep(float(os.environ.get('PSB_LOCAL_RETRY_BACKOFF', '2')) * 2**attempt)


async def wait_disconnect(request):
    # Body has already been read. Await ASGI disconnect directly so task
    # cancellation cannot be swallowed by is_disconnected's inner cancel scope.
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
    return {'data': {'label': 'local-vllm', 'is_free_tier': False, 'limit': None}}


@app.get('/api/v1/models')
async def models(request: Request):
    response = await request.app.state.upstream.get('/models')
    if response.status_code != 200:
        return JSONResponse({'error': 'Local vLLM is not ready'}, status_code=503)
    data = response.json()
    for model in data['data']:
        model.update(pricing={'prompt': '0', 'completion': '0'},
                     supported_parameters=PARAMETERS, deployment='local-vllm')
    return data


@app.post('/api/v1/chat/completions')
async def completion(request: Request):
    payload = await request.json()
    if payload.get('stream'):
        raise HTTPException(400, 'This compatibility endpoint supports non-streaming calls only')
    # Provider routing/price constraints are irrelevant to a single local model.
    payload.pop('provider', None)
    reasoning = payload.pop('reasoning', None)
    if reasoning:
        effort = reasoning.get('effort')
        if effort not in ('low', 'medium', 'xhigh'):
            raise HTTPException(400, 'Supported reasoning efforts: low, medium, xhigh')
        payload['reasoning_effort'] = effort
    if isinstance(payload.get('tool_choice'), dict):
        payload['parallel_tool_calls'] = False
    request_id = uuid.uuid4().hex
    task = asyncio.create_task(forward(request, payload, request_id))
    disconnect = asyncio.create_task(wait_disconnect(request))
    try:
        done, _ = await asyncio.wait([task, disconnect], timeout=1800, return_when=asyncio.FIRST_COMPLETED)
        if task in done:
            return task.result()
        status = 499 if disconnect in done else 504
        record({'request_id': request_id, 'status': status, 'error': 'client_disconnected' if status==499 else 'total_deadline'})
        return JSONResponse({'error': {'message': 'Client disconnected' if status==499 else 'Local request exceeded total deadline'}}, status_code=status)
    finally:
        task.cancel()
        disconnect.cancel()
        await asyncio.gather(task, disconnect, return_exceptions=True)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=int(os.environ.get('PSB_LOCAL_API_PORT', '8001')))
