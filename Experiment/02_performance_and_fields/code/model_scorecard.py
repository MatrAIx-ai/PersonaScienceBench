"""Offline model scorecard on fixed five-setting common-question panels."""
from pathlib import Path
import sys,json,hashlib,ast
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from numba import njit
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/02_performance_and_fields';OUT=BASE/'data/model_scorecard'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import B,SEED,bootstrap_weights,write_json,write_csv,markdown_table
sys.path.insert(0,str(ROOT/'Experiment/09_offline_metric_suite/code'))
from word_repetition import tokenize,SEGMENTER
from self_repetition import messages
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
MODEL='GPT-6 Astra (low)'

def key(r):return r['source'],r['task_id'],r['arm'],r['trial']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def extract():
    snapshot=ROOT/'Experiment/09_offline_metric_suite/data/snapshot.json'
    snap=json.loads(snapshot.read_text())
    traces=[r for r in snap['traces'] if r['exclusion'] is None and r['arm'] in ARMS]
    scores={key(r):r for r in snap['scores'] if r['score'] is not None}
    recovery={key(r):r for r in snap['recovery'] if r['recovery'] is not None and r.get('exclusion') is None}
    tool_path=ROOT/'Experiment/01_behavioral_diversity/data/tool_calls/episodes.csv'
    import csv
    tools={ (r['source'],r['task_id'],r['arm'],int(r['trial'])):r for r in csv.DictReader(tool_path.open())}
    # Reuse the exact tested 6-word positional matcher from Experiment 09.
    nb_path=ROOT/'Experiment/09_offline_metric_suite/metric_suite.ipynb'
    notebook=json.loads(nb_path.read_text())
    source=next(''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code' and 'def max_aligned_matches' in ''.join(c['source']))
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ['max_aligned_matches','best_matches']]
    assert len(nodes)==2
    namespace={'np':np,'njit':njit};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<recorded repetition matcher>','exec'),namespace)
    best_matches=namespace['best_matches'];SEGMENTER.initialize()
    # Independent direct-match check for the exact selected setting.
    prior=np.array([0,1,2,3,4,5,0,1,2],dtype=np.int64);current=np.array([0,1,2,8,8,8,4,5,0],dtype=np.int64)
    refs=np.lib.stride_tricks.sliding_window_view(prior,6)
    expected=np.array([np.max(np.sum(refs==w,axis=1)) for w in np.lib.stride_tricks.sliding_window_view(current,6)])
    np.testing.assert_array_equal(best_matches(current,[prior],6,9),expected)
    def one(t):
        r={k:t[k] for k in ['source','task_id','study_id','family','arm','trial']}
        r.update(performance=scores.get(key(t),{}).get('score'),fact_recovery=recovery.get(key(t),{}).get('recovery'),self_repetition=None,actor_output_tokens=None,tool_calls=None)
        tool=tools.get(key(t))
        if tool and tool['status']=='available':r['tool_calls']=int(tool['tool_calls'])
        p=ROOT/t['trace_path'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==t['sha256']
        events=[json.loads(x) for x in raw.splitlines() if x.strip()]
        text=[x for x in messages(events,t['source'],normalizer=tokenize)['actor'] if len(x)>=9]
        if len(text)>=2:
            vocab={w:i for i,w in enumerate(dict.fromkeys(w for msg in text for w in msg))}
            encoded=[np.array([vocab[w] for w in msg],dtype=np.int64) for msg in text]
            r['self_repetition']=float(np.mean([100*np.mean(best_matches(encoded[i],encoded[:i],6,len(vocab))>=3) for i in range(1,len(encoded))]))
        r.update(trace_path=str(p.relative_to(ROOT)),trace_sha256=t['sha256'],evaluator_version=scores.get(key(t),{}).get('evaluator_version'))
        api=p.parent/'api_calls.private.jsonl'
        if not api.exists():api=p.parent/'api_calls.jsonl'
        if api.exists():
            raw=api.read_bytes();values=[]
            for line in raw.splitlines():
                if not line.strip():continue
                c=json.loads(line)
                if c.get('phase')=='request' or c.get('role')!='actor':continue
                usage=c.get('usage') or (c.get('response') or {}).get('usage') or {}
                value=usage.get('completion_tokens');assert value is None or value>=0
                values.append(value)
            if values and all(x is not None for x in values):r['actor_output_tokens']=sum(values)
            r.update(api_log=str(api.relative_to(ROOT)),api_sha256=hashlib.sha256(raw).hexdigest(),actor_call_records=len(values),actor_calls_missing_usage=sum(x is None for x in values))
        return r
    with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(one,traces))
    assert len({key(r) for r in rows})==len(rows)==1958
    write_json(OUT/'episodes.json',rows);write_csv(OUT/'episodes.csv',rows)
    write_json(OUT/'provenance.json',{'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [snapshot,tool_path,nb_path]],'matcher_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'no_inference':True})
    return rows

def panel(rows,metric):
    groups=defaultdict(list)
    for r in rows:
        if r.get(metric) is not None:groups[(r['source'],r['task_id'],r['study_id'],r['arm'])].append(r)
    sets=[{k[:3] for k in groups if k[3]==a} for a in ARMS]
    common=sorted(set.intersection(*sets));assert common
    values={q:np.array([np.mean([r[metric] for r in groups[(*q,a)]]) for a in ARMS]) for q in common}
    sources=sorted({q[0] for q in common});point=np.zeros(5);boot=np.zeros((B,5))
    for src in sources:
        qs=[q for q in common if q[0]==src];clusters=tuple(sorted({q[2] for q in qs}))
        sums=np.array([sum((values[q] for q in qs if q[2]==c),start=np.zeros(5)) for c in clusters])
        counts=np.array([sum(q[2]==c for q in qs) for c in clusters])
        point+=np.mean([values[q] for q in qs],axis=0)/len(sources)
        w=bootstrap_weights(src,clusters)
        boot+=(w@sums)/(w@counts)[:,None]/len(sources)
    def stat(value,draws):return {'mean':float(value),'ci95':np.quantile(draws,[.025,.975]).tolist()}
    ratio=None
    if metric in ['actor_output_tokens','tool_calls']:
        # Ratio of balanced means; shared bootstrap draws preserve baseline covariance.
        assert point[0]>0 and np.all(boot[:,0]>0), 'Undefined zero-baseline resource ratio'
        ratio=stat(np.mean(point[1:])/point[0],np.mean(boot[:,1:],axis=1)/boot[:,0])
    return {'persona_mean':stat(np.mean(point[1:]),np.mean(boot[:,1:],axis=1)),
            'off':stat(point[0],boot[:,0]),'relative_to_off':ratio,
            'by_setting':{a:stat(point[i],boot[:,i]) for i,a in enumerate(ARMS)},
            'questions':len(common),'source_questions':dict(Counter(q[0] for q in common)),
            'episodes_by_setting':{a:sum(len(groups[(*q,a)]) for q in common) for a in ARMS},
            'trials_by_setting':{a:sorted({r['trial'] for q in common for r in groups[(*q,a)]}) for a in ARMS},
            'question_keys':[list(q) for q in common]}

METRICS=['performance','fact_recovery','self_repetition','actor_output_tokens','tool_calls']
COLUMNS=[('Persona-off performance','performance','off'),('Mean Persona Performance','performance','persona_mean'),('Fact recovery (%)','fact_recovery','persona_mean'),('Self-repetition (%)','self_repetition','persona_mean')]

def build(rows=None):
    rows=rows if rows is not None else json.loads((OUT/'episodes.json').read_text())
    panels={m:panel(rows,m) for m in METRICS}
    result={'model':MODEL,'model_scope':'Historical Astra actor campaign; simulator Astra low; native/model-based evaluators include historical version differences. Not a uniform-judge cross-model release.',
            'arms':ARMS,'persona_average_includes_off':False,'panels':panels,'bootstrap':{'resamples':B,'seed':SEED,'unit':'study within benchmark; same draws for all settings; trials averaged within question; equal benchmarks and equal four injected personas','resource_ratio':'Ratio of equally benchmark-weighted persona and off means on the same common question panel; recompute numerator and denominator together in each draw; no per-question division or pseudocounts.'},
            'evaluator_versions':{s:dict(Counter(r.get('evaluator_version') or 'unknown' for r in rows if r['source']==s and r['performance'] is not None)) for s in sorted({r['source'] for r in rows})}}
    write_json(OUT/'summary.json',result)
    flat={'model':MODEL,'actor_reasoning':'low','status':'historical_partial_coverage'}
    formatted=[]
    for title,metric,which in COLUMNS:
        raw_value=panels[metric][which]
        scale=1000.0 if metric=='actor_output_tokens' else 1.0
        v={'mean':raw_value['mean']/scale,'ci95':[x/scale for x in raw_value['ci95']]}
        name='off_performance' if which=='off' else 'mean_persona_performance' if metric=='performance' else 'actor_output_ktokens_per_episode' if metric=='actor_output_tokens' else 'tool_calls_per_episode' if metric=='tool_calls' else metric
        flat.update({name:v['mean'],name+'_ci_low':v['ci95'][0],name+'_ci_high':v['ci95'][1],name+'_questions':panels[metric]['questions']})
        digits=2
        formatted.append(f"{v['mean']:,.{digits}f} [{v['ci95'][0]:,.{digits}f}, {v['ci95'][1]:,.{digits}f}]")
    write_csv(OUT/'model_scorecard.csv',[flat])
    raw=[]
    for metric in ['actor_output_tokens','tool_calls']:
        p=panels[metric]
        raw.append({'model':MODEL,'metric':metric,'unit':'tokens/episode' if metric=='actor_output_tokens' else 'calls/episode',
                    'off_mean':p['off']['mean'],'off_ci_low':p['off']['ci95'][0],'off_ci_high':p['off']['ci95'][1],
                    'persona_mean':p['persona_mean']['mean'],'persona_ci_low':p['persona_mean']['ci95'][0],'persona_ci_high':p['persona_mean']['ci95'][1],
                    'ratio':p['relative_to_off']['mean'],'ratio_ci_low':p['relative_to_off']['ci95'][0],'ratio_ci_high':p['relative_to_off']['ci95'][1],
                    'overhead_percent':100*(p['relative_to_off']['mean']-1),'questions':p['questions']})
    write_csv(OUT/'resource_use_raw.csv',raw)
    raw_table=markdown_table(['Metric','Persona-off mean / episode','Persona mean / episode','Ratio to off','Change from off (%)'],
        [[r['metric'],f"{r['off_mean']:,.2f}",f"{r['persona_mean']:,.2f}",f"{r['ratio']:.3f}×",f"{r['overhead_percent']:+.2f}"] for r in raw])
    (OUT/'resource_use_raw.md').write_text(raw_table+'\n')
    coverage=[{'metric':m,'questions':p['questions'],'source_questions':json.dumps(p['source_questions']),**{a+'_episodes':p['episodes_by_setting'][a] for a in ARMS}} for m,p in panels.items()]
    write_csv(OUT/'coverage.csv',coverage)
    table=markdown_table(['Actor model',*[c[0] for c in COLUMNS]],[[MODEL,*formatted]])
    caption='Values are estimates [pointwise 95% study-cluster bootstrap CI]. Persona means average 155/001/003/046 equally; off is a separate reference. Resource metrics are retained as supporting data, outside the main table. For each metric, use questions observed under all five settings, average available trials within question, questions within benchmark, and applicable benchmarks equally. Panels differ by metric; these are historical available-data estimates, not full 200-question coverage. CIs condition on observed trials and do not estimate unseen rollout variation for single-trial settings.'
    definitions='''## Definitions and limits

- **Mean Persona Performance:** native score on the existing 0–100 scale; equal weights over five source benchmarks. Original endpoints only, with complete traces and scored outcomes. Historical evaluator versions differ (see summary.json); use this as a provisional retrospective row, not a uniform-judge leaderboard claim.
- **Fact recovery:** mean percentage of required withheld facts recovered, using all eligible SciConv disambiguation runs, without conditioning on success/failure. It is not the failure-conditioned all-facts-complete metric in Experiment 09 panel B.
- **Self-repetition:** Experiment 09's selected 6-word/3-position match definition; messages must have at least 9 word tokens and an episode needs at least two eligible actor messages. Average later-message matched-window fractions. This threshold was selected after exploratory inspection; retain that limitation in the paper. Includes shared actor handoffs/questions, not private reasoning, tool text or final SciConv specifications.
- **Output tokens:** recorded completion tokens summed over all logged actor response records in the entire episode, including reasoning, tool-call generation and final replies. Excludes simulator/judge/input tokens. Missing usage makes the episode unavailable; this differs from Experiment 01's tokens-per-completed-interaction metric.
- **Tool calls:** recorded execute_command, inspect_repository and execute_check invocations; excludes communication/control actions. Applicable to ASI/Bix/Discovery/EXP; SciConv is not assigned zero. Counts do not measure successful execution or the number of shell subcommands.
- **Resource units:** the main table uses absolute means; tokens and their CI endpoints are divided by 1,000 solely for readability. Tool calls remain counts per episode. Persona-off ratios and raw counts are retained only as supporting comparisons; they do not define the primary resource metrics.
- Repetition, tokens and tool counts are descriptive; lower values do not automatically mean better adaptation. Do not combine them into a scalar adaptation score.
- Some settings have only trial 1; repeated settings use all available original trials with equal question/setting weighting. Common questions do not imply matched trial counts. Availability may be outcome-dependent. The closed fixed panel is exploratory and was partly selected using prior effects.
- The Astra metric panels above use historical available data; the full Haiku performance row is appended below. The withdrawn incomplete Sol campaign is excluded. Additional models need the same frozen metric contract and shared question support before ranking; do not reuse these model-specific common panels uncritically.
'''
    report='# Model-level scientific-agent scorecard\n\n'+table+'\n\n'+caption+'\n\n'+definitions+'\n## Raw resource-use transparency\n\n'+raw_table+'\n## Coverage\n\n'+markdown_table(['Metric','Common questions','Questions by benchmark','Episodes: off / 155 / 001 / 003 / 046'],[[m,p['questions'],json.dumps(p['source_questions']),' / '.join(str(p['episodes_by_setting'][a]) for a in ARMS)] for m,p in panels.items()])+'\n'
    (BASE/'MODEL_SCORECARD.md').write_text(report)
    (OUT/'model_scorecard.md').write_text(table+'\n\n'+caption+'\n')
    latex='\\begin{tabular}{l'+'r'*len(COLUMNS)+'}\n\\hline\n'+' & '.join(['Actor model']+[c[0].replace('%',r'\%').replace('×',r'$\times$') for c in COLUMNS])+r' \\'+'\n\\hline\n'+' & '.join([MODEL,*formatted])+r' \\'+'\n\\hline\n\\end{tabular}\n'
    (OUT/'model_scorecard.tex').write_text(latex)
    result=append_haiku(result, flat, formatted)
    print((OUT/'model_scorecard.md').read_text(),flush=True)
    return result

def haiku_metrics(rows, folder):
    import csv
    files=[folder/'traces/full-campaign-shared-events.jsonl',folder/'traces/full-campaign-results.json',
           folder/'actor_metrics/per_episode.csv',ROOT/'Experiment/09_offline_metric_suite/metric_suite.ipynb']
    provenance={str(p.relative_to(ROOT)):sha(p) for p in files}
    cache=OUT/'haiku_metric_episodes.json';stamp=OUT/'haiku_metric_provenance.json'
    if cache.exists() and stamp.exists() and json.loads(stamp.read_text()).get('inputs')==provenance:
        return json.loads(cache.read_text())
    ident=lambda r:(r.get('benchmark',r.get('source')),r['task_id'],r['arm'])
    resources={ident(r):r for r in csv.DictReader(files[2].open())}
    native={ident(r):r['native_results'][0] for r in json.loads(files[1].read_text())}
    events={ident(r):r['events'] for r in map(json.loads,files[0].read_text().splitlines())}
    assert len(resources)==len(native)==len(events)==len(rows)==1000
    nb=json.loads(files[3].read_text())
    source=next(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code' and 'def max_aligned_matches' in ''.join(c['source']))
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ['max_aligned_matches','best_matches']]
    namespace={'np':np,'njit':njit};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<recorded repetition matcher>','exec'),namespace)
    matcher=namespace['best_matches'];SEGMENTER.initialize()
    for r in rows:
        k=ident(r);usage=resources[k];n=native[k]
        assert int(usage['actor_api_calls'])==int(usage['recorded_actor_calls'])
        r.update(actor_output_tokens=int(usage['actor_output_tokens']),tool_calls=None,fact_recovery=None,self_repetition=None)
        if r['source']!='sciconvbench':
            names=json.loads(usage['tool_name_counts'])
            r['tool_calls']=sum(names.get(t,0) for t in ['execute_command','inspect_repository','execute_check'])
        elif '/disambiguation/' in r['task_id']:
            recovery=n['evaluation']['metrics'].get('entity_recovery')
            assert recovery is not None and 0<=recovery<=1
            r['fact_recovery']=100*recovery
        texts=[x for x in messages(events[k],r['source'],normalizer=tokenize)['actor'] if len(x)>=9]
        r['repetition_eligible_messages']=len(texts)
        if len(texts)>=2:
            vocab={w:i for i,w in enumerate(dict.fromkeys(w for text in texts for w in text))}
            encoded=[np.array([vocab[w] for w in text],dtype=np.int64) for text in texts]
            r['self_repetition']=float(np.mean([100*np.mean(matcher(encoded[i],encoded[:i],6,len(vocab))>=3) for i in range(1,len(encoded))]))
    write_json(cache,rows);write_csv(OUT/'haiku_metric_episodes.csv',rows)
    write_json(stamp,{'inputs':provenance,'no_inference':True,'repetition':'Same 6-word/3-aligned-position matcher and >=9-word message eligibility as Astra',
        'recovery':'100 * native entity_recovery (saved recovered-fact share, before intent gating)',
        'tools':'Model-issued execute_command + inspect_repository + execute_check; SciConv excluded',
        'tokens':'Imported actor completion-token aggregates; original private API logs not included'})
    return rows

def append_haiku(result, astra_flat, astra_formatted):
    """Self-Haiku scores plus explicitly collaborator-reported behavioral means."""
    import csv
    path=ROOT/'results/haiku-actor-haiku-simulator-astra-judge/trial-1/episodes.csv'
    manifest=json.loads((path.parent/'bundle_manifest.json').read_text())
    assert sha(path)==manifest['files']['episodes.csv']['sha256']
    raw=list(csv.DictReader(path.open()))
    assert len(raw)==len({(r['benchmark'],r['task_id'],r['arm']) for r in raw})==1000
    rows=[dict(source=r['benchmark'],task_id=r['task_id'],study_id=r['study_id'],
        arm=r['arm'],trial=1,performance=float(r['score_0_100'])) for r in raw]
    performance=panel(rows,'performance')
    reported_path=OUT/'haiku_self_reported_metrics.json'
    reported=json.loads(reported_path.read_text())
    label='Claude Haiku 4.5'
    flat=dict(model=label,actor_reasoning='not specified',status='self_haiku_scores_with_collaborator_reported_behavior')
    display=[]
    for title,metric,which in COLUMNS:
        name='off_performance' if which=='off' else 'mean_persona_performance' if metric=='performance' else metric
        if metric=='performance':
            v=performance[which];lo,hi=v['ci95']
            flat.update({name:v['mean'],name+'_ci_low':lo,name+'_ci_high':hi,name+'_questions':performance['questions']})
            display.append(f"{v['mean']:.2f} [{lo:.2f}, {hi:.2f}]")
        else:
            lo,hi=reported['ci95'][metric]
            flat.update({name:reported[metric],name+'_ci_low':lo,name+'_ci_high':hi,name+'_questions':None})
            display.append(f"{reported[metric]:.2f} [{lo:.2f}, {hi:.2f}]")
    note=('Haiku actor and simulator: Claude Haiku 4.5; judge: GPT-6 Astra. '
          'Performance uses 200 questions (40 per benchmark), five settings, one trial, including 120 non-submissions; '
          '95% intervals use the benchmark-stratified study-cluster bootstrap. '
          'Haiku fact recovery (67.95%) and self-repetition (21.43%) are collaborator-reported measurements and 95% confidence intervals supplied by the author on 2026-10-07. '
          'Their underlying metric records, exact aggregation, sample counts and CI computation method are not available locally; '
          'these estimates and intervals have not been independently reproduced. They replace the incorrectly labelled older Opus-simulator values. '
          'All non-Off columns represent the four-persona mean; performance weights benchmarks and personas equally.')
    table=markdown_table(['Actor model',*[c[0] for c in COLUMNS]],[[MODEL,*astra_formatted],[label,*display]])
    write_csv(OUT/'model_scorecard.csv',[astra_flat,flat])
    (OUT/'model_scorecard.md').write_text(table+'\n\nEstimates [95% CI where available].\n\n'+note+'\n')
    headers=['Actor model']+[c[0].replace('%',r'\%') for c in COLUMNS]
    body=[' & '.join([MODEL,*astra_formatted])+r' \\', ' & '.join([label,*display])+r' \\']
    (OUT/'model_scorecard.tex').write_text('\\begin{tabular}{lrrrr}\n\\hline\n'+' & '.join(headers)+r' \\'+'\n\\hline\n'+'\n'.join(body)+'\n\\hline\n\\end{tabular}\n% '+note+'\n')
    result['additional_models']=[{'model':label,'panels':{'performance':performance},
        'reported_metrics':reported,'role_configuration':reported['configuration'],
        'input':str(path.relative_to(ROOT)),'sha256':sha(path),
        'reported_metrics_input':str(reported_path.relative_to(ROOT)),'note':note}]
    write_json(OUT/'summary.json',result)
    write_json(OUT/'haiku_performance_episodes.json',rows)
    report=BASE/'MODEL_SCORECARD.md'
    report.write_text(report.read_text()+'\n## Haiku self-collaboration campaign\n\n'+table+'\n\n'+note+'\n')
    return result
if __name__=='__main__':build(extract() if '--extract' in sys.argv else None)
