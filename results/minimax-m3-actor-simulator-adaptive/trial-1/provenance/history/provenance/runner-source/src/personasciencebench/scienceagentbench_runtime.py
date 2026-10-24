"""Separate Bubblewrap program replay and native ScienceAgentBench verification.

This is a recorded environment adaptation of the verified benchmark. Native
evaluator modules are unchanged. Candidate code never sees private references;
artifact deserialization happens only inside the later, networkless verifier.
"""

from __future__ import annotations

import json
from pathlib import Path
import shlex
import shutil

from personasciencebench.adapters.base import check_submission, read_json, sha256
from personasciencebench.adapters.scienceagentbench import DATASET_REVISION, _plain_file
from personasciencebench.runtime import Sandbox
from personasciencebench.schema import Episode, EvaluationResult, Submission


RUNTIME_VERSION = "scienceagentbench-verified-split-execution-bubblewrap-v2"
RESULT_MARKER = "PSB_NATIVE_RESULT="


class NativeVerifierSandbox(Sandbox):
    """The grading script, submitted output, and references are read-only."""

    def _argv(self, command: str) -> list[str]:
        arguments = super()._argv(command)
        for index in range(len(arguments) - 2):
            if arguments[index:index + 3] == ["--bind", str(self.workspace), "/workspace"]:
                arguments[index] = "--ro-bind"
                return arguments
        raise ValueError("Native verifier workspace mount could not be made read-only")


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
    path.chmod(0o600)


def native_worker(script: str) -> str:
    """Trusted wrapper around the unchanged native eval(); all output is private."""
    return '''import contextlib, json, runpy, traceback
class BoundedLog:
    def __init__(self): self.text = ''; self.count = 0
    def write(self, value):
        self.count += len(value)
        self.text += value[:max(0, 12000-len(self.text))]
        return len(value)
    def flush(self): pass
log = BoundedLog()
result = {}
try:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        module = runpy.run_path(''' + repr("/workspace/benchmark/eval_programs/" + script) + ''')
        value = module['eval']()
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError('Native eval() did not return success and diagnostic')
        success, diagnostic = value
        if success not in (0, 1, False, True):
            raise ValueError('Native task success is not binary')
        result = {'status': 'scored', 'success_rate': int(success), 'log_info': str(diagnostic)}
except Exception as exc:
    result = {'status': 'native_exception', 'exception_type': type(exc).__name__,
              'error': str(exc), 'traceback': traceback.format_exc()}
result['private_stdout'] = log.text
result['private_stdout_characters'] = log.count
print(''' + repr(RESULT_MARKER) + ''' + json.dumps(result, allow_nan=False))
'''


def evaluate_in_sandbox(episode: Episode, submission: Submission, bundle: Path,
                        python_root: Path, output: Path) -> EvaluationResult:
    check_submission(episode, submission)
    key = episode.source_task_id
    if episode.benchmark != "scienceagentbench":
        raise ValueError("Unsupported verified ScienceAgentBench episode")
    expected = episode.evaluator.config["expected_output"]
    if not submission.artifacts.get("solution.py") or not submission.artifacts.get(expected):
        return EvaluationResult(status="missing_submission", evaluator_version=RUNTIME_VERSION,
                                errors=["A standalone program and its native output are required"])
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    try:
        bundle = bundle.resolve()
        provision = read_json(_plain_file(bundle / "provisioning.json"))
        if provision.get("split") != "verified" or provision.get("dataset_revision") != DATASET_REVISION:
            raise ValueError("Verified-bundle provenance differs from the annotation split")
        actor_inputs = {Path(asset.source_path).relative_to(bundle).as_posix(): asset.sha256
                        for asset in episode.assets if asset.visibility == "actor"
                        and Path(asset.source_path).is_relative_to(bundle)}
        for relative, episode_digest in actor_inputs.items():
            digest = provision.get("files", {}).get(relative, episode_digest)
            if digest is None or sha256(_plain_file(bundle / relative)) != digest:
                raise ValueError("Verified actor input changed after archive provisioning")
        reviewed = provision.get("reviewed_evaluators", {}).get(key, {})
        script = episode.evaluator.reference["native_eval_script"]
        verifier_source = _plain_file(bundle / "eval_programs" / script)
        if reviewed.get("script_sha256") != sha256(verifier_source):
            raise ValueError("Native evaluator source changed or lacks reviewed provenance")
        if "dependencies" not in reviewed:
            raise ValueError("Native evaluator dependency discovery has not been recorded")
        for relative, digest in reviewed["dependencies"].items():
            source = _plain_file(bundle / relative)
            if not source.is_relative_to(bundle) or sha256(source) != digest:
                raise ValueError("Private native evaluator dependency changed")
        replay = output / "program_replay"
        replay.mkdir(mode=0o700)
        program = _plain_file(Path(submission.artifacts["solution.py"]))
        submitted_artifact = _plain_file(Path(submission.artifacts[expected]))
        shutil.copyfile(program, replay / "solution.py")
        for asset in episode.assets:
            if asset.visibility != "actor":
                continue
            source = _plain_file(Path(asset.source_path))
            if asset.sha256 is None or sha256(source) != asset.sha256:
                raise ValueError("Native actor data lack a matching source hash")
            destination = replay / asset.target_path
            if not destination.resolve().is_relative_to(replay):
                raise ValueError("Actor input destination escapes the replay workspace")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        (replay / "pred_results").mkdir()
        sandbox = Sandbox(replay, python_root)
        _write(output / "program_sandbox_check.json", sandbox.check())
        execution = sandbox.execute("python -I solution.py", timeout_seconds=900)
        _write(output / "program_execution.private.json", execution)
        provenance = {"environment_adaptation": "Networkless Bubblewrap replaces upstream Docker/conda",
                      "program_sha256": sha256(program), "archive_sha256": provision["archive_sha256"],
                      "dataset_revision": DATASET_REVISION, "eval_script_sha256": sha256(verifier_source),
                      "actor_program_timeout_seconds": 900, "python_root": str(python_root.resolve()),
                      "runtime_dependency_check": provision.get("runtime_dependency_check"),
                      "codebert_score": "not_computed", "judge_model_used": False,
                      "native_quirks_preserved": ["PSS evaluator skips its first CSV row despite headerless instruction",
                                                  "Papyrus evaluator iterates reference rows without an extra-row gate"]}
        result_path = replay / expected
        if execution["exit_code"] != 0 or execution["timeout"] or not result_path.is_file():
            # The native benchmark assigns program/runtime/missing-output failures
            # scientific zero. Namespace startup failures were checked beforehand.
            result = EvaluationResult(status="scored", evaluator_version=RUNTIME_VERSION,
                                      metrics={"valid_program": 0, "success_rate": 0},
                                      details={**provenance, "score_denominator": 1,
                                               "program_execution_status": "timeout" if execution["timeout"] else "failed_or_missing_output",
                                               "private_execution_record": str(output / "program_execution.private.json")})
            _write(output / "evaluation.json", result.model_dump(mode="json"))
            return result
        artifact = _plain_file(result_path)
        if not artifact.is_relative_to(replay):
            raise ValueError("Replayed output escaped the public replay workspace")
        actual_hash, submitted_hash = sha256(artifact), sha256(submitted_artifact)
        receipt = {"episode_id": episode.id, "stage": "final", "status": "completed", "exit_code": 0,
                   "program_sha256": sha256(program), "artifacts": {expected: actual_hash},
                   "submitted_artifact_sha256": submitted_hash,
                   "replayed_output_matches_submission": actual_hash == submitted_hash}
        _write(output / "controller_execution_receipt.json", receipt)
        verifier = output / "native_verifier"
        verifier.mkdir(mode=0o700)
        references = {"eval_programs/" + script: sha256(verifier_source), **reviewed["dependencies"]}
        for relative in references:
            target = verifier / "benchmark" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundle / relative, target)
        sealed = verifier / expected
        sealed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(artifact, sealed)
        sealed.chmod(0o400)
        native_sandbox = NativeVerifierSandbox(verifier, python_root)
        _write(output / "verifier_sandbox_check.json", native_sandbox.check())
        command = "python -I -c " + shlex.quote(native_worker(script))
        native_run = native_sandbox.execute(command, timeout_seconds=300)
        _write(output / "native_execution.private.json", native_run)
        if native_run["exit_code"] != 0 or native_run["timeout"]:
            raise RuntimeError("Isolated native verification failed or timed out")
        lines = [line[len(RESULT_MARKER):] for line in native_run["stdout"].splitlines() if line.startswith(RESULT_MARKER)]
        if len(lines) != 1:
            raise RuntimeError("Missing or ambiguous native verifier result")
        native = json.loads(lines[0])
        _write(output / "native_result.private.json", native)
        if native["status"] == "native_exception":
            if native.get("exception_type") in {"ModuleNotFoundError", "ImportError", "MemoryError"}:
                raise RuntimeError("Native verifier environment lacks a required dependency or resource")
            # compute_scores.py catches evaluator exceptions and records valid=1,
            # success=0; preserve this behavior for invalid generated artifacts.
            score = 0
            native_status = "native_evaluator_exception"
        elif native["status"] == "scored" and native.get("success_rate") in (0, 1):
            score = native["success_rate"]
            native_status = "evaluated"
        else:
            raise ValueError("Unexpected native verifier result")
        result = EvaluationResult(
            status="scored", evaluator_version=RUNTIME_VERSION,
            metrics={"valid_program": 1, "success_rate": score},
            details={**provenance, "score_denominator": 1, "native_status": native_status,
                     "scientifically_scored_artifact": "fresh_program_replay",
                     "submitted_artifact_sha256": submitted_hash, "replayed_artifact_sha256": actual_hash,
                     "replayed_output_matches_submission": actual_hash == submitted_hash,
                     "output_mismatch": None if actual_hash == submitted_hash else
                     "Replayed output bytes differ from the immutable actor submission; both are retained and the native score applies to the replay.",
                     "native_diagnostic": native.get("log_info"),
                     "private_native_record": str(output / "native_result.private.json")})
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        result = EvaluationResult(status="error", evaluator_version=RUNTIME_VERSION,
                                  errors=[str(exc)], details={"score_denominator": 0})
    _write(output / "evaluation.json", result.model_dump(mode="json"))
    return result
