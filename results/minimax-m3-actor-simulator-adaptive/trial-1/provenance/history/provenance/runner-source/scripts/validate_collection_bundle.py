#!/usr/bin/env python3
"""Validate collection export bytes, coverage and portable payload mappings."""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARMS=('persona_off','candidate_155','candidate_001','candidate_003','candidate_046')


def read(p):return json.loads(p.read_text())
def lines(p):
    opener=gzip.open if p.suffix=='.gz' else open
    with opener(p,'rt') as stream:
        return [json.loads(line) for line in stream if line.strip()]
def identity(row):return row['source'],row['task_id'],row['arm'],int(row.get('trial',1))


def validate(directory):
    directory=directory.resolve();manifest=read(directory/'bundle_manifest.json')
    def path(name):
        p=directory/name
        if Path(name).is_absolute() or '..' in Path(name).parts or p.is_symlink() or not p.resolve().is_relative_to(directory):
            raise ValueError(f'Unsafe exported path: {name}')
        if not p.is_file():raise ValueError(f'Missing exported file: {name}')
        return p
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name!='bundle_manifest.json'}
    if actual!=set(manifest['files']):raise ValueError('Manifest does not describe every exported file')
    for name,entry in manifest['files'].items():
        p=path(name);h=hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
        if p.stat().st_size!=entry['bytes'] or h.hexdigest()!=entry['sha256']:
            raise ValueError(f'File checksum/size mismatch: {name}')
    selection=list(csv.DictReader((ROOT/'configs/main_run/selection.csv').open()))
    expected={(r['source'],r['task_id'],arm,1) for r in selection for arm in ARMS}
    rows=list(csv.DictReader((directory/'episodes.csv').open()))
    def keyed(values,label):
        keys=[identity(r) for r in values]
        if len(keys)!=1000 or len(set(keys))!=1000 or set(keys)!=expected:
            raise ValueError(f'Invalid 1000-slot inventory: {label}')
        return dict(zip(keys,values))
    endpoints=keyed(rows,'episodes.csv')
    final=keyed(read(directory/'traces/final-results.json'),'final results')
    events=lines(directory/'traces/shared-events.jsonl');event_map=keyed(events,'shared events')
    index=keyed(list(csv.DictReader((directory/'traces/shared-events-index.csv').open())),'event index')
    metrics=keyed(lines(directory/'evaluations/metrics.jsonl'),'metrics')
    inputs=keyed(read(directory/'grading_inputs/manifest.json')['slots'],'grading inputs')
    for k,row in endpoints.items():
        attempt=int(row['selected_attempt'])
        if any(int(v)!=attempt for v in (final[k]['attempt'],event_map[k]['attempt'],index[k]['selected_attempt'],metrics[k]['attempt'],inputs[k]['selected_attempt'])):
            raise ValueError(f'Attempt identity mismatch: {k}')
        indexed=events[int(index[k]['jsonl_line'])-1]
        if identity(indexed)!=k or len(indexed['events'])!=int(index[k]['event_count']):
            raise ValueError(f'Event index mismatch: {k}')
        refs=json.loads(row['submission_manifest'])
        if refs!=inputs[k]['submission_paths'] or refs!=metrics[k]['submission_paths'] or refs!=final[k]['bundle_paths']['submissions']:
            raise ValueError(f'Submission mapping mismatch: {k}')
        if not (row['grading_input'] == inputs[k]['snapshot'] == metrics[k]['grading_input'] == final[k]['bundle_paths']['grading_input']):
            raise ValueError(f'Grading-input mapping mismatch: {k}')
        snapshot=read(path(row['grading_input']))
        if (snapshot.get('task_id') != k[1] if k[0]=='expbench' else snapshot.get('id') != k[0]+':'+k[1]):
            raise ValueError(f'Grading snapshot task identity mismatch: {k}')
        for ref in refs:
            submitted=read(path(ref))
            for artifact in submitted.get('artifacts',{}).values():path(artifact)
        if row['evaluation_status'] in ('grading_pending','execution_error') and (row['native_score'] or row['normalized_score']):
            raise ValueError('Pending/unavailable scores must be null')
    attempts=lines(directory/'repairs/all-attempts.jsonl.gz')
    seen=set();chosen={}
    for attempt in attempts:
        k=identity(attempt);ak=(*k,attempt['attempt'])
        if ak in seen:raise ValueError('Duplicate historical attempt')
        seen.add(ak);path(attempt['grading_input'])
        for ref in attempt['submission_paths']:
            submitted=read(path(ref))
            for artifact in submitted.get('artifacts',{}).values():path(artifact)
        if attempt['selected']:
            if k in chosen:raise ValueError('Multiple selected attempts')
            chosen[k]=attempt['attempt']
    if chosen!={k:int(row['selected_attempt']) for k,row in endpoints.items()}:
        raise ValueError('Selected attempts differ from history')
    if not all((*k,1) in seen for k in expected):raise ValueError('Missing original attempt')
    delivery=read(directory/'delivery.json');counts=dict(Counter(r['evaluation_status'] for r in rows))
    if delivery['selected_statuses']!=counts or delivery['attempts']!=len(attempts):raise ValueError('Delivery counts mismatch')
    if delivery['unresolved_execution_errors']!=counts.get('execution_error',0):raise ValueError('Execution error count mismatch')
    if delivery['status']=='complete_collection_grading_pending' and (counts.get('execution_error') or delivery.get('endpoint_snapshot_sha256')):
        raise ValueError('Incomplete checkpoint labeled complete')
    calls=lines(directory/'supporting/api-usage.jsonl.gz')
    if any(c['role']=='judge' for c in calls):raise ValueError('Unexpected judge calls')
    previous={}
    for call in calls:
        group=(*identity(call),call['attempt'],call['role'])
        repair=call.get('response_repair') or {}
        if repair.get('request_attempt',1)>1:
            prior=previous.get(group,{})
            prior_repair=prior.get('response_repair') or {}
            if (call.get('request_sha256') is None or call['request_sha256']!=prior.get('request_sha256')
                    or not prior_repair.get('retry_scheduled')
                    or repair['request_attempt']!=prior_repair.get('request_attempt',0)+1
                    or repair['request_attempt']>3):
                raise ValueError('Response repair changed its request or exceeded its bound')
        previous[group]=call
    return {'verified':True,'files':len(actual),'slots':len(rows),'attempts':len(attempts),'status':delivery['status'],'selected_statuses':counts,'bytes':sum(v['bytes'] for v in manifest['files'].values()),'api_records':len(calls)}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    print(json.dumps(validate(p.parse_args().directory),indent=2))
