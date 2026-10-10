#!/usr/bin/env python3
"""Original matched benchmark and family heatmap, preserved alongside the ARS alternative."""
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.transforms import ScaledTranslation
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Experiment/shared'))
sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
from analysis_utils import ARMS,SOURCES,FAMILIES,NAMES,label,write_csv
from audit_panel_alignment import require_matplotlib_panel_alignment
BASE=ROOT/'Experiment/02_performance_and_fields';FIG=BASE/'figures/consolidated'

def main():
    s=json.loads((BASE/'data/consolidated/summary.json').read_text())
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':7,'axes.titlesize':8,
        'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,'pdf.fonttype':42,
        'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(7.204724409,160/25.4))
    fig.subplots_adjust(left=.11,right=.95,bottom=.23,top=.87,hspace=.47)
    arrays=[]
    for field,groups in [('source',SOURCES),('family',FAMILIES)]:
        arrays.append(np.array([[s['paired']['original'][a][field][g]['mean'] if s['paired']['original'][a][field][g]['mean'] is not None else np.nan for g in groups] for a in ARMS[1:]]))
    bound=max(.1,max(float(np.nanmax(np.abs(v))) for v in arrays))
    cmap=plt.get_cmap('BrBG').copy();cmap.set_bad('#E9E9E9');source=[]
    for i,(ax,field,groups,vals) in enumerate(zip(axes,['source','family'],[SOURCES,FAMILIES],arrays)):
        im=ax.imshow(vals,aspect='auto',cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound))
        ax.set_yticks(range(5),[label(a) for a in ARMS[1:]]);ax.set_ylabel('Persona')
        names=[NAMES[g].replace('Physical / engineering','Physical /\nengineering').replace('Social / humanities','Social /\nhumanities')+('*' if g=='asibench' else '') for g in groups]
        ax.set_xticks(range(len(groups)),names);ax.tick_params(length=0,pad=6)
        ax.set_title('By benchmark' if field=='source' else 'By super-family (descriptive source mixtures)',fontsize=8,pad=11)
        ax.text(0,1,chr(97+i),transform=ax.transAxes+ScaledTranslation(-25/72,15/72,fig.dpi_scale_trans),fontsize=8,weight='bold')
        for y,a in enumerate(ARMS[1:]):
            for x,g in enumerate(groups):
                v=s['paired']['original'][a][field][g]
                if v['mean'] is None:
                    ax.text(x,y,'No matched data',ha='center',va='center',fontsize=5.5);continue
                lo,hi=v['ci95'];color='white' if abs(vals[y,x])>bound*.65 else '#17212B'
                ax.text(x,y,f"{v['mean']:+.2f}\n[{lo:.2f}, {hi:.2f}]",ha='center',va='center',fontsize=5.5,color=color,linespacing=1.5)
                source.append(dict(level=field,group=g,arm=a,mean=v['mean'],ci_low=lo,ci_high=hi,tasks=v['tasks'],episode_pairs=v['episodes']))
    cax=fig.add_axes([.29,.135,.48,.025]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('Persona − off (percentage points)',fontsize=6)
    fig.text(.11,.955,'Scientific outcomes on matched tasks and trials',fontsize=10,weight='bold')
    fig.text(.11,.918,'Original Astra trials · cell text: paired change [95% CI]',fontsize=7)
    fig.text(.11,.012,'* ASI: configured-judge bridge on both episodes; legacy/unknown versions excluded.\nStudy-cluster bootstrap within source; varying pairwise coverage. Family metrics have distinct native meanings.\nPointwise intervals; no multiplicity-corrected significance or persona ranking claim.',fontsize=6,linespacing=1.5)
    FIG.mkdir(parents=True,exist_ok=True);(FIG/'qa').mkdir(exist_ok=True)
    write_csv(FIG/'matched_performance.source_data.csv',source)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa/matched_performance.alignment.json'),overlay_svg=str(FIG/'qa/matched_performance.alignment.svg'),tolerance_pt=1.5,strict=True,exclude_axes=[cax])
    fig.savefig(FIG/'matched_performance.pdf',facecolor='white')
    fig.savefig(FIG/'matched_performance.svg',facecolor='white')
    fig.savefig(FIG/'matched_performance.png',dpi=600,facecolor='white')
    fig.savefig(FIG/'matched_performance.tiff',dpi=600,facecolor='white')
    plt.close(fig)

if __name__=='__main__':main()
