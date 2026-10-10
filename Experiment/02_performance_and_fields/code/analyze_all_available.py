#!/usr/bin/env python3
"""All available Astra personas/repeats on the frozen panel; no model calls."""
from pathlib import Path
from collections import Counter
import argparse, importlib.util, json, re, sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import SOURCES,FAMILIES,NAMES,B,SEED,label,sha,write_json,write_csv,selection,summarize,paired,markdown_table
from consolidate_performance import compatible
BASE=ROOT/'Experiment/02_performance_and_fields';DATA=BASE/'data/all_available'
spec=importlib.util.spec_from_file_location('native_scores',ROOT/'scripts/report_first_pass_ci.py');scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)

def collect():
    tasks={(r['source'],r['task_id']):r for r in selection()}
    selection_sha=sha((ROOT/'Experiment/shared/task_selection.csv').read_bytes())
    provenance=[];views={'original':{},'available':{}};declared=set();trial_sets={}
    def read(path):
        raw=path.read_bytes();provenance.append({'file':str(path.relative_to(ROOT)),'sha256':sha(raw)});return json.loads(raw)
    def normal(row,trial,path):
        meta=tasks[(row['source'],row['task_id'])]
        v=scoring.score(row) if row['status']=='finished' else None
        assert v is None or 0<=v<=100
        native=scoring.native(row)
        status='missing_submission' if v is not None and native.get('status')=='missing_submission' else 'scored' if v is not None else row['status']
        return dict(source=row['source'],task_id=row['task_id'],study_id=meta.get('study_id') or row.get('study_id') or row['task_id'],family=meta['family'],arm=row['arm'],trial=trial,score=v,status=status,evaluator_version=(native.get('evaluation') or {}).get('evaluator_version'),input_file=str(path.relative_to(ROOT)))
    jobs=read(ROOT/'Experiment/07_error_repairs/status.json')['jobs']
    for job in jobs:
        source=Path(job['source_run']);run=Path(job['run_dir'])
        match=re.search(r'(?:trial-)(\d+)',source.name);trial=int(match[1]) if match else 1
        config=read(run/'manifest.json')
        assert config['selection_sha256']==selection_sha and config['model']=='gpt-6-astra' and config['reasoning_effort']=='low'
        for arm in config['arms']:declared.add(arm);trial_sets.setdefault(arm,set()).add(trial)
        originals={}
        for row in read(run/'original_results_snapshot.json'):
            r=normal(row,trial,run/'original_results_snapshot.json');key=(trial,r['source'],r['task_id'],r['arm']);assert key not in views['original'];originals[key]=r;views['original'][key]=r;views['available'][key]=dict(r,endpoint='original')
        assert len(originals)==200*len(config['arms'])
        assert all(sum(r['arm']==a for r in originals.values())==200 for a in config['arms'])
        for row in read(run/'results.json'):
            r=normal(row,trial,run/'results.json');key=(trial,r['source'],r['task_id'],r['arm']);assert key in originals
            # Latest evaluable endpoint, never maximum score; failed repair cannot erase valid original evidence.
            if r['score'] is not None:views['available'][key]=dict(r,endpoint='after_repair')
            elif originals[key]['score'] is None:views['available'][key]=dict(r,endpoint='unscored_after_repair')
            else:views['available'][key]['endpoint']='original_fallback_after_failed_repair'
    expansion=read(ROOT/'Experiment/shared/top10_expansion.json')
    declared.update(expansion['ranked_personas']);declared.add(expansion['additional_existing_persona'])
    # Audit other planned expansion paths so newly saved repeats cannot silently be omitted.
    audited=[]
    known={Path(j['source_run']).name for j in jobs}
    for batch in expansion['batches']:
        run=Path(batch['run_dir'])
        if run.name in known:continue
        if (run/'manifest.json').exists():
            raise RuntimeError(f'Additional started campaign batch requires ingestion: {run}')
        audited.append({'run':str(run.relative_to(ROOT)),'status':'not started; no manifest'})
    assert all(r['status'] not in ['running','pending'] for r in views['available'].values())
    episodes=[dict(r,view=view) for view,rows in views.items() for r in rows.values()]
    snapshot=dict(captured_at_utc=datetime.now(timezone.utc).isoformat(),selection_sha256=selection_sha,provenance=provenance,unstarted_batches=audited,declared_arms=sorted(declared),trial_sets={a:sorted(t) for a,t in trial_sets.items()},episodes=episodes)
    write_json(DATA/'snapshot.json',snapshot);write_csv(DATA/'episodes.csv',episodes)
    return snapshot

def stat(rows,field='score'):
    s=summarize(rows,field)
    s['trial_ids']=sorted({r['trial'] for r in rows if r.get(field) is not None})
    s['ci_estimable']=s['studies']>=2
    if not s['ci_estimable']:s['ci95']=None
    return s

def analyze(refresh=False):
    snap=collect() if refresh or not (DATA/'snapshot.json').exists() else json.loads((DATA/'snapshot.json').read_text())
    rows=snap['episodes'];available=[r for r in rows if r['view']=='available']
    preferred=['persona_off','candidate_148','candidate_155','candidate_089','candidate_001','candidate_127','candidate_003','candidate_004','candidate_046']
    observed={r['arm'] for r in available if r['score'] is not None}
    arms=[a for a in preferred if a in observed]+sorted(observed-set(preferred))
    summary=dict(arms=arms,coverage={},absolute={},paired={},resamples=B,seed=SEED,snapshot_sha256=sha((DATA/'snapshot.json').read_bytes()),unstarted_batches=snap['unstarted_batches'])
    for arm in sorted(set(snap['declared_arms'])|observed):
        rr=[r for r in available if r['arm']==arm];valid=[r for r in rr if r['score'] is not None];trials=snap['trial_sets'].get(arm,[])
        summary['coverage'][arm]=dict(trials_with_scores=sorted({r['trial'] for r in valid}),attempted_trial_ids=trials,recorded_slots=len(rr),evaluable=len(valid),tasks=len({(r['source'],r['task_id']) for r in valid}),statuses=dict(Counter(r['status'] for r in rr)),not_recorded=200*len(trials)-len(rr),endpoint_counts=dict(Counter(r['endpoint'] for r in valid)))
    pairs=[];flat=[]
    for view in ['available','original']:
        rr=[r for r in rows if r['view']==view];summary['absolute'][view]={};summary['paired'][view]={}
        for arm in arms:
            aa=[r for r in rr if r['arm']==arm];pp=paired(rr,'score',arm,compatible) if arm!='persona_off' else []
            pairs.extend(pp);summary['absolute'][view][arm]={};summary['paired'][view][arm]={}
            for field,groups in [('source',SOURCES),('family',FAMILIES)]:
                summary['absolute'][view][arm][field]={g:stat([r for r in aa if r[field]==g]) for g in groups}
                summary['paired'][view][arm][field]={g:stat([r for r in pp if r[field]==g],'value') for g in groups}
                for g in groups:
                    for kind in ['absolute','paired']:
                        if kind=='paired' and arm=='persona_off':continue
                        s=summary[kind][view][arm][field][g]
                        flat.append(dict(view=view,kind=kind,arm=arm,level=field,group=g,mean=s['mean'],ci_low=s['ci95'][0] if s['ci95'] else None,ci_high=s['ci95'][1] if s['ci95'] else None,tasks=s['tasks'],episodes=s['episodes'],studies=s['studies'],trial_ids=','.join(map(str,s['trial_ids']))))
    write_json(DATA/'summary.json',summary);write_csv(DATA/'summary.csv',flat);write_csv(DATA/'paired_episodes.csv',pairs)
    return summary

def cell(s,signed=False):
    if s['mean'] is None:return '—'
    value=format(s['mean'],'+.2f' if signed else '.2f')
    ci=f"[{s['ci95'][0]:.2f}, {s['ci95'][1]:.2f}]" if s['ci95'] else '[CI unavailable]'
    return f"{value} {ci}; n={s['tasks']}, e={s['episodes']}"

def report(s):
    arms=s['arms'];lines=['# All available Astra personas and trials','',
    f"**{len(arms)-1} personas plus persona-off**, from completed trial jobs, including single-trial personas. All saved results from their completed Astra-low trial jobs on the frozen 200-task panel are eligible; no three-trial requirement. The cancelled initial run is excluded entirely. Sol and the redesigned SciConv campaign are different model/protocol settings and are not pooled.",'',
    '## Available evidence','',markdown_table(['Persona','Trial IDs with scores','Evaluable episodes','Distinct tasks','Scored','Missing submission (zero)','Recorded unscored','Unrecorded slots in started trials'],[[label(a),','.join(map(str,v['trials_with_scores'])) or 'none',v['evaluable'],v['tasks'],v['statuses'].get('scored',0),v['statuses'].get('missing_submission',0),v['recorded_slots']-v['evaluable'],v['not_recorded']] for a,v in s['coverage'].items()]),'',
    'No-result personas remain in the coverage table, without fabricated zero scores. Three selected personas (262/224/026) never completed a trial. Personas 228 and 137 from the cancelled initial job are excluded, as requested. A completed trial job can still contain technical failures; those do not become zero scientific scores.','',
    '## Aggregation and uncertainty','',
    'Use the latest evaluable endpoint within each task/persona/trial slot. A failed repair falls back to an evaluable original outcome; a scored repair replaces its original regardless of whether its score is higher or lower. Repairs are not extra trials; no partial cancelled-job records are added. Original-only results are retained as a sensitivity. Scientific missing submissions are zero; infrastructure/unscored slots are missing.','',
    'First average available trial scores within task, then give tasks equal weight. Pointwise 95% CIs use 20,000 study-cluster bootstrap draws within benchmark, with observed source proportions fixed. CIs condition on available trials; one-trial rows do not estimate run-to-run variation. Fewer than two studies yields an unavailable CI. Singleton source-by-family strata contribute no bootstrap variation. Incomplete tasks, conditional repair selection, unequal trial counts and outcome-selected personas limit comparisons.','',
    'Absolute scores use all evaluable outcomes and are descriptive; historical ASI judge versions are mixed. Paired changes require the same task and trial, with corrected ASI judges on both sides and compatible evaluator versions elsewhere. Unavailable matched cells remain explicitly missing. Super-family averages mix native metrics and source composition; these are not pure field effects. No equivalence, multiplicity-adjusted significance or persona ranking is claimed.','']
    for kind in ['absolute','paired']:
        aa=arms if kind=='absolute' else arms[1:]
        lines+=['## '+('Available performance' if kind=='absolute' else 'Matched changes from persona-off'),'',f'![{kind} heatmap](figures/all_available/{kind}_performance.png)','']
        for field,groups,title in [('source',SOURCES,'By benchmark'),('family',FAMILIES,'By super-family')]:
            lines+=['### '+title,'',markdown_table(['Persona · available trials',*[NAMES[g] for g in groups]],[[label(a)+' · '+str(len(s['coverage'][a]['trials_with_scores'])),*[cell(s[kind]['available'][a][field][g],kind=='paired') for g in groups]] for a in aa]),'']
    lines+=['## Original-only sensitivity','']
    for field,groups in [('source',SOURCES),('family',FAMILIES)]:
        lines += [markdown_table(['Persona',*[NAMES[g] for g in groups]],[[label(a),*[cell(s['absolute']['original'][a][field][g]) for g in groups]] for a in arms]),'']
    lines+=['## Reproduction','', '[Executed notebook](performance_analysis.ipynb) · [Frozen episode snapshot](data/all_available/snapshot.json) · [Summary and CI source data](data/all_available/summary.csv) · [Paired episodes](data/all_available/paired_episodes.csv)','',
    'The previous six-setting report and heatmap remain as historical analyses. The forest-plot alternative has been removed at the user’s request. Rerun `code/analyze_all_available.py` to use the saved snapshot, or add `--refresh` to re-read the saved run files. No new model calls.','']
    (BASE/'ALL_AVAILABLE_PERFORMANCE.md').write_text('\n'.join(lines))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args();s=analyze(args.refresh);report(s)
    print(json.dumps({'arms':s['arms'],'coverage':s['coverage']},indent=2))
