"""M(t): final native score averaged only over episodes completed by t."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/09_offline_metric_suite'
DATA=BASE/'data/completed_mean'
FIG=BASE/'figures/completed_mean'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import write_csv,write_json
sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
from audit_panel_alignment import require_matplotlib_panel_alignment
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
LABELS=['Persona-off','155','001','003','046']
COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']

def calculate():
    p=BASE/'data/snapshot.json';raw=p.read_bytes();s=json.loads(raw)
    key=lambda r:(r['source'],r['task_id'],r['arm'],r['trial'])
    scores={key(r):r['score'] for r in s['scores'] if r['score'] is not None}
    rows=[r|{'score':scores[key(r)]} for r in s['traces'] if r.get('exclusion') is None and key(r) in scores]
    assert len(rows)==1958
    cells=[];composition=[]
    for arm in ARMS:
        all_runs=[r for r in rows if r['arm']==arm]
        for t in range(max(r['interaction_length'] for r in rows)+1):
            sub=[r for r in all_runs if r['interaction_length']<=t]
            total=sum(r['score'] for r in sub)
            cells.append(dict(arm=arm,t=t,finished_runs=len(sub),all_runs=len(all_runs),score_sum=total,mean=total/len(sub) if sub else None,fixed_denominator_score=total/len(all_runs),benchmarks=len({r['source'] for r in sub}),questions=len({(r['source'],r['task_id']) for r in sub})))
            for benchmark in sorted({r['source'] for r in rows}):
                ss=[r for r in sub if r['source']==benchmark]
                composition.append(dict(arm=arm,t=t,source=benchmark,finished_runs=len(ss),score_sum=sum(r['score'] for r in ss),mean=np.mean([r['score'] for r in ss]).item() if ss else None))
    write_csv(DATA/'estimates.csv',cells);write_csv(DATA/'benchmark_composition.csv',composition)
    write_json(DATA/'provenance.json',dict(input_sha256=hashlib.sha256(raw).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),episodes=len(rows),formula='sum(final native scores where length<=t) / count(length<=t)',weighting='equal completed episodes within setting; matches original Panel C except denominator',uncertainty='not computed'))
    return cells

def render():
    cells=calculate()
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':10,'axes.labelsize':10,'axes.titlesize':11,'xtick.labelsize':9,'ytick.labelsize':9,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7.2,3.6));fig.subplots_adjust(left=.11,right=.98,bottom=.18,top=.77)
    for arm,label,color,marker in zip(ARMS,LABELS,COLORS,['o','s','^','D','v']):
        sub=[r for r in cells if r['arm']==arm]
        ax.plot([r['t'] for r in sub],[r['mean'] if r['mean'] is not None else np.nan for r in sub],color=color,marker=marker,ms=4,lw=1.6,label=label,mfc='white' if arm=='persona_off' else color)
    ax.set(xlabel='Completed by interaction t',ylabel='Mean native score M(t)',xlim=(-.2,max(r['t'] for r in cells)+.2),ylim=(-2,105),xticks=range(max(r['t'] for r in cells)+1),yticks=[0,20,40,60,80,100])
    fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.54,.98),ncol=5,frameon=False,fontsize=9,handlelength=1.5,columnspacing=1)
    FIG.mkdir(parents=True,exist_ok=True);fig.canvas.draw()
    write_json(FIG/'alignment.json',{'status':'not_applicable','reason':'single data axes; no inter-panel alignment'})
    fig.savefig(FIG/'completed_mean.pdf',bbox_inches='tight',pad_inches=.04)
    fig.savefig(FIG/'completed_mean.svg',bbox_inches='tight',pad_inches=.04)
    fig.savefig(FIG/'completed_mean.png',dpi=300,bbox_inches='tight',pad_inches=.04)
    return fig

if __name__=='__main__':plt.close(render())
