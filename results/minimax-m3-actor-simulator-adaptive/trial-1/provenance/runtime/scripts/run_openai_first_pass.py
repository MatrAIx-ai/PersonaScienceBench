#!/usr/bin/env python3
"""Run the frozen 200-task, configurable-condition first pass. No smoke/test episodes."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import fcntl

ROOT = Path(__file__).resolve().parents[1]
ARMS = ['persona_off', 'candidate_148', 'candidate_046', 'candidate_155', 'candidate_228', 'candidate_137', 'candidate_089', 'candidate_003', 'candidate_004', 'candidate_001', 'candidate_127', 'candidate_262', 'candidate_224', 'candidate_026']
PYTHON = ROOT / '.venv/bin/python'


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_models(model, effort, actor_model=None, actor_effort=None,
                researcher_model=None, researcher_effort=None):
    roles = {r: {'model': model, 'provider': 'openai', 'reasoning_effort': effort}
             for r in ('actor', 'researcher', 'judge')}
    if actor_model:
        roles['actor']['model'] = actor_model
    if actor_effort:
        roles['actor']['reasoning_effort'] = actor_effort
    if researcher_model:
        roles['researcher']['model'] = researcher_model
    if researcher_effort:
        roles['researcher']['reasoning_effort'] = researcher_effort
    return roles


def load_native_result(output, source, task_id, key):
    # Only read the harness result, never actor-created result.json artifacts.
    path = output / (task_id.replace('/', '__') if source == 'expbench' else key) / 'result.json'
    if not path.exists():
        return []
    result = json.loads(path.read_text())
    if not isinstance(result, dict):
        raise ValueError(f'Native result must be an object: {path}')
    expected = result.get('task_id') if source == 'expbench' else result.get('source_task_id')
    if expected != task_id:
        raise ValueError(f'Native result task does not match {task_id}')
    return [result]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--selection', type=Path, default=ROOT/'reports/conversion_v2/superfamily_audit/diagnostic_plots_allowed.random_sample.csv')
    p.add_argument('--arms', nargs='+', choices=ARMS, default=['persona_off', 'candidate_148', 'candidate_155'])
    p.add_argument('--baseline-run', type=Path, help='Existing matching trial supplying persona-off; allows persona-only expansion batches')
    p.add_argument('--workers', type=int, default=30)
    p.add_argument('--model', default='gpt-6-astra')
    p.add_argument('--reasoning-effort', default='low')
    p.add_argument('--actor-model', help='Override only the actor; keep researcher/judge on --model')
    p.add_argument('--actor-reasoning-effort', help='Override only actor reasoning')
    p.add_argument('--researcher-model', help='Override the researcher simulator model')
    p.add_argument('--researcher-reasoning-effort', help='Override researcher simulator reasoning')
    p.add_argument('--require-prepared', action='store_true', help='Require frozen prepared tasks; never regenerate source conversions')
    p.add_argument('--retry-infrastructure', action='store_true')
    p.add_argument('--retry-missing', action='store_true', help='Retry missing submissions; retain earlier attempts and report this as a repair pass')
    a = p.parse_args()
    models = role_models(a.model, a.reasoning_effort, a.actor_model, a.actor_reasoning_effort,
                         a.researcher_model, a.researcher_reasoning_effort)
    arms = a.arms
    if len(arms) != len(set(arms)) or ("persona_off" not in arms and a.baseline_run is None):
        raise ValueError("Choose unique conditions and include persona_off or supply --baseline-run")
    if "persona_off" in arms and a.baseline_run is not None:
        raise ValueError("Choose a new baseline or an existing baseline, not both")
    os.chdir(ROOT)
    os.umask(0o077)
    if not 1 <= a.workers <= int(os.environ.get('SLURM_CPUS_PER_TASK', '30')):
        raise ValueError('Workers must fit the CPU allocation')
    run = a.run_dir.resolve(); run.mkdir(parents=True, exist_ok=True)
    lock = (run/'coordinator.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.environ['PSB_FATAL_API_FILE'] = str(run/'fatal_api.json')
    from personasciencebench.inference import load_env, preflight
    load_env(ROOT/'.env')
    rows = list(csv.DictReader(a.selection.open()))
    counts = Counter(r['source'] for r in rows)
    if len(rows) != 200 or set(counts.values()) != {40} or len(counts) != 5 or len({(r['source'],r['task_id']) for r in rows}) != 200:
        raise ValueError('Expected 200 unique tasks: 40 per source')
    identity = {'model': a.model, 'provider': 'openai', 'reasoning_effort': a.reasoning_effort,
                'selection_sha256': digest(a.selection), 'arms': arms, 'episode_repeats': 1,
                'task_count':200, 'episode_count':len(rows)*len(arms), 'source_counts':dict(counts)}
    if a.actor_model or a.actor_reasoning_effort or a.researcher_model or a.researcher_reasoning_effort:
        identity['role_models'] = models
    if a.baseline_run is not None:
        a.baseline_run = a.baseline_run.resolve()
        baseline = json.loads((a.baseline_run/'manifest.json').read_text())
        if 'persona_off' not in baseline['arms'] or any(baseline[k] != identity[k] for k in ('model','provider','reasoning_effort','selection_sha256','task_count','source_counts')):
            raise ValueError('External baseline does not match the model, reasoning, or frozen task panel')
        baseline_models = baseline.get('role_models') or role_models(baseline['model'], baseline['reasoning_effort'])
        if baseline_models != models:
            raise ValueError('External baseline uses different role models')
        identity['baseline_run'] = str(a.baseline_run)
    if (run/'manifest.json').exists():
        if json.loads((run/'manifest.json').read_text()) != identity:
            raise ValueError('Run identity changed; use a new run directory')
    else:
        write(run/'manifest.json', identity)
        (run/'selection.csv').write_bytes(a.selection.read_bytes())
    model = {'model':a.model, 'provider':'openai', 'reasoning_effort':a.reasoning_effort}
    write(run/'api_access.json', preflight(models))
    if (run/'fatal_api.json').exists():
        raise RuntimeError('Resolve fatal_api.json before resuming')
    for arm in arms:
        persona = {'enabled':False} if arm == 'persona_off' else {'enabled':True, 'id':arm, 'system_prompt':(ROOT/f'data/persona_case_study/full_persona_v2/prompts/{arm}.md').read_text()}
        for kind in ('shared','exp'):
            config = json.loads((ROOT/f'configs/full_persona_v2/{kind}.json').read_text())
            config['persona'] = persona
            for role, spec in config['models'].items():
                spec.update(models[role])
                if kind == 'exp':
                    prices = {'gpt-6-astra': (10, 50), 'gpt-5.6-sol': (4, 20)}
                    if spec['model'] not in prices:
                        raise ValueError(f"Set verified EXP accounting prices for {spec['model']}")
                    input_price, output_price = prices[spec['model']]
                    spec.update(input_usd_per_million=input_price, output_usd_per_million=output_price)
                else:
                    spec['timeout'] = 600
            if kind == 'exp':
                config['limits']['request_timeout_seconds'] = 600
            else:
                config['notes'] = [f'Frozen 200-task first pass: 40 per source, {len(arms)} conditions, one episode each.']
            if a.baseline_run is not None:
                baseline_config = json.loads((a.baseline_run/'configs'/f'persona_off.{kind}.json').read_text())
                comparable = lambda c: {k:v for k,v in c.items() if k not in ('persona','notes')}
                if comparable(config) != comparable(baseline_config):
                    raise ValueError('Expansion configuration differs from its paired baseline')
            path = run/'configs'/f'{arm}.{kind}.json'
            if path.exists() and json.loads(path.read_text()) != config:
                raise ValueError('Configuration changed since run creation')
            write(path, config)
    # Freeze implementation hashes separately per submission for debugging provenance.
    write(run/f'code.{os.environ.get("SLURM_JOB_ID", str(time.time_ns()))}.json',
          {str(p.relative_to(ROOT)):digest(p) for folder in ('src','scripts') for p in (ROOT/folder).rglob('*.py')})
    from personasciencebench.registry import load_adapter
    from personasciencebench.packaging import export_episode, safe_component
    adapters = {name:load_adapter(name,ROOT/'external/sources',ROOT/'manifests/sources.json') for name in counts if name != 'expbench'}
    raw = {r['task_id']:r for r in map(json.loads,(ROOT/'data/exp_bench/tasks.jsonl').read_text().splitlines())}
    spec = importlib.util.spec_from_file_location('design_builder', ROOT/'scripts/expbench/build_full_design_catalog.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    from expbench.context_conversion import extract
    source_hash = digest(ROOT/'data/exp_bench/tasks.jsonl')

    def prepare(row):
        tid, source = row['task_id'], row['source']
        key = safe_component(source+':'+tid)
        prepared = run/'prepared'/key
        required = prepared/('tasks.jsonl' if source == 'expbench' else 'pilot_manifest.json')
        if a.require_prepared and not required.exists():
            raise ValueError(f'Frozen preparation missing: {required}')
        if source == 'expbench':
            path = prepared/'tasks.jsonl'
            if not path.exists():
                facts = extract(raw[tid], ROOT, {**model,'max_tokens':8192,'timeout':600})
                card = builder.build_card(raw[tid],facts,source_hash)
                prepared.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps(card)+'\n')
        elif not (prepared/'pilot_manifest.json').exists():
            prepared.mkdir(parents=True,exist_ok=True)
            episode = adapters[source].convert(tid)
            record = export_episode(episode, prepared/safe_component(episode.id))
            if not record['assets_ready']:
                raise ValueError(f'Missing assets: {record.get("missing")}')
            write(prepared/'pilot_manifest.json', {'schema_version':'0.1','source_root':str(ROOT/'external/sources'), 'source_manifest':str(ROOT/'manifests/sources.json'),'cases':[record],'cases_per_benchmark':1,'scientific_runs_started':False,'runtime_tested':False})
        return key, prepared

    # Prepare only the selected cohort; failures stay visible, never resample.
    prepared_tasks = {}
    failures = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = {pool.submit(prepare,row):row for row in rows}
        for future in as_completed(futures):
            row = futures[future]
            try:
                prepared_tasks[(row['source'],row['task_id'])] = future.result()
            except Exception as exc:
                failures.append({**row,'error':str(exc),'status':'preparation_error'})
                print('Preparation failed:',row['source'],row['task_id'],str(exc),flush=True)
    write(run/'preparation_errors.json', failures)
    print(f'Prepared {len(prepared_tasks)}/200 tasks; starting actual episodes',flush=True)
    jobs = [(row,arm) for row in rows for arm in arms if (row['source'],row['task_id']) in prepared_tasks]
    random.Random(20260929).shuffle(jobs)

    def one(job):
        row, arm = job; source = row['source']
        key, prepared = prepared_tasks[(source,row['task_id'])]
        base = run/'episodes'/key/arm
        state = base/'state.json'
        if state.exists():
            old = json.loads(state.read_text())
            missing = any(r.get('status') == 'missing_submission' for r in old.get('native_results', []))
            retry = (old['status'] == 'running'
                     or (old['status'] == 'infrastructure_error' and a.retry_infrastructure)
                     or (missing and a.retry_missing))
            if not retry:
                return old
        base.mkdir(parents=True,exist_ok=True)
        attempt = 1
        while (base/f'attempt-{attempt}').exists(): attempt += 1
        out = base/f'attempt-{attempt}'; out.mkdir()
        result = {**row,'arm':arm,'attempt':attempt,'status':'running','started_at':time.time()}
        write(state,result)
        output = out/'output'
        config = run/'configs'/f'{arm}.{"exp" if source=="expbench" else "shared"}.json'
        if source == 'expbench':
            cmd = [str(PYTHON),'-m','expbench.realistic','run','--mode','live','--tasks',str(prepared/'tasks.jsonl'),'--config',str(config),'--output',str(output),'--env-file',str(ROOT/'.env'),'--parallel','1']
        elif source == 'sciconvbench':
            cmd = [str(PYTHON),'-m','personasciencebench.sciconv_runner','--prepared',str(prepared),'--output',str(output),'--config',str(config),'--parallel','1']
        else:
            cmd = [str(PYTHON),'-m','personasciencebench.cli','--source-root',str(ROOT/'external/sources'),'run','--prepared',str(prepared),'--benchmarks',source,'--output',str(output),'--actor-python',str(ROOT/'.actor-venv'),'--config',str(config),'--parallel','1']
        if (run/'fatal_api.json').exists():
            result.update(status='infrastructure_error',error='Fatal API error stopped further episodes')
        else:
            with (out/'process.log').open('w') as log:
                proc = subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
            try:
                native = load_native_result(output, source, row['task_id'], key)
            except (ValueError, OSError) as exc:
                native = []
                result['result_read_error'] = str(exc)
            result.update(returncode=proc.returncode,native_results=native,
                          status='infrastructure_error' if proc.returncode or not native or any(r.get('status') in ('infrastructure_error','runtime_error','error') for r in native) else 'finished')
        result['finished_at'] = time.time(); write(state,result)
        print(f'{source} {key} {arm}: {result["status"]}',flush=True)
        return result

    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(one,j) for j in jobs]
        for future in as_completed(futures):
            results.append(future.result())
            write(run/'progress.json', {'planned':len(rows)*len(arms),'preparation_failed_episodes':len(arms)*len(failures), 'processed':len(results),'statuses':dict(Counter(r['status'] for r in results)),'updated_at':time.time()})
    write(run/'results.json',results)
    if failures or any(r['status']=='infrastructure_error' for r in results):
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
