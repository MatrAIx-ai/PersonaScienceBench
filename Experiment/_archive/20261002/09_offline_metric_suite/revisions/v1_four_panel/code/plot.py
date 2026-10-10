"""Paper-ready four-metric figures, matching the established semantic-figure palette."""
import sys,json,csv
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from extract import ROOT,BASE,DATA,ARMS,SOURCES,FAMILIES,LABELS,write_csv
sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
from audit_panel_alignment import require_matplotlib_panel_alignment
FIG=BASE/'figures';COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']
NAMES=dict(zip(SOURCES,['ASI-Bench','BixBench','DiscoveryBench','EXP-Bench','SciConvBench']))
NAMES.update(dict(zip(FAMILIES,['Life sciences','Physical / engineering','Math / CS','Social / humanities'])))
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':6,'ytick.labelsize':6,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6})

def pick(rows,**kw):
 match=[r for r in rows if all(r.get(k)==v for k,v in kw.items())]
 assert len(match)==1,(kw,len(match))
 return match[0]

def axes_clean(ax):
 for spine in ax.spines.values():spine.set_visible(False)
 ax.tick_params(length=0,pad=4)

def repetition_heat(ax,s,level='all',group='all',variant='primary'):
 matrix=np.full((5,5),np.nan)
 for i,a in enumerate(ARMS):
  for j,b in enumerate(ARMS[:i+1]):
   r=pick(s['repetition'],persona_i=a,persona_j=b,level=level,group=group,variant=variant)
   if r['mean'] is not None:matrix[i,j]=r['mean']
 cmap=plt.get_cmap('PuBuGn').copy();cmap.set_bad('white');im=ax.imshow(matrix,cmap=cmap,vmin=0,vmax=100,aspect='auto')
 for i in range(5):
  for j in range(i+1):
   m=matrix[i,j]
   if np.isnan(m):ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor='#EEEEEE',edgecolor='none'));txt='—';color='#777777'
   else:txt=f'{m:.1f}';color='white' if m>65 else '#182229'
   ax.text(j,i,txt,ha='center',va='center',fontsize=7,color=color)
 ax.set_xticks(range(5),LABELS);ax.set_yticks(range(5),LABELS);axes_clean(ax)
 return im

def score_heat(ax,s,field,groups,show_ci=False):
 matrix=np.array([[pick(s['outcomes'],metric='native_score',arm=a,level=field,group=g)['mean'] for g in groups] for a in ARMS],float)
 cmap=plt.get_cmap('Blues').copy();cmap.set_bad('#EEEEEE');im=ax.imshow(matrix,cmap=cmap,vmin=0,vmax=100,aspect='auto')
 for i,a in enumerate(ARMS):
  for j,g in enumerate(groups):
   r=pick(s['outcomes'],metric='native_score',arm=a,level=field,group=g);m=r['mean'];ci=r['ci95']
   txt='—' if m is None else f'{m:.1f}'
   if show_ci:txt+='\n'+(f'[{ci[0]:.1f}, {ci[1]:.1f}]' if ci else 'CI unavailable')
   ax.text(j,i,txt,ha='center',va='center',fontsize=6.5 if show_ci else 7,color='white' if m is not None and m>65 else '#182229',linespacing=1.4)
 labels=[NAMES[g].replace('DiscoveryBench','Discovery\nBench').replace('SciConvBench','SciConv\nBench').replace('Physical / engineering','Physical /\nengineering').replace('Social / humanities','Social /\nhumanities')+('*' if g=='asibench' else '') for g in groups]
 ax.set_xticks(range(len(groups)),labels);ax.set_yticks(range(5),LABELS);axes_clean(ax)
 return im

def save(fig,name,groups,exclude=()):
 fig.canvas.draw()
 for k,axes in enumerate(groups):
  ids=[f'p{i}' for i in range(len(axes))];rows=defaultdict(list);cols=defaultdict(list)
  for ident,axis in zip(ids,axes):
   pos=axis.get_position();rows[(round(pos.y0,6),round(pos.y1,6))].append(ident);cols[(round(pos.x0,6),round(pos.x1,6))].append(ident)
  require_matplotlib_panel_alignment(fig,panel_ids=ids,row_groups=[v for v in rows.values() if len(v)>1],column_groups=[v for v in cols.values() if len(v)>1],json_out=str(FIG/f'qa/{name}.alignment{k}.json'),overlay_svg=str(FIG/f'qa/{name}.alignment{k}.svg'),strict=True,tolerance_pt=1.5,axes=axes,exclude_axes=exclude)
 fig.savefig(FIG/(name+'.pdf'),facecolor='white')
 fig.savefig(FIG/(name+'.svg'),facecolor='white')
 fig.savefig(FIG/(name+'.png'),dpi=600,facecolor='white')
 fig.savefig(FIG/(name+'.tiff'),dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
 plt.close(fig)

def main():
 FIG.mkdir(exist_ok=True);(FIG/'qa').mkdir(exist_ok=True);s=json.loads((DATA/'summary.json').read_text())
 fig=plt.figure(figsize=(240/25.4,195/25.4))
 # Intentional mixed layout: left heatmaps, right outcome plot and two matched coverage axes.
 a=fig.add_axes([.075,.625,.34,.27]);b=fig.add_axes([.58,.625,.34,.27]);c=fig.add_axes([.075,.185,.34,.27])
 d1=fig.add_axes([.555,.185,.155,.27]);d2=fig.add_axes([.785,.185,.155,.27])
 fig.text(.245,.958,'A  Interaction-pattern repetition',ha='center',fontsize=9,weight='bold')
 fig.text(.75,.958,'B  Missing-fact recovery',ha='center',fontsize=9,weight='bold')
 fig.text(.245,.487,'C  Native scientific outcomes',ha='center',fontsize=9,weight='bold')
 fig.text(.75,.487,'D  Equal-budget failure coverage',ha='center',fontsize=9,weight='bold')
 im=repetition_heat(a,s);a.set_ylabel('Persona');a.set_xlabel('Persona',labelpad=2)
 ca=fig.add_axes([.13,.557,.23,.012]);cb=fig.colorbar(im,cax=ca,orientation='horizontal');cb.set_label('Identical interaction patterns (%)',fontsize=6,labelpad=2);cb.ax.tick_params(labelsize=5.5,length=2,pad=2)
 for i,arm in enumerate(ARMS):
  r=pick(s['outcomes'],metric='fact_recovery',arm=arm,level='all',group='all');m=r['mean'];lo,hi=r['ci95']
  b.errorbar(m,i,xerr=[[m-lo],[hi-m]],fmt='o',color=COLORS[i],markersize=4,capsize=2,elinewidth=.9)
  b.text(101,i,f'{m:.1f} [{lo:.1f}, {hi:.1f}]',fontsize=6,va='center')
 b.set_yticks(range(5),LABELS);b.set_ylim(4.6,-.6);b.set_xlim(60,129);b.set_xticks([60,70,80,90,100]);b.set_xlabel('Recovered target facts (%)');b.spines['bottom'].set_bounds(60,100);b.tick_params(length=2,pad=3)
 im2=score_heat(c,s,'source',SOURCES);c.set_ylabel('Persona')
 cc=fig.add_axes([.13,.103,.23,.012]);cb2=fig.colorbar(im2,cax=cc,orientation='horizontal');cb2.set_label('Native score (0–100)',fontsize=6,labelpad=2);cb2.ax.tick_params(labelsize=5.5,length=2,pad=2)
 for ax,source in [(d1,'bixbench'),(d2,'sciconvbench')]:
  for strategy,color,marker in [('off',COLORS[0],'o'),('mixture',COLORS[3],'s')]:
   rr=[pick(s['failure_coverage'],variant='primary',budget=m,strategy=strategy,level='source',group=source) for m in [1,2,3]]
   y=np.array([r['mean'] for r in rr]);ci=np.array([r['ci95'] for r in rr]);xx=np.array([1,2,3])
   ax.plot(xx,y,color=color,marker=marker,markersize=3,lw=.9,label='Repeated off' if strategy=='off' else 'Persona mixture',linestyle='-' if strategy=='off' else '--')
   ax.fill_between(xx,ci[:,0],ci[:,1],color=color,alpha=.10,lw=0)
  ax.set_title(NAMES[source],fontsize=7,pad=5);ax.set_xlim(.8,3.2);ax.set_ylim(0,100);ax.set_xticks([1,2,3]);ax.set_yticks([0,25,50,75,100]);ax.set_xlabel('Episodes / question',fontsize=6);ax.tick_params(length=2)
 d1.set_ylabel('Questions with ≥1 failure (%)',fontsize=6)
 handles,labels=d1.get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.75,.085),frameon=False,ncol=2,fontsize=6)
 fig.text(.075,.023,'Original endpoints · Pointwise 95% study-cluster CIs · Full denominators and paired differences in the accompanying tables.\nA: diagonal = within-persona repeats; — = no repeats. B: 20 disambiguation cases. C: *ASI mixes historical judges.\nD: fixed common panels (BixBench 26; SciConvBench 40); scientific failures only. Exploratory, conditional on saved trials.',fontsize=5.8,linespacing=1.5)
 save(fig,'metric_suite',[[a,b,c],[d1,d2]],exclude=[ca,cc])
 # Source-specific structural repetition, with a super-family aggregate supplement in tables.
 fig,axes=plt.subplots(2,3,figsize=(240/25.4,155/25.4));fig.subplots_adjust(left=.07,right=.97,bottom=.16,top=.88,wspace=.3,hspace=.42)
 for ax,g in zip(axes.flat,[*SOURCES,'all']):
  level='all' if g=='all' else 'source';repetition_heat(ax,s,level,g)
  n=pick(s['repetition'],persona_i=ARMS[0],persona_j=ARMS[0],variant='primary',level=level,group=g)['tasks']
  ax.set_title(('Equal-benchmark mean' if g=='all' else NAMES[g])+f' · n={n}',fontsize=7,pad=6)
 fig.text(.52,.96,'Interaction-pattern repetition by benchmark',ha='center',fontsize=9,weight='bold')
 ca=fig.add_axes([.35,.065,.3,.015]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,100),cmap='PuBuGn'),cax=ca,orientation='horizontal');cb.set_label('Identical interaction patterns (%)',fontsize=6);cb.ax.tick_params(labelsize=6)
 save(fig,'repetition_by_benchmark',[list(axes.flat)],exclude=[ca])
 fig,axes=plt.subplots(2,1,figsize=(183/25.4,170/25.4));fig.subplots_adjust(left=.1,right=.96,top=.88,bottom=.13,hspace=.38)
 for ax,field,gs in zip(axes,['source','family'],[SOURCES,FAMILIES]):
  score_heat(ax,s,field,gs,True);ax.set_title('By benchmark' if field=='source' else 'By super-family (descriptive mixtures)',pad=8,fontsize=8)
 fig.text(.53,.965,'Native scientific outcomes · mean [95% CI]',ha='center',fontsize=9,weight='bold')
 fig.text(.1,.025,'Original endpoints; per-cell coverage varies. *ASI mixes historical judge versions.\nSuper-families mix native metrics. Paired comparisons apply evaluator compatibility filters.',fontsize=6,linespacing=1.5)
 save(fig,'native_scores_with_ci',[list(axes)])
 # Source data are complete metric tables, not a rounded transcription from the figure.
 for name in ['repetition','outcomes','failure_coverage','matched_contrasts']:
  write_csv(FIG/(name+'.source_data.csv'),list(csv.DictReader((DATA/(name+'.csv')).open())))
 print('Saved main figure and two supporting figures.',flush=True)
if __name__=='__main__':main()
