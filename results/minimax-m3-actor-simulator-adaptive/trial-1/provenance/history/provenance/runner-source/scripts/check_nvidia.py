#!/usr/bin/env python3
"""Check NVIDIA model metadata; --live additionally makes small paid API probes."""
import argparse
import json
from pathlib import Path

from personasciencebench.inference import OpenRouterClient, load_env, preflight
from personasciencebench.nvidia_transport import GEMINI_MODEL


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    parser.add_argument('--model', default=GEMINI_MODEL)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    load_env(args.env_file)
    spec = {'provider':'nvidia', 'model':args.model, 'reasoning_effort':'medium'}
    evidence = {'catalog':preflight({'actor':spec, 'researcher':spec}), 'live_probes':[]}
    if args.live:
        calls = []
        client = OpenRouterClient(**spec, role='actor', max_tokens=2048, record=calls.append)
        tools = [{'type':'function', 'function':{'name':'echo', 'description':'Return the supplied value.',
                  'parameters':{'type':'object','properties':{'value':{'type':'string'}},
                                'required':['value'],'additionalProperties':False}}}]
        messages = [{'role':'user','content':'Call echo with value ok. After receiving the result, reply only ok.'}]
        first = client.completion(messages, tools=tools, tool_choice={'type':'function','function':{'name':'echo'}})
        message = first['choices'][0]['message']
        tool_calls = message.get('tool_calls', [])
        assert len(tool_calls) == 1 and tool_calls[0]['function']['name'] == 'echo'
        assert json.loads(tool_calls[0]['function']['arguments']) == {'value':'ok'}
        messages += [message, {'role':'tool','tool_call_id':tool_calls[0]['id'],'content':'ok'}]
        second = client.completion(messages, tools=tools, tool_choice='none')
        assert second['choices'][0]['message']['content'].strip().lower() == 'ok'
        decision = json.loads(client.complete_decision(
            [{'role':'user','content':'Return a decision with action approve.'}],
            {'type':'object','properties':{'action':{'type':'string','enum':['approve']}},
             'required':['action'],'additionalProperties':False}))
        assert decision == {'action':'approve'}
        value = json.loads(client.complete([{'role':'user','content':'Return JSON with status equal to ok.'}], json_mode=True))
        assert value == {'status':'ok'}
        evidence['live_probes'] = [{'request':c['request'], 'response':c['response'], 'usage':c['usage']}
                                   for c in calls]
        evidence['verified'] = ['explicit_medium_accepted', 'forced_tools', 'tool_result_continuation',
                                'typed_researcher_decision', 'json_object', 'token_usage']
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + '\n')
        args.output.chmod(0o600)
    print(json.dumps({'model':args.model, 'checks':evidence.get('verified', ['catalog']),
                      'paid_calls':len(evidence['live_probes']), 'output':str(args.output) if args.output else None}))


if __name__ == '__main__':
    main()
