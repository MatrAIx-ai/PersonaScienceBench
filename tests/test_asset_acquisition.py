"""Acquisition must respect selected tasks and never report missing inputs as ready."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/acquire_conversion_assets.py'


@pytest.fixture
def acquisition(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location('acquire_conversion_assets_test', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    return module


def test_selection_requires_cases_for_benchmark(acquisition, tmp_path):
    selection = tmp_path / 'selection.csv'
    selection.write_text('source,task_id\nbixbench,bix-1-q1\nbixbench,bix-1-q1\nasibench,physics.example\n')
    assert acquisition.selected_tasks(selection, 'bixbench') == ['bix-1-q1']
    with pytest.raises(ValueError, match='No sciconvbench questions'):
        acquisition.selected_tasks(selection, 'sciconvbench')


def bix_fixture(acquisition, monkeypatch, tmp_path, bad_hash=False):
    prepared = []
    payload = b'capsule payload'
    rows = [{'question_id': 'bix-1-q1', 'capsule_uuid': 'one'},
            {'question_id': 'bix-1-q2', 'capsule_uuid': 'one'},
            {'question_id': 'bix-2-q1', 'capsule_uuid': 'two'}]
    adapter = SimpleNamespace(_rows=lambda: rows, source=SimpleNamespace(assets=tmp_path / 'assets'),
                              prepare_assets=lambda task: prepared.append(task) or ['input'])
    monkeypatch.setattr(acquisition, 'load_adapter', lambda *args: adapter)
    digest = '0' * 64 if bad_hash else hashlib.sha256(payload).hexdigest()
    files = [SimpleNamespace(rfilename='CapsuleFolder-one.zip', lfs=SimpleNamespace(sha256=digest))]
    monkeypatch.setitem(sys.modules, 'huggingface_hub', SimpleNamespace(
        HfApi=lambda: SimpleNamespace(dataset_info=lambda *a, **kw: SimpleNamespace(siblings=files))))
    requests = []
    monkeypatch.setattr(acquisition.urllib.request, 'urlopen', lambda url, **kw: requests.append(url) or io.BytesIO(payload))
    return requests, prepared


def test_bix_only_downloads_selected_capsules_once(acquisition, monkeypatch, tmp_path):
    requests, prepared = bix_fixture(acquisition, monkeypatch, tmp_path)
    result = acquisition.bixbench(['bix-1-q1', 'bix-1-q2'])
    assert len(requests) == len(prepared) == len(result) == 1
    assert result[0]['capsule'] == 'one'
    assert result[0]['status'] == 'prepared'
    acquisition.bixbench(['bix-1-q1'])
    assert len(requests) == 1  # Verified cached download is reused.


def test_bix_unknown_task_stops_before_download(acquisition, monkeypatch, tmp_path):
    requests, _ = bix_fixture(acquisition, monkeypatch, tmp_path)
    with pytest.raises(ValueError, match='Unknown BixBench'):
        acquisition.bixbench(['not-a-question'])
    assert requests == []


def test_bix_corrupt_download_fails_setup(acquisition, monkeypatch, tmp_path):
    _, prepared = bix_fixture(acquisition, monkeypatch, tmp_path, bad_hash=True)
    with pytest.raises(RuntimeError, match='1 BixBench capsules failed'):
        acquisition.bixbench(['bix-1-q1'])
    assert prepared == []
    assert not (tmp_path / 'assets/CapsuleFolder-one.zip').exists()
    report = json.loads((tmp_path / 'data/conversion_catalog/bixbench_acquisition.json').read_text())
    assert report[0]['status'] == 'blocked'
    assert 'hash mismatch' in report[0]['error']


def test_asi_incomplete_cached_instance_does_not_pass(acquisition, monkeypatch, tmp_path):
    (tmp_path / 'manifests').mkdir()
    (tmp_path / 'manifests/sources.json').write_text(json.dumps({'asibench': {'dataset_revision': 'fixed'}}))
    result = SimpleNamespace(instance_ids=[], skipped=['physics.example__seed31415'])
    monkeypatch.setitem(sys.modules, 'ai4sci_bench.hf.pull', SimpleNamespace(pull_instances=lambda *a, **kw: result))
    with pytest.raises(RuntimeError, match='Incomplete ASI-Bench'):
        acquisition.asibench(['physics.example'])
    instance = tmp_path / 'external/sources/_assets/asibench/instances/physics.example__seed31415'
    instance.mkdir(parents=True)
    (instance / 'prompt_b3.md').write_text('Task')
    (instance / 'data').mkdir()
    (instance / 'reference').mkdir()
    assert acquisition.asibench(['physics.example']) is result
