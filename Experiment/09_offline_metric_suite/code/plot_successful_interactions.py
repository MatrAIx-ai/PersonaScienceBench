"""Successful-run distribution and matched-question lengths; see SUCCESSFUL_INTERACTIONS.md."""
from pathlib import Path
from statistics import mean
from collections import defaultdict
import sys
import csv
import numpy as np
import hashlib
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/09_offline_metric_suite'
DATA=BASE/'data/successful_interactions'
FIG=BASE/'figures/successful_interactions'
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
COLORS=['#0072B2','#D55E00']
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import write_csv, write_json
sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
from audit_panel_alignment import require_matplotlib_panel_alignment

def key(r):
    return r['source'],r['task_id'],r['arm'],r['trial']

def calculate_all_benchmarks(snap):
    scores={key(r):r['score'] for r in snap['scores'] if r['score'] is not None}
    groups=defaultdict(lambda:defaultdict(list))
    for r in snap['traces']:
        if r.get('exclusion') is None and key(r) in scores:
            groups[(r['source'],r['task_id'])][r['arm']].append(r|{'score':scores[key(r)]})
    pairs=[];coverage=[]
    for benchmark in sorted({s for s,q in groups}):
        for mode in ['all_matched','shared_full_credit']:
            selected=[]
            for (source,q),by_arm in groups.items():
                if source!=benchmark:continue
                eligible={a:[r for r in by_arm.get(a,[]) if mode=='all_matched' or r['score']>=100-1e-8] for a in ARMS}
                if not all(eligible.values()):continue
                off=mean(r['interaction_length'] for r in eligible[ARMS[0]])
                persona=mean(mean(r['interaction_length'] for r in eligible[a]) for a in ARMS[1:])
                row=dict(source=benchmark,mode=mode,question=q,off=off,persona=persona,difference=persona-off)
                selected.append(row);pairs.append(row)
            coverage.append(dict(source=benchmark,mode=mode,questions=len(selected),off=mean(r['off'] for r in selected) if selected else None,persona=mean(r['persona'] for r in selected) if selected else None,difference=mean(r['difference'] for r in selected) if selected else None))
    write_csv(DATA/'all_benchmark_pairs.csv',pairs)
    write_csv(DATA/'all_benchmark_coverage.csv',coverage)
    return pairs,coverage

def calculate():
    p=BASE/'data/snapshot.json';raw=p.read_bytes();snap=json.loads(raw)
    calculate_all_benchmarks(snap)
    scores={key(r):r for r in snap['scores'] if r['score'] is not None}
    rows=[r|dict(score=scores[key(r)]['score']) for r in snap['traces'] if r['source']=='sciconvbench' and r.get('exclusion') is None and key(r) in scores]
    qs=sorted({r['task_id'] for r in rows});assert len(qs)==40 and len(rows)==440
    cells=[]
    for q in qs:
        for a in ARMS:
            sub=[r for r in rows if r['task_id']==q and r['arm']==a]
            assert sub and all(r['score'] in (0,100) for r in sub)
            succ=[r for r in sub if r['score']==100]
            cells.append(dict(question=q,arm=a,runs=len(sub),successful_runs=len(succ),success_rate=mean(r['score'] for r in sub),successful_mean_exchanges=mean(r['interaction_length'] for r in succ) if succ else None))
    common=[q for q in qs if all(c['successful_runs']>0 for c in cells if c['question']==q)]
    pairs=[]
    for q in common:
        sub=[c for c in cells if c['question']==q]
        off=next(c['successful_mean_exchanges'] for c in sub if c['arm']=='persona_off')
        persona=mean(c['successful_mean_exchanges'] for c in sub if c['arm']!='persona_off')
        pairs.append(dict(question=q,off=off,persona=persona,difference=persona-off))
    off=mean(r['off'] for r in pairs);persona=mean(r['persona'] for r in pairs)
    success=[mean(c['success_rate'] for c in cells if c['arm']=='persona_off'),mean(c['success_rate'] for c in cells if c['arm']!='persona_off')]
    result=dict(matched_questions=len(common),all_questions=len(qs),successful_exchanges_off=off,successful_exchanges_mean_persona=persona,difference=persona-off,relative_reduction_percent=100*(off-persona)/off,success_off=success[0],success_mean_persona=success[1],shorter_questions=sum(r['difference']< -1e-9 for r in pairs),longer_questions=sum(r['difference']>1e-9 for r in pairs),tied_questions=sum(abs(r['difference'])<=1e-9 for r in pairs),snapshot_sha256=hashlib.sha256(raw).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inference='descriptive; Panel A has 95% pointwise question-bootstrap CIs; no significance tests; success-conditioned lengths are not causal efficiency')
    write_csv(DATA/'question_setting.csv',cells);write_csv(DATA/'paired_questions.csv',pairs);write_json(DATA/'summary.json',result)
    distribution=[]
    for arm in ARMS:
        successes=[r for r in rows if r['arm']==arm and r['score']==100]
        assert successes
        for t,label in enumerate(['0','1','2+']):
            n=sum(min(r['interaction_length'],2)==t for r in successes)
            distribution.append(dict(arm=arm,exchanges=label,episodes=n,successful_episodes=len(successes),percent=100*n/len(successes)))
    bars=[]
    for series,arms in [('Persona-off',ARMS[:1]),('Mean persona',ARMS[1:])]:
        for label in ['0','1','2+']:
            sub=[r for r in distribution if r['arm'] in arms and r['exchanges']==label]
            bars.append(dict(series=series,exchanges=label,percent=mean(r['percent'] for r in sub),contributing_settings=len(sub)))
    write_csv(DATA/'successful_lengths_by_persona.csv',distribution)
    write_csv(DATA/'successful_lengths_split.csv',bars)
    return bars,pairs,result

def matched_distribution(pairs):
    snap=json.loads((BASE/'data/snapshot.json').read_text())
    scores={key(r):r['score'] for r in snap['scores'] if r['score'] is not None}
    groups=defaultdict(list)
    for r in snap['traces']:
        if r.get('exclusion') is None and scores.get(key(r),-1)>=100-1e-8:
            groups[(r['source'],r['task_id'],r['arm'])].append(r['interaction_length'])
    cells=[]
    for pair in pairs:
        for arm in ARMS:
            lengths=groups[(pair['source'],pair['question'],arm)]
            assert lengths
            for t,label in enumerate(['0','1','2','3+']):
                numerator=sum(min(v,3)==t for v in lengths)
                cells.append(dict(source=pair['source'],question=pair['question'],arm=arm,interactions=label,successful_runs=len(lengths),runs_in_bin=numerator,percent=100*numerator/len(lengths)))
    benchmarks=sorted({r['source'] for r in pairs})
    components=[];bars=[]
    for series,arms in [('Persona-off',ARMS[:1]),('Mean persona',ARMS[1:])]:
        for label in ['0','1','2','3+']:
            for benchmark in benchmarks:
                subset=[r for r in cells if r['source']==benchmark and r['arm'] in arms and r['interactions']==label]
                components.append(dict(source=benchmark,series=series,interactions=label,percent=mean(r['percent'] for r in subset)))
            bars.append(dict(series=series,exchanges=label,percent=mean(r['percent'] for r in components if r['series']==series and r['interactions']==label),contributing_benchmarks=len(benchmarks)))
    # Shared question resamples preserve off/persona and bin dependence.
    questions=sorted({r['question'] for r in pairs})
    assert len(benchmarks)==1 and benchmarks[0]=='sciconvbench'
    matrix=np.array([[mean(r['percent'] for r in cells if r['question']==q and r['interactions']==bar['exchanges'] and ((r['arm']=='persona_off')==(bar['series']=='Persona-off'))) for bar in bars] for q in questions])
    rng=np.random.default_rng(20261005)
    indices=rng.integers(0,len(questions),size=(20000,len(questions)))
    draws=matrix[indices].mean(axis=1)
    limits=np.quantile(draws,[.025,.975],axis=0)
    assert np.allclose(matrix.mean(axis=0),[bar['percent'] for bar in bars])
    for i,bar in enumerate(bars):
        bar.update(ci_low=float(limits[0,i]),ci_high=float(limits[1,i]),questions=len(questions),bootstrap_draws=20000,seed=20261005)
    write_csv(DATA/'matched_distribution_question_setting.csv',cells)
    write_csv(DATA/'matched_distribution_by_benchmark.csv',components)
    write_csv(DATA/'matched_distribution.csv',bars)
    return bars

def render():
    bars,pairs,summary=calculate()
    pairs=[r for r in csv.DictReader((DATA/'all_benchmark_pairs.csv').open()) if r['mode']=='shared_full_credit' and r['source']=='sciconvbench']
    coverage=[r for r in csv.DictReader((DATA/'all_benchmark_coverage.csv').open()) if r['mode']=='shared_full_credit' and r['source']=='sciconvbench' and int(r['questions'])>0]
    assert len(pairs)==29 and len(coverage)==1
    bars=matched_distribution(pairs)
    means=[mean(float(r[k]) for r in coverage) for k in ['off','persona']]
    summary['panel_a_bootstrap']={'unit':'whole matched question, shared across settings and bins','draws':20000,'seed':20261005,'interval':'95% percentile, pointwise; conditional on observed matched-success set'}
    summary['panel_a_questions']=len(pairs)
    summary['panel_a_weighting']='successful repeats within question/setting, equal personas, equal questions within benchmark, equal contributing benchmarks'
    summary['shared_full_credit_questions']=len(pairs)
    summary['shared_full_credit_mean_interactions_off']=means[0]
    summary['shared_full_credit_mean_interactions_persona']=means[1]
    summary['shared_full_credit_weighting']='equal benchmarks, equal questions within benchmark, equal personas, equal repeats within setting'
    write_json(DATA/'summary.json',summary)
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':10,'ytick.labelsize':9,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(8.4,3.7))
    fig.subplots_adjust(left=.085,right=.985,bottom=.22,top=.82,wspace=.38)
    for series,color,offset in zip(['Persona-off','Mean persona'],COLORS,[-.19,.19]):
        vals=[float(r['percent']) for r in bars if r['series']==series]
        selected=[r for r in bars if r['series']==series]
        errors=np.array([[r['percent']-r['ci_low'] for r in selected],[r['ci_high']-r['percent'] for r in selected]])
        axes[0].bar([i+offset for i in range(4)],vals,width=.36,color=color,label=series,yerr=errors,capsize=3,error_kw={'elinewidth':1,'capthick':1})

    axes[0].legend(loc='upper left',ncol=2,frameon=False,fontsize=9,handlelength=1.2,columnspacing=1)
    axes[0].set(title='A  Matched successes · 95% CI',xlabel='Clarification exchanges',ylabel='Share of successes (%)',xticks=[0,1,2,3],xticklabels=['0','1','2','3+'],ylim=(0,85),yticks=[0,20,40,60,80])
    for r in pairs:axes[1].plot([0,1],[float(r['off']),float(r['persona'])],color='#BBBBBB',alpha=.65,lw=.65,marker='o',ms=2,zorder=1)
    axes[1].plot([0,1],means,color='#333333',lw=2.5,zorder=3)
    axes[1].scatter([0,1],means,c=COLORS,s=65,zorder=4)
    axes[1].set(title=f"B  Shared successes · 29 questions",ylabel='Clarification exchanges',xticks=[0,1],xticklabels=[f'Persona-off\nMean {means[0]:.2f}',f'Mean persona\nMean {means[1]:.2f}'],xlim=(-.35,1.35),ylim=(-.4,10.5),yticks=[0,2,4,6,8,10])
    FIG.mkdir(parents=True,exist_ok=True);fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,axes=list(axes),panel_ids=['a','b'],row_groups=[['a','b']],column_groups=[],json_out=FIG/'alignment.json',tolerance_pt=1.5,gutter_tolerance_pt=1.5,strict=True)
    fig.savefig(FIG/'successful_interactions.pdf',bbox_inches='tight',pad_inches=.04)
    fig.savefig(FIG/'successful_interactions.svg',bbox_inches='tight',pad_inches=.04)
    fig.savefig(FIG/'successful_interactions.png',dpi=300,bbox_inches='tight',pad_inches=.04)
    write_json(FIG/'provenance.json',dict(inputs={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.glob('*')) if p.is_file()},code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),snapshot_sha256=summary['snapshot_sha256']))
    return fig

if __name__=='__main__':plt.close(render())
