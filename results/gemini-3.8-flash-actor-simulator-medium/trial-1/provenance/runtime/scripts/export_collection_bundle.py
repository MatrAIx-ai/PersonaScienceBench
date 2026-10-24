#!/usr/bin/env python3
"""Export a frozen collect-only run, preserving all attempts without model calls.

Refuses running/incomplete collections by default. --allow-partial creates an
explicit checkpoint, never a completed delivery. Does not commit or upload.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['persona_off', 'candidate_155', 'candidate_001', 'candidate_003', 'candidate_046']
SHARED = {'initial_request', 'researcher_decision', 'agent_handoff', 'researcher_question',
          'researcher_reply', 'final_specification', 'collaboration_budget_exhausted',
          'collaboration_missing_submission', 'collaboration_stopped'}
SHARED_FIELDS = {'message', 'question', 'answer', 'stage', 'interaction', 'phase', 'action',
                 'approve_approach', 'evidence', 'objectives_open', 'assumptions', 'uncertainties', 'reason'}
SECRET_PATTERN = re.compile(rb'(?:sk-(?:proj-|or-v1-)[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def key(source, task):
    text = source + ':' + task
    return (re.sub(r'[^A-Za-z0-9_.-]', '_', text).strip('.')[:100] or 'episode') + '-' + hashlib.sha256(text.encode()).hexdigest()[:12]


def shared_events(events):
    selected = []
    for i, event in enumerate(events):
        if event.get('type') not in SHARED:
            continue
        payload = {k: v for k, v in (event.get('payload') or {}).items() if k in SHARED_FIELDS}
        selected.append({**{k: v for k, v in event.items() if k in ('sequence', 'time', 'type', 'episode_id')},
                         'source_event_index': i, 'payload': payload})
    return selected


def scan_bytes(raw, secrets, name):
    if SECRET_PATTERN.search(raw) or any(secret in raw for secret in secrets):
        raise ValueError(f'Credential-like content detected; review locally: {name}')


def public_sdk_trace(trace):
    """Retain original scientific actions/observations, not SDK private reasoning."""
    if trace == 'No actor events recorded.':
        return trace
    private = {'thought', 'reasoning_content', 'thinking_blocks', 'responses_reasoning_item',
               'reasoning_details', 'critic_result', 'summary'}
    result = []
    for index, line in enumerate(trace.splitlines()):
        if not line.strip():continue
        event=json.loads(line)
        if event.get('kind')=='SystemPromptEvent':continue
        message=event.get('llm_message')
        if isinstance(message,dict) and message.get('role')=='system':continue
        event={k:v for k,v in event.items() if k not in private}
        event['source_event_index']=index
        if isinstance(message,dict):
            message={k:v for k,v in message.items() if k not in private}
            if isinstance(message.get('content'),list):
                message['content']=[v for v in message['content'] if not isinstance(v,dict) or v.get('type') not in ('thinking','reasoning','redacted_thinking')]
            event['llm_message']=message
        result.append(json.dumps(event,ensure_ascii=False))
    return '\n'.join(result) + ('\n' if result else '')


def copy_checked(source, target):
    if source.is_symlink() or not source.is_file():
        raise ValueError(f'Expected regular non-symlink input: {source}')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def csv_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def disposition(native, runner_status):
    status = native.get('status')
    if runner_status == 'infrastructure_error' and status not in ('no_submission', 'missing_submission'):
        return 'execution_error', None, 'Unresolved actor/simulator execution failure'
    if status in ('missing_submission', 'no_submission'):
        return 'missing_submission', None, 'No scientific submission; preserve native zero-score convention for receiving analysis'
    return 'grading_pending', None, 'Final native/Astra grading deferred; no judge calls during collection'


def export(run, output, *, allow_partial=False, secrets=(), snapshot=None):
    run, output = run.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Refusing to overwrite an existing export')
    if snapshot is not None and not allow_partial:
        raise ValueError('Snapshot exports are partial checkpoints; use --allow-partial')
    rows = read(snapshot) if snapshot is not None else [read(p) for p in sorted((run/'episodes').glob('*/*/state.json'))]
    selection = list(csv.DictReader((ROOT/'configs/main_run/selection.csv').open()))
    expected = {(r['source'], r['task_id'], arm) for r in selection for arm in ARMS}
    actual = [(r['source'], r['task_id'], r['arm']) for r in rows]
    if len(actual) != 1000 or len(set(actual)) != 1000 or set(actual) != expected:
        raise ValueError('Expected the exact 1,000 frozen slots')
    if any(r['status'] == 'running' for r in rows):
        raise ValueError('Wait for the coordinator to stop before exporting')
    manifest = read(run/'manifest.json')
    if manifest.get('collect_only') is not True:
        raise ValueError('This exporter currently requires explicitly collect-only results')
    if sha(run/'selection.csv') != sha(ROOT/'configs/main_run/selection.csv'):
        raise ValueError('Run selection differs from the frozen selection')
    failures = [r for r in rows if disposition(r['native_results'][0], r['status'])[0] == 'execution_error']
    if failures and not allow_partial:
        raise ValueError(f'{len(failures)} unresolved execution failures; not a completed collection')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.collection-export-', dir=output.parent))
    replacements = {str(run): '@RAW_RUN', str(ROOT): '@SOURCE_REPOSITORY'}
    source_receipts = []
    def portable(value):
        if isinstance(value, str):
            for old, new in replacements.items(): value = value.replace(old, new)
            return value
        if isinstance(value, list): return [portable(v) for v in value]
        if isinstance(value, dict): return {k: portable(v) for k, v in value.items()}
        return value
    def save_json(relative, value): write(staging/relative, portable(value))
    def receipt(path):
        source_receipts.append({'raw_source':portable(str(path.resolve())), 'sha256':sha(path), 'bytes':path.stat().st_size})
    def jsonlines(path):
        with path.open() as stream:
            for line in stream:
                if line.strip(): yield json.loads(line)
    def gzlines(relative, records):
        path=staging/relative;path.parent.mkdir(parents=True,exist_ok=True)
        # Deterministic gzip header avoids host filenames/timestamps in exports.
        with path.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as gz:
            for record in records:
                data=(json.dumps(portable(record),ensure_ascii=False)+'\n').encode()
                scan_bytes(data,secrets,relative);gz.write(data)
    attempt_records=[]; endpoint_rows=[]; final_records=[]; event_rows=[]; event_index=[]; metrics=[]; usage_records=[]; tool_records=[]; input_map=[]
    try:
        for row in rows:
            source, task, arm = row['source'], row['task_id'], row['arm']
            task_key = key(source, task)
            slot = {'source':source,'task_id':task,'study_id':row.get('study_id'),'family':row.get('family'),'arm':arm,'trial':1}
            base = run/'episodes'/task_key/arm
            attempts = sorted(base.glob('attempt-*'), key=lambda p:int(p.name.split('-')[-1]))
            if snapshot is not None:
                attempts = [p for p in attempts if int(p.name.split('-')[-1]) <= row['attempt']]
            selected_record = None
            for attempt_dir in attempts:
                attempt=int(attempt_dir.name.split('-')[-1]); selected=attempt==row['attempt']
                case=attempt_dir/'output'/(task.replace('/','__') if source=='expbench' else task_key)
                controller=case if source=='expbench' else case/'controller'
                native_path=case/'result.json'
                if not native_path.is_file():
                    raise ValueError(f'Missing attempt result: {native_path}')
                native=read(native_path);receipt(native_path)
                if selected and native != row['native_results'][0]:
                    raise ValueError(f'Selected state/native mismatch: {case}')
                aid=f'{task_key}/{arm}/attempt-{attempt}'
                events_path=controller/'events.jsonl'
                if not events_path.is_file():raise ValueError(f'Missing recorded events: {events_path}')
                all_events=list(jsonlines(events_path));events=shared_events(all_events);receipt(events_path)
                task_snapshot=controller/('task_snapshot.private.json' if source=='expbench' else 'episode.private.json')
                if not task_snapshot.is_file():raise ValueError(f'Missing grading snapshot: {task_snapshot}')
                snapshot_out=f'grading_inputs/task_snapshots/{task_key}.json'
                snapshot_value=portable(read(task_snapshot))
                prior=staging/snapshot_out
                if prior.exists() and read(prior)!=snapshot_value:
                    raise ValueError(f'Task inputs changed across attempts/arms: {task_key}')
                save_json(snapshot_out,snapshot_value)
                receipt(task_snapshot)
                submission_refs=[]
                if source=='expbench':
                    for name in ('initial_design.json','final_design.json'):
                        p=case/name
                        if p.is_file():
                            checkpoint=read(p)
                            checkpoint['trace']=public_sdk_trace(checkpoint.get('trace',''))
                            checkpoint['export_trace_policy']='SDK private reasoning/system prompts removed; original scientific actions and observations retained. Raw checkpoint checksum is in provenance/raw-file-receipts.json.'
                            rel=f'submissions/{aid}/{name}';save_json(rel,checkpoint);receipt(p);submission_refs.append(rel)
                else:
                    p=controller/'submission.json'
                    if p.is_file():
                        submitted=read(p);hashes=read(controller/'submission_hashes.json') if submitted.get('artifacts') else {}
                        mapped={}
                        for name, original in submitted.get('artifacts',{}).items():
                            original=Path(original)
                            if not original.resolve().is_relative_to((controller/'submitted_artifacts').resolve()):
                                raise ValueError('Submitted artifact is outside sealed controller storage')
                            digest=sha(original)
                            if hashes.get(name)!=digest:raise ValueError(f'Submission artifact hash mismatch: {original}')
                            suffix=original.suffix if re.fullmatch(r'\.[A-Za-z0-9]{1,10}',original.suffix) else ''
                            rel=f'submissions/files/{digest}{suffix}'
                            if not (staging/rel).exists():copy_checked(original,staging/rel)
                            mapped[name]=rel;receipt(original)
                        submitted['artifacts']=mapped
                        rel=f'submissions/{aid}/submission.json';save_json(rel,submitted);receipt(p);submission_refs.append(rel)
                api_path=controller/('api_calls.jsonl' if source=='expbench' else 'api_calls.private.jsonl')
                if api_path.is_file():
                    receipt(api_path)
                    for i, call in enumerate(jsonlines(api_path)):
                        request=call.get('request',call.get('payload',{})); response=call.get('response',{})
                        usage_records.append({**slot,'attempt':attempt,'api_record_index':i,'role':call.get('role'),'model':call.get('model',request.get('model')),'usage':call.get('usage',response.get('usage',{})), 'response_id':response.get('id'),'finish_reasons':[c.get('finish_reason') for c in response.get('choices',[])], 'settings':{k:request[k] for k in ('model','max_tokens','reasoning_effort','reasoning','temperature','top_p') if k in request},'request_sha256':hashlib.sha256(json.dumps(request,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'response_repair':call.get('response_repair'),'raw_log_sha256':source_receipts[-1]['sha256']})
                for i,e in enumerate(all_events):
                    if e.get('type') in ('actor_command','actor_command_result'):
                        tool_records.append({**slot,'attempt':attempt,'source_event_index':i,**e})
                attempt_record={**slot,'attempt':attempt,'selected':selected,'native_result':native,'shared_events':events,'empty_conversation_reason':None if events else native.get('actor',{}).get('error','No shared events were produced'),'submission_paths':submission_refs,'grading_input':snapshot_out,'source_events_sha256':sha(events_path)}
                attempt_records.append(attempt_record)
                if selected:
                    selected_record=attempt_record
                    state,score,reason=disposition(native,row['status'])
                    evaluation=native.get('evaluation') or {'status':state,'metrics':{},'score':score,'details':{'reason':reason}}
                    metrics.append({**slot,'attempt':attempt,'disposition':state,'evaluation':evaluation,'intended_judge':manifest['role_models']['judge'],'grading_input':snapshot_out,'submission_paths':submission_refs})
                    rec={**slot,'selected_attempt':attempt,'runner_status':row['status'],'native_status':native['status'],'evaluation_status':state,'submitted':bool(submission_refs),'native_score':None,'normalized_score':None,'exclusion_reason':reason,'termination':native.get('collaboration_termination',native.get('actor',{}).get('collaboration',{}).get('termination','native_end')),'actor_calls':native.get('actor_calls',native.get('actor',{}).get('actor_calls')),'researcher_questions':native.get('researcher_questions'),'researcher_requests':native.get('researcher_requests'),'submission_manifest':json.dumps(submission_refs),'grading_input':snapshot_out}
                    endpoint_rows.append(rec)
                    event_rows.append({**slot,'attempt':attempt,'events':events,'empty_reason':attempt_record['empty_conversation_reason']})
                    event_index.append({**slot,'selected_attempt':attempt,'jsonl_line':len(event_rows),'event_count':len(events),'source_sha256':sha(events_path)})
                    final_records.append({**row,'bundle_paths':{'submissions':submission_refs,'grading_input':snapshot_out,'events_line':len(event_rows)},'grading_disposition':state})
                    input_map.append({**slot,'selected_attempt':attempt,'snapshot':snapshot_out,'restored_prepared_package':f'prepared/{task_key}','frozen_preparation_id':'astra-20260929-v1','submission_paths':submission_refs})
            if selected_record is None:raise ValueError(f'Missing selected attempt: {base}')
        csv_write(staging/'episodes.csv',portable(endpoint_rows))
        csv_write(staging/'traces/shared-events-index.csv',event_index)
        save_json('traces/final-results.json',final_records)
        for relative, records in [('traces/shared-events.jsonl',event_rows),('evaluations/metrics.jsonl',metrics)]:
            path=staging/relative;path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('w') as stream:
                for r in records:stream.write(json.dumps(portable(r),ensure_ascii=False)+'\n')
        gzlines('repairs/all-attempts.jsonl.gz',attempt_records)
        gzlines('supporting/api-usage.jsonl.gz',usage_records)
        gzlines('supporting/tool-actions.jsonl.gz',tool_records)
        save_json('grading_inputs/manifest.json',{'path_base':'All submission and snapshot paths are relative to this bundle root.','source_path_placeholder':'@SOURCE_REPOSITORY is the receiving repository root after pinned public asset acquisition. @RAW_RUN is provenance only; the bundle_paths fields identify delivered equivalents.','restoration':'Run the shipped scripts/restore_main_preparation.py with --bundle pointing at grading_inputs/frozen and a new --run-dir. Acquire pinned assets with scripts/setup_main.sh first. No extraction or actor calls are needed.','slots':input_map})
        for folder in ('src','scripts','configs','manifests','tests'):
            for p in sorted((ROOT/folder).rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and not p.name.endswith('.local.json'):
                    copy_checked(p,staging/'provenance/runtime'/p.relative_to(ROOT))
        for name in ('pyproject.toml','uv.lock','README.md','docs/TEAM_HANDOFF.md','docs/NVIDIA_RUN.md'):
            copy_checked(ROOT/name,staging/'provenance/runtime'/name)
        shutil.copytree(ROOT/'configs/main_run/frozen/astra-20260929-v1',staging/'grading_inputs/frozen')
        for p in sorted(run.glob('*.json')):
            save_json('provenance/run/'+p.name,read(p));receipt(p)
        for p in sorted((run/'configs').glob('*.json')):save_json('provenance/run/configs/'+p.name,read(p))
        for folder in ('provenance','repairs'):
            for p in sorted((run/folder).rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.json','.patch','.py','.md','.sh','.toml','.lock','.example'):
                    dest=staging/'provenance/history'/p.relative_to(run)
                    if p.suffix=='.json':write(dest,portable(read(p)))
                    else:copy_checked(p,dest)
        copy_checked(run/'selection.csv',staging/'provenance/selection.csv')
        save_json('provenance/raw-file-receipts.json',source_receipts)
        save_json('provenance/export-policy.json',{'shared_event_types':sorted(SHARED),'shared_payload_fields':sorted(SHARED_FIELDS),'raw_api_payloads_exported':False,'private_reasoning_exported_in_public_conversations':False,'exp_checkpoint_sdk_trace':'Private reasoning and system-prompt records removed; scientific actions/observations preserved','path_replacements':portable(replacements),'credential_scan':'Exact configured API keys and common token patterns; scans decompressed gzip records too.','artifact_bytes':'Sealed submission artifacts copied without modification and verified against submission hashes.','selection_policy':'Latest explicitly authorized attempt, not best score. Every original/repair attempt is retained in repairs/all-attempts.jsonl.gz and corresponding submissions.','missing_submission_policy':'No fabricated grade. Receiving native analysis applies documented scientific zero conventions.'})
        counts=dict(Counter(r['evaluation_status'] for r in endpoint_rows))
        delivery={'schema_version':1,'expected_slots':1000,'status':'partial_collection_checkpoint' if failures or snapshot is not None else 'complete_collection_grading_pending','created_at':datetime.now(timezone.utc).isoformat(),'selected_statuses':counts,'attempts':len(attempt_records),'unresolved_execution_errors':len(failures),'judge_calls':sum(1 for c in usage_records if c['role']=='judge'),'runtime_git_commit':read(run/'provenance/checkout.json')['git_commit'],'ready_to_publish':not failures and snapshot is None,'endpoint_snapshot_sha256':sha(snapshot) if snapshot is not None else None}
        if delivery['judge_calls']:raise ValueError('Unexpected judge calls in collect-only collection')
        save_json('delivery.json',delivery)
        text=f'''# Gemini 3.8 Flash actor / simulator, medium — trial 1

Status: **{delivery['status']}**. All 1,000 frozen slots are indexed. Selected
dispositions: `{json.dumps(counts)}`. There are {len(attempt_records)} retained
attempts, including originals and explicitly authorized repairs. Judge calls: 0.

Actor and researcher simulator: `gcp/google/gemini-3.8-flash`, NVIDIA gateway,
`reasoning_effort=medium`. Final judge: GPT-6 Astra / low, **deferred**.
The gateway's advertised deployment/accounting-model discrepancy is preserved in
`provenance/run/api_access.json`; the requested model ID has not been relabeled.
One trial: 200 questions, 40 per benchmark, off / 155 / 001 / 003 / 046.
Actual protocol/configs and limits are in `provenance/run/configs/`.

## Commands and provenance

Original: `ENV_FILE=/path/to/.env WORKERS=4 bash scripts/run_gemini_nvidia.sh`.
Repairs: same command plus `--retry-infrastructure`. Retry 2 additionally sets
`PSB_NVIDIA_EMPTY_LENGTH_RETRIES=2`: at most two identical-request replays for
empty actor `length` replies below the requested output cap; every response and
usage is logged. Content filters/refusals are not automatically retried.
See the exact repair selections and source snapshots in `provenance/history/`.
The first repair intentionally included four EXP non-submissions that the
coordinator had labeled infrastructure failures. This scientific-outcome repair
is distinguished from technical repairs; the other missing outcomes were retained.
Original-only paper analysis must read attempt 1 from `repairs/all-attempts.jsonl.gz`;
selected endpoints use the latest authorized attempt, never the highest score.

## Files and paths

`episodes.csv`, `traces/final-results.json`, `traces/shared-events.jsonl`, and its
index map every selected slot to an attempt, original shared exchanges, grading
input, and submitted files. `repairs/all-attempts.jsonl.gz` retains all attempts.
Shared conversations exclude private reasoning, tool output and evaluator keys.
`supporting/` retains token accounting (including failed-response repair calls)
and tool actions. Raw authenticated API request payloads are not published.

All explicit `submission_paths`, `artifacts`, and `grading_input` entries are
relative to this bundle's root. Native provenance strings use `@RAW_RUN` or
`@SOURCE_REPOSITORY`; those are not payload download links. Sealed artifact bytes
are content-addressed under `submissions/files/`. EXP design checkpoints retain
initial/final labels as recorded; a nonexistent final design is not invented.
Their embedded SDK traces omit private reasoning and system-prompt records,
while preserving original scientific actions and observations with source indices.

`grading_inputs/task_snapshots/` contains controller-only facts/evaluator data;
keep it private to the receiving grading team and out of actor mounts. This
bundle is prepared for the existing team repository, not a public dataset release.
The frozen metadata bundle is included in `grading_inputs/frozen/`. Public
source/data dependencies have pinned download routes and hashes in its manifest,
source manifests and acquisition scripts; virtual environments and downloaded
input copies are excluded. On the receiving host, install the recorded runtime
and acquire pinned public assets, then restore the frozen bundle with:

```bash
.venv/bin/python scripts/restore_main_preparation.py --bundle /path/to/this/bundle/grading_inputs/frozen --run-dir /path/to/new/reference-run
```

Replace `@SOURCE_REPOSITORY` in task snapshot path fields with that receiving
checkout root. A native grader should load the listed snapshot and submission,
resolving artifact values relative to this bundle root. Every input/output is
mapped in `grading_inputs/manifest.json`. No actor/simulator rerun is required.
ASI reference directories use pinned acquisition and presence checks where the
historical bundle lacked tree hashes; that source limitation is preserved.

## Grading and validation

Scores remain null until the receiving team performs native/Astra grading.
Scientific non-submissions follow native zero conventions; execution errors are
unavailable, not zeros. The receiving team computes the four separate scorecard
columns and CIs using the repository handoff definitions; no aggregate score is
claimed here. Repetition uses original shared actor text; SciConv fact recovery
requires pending native evaluation with the preserved task facts.

Verify every path/size/SHA-256 in `bundle_manifest.json` and all 1,000 slot keys.
`delivery.json` records any unresolved execution errors. A partial checkpoint
must never be labeled a completed collection. All files are included directly;
`.gz` files are standard gzip streams, not missing external payloads.
'''
        (staging/'README.md').write_text(text)
        (staging/'.gitattributes').write_text('* -text\n')
        # Audit every delivered byte, including code snapshots and compressed data.
        files={}
        for p in sorted(staging.rglob('*')):
            if not p.is_file():continue
            raw=p.read_bytes();scan_bytes(raw,secrets,str(p.relative_to(staging)))
            if p.suffix=='.gz':scan_bytes(gzip.decompress(raw),secrets,str(p.relative_to(staging)))
            if len(raw)>50*1024*1024:raise ValueError(f'Artifact needs reviewed compression/sharding: {p}')
            files[str(p.relative_to(staging))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        write(staging/'bundle_manifest.json',{'schema_version':1,'files':files})
        staging.rename(output)
        return delivery
    finally:
        if staging.exists():shutil.rmtree(staging)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--allow-partial',action='store_true');p.add_argument('--env-file',type=Path)
    p.add_argument('--endpoint-snapshot',type=Path,help='Immutable prior results for an explicitly partial checkpoint')
    a=p.parse_args()
    if a.env_file:
        from personasciencebench.inference import load_env
        load_env(a.env_file)
    secrets=tuple(v.encode() for k,v in os.environ.items() if k in ('NVIDIA_API_KEY','OPENAI_API_KEY','OPENROUTER_API_KEY') and v)
    import fcntl
    if a.endpoint_snapshot is not None:
        result=export(a.run_dir,a.output,allow_partial=a.allow_partial,secrets=secrets,snapshot=a.endpoint_snapshot)
    else:
        with (a.run_dir/'coordinator.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
            result=export(a.run_dir,a.output,allow_partial=a.allow_partial,secrets=secrets)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
