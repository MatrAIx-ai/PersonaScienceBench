"""OpenHands actor loop with controller-owned, isolated benchmark tools.

Importing this module neither imports the SDK nor constructs an inference client.
Only the execution tool reaches the sandbox; SDK state stays in an empty private
temporary directory and the actor receives Episode.actor_input() exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from threading import Lock
from typing import Any, Literal
from uuid import uuid4

from personasciencebench.schema import Submission


SYSTEM_PROMPT = """You are a scientific research actor working on the supplied benchmark task.
Use the public task, its data descriptions, and the files in /workspace. Inspect data,
perform the requested analysis, and report only findings supported by your work.
You can ask the researcher for study context or research preferences when useful. Asking is optional and
the researcher cannot provide missing scientific results. Shared progress updates
are explicit; your private reasoning and shell activity are not sent to the researcher.

Use execute_command for all file inspection, code writing, and analysis execution.
Commands run inside the isolated scientific workspace, with no network access.
Use workspace-relative paths for submitted artifacts. Create an analysis script
or notebook and execute the analysis before claiming it was executed. A successful
command alone is not evidence that its scientific conclusions are correct.
submit_plan saves an optional initial checkpoint; full-workflow tasks continue
through execution and final results. Use submit_result to finish, preserving the
task's exact answer requirements. Include relevant analysis artifacts and use
payload.executed_analysis=true only after performing the analysis. For BixBench,
an actual nonempty analysis script/notebook is required under artifacts.analysis.
For ScienceAgentBench, include artifacts["solution.py"] and an artifact entry
whose key exactly matches each required output path in the public task.
Final text outside submit_result does not count as a submitted result.
"""


COLLABORATION_PROMPT = """You are a research agent collaborating with a researcher on the supplied benchmark.
Keep its original question, fixed methods, constraints and required outputs unchanged.
First inspect inputs/repository and propose an approach. Before the main analysis or
implementation, yield a stage=plan handoff: describe observations, proposed choices,
assumptions and important uncertainties. Wait for explicit researcher approval.
Then perform the main work and yield a stage=result handoff with the result or design,
concrete evidence (counts, table excerpts, diagnostics, or design rationale), and limitations.
Use end_researcher_turn for every handoff. The same conversation and workspace persist.
Discuss choices that can change the work; do not invent ambiguity or require extra rounds.
Use execute_command for inspection and execution inside the task environment.
Follow the public submission contract exactly. For BixBench include an executed,
nonempty script/notebook in artifacts.analysis and payload.executed_analysis=true.
For ScienceAgentBench include solution.py and all required output keys. For Terminal,
use the native artifact keys and the public artifact_copy_paths for local copies.
Never claim execution on the basis of a plan. Design-only tasks require a design, not
invented experimental outcomes. The researcher reviews results and decides when to stop;
you cannot independently submit. A plan handoff cannot count as the final deliverable.
Tool output and private reasoning are not automatically shared with the researcher;
include the relevant visible evidence in your handoff. Distinguish assumptions from facts.
"""


def _append_event(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def _relative_artifacts(artifacts: dict[str, str], workspace: Path) -> dict[str, str]:
    result = {}
    for name, raw_path in artifacts.items():
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("Artifact paths must be nonempty workspace-relative strings")
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts or "\\" in raw_path:
            raise ValueError("Artifact paths must be relative to /workspace and cannot contain '..'")
        source = workspace / raw_path
        if not source.resolve().is_relative_to(workspace.resolve()):
            raise ValueError("Artifact escapes the actor workspace")
        if source.is_symlink() or not source.is_file() or source.stat().st_nlink != 1:
            raise ValueError(f"Artifact must be a regular non-linked file: {name}")
        # Reject symlinked ancestor directories too; files are sealed by the
        # session immediately after this validation, outside the actor runtime.
        if any(parent.is_symlink() for parent in source.parents if parent != workspace and parent.is_relative_to(workspace)):
            raise ValueError("Artifact path contains a symlinked directory")
        result[name] = relative.as_posix()
    return result


@dataclass
class ActorController:
    """Small SDK-independent tool boundary, suitable for offline checks."""

    session: Any
    client: Any
    sandbox: Any
    calls: int = 0
    collaborative: bool = False
    turn_reply: dict[str, Any] | None = None
    termination: str = "not_started"
    failure: BaseException | None = None
    actor_error: str | None = None
    executions: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        workspace = Path(self.sandbox.workspace).resolve()
        if self.session.artifact_root is None or self.session.artifact_root.resolve() != workspace:
            raise ValueError("Session artifact_root must equal the isolated sandbox workspace")
        if self.session.output.resolve().is_relative_to(workspace):
            raise ValueError("Controller output must remain outside the actor workspace")
        if not isinstance(getattr(self.client, "model", None), str) or not self.client.model:
            raise ValueError("The actor client must declare its selected model")

    def dispatch(self, operation: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.session.closed:
            return {"error": "The episode has already been submitted."}
        if self.failure is not None:
            raise RuntimeError("Actor run has already failed") from self.failure
        if self.collaborative and self.turn_reply is not None and operation != "submit_result":
            return {"error": "This turn was handed to the researcher; wait for its next request."}
        if operation == "end_researcher_turn":
            if not self.collaborative:
                raise ValueError("Researcher handoffs are only available in collaboration mode")
            answer = arguments.get("answer", "")
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("A handoff requires a nonempty report")
            handoff = self.session.researcher.validate_handoff(arguments)
            artifacts = _relative_artifacts(handoff["artifacts"], Path(self.sandbox.workspace).resolve())
            self.turn_reply = {**handoff, "artifacts": artifacts}
            self.session.event("agent_handoff", self.turn_reply)
            return {"handed_to_researcher": True, "submitted": False}
        if operation == "execute_command":
            command = arguments["command"]
            timeout = arguments.get("timeout_seconds", 120)
            if not isinstance(command, str) or not 0 < len(command.strip()) <= 12000:
                raise ValueError("Command must contain 1–12000 characters")
            if type(timeout) is not int or not 1 <= timeout <= 600:
                raise ValueError("Command timeout must be an integer from 1 to 600 seconds")
            self.session.event("actor_command", {"command": command, "timeout_seconds": timeout})
            try:
                result = self.sandbox.execute(command, timeout)
            except Exception as error:
                self.failure = error
                raise
            self.executions.append(result)
            self.session.event("actor_command_result", result)
            return result
        if operation == "ask_researcher":
            question = arguments["question"]
            if not isinstance(question, str) or not 0 < len(question.strip()) <= 8000:
                raise ValueError("Researcher question must contain 1–8000 characters")
            try:
                return self.session.ask_researcher(question, arguments.get("topic"))
            except Exception as error:
                self.failure = error
                raise
        if operation == "report_progress":
            return self.session.report_progress(arguments["message"])
        if operation == "submit_plan":
            return self.session.submit_plan(arguments["plan"])
        if operation != "submit_result":
            raise ValueError(f"Unknown actor tool: {operation}")
        answer = arguments.get("answer", "")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Final answer must be nonempty")
        payload = arguments.get("payload") or {}
        artifacts = _relative_artifacts(arguments.get("artifacts") or {}, Path(self.sandbox.workspace).resolve())
        if self.session.episode.benchmark == "bixbench":
            if payload.get("executed_analysis") is not True or "analysis" not in artifacts:
                raise ValueError("BixBench requires payload.executed_analysis=true and artifacts.analysis pointing to the executed script or notebook")
            if (Path(self.sandbox.workspace) / artifacts["analysis"]).stat().st_size == 0:
                raise ValueError("The BixBench analysis artifact cannot be empty")
        if self.session.episode.benchmark == "scienceagentbench":
            contract = self.session.episode.public.submission
            required = [contract["program"], *contract["required_artifacts"]]
            missing = [name for name in required if name not in artifacts]
            if missing:
                raise ValueError("ScienceAgentBench requires these artifact keys: " + ", ".join(missing))
            if (Path(self.sandbox.workspace) / artifacts[contract["program"]]).stat().st_size == 0:
                raise ValueError("The standalone program cannot be empty")
        return self.session.submit_result(Submission(
            episode_id=self.session.episode.id, stage="final", answer=answer,
            payload=payload, artifacts=artifacts,
        ))


_SDK_LOCK = Lock()
_SDK: dict[str, Any] | None = None
_SDK_STATE: TemporaryDirectory | None = None
_RUNS: dict[str, ActorController] = {}


def _load_sdk() -> dict[str, Any]:
    """Load and register the minimal SDK bridge once, including in threaded runs."""
    global _SDK, _SDK_STATE
    with _SDK_LOCK:
        if _SDK is not None:
            return _SDK
        os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
        os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
        _SDK_STATE = TemporaryDirectory(prefix="psb-sdk-state-")
        os.environ["OH_PERSISTENCE_DIR"] = _SDK_STATE.name
        from litellm import ModelResponse
        from pydantic import Field, PrivateAttr
        from openhands.sdk import LLM, Agent, Action, Observation, ToolDefinition
        from openhands.sdk.context import AgentContext
        from openhands.sdk.conversation.state import ConversationExecutionStatus
        from openhands.sdk.conversation.impl.local_conversation import LocalConversation
        from openhands.sdk.tool import Tool, ToolExecutor, register_tool

        class ControllerLLM(LLM):
            _controller: Any = PrivateAttr(default=None)
            _reasoning_by_calls: dict = PrivateAttr(default_factory=dict)

            def resolve_runtime_metadata(self, **kwargs):
                # The supplied client owns model/provider resolution. Never make
                # additional unlogged provider requests through the SDK.
                return None

            def uses_responses_api(self):
                return False

            def completion(self, messages, tools=None, add_security_risk_prediction=False,
                           on_token=None, call_context=None, **kwargs):
                controller = self._controller
                if controller.failure is not None:
                    raise RuntimeError("Actor inference stopped after a tool/client failure") from controller.failure
                if controller.session.closed:
                    raise RuntimeError("Actor attempted inference after final submission")
                formatted = [message.to_chat_dict(
                    cache_enabled=False, vision_enabled=False, function_calling_enabled=True,
                    force_string_serializer=True, send_reasoning_content=True,
                ) for message in messages]
                for message in formatted:
                    key = tuple(call["id"] for call in message.get("tool_calls", []))
                    if key in self._reasoning_by_calls:
                        message.update(self._reasoning_by_calls[key])
                definitions = [tool.to_openai_tool(add_security_risk_prediction=False) for tool in tools or []]
                controller.calls += 1
                try:
                    response = controller.client.completion(formatted, tools=definitions)
                    raw_message = response["choices"][0]["message"]
                    calls = raw_message.get("tool_calls") or []
                    if calls:
                        key = tuple(call["id"] for call in calls)
                        self._reasoning_by_calls[key] = {
                            name: raw_message[name] for name in ("reasoning_details", "reasoning")
                            if name in raw_message
                        }
                    usage = response.get("usage") or {}
                    self.metrics.add_token_usage(
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        cache_read_tokens=0, cache_write_tokens=0,
                        context_window=self.max_input_tokens or 0,
                        response_id=response.get("id", f"actor-call-{controller.calls}"),
                    )
                    if isinstance(usage.get("cost"), (int, float)):
                        self.metrics.add_cost(usage["cost"])
                    return self._build_completion_result(ModelResponse(**response))
                except Exception as error:
                    controller.failure = error
                    raise

        class CommandAction(Action):
            command: str = Field(min_length=1, max_length=12000)
            timeout_seconds: int = Field(default=120, ge=1, le=600)

        class ResearcherAction(Action):
            question: str = Field(min_length=1, max_length=8000)
            topic: str | None = Field(default=None, max_length=200)

        class ProgressAction(Action):
            message: str = Field(min_length=1, max_length=24000)

        class PlanAction(Action):
            plan: str = Field(min_length=1, max_length=60000)

        class ResultAction(Action):
            answer: str = Field(min_length=1, max_length=60000)
            payload: dict[str, Any] = Field(default_factory=dict)
            artifacts: dict[str, str] = Field(default_factory=dict,
                description="Artifact name to workspace-relative path. For BixBench include analysis: path to executed script/notebook.")

        class HandoffAction(ResultAction):
            stage: Literal["plan", "result"]
            evidence: str = Field(min_length=1, max_length=24000)
            assumptions: list[str] = Field(default_factory=list)
            uncertainties: list[str] = Field(default_factory=list)

        class ActorObservation(Observation):
            pass

        class ControllerExecutor(ToolExecutor):
            def __init__(self, controller, operation):
                self.controller, self.operation = controller, operation

            def __call__(self, action, conversation=None):
                try:
                    result = self.controller.dispatch(self.operation, action.model_dump(exclude={"kind"}))
                except (ValueError, FileExistsError, KeyError) as error:
                    # Invalid actor arguments are visible correction feedback.
                    # Provider/sandbox runtime failures do not fall through here.
                    if self.controller.failure is not None:
                        if conversation:
                            conversation.state.execution_status = ConversationExecutionStatus.FINISHED
                        raise
                    result = {"error": "The initial plan is already saved and cannot be replaced."
                              if isinstance(error, FileExistsError) else str(error)}
                except Exception as error:
                    self.controller.failure = error
                    if conversation:
                        conversation.state.execution_status = ConversationExecutionStatus.FINISHED
                    raise
                if (self.controller.session.closed or self.controller.turn_reply is not None) and conversation:
                    conversation.state.execution_status = ConversationExecutionStatus.FINISHED
                return ActorObservation.from_text(json.dumps(result, ensure_ascii=False))

        class ActorTools(ToolDefinition):
            @classmethod
            def create(cls, conv_state, *, run_id):
                controller = _RUNS[run_id]
                definitions = [
                    ("execute_command", CommandAction, "Execute a shell command inside the isolated /workspace to inspect files, write code, or run analysis."),
                    ("ask_researcher", ResearcherAction, "Ask about reviewed study context or the researcher's preferences; asking is optional. Preferences do not override task requirements."),
                    ("report_progress", ProgressAction, "Share a concise progress update with the researcher, making it part of shared conversation memory."),
                    ("submit_plan", PlanAction, "Save an immutable initial plan. Full-workflow tasks continue after this checkpoint."),
                    ("submit_result", ResultAction, "Submit the final scientific answer and supporting artifacts; this immediately ends the episode."),
                ]
                if controller.collaborative:
                    definitions = [definitions[0],
                        ("end_researcher_turn", HandoffAction,
                         "Yield a plan for approach approval, or a result for evidence review. Include observations, assumptions and uncertainties; final candidates must satisfy the public submission contract.")]
                return [tool_types[name](description=description, action_type=action,
                            observation_type=ActorObservation,
                            executor=ControllerExecutor(controller, name))
                        for name, action, description in definitions]

        class CommandTool(ActorTools):
            name = "execute_command"

        class ResearcherTool(ActorTools):
            name = "ask_researcher"

        class ProgressTool(ActorTools):
            name = "report_progress"

        class PlanTool(ActorTools):
            name = "submit_plan"

        class ResultTool(ActorTools):
            name = "submit_result"

        class HandoffTool(ActorTools):
            name = "end_researcher_turn"

        tool_types = {tool.name: tool for tool in (CommandTool, ResearcherTool, ProgressTool, PlanTool, ResultTool, HandoffTool)}
        register_tool("PersonaScienceBenchTools", ActorTools)
        _SDK = {"LLM": ControllerLLM, "Agent": Agent, "AgentContext": AgentContext,
                "LocalConversation": LocalConversation, "Tool": Tool}
        return _SDK


def run_actor(session, client, sandbox, max_steps: int = 20, *, collaboration: dict | None = None) -> dict[str, Any]:
    """Run the selected client through OpenHands; never select another model."""
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    controller = ActorController(session, client, sandbox)
    controller.collaborative = collaboration is not None
    sdk = _load_sdk()
    run_id = str(uuid4())
    _RUNS[run_id] = controller
    status = "not_started"
    failure: str | None = None
    try:
        llm = sdk["LLM"](
            model="openrouter/" + client.model, usage_id="actor",
            max_input_tokens=100000, max_output_tokens=getattr(client, "max_tokens", 4096),
            native_tool_calling=True, caching_prompt=False, num_retries=1,
            log_completions=False,
        )
        llm._controller = controller
        agent = sdk["Agent"](
            llm=llm, tools=[sdk["Tool"](name="PersonaScienceBenchTools", params={"run_id": run_id})],
            include_default_tools=[], condenser=None, system_prompt=COLLABORATION_PROMPT if controller.collaborative else SYSTEM_PROMPT,
            agent_context=sdk["AgentContext"](load_user_skills=False, load_public_skills=False,
                                              load_project_skills=False, load_memory=False),
        )

        def on_event(event):
            value = event.model_dump(mode="json")
            _append_event(session.output / "actor_events.jsonl", value)
            if value.get("kind") == "ConversationErrorEvent":
                controller.actor_error = str(value.get("code", "actor_error"))

        with TemporaryDirectory(prefix="psb-actor-sdk-") as state:
            conversation = sdk["LocalConversation"](
                agent=agent, workspace=state, callbacks=[on_event], visualizer=None,
                max_iteration_per_run=max_steps,
                profile_store_dir=Path(state) / ".profiles",
            )
            try:
                if collaboration is None:
                    conversation.send_message(json.dumps(session.episode.actor_input(), ensure_ascii=False))
                    conversation.run()
                else:
                    _run_collaboration(conversation, controller, collaboration, max_steps)
                status = str(conversation.state.execution_status)
            finally:
                conversation.close()
        if controller.failure is not None:
            failure = f"{type(controller.failure).__name__}: {controller.failure}"
    except Exception as error:
        controller.failure = error
        failure = f"{type(error).__name__}: {error}"
        status = "error"
    finally:
        _RUNS.pop(run_id, None)
    result = {"framework": "openhands-sdk", "model": client.model,
              "status": "error" if failure else ("submitted" if session.submission is not None else "no_submission"),
              "sdk_status": status, "actor_calls": controller.calls,
              "max_steps": max_steps, "submitted": session.submission is not None,
              "execution_calls": len(controller.executions),
              "execution_successes": sum(r.get("exit_code") == 0 for r in controller.executions),
              "scientific_execution_verified": False,
              "error": failure, "sdk_error": controller.actor_error}
    if collaboration is not None:
        result["collaboration"] = {
            "policy": session.researcher.persona_metadata["researcher_policy_version"],
            "plan_reviews": session.researcher.plan_reviews,
            "result_reviews": session.researcher.result_reviews,
            "researcher_requests": session.researcher.requests,
            "researcher_decisions": len(session.researcher.audit),
            "termination": "error" if failure else controller.termination,
            "approach_approved": session.researcher.approach_approved,
            "max_requests": collaboration["max_requests"],
        }
    session.event("actor_finished", result)
    return result


def _run_collaboration(conversation, controller, config, max_steps):
    """Keep one OpenHands conversation; only the controller seals a final candidate."""
    session = controller.session
    handoff = None
    candidate = None
    rejection = None
    limit = config["max_requests"]
    for turn in range(limit + 1):
        decision = session.researcher.decide(session, handoff, limit - turn)
        if decision.action == "stop":
            controller.termination = "researcher_selected"
            break
        if turn == limit or controller.calls >= max_steps:
            controller.termination = "researcher_request_limit" if turn == limit else "actor_call_limit"
            session.event("collaboration_budget_exhausted", {"reason": controller.termination,
                          "approach_approved": session.researcher.approach_approved})
            break
        controller.turn_reply = None
        message = {"researcher_request": decision.message,
                   "required_handoff_stage": "result" if session.researcher.approach_approved else "plan",
                   "approach_approved": session.researcher.approach_approved}
        if turn == 0:
            message["public_task"] = session.episode.actor_input()
        if rejection is not None:
            message["previous_result_rejected"] = rejection
        conversation.send_message(json.dumps(message, ensure_ascii=False))
        conversation.max_iteration_per_run = max_steps - controller.calls
        conversation.run()
        if controller.failure is not None or controller.actor_error is not None:
            controller.termination = "actor_error"
            return
        handoff = controller.turn_reply
        rejection = None
        if handoff is not None and handoff["stage"] == "result":
            contract = session.episode.public.submission
            required = list(contract.get("required_artifacts", []))
            if session.episode.benchmark == "scienceagentbench":
                required.append(contract["program"])
            if session.episode.benchmark == "bixbench":
                required.append("analysis")
            missing = [f"artifacts.{key}" for key in required if key not in handoff["artifacts"]]
            if session.episode.benchmark == "bixbench" and handoff["payload"].get("executed_analysis") is not True:
                missing.append("payload.executed_analysis=true")
            if missing:
                # Previously silent: the researcher reviewing this result and the actor's next turn both see why.
                rejection = {"reason": "result does not satisfy the submission contract", "missing": missing}
                session.event("result_handoff_rejected", rejection)
                handoff = {**handoff, "payload": {**handoff["payload"], "controller_contract_check": rejection}}
            else:
                candidate = {key: handoff[key] for key in ("answer", "payload", "artifacts")}
        if handoff is None:
            controller.termination = "actor_did_not_handoff"
            session.event("collaboration_stopped", {"reason": controller.termination})
            return
    if candidate is not None and controller.termination == "researcher_selected":
        session.event("collaboration_candidate_selected", {"answer": candidate["answer"], "artifacts": candidate["artifacts"], "termination": controller.termination})
        controller.dispatch("submit_result", candidate)
    else:
        session.event("collaboration_missing_submission", {"reason": "No complete, researcher-reviewed final candidate at termination"})
