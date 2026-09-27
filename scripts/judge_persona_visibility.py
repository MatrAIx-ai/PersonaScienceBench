#!/usr/bin/env python3
"""Blind match-to-sample: can a judge tell, from the researcher's words alone, which profile it was given?

Persona and twin episodes are judged against their own profile plus k-1 cohort distractors; neutral
episodes against k random cohort profiles, which shows the judge's bias when no profile is correct.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from math import comb
from pathlib import Path
import random
import string
import sys
import threading

from personasciencebench.arms import NEUTRAL, PERSONA, TWIN, arm_kind, twin_of
from personasciencebench.run_io import (BudgetExhausted, JudgeCaller, is_verbatim, jsonl, load_run, model_spec,
                                        profile_text, researcher_messages, write_json)

NAME = 'judge_persona_visibility'
OUTPUT = 'persona_visibility'
NONE_FITS = 'X'

SYSTEM = """You read everything one researcher wrote while collaborating with an AI agent on a scientific task.
The agent's messages are not shown. The researcher may have been given one of the [PROFILES] as a description of who they are.

YOUR TASK:
1. "choice": the letter of the profile that the researcher's writing fits best, or "X" if no profile fits better than the others.
   Judge how the researcher writes and what they care about, not the scientific task itself.
2. "confidence": 1 (weak), 2 (moderate) or 3 (strong).
3. "evidence": one short passage of the [RESEARCHER_TEXT], copied VERBATIM, that most informed your choice.

OUTPUT FORMAT:
Output a JSON object enclosed EXACTLY within <FINAL_JSON> tags.
<FINAL_JSON>
{"choice": "A", "confidence": 2, "evidence": "verbatim passage"}
</FINAL_JSON>"""

USER = """<PROFILES>
{profiles}
</PROFILES>

<RESEARCHER_TEXT>
{text}
</RESEARCHER_TEXT>"""


def binomial_p(hits, n, chance):
    """Exact one-sided P(X >= hits) for X ~ Binomial(n, chance)."""
    return sum(comb(n, i) * chance**i * (1-chance)**(n-i) for i in range(hits, n+1))


def cohort(run, records):
    arms = sorted({r['arm'] for r in records if r['kind'] == PERSONA}
                  | {d.name for d in (Path(run) / 'configs').glob('*') if arm_kind(d.name) == PERSONA})
    return {arm: text for arm in arms if (text := profile_text(run, arm))}


def candidates(record, profiles, k):
    """Labelled candidate arms and the target arm (None for neutral), seeded by the episode key."""
    rng = random.Random(record['key'])
    if record['kind'] == NEUTRAL:
        target, chosen = None, rng.sample(sorted(profiles), k)
    else:
        target = twin_of(record['arm']) or record['arm']
        chosen = [target] + rng.sample(sorted(a for a in profiles if a != target), k - 1)
    rng.shuffle(chosen)
    return target, dict(zip(string.ascii_uppercase, chosen))


def messages_for(options, profiles, text):
    listed = '\n\n'.join(f'{label}:\n{profiles[arm]}' for label, arm in options.items())
    listed += f'\n\n{NONE_FITS}: no profile fits better than the others'
    return [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': USER.format(profiles=listed, text=text)}]


def valid_answer(options):
    def check(value):
        return (value.get('choice') in {*options, NONE_FITS} and type(value.get('confidence')) is int
                and 1 <= value['confidence'] <= 3 and isinstance(value.get('evidence'), str)
                and bool(value['evidence'].strip()))
    return check


def judge(record, profiles, k, caller):
    """The result row, or None in a dry run."""
    row = {'key': record['key'], 'arm': record['arm'], 'kind': record['kind'], 'benchmark': record['benchmark'],
           'task': record['task'], 'k': k}
    written = researcher_messages(record)
    target, options = candidates(record, profiles, k)
    row.update(target=target, candidates=options)
    if target is not None and target not in profiles:
        return {**row, 'status': 'no_profile'}
    if not written:
        return {**row, 'status': 'no_text'}
    text = '\n\n'.join(written)
    value, attempts = caller.call_json(messages_for(options, profiles, text), record['key'], valid_answer(options))
    if caller.dry_run:
        return None
    if value is None:
        return {**row, 'status': 'parse_failure', 'attempts': attempts}
    choice = value['choice']
    return {**row, 'status': 'judged', 'attempts': attempts, 'choice': choice, 'chosen_arm': options.get(choice),
            'confidence': value['confidence'], 'evidence': value['evidence'],
            'evidence_ok': is_verbatim(value['evidence'], text),
            'hit': None if target is None else options.get(choice) == target}


def hit_stats(rows, chance):
    hits = sum(r['hit'] for r in rows)
    return {'hits': hits, 'n': len(rows), 'hit_rate': hits/len(rows) if rows else None, 'chance': chance,
            'binomial_p': binomial_p(hits, len(rows), chance) if rows else None}


def shares(rows):
    n = len(rows)
    return {'x_share': sum(r['choice'] == NONE_FITS for r in rows)/n if n else None,
            'evidence_ok_share': sum(r['evidence_ok'] for r in rows)/n if n else None}


def summarize(rows, k):
    chance = 1/k
    summary = {'k': k, 'chance': chance, 'status': dict(Counter(r['status'] for r in rows))}
    for kind in (PERSONA, TWIN):
        judged = [r for r in rows if r['kind'] == kind and r['status'] == 'judged']
        groups = {'benchmark': defaultdict(list), 'target': defaultdict(list)}
        for r in judged:
            groups['benchmark'][r['benchmark']].append(r)
            groups['target'][r['target']].append(r)
        summary[kind] = {'overall': {**hit_stats(judged, chance), **shares(judged)},
                         'per_benchmark': {b: {**hit_stats(v, chance), **shares(v)} for b, v in sorted(groups['benchmark'].items())},
                         'per_persona': {a: hit_stats(v, chance) for a, v in sorted(groups['target'].items())}}
    neutral = [r for r in rows if r['kind'] == NEUTRAL and r['status'] == 'judged']
    summary[NEUTRAL] = {'n': len(neutral), **shares(neutral),
                        'choice_letters': dict(sorted(Counter(r['choice'] for r in neutral).items())),
                        'chosen_arms': dict(Counter(r['chosen_arm'] or NONE_FITS for r in neutral).most_common())}
    return summary


def fmt(value, spec='.3f'):
    return 'n/a' if value is None else format(value, spec)


def markdown(summary):
    lines = ['# Persona visibility', '',
             f"Blind match-to-sample over the researcher's own messages: k={summary['k']} profiles plus X (no profile fits better), chance {summary['chance']:.3f}. "
             'p is the exact one-sided binomial probability of at least that many hits by chance.', '',
             f"Statuses: {summary['status']}", '']
    for kind in (PERSONA, TWIN):
        s = summary[kind]
        o = s['overall']
        lines += [f'## {kind} arms', '', f"Overall: {o['hits']}/{o['n']} hits (rate {fmt(o['hit_rate'])}, p={fmt(o['binomial_p'], '.3g')}); "
                  f"X share {fmt(o['x_share'])}; evidence_ok share {fmt(o['evidence_ok_share'])}.", '',
                  '| Benchmark | Hits / n | Hit rate | p | X share | evidence_ok |', '|---|---:|---:|---:|---:|---:|']
        for b, v in s['per_benchmark'].items():
            lines.append(f"| {b} | {v['hits']}/{v['n']} | {fmt(v['hit_rate'])} | {fmt(v['binomial_p'], '.3g')} | {fmt(v['x_share'])} | {fmt(v['evidence_ok_share'])} |")
        lines += ['', '| Persona | Hits / n | p |', '|---|---:|---:|']
        for a, v in s['per_persona'].items():
            lines.append(f"| {a} | {v['hits']}/{v['n']} | {fmt(v['binomial_p'], '.3g')} |")
        lines.append('')
    n = summary[NEUTRAL]
    lines += ['## neutral arms (no correct profile)', '',
              f"{n['n']} judged; X share {fmt(n['x_share'])}; evidence_ok share {fmt(n['evidence_ok_share'])}.", '',
              f"Choice letters: {n['choice_letters']}", '', f"Chosen profiles: {n['chosen_arms']}", '']
    return '\n'.join(lines)


def run(args, client=None):
    run_dir = args.run.resolve()
    out = run_dir / OUTPUT
    records = load_run(run_dir)
    profiles = cohort(run_dir, records)
    if len(profiles) < args.k:
        raise ValueError(f'Only {len(profiles)} cohort profiles for k={args.k}')
    results_path = out / 'results.jsonl'
    done = set() if args.force else {r['key'] for r in jsonl(results_path)}
    todo = [r for r in records if r['kind'] in (PERSONA, TWIN, NEUTRAL) and r['key'] not in done]
    caller = JudgeCaller(run_dir, NAME, model_spec(run_dir, args.model), budget_usd=args.budget_usd,
                         dry_run=args.dry_run, price_in=args.price_in, price_out=args.price_out, client=client)
    if args.force and results_path.exists() and not args.dry_run:
        results_path.unlink()
    lock = threading.Lock()
    stopped = []

    def one(record):
        try:
            row = judge(record, profiles, args.k, caller)
        except BudgetExhausted as exc:
            stopped.append(str(exc))
            return
        if row is not None and not args.dry_run:
            with lock:
                out.mkdir(parents=True, exist_ok=True)
                with results_path.open('a') as f:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in [pool.submit(one, r) for r in todo]:
            future.result()
    report = {**caller.report(), 'episodes_pending': len(todo), 'budget_stopped': bool(stopped)}
    if not args.dry_run and results_path.exists():
        summary = summarize(jsonl(results_path), args.k)
        write_json(out / 'summary.json', {**summary, 'calls': report})
        (out / 'SUMMARY.md').write_text(markdown(summary))
    return report


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--model', help='Judge model; default: the judge in configs/persona_off/shared.json')
    p.add_argument('--budget-usd', type=float, required=True)
    p.add_argument('--k', type=int, default=4)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--force', action='store_true')
    p.add_argument('--price-in', type=float, help='USD per million input tokens, when responses carry no cost')
    p.add_argument('--price-out', type=float, help='USD per million output tokens')
    return p


def main(argv=None):
    print(json.dumps(run(parser().parse_args(argv)), indent=2))


if __name__ == '__main__':
    sys.exit(main())
