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
from typing import Any
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

        class ActorObservation(Observation):
            pass

        class ControllerExecutor(ToolExecutor):
            def __init__(self, controller, operation):
                self.controller, self.operation = controller, operation

            def __call__(self, action, conversation=None):
                try:
                    result = self.controller.dispatch(self.operation, action.model_dump())
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
                if self.controller.session.closed and conversation:
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

        tool_types = {tool.name: tool for tool in (CommandTool, ResearcherTool, ProgressTool, PlanTool, ResultTool)}
        register_tool("PersonaScienceBenchTools", ActorTools)
        _SDK = {"LLM": ControllerLLM, "Agent": Agent, "AgentContext": AgentContext,
                "LocalConversation": LocalConversation, "Tool": Tool}
        return _SDK


def run_actor(session, client, sandbox, max_steps: int = 20) -> dict[str, Any]:
    """Run the selected client through OpenHands; never select another model."""
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    controller = ActorController(session, client, sandbox)
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
            include_default_tools=[], condenser=None, system_prompt=SYSTEM_PROMPT,
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
                conversation.send_message(json.dumps(session.episode.actor_input(), ensure_ascii=False))
                conversation.run()
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
    session.event("actor_finished", result)
    return result
