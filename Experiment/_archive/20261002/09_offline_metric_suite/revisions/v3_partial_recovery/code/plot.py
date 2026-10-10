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

def self_repetition_violin(ax,role):
 from scipy.stats import gaussian_kde
 from collections import Counter
 sr=json.loads((DATA/'self_repetition_summary.json').read_text())
 for i,arm in enumerate(ARMS):
  rows=[r for r in sr['cases'] if r['arm']==arm and r['role']==role and r['width']==40 and r['panel']=='common']
  values=np.array([r['value'] for r in rows]);counts=Counter(r['source'] for r in rows)
  w=np.array([1/len(counts)/counts[r['source']] for r in rows])
  if len(values)>1 and np.ptp(values)>1e-8:
   kde=gaussian_kde(values,weights=w,bw_method='scott');grid=np.linspace(values.min(),values.max(),150)
   density=kde(grid);width=.38*density/density.max()
   ax.fill_betweenx(grid,i-width,i+width,facecolor=COLORS[i],edgecolor=COLORS[i],alpha=.25,lw=.7)
  ax.scatter(i+np.linspace(-.23,.23,len(values)),values,s=5,color=COLORS[i],alpha=.4,edgecolors='none',zorder=3)
  r=pick(sr['cells'],arm=arm,role=role,width=40,panel='common',level='all',group='all');lo,hi=r['ci95']
  ax.errorbar(i,r['mean'],yerr=[[r['mean']-lo],[hi-r['mean']]],fmt='D',mfc='white',mec='#222222',ecolor='#222222',markersize=3.5,capsize=2,elinewidth=.8,zorder=5)
 peak=max(r['value'] for r in sr['cases'] if r['width']==40 and r['panel']=='common')
 ax.set_xticks(range(5),LABELS);ax.set_xlim(-.6,4.6);ax.set_ylim(-.5,peak*1.1);ax.set_ylabel('Repeated text windows (%)');ax.tick_params(length=2)
 return len(rows)

def self_repetition_points(ax):
 sr=json.loads((DATA/'self_repetition_summary.json').read_text());largest=0
 for i,arm in enumerate(ARMS):
  r=pick(sr['cells'],arm=arm,role='simulator',width=40,panel='common',level='all',group='all');lo,hi=r['ci95'];largest=max(largest,hi)
  ax.errorbar(r['mean'],i,xerr=[[r['mean']-lo],[hi-r['mean']]],fmt='o',color=COLORS[i],markersize=4,capsize=2,elinewidth=.9)
 ax.set_yticks(range(5),LABELS);ax.set_ylim(4.6,-.6);ax.set_xlim(0,largest*1.12);ax.set_xlabel('Repeated text windows (%)');ax.tick_params(length=2)
 return r['tasks']

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
 fig=plt.figure(figsize=(240/25.4,100/25.4))
 a,b,d=[fig.add_axes([left,.33,.24,.52]) for left in [.065,.395,.725]]
 for center,title in [(.185,'A  Simulator self-repetition'),(.515,'B  Missing-fact recovery'),(.845,'D  SciConvBench failure coverage')]:
  fig.text(center,.925,title,ha='center',fontsize=8,weight='bold')
 n=self_repetition_points(a)
 a.text(.5,-.27,f'{n} common questions · simulator turns\nSource-balanced mean / 95% CI',transform=a.transAxes,ha='center',va='top',fontsize=6,linespacing=1.5)
 # Violin observations are 20 question means, not all repeated episodes.
 from analyze import task_values
 snap=json.loads((DATA/'snapshot.json').read_text());violin_rows=[]
 for i,arm in enumerate(ARMS):
  rows=task_values([r for r in snap['recovery'] if r['arm']==arm],'recovery')
  violin_rows.extend([r|dict(arm=arm) for r in rows]);y=np.array([r['value'] for r in rows])
  parts=b.violinplot([y],positions=[i],widths=.76,showextrema=False,bw_method='scott',points=150)
  for body in parts['bodies']:
   body.set_facecolor(COLORS[i]);body.set_edgecolor(COLORS[i]);body.set_alpha(.25);body.set_linewidth(.7)
  # Deterministic offsets expose individual cases; vertical values are unchanged.
  offsets=np.linspace(-.23,.23,len(y));b.scatter(i+offsets,y,s=7,color=COLORS[i],alpha=.75,edgecolors='none',zorder=3)
  r=pick(s['outcomes'],metric='fact_recovery',arm=arm,level='all',group='all');lo,hi=r['ci95']
  b.errorbar(i,r['mean'],yerr=[[r['mean']-lo],[hi-r['mean']]],fmt='D',mfc='white',mec='#222222',ecolor='#222222',markersize=3.5,capsize=2,elinewidth=.8,zorder=5)
 b.set_xticks(range(5),LABELS);b.set_xlim(-.6,4.6);b.set_ylim(-5,108);b.set_yticks([0,25,50,75,100]);b.set_ylabel('Recovered target facts (%)');b.tick_params(length=2)
 b.text(.5,-.19,'Dots: 20 case means per setting\nDiamond / bar: mean / 95% CI',transform=b.transAxes,ha='center',va='top',fontsize=6,linespacing=1.5)
 markers=['o','s','^','D','v']
 for i,(arm,label) in enumerate(zip(ARMS,LABELS)):
  rr=[r for r in s['persona_failure_coverage'] if r['arm']==arm]
  xx=np.array([r['budget'] for r in rr]);y=np.array([r['mean'] for r in rr]);ci=np.array([r['ci95'] for r in rr])
  d.plot(xx,y,color=COLORS[i],marker=markers[i],markersize=4,lw=1,label=label,linestyle=['-','--',':','-','-'][i],mfc='white' if i==0 else COLORS[i],zorder=4)
  if len(rr)>1:d.fill_between(xx,ci[:,0],ci[:,1],color=COLORS[i],alpha=.10,lw=0)
  else:d.errorbar(xx,y,yerr=[y-ci[:,0],ci[:,1]-y],fmt='none',ecolor=COLORS[i],capsize=2,elinewidth=.8,zorder=3)
 d.set_xlim(.75,3.2);d.set_ylim(0,55);d.set_xticks([1,2,3]);d.set_yticks([0,10,20,30,40,50]);d.set_xlabel('Episodes / question');d.set_ylabel('Questions with ≥1 failure (%)');d.tick_params(length=2)
 d.legend(loc='upper center',bbox_to_anchor=(.5,-.27),frameon=False,ncol=3,fontsize=6,columnspacing=1,handlelength=1.5)
 fig.text(.065,.035,'A: verbatim reuse across turns within one conversation (40-character windows).  D: 003 / 046 have one trial only.',fontsize=5.8)
 save(fig,'metric_suite',[[a,b,d]])
 write_csv(DATA/'recovery_case_means.csv',violin_rows)
 write_csv(FIG/'recovery_case_means.source_data.csv',violin_rows)
 fig,axes=plt.subplots(1,2,figsize=(183/25.4,95/25.4));fig.subplots_adjust(left=.09,right=.97,bottom=.25,top=.82,wspace=.3)
 for ax,role in zip(axes,['simulator','actor']):
  n=self_repetition_violin(ax,role);ax.set_title(f'{role.capitalize()} · {n} common questions',pad=8,fontsize=8)
 fig.text(.53,.95,'Within-conversation self-repetition',ha='center',fontsize=9,weight='bold')
 fig.text(.09,.065,'40-character verbatim reuse; dots = question means. Source-balanced KDE and mean; bars = 95% CI.\nSeparate role-specific common panels; fewer than two eligible messages is unavailable, not zero.',fontsize=6,linespacing=1.5)
 save(fig,'self_repetition_roles',[list(axes)])
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
 for name in ['repetition','outcomes','failure_coverage','matched_contrasts','persona_failure_coverage','self_repetition_cases','self_repetition_cells','self_repetition_contrasts']:
  write_csv(FIG/(name+'.source_data.csv'),list(csv.DictReader((DATA/(name+'.csv')).open())))
 print('Saved main figure and two supporting figures.',flush=True)
if __name__=='__main__':main()
