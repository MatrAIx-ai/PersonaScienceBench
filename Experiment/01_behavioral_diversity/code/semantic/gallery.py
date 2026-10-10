#!/usr/bin/env python3
"""Private exploratory trajectory gallery; does not modify aggregate results."""
import csv,html,json,re,sys
from collections import Counter,defaultdict
from io import StringIO
from pathlib import Path
import numpy as np
from importlib.metadata import version
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.path import Path as MplPath
from matplotlib.backends.backend_pdf import PdfPages
from analyze import ROOT,BASE,OUT,CACHE,config,sha,write_json,write_csv,NAMES

DEST=ROOT/'runs/semantic-review'
PUBLIC=BASE/'data/semantic_review'
SEED='20261006'
ORIGINAL_REVIEW_EXCLUSIONS={('bixbench','bix-43-q5'),('sciconvbench','fluids/disambiguation/case_001')}
MIN_EXCHANGES=4
REQUIRE_ALL_LONG=False
SELECTION_RULE='Require complete trial-1 data for five settings; exclude the two original PCA main-figure cases. Retain questions with at least four paired simulator–actor exchanges in at least one setting. Rank by number of settings reaching four exchanges, then minimum and total paired exchanges across settings, all descending; hash breaks ties. Take up to 30 per benchmark. Selection is length-enriched and exploratory.'
UMAP_SETTINGS=dict(n_components=2,n_neighbors=15,min_dist=0.1,metric='cosine',random_state=42,transform_seed=42,n_epochs=500,init='spectral',n_jobs=1)
sys.path.insert(0,str(BASE/'code'))
from audit_panel_alignment import require_matplotlib_panel_alignment
COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']
SOURCES=['asibench','bixbench','discoverybench','expbench','sciconvbench']
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6})

def load():
 c=config();allrows=json.loads((CACHE/'messages.private.json').read_text());f=np.load(CACHE/'embeddings.npz',allow_pickle=False)
 assert np.array_equal(f['hashes'],[r['text_sha256'] for r in allrows])
 selected=[i for i,r in enumerate(allrows) if r['trial']==1 and r['arm'] in c['arms']]
 rows=[allrows[i] for i in selected];z=f['embeddings'][selected]
 return c,rows,z

def select_cases(rows=None):
 if rows is None: _,rows,_=load()
 arms=config()['arms'];rounds=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
 for r in rows:rounds[(r['source'],r['task_id'])][r['arm']][r['role']].add(r['round'])
 def lengths(k):return {a:len(rounds[k][a]['simulator'] & rounds[k][a]['actor']) for a in arms}
 def count_long(k):return sum(v>=MIN_EXCHANGES for v in lengths(k).values())
 cov=list(csv.DictReader((OUT/'round_coverage.csv').open()));eligible=defaultdict(set)
 for r in cov:
  if int(r['eligible_round_count']):eligible[(r['source'],r['task_id'])].add(r['role'])
 previous=ORIGINAL_REVIEW_EXCLUSIONS
 families={(r['source'],r['task_id']):r['family'] for r in csv.DictReader((ROOT/'Experiment/shared/task_selection.csv').open())}
 selected=[];coverage=[]
 for source in SOURCES:
  all_cases=[k for k,v in eligible.items() if k[0]==source and v=={'actor','simulator'}]
  available=[k for k in all_cases if k not in previous]
  long_cases=[k for k in available if count_long(k)>=(len(arms) if REQUIRE_ALL_LONG else 1)]
  ordered=sorted(long_cases,key=lambda k:(-count_long(k),-min(lengths(k).values()),-sum(lengths(k).values()),sha((SEED+'|'+k[0]+'|'+k[1]).encode())))
  picked=ordered[:30]
  coverage.append(dict(source=source,requested=30,eligible=len(all_cases),previously_displayed=len(all_cases)-len(available),additional_available=len(available),long_eligible=len(long_cases),all_five_long=sum(count_long(k)==len(arms) for k in available),selected=len(picked),shortfall=max(0,30-len(picked))))
  selected.extend(dict(source=k[0],task_id=k[1],family=families[k],id=sha((k[0]+'|'+k[1]).encode())[:16],selection_rank=i+1,paired_exchanges=lengths(k),long_persona_count=count_long(k)) for i,k in enumerate(picked))
 assert len({(r['source'],r['task_id']) for r in selected})==len(selected)
 assert not previous & {(r['source'],r['task_id']) for r in selected}
 return selected,coverage

def local_umap(x):
 import umap
 settings=UMAP_SETTINGS | {'n_neighbors':min(UMAP_SETTINGS['n_neighbors'],len(x)-1)}
 xy=umap.UMAP(**settings).fit_transform(x)
 assert xy.shape==(len(x),2) and np.isfinite(xy).all()
 return xy,settings

def place_labels(fig,axs):
 # Move labels only; never move the projected nodes or trajectory segments.
 fig.canvas.draw();renderer=fig.canvas.get_renderer();scale=fig.dpi/72
 for ax in axs:
  paths=[MplPath(ax.transData.transform(line.get_xydata())) for line in ax.lines]
  nodes=np.concatenate([p.vertices for p in paths])
  taken=[]
  for text in ax.texts:
   if not text.get_text():continue
   text.set_ha('center');text.set_va('center')
   extent=text.get_window_extent(renderer);w,h=extent.width,extent.height
   origin=ax.transData.transform(text.xy);best=None
   for radius in [9,13,18,24,32,42,54,70,90]:
    for theta in np.linspace(0,2*np.pi,24,endpoint=False):
     offset=np.array([np.cos(theta),np.sin(theta)])*radius
     center=origin+offset*scale
     box=Bbox.from_bounds(center[0]-w/2-2,center[1]-h/2-2,w+4,h+4)
     if not ax.bbox.contains(*box.p0) or not ax.bbox.contains(*box.p1):continue
     if any(box.overlaps(b) for b in taken):continue
     if any(path.intersects_bbox(box,filled=False) for path in paths):continue
     if np.any((nodes[:,0]>box.x0-12)&(nodes[:,0]<box.x1+12)&(nodes[:,1]>box.y0-12)&(nodes[:,1]<box.y1+12)):continue
     best=(offset,box);break
    if best is not None:break
   if best is None:raise RuntimeError('No clear round-label position')
   text.set_position(best[0]);taken.append(best[1])

def figure(case,rows,z,c):
 fig,axs=plt.subplots(1,2,figsize=(11.7,6.5));fig.subplots_adjust(left=.075,right=.975,bottom=.19,top=.74,wspace=.27)
 coordinates=[];projections=[]
 for ax,role in zip(axs,['simulator','actor']):
  ids=[i for i,r in enumerate(rows) if r['role']==role];x=z[ids].astype(float);xy,settings=local_umap(x)
  projections.append({'role':role,'method':'UMAP','settings':settings,'fit_messages':len(ids),'umap_learn_version':version('umap-learn'),'input_sha256':sha(x.tobytes())})
  points=[]
  for i,point in zip(ids,xy):
   r=rows[i];points.append(r|{'umap1':float(point[0]),'umap2':float(point[1])})
   coordinates.append({k:v for k,v in r.items() if k!='text'}|{'case_id':case['id'],'umap1':float(point[0]),'umap2':float(point[1])})
  for pi,arm in enumerate(c['arms']):
   values=sorted([r for r in points if r['arm']==arm],key=lambda r:r['round']);p=np.array([[r['umap1'],r['umap2']] for r in values]);color=COLORS[pi]
   ax.plot(p[:,0],p[:,1],color=color,lw=1,alpha=.8,zorder=2)
   for j,(r,node) in enumerate(zip(values,p)):
    artist=ax.scatter(*node,s=28,color=color,edgecolor='white',linewidth=.5,zorder=4)
    artist.set_gid(f"node-{role}-{arm}-{r['round']}")
    ax.annotate(str(r['round']),node,xytext=[(5,6),(-7,6),(5,-9),(-7,-9),(0,10)][(pi+j)%5],textcoords='offset points',fontsize=7,color=color,zorder=5)
   ax.scatter(*p[-1],s=65,marker='D',facecolors='none',edgecolors=color,linewidths=1.1,zorder=5)
   for a,b in zip(p[:-1],p[1:]):
    delta=b-a;ax.annotate('',xy=a+.65*delta,xytext=a+.42*delta,arrowprops={'arrowstyle':'-|>','color':color,'lw':.9,'mutation_scale':8})
  ax.margins(.17);ax.set_title(role.capitalize(),weight='bold');ax.set_xlabel('UMAP 1');ax.set_ylabel('UMAP 2')
 fig.suptitle(NAMES[case['source']]+' | '+case['task_id'],fontsize=11,y=.96)
 from textwrap import fill
 title=case['question'].replace('\n',' ')
 if len(title)>250:title=title[:247]+'…'
 fig.text(.075,.88,fill(title,135),fontsize=8,va='top')
 handles=[Line2D([0],[0],marker='o',color=color,lw=1,label=c['labels'][arm],markersize=4) for arm,color in zip(c['arms'],COLORS)]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.07),ncol=5,frameon=False,fontsize=9)
 fig.text(.075,.035,'Trial 1 · round numbers = observed messages · diamond = final node · local UMAP axes are not comparable across cases.',fontsize=8)
 place_labels(fig,axs)
 fig.canvas.draw()
 require_matplotlib_panel_alignment(fig,json_out=PUBLIC/'qa'/f"{case['id']}.alignment.json",strict=True)
 return fig,coordinates,projections

def build():
 DEST.mkdir(parents=True,exist_ok=True);(DEST/'plots').mkdir(exist_ok=True);(DEST/'pdf').mkdir(exist_ok=True)
 c,rows,z=load();cases,coverage=select_cases(rows);indexed=defaultdict(list)
 for i,r in enumerate(rows):indexed[(r['source'],r['task_id'])].append(i)
 prov=json.loads((OUT/'provenance.json').read_text());logs={(r['source'],r['task_id']):r for r in prov['event_logs'] if r['arm']=='persona_off' and r['trial']==1}
 case_data=[];coordinate_rows=[];manifest=[]
 for source in SOURCES:
  subset=[r for r in cases if r['source']==source]
  if not subset:continue
  with PdfPages(DEST/'pdf'/f'{source}.pdf') as pdf:
   for case in subset:
    k=(case['source'],case['task_id']);ids=indexed[k];messages=[rows[i] for i in ids]
    assert all({r['arm'] for r in messages if r['role']==role}==set(c['arms']) for role in c['roles'])
    public=json.loads((ROOT/logs[k]['path']).parent.joinpath('public_input.json').read_text())
    case['question']=public['question'];case['source_label']=NAMES[source];case['family_label']=NAMES[case['family']]
    fig,coords,projections=figure(case,messages,z[ids],c);stream=StringIO();fig.savefig(stream,format='svg',facecolor='white');svg=stream.getvalue();svg=svg[svg.index('<svg'):]
    # SVG geometry comes from Matplotlib. These titles/link IDs expose the
    # corresponding current message on hover/click, without any extra model.
    for r in messages:
     gid=f"node-{r['role']}-{r['arm']}-{r['round']}";tip=f"{c['labels'][r['arm']]} · {r['role']} · round {r['round']}"
     svg=svg.replace(f'<g id="{gid}">',f'<g id="{gid}" class="message-node" data-role="{r["role"]}" data-arm="{r["arm"]}" data-round="{r["round"]}" style="cursor:pointer"><title>{html.escape(tip)}</title>')
    (DEST/'plots'/f"{case['id']}.svg").write_text(svg);pdf.savefig(fig);plt.close(fig)
    case_data.append(case|{'svg':svg,'messages':messages,'projection':projections})
    write_json(DEST/'plots'/f"{case['id']}.projection.json",projections)
    coordinate_rows.extend(coords)
    manifest.append({k:v for k,v in case.items() if k!='question'}|{'trial':1,'message_count':len(messages),'round_counts':{role:{a:sum(r['role']==role and r['arm']==a for r in messages) for a in c['arms']} for role in c['roles']}})
   print(f'{source}: rendered {len(subset)} question pages',flush=True)
 case_data.sort(key=lambda r:(-r['long_persona_count'],-min(r['paired_exchanges'].values()),-sum(r['paired_exchanges'].values()),r['id']))
 payload={'config':{'arms':c['arms'],'labels':c['labels'],'colors':dict(zip(c['arms'],COLORS))},'coverage':coverage,'cases':case_data}
 template=Path(__file__).with_name('gallery_template.html').read_text();data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
 (DEST/'index.html').write_text(template.replace('__DATA_JSON__',data))
 write_json(PUBLIC/'manifest.json',{'selection_rule':SELECTION_RULE,'minimum_paired_exchanges':MIN_EXCHANGES,'require_all_long':REQUIRE_ALL_LONG,'seed':SEED,'scope':'Exploratory manual case review, separate from aggregate estimates.','projection_method':'UMAP','projection_settings':UMAP_SETTINGS,'umap_learn_version':version('umap-learn'),'runtime_versions':{p:version(p) for p in ['numpy','scipy','scikit-learn','numba','pynndescent','matplotlib']},'embedding_model':c['model_id'],'embedding_revision':c['model_revision'],'coverage':coverage,'cases':manifest})
 write_csv(PUBLIC/'coordinates.csv',coordinate_rows)
 write_csv(PUBLIC/'coverage.csv',coverage)
 write_csv(PUBLIC/'selection_template.csv',[dict(case_id=r['id'],source=r['source'],task_id=r['task_id'],family=r['family'],selected='',notes='') for r in manifest])
 write_json(PUBLIC/'validation.json',{'cases':len(cases),'question_pair_duplicates':0,'existing_main_cases_excluded':True,'all_five_personas_per_role':True,'trial':1,'private_message_text_location':'ignored runs/semantic-review/index.html','new_model_calls':0,'umap_fit':'Each question and role independently, all observed trial-1 rounds and five settings','source_counts':dict(Counter(r['source'] for r in cases)),'coordinate_rows':len(coordinate_rows)})
 # Remove only obsolete generated review artifacts, never raw traces or embeddings.
 keep={r['id'] for r in manifest};sources={r['source'] for r in manifest}
 for path in (DEST/'plots').iterdir():
  if re.fullmatch(r'[0-9a-f]{16}\.(svg|projection\.json)',path.name) and path.name.split('.')[0] not in keep:path.unlink()
 for path in (DEST/'pdf').glob('*.pdf'):
  if path.stem in SOURCES and path.stem not in sources:path.unlink()
 for path in (PUBLIC/'qa').glob('*.alignment.json'):
  if path.name.split('.')[0] not in keep:path.unlink()
 for path in (PUBLIC/'qa').glob('*.collisions.json'):
  path.unlink() # Geometry audits must be rerun on the replacement books.
 return manifest,coverage

if __name__=='__main__':build()
