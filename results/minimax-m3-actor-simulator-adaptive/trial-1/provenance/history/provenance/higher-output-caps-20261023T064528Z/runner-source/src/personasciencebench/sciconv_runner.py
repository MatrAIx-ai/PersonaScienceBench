"""Native SciConv dialogue/judges with an injected, fully recorded model service."""
import argparse,ast,dataclasses,importlib.util,json,os,re,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from types import SimpleNamespace
from typing import Any,Dict,List
from personasciencebench.inference import OpenRouterClient,load_env,preflight
from personasciencebench.collection import active_models,pending_evaluation
from personasciencebench.packaging import safe_component,write_json
from personasciencebench.registry import load_adapter,project_root
from personasciencebench.persona import resolve_persona,persona_record,render_persona
from personasciencebench.adapters.sciconvbench import POLICY
from personasciencebench.collaboration import replace_once

USER_PROMPT_POLICY='sciconv-user-prompt-v2'
# Edits to the native simulated-user prompt, grouped by the one switch that owns each.
KNOWLEDGE_EDITS=[("should answer based strictly on that.","may also use your general knowledge."),
    ("3. If the complete requirement doesn't specify something, tell the agent: \"Make a reasonable assumption based on best practices.\"",
     '3. You may offer your own suggestions; distinguish them from stated task requirements.')]
STYLE_EDITS=[("- Be concise.","- Respond naturally as the supplied identity, if any."),("- Do not explain your reasoning.","")]
DISCLOSURE_EDITS=[("- Do not provide information not asked for.","")]
TRUTH_EDITS=[("- Answer like a human user would.","- Answer like a human user would.\n        - What you say about this conversation must be true: never claim you already told the agent something that is not in the incomplete requirement or in your earlier answers.")]
# The native instruction for unspecified details, returned verbatim by the floor ('mute') researcher.
MUTE_REPLY="Make a reasonable assumption based on best practices."
# Mirrors the core researcher's knowledge boundary: persona text never adds task facts.
PERSONA_BOUNDARY=("\n\nIDENTITY. The identity below sets how you communicate. It does not change the task: "
    "values you give as requirements come only from the COMPLETE requirement.\n")

def researcher_system_prompt(native,*,unrestricted_knowledge=False,embody_identity=False,volunteer_information=False,truthful_history=False,persona_text=''):
    """Native SciConv user system prompt plus the configured edits; the identity only when a persona is on.
    Edits apply in every arm, so persona and control differ only by the identity text."""
    edits=(KNOWLEDGE_EDITS if unrestricted_knowledge else [])+(STYLE_EDITS if embody_identity else [])+(DISCLOSURE_EDITS if volunteer_information else [])+(TRUTH_EDITS if truthful_history else [])
    for old,new in edits:native=replace_once(native,old,new)
    return native+(PERSONA_BOUNDARY+persona_text if persona_text else '')

class Service:
    def __init__(self,client,persona_text='',prompt_options=None):
        self.client=client;self.persona_text=persona_text;self.prompt_options=prompt_options or {};self.scripted_reply=None
        self.stats={k:0 for k in ['prompt_tokens','completion_tokens','total_tokens','total_calls','failed_calls','total_retries']}
    def script(self,reply):
        self.scripted_reply=reply;self.stats['scripted_replies']=0
    def invoke(self,user_prompt,system_prompt):
        if self.scripted_reply is not None:
            self.stats['scripted_replies']+=1;return self.scripted_reply
        self.stats['total_calls']+=1
        # The native user class swallows every exception into a canned reply, so a failed prompt edit must be
        # counted here, where the runner's failed_calls check sees it.
        try:
            if self.prompt_options or self.persona_text:
                system_prompt=researcher_system_prompt(system_prompt,persona_text=self.persona_text,**self.prompt_options)
            r=self.client.completion([{'role':'system','content':system_prompt},{'role':'user','content':user_prompt}])
        except Exception:
            self.stats['failed_calls']+=1;raise
        for key in ('prompt_tokens','completion_tokens','total_tokens'):self.stats[key]+=r.get('usage',{}).get(key,0)
        return r['choices'][0]['message']['content']
    def get_statistics(self):return dict(self.stats)

def native_class(root,filename,name,service):
    source=(root/filename).read_text();tree=ast.parse(source)
    nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==name]
    if len(nodes)!=1:raise ValueError('Native class structure changed')
    scope={'__name__':__name__,'Config':SimpleNamespace,'LLMService':lambda config:service,'json':json,'re':re,'os':os,'time':time,'Dict':Dict,'List':List,'Any':Any,'dataclass':dataclasses.dataclass,'field':dataclasses.field}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(root/filename),'exec'),scope)
    return scope[name]

def paper_module(root):
    spec=importlib.util.spec_from_file_location('psb_sciconv_native_metrics',root/'make_paper_artifacts.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def grade_saved_dialogue(ep, final, case, config, service, repository, limit_reached):
    """Apply the native judges/scorer to an existing dialogue; never run an actor."""
    native=paper_module(repository)
    row=ep.evaluator.reference['native_row'];mode=ep.evaluator.reference['mode'];domain=ep.evaluator.reference['domain'];truth=ep.researcher.facts[0].text
    issues=row['missing_entities' if mode=='disambiguation' else 'inconsistencies']
    name='Disambiguation' if mode=='disambiguation' else 'Inconsistency'
    judge=native_class(repository,f'llm_judge_{mode}.py','LLMJudge'+name,service)()
    grading=judge.evaluate(truth,final,issues) if mode=='disambiguation' else judge.evaluate(final,issues,ep.public.question,truth)
    recovered=None
    if mode=='disambiguation':
        a,b=map(int,grading['score'].split('/'));grading['strict_score']='1/1' if a==b and b>0 else '0/1'
        grading['partial_score']=f'{a}/{b}';recovered=a/b if b else None
    else:grading['strict_score']=grading.get('score','0/1')
    Chat=native_class(repository,f'llm_judge_{mode}_chat.py','LLMJudge'+name+'Chat',service);chat=Chat()
    parsed=chat.parse_conversation_log((case/'conversation_log.txt').read_text())
    chat_result=chat.evaluate(parsed,issues,final)
    chat_result['total_questions_asked_in_chat']=len(parsed)
    chat_result['total_missing_entities' if mode=='disambiguation' else 'total_planted_inconsistencies']=len(issues)
    intent=native_class(repository,'llm_judge_intent.py','LLMJudgeIntent',service)().evaluate(final,truth)
    for suffix,value in [(mode,grading),(mode+'_chat',chat_result),('intent',intent)]:write_json(case/f'llm_judge_{suffix}_score.json',value)
    if any('parsing failed' in json.dumps(v).lower() or 'could not parse' in json.dumps(v).lower() for v in [grading,chat_result,intent]):raise ValueError('Native judge output parsing failed; retained raw judgement')
    scorer=native._score_disambiguation if mode=='disambiguation' else native._score_inconsistency
    native_case=scorer(case,len(ep.public.question),domain,config['models']['actor']['model'],row['id'],row)
    fr=int(native_case.FR and native_case.IC);ground=int(native_case.grounded and native_case.IC)
    # FR before the intent gate and the recovered share keep fact recovery separable from the intent judge.
    metrics={'FRR':fr,'FR':int(native_case.FR),'entity_recovery':recovered,'question_limit_reached':int(limit_reached),'CGRR':fr*ground,'SRR':fr*(1-ground),'intent_capture':native_case.IC,'clarification_recall':chat_result.get('questions_about_missing_entities' if mode=='disambiguation' else 'questions_about_inconsistencies',{}).get('count',0)/len(issues),'clarification_precision':chat_result.get('relevant_questions',{}).get('count',0)/len(parsed) if parsed else 0.0,'native_paper_CR':native_case.CR,'native_paper_CP':native_case.CP,'memory_consistency':native_case.MC}
    evaluation={'status':'scored','evaluator_version':POLICY+'+native-judge','metrics':metrics,'details':{'judge_model':config['models']['judge']['model'],'judge_provider':config['models']['judge'].get('provider','openrouter'),'judge_reasoning_effort':config['models']['judge'].get('reasoning_effort'),'native_case':dataclasses.asdict(native_case),'native_silent_resolution_correction':True,'clarification_ratio_policy':'native case scripts: covered issues / total issues; relevant questions / all questions; paper aggregator values also retained','score_scope':'specification and conversation; no scientific solver execution'}}
    if service.stats['failed_calls']:
        raise ValueError('Native judge service failed; do not convert fallback output to a score')
    return evaluation, len(parsed)

def run(prepared,output,config,parallel):
    manifest=json.loads((prepared/'pilot_manifest.json').read_text());records=manifest['cases']
    adapter=load_adapter('sciconvbench',Path(manifest['source_root']),Path(manifest['source_manifest']))
    native=paper_module(adapter.source.repository)
    models=active_models(config['models'],config.get('collect_only',False))
    catalog=preflight(models);output.mkdir(parents=True,exist_ok=False);output.chmod(0o700)
    write_json(output/'config.json',config);write_json(output/'api_preflight.json',catalog)
    def one(record):
        from personasciencebench.schema import Episode
        ep=Episode.model_validate_json((Path(record['package'])/'controller/episode.private.json').read_text())
        case=output/safe_component(ep.id);case.mkdir(mode=0o700);controller=case/'controller';controller.mkdir()
        write_json(controller/'episode.private.json',ep.model_dump(mode='json'));write_json(controller/'public_input.json',ep.actor_input())
        profile=resolve_persona(config,ep);write_json(controller/'persona.private.json',persona_record(profile))
        events=[]
        def event(kind,payload):
            data={'sequence':len(events),'type':kind,'time':time.time(),'payload':payload};events.append(data)
            with (controller/'events.jsonl').open('a') as f:f.write(json.dumps(data)+'\n')
        def log(call):
            with (controller/'api_calls.private.jsonl').open('a') as f:f.write(json.dumps(call)+'\n')
        services={r:Service(OpenRouterClient(**c,role=r,record=log,supported_parameters=catalog[r]['supported_parameters'])) for r,c in models.items()}
        collab=config.get('collaboration') or {}
        prompt_options={k:bool(collab.get(k,False)) for k in ('unrestricted_knowledge','embody_identity','volunteer_information','truthful_history')}
        services['researcher'].prompt_options=prompt_options
        if profile.enabled:services['researcher'].persona_text=render_persona(profile)
        policy=collab.get('researcher_policy','llm')
        if policy=='mute':services['researcher'].script(MUTE_REPLY)
        result={'episode_id':ep.id,'benchmark':'sciconvbench','source_task_id':ep.source_task_id,'status':'infrastructure_error','case_directory':str(case.resolve()),'interaction_protocol':POLICY,'user_prompt_policy':USER_PROMPT_POLICY,'user_prompt_options':prompt_options,'researcher_policy':policy,'framework':'native ConvAgent'}
        try:
            Actor=native_class(adapter.source.repository,'main.py','ConvAgent',services['actor'])
            User=native_class(adapter.source.repository,'llm_user_interface.py','LLMUserInterface',services['researcher'])
            actor=Actor(SimpleNamespace());user=User(services['researcher'],ep.public.question,ep.researcher.facts[0].text,log_file=str(case/'conversation_log.txt'))
            # The oracle agent starts from the complete requirement; the user still holds the native incomplete/complete pair.
            current=ep.researcher.facts[0].text if policy=='oracle' else ep.public.question;final=None;limit_reached=False
            event('initial_request',{'message':current})
            for turn in range(10):
                answer=actor.chat(current)
                if '[COMPLETE]' in answer:
                    final=answer.replace('[COMPLETE]','').strip();break
                event('researcher_question',{'question':answer})
                current=user.answer_clarification_question(answer)
                event('researcher_reply',{'answer':current})
                if services['researcher'].stats['failed_calls']:raise RuntimeError('Native researcher model call failed')
            if final is None:final=actor.get_final_attempt();limit_reached=True
            if services['actor'].stats['failed_calls']:raise RuntimeError('Native actor model call failed')
            event('final_specification',{'answer':final})
            (case/'generated_prompt.txt').write_text(final)
            write_json(controller/'submission.json',{'episode_id':ep.id,'stage':'final','answer':final,'artifacts':{},'payload':{}})
            if config.get('collect_only',False):
                evaluation=pending_evaluation(config['models']['judge'])
                write_json(case/'evaluation.json',evaluation)
                result.update(status='grading_pending',evaluation=evaluation,actor_calls=services['actor'].stats['total_calls'],question_limit_reached=limit_reached)
            else:
                evaluation,question_count=grade_saved_dialogue(ep,final,case,config,services['judge'],adapter.source.repository,limit_reached)
                write_json(case/'evaluation.json',evaluation);result.update(status='scored',evaluation=evaluation,researcher_questions=question_count,actor_calls=services['actor'].stats['total_calls'])
        except Exception as exc:result.update(error_type=type(exc).__name__,error=str(exc))
        result['researcher_questions']=sum(e['type']=='researcher_question' for e in events)
        if 'scripted_replies' in services['researcher'].stats:result['scripted_replies']=services['researcher'].stats['scripted_replies']
        write_json(case/'result.json',result)
        lines=['# SciConvBench interaction trace','',f"Task: {ep.source_task_id}",'',f"Status: {result['status']}",'']
        for e in events:
            lines.extend([f"## {e['sequence']+1}. {e['type']}",'',next(iter(e['payload'].values())),''])
        lines+=['## Evaluation','', '```json',json.dumps(result.get('evaluation',result),indent=2),'```']
        (case/'TRACE.md').write_text('\n'.join(lines))
        return result
    results=[]
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        for f in as_completed([pool.submit(one,r) for r in records]):results.append(f.result());write_json(output/'results.json',results)
    write_json(output/'summary.json',{'cases':results,'requested':len(records),'scored':sum(r['status']=='scored' for r in results)})
    (output/'TRACE_INDEX.md').write_text('# SciConvBench traces\n\n'+'\n'.join(f"- [{r['source_task_id']}]({Path(r['case_directory']).name}/TRACE.md) — {r['status']}" for r in results)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--parallel',type=int,default=2);a=p.parse_args()
    load_env(project_root()/'.env');run(a.prepared,a.output,json.loads(a.config.read_text()),a.parallel)
if __name__=='__main__':main()
