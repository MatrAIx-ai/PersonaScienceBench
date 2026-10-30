"""Text-only IG-Arena actor using the shared researcher, session and transport.

Only explicit CLI run requests make model calls. Actor has a single handoff tool,
no filesystem/network/execution capabilities. Native grading runs after sealing.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from personasciencebench.adapters.base import read_json, sha256
from personasciencebench.adapters.ideagene import POLICY as CONVERSION, EVALUATOR_VERSION, PILOT_IDS
from personasciencebench.collaboration import ActiveResearcher, CollaborationHandoff, validate_collaboration, POLICY
from personasciencebench.inference import OpenRouterClient, preflight, strict_json
from personasciencebench.packaging import safe_component, write_json
from personasciencebench.persona import Persona, render_persona
from personasciencebench.registry import load_adapter, project_root
from personasciencebench.schema import Submission
from personasciencebench.session import EpisodeSession

RUNNER_VERSION = "ideagene-text-review-v2"
TOOL_NAME = "end_researcher_turn"
PROPOSAL_MAX_CHARACTERS = 20000
NATIVE_PROPOSAL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "idea_genome", "evolution_rationale", "validation_plan", "known_unknowns"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "idea_genome": {
            "type": "object", "additionalProperties": False,
            "required": ["problem_niche", "core_mechanism", "inherited_genes",
                         "mutated_or_novel_genes", "addressed_limitation", "expected_contribution"],
            "properties": {
                "problem_niche": {"type": "string", "minLength": 21},
                "core_mechanism": {"type": "string", "minLength": 21},
                "inherited_genes": {"type": "array", "minItems": 1,
                                    "items": {"type": "string", "minLength": 21}},
                "mutated_or_novel_genes": {"type": "array", "minItems": 1,
                                           "items": {"type": "string", "minLength": 21}},
                "addressed_limitation": {"type": "string", "minLength": 21},
                "expected_contribution": {"type": "string", "minLength": 21},
            },
        },
        "evolution_rationale": {
            "type": "object", "additionalProperties": False,
            "required": ["dynamics_type", "source_ideas", "why_plausible", "lineage_risk",
                         "inherited_components", "changed_components"],
            "properties": {
                "dynamics_type": {"type": "string",
                                  "enum": ["Mutation", "Recombination", "Hybridization", "Speciation"]},
                "source_ideas": {"type": "array", "minItems": 1,
                                 "items": {"type": "string", "minLength": 1}},
                "why_plausible": {"type": "string", "minLength": 21},
                "lineage_risk": {"type": "string", "minLength": 21},
                "inherited_components": {"type": "array", "minItems": 1,
                                         "items": {"type": "string", "minLength": 21}},
                "changed_components": {"type": "array", "minItems": 1,
                                       "items": {"type": "string", "minLength": 21}},
            },
        },
        "validation_plan": {
            "type": "object", "additionalProperties": False,
            "required": ["hypothesis", "experiment", "baselines", "metrics", "falsification_criteria"],
            "properties": {
                "hypothesis": {"type": "string", "minLength": 21},
                "experiment": {"type": "string", "minLength": 21},
                "baselines": {"type": "array", "minItems": 1,
                              "items": {"type": "string", "minLength": 1}},
                "metrics": {"type": "array", "minItems": 1,
                            "items": {"type": "string", "minLength": 1}},
                "falsification_criteria": {"type": "array", "minItems": 1,
                                           "items": {"type": "string", "minLength": 1}},
            },
        },
        "known_unknowns": {"type": "array", "minItems": 1,
                           "items": {"type": "string", "minLength": 1}},
    },
}
ACTOR_PROMPT = (
    "You are the scientific assistant. Inspect the supplied public research question and propose an approach first. "
    "Expose consequential choices, evidence, assumptions and uncertainties. Main design work requires researcher "
    "approval. After approval develop a complete, falsifiable research proposal. You have no tools for experiments, "
    "files or browsing; do not claim unperformed work or invent references. At every turn call end_researcher_turn "
    "exactly once. Use stage=plan before approval and stage=result afterwards. Place the complete proposal JSON "
    "object in payload.proposal at result stage. Follow the supplied schema exactly; the native PES parser requires "
    "all six idea_genome fields. A clarification-only result may omit it, "
    "in which case the previously shared proposal remains the candidate. Do not put persona, grader guesses or "
    "dialogue in the proposal. At plan stage payload must be an empty object. At result stage payload may contain "
    "only proposal. The complete proposal must not exceed 20,000 characters; prioritize testable mechanisms, "
    "controls and decision criteria over exhaustive prose. Design quality is "
    "evaluated later by the native grader, not by user satisfaction."
)


def serialize_native_proposal(value):
    """Fail closed on proposals that the deterministic native PES format gate rejects."""
    if not isinstance(value, dict):
        raise ValueError("IdeaGene result proposal must be a JSON object")
    if not set(NATIVE_PROPOSAL_SCHEMA["required"]) <= set(value):
        raise ValueError("IdeaGene proposal is missing required top-level fields")
    genome = value.get("idea_genome")
    expected_genome = set(NATIVE_PROPOSAL_SCHEMA["properties"]["idea_genome"]["required"])
    if not isinstance(genome, dict) or not expected_genome <= set(genome):
        raise ValueError("IdeaGene proposal has an incomplete idea_genome")
    for field in ("problem_niche", "core_mechanism", "addressed_limitation", "expected_contribution"):
        if not isinstance(genome[field], str) or len(genome[field].strip()) <= 20:
            raise ValueError(f"IdeaGene idea_genome.{field} is too short")
    for field in ("inherited_genes", "mutated_or_novel_genes"):
        values = genome[field]
        if (not isinstance(values, list) or not values
                or any(not isinstance(item, str) or len(item.strip()) <= 20 for item in values)):
            raise ValueError(f"IdeaGene idea_genome.{field} must contain substantive strings")
    rationale = value.get("evolution_rationale")
    expected_rationale = set(NATIVE_PROPOSAL_SCHEMA["properties"]["evolution_rationale"]["required"])
    if not isinstance(rationale, dict) or not expected_rationale <= set(rationale):
        raise ValueError("IdeaGene proposal has an incomplete evolution_rationale")
    plan = value.get("validation_plan")
    expected_plan = set(NATIVE_PROPOSAL_SCHEMA["properties"]["validation_plan"]["required"])
    if not isinstance(plan, dict) or not expected_plan <= set(plan):
        raise ValueError("IdeaGene proposal has an incomplete validation_plan")
    if not isinstance(value.get("known_unknowns"), list) or not value["known_unknowns"]:
        raise ValueError("IdeaGene proposal must state known_unknowns")
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if len(serialized) > PROPOSAL_MAX_CHARACTERS:
        raise ValueError("IdeaGene native proposal exceeds the character limit")
    return serialized


def parse_actor_arguments(raw):
    """Parse a tool call, permitting only redundant trailing right braces.

    Some OpenAI-compatible providers return a complete tool-call object followed
    by one extra ``}``. Removing that suffix is lossless and auditable; no other
    malformed JSON is repaired.
    """
    try:
        return strict_json(raw), None
    except json.JSONDecodeError as error:
        suffix = raw[error.pos:]
        if (error.msg != "Extra data" or not suffix or len(suffix.strip()) > 2
                or set(suffix.strip()) != {"}"}):
            raise
        normalized = raw[:error.pos].rstrip()
        value = strict_json(normalized)
        return value, {
            "normalization": "redundant_trailing_right_brace_removed",
            "removed_characters": len(suffix.strip()),
            "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
        }


def selected_profiles(ids, root=None):
    """Restore exact published identities; no profile summarization or task rewriting."""
    root = root or project_root()
    manifest = read_json(root / "configs/full_persona_v2/cohort.json")
    rows = {r["candidate_id"]: r for r in manifest["profiles"]}
    result = {}
    if len(ids) != len(set(ids)) or "persona_off" not in ids:
        raise ValueError("Select unique persona IDs including persona_off")
    for pid in ids:
        if pid == "persona_off":
            result[pid] = Persona(enabled=False)
            continue
        if pid not in rows:
            raise ValueError("Unknown published persona ID")
        row = rows[pid]
        if "prompt" in row:
            prompt = (root / row["prompt"]).read_text(encoding="utf-8")
        else:
            # Retain compatibility with historical Markdown profile exports.
            text = (root / row["published_profile"]).read_text(encoding="utf-8")
            prompt = text.split("```text\n", 1)[1].rsplit("\n```", 1)[0]
        if hashlib.sha256(prompt.encode()).hexdigest() != row["prompt_sha256"]:
            raise ValueError("Published persona hash mismatch")
        result[pid] = Persona(enabled=True, id=pid, version="full-persona-v2", system_prompt=prompt)
    return result


def validate_config(config):
    if config.get("version") != RUNNER_VERSION:
        raise ValueError("Unknown IdeaGene runner version")
    task_ids = config.get("task_ids")
    if (not isinstance(task_ids, list) or not task_ids or len(task_ids) != len(set(task_ids))
            or any(task_id not in PILOT_IDS for task_id in task_ids)):
        raise ValueError("IdeaGene tasks must be a unique, nonempty subset of the reviewed pilot")
    if type(config.get("repetitions")) is not int or config["repetitions"] < 1:
        raise ValueError("repetitions must be a positive integer")
    if set(config.get("models", {})) != {"actor", "researcher"}:
        raise ValueError("Configure actor and researcher separately; PES uses native judge configuration")
    collab = validate_collaboration(config.get("collaboration"))
    if collab is None or not collab["unrestricted_knowledge"]:
        raise ValueError("This pilot preserves full-profile general knowledge in every arm")
    return collab


def run_episode(episode, persona, actor, researcher_backend, output, *, max_requests=12):
    researcher = ActiveResearcher(episode, researcher_backend, persona=persona, unrestricted_knowledge=True)
    session = EpisodeSession(episode, researcher, output)
    candidate = None
    result = {"episode_id": episode.id, "status": "infrastructure_error", "submission": None,
              "interaction_protocol": POLICY, "runner_version": RUNNER_VERSION}
    messages = [{"role": "system", "content": ACTOR_PROMPT},
                {"role": "user", "content": json.dumps(episode.actor_input(), ensure_ascii=False)}]
    handoff_schema = CollaborationHandoff.model_json_schema()
    handoff_schema["properties"]["payload"] = {
        "type": "object", "additionalProperties": False,
        "properties": {"proposal": NATIVE_PROPOSAL_SCHEMA}}
    handoff_schema["properties"]["artifacts"] = {
        "type": "object", "additionalProperties": False, "properties": {}}
    tool = {"type": "function", "function": {"name": TOOL_NAME,
            "description": "Share the current approach or design with the researcher.",
            "parameters": handoff_schema}}
    try:
        decision = researcher.decide(session, None, max_requests - 1)
        messages.append({"role": "user", "content": decision.message})
        for index in range(max_requests - 1):
            response = actor.completion(messages, tools=[tool],
                tool_choice={"type": "function", "function": {"name": TOOL_NAME}})
            message = response["choices"][0]["message"]
            calls = message.get("tool_calls", [])
            if len(calls) != 1 or calls[0]["function"]["name"] != TOOL_NAME:
                raise ValueError("Exactly one actor handoff tool call is required")
            call = calls[0]
            try:
                parsed_handoff, normalization = parse_actor_arguments(call["function"]["arguments"])
                if normalization:
                    session.event("actor_format_normalization", normalization)
                handoff = researcher.validate_handoff(parsed_handoff)
                if handoff["artifacts"] or set(handoff["payload"]) - {"proposal"}:
                    raise ValueError("Text-only IdeaGene handoffs support payload.proposal and no artifacts")
                if "proposal" in handoff["payload"]:
                    value = handoff["payload"]["proposal"]
                    if handoff["stage"] != "result":
                        raise ValueError("Proposal is only valid at result stage")
                    candidate = serialize_native_proposal(value)
                    # Normalize the audited/researcher-visible handoff to exactly the
                    # string consumed later by the upstream evaluator.
                    handoff = dict(handoff)
                    handoff["payload"] = {"proposal": candidate}
                if handoff["stage"] == "result" and candidate is None:
                    raise ValueError("Result review requires a complete candidate proposal")
            except (ValueError, TypeError) as error:
                session.event("actor_handoff_rejected", {
                    "error_type": type(error).__name__, "raw_arguments_persisted": False,
                    "correction_requested": True})
                messages.append({"role": "assistant", "content": None, "tool_calls": [call]})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps({
                    "accepted": False,
                    "message": "Controller rejected this handoff. Return exactly one corrected handoff matching the supplied schema and current stage. Keep a complete native-format proposal under 20,000 characters; do not add artifacts.",
                    "expected_stage": "result" if researcher.approach_approved else "plan",
                    "approach_approved": researcher.approach_approved})})
                continue
            session.event("actor_handoff", handoff)
            checkpoint = {"handoff": handoff, "trace_sequence": session.sequence - 1,
                          "time": datetime.now(timezone.utc).isoformat(),
                          "disclosed_fact_ids": list(researcher.disclosed),
                          "disclosed_context": list(researcher.disclosed.values())}
            write_json(output / f"handoff_{index:03d}.json", checkpoint, exclusive=True)
            reviewed = dict(handoff)
            if handoff["stage"] == "result" and "proposal" not in handoff["payload"]:
                reviewed["payload"] = {"proposal": candidate}
                session.event("candidate_retained", {"from_previous_handoff": True,
                              "proposal_sha256": hashlib.sha256(candidate.encode()).hexdigest()})
            # Only allowlisted handoff reaches the researcher, never private model reasoning.
            decision = researcher.decide(session, reviewed, max_requests - index - 2)
            # Do not persist provider-specific reasoning fields in future actor prompts.
            messages.append({"role": "assistant", "content": None, "tool_calls": [call]})
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": json.dumps({"message": decision.message,
                                                    "approach_approved": researcher.approach_approved})})
            if decision.action == "stop":
                submission = Submission(episode_id=episode.id, stage="final", answer=candidate)
                session.submit_result(submission)
                write_json(output / "proposal_receipt.json", {
                    "submission_sha256": sha256(output / "submission.json"),
                    "proposal_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                    "trace_sequence": session.sequence, "time": datetime.now(timezone.utc).isoformat()}, exclusive=True)
                result.update(status="submitted", submission=str(output / "submission.json"))
                break
        else:
            result["status"] = "missing_submission"
            result["reason"] = "researcher_budget_exhausted_without_acceptance"
    except Exception as error:
        result.update(error_type=type(error).__name__)
        session.event("episode_error", {"error_type": type(error).__name__})
    finally:
        result.update(plan_reviews=researcher.plan_reviews, result_reviews=researcher.result_reviews,
                      approach_approved=researcher.approach_approved,
                      researcher_decisions=len(researcher.audit),
                      optional_result_revisions=max(0, researcher.result_reviews - 1))
        write_json(output / "episode_result.json", result)
    return result


def pilot_plan(adapter, config, *, root=None):
    collab = validate_config(config)
    profiles = selected_profiles(config["persona_ids"], root)
    episodes = [adapter.convert(t) for t in config["task_ids"]]
    return {"runner_version": RUNNER_VERSION, "conversion_version": CONVERSION,
            "tasks": [{"id": e.source_task_id, "question_sha256": hashlib.sha256(e.public.question.encode()).hexdigest(),
                       "source_sha256": e.conversion["source_sha256"]} for e in episodes],
            "personas": [{"id": pid, "prompt_sha256": hashlib.sha256(render_persona(p).encode()).hexdigest(),
                          "enabled": p.enabled} for pid, p in profiles.items()],
            "scheduled_episodes": len(episodes) * len(profiles) * config["repetitions"],
            "repetitions": config["repetitions"], "max_requests": collab["max_requests"],
            "models": config["models"], "native_evaluator": EVALUATOR_VERSION,
            "runtime": "text-only; no tools other than handoff; no actor code execution",
            "model_calls": 0, "native_evaluation": "not_run", "scientific_runs_started": False}


def render_trace(controller, destination):
    lines = ["# IdeaGene interaction trace", "", "Real run records; acceptance is not a scientific score.", ""]
    for raw in (controller / "events.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(raw)
        if event["type"] == "actor_handoff":
            data = event["payload"]
            lines.extend([f"## Actor — {data['stage']}", "", data["answer"], "", "Evidence: " + data["evidence"], ""])
            if data["payload"].get("proposal"):
                lines.extend(["### Proposal", "", data["payload"]["proposal"], ""])
        elif event["type"] == "researcher_decision":
            data = event["payload"]
            lines.extend(["## Researcher — " + data["phase"], "", data["message"], ""])
    destination.write_text("\n".join(lines), encoding="utf-8")


def run_pilot(source_root, manifest, config, output, *, evaluate_native=False, native_python=None):
    adapter = load_adapter("ideagene", source_root, manifest)
    plan = pilot_plan(adapter, config)
    profiles = selected_profiles(config["persona_ids"])
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "plan.json", plan)
    write_json(output / "config.json", config)
    write_json(output / "source_manifest.json", read_json(manifest))
    results = []
    summary = {"scheduled": plan["scheduled_episodes"], "attempted": 0, "submitted": 0,
               "evaluated": 0, "scored": 0, "mean_pes": None, "cases": results,
               "run_kind": "live_api", "status": "preflight", "scientific_experiments_executed": False}
    try:
        catalog = preflight(config["models"])
        for role in ("actor", "researcher"):
            if "tools" not in catalog[role]["supported_parameters"]:
                raise ValueError("Both roles require typed tool calling")
            # Validate constructor settings before an episode is counted as attempted.
            OpenRouterClient(**config["models"][role], role=role, record=None,
                             supported_parameters=catalog[role]["supported_parameters"])
        write_json(output / "api_preflight.json", catalog)
        for task_id in config["task_ids"]:
            episode = adapter.convert(task_id)
            for pid, persona in profiles.items():
                for repetition in range(config["repetitions"]):
                    started = time.monotonic()
                    case = output / safe_component(f"{task_id}-{pid}-r{repetition}")
                    case.mkdir()
                    summary["attempted"] += 1
                    usage = []
                    def record_api(row):
                        with (case / "api_calls.private.jsonl").open("a", encoding="utf-8") as stream:
                            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                        usage.append({"role": row["role"], "usage": row.get("usage", {})})
                    clients = {role: OpenRouterClient(**spec, role=role, record=record_api,
                               supported_parameters=catalog[role]["supported_parameters"])
                               for role, spec in config["models"].items()}
                    controller = case / "controller"
                    result = run_episode(episode, persona, clients["actor"], clients["researcher"], controller,
                                         max_requests=plan["max_requests"])
                    result.update(task_id=task_id, persona_id=pid, repetition=repetition,
                                  evaluation_status="not_run", native_pes=None)
                    if result["submission"]:
                        summary["submitted"] += 1
                        submission = Submission.model_validate(read_json(Path(result["submission"])))
                        try:
                            if evaluate_native:
                                evaluation = adapter.run_native(episode, submission, controller / "native_request.json",
                                                                python=native_python)
                                write_json(controller / "evaluation.json", evaluation.model_dump(mode="json"))
                                result["evaluation_status"] = evaluation.status
                                if evaluation.status in ("scored", "error"):
                                    summary["evaluated"] += 1
                                if evaluation.status == "scored":
                                    summary["scored"] += 1
                                    result["native_pes"] = evaluation.metrics["pes"]
                            else:
                                adapter.evaluation_request(episode, submission, controller / "native_request.json")
                        except Exception as error:
                            result.update(evaluation_status="error", evaluation_error_type=type(error).__name__)
                    result.update(elapsed_seconds=round(time.monotonic() - started, 3), api_usage=usage,
                                  proposal_submitted=bool(result["submission"]))
                    # API usage may omit billing cost; missing stays unknown.
                    result["reported_cost_usd"] = (sum(u["usage"]["cost"] for u in usage)
                        if usage and all(isinstance(u["usage"].get("cost"), (int, float)) for u in usage) else None)
                    write_json(case / "result.json", result)
                    render_trace(controller, case / "trace.md")
                    results.append(result)
                    write_json(output / "summary.json", summary)
        summary["status"] = "finished"
    except Exception as error:
        summary.update(status="infrastructure_error", error_type=type(error).__name__)
        raise
    finally:
        scores = [r["native_pes"] for r in results if r["native_pes"] is not None]
        summary["mean_pes"] = sum(scores) / len(scores) if scores else None
        summary["score_denominator"] = len(scores)
        summary["not_attempted"] = summary["scheduled"] - summary["attempted"]
        summary["by_persona"] = {}
        for pid in profiles:
            rows = [r for r in results if r["persona_id"] == pid]
            values = [r["native_pes"] for r in rows if r["native_pes"] is not None]
            summary["by_persona"][pid] = {
                "attempted": len(rows), "submitted": sum(r["proposal_submitted"] for r in rows),
                "scored": len(values), "mean_pes": sum(values) / len(values) if values else None,
                "denominator": len(values), "missing_scores": len(rows) - len(values)}
        write_json(output / "summary.json", summary)
    return summary
