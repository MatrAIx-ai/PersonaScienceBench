#!/usr/bin/env python3
"""Final-response domain separation with blocked permutations and question bootstrap."""
import csv,json
from collections import Counter,defaultdict
from itertools import combinations
import numpy as np
from analyze import ROOT,BASE,OUT,CACHE,config,write_json,write_csv
DEST=BASE/'data/semantic_final'
FAMILIES=['life','physical_engineering','math_cs','social_humanities']
PERMUTATIONS=10000
BOOTSTRAPS=20000
SEED=20261008

def holm(ps):
 ps=np.asarray(ps);order=np.argsort(ps);adjusted=np.empty(len(ps));adjusted[order]=np.minimum(1,np.maximum.accumulate(ps[order]*(len(ps)-np.arange(len(ps)))))
 return adjusted

def kernel(x,y):
 # Off-diagonal U statistic equals B_ij -(W_i+W_j)/2 for q != s.
 delta=x-y;k=delta@delta.T/2;np.fill_diagonal(k,0)
 return k

def direct_components(x,y):
 n=len(x);mask=~np.eye(n,dtype=bool)
 wi=(1-x@x.T)[mask].mean();wj=(1-y@y.T)[mask].mean();between=(1-x@y.T)[mask].mean()
 return float(between),float(wi),float(wj)

def quadratic_samples(weights,k):
 return np.einsum('bi,ij,bj->b',weights,k,weights,optimize=True)

def main(question_filter=None, output_dir=None):
 dest=DEST if output_dir is None else output_dir
 c=config();records=json.loads((CACHE/'messages.private.json').read_text());f=np.load(CACHE/'embeddings.npz',allow_pickle=False)
 assert list(f['hashes'])==[r['text_sha256'] for r in records]
 embeddings=f['embeddings']  # Load the compressed matrix once, not once per message.
 selected={}
 for i,r in enumerate(records):
  if r['trial']!=1 or r['arm'] not in c['arms']:continue
  key=(r['source'],r['task_id'],r['arm'],r['role'])
  if key not in selected or (r['round'],r['event_index'])>(records[selected[key]]['round'],records[selected[key]]['event_index']):selected[key]=i
 family={(r['source'],r['task_id']):r['family'] for r in csv.DictReader((ROOT/'Experiment/shared/task_selection.csv').open())}
 questions=sorted({k[:2] for k in selected if all((*k[:2],a,role) in selected for a in c['arms'] for role in c['roles'])})
 if question_filter is not None:questions=[q for q in questions if q in question_filter]
 final_rows=[];results=[];family_results=[];roles={};boot_all=[]
 for role_index,role in enumerate(c['roles']):
  matrices={};bootweights={};metadata={}
  for fi,fam in enumerate(FAMILIES):
   qs=[q for q in questions if family[q]==fam];n=len(qs);assert n>=2
   x=np.array([[embeddings[selected[(*q,a,role)]] for q in qs] for a in c['arms']],dtype=float)
   assert np.allclose(np.linalg.norm(x,axis=2),1,atol=1e-5)
   x/=np.linalg.norm(x,axis=2,keepdims=True)
   rng=np.random.default_rng(SEED+fi);weights=np.zeros((BOOTSTRAPS,n),dtype=float)
   for src in sorted({q[0] for q in qs}):
    ids=[i for i,q in enumerate(qs) if q[0]==src];weights[:,ids]=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)),size=BOOTSTRAPS)
   denominator=n*n-np.sum(weights**2,axis=1);assert np.all(denominator>0)
   matrices[fam]=x;bootweights[fam]=(weights,denominator);metadata[fam]={'n':n,'sources':dict(Counter(q[0] for q in qs))}
   for ai,a in enumerate(c['arms']):
    for q in qs:
     r=records[selected[(*q,a,role)]];final_rows.append({k:v for k,v in r.items() if k!='text'}|{'family':fam,'endpoint':'last nonempty generated message for this role in a complete episode'})
  estimates=np.zeros((5,5));lo=np.zeros((5,5));hi=np.zeros((5,5))
  for pair_index,(i,j) in enumerate(combinations(range(5),2)):
   rng=np.random.default_rng(SEED+100+role_index*10+pair_index)
   observed=[];permutation=np.zeros(PERMUTATIONS);bootstrap=np.zeros(BOOTSTRAPS);components=[]
   for fam in FAMILIES:
    x=matrices[fam];n=x.shape[1];k=kernel(x[i],x[j]);effect=float(k.sum()/(n*(n-1)));b,wi,wj=direct_components(x[i],x[j]);assert np.isclose(effect,b-(wi+wj)/2,atol=1e-10)
    signs=rng.choice([-1.,1.],size=(PERMUTATIONS,n));permutation+=quadratic_samples(signs,k)/(n*(n-1)*4)
    weights,denominator=bootweights[fam];boots=quadratic_samples(weights,k)/denominator;bootstrap+=boots/4;observed.append(effect);components.append((b,wi,wj))
    ci=np.quantile(boots,[.025,.975]);family_results.append(dict(role=role,family=fam,persona_i=c['arms'][i],persona_j=c['arms'][j],questions=n,between=b,within_i=wi,within_j=wj,estimate=effect,ci_low=float(ci[0]),ci_high=float(ci[1])))
   value=float(np.mean(observed));ci=np.quantile(bootstrap,[.025,.975]);p=(1+np.count_nonzero(permutation>=value-1e-12))/(PERMUTATIONS+1)
   for a,b in [(i,j),(j,i)]:estimates[a,b]=value;lo[a,b]=ci[0];hi[a,b]=ci[1]
   av=np.mean(components,axis=0);results.append(dict(role=role,persona_i=c['arms'][i],persona_j=c['arms'][j],questions=len(questions),between=float(av[0]),within_i=float(av[1]),within_j=float(av[2]),estimate=value,ci_low=float(ci[0]),ci_high=float(ci[1]),p_permutation=float(p)))
   boot_all.append(bootstrap)
  roles[role]={'questions':len(questions),'family_counts':{f:m['n'] for f,m in metadata.items()},'source_counts':dict(Counter(q[0] for q in questions)),'family_source_counts':metadata,'estimate':estimates.tolist(),'ci_low':lo.tolist(),'ci_high':hi.tolist()}
 for r,p in zip(results,holm([r['p_permutation'] for r in results])):r.update(p_holm=float(p),significant_holm_005=bool(p<.05))
 for role in c['roles']:
  mat=np.ones((5,5))
  for r in results:
   if r['role']==role:
    i=c['arms'].index(r['persona_i']);j=c['arms'].index(r['persona_j']);mat[i,j]=mat[j,i]=r['p_holm']
  roles[role]['p_holm']=mat.tolist()
 methods={'endpoint':'Last nonempty generated role message among the saved simulator–actor exchanges in a complete original trial-1 episode. Simulator may be a closing message; actor may be its last handoff/question/specification. Not necessarily a successful task submission. Roles may end at different rounds.','question_set':'Common complete five-persona question set for BOTH roles. One final message per persona/question/role.','statistic':'Within each super-family: mean cosine distance across ordered distinct-question cross-persona pairs minus half the sum of the two within-persona distinct-question means. Exclude same question pairs from both quantities. Average four family effects equally (25% each).','permutation':'Independently swap the two persona labels within each question; keep family, benchmark and question identities fixed. This preserves question dependence without using same-question distances. One-sided alternative: cross-persona excess > 0. Monte Carlo p=(1+number of permuted statistics >= observed)/(10000+1).','bootstrap':'Resample whole questions within source benchmark × super-family; retain all five persona outputs together. 20000 resamples, percentile pointwise 95% CI. Exclude pairs representing the same original question even if selected twice; multiplicity-weight the remaining pairs and renormalize. Stratum sizes fixed.','multiplicity':'Holm correction across all 20 role × persona-pair tests. Family-specific estimates and CIs are descriptive, without additional significance testing.','null':'Pairwise persona-label exchangeability within each question. Tests association under this null, not causality or rollout variability.','limitations':'Within-persona spread includes question differences. One observed trial; bootstrap conditions on it. Source-study dependence beyond question is not modeled. Final-message functions and lengths vary by source/persona. Persona panel and endpoint were selected during exploratory analysis; results require confirmatory validation.','permutations':PERMUTATIONS,'bootstrap_resamples':BOOTSTRAPS,'seed':SEED}
 analysis_config={k:c[k] for k in ['arms','labels','roles','model_id','model_revision','preprocessing','manual_cases','case_rule','projection','projection_method','display_rollout','rollouts']}
 analysis_config.update(mode='domain_final_excess',aggregation='equal_super_family',seed=SEED,permutations=PERMUTATIONS,bootstrap_resamples=BOOTSTRAPS)
 write_json(dest/'summary.json',{'config':analysis_config,'roles':roles,'cases':c['manual_cases'],'methods':methods,'message_count':len(final_rows)})
 write_csv(dest/'heatmap_cells.csv',results);write_csv(dest/'family_cells.csv',family_results);write_csv(dest/'final_message_index.csv',final_rows)
 write_csv(dest/'coverage.csv',[dict(source=q[0],task_id=q[1],family=family[q]) for q in questions])
 np.savez_compressed(dest/'bootstrap_estimates.npz',estimates=np.array(boot_all))
 print(json.dumps({'questions':len(questions),'messages':len(final_rows),'significant':{role:sum(r['significant_holm_005'] for r in results if r['role']==role) for role in c['roles']}},indent=2),flush=True)
 return roles

if __name__=='__main__':main()
