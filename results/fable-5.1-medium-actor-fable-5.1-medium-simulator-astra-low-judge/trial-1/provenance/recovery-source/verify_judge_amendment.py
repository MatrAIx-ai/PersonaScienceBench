"""Audit the approved judge recovery against original inputs and transmitted calls."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def object_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode())


def key(row):
    return tuple(row[field] for field in ("source", "task_id", "arm"))


def main():
    approval = read(ROOT / "judge_cap_approval.json")
    assert approval["approved"] is True and approval["approver"] == "Robert"
    assert approval["remaining_native_judge_cap"] == 4096
    for name, expected in approval["approved_file_sha256"].items():
        assert sha((ROOT / name).read_bytes()) == expected
    previous = read(ROOT / "judge_recovery/results.json")
    pending = {key(row): row for row in previous if row["status"] == "judge_pending"}
    assert len(pending) == 7 and sorted(pending) == [tuple(k) for k in approval["slots"]]
    current = read(ROOT / "judge_recovery_cap4096/results.json")
    assert len(current) == 7 and {key(row) for row in current} == set(pending)
    inventory = {key(row): row for row in read(ROOT / "failure_inventory.json")}
    evaluations = {
        key(read(path)): path
        for path in (ROOT / "judge_recovery_cap4096").glob("*/*/evaluation.json")
    }
    totals = Counter()
    slot_reports = []
    for row in current:
        k = key(row)
        assert row["status"] == "recovered" and row["evaluation"]["status"] == "scored"
        assert row["actor_rerun"] is False
        assert row["evaluation"]["details"]["judge_recovery"]["caps_changed"] is True
        saved_approval = dict(row["budget_amendment"])
        assert saved_approval.pop("approval_file_sha256") == sha((ROOT / "judge_cap_approval.json").read_bytes())
        assert saved_approval == approval
        assert datetime.fromisoformat(row["created_at"]) >= datetime.fromisoformat(approval["received_at"])
        assert row["script_sha256"] == approval["approved_file_sha256"]["recover_judges_v2.py"]
        case = Path(inventory[k]["case_path"])
        unchanged = {
            "episode_sha256": case / "controller/episode.private.json",
            "submission_sha256": case / "controller/submission.json",
            "source_api_log_sha256": case / "controller/api_calls.private.jsonl",
            "original_result_sha256": case / "result.json",
            "config_sha256": ROOT.parent / "actor32768/run/configs" / (row["arm"] + ".shared.json"),
        }
        for field, path in unchanged.items():
            assert row[field] == pending[k][field] == sha(path.read_bytes()), (k, field)
        submission = read(unchanged["submission_sha256"])
        assert row["artifact_hashes"] == pending[k]["artifact_hashes"]
        for name, expected in row["artifact_hashes"].items():
            assert sha(Path(submission["artifacts"][name]).read_bytes()) == expected
            totals["artifacts_verified"] += 1
        source_lines = unchanged["source_api_log_sha256"].read_text().splitlines(keepends=True)
        source_judge = [json.loads(line) for line in source_lines if json.loads(line).get("role") == "judge"]
        directory = evaluations[k].parent
        assert read(evaluations[k]) == row
        receipts = lines(directory / "replay_receipts.jsonl")
        api = lines(directory / "api_calls.private.jsonl")
        wire = lines(directory / "wire_calls.private.jsonl")
        cached = [item for item in receipts if not item["new_model_call"]]
        fresh = [item for item in receipts if item["new_model_call"]]
        assert len(cached) == row["cached_calls"] == row["reused_calls"] == len(source_judge)
        assert len(fresh) == len(wire) == row["fresh_calls"]
        assert len(api) == len(receipts) == len(cached) + len(fresh)
        prior_directory = ROOT / "judge_recovery" / directory.relative_to(ROOT / "judge_recovery_cap4096")
        previous_fresh = lines(prior_directory / "wire_calls.private.jsonl")
        first_native = api[len(cached)]["response"]["_native_requested_responses_request"]
        assert first_native == previous_fresh[0]["request"]
        for index, item in enumerate(cached):
            assert item["call"] == index + 1
            original_line = source_lines[item["source_line"] - 1]
            original = json.loads(original_line)
            assert item["source_line_sha256"] == sha(original_line.encode())
            assert original == source_judge[index]
            assert api[index]["recovery_reused"] is True
            assert api[index]["response"] == original["response"]
            assert item["wire_request_sha256"] == object_sha(original["response"]["_responses_request"])
        for index, (item, call) in enumerate(zip(fresh, wire)):
            assert item["call"] == len(cached) + index + 1
            entry = api[len(cached) + index]
            assert entry["recovery_reused"] is False
            request, response = call["request"], call["response"]
            native = entry["response"]["_native_requested_responses_request"]
            expected = dict(native)
            assert native["max_output_tokens"] in (250, 4096)
            expected["max_output_tokens"] = 4096
            assert request == expected == entry["response"]["_responses_request"]
            assert response == entry["response"]["_responses_response"]
            assert request["model"] == response["model"] == "us.openai.gpt-6-astra"
            assert request["reasoning"]["effort"] == "low"
            assert response["status"] == "completed"
            assert request["max_output_tokens"] == item["transmitted_max_output_tokens"] == 4096
            assert native["max_output_tokens"] == item["native_max_output_tokens"]
            assert object_sha(request) == item["transmitted_request_sha256"] == entry["transmitted_request_sha256"]
            assert object_sha(native) == item["native_request_sha256"]
            totals["amended_helper_calls"] += native["max_output_tokens"] == 250
            totals["transport_retries"] += call["transport_retries"]
        totals["original_prefix_calls_reused"] += len(cached)
        totals["fresh_calls"] += len(fresh)
        slot_reports.append({
            "slot": list(k), "status": row["status"],
            "reused_calls": len(cached), "fresh_calls": len(fresh),
            "original_inputs_unchanged": True,
            "first_native_request_matches_unchanged_cap_recovery": True,
        })
    report = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "approved_slots": 7, "recovered_slots": len(current), "actor_reruns": 0,
        "actual_judge_model": "us.openai.gpt-6-astra", "reasoning_effort": "low",
        "fresh_call_cap": 4096, **totals, "slots": slot_reports,
        "scope": "Full wire equality and input immutability checked against retained private native logs; the portable bundle verifier separately checks authorization, cohort membership and call metadata hashes.",
        "verifier_sha256": sha(Path(__file__).read_bytes()),
    }
    (ROOT / "judge_cap4096_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "slots"}, indent=2))


if __name__ == "__main__":
    main()
