"""Matched-arm and incomplete-result checks for the DiscoveryBench pilot."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT / 'scripts/run_discoverybench_persona_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def test_arms_change_only_persona_and_single_attribute():
    base = json.loads((ROOT / 'configs/discoverybench-azure.json').read_text())
    reference = json.loads((ROOT / 'examples/science_personas/phase1/reference.json').read_text())
    arms = pilot.arm_configs(base, reference)
    fixed = {k: v for k, v in base.items() if k != 'persona'}
    for config in arms.values():
        assert {k: v for k, v in config.items() if k != 'persona'} == fixed
    assert arms['off']['persona'] == {'enabled': False}
    low = arms['statistics_low']['persona']['science_profile']
    high = arms['statistics_high']['persona']['science_profile']
    assert low['role'] == high['role'] and low['domain'] == high['domain']
    assert [k for k in low['attributes'] if low['attributes'][k] != high['attributes'][k]] == ['statistical_inference']
    assert len(low['attributes']) == 56


def test_missing_scores_stay_missing_and_pairs_use_task_and_repeat():
    rows = []
    for arm, repeat, score in [('off', 1, .2), ('off', 2, None), ('reference', 1, .5), ('reference', 2, .9), ('statistics_low', 1, None)]:
        rows.append({'arm': arm, 'repeat': repeat, 'episode_id': 'task', 'study_id': 'study', 'score': score, 'researcher_requests': 2})
    result = pilot.summarize(rows)
    ref = next(a for a in result['arms'] if a['arm'] == 'reference')
    low = next(a for a in result['arms'] if a['arm'] == 'statistics_low')
    assert ref['paired_n'] == 1 and round(ref['paired_mean_delta_vs_off'], 6) == .3
    assert ref['scored'] == 2 and ref['wins_ties_losses'] == [1, 0, 0]
    assert low['mean_native_score'] is None and low['paired_n'] == 0
    assert result['distinct_studies'] == 1


def test_frozen_inventory_detects_external_launcher_changes(tmp_path, monkeypatch):
    launcher = tmp_path / 'approved-launcher'
    launcher.write_text('#!/bin/sh\nexit 0\n')
    launcher.chmod(0o755)
    monkeypatch.setenv('PERSONASCIENCEBENCH_BWRAP', str(launcher))
    prepared = tmp_path / 'prepared'
    prepared.mkdir()
    runtime = tmp_path / 'runtime'
    runtime.mkdir()
    before = pilot.inventory(prepared, runtime)
    assert str(launcher.resolve()) in before
    launcher.write_text('#!/bin/sh\nexit 1\n')
    assert pilot.inventory(prepared, runtime) != before
