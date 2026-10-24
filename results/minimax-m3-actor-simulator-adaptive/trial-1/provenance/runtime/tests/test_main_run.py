"""Offline guards for the selected main-run inputs and launch interface."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_main', ROOT / 'scripts/check_main.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


@pytest.fixture
def frozen_root(tmp_path):
    shutil.copytree(ROOT / 'configs/main_run', tmp_path / 'configs/main_run')
    cohort = tmp_path / 'configs/full_persona_v2'
    cohort.mkdir()
    shutil.copyfile(ROOT / 'configs/full_persona_v2/cohort.json', cohort / 'cohort.json')
    return tmp_path


def test_frozen_cohort_and_exact_copy_are_valid(frozen_root):
    selection = frozen_root / 'selection.csv'
    shutil.copyfile(frozen_root / 'configs/main_run/selection.csv', selection)
    assert len(check.validate_inputs(frozen_root, selection)) == 200


def test_replacement_question_with_unchanged_counts_is_rejected(frozen_root):
    selection = frozen_root / 'configs/main_run/selection.csv'
    data = selection.read_bytes()
    lines = data.splitlines(keepends=True)
    # Modify one scientific record without changing row/source counts.
    lines[1] = lines[1].replace(b',', b'-changed,', 1)
    selection.write_bytes(b''.join(lines))
    with pytest.raises(ValueError, match='Selection checksum'):
        check.validate_inputs(frozen_root)


def test_modified_profile_is_rejected(frozen_root):
    prompt = frozen_root / 'configs/main_run/personas/candidate_155.md'
    prompt.write_text(prompt.read_text() + '\nChanged identity.\n')
    with pytest.raises(ValueError, match='Persona prompt checksum'):
        check.validate_inputs(frozen_root)


def test_unshipped_persona_rejected_before_run_creation(tmp_path):
    run = tmp_path / 'run'
    result = subprocess.run(
        [sys.executable, '-S', str(ROOT / 'scripts/run_main.py'),
         '--run-dir', str(run), '--arms', 'persona_off', 'candidate_148'],
        capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert 'invalid choice' in result.stderr
    assert not run.exists()


@pytest.mark.parametrize('provider,key', [
    ('openai', 'OPENAI_API_KEY'), ('openrouter', 'OPENROUTER_API_KEY'),
])
def test_missing_credential_names_selected_provider(monkeypatch, provider, key):
    from personasciencebench.inference import OpenRouterClient
    monkeypatch.delenv(key, raising=False)
    client = OpenRouterClient('synthetic-model', role='actor', provider=provider)
    with pytest.raises(ValueError, match=f'{key} is not configured'):
        client.complete([{'role': 'user', 'content': 'Offline fixture'}])
