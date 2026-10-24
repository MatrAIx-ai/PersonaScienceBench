"""Credential-free ASI sandbox requests served by the configured controller judge.

Only the evaluator subprocess installs the native LiteLLM boundary replacement.
The source checkout, scorer prompts, rubrics, parsers, and aggregation stay intact.
"""
import json
import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

BRIDGE_VERSION = 'asi-configured-judge-v1'
MAX_REQUEST_BYTES = 32 * 1024 * 1024
MAX_CALLS = 64


def atomic_json(path, value):
    tmp = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
    with tmp.open('x') as f:
        json.dump(value, f)
    tmp.replace(path)


def install_sandbox_bridge(directory):
    """Called before importing the native scoring entry point."""
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    import litellm
    from ai4sci_bench.scorers import _judge_common
    directory = Path(directory)
    config = json.loads((directory/'config.json').read_text())
    # Native result metadata must name the effective model too.
    def resolve(config_native):
        return _judge_common.ResolvedJudgeAPI(model=config['model'])
    _judge_common.resolve_judge_api = resolve
    # scorers/__init__.py eagerly imports both modules, so update their aliases.
    from ai4sci_bench.scorers import llm_judge, multimodal
    llm_judge.resolve_judge_api = resolve
    multimodal.resolve_judge_api = resolve

    def completion(*args, **kwargs):
        if args or kwargs.get('stream') or kwargs.get('tools'):
            raise ValueError('ASI judge bridge supports only non-streaming scoring messages')
        request_id = uuid4().hex
        request = {k:v for k,v in kwargs.items() if k not in ('api_key', 'api_base')}
        atomic_json(directory/f'{request_id}.request.json', request)
        output = directory/f'{request_id}.response.json'
        deadline = time.monotonic() + 900
        while not output.exists():
            if time.monotonic() >= deadline:
                raise TimeoutError('Configured controller judge did not respond within 900 seconds')
            time.sleep(0.1)
        result = json.loads(output.read_text())
        if 'error' in result:
            raise RuntimeError(result['error'])
        return litellm.ModelResponse(**result['response'])
    litellm.completion = completion


def validate_request(request):
    messages = request.get('messages')
    if not isinstance(messages, list) or not messages or len(messages) > 32:
        raise ValueError('ASI judge requires a bounded message list')
    for message in messages:
        if message.get('role') not in ('system', 'user', 'assistant'):
            raise ValueError('ASI judge message role is unsupported')
        content = message.get('content')
        if isinstance(content, str):
            continue
        if not isinstance(content, list):
            raise ValueError('ASI judge content must be text or text/image parts')
        for part in content:
            if part.get('type') == 'text' and isinstance(part.get('text'), str):
                continue
            if part.get('type') == 'image_url':
                url = part.get('image_url', {}).get('url', '')
                if isinstance(url, str) and url.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,', 'data:image/webp;base64,')):
                    continue
            raise ValueError('Only text and embedded images are accepted; remote URLs are forbidden')
    return messages


def execute_with_judge(sandbox, work, judge, timeout_seconds=1800):
    """Execute native scoring without giving sandboxed code credentials/network."""
    work = Path(work)
    directory = work/'judge_bridge'
    directory.mkdir()
    config = {'version':BRIDGE_VERSION, 'model':getattr(judge, 'model', None),
              'provider':getattr(judge, 'provider', None),
              'reasoning_effort':getattr(judge, 'reasoning_effort', None),
              'max_tokens':getattr(judge, 'max_tokens', None), 'max_calls':MAX_CALLS}
    atomic_json(directory/'config.json', config)
    processed = set()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(sandbox.execute, 'PYTHONPATH=/workspace python evaluate.py', timeout_seconds=timeout_seconds)
        while not future.done():
            for path in sorted(directory.glob('*.request.json')):
                if path.name in processed:
                    continue
                processed.add(path.name)
                response = path.with_name(path.name.replace('.request.json', '.response.json'))
                request = {}
                try:
                    if judge is None:
                        raise ValueError('Native ASI model judge requires an explicit configured judge')
                    if len(processed) > MAX_CALLS:
                        raise ValueError('ASI judge exceeded its bounded call allowance')
                    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
                    with os.fdopen(fd) as f:
                        if os.fstat(f.fileno()).st_size > MAX_REQUEST_BYTES:
                            raise ValueError('ASI judge request exceeds 32 MiB')
                        request = json.load(f)
                    messages = validate_request(request)
                    adaptation = {'bridge_version':BRIDGE_VERSION,
                        'requested_model':request.get('model'),
                        'requested_native_settings':{k:v for k,v in request.items() if k not in ('messages','model')},
                        'effective_judge':config,
                        'policy':'Use controller model, reasoning, and output budget; native sampling parameters omitted; prompts/rubrics unchanged.'}
                    with (directory/'adaptations.jsonl').open('a') as f:
                        f.write(json.dumps(adaptation)+'\n')
                    # The controller client logs the exact API request, response and usage.
                    data = judge.completion(messages)
                    atomic_json(response, {'response':{k:v for k,v in data.items() if not k.startswith('_')}})
                except Exception as exc:
                    error = f'{type(exc).__name__}: {exc}'
                    for key in ('OPENAI_API_KEY','OPENROUTER_API_KEY'):
                        secret = os.environ.get(key)
                        if secret:
                            error = error.replace(secret, '[REDACTED]')
                    atomic_json(response, {'error':error})
            time.sleep(0.1)
        return future.result(), config
