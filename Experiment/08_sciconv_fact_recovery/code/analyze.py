#!/usr/bin/env python3
"""Offline fact-recovery extraction, paired analysis and figures; never invokes a model."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse, csv, hashlib, json, re
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/08_sciconv_fact_recovery'
ARMS=['persona_off','candidate_148','candidate_155','candidate_089','candidate_001','candidate_127']
LABELS=['Off','148','155','089','001','127']
COLORS=['#65758B','#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']
RESAMPLES=20000; SEED=20261001

def read(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def parse_fraction(value,expected=None):
    match=re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*',str(value))
    if not match:raise ValueError('Malformed recovery fraction')
    k,n=map(int,match.groups())
    if n<=0 or not 0<=k<=n:raise ValueError('Invalid recovery counts')
    if expected is not None and n!=expected:raise ValueError('Judge denominator does not match native issue count')
    return k,n

def extract_one(args):
    row,view,trial,meta=args
    native=next((n for n in row.get('native_results',[]) if n.get('benchmark')=='sciconvbench'),{})
    mode=row['task_id'].split('/')[1]
    out={'view':view,'trial':trial,'case':row['task_id'],'domain':row['task_id'].split('/')[0],
         'study_id':meta.get('study_id') or row.get('study_id') or row['task_id'],'arm':row['arm'],
         'mode':mode,'attempt':row.get('attempt'),'status':row['status'],'facts_recovered':None,
         'facts_total':None,'recovery_share':None,'FRR':None,'full_recovery':None,'intent_capture':None,
         'question_limit_hit':None,'researcher_replies':None,'reply_words_mean':None,
         'evaluator_version':(native.get('evaluation') or {}).get('evaluator_version'),'files':[]}
    if mode!='disambiguation':out['status']='excluded_inconsistency';return out
    if row['status']!='finished' or native.get('status')!='scored':return out
    case=Path(native['case_directory']);evaluation=native['evaluation'];metrics=evaluation['metrics']
    try:
        judge_path=case/'llm_judge_disambiguation_score.json';judge=read(judge_path)
        k,n=parse_fraction(judge.get('score'),evaluation['details']['native_case'].get('n_items'))
        events_path=case/'controller/events.jsonl'
        events=[json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
        replies=[str(e['payload']['answer']) for e in events if e['type']=='researcher_reply']
        out.update(status='scored',facts_recovered=k,facts_total=n,recovery_share=k/n,
                   FRR=metrics['FRR'],full_recovery=int(k==n),intent_capture=metrics['intent_capture'],
                   question_limit_hit=int(len(replies)>=10),researcher_replies=len(replies),
                   reply_words_mean=float(np.mean([len(s.split()) for s in replies])) if replies else 0.0,
                   files=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in [judge_path,events_path]])
    except (OSError,ValueError,KeyError,TypeError):out['status']='invalid_or_missing_saved_judgement'
    return out

def collect():
    selection={r['task_id']:r for r in csv.DictReader((ROOT/'Experiment/shared/task_selection.csv').open()) if r['source']=='sciconvbench'}
    jobs=read(ROOT/'Experiment/07_error_repairs/status.json')['jobs'][:6]
    work=[];provenance=[];configs=[]
    for index,job in enumerate(jobs):
        trial=index%3+1;run=Path(job['run_dir'])
        manifest=read(run/'manifest.json');assert manifest['model']=='gpt-6-astra' and manifest['reasoning_effort']=='low'
        for arm in manifest['arms']:
            p=run/'configs'/f'{arm}.shared.json';config=read(p)
            models={role:{k:v.get(k) for k in ['model','reasoning_effort']} for role,v in config['models'].items()}
            assert all(v['model']=='gpt-6-astra' and v['reasoning_effort']=='low' for v in models.values())
            configs.append({'trial':trial,'arm':arm,'path':str(p.relative_to(ROOT)),'sha256':digest(p),'models':models})
        for view,filename in [('original','original_results_snapshot.json'),('after_repair','results.json')]:
            p=run/filename;provenance.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'view':view,'trial':trial})
            work.extend((row,view,trial,selection[row['task_id']]) for row in read(p) if row['source']=='sciconvbench')
    with ThreadPoolExecutor(max_workers=16) as pool:episodes=list(pool.map(extract_one,work))
    assert len(episodes)==1440 and len({(e['view'],e['trial'],e['case'],e['arm']) for e in episodes})==1440
    snapshot={'captured_at_utc':datetime.now(timezone.utc).isoformat(),'selection_sha256':digest(ROOT/'Experiment/shared/task_selection.csv'),
              'method':'Native disambiguation score k/n, checked against native issue count. No new grading. Inconsistency cases excluded.',
              'provenance':provenance,'model_configs':configs,'episodes':episodes}
    write(BASE/'data/snapshot.json',snapshot)
    with (BASE/'data/episodes.csv').open('w',newline='') as f:
        fields=[k for k in episodes[0] if k!='files'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in episodes)
    return snapshot

def ci(group,rng):
    if not group:return {'mean':None,'ci95':None,'cases':0,'episodes':0,'clusters':0}
    boots=np.zeros(RESAMPLES);clusters_total=0
    for domain in sorted({r['domain'] for r in group}):
        sub=[r for r in group if r['domain']==domain];clusters=sorted({r['study_id'] for r in sub});clusters_total+=len(clusters)
        sums=np.array([sum(r['value'] for r in sub if r['study_id']==c) for c in clusters]);counts=np.array([sum(r['study_id']==c for r in sub) for c in clusters])
        weights=rng.multinomial(len(clusters),np.ones(len(clusters))/len(clusters),size=RESAMPLES)
        boots+=(weights@sums)/(weights@counts)*len(sub)/len(group)
    return {'mean':float(np.mean([r['value'] for r in group])),'ci95':np.quantile(boots,[.025,.975]).tolist(),
            'cases':len(group),'episodes':sum(r['episodes'] for r in group),'clusters':clusters_total,'domains':dict(Counter(r['domain'] for r in group))}

def task_means(rows,metric):
    cases=defaultdict(list)
    for r in rows:
        if r['status']=='scored' and r.get(metric) is not None:cases[r['case']].append(r)
    return [{'case':case,'domain':rs[0]['domain'],'study_id':rs[0]['study_id'],'value':float(np.mean([r[metric] for r in rs])),'episodes':len(rs)} for case,rs in sorted(cases.items())]

def analyze(snapshot):
    rng=np.random.default_rng(SEED);summary={'seed':SEED,'resamples':RESAMPLES,'views':{}}
    for view in ['original','after_repair']:
        rows=[r for r in snapshot['episodes'] if r['view']==view and r['mode']=='disambiguation']
        panels={}
        for panel in ['all','exclude_question_limit']:
            rr=[r for r in rows if panel=='all' or r['question_limit_hit']==0]
            arms={arm:{metric:ci(task_means([r for r in rr if r['arm']==arm],metric),rng) for metric in ['recovery_share','FRR','full_recovery','researcher_replies','reply_words_mean']} for arm in ARMS}
            baseline={(r['case'],r['trial']):r for r in rr if r['arm']=='persona_off' and r['status']=='scored'}
            paired={}
            for arm in ARMS[1:]:
                diffs=[]
                for r in rr:
                    b=baseline.get((r['case'],r['trial']))
                    if r['arm']==arm and r['status']=='scored' and b:
                        diffs.append({**r,'difference':r['recovery_share']-b['recovery_share']})
                paired[arm]=ci(task_means(diffs,'difference'),rng)
            panels[panel]={'arms':arms,'paired_recovery_vs_off':paired}
        summary['views'][view]={'coverage':{arm:dict(Counter(r['status'] for r in rows if r['arm']==arm)) for arm in ARMS},
            'limit_hits':{arm:sum(r['question_limit_hit']==1 for r in rows if r['arm']==arm) for arm in ARMS},'panels':panels}
    off=[r for r in snapshot['episodes'] if r['view']=='original' and r['arm']=='persona_off' and r['status']=='scored']
    screen=[]
    for t in task_means(off,'recovery_share'):
        rs=[r for r in off if r['case']==t['case']];ns={r['facts_total'] for r in rs};assert len(ns)==1
        n=next(iter(ns));band='single_fact' if n==1 else 'near_ceiling' if t['value']>.9 else 'low' if t['value']<.3 else 'multi_fact_mid'
        screen.append({**t,'facts_total':n,'band':band})
    summary['exploratory_difficulty_screen']=screen
    summary['original_vs_repair_changed']=sum(a['recovery_share']!=b['recovery_share'] for a,b in zip(sorted([r for r in snapshot['episodes'] if r['view']=='original'],key=lambda r:(r['trial'],r['case'],r['arm'])),sorted([r for r in snapshot['episodes'] if r['view']=='after_repair'],key=lambda r:(r['trial'],r['case'],r['arm']))))
    return summary

def fmt(s,scale=100):
    if s['mean'] is None:return '—'
    lo,hi=s['ci95'];return f"{s['mean']*scale:.1f} [{lo*scale:.1f}, {hi*scale:.1f}]"

def table(summary,panel='all'):
    data=summary['views']['original'];p=data['panels'][panel]
    lines=['| Persona | Recovery % [95% CI] | Paired Δ vs off (pp) [95% CI] | FRR % | Cases / episodes | Cap hits (all) |','|---|---|---|---:|---:|---:|']
    for arm,label in zip(ARMS,LABELS):
        s=p['arms'][arm]['recovery_share'];f=p['arms'][arm]['FRR']['mean']
        lines.append(f"| {label} | {fmt(s)} | {'reference' if arm=='persona_off' else fmt(p['paired_recovery_vs_off'][arm])} | {f*100:.1f} | {s['cases']} / {s['episodes']} | {data['limit_hits'][arm]} |" if f is not None else f'| {label} | — | — | — | 0 / 0 | — |')
    return '\n'.join(lines)

def plot(summary,show=False):
    import sys
    code_dir=str(BASE/'code')
    if code_dir not in sys.path:sys.path.insert(0,code_dir)
    from plot_fact_recovery import plot as render
    return render(summary,show=show)


def save_report(snapshot,summary):
    write(BASE/'data/summary.json',summary)
    with (BASE/'data/difficulty_screen.csv').open('w',newline='') as f:
        rows=summary['exploratory_difficulty_screen'];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    panels=summary['views']['original']['panels'];diff=summary['original_vs_repair_changed']
    coverage=summary['views']['original']['coverage']
    usable=sum(c.get('scored',0) for c in coverage.values())
    bands=dict(Counter(r['band'] for r in summary['exploratory_difficulty_screen']))
    lines=['# Experiment 08 — SciConv fact recovery','', '[Executed analysis notebook](analysis.ipynb) · [Plan](PLAN.md)','',
    'Exploratory reanalysis of saved Astra-low judgements: 20 disambiguation cases × 6 persona settings × 3 original trials = 360 eligible episode slots. The other 20 SciConv inconsistency cases per condition/trial are excluded: inconsistency resolution is not a deleted-fact count. No new model calls or regrading.','',
    'Primary metric: recovered deleted facts / total deleted facts, from native `llm_judge_disambiguation_score.json`, validated against the native issue count. Recovery is not intent-gated; FRR remains a separate outcome. We average trial scores within each case, then give each case equal weight, rather than giving cases with more facts more weight.','',
    'Original outcomes are primary; the after-repair view is a sensitivity check. A retry is never an independent trial. Five persona-minus-off contrasts pair the same case and trial before averaging within cases. Pointwise 95% percentile intervals use 20,000 study-cluster bootstrap draws within domains, preserving observed domain weights (seed 20261001). They condition on the observed trials, do not separately estimate repeat-run uncertainty, and are not multiplicity-corrected significance tests. Sparse study/domain strata can produce unstable or degenerate intervals.','',
    '## Original three-trial results','',table(summary),'','![Fact recovery and paired differences](figures/fact_recovery.png)','',
    '**Figure.** Native deleted-fact recovery and matched changes relative to persona-off. Bars and printed brackets show means and pointwise 95% CIs; n counts cases and e counts episodes (matched pairs for differences). No inference of a personality mechanism is warranted without neutral-wording and response-length controls.','',
    '## Observations','',
    f'Usable original disambiguation judgements: **{usable}/360**. Baseline difficulty bands: {bands}. The fixed panel is largely near ceiling; it is not a confirmed intermediate-difficulty panel.','',
    'All five persona point estimates exceed off, but most paired intervals include zero. Persona 001 has a lower primary pointwise CI bound just above zero; its cap-exclusion interval reaches zero. These five exploratory comparisons are not multiplicity-corrected, and no neutral-wording or response-length intervention was run. Do not interpret this as a confirmed persona benefit.','',
    '## Excluding episodes reaching the ten-question limit','',
    'A limit hit is inferred from at least ten researcher-reply events, following PR #17. Apply the exclusion to both members of a paired comparison. This is a proxy for the known last-answer handling issue, not a correction or rerun. The cap-hits column retains counts from the full panel.','',table(summary,'exclude_question_limit'),'','## Provenance and scope','',
    f'Original versus repair views differ in recovery share in **{diff}** episode slots. The full sensitivity results are stored in `data/summary.json`. The snapshot includes 1,440 records: two outcome views of all 720 SciConv episode slots, with inconsistency exclusions explicit.','',
    'The old runner labels its evaluator version `+luna-judge` even though the frozen configs specify Astra low. This stale label is retained in the snapshot; actual per-role configuration hashes and model names are recorded separately. The campaign uses the pinned pre-PR-6 persona protocol, not current main defaults.','',
    'Whitespace-separated reply length and question counts are descriptive only. They are not language-normalized token counts. Saved conversation judges do not supply all PR #12 per-fact delivered/volunteered labels, so those mechanisms are not inferred here.','',
    'The persona-off difficulty screen is exploratory and does not select the cases used above. See `data/difficulty_screen.csv`; fresh confirmation and held-out evaluation are required before adopting a screened panel.','',
    '[Snapshot with input hashes](data/snapshot.json) · [Numeric episode CSV](data/episodes.csv) · [Summary](data/summary.json) · [PDF](figures/fact_recovery.pdf) · [SVG](figures/fact_recovery.svg)','',
    'Reproduce offline: `.venv/bin/python Experiment/08_sciconv_fact_recovery/code/analyze.py`. Add `--refresh` only to re-extract the snapshot from raw saved judgements. No command in this script invokes a model.','']
    (BASE/'REPORT.md').write_text('\n'.join(lines))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    snapshot=collect() if args.refresh or not (BASE/'data/snapshot.json').exists() else read(BASE/'data/snapshot.json')
    summary=analyze(snapshot);save_report(snapshot,summary);plot(summary)
    print(table(summary));print('Recovery changes after repair:',summary['original_vs_repair_changed'])
if __name__=='__main__':main()
