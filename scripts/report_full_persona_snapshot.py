#!/usr/bin/env python3
"""Publish a fixed partial-run snapshot with matched scores and linked traces."""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from statistics import mean
import os
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

def link(path,parent): return os.path.relpath(path,parent)
def fmt(v): return '—' if v is None else f'{v:.2f}'
def behavior_pairs(pairs,key):
    vals=[]
    for on,off in pairs:
        if key=='turns': a,b=on['behavior']['exchanges'],off['behavior']['exchanges']
        else:
            a=simulator_behavior(on['trace'],on['benchmark'])[key]
            b=simulator_behavior(off['trace'],off['benchmark'])[key]
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


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ['profiles','traces']: (OUT/name).mkdir(exist_ok=True)
    data=json.loads((RUN/'comparison.json').read_text())
    manifest=json.loads((RUN/'manifest.json').read_text())
    rows=data['episodes']; tasks=manifest['tasks']; arms=sorted({j['arm'] for j in manifest['jobs']} - {'persona_off'})
    lookup={(r['arm'],r['task']):r for r in rows}
    controls={r['task']:r for r in rows if r['arm']=='persona_off'}
    common=[t['id'] for t in tasks if all(score(lookup.get((a,t['id']))) is not None for a in ['persona_off',*arms])]
    assert common,'No common scored tasks for ranking'
    rankings=[]
    for arm in arms:
        pairs=[(lookup[arm,t],controls[t]) for t in common]
        on=mean(score(a) for a,b in pairs);off=mean(score(b) for a,b in pairs)
        rankings.append({'persona':arm,'on':on,'off':off,'delta':on-off,'pairs':pairs})
    rankings.sort(key=lambda r:(-abs(r['delta']),r['persona']))
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    lines=['# Full-persona experiment: partial results','',f'Snapshot: {now}. **{len(rows)}/310 episodes finished**. The batch continues; this report is a fixed snapshot, not a live counter.','',
        '30 source-balanced, behaviorally diverse profiles; two fixed questions per benchmark; one fresh shared persona-off baseline per question. Actor, simulator and judge use GPT-6 Luna with reasoning effort `none`. Full persona text is injected only into the simulator system prompt. Both conditions can use general knowledge; evaluator references remain private.','',
        'Scores use ASI score/max score, Bix grade, Discovery final score, EXP gated coverage/100 and SciConv FRR. **Missing submissions count as zero for both persona and baseline** in this report (an explicit analysis convention, not a fabricated native grade). Infrastructure failures and pending episodes are excluded. All comparisons are task-matched; these single-run descriptive results do not establish causality or statistical significance.','',
        '| Benchmark | Finished / 62 | Missing submissions: on / off | Infrastructure failures | Paired cases | Persona mean | Matched off mean | Difference |','|---|---:|---:|---:|---:|---:|---:|---:|']
    stats=[]
    for benchmark in sorted({t['benchmark'] for t in tasks}):
        rr=[r for r in rows if r['benchmark']==benchmark]
        pairs=[(r,controls[r['task']]) for r in rr if r['arm']!='persona_off' and score(r) is not None and score(controls[r['task']]) is not None]
        on=mean(score(a) for a,b in pairs) if pairs else None;off=mean(score(b) for a,b in pairs) if pairs else None
        record={'benchmark':benchmark,'finished':len(rr),'pairs':len(pairs),'on':on,'off':off,'delta':on-off if pairs else None}
        stats.append(record)
        missing=[sum(r['status']=='missing_submission' and (r['arm']=='persona_off')==control for r in rr) for control in [False,True]]
        failures=sum(r['status'] not in {'scored','completed','missing_submission'} for r in rr)
        delta=f'{100*(on-off):+.2f} pp' if pairs else '—'
        lines.append(f'| {benchmark} | {len(rr)}/62 | {missing[0]} / {missing[1]} | {failures} | {len(pairs)} | {fmt(100*on) if on is not None else "—"}% | {fmt(100*off) if off is not None else "—"}% | {delta} |')
    lines += ['', 'Partial benchmark means reflect the profiles that finished so far. Matched off means can differ by task mix; no baseline is regenerated. BixBench comparisons use the explicit missing-submission convention because both baseline runs produced no submission.','',
              '## Ten largest absolute persona deviations','',
              f'Ranking uses **the same {len(common)} questions for all 30 profiles**, with complete comparable outcomes: '+', '.join('`'+t+'`' for t in common)+'. Other benchmarks are excluded from this ranking until comparable coverage is available. No candidate is excluded by identity. Ties use candidate ID.','',
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
            for item in [a,b]:
                path=Path(item['trace']) if item and item.get('trace') else None
                links.append(f'[Read]({link(path,OUT/"traces")})' if path and path.is_file() else 'Pending/unavailable')
            sa,sb=score(a),score(b)
            detail.append(f'| `{tid}` | {a["status"] if a else "pending"} | {fmt(sa)} / {fmt(sb)} | {links[0]} | {links[1]} | {a["behavior"]["exchanges"] if a else "—"} / {b["behavior"]["exchanges"]} |')
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
    block=start+'\n\n## Current persona results\n\n'+f'Partial snapshot: **{len(rows)}/310 episodes finished**. [Benchmark results, all 30 profiles, and interaction traces](reports/full_persona_v2/README.md).\n\n'
    block+=f'Top deviations below use the same **{len(common)} completed questions** for every persona; they are not a five-benchmark final ranking. Differences are normalized score percentage points.\n\n'
    block+='\n'.join(x.replace('](profiles/','](reports/full_persona_v2/profiles/').replace('](traces/','](reports/full_persona_v2/traces/') for x in table)+'\n\n'+end
    if start in s:s=s[:s.index(start)]+block+s[s.index(end)+len(end):]
    else:s=s.replace('## Repository guide',block+'\n\n## Repository guide')
    readme.write_text(s)
    print(json.dumps({k:snapshot[k] for k in ['finished','statuses','common_tasks','benchmarks','rankings']},indent=2))

if __name__=='__main__': main()
