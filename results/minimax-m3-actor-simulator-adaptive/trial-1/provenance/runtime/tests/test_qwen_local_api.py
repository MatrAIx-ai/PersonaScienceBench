"""Server-side compatibility checks; no model inference or external requests."""
import importlib.util
import os
from pathlib import Path
import unittest
import asyncio
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

os.environ['PSB_LOCAL_API_KEY'] = 'local-test-key'
spec = importlib.util.spec_from_file_location('qwen_local_api', Path(__file__).resolve().parents[1] / 'scripts/qwen_local_api.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LocalAPITest(unittest.TestCase):
    def test_timeout_recovery_and_nonretryable_error_body(self):
        calls=[]
        def upstream(request):
            calls.append(request)
            if len(calls)==1:
                raise httpx.ReadTimeout('timed out', request=request)
            return httpx.Response(200, json={'choices': [], 'usage': {}})
        with TestClient(module.app) as client:
            module.app.state.upstream=httpx.AsyncClient(base_url=module.UPSTREAM,transport=httpx.MockTransport(upstream))
            os.environ['PSB_LOCAL_RETRY_BACKOFF']='0'
            headers={'Authorization':'Bearer local-test-key'}
            response=client.post('/api/v1/chat/completions',headers=headers,json={'messages':[]})
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['local_transport']['retries'],1)
            self.assertEqual(len(calls),2)
            calls.clear()
            def rejected(request):
                calls.append(request)
                return httpx.Response(400,json={'error':{'message':'Context too long'}})
            module.app.state.upstream=httpx.AsyncClient(base_url=module.UPSTREAM,transport=httpx.MockTransport(rejected))
            response=client.post('/api/v1/chat/completions',headers=headers,json={'messages':[]})
            self.assertEqual(response.status_code,400)
            self.assertEqual(response.json()['error']['message'],'Context too long')
            self.assertEqual(len(calls),1)
            calls.clear()
            def timeout(request):
                calls.append(request)
                raise httpx.ReadTimeout('timed out',request=request)
            module.app.state.upstream=httpx.AsyncClient(base_url=module.UPSTREAM,transport=httpx.MockTransport(timeout))
            response=client.post('/api/v1/chat/completions',headers=headers,json={'messages':[]})
            self.assertEqual(response.status_code,504)
            self.assertEqual(len(calls),3)

    def test_auth_catalog_and_forwarding(self):
        captured = []
        def upstream(request):
            import json
            if request.url.path.endswith('/models'):
                return httpx.Response(200, json={'data': [{'id': 'qwen/qwen3.8-27b'}]})
            captured.append(json.loads(request.content))
            return httpx.Response(200, json={'choices': [], 'usage': {'completion_tokens': 5}})
        with TestClient(module.app) as client:
            module.app.state.upstream = httpx.AsyncClient(base_url='http://127.0.0.1:8000/v1',
                transport=httpx.MockTransport(upstream))
            self.assertEqual(client.get('/api/v1/models').status_code, 401)
            headers = {'Authorization': 'Bearer local-test-key'}
            self.assertEqual(client.get('/api/v1/key', headers=headers).status_code, 200)
            model = client.get('/api/v1/models', headers=headers).json()['data'][0]
            self.assertEqual(model['pricing']['prompt'], '0')
            self.assertIn('structured_outputs', model['supported_parameters'])
            result = client.post('/api/v1/chat/completions', headers=headers,
                json={'model': model['id'], 'messages': [], 'provider': {'max_price': {}},
                      'reasoning': {'effort': 'low'}, 'max_tokens': 123})
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()['provider'], 'local-vllm')
            self.assertEqual(captured[0]['reasoning_effort'], 'low')
            self.assertNotIn('provider', captured[0])
            self.assertNotIn('reasoning', captured[0])
            self.assertEqual(captured[0]['max_tokens'], 123)
            invalid = client.post('/api/v1/chat/completions', headers=headers,
                json={'reasoning': {'effort': 'none'}})
            self.assertEqual(invalid.status_code, 400)


class CancellationTest(unittest.IsolatedAsyncioTestCase):
    async def test_concurrency_bound_and_cancellation(self):
        active=0
        peak=0
        async def send(request):
            nonlocal active, peak
            active+=1
            peak=max(peak,active)
            try:
                await asyncio.sleep(.03)
                return httpx.Response(200,json={'choices':[]})
            finally:
                active-=1
        async with httpx.AsyncClient(base_url=module.UPSTREAM,transport=httpx.MockTransport(send)) as upstream:
            request=SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(slots=asyncio.Semaphore(2),upstream=upstream)))
            await asyncio.gather(*(module.forward(request,{},str(i)) for i in range(6)))
            self.assertEqual(peak,2)
            task=asyncio.create_task(module.forward(request,{},'cancel'))
            await asyncio.sleep(.01)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):await task
            self.assertEqual(active,0)
            self.assertEqual(request.app.state.slots._value,2)

if __name__ == '__main__':
    unittest.main()
