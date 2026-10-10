"""Manuscript-sized rendering of the unchanged original-trial recovery summary."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
from audit_panel_alignment import require_matplotlib_panel_alignment
BASE=Path(__file__).resolve().parents[1]
ARMS=['persona_off','candidate_148','candidate_155','candidate_089','candidate_001','candidate_127']
LABELS=['Off','148','155','089','001','127']

def plot(summary,show=False):
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],
        'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':6.5,'ytick.labelsize':6.5,
        'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.6,
        'xtick.major.width':0.6,'ytick.major.width':0.6,'xtick.major.size':2.5,'ytick.major.size':2.5,
        'pdf.fonttype':42,'svg.fonttype':'none','legend.frameon':False})
    p=summary['views']['original']['panels']['all']
    fig,axes=plt.subplots(1,2,figsize=(7.2047244094,3.9370078740),gridspec_kw={'width_ratios':[6,5]})
    fig.subplots_adjust(left=.085,right=.985,bottom=.255,top=.81,wspace=.28)
    rows=[]
    specs=[(axes[0],ARMS,LABELS,[p['arms'][a]['recovery_share'] for a in ARMS],'Fact recovery','Recovery (%)'),
           (axes[1],ARMS[1:],LABELS[1:],[p['paired_recovery_vs_off'][a] for a in ARMS[1:]],'Paired effect versus off','Change (percentage points)')]
    for letter,(ax,arms,labels,stats,title,ylabel) in zip(['a','b'],specs):
        ax.set_title(title,loc='left',fontweight='normal',pad=12)
        ax.text(0,1,letter,transform=ax.transAxes+ScaledTranslation(-19/72,12/72,fig.dpi_scale_trans),fontsize=9,fontweight='bold',va='bottom')
        for i,(arm,s) in enumerate(zip(arms,stats)):
            assert s['mean'] is not None and len(s['ci95'])==2
            mean=s['mean']*100;lo,hi=np.array(s['ci95'])*100
            assert np.isfinite([mean,lo,hi]).all() and lo<=mean<=hi
            ax.bar(i,mean,width=.64,color='#9DA6AE' if arm=='persona_off' else '#528D96',edgecolor='none',zorder=2)
            ax.errorbar(i,mean,yerr=[[mean-lo],[hi-mean]],fmt='none',ecolor='#25343B',elinewidth=.75,capsize=2.5,capthick=.75,zorder=3)
            ax.annotate(f'{mean:.1f}\n[{lo:.1f}–{hi:.1f}]',(i,hi),xytext=(0,5),textcoords='offset points',ha='center',va='bottom',fontsize=5.5,linespacing=1.3)
            rows.append({'panel':letter,'persona':arm,'mean':mean,'ci95_low':lo,'ci95_high':hi,'cases':s['cases'],'episodes_or_pairs':s['episodes']})
        ax.set_xticks(range(len(labels)),[f'{label}\n{s["cases"]}/{s["episodes"]}' for label,s in zip(labels,stats)])
        ax.set_xlabel('Persona · cases/episodes' if letter=='a' else 'Persona · cases/matched pairs',labelpad=6)
        ax.set_ylabel(ylabel,labelpad=4)
        ax.set_axisbelow(True)
        ax.grid(False)
        ax.margins(x=.08)
    axes[0].set_ylim(0,124);axes[0].set_yticks([0,25,50,75,100])
    axes[1].set_ylim(-6,19);axes[1].set_yticks([-5,0,5,10,15]);axes[1].axhline(0,color='#68767D',lw=.7,zorder=1)
    fig.suptitle('SciConv fact recovery across researcher personas',x=.085,y=.975,ha='left',fontsize=10,fontweight='bold')
    fig.text(.085,.912,'GPT-6 Astra · low reasoning · three original trials · 20 disambiguation cases',fontsize=6.5,color='#4C5960')
    fig.text(.085,.10,'Bars: equal-weight case means across available trials. Whiskers and brackets: pointwise 95% CIs.',fontsize=6)
    fig.text(.085,.062,'20,000 study-cluster bootstrap draws within domains; paired contrasts match case and trial.',fontsize=6)
    fig.text(.085,.024,'Exploratory analysis; intervals are not multiplicity-corrected. No additional model calls.',fontsize=6,color='#4C5960')
    destination=BASE/'figures';qa=destination/'qa';qa.mkdir(exist_ok=True)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=qa/'fact_recovery.alignment.json',overlay_svg=qa/'fact_recovery.alignment.svg',
        tolerance_pt=1.5,gutter_tolerance_pt=1.5,require_panel_labels=True,strict=True,panel_ids=['a','b'],
        exemptions=[{'panels':['a'],'checks':['panel-width'],'reason':'Six absolute conditions versus five paired contrasts; equal category spacing.'}])
    # Fixed physical size: never crop or change layout after the alignment gate.
    fig.savefig(destination/'fact_recovery.pdf',facecolor='white')
    fig.savefig(destination/'fact_recovery.svg',facecolor='white')
    fig.savefig(destination/'fact_recovery.png',dpi=600,facecolor='white')
    fig.savefig(destination/'fact_recovery.tiff',dpi=600,facecolor='white')
    with (destination/'fact_recovery.source_data.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (qa/'input_summary.sha256').write_text(hashlib.sha256((BASE/'data/summary.json').read_bytes()).hexdigest()+'\n')
    if show:plt.show()
    else:plt.close(fig)
    return fig

if __name__=='__main__':plot(json.loads((BASE/'data/summary.json').read_text()))
