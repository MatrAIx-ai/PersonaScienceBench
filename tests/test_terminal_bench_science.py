"""Offline task-boundary and mocked Harbor replay checks; no scientific runs."""

import asyncio
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from personasciencebench.adapters.base import SourceConfig
from personasciencebench.adapters.terminal_bench_science import (
    HBV, ODE, PILOTS, TerminalBenchScienceAdapter, replay_submission, verify,
)
from personasciencebench.schema import Submission


class TerminalBenchScienceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        for task_id in (HBV, ODE):
            task = self.repo / "tasks" / task_id
            task.mkdir(parents=True)
            (task / "instruction.md").write_text("PUBLIC INSTRUCTION: preserve criteria and output paths.\n")
            description = PILOTS[task_id]["facts"][0][4] if task_id == HBV else "Public ODE description"
            (task / "task.toml").write_text(
                'schema_version = "1.0"\nartifacts = ["/results"]\n'
                f'[task]\nname = "terminal-bench-science/{task.name}"\ndescription = {json.dumps(description)}\n'
                '[metadata]\ndomain = "fixture domain"\n'
                '[agent]\ntimeout_sec = 28800.0\n'
                '[environment]\ncpus=4\nmemory_mb=8192\nstorage_mb=10240\ngpus=0\nnetwork_mode="public"\n'
                '[verifier]\ntimeout_sec=300.0\nenvironment_mode="separate"\n'
                '[verifier.environment]\nnetwork_mode="no-network"\n')
            (task / "README.md").write_text(
                "# Fixture\n\n## Difficulty\n" + " ".join(fact[4] for fact in PILOTS[task_id]["facts"])
                + "\n## Reference solution\nSECRET_REFERENCE_SOLUTION\n")
            for name in PILOTS[task_id]["files"]:
                path = task / "environment/data" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Synthetic public input; never scientifically executed")
            for folder in ("tests", "solution"):
                (task / folder).mkdir()
                (task / folder / "private.txt").write_text("HIDDEN_REFERENCE_VALUE")
        fixture = self.repo / "ci_checks/test-tasks/intentional-failure/task.toml"
        fixture.parent.mkdir(parents=True)
        fixture.write_text("This must never be parsed as an active scientific task")
        self.adapter = TerminalBenchScienceAdapter(SourceConfig(self.repo, self.root / "assets", "pinned-revision"))

    def submission(self, episode):
        artifacts = {}
        for index, target in enumerate(PILOTS[episode.source_task_id]["outputs"]):
            path = self.root / f"submitted_{index}"
            path.write_text("Synthetic unit fixture, not a benchmark answer")
            artifacts[target] = str(path)
        return Submission(episode_id=episode.id, artifacts=artifacts)

    def request(self, task_id=ODE):
        episode = self.adapter.convert(task_id)
        submission = self.submission(episode)
        output = self.root / "receipt.json"
        with patch("subprocess.run", side_effect=AssertionError("Construction must not execute")):
            request = self.adapter.evaluation_request(episode, submission, output)
        manifest = Path(request.argv[request.argv.index("--manifest") + 1])
        config = Path(request.argv[request.argv.index("--config") + 1])
        return episode, submission, output, manifest, config

    def test_active_inventory_and_public_input_preserve_boundaries(self):
        self.assertEqual(len(self.adapter.enumerate_tasks()), 2)
        self.assertEqual(self.adapter.pilot_task_ids(), [HBV, ODE])
        for task_id in (HBV, ODE):
            episode = self.adapter.convert(task_id)
            self.assertEqual(episode.public.question, "PUBLIC INSTRUCTION: preserve criteria and output paths.\n")
            self.assertEqual(episode.public.environment["agent_timeout_seconds"], 28800)
            for exported in (json.dumps(episode.actor_input()), episode.researcher.model_dump_json()):
                self.assertNotIn("SECRET_REFERENCE_SOLUTION", exported)
                self.assertNotIn("HIDDEN_REFERENCE_VALUE", exported)
            self.assertTrue(all("/environment/data/" in asset.source_path for asset in episode.assets))
        self.assertEqual(self.adapter.convert(ODE).researcher.facts[1].kind, "optional_advice")

    def test_source_changes_and_unknown_tasks_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown Terminal-Bench-Science"):
            self.adapter.convert("another/task/name")
        path = self.repo / "tasks" / ODE / "README.md"
        path.write_text(path.read_text().replace("## Difficulty", "## Reference solution"))
        with self.assertRaises((ValueError, IndexError)):
            self.adapter.convert(ODE)

    def test_missing_submission_plan_and_self_reported_scores(self):
        episode = self.adapter.convert(HBV)
        result = self.adapter.evaluate(episode, Submission(episode_id=episode.id, payload={"reward": 1}))
        self.assertEqual(result.status, "missing_submission")
        with self.assertRaisesRegex(ValueError, "plan"):
            self.adapter.evaluate(episode, Submission(episode_id=episode.id, stage="plan"))
        result = self.adapter.evaluate(episode, self.submission(episode))
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.metrics, {})

    def test_request_seals_artifacts_and_replay_uploads_only_native_paths(self):
        episode, submission, output, manifest, config = self.request()
        self.assertFalse(output.exists())
        job = json.loads(config.read_text())
        self.assertEqual(job["retry"], {"max_retries": 0})
        self.assertIsNone(job["agents"][0]["name"])
        self.assertNotIn("override_timeout_sec", json.dumps(job))
        self.assertEqual(job["n_attempts"], 1)
        uploads = []

        class FakeEnvironment:
            async def exec(self, *, command):
                self.assertion = command
                return SimpleNamespace(return_code=0)

            async def upload_file(self, *, source_path, target_path):
                uploads.append((source_path, target_path))

        asyncio.run(replay_submission(FakeEnvironment(), manifest))
        self.assertEqual([target for _, target in uploads], PILOTS[ODE]["outputs"])
        sealed_root = output.with_suffix(".harbor").resolve()
        self.assertTrue(all(Path(source).resolve().is_relative_to(sealed_root)
                            for source, _ in uploads))
        original = Path(next(iter(submission.artifacts.values())))
        original.write_text("later actor modification")
        self.assertNotEqual(original.read_text(), uploads[0][0].read_text())

    def test_native_zero_reward_is_scored_and_wrong_task_is_rejected(self):
        episode, submission, output, manifest, config = self.request()
        job = json.loads(config.read_text())
        native_path = Path(job["jobs_dir"]) / job["job_name"] / "trial" / "result.json"

        def fake_harbor(argv, **kwargs):
            self.assertEqual(argv, ["harbor", "run", "-c", str(config)])
            native_path.parent.mkdir(parents=True)
            native_path.write_text(json.dumps({
                "task_name": "terminal-bench-science/ode-law-discovery",
                "verifier_environment_mode": "separate",
                "agent_info": {"name": "personasciencebench-sealed-submission"},
                "verifier_result": {"rewards": {"reward": 0}}, "exception_info": None,
            }))
            return SimpleNamespace(returncode=0)

        with patch("personasciencebench.adapters.terminal_bench_science.package_version", return_value="0.21.0"), \
             patch("subprocess.run", side_effect=fake_harbor):
            verify(manifest, config, output)
        result = self.adapter.evaluate(episode, submission)
        self.assertEqual(result.status, "scored")
        self.assertEqual(result.metrics, {"reward": 0})
        record = json.loads(output.read_text())
        record["episode_id"] = "different-episode"
        output.write_text(json.dumps(record))
        self.assertEqual(self.adapter.evaluate(episode, submission).status, "error")

    def test_mutated_native_package_cannot_be_evaluated(self):
        episode, submission, output, manifest, config = self.request()
        (self.repo / "tasks" / ODE / "tests/private.txt").write_text("Changed native verifier")
        with patch("subprocess.run", side_effect=AssertionError("Must reject before execution")):
            with self.assertRaisesRegex(ValueError, "task package changed"):
                verify(manifest, config, output)


if __name__ == "__main__":
    unittest.main()
