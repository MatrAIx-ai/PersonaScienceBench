"""Audit model/effort/caps and terminal stops without exporting private content."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
RUN = ROOT.parent / "actor32768/run"


def safe(value):
    return (re.sub(r"[^A-Za-z0-9_.-]", "_", value).strip(".")[:100] or "episode") + "-" + hashlib.sha256(value.encode()).hexdigest()[:12]


def case_path(row, attempt):
    key = safe(row["source"] + ":" + row["task_id"])
    name = row["task_id"].replace("/", "__") if row["source"] == "expbench" else key
    return RUN / "episodes" / key / row["arm"] / f"attempt-{attempt}" / "output" / name


def audit(row, attempt):
    case = case_path(row, attempt)
    path = case / ("api_calls.jsonl" if row["source"] == "expbench" else "controller/api_calls.private.jsonl")
    result = {key: row[key] for key in ("source", "task_id", "arm")}
    result.update(attempt=attempt, original_status=row["status"], calls={}, stops={},
                  unusual=[], mismatches=[], token_usage={}, wire_settings={},
                  log_present=path.is_file())
    if not path.exists():
        return result
    counts, stops, settings = Counter(), Counter(), Counter()
    tokens = Counter()
    file_hash = hashlib.sha256()
    requests = {}
    actor_responses = 0
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            file_hash.update(line)
            entry = json.loads(line)
            if entry.get("phase") == "request":
                requests[entry["call_id"]] = entry["payload"]
                continue
            response = entry.get("response")
            if not response:
                continue
            role = entry["role"]
            request = entry.get("request") or requests.get(entry.get("call_id"), {})
            native = response.get("_native_response") or response.get("_responses_response")
            wire = response.get("_native_request") or response.get("_responses_request")
            if not native or not wire:
                result["mismatches"].append({"line": number, "error": "missing_native_payload"})
                continue
            counts[role] += 1
            fable = role != "judge"
            expected_request = "us.anthropic.claude-fable-5-1" if fable else "us.openai.gpt-6-astra"
            expected_actual = "claude-fable-5-1" if fable else expected_request
            actual_model = native.get("model")
            effort = wire.get("output_config", {}).get("effort") if fable else wire.get("reasoning", {}).get("effort")
            cap = wire.get("max_tokens") if fable else wire.get("max_output_tokens")
            stop = native.get("stop_reason") if fable else native.get("status")
            settings[f"{role}|{actual_model}|{effort}|{cap}"] += 1
            stops[f"{role}|{stop}"] += 1
            if request.get("model") != expected_request or actual_model != expected_actual or effort != ("medium" if fable else "low"):
                result["mismatches"].append({"line": number, "role": role,
                                            "requested_model": request.get("model"), "actual_model": actual_model,
                                            "effort": effort})
            if (role == "actor" and cap != 32768) or (role == "researcher" and cap != 8192):
                result["mismatches"].append({"line": number, "role": role, "unexpected_cap": cap})
            if fable and wire.get("thinking") != {"type": "adaptive"}:
                result["mismatches"].append({"line": number, "role": role, "thinking": wire.get("thinking")})
            usage = native.get("usage") or {}
            for token_key in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                tokens[f"{role}|{token_key}"] += usage.get(token_key, 0) or 0
            if stop not in ("end_turn", "tool_use", "completed"):
                result["unusual"].append({
                    "line": number, "role": role, "stop_reason": stop, "cap": cap,
                    "usage": usage, "prior_actor_responses": actor_responses,
                    "refusal_phase": ("pre_actor" if actor_responses == 0 else "mid_episode") if role == "researcher" else None,
                    "native_response_sha256": hashlib.sha256(json.dumps(native, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                })
            if role == "actor":
                actor_responses += 1
    result.update(calls=dict(counts), stops=dict(stops), wire_settings=dict(settings),
                  token_usage=dict(tokens), source_api_sha256=file_hash.hexdigest())
    return result


def main():
    states = json.loads((ROOT / "all_states.before.json").read_text())
    rows = [audit(state, state["attempt"]) for state in states]
    summary = {"slots": len(rows), "logged_slots": sum(r["log_present"] for r in rows),
               "unusual_slots": sum(bool(r["unusual"]) for r in rows),
               "finished_with_unusual": [{k: r[k] for k in ("source", "task_id", "arm", "unusual")}
                                         for r in rows if r["original_status"] == "finished" and r["unusual"]],
               "mismatches": [{k: r[k] for k in ("source", "task_id", "arm", "mismatches")}
                              for r in rows if r["mismatches"]]}
    for key in ("calls", "stops", "wire_settings", "token_usage"):
        total = Counter()
        for row in rows:
            total.update(row[key])
        summary[key] = dict(total)
    (ROOT / "native_call_audit.json").write_text(json.dumps({"summary": summary, "slots": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
