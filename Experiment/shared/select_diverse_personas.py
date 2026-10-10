#!/usr/bin/env python3
"""Exploratory five-setting selection from saved summaries; no model calls.

Maximize the minimum pairwise profile distance with off forced into each set.
This selects complementary estimated profiles; it is not an inferential test.
"""
from pathlib import Path
from itertools import combinations
import csv
import hashlib
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Experiment/01_behavioral_diversity/data/persona_selection'
BP=ROOT/'Experiment/01_behavioral_diversity/data/behavior_all_personas/summary.json'
PP=ROOT/'Experiment/02_performance_and_fields/data/all_available/summary.json'
B=json.loads(BP.read_text());P=json.loads(PP.read_text())
ARMS=B['arms']
BM=['simulator_chars','exchanges','extra_plan_reviews','revision_requests','clarification_recall','clarification_precision']
PS=['bixbench','discoverybench','expbench','sciconvbench']

def features(metrics=BM,sources=PS,language=False):
    behavior=np.array([[0 if i==0 else B['paired'][m]['all'][a]['mean']/B['absolute'][m]['all']['persona_off']['task_sd'] for m in metrics] for i,a in enumerate(ARMS)])
    if language:
        behavior=np.column_stack([behavior,[[0,0] if a=='persona_off' else [B['paired'][m]['all'][a]['mean']/100 for m in ['simulator_cjk_share','simulator_devanagari_share']] for a in ARMS]])
    performance=np.array([[0 if i==0 else P['paired']['available'][a]['source'][src]['mean']/P['absolute']['available']['persona_off']['source'][src]['task_sd'] for src in sources] for i,a in enumerate(ARMS)])
    return behavior,performance

def pool(threshold=20,repeated=False):
    return [0]+[i for i,a in enumerate(ARMS) if i and (not repeated or B['planned_trials'][a]==3) and all(P['paired']['available'][a]['source'][src]['tasks']>=threshold for src in PS)]

def rank(eligible,weight=.5,metrics=BM,sources=PS,language=False):
    matrices=features(metrics,sources,language)
    dist=[]
    for x in matrices:
        d=np.mean((x[:,None,:]-x[None,:,:])**2,axis=2)
        # Equal average squared distance per block before assigning weights.
        normalizer=np.mean([d[i,j] for i,j in combinations(eligible,2)])
        assert normalizer>0
        dist.append(d/normalizer)
    d=np.sqrt(weight*dist[0]+(1-weight)*dist[1]);results=[]
    for subset in combinations(eligible[1:],4):
        ds=[d[i,j] for i,j in combinations([0,*subset],2)]
        results.append(dict(personas=[ARMS[i] for i in subset],minimum_distance=float(min(ds)),mean_distance=float(np.mean(ds))))
    return sorted(results,key=lambda r:(-r['minimum_distance'],-r['mean_distance'],r['personas']))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    eligible=pool();primary=rank(eligible);sens={}
    for w in [.25,.5,.75]:
        sens[f'behavior_weight_{w}']=rank(eligible,weight=w)[0]
        sens[f'language_features_weight_{w}']=rank(eligible,weight=w,language=True)[0]
    for src in PS:sens['omit_source_'+src]=rank(eligible,sources=[s for s in PS if s!=src])[0]
    for m in BM:sens['omit_behavior_'+m]=rank(eligible,metrics=[s for s in BM if s!=m])[0]
    for n in [10,16,20,24,30]:sens[f'minimum_matched_tasks_{n}']=rank(pool(n))[0]
    sens['include_sparse_003']=rank(pool(0))[0]
    sens['include_ASI']=rank(eligible,sources=['asibench',*PS])[0]
    sens['three_trial_settings_only']=rank(pool(repeated=True))[0]
    mean_best=max(primary,key=lambda r:r['mean_distance'])
    result={'method':'maximin estimated profile separation, off fixed; mean distance breaks ties','eligible_personas':[ARMS[i] for i in eligible[1:]],'recommended':primary[0],'behavior_metrics':BM,'performance_sources':PS,'minimum_matched_tasks_per_performance_source':20,'behavior_weight':.5,'subsets_compared':len(primary),'all_eight_candidate_subsets':len(rank(pool(0))),'sensitivity':sens,'mean_distance_alternative':mean_best,'files_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BP,PP]}}
    (OUT/'selection.json').write_text(json.dumps(result,indent=2)+'\n')
    with (OUT/'ranked_subsets.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['rank','personas','minimum_distance','mean_distance']);wr.writeheader()
        for i,r in enumerate(primary,1):wr.writerow(dict(rank=i,**(r|{'personas':'|'.join(r['personas'])})))
    lines=['# Exploratory choice of four personas plus off','',
      '**Recommendation for a reduced future campaign: off + '+', '.join(a.removeprefix('candidate_') for a in primary[0]['personas'])+'.** This is a coverage-constrained descriptive selection from observed summaries, not proof of a uniquely most diverse population subset. No settings or jobs were changed.','',
      '## Data and experimental unit','',
      'Eight candidates have at least one completed Astra trial job. 148/155/089/001/127 have three trials; 003/004/046 have one. Behavior uses original complete traces; performance uses the available repaired endpoint within each trial and evaluator-compatible matching. These policies differ and the resulting feature blocks do not describe identical episode sets. Repeats average within task; uncertainty in the input summaries resamples studies within benchmark. Trials, metrics and persona pairs are not independent experimental units.','',
      '## Transparent selection rule','',
      '1. Force persona-off into every five-setting set. Exhaustively evaluate all four-persona combinations.','2. Performance features are paired changes on Bix, Discovery, EXP and SciConv. Exclude ASI from the primary selection because the new personas have only 2–5 matched cases under a compatible judge. Require at least 20 of the planned 40 distinct matched tasks on each remaining benchmark: 003 fails with six EXP cases. This is an analyst-chosen half-coverage guard, not a power calculation or preregistered rule. Threshold sensitivities from 10 to 30 are saved.','3. Behavior features are the six existing heatmap metrics: reply characters, exchanges, extra approach reviews, revision requests, clarification recall and precision. Use their existing equal-benchmark means. Features are correlated; equal feature weighting is a stated design choice. Do not duplicate benchmark performance by also adding super-family summaries of the same outcomes.','4. Divide each feature by a fixed persona-off task-level SD. Within each block, compute mean squared feature differences and normalize to unit average pairwise squared distance over eligible profiles including off. Combine behavior and performance with 50:50 weights, then take square roots. Off has a zero paired-effect vector.','5. Maximize the smallest of the ten pairwise distances among the five selected settings. This avoids spending slots on nearly overlapping profiles. Mean pairwise distance breaks ties. This objective describes separation of estimated mean profiles, not within-persona dispersion, semantic diversity or a validated latent trait.','',
      f"The primary search compared {len(primary)} eligible subsets; the unrestricted search compared 70. With the baseline required, 148 can be partially redundant despite its clearly longer replies. The maximin rule deliberately values complementarity, rather than selecting the largest four individual changes from off.",'',
      '## Sensitivity results','', '| Change | Winning four personas |','|---|---|']
    for k,r in sens.items():lines.append('| '+k+' | '+', '.join(a.removeprefix('candidate_') for a in r['personas'])+' |')
    lines+=['', 'Maximizing mean distance instead of minimum distance selects '+', '.join(a.removeprefix('candidate_') for a in mean_best['personas'])+'. Thus “biggest diversity” depends on the stated objective. Weight and leave-one-feature checks are deterministic sensitivity analyses, not bootstrap selection probabilities.','',
      '## Selected profiles: observed changes','', '| Persona | Trials | Reply characters: Δ [95% CI] | SciConv performance: Δ pp [95% CI] |','|---|---:|---|---|']
    for a in primary[0]['personas']:
        c=B['paired']['simulator_chars']['all'][a];v=P['paired']['available'][a]['source']['sciconvbench']
        lines.append(f"| {a.removeprefix('candidate_')} | {B['planned_trials'][a]} | {c['mean']:+.1f} [{c['ci95'][0]:.1f}, {c['ci95'][1]:.1f}] | {v['mean']:+.1f} [{v['ci95'][0]:.1f}, {v['ci95'][1]:.1f}] |")
    lines+=['','All intervals above are pointwise, conditional on observed trials and based on studies/tasks, not a comparison of four independent persona populations. Character differences are language-dependent. 004’s revision-request change is −0.113 [−0.307, 0.018], so its apparent interaction difference is not established separately. 046’s SciConv change is −7.5 [−20.0, 5.0] pp; the negative estimate is not evidence of a confirmed decrease. Its Discovery estimate is +6.76 [2.43, 12.64] pp over 39 matched tasks clustered in studies. Full cell denominators remain in the source summaries.','',
      '## Statistical reporting boundary','',
      'The selection uses observed outcomes and analyst-chosen scaling, endpoints and weighting; it is exploratory and post hoc. Input pointwise CIs are not selection-adjusted. Subtracting different persona-minus-off summaries is a descriptive profile distance on differing observed task panels, not a direct matched pairwise treatment-effect estimate. Missingness, conditional repair and single-trial noise can change rankings. No p values or claims of statistical distinguishability are attached to the selection. A further common-task-panel analysis and joint study bootstrap of the entire selection pipeline would be needed to estimate selection stability.','',
      'For a future experiment, freeze this subset and rule before collecting fresh comparable trials, and complete trials 2–3 for 004/046 if repeat variation is part of the claim. Independent tasks/studies are needed to assess selection generalization; additional runs on the same tasks measure stochastic repeatability only. Keep the all-persona exploratory table in the paper/supplement so the selection is visible. Human realism and semantic collapse are not inferred.','',
      'Reproduce: `.venv/bin/python Experiment/shared/select_diverse_personas.py`. [Selection JSON](data/persona_selection/selection.json) · [All eligible subsets](data/persona_selection/ranked_subsets.csv).','']
    (ROOT/'Experiment/01_behavioral_diversity/PERSONA_SELECTION.md').write_text('\n'.join(lines))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
