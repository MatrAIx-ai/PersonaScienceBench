"""OpenProblems task_denoising: the actor implements a denoising method; native MCV metrics score it.

Information boundary (benchmark standards §2):
- Public: the task definition and file contracts from the pinned repository, and `train.h5ad`
  (the training half of each cell's molecules; raw counts only).
- Researcher: the dataset's descriptive metadata (name, summary, description, source URL and
  reference). The native task keeps these in `test.h5ad` and never gives them to methods, so
  disclosing them to the simulated researcher is a labelled variant recorded in `conversion`.
- Evaluator only: `test.h5ad` (the held-out molecules and `train_sum`).

Scoring runs the pinned native metric scripts (`mse`, `poisson`) and control methods
(`no_denoising`, `perfect_denoising`) unchanged in a separate Bubblewrap sandbox with the pinned
evaluator environment. Raw metric values are reported as native results; the headline `score`
scales each metric so the negative control is 0 and the positive control is 1, as OpenProblems
does for its leaderboards, and averages the metrics.
"""
from functools import cache
import json
from pathlib import Path
import shutil

from personasciencebench.adapters.base import Adapter, check_submission, sha256
from personasciencebench.schema import (Asset, Episode, EvaluationResult, EvaluatorSpec, Fact,
                                       Provenance, PublicContext, ResearcherContext, TaskSummary)

POLICY = "openproblems-denoising-psb-v1"
METRICS = ("mse", "poisson")  # both minimised (config.vsh.yaml: maximize: false)
CONTROLS = {"negative": "no_denoising", "positive": "perfect_denoising"}
NORMALIZATION = "log_cp10k"  # the processed-dataset directory published for every dataset
RESEARCHER_KEYS = ("dataset_name", "dataset_summary", "dataset_description", "dataset_organism", "dataset_url", "dataset_reference")
EVALUATOR_VENV = ".openproblems-eval-venv"

QUESTION = """Implement and run a denoising method for this single-cell RNA-seq dataset.

`data/train.h5ad` holds raw integer UMI counts in `layers["counts"]` (cells x genes). They are a random
subset of the molecules originally observed in each cell; the remaining molecules are held out.
Estimate the true expression level of every gene in every cell and write `denoised.h5ad`:

- an AnnData object with the same cells and genes, in the same order, as `data/train.h5ad`;
- `layers["denoised"]`: the denoised values (a matrix of that shape; non-negative);
- `uns["dataset_id"]`: copied from the training data; `uns["method_id"]`: a short name for your method.

Evaluation follows molecular cross-validation: the denoised values are compared with the held-out
molecules by mean squared error after library-size normalisation and log1p, and by Poisson loss after
rescaling to the held-out library size. Lower is better for both. The held-out data are not available
to you."""


class OpenProblemsDenoisingAdapter(Adapter):
    name = "openproblems_denoising"

    @cache
    def _datasets(self) -> dict[str, Path]:
        """Dataset id (source/name) -> directory holding train.h5ad and test.h5ad."""
        found = {}
        for train in sorted(self.source.assets.glob(f"*/*/{NORMALIZATION}/train.h5ad")):
            directory = train.parent
            if (directory / "test.h5ad").is_file():
                source, name = directory.relative_to(self.source.assets).parts[:2]
                found[f"{source}/{name}"] = directory
        return found

    def enumerate_tasks(self) -> list[TaskSummary]:
        return [TaskSummary(id=task_id, study_id=f"openproblems:{task_id}", domain="single-cell transcriptomics",
                            title=f"Denoise {task_id}", source_locator=f"resources/task_denoising/datasets/{task_id}/{NORMALIZATION}")
                for task_id in self._datasets()]

    def pilot_task_ids(self) -> list[str]:
        return list(self._datasets())[:2]

    def _api(self, name: str) -> str:
        return (self.source.repository / "src/api" / name).read_text()

    def convert(self, task_id: str) -> Episode:
        import h5py
        directory = self._datasets()[task_id]
        train, test = directory / "train.h5ad", directory / "test.h5ad"
        train_digest, test_digest = sha256(train), sha256(test)
        with h5py.File(train, "r") as handle:
            shape = [int(x) for x in handle["layers/counts"].attrs["shape"]]
            organism = _uns_text(handle, "dataset_organism")
        with h5py.File(test, "r") as handle:
            metadata = {key: _uns_text(handle, key) for key in RESEARCHER_KEYS}
        facts = [Fact(id=f"{task_id}.{key}", topic="dataset_context", text=f"{key.removeprefix('dataset_').replace('_', ' ').capitalize()}: {value}",
                      kind="context", review_status="automated",
                      source=Provenance(source_path=f"resources/task_denoising/datasets/{task_id}/{NORMALIZATION}/test.h5ad",
                                        revision=self.source.revision, locator=f"/uns/{key}", sha256=test_digest))
                 for key, value in metadata.items() if value]
        return Episode(
            id=f"{self.name}:{task_id}", benchmark=self.name, source_task_id=task_id, study_id=f"openproblems:{task_id}",
            domain="single-cell transcriptomics", source_revision=self.source.revision, review_status="automated",
            public=PublicContext(
                question=QUESTION,
                context=("OpenProblems task_denoising at the pinned revision. Implement and execute the method yourself inside "
                         "the workspace; no network access. Researcher consultation is optional."),
                documents={"file_train.yaml": self._api("file_train.yaml"),
                           "file_prediction.yaml": self._api("file_prediction.yaml"),
                           "comp_method.yaml": self._api("comp_method.yaml")},
                submission={"required_artifacts": ["denoised.h5ad", "analysis"],
                            "artifact_keys": ("artifacts['denoised.h5ad']: the written prediction file; artifacts['analysis']: "
                                              "the executed script or notebook that produced it."),
                            "answer": "Describe the method, its parameters and the checks you ran.",
                            "payload": {"executed_analysis": "Set true only after executing the analysis."}},
                environment={"input_paths": ["data/train.h5ad"], "train_shape_cells_genes": shape,
                             **({"organism": organism} if organism else {}),
                             "runtime": "CPU only; Python with numpy, scipy, pandas, anndata, scanpy and scikit-learn; no network"},
                researcher_topics=["dataset_context"] if facts else []),
            researcher=ResearcherContext(facts=facts, unknowns=["Held-out molecules, reference scores and method rankings."],
                                         notes=["Dataset metadata only; the native task keeps it out of the method's inputs."]),
            assets=[Asset(id="train", source_path=str(train.resolve()), target_path="data/train.h5ad", sha256=train_digest),
                    Asset(id="test", source_path=str(test.resolve()), target_path="reference/test.h5ad",
                          visibility="evaluator", sha256=test_digest)],
            evaluator=EvaluatorSpec(kind="native_programmatic", version=POLICY,
                                    entrypoint="personasciencebench.adapters.openproblems_denoising:OpenProblemsDenoisingAdapter.evaluate",
                                    reference={"test_path": str(test.resolve()), "test_sha256": test_digest,
                                               "train_path": str(train.resolve()), "train_sha256": train_digest},
                                    config={"metrics": list(METRICS), "controls": CONTROLS, "native_scripts_unchanged": True,
                                            "environment": "configs/openproblems-evaluator-requirements.lock.txt (not the openproblems/base_python:1 image)",
                                            "score": "mean over metrics of (negative control - value) / (negative control - positive control)"}),
            conversion={"version": POLICY, "task_repository_revision": self.source.revision,
                        "variant": "researcher_holds_dataset_metadata",
                        "variant_note": "The native task gives methods only train.h5ad; dataset metadata stays in test.h5ad. Here the simulated researcher holds that metadata.",
                        "train_sha256": train_digest, "test_sha256": test_digest})

    def _controls_cache(self, test_sha256: str) -> Path:
        return self.source.assets / "_controls" / f"{test_sha256[:16]}-{_scripts_digest(self.source.repository)}.json"

    def evaluate(self, episode, submission, judge=None) -> EvaluationResult:
        check_submission(episode, submission)
        prediction = submission.artifacts.get("denoised.h5ad")
        if not prediction:
            return EvaluationResult(status="missing_submission", evaluator_version=POLICY,
                                    errors=["No denoised.h5ad artifact was submitted."])
        reference = episode.evaluator.reference
        for key in ("test", "train"):
            if sha256(Path(reference[f"{key}_path"])) != reference[f"{key}_sha256"]:
                return EvaluationResult(status="error", evaluator_version=POLICY, errors=[f"{key}.h5ad changed since conversion"])
        work = Path(prediction).parent.parent / "openproblems_evaluation"
        work.mkdir(exist_ok=False)
        shutil.copyfile(prediction, work / "prediction.h5ad")
        shutil.copyfile(reference["test_path"], work / "test.h5ad")
        shutil.copyfile(reference["train_path"], work / "train.h5ad")
        for kind in ("metrics", "control_methods"):
            for name in (METRICS if kind == "metrics" else CONTROLS.values()):
                shutil.copyfile(self.source.repository / "src" / kind / name / "script.py", work / f"{name}.py")
        (work / "evaluate.py").write_text(HARNESS)
        from personasciencebench.runtime import Sandbox
        runtime = Path(__file__).resolve().parents[3] / EVALUATOR_VENV
        cache = self._controls_cache(reference["test_sha256"])
        cache.parent.mkdir(parents=True, exist_ok=True)
        # The native metrics densify the count matrices (about 5-6x the dense size in memory), so
        # only one native evaluation runs at a time on a host; actor episodes still run in parallel.
        import fcntl
        with open(cache.parent / ".evaluation.lock", "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            controls = json.loads(cache.read_text()) if cache.is_file() else None
            command = "python evaluate.py" + ("" if controls else " --controls")
            receipt = Sandbox(work, runtime).execute(command, timeout_seconds=1800)
            output = work / "native_scores.json"
            native = json.loads(output.read_text()) if output.is_file() else None
            if native is not None and not controls and "negative" in native:
                # Control scores depend only on the dataset and the pinned scripts; publish them atomically.
                temporary = cache.with_suffix(f".{work.parent.name}.tmp")
                temporary.write_text(json.dumps({k: native[k] for k in ("negative", "positive")}))
                temporary.replace(cache)
        (work / "execution.json").write_text(json.dumps(receipt, indent=2))
        if native is None:
            return EvaluationResult(status="error", evaluator_version=POLICY, errors=["Native OpenProblems evaluation failed"],
                                    details={"stderr_tail": receipt["stderr"][-2000:], "evaluator_directory": str(work)})
        if controls:
            native.update(controls, controls_cached=True)
        if native.get("contract_violation"):
            # A prediction the native metrics cannot read is a failed method, reported like a missing submission.
            return EvaluationResult(status="missing_submission", evaluator_version=POLICY,
                                    errors=[f"Prediction violates the file contract: {native['contract_violation']}"],
                                    details={"native_result": native, "evaluator_directory": str(work)})
        return EvaluationResult(status="scored", evaluator_version=POLICY, metrics=scaled_metrics(native),
                                details={"native_result": native, "evaluator_directory": str(work),
                                         "score_scope": "Native MCV metrics on held-out molecules; execution checked by the metric scripts reading the file."})


def _scripts_digest(repository: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    for kind, names in (("metrics", METRICS), ("control_methods", tuple(CONTROLS.values()))):
        for name in names:
            digest.update((repository / "src" / kind / name / "script.py").read_bytes())
    return digest.hexdigest()[:16]


def scaled_metrics(native: dict) -> dict:
    """Raw native values plus control-scaled values (negative control 0, positive control 1) and their mean."""
    metrics = {}
    for name in METRICS:
        value, negative, positive = native["prediction"][name], native["negative"][name], native["positive"][name]
        metrics[name] = value
        metrics[f"{name}_scaled"] = (negative - value) / (negative - positive) if negative != positive else None
    scaled = [metrics[f"{name}_scaled"] for name in METRICS if metrics[f"{name}_scaled"] is not None]
    metrics["score"] = sum(scaled) / len(scaled) if scaled else None
    metrics["score_clipped"] = (sum(min(1.0, max(0.0, s)) for s in scaled) / len(scaled)) if scaled else None
    return metrics


def _uns_text(handle, key: str) -> str | None:
    if f"uns/{key}" not in handle:
        return None
    value = handle[f"uns/{key}"][()]
    return (value.decode() if isinstance(value, bytes) else str(value)).strip()


# Runs inside the evaluator sandbox. Each native script is executed unchanged except that the block
# between "## VIASH START" and "## VIASH END" (placeholder parameters) is replaced by the real ones.
HARNESS = r'''
import json, subprocess, sys, traceback

RUNNER = """
import sys, json
script, par, name = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
source = open(script).read()
start, end = source.index("## VIASH START"), source.index("## VIASH END")
source = source[:start] + f"par = {par!r}\\nmeta = {{'name': {name!r}, 'resources_dir': '.'}}\\n" + source[end:]
exec(compile(source, script, "exec"), {"__name__": "__main__"})
"""

def run(script, par, name):
    # A fresh process per native script releases each metric's dense matrices before the next one.
    subprocess.run([sys.executable, "-c", RUNNER, script, json.dumps(par), name], check=True)

def metrics_for(prediction):
    import anndata as ad
    values = {}
    for metric in ("mse", "poisson"):
        out = f"score_{metric}_{prediction.replace('.h5ad', '')}.h5ad"
        run(f"{metric}.py", {"input_test": "test.h5ad", "input_prediction": prediction, "output": out}, metric)
        values[metric] = float(ad.read_h5ad(out, backed="r").uns["metric_values"])
    return values

def check_contract():
    import anndata as ad
    train = ad.read_h5ad("train.h5ad", backed="r")
    try:
        prediction = ad.read_h5ad("prediction.h5ad", backed="r")
    except Exception as error:
        return [f"unreadable prediction: {type(error).__name__}: {error}"]
    problems = []
    if "denoised" not in prediction.layers:
        problems.append("layers['denoised'] is missing")
    elif tuple(prediction.layers["denoised"].shape) != tuple(train.shape):
        problems.append(f"layers['denoised'] has shape {tuple(prediction.layers['denoised'].shape)}, expected {tuple(train.shape)}")
    if list(prediction.obs_names) != list(train.obs_names) or list(prediction.var_names) != list(train.var_names):
        problems.append("cells or genes differ from train.h5ad in identity or order")
    if "method_id" not in prediction.uns:
        problems.append("uns['method_id'] is missing")
    return problems

result = {}
problems = check_contract()
if problems:
    result["contract_violation"] = "; ".join(problems)
else:
    try:
        result["prediction"] = metrics_for("prediction.h5ad")
    except Exception:
        result["contract_violation"] = "native metric failed on the prediction: " + traceback.format_exc(limit=2)[-600:]
if "contract_violation" not in result and "--controls" in sys.argv:
    run("no_denoising.py", {"input_train": "train.h5ad", "output": "control_negative.h5ad"}, "no_denoising")
    run("perfect_denoising.py", {"input_train": "train.h5ad", "input_test": "test.h5ad", "output": "control_positive.h5ad"}, "perfect_denoising")
    result["negative"] = metrics_for("control_negative.h5ad")
    result["positive"] = metrics_for("control_positive.h5ad")
json.dump(result, open("native_scores.json", "w"), indent=2)
'''
