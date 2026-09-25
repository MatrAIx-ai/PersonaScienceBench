"""Offline examples and explicit native evaluation; no automatic model calls."""

import argparse
import json
from pathlib import Path

from .profiles import SciencePersona, load_catalog, profile_json_schema, profile_record
from .interaction import InteractionController, score_ratings
from .task import fetch_sources, prepare, native_verify, write_json


def demo(profile: SciencePersona, output: Path):
    if output.exists():
        raise FileExistsError("Use a fresh demo output directory")
    output.mkdir(parents=True)
    controller = InteractionController(profile)
    controller.act({"kind": "question", "text": "Before choosing the scope of model search, how would you like to review consequential modeling decisions and receive questions?", "topics": ["workflow"]})
    controller.act({"kind": "plan", "text": "I will inspect the public data and begin with a compact baseline. I will share options and my recommendation before a consequential model-family expansion. I will use low-cost diagnostics first."})
    controller.act({"kind": "draft", "text": "This is a protocol demonstration. No model was fit and no scientific validation was executed. The draft report therefore cannot claim native success."})
    report = output / "report.md"
    report.write_text(
        "# Protocol demonstration report\n\n"
        "No ODE model was fit in this scripted interaction. No measured validation score is available. "
        "The proposed next step is to inspect public data and validate an allowed compact baseline. "
        "The public advisory diagnostic cannot guarantee the hidden gates or establish a unique causal mechanism. "
        "Decision: no-go for a scientific success claim; continue analysis in a real actor run. "
        "This report was revised after the researcher's review request. It is an interaction fixture, "
        "not a valid native scientific submission.\n")
    artifact = controller.record_artifact(report, "post-review report.md")
    controller.act({"kind": "final", "text": "I revised report.md and recorded its snapshot. No scientific execution or native score is available. No-go for a success claim; the next step is to fit and validate a compact baseline using public evidence."})
    packet = controller.judge_packet()
    write_json(output / "judge_packet.json", packet)
    write_json(output / "profile.private.json", profile_record(profile))
    write_json(output / "burden.json", controller.burden())
    write_json(output / "public_transcript.json", controller.public_transcript())
    # These are intentionally human-authored fixture expectations, not measured model ratings.
    final_id = controller.events[-1]["id"]
    agent_events = [e for e in controller.events if e["actor"] == "agent"]
    expected = [
        {"criterion_id": "question_value", "status": "scored", "score": 3, "evidence_refs": [agent_events[0]["id"]], "reason": "Authored fixture: one decision-relevant request about collaboration."},
        {"criterion_id": "scientific_calibration", "status": "scored", "score": 3, "evidence_refs": [final_id], "reason": "Authored fixture: explicitly reports that no scientific execution occurred."},
        {"criterion_id": "decision_process", "status": "not_applicable", "score": None, "evidence_refs": [], "reason": "No actual consequential model-selection decision occurred in this protocol fixture."},
        {"criterion_id": "burden", "status": "not_applicable", "score": None, "evidence_refs": [], "reason": "No questions after workflow disclosure."},
        {"criterion_id": "revision", "status": "scored", "score": 2, "evidence_refs": [artifact, final_id], "reason": "Authored fixture: report responds to review, but the scientific validation requested is not available."},
        {"criterion_id": "go_no_go", "status": "scored", "score": 3, "evidence_refs": [final_id], "reason": "Authored fixture: no-go for unsupported success, with a concrete next step."},
    ]
    write_json(output / "fixture_ratings.json", expected)
    result = score_ratings(packet, expected)
    result.update(evaluation_kind="scripted_protocol_fixture", scientific_status="not_run", model_calls=0)
    write_json(output / "fixture_score.json", result)
    return {"output": str(output), "kind": "scripted_protocol_fixture", "native_science": "not_run", "model_calls": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cat = commands.add_parser("catalog")
    cat.add_argument("--schema", type=Path)
    d = commands.add_parser("demo")
    d.add_argument("--persona", type=Path, required=True)
    d.add_argument("--output", type=Path, required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--lock", type=Path, required=True)
    p.add_argument("--download", action="store_true")
    n = commands.add_parser("native-verify")
    n.add_argument("--prepared", type=Path, required=True)
    n.add_argument("--artifacts", type=Path, required=True)
    n.add_argument("--output", type=Path, required=True)
    j = commands.add_parser("score")
    j.add_argument("--packet", type=Path, required=True)
    j.add_argument("--ratings", type=Path, required=True)
    j.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "catalog":
        if args.schema:
            write_json(args.schema, profile_json_schema())
        result = {"version": load_catalog()["version"], "count": len(load_catalog()["attributes"])}
    elif args.command == "demo":
        result = demo(SciencePersona.model_validate_json(args.persona.read_text()), args.output)
    elif args.command == "prepare":
        lock = json.loads(args.lock.read_text())
        if args.download:
            fetch_sources(args.source, lock)
        result = prepare(args.source, args.output, lock)
    elif args.command == "native-verify":
        result = native_verify(args.prepared, args.artifacts, args.output)
    else:
        if args.output.exists():
            raise FileExistsError("Scores are immutable; use a fresh path")
        result = score_ratings(json.loads(args.packet.read_text()), json.loads(args.ratings.read_text()))
        write_json(args.output, result)
    print(json.dumps(result, indent=2))
    return 1 if args.command == "native-verify" and result["status"] != "scored" else 0


if __name__ == "__main__":
    raise SystemExit(main())
