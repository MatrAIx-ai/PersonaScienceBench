"""Within-conversation lexical reuse; no inference, embeddings, or saved prose."""
import json
import re
import unicodedata
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from extract import ROOT, BASE, DATA, ARMS, SOURCES, sha, write_json, write_csv
from analyze import task_values, summary, group_summaries, flatten

WINDOWS = (20, 40, 80)
PRIMARY = 40  # Fixed before inspecting outcomes; neighboring lengths are sensitivities.


def normalize(text):
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'^\s*>.*$', '', text, flags=re.M)
    text = unicodedata.normalize('NFKC', text).casefold()
    # Include combining marks (e.g. Devanagari); no whitespace-token assumptions.
    return ''.join(c for c in text if unicodedata.category(c)[0] in 'LNM')


def reuse(messages, width):
    """Mean later-turn fraction of windows seen in earlier same-role messages.

    The first eligible message establishes history. A window repeated inside
    the current message alone is not a cross-turn repetition. Short messages
    cannot supply this statistic and are excluded, not assigned zero.
    """
    seen = set()
    turns = []
    eligible = 0
    for index, text in enumerate(messages, 1):
        if len(text) < width:
            continue
        grams = [text[i:i+width] for i in range(len(text)-width+1)]
        if eligible:
            hits = sum(g in seen for g in grams)
            turns.append(dict(turn=index, value=100*hits/len(grams), matched_windows=hits, windows=len(grams)))
        seen.update(grams)
        eligible += 1
    return (float(np.mean([r['value'] for r in turns])) if turns else None), eligible, turns


def messages(events, source, normalizer=normalize):
    out = {'simulator': [], 'actor': []}
    for event in events:
        kind = event['type']; payload = event.get('payload') or {}
        if source == 'sciconvbench':
            if kind == 'researcher_reply': out['simulator'].append(payload.get('answer', ''))
            elif kind == 'researcher_question': out['actor'].append(payload.get('question', ''))
        else:
            if kind == 'researcher_decision' and payload.get('phase') != 'initial_inspection' and payload.get('interaction') != 'initial_request':
                out['simulator'].append(payload.get('message', ''))
            elif kind == 'agent_handoff': out['actor'].append(payload.get('answer', ''))
    assert all(isinstance(t, str) for role in out.values() for t in role)
    return {role: [normalizer(t) for t in texts] for role, texts in out.items()}


def extract_one(trace):
    meta = {k:trace[k] for k in ['source','task_id','study_id','family','arm','trial']}
    if trace.get('exclusion') is not None:
        return [meta|dict(role=role,width=w,value=None,exclusion=trace['exclusion']) for role in ['simulator','actor'] for w in WINDOWS], []
    raw = (ROOT/trace['trace_path']).read_bytes()
    assert sha(raw) == trace['sha256'], trace['trace_path']
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    rows=[]; turns=[]
    for role,texts in messages(events,trace['source']).items():
        for width in WINDOWS:
            value,eligible,parts = reuse(texts,width)
            rows.append(meta|dict(role=role,width=width,value=value,exclusion=None if value is not None else 'fewer_than_two_length_eligible_messages',messages=len(texts),eligible_messages=eligible,scored_turns=len(parts),normalized_chars=sum(map(len,texts)),trace_sha256=trace['sha256']))
            turns.extend([meta|dict(role=role,width=width,**part) for part in parts])
    return rows, turns


def analyze_rows(rows, windows=WINDOWS):
    cells=[]; cases=[]; contrasts=[]; coverage=[]
    for role in ['simulator','actor']:
        for width in windows:
            selected=[r for r in rows if r['role']==role and r['width']==width and r['value'] is not None]
            available={arm:task_values([r for r in selected if r['arm']==arm],'value') for arm in ARMS}
            common=set.intersection(*[{(r['source'],r['task_id']) for r in available[a]} for a in ARMS])
            for arm in ARMS:
                for panel in ['common','available']:
                    rr=[r for r in available[arm] if panel=='available' or (r['source'],r['task_id']) in common]
                    cases.extend([r|dict(arm=arm,role=role,width=width,panel=panel) for r in rr])
                    for level,group,result in group_summaries(rr,True):
                        cells.append(dict(arm=arm,role=role,width=width,panel=panel,level=level,group=group,**result))
            coverage.append(dict(role=role,width=width,questions=len(common),source_counts=dict(Counter(src for src,_ in common))))
            # Matched available case means; single-trial settings are not given artificial repeats.
            by_arm={arm:{(r['source'],r['task_id']):r for r in available[arm]} for arm in ARMS}
            for arm in ARMS[1:]:
                delta=[by_arm[arm][q]|dict(value=by_arm[arm][q]['value']-by_arm[ARMS[0]][q]['value']) for q in sorted(common)]
                contrasts.append(dict(arm=arm,role=role,width=width,**summary(delta,True)))
    return dict(cells=cells,cases=cases,contrasts=contrasts,coverage=coverage)

def report(result):
    from report import table,cell
    def chosen(role,width=PRIMARY):
        return [r for r in result['cells'] if r['role']==role and r['width']==width and r['panel']=='common' and r['level']=='all']
    lines=['# Historical character-based self-repetition', '', 'The current figure uses word-based repetition; see [WORD_REPETITION.md](WORD_REPETITION.md). This page preserves the earlier 40-character definition and results.', '',
           'This replaces the cross-run structural heatmap in panel A. It uses saved original messages only, separated into simulator and actor roles. No LLM inference or new embeddings. B and D retain their previous values. The prior structural figure and notebook are archived under `revisions/v2_structural_A/`.', '',
           '## Definition', '',
           'For each later message of one role in a conversation, form every overlapping window of 40 normalized Unicode characters. Count a window as repeated if exactly the same window appeared in an earlier message of that same role and episode. Divide matched windows by all windows in the current message, then average these fractions across eligible later turns. Repeated windows inside the current message alone do not count. The first eligible message supplies history and is not scored.', '',
           'Normalization: remove fenced code blocks and Markdown blockquote lines; Unicode NFKC and casefold; retain letters, combining marks and numbers, removing punctuation/whitespace. No word-tokenizer, translation, summaries or semantic judge. Simulator messages omit initial requests/inspection; actor messages are handoffs or SciConv clarification questions, excluding tool logs, transcript history and final SciConv specification. Naturally restated or unmarked quoted material remains part of the observed output.', '',
           'The primary width of 40 was set before examining outcomes, following the existing 40-character opening analysis. Widths 20 and 80 are sensitivity checks, not alternatives selected by the result. Characters span languages differently; multilingual persona settings and code-heavy messages can affect this metric. It measures long verbatim phrase reuse, not semantic redundancy, unnecessary questioning, lack of progress, or mode collapse. Necessary scientific terms or facts may repeat legitimately.', '',
           '## Aggregation and missingness', '',
           'Require at least two messages of the same role with sufficient normalized length. Too-short or single-message conversations are unavailable, never zero. Average eligible original trials within question, retain questions eligible for all five settings, average questions within benchmark and then the five benchmarks equally. Simulator and actor panels are matched separately. Eligibility conditions on conversation length and successful trace completion. Longer conversations have more opportunities for reuse; this is descriptive and does not remove that confounding. Three-trial settings use their available eligible trials; 003/046 use one. Paired contrasts compare question means, not necessarily the same number of trials.', '',
           'Pointwise 95% percentile CIs use 20,000 source-study cluster bootstrap draws, retaining each sampled study’s matched questions. Trial noise is conditional on saved repeats, not independently re-estimated. No significance stars or multiplicity-adjusted claims.', '',
           table(['Role','Window length','Common questions','Source counts'],[[r['role'],r['width'],r['questions'],json.dumps(r['source_counts'],sort_keys=True)] for r in result['coverage']]), '']
    for role in ['simulator','actor']:
        lines.extend(['## '+role.capitalize()+' results — 40 characters','',table(['Setting','Repeated windows % [95% CI]','Paired difference vs off (pp)'],[[r['arm'].replace('candidate_','').replace('persona_off','Off'),cell(r),'Reference' if r['arm']==ARMS[0] else cell(next(c for c in result['contrasts'] if c['arm']==r['arm'] and c['role']==role and c['width']==PRIMARY))] for r in chosen(role)]),''])
    lines.extend(['## Sensitivity to phrase length','',table(['Role','Window','Off','155','001','003','046'],[[role,width,*[f"{r['mean']:.4f}" for r in chosen(role,width)]] for role in ['simulator','actor'] for width in WINDOWS]),'',
                  'Sensitivity panels can have different eligible questions; coverage is reported above. The primary simulator contrasts all have CIs including zero. The data do not establish that persona injection reduces within-conversation simulator self-repetition. Low lexical repetition does not rule out semantic or strategic repetition.', '',
                  '## Figure and data','',
                  '[Archived character figure](revisions/v5_character_matching/figures/metric_suite.pdf) · [Archived character distributions](revisions/v5_character_matching/figures/self_repetition_roles.pdf) · [Executed notebook](metric_suite.ipynb). A shows mean/CI because most case-level values are zero and a few outliers dominate the raw scale. Supporting violins show source-balanced KDEs (Scott bandwidth; observed range; equal maximum width), case dots, source-balanced mean and CI. Density is not uncertainty.', '',
                  'CSV files under data/: `self_repetition_episodes`, `self_repetition_turns`, `self_repetition_cases`, `self_repetition_cells`, `self_repetition_contrasts`. They contain numbers and hashes, not message text. Frozen trace hashes are checked on extraction.', '',
                  '`OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/self_repetition.py` regenerates the extraction, statistics and this report.'])
    (BASE/'SELF_REPETITION.md').write_text('\n'.join(lines)+'\n')


def main():
    snap=json.loads((DATA/'snapshot.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool: pieces=list(pool.map(extract_one,snap['traces']))
    rows=[r for a,_ in pieces for r in a];turns=[r for _,b in pieces for r in b]
    result=analyze_rows(rows)
    result['method']=dict(primary_window=PRIMARY,sensitivity_windows=list(WINDOWS),unit='normalized Unicode characters, preserving letters/numbers/combining marks',within_trace='mean repeated-window fraction over later length-eligible same-role turns',question='mean over available eligible original trials',aggregate='common five-setting questions; equal questions within source, equal represented-source weights',ci='20000 source-study cluster percentile draws, conditional on saved trials',interpretation='verbatim cross-turn reuse; not judged semantic redundancy or mode collapse',normalization='NFKC, casefold, strip fenced code and blockquote lines, remove punctuation/whitespace',source_sha256=sha((DATA/'snapshot.json').read_bytes()))
    write_json(DATA/'self_repetition_summary.json',result)
    for name,rr in [('self_repetition_episodes',rows),('self_repetition_turns',turns),('self_repetition_cells',result['cells']),('self_repetition_cases',result['cases']),('self_repetition_contrasts',result['contrasts'])]:write_csv(DATA/(name+'.csv'),flatten(rr))
    print(json.dumps(result['coverage'],indent=2),flush=True)
    for r in result['cells']:
        if r['role']=='simulator' and r['width']==PRIMARY and r['panel']=='common' and r['level']=='all':print(r['arm'],r['mean'],r['ci95'],flush=True)
    report(result)


if __name__ == '__main__': main()
