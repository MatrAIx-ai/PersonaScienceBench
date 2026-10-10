"""Absolute score heatmaps plus nine categorical-significance pairwise matrices."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch
from plot_all_available import BASE,FIG,SOURCES,FAMILIES,NAMES,label,write_csv,require_matplotlib_panel_alignment
from pairwise_performance import ARMS,DEST

def main(dest=DEST, fig_dir=FIG, test_label="Study-cluster sign flip"):
    FIG=fig_dir
    FIG.mkdir(parents=True,exist_ok=True);(FIG/"qa").mkdir(exist_ok=True)
    s=json.loads((BASE/'data/all_available/summary.json').read_text());pairs=json.loads((dest/'summary.json').read_text())
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':7,'xtick.labelsize':6,'ytick.labelsize':6,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig=plt.figure(figsize=(310/25.4,215/25.4))
    left=fig.add_gridspec(2,1,left=.06,right=.355,bottom=.22,top=.88,hspace=.32)
    right=fig.add_gridspec(3,3,left=.435,right=.98,bottom=.19,top=.88,wspace=.38,hspace=.47)
    la=[];ra=[];data=[]
    for row,(field,groups) in enumerate([('source',SOURCES),('family',FAMILIES)]):
        ax=fig.add_subplot(left[row]);la.append(ax)
        values=np.array([[s['absolute']['available'][a][field][g]['mean'] for g in groups] for a in ARMS],float)
        im=ax.imshow(values,cmap='Blues',vmin=0,vmax=100,aspect='auto')
        ax.set_yticks(range(5),[f"{label(a)} · {len(s['coverage'][a]['trials_with_scores'])}T" for a in ARMS])
        ax.set_xticks(range(len(groups)),[NAMES[g].replace('Physical / engineering','Physical /\nengineering').replace('Social / humanities','Social /\nhumanities') for g in groups]);ax.tick_params(length=0)
        ax.set_title('By benchmark' if row==0 else 'By super-family',fontsize=8,pad=8)
        for y,a in enumerate(ARMS):
            for x,g in enumerate(groups):
                z=s['absolute']['available'][a][field][g];m=z['mean'];ci=z['ci95']
                txt='No data' if m is None else f'{m:.2f}\n'+(f'[{ci[0]:.2f}, {ci[1]:.2f}]' if ci else 'CI unavailable')
                ax.text(x,y,txt,ha='center',va='center',fontsize=5.5,color='white' if m is not None and m>65 else '#17212B')
        for spine in ax.spines.values():spine.set_visible(False)
    colors=['#D98E4B','#EEEEEE','#58AA85','#D0D0D0','#FFFFFF']
    cmap=ListedColormap(colors);norm=BoundaryNorm(np.arange(-.5,5,.999999),5)
    groups=[('source',g) for g in SOURCES]+[('family',g) for g in FAMILIES]
    for k,(field,g) in enumerate(groups):
        ax=fig.add_subplot(right[k//3,k%3]);ra.append(ax);classes=np.full((5,5),3.);texts={}
        for r in pairs['comparisons']:
            if r['level']!=field or r['group']!=g:continue
            i=ARMS.index(r['persona_i']);j=ARMS.index(r['persona_j'])
            for y,x,sign in [(i,j,1),(j,i,-1)]:
                m=None if r['mean'] is None else r['mean']*sign;p=r['p_holm']
                classes[y,x]=4 if m is None or p is None else (2 if m>0 else 0) if p<.05 else 1
                texts[y,x]='NA' if m is None else ('0.00' if abs(m)<.005 else f'{m:+.2f}')
                data.append(dict(r,row_persona=ARMS[y],column_persona=ARMS[x],display_difference=m,category=['negative significant','not significant','positive significant','diagonal','unavailable test'][int(classes[y,x])]))
        ax.imshow(classes,cmap=cmap,norm=norm,aspect='auto',interpolation='nearest')
        for (y,x),txt in texts.items():ax.text(x,y,txt,ha='center',va='center',fontsize=6)
        ax.set_xticks(range(5),[label(a) for a in ARMS]);ax.set_yticks(range(5),[label(a) for a in ARMS]);ax.tick_params(length=0,pad=3)
        title=NAMES[g].replace('Physical / engineering','Physical / engineering').replace('Social / humanities','Social / humanities')
        ax.set_title(title,fontsize=7,pad=7)
        for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.2075,.962,'A  Available performance',ha='center',fontsize=10,weight='bold')
    fig.text(.2075,.93,'Mean [pointwise 95% CI]',ha='center',fontsize=7)
    fig.text(.7075,.962,'B  Pairwise performance changes',ha='center',fontsize=10,weight='bold')
    fig.text(.7075,.93,'Row − column · '+test_label,ha='center',fontsize=7)
    cax=fig.add_axes([.10,.12,.21,.014]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('Native score normalized to 0–100',fontsize=7);cb.ax.tick_params(labelsize=6)
    fig.legend(handles=[Patch(facecolor=colors[2],label='Positive, adjusted p < .05'),Patch(facecolor=colors[0],label='Negative, adjusted p < .05'),Patch(facecolor=colors[1],label='Not significant'),Patch(facecolor='white',edgecolor='#777777',label='Test unavailable')],loc='lower center',bbox_to_anchor=(.7075,.075),ncol=2,frameon=False,fontsize=7)
    fig.text(.06,.018,'Two-sided '+test_label+'; Holm correction across 90 unique comparisons. Diagonal: self-comparison, not tested.\nExploratory, conditional on observed trials. Pairwise coverage varies; gray does not establish equivalence. Super-families mix native metrics.\nASI available scores mix historical judges; pairwise comparisons require corrected judges. T: trials with evaluable results.',fontsize=6,linespacing=1.5)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa/pairwise_performance.alignment.json'),overlay_svg=str(FIG/'qa/pairwise_performance.alignment.svg'),strict=True,tolerance_pt=1.5,axes=ra,exclude_axes=[cax])
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa/pairwise_absolute.alignment.json'),strict=True,tolerance_pt=1.5,axes=la)
    write_csv(FIG/'pairwise_performance.source_data.csv',data)
    fig.savefig(FIG/'pairwise_performance.pdf',facecolor='white')
    fig.savefig(FIG/'pairwise_performance.svg',facecolor='white')
    fig.savefig(FIG/'pairwise_performance.png',dpi=600,facecolor='white')
    fig.savefig(FIG/'pairwise_performance.tiff',dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
    plt.close(fig)
if __name__=='__main__':main()
