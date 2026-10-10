"""Available scores and matched changes; consumes frozen estimates without reanalysis."""
import sys,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,TwoSlopeNorm
from matplotlib.patches import Rectangle
from plot_all_available import BASE,FIG,write_csv,SOURCES,FAMILIES,NAMES,label,require_matplotlib_panel_alignment

def main():
    s=json.loads((BASE/'data/all_available/summary.json').read_text());arms=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'xtick.labelsize':6,'ytick.labelsize':6,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,2,figsize=(260/25.4,165/25.4))
    fig.subplots_adjust(left=.085,right=.98,top=.87,bottom=.23,wspace=.25,hspace=.26)
    bound=max(abs(s['paired']['available'][a][f][g]['mean']) for a in arms[1:] for f,gs in [('source',SOURCES),('family',FAMILIES)] for g in gs if s['paired']['available'][a][f][g]['mean'] is not None)
    records=[];images=[]
    for col,kind in enumerate(['absolute','paired']):
        cmap=plt.get_cmap('Blues' if col==0 else 'BrBG').copy();cmap.set_bad('#EEEEEE')
        norm=Normalize(0,100) if col==0 else TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound)
        for row,(field,groups) in enumerate([('source',SOURCES),('family',FAMILIES)]):
            ax=axes[row,col];v=np.full((len(arms),len(groups)),np.nan)
            for y,a in enumerate(arms):
                for x,g in enumerate(groups):
                    if col==1 and y==0:continue
                    z=s[kind]['available'][a][field][g]
                    if z['mean'] is not None:v[y,x]=z['mean']
            im=ax.imshow(v,aspect='auto',cmap=cmap,norm=norm,interpolation='nearest')
            ax.set_yticks(range(len(arms)),[f"{label(a)} · {len(s['coverage'][a]['trials_with_scores'])}T" for a in arms] if col==0 else [])
            names=[NAMES[g].replace('Physical / engineering','Physical /\nengineering').replace('Social / humanities','Social /\nhumanities')+('*' if g=='asibench' else '') for g in groups]
            ax.set_xticks(range(len(groups)),names);ax.tick_params(length=0,pad=5)
            if col==0:ax.set_ylabel('Persona · trials',fontsize=7)
            ax.set_title('By benchmark' if row==0 else 'By super-family',fontsize=8,pad=8)
            for spine in ax.spines.values():spine.set_visible(False)
            for y,a in enumerate(arms):
                for x,g in enumerate(groups):
                    if col==1 and y==0:
                        ax.text(x,y,'Reference',ha='center',va='center',fontsize=6,color='#555555');continue
                    z=s[kind]['available'][a][field][g];m=z['mean'];ci=z['ci95']
                    txt='No matched data' if col else 'No data';color='#17212B'
                    if m is not None:
                        txt=(f'{m:+.2f}' if col else f'{m:.2f}')+'\n'+(f'[{ci[0]:.2f}, {ci[1]:.2f}]' if ci else 'CI unavailable')
                        color='white' if (abs(m)>bound*.65 if col else m>65) else color
                    ax.text(x,y,txt,ha='center',va='center',fontsize=5.8,color=color,linespacing=1.35)
                    records.append(dict(kind=kind,arm=a,level=field,group=g,mean=m,ci_low=ci[0] if ci else None,ci_high=ci[1] if ci else None,tasks=z['tasks'],episodes=z['episodes'],studies=z['studies'],trial_ids=','.join(map(str,z['trial_ids']))))
        images.append(im)
    color_axes=[]
    for col,title in enumerate(['A  Available performance','B  Task–trial-matched change']):
        pos=axes[0,col].get_position();center=(pos.x0+pos.x1)/2
        fig.text(center,.95,title,ha='center',fontsize=10,weight='bold')
        fig.text(center,.923,'Mean [pointwise 95% CI]' if col==0 else 'Persona − off [pointwise 95% CI]',ha='center',fontsize=7)
        ca=fig.add_axes([pos.x0+.06,.14,pos.width-.12,.015]);color_axes.append(ca)
        cb=fig.colorbar(images[col],cax=ca,orientation='horizontal')
        cb.set_label('Native score normalized to 0–100' if col==0 else 'Difference on 0–100 score scale',fontsize=7);cb.ax.tick_params(labelsize=6)
    fig.text(.085,.02,'* ASI: available scores mix historical judges; matched changes require corrected judges on both episodes.\nCoverage differs between panels and personas; subtracting left-panel scores need not reproduce right-panel changes.\nStudy-cluster bootstrap, conditional on observed trials. Super-families mix native metrics. T: trials with evaluable results.',fontsize=6,linespacing=1.5)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa/combined_performance.alignment.json'),overlay_svg=str(FIG/'qa/combined_performance.alignment.svg'),strict=True,tolerance_pt=1.5,exclude_axes=color_axes)
    write_csv(FIG/'combined_performance.source_data.csv',records)
    fig.savefig(FIG/'combined_performance.pdf',facecolor='white')
    fig.savefig(FIG/'combined_performance.svg',facecolor='white')
    fig.savefig(FIG/'combined_performance.png',dpi=600,facecolor='white')
    fig.savefig(FIG/'combined_performance.tiff',dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
    plt.close(fig)

if __name__=='__main__':main()
