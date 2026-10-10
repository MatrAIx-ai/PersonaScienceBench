#!/usr/bin/env python3
"""Expand original-trial behavior to all personas with a completed trial job."""
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import analyze_behavior as core
from analysis_utils import ARMS as REPEATED_ARMS, label, cell, markdown_table, sha, write_json
BASE=core.BASE
DATA=BASE/'data/behavior_all_personas'
ARMS=[*REPEATED_ARMS,'candidate_003','candidate_004','candidate_046']
METRICS=core.METRICS
HEAT_METRICS=core.HEAT_METRICS
extract=core.extract

def collect():
    old=json.loads((BASE/'data/behavior/snapshot.json').read_text())
    jobs=json.loads((core.ROOT/'Experiment/07_error_repairs/status.json').read_text())['jobs']
    job=next(j for j in jobs if Path(j['source_run']).name=='openai-astra-top10-trial-1-batch-1')
    path=Path(job['run_dir'])/'original_results_snapshot.json'
    raw=path.read_bytes(); rows=json.loads(raw)
    assert len(rows)==600 and {r['arm'] for r in rows}==set(ARMS[-3:])
    with ThreadPoolExecutor(max_workers=12) as pool:
        results=list(pool.map(extract,[(1,job['source_run'],r) for r in rows]))
    snap=dict(old)
    snap['episodes']=[*old['episodes'],*[r[0] for r in results]]
    snap['event_logs']=[*old['event_logs'],*[r[1] for r in results if r[1]]]
    snap['source_results']=[*old['source_results'],dict(path=str(path),sha256=sha(raw),trial=1)]
    snap['method']='Original endpoints from completed trial jobs only. Six settings have three trials; 003/004/046 have one. Repairs and cancelled initial runs excluded. Complete traces only.'
    assert len(snap['episodes'])==4200
    assert len({(r['trial'],r['source'],r['task_id'],r['arm']) for r in snap['episodes']})==4200
    assert all(n==200 for n in Counter((r['trial'],r['arm']) for r in snap['episodes']).values())
    write_json(DATA/'snapshot.json',snap)
    return snap

def analyze(snap):
    previous=core.DATA
    try:
        core.DATA=DATA
        s=core.analyze(snap,arms=ARMS)
    finally:
        core.DATA=previous
    s['arms']=ARMS
    s['planned_trials']={a:3 if a in REPEATED_ARMS else 1 for a in ARMS}
    s['repeat_panel']=REPEATED_ARMS
    s['endpoint_policy']=snap['method']
    old=json.loads((BASE/'data/behavior/summary.json').read_text())
    assert s['repeat_variation']==old['repeat_variation'], 'Repeated panel must remain unchanged'
    write_json(DATA/'summary.json',s)
    return s

def report(s):
    lines=['# Behavioral analysis — all completed-trial personas','',
    '[Executed notebook](behavioral_analysis.ipynb) · [Preserved six-setting report](BEHAVIOR_REPORT.md)','',
    'Eight personas plus off. Off/148/155/089/001/127 have three completed trial jobs; 003/004/046 have one. A completed job can contain failed episodes: only complete saved episode traces contribute. Cancelled initial runs, repairs, Sol and the new-design SciConv run are excluded. This retains the original behavioral endpoint policy; the performance primary analysis separately uses repaired endpoints.','',
    '## Coverage','',markdown_table(['Setting','Trial jobs','Analyzed episodes','Excluded slots'],[[label(a),s['planned_trials'][a],s['coverage'][a].get('analyzed',0),200*s['planned_trials'][a]-s['coverage'][a].get('analyzed',0)] for a in ARMS]),'',
    '## Paired behavioral effects','',
    '![Behavioral heatmap](figures/behavior_all_personas/behavior_effects.png)','',
    'Cell text is raw paired change with a pointwise 95% study-cluster bootstrap CI (20,000 draws within benchmark); color divides that change by the matched baseline task SD. Repetitions average within task and benchmarks receive equal weight. Pairing uses the same task and trial. One-trial CIs reflect task/study uncertainty conditional on that trial, not run-to-run variation. Denominators vary with trace availability. T labels planned completed trial jobs.','',
    '![Reply-length distribution](figures/behavior_all_personas/reply_length_distribution.png)','',
    'Every point is a matched task; no point subsampling. Character counts depend on language and workflow and do not measure information quality.','']
    for metric in METRICS:
        lines+=['### '+METRICS[metric][0],'',markdown_table(['Setting','Mean [95% CI]; tasks/episodes','Paired change [95% CI]; tasks/pairs'],[[label(a),cell(s['absolute'][metric]['all'][a]),'reference' if a==ARMS[0] else cell(s['paired'][metric]['all'][a],True)] for a in ARMS]),'']
    lines+=['## Repeat variation and interpretation','',
    '![Original repeated panel](figures/behavior_all_personas/repeat_variation.png)','',
    'Repeat variation, script-matched opening collisions and English-primary sensitivity retain the original off/148/155/089/001/127 panel and its three trials. Their values are checked against the preserved analysis. 003/004/046 are excluded from these repeat-dependent estimates. All metric definitions and repeat tables remain in [the original report](BEHAVIOR_REPORT.md).','',
    'These are descriptive measures of observable behavior and lexical reuse. They do not establish semantic collapse or human realism. Persona selection, unequal trial counts and incomplete traces limit comparisons. Semantic trajectories remain deferred.','',
    '[All metrics by benchmark](data/behavior_all_personas/summary.json) · [Episode features](data/behavior_all_personas/episodes.csv) · [Paired effects](data/behavior_all_personas/paired_effects.csv) · [Provenance](data/behavior_all_personas/snapshot.json)','']
    (BASE/'ALL_PERSONAS_BEHAVIOR.md').write_text('\n'.join(lines))

if __name__=='__main__':
    snap=collect(); s=analyze(snap); report(s)
    print(json.dumps(s['coverage'],indent=2))
