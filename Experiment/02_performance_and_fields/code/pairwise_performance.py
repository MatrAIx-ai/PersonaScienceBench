"""Exploratory all-pairs performance: paired study-block sign flips, global Holm."""
import json,hashlib,itertools
from collections import defaultdict
import numpy as np
from analyze_all_available import BASE,DATA,compatible
from analysis_utils import SOURCES,FAMILIES,NAMES,write_csv
ARMS=['persona_off','candidate_155','candidate_001','candidate_003','candidate_046']
DEST=BASE/'data/pairwise_selected';DRAWS=99999;SEED=20261001

def sign_test(sums,n,seed):
    sums=np.asarray(sums,float);k=len(sums);obs=abs(sums.sum()/n)
    if k<2:return None,0,'unavailable: fewer than two study clusters'
    if k<=16:
        bits=(np.arange(2**k,dtype=np.uint64)[:,None]>>np.arange(k,dtype=np.uint64))&1
        null=(bits.astype(float)*2-1)@sums/n
        return float(np.mean(np.abs(null)>=obs-1e-12)),len(null),'exact'
    rng=np.random.default_rng(seed);extreme=0
    for start in range(0,DRAWS,2048):
        count=min(2048,DRAWS-start)
        null=(rng.integers(0,2,(count,k))*2-1)@sums/n
        extreme+=np.count_nonzero(np.abs(null)>=obs-1e-12)
    return float((extreme+1)/(DRAWS+1)),DRAWS,'Monte Carlo'

def holm(values):
    order=np.argsort(values);out=np.empty(len(values));last=0.
    for rank,i in enumerate(order):
        last=max(last,min(1.,(len(values)-rank)*values[i]));out[i]=last
    return out

def main():
    raw=(DATA/'snapshot.json').read_bytes();snap=json.loads(raw)
    rows=[r for r in snap['episodes'] if r['view']=='available' and r['arm'] in ARMS and r.get('score') is not None]
    index={(r['arm'],r['source'],r['task_id'],r['trial']):r for r in rows};out=[];matched=[]
    for i,j in itertools.combinations(range(5),2):
        pairs=[]
        for r in rows:
            if r['arm']!=ARMS[i]:continue
            b=index.get((ARMS[j],r['source'],r['task_id'],r['trial']))
            if b is None or not compatible(r,b):continue
            assert r['study_id']==b['study_id'] and r['family']==b['family']
            pairs.append(dict(source=r['source'],family=r['family'],task_id=r['task_id'],study_id=r['study_id'],trial=r['trial'],value=r['score']-b['score']))
        matched.extend(dict(p,persona_i=ARMS[i],persona_j=ARMS[j]) for p in pairs)
        for field,groups in [('source',SOURCES),('family',FAMILIES)]:
            for group in groups:
                pp=[p for p in pairs if p[field]==group];tasks=defaultdict(list)
                for p in pp:tasks[(p['source'],p['study_id'],p['task_id'])].append(p['value'])
                clusters=defaultdict(float)
                for (source,study,task),values in tasks.items():clusters[(source,study)]+=float(np.mean(values))
                n=len(tasks);seed=SEED+int(hashlib.sha256(f'{i},{j},{field},{group}'.encode()).hexdigest()[:8],16)
                pval,draws,method=sign_test(list(clusters.values()),n,seed) if n else (None,0,'no matched data')
                out.append(dict(persona_i=ARMS[i],persona_j=ARMS[j],level=field,group=group,mean=sum(clusters.values())/n if n else None,p_raw=pval,p_holm=None,tasks=n,episodes=len(pp),studies=len(clusters),trial_ids=','.join(map(str,sorted({p['trial'] for p in pp}))),draws=draws,method=method))
    # Include unavailable hypotheses as p=1 to retain the declared family of 90 tests.
    adj=holm([r['p_raw'] if r['p_raw'] is not None else 1. for r in out])
    for r,p in zip(out,adj):r['p_holm']=float(p) if r['p_raw'] is not None else None
    DEST.mkdir(exist_ok=True)
    result=dict(arms=ARMS,comparisons=out,methods=dict(statistic='Row minus column; match task and trial, average trials within task, then tasks equally.',test='Two-sided study-cluster sign flip: all questions/trials in each source-study block change sign together; exact if <=16 clusters, otherwise 99999 random flips with plus-one correction.',assumptions='Independent study blocks and joint sign symmetry under null (or valid blockwise label exchangeability); not a distribution-free test of only a zero mean.',multiplicity='Holm over all 90 unique persona-pair × group comparisons; mirrored cells are not additional tests; unavailable tests count as p=1.',scope='Exploratory, outcome-selected personas, conditional on observed trials and evaluable compatible pairs. Sparse clusters yield coarse p values; no test for <2 clusters. Missing scientific submissions score zero; infrastructure failures excluded. Source-study blocks preserved; families are descriptive mixtures.',snapshot_sha256=hashlib.sha256(raw).hexdigest(),seed=SEED))
    (DEST/'summary.json').write_text(json.dumps(result,indent=2)+'\n');write_csv(DEST/'comparisons.csv',out);write_csv(DEST/'matched_episodes.csv',matched)
    print('Pairwise comparisons:',len(out),'Holm significant:',sum(r['p_holm'] is not None and r['p_holm']<.05 for r in out))
    return result
if __name__=='__main__':main()
