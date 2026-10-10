"""Four-panel paired behavior figure; offline events and recorded API usage only."""
import json,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'Experiment/01_behavioral_diversity'
DATA=BASE/'data/compact_behavior';FIG=BASE/'figures/compact_behavior'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import summarize,write_json,write_csv,markdown_table
sys.path.insert(0,str(ROOT/'Experiment/02_performance_and_fields/code'))
from pairwise_performance import sign_test,holm
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
LABELS=['Off','155','001','003','046']
METRICS=[('simulator_tokens_total','A  Simulator output','k tokens / episode',2,1000),('actor_tokens_total','B  Actor output','k tokens / episode',2,1000),('revision_requests','B  Revision requests','Requests / episode',2,1),('clarification_recall','C  Clarification recall','Percentage points',1,1),('tool_calls','D  Actor tool use','Calls / episode',2,1)]
STAR_NOTE='Star key: A/B, Holm-adjusted p < 0.20 across 50 comparisons; C, absolute difference > 2 percentage points; D, absolute difference > 0.2 calls/episode. C/D stars highlight user-selected effect-size thresholds, not statistical significance or 95% confidence. Thresholds were selected after inspection.'
def figure_star(r):
    if r['metric']=='clarification_recall':return '*' if abs(r['mean'])>2 else ''
    if r['metric']=='tool_calls':return '*' if abs(r['mean'])>.2 else ''
    return r['star']
def key(r):return r['source'],r['task_id'],r['arm'],r['trial']
def extract():
    p=ROOT/'Experiment/02_performance_and_fields/data/model_scorecard/episodes.json';source=json.loads(p.read_text())
    b=BASE/'data/behavior_all_personas/snapshot.json';behavior={key(r):r for r in json.loads(b.read_text())['episodes']}
    def one(r):
        out={k:r[k] for k in ['source','task_id','study_id','arm','trial','performance']};v=behavior[key(r)]
        out.update(revision_requests=v.get('revision_requests'),clarification_recall=v.get('clarification_recall'),tool_calls=r.get('tool_calls'),combined_tokens=None)
        if not r.get('api_log'):return out
        log=ROOT/r['api_log'];raw=log.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['api_sha256']
        usage={'actor':[],'researcher':[]}
        for line in raw.splitlines():
            if not line.strip():continue
            c=json.loads(line)
            if c.get('phase')=='request' or c.get('role') not in usage:continue
            u=c.get('usage') or (c.get('response') or {}).get('usage') or {}
            count=u.get('completion_tokens');assert count is None or count>=0
            usage[c['role']].append(count)
        if all(usage.values()) and all(x is not None for vv in usage.values() for x in vv):
            out['combined_tokens']=sum(sum(vv) for vv in usage.values())
            out['actor_tokens_total']=sum(usage['actor']);out['simulator_tokens_total']=sum(usage['researcher'])
            if r.get('actor_output_tokens') is not None:assert out['actor_tokens_total']==r['actor_output_tokens']
        out.update(api_log=r['api_log'],api_sha256=r['api_sha256'])
        return out
    with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(one,source))
    assert len(rows)==1958 and len({key(r) for r in rows})==1958
    write_json(DATA/'episodes.json',rows)
    write_json(DATA/'provenance.json',{'inputs':[{'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in [p,b]],'combined_tokens':'Whole-episode actor + researcher completion tokens including reasoning, initial researcher decisions and final actor responses; no judge, input or estimated tokens; EXP request records excluded.'})
    return rows

def analyze(rows=None):
    rows=rows or json.loads((DATA/'episodes.json').read_text());results=[]
    for metric,title,unit,precision,scale in METRICS:
        index={a:{(r['source'],r['task_id'],r['trial']):r for r in rows if r['arm']==a and r.get(metric) is not None} for a in ARMS}
        for i,a in enumerate(ARMS):
            for j,b in enumerate(ARMS[:i]):
                common=sorted(index[a].keys()&index[b].keys())
                differences=[index[a][k]|dict(value=(index[a][k][metric]-index[b][k][metric])/scale) for k in common]
                stat=summarize(differences,balanced=True);assert stat['mean'] is not None
                tasks=defaultdict(list)
                for r in differences:tasks[(r['source'],r['study_id'],r['task_id'])].append(r['value'])
                counts=Counter(k[0] for k in tasks);blocks=defaultdict(float)
                for (src,study,task),vv in tasks.items():blocks[(src,study)]+=float(np.mean(vv))/(counts[src]*len(counts))
                assert np.isclose(sum(blocks.values()),stat['mean'])
                p,draws,method=sign_test(list(blocks.values()),1,20261002+len(results));assert p is not None
                results.append(dict(metric=metric,row=a,column=b,row_index=i,column_index=j,unit=unit,p_raw=p,draws=draws,test=method,**stat))
    adjusted=holm([r['p_raw'] for r in results])
    for r,p in zip(results,adjusted):r.update(p_holm=float(p),star='*' if p<.20 else '')
    for r in results:r['figure_star']=figure_star(r)
    assert len(results)==50
    result={'arms':ARMS,'comparisons':results,'methods':{'test':'Two-sided paired study-cluster sign flip; exact <=16 study blocks, otherwise 99,999 Monte Carlo draws with plus-one correction. Source-balanced weighted task differences; all tasks in a study share a sign. Requires independent study blocks and blockwise sign symmetry/exchangeability under the null.', 'multiplicity':'Holm across the original 50 metric/persona-pair comparisons (including the undisplayed revision-request comparisons); one star for adjusted p<0.20, none otherwise. CIs are pointwise 95% study bootstrap, not multiplicity-adjusted.','outcome_condition':'All panels include all eligible matched episodes, without filtering on final performance. Metrics are calculated per episode before averaging; coverage varies by pair and metric.', 'pairing':'Match source/question/trial, average repeats within question, then questions within benchmark and benchmarks equally. Pair/metric-specific coverage.','tokens':'Actor and simulator recorded output separately per whole episode including reasoning, initial simulator decisions and final actor responses; no judge usage. Display in thousands.','limits':'Historical selected persona panel, unequal repeats and metric-specific availability; exploratory. The display threshold was changed to 0.20 after inspecting the results. Stars do not establish better adaptation or human realism.'}}
    result['methods']['figure_annotations']=STAR_NOTE
    write_json(DATA/'summary.json',result)
    write_csv(DATA/'comparisons.csv',[{k:v for k,v in r.items() if k not in ['ci95','source_counts','studies_by_source']}|dict(ci_low=r['ci95'][0],ci_high=r['ci95'][1],source_counts=json.dumps(r['source_counts'])) for r in results])
    return result

def plot(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.patches import Rectangle
    from audit_panel_alignment import require_matplotlib_panel_alignment
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,4,figsize=(10.8,3.05));fig.subplots_adjust(left=.045,right=.992,top=.89,bottom=.30,wspace=.21)
    caxes=[]
    panels=[m for m in METRICS if m[0]!='revision_requests']
    token_bound=max(abs(r['mean']) for r in s['comparisons'] if r['metric'] in ['simulator_tokens_total','actor_tokens_total'])
    for ax,(metric,title,unit,precision,scale) in zip(axes,panels):
        rr=[r for r in s['comparisons'] if r['metric']==metric];mat=np.full((5,5),np.nan)
        for r in rr:mat[r['row_index'],r['column_index']]=r['mean']
        bound=max(token_bound if metric in ['simulator_tokens_total','actor_tokens_total'] else float(np.nanmax(np.abs(mat))),1e-6)
        cmap=plt.get_cmap('BrBG').copy();cmap.set_bad('white')
        im=ax.imshow(np.ma.masked_invalid(mat),cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound),aspect='auto')
        for i in range(5):ax.add_patch(Rectangle((i-.5,i-.5),1,1,facecolor='#E5E5E5',edgecolor='none'))
        for r in rr:
            v=r['mean'];txt=f'{v:+.{precision}f}'
            if float(txt)==0:txt=f'{0:.{precision}f}'
            ax.text(r['column_index'],r['row_index'],txt+figure_star(r),ha='center',va='center',fontsize=8.5,color='white' if abs(v)>.65*bound else '#17212B')
        ax.set_xticks(range(5),LABELS);ax.set_yticks(range(5),LABELS);ax.tick_params(length=0,pad=3,labelsize=9)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.set_title(title,fontsize=10,weight='bold',pad=6)
        box=ax.get_position();ca=fig.add_axes([box.x0,.16,box.width,.025]);caxes.append(ca)
        cb=fig.colorbar(im,cax=ca,orientation='horizontal');cb.ax.tick_params(labelsize=8,length=2,pad=2);cb.set_label(unit,fontsize=9,labelpad=3)
        from matplotlib.ticker import MaxNLocator
        cb.locator=MaxNLocator(nbins=3);cb.update_ticks()
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,axes=list(axes),panel_ids=['A','B','C','D'],row_groups=[['A','B','C','D']],exclude_axes=caxes,json_out=str(FIG/'alignment.json'),strict=True,tolerance_pt=1.5)
    fig.savefig(FIG/'pairwise_behavior_four.pdf',bbox_inches='tight',pad_inches=.025)
    fig.savefig(FIG/'pairwise_behavior_four.svg',bbox_inches='tight',pad_inches=.025)
    fig.savefig(FIG/'pairwise_behavior_four.png',dpi=600,bbox_inches='tight',pad_inches=.025)
    plt.close(fig)
    return FIG

def report(s):
    caption='**Four-panel behavioral comparison.** Cells show row minus column for Off/155/001/003/046. A: simulator episode-total output tokens; B: actor episode-total output tokens. Both include reasoning, are expressed in thousands, and share color limits. C: mean per-episode clarification recall (percentage-point differences). D: actor tool calls per episode. All four panels show lower triangles; gray diagonal denotes self-comparison. All eligible matched episodes are included regardless of final performance. Tool use applies to four execution/design sources; clarification recall applies to SciConv. Match question/trial before averaging, then equally weight questions within benchmarks and available benchmarks. Coverage varies by metric/pair. Revision requests were removed from this display after inspection of nonsignificant results; their ten tests remain in the original 50-comparison Holm correction and source-data tables. '+STAR_NOTE
    text='# Compact paired behavioral analysis\n\n'+caption+'\n\nStars alongside p values in the tables below indicate Holm-adjusted p < 0.20 only; these statistical flags are distinct from the C/D figure highlights.\n\n'
    for metric,title,unit,precision,scale in METRICS:
        if metric=='revision_requests':continue
        rr=[r for r in s['comparisons'] if r['metric']==metric]
        text+='## '+title+'\n\n'+markdown_table(['Row − column','Difference [95% CI]','Holm p','Questions','Episode pairs','Questions by source'],[[LABELS[r['row_index']]+' − '+LABELS[r['column_index']],f"{r['mean']:+.3f} [{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}]",f"{r['p_holm']:.4g}"+r['star'],r['tasks'],r['episodes'],json.dumps(r['source_counts'])] for r in rr])+'\n\n'
    text+='## Methods\n\n'+'\n\n'.join(s['methods'].values())+'\n'
    (BASE/'COMPACT_BEHAVIOR.md').write_text(text);return text
if __name__=='__main__':
    s=analyze(extract() if '--extract' in sys.argv else None);report(s);plot(s)
    print('Stars by metric:',dict(Counter(r['metric'] for r in s['comparisons'] if r['star'])),flush=True)
