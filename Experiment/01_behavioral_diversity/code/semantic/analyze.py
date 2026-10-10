#!/usr/bin/env python3
"""Question-controlled, role-separated semantic analysis. No LLM judgments."""
import argparse
import csv
from collections import Counter,defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'Experiment/01_behavioral_diversity'
CONFIG=Path(__file__).with_name('config.json')
OUT=BASE/'data/semantic'
CACHE=ROOT/'runs/semantic-analysis'
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import write_csv,write_json,sha,NAMES

def config():return json.loads(CONFIG.read_text())
def key(row):return (row['source'],row['task_id'],row['arm'],row['trial'])

def parse_events(events):
    """Pair simulator message with next actor contribution; preserve missing endings."""
    rounds=[];pre_actor=0
    for index,event in enumerate(events):
        kind=event['type'];p=event.get('payload') or {}
        sim=None;actor=None
        if kind=='researcher_reply':sim=p.get('answer')
        elif kind=='researcher_decision':sim=p.get('message')
        elif kind=='agent_handoff':actor=p.get('answer')
        elif kind=='researcher_question':actor=p.get('question')
        elif kind=='final_specification':actor=p.get('answer')
        if sim is not None:
            rounds.append(dict(round=len(rounds)+1,simulator=sim.strip(),actor=None,simulator_event_index=index,actor_event_index=None))
        if actor is not None:
            if not rounds:pre_actor+=1;continue
            # A second handoff without intervening simulator feedback is not one response.
            if rounds[-1]['actor'] is not None:
                raise ValueError('Multiple actor contributions in one simulator exchange; inspect protocol')
            rounds[-1]['actor']=actor.strip();rounds[-1]['actor_event_index']=index
    return rounds,pre_actor

def extract():
    c=config();snap_path=BASE/'data/behavior_all_personas/snapshot.json';snap=json.loads(snap_path.read_text())
    logs={key(x):x for x in snap['event_logs']};records=[];coverage=[];prov=[]
    for episode_index,row in enumerate(snap['episodes']):
        if episode_index%100==0:print(f'Examining episode {episode_index}/{len(snap["episodes"])}',flush=True)
        if row['arm'] not in c['arms'] or row['trial'] not in c['rollouts'][row['arm']]:continue
        meta={k:row[k] for k in ['source','task_id','arm','trial','study_id']}
        meta['termination_status']=row['coordinator_status'];meta['native_status']=row.get('native_status')
        meta['exclusion']=None if row['eligible'] else row['trace_issue']
        if not row['eligible']:
            coverage.append(meta|{'rounds':0});continue
        log=logs[key(row)];path=ROOT/log['path'];raw=path.read_bytes()
        assert sha(raw)==log['sha256'],f'Trace changed: {key(row)}'
        events=[json.loads(x) for x in raw.splitlines() if x.strip()]
        rounds,pre=parse_events(events)
        coverage.append(meta|{'rounds':len(rounds),'pre_simulator_actor_messages':pre})
        prov.append(log)
        for r in rounds:
            for role in c['roles']:
                text=r[role]
                if text:
                    records.append(meta|{'role':role,'round':r['round'],'event_index':r[role+'_event_index'],'text':text,'text_sha256':sha(text.encode())})
    assert len({(*key(r),r['role'],r['round']) for r in records})==len(records)
    CACHE.mkdir(parents=True,exist_ok=True)
    write_json(CACHE/'messages.private.json',records)
    write_csv(OUT/'message_index.csv',[{k:v for k,v in r.items() if k!='text'} for r in records])
    write_csv(OUT/'episode_coverage.csv',coverage)
    write_json(OUT/'provenance.json',{'config':c,'config_sha256':sha(CONFIG.read_bytes()),'input_snapshot_sha256':sha(snap_path.read_bytes()),'event_logs':prov,'message_count':len(records),'slot_count':len(coverage),'eligible_episodes':sum(r['exclusion'] is None for r in coverage),'excluded_episodes':dict(Counter(r['exclusion'] for r in coverage if r['exclusion']))})
    print(json.dumps({'messages':len(records),'episodes':len(coverage),'complete':sum(r['exclusion'] is None for r in coverage)}),flush=True)
    return records

def cosine_matrix(x,y):return 1-np.asarray(x,dtype=float)@np.asarray(y,dtype=float).T

def within(x):
    if len(x)<2:raise ValueError('At least two rollouts required for within-persona distance')
    d=cosine_matrix(x,x);return float(d[np.triu_indices(len(x),1)].mean())

def pair_matrix(groups,adjusted):
    n=len(groups);m=np.zeros((n,n));w=[within(x) for x in groups] if adjusted else [None]*n
    for i,j in combinations(range(n),2):
        value=float(cosine_matrix(groups[i],groups[j]).mean())
        if adjusted:value-=(w[i]+w[j])/2
        m[i,j]=m[j,i]=value
    return m,w

def aggregate(records,z,c):
    if c['mode']=='adjusted' and any(len(c['rollouts'][a])<2 for a in c['arms']):
        raise ValueError('Adjusted heatmap requires at least two configured rollouts for EVERY persona; choose raw explicitly or supply repeats.')
    assert len(records)==len(z) and np.allclose(np.linalg.norm(z,axis=1),1,atol=2e-5)
    idx={(*key(r),r['role'],r['round']):i for i,r in enumerate(records)}
    families={(r['source'],r['task_id']):r['family'] for r in csv.DictReader((ROOT/'Experiment/shared/task_selection.csv').open())}
    questions=sorted({(r['source'],r['task_id']) for r in records});mats={role:{} for role in c['roles']};coverage=[];rounddata=[]
    for role in c['roles']:
        for src,q in questions:
            rounds=sorted({r['round'] for r in records if r['source']==src and r['task_id']==q and r['role']==role})
            valid=[];per=[]
            for t in rounds:
                keys=[(src,q,a,r,role,t) for a in c['arms'] for r in c['rollouts'][a]]
                if not all(k in idx for k in keys):continue
                groups=[z[[idx[(src,q,a,r,role,t)] for r in c['rollouts'][a]]] for a in c['arms']]
                m,w=pair_matrix(groups,c['mode']=='adjusted');valid.append(t);per.append(m)
                for i,j in combinations(range(5),2):rounddata.append(dict(source=src,task_id=q,role=role,round=t,persona_i=c['arms'][i],persona_j=c['arms'][j],distance=float(m[i,j]),within_i=w[i],within_j=w[j]))
            coverage.append(dict(source=src,task_id=q,family=families[(src,q)],role=role,observed_rounds='|'.join(map(str,rounds)),eligible_rounds='|'.join(map(str,valid)),eligible_round_count=len(valid)))
            if per:mats[role][(src,q)]=np.mean(per,axis=0)
    summary={};cells=[];questiondata=[]
    for role,values in mats.items():
        if not values:raise ValueError(f'No complete question-round panel for {role}')
        items=sorted(values);arr=np.array([values[k] for k in items]);family_counts=Counter(families[k] for k in items)
        family_balanced=c.get('aggregation')=='equal_super_family'
        if family_balanced:assert set(family_counts)=={'life','physical_engineering','math_cs','social_humanities'}, 'All four families required'
        weights=np.array([1/(len(family_counts)*family_counts[families[k]]) if family_balanced else 1/len(items) for k in items])
        assert np.isclose(weights.sum(),1)
        point=np.einsum('i,ijk->jk',weights,arr)
        rng=np.random.default_rng(c['seed']);boot=np.zeros((c['bootstrap_resamples'],5,5))
        strata=sorted({(k[0],families[k]) for k in items}) if family_balanced else sorted({(k[0],None) for k in items})
        stratum_counts={}
        for src,family in strata:
            ids=[i for i,k in enumerate(items) if k[0]==src and (family is None or families[k]==family)];n=len(ids)
            counts=rng.multinomial(n,np.ones(n)/n,size=c['bootstrap_resamples'])
            boot+=np.einsum('bi,i,ijk->bjk',counts,weights[ids],arr[ids])
            stratum_counts[src+'|'+str(family)]=n
        lo,hi=np.quantile(boot,[.025,.975],axis=0)
        summary[role]={'estimate':point.tolist(),'ci_low':lo.tolist(),'ci_high':hi.tolist(),'questions':len(items),'source_counts':dict(Counter(k[0] for k in items)),'family_counts':dict(family_counts),'bootstrap_stratum_counts':stratum_counts,'question_weights':[{'source':k[0],'task_id':k[1],'family':families[k],'weight':float(w)} for k,w in zip(items,weights)]}
        for i,j in combinations(range(5),2):
            cells.append(dict(role=role,persona_i=c['arms'][i],persona_j=c['arms'][j],estimate=point[i,j],ci_low=lo[i,j],ci_high=hi[i,j],questions=len(items)))
        for k,m in zip(items,arr):
            for i,j in combinations(range(5),2):questiondata.append(dict(source=k[0],task_id=k[1],family=families[k],role=role,persona_i=c['arms'][i],persona_j=c['arms'][j],distance=float(m[i,j])))
    write_csv(OUT/'heatmap_cells.csv',cells);write_csv(OUT/'question_distances.csv',questiondata);write_csv(OUT/'round_distances.csv',rounddata);write_csv(OUT/'round_coverage.csv',coverage)
    return summary,mats

def choose_cases(records,z,mats,c):
    if c.get('manual_cases'):
        chosen=c['manual_cases'];keys={(r['source'],r['task_id']) for r in chosen}
        assert all(k in mats[role] for k in keys for role in c['roles'])
        coords=list(csv.DictReader((OUT/'selected_case_coordinates.csv').open()))
        def key(r):return (r['source'],r['task_id'],r['role'],r['arm'],int(r['trial']),int(r['round']),r['text_sha256'])
        expected={key(r) for r in records if (r['source'],r['task_id']) in keys}
        assert {key(r) for r in coords}==expected,'Frozen projection/message mismatch'
        write_json(OUT/'cases.json',chosen);write_csv(OUT/'trajectory_coordinates.csv',coords)
        return chosen

    # Use only cases with aggregate evidence in both roles and actual multi-round
    # displayed traces. Fixed index was declared before reading embeddings.
    common=set.intersection(*(set(v) for v in mats.values()));chosen=[]
    for src in c['case_source_priority']:
        candidates=[]
        for k in sorted(common):
            if k[0]!=src:continue
            if not all(sum(r['source']==k[0] and r['task_id']==k[1] and r['role']==role and r['arm']==a and r['trial']==c['display_rollout'] for r in records)>=2 for a in c['arms'] for role in c['roles']):continue
            val=float(np.mean([mats[role][k][np.triu_indices(5,1)].mean() for role in c['roles']]))
            candidates.append((k,val))
        if not candidates:continue
        median=float(np.median([v for _,v in candidates]));k,value=min(candidates,key=lambda kv:(abs(kv[1]-median),kv[0]))
        chosen.append({'source':k[0],'task_id':k[1],'separation':value,'source_candidate_median':median,'eligible_cases_in_source':len(candidates),'display_rollout':c['display_rollout']})
        if len(chosen)==2:break
    if len(chosen)!=2:raise ValueError('Fewer than two benchmarks have eligible multiround cases; do not silently change case rule.')
    coords=[];projection=[]
    for case in chosen:
        for role in c['roles']:
            ids=[i for i,r in enumerate(records) if r['source']==case['source'] and r['task_id']==case['task_id'] and r['role']==role]
            x=z[ids].astype(float);center=x.mean(axis=0);u,s,vt=np.linalg.svd(x-center,full_matrices=False);components=vt[:2]
            # Deterministic sign convention; this changes orientation only.
            for v in components:
                if v[np.argmax(np.abs(v))]<0:v*=-1
            xy=(x-center)@components.T;variance=s[:2]**2/np.sum(s**2)
            projection.append(case|{'role':role,'fit_messages':len(ids),'variance_ratio':variance.tolist(),'center':center.tolist(),'components':components.tolist()})
            for i,point in zip(ids,xy):
                r=records[i]
                coords.append({k:v for k,v in r.items() if k!='text'}|{'pc1':float(point[0]),'pc2':float(point[1]),'displayed':r['trial']==c['display_rollout']})
    write_json(OUT/'cases.json',chosen);write_json(OUT/'pca.json',projection);write_csv(OUT/'trajectory_coordinates.csv',coords)
    return chosen

def analyze():
    c=config();records=json.loads((CACHE/'messages.private.json').read_text());embedding=np.load(CACHE/'embeddings.npz',allow_pickle=False)
    hashes=np.array([r['text_sha256'] for r in records]);assert np.array_equal(embedding['hashes'],hashes),'Embedding/message index mismatch'
    keep=[i for i,r in enumerate(records) if r['arm'] in c['arms'] and r['trial'] in c['rollouts'][r['arm']]]
    records=[records[i] for i in keep];z=embedding['embeddings'][keep]
    selected=[r for r in csv.DictReader((OUT/'episode_coverage.csv').open()) if r['arm'] in c['arms'] and int(r['trial']) in c['rollouts'][r['arm']]]
    analysis_coverage=dict(message_count=len(records),episode_slots=len(selected),complete_episodes=sum(not r['exclusion'] for r in selected),exclusions=dict(Counter(r['exclusion'] for r in selected if r['exclusion'])))
    write_csv(OUT/'selected_message_index.csv',[{k:v for k,v in r.items() if k!='text'} for r in records])
    summary,mats=aggregate(records,z,c);cases=choose_cases(records,z,mats,c)
    write_json(OUT/'summary.json',{'config':c,'analysis_coverage':analysis_coverage,'roles':summary,'cases':cases,'embedding_provenance':json.loads((CACHE/'embedding_provenance.json').read_text())})
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('step',choices=['extract','analyze']);a=p.parse_args()
    extract() if a.step=='extract' else analyze()
