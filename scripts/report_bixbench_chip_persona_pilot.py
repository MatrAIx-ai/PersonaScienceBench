#!/usr/bin/env python3
"""Summarize the BixBench CHIP persona pilot without model calls.

Native grades are reported unchanged. A separate deterministic range check reads
the first bold number in the submitted answer and compares it with the private
range key; it is a secondary analysis, not a replacement grade.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics as st

ROOT = Path(__file__).resolve().parents[1]
NUMBER = r'[-+]?\d[\d,]*\.?\d*'


def read(path):
    return json.loads(Path(path).read_text())


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def headline(answer, percentage=False):
    """Percentage questions: first number followed by %. Otherwise first bold number, else first number."""
    if percentage:
        found = re.findall('(' + NUMBER + r')\s*%', answer)
        return (float(found[0].replace(',', '')), 'first percentage') if found else (None, 'no percentage')
    bold = re.findall(r'\*\*[^*]*?(' + NUMBER + r')[^*]*?\*\*', answer)
    found = bold or re.findall(NUMBER, answer)
    if not found:
        return None, 'no number'
    return float(found[0].replace(',', '')), 'first bold number' if bold else 'first number'


def in_range(value, target):
    low, high = (float(x) for x in target.strip('()[] ').split(','))
    return value is not None and low <= value <= high


def episode(case, keys, questions):
    result = read(case / 'result.json')
    task = result['source_task_id']
    events = jsonl(case / 'controller/events.jsonl')
    calls = jsonl(case / 'controller/api_calls.private.jsonl')
    submission = read(case / 'controller/submission.json') if (case / 'controller/submission.json').exists() else {}
    answer = str(submission.get('answer', ''))
    percentage = 'percentage' in questions[task].lower()
    value, rule = headline(answer, percentage) if answer else (None, 'no submission')
    decisions = [e['payload'] for e in events if e['type'] == 'researcher_decision']
    replies = [d['message'] for d in decisions[1:]]  # exclude the initial request
    fact_ids = sorted({f for d in decisions for f in d.get('fact_ids', [])})
    collab = (result.get('actor') or {}).get('collaboration') or {}
    usage = [c.get('usage') or {} for c in calls]
    cjk = sum(len(re.findall(r'[一-鿿]', m)) for m in replies)
    grade = ((result.get('evaluation') or {}).get('metrics') or {}).get('grade')
    return {
        'task': task, 'status': result['status'], 'native_grade': grade,
        'answer_value': value, 'value_rule': rule, 'key': keys[task],
        'range_check': in_range(value, keys[task]) if value is not None else False,
        'researcher_requests': result.get('researcher_requests'),
        'approach_reviews': collab.get('plan_reviews'), 'result_reviews': collab.get('result_reviews'),
        'disclosed_facts': len(fact_ids), 'fact_ids': fact_ids,
        'approved_at': next((i for i, d in enumerate(decisions) if d.get('approve_approach')), None),
        'reply_chars_mean': round(st.mean(len(m) for m in replies), 1) if replies else 0,
        'reply_cjk_chars': cjk,
        'reply_cyrillic_chars': sum(len(re.findall(r'[Ѐ-ӿ]', m)) for m in replies),
        'actor_calls': (result.get('actor') or {}).get('actor_calls'),
        'execution_calls': (result.get('actor') or {}).get('execution_calls'),
        **{f'{role}_tokens': sum((c.get('usage') or {}).get('total_tokens', 0) or 0 for c in calls if c['role'] == role)
           for role in ('actor', 'researcher', 'judge')},
        'prompt_tokens': sum(u.get('prompt_tokens', 0) or 0 for u in usage),
        'completion_tokens': sum(u.get('completion_tokens', 0) or 0 for u in usage),
        'cost_usd': round(sum((u.get('cost', 0) or 0) + ((u.get('cost_details') or {}).get('upstream_inference_cost', 0) or 0)
                              for u in usage), 5),
        'elapsed_seconds': result.get('elapsed_seconds'),
        'answer_excerpt': answer[:240],
    }


def clip(text, limit=600):
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text if len(text) <= limit else text[:limit] + ' …'


def conversation(case):
    """Researcher decisions and actor handoffs only; judge prompts (which contain the reference) are excluded."""
    out = []
    for e in jsonl(case / 'controller/events.jsonl'):
        p = e['payload']
        if e['type'] == 'researcher_decision':
            out.append({'sequence': e['sequence'], 'type': 'researcher_decision', 'interaction': p['interaction'],
                        'approve_approach': p.get('approve_approach'), 'fact_ids': p.get('fact_ids', []),
                        'message': clip(p['message'])})
        elif e['type'] == 'agent_handoff':
            out.append({'sequence': e['sequence'], 'type': 'actor_handoff', 'stage': p.get('stage'),
                        'answer': clip(p.get('answer', ''))})
    return out


# Episodes cited in README; key = (arm, task, repeat).
CASES = [
    ('grader_false_negative', 'candidate_148', 'bix-2-q2', 1,
     'In-range answer graded incorrect by the native judge (README point 4).'),
    ('grader_false_negative', 'candidate_148', 'bix-7-q2', 3,
     'In-range answer graded incorrect by the native judge (README point 4).'),
    ('grader_same_answer_credited', 'persona_off', 'bix-2-q2', 2,
     'Identical headline value credited in persona off (README point 4).'),
    ('grader_same_answer_credited', 'persona_off', 'bix-7-q2', 1,
     'Identical headline value credited in persona off (README point 4).'),
    ('grader_false_positive', 'candidate_251', 'bix-2-q2', 1,
     'Out-of-range answer graded correct by the native judge (README point 4).'),
    ('actor_filter_accepted', 'candidate_148', 'bix-2-q2', 2,
     'Actor adds a heterozygous-only filter; the researcher restates and accepts it (README point 4).'),
    ('approval_flag_loop', 'candidate_155', 'bix-7-q2', 3,
     'Researcher prose says the plan is approved while approve_approach stays false (README point 5).'),
    ('actor_reading_failure', 'candidate_155', 'bix-2-q2', 3,
     'Actor concludes no usable VAF values exist (README point 1).'),
    ('actor_reading_failure', 'candidate_003', 'bix-2-q2', 3,
     'Actor concludes the workbooks are placeholder sheets (README point 1).'),
]


def case_evidence(run, rows):
    index = {(r['arm'], r['task'], r['rep']): r for r in rows}
    evidence = []
    for kind, arm, task, rep, note in CASES:
        r = index.get((arm, task, rep))
        if not r or r['status'] == 'pending':
            continue
        case = next((run / 'episodes' / f'{arm}-{task}-r{rep}').glob('*/'))
        evidence.append({'id': f'{task}--{arm}--r{rep}', 'kind': kind, 'note': note,
                         'native_grade': r['native_grade'], 'answer_value': r['answer_value'],
                         'range_check': r['range_check'], 'researcher_requests': r['researcher_requests'],
                         'events': conversation(case)})
    front = []
    for r in rows:
        if r['status'] != 'scored':
            continue
        case = next((run / 'episodes' / f"{r['arm']}-{r['task']}-r{r['rep']}").glob('*/'))
        decisions = [e['payload'] for e in jsonl(case / 'controller/events.jsonl') if e['type'] == 'researcher_decision']
        used = sorted({f for d in decisions for f in d.get('fact_ids', [])})
        front.append({'episode': f"{r['task']}--{r['arm']}--r{r['rep']}", 'facts_in_first_message': len(set(decisions[0].get('fact_ids', []))),
                      'facts_used_in_episode': len(used)})
    evidence.append({'id': 'first-message-disclosure', 'kind': 'fact_front_loading',
                     'note': 'Per scored episode: approved facts in the first researcher message vs all facts disclosed (README point 2).',
                     'episodes_all_facts_in_first_message': sum(f['facts_in_first_message'] == f['facts_used_in_episode'] for f in front),
                     'scored_episodes': len(front), 'per_episode': front})
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = read(args.run / 'manifest.json')
    keys, questions = {}, {}
    for task in manifest['tasks']:
        case = next((ROOT / 'prepared/bixbench-chip-persona').glob(f"bixbench_{task['slug']}-*"))
        reference = read(case / 'controller/evaluator.private.json')['reference']
        keys[task['slug']], questions[task['slug']] = reference['target'], reference['question']
    rows = []
    for job in manifest['jobs']:
        cases = list((args.run / 'episodes' / job['key']).glob('*/result.json'))
        if not cases:
            rows.append({'arm': job['arm'], 'rep': job['rep'], 'task': job['slug'], 'status': 'pending'})
            continue
        rows.append({'arm': job['arm'], 'rep': job['rep'], **episode(cases[0].parent, keys, questions)})
    rows.sort(key=lambda r: (manifest['arms'].index(r['arm']), r['task'], r['rep']))
    for r in rows:
        r.pop('key', None)  # private reference ranges stay out of published outputs
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    columns = [c for c in rows[0] if c != 'answer_excerpt'] if rows else []
    for r in rows:
        columns += [c for c in r if c not in columns and c != 'answer_excerpt']
    with (args.output / 'results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, 'fact_ids': ';'.join(r.get('fact_ids', []))})
    (args.output / 'case_evidence.json').write_text(
        json.dumps(case_evidence(args.run, rows), indent=2, ensure_ascii=False) + '\n')
    cells = []
    for arm in manifest['arms']:
        for task in [t['slug'] for t in manifest['tasks']]:
            scheduled = [r for r in rows if r['arm'] == arm and r['task'] == task]
            scored = [r for r in scheduled if r['status'] == 'scored']
            cells.append({'arm': arm, 'task': task, 'scheduled': len(scheduled), 'scored': len(scored),
                          'native_correct': sum(r['native_grade'] == 1 for r in scored),
                          'range_check_correct': sum(bool(r['range_check']) for r in scored),
                          **{f: [r[k] for r in scored] for f, k in [
                              ('answers', 'answer_value'), ('researcher_requests', 'researcher_requests'),
                              ('approach_reviews', 'approach_reviews'), ('result_reviews', 'result_reviews'),
                              ('disclosed_facts', 'disclosed_facts'), ('reply_chars_mean', 'reply_chars_mean'),
                              ('actor_tokens', 'actor_tokens'), ('researcher_tokens', 'researcher_tokens'),
                              ('elapsed_seconds', 'elapsed_seconds')]},
                          'cost_usd': round(sum(r['cost_usd'] for r in scored), 4)})
    retry = read(args.run / 'RETRY.json') if (args.run / 'RETRY.json').exists() else {}
    summary = {
        'version': manifest['version'], 'episodes_scheduled': len(rows),
        'status_counts': dict(Counter(r['status'] for r in rows)),
        'total_cost_usd_scored': round(sum(r['cost_usd'] for r in rows if r['status'] == 'scored'), 4),
        'cells': cells,
        'retries': {'attempt2_jobs': len(retry.get('jobs', [])),
                    'attempt3_jobs': len(retry.get('second_retry', {}).get('jobs', [])),
                    'reason': 'Infrastructure only (OpenRouter HTTP 402 after non-BYOK fallback exhausted a zero '
                              'credit balance; transport ReadError). No score-based reruns.'},
        'unresolved': [f"{r['arm']}-{r['task']}-r{r['rep']}" for r in rows if r['status'] != 'scored']}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    source = manifest['source_sha256']
    runtime = {
        'models': manifest['models'],
        'protocol': 'researcher-review-v2 (active_researcher, max 12 researcher requests, 60 actor steps)',
        'knowledge': manifest['knowledge'], 'injection': manifest['injection'],
        'persona_selection': manifest['persona_selection'],
        'persona_prompt_sha256': {arm: read(args.run / 'configs' / arm / 'persona.private.json').get('sha256')
                                  for arm in manifest['arms']},
        'tasks': [t['id'] for t in manifest['tasks']], 'repeats': manifest['repeats'], 'job_order_seed': 20260928,
        'source_sha256': {k: v for k, v in source.items() if not k.startswith('src/')},
        'src_tree_sha256': hashlib.sha256(json.dumps({k: v for k, v in source.items() if k.startswith('src/')},
                                                     sort_keys=True).encode()).hexdigest()}
    (args.output / 'runtime_config.json').write_text(json.dumps(runtime, indent=2) + '\n')
    print(json.dumps(summary['status_counts']), summary['total_cost_usd_scored'])


if __name__ == '__main__':
    main()
