"""Offline conversion/information-boundary and mocked native-bridge checks."""

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None

from personasciencebench.adapters.base import SourceConfig, sha256
from personasciencebench.adapters.scienceagentbench import (
    BUNDLE, DATASET_REVISION, PARQUET, PILOTS, VERSION,
    ScienceAgentBenchAdapter, grade,
)
from personasciencebench.schema import Submission


@unittest.skipIf(pa is None, "ScienceAgentBench fixtures require optional pyarrow")
class ScienceAgentBenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = self.root / "assets"
        self.repository = self.root / "repository"
        self.repository.mkdir()
        self.rows = [self.row(key) for key in ("22", "45")]
        self.write_rows()
        self.adapter = ScienceAgentBenchAdapter(SourceConfig(
            self.repository, self.assets, "repository-revision", DATASET_REVISION))

    @staticmethod
    def row(key):
        return {
            "instance_id": int(key), "domain": "Synthetic unit fixture",
            "github_name": "fixture/repository", "task_inst": "A public scientific task.",
            "subtask_categories": "Data analysis",
            "domain_knowledge": " ".join(f[2] for f in PILOTS[key]["facts"]),
            "dataset_preview": "APPROVED_PREVIEW", "dataset_folder_tree": "UNREVIEWED_TREE_SECRET",
            "src_file_or_path": "PRIVATE_SOLUTION_LOCATOR",
            "gold_program_name": f"private_solution_{key}.py",
            "eval_script_name": f"private_evaluator_{key}.py",
            "output_fname": PILOTS[key]["output"],
            "extra_nested_reference": {"answer": "NESTED_GOLD_SECRET"},
        }

    def write_rows(self):
        path = self.assets / PARQUET
        path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pylist(self.rows), path)

    def submission(self, episode):
        self.program = self.root / "solution.py"
        self.program.write_text("# synthetic fixture; never executed\n")
        self.artifact = self.root / "artifact.bin"
        self.artifact.write_bytes(b"synthetic artifact, never scientifically scored")
        self.execution = self.root / "controller_execution.json"
        self.execution.write_text(json.dumps({
            "episode_id": episode.id, "stage": "final", "status": "completed", "exit_code": 0,
            "program_sha256": sha256(self.program),
            "artifacts": {episode.evaluator.config["expected_output"]: sha256(self.artifact)},
        }))
        return Submission(
            episode_id=episode.id,
            artifacts={"solution.py": str(self.program),
                       episode.evaluator.config["expected_output"]: str(self.artifact)},
            payload={"controller_execution_receipt": str(self.execution)},
        )

    def provision(self, episode):
        bundle = self.assets / BUNDLE
        script = bundle / "eval_programs" / episode.evaluator.reference["native_eval_script"]
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("# Synthetic verifier placeholder; never executed\n")
        (bundle / "provisioning.json").write_text(json.dumps({
            "split": "verified", "dataset_revision": DATASET_REVISION,
            "archive_sha256": "a" * 64, "evaluator_image": "unit-fixture@sha256:" + "b" * 64,
            "reviewed_evaluators": {episode.source_task_id: {"script_sha256": sha256(script), "dependencies": {}}},
        }))
        return bundle

    def test_conversion_is_allowlisted_and_separates_private_fields(self):
        self.assertEqual(self.adapter.pilot_task_ids(), ["22", "45"])
        self.assertEqual(len(self.adapter.enumerate_tasks()), 2)
        episode = self.adapter.convert("22")
        actor = json.dumps(episode.actor_input())
        researcher = episode.researcher.model_dump_json()
        for hidden in ("PRIVATE_SOLUTION_LOCATOR", "NESTED_GOLD_SECRET", "UNREVIEWED_TREE_SECRET",
                       "private_evaluator_22.py", "private_solution_22.py"):
            self.assertNotIn(hidden, actor)
            self.assertNotIn(hidden, researcher)
        self.assertNotIn(PILOTS["22"]["facts"][0][2], actor)
        self.assertIn("APPROVED_PREVIEW", actor)
        self.assertEqual(episode.public.question, "A public scientific task.")
        self.assertEqual(episode.evaluator.reference["source_solution_locator"], "PRIVATE_SOLUTION_LOCATOR")
        self.assertEqual(len([a for a in episode.assets if a.visibility == "actor"]), 2)
        self.assertTrue(all(f.review_status == "reviewed" and f.source.sha256 for f in episode.researcher.facts))

    def test_psychology_advice_is_not_a_fixed_requirement(self):
        episode = self.adapter.convert("45")
        self.assertEqual([fact.kind for fact in episode.researcher.facts], ["context", "optional_advice"])
        self.assertNotEqual(episode.study_id, self.adapter.convert("22").study_id)

    def test_unreviewed_task_revision_and_changed_excerpt_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "reviewed interactive"):
            self.adapter.convert("1")
        self.adapter._load_rows()["22"]["domain_knowledge"] = "Changed scientific facts"
        with self.assertRaisesRegex(ValueError, "excerpt changed"):
            self.adapter.convert("22")
        other = ScienceAgentBenchAdapter(SourceConfig(self.repository, self.assets, "repo", "other-data-revision"))
        with self.assertRaisesRegex(ValueError, "re-reviewed"):
            other.convert("45")

    def test_plan_and_wrong_episode_cannot_be_native_scored(self):
        episode = self.adapter.convert("22")
        with self.assertRaisesRegex(ValueError, "plan"):
            self.adapter.evaluate(episode, Submission(episode_id=episode.id, stage="plan"))
        with self.assertRaisesRegex(ValueError, "episode ID"):
            self.adapter.evaluate(episode, Submission(episode_id="other"))

    def test_self_reported_scores_and_missing_result_remain_unscored(self):
        episode = self.adapter.convert("22")
        missing = self.adapter.evaluate(episode, Submission(episode_id=episode.id, payload={"success_rate": 1}))
        self.assertEqual(missing.status, "missing_submission")
        submission = self.submission(episode)
        submission.payload["success_rate"] = 1
        result = self.adapter.evaluate(episode, submission)
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.metrics, {})
        output = self.root / "private_result.json"
        with patch("subprocess.run", side_effect=AssertionError("Request construction must be offline")):
            request = self.adapter.evaluation_request(episode, submission, output)
        self.assertIn("grade", request.argv)
        self.assertIn(str(self.assets / BUNDLE / "provisioning.json"), request.required_paths)
        self.assertFalse(output.exists())
        self.assertEqual(self.adapter.evaluate(episode, submission).status, "blocked")

    def test_registered_receipt_is_bound_to_identity_and_artifact_hashes(self):
        episode = self.adapter.convert("45")
        submission = self.submission(episode)
        output = self.root / "result.json"
        self.adapter.evaluation_request(episode, submission, output)
        result = {"episode_id": "wrong", "evaluator_version": VERSION,
                  "program_sha256": sha256(self.program), "artifact_sha256": sha256(self.artifact),
                  "status": "scored", "success_rate": 1}
        output.write_text(json.dumps(result))
        self.assertEqual(self.adapter.evaluate(episode, submission).status, "error")
        result["episode_id"] = episode.id
        output.write_text(json.dumps(result))
        self.assertEqual(self.adapter.evaluate(episode, submission).metrics["success_rate"], 1)
        self.artifact.write_bytes(b"changed after evaluation")
        self.assertEqual(self.adapter.evaluate(episode, submission).status, "error")

    def test_bridge_preserves_native_failure_and_never_mounts_program(self):
        episode = self.adapter.convert("22")
        submission = self.submission(episode)
        bundle = self.provision(episode)
        output = self.root / "native_receipt.json"
        self.adapter.evaluation_request(episode, submission, output)

        def fake_docker(argv, **kwargs):
            self.assertEqual(argv[:3], ["docker", "run", "--rm"])
            self.assertIn("--network=none", argv)
            self.assertIn("--read-only", argv)
            self.assertNotIn(str(self.program), " ".join(argv))
            receipt_mount = next(arg for arg in argv if arg.startswith("type=bind,") and arg.endswith("dst=/receipt"))
            receipt_dir = Path(receipt_mount.split("src=", 1)[1].split(",dst=", 1)[0])
            (receipt_dir / "native_result.json").write_text(json.dumps({
                "status": "scored", "success_rate": 0, "log_info": "Synthetic unit-fixture failure",
            }))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=fake_docker) as mocked:
            grade(bundle, "22", self.program, self.artifact, self.execution,
                  episode.evaluator.reference["native_eval_script"], output)
        mocked.assert_called_once()
        result = self.adapter.evaluate(episode, submission)
        self.assertEqual(result.status, "scored")
        self.assertEqual(result.metrics, {"success_rate": 0, "valid_program": 1})
        self.assertEqual(result.details["codebert_score"], "not_computed")

    def test_bridge_fails_before_execution_for_wrong_bundle_or_stale_receipt(self):
        episode = self.adapter.convert("45")
        self.submission(episode)
        bundle = self.provision(episode)
        provision_path = bundle / "provisioning.json"
        provision = json.loads(provision_path.read_text())
        provision["split"] = "validation"
        provision_path.write_text(json.dumps(provision))
        with patch("subprocess.run", side_effect=AssertionError("Must not execute")):
            with self.assertRaisesRegex(ValueError, "verified artifact bundle"):
                grade(bundle, "45", self.program, self.artifact, self.execution,
                      episode.evaluator.reference["native_eval_script"], self.root / "unused.json")
            self.program.write_text("# changed program")
            with self.assertRaisesRegex(ValueError, "does not attest"):
                grade(bundle, "45", self.program, self.artifact, self.execution,
                      episode.evaluator.reference["native_eval_script"], self.root / "unused.json")

    def sandbox_fixture(self):
        episode = self.adapter.convert("22")
        bundle = self.provision(episode)
        reference = bundle / "eval_programs/gold_results/synthetic.bin"
        reference.parent.mkdir()
        reference.write_bytes(b"PRIVATE_REFERENCE_CANARY")
        path = bundle / "provisioning.json"
        manifest = json.loads(path.read_text())
        manifest["reviewed_evaluators"]["22"]["dependencies"] = {
            "eval_programs/gold_results/synthetic.bin": sha256(reference)}
        path.write_text(json.dumps(manifest))
        for name in PILOTS["22"]["files"]:
            source = bundle / "datasets" / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(b"public input fixture")
        episode = self.adapter.convert("22")
        return episode, self.submission(episode)

    def test_sandbox_replay_separates_private_gold_and_reports_output_mismatch(self):
        from personasciencebench.scienceagentbench_runtime import RESULT_MARKER
        episode, submission = self.sandbox_fixture()
        expected = episode.evaluator.config["expected_output"]

        class FakeSandbox:
            def __init__(inner, workspace, python_root):
                inner.workspace = workspace

            def check(inner):
                return {"isolation_ok": True}

            def execute(inner, command, **kwargs):
                if inner.workspace.name == "program_replay":
                    self.assertTrue((inner.workspace / "solution.py").is_file())
                    self.assertFalse((inner.workspace / "benchmark/eval_programs").exists())
                    (inner.workspace / expected).write_bytes(b"fresh independent replay")
                    stdout = ""
                else:
                    self.assertFalse((inner.workspace / "solution.py").exists())
                    self.assertFalse((inner.workspace / "benchmark/datasets").exists())
                    self.assertTrue((inner.workspace / "benchmark/eval_programs/gold_results/synthetic.bin").is_file())
                    stdout = RESULT_MARKER + json.dumps({"status": "scored", "success_rate": 0})
                return {"exit_code": 0, "timeout": False, "stdout": stdout, "stderr": ""}

        with patch("personasciencebench.scienceagentbench_runtime.Sandbox", FakeSandbox), \
             patch("personasciencebench.scienceagentbench_runtime.NativeVerifierSandbox", FakeSandbox):
            result = self.adapter.evaluate_in_sandbox(episode, submission, self.root, self.root / "evaluation")
        self.assertEqual(result.status, "scored")
        self.assertEqual(result.metrics, {"valid_program": 1, "success_rate": 0})
        self.assertFalse(result.details["replayed_output_matches_submission"])
        self.assertEqual(self.artifact.read_bytes(), b"synthetic artifact, never scientifically scored")
        self.assertIsNotNone(result.details["output_mismatch"])

    def test_sandbox_startup_failure_has_no_scientific_score(self):
        episode, submission = self.sandbox_fixture()
        with patch("personasciencebench.scienceagentbench_runtime.Sandbox") as sandbox:
            sandbox.return_value.check.side_effect = RuntimeError("namespace denied")
            result = self.adapter.evaluate_in_sandbox(episode, submission, self.root, self.root / "evaluation")
        self.assertEqual(result.status, "error")
        self.assertEqual(result.metrics, {})
        sandbox.return_value.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
