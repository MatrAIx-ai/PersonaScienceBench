"""Offline Phase 1 arm generation and declared-input integrity checks.

This module neither executes episodes nor evaluates scientific results. Its
output is private operator material and must never be mounted into the actor.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import tomllib
from typing import Literal

from pydantic import Field, model_validator

from personasciencebench.researcher import RESEARCHER_POLICY_VERSION
from personasciencebench.schema import Episode, Record
from .config import attach_profile
from .profiles import SciencePersona, catalog_sha256, render_profile


class Contrast(Record):
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$")
    dimension: str
    value: str


class Design(Record):
    version: Literal['phase1-design-1'] = 'phase1-design-1'
    status: Literal['proposal', 'registered'] = 'proposal'
    reference: SciencePersona
    contrasts: list[Contrast] = Field(min_length=1)
    order_seed: int = Field(strict=True, ge=0)

    @model_validator(mode='after')
    def valid_contrasts(self):
        names = [c.id for c in self.contrasts]
        if len(set(names)) != len(names) or {'persona_off', 'reference'} & set(names):
            raise ValueError('Arm IDs must be unique and cannot reuse control IDs')
        seen = set()
        for c in self.contrasts:
            if c.dimension == 'field':
                if not c.value.strip() or c.value == self.reference.domain:
                    raise ValueError('A field contrast must change the field label')
            elif c.dimension in self.reference.attributes:
                if c.value not in {'low', 'medium', 'high'} or c.value == self.reference.attributes[c.dimension]:
                    raise ValueError('An attribute contrast must change exactly one level')
            else:
                raise ValueError(f'Unknown persona dimension: {c.dimension}')
            key = (c.dimension, c.value)
            if key in seen:
                raise ValueError('Duplicate treatment')
            seen.add(key)
        return self


class FixedInputs(Record):
    # Point to all relevant files/trees. One file may cover several categories.
    task: list[str] = Field(min_length=1)
    data: list[str] = Field(min_length=1)
    environment: list[str] = Field(min_length=1)
    execution: list[str] = Field(min_length=1)
    scientific_facts: list[str] = Field(min_length=1)
    gold: list[str] = Field(min_length=1)
    verifier: list[str] = Field(min_length=1)


class TaskInput(Record):
    episode: str
    config: str
    fixed_inputs: FixedInputs
    task_id: str | None = None  # Required when selecting from an EXP JSONL catalog.


class Cohort(Record):
    version: Literal['phase1-cohort-1'] = 'phase1-cohort-1'
    tasks: list[TaskInput] = Field(min_length=50, max_length=50)


class ResearcherSettings(Record):
    mode: Literal['grounded', 'extractive']
    max_questions: int | None = Field(ge=0, strict=True)
    max_facts_per_reply: int = Field(ge=1, strict=True)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def arm_profiles(design: Design) -> dict[str, SciencePersona | None]:
    """Off + reference + one-dimension contrasts; no task-dependent selection."""
    design = Design.model_validate(design.model_dump())
    result = {'persona_off': None, 'reference': design.reference.model_copy(deep=True)}
    for contrast in design.contrasts:
        data = design.reference.model_dump()
        data['id'] = contrast.id  # Bookkeeping only; IDs are not rendered.
        if contrast.dimension == 'field':
            data['domain'] = contrast.value
        else:
            data['attributes'][contrast.dimension] = contrast.value
        result[contrast.id] = SciencePersona.model_validate(data)
    return result


def arm_configs(config: dict, design: Design) -> dict[str, dict]:
    """All arms retain the same simulator, model settings and execution budgets."""
    profiles = arm_profiles(design)
    reference = attach_profile(config, profiles['reference'])
    result = {}
    for name, profile in profiles.items():
        attached = attach_profile(config, profile) if profile else deepcopy(reference)
        if profile is None:
            attached['persona'] = {'enabled': False}
        result[name] = attached
    return result


def _path(raw: str, base: Path) -> Path:
    path = Path(raw).expanduser()
    path = path if path.is_absolute() else base / path
    # Resolve common OS aliases (e.g. /tmp on macOS); reject supplied leaf links.
    if path.is_symlink():
        raise ValueError(f'Fixed input cannot be a symlink: {path}')
    return path.resolve(strict=True)


def fingerprint(path: Path) -> dict:
    """Hash declared bytes and executable bits, including directory contents."""
    if path.is_symlink():
        raise ValueError(f'Fixed input cannot be a symlink: {path}')
    entries = [path] if path.is_file() else sorted(path.rglob('*')) if path.is_dir() else []
    if not entries:
        raise ValueError(f'Fixed input is absent or empty: {path}')
    files = {}
    for item in entries:
        if item.is_symlink():
            raise ValueError(f'Fixed input tree contains a symlink: {item}')
        if item.is_dir():
            continue
        if not item.is_file():
            raise ValueError(f'Fixed input must be a regular file: {item}')
        with item.open('rb') as stream:
            sha = hashlib.file_digest(stream, 'sha256').hexdigest()
        files['.' if path.is_file() else item.relative_to(path).as_posix()] = {
            'sha256': sha, 'executable_bits': item.stat().st_mode & 0o111,
        }
    if not files:
        raise ValueError(f'Fixed input contains no files: {path}')
    return {'path': str(path), 'files': files, 'sha256': digest(files)}


def task_contract(path: Path, task_id: str | None, config: dict) -> dict:
    """Normalize planning metadata while retaining each runner's native task schema."""
    from personasciencebench.collaboration import CollaborationConfig, POLICY
    raw_text = path.read_text()
    if path.suffix == '.jsonl':
        if task_id is None:
            raise ValueError('An EXP JSONL catalog requires an explicit task_id')
        matches = [row for line in raw_text.splitlines() if line.strip()
                   for row in [json.loads(line)] if row.get('task_id') == task_id]
        if len(matches) != 1:
            raise ValueError('EXP task_id must identify exactly one catalog entry')
        raw = matches[0]
    else:
        raw = json.loads(raw_text)
    if 'reference_design' in raw:
        from expbench.schema import Task, Config
        episode = Task.model_validate(raw)
        parsed = Config.model_validate(config)
        if task_id is not None and task_id != episode.task_id:
            raise ValueError('Task selector does not match EXP task card')
        return {'episode_id': 'expbench:' + episode.task_id, 'benchmark': 'expbench',
                'source_task_id': episode.task_id, 'runner': 'expbench.realistic',
                'public': episode.public.model_dump(mode='json'),
                'facts': [f.model_dump(mode='json') for f in episode.researcher.facts],
                'evaluator': {'reference_design': episode.reference_design.model_dump(mode='json'),
                              'provenance': episode.provenance, 'track': 'design_only'},
                'policy': POLICY if parsed.collaboration is not None else 'expbench-scoped'}
    episode = Episode.model_validate(raw)
    if task_id is not None and task_id != episode.source_task_id:
        raise ValueError('Task selector does not match episode')
    if episode.review_status not in {'reviewed', 'automated'}:
        raise ValueError(f'Unreviewed episode: {episode.id}')
    if episode.benchmark == 'expbench':
        raise ValueError('The separate EXP runner requires its native task card or JSONL catalog')
    if episode.benchmark not in {'bixbench', 'discoverybench', 'scienceagentbench',
                                 'terminal_bench_science', 'asibench', 'sciconvbench'}:
        raise ValueError('Unsupported benchmark runner')
    if {'collaboration_version', 'collaboration_addendum', 'new_collaboration_review_status'} & episode.conversion.keys():
        raise ValueError('Superseded collaboration task extension; prepare with the current adapter')
    ResearcherSettings.model_validate(config['researcher'])
    collaboration = config.get('collaboration')
    if collaboration is not None:
        CollaborationConfig.model_validate(collaboration)
    runner = 'personasciencebench.cli'
    policy = POLICY if collaboration is not None else RESEARCHER_POLICY_VERSION
    if episode.benchmark == 'terminal_bench_science':
        runner = 'personasciencebench.terminal_runner'
    elif episode.benchmark == 'sciconvbench':
        from personasciencebench.adapters.sciconvbench import POLICY as SCICONV_POLICY
        runner, policy = 'personasciencebench.sciconv_runner', SCICONV_POLICY
    return {'episode_id': episode.id, 'benchmark': episode.benchmark,
            'source_task_id': episode.source_task_id, 'runner': runner, 'policy': policy,
            'public': episode.actor_input(),
            'facts': [f.model_dump(mode='json') for f in episode.researcher.facts
                      if f.review_status in {'reviewed', 'automated'}],
            'evaluator': episode.evaluator.model_dump(mode='json')}


def make_plan(design: Design, cohort: Cohort, *, base: Path) -> tuple[dict, dict[str, dict]]:
    """Prepare a manifest, never an inference job. Exactly 50 distinct tasks."""
    design = Design.model_validate(design.model_dump())
    cohort = Cohort.model_validate(cohort.model_dump())
    profiles = arm_profiles(design)
    snapshots, configs, records, normalized = [], {}, [], []
    seen_ids, seen_sources = set(), set()
    common_models = None
    for index, task in enumerate(cohort.tasks):
        episode_path = _path(task.episode, base)
        config_path = _path(task.config, base)
        config = (tomllib.loads(config_path.read_text()) if config_path.suffix == '.toml'
                  else json.loads(config_path.read_text()))
        contract = task_contract(episode_path, task.task_id, config)
        source_key = (contract['benchmark'], contract['source_task_id'])
        if contract['episode_id'] in seen_ids or source_key in seen_sources:
            raise ValueError('The cohort must contain 50 distinct source tasks and episode IDs')
        seen_ids.add(contract['episode_id'])
        seen_sources.add(source_key)
        selected_models = {name: {key: config['models'][name].get(key)
                                  for key in ('model', 'reasoning_effort')}
                           for name in ('actor', 'researcher')}
        if common_models is not None and selected_models != common_models:
            raise ValueError('Actor and researcher models and reasoning effort must be the same across the cohort')
        common_models = selected_models

        # Normalized absolute paths refer to the SAME source artifacts for every arm.
        fixed = {key: [str(_path(raw, base)) for raw in paths]
                 for key, paths in task.fixed_inputs.model_dump().items()}
        normalized.append({'episode': str(episode_path), 'config': str(config_path), 'fixed_inputs': fixed, 'task_id': task.task_id})
        snapshot = {
            'episode_id': contract['episode_id'], 'source_task_id': contract['source_task_id'],
            'benchmark': contract['benchmark'], 'runner': contract['runner'],
            'researcher_policy_version': contract['policy'],
            'episode': fingerprint(episode_path), 'base_config': fingerprint(config_path),
            'fixed_inputs': {key: [fingerprint(Path(p)) for p in paths] for key, paths in fixed.items()},
            'public_task_sha256': digest(contract['public']),
            'approved_facts_sha256': digest(contract['facts']),
            'task_eval_sha256': digest(contract['evaluator']),
            'non_persona_config_sha256': digest({k: v for k, v in config.items() if k != 'persona'}),
        }
        snapshots.append(snapshot)
        invariant = digest(snapshot)
        for arm, attached in arm_configs(config, design).items():
            relative = f'configs/task_{index:03d}/{arm}.json'
            configs[relative] = attached
            records.append({'task_index': index, 'episode_id': contract['episode_id'], 'source_task_id': contract['source_task_id'],
                            'runner': contract['runner'], 'arm': arm,
                            'episode': str(episode_path), 'config': relative,
                            'config_sha256': digest(attached), 'fixed_inputs_sha256': invariant})
    random.Random(design.order_seed).shuffle(records)
    plan = {
        'version': 'phase1-plan-2', 'status': 'offline_plan_not_executed',
        'design': design.model_dump(mode='json'), 'cohort': {'version': cohort.version, 'tasks': normalized},
        'cohort_size': 50, 'arm_count': len(profiles), 'episode_count': len(records),
        'catalog_sha256': catalog_sha256(), 'researcher_policy_versions': sorted({s['researcher_policy_version'] for s in snapshots}),
        'implementation_sha256': {
            str(p.relative_to(Path(__file__).resolve().parents[2])): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__).resolve(), Path(__file__).with_name('profiles.py'),
                      Path(__file__).with_name('config.py'), Path(__file__).resolve().parents[1] / 'persona.py',
                      Path(__file__).resolve().parents[1] / 'researcher.py',
                      Path(__file__).resolve().parents[1] / 'collaboration.py',
                      Path(__file__).resolve().parents[1] / 'sciconv_runner.py',
                      Path(__file__).resolve().parents[2] / 'expbench' / 'schema.py',
                      Path(__file__).resolve().parents[2] / 'expbench' / 'collaboration.py',
                      Path(__file__).resolve().parents[2] / 'expbench' / 'realistic.py']
        },
        'identity_sha256': {arm: digest(render_profile(p)) if p else None for arm, p in profiles.items()},
        'fixed_inputs': snapshots, 'episodes': records,
        'limitations': [
            'A proposal is not a registered experiment. This file schedules no jobs and calls no model or verifier.',
            'Hashes cover declared local artifacts; owners must check complete dependency coverage and live runtime/container identity.',
            'Use the recorded native/shared runner and exact source_task_id; this planner does not launch cases.',
            'Model identifiers and reasoning effort match across tasks; task-specific token caps/runtimes remain frozen across arms.',
            'Approved fact hashes include both reviewed and automated source-attributed facts.',
            'Never expose this private manifest or generated configs to the actor. Recheck inputs before and after execution.',
        ],
    }
    return plan, configs


def write_plan(design_path: Path, cohort_path: Path, output: Path) -> dict:
    design = Design.model_validate_json(design_path.read_text())
    cohort = Cohort.model_validate_json(cohort_path.read_text())
    plan, configs = make_plan(design, cohort, base=cohort_path.resolve().parent)
    output = output.resolve()
    # Do not write outputs into any input tree whose fingerprint was frozen.
    for task in plan['cohort']['tasks']:
        inputs = [task['episode'], task['config'], *[p for paths in task['fixed_inputs'].values() for p in paths]]
        if any(output == Path(p) or (Path(p).is_dir() and output.is_relative_to(p)) for p in inputs):
            raise ValueError('Plan output must be separate from fixed inputs')
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    for relative, config in configs.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2) + '\n')
    (output / 'plan.private.json').write_text(json.dumps(plan, indent=2) + '\n')
    return plan


def verify_plan(directory: Path) -> dict:
    saved = json.loads((directory / 'plan.private.json').read_text())
    rebuilt, configs = make_plan(Design.model_validate(saved['design']), Cohort.model_validate(saved['cohort']), base=directory)
    if rebuilt != saved:
        raise ValueError('Plan or frozen inputs changed; stop before running an arm')
    observed = {p.relative_to(directory).as_posix() for p in (directory / 'configs').rglob('*.json')}
    if observed != set(configs):
        raise ValueError('Generated config set changed')
    for relative, expected in configs.items():
        if json.loads((directory / relative).read_text()) != expected:
            raise ValueError(f'Generated config changed: {relative}')
    return {'ok': True, 'cohort_size': 50, 'arms': saved['arm_count'], 'episodes_planned': saved['episode_count'],
            'episodes_executed': 0, 'note': 'Local declared-input verification only; not a scientific evaluation.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('design-check')
    check.add_argument('--design', type=Path, required=True)
    build = commands.add_parser('build')
    build.add_argument('--design', type=Path, required=True)
    build.add_argument('--cohort', type=Path, required=True)
    build.add_argument('--output', type=Path, required=True)
    verify = commands.add_parser('verify')
    verify.add_argument('--plan-directory', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            result = verify_plan(args.plan_directory)
        elif args.command == 'design-check':
            design = Design.model_validate_json(args.design.read_text())
            arms = arm_profiles(design)
            result = {'valid': True, 'status': design.status, 'arms': list(arms), 'planned_episodes_for_50_tasks': 50 * len(arms)}
        else:
            plan = write_plan(args.design, args.cohort, args.output)
            result = {'written': str(args.output), 'episodes_planned': plan['episode_count'], 'episodes_executed': 0}
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
