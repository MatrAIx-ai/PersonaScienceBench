#!/usr/bin/env python3
"""Matched three-trial performance and coverage from the frozen result snapshot."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Experiment/shared'))
from analysis_utils import (ARMS,SOURCES,FAMILIES,NAMES,B,SEED,label,sha,write_json,
                            write_csv,selection,summarize,paired,cell,markdown_table)
BASE=ROOT/'Experiment/02_performance_and_fields'
DATA=BASE/'data/consolidated'
BRIDGE='asi-b3-collaborative-b2-v1+asi-configured-judge-v1'

def compatible(r,b,exclude_asi=False):
    if r['source']=='asibench':
        return not exclude_asi and r.get('evaluator_version')==BRIDGE and b.get('evaluator_version')==BRIDGE
    # Missing submissions have no evaluation; the zero is scientific noncompletion.
    if r['status']=='missing_submission' or b['status']=='missing_submission':
        return True
    return r.get('evaluator_version')==b.get('evaluator_version')

# These are metadata overlap rules, not inferred competence or a human annotation.
TOPICS={
    'genomics':['Genetics','Molecular biology'], 'transcriptomics':['Molecular biology','Genetics'],
    'rna-seq':['Molecular biology','Genetics'], 'epigenomics':['Genetics','Molecular biology'],
    'proteomics':['Biochemistry','Molecular biology'], 'differential expression':['Molecular biology','Genetics'],
    'biology':['Molecular biology','Genetics','Ecology','Marine biology'],
    'chemistry':['Organic chemistry','Physical chemistry','Biochemistry'],
    'astronomy':['Astronomy','Astrophysics'], 'earth_science':['Geology','Climate science'],
    'robotics':['Robotics'], 'electrical_engineering':['Electrical engineering'],
    'materials':['Materials science'], 'matsci':['Materials science'],
    'sociology':['Sociology'], 'economics':['Macroeconomics','Microeconomics'],
    'machine learning':['Machine learning'], 'deep learning':['Machine learning'],
    'language model':['Natural language processing','Machine learning'],
    'llm':['Natural language processing','Machine learning'],
    'computer_science':['Databases','Distributed systems','Operating systems','Compilers'],
    'engineering':['Structural engineering','Electrical engineering','Chemical engineering'],
    'humanities':['History','Comparative literature','Linguistics','Art history'],
}
SPECIFIC={'genomics','transcriptomics','rna-seq','epigenomics','proteomics','differential expression',
          'astronomy','robotics','electrical_engineering','materials','matsci','sociology','economics',
          'machine learning','deep learning','language model','llm'}
LEVEL={'Aware':0,'Familiar':1,'Proficient':2,'Expert':3}

def expertise_audit():
    profiles,records,provenance={},[],[]
    for arm in ARMS[1:]:
        p=ROOT/'data/persona_case_study/full_persona_v2/prompts'/f'{arm}.md'
        raw=p.read_bytes();text=raw.decode()
        familiarity=dict(re.findall(r'^- Familiarity: (.+): (Aware|Familiar|Proficient|Expert)\s*$',text,re.M))
        skills=dict(re.findall(r'^- Skill: (.+): (.+)\s*$',text,re.M))
        fields={k:(re.search(r'^- '+re.escape(k)+r': (.+)$',text,re.M).group(1) if re.search(r'^- '+re.escape(k)+r': (.+)$',text,re.M) else None) for k in ['Domain','Academic field','Primary language']}
        profiles[arm]=dict(familiarity=familiarity,skills=skills,**fields)
        provenance.append({'arm':arm,'path':str(p.relative_to(ROOT)),'sha256':sha(raw)})
        records.append(dict(arm=arm,domain=fields['Domain'],academic_field=fields['Academic field'],language=fields['Primary language'],statistics=familiarity.get('Statistics','not stated'),coding=skills.get('Coding','not stated'),data_analysis=skills.get('Data analysis','not stated'),statistical_modeling=skills.get('Statistical modeling','not stated')))
    relationships=[]
    for task in selection():
        text=(task['subfield']+' '+task['task_id']).lower()
        matches=[k for k in TOPICS if k in text]
        for arm in ARMS[1:]:
            familiar=profiles[arm]['familiarity']
            evidence=sorted({(key,term,familiar[term]) for key in matches for term in TOPICS[key] if term in familiar})
            direct=[e for e in evidence if e[0] in SPECIFIC and LEVEL[e[2]]>=1]
            adjacent=[e for e in evidence if LEVEL[e[2]]>=0]
            # Unmapped or broad fields cannot support a confident negative inference.
            relation='direct' if direct else 'adjacent' if adjacent else 'outside' if matches and any(k in SPECIFIC for k in matches) else 'unknown'
            support=direct if direct else adjacent
            relationships.append({**task,'arm':arm,'relationship':relation,
                'evidence':'; '.join(f'{key} -> {term}: {level}' for key,term,level in support),
                'definition':'explicit-topic familiarity' if direct else 'broader-topic or awareness overlap' if adjacent else 'outside the explicit familiarity list' if relation=='outside' else 'insufficient metadata',
                'annotation':'automatic conservative metadata overlap; not validated expertise'})
    write_csv(DATA/'persona_expertise.csv',records)
    write_csv(DATA/'task_field_relationships.csv',relationships)
    return profiles,relationships,provenance

def analyze():
    path=BASE/'data/three_trials/snapshot.json';raw=path.read_bytes();snapshot=json.loads(raw)
    rows=snapshot['episodes']
    assert len(rows)==7200 and len({(r['view'],r['trial'],r['source'],r['task_id'],r['arm']) for r in rows})==7200
    for r in rows:
        assert r['score'] is None or 0<=r['score']<=100
        if r['status']=='missing_submission':assert r['score']==0
        r['submitted']=100. if r['status']=='scored' else 0. if r['status']=='missing_submission' else None
        r['score_when_submitted']=r['score'] if r['status']=='scored' else None
    profiles,relationships,profile_provenance=expertise_audit()
    relationship={(r['source'],r['task_id'],r['arm']):r['relationship'] for r in relationships}
    summary={'resamples':B,'seed':SEED,'snapshot_sha256':sha(raw),'source_provenance':snapshot['provenance'],
             'profile_provenance':profile_provenance,'asi_policy':'configured judge bridge on both matched episodes; legacy and unknown versions excluded from contrasts',
             'absolute':{},'paired':{},'coverage':{},'expertise':{},'common_panel':{},'run_variation':{}}
    pair_records,flat=[],[]
    for view in ['original','after_repair']:
        rr=[r for r in rows if r['view']==view]
        summary['absolute'][view]={};summary['coverage'][view]={};summary['paired'][view]={};summary['expertise'][view]={};summary['run_variation'][view]={}
        for arm in ARMS:
            aa=[r for r in rr if r['arm']==arm]
            counts=Counter(r['status'] for r in aa)
            summary['coverage'][view][arm]=dict(counts)
            summary['absolute'][view][arm]={}
            repeat_groups=defaultdict(list)
            for r in aa:
                if r['score'] is not None and (r['source']!='asibench' or r.get('evaluator_version')==BRIDGE):
                    repeat_groups[(r['source'],r['task_id'])].append(r)
            sd_rows=[dict(records[0],value=float(np.std([r['score'] for r in records],ddof=1)),observed_trials=len(records)) for records in repeat_groups.values() if len(records)>=2]
            summary['run_variation'][view][arm]={}
            for src in SOURCES:
                subset=[r for r in sd_rows if r['source']==src]
                stat=summarize(subset)
                stat['task_statistics']=stat.pop('episodes')
                stat['observed_trial_episodes']=sum(r['observed_trials'] for r in subset)
                summary['run_variation'][view][arm][src]=stat
            for field,groups in [('source',SOURCES),('family',FAMILIES)]:
                summary['absolute'][view][arm][field]={g:{m:summarize([r for r in aa if r[field]==g],m) for m in ['score','submitted','score_when_submitted']} for g in groups}
            if arm==ARMS[0]:continue
            pairs=paired(rr,'score',arm,compatible)
            pair_records.extend({k:r[k] for k in ['view','trial','source','task_id','study_id','family','arm','value','baseline','persona_value','evaluator_version']} for r in pairs)
            summary['paired'][view][arm]={}
            for field,groups in [('source',SOURCES),('family',FAMILIES)]:
                summary['paired'][view][arm][field]={}
                for g in groups:
                    pp=[r for r in pairs if r[field]==g]
                    stats=summarize(pp)
                    stats['without_asi']=summarize([r for r in pp if r['source']!='asibench'])
                    summary['paired'][view][arm][field][g]=stats
                    flat.append(dict(view=view,arm=arm,level=field,group=g,mean=stats['mean'],ci_low=stats['ci95'][0] if stats['ci95'] else None,ci_high=stats['ci95'][1] if stats['ci95'] else None,tasks=stats['tasks'],pairs=stats['episodes']))
            # Source-stratified relationship summaries avoid a pooled expertise story.
            summary['expertise'][view][arm]={src:{rel:summarize([r for r in pairs if r['source']==src and relationship[(r['source'],r['task_id'],arm)]==rel]) for rel in ['direct','adjacent','outside','unknown']} for src in SOURCES}
        index={(r['source'],r['task_id'],r['arm'],r['trial']):r for r in rr}
        common=[]
        for task in selection():
            panel=[index[(task['source'],task['task_id'],a,t)] for a in ARMS for t in [1,2,3]]
            if all(r['score'] is not None for r in panel) and all(compatible(index[(task['source'],task['task_id'],a,t)],index[(task['source'],task['task_id'],ARMS[0],t)]) for a in ARMS[1:] for t in [1,2,3]):
                common.append((task['source'],task['task_id']))
        summary['common_panel'][view]={'tasks':len(common),'source_counts':dict(Counter(s for s,t in common)),
            'paired_by_source':{a:{s:summarize([p for p in pair_records if p['view']==view and p['arm']==a and p['source']==s and (p['source'],p['task_id']) in common]) for s in SOURCES} for a in ARMS[1:]}}
    write_json(DATA/'summary.json',summary)
    write_csv(DATA/'matched_episode_differences.csv',pair_records)
    write_csv(DATA/'paired_summary.csv',flat)
    write_json(DATA/'analysis_contract.json',{
        'primary_contrasts':'Original same-task/same-trial pairs; ASI bridge-only; other native versions matched except scientific missing submissions.',
        'legacy_absolute_tables':'Latest after-repair available-task means retained in their original structure; descriptive mixed-version ASI values labeled.',
        'sensitivities':['after_repair','all-six-settings/all-three-trials complete panel','super-family excluding ASI'],
        'ci':'20,000 study-cluster draws within source, observed source weights fixed; conditional on observed trials; pointwise intervals, no significance search',
        'expertise':'Automatic metadata overlap with explicit evidence, separate methodological skills; exploratory, not a validated competence annotation.',
        'source_snapshot':str(path.relative_to(ROOT)),'source_sha256':sha(raw)})
    return summary

def report(s):
    def complete_cell(v):
        if v['mean'] is not None and v['studies'] < 2:
            return f"{v['mean']:+.2f}; CI unavailable; n={v['tasks']}, e={v['episodes']}"
        return cell(v, True)
    lines=['# Experiment 02 — Consolidated performance and field analysis','',
           '[Executed notebook](performance_analysis.ipynb) · [Earlier descriptive report](three_trial_persona_results.md)','',
           'Six settings (off/148/155/089/001/127), 200 frozen tasks, three Astra trials. This report preserves the existing benchmark and super-family table structures, and adds same-task/same-trial contrasts, version filtering, completion, conditional scores, and coverage sensitivities. No new inference or regrading.','',
           '## Principal observations','',
           '- The 108 original/after-repair absolute-score means and task/episode denominators reproduce the earlier report. Intervals are recomputed with this analysis\'s fixed bootstrap seed; small Monte Carlo endpoint differences are expected.',
           '- Most original benchmark-level paired intervals include zero. The tables retain all directions and magnitudes rather than selecting a winning persona. ASI bridge-only coverage is smaller than the descriptive ASI panel.',
           f"- The strict all-six-settings/all-three-trials panel contains {s['common_panel']['original']['tasks']} original tasks and {s['common_panel']['after_repair']['tasks']} after-repair tasks. Original ASI has no task satisfying that full bridge-only panel. Results on incomplete pairwise panels should not be presented as a common-panel ranking.",
           '- Several Bix paired intervals are exactly [0,0] because every observed matched difference is zero. This describes the observed panel; it is not an equivalence test or a guarantee about new tasks.',
           '- Super-family patterns are descriptive mixtures of different benchmark metrics. Automatic field-overlap annotations document explicit profile/task relationships but do not establish an expertise-match mechanism.','',
           '## How to read the evidence','',
           'The first two tables retain latest-after-repair available-case means for continuity. They are descriptive: ASI mixes legacy and corrected evaluator configurations, and conditions have unequal surviving coverage. Original matched contrasts below are the primary persona comparisons. ASI contrasts require the configured-judge bridge on both episodes; all legacy/unknown ASI pairs are excluded. Other native evaluator versions must match except for missing submissions, whose scientific zero does not require grading.','',
           'Scientific missing submissions score zero. Infrastructure failures are missing, not zero. “Submitted” means a scored deliverable exists, including incorrect scored answers; for EXP the native initial-design fallback is retained. Conditional scores use only scored submissions. The submitted/planned fraction includes infrastructure failures in the planned denominator and therefore measures operational coverage, not isolated scientific ability.','',
           'Means average available trials within task, then tasks equally. Paired changes match task and trial before averaging within task. Pointwise 95% CIs use 20,000 source-stratified study-cluster bootstrap draws with observed source weights fixed. They condition on observed trials and do not separately quantify trial randomness. Different pairwise panels can differ in coverage; no winner or significance claim follows from CI overlap or individual intervals.','']
    for field,groups,title in [('source',SOURCES,'Table 1 — By benchmark'),('family',FAMILIES,'Table 2 — By super-family')]:
        lines+=['## '+title,'',markdown_table(['Persona',*[NAMES[g]+('*' if g=='asibench' else '') for g in groups]],
                    [[label(a),*[cell(s['absolute']['after_repair'][a][field][g]['score']) for g in groups]] for a in ARMS]),'']
    lines+=['*ASI absolute means remain mixed-version descriptive values. Super-families combine distinct native metrics and their source composition, rather than measuring a pure field effect. The existing annotated [benchmark bars](figures/three_trials/benchmark.png) and [super-family bars](figures/three_trials/superfamily.png) remain unchanged.','',
            'Sparse-stratum limitation: some source-by-family cells contain only one study. Resampling that study cannot estimate its between-study uncertainty, so the combined interval holds that component fixed and can be very narrow or degenerate. These intervals are conditional descriptive ranges, not evidence of precise population field effects. Study counts by source are recorded in the numeric summary. A source-only result with one study has no estimable study-level CI; the complete-panel table marks it unavailable.','',
            '## Task- and trial-matched original contrasts','', '![Matched performance changes](figures/consolidated/matched_performance.png)','',
            'The original six-setting Figure 4 heatmap is preserved. The expanded [all-available-persona report](ALL_AVAILABLE_PERFORMANCE.md) and performance notebook now include every persona with at least one completed trial job.','']
    for view in ['original','after_repair']:
        lines+=['### '+view.replace('_',' ').title(),'']
        for field,groups in [('source',SOURCES),('family',FAMILIES)]:
            lines += [markdown_table(['Persona Δ vs off',*[NAMES[g] for g in groups]],[[label(a),*[cell(s['paired'][view][a][field][g],True) for g in groups]] for a in ARMS[1:]]),'']
    lines+=['## Coverage and conditional outcomes','']
    for view in ['original','after_repair']:
        lines+=['### '+view.replace('_',' ').title(),'',markdown_table(['Persona','Scored / 600','Missing submission','Infrastructure / other','Submitted / planned (%)'],
            [[label(a),s['coverage'][view][a].get('scored',0),s['coverage'][view][a].get('missing_submission',0),600-s['coverage'][view][a].get('scored',0)-s['coverage'][view][a].get('missing_submission',0),f"{100*s['coverage'][view][a].get('scored',0)/600:.1f}"] for a in ARMS]),'']
    for metric,title in [('submitted','Submission among evaluable attempts (%)'),('score_when_submitted','Score conditional on submission')]:
        lines+=['### '+title+' — original trials','',markdown_table(['Persona',*[NAMES[g] for g in SOURCES]],[[label(a),*[cell(s['absolute']['original'][a]['source'][g][metric]) for g in SOURCES]] for a in ARMS]),'']
    lines+=['## Observed run-to-run score variation','',
            'For each task with at least two evaluable trials, compute its sample standard deviation, then average those task SDs. CIs resample studies, not the two or three runs. ASI uses corrected-bridge episodes only. This separately describes observed run variation; it is not the uncertainty represented by the score-mean CIs. Tasks with only one valid run are excluded rather than assigned zero SD.','',
            markdown_table(['Persona: mean within-task SD',*[NAMES[g] for g in SOURCES]],[[label(a),*[cell(s['run_variation']['original'][a][g],counts=False)+f"; n={s['run_variation']['original'][a][g]['tasks']}" for g in SOURCES]] for a in ARMS]),'',
            '## Shared complete-panel sensitivity','',
            'Require all six settings and all three trials to be evaluable, plus the same evaluator-version rule. This is stricter than pairwise matching and can remove difficult or failure-prone tasks. It is a sensitivity, not a replacement target population.','']
    for view,c in s['common_panel'].items():
        lines += [f"**{view}: {c['tasks']} tasks**, source counts {c['source_counts']}.",'',markdown_table(['Persona Δ vs off',*[NAMES[g] for g in SOURCES]],[[label(a),*[complete_cell(c['paired_by_source'][a][g]) for g in SOURCES]] for a in ARMS[1:]]),'']
    lines+=['## Super-family sensitivity without ASI','',markdown_table(['Persona Δ vs off',*[NAMES[g] for g in FAMILIES]],[[label(a),*[cell(s['paired']['original'][a]['family'][g]['without_asi'],True) for g in FAMILIES]] for a in ARMS[1:]]),'',
            '## Documented field overlap and methods familiarity','',
            'An exploratory metadata audit maps each persona/task to direct, adjacent, outside, or unknown overlap. Direct requires an explicit specific-topic familiarity at Familiar/Proficient/Expert; adjacent includes broader-topic matches or Aware-level knowledge; outside means no overlap in the explicit familiarity list for a mapped specific topic; unknown covers unmapped/coarse metadata. These labels do not establish actual expertise, absence of knowledge, or a causal expertise-match effect. Broad or incomplete task labels limit this analysis. Statistics/coding/data-analysis skills are recorded separately and do not automatically convert a domain mismatch into a direct match.','',
            '[Persona methods/background audit](data/consolidated/persona_expertise.csv) · [All 1,000 task–persona relationships and evidence](data/consolidated/task_field_relationships.csv)','',
            'Source-specific effect summaries for each relationship category are included in the JSON and notebook. Do not pool them into an expertise benefit claim: persona selection, coarse metadata, source/field confounding and sparse study clusters remain. Neutral wording and isolated-trait controls were not run.','',
            '## Reproduction and scope','',
            '[Numeric summary](data/consolidated/summary.json) · [Matched episode differences](data/consolidated/matched_episode_differences.csv) · [Paired tables](data/consolidated/paired_summary.csv) · [Analysis contract](data/consolidated/analysis_contract.json)','',
            'Reproduce: `.venv/bin/python Experiment/02_performance_and_fields/code/consolidate_performance.py`; render with `code/plot_matched_performance.py`. The original frozen snapshot is hashed and unchanged. Single-trial 003/004/046 remain in their separate exploratory report. Sol, new-protocol SciConv and semantic trajectories are outside this report.','']
    (BASE/'PERFORMANCE_REPORT.md').write_text('\n'.join(lines))

if __name__=='__main__':
    summary=analyze();report(summary)
    print(json.dumps({'common_panel':{v:{k:c[k] for k in ['tasks','source_counts']} for v,c in summary['common_panel'].items()},'original_differences':{a:{g:summary['paired']['original'][a]['source'][g]['mean'] for g in SOURCES} for a in ARMS[1:]}},indent=2))
