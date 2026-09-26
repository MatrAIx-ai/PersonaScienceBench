#!/usr/bin/env python3
"""Publish a fixed partial-run snapshot with matched scores and linked traces."""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from statistics import mean
import os
import shutil
import hashlib
from summarize_persona_benchmark_scores import normalized
from report_top_persona_deviations import simulator_behavior

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/full-persona-v2-two-20260926'
OUT=ROOT/'reports/full_persona_v2'

def score(row):
    if row is None: return None
    if row['status']=='missing_submission': return 0.0
    if row['status'] not in {'scored','completed'}: return None
    return normalized(row)

def ungated(row):
    if row is None: return None
    if row['status']=='missing_submission': return 0.0
    if row['status'] not in {'scored','completed'} or 'coverage_mean' not in row['metrics']: return None
    return float(row['metrics']['coverage_mean'])/100.0

def is_control(arm): return arm=='persona_off' or arm.startswith('persona_off_r')
def control_mean(rows,fn=None):
    vals=[v for v in ((fn or score)(r) for r in rows) if v is not None]
    return mean(vals) if vals else None

def link(path,parent): return os.path.relpath(path,parent)
def fmt(v): return '—' if v is None else f'{v:.2f}'
def behavior_pairs(pairs,key):
    vals=[]
    for on,off in pairs:
        if key=='turns': a,b=on['behavior']['exchanges'],control_mean(off,lambda c:c['behavior']['exchanges'])
        else:
            a=simulator_behavior(on['trace'],on['benchmark'])[key]
            b=control_mean(off,lambda c:simulator_behavior(c['trace'],c['benchmark'])[key])
        if a is not None and b is not None: vals.append((a,b))
    return (mean(x[0] for x in vals),mean(x[1] for x in vals)) if vals else (None,None)


def top_tables(rankings, common):
    baseline = rankings[0]['off'] * 100
    lines = [f'**Shared baseline: {baseline:.2f}%.** All personas are compared on the same {len(common)} questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.', '',
             '| Rank | Persona | Score | Change vs off | Traces |',
             '|---:|---|---:|---:|---|']
    for rank, r in enumerate(rankings[:10], 1):
        arm = r['persona']
        lines.append(f'| {rank} | [{arm.removeprefix("candidate_")}](profiles/{arm}.md) | {100*r["on"]:.2f}% | **{100*r["delta"]:+.2f} pp** | [Read](traces/{arm}.md) |')
    lines += ['', '**Behavior on the same questions**', '',
              'Each cell shows **persona on / baseline**. Rows follow the performance ranking.', '',
              '| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |',
              '|---|---:|---:|---:|']
    for r in rankings[:10]:
        arm = r['persona']
        cols = [' / '.join(fmt(v) for v in behavior_pairs(r['pairs'], key))
                for key in ['turns', 'words_per_reply', 'revision_requests']]
        lines.append(f'| [{arm.removeprefix("candidate_")}](profiles/{arm}.md) | ' + ' | '.join(cols) + ' |')
    lines += ['', 'Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.', '']
    return lines


def publish_traces(rows):
    destination = OUT / 'recorded_traces'
    destination.mkdir(exist_ok=True)
    mapping, inventory = {}, {}
    for row in rows:
        if not row.get('trace'):
            continue
        source = Path(row['trace'])
        if not source.is_file():
            continue
        name = source.parent.parent.name + '.md'
        target = destination / name
        content = source.read_bytes()
        if not target.exists() or target.read_bytes() != content:
            temporary = target.with_suffix(".md.tmp")
            temporary.write_bytes(content)
            temporary.replace(target)
        mapping[source.resolve()] = '../recorded_traces/' + name
        inventory[name] = {'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size}
    import re
    for index in (OUT / 'traces').glob('*.md'):
        text = index.read_text()
        def replace(match):
            target = mapping.get((index.parent / match.group(1)).resolve())
            return '[Read](' + target + ')' if target else match.group(0)
        text = re.sub(r'\[Read\]\(([^)]+)\)', replace, text)
        text = text.replace('raw traces require the local run directory.', 'recorded Markdown traces are included in the repository. Links inside them to raw JSON logs and execution artifacts remain local.')
        index.write_text(text)
    (destination / 'manifest.json').write_text(json.dumps(inventory, indent=2) + '\n')
    (destination / 'README.md').write_text(f'# Recorded interaction traces\n\n{len(inventory)} exact recorded Markdown traces accompany the current report. They include recorded prompts, responses, tool activity and grading records. Raw JSON logs and execution artifacts linked inside them remain local. Browse the [report and persona indexes](../README.md).\n')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ['profiles','traces']: (OUT/name).mkdir(exist_ok=True)
    data=json.loads((RUN/'comparison.json').read_text())
    manifest=json.loads((RUN/'manifest.json').read_text())
    rows=data['episodes']; tasks=manifest['tasks']; arms=sorted(a for a in {j['arm'] for j in manifest['jobs']} if not is_control(a))
    lookup={(r['arm'],r['task']):r for r in rows}
    controls={t['id']:[] for t in tasks}
    for r in rows:
        if is_control(r['arm']): controls[r['task']].append(r)
    common=[t['id'] for t in tasks if control_mean(controls[t['id']]) is not None and all(score(lookup.get((a,t['id']))) is not None for a in arms)]
    assert common,'No common scored tasks for ranking'
    rankings=[]
    for arm in arms:
        pairs=[(lookup[arm,t],controls[t]) for t in common]
        on=mean(score(a) for a,b in pairs);off=mean(control_mean(b) for a,b in pairs)
        rankings.append({'persona':arm,'on':on,'off':off,'delta':on-off,'pairs':pairs})
    rankings.sort(key=lambda r:(-abs(r['delta']),r['persona']))
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    complete = len(rows) == len(manifest['jobs'])
    state = 'Final results' if complete else 'Partial results'
    lines=[f'# Full-persona experiment: {state.lower()}','',f'Snapshot: {now}. **{len(rows)}/310 episodes finished**. ' + ('The batch is complete.' if complete else 'The batch continues; this report is a fixed snapshot.'),'',
        '30 source-balanced, behaviorally diverse profiles; two fixed questions per benchmark; one fresh shared persona-off baseline per question. Actor, simulator and judge use GPT-6 Luna with reasoning effort `none`. Full persona text is injected only into the simulator system prompt. Both conditions can use general knowledge; evaluator references remain private.','',
        'Scores use ASI score/max score, Bix grade, Discovery final score, EXP gated coverage/100 and SciConv FRR. **Missing submissions count as zero for both persona and baseline** in this report (an explicit analysis convention, not a fabricated native grade). Infrastructure failures and pending episodes are excluded. All comparisons are task-matched; these single-run descriptive results do not establish causality or statistical significance.','',
        '| Benchmark | Finished / 62 | Missing submissions: on / off | Infrastructure failures | Paired cases | Persona mean | Matched off mean | Difference | Ungated persona / off |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    stats=[]
    for benchmark in sorted({t['benchmark'] for t in tasks}):
        rr=[r for r in rows if r['benchmark']==benchmark]
        pairs=[(r,controls[r['task']]) for r in rr if not is_control(r['arm']) and score(r) is not None and control_mean(controls[r['task']]) is not None]
        on=mean(score(a) for a,b in pairs) if pairs else None;off=mean(control_mean(b) for a,b in pairs) if pairs else None
        record={'benchmark':benchmark,'finished':len(rr),'pairs':len(pairs),'on':on,'off':off,'delta':on-off if pairs else None}
        ungated_text='—'
        if benchmark=='expbench':
            upairs=[(ungated(a),control_mean(b,ungated)) for a,b in pairs]
            upairs=[(a,b) for a,b in upairs if a is not None and b is not None]
            record.update(ungated_on=mean(a for a,b in upairs) if upairs else None,ungated_off=mean(b for a,b in upairs) if upairs else None,ungated_pairs=len(upairs))
            if upairs: ungated_text=f'{fmt(100*record["ungated_on"])}% / {fmt(100*record["ungated_off"])}% (n={len(upairs)})'
        stats.append(record)
        missing=[sum(r['status']=='missing_submission' and is_control(r['arm'])==control for r in rr) for control in [False,True]]
        failures=sum(r['status'] not in {'scored','completed','missing_submission'} for r in rr)
        delta=f'{100*(on-off):+.2f} pp' if pairs else '—'
        lines.append(f'| {benchmark} | {len(rr)}/62 | {missing[0]} / {missing[1]} | {failures} | {len(pairs)} | {fmt(100*on) if on is not None else "—"}% | {fmt(100*off) if off is not None else "—"}% | {delta} | {ungated_text} |')
    lines += ['', 'Benchmark means use available comparable outcomes; infrastructure failures are excluded. Matched off means can differ by task mix; no baseline is regenerated. BixBench comparisons use the explicit missing-submission convention because both baseline runs produced no submission.','',
              '## Ten largest absolute persona deviations','',
              f'Ranking uses **the same {len(common)} questions for all 30 profiles**, with complete comparable outcomes: '+', '.join('`'+t+'`' for t in common)+'. Questions with an infrastructure or evaluator error in any arm are excluded from this common-task ranking. Missing submissions remain zero in both arms. No candidate is excluded by identity. Ties use candidate ID.','',
              'Turns are actor–simulator handoffs (native clarification Q&A for SciConv), excluding tool calls. Words/reply uses visible simulator replies, excluding initial requests and private evidence, averaged per task. Revisions count result-review requests for more work; SciConv has no such stage and is omitted. All behavioral columns use the same ranked questions and show persona on / matched off.','',
              ]
    for r in rankings:
        arm=r['persona'];profile=json.loads((RUN/'configs'/arm/'persona.private.json').read_text())
        (OUT/'profiles'/f'{arm}.md').write_text(f'# {arm}: exact simulator persona\n\nThis is the full rendered identity block injected into the simulator system prompt. Common protocol instructions and task context are separate and recorded in local API traces. The actor and judge do not receive this block.\n\n[Task traces](../traces/{arm}.md)\n\n```text\n'+profile['identity_prompt']+'\n```\n')
        detail=[f'# {arm}: interaction traces','',f'[Exact persona](../profiles/{arm}.md) · [Results](../README.md)','',
                'Snapshot statuses; raw traces require the local run directory. All ten questions are listed, including pending and unscored cases.','',
                '| Task | Persona status | Score: on / off | Persona trace | Baseline trace | Turns: on / off |','|---|---|---:|---|---|---:|']
        for task in tasks:
            tid=task['id'];a=lookup.get((arm,tid));b=controls[tid]
            links=[]
            for items in [[a],b]:
                cells=[]
                for item in items:
                    path=Path(item['trace']) if item and item.get('trace') else None
                    cells.append(f'[Read]({link(path,OUT/"traces")})' if path and path.is_file() else 'Pending/unavailable')
                links.append(', '.join(cells) or 'Pending/unavailable')
            sa,sb=score(a),control_mean(b)
            tb=control_mean(b,lambda c:c['behavior']['exchanges'])
            detail.append(f'| `{tid}` | {a["status"] if a else "pending"} | {fmt(sa)} / {fmt(sb)} | {links[0]} | {links[1]} | {a["behavior"]["exchanges"] if a else "—"} / {fmt(tb)} |')
        (OUT/'traces'/f'{arm}.md').write_text('\n'.join(detail)+'\n')
    table = top_tables(rankings, common)
    lines += table
    lines+=['','## All 30 profiles on the common questions','', '| Persona | Persona mean | Fixed baseline mean | Difference |','|---|---:|---:|---:|']
    for r in sorted(rankings,key=lambda r:-r['delta']):
        lines.append(f'| [{r["persona"]}](profiles/{r["persona"]}.md) | {100*r["on"]:.2f}% | {100*r["off"]:.2f}% | {100*r["delta"]:+.2f} pp |')
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    snapshot={'timestamp':now,'finished':len(rows),'total':310,'statuses':dict(Counter(r['status'] for r in rows)),'common_tasks':common,'benchmarks':stats,'rankings':[{k:v for k,v in r.items() if k!='pairs'} for r in rankings],'episodes':rows}
    (OUT/'snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    readme=ROOT/'README.md';s=readme.read_text();start='<!-- FULL_PERSONA_RESULTS_START -->';end='<!-- FULL_PERSONA_RESULTS_END -->'
    block=start+'\n\n## Current persona results\n\n'+f'{state}: **{len(rows)}/310 episodes finished**. [Benchmark results, all 30 profiles, and interaction traces](reports/full_persona_v2/README.md).\n\n'
    block+=f'Top deviations below use the same **{len(common)} completed questions** for every persona; questions with infrastructure or evaluator errors are excluded for every persona. Differences are normalized score percentage points.\n\n'
    block+='\n'.join(x.replace('](profiles/','](reports/full_persona_v2/profiles/').replace('](traces/','](reports/full_persona_v2/traces/') for x in table)+'\n\n'+end
    if start in s:s=s[:s.index(start)]+block+s[s.index(end)+len(end):]
    else:s=s.replace('## Repository guide',block+'\n\n## Repository guide')
    readme.write_text(s)
    publish_traces(rows)
    print(json.dumps({k:snapshot[k] for k in ['finished','statuses','common_tasks','benchmarks','rankings']},indent=2))

if __name__=='__main__': main()
