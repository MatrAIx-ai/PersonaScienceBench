"""Exercise concurrent reasoning/tool requests before resuming scientific episodes."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import time
import httpx

def one(i):
    # Repeated source material represents a moderate prompt, distinct per request.
    context=('The observations include noisy repeated measurements, a calibration control, '
             'three instrument batches, missing measurements, and independent biological samples. ')*180
    payload={'model':'qwen/qwen3.8-27b','messages':[{'role':'user','content':
        f'Study {i}. '+context+'Propose a concise experiment and analysis in 150 words. '
        'Call researcher_decision exactly once with your recommendation.'}],
        'reasoning':{'effort':'low'},'max_tokens':4096,
        'tools':[{'type':'function','function':{'name':'researcher_decision','parameters':{
            'type':'object','properties':{'recommendation':{'type':'string'}},
            'required':['recommendation'],'additionalProperties':False}}}],
        'tool_choice':{'type':'function','function':{'name':'researcher_decision'}}}
    start=time.monotonic()
    response=httpx.post(os.environ['OPENROUTER_BASE_URL']+'/chat/completions',json=payload,
        headers={'Authorization':'Bearer '+os.environ['PSB_LOCAL_API_KEY']},timeout=1900,trust_env=False)
    response.raise_for_status()
    data=response.json();choice=data['choices'][0]
    assert choice['finish_reason'] not in ('length','error','content_filter'), choice['finish_reason']
    calls=choice['message'].get('tool_calls') or []
    assert len(calls)==1 and calls[0]['function']['name']=='researcher_decision', 'Invalid single-tool response'
    assert isinstance(json.loads(calls[0]['function']['arguments'])['recommendation'],str)
    return {'request':i,'elapsed_seconds':time.monotonic()-start,'usage':data['usage'],
            'transport':data.get('local_transport')}

if __name__=='__main__':
    start=time.monotonic()
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows=list(pool.map(one,range(8)))
    result={'requests':rows,'wall_seconds':time.monotonic()-start,'passed':max(r['elapsed_seconds'] for r in rows)<600,
            'note':'Synthetic concurrent API validation; excluded from benchmark results.'}
    Path(os.environ['VLLM_RUN_DIR'],'load_check.json').write_text(json.dumps(result,indent=2)+'\n')
    assert max(r['elapsed_seconds'] for r in rows)<600, 'Concurrent validation exceeded latency gate; benchmark not started'
    print(f"Concurrent local API validation passed: 8 requests in {result['wall_seconds']:.1f}s",flush=True)
