#!/usr/bin/env python3
"""Snapshot available Trial 1 episodes and produce reproducible descriptive EDA."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'Experiment/02_performance_and_fields'
spec = importlib.util.spec_from_file_location('first_pass_ci', ROOT/'scripts/report_first_pass_ci.py')
scoring = importlib.util.module_from_spec(spec); spec.loader.exec_module(scoring)
ARMS = ['persona_off','candidate_148','candidate_155','candidate_046','candidate_003','candidate_004','candidate_089','candidate_001','candidate_127','candidate_262','candidate_224','candidate_026']
SOURCES = ['asibench','bixbench','discoverybench','expbench','sciconvbench']
FAMILIES = ['life','physical_engineering','math_cs','social_humanities']
NAMES = {'asibench':'ASI-Bench*','bixbench':'BixBench','discoverybench':'DiscoveryBench','expbench':'EXP-Bench','sciconvbench':'SciConvBench','life':'Life sciences','physical_engineering':'Physical sciences & engineering','math_cs':'Math & CS','social_humanities':'Social sciences & humanities'}

def label(arm):return 'Off' if arm=='persona_off' else arm.removeprefix('candidate_')
def sha(data):return hashlib.sha256(data).hexdigest()
def table(headers, rows):return ['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(map(str,row))+' |' for row in rows],'']
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resamples',type=int,default=20000)
    p.add_argument('--seed',type=int,default=20260929)
    p.add_argument('--snapshot',type=Path,help='Reuse an existing normalized snapshot, avoiding live files')
    a=p.parse_args()
    out=BASE/'data/trial_1_all_personas';out.mkdir(parents=True,exist_ok=True)
    if a.snapshot:
        snapshot=json.loads(a.snapshot.read_text())
    else:
        snapshot={'captured_at_utc':datetime.now(timezone.utc).isoformat(),'runs':[],'episodes':[]}
        sel=ROOT/'Experiment/shared/task_selection.csv'
        selection=list(csv.DictReader(sel.open()));expected={(x['source'],x['task_id']):x for x in selection}
        assert len(expected)==200
        snapshot['selection']=selection;snapshot['selection_sha256']=sha(sel.read_bytes())
        exp=json.loads((ROOT/'runs/openai-astra-top10-expansion.json').read_text())
        paths=[ROOT/'runs/openai-astra-top2-first-pass',*[Path(b['run_dir']) for b in exp['batches'] if b['trial']==1]]
        seen=set()
        for run in paths:
            record={'run_dir':str(run.relative_to(ROOT)) if run.is_relative_to(ROOT) else str(run),'files':[]}
            manifest=run/'manifest.json'
            if not manifest.exists():
                record['snapshot_mode']='not_started';snapshot['runs'].append(record);continue
            config=json.loads(manifest.read_text())
            assert config['selection_sha256']==snapshot['selection_sha256']
            assert (config['model'],config['reasoning_effort'])==('gpt-6-astra','low')
            record['arms']=config['arms'];record['manifest_sha256']=sha(manifest.read_bytes())
            if (run/'results.json').exists():
                path=run/'results.json';raw=path.read_bytes();rows=json.loads(raw)
                record['snapshot_mode']='final_results';record['files']=[{'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'sha256':sha(raw)}]
            else:
                record['snapshot_mode']='live_state_snapshot'
                def read(path):
                    raw=path.read_bytes()
                    return json.loads(raw),{'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'sha256':sha(raw)}
                with ThreadPoolExecutor(max_workers=16) as pool: pairs=list(pool.map(read,sorted(run.glob('episodes/*/*/state.json'))))
                rows=[x[0] for x in pairs];record['files']=[x[1] for x in pairs]
            for row in rows:
                key=(row['source'],row['task_id']);assert key in expected
                ident=(*key,row['arm']);assert ident not in seen;seen.add(ident)
                assert row['family']==expected[key]['family']
                n=scoring.native(row);value=scoring.score(row) if row['status']=='finished' else None
                assert value is None or (np.isfinite(value) and 0<=value<=100),(ident,value)
                status=('technical_error' if row['status']=='infrastructure_error' else 'running' if row['status']=='running' else 'unscored' if value is None else 'missing_submission' if n.get('status')=='missing_submission' else 'scored')
                snapshot['episodes'].append({'source':row['source'],'task_id':row['task_id'],'family':row['family'],'study_id':row.get('study_id'),'arm':row['arm'],'status':status,'coordinator_status':row['status'],'score':value,'attempt':row.get('attempt'),'evaluator_version':(n.get('evaluation') or {}).get('evaluator_version'),'run_dir':record['run_dir']})
            snapshot['runs'].append(record)
        (out/'snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    episodes=snapshot['episodes'];selection=snapshot['selection']
    by={(r['source'],r['task_id'],r['arm']):r for r in episodes}
    rng=np.random.default_rng(a.seed)
    def summary(group,field='score'):
        if not group:return {'n':0,'mean':None,'ci95':None,'source_counts':{}}
        vals=np.array([r[field] for r in group],dtype=float)
        boot=np.zeros(a.resamples)
        for source in SOURCES:
            x=np.array([r[field] for r in group if r['source']==source],dtype=float)
            if len(x):boot+=x[rng.integers(0,len(x),size=(a.resamples,len(x)))].sum(axis=1)/len(group)
        return {'n':len(group),'mean':float(vals.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'source_counts':dict(Counter(r['source'] for r in group)),'study_clusters':len({(r['source'],r['study_id']) for r in group})}
    metrics={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'snapshot_at_utc':snapshot['captured_at_utc'],'resamples':a.resamples,'seed':a.seed,'coverage':{},'benchmark':{},'superfamily':{},'paired_benchmark_without_asi':{},'paired_superfamily_without_asi':{}}
    for arm in ARMS:
        rows=[r for r in episodes if r['arm']==arm];counts=Counter(r['status'] for r in rows)
        counts['not_started']=200-len(rows)
        metrics['coverage'][arm]=dict(counts)
        valid=[r for r in rows if r['score'] is not None]
        metrics['benchmark'][arm]={s:summary([r for r in valid if r['source']==s]) for s in SOURCES}
        metrics['superfamily'][arm]={f:summary([r for r in valid if r['family']==f]) for f in FAMILIES}
        paired=[]
        if arm!='persona_off':
            for r in valid:
                b=by.get((r['source'],r['task_id'],'persona_off'))
                if r['source']!='asibench' and b and b['score'] is not None:paired.append(dict(r,delta=r['score']-b['score']))
        metrics['paired_benchmark_without_asi'][arm]={s:summary([r for r in paired if r['source']==s],'delta') for s in SOURCES if s!='asibench'}
        metrics['paired_superfamily_without_asi'][arm]={f:summary([r for r in paired if r['family']==f],'delta') for f in FAMILIES}
    # One complete-case panel for sensitivity to unequal pairwise coverage.
    available=[arm for arm in ARMS if any(r['arm']==arm and r['score'] is not None for r in episodes)]
    common=[s for s in selection if s['source']!='asibench' and all(by.get((s['source'],s['task_id'],arm),{}).get('score') is not None for arm in available)]
    metrics['common_panel_without_asi']={'n':len(common),'source_counts':dict(Counter(s['source'] for s in common)),'arms':{}}
    for arm in available:
        metrics['common_panel_without_asi']['arms'][arm]={s:summary([by[(x['source'],x['task_id'],arm)] for x in common if x['source']==s]) for s in SOURCES if s!='asibench'}
    def cell(s,delta=False):
        if not s['n']:return '—'
        fmt='+.2f' if delta else '.2f'
        return f"{s['mean']:{fmt}} [{s['ci95'][0]:.2f}, {s['ci95'][1]:.2f}]; n={s['n']}"
    lines=['# Trial 1 EDA: persona performance by benchmark and super-family','',f"Snapshot: **{snapshot['captured_at_utc']}**. One Trial 1 episode per task/condition; this is an interim descriptive analysis, not the three-trial paper result.",'',
    '## Scope and principal findings','',
    f"Available results cover **{len(available)-1} personas plus persona-off**. Personas 262, 224, and 026 have no Trial 1 results yet. Each condition targets the same 200 tasks, with 40 per benchmark. Actor, researcher simulator, and model judge use GPT-6 Astra with low reasoning.",'',
    'Technical failures cause uneven coverage, especially for persona 003. Raw available-case means must not be interpreted as a fair overall ranking. Pairwise matched comparisons and a common-panel sensitivity analysis appear below. Missing submissions are zero; technical errors, running episodes, and otherwise unscored cases are excluded from score means, not silently treated as incorrect scientific answers.','',
    '**ASI comparability warning:** off/148/155 were evaluated with the older ASI judge setup; expansion personas use the repaired configured-judge bridge. The reported ASI means are descriptive snapshots. Judge/model configuration drift prevents a clean cross-batch persona attribution. Paired comparison tables exclude ASI for every persona; the raw super-family tables include it and inherit this caveat.','',
    '## Episode coverage','',
    'Finished episodes can include missing submissions. Every row below has a planned denominator of 200.']
    lines+=['']+table(['Persona','Scored','Missing submission (0)','Technical errors','Running','Other unscored','Not started','Evaluable / 200'],[[label(arm),*(metrics['coverage'][arm].get(k,0) for k in ['scored','missing_submission','technical_error','running','unscored','not_started']),sum(metrics['coverage'][arm].get(k,0) for k in ['scored','missing_submission'])] for arm in ARMS])
    lines+=['## Score definitions and uncertainty','',
    '- ASI-Bench: native score / native maximum × 100; only valid scored evaluations.',
    '- BixBench: correctness × 100.',
    '- DiscoveryBench: native final score × 100.',
    '- EXP-Bench: final gated coverage mean, falling back to initial only when no final record exists; already on a 0–100 scale.',
    '- SciConvBench: final resolution with intent preserved (FRR) × 100; this evaluates the specification/conversation, not scientific solver correctness.',
    '',f'Each cell is **mean [pointwise 95% CI]; n=evaluable tasks**. Intervals use {a.resamples:,} percentile task-bootstrap resamples (seed {a.seed}), stratified by benchmark source. Within-source observed sample sizes are fixed. Pairwise differences resample matched task differences. These follow the earlier Trial 1 descriptive CI convention.',
    '', 'These intervals reflect task resampling, not repeat-run uncertainty. They do not account for dependence among tasks from the same study or correct for multiple comparisons; sparse or constant-valued groups may have degenerate intervals. They should not establish statistical significance, equivalence, or a final persona ranking.','',
    '## Performance by benchmark','', 'Available-case means use each persona’s own evaluable tasks. Each benchmark has 40 planned tasks per condition. Higher values are better within each benchmark; different native metrics are not calibrated to one another.','']
    lines+=table(['Persona',*[NAMES[s] for s in SOURCES]],[[label(arm),*[cell(metrics['benchmark'][arm][s]) for s in SOURCES]] for arm in ARMS])
    lines+=['## Performance by scientific super-family','', 'Task-weighted averages of normalized native scores; these are descriptive composites of different metrics. No reweighting to equal source or family weights is applied. The available source composition can differ across personas because failures are excluded.','']
    lines+=table(['Super-family','Planned tasks','ASI','Bix','Discovery','EXP','SciConv'],[[NAMES[f],sum(x['family']==f for x in selection),*[sum(x['family']==f and x['source']==s for x in selection) for s in SOURCES]] for f in FAMILIES])
    lines+=table(['Persona',*[NAMES[f] for f in FAMILIES]],[[label(arm),*[cell(metrics['superfamily'][arm][f]) for f in FAMILIES]] for arm in ARMS])
    lines+=['## Matched differences from persona-off: benchmark','', '**Positive = persona exceeds off on exactly the same evaluable tasks.** Each persona has its own matched subset, so rows can still differ in task coverage. ASI is omitted for all rows because of the evaluator change. The baseline is the existing Trial 1 persona-off run; no baseline episodes were duplicated.','']
    lines+=table(['Persona',*[NAMES[s] for s in SOURCES if s!='asibench']],[[label(arm),*[cell(metrics['paired_benchmark_without_asi'][arm][s],True) for s in SOURCES if s!='asibench']] for arm in ARMS if arm!='persona_off'])
    lines+=['## Matched differences from persona-off: super-family','', '**ASI excluded for all personas in this table.** These composites therefore target different source mixtures than the raw super-family table. All source counts and study-cluster counts are retained in the machine-readable summary.','']
    lines+=table(['Persona',*[NAMES[f] for f in FAMILIES]],[[label(arm),*[cell(metrics['paired_superfamily_without_asi'][arm][f],True) for f in FAMILIES]] for arm in ARMS if arm!='persona_off'])
    lines+=['## Common-panel sensitivity analysis','', f"The same **{len(common)} non-ASI tasks** are evaluable across every available condition (off plus eight personas). This sacrifices coverage and may select easier tasks, but prevents each row from using a different task subset. Source counts: "+', '.join(f'{NAMES[s]} {sum(x["source"]==s for x in common)}' for s in SOURCES if s!='asibench')+'.','']
    lines+=table(['Persona',*[NAMES[s] for s in SOURCES if s!='asibench']],[[label(arm),*[cell(metrics['common_panel_without_asi']['arms'][arm][s]) for s in SOURCES if s!='asibench']] for arm in available])
    lines+=['## Observations from this snapshot','',
        f"- **SciConvBench:** persona 127 has {metrics['benchmark']['candidate_127']['sciconvbench']['mean']:.2f}, versus off at {metrics['benchmark']['persona_off']['sciconvbench']['mean']:.2f}; its matched difference is {cell(metrics['paired_benchmark_without_asi']['candidate_127']['sciconvbench'],True)}. Persona 089 has {metrics['benchmark']['candidate_089']['sciconvbench']['mean']:.2f}; persona 046 has {metrics['benchmark']['candidate_046']['sciconvbench']['mean']:.2f}. These are specification-resolution outcomes, not solver success rates.",
        '- **BixBench:** most personas have exactly zero matched difference from off in this snapshot. Apparent differences in raw means can come from different surviving task subsets; the common-panel means are identical across all available conditions.',
        f"- **DiscoveryBench:** persona 046 has a matched improvement of {cell(metrics['paired_benchmark_without_asi']['candidate_046']['discoverybench'],True)}. Its interval includes zero. The other personas also have positive point estimates in this snapshot; these are exploratory signals.",
        f"- **EXP-Bench:** persona 003 has only {metrics['benchmark']['candidate_003']['expbench']['n']} evaluable tasks. Its negative paired interval should not be promoted to a reliable persona effect given severe missingness, few tasks, shared-study dependence, and multiple comparisons.",
        f"- **Super-family composition:** persona 003’s raw Math & CS mean is {metrics['superfamily']['candidate_003']['math_cs']['mean']:.2f} on {metrics['superfamily']['candidate_003']['math_cs']['n']} tasks, compared with off at {metrics['superfamily']['persona_off']['math_cs']['mean']:.2f} on {metrics['superfamily']['persona_off']['math_cs']['n']} tasks. That is not an apples-to-apples advantage. On matched non-ASI Math & CS tasks its difference is {cell(metrics['paired_superfamily_without_asi']['candidate_003']['math_cs'],True)}.",'']
    lines+=['## Interpretation and next steps','',
    '1. Use the matched-difference tables to inspect possible persona effects; available-case means alone confound performance and which tasks survived technical failures.',
    '2. Repair rate-limit failures and regrade sealed submissions after documenting evaluator settings. ASI comparisons need a common judge configuration before being used as evidence of persona effects.',
    '3. Finish the prioritized independent repeats for 089/001/127 and aggregate at the task/condition level; account for shared-study dependence in the eventual paper analysis.',
    '4. Keep unrun personas visibly absent. Do not select a winning persona or claim a significant improvement from this single, incomplete trial.','',
    '## Provenance and reproduction','',
    '[Normalized episode snapshot](data/trial_1_all_personas/snapshot.json) records original statuses, task IDs, scores, evaluator versions, and source-file hashes. [Summary](data/trial_1_all_personas/summary.json) stores all CIs, denominators, and source compositions. [Episode CSV](data/trial_1_all_personas/episodes.csv) supports independent inspection.','',
    'The input snapshot is taken once; a live run may advance while it is read. Final-result files are used when available, otherwise per-episode state files are snapshotted. Historical failed attempts are not counted as extra trials. Original baseline results include three episodes retained from the initial cancelled first-pass job, as in the existing Trial 1 analysis.','',
    'Rebuild exactly from the saved snapshot (no API calls):','', '```bash', '.venv/bin/python Experiment/02_performance_and_fields/code/report_all_trial1.py \\', '  --snapshot Experiment/02_performance_and_fields/data/trial_1_all_personas/snapshot.json', '```','']
    (out/'summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
    with (out/'episodes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(episodes[0]));w.writeheader();w.writerows(episodes)
    report=BASE/'trial_1_all_personas_eda.md';report.write_text('\n'.join(lines))
    print(json.dumps({'report':str(report),'coverage':metrics['coverage'],'common_tasks':len(common)},indent=2))

if __name__=='__main__':main()
