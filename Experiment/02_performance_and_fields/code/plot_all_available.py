#!/usr/bin/env python3
"""Preserved heatmap design expanded to all personas with completed trial jobs."""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,TwoSlopeNorm
from matplotlib.transforms import ScaledTranslation
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Experiment/shared'));sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
from analysis_utils import SOURCES,FAMILIES,NAMES,label,write_csv
from audit_panel_alignment import require_matplotlib_panel_alignment
BASE=ROOT/'Experiment/02_performance_and_fields';FIG=BASE/'figures/all_available'

def main():
    s=json.loads((BASE/'data/all_available/summary.json').read_text())
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':7,'axes.titlesize':8,'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    FIG.mkdir(parents=True,exist_ok=True);(FIG/'qa').mkdir(exist_ok=True)
    for kind in ['absolute','paired']:
        arms=s['arms'] if kind=='absolute' else s['arms'][1:]
        arrays=[np.array([[s[kind]['available'][a][field][g]['mean'] if s[kind]['available'][a][field][g]['mean'] is not None else np.nan for g in groups] for a in arms]) for field,groups in [('source',SOURCES),('family',FAMILIES)]]
        bound=max(.1,max(float(np.nanmax(np.abs(v))) for v in arrays))
        cmap=plt.get_cmap('Blues' if kind=='absolute' else 'BrBG').copy();cmap.set_bad('#E9E9E9')
        norm=Normalize(0,100) if kind=='absolute' else TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound)
        fig,axes=plt.subplots(2,1,figsize=(7.204724409,210/25.4))
        fig.subplots_adjust(left=.17,right=.96,bottom=.215,top=.875,hspace=.34)
        source=[]
        for i,(ax,field,groups,vals) in enumerate(zip(axes,['source','family'],[SOURCES,FAMILIES],arrays)):
            im=ax.imshow(vals,aspect='auto',cmap=cmap,norm=norm)
            labels=[f"{label(a)} · {len(s['coverage'][a]['trials_with_scores'])}T" for a in arms]
            ax.set_yticks(range(len(arms)),labels);ax.set_ylabel('Persona · trials')
            names=[NAMES[g].replace('Physical / engineering','Physical /\nengineering').replace('Social / humanities','Social /\nhumanities')+('*' if g=='asibench' else '') for g in groups]
            ax.set_xticks(range(len(groups)),names);ax.tick_params(length=0,pad=5)
            ax.set_title('By benchmark' if field=='source' else 'By super-family (descriptive source mixtures)',fontsize=8,pad=10)
            ax.text(0,1,chr(97+i),transform=ax.transAxes+ScaledTranslation(-28/72,13/72,fig.dpi_scale_trans),fontsize=8,weight='bold')
            for y,a in enumerate(arms):
                for x,g in enumerate(groups):
                    v=s[kind]['available'][a][field][g];mean=v['mean'];ci=v['ci95']
                    if mean is None:txt='No matched data' if kind=='paired' else 'No data';color='#17212B'
                    else:
                        ci_text=f'[{ci[0]:.2f}, {ci[1]:.2f}]' if ci else '[CI unavailable]'
                        txt=(f'{mean:+.2f}' if kind=='paired' else f'{mean:.2f}')+'\n'+ci_text
                        color='white' if (mean>65 if kind=='absolute' else abs(mean)>bound*.65) else '#17212B'
                    ax.text(x,y,txt,ha='center',va='center',fontsize=6,color=color,linespacing=1.4)
                    source.append(dict(arm=a,level=field,group=g,mean=mean,ci_low=ci[0] if ci else None,ci_high=ci[1] if ci else None,tasks=v['tasks'],episodes=v['episodes'],studies=v['studies'],trial_ids=','.join(map(str,v['trial_ids']))))
        cax=fig.add_axes([.30,.125,.50,.022]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('Native score normalized to 0–100' if kind=='absolute' else 'Persona − off (percentage points)',fontsize=6)
        fig.text(.17,.959,'Available performance across all eligible personas' if kind=='absolute' else 'Matched changes across all eligible personas',fontsize=10,weight='bold')
        fig.text(.17,.927,'Astra low · completed trial jobs only · mean [pointwise 95% CI]',fontsize=7)
        note='* ASI absolute scores mix historical judge versions; descriptive only.' if kind=='absolute' else '* ASI contrasts require corrected judges on both matched episodes.'
        fig.text(.17,.022,note+'\nT: trials with evaluable results; per-cell coverage varies. Repairs are not extra trials.\nTask-equal means; study-cluster CIs conditional on observed trials.\nUnequal coverage and source mixtures limit comparisons; no persona ranking.',fontsize=5.7,linespacing=1.5)
        name=f'{kind}_performance';write_csv(FIG/f'{name}.source_data.csv',source)
        fig.canvas.draw();require_matplotlib_panel_alignment(fig,json_out=str(FIG/f'qa/{name}.alignment.json'),overlay_svg=str(FIG/f'qa/{name}.alignment.svg'),strict=True,tolerance_pt=1.5,exclude_axes=[cax])
        fig.savefig(FIG/f'{name}.pdf',facecolor='white');fig.savefig(FIG/f'{name}.svg',facecolor='white')
        fig.savefig(FIG/f'{name}.png',dpi=600,facecolor='white');fig.savefig(FIG/f'{name}.tiff',dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
        plt.close(fig)
    print('Saved absolute and paired heatmaps for all eight eligible personas plus off.')

if __name__=='__main__':main()
