"""Prespecified method set for exploratory sensitivity; no method selection by p value."""
import csv,json,hashlib,copy
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import t as tdist
from pairwise_performance import DEST,BASE,holm
OUT=BASE/'data/test_sensitivity'
METHODS={'sign_flip':'Study-cluster sign flip','cluster_t':'Cluster-robust t (CR1)','studentized_sign_flip':'Studentized cluster sign flip'}

def tstat(sums,counts):
    sums=np.asarray(sums,float);counts=np.asarray(counts,float);g=len(counts);n=counts.sum()
    means=sums.sum(axis=-1)/n
    resid=sums-means[...,None]*counts
    se=np.sqrt(g/(g-1)*np.sum(resid**2,axis=-1))/n
    return np.divide(np.abs(means),se,out=np.where(np.abs(means)<1e-12,0.,np.inf),where=se>1e-12)

def studentized_p(sums,counts,seed):
    g=len(sums);obs=tstat(sums,counts);rng=np.random.default_rng(seed);exact=g<=16
    total=2**g if exact else 99999;exceed=0
    for lo in range(0,total,2048):
        size=min(2048,total-lo)
        signs=(((np.arange(lo,lo+size,dtype=np.uint64)[:,None]>>np.arange(g,dtype=np.uint64))&1).astype(float)*2-1) if exact else rng.integers(0,2,(size,g))*2-1
        null=tstat(signs*np.asarray(sums),counts)
        exceed+=np.count_nonzero(null>=obs-1e-12)
    return exceed/total if exact else (exceed+1)/(total+1)

def main():
    base=json.loads((DEST/'summary.json').read_text());pairs=list(csv.DictReader((DEST/'matched_episodes.csv').open()));results={m:copy.deepcopy(base) for m in METHODS}
    for idx,r in enumerate(base['comparisons']):
        tasks=defaultdict(list)
        for x in pairs:
            if x['persona_i']==r['persona_i'] and x['persona_j']==r['persona_j'] and x[r['level']]==r['group']:
                tasks[(x['source'],x['study_id'],x['task_id'])].append(float(x['value']))
        clusters=defaultdict(list)
        for (source,study,task),v in tasks.items():clusters[(source,study)].append(np.mean(v))
        sums=np.array([sum(v) for v in clusters.values()]);counts=np.array([len(v) for v in clusters.values()]);g=len(sums)
        assert len(tasks)==r['tasks'] and g==r['studies']
        if len(tasks):assert np.isclose(sums.sum()/counts.sum(),r['mean'])
        for m in ['cluster_t','studentized_sign_flip']:
            z=results[m]['comparisons'][idx];p=None
            z['method']=METHODS[m];z['draws']=0
            if g>=2:
                # Degenerate nonzero cluster-residual variance is not estimable for CR1.
                stat=float(tstat(sums,counts))
                if m=='cluster_t':p=float(2*tdist.sf(stat,g-1)) if np.isfinite(stat) else None
                else:
                    seed=20261001+int(hashlib.sha256(str(idx).encode()).hexdigest()[:8],16)
                    p=float(studentized_p(sums,counts,seed));z['draws']=2**g if g<=16 else 99999
            z['p_raw']=p;z['p_holm']=None;z['few_clusters']=g<20;z['degrees_of_freedom']=g-1 if g>=2 else None
    flat=[];overview=[]
    for m,s in results.items():
        pp=[r['p_raw'] if r['p_raw'] is not None else 1 for r in s['comparisons']]
        for r,p in zip(s['comparisons'],holm(pp)):
            r['p_holm']=float(p) if r['p_raw'] is not None else None
            flat.append(dict(r,test=m))
        s['methods']['test']=METHODS[m]
        s['methods']['sensitivity']='Fixed three-method comparison; same task-weighted effect and matching, two-sided, Holm across 90 tests within each method. No correction across choosing methods; outcome-driven selection remains exploratory.'
        if m=='cluster_t':s['methods']['assumptions']='Intercept-only OLS on task means; CR1 study-cluster sandwich SE, factor G/(G-1), t reference with G-1 df. Independent clusters, sufficiently many clusters; few or highly unequal clusters can distort size. No normality of individual episodes required asymptotically. Zero nonzero-effect residual variance marked unavailable.'
        if m=='studentized_sign_flip':s['methods']['assumptions']='Same blockwise sign-symmetry/exchangeability assumptions as unstudentized test; recompute CR1 t statistic for every flip. Exact <=16 clusters, else 99999 draws with plus-one correction.'
        folder=OUT/m;folder.mkdir(parents=True,exist_ok=True);(folder/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
        overview.append(dict(test=m,label=METHODS[m],tests=len(pp),unavailable=sum(r['p_raw'] is None for r in s['comparisons']),raw_p_below_05=sum(p<.05 for p in pp),holm_below_05=sum(r['p_holm'] is not None and r['p_holm']<.05 for r in s['comparisons'])))
    from analysis_utils import write_csv
    write_csv(OUT/'comparisons.csv',flat);(OUT/'overview.json').write_text(json.dumps(overview,indent=2)+'\n');print(json.dumps(overview,indent=2))
    return overview
if __name__=='__main__':main()
