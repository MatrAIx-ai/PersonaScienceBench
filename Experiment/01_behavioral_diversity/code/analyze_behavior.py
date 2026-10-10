#!/usr/bin/env python3
"""Experiment 01: offline behavior and lexical repetition, without embeddings."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations, product
import json
from pathlib import Path
import re
import sys
import unicodedata
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Experiment/shared'))
from analysis_utils import (ARMS, SOURCES, NAMES, B, SEED, label, sha, write_json,
                            write_csv, native, safe_component, original_work,
                            selection, summarize, paired, cell, markdown_table)
BASE = ROOT / 'Experiment/01_behavioral_diversity'
DATA = BASE / 'data/behavior'
REVIEW = SOURCES[:-1]
# Units and applicability are explicit; an inapplicable metric is never zero.
METRICS = {
    'simulator_chars': ('Simulator characters/reply', SOURCES),
    'actor_chars': ('Actor characters/handoff or question', SOURCES),
    'exchanges': ('Completed handoffs or clarification replies', SOURCES),
    'extra_plan_reviews': ('Additional approach reviews', REVIEW),
    'extra_result_reviews': ('Additional result reviews', REVIEW),
    'revision_requests': ('Result-review requests to continue', REVIEW),
    'request_budget_exhausted': ('Researcher budget reached (%)', REVIEW),
    'actor_budget_exhausted': ('Actor call budget reached (%)', REVIEW),
    'script_match': ('Actor/simulator dominant-script agreement (%)', SOURCES),
    'simulator_cjk_share': ('Simulator CJK letters (%)', SOURCES),
    'simulator_devanagari_share': ('Simulator Devanagari letters (%)', SOURCES),
    'repeat_question_rate': ('Exact repeated SciConv questions (%)', ['sciconvbench']),
    'post_reply_questions': ('SciConv questions after first simulator reply', ['sciconvbench']),
    'question_cap_hit': ('Ten-reply limit reached (%)', ['sciconvbench']),
    'clarification_recall': ('Clarification recall (%)', ['sciconvbench']),
    'clarification_precision': ('Clarification precision (%)', ['sciconvbench']),
    'CGRR': ('Conversation-grounded resolution (%)', ['sciconvbench']),
    'SRR': ('Silent resolution (%)', ['sciconvbench']),
    'memory_consistency': ('Memory consistency (%)', ['sciconvbench']),
    'intent_capture': ('Intent capture (%)', ['sciconvbench']),
    'opening_repeat_rate': ('Repeated reply openings within episode (%)', SOURCES),
}
HEAT_METRICS = ['simulator_chars', 'exchanges', 'extra_plan_reviews', 'revision_requests',
                'clarification_recall', 'clarification_precision']
REPEAT_METRICS = ['simulator_chars', 'extra_plan_reviews', 'revision_requests', 'post_reply_questions']

def prose(text):
    return re.sub(r'```.*?```', '', text or '', flags=re.S)

def normalized(text):
    text = unicodedata.normalize('NFKC', prose(text)).casefold()
    return ''.join(c for c in text if c.isalnum())

def script_features(text):
    letters = [c for c in prose(text) if c.isalpha()]
    counts = Counter()
    for c in letters:
        name = unicodedata.name(c, '')
        kind = 'CJK' if 'CJK' in name or 'HIRAGANA' in name or 'KATAKANA' in name else 'Devanagari' if 'DEVANAGARI' in name else 'Latin' if 'LATIN' in name else 'Other'
        counts[kind] += 1
    if not letters:
        return {'script': None, 'cjk': None, 'devanagari': None}
    most, n = counts.most_common(1)[0]
    return {'script': most if len(letters) >= 20 and n / len(letters) >= .6 else None,
            'cjk': 100 * counts['CJK'] / len(letters),
            'devanagari': 100 * counts['Devanagari'] / len(letters)}

def event_path(source_run, row, n):
    if n.get('case_directory'):
        case = Path(n['case_directory'])
        return next((p for p in [case/'controller/events.jsonl', case/'events.jsonl'] if p.exists()), None)
    if row['source'] == 'expbench':
        output = Path(source_run)/'episodes'/safe_component(row['source']+':'+row['task_id'])/row['arm']/f"attempt-{row['attempt']}"/'output'
        candidates = list(output.glob('*/events.jsonl'))
        assert len(candidates) <= 1, (str(output), len(candidates))
        return candidates[0] if candidates else None
    return None

def extract(work):
    trial, source_run, row = work
    n = native(row)
    meta = dict(trial=trial, source=row['source'], task_id=row['task_id'], arm=row['arm'],
                family=row['family'], study_id=row.get('study_id') or row['task_id'],
                coordinator_status=row['status'], native_status=n.get('status'), attempt=row.get('attempt'))
    meta.update({m: None for m in METRICS})
    meta.update(trace_available=False, eligible=False, first_reply_opening_hash=None,
                first_reply_script=None, optional_pattern_hash=None)
    p = event_path(source_run, row, n)
    if p is None:
        meta['trace_issue'] = 'no_saved_event_log'
        return meta, None
    raw = p.read_bytes()
    events = [json.loads(l) for l in raw.splitlines() if l.strip()]
    meta['trace_available'] = True
    meta['event_count'] = len(events)
    meta['eligible'] = row['status'] == 'finished'
    meta['trace_issue'] = None if meta['eligible'] else 'incomplete_episode_excluded'
    provenance = dict(trial=trial, source=row['source'], task_id=row['task_id'], arm=row['arm'],
                      path=str(p.resolve().relative_to(ROOT)), sha256=sha(raw))
    if not meta['eligible']:
        return meta, provenance
    sci = row['source'] == 'sciconvbench'
    sim, actor, script_pairs, questions = [], [], [], []
    previous_sim = None
    decisions = []
    for e in events:
        kind, payload = e['type'], e.get('payload') or {}
        if kind == 'researcher_decision':
            decisions.append(payload)
        if (sci and kind == 'researcher_reply') or (not sci and kind == 'researcher_decision' and payload.get('phase') != 'initial_inspection' and payload.get('interaction') != 'initial_request'):
            message = payload.get('answer' if sci else 'message', '')
            sim.append(message)
            previous_sim = script_features(message)['script']
        if (sci and kind == 'researcher_question') or (not sci and kind == 'agent_handoff'):
            message = payload.get('question' if sci else 'answer', '')
            actor.append(message)
            if sci:
                questions.append(message)
            script = script_features(message)['script']
            if previous_sim is not None and script is not None:
                script_pairs.append(script == previous_sim)
    meta.update(simulator_replies=len(sim), actor_handoffs_or_questions=len(actor),
                simulator_chars=float(np.mean([len(x) for x in sim])) if sim else None,
                actor_chars=float(np.mean([len(x) for x in actor])) if actor else None,
                exchanges=len(sim) if sci else sum(e['type'] == 'agent_handoff' for e in events),
                script_match=100 * float(np.mean(script_pairs)) if script_pairs else None,
                script_match_pairs=len(script_pairs))
    features = [script_features(x) for x in sim]
    for key, dest in [('cjk', 'simulator_cjk_share'), ('devanagari', 'simulator_devanagari_share')]:
        vals = [f[key] for f in features if f[key] is not None]
        meta[dest] = float(np.mean(vals)) if vals else None
    prefixes = [normalized(x)[:40] for x in sim if len(normalized(x)) >= 40]
    meta['opening_eligible_replies'] = len(prefixes)
    if len(prefixes) >= 2:
        meta['opening_repeat_rate'] = 100 * (len(prefixes) - len(set(prefixes))) / len(prefixes)
    if sim and len(normalized(sim[0])) >= 40:
        meta['first_reply_opening_hash'] = sha(normalized(sim[0])[:40].encode())
        meta['first_reply_script'] = features[0]['script']
    if sci:
        norm_questions = [normalized(q) for q in questions]
        meta.update(post_reply_questions=max(len(questions)-1, 0),
                    question_cap_hit=100 * int(len(sim) >= 10),
                    repeat_question_rate=100 * (len(norm_questions)-len(set(norm_questions)))/len(norm_questions) if len(norm_questions) >= 2 else None)
        metrics = (n.get('evaluation') or {}).get('metrics') or {}
        invalid = []
        for key in ['clarification_recall', 'clarification_precision', 'CGRR', 'SRR', 'memory_consistency', 'intent_capture']:
            value = metrics.get(key)
            if isinstance(value, (int, float)) and np.isfinite(value) and 0 <= value <= 1:
                meta[key] = 100 * value
            elif value is not None:
                invalid.append(key)
        meta['invalid_native_metrics'] = ','.join(invalid)
        if metrics.get('FRR') is not None:
            assert metrics['FRR'] == metrics.get('CGRR', 0) + metrics.get('SRR', 0)
    else:
        plans = [d for d in decisions if d.get('phase') == 'approach_review']
        results = [d for d in decisions if d.get('phase') == 'result_review']
        collab = (n.get('actor') or {}).get('collaboration') or {}
        termination = n.get('collaboration_termination') or collab.get('termination')
        reasons = [e['payload'].get('reason') for e in events if e['type'] == 'collaboration_budget_exhausted']
        meta.update(plan_reviews=len(plans), result_reviews=len(results),
                    extra_plan_reviews=max(len(plans)-1, 0), extra_result_reviews=max(len(results)-1, 0),
                    revision_requests=sum(d.get('action') == 'continue' for d in results),
                    request_budget_exhausted=100 * int(termination == 'researcher_request_limit' or 'researcher_request_limit' in reasons),
                    actor_budget_exhausted=100 * int(termination == 'actor_call_limit' or 'actor_call_limit' in reasons),
                    termination=termination)
        optional = [(d.get('phase'), d.get('action'), d.get('interaction')) for d in plans[1:]+results[1:]]
        meta['optional_pattern_hash'] = sha(json.dumps(optional).encode()) if optional else None
        for metric, value in [('plan_reviews', len(plans)), ('result_reviews', len(results))]:
            expected = n.get(metric, collab.get(metric))
            assert expected is None or expected == value, (row['task_id'], metric, expected, value)
    return meta, provenance

def collect():
    work, provenance = original_work()
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(extract, work))
    rows = [r[0] for r in results]
    snap = {'source_results': provenance, 'selection_sha256': sha((ROOT/'Experiment/shared/task_selection.csv').read_bytes()),
            'episodes': rows, 'event_logs': [r[1] for r in results if r[1]],
            'method': 'Original trials; complete coordinator episodes only; numeric and hashed derived data, no transcript text.'}
    write_json(DATA/'snapshot.json', snap)
    return snap

def repeat_analysis(rows):
    def task_stat(data,field):
        stat=summarize(data,field,balanced=True)
        stat['task_statistics']=stat.pop('episodes')
        return stat
    by = defaultdict(dict)
    for r in rows:
        by[(r['source'], r['task_id'])][(r['arm'], r['trial'])] = r
    results, task_data = {}, []
    for metric in REPEAT_METRICS:
        tasks = []
        for key, panel in by.items():
            if key[0] not in METRICS[metric][1]:
                continue
            if not all(panel.get((a, t), {}).get(metric) is not None for a in ARMS for t in [1, 2, 3]):
                continue
            vals = {a: [panel[(a,t)][metric] for t in [1,2,3]] for a in ARMS}
            distance = lambda x,y: abs(x-y)
            off = np.mean([distance(x,y) for x,y in combinations(vals[ARMS[0]],2)])
            within = np.mean([np.mean([distance(x,y) for x,y in combinations(vals[a],2)]) for a in ARMS[1:]])
            between = np.mean([np.mean([distance(x,y) for x,y in product(vals[a],vals[b])]) for a,b in combinations(ARMS[1:],2)])
            r = panel[(ARMS[0],1)]
            tasks.append({k:r[k] for k in ['source','task_id','study_id','family']} | dict(metric=metric, baseline_within=float(off), persona_within=float(within), between_personas=float(between), excess=float(between-within)))
        results[metric] = {k:task_stat(tasks,k) for k in ['baseline_within','persona_within','between_personas','excess']}
        task_data.extend(tasks)
    write_csv(DATA/'repeat_task_statistics.csv', task_data)
    # Exact-prefix collisions: fixed-length prefix, same task and script.
    template_tasks = []
    for _, panel in by.items():
        if not all(panel.get((a,t), {}).get('first_reply_opening_hash') for a in ARMS for t in [1,2,3]):
            continue
        base = panel[(ARMS[0],1)]
        def collision(pairs):
            eligible = [(a,b) for a,b in pairs if a['first_reply_script'] and a['first_reply_script'] == b['first_reply_script']]
            return (100*float(np.mean([a['first_reply_opening_hash']==b['first_reply_opening_hash'] for a,b in eligible])),len(eligible)) if eligible else (None,0)
        off,n_off = collision(combinations([panel[(ARMS[0],t)] for t in [1,2,3]],2))
        baseline_scripts={panel[(ARMS[0],t)]['first_reply_script'] for t in [1,2,3]}
        if len(baseline_scripts)!=1 or None in baseline_scripts:
            continue
        baseline_script=next(iter(baseline_scripts))
        eligible_arms=[a for a in ARMS[1:] if all(panel[(a,t)]['first_reply_script']==baseline_script for t in [1,2,3])]
        if len(eligible_arms)<2:
            continue
        within = [collision(combinations([panel[(a,t)] for t in [1,2,3]],2))[0] for a in eligible_arms]
        between = [collision(product([panel[(a,t)] for t in [1,2,3]],[panel[(b,t)] for t in [1,2,3]]))[0] for a,b in combinations(eligible_arms,2)]
        within = [x for x in within if x is not None]
        between = [x for x in between if x is not None]
        if off is not None and within and between:
            template_tasks.append({k:base[k] for k in ['source','task_id','study_id','family']} | dict(baseline_within=off,persona_within=float(np.mean(within)),between_personas=float(np.mean(between)),reduction_vs_off=float(off-np.mean(between)),reduction_vs_within=float(np.mean(within)-np.mean(between)),eligible_personas='|'.join(eligible_arms)))
    results['opening_collision_same_script'] = {k:task_stat(template_tasks,k) for k in ['baseline_within','persona_within','between_personas','reduction_vs_off','reduction_vs_within']}
    write_csv(DATA/'opening_collision_tasks.csv',template_tasks)
    # Explicitly English-primary personas only; observed Latin script required.
    # This is a sensitivity, not language detection or an outcome-selected subset.
    english_arms=['persona_off','candidate_148','candidate_089','candidate_127']
    language_tasks=[]
    for _,panel in by.items():
        if not all(panel.get((a,t),{}).get('simulator_chars') is not None and panel[(a,t)].get('first_reply_script')=='Latin' for a in english_arms for t in [1,2,3]):
            continue
        vals={a:[panel[(a,t)]['simulator_chars'] for t in [1,2,3]] for a in english_arms}
        within=float(np.mean([np.mean([abs(x-y) for x,y in combinations(vals[a],2)]) for a in english_arms[1:]]))
        between=float(np.mean([np.mean([abs(x-y) for x,y in product(vals[a],vals[b])]) for a,b in combinations(english_arms[1:],2)]))
        r=panel[(english_arms[0],1)]
        language_tasks.append({k:r[k] for k in ['source','task_id','study_id','family']} | dict(persona_within=within,between_personas=between,excess=between-within))
    results['english_primary_length_sensitivity']={k:task_stat(language_tasks,k) for k in ['persona_within','between_personas','excess']}
    write_csv(DATA/'english_primary_length_tasks.csv',language_tasks)
    return results

def analyze(snap, arms=None):
    arms = ARMS if arms is None else arms
    rows = [r for r in snap['episodes'] if r['eligible']]
    summary = dict(resamples=B,seed=SEED,metrics={m:{'label':v[0],'sources':v[1]} for m,v in METRICS.items()},
                   coverage={a:dict(Counter('analyzed' if r['eligible'] else r['trace_issue'] for r in snap['episodes'] if r['arm']==a)) for a in arms},
                   absolute={}, paired={})
    flat = []
    for metric, (_, sources) in METRICS.items():
        summary['absolute'][metric] = {}
        summary['paired'][metric] = {}
        for group in ['all', *sources]:
            sub = [r for r in rows if r['source'] in sources and (group=='all' or r['source']==group)]
            summary['absolute'][metric][group] = {a:summarize([r for r in sub if r['arm']==a],metric,balanced=group=='all') for a in arms}
            summary['paired'][metric][group] = {}
            for a in arms[1:]:
                pairs = paired(sub,metric,a)
                stat = summarize(pairs,balanced=group=='all')
                baseline = summarize(pairs,'baseline',balanced=group=='all')
                sd = baseline['task_sd']
                stat['baseline_task_sd'] = sd
                stat['standardized_delta'] = stat['mean']/sd if sd and stat['mean'] is not None else None
                summary['paired'][metric][group][a] = stat
                flat.append(dict(metric=metric,group=group,arm=a,mean=stat['mean'],ci_low=stat['ci95'][0] if stat['ci95'] else None,ci_high=stat['ci95'][1] if stat['ci95'] else None,tasks=stat['tasks'],episodes=stat['episodes'],standardized_delta=stat['standardized_delta']))
    summary['repeat_variation'] = repeat_analysis(rows)
    summary['invalid_native_metric_episodes'] = sum(bool(r.get('invalid_native_metrics')) for r in rows)
    write_json(DATA/'summary.json', summary)
    write_csv(DATA/'episodes.csv',snap['episodes'])
    write_csv(DATA/'paired_effects.csv',flat)
    return summary

def report(s):
    task_cell=lambda v:cell(v,counts=False)+f"; n={v['tasks']} tasks"
    repeats=s['repeat_variation']
    lines = ['# Experiment 01 — Behavioral diversity without semantic trajectories','',
             '[Executed notebook](behavioral_analysis.ipynb) · [Separate SciConv API-token analysis](SCICONV_TOKENS.md)','',
             'Original Astra-low panel: off/148/155/089/001/127 × 200 frozen tasks × three trials. Analyses use complete saved episodes, including completed scientific missing submissions; infrastructure-truncated traces are excluded. Repairs, Sol and the post-PR6 failed baseline are not pooled. No model calls or semantic embeddings.','',
             '## Principal observations','',
             f"- Communication length separates the selected personas beyond repeat variation: excess between-persona absolute reply-length difference is {cell(repeats['simulator_chars']['excess'], counts=False)} characters (n={repeats['simulator_chars']['excess']['tasks']} tasks). Restricting to English-primary personas with Latin-script replies retains an excess of {cell(repeats['english_primary_length_sensitivity']['excess'], counts=False)} characters (n={repeats['english_primary_length_sensitivity']['excess']['tasks']} tasks).",
             '- Extra approach reviews, revision requests and post-reply SciConv question counts show much smaller excess variation; all three excess-distance intervals include zero. Required-review workflows leave little optional review variation in the complete panel.',
             f"- Exact 40-character opening collisions are lower between personas than within persona-off by {cell(repeats['opening_collision_same_script']['reduction_vs_off'], counts=False)} percentage points (n={repeats['opening_collision_same_script']['reduction_vs_off']['tasks']} tasks). This is a script-matched lexical diagnostic, not evidence about semantic collapse.",
             '- Character counts and API tokens can move differently across languages. In particular, Mandarin-primary 155 has shorter character strings despite its larger SciConv token usage in the separate token report. Neither measures information quality.','',
             '## Coverage','',markdown_table(['Persona','Complete analyzed episodes','Excluded slots'],[[label(a),s['coverage'][a].get('analyzed',0),600-s['coverage'][a].get('analyzed',0)] for a in ARMS]),'',
             '## Definitions and uncertainty','',
             'An observation is an episode-level summary; repeats average within task, then sources receive equal weights for all-source summaries. Within a source tasks have equal weight. Pointwise 95% intervals use 20,000 study-cluster bootstrap draws within source, conditional on the observed trials. Paired changes match task and trial before averaging. The same trial number is a run block, not a shared random seed. No multiplicity-corrected significance claim is made.','',
             'Simulator length counts visible reply characters, excluding initial requests and private evidence. Actor length counts shared handoff answers or SciConv questions; tool calls and final SciConv specifications are excluded. Additional reviews subtract the required first review in each phase. Revision requests are simulator requests to continue during result review, not proof that a revision was completed. Absent opportunities remain missing rather than zero.','',
             'Script agreement compares actor text with the preceding noninitial simulator reply. Unicode script labels (Latin, CJK, Devanagari, Other) require at least 20 letters and 60% dominance; they are not language identification. Code fences are excluded for script/repetition analysis. Length and script differences do not establish information quality.','',
             'SciConv first questions precede persona-conditioned replies, so post-reply questions exclude the first. Exact repeated-question percentage requires at least two questions. Native clarification/grounding/memory fields are retained only inside [0,1], then displayed as percentages; invalid values are missing, not clipped. Ten-reply cap hits remain a proxy for the historical last-answer issue.','',
             f"Native-metric validation flagged {s['invalid_native_metric_episodes']} episodes with at least one invalid field.",'',
             '## Behavioral patterns','', '![Matched behavioral changes](figures/behavior/behavior_effects.png)','',
             'Colors show paired differences divided by the matched baseline task-level standard deviation, solely for display. Cell text gives the raw change and its 95% CI. Negative and positive changes are not intrinsically bad or good. See the tables below for all units and denominators.','']
    lines += ['![Task-level reply-length changes](figures/behavior/reply_length_distribution.png)','',
              'All matched task-level reply-length differences are shown, with no point subsampling. The teal estimates use equal source weights; raw points display individual tasks. Language and workflow affect character counts.','']
    for metric in METRICS:
        lines += ['### '+METRICS[metric][0],'',markdown_table(['Persona','Mean [95% CI]; tasks/episodes','Paired change vs off [95% CI]; tasks/pairs'],
                   [[label(a),cell(s['absolute'][metric]['all'][a]),'reference' if a==ARMS[0] else cell(s['paired'][metric]['all'][a],True)] for a in ARMS]),'']
    lines += ['## Repeat variation','', '![Within- and between-persona variation](figures/behavior/repeat_variation.png)','',
              'Each metric uses tasks with all three eligible values in every one of the six conditions. Within-condition distance is mean absolute difference over the three run pairs. Between-persona distance averages all nine episode pairs for each of the ten pairs among the five personas. Personas and persona pairs have equal weights. Pair combinations are not independent samples: distances are summarized once per task before the study bootstrap. Excess is between-persona minus within-persona distance; it describes these selected conditions rather than isolating a personality trait.','',
              markdown_table(['Metric','Within off','Within personas','Between personas','Excess between − within'],
                             [[METRICS[m][0],*[task_cell(s['repeat_variation'][m][k]) for k in ['baseline_within','persona_within','between_personas','excess']]] for m in REPEAT_METRICS]),'',
              '### English-primary length sensitivity','',
              'Restrict to off/148/089/127, selected by their explicit English-primary profile instruction, and require Latin-script first replies in all three runs. This removes the Mandarin/Hindi-primary personas; it is a sensitivity on a different complete task panel, not a controlled language intervention.','',
              markdown_table(['Comparison','Absolute reply-length difference [95% CI]'],[[k.replace('_',' '),task_cell(v)] for k,v in s['repeat_variation']['english_primary_length_sensitivity'].items()]),'',
              '## Exploratory template concentration','',
              'Openings are the first 40 alphanumeric Unicode characters after NFKC normalization, case folding and code-fence removal. Only replies with at least 40 such characters qualify. Initial requests and required controller/schema text are excluded; only researcher message content is used. First-reply collisions require the full repeated panel, one consistent baseline script across its three runs, and at least two personas sharing that script in all three runs. The same eligible personas enter within- and between-persona comparisons; persona pairs receive equal weights. Eligible personas can vary by task and are recorded. Fixed prefix length limits sample-length artifacts, but does not make this a semantic or language-normalized measure. The within-episode opening-repeat metric is separate and conditions on at least two eligible replies. Neither measure proves semantic collapse.','',
              markdown_table(['Comparison','Opening collision % or reduction (pp) [95% CI]; tasks'],[[k.replace('_',' '),task_cell(v)] for k,v in s['repeat_variation']['opening_collision_same_script'].items()]),'',
              '## Scope remaining','',
              'Semantic trajectories and embedding-based distances are deliberately deferred. Disagreement, feedback adoption, and per-fact volunteering need content annotation and are not inferred from character counts or decision actions. No human realism evaluation is planned. The selected profiles were chosen using prior performance, and missing complete traces can change coverage. All-source summaries mix workflows; per-benchmark values and full denominators are in the numeric summary.','',
              '[Numeric summary](data/behavior/summary.json) · [Episode features](data/behavior/episodes.csv) · [Paired effects](data/behavior/paired_effects.csv) · [Frozen provenance](data/behavior/snapshot.json)','',
              'Reproduce: `.venv/bin/python Experiment/01_behavioral_diversity/code/analyze_behavior.py`; use `--refresh` only to re-extract saved event logs. Plot with `code/plot_behavior.py`.','']
    (BASE/'BEHAVIOR_REPORT.md').write_text('\n'.join(lines))

def main():
    p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args()
    snap=collect() if args.refresh or not (DATA/'snapshot.json').exists() else json.loads((DATA/'snapshot.json').read_text())
    s=analyze(snap);report(s)
    print(json.dumps({'coverage':s['coverage'],'repeat_excess':{m:s['repeat_variation'][m]['excess'] for m in REPEAT_METRICS}},indent=2))

if __name__=='__main__':
    main()
