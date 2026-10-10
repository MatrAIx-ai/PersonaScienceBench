"""Split the existing metric-suite figure; preserve its estimators."""
# Notebook-only figure revision: actor only, windows=6, minimum matching positions=3.
# Frozen selected-grid summary below; raw computation and all 27 combinations follow in this notebook.
from pathlib import Path
import sys, json, tempfile, contextlib, io, subprocess
from IPython.display import display, Image
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'Experiment/shared/task_selection.csv').exists())
sys.path.insert(0,str(ROOT/'Experiment/09_offline_metric_suite/code'))
import plot
selected_grid_summary = {'candidate_001': {'ci95': [11.27258234647533, 13.582045277464605], 'episodes': 227, 'mean': 12.358495061754986, 'singleton_sources': [], 'source_counts': {'asibench': 6, 'bixbench': 27, 'discoverybench': 21, 'expbench': 6, 'sciconvbench': 19}, 'studies': 56, 'studies_by_source': {'asibench': 6, 'bixbench': 20, 'discoverybench': 5, 'expbench': 6, 'sciconvbench': 19}, 'tasks': 79}, 'candidate_003': {'ci95': [6.824208579436393, 9.304061246857772], 'episodes': 79, 'mean': 8.026294543393588, 'singleton_sources': [], 'source_counts': {'asibench': 6, 'bixbench': 27, 'discoverybench': 21, 'expbench': 6, 'sciconvbench': 19}, 'studies': 56, 'studies_by_source': {'asibench': 6, 'bixbench': 20, 'discoverybench': 5, 'expbench': 6, 'sciconvbench': 19}, 'tasks': 79}, 'candidate_046': {'ci95': [14.099854316056147, 17.663390033502466], 'episodes': 79, 'mean': 15.940255616203519, 'singleton_sources': [], 'source_counts': {'asibench': 6, 'bixbench': 27, 'discoverybench': 21, 'expbench': 6, 'sciconvbench': 19}, 'studies': 56, 'studies_by_source': {'asibench': 6, 'bixbench': 20, 'discoverybench': 5, 'expbench': 6, 'sciconvbench': 19}, 'tasks': 79}, 'candidate_155': {'ci95': [13.12154955069449, 15.746704688908217], 'episodes': 230, 'mean': 14.44103721096088, 'singleton_sources': [], 'source_counts': {'asibench': 6, 'bixbench': 27, 'discoverybench': 21, 'expbench': 6, 'sciconvbench': 19}, 'studies': 56, 'studies_by_source': {'asibench': 6, 'bixbench': 20, 'discoverybench': 5, 'expbench': 6, 'sciconvbench': 19}, 'tasks': 79}, 'match_fraction': 0.5, 'off_minus_largest_persona': -2.441021225345816, 'off_rank': 3, 'persona_off': {'ci95': [12.133342696672829, 14.880134166029377], 'episodes': 233, 'mean': 13.499234390857703, 'singleton_sources': [], 'source_counts': {'asibench': 6, 'bixbench': 27, 'discoverybench': 21, 'expbench': 6, 'sciconvbench': 19}, 'studies': 56, 'studies_by_source': {'asibench': 6, 'bixbench': 20, 'discoverybench': 5, 'expbench': 6, 'sciconvbench': 19}, 'tasks': 79}, 'threshold': 3, 'window': 6}


def actor_only_points(ax):
    selected = next((r for r in globals().get('grid_search_result',{}).get('grid',[]) if r['window']==6 and r['threshold']==3), selected_grid_summary)
    largest=0
    for i,arm in enumerate(plot.ARMS):
        row=selected[arm];lo,hi=row['ci95'];largest=max(largest,hi)
        ax.errorbar(row['mean'],i,xerr=[[row['mean']-lo],[hi-row['mean']]],fmt='o',color=plot.COLORS[i],markersize=4,capsize=2,elinewidth=.9)
    ax.set_yticks(range(5),plot.LABELS);ax.set_ylim(4.6,-.6)
    ax.set_xlim(0,largest*1.12);ax.set_xlabel('Matched Windows (%)');ax.tick_params(length=2)

def unsuccessful_recovery_points(ax):
    from analyze import task_values
    snap=json.loads((plot.DATA/'snapshot.json').read_text())
    ax.clear()
    counts=[]
    for i,arm in enumerate(plot.ARMS):
        available=[r for r in snap['recovery'] if r['arm']==arm and r['recovery'] is not None]
        failed=[r for r in available if r['FRR']==0]
        rows=task_values([r|dict(complete_recovery=100*int(r['facts_recovered']==r['facts_total'])) for r in failed],'complete_recovery')
        y=plot.np.array([r['value'] for r in rows])
        assert len(y), 'No eligible unsuccessful cases for this setting.'
        mean=float(plot.np.mean(y))
        ax.bar(i,mean,width=.66,color=plot.COLORS[i],alpha=.8,edgecolor=plot.COLORS[i],linewidth=.8,zorder=3)
        counts.append(dict(setting=plot.LABELS[i],failed_runs=len(failed),total_runs=len(available),cases=len(y),mean=mean))
    ax.set_xticks(range(5),[r['setting'] for r in counts])
    ax.set_xlim(-.6,4.6);ax.set_ylim(-5,108);ax.set_yticks([0,25,50,75,100])
    ax.set_ylabel('Unsuccessful runs recovering\nevery fact (%)');ax.tick_params(length=2)
    globals()['unsuccessful_recovery_summary']=counts


def success_by_length(ax):
    snap=json.loads((plot.DATA/'snapshot.json').read_text())
    def key(r):return (r['source'],r['task_id'],r['arm'],r['trial'])
    outcomes={key(r):r for r in snap['scores'] if r['score'] is not None}
    joined=[]
    for r in snap['traces']:
        if r.get('exclusion') is None and key(r) in outcomes:
            score=outcomes[key(r)]['score']
            joined.append(r|dict(score=score))
    assert len(joined)==1958
    ax.clear();rows=[];source_rows=[]
    max_length=max(r['interaction_length'] for r in joined)
    xx=plot.np.arange(max_length+1)
    for i,arm in enumerate(plot.ARMS):
        rates=[]
        arm_runs=[r for r in joined if r['arm']==arm]
        denominator=len(arm_runs)
        for length in xx:
            sub=[r for r in joined if r['arm']==arm and r['interaction_length']<=length]
            score_sum=sum(r['score'] for r in sub)
            rate=score_sum/denominator
            rates.append(rate)
            rows.append(dict(setting=plot.LABELS[i],interactions=int(length),runs=denominator,finished_runs=len(sub),cases=len({(r['source'],r['task_id']) for r in arm_runs}),score_sum=score_sum,rate=rate))
            for source in plot.SOURCES:
                ss=[r for r in sub if r['source']==source]
                source_rows.append(dict(setting=plot.LABELS[i],source=source,interactions=int(length),runs=len(ss),score_sum=sum(r['score'] for r in ss),mean=plot.np.mean([r['score'] for r in ss]).item() if ss else None))
        assert plot.np.all(plot.np.diff(rates)>=-1e-10)
        assert abs(rates[-1]-plot.np.mean([r['score'] for r in arm_runs]))<1e-9
        ax.plot(xx,rates,color=plot.COLORS[i],marker=['o','s','^','D','v'][i],markersize=4,lw=1,label=plot.LABELS[i],linestyle=['-','--',':','-','-'][i],mfc='white' if i==0 else plot.COLORS[i])
    ax.set_xlim(-.35,max_length+.35);ax.set_ylim(-5,108)
    ax.set_xticks(xx);ax.set_yticks([0,25,50,75,100])
    ax.set_xlabel('Observed interactions (≤ t)');ax.set_ylabel('Avg Score before t');ax.tick_params(length=2)
    ax.legend(loc='upper left',frameon=False,ncol=3,fontsize=6,columnspacing=1,handlelength=1.5)
    globals().setdefault('success_length_summary',[]).extend(rows)
    globals().setdefault('success_length_source_summary',[]).extend(source_rows)



OUT=ROOT/'Experiment/09_offline_metric_suite/figures/metric_suite_split'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import write_csv,write_json

def export(fig,name,axes):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.canvas.draw()
    if len(axes)>1:
        plot.require_matplotlib_panel_alignment(fig,axes=axes,panel_ids=['a','b'],row_groups=[['a','b']],column_groups=[],json_out=OUT/f'{name}.alignment.json',tolerance_pt=1.5,gutter_tolerance_pt=1.5,strict=True)
    else:write_json(OUT/f'{name}.alignment.json',{'status':'not_applicable','reason':'single axes'})
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight',pad_inches=.035)
    fig.savefig(OUT/f'{name}.svg',bbox_inches='tight',pad_inches=.035)
    fig.savefig(OUT/f'{name}.png',dpi=300,bbox_inches='tight',pad_inches=.035)

def render():
    plot.plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42})
    ab,axs=plot.plt.subplots(1,2,figsize=(7.2,3.0))
    ab.subplots_adjust(left=.08,right=.98,bottom=.19,top=.85,wspace=.55)
    actor_only_points(axs[0]);unsuccessful_recovery_points(axs[1])
    axs[0].set_title('A  Actor self-repetition',pad=8)
    axs[1].set_title('B  Fact recovery given failure',pad=8)
    export(ab,'metric_suite_AB',list(axs))
    c,ax=plot.plt.subplots(figsize=(4.2,4.2))
    c.subplots_adjust(left=.18,right=.98,bottom=.18,top=.97)
    globals()['success_length_summary']=[]
    globals()['success_length_source_summary']=[]
    success_by_length(ax)
    ax.set_xlabel('Observed interactions (≤ t)',fontsize=12)
    ax.set_ylabel('Avg Score before t',fontsize=13)
    ax.tick_params(axis='both',labelsize=11,length=3)
    ax.set_xticks(range(0,13,2))
    ax.legend(loc='upper left',frameon=False,ncol=3,fontsize=10,columnspacing=.9,handlelength=1.5,handletextpad=.4)
    for line in ax.lines:
        line.set_linewidth(1.5)
        line.set_markersize(5)
    export(c,'metric_suite_C',[ax])
    write_csv(OUT/'panel_B.source_data.csv',unsuccessful_recovery_summary)
    write_csv(OUT/'panel_C.source_data.csv',success_length_summary)
    write_csv(OUT/'panel_C_benchmark_composition.source_data.csv',success_length_source_summary)
    write_json(OUT/'panel_A.source_data.json',selected_grid_summary)
    return ab,c

if __name__=='__main__':
    for fig in render():plot.plt.close(fig)
