"""Describe an existing interaction trace without changing or scoring a task."""

import argparse
import hashlib
import json
from pathlib import Path


def summarize(events_path: Path, evaluation_path: Path | None = None) -> dict:
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    questions = [e for e in events if e['type'] == 'researcher_question']
    replies = [e for e in events if e['type'] == 'researcher_reply']
    facts = {f for e in replies for f in e['payload'].get('fact_ids', [])}
    result = {
        'kind': 'descriptive_interaction_observations',
        'events_sha256': hashlib.sha256(events_path.read_bytes()).hexdigest(),
        'question_calls': len(questions), 'researcher_reply_events': len(replies),
        'unique_disclosed_fact_ids': len(facts),
        'reply_characters': sum(len(e['payload'].get('answer', '')) for e in replies),
        'fallback_events': sum(bool(e['payload'].get('fallback')) for e in replies),
        'question_limit_events': sum(e['payload'].get('fallback') == 'question_limit' for e in replies),
        'shared_progress_events': sum(e['type'] == 'shared_progress' for e in events),
        'question_sequences': [e['sequence'] for e in questions],
        'native_evaluation': None,
        'interpretation': 'Counts are descriptive. They do not establish question quality, dependence, adaptation or scientific success.',
    }
    if evaluation_path is not None:
        result['native_evaluation'] = {
            'sha256': hashlib.sha256(evaluation_path.read_bytes()).hexdigest(),
            'unchanged_result': json.loads(evaluation_path.read_text()),
        }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True, type=Path)
    parser.add_argument('--evaluation', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        text = json.dumps(summarize(args.events, args.evaluation), indent=2) + '\n'
        if args.output:
            with args.output.open('x') as stream:
                stream.write(text)
        else:
            print(text, end='')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
