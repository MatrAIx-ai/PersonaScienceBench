"""Inspect the existing simulator's identity slot without making a model call.

Reads an already prepared episode and existing run config. It never writes the
source episode, submits work, invokes a verifier, or alters the task protocol.
The output is a controller/operator preview, not an actor input.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from personasciencebench.persona import resolve_persona
from personasciencebench.researcher import Researcher
from personasciencebench.schema import Episode
from personasciencebench.science_personas.config import attach_profile
from personasciencebench.science_personas.profiles import SciencePersona, profile_record


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class CapturedRequest(Exception):
    pass


class CaptureBackend:
    def __init__(self):
        self.messages = None

    def complete(self, messages, **kwargs):
        self.messages = deepcopy(messages)
        raise CapturedRequest


def inspect_injection(episode, config, profile, question):
    before = episode.model_dump()
    attached = attach_profile(config, profile) if profile is not None else deepcopy(config)
    if profile is None:
        attached['persona'] = {'enabled': False}
    backend = CaptureBackend()
    researcher = Researcher(episode, backend, persona=resolve_persona(attached, episode),
                            **attached['researcher'])
    try:
        researcher.ask(question)
    except CapturedRequest:
        pass
    assert episode.model_dump() == before
    result = {
        'kind': 'offline-simulator-injection-preview', 'model_calls': 0,
        'profile': profile_record(profile) if profile is not None else None,
        'episode_unchanged': True, 'public_task_sha256': digest(episode.actor_input()),
        'task_eval_sha256': digest(episode.evaluator.model_dump()),
        'non_persona_config_sha256': digest({k: v for k, v in attached.items() if k != 'persona'}),
        'existing_researcher_settings': attached['researcher'],
        'simulator_request_observed': backend.messages is not None,
    }
    if backend.messages is not None:
        system = json.loads(backend.messages[0]['content'])
        result['identity'] = system.pop('identity', None)
        result['non_identity_system_sha256'] = digest(system)
        result['eligible_fact_ids'] = [fact['id'] for fact in system['facts']]
    else:
        result['note'] = 'The existing simulator did not issue a request under these settings; no interaction was forced.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--profile', type=Path)
    selection.add_argument('--persona-off', action='store_true')
    parser.add_argument('--question', default='How would you prefer to discuss the analysis?')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    result = inspect_injection(Episode.model_validate_json(args.episode.read_text()),
        json.loads(args.config.read_text()), SciencePersona.model_validate_json(args.profile.read_text()) if args.profile else None, args.question)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as output:
            output.write(text)
    else:
        print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
