"""OpenProblems denoising conversion, information boundary and score scaling; synthetic files, no models."""
import json
from pathlib import Path

import pytest

from personasciencebench.adapters.base import SourceConfig
from personasciencebench.adapters import openproblems_denoising as op


def test_scaling_puts_the_negative_control_at_zero_and_the_positive_at_one():
    native = {"prediction": {"mse": 6.0, "poisson": 1.0}, "negative": {"mse": 10.0, "poisson": 1.0},
              "positive": {"mse": 2.0, "poisson": 0.0}}
    metrics = op.scaled_metrics(native)
    assert metrics["mse"] == 6.0 and metrics["mse_scaled"] == pytest.approx(0.5)
    assert metrics["poisson_scaled"] == pytest.approx(0.0)
    assert metrics["score"] == pytest.approx(0.25) and metrics["score_clipped"] == pytest.approx(0.25)
    worse = op.scaled_metrics({**native, "prediction": {"mse": 14.0, "poisson": 1.0}})
    assert worse["mse_scaled"] == pytest.approx(-0.5) and worse["score_clipped"] == pytest.approx(0.0)


def test_equal_controls_give_no_scaled_value():
    metrics = op.scaled_metrics({"prediction": {"mse": 1.0, "poisson": 1.0}, "negative": {"mse": 1.0, "poisson": 2.0},
                                 "positive": {"mse": 1.0, "poisson": 0.0}})
    assert metrics["mse_scaled"] is None and metrics["score"] == pytest.approx(0.5)


def _write_h5ad(path: Path, shape, uns: dict):
    h5py = pytest.importorskip("h5py")
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as handle:
        counts = handle.create_group("layers").create_group("counts")
        counts.attrs["shape"] = shape
        group = handle.create_group("uns")
        for key, value in uns.items():
            group.create_dataset(key, data=value)


@pytest.fixture
def adapter(tmp_path):
    repository, assets = tmp_path / "repo", tmp_path / "assets"
    (repository / "src/api").mkdir(parents=True)
    for name in ("file_train.yaml", "file_prediction.yaml", "comp_method.yaml"):
        (repository / "src/api" / name).write_text(f"contract: {name}\n")
    directory = assets / "cellxgene_census/example/log_cp10k"
    _write_h5ad(directory / "train.h5ad", [120, 300], {"dataset_id": "cellxgene_census/example", "dataset_organism": "homo_sapiens"})
    _write_h5ad(directory / "test.h5ad", [120, 300], {
        "dataset_id": "cellxgene_census/example", "dataset_name": "Example atlas", "dataset_summary": "Kidney cells.",
        "dataset_description": "Single-nucleus RNA-seq of kidney.", "dataset_url": "https://example.org",
        "dataset_reference": "@article{x}", "dataset_organism": "homo_sapiens", "train_sum": 12345})
    return op.OpenProblemsDenoisingAdapter(SourceConfig(repository, assets, "pinned-revision"))


def test_enumerates_each_processed_dataset_once(adapter):
    assert [t.id for t in adapter.enumerate_tasks()] == ["cellxgene_census/example"]


def test_actor_sees_train_and_contracts_but_never_the_held_out_data(adapter):
    episode = adapter.convert("cellxgene_census/example")
    public = json.dumps(episode.actor_input())
    assert episode.public.environment["train_shape_cells_genes"] == [120, 300]
    assert set(episode.public.documents) == {"file_train.yaml", "file_prediction.yaml", "comp_method.yaml"}
    assert "test.h5ad" not in public and "12345" not in public and "Kidney cells" not in public
    visibility = {a.id: a.visibility for a in episode.assets}
    assert visibility == {"train": "actor", "test": "evaluator"}
    assert episode.public.submission["required_artifacts"] == ["denoised.h5ad", "analysis"]


def test_researcher_holds_dataset_metadata_as_a_labelled_variant(adapter):
    episode = adapter.convert("cellxgene_census/example")
    facts = {f.source.locator: f.text for f in episode.researcher.facts}
    assert facts["/uns/dataset_summary"] == "Summary: Kidney cells."
    assert "/uns/train_sum" not in facts and all(f.kind == "context" for f in episode.researcher.facts)
    assert facts["/uns/dataset_organism"] == "Organism: homo_sapiens"
    assert episode.conversion["variant"] == "researcher_holds_dataset_metadata"


def test_missing_prediction_is_a_missing_submission(adapter):
    from personasciencebench.schema import Submission
    episode = adapter.convert("cellxgene_census/example")
    result = adapter.evaluate(episode, Submission(episode_id=episode.id, answer="done", artifacts={}))
    assert result.status == "missing_submission"


def test_changed_reference_files_are_refused(adapter, tmp_path):
    from personasciencebench.schema import Submission
    episode = adapter.convert("cellxgene_census/example")
    Path(episode.evaluator.reference["test_path"]).write_bytes(b"tampered")
    prediction = tmp_path / "sealed/submitted_artifacts/denoised.h5ad"
    prediction.parent.mkdir(parents=True)
    prediction.write_bytes(b"x")
    result = adapter.evaluate(episode, Submission(episode_id=episode.id, answer="done",
                                                  artifacts={"denoised.h5ad": str(prediction)}))
    assert result.status == "error" and "changed" in result.errors[0]


def test_harness_replaces_only_the_viash_parameter_block():
    source = "import x\n## VIASH START\npar = {'a': 1}\n## VIASH END\nprint(par)\n"
    start, end = source.index("## VIASH START"), source.index("## VIASH END")
    assert "source[:start]" in op.HARNESS and "source[end:]" in op.HARNESS
    assert source[:start] == "import x\n" and source[end:].startswith("## VIASH END")
