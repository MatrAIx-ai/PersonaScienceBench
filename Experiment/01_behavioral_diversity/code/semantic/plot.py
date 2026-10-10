#!/usr/bin/env python3
"""Only A: pairwise heatmaps and B: two question-controlled trajectory cases."""
import csv
import json
from pathlib import Path
import sys
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox
from matplotlib.path import Path as MplPath
from matplotlib.text import Text
from analyze import BASE,OUT,config,write_csv,NAMES
sys.path.insert(0,'/home/siyangwu/.codex/skills/nature-figure/scripts')
from audit_panel_alignment import require_matplotlib_panel_alignment
FIG=BASE/'figures/semantic'
PLACEMENTS=[]
COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':8,'axes.labelsize':8,'axes.titlesize':8.5,'xtick.labelsize':7.2,'ytick.labelsize':7.2,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6})

def place_round_labels(ax,specs,segments,context):
    """Place every real round label near its node, avoiding text and paths."""
    fig=ax.figure;fig.canvas.draw();renderer=fig.canvas.get_renderer()
    font=FontProperties(size=5.3);scale=fig.dpi/72
    extent=ax.get_window_extent();placed=[];drawn=[]
    nodes=np.array([ax.transData.transform(s[0]) for s in specs])
    lines=[MplPath(ax.transData.transform(np.array([a,b]))) for a,b in segments]
    lines.extend(t.arrow_patch.get_path().transformed(t.arrow_patch.get_transform()) for t in ax.texts if getattr(t,'arrow_patch',None) is not None)
    for node,text,color in specs:
        center=ax.transData.transform(node)
        width,height,_=renderer.get_text_width_height_descent(text,font,False)
        height=5.3*scale*1.3
        candidates=[]
        minimum_radius={('simulator','bix-43-q5','#0072B2','13'):20,('simulator','bix-43-q5','#0072B2','11'):16,('simulator','bix-43-q5','#D55E00','2'):16,('actor','fluids/disambiguation/case_001','#D55E00','4'):16}.get((*context,color,text),7)
        for radius in [r for r in [7,10,13,16,20,24,28] if r>=minimum_radius]:
            for angle in np.arange(0,360,30):
                offset=np.array([np.cos(np.deg2rad(angle)),np.sin(np.deg2rad(angle))])*radius*scale
                pos=center+offset
                rect=Bbox.from_bounds(pos[0]-width/2-2*scale,pos[1]-height/2-2*scale,width+4*scale,height+4*scale)
                outside=not(extent.contains(rect.x0,rect.y0) and extent.contains(rect.x1,rect.y1))
                overlap=sum(rect.overlaps(b) for b in placed)
                node_box=rect.expanded(1+6*scale/rect.width,1+6*scale/rect.height)
                on_node=sum(node_box.contains(*n) for n in nodes)
                crosses=sum(path.intersects_bbox(rect,filled=False) for path in lines)
                leader=MplPath(np.array([center+offset/radius*3.5,pos-offset/radius*5]))
                leader_crosses=sum(leader.intersects_bbox(b,filled=False) for b in placed) if radius>8 else 0
                score=1e9*outside+1e8*overlap+1e6*on_node+1e5*leader_crosses+1e5*crosses+radius
                candidates.append((score,angle,radius,offset,rect))
        _,_,radius,offset,rect=min(candidates,key=lambda c:(c[0],c[1]))
        forced={('simulator','bix-43-q5','#009E73','1'):(-16,25),('simulator','bix-43-q5','#0072B2','12'):(-25,25),('actor','fluids/disambiguation/case_001','#0072B2','3'):(-20,10),('actor','fluids/disambiguation/case_001','#009E73','3'):(14,25),('actor','fluids/disambiguation/case_001','#D55E00','3'):(-14,28)}.get((*context,color,text))
        if forced:
            offset=np.array(forced)*scale;radius=float(np.linalg.norm(offset)/scale);pos=center+offset
            rect=Bbox.from_bounds(pos[0]-width/2-2*scale,pos[1]-height/2-2*scale,width+4*scale,height+4*scale)
        placed.append(rect)
        PLACEMENTS.append(dict(context=context,text=text,color=color,offset_pt=(offset/scale).tolist(),score=min(candidates,key=lambda c:(c[0],c[1]))[0]))
        kwargs=dict(arrowprops=dict(arrowstyle='-',lw=.35,color=color,alpha=.75,shrinkA=4,shrinkB=3)) if radius>8 else {}
        annotation=ax.annotate(text,xy=node,xytext=offset/scale,textcoords='offset points',ha='center',va='center',fontsize=5.3,color=color,zorder=6,**kwargs)
        drawn.append((annotation,node,color,radius))
        if annotation.arrow_patch is not None:
            fig.canvas.draw()
            lines.append(annotation.arrow_patch.get_path().transformed(annotation.arrow_patch.get_transform()))

    # Round-label guides are annotations, not trajectory segments. Stop guide
    # strokes around every label instead of letting them cross text. No data
    # lines, nodes, round numbers or trajectory coordinates are masked.
    for annotation,_,_,_ in drawn:
        if annotation.arrow_patch is not None:annotation.arrow_patch.set_visible(False)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    boxes=[Text.get_window_extent(a,renderer).expanded(1.6,1.65) for a,_,_,_ in drawn]
    inverse=ax.transData.inverted()
    for annotation,node,color,radius in drawn:
        if radius<=8:continue
        start=ax.transData.transform(node);bbox=Text.get_window_extent(annotation,renderer);end=np.array([(bbox.x0+bbox.x1)/2,(bbox.y0+bbox.y1)/2])
        length=np.linalg.norm(end-start)
        if length<=8*scale:continue
        direction=(end-start)/length;start=start+direction*3*scale;end=end-direction*4*scale
        ts=np.linspace(0,1,400);points=start[None,:]+ts[:,None]*(end-start)[None,:]
        good=np.array([not any(b.contains(*point) for b in boxes) for point in points])
        changes=np.diff(np.r_[False,good,False].astype(int));begins=np.where(changes==1)[0];ends=np.where(changes==-1)[0]-1
        for lo,hi in zip(begins,ends):
            if hi-lo<2:continue
            segment=inverse.transform(points[[lo,hi]])
            ax.plot(segment[:,0],segment[:,1],lw=.35,color=color,alpha=.6,zorder=1.5)

def curved_connection(ax,start,end,color):
    """Quadratic visual connector; observed endpoints remain exact."""
    lo=np.array([ax.get_xlim()[0],ax.get_ylim()[0]])
    span=np.array([np.diff(ax.get_xlim())[0],np.diff(ax.get_ylim())[0]])
    a=(start-lo)/span;b=(end-lo)/span;delta=b-a
    if np.linalg.norm(delta)<1e-12:return
    control=((a+b)/2+.14*np.array([-delta[1],delta[0]]))*span+lo
    path=MplPath([start,control,end],[MplPath.MOVETO,MplPath.CURVE3,MplPath.CURVE3])
    ax.add_patch(PathPatch(path,facecolor='none',edgecolor=color,lw=.8,alpha=.9,zorder=2))

def main():
    PLACEMENTS.clear()
    s=json.loads((BASE/'data/semantic_final/summary.json').read_text());c=s['config'];cases=s['cases'];roles=c['roles']
    coords=list(csv.DictReader((OUT/'trajectory_coordinates.csv').open()));projection=json.loads((OUT/'umap.json').read_text())
    descriptions=json.loads((OUT/'case_descriptions.json').read_text()) if (OUT/'case_descriptions.json').exists() else {}
    FIG.mkdir(parents=True,exist_ok=True);(FIG/'qa').mkdir(exist_ok=True)
    fig,axes=plt.subplots(len(roles),3,squeeze=False,figsize=(7.204724409,(128 if len(roles)==2 else 86)/25.4))
    fig.subplots_adjust(left=.09,right=.99,top=.86,bottom=.19 if len(roles)==2 else .32,wspace=.32,hspace=.30)
    bound=max(abs(v) for role in roles for row in s['roles'][role]['estimate'] for v in row);bound=max(bound,.001)
    cmap=plt.get_cmap('BrBG').copy();cmap.set_bad('white')
    plotted=[]
    for ri,role in enumerate(roles):
        ax=axes[ri,0];value=np.array(s['roles'][role]['estimate']);masked=np.ma.array(value,mask=np.triu(np.ones((5,5),dtype=bool)))
        im=ax.imshow(masked,cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound),aspect='auto',interpolation='nearest')
        for d in range(5):ax.add_patch(Rectangle((d-.5,d-.5),1,1,facecolor='#EEEEEE',edgecolor='none',zorder=1))
        for spine in ax.spines.values():spine.set_visible(False)
        labels=[c['labels'][a].replace('Persona ','') for a in c['arms']]
        ax.set_xticks(range(5),labels);ax.set_yticks(range(5),labels);ax.tick_params(length=0,pad=3)
        for i in range(5):
            for j in range(5):
                if i>j:ax.text(j,i,f"{value[i,j]:.3f}"+('*' if s['roles'][role]['p_holm'][i][j]<.05 else ''),ha='center',va='center',fontsize=7.2,color='white' if abs(value[i,j])>bound*.62 else '#182229')
        ax.set_ylabel(role.capitalize(),fontsize=9,labelpad=8,weight='bold')
        for col,case in enumerate(cases,1):
            ax=axes[ri,col]
            points=[r for r in coords if r['source']==case['source'] and r['task_id']==case['task_id'] and r['role']==role and r['displayed']=='True']
            projected=next(v for v in projection if v['source']==case['source'] and v['task_id']==case['task_id'] and v['role']==role)
            allxy=np.array([[float(r['umap1']),float(r['umap2'])] for r in points]);xmin,ymin=allxy.min(axis=0);xmax,ymax=allxy.max(axis=0);dx=max(xmax-xmin,.01);dy=max(ymax-ymin,.01)
            ax.set_xlim(xmin-.13*dx,xmax+.13*dx);ax.set_ylim(ymin-.15*dy,ymax+.15*dy)
            label_specs=[];segments=[]
            for pi,a in enumerate(c['arms']):
                rows=sorted([r for r in points if r['arm']==a],key=lambda r:int(r['round']));xy=np.array([[float(r['umap1']),float(r['umap2'])] for r in rows]);color=COLORS[pi]
                if len(xy)>2:
                    ax.scatter(xy[1:-1,0],xy[1:-1,1],s=11,color=color,edgecolors='white',linewidths=.3,zorder=3)
                ax.scatter(*xy[0],s=40 if len(xy)==1 else 31,marker='o',facecolors='white',edgecolors=color,linewidths=1,zorder=4)
                ax.scatter(*xy[-1],s=12 if len(xy)==1 else 31,marker='o',facecolors=color,edgecolors='white',linewidths=.4,zorder=5)
                for start,end in zip(xy[:-1],xy[1:]):
                    segments.append((start,end))
                    curved_connection(ax,start,end,color)
                for k,(r,point) in enumerate(zip(rows,xy)):
                    label_specs.append((point,r['round'],color))
                    plotted.append(r)
            # Round indices remain in source data; omit point labels in the figure.
            ax.set_xlabel('UMAP 1',labelpad=2);ax.set_ylabel('UMAP 2',labelpad=2)
            ax.locator_params(nbins=3);ax.tick_params(length=2,pad=2)
            if ri==0:
                title={'bix-57-q1':'BixBench\nbix 57','matToolUse/disambiguation/case_236':'SciConvBench\ncase 236'}[case['task_id']]
                ax.set_title(title,fontsize=8.5,pad=3)
    # Only two main panel labels; the role axes remain subplots.
    left_panel=axes[0,0].get_position()
    right_start=axes[0,1].get_position();right_end=axes[0,2].get_position()
    fig.text((left_panel.x0+left_panel.x1)/2,.95,'A  Final-response separation',ha='center',fontsize=9.5,weight='bold')
    fig.text((right_start.x0+right_end.x1)/2,.95,'B  Question-controlled trajectories',ha='center',fontsize=9.5,weight='bold')
    metric='Excess cosine distance'
    cax=fig.add_axes([left_panel.x0,.105,left_panel.width,.015]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label(metric,fontsize=8,labelpad=2);cb.ax.tick_params(labelsize=7.2,length=2);cb.locator=plt.MaxNLocator(nbins=3);cb.update_ticks()
    handles=[Line2D([0],[0],color=color,marker='o',lw=1,markersize=3,label=c['labels'][a]) for a,color in zip(c['arms'],COLORS)]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=((right_start.x0+right_end.x1)/2,.04),ncol=3,frameon=False,fontsize=7.5,columnspacing=.9,handlelength=1.2,handletextpad=.4)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=str(FIG/'qa/semantic.alignment.json'),overlay_svg=str(FIG/'qa/semantic.alignment.svg'),tolerance_pt=1.5,strict=True,exclude_axes=[cax])
    (FIG/'qa/label_placement.json').write_text(json.dumps(PLACEMENTS,indent=2))
    write_csv(FIG/'trajectory.source_data.csv',plotted)
    write_csv(FIG/'heatmap.source_data.csv',list(csv.DictReader((BASE/'data/semantic_final/heatmap_cells.csv').open())))
    fig.savefig(FIG/'semantic.pdf',facecolor='white',bbox_inches='tight',pad_inches=.025)
    fig.savefig(FIG/'semantic.svg',facecolor='white',bbox_inches='tight',pad_inches=.025)
    fig.savefig(FIG/'semantic.png',dpi=600,facecolor='white',bbox_inches='tight',pad_inches=.025)
    fig.savefig(FIG/'semantic.tiff',dpi=600,facecolor='white',bbox_inches='tight',pad_inches=.025)
    plt.close(fig)

if __name__=='__main__':main()
