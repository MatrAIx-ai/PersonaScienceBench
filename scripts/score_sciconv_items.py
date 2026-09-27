#!/usr/bin/env python3
"""Per-fact scoring of SciConv episodes: which missing entities were asked for, told, and recovered.

Ported from SciConvBench persona_eval.py (attribution prompt, three-valued item flags, entity matching)
with the native row's missing_entities in place of fact cards. One judge call per (question, reply) turn;
"asked" comes from that same call. Recovery reuses the native disambiguation judge's recovered_entities.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys

from personasciencebench.arms import CONTROL, PERSONA
from personasciencebench.run_io import (BudgetExhausted, JudgeCaller, final_specification, is_verbatim, load_run,
                                        model_spec, norm_ws, read_json, sciconv_turns, write_json)

NAME = 'score_sciconv_items'
OUTPUT = 'sciconv_items'
FLAGS = ('asked', 'delivered', 'partial', 'unasked_delivered', 'unasked_partial', 'recovered', 'grounded', 'silent')

ATTRIBUTION_SYSTEM = """
        You label one turn of a clarification dialogue between an Agent and a User.
        The User holds the information on the [FACT_CARDS] (each has a card_id and the information it concerns).
        You get the Agent's [QUESTION] and the User's [ANSWER].

        **YOUR TASK:**
        1. "asked": the card_ids whose information the QUESTION asks for, directly or as part of a broader question.
        2. "conveyed": one entry per card whose information the ANSWER gives to the Agent.
           - "level": "full" if the answer gives all of the card's information, "partial" if it gives only part of it.
             Confirming a value that the question proposes counts as conveying it.
           - "evidence": the shortest passage of the ANSWER that carries the information, copied VERBATIM from the ANSWER.
           Cards whose information is not in the answer are left out.

        **OUTPUT FORMAT:**
        You must output your final evaluation as a JSON object enclosed EXACTLY within <FINAL_JSON> tags.
        <FINAL_JSON>
        {
            "asked": ["card_id"],
            "conveyed": [{"card_id": "card_id", "level": "full", "evidence": "verbatim passage of the answer"}]
        }
        </FINAL_JSON>
        """

ATTRIBUTION_USER = """
        <FACT_CARDS>
        {cards}
        </FACT_CARDS>

        <QUESTION>
        {question}
        </QUESTION>

        <ANSWER>
        {answer}
        </ANSWER>
        """

RANK = {'partial': 1, 'full': 2}


def cards(items):
    return [{'card_id': f'E{i}', 'text': item} for i, item in enumerate(items)]


def attribution_messages(items, turn):
    user = ATTRIBUTION_USER.format(cards=json.dumps(cards(items), indent=2, ensure_ascii=False),
                                   question=turn['question'], answer=turn['answer'])
    return [{'role': 'system', 'content': ATTRIBUTION_SYSTEM}, {'role': 'user', 'content': user}]


def well_formed(value):
    return isinstance(value.get('asked', []), list) and isinstance(value.get('conveyed', []), list)


def label_turn(parsed, items, answer):
    """Per-turn asked ids and best conveyed level per id; both None when the judge output was unusable."""
    ids = {c['card_id'] for c in cards(items)}
    out = {'asked': None, 'conveyed': None, 'parse_failure': parsed is None,
           'dropped_evidence': 0, 'unknown_ids': 0, 'invalid_level': 0}
    if parsed is None:
        return out
    out['asked'] = []
    for cid in parsed.get('asked') or []:
        if cid in ids:
            if cid not in out['asked']:
                out['asked'].append(cid)
        else:
            out['unknown_ids'] += 1
    out['conveyed'] = {}
    for entry in parsed.get('conveyed') or []:
        if not isinstance(entry, dict):
            continue
        cid, level, ev = entry.get('card_id'), entry.get('level'), entry.get('evidence') or ''
        if cid not in ids:
            out['unknown_ids'] += 1
            continue
        if level not in RANK:
            out['invalid_level'] += 1
            continue
        if not is_verbatim(ev, answer):
            out['dropped_evidence'] += 1
            continue
        prev = out['conveyed'].get(cid)
        if prev is None or RANK[level] > RANK[prev['level']]:
            out['conveyed'][cid] = {'level': level, 'evidence': ev}
    return out


# three-valued logic: None = unknown because a turn's judge output could not be parsed
def _or(vals):
    vals = list(vals)
    return True if True in vals else (None if None in vals else False)


def _and(*vals):
    return False if False in vals else (None if None in vals else True)


def _not(v):
    return None if v is None else not v


def attribution_flags(card_id, turns):
    def has_level(t, level):
        return None if t['conveyed'] is None else t['conveyed'].get(card_id, {}).get('level') == level

    def asked(t):
        return None if t['asked'] is None else card_id in t['asked']

    delivered = _or(has_level(t, 'full') for t in turns)
    # leak: conveyed in a turn that does not ask for it, before any turn has asked for it
    leak, leak_partial, asked_before = False, False, False
    for t in turns:
        unasked = _and(_not(asked(t)), _not(asked_before))
        leak = _or([leak, _and(has_level(t, 'full'), unasked)])
        leak_partial = _or([leak_partial, _and(has_level(t, 'partial'), unasked)])
        asked_before = _or([asked_before, asked(t)])
    return {'asked': _or(asked(t) for t in turns), 'delivered': delivered,
            'partial': _and(_not(delivered), _or(has_level(t, 'partial') for t in turns)),
            'unasked_delivered': leak, 'unasked_partial': leak_partial}


def norm_entity(s):
    return re.sub(r'^[\W_]+|[\W_]+$', '', norm_ws(str(s)).lower())


def match_entities(items, entities):
    """Per item, the index of the judge entity it matches or None: exact normalised match first, then
    containment either way; each entity matches at most one item; longest items first."""
    item_n = [norm_entity(e) for e in items]
    ent_n = [norm_entity(e) for e in entities]
    order = sorted(range(len(items)), key=lambda i: -len(item_n[i]))
    match, used = [None] * len(items), set()
    for exact in (True, False):
        for i in order:
            if match[i] is not None or not item_n[i]:
                continue
            for j, e in enumerate(ent_n):
                if j in used or not e:
                    continue
                if e == item_n[i] if exact else (e in item_n[i] or item_n[i] in e):
                    match[i] = j
                    used.add(j)
                    break
    return match


def recovery(case, items, events):
    """Per-item recovered flags from the native judge, or None when there is no final specification or judgement."""
    path = case / 'llm_judge_disambiguation_score.json'
    if final_specification(events) is None or not path.exists():
        return [None] * len(items), {'source': None}
    judged = read_json(path)
    entities = judged.get('recovered_entities') or []
    match = match_entities(items, entities)
    score = re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*', str(judged.get('score', '')))
    matched = sum(m is not None for m in match)
    return [m is not None for m in match], {
        'source': path.name, 'unmatched_entities': [e for j, e in enumerate(entities) if j not in set(match)],
        'item_match_mismatch': None if score is None else matched != int(score.group(1))}


def score_episode(record, caller):
    """The item_scores record, or None in a dry run."""
    reference = record['episode'].get('evaluator', {}).get('reference', {})
    if reference.get('mode', 'disambiguation') != 'disambiguation':
        return {'key': record['key'], 'arm': record['arm'], 'status': 'not_disambiguation'}
    items = reference['native_row'].get('missing_entities') or []
    turns = sciconv_turns(record['events'])
    labels = []
    for n, turn in enumerate(turns if items else []):
        parsed, attempts = caller.call_json(attribution_messages(items, turn), f"{record['key']}:turn{n}", well_formed)
        labels.append({**label_turn(parsed, items, turn['answer']), 'attempts': attempts})
    if caller.dry_run:
        return None
    recovered, recovery_details = recovery(record['case'], items, record['events'])
    rows = []
    for i, item in enumerate(items):
        row = {'index': i, 'item': item, 'card_id': f'E{i}', **attribution_flags(f'E{i}', labels),
               'recovered': recovered[i], 'grounded': None, 'silent': None}
        if row['recovered'] is not None and row['delivered'] is not None:
            row['grounded'] = row['recovered'] and row['delivered']
            row['silent'] = row['recovered'] and not row['delivered']
        rows.append(row)
    return {'key': record['key'], 'arm': record['arm'], 'kind': record['kind'], 'task': record['task'],
            'status': 'scored', 'model': caller.spec.get('model'), 'items': rows, 'turns': labels,
            'parse_failures': sum(t['parse_failure'] for t in labels), 'recovery': recovery_details}


def rate(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return sum(vals)/len(vals) if vals else None


def summarize(scores):
    scored = [s for s in scores if s.get('status') == 'scored']
    by_arm = defaultdict(list)
    for s in scored:
        by_arm[s['arm']].append(s)
    per_arm = {arm: {'kind': group[0]['kind'], 'episodes': len(group), 'items': sum(len(s['items']) for s in group),
                     **{f: rate([r for s in group for r in s['items']], f) for f in FLAGS}}
               for arm, group in sorted(by_arm.items())}
    episode_rates = [{**s, 'rates': {f: rate(s['items'], f) for f in FLAGS}} for s in scored]
    controls = defaultdict(list)
    for s in episode_rates:
        if s['kind'] == CONTROL:
            controls[s['task']].append(s['rates'])
    baseline = {task: {f: rate([{f: r[f]} for r in group], f) for f in FLAGS} for task, group in controls.items()}
    deltas = defaultdict(lambda: defaultdict(list))
    for s in episode_rates:
        if s['kind'] != PERSONA or s['task'] not in baseline:
            continue
        for f in FLAGS:
            if s['rates'][f] is not None and baseline[s['task']][f] is not None:
                deltas[s['arm']][f].append(s['rates'][f] - baseline[s['task']][f])
    vs_control = {arm: {f: {'mean_delta': sum(v)/len(v), 'tasks': len(v)} for f, v in flags.items()}
                  for arm, flags in sorted(deltas.items())}
    return {'episodes': len(scores), 'scored': len(scored),
            'status': {k: sum(s.get('status') == k for s in scores) for k in sorted({s.get('status') for s in scores})},
            'parse_failures': sum(s.get('parse_failures', 0) for s in scored),
            'recovered_unavailable_episodes': sum(s['recovery']['source'] is None for s in scored),
            'per_arm': per_arm, 'persona_minus_control': vs_control}


def fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def markdown(summary):
    lines = ['# SciConv per-item scores', '',
             f"Scored episodes: {summary['scored']} / {summary['episodes']}; statuses {summary['status']}; "
             f"turn parse failures {summary['parse_failures']}; episodes without recovery judgement "
             f"{summary['recovered_unavailable_episodes']}.", '',
             'Rates pool items across an arm\'s episodes; unknown flags (parse failure, no recovery judgement) are excluded.', '',
             '| Arm | Kind | Episodes | Items | ' + ' | '.join(FLAGS) + ' |', '|---|---|---:|---:|' + '---:|' * len(FLAGS)]
    for arm, v in summary['per_arm'].items():
        lines.append(f"| {arm} | {v['kind']} | {v['episodes']} | {v['items']} | " + ' | '.join(fmt(v[f]) for f in FLAGS) + ' |')
    lines += ['', '## Persona minus control', '',
              'Per episode item rate minus the mean of the control arms on the same task, averaged over tasks.', '',
              '| Arm | ' + ' | '.join(FLAGS) + ' |', '|---|' + '---:|' * len(FLAGS)]
    for arm, flags in summary['persona_minus_control'].items():
        cells = [f"{flags[f]['mean_delta']:+.3f} (n={flags[f]['tasks']})" if f in flags else 'n/a' for f in FLAGS]
        lines.append(f'| {arm} | ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n'


def run(args, client=None):
    run_dir = args.run.resolve()
    base = run_dir / 'replay' if args.replay else run_dir
    records = [r for r in load_run(run_dir, replay=args.replay) if r['benchmark'] == 'sciconvbench']
    todo = [r for r in records if args.force or not (r['case'] / 'item_scores.json').exists()]
    caller = JudgeCaller(base, NAME, model_spec(run_dir, args.model), budget_usd=args.budget_usd,
                         dry_run=args.dry_run, price_in=args.price_in, price_out=args.price_out, client=client)
    stopped = []

    def one(record):
        try:
            scores = score_episode(record, caller)
        except BudgetExhausted as exc:
            stopped.append(str(exc))
            return
        if scores is not None:
            write_json(record['case'] / 'item_scores.json', scores)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in [pool.submit(one, r) for r in todo]:
            future.result()
    report = {**caller.report(), 'episodes_pending': len(todo), 'budget_stopped': bool(stopped)}
    if not args.dry_run:
        scores = [read_json(r['case'] / 'item_scores.json') for r in records if (r['case'] / 'item_scores.json').exists()]
        summary = summarize(scores)
        write_json(base / OUTPUT / 'summary.json', {**summary, 'calls': report})
        (base / OUTPUT / 'SUMMARY.md').write_text(markdown(summary))
    return report


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--replay', action='store_true', help='Score the replayed replies under <run>/replay/ instead of the run')
    p.add_argument('--model', help='Judge model; default: the judge in configs/persona_off/shared.json')
    p.add_argument('--budget-usd', type=float, required=True)
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
