"""One judge-only repair of each audited grade, with exact ordered wire replay."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from personasciencebench.inference import OpenRouterClient, preflight
from personasciencebench.registry import load_adapter
from personasciencebench.schema import Episode, Submission

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / "checkout"
RUN = ROOT.parent / "actor32768/run"
OUT = ROOT / "judge_recovery"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def object_hash(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode())


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")


def one(row, catalog):
    case = Path(row["case_path"])
    output = OUT / case.name / row["arm"]
    output.mkdir(parents=True, exist_ok=False)
    episode_path = case / "controller/episode.private.json"
    submission_path = case / "controller/submission.json"
    episode = Episode.model_validate(read(episode_path))
    submission = Submission.model_validate(read(submission_path))
    hashes = read(case / "controller/submission_hashes.json")
    assert set(hashes) == set(submission.artifacts)
    for name, path in submission.artifacts.items():
        assert digest(Path(path).read_bytes()) == hashes[name], name
    config_path = RUN / "configs" / f'{row["arm"]}.shared.json'
    spec = read(config_path)["models"]["judge"]
    assert spec["provider"] == "bedrock" and spec["model"] == "us.openai.gpt-6-astra"
    assert spec["reasoning_effort"] == "low" and spec["max_tokens"] == 4096
    helper_settings = episode.evaluator.config["native_helper_settings"]
    assert helper_settings["variable_and_relation"]["max_tokens"] == 250
    assert helper_settings["decomposition_and_context"]["max_tokens"] == 4096
    cached = []
    source_log = case / "controller/api_calls.private.jsonl"
    for number, line in enumerate(source_log.open(), 1):
        entry = json.loads(line)
        if entry.get("role") == "judge":
            assert entry["response"]["choices"][0]["finish_reason"] == "stop"
            assert entry["response"]["_responses_response"]["status"] == "completed"
            cached.append((number, digest(line.encode()), entry))
    assert cached
    receipt = {
        "source": row["source"], "task_id": row["task_id"], "arm": row["arm"],
        "actor_attempt": row["attempt"], "actor_rerun": False,
        "policy": "Reuse the exact ordered completed wire-request prefix, then one fresh invocation per remaining native call; stop on the first failure.",
        "judge_spec": spec, "native_helper_settings": helper_settings,
        "config_sha256": digest(config_path.read_bytes()),
        "episode_sha256": digest(episode_path.read_bytes()),
        "submission_sha256": digest(submission_path.read_bytes()),
        "artifact_hashes": hashes, "source_api_log_sha256": digest(source_log.read_bytes()),
        "original_result_sha256": digest((case / "result.json").read_bytes()),
        "cached_calls": len(cached), "created_at": datetime.now(timezone.utc).isoformat(),
        "script_sha256": digest(Path(__file__).read_bytes()),
    }
    write(output / "inputs.json", receipt)
    index, live_count, pending_entry = 0, 0, None

    def record(value):
        nonlocal pending_entry
        if pending_entry is not None:
            original = pending_entry
            assert value["request"] == original["request"], "Generic request differs"
            assert value["requested_native_settings"] == original["requested_native_settings"]
            assert value["omitted_native_settings"] == original["omitted_native_settings"]
            pending_entry = None
            value["recovery_reused"] = True
        else:
            value["recovery_reused"] = False
        append(output / "api_calls.private.jsonl", value)

    judge = OpenRouterClient(**spec, role="judge", record=record,
                             supported_parameters=catalog["judge"]["supported_parameters"])
    actual_send = judge.bedrock._send

    def send(request):
        nonlocal index, live_count, pending_entry
        assert request["model"] == spec["model"] and request["reasoning"]["effort"] == "low"
        assert request["max_output_tokens"] in (250, 4096)
        request_hash = object_hash(request)
        if index < len(cached):
            number, line_hash, entry = cached[index]
            original_hash = object_hash(entry["response"]["_responses_request"])
            assert request == entry["response"]["_responses_request"]
            assert request_hash == original_hash
            index += 1
            pending_entry = entry
            append(output / "replay_receipts.jsonl", {
                "call": index, "source_line": number, "source_line_sha256": line_hash,
                "wire_request_sha256": request_hash, "new_model_call": False,
            })
            return entry["response"]["_responses_response"], 0
        live_count += 1
        append(output / "replay_receipts.jsonl", {
            "call": index + live_count, "wire_request_sha256": request_hash,
            "max_output_tokens": request["max_output_tokens"], "new_model_call": True,
        })
        raw, retries = actual_send(request)
        append(output / "wire_calls.private.jsonl", {
            "request": request, "response": raw, "transport_retries": retries,
        })
        return raw, retries

    judge.bedrock._send = send
    adapter = load_adapter("discoverybench", REPO / "external/sources", REPO / "manifests/sources.json")
    evaluation = adapter.evaluate(episode, submission, judge)
    evaluation.details.update(judge_model=spec["model"], judge_reasoning_effort="low",
                              judge_recovery={"reused_calls": index, "fresh_calls": live_count,
                                              "actor_rerun": False, "caps_changed": False})
    if judge.parameter_adaptations:
        evaluation.evaluator_version += "+openrouter-provider-defaults-v1"
        evaluation.details["judge_parameter_adaptations"] = judge.parameter_adaptations
        evaluation.details["native_sampling_settings_preserved"] = False
    if judge.format_adaptations:
        evaluation.evaluator_version += "+json-fence-v1"
        evaluation.details["transport_format_adaptations"] = judge.format_adaptations
    assert digest(episode_path.read_bytes()) == receipt["episode_sha256"]
    assert digest(submission_path.read_bytes()) == receipt["submission_sha256"]
    for name, path in submission.artifacts.items():
        assert digest(Path(path).read_bytes()) == hashes[name]
    result = {**receipt, "finished_at": datetime.now(timezone.utc).isoformat(),
              "reused_calls": index, "fresh_calls": live_count,
              "status": "recovered" if evaluation.status == "scored" else "judge_pending",
              "evaluation": evaluation.model_dump(mode="json")}
    write(output / "evaluation.json", result)
    print(json.dumps({key: result[key] for key in
                      ("task_id", "arm", "status", "reused_calls", "fresh_calls")}), flush=True)
    return result


def main():
    os.umask(0o077)
    rows = [row for row in read(ROOT / "failure_inventory.json") if row["category"] == "judge_only"]
    assert len(rows) == 9 and not OUT.exists()
    os.environ.update(read(RUN.parent / "pilot_launch.json")["nonsecret_environment_overrides"])
    os.environ["PSB_FATAL_API_FILE"] = str(RUN / "fatal_api.json")
    spec = read(RUN / "configs/persona_off.shared.json")["models"]["judge"]
    catalog = preflight({"judge": spec})
    OUT.mkdir()
    write(OUT / "plan.json", {
        "slots": [{k: r[k] for k in ("source", "task_id", "arm")} for r in rows],
        "workers": 2, "judge_spec": spec, "catalog": catalog,
        "original_actor_submissions_immutable": True,
        "restrictions": "No JavaScript/TypeScript, no servers/listeners, no RLScience cluster.",
        "retry_policy": "One fresh invocation at unchanged native settings after the exact completed prefix; no grade selection.",
    })
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(one, row, catalog) for row in rows]
        for job in as_completed(jobs):
            results.append(job.result())
            write(OUT / "results.json", results)
    return int(any(r["status"] != "recovered" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
