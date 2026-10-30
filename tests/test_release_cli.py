"""Release CLI entrypoints fail with actionable arguments rather than missing defaults."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('args', [
    ['persona', '--episode', 'missing.json'],
    ['serve', '--episode', 'missing.json', '--output', 'unused', '--artifact-root', 'unused'],
    ['run', '--prepared', 'missing', '--benchmarks', 'discoverybench',
     '--output', 'unused', '--actor-python', 'unused'],
    ['regrade', '--run', 'missing', '--output', 'unused'],
    ['run-ideagene', '--output', 'unused'],
])
def test_shared_cli_requires_explicit_config_before_accessing_files(args, capsys):
    from personasciencebench.cli import main
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    error = capsys.readouterr().err
    assert 'required: --config' in error
    assert 'FileNotFoundError' not in error


@pytest.mark.parametrize('module,command', [('cli', 'validate'), ('realistic', 'run')])
def test_exp_cli_requires_explicit_tasks_and_config(module, command, capsys):
    import importlib
    main = importlib.import_module('expbench.' + module).main
    with pytest.raises(SystemExit) as exc:
        main([command])
    assert exc.value.code == 2
    error = capsys.readouterr().err
    assert '--tasks' in error and '--config' in error and 'required' in error
    assert 'FileNotFoundError' not in error


def test_source_default_matches_setup_download_location(monkeypatch):
    from personasciencebench import cli
    observed = []

    def fake_adapter(name, source_root, manifest):
        observed.append(source_root)
        return SimpleNamespace(enumerate_tasks=lambda: [], pilot_task_ids=lambda: [])

    monkeypatch.setattr(cli, 'load_adapter', fake_adapter)
    assert cli.main(['catalog', '--benchmarks', 'discoverybench']) == 0
    assert observed == [ROOT / 'external/sources']


def test_ideagene_reads_all_shipped_prompt_files_exactly():
    from personasciencebench.ideagene_runner import selected_profiles
    manifest = json.loads((ROOT / 'configs/full_persona_v2/cohort.json').read_text())
    ids = ['persona_off'] + [row['candidate_id'] for row in manifest['profiles']]
    profiles = selected_profiles(ids, ROOT)
    assert len(profiles) == 5
    assert profiles['persona_off'].enabled is False
    for row in manifest['profiles']:
        assert profiles[row['candidate_id']].system_prompt == (ROOT / row['prompt']).read_text()


@pytest.mark.parametrize('legacy', [False, True])
def test_ideagene_preserves_hash_validation_for_both_profile_formats(tmp_path, legacy):
    from personasciencebench.ideagene_runner import selected_profiles
    prompt = 'A fixed identity.\n'
    profile = tmp_path / 'profile.md'
    profile.write_text('```text\n' + prompt + '\n```' if legacy else prompt)
    row = {'candidate_id': 'candidate_155', 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
           'published_profile' if legacy else 'prompt': 'profile.md'}
    cohort = tmp_path / 'configs/full_persona_v2/cohort.json'
    cohort.parent.mkdir(parents=True)
    cohort.write_text(json.dumps({'profiles': [row]}))
    ids = ['persona_off', 'candidate_155']
    assert selected_profiles(ids, tmp_path)['candidate_155'].system_prompt == prompt
    profile.write_text(profile.read_text().replace('fixed', 'changed'))
    with pytest.raises(ValueError, match='Published persona hash mismatch'):
        selected_profiles(ids, tmp_path)
