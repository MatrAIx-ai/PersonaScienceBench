#!/usr/bin/env python3
"""Render complete recorded benchmark interactions as readable Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    if path.is_file():
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append({"kind": "MalformedEvent", "line": number, "raw": line})
    return records


def load_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(errors="replace"))
    except json.JSONDecodeError:
        return default


def text_content(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(item.get("text", item)) if isinstance(item, dict)
                          else str(item) for item in value)
    if isinstance(value, dict):
        if "content" in value:
            return text_content(value["content"])
        if "text" in value:
            return text_content(value["text"])
        return json.dumps(value, indent=2, ensure_ascii=False)
    return str(value)


def fenced(value, language: str = "text") -> str:
    content = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)
    fence = "````"
    while fence in content:
        fence += "`"
    return f"{fence}{language}\n{content}\n{fence}"


def details(label: str, value, language: str = "text") -> str:
    return f"<details>\n<summary>{label}</summary>\n\n{fenced(value, language)}\n\n</details>"


def render_collaboration(events: list[dict]) -> list[str]:
    if not any(e.get("type") == "researcher_decision" for e in events):
        if not any(e.get("type") == "final_specification" for e in events):
            return []
        output = ["## Scientific clarification conversation", ""]
        labels = {"initial_request":"Initial task", "researcher_question":"Agent question",
                  "researcher_reply":"Researcher answer", "final_specification":"Final specification"}
        for event in events:
            if event.get("type") in labels:
                output += ["**" + labels[event["type"]] + "**", next(iter(event["payload"].values()))]
        return output
    output = ["## Researcher–agent collaboration", "",
              "Chronological shared conversation. The researcher sees these handoffs, not private tool output. Full tool and model records follow."]
    turn = 0
    for event in events:
        payload = event.get("payload", {})
        if event.get("type") == "researcher_decision":
            turn += 1
            output += [f"### {turn}. Researcher — {payload['interaction']}", payload["message"],
                       f"**Decision:** {payload['action']}",
                       f"**Review phase:** {payload.get('phase', 'legacy')}; **approach approved:** {payload.get('approve_approach', False)}",
                       f"**Basis:** {payload['evidence']}",
                       "**Open objectives:** " + ("; ".join(payload["objectives_open"]) or "None")]
        elif event.get("type") == "agent_handoff":
            output += ["**Agent reply" + (f" ({payload['stage']})" if payload.get("stage") else "") + "**", payload["answer"]]
            if payload.get("evidence"):
                output += ["**Shared evidence:**", payload["evidence"]]
            if payload.get("assumptions"):
                output += ["**Assumptions:** " + "; ".join(payload["assumptions"])]
            if payload.get("uncertainties"):
                output += ["**Uncertainties:** " + "; ".join(payload["uncertainties"])]
            if payload.get("artifacts"):
                output.append(details("Candidate artifacts and execution declaration", {
                    "artifacts": payload["artifacts"], "payload": payload.get("payload", {})}, "json"))
        elif event.get("type") in {"collaboration_budget_exhausted", "collaboration_missing_submission", "collaboration_stopped"}:
            output += ["**Controller termination:** " + str(payload.get("reason", ""))]
    return output


def render_actor(events: list[dict]) -> list[str]:
    output = ["## Actor event stream", ""]
    if not events:
        return output + ["No actor event stream was recorded."]
    for index, event in enumerate(events, 1):
        kind = event.get("kind", "Event")
        timestamp = event.get("timestamp", "")
        heading = f"### A{index}. {kind}"
        if timestamp:
            heading += f" — {timestamp}"
        output.append(heading)
        if kind == "SystemPromptEvent":
            output.append(details("System prompt", event.get("system_prompt", "")))
            if event.get("dynamic_context"):
                output.append(details("Dynamic context", event["dynamic_context"], "json"))
            if event.get("tools"):
                output.append(details("Available tools", event["tools"], "json"))
        elif kind == "MessageEvent":
            message = event.get("llm_message") or {}
            role = message.get("role") or event.get("source", "message")
            output.append(f"**{str(role).title()}**\n\n{text_content(message)}")
        elif kind == "ActionEvent":
            tool = event.get("tool_name") or (event.get("action") or {}).get("kind", "action")
            output.append(f"**Tool:** `{tool}`")
            if event.get("thought"):
                output.append(details("Recorded actor thought", event["thought"]))
            if event.get("reasoning_content"):
                output.append(details("Recorded reasoning content", event["reasoning_content"]))
            call = event.get("tool_call") or event.get("action") or {}
            output.append(details("Tool call", call, "json"))
        elif kind == "ObservationEvent":
            output.append(details("Tool observation", event.get("observation", {}), "json"))
        elif kind == "AgentErrorEvent":
            output.append(details("Agent error", event, "json"))
        else:
            output.append(details("Event record", event, "json"))
    return output


def render_controller(events: list[dict]) -> list[str]:
    output = ["## Controller event stream", ""]
    if not events:
        return output + ["No separate controller event stream was recorded."]
    for index, event in enumerate(events, 1):
        event_type = event.get("type") or event.get("event") or "controller_event"
        timestamp = event.get("time", "")
        title = f"### C{index}. `{event_type}`"
        if timestamp:
            title += f" — {timestamp}"
        output += [title, details("Controller payload", event.get("payload", event), "json")]
    return output


def render_researcher(history: list[dict]) -> list[str]:
    output = ["## Simulator conversation", ""]
    if not history:
        return output + ["The actor did not ask the simulator a question in this case."]
    for index, message in enumerate(history, 1):
        role = str(message.get("role", "message")).title()
        output += [f"### S{index}. {role}", text_content(message)]
    return output


def response_message(response: dict) -> dict:
    choices = response.get("choices") or []
    if choices and isinstance(choices[0], dict):
        return choices[0].get("message") or {}
    return {}


def render_api(records: list[dict]) -> list[str]:
    output = ["## Model calls: actor, simulator, and judge", ""]
    if not records:
        return output + ["No model-call record was found."]
    calls: list[dict] = []
    phased: dict[object, dict] = {}
    for record in records:
        if "phase" not in record:
            calls.append(record)
            continue
        call_id = record.get("call_id", len(phased) + 1)
        merged = phased.setdefault(call_id, {"call_id": call_id, "role": record.get("role"),
                                              "model": record.get("requested_model")})
        if record.get("phase") == "request":
            merged["request"] = record.get("payload", {})
            merged["reserved_usd"] = record.get("reserved_usd")
        elif record.get("phase") == "response":
            merged["response"] = record.get("response", {})
        else:
            merged.setdefault("other_phases", []).append(record)
    calls.extend(phased[key] for key in sorted(phased, key=lambda value: str(value)))
    for index, call in enumerate(calls, 1):
        role = call.get("role", "unknown")
        model = call.get("resolved_model") or call.get("model") or call.get("requested_model", "unknown")
        output.append(f"### M{index}. {str(role).title()} call — `{model}`")
        request = call.get("request") or {}
        for msg_index, message in enumerate(request.get("messages") or [], 1):
            msg_role = str(message.get("role", "message")).title()
            output.append(details(f"Request message {msg_index}: {msg_role}", text_content(message)))
        request_meta = {key: value for key, value in request.items() if key != "messages"}
        if request_meta:
            output.append(details("Request settings and tool schemas", request_meta, "json"))
        response = call.get("response") or {}
        message = response_message(response)
        if message:
            output.append(details("Model response", message, "json"))
        elif response:
            output.append(details("Model response", response, "json"))
        usage = call.get("usage") or response.get("usage")
        if usage:
            output.append(details("Usage", usage, "json"))
        transport = {key: call.get(key) for key in ("requested_native_settings",
                                                     "omitted_native_settings",
                                                     "automatic_retries") if key in call}
        if transport:
            output.append(details("Transport record", transport, "json"))
    return output


def find_first(case: Path, relatives: list[str]) -> Path | None:
    for relative in relatives:
        candidate = case / relative
        if candidate.is_file():
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    cases: list[Path] = []
    for result in args.run.glob("*/result.json"):
        case = result.parent
        cases.append(case)

    index_rows = []
    for case in sorted(set(cases)):
        result = load_json(case / "result.json", {})
        actor_path = find_first(case, ["controller/actor_events.jsonl", "actor_events.jsonl"])
        controller_path = find_first(case, ["controller/events.jsonl", "events.jsonl"])
        researcher_path = find_first(case, ["controller/researcher_history.private.json",
                                             "researcher_history.private.json", "researcher_history.json"])
        api_path = find_first(case, ["controller/api_calls.private.jsonl",
                                     "api_calls.private.jsonl", "api_calls.jsonl"])
        instance = result.get("episode_id", result.get("task_id", case.name))
        status = result.get("status", "unknown")
        raw = [path.relative_to(case).as_posix() for path in
               (actor_path, controller_path, researcher_path, api_path) if path]
        sections = [
            "# Complete recorded interaction trace", "",
            f"- **Instance:** `{instance}`",
            f"- **Status:** `{status}`",
            "- **Persona:** disabled for this run; the grounded simulator remains available.",
            "- **Scope:** all recorded prompts, model responses, tool calls, observations, simulator turns, controller events, and judge calls. Hidden model chain-of-thought is unavailable; any reasoning field explicitly returned by the provider is retained.",
            f"- **Raw records:** {', '.join(f'[`{name}`]({name})' for name in raw)}", "",
        ]
        if result.get("submission_recovery"):
            sections += ["**Submission recovery:** A complete candidate from an earlier handoff was sealed and graded after a candidate-retention bug. The original result is preserved in `result.before_candidate_retention_recovery.json`; no actor was rerun. See `submission_recovery/` for the sealing and evaluation records."]
        sections += render_collaboration(load_jsonl(controller_path) if controller_path else [])
        sections += render_actor(load_jsonl(actor_path) if actor_path else [])
        sections += render_researcher(load_json(researcher_path, []) if researcher_path else [])
        sections += render_controller(load_jsonl(controller_path) if controller_path else [])
        sections += render_api(load_jsonl(api_path) if api_path else [])
        sections += ["## Final result", "", fenced(result, "json")]
        trace = case / "trace.md"
        trace.write_text("\n\n".join(sections).rstrip() + "\n")
        index_rows.append((str(instance), str(status), trace.relative_to(args.run).as_posix()))

    lines = ["# GPT-6 Luna persona-off run: interaction traces", "",
             "Each case preserves its raw JSON/JSONL records beside a readable Markdown rendering.", "",
             "| Benchmark instance | Status | Trace |", "|---|---:|---|"]
    for instance, status, relative in index_rows:
        lines.append(f"| `{instance}` | `{status}` | [readable trace]({relative}) |")
    (args.run / "TRACE_INDEX.md").write_text("\n".join(lines) + "\n")
    print(f"Rendered {len(index_rows)} complete readable traces under {args.run}")


if __name__ == "__main__":
    main()
