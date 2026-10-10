"""Offline recorded actor actions; paired, source-balanced tool-use differences."""
import json,sys,hashlib
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Experiment/01_behavioral_diversity'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import summarize,write_csv,write_json,B,SEED
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
SOURCES=['asibench','bixbench','discoverybench','expbench']
TOOLS={'execute_command','inspect_repository','execute_check'}
EXCLUDE={'end_researcher_turn','ask_researcher','report_progress','submit_plan','submit_result','submit_design'}
DATA=BASE/'data/tool_calls'
def key(r):return r['source'],r['task_id'],r['arm'],r['trial']
def extract():
    snapshot=BASE/'data/behavior_all_personas/snapshot.json'
    s=json.loads(snapshot.read_text());logs={key(r):r for r in s['event_logs']}
    eligible=[r for r in s['episodes'] if r['eligible'] and r['arm'] in ARMS]
    assert len({key(r) for r in eligible})==len(eligible)
    def one(r):
        out={k:r[k] for k in ['source','task_id','arm','trial','study_id','family']}
        out.update(tool_calls=None,status='not_applicable' if r['source'] not in SOURCES else 'missing_log')
        if r['source'] not in SOURCES:return out,[]
        log=logs.get(key(r));p=ROOT/Path(log['path']).parent/'actor_events.jsonl' if log else None
        if p is None or not p.exists():return out,[]
        raw=p.read_bytes();counts=Counter();seen=set()
        for line in raw.splitlines():
            if not line.strip():continue
            e=json.loads(line)
            if e.get('kind')!='ActionEvent':continue
            ident=e.get('tool_call_id') or e.get('id')
            assert ident and ident not in seen, ('duplicate/unidentified action',str(p),ident)
            seen.add(ident);name=e['tool_name']
            assert name in TOOLS|EXCLUDE,('Unclassified tool',name)
            counts[name]+=1
        out.update(tool_calls=sum(counts[t] for t in TOOLS),status='available',action_log=str(p.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest())
        return out,[dict(source=r['source'],task_id=r['task_id'],arm=r['arm'],trial=r['trial'],tool=t,calls=n,included=t in TOOLS) for t,n in sorted(counts.items())]
    with ThreadPoolExecutor(max_workers=12) as pool:results=list(pool.map(one,eligible))
    episodes=[x[0] for x in results];tools=[r for x in results for r in x[1]]
    absolute={a:summarize([r for r in episodes if r['arm']==a],field='tool_calls',balanced=True) for a in ARMS}
    index={a:{(r['source'],r['task_id'],r['trial']):r for r in episodes if r['arm']==a and r['tool_calls'] is not None} for a in ARMS}
    pairs=[]
    for i,a in enumerate(ARMS):
        for b in ARMS[:i]:
            keys=sorted(index[a].keys()&index[b].keys())
            rows=[index[a][k]|dict(value=index[a][k]['tool_calls']-index[b][k]['tool_calls']) for k in keys]
            stat=summarize(rows,balanced=True)
            assert set(stat['source_counts'])==set(SOURCES)
            pairs.append(dict(row=a,column=b,**stat))
    summary=dict(arms=ARMS,absolute=absolute,pairs=pairs,coverage={src:dict(Counter(r['status'] for r in episodes if r['source']==src)) for src in SOURCES+['sciconvbench']},method=dict(unit='Recorded actor execution/inspection actions per complete original episode; not API requests or shell subcommands',included_tools=sorted(TOOLS),excluded_tools=sorted(EXCLUDE),aggregation='Pair matched source/question/trial first; average matched trial differences within question, then questions within source; equal source weights (four sources). Absolute means use each setting available cases and need not subtract to the paired differences.',uncertainty=f'{B} source-stratified study-cluster bootstrap resamples; percentile 95% CI; seed {SEED}; marginal descriptive intervals, no significance color or stars',missing='SciConv not applicable; missing actor logs excluded, never zero-filled',snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest()))
    write_csv(DATA/'episodes.csv',episodes);write_csv(DATA/'tool_composition.csv',tools)
    write_csv(DATA/'pairwise.csv',[{k:v for k,v in r.items() if k not in ['ci95','source_counts','studies_by_source']}|dict(ci_low=r['ci95'][0],ci_high=r['ci95'][1],source_counts=json.dumps(r['source_counts'])) for r in pairs])
    write_json(DATA/'summary.json',summary)
    return summary

def plot(summary):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    from audit_panel_alignment import require_matplotlib_panel_alignment
    out=BASE/'figures/tool_calls';out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none'})
    m=np.zeros((5,5))
    for r in summary['pairs']:
        i,j=ARMS.index(r['row']),ARMS.index(r['column']);m[i,j]=r['mean'];m[j,i]=-r['mean']
    assert np.allclose(m,-m.T)
    bound=max(float(np.max(np.abs(m))),.01)
    fig,ax=plt.subplots(figsize=(4.15,3.7));fig.subplots_adjust(left=.16,right=.91,bottom=.22,top=.86)
    cmap=plt.get_cmap('BrBG').copy();cmap.set_bad('#E5E5E5')
    im=ax.imshow(np.ma.array(m,mask=np.eye(5,dtype=bool)),cmap=cmap,norm=TwoSlopeNorm(vmin=-bound,vcenter=0,vmax=bound))
    labels=['Off','155','001','003','046'];ax.set_xticks(range(5),labels);ax.set_yticks(range(5),labels);ax.tick_params(length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    for i in range(5):
        for j in range(5):
            if i!=j:ax.text(j,i,f'{m[i,j]:+.2f}',ha='center',va='center',fontsize=8,color='white' if abs(m[i,j])>.65*bound else '#17212B')
    ax.set_title('Actor tool-call difference',fontsize=10,pad=10)
    cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.13,fraction=.06,aspect=30)
    cb.set_label('Calls / episode · row − column',fontsize=8);cb.ax.tick_params(labelsize=7)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,axes=[ax],exclude_axes=[cb.ax],json_out=str(out/'alignment.json'),strict=True,tolerance_pt=1.5)
    fig.savefig(out/'tool_call_pairwise.pdf',bbox_inches='tight',pad_inches=.035,facecolor='white')
    fig.savefig(out/'tool_call_pairwise.svg',bbox_inches='tight',pad_inches=.035,facecolor='white')
    fig.savefig(out/'tool_call_pairwise.png',dpi=600,bbox_inches='tight',pad_inches=.035,facecolor='white')
    plt.close(fig)
    return out

def report(s):
    lines=['# Actor tool-use analysis','',s['method']['unit']+'.','',s['method']['aggregation'],'',s['method']['uncertainty'],'',s['method']['missing'], '', '| Setting | Calls / episode [95% CI] | Questions | Episodes |','|---|---:|---:|---:|']
    label=lambda a:'Off' if a=='persona_off' else a.split('_')[1]
    for a,v in s['absolute'].items():lines.append(f"| {label(a)} | {v['mean']:.2f} [{v['ci95'][0]:.2f}, {v['ci95'][1]:.2f}] | {v['tasks']} | {v['episodes']} |")
    lines+=['','| Row − column | Paired difference [95% CI] | Questions | Episode pairs |','|---|---:|---:|---:|']
    for v in s['pairs']:lines.append(f"| {label(v['row'])} − {label(v['column'])} | {v['mean']:+.2f} [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}] | {v['tasks']} | {v['episodes']} |")
    lines+=['','## Candidate caption','', 'Pairwise differences in recorded actor tool calls under five simulator persona settings. Calls include execute_command (ASI, BixBench, DiscoveryBench), inspect_repository and execute_check (EXP-Bench); researcher handoffs and protocol actions are excluded. Each cell is row minus column, matched on source, question and trial, averaged over trials within question and over questions within source, then equally over the four sources. Color encodes magnitude and direction, not statistical significance. The diagonal is masked. SciConvBench uses a different interaction interface and is excluded rather than assigned zero calls. Marginal 95% study-cluster bootstrap intervals and pair-specific coverage are supplied in the table. More calls do not necessarily imply better scientific performance or greater behavioral diversity. Single-trial settings do not support estimates of rollout variability.','', 'Extracted tool-call IDs are checked for duplicates within each episode. Counts refer to recorded action invocations, not successful execution or distinct shell commands. Coverage and per-episode provenance hashes are saved in data/tool_calls/.']
    text='\n'.join(lines)+'\n';(BASE/'TOOL_CALLS.md').write_text(text);return text
if __name__=='__main__':
    s=extract();report(s);print(plot(s));print(json.dumps(s['coverage']))
