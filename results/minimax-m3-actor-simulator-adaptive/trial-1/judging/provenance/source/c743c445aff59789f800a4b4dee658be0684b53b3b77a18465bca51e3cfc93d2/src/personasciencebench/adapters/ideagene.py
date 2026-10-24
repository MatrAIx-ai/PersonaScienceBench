"""IG-Arena Question tasks with native, controller-only PES evaluation.

No upstream imports, network access or model calls occur during conversion.
"""

import hashlib
import math
from pathlib import Path
import re
import subprocess
import sys

from personasciencebench.adapters.base import Adapter, check_submission, read_json, sha256
from personasciencebench.packaging import write_json
from personasciencebench.schema import (
    Episode, EvaluationRequest, EvaluationResult, EvaluatorSpec, PublicContext,
    ResearcherContext, TaskSummary,
)

POLICY = "ideagene-question-review-v2"
REVISION = "938fa9edfe54bee9a78359b42810b9c20857e432"
SOURCE_TREE = "61507ee2964f6dd4fb365c5875505939b1cb1641"
SMOKE_IDS = ["cs_LLMReasoning", "biology_SingleCellFoundation"]
PILOT_IDS = [
    "biology_ProteinDesign",
    "biology_SingleCellFoundation",
    "chemistry_DrugDiscovery",
    "chemistry_Retrosynthesis",
    "climate_ClimateSimulation",
    "cs_LLMReasoning",
    "energy_SmartGridOptimization",
    "math_AutomatedTheoremProving",
    "medicine_MedicalFoundationModels",
    "physics_FusionPlasmaControl",
]
NATIVE_JUDGES = ["judge-gpt4o", "judge-gpt4o-mini", "judge-gpt4.1-mini"]
EVALUATOR_VERSION = f"ideagene-pes-v2@{REVISION}"
OPTIONAL_GENOME_DB = Path("gene_arena/genome_db/paper_gene_cards.json")


class IdeaGeneAdapter(Adapter):
    name = "ideagene"

    def task_path(self, task_id):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
            raise ValueError("Unsafe IdeaGene task ID")
        path = self.source.repository / "gene_arena/task" / f"{task_id}.json"
        if path.is_symlink() or not path.resolve().is_relative_to(self.source.repository.resolve()):
            raise ValueError("IdeaGene task path escapes the source repository")
        return path

    def _task(self, task_id):
        row = read_json(self.task_path(task_id))
        if row.get("trace_id") != task_id:
            raise ValueError("IdeaGene filename and native trace ID differ")
        for field in ("domain", "subfield", "open_question"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing native field: {field}")
        return row

    def enumerate_tasks(self):
        tasks = []
        for path in sorted((self.source.repository / "gene_arena/task").glob("*.json")):
            row = self._task(path.stem)
            tasks.append(TaskSummary(id=path.stem, study_id=path.stem, domain=row["domain"],
                                     title=row["subfield"], source_locator=f"gene_arena/task/{path.name}"))
        return tasks

    def pilot_task_ids(self):
        return list(PILOT_IDS)

    def convert(self, task_id):
        row = self._task(task_id)
        path = self.task_path(task_id)
        source_hash = sha256(path)
        # Explicit allowlist. In particular, do not export papers/genomes/edges,
        # frontier evidence, dynamics labels or nested gold/reference additions.
        return Episode(
            id=f"ideagene:{task_id}:Question", benchmark=self.name, source_task_id=task_id,
            study_id=task_id, domain=row["domain"], source_revision=self.source.revision,
            track="design_only", review_status="automated",
            public=PublicContext(
                question=row["open_question"], context=f"Domain: {row['domain']}. Subfield: {row['subfield']}. "
                "Propose a next-step research direction. This is IG-Arena Question: no literature "
                "library or lineage is supplied. Proposals are hypotheses, not executed experiments.",
                submission={"answer": "Report the approach or evidence in answer. At result stage put one complete "
                            "native-format JSON object in payload.proposal. It must include the six idea_genome fields, "
                            "evolution_rationale, validation_plan and known_unknowns. The serialized content is unchanged.",
                            "native_format": {"content": "serialized native-format proposal JSON"},
                            "recommended_sections": ["Idea Genome", "Evolution Rationale", "Validation plan"],
                            "required_artifacts": []},
                environment={"runtime": "text-only review; no actor shell, files, browser or retrieval tools",
                             "execution_required": False},
                researcher_topics=["research approach", "assumptions", "validation design"]),
            researcher=ResearcherContext(facts=[], unknowns=[
                "Actual data availability, hardware and research budget are unspecified.",
                "No experiment results, hidden lineage or evaluator references are available."],
                notes=["Empty source fact pack is intentional; general knowledge follows the common run policy."]),
            evaluator=EvaluatorSpec(kind="native_request", version=EVALUATOR_VERSION,
                entrypoint="gene_arena/run_arena.py:pes",
                reference={"task_path": str(path.resolve()), "task_sha256": source_hash},
                config={"setting": "Question", "scale": [0, 100], "judge_ids": NATIVE_JUDGES,
                        "metrics": ["pes", "heredity_score", "variation_score", "selection_score"],
                        "native_scoring_unchanged": True, "official_leaderboard_comparable": False}),
            conversion={"version": POLICY, "setting": "Question", "source_path": f"gene_arena/task/{path.name}",
                        "source_sha256": source_hash, "public_locators": ["/domain", "/subfield", "/open_question"],
                        "researcher_fact_pack": {"version": "empty-v1", "facts": [],
                            "sha256": hashlib.sha256(b"[]").hexdigest()},
                        "upstream_verified": row.get("verified"), "scientific_review": "not_independently_reviewed",
                        "changes": ["Add researcher-review-v2 approach/result checkpoints to native Question generation.",
                                    "Text-only actor; configurable dialogue budget. No language restriction added."],
                        "study_group_basis": "native lineage trace; cross-trace literature overlap not yet audited",
                        "runtime_verified": False, "native_evaluator_verified": False})

    def _check(self, episode, submission):
        check_submission(episode, submission)
        if episode.benchmark != self.name or episode.source_revision != self.source.revision:
            raise ValueError("IdeaGene episode source mismatch")
        if episode.source_revision != REVISION:
            raise ValueError("Unsupported IdeaGene evaluator revision")
        if episode.evaluator.version != EVALUATOR_VERSION:
            raise ValueError("Unknown IdeaGene evaluator version")
        if sha256(self.task_path(episode.source_task_id)) != episode.conversion["source_sha256"]:
            raise ValueError("Source task changed after conversion")
        if submission.stage != "final":
            raise ValueError("Only a completed design, not the approach checkpoint, can be evaluated")
        if not submission.answer.strip():
            raise ValueError("Missing proposal answer")
        if submission.artifacts or submission.payload:
            raise ValueError("Question proposals use answer only; artifact/payload submissions are unsupported")

    def evaluate(self, episode, submission, judge=None):
        self._check(episode, submission)
        return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
            errors=["Native PES has not run. Export a native request or use run-ideagene --evaluate-native."],
            details={"native_score": None, "external_native_judges": NATIVE_JUDGES,
                     "reason": "No proxy or researcher-acceptance score is substituted for PES."})

    def evaluation_request(self, episode, submission, output):
        self._check(episode, submission)
        root = output.resolve().parent / (output.stem + ".native")
        root.mkdir(parents=True, exist_ok=False)
        task_id = episode.source_task_id
        proposal = root / "ideas" / task_id / "submission_Question.json"
        write_json(proposal, {"content": submission.answer}, exclusive=True)
        score = root / "pes_eval" / task_id / "submission_Question.json"
        required = [self.task_path(task_id), self.source.repository / "gene_arena/run_arena.py",
                    self.source.repository / "gene_arena/population_evolving_score.py",
                    self.source.repository / "gene_arena/dynamics_eval.py",
                    self.source.repository / "gene_arena/arena_config.py"]
        genome_db = self.source.repository / OPTIONAL_GENOME_DB
        genome_db_locator = OPTIONAL_GENOME_DB.as_posix()
        genome_db_record = {
            "path": genome_db_locator,
            "status": "present" if genome_db.is_file() else "missing_task_json_fallback",
            "sha256": sha256(genome_db) if genome_db.is_file() else None,
        }
        request = EvaluationRequest(
            argv=[sys.executable, str(required[1].resolve()), "pes", "--results-dir", str(root),
                  "--tasks", task_id, "--participants", "submission", "--settings", "Question",
                  "--judge-models", *NATIVE_JUDGES], cwd=str(self.source.repository.resolve()),
            required_paths=[str(p.resolve()) for p in required],
            output_paths=[str(score), str(root / "scores/pes_scores.json")],
            notes=["Executes trusted pinned native evaluator only; actor has no executable tools.",
                   "Native judges require API_KEY and upstream dependencies. No paid call during request construction.",
                   "Keep native defaults, no fallback judges or partial-judge scoring.",
                   "The upstream paper_gene_cards.json is optional; when absent, native PES uses gene cards "
                   "from the pinned task JSON as implemented by population_evolving_score.py."])
        write_json(output, request.model_dump(mode="json"), exclusive=True)
        write_json(root / "submission_provenance.json", {
            "episode_id": episode.id, "evaluator_version": EVALUATOR_VERSION,
            "submission_sha256": sha256(proposal), "source_sha256": sha256(self.task_path(task_id)),
            "source_revision": self.source.revision,
            "source_git_tree": SOURCE_TREE,
            "native_code_hashes": {str(p.relative_to(self.source.repository)): sha256(p)
                                   for p in required if p.is_file()},
            "optional_native_assets": {genome_db_locator: genome_db_record},
            "judge_ids": NATIVE_JUDGES}, exclusive=True)
        return request

    def collect_evaluation(self, request):
        try:
            detail = read_json(Path(request.output_paths[0]))
            summary = read_json(Path(request.output_paths[1]))
            if (summary.get("n_eval_files") != 1 or summary.get("n_incomplete_eval_files_skipped") != 0
                    or summary.get("n_incomplete_eval_files_included") != 0
                    or summary.get("expected_judge_ids") != NATIVE_JUDGES):
                raise ValueError("Native PES did not score exactly one complete three-judge record")
            metrics = {k: detail["scores"][k] for k in
                       ("pes", "heredity_score", "variation_score", "selection_score")}
            for value in metrics.values():
                if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
                    raise ValueError("Invalid native PES score")
            if summary["by_participant_setting"]["submission"]["Question"]["n"] != 1:
                raise ValueError("Native score denominator differs")
            return EvaluationResult(status="scored", evaluator_version=EVALUATOR_VERSION,
                                    metrics=metrics, details={"native_record": detail, "native_summary": summary,
                                        "metric_scale": "0–100", "official_leaderboard_comparable": False})
        except (OSError, ValueError, KeyError, TypeError) as error:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=[f"Native result incomplete/invalid: {type(error).__name__}"])

    def run_native(self, episode, submission, output, *, python=None, timeout=1800):
        import os
        request = self.evaluation_request(episode, submission, output)
        if python is not None:
            request.argv[0] = str(Path(python).resolve())
            write_json(output, request.model_dump(mode="json"))
        missing = [p for p in request.required_paths if not Path(p).is_file()]
        overrides = [k for k in os.environ if k.startswith("GENE_")]
        # Unknown native environment knobs can change the scorer silently.
        if missing or not os.environ.get("API_KEY") or overrides:
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["Native PES preflight blocked: missing assets, API_KEY or nondefault GENE_* environment."],
                details={"missing_paths": missing, "override_names": overrides, "request": str(output)})
        receipt = output.with_suffix(".execution.json")
        try:
            actual = subprocess.check_output(["git", "-C", str(self.source.repository), "rev-parse", "HEAD"],
                                             text=True, stderr=subprocess.PIPE).strip()
            actual_tree = subprocess.check_output(
                ["git", "-C", str(self.source.repository), "rev-parse", "HEAD^{tree}"],
                text=True, stderr=subprocess.PIPE).strip()
            changed = subprocess.check_output(["git", "-C", str(self.source.repository), "diff", "--name-only", "HEAD"],
                                              text=True, stderr=subprocess.PIPE).strip()
            if (actual != REVISION and actual_tree != SOURCE_TREE) or changed:
                return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                                        errors=["Native source revision or tracked files changed before evaluation."])
            done = subprocess.run(request.argv, cwd=request.cwd, capture_output=True,
                                  timeout=timeout, check=False)
            # Never persist raw exception/console text: providers may echo credentials.
            write_json(receipt, {"exit_code": done.returncode, "timeout_seconds": timeout,
                                "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
                                "stderr_sha256": hashlib.sha256(done.stderr).hexdigest()})
            if done.returncode != 0:
                return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                        errors=["Native PES process failed; see execution receipt."])
        except (OSError, subprocess.SubprocessError) as error:
            write_json(receipt, {"error_type": type(error).__name__, "timeout_seconds": timeout})
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Native PES process failed or timed out."])
        return self.collect_evaluation(request)
