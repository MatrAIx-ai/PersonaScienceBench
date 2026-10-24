"""MLAgentBench ML-experimentation tasks; native per-task get_score evaluation.

Each source task is a starter-code workspace whose native verifier is
``MLAgentBench/benchmarks/<task>/scripts/eval.py:get_score(final_workspace)``.
The adapter preserves that kernel exactly and never routes it through the
upstream harness driver (``python -m MLAgentBench.eval``), whose import chain
and log-stub requirements are agent-framework plumbing we replace.
"""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import statistics
import tarfile
import tempfile
import urllib.request

from personasciencebench.adapters.base import Adapter, check_submission, sha256
from personasciencebench.schema import (
    Asset, Episode, EvaluationResult, EvaluatorSpec, Fact, Provenance,
    PublicContext, ResearcherContext, TaskSummary,
)

SOURCE_REVISION = "5d71205cc20a8e95d43aa7cb7120e89ca3323e31"
ADAPTER_VERSION = "mlagentbench-adapter-v1"
EVALUATOR_VERSION = "mlagentbench-native-get-score-v1"
BENCHMARKS = "MLAgentBench/benchmarks"

# Native run budget (upstream runner.py:44-45); the shared PSB actor replaces it
# with configured actor steps and a <=600 second per-command limit. That budget
# substitution is a declared altered-budget adaptation, not a native condition.
NATIVE_BUDGET = {"max_steps": 50, "max_time_hours": 5}

# Paper categories (Huang et al., ICML 2024, Table 2) group related tasks for
# splits; the metric direction list mirrors upstream plot.py:144.
TASKS = {
    "cifar10": {
        "category": "canonical", "domain": "computer vision",
        "title": "Improve a CIFAR-10 CNN training script",
        "metric": "test_accuracy", "direction": "higher", "requires_gpu": False,
        "data": "cifar10_archive", "eval_cache": "data",
        "failure_sentinel": None,
    },
    "imdb": {
        "category": "canonical", "domain": "natural language processing",
        "title": "Finetune DistilBERT on IMDb from a skeleton script",
        "metric": "test_accuracy", "direction": "higher", "requires_gpu": True,
        "data": "huggingface_runtime", "eval_cache": None, "failure_sentinel": None,
    },
    "ogbn-arxiv": {
        "category": "canonical", "domain": "graph learning",
        "title": "Improve node classification on ogbn-arxiv",
        "metric": "test_accuracy", "direction": "higher", "requires_gpu": False,
        "data": "ogb_dataset", "eval_cache": "networks", "failure_sentinel": None,
    },
    "house-price": {
        "category": "classic-kaggle", "domain": "tabular regression",
        "title": "Predict house prices from tabular features",
        "metric": "mean_absolute_error", "direction": "lower", "requires_gpu": False,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "spaceship-titanic": {
        "category": "classic-kaggle", "domain": "tabular classification",
        "title": "Predict passenger transport on Spaceship Titanic",
        "metric": "test_accuracy", "direction": "higher", "requires_gpu": False,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "amp-parkinsons-disease-progression-prediction": {
        "category": "kaggle-challenge", "domain": "clinical time series",
        "title": "Predict Parkinson's disease progression",
        "metric": "smape", "direction": "lower", "requires_gpu": False,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "fathomnet": {
        "category": "kaggle-challenge", "domain": "marine image recognition",
        "title": "Multi-label classification of ocean imagery",
        "metric": "map_at_20", "direction": "higher", "requires_gpu": True,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "feedback": {
        "category": "kaggle-challenge", "domain": "essay assessment",
        "title": "Score English-learner essays",
        "metric": "mcrmse", "direction": "lower", "requires_gpu": True,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "identify-contrails": {
        "category": "kaggle-challenge", "domain": "satellite image segmentation",
        "title": "Identify aviation contrails in satellite images",
        "metric": "dice", "direction": "higher", "requires_gpu": True,
        "data": "kaggle", "eval_cache": None, "failure_sentinel": None,
    },
    "CLRS": {
        "category": "research", "domain": "algorithmic reasoning",
        "title": "Improve a CLRS floyd_warshall baseline model",
        "metric": "eval_score", "direction": "higher", "requires_gpu": True,
        "data": "clrs_runtime_download", "eval_cache": None, "failure_sentinel": None,
    },
    "babylm": {
        "category": "research", "domain": "language modeling",
        "title": "Train a small language model on the BabyLM data",
        "metric": "perplexity", "direction": "lower", "requires_gpu": True,
        "data": "babylm_data", "eval_cache": None, "failure_sentinel": None,
    },
    "vectorization": {
        "category": "code-improvement", "domain": "numerical computing",
        "title": "Vectorise a NumPy convolution forward pass",
        "metric": "runtime_seconds", "direction": "lower", "requires_gpu": False,
        "data": "none", "eval_cache": None, "failure_sentinel": 1e10,
    },
}

# No scripts/eval.py exists upstream, so the preserved-native-evaluation
# contract cannot be met; recorded exclusions, not silent omissions.
EXCLUDED = {
    "llama-inference": "No native scripts/eval.py; the paper timed it outside the harness.",
    "bibtex-generation": "No native verifier; paper Appendix B used preliminary human evaluation.",
    "literature-review-tool": "No native verifier; paper Appendix B used preliminary human evaluation.",
}

# Hand-reviewed pilot pins; any drift fails conversion closed.
PINNED = {
    "vectorization": {
        "scripts/research_problem.txt": "49ccb7b07a615230acb7d29826d2ff6a1b343192741b558f2443acb4eb1e61ab",
        "scripts/eval.py": "991953c1c4e770a9335f1d8cff3a7edead961cbee81842133a0ef2b007b41d55",
        "env/train.py": "fe9442577dc78d1e53657f9ddf0904272d70de2b8e8759a531a484c68e2cbcf5",
    },
    "cifar10": {
        "scripts/research_problem.txt": "19a3fe2fb03b45b14386d74fddac2806827402d0aca6a3e87bf861bc8a373559",
        "scripts/eval.py": "7c0b387a0b25c991045f2edba90cf56c13aa730a4985941ae07593afc5197e51",
        "scripts/prepare.py": "b8e0a19b6d35d5e401579e30ec6947dffb47f96489c9e61ec976fe0bf83b7c39",
        "scripts/read_only_files.txt": "f1cffc9e04f54186b51f98bdd6866dc789a587efe29d7e2d51d4ad637bb8ac77",
        "env/train.py": "1d31d90aae58152e20e222f36721cbe224f96021f4f3fccbddfe619a96bd60ad",
    },
}

# Explicit statements of a starter's own output layout, added to the public
# submission contract where the native wording ("as shown in train.py") proved
# ambiguous in practice. Each is a labeled public-task adaptation derived from
# pinned starter code; it states the artifact layout, never grader internals.
PUBLIC_FORMATS = {
    "cifar10": {
        "text": ("submission.csv keeps the starter's layout: a header row, then one row per test "
                 "example in test-set order; the first column is the test-example index 0-9999 "
                 "(the DataFrame index that train.py's to_csv('submission.csv') writes by default), "
                 "followed by ten columns named 0-9 holding the per-class probabilities. The index "
                 "column is part of the required format; do not remove it."),
        "source": "env/train.py",
        "locator": "lines 99-106",
    },
}

CIFAR10_ARCHIVE = {
    "url": "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
    "sha256": "6d958be074577803d12ecdefd02955f39262c83c16fe9348329d7fe0b5c001ce",
    "extracted": "cifar-10-batches-py",
}

DATA_ACQUISITION = {
    "cifar10_archive": "prepare_assets downloads the pinned CIFAR-10 python archive (~170MB) into the assets directory.",
    "ogb_dataset": "Not provisioned in v1: requires the ogb package to stage ogbn-arxiv under networks/; see the adapter guide.",
    "huggingface_runtime": "Not provisioned in v1: native training/eval load HuggingFace datasets at runtime and need a pre-staged cache.",
    "kaggle": "Not provisioned in v1: upstream scripts/prepare.py needs Kaggle credentials and an interactive consent prompt, and generates the evaluator-private gold data from a held-out slice of the Kaggle data (scripts/answer.csv; identify-contrails: scripts/test_answer/).",
    "babylm_data": "Not provisioned in v1: upstream scripts/prepare.py downloads babylm_data.zip into env/; training and evaluation also load HuggingFace models at runtime and need a pre-staged cache.",
    "clrs_runtime_download": "Not provisioned in v1: native training downloads the full CLRS30 corpus mid-run; see the adapter guide for this task's further native quirks.",
}


class MLAgentBenchAdapter(Adapter):
    name = "mlagentbench"

    def _task_dir(self, task_id: str) -> Path:
        return self.source.repository / BENCHMARKS / task_id

    def enumerate_tasks(self):
        return [TaskSummary(id=task_id, study_id=f"mlagentbench:{spec['category']}",
                            domain=spec["domain"], title=spec["title"],
                            source_locator=f"{BENCHMARKS}/{task_id}/scripts/research_problem.txt")
                for task_id, spec in TASKS.items()]

    def pilot_task_ids(self):
        return ["cifar10", "vectorization"]

    def _pinned_file(self, task_id: str, relative: str) -> Path:
        # Re-hash on every call: a long-lived adapter must not trust a file it
        # verified once if the tree drifts between conversions.
        path = self._task_dir(task_id) / relative
        expected = PINNED.get(task_id, {}).get(relative)
        if expected is not None and sha256(path) != expected:
            raise ValueError(f"{task_id}/{relative} changed upstream; re-curation required")
        return path

    def _facts(self, task_id: str) -> list[Fact]:
        if task_id not in PINNED:
            return []
        revision = self.source.revision

        def fact(key, topic, text, kind, relative, locator):
            path = self._pinned_file(task_id, relative)
            return Fact(id=f"{task_id}.{key}", topic=topic, text=text, kind=kind,
                        review_status="reviewed",
                        source=Provenance(source_path=f"{BENCHMARKS}/{task_id}/{relative}",
                                          revision=revision, locator=locator, sha256=sha256(path)))
        if task_id == "vectorization":
            return [
                fact("numpy_only", "constraints",
                     "Only the numpy library and vectorisation may be used to speed up the "
                     "forward computation, targeting train.py lines 105 to 123, and the run "
                     "time must be stored in submission.csv as shown in train.py.",
                     "fixed_requirement", "scripts/research_problem.txt", "full text"),
                fact("starter_semantics", "starter_implementation",
                     "The starter Conv2DLayer pads only the height/width axes of the "
                     "[batch, height, width, channels] input and adds one bias value per "
                     "filter inside each window step; a faithful speedup must preserve "
                     "these semantics.",
                     "context", "env/train.py", "add_padding line 16; biases line 56; convolution_step line 62"),
                fact("measurement_setup", "measurement_setup",
                     "The measured computation is a single forward pass over a fixed random "
                     "batch of shape (32, 64, 64, 3) through a Conv2DLayer with 8 filters, "
                     "kernel size 3, stride 2 and padding 2.",
                     "context", "env/train.py", "lines 133-136"),
            ]
        return [
            fact("epoch_budget", "constraints",
                 "Training epochs must stay within 10, and per-class probabilities for the "
                 "test set must be saved to submission.csv in the format shown in train.py.",
                 "fixed_requirement", "scripts/research_problem.txt", "full text"),
            fact("baseline_configuration", "starter_implementation",
                 "The starter trains a small two-convolution CNN (conv 3->6 and 6->16, three "
                 "linear layers) with SGD lr=0.1 momentum=0.9, batch size 128, for 5 epochs, "
                 "using only ToTensor and Normalize transforms; a comment mentions data "
                 "augmentation but none is applied, and both dataloaders drop the last "
                 "partial batch.",
                 "context", "env/train.py", "transforms lines 7-10; model lines 17-22; loaders lines 42-44; optimizer line 48; epochs line 67"),
            fact("dataset_layout", "measurement_setup",
                 "The task data is the standard torchvision CIFAR-10 dataset, train and "
                 "test splits, staged under data/ by the preparation step.",
                 "context", "scripts/prepare.py", "datasets.CIFAR10 train/test download"),
        ]

    def _assets(self, task_id: str) -> list[Asset]:
        spec = TASKS[task_id]
        assets = []
        env = self._task_dir(task_id) / "env"
        for path in sorted(env.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(env).as_posix()
            pinned = PINNED.get(task_id, {}).get(f"env/{relative}")
            assets.append(Asset(id=f"env-{relative}", source_path=str(path.resolve()),
                                target_path=relative, sha256=pinned or sha256(path)))
        if spec["data"] == "cifar10_archive":
            assets.append(Asset(id="cifar10-data", kind="directory",
                                source_path=str((self.source.assets / "cifar10/data").resolve()),
                                target_path="data", required=True,
                                acquisition=DATA_ACQUISITION[spec["data"]]))
        elif spec["data"] == "ogb_dataset":
            assets.append(Asset(id="ogbn-arxiv-networks", kind="directory",
                                source_path=str((self.source.assets / "ogbn-arxiv/networks").resolve()),
                                target_path="networks", required=True,
                                acquisition=DATA_ACQUISITION[spec["data"]]))
        elif spec["data"] != "none":
            # Kaggle/HuggingFace/CLRS staging layouts are finalized with their
            # acquisition implementations; a required-missing placeholder keeps
            # every unprovisioned requirement visible in readiness.json.
            assets.append(Asset(id="native-data-unprovisioned", kind="directory",
                                source_path=str((self.source.assets / task_id / "data").resolve()),
                                target_path="data", required=True,
                                acquisition=DATA_ACQUISITION[spec["data"]]))
        return assets

    def _read_only(self, task_id: str) -> list[str]:
        path = self._task_dir(task_id) / "scripts/read_only_files.txt"
        if task_id in PINNED and path.exists():
            self._pinned_file(task_id, "scripts/read_only_files.txt")
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text().splitlines() if line.strip()]

    def convert(self, task_id: str) -> Episode:
        if task_id in EXCLUDED:
            raise ValueError(f"{task_id} is excluded from conversion: {EXCLUDED[task_id]}")
        if task_id not in TASKS:
            raise ValueError(f"Unknown MLAgentBench task: {task_id}")
        if self.source.revision != SOURCE_REVISION:
            raise ValueError("MLAgentBench source revision differs from the reviewed pin; re-curation required")
        spec = TASKS[task_id]
        reviewed = task_id in PINNED
        question_file = (self._pinned_file(task_id, "scripts/research_problem.txt") if reviewed
                         else self._task_dir(task_id) / "scripts/research_problem.txt")
        eval_file = (self._pinned_file(task_id, "scripts/eval.py") if reviewed
                     else self._task_dir(task_id) / "scripts/eval.py")
        facts = self._facts(task_id)
        assets = self._assets(task_id)
        submission = {
            "stage": "final",
            "required_artifacts": ["submission.csv", "train.py"],
            "artifact_keys": "Use each exact workspace-relative path as its artifacts dictionary key.",
            "native_metric": f"{spec['metric']} ({'lower' if spec['direction'] == 'lower' else 'higher'} is better), "
                             "computed by the native task grader from the final workspace",
            "answer": "Describe the change you made and the measured outcome.",
        }
        public_format = PUBLIC_FORMATS.get(task_id)
        if public_format:
            submission["format"] = public_format["text"]
        environment = {
            "input_paths": [a.target_path for a in assets if a.visibility == "actor"],
            "read_only_paths": self._read_only(task_id),
            "requires_gpu": spec["requires_gpu"],
            "native_budget": dict(NATIVE_BUDGET),
            "budget_adaptation": "Altered-budget track: the shared PSB actor uses its configured "
                                 "step budget and a 600-second per-command limit instead of the "
                                 "native 50-step/5-hour run budget.",
            "runtime_policy": "Networkless Bubblewrap sandbox with a dedicated CPU Python "
                              "environment; GPU tasks are converted but not scheduled in v1.",
        }
        return Episode(
            id=f"mlagentbench:{task_id}", benchmark=self.name, source_task_id=task_id,
            study_id=f"mlagentbench:{spec['category']}", domain=spec["domain"],
            source_revision=self.source.revision,
            review_status="reviewed" if reviewed else "automated",
            public=PublicContext(
                question=question_file.read_text(),
                context="Improve the supplied starter workspace within its stated constraints. "
                        "A researcher is available for optional consultation and the configured "
                        "approach/result reviews; interaction never changes the task contract.",
                submission=submission, environment=environment,
                researcher_topics=sorted({f.topic for f in facts})),
            researcher=ResearcherContext(
                facts=facts,
                unknowns=["Reference results, baseline scores, hidden evaluator state, and unstated study facts."],
                notes=["Grader internals stay evaluator-private; facts cite only pinned task files."]),
            assets=assets,
            evaluator=EvaluatorSpec(
                kind="native_local_get_score", version=EVALUATOR_VERSION,
                entrypoint="personasciencebench.adapters.mlagentbench:MLAgentBenchAdapter.evaluate",
                reference={"eval_script_path": f"{BENCHMARKS}/{task_id}/scripts/eval.py",
                           "eval_script_sha256": sha256(eval_file),
                           "metric": {"name": spec["metric"], "direction": spec["direction"]},
                           "failure_sentinel": spec["failure_sentinel"],
                           "eval_cache": spec["eval_cache"]},
                config={"adaptations": [
                    "Direct get_score kernel call instead of the upstream eval driver",
                    "Execution inside the networkless Bubblewrap evaluator sandbox",
                    "Pre-warmed dataset cache copied beside the scored workspace",
                    "Baseline measured as the mean of repeated controller runs of the pristine "
                    "starter on the evaluation machine (native: mean over baseline agent runs; "
                    "plot.py also hardcodes reference constants for some tasks)",
                    "Single-episode scoring; the paper's 8-run success-rate aggregation happens "
                    "at the experiment level",
                ], "native_success_rule": "strict >10% directional relative improvement over the "
                                          "starter baseline (upstream plot.py:181, final_* variant "
                                          "plot.py:303-307)"}),
            conversion={
                "adapter_version": ADAPTER_VERSION,
                "public_contract_adaptations": [{
                    "field": "submission.format",
                    "change": "States the starter's output layout explicitly; the native task "
                              "only says 'as shown in train.py'.",
                    "source_path": f"{BENCHMARKS}/{task_id}/{public_format['source']}",
                    "locator": public_format["locator"],
                    "sha256": sha256(self._pinned_file(task_id, public_format["source"])),
                }] if public_format else [],
                "question_sha256": sha256(question_file),
                "eval_script_sha256": sha256(eval_file),
                "fact_pack_sha256": hashlib.sha256(json.dumps(
                    [f.model_dump(mode="json") for f in facts],
                    sort_keys=True).encode()).hexdigest(),
                "validation_method": "human_reviewed" if reviewed else "automated_structural",
                "context_status": "reviewed_task_facts" if facts else "no_permitted_guidance",
                "researcher_exclusive_information": False,
                "data_provisioning": spec["data"],
                "excluded_source_files": ["scripts/eval.py", "scripts/prepare.py"],
                "runtime_verified": False,
                "model_testing": "awaiting_user_confirmation",
            })

    def prepare_assets(self, task_id: str) -> list[Path]:
        """Stage downloadable pilot data under the assets directory, never inside
        the pinned checkout (upstream prepare.py writes into its own repo tree)."""
        if task_id != "cifar10" or TASKS.get(task_id, {}).get("data") != "cifar10_archive":
            return []
        root = self.source.assets / "cifar10"
        data = root / "data"
        archive = root / "cifar-10-python.tar.gz"
        receipt = root / "acquisition.json"
        if receipt.is_file() and (data / CIFAR10_ARCHIVE["extracted"]).is_dir():
            recorded = json.loads(receipt.read_text())
            if recorded.get("archive_sha256") == CIFAR10_ARCHIVE["sha256"]:
                return [data]
            raise ValueError("cifar10 assets exist with a different archive hash; remove them to re-acquire")
        root.mkdir(parents=True, exist_ok=True)
        if not archive.is_file():
            temporary = archive.with_suffix(".part")
            with urllib.request.urlopen(CIFAR10_ARCHIVE["url"], timeout=600) as stream, temporary.open("wb") as target:
                shutil.copyfileobj(stream, target)
            temporary.rename(archive)
        if sha256(archive) != CIFAR10_ARCHIVE["sha256"]:
            raise ValueError("cifar10 archive hash mismatch; delete the download and re-acquire")
        if data.exists():
            shutil.rmtree(data)
        with tarfile.open(archive) as bundle:
            for member in bundle.getmembers():
                name = PurePosixPath(member.name)
                if name.is_absolute() or ".." in name.parts or not member.isreg():
                    if member.isdir():
                        continue
                    raise ValueError(f"Unsafe archive member: {member.name}")
            bundle.extractall(data, filter="data")
        json.dump({"archive_sha256": CIFAR10_ARCHIVE["sha256"], "url": CIFAR10_ARCHIVE["url"],
                   "extracted": CIFAR10_ARCHIVE["extracted"]}, receipt.open("w"), indent=2)
        return [data]

    def _evaluator_python(self) -> Path:
        override = os.environ.get("PERSONASCIENCEBENCH_MLAB_EVAL_PYTHON")
        return Path(override) if override else Path(__file__).resolve().parents[3] / ".venv"

    def _run_driver(self, work: Path) -> dict:
        from personasciencebench.runtime import Sandbox
        return Sandbox(work, self._evaluator_python()).execute("python evaluate_driver.py",
                                                               timeout_seconds=1800)

    def evaluate(self, episode: Episode, submission, judge=None) -> EvaluationResult:
        check_submission(episode, submission)
        details = {"native_grader": "deterministic_get_score", "denominator": 1, "scored": 0}
        # Contract violations raise before any directory is created; everything
        # about the submission's content maps to an explicit status instead.
        for name in submission.artifacts:
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe MLAgentBench artifact key")
        if not submission.artifacts:
            return EvaluationResult(status="missing_submission", evaluator_version=EVALUATOR_VERSION,
                                    details=details)
        required = episode.public.submission.get("required_artifacts", ["submission.csv"])
        missing = [name for name in required if name not in submission.artifacts]
        if missing:
            return EvaluationResult(status="missing_submission", evaluator_version=EVALUATOR_VERSION,
                                    errors=[f"Required artifact absent: {name}" for name in missing],
                                    details=details)
        task_id = episode.source_task_id
        eval_file = self._task_dir(task_id) / "scripts/eval.py"
        reference = episode.evaluator.reference
        if not eval_file.is_file() or sha256(eval_file) != reference["eval_script_sha256"]:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Native grader changed or missing; re-curation required"],
                                    details=details)
        cache_name = reference.get("eval_cache")
        cache_source = None
        if cache_name:
            cache_source = {a.id: Path(a.source_path) for a in episode.assets}.get(f"{task_id}-{cache_name}")
            if cache_source is None or not cache_source.is_dir():
                return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                                        errors=[f"Evaluator-side dataset cache '{cache_name}' is not provisioned"],
                                        details=details)
        sealed = Path(next(iter(submission.artifacts.values()))).parent
        # A unique directory per evaluation keeps repeated grading of the same
        # sealed submission (regrade, CLI evaluate) from colliding.
        work = Path(tempfile.mkdtemp(prefix="mlagentbench_native_evaluation-", dir=sealed.parent))
        workspace = work / "workspace"
        workspace.mkdir()
        for name, source in submission.artifacts.items():
            destination = workspace / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        shutil.copyfile(eval_file, work / "native_eval.py")
        if cache_source is not None:
            shutil.copytree(cache_source, work / cache_name, symlinks=False)
        (work / "evaluate_driver.py").write_text(
            "import importlib.util, json\n"
            "spec = importlib.util.spec_from_file_location('native_eval', 'native_eval.py')\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "json.dump({'score': float(module.get_score('workspace'))}, open('native_score.json', 'w'))\n")
        try:
            receipt = self._run_driver(work)
        except (ValueError, RuntimeError, OSError) as exc:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Evaluator sandbox unavailable",
                                            f"{type(exc).__name__}: {exc}"],
                                    details={**details, "evaluator_directory": str(work)})
        (work / "execution.json").write_text(json.dumps(receipt, indent=2))
        details.update(evaluator_directory=str(work),
                       eval_script_sha256=reference["eval_script_sha256"],
                       execution_receipt={key: receipt[key] for key in
                                          ("exit_code", "timeout", "duration")})
        output = work / "native_score.json"
        if receipt["exit_code"] != 0 or not output.exists():
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Native get_score execution failed",
                                            receipt["stderr"][-2000:]],
                                    details=details)
        score = json.loads(output.read_text())["score"]
        sentinel = reference.get("failure_sentinel")
        if sentinel is not None and score == sentinel:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Native grader returned its failure sentinel "
                                            "(the submission artifact was unparseable)"],
                                    details={**details, "native_sentinel": sentinel})
        details["scored"] = 1
        return EvaluationResult(status="scored", evaluator_version=EVALUATOR_VERSION,
                                metrics={"native_score": score,
                                         "metric_name": reference["metric"]["name"],
                                         "metric_direction": reference["metric"]["direction"]},
                                details=details)

    def measure_baseline(self, episode: Episode, output: Path, *, runs: int = 3,
                         timeout_seconds: int = 1800) -> dict:
        """Controller-only baseline receipt: run the pristine starter and score it.

        The receipt is evaluator-private material; never mount it into an actor
        workspace or disclose it through the researcher.
        """
        if runs < 1:
            raise ValueError("Baseline needs at least one run")
        task_id = episode.source_task_id
        # Same fail-closed rule as evaluate(): never execute a drifted grader or
        # starter, and re-check the reviewed pins for pilot tasks.
        eval_file = self._task_dir(task_id) / "scripts/eval.py"
        eval_sha = sha256(eval_file)
        if eval_sha != episode.evaluator.reference["eval_script_sha256"]:
            raise ValueError("Native grader changed; re-curation required")
        for relative in PINNED.get(task_id, {}):
            self._pinned_file(task_id, relative)
        output.mkdir(parents=True, exist_ok=False)
        scores, receipts = [], []
        for index in range(runs):
            work = output / f"baseline-{index}"
            workspace = work / "workspace"
            shutil.copytree(self._task_dir(task_id) / "env", workspace, symlinks=False)
            cache_name = episode.evaluator.reference.get("eval_cache")
            if cache_name:
                source = {a.id: Path(a.source_path) for a in episode.assets}[f"{task_id}-{cache_name}"]
                shutil.copytree(source, workspace / cache_name, symlinks=False)
                shutil.copytree(source, work / cache_name, symlinks=False)
            shutil.copyfile(eval_file, work / "native_eval.py")
            (work / "evaluate_driver.py").write_text(
                "import importlib.util, json\n"
                "spec = importlib.util.spec_from_file_location('native_eval', 'native_eval.py')\n"
                "module = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(module)\n"
                "json.dump({'score': float(module.get_score('workspace'))}, open('native_score.json', 'w'))\n")
            from personasciencebench.runtime import Sandbox
            sandbox = Sandbox(work, self._evaluator_python())
            training = sandbox.execute("cd workspace && python train.py", timeout_seconds=timeout_seconds)
            scoring = sandbox.execute("python evaluate_driver.py", timeout_seconds=1800)
            if training["exit_code"] != 0 or scoring["exit_code"] != 0:
                raise RuntimeError(f"Baseline run {index} failed; see receipts under {work}")
            score = json.loads((work / "native_score.json").read_text())["score"]
            scores.append(score)
            receipts.append({"train": {k: training[k] for k in ("exit_code", "duration", "timeout")},
                             "score": score})
            (work / "receipts.json").write_text(json.dumps(receipts[-1], indent=2))
        receipt = {"episode_id": episode.id, "task_id": task_id, "runs": scores,
                   "mean": statistics.fmean(scores),
                   "stdev": statistics.stdev(scores) if len(scores) > 1 else None,
                   "metric": episode.evaluator.reference["metric"],
                   "evaluator_version": EVALUATOR_VERSION,
                   "eval_script_sha256": eval_sha,
                   "host": platform.node(),
                   "python_root": str(self._evaluator_python()),
                   "visibility": "evaluator_private", "details": receipts}
        (output / "baseline_receipt.json").write_text(json.dumps(receipt, indent=2))
        return receipt


def derive_improvement(baseline_receipt: dict, native_score: float) -> dict:
    """Native success arithmetic: strict >10% directional relative improvement."""
    mean = baseline_receipt["mean"]
    if mean == 0:
        raise ValueError("A zero baseline has no native relative improvement")
    relative = (native_score - mean) / mean
    if baseline_receipt["metric"]["direction"] == "lower":
        relative = -relative
    return {"baseline_mean": mean, "native_score": native_score,
            "relative_improvement": relative, "success_10pct": relative > 0.10}
