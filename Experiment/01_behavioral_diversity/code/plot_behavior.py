#!/usr/bin/env python3
"""Publication exports for nonsemantic behavioral analysis."""
import json
from collections import defaultdict
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.transforms import ScaledTranslation
from audit_panel_alignment import require_matplotlib_panel_alignment
from analyze_behavior import BASE, DATA, HEAT_METRICS, REPEAT_METRICS, METRICS
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'Experiment/shared'))
from analysis_utils import ARMS,label,write_csv,paired,sha

FIG=BASE/'figures/behavior'
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':7,'axes.titlesize':8,
    'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,'pdf.fonttype':42,
    'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6})

def export(fig,name,exclude_axes=None):
    FIG.mkdir(parents=True,exist_ok=True);(FIG/'qa').mkdir(exist_ok=True)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa'/f'{name}.alignment.json'),
        overlay_svg=str(FIG/'qa'/f'{name}.alignment.svg'),tolerance_pt=1.5,strict=True,exclude_axes=exclude_axes or [])
    fig.savefig(FIG/f'{name}.pdf',facecolor='white')
    fig.savefig(FIG/f'{name}.svg',facecolor='white')
    fig.savefig(FIG/f'{name}.png',dpi=600,facecolor='white')
    fig.savefig(FIG/f'{name}.tiff',dpi=600,facecolor='white')
    plt.close(fig)

def main():
    s=json.loads((DATA/'summary.json').read_text())
    values=np.array([[s['paired'][m]['all'][a]['standardized_delta'] if s['paired'][m]['all'][a]['standardized_delta'] is not None else np.nan for m in HEAT_METRICS] for a in ARMS[1:]])
    bound=max(.1,float(np.nanmax(np.abs(values))))
    fig,ax=plt.subplots(figsize=(7.204724409,108/25.4))  # 183 mm wide
    fig.subplots_adjust(left=.09,right=.95,bottom=.30,top=.84)
    cmap=plt.get_cmap('BrBG').copy();cmap.set_bad('#E9E9E9')
    im=ax.imshow(values,cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound),aspect='auto')
    ax.set_yticks(range(5),[label(a) for a in ARMS[1:]]);ax.set_ylabel('Persona')
    ax.set_xticks(range(6),['Simulator\ncharacters/reply','Completed\nexchanges','Extra approach\nreviews','Revision\nrequests','Clarification\nrecall (pp)','Clarification\nprecision (pp)'])
    ax.tick_params(length=0,pad=6)
    source=[]
    for i,a in enumerate(ARMS[1:]):
        for j,m in enumerate(HEAT_METRICS):
            v=s['paired'][m]['all'][a];mean=v['mean'];lo,hi=v['ci95']
            f='.0f' if m=='simulator_chars' else '.3f' if m in ['extra_plan_reviews','revision_requests','exchanges'] else '.1f'
            color='white' if np.isfinite(values[i,j]) and abs(values[i,j])>bound*.64 else '#17212B'
            ax.text(j,i,f'{mean:+{f}}\n[{lo:{f}}, {hi:{f}}]',ha='center',va='center',fontsize=5.5,color=color,linespacing=1.5)
            source.append(dict(arm=a,metric=m,mean=mean,ci_low=lo,ci_high=hi,standardized_delta=v['standardized_delta'],tasks=v['tasks'],episode_pairs=v['episodes']))
    cax=fig.add_axes([.26,.17,.53,.035]);cb=fig.colorbar(im,cax=cax,orientation='horizontal')
    cb.set_label('Color: paired change / matched baseline task SD',fontsize=6)
    fig.text(.09,.94,'Behavior changes relative to persona-off',fontsize=10,weight='bold')
    fig.text(.09,.885,'Cell text: raw paired change [95% CI] · original Astra trials',fontsize=7)
    fig.text(.09,.025,'Source-balanced means; matched task/trial pairs; study-cluster bootstrap.\nPositive and negative changes have no universal desirable direction. Gray: undefined baseline SD.',fontsize=6,linespacing=1.5)
    write_csv(FIG/'behavior_effects.source_data.csv',source)
    export(fig,'behavior_effects',exclude_axes=[cax])
    fig,axes=plt.subplots(2,2,figsize=(7.204724409,145/25.4))
    fig.subplots_adjust(left=.11,right=.97,bottom=.13,top=.84,wspace=.32,hspace=.65)
    source=[]
    titles=['Reply-length variation','Extra approach-review variation','Revision-request variation','SciConv question-count variation']
    cats=['baseline_within','persona_within','between_personas']
    for i,(ax,m) in enumerate(zip(axes.flat,REPEAT_METRICS)):
        stats=[s['repeat_variation'][m][k] for k in cats]
        means=np.array([v['mean'] for v in stats]);lo=np.array([v['ci95'][0] for v in stats]);hi=np.array([v['ci95'][1] for v in stats]);x=np.arange(3)
        ax.bar(x,means,width=.58,color=['#90969C','#A7C9C4','#267C72'],zorder=2)
        ax.vlines(x,lo,hi,color='#17212B',lw=.8,zorder=3)
        ax.hlines(lo,x-.07,x+.07,color='#17212B',lw=.8,zorder=3);ax.hlines(hi,x-.07,x+.07,color='#17212B',lw=.8,zorder=3)
        upper=max(float(hi.max()),.01);ax.set_ylim(0,upper*1.65)
        fmt='.0f' if m=='simulator_chars' else '.2f'
        for j,v in enumerate(stats):
            ax.text(j,hi[j]+upper*.06,f"{v['mean']:{fmt}}\n[{lo[j]:{fmt}}, {hi[j]:{fmt}}]",ha='center',va='bottom',fontsize=5.5,linespacing=1.5)
            source.append(dict(metric=m,comparison=cats[j],mean=v['mean'],ci_low=lo[j],ci_high=hi[j],tasks=v['tasks']))
        ax.set_xticks(x,['Within\noff','Within\npersonas','Between\npersonas'])
        ax.set_ylabel('Mean absolute difference\n'+('characters/reply' if m=='simulator_chars' else 'count'))
        ax.set_title(titles[i]+f" (n={stats[0]['tasks']} tasks)",fontsize=7,pad=11)
        ax.text(0,1,chr(97+i),transform=ax.transAxes+ScaledTranslation(-25/72,15/72,fig.dpi_scale_trans),fontsize=8,weight='bold')
    fig.text(.11,.95,'Between-persona differences versus repeat variation',fontsize=10,weight='bold')
    fig.text(.11,.895,'Same complete task panel within each metric · mean [95% CI]',fontsize=7)
    fig.text(.11,.035,'Three trials per task/condition. Pairwise run distances average within task before study resampling.\nSelected persona panel; no semantic or realism inference. Exact excess-distance intervals are in the report.',fontsize=6,linespacing=1.5)
    write_csv(FIG/'repeat_variation.source_data.csv',source)
    export(fig,'repeat_variation')
    # All matched task effects, without subsampling; a complement to mean CIs.
    rows=[r for r in json.loads((DATA/'snapshot.json').read_text())['episodes'] if r['eligible']]
    task_points=[]
    for a in ARMS[1:]:
        grouped=defaultdict(list)
        for r in paired(rows,'simulator_chars',a):
            grouped[(r['source'],r['task_id'])].append(r['value'])
        task_points.extend(dict(arm=a,source=k[0],task_id=k[1],value=float(np.mean(v)),trial_pairs=len(v)) for k,v in grouped.items())
    fig,ax=plt.subplots(figsize=(7.204724409,112/25.4))
    fig.subplots_adjust(left=.13,right=.97,bottom=.20,top=.81)
    lower=min(r['value'] for r in task_points);upper=max(r['value'] for r in task_points);span=upper-lower
    for i,a in enumerate(ARMS[1:]):
        sub=[r for r in task_points if r['arm']==a]
        jitter=[(int(sha((r['source']+r['task_id']).encode())[:8],16)/0xffffffff-.5)*.46 for r in sub]
        ax.scatter(i+np.array(jitter),[r['value'] for r in sub],s=6,color='#6B777C',alpha=.30,linewidths=0,zorder=2)
        stat=s['paired']['simulator_chars']['all'][a];lo,hi=stat['ci95']
        ax.vlines(i,lo,hi,color='#126C63',lw=1.7,zorder=4)
        ax.hlines([lo,hi],i-.07,i+.07,color='#126C63',lw=1.2,zorder=4)
        ax.scatter([i],[stat['mean']],s=24,color='#126C63',edgecolor='white',linewidth=.6,zorder=5)
        ax.text(i,upper+span*.07,f"{stat['mean']:+.0f} [{lo:.0f}, {hi:.0f}]\nn={stat['tasks']} tasks",ha='center',va='bottom',fontsize=6,linespacing=1.5)
    ax.set_ylim(lower-span*.05,upper+span*.25);ax.axhline(0,color='#647078',lw=.6,zorder=1)
    ax.set_xticks(range(5),[label(a) for a in ARMS[1:]])
    ax.set_xlabel('Persona');ax.set_ylabel('Reply-length change vs off (characters)')
    fig.text(.13,.94,'Task-level distribution of reply-length changes',fontsize=10,weight='bold')
    fig.text(.13,.885,'Every gray point is one matched task; teal shows source-balanced mean and 95% CI',fontsize=6.5)
    fig.text(.13,.04,'Task effects average matched trial differences. All points are shown; means give benchmarks equal weight.\nCharacter counts vary with language and workflow. Script-restricted sensitivity is reported separately.',fontsize=6,linespacing=1.5)
    write_csv(FIG/'reply_length_distribution.source_data.csv',task_points)
    export(fig,'reply_length_distribution')

if __name__=='__main__':main()
