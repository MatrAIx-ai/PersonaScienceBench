#!/usr/bin/env python3
"""Collect the declared fourteen-case conversion trial, retaining every recovery."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/conversion_v2'
BATCHES={
 'base_python':'conversion-v2-two-python-20260925',
 'base_terminal':'conversion-v2-two-terminal-20260925',
 'exp':'conversion-v2-two-exp-fixed-20260925',
 'asi':'conversion-v2-two-asi-ready-20260925',
 'sciconv':'conversion-v2-two-sciconv-ready-20260925',
 'discovery_recovery':'conversion-v2-recovery-discovery-turnfix-20260925',
 'terminal_recovery':'conversion-v2-recovery-terminal-turnfix-20260925',
 'asi_recovery':'conversion-v2-recovery-asi-typed-20260925',
}
def read(path,default=None):return json.loads(path.read_text()) if path.exists() else default

def outcome(record):
    metrics=record.get("metrics") or {}
    benchmark=record["episode_id"].split(":",1)[0]
    if not metrics:return "No sealed submission" if record["status"]=="missing_submission" else "Unscored"
    if benchmark=="bixbench":return f"Correct: {metrics['grade']}/1"
    if benchmark=="terminal_bench_science":return f"Reward: {metrics['reward']:g}/1"
    if benchmark=="scienceagentbench":return f"Success: {metrics['success_rate']}/1"
    if benchmark=="discoverybench":return f"Score: {metrics['final_score']:.3f}/1"
    if benchmark=="asibench":return f"Score: {metrics['score']:.2f}/{metrics['max_score']:g}"
    if benchmark=="expbench":return f"Coverage: {metrics['coverage_mean']:.2f}/100; gated: {metrics['gated_coverage_mean']:.2f}"
    if benchmark=="sciconvbench":return f"FRR: {metrics['FRR']}; CGRR: {metrics['CGRR']}"
    return json.dumps(metrics)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 attempts=[]
 for root in sorted((ROOT/'runs').glob('conversion-v2-*20260925')):
  if not list(root.glob('*/result.json')):continue
  subprocess.run([sys.executable,str(ROOT/'scripts/render_run_traces.py'),str(root)],check=True,capture_output=True,text=True)
  for p in sorted(root.glob('*/result.json')):
   r=read(p);tid=r.get('episode_id') or 'expbench:'+r['task_id'];case=p.parent
   events=case/'controller/events.jsonl'
   if not events.exists():events=case/'events.jsonl'
   rows=[json.loads(x) for x in events.read_text().splitlines()] if events.exists() else []
   handoffs=[x for x in rows if x['type']=='agent_handoff']
   replies=[x for x in rows if x['type']=='researcher_reply']
   stages={stage:sum(x['payload'].get('stage')==stage for x in handoffs) for stage in ['plan','result']}
   metrics=r.get('evaluation',{}).get('metrics')
   if tid.startswith('expbench:'):
    native=r.get('initial') or {};metrics={k:native.get(k) for k in ['coverage_mean','gated_coverage_mean']}
   attempts.append({'episode_id':tid,'batch':root.name,'status':r['status'],'metrics':metrics,'agent_handoffs':len(handoffs),'plan_handoffs':stages['plan'],'result_handoffs':stages['result'],'clarification_exchanges':len(replies),'trace':str((case/'trace.md').relative_to(ROOT)),'result':str(p.relative_to(ROOT))})
 selected={}
 for key,batch in BATCHES.items():
  for record in attempts:
   if record['batch']==batch:selected[record['episode_id']]=record
 # No score-based selection: fixed recovery batches override only failed-infrastructure attempts.
 ordered=sorted(selected.values(),key=lambda r:r['episode_id'])
 report={'selection_policy':'Fixed original batches plus declared infrastructure recoveries; no best-score selection','models':'openai/gpt-6-luna','persona_enabled':False,'selected_cases':ordered,'attempts':attempts,'raw_records_scope':'Trace and result paths point to ignored local files, not files distributed on GitHub.','expected_cases':14,'completed_records':len(ordered)}
 (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# Automated conversion revision: two cases per benchmark','',
 'Persona off; actor, researcher and LLM judges use GPT-6 Luna. Native programmatic graders remain programmatic. Independent cases ran concurrently. These are integration trials, not a controlled estimate of persona or collaboration effects.','',
 'Full population: [conversion counts and readiness](conversion_summary.md). Conversion rules: [per-benchmark revision](../../docs/design/conversion_revision_v2.md).','',
 '| Case | Status | Native outcome | Exchanges / handoffs | Local trace (not in Git) |','|---|---|---|---:|---|']
 for r in ordered:
  count=r['clarification_exchanges'] if r['episode_id'].startswith('sciconvbench:') else r['agent_handoffs']
  lines.append(f"| `{r['episode_id']}` | {r['status']} | {outcome(r)} | {count} | `{r['trace']}` |")
 lines+=['','## Interpretation','',
 '- Execution/design tracks count agent-to-researcher handoffs, including required approach and result reviews. SciConvBench counts clarification question/answer pairs. These counts are not interchangeable measures of useful collaboration.',
 '- EXP-Bench remains design-only. ASI scores are local seed31415 scores for a B3-plus-B2-guidance adaptation, not official autonomous B3 scores. SciConvBench evaluates specifications and dialogue, not solver execution.',
 '- ScienceAgentBench instance 22 reached researcher-selected stopping after review but had no sealed submission; it remains unscored and is not replaced by an easier case.',
 '- Missing submissions remain missing unless the benchmark has a declared penalty policy. Infrastructure failures are separately recorded; scientific zeros are retained.',
 '- Early researcher responses sometimes generated multiple imagined decisions or were truncated. Recovery requests introduced an explicit current-turn boundary, then a typed single-decision tool. Exact request versions and token caps are recorded per attempt; successful runs were not repeated to homogenize configuration.',
 '- EXP’s first attempts failed before actor calls because repeated fact topics violated the legacy interface. Unique source-span topics fixed preparation.',
 '- SciConvBench retains the native paper metric calculations and silent-resolution correction. Its clarification ratios use the native case-script count definitions; the paper aggregator ratios are also retained because its recall can exceed one.',
 '', '## All attempts and recoveries','', '| Case | Batch | Status | Local trace (not in Git) |','|---|---|---|---|']
 for r in attempts:lines.append(f"| `{r['episode_id']}` | `{r['batch']}` | {r['status']} | `{r['trace']}` |")
 lines+=['','Trace paths above are local locators under ignored `runs/`, not GitHub links. Full raw model calls, shared dialogue, tool activity, sealed submissions and grader outputs remain locally beside each readable trace. No additional benchmark cases were run as a separate test suite.','']
 (OUT/'README.md').write_text('\n'.join(lines))
 print(json.dumps({'cases':len(ordered),'attempts':len(attempts),'report':str(OUT/'README.md')}))
if __name__=='__main__':main()
