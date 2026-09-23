"""Pinned OpenHands actor adapter with a separately budgeted inference gateway."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

# Avoid LiteLLM's remote price-map download; live catalog checks use our gateway.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")
# The pinned SDK checks default vision profiles for text-only models even when
# default tools are disabled. Keep that lookup away from personal profiles and
# credentials. The SDK freezes this path at import time.
_SDK_PERSISTENCE = TemporaryDirectory(prefix="expbench-sdk-state-")
os.environ["OH_PERSISTENCE_DIR"] = _SDK_PERSISTENCE.name

from litellm import ModelResponse
from pydantic import Field, PrivateAttr
from openhands.sdk import LLM, Agent, Action, Observation, ToolDefinition
from openhands.sdk.context import AgentContext
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.conversation.impl.local_conversation import LocalConversation
from openhands.sdk.tool import Tool, ToolExecutor, register_tool

from expbench import prompts
from expbench.artifacts import append_jsonl
from expbench.gateway import ModelError
from expbench.schema import Design


class GatewayLLM(LLM):
    """Only inference is customized; planning/history/tool execution stay in SDK."""

    _episode: object = PrivateAttr(default=None)
    _reasoning_by_call: dict = PrivateAttr(default_factory=dict)

    def resolve_runtime_metadata(self, **kwargs):
        # The controller preflights OpenRouter. No unbudgeted provider calls here.
        return None

    def uses_responses_api(self):
        return False

    def completion(self, messages, tools=None, add_security_risk_prediction=False,
                   on_token=None, call_context=None, **kwargs):
        if self._episode.design is not None:
            raise ModelError("Actor attempted inference after design submission")
        self._episode.actor_calls += 1
        formatted = [message.to_chat_dict(
            cache_enabled=False, vision_enabled=False, function_calling_enabled=True,
            force_string_serializer=True, send_reasoning_content=True,
        ) for message in messages]
        for message in formatted:
            calls = message.get("tool_calls", [])
            key = tuple(call["id"] for call in calls)
            if key and key in self._reasoning_by_call:
                message.update(self._reasoning_by_call[key])
        try:
            response = self._episode.gateway.complete(
                "actor", formatted,
                tools=[tool.to_openai_tool(add_security_risk_prediction=False)
                       for tool in tools or []],
            )
        except Exception as exc:
            self._episode.failure = exc
            raise
        raw_message = response["choices"][0]["message"]
        calls = raw_message.get("tool_calls") or []
        if calls:
            key = tuple(call["id"] for call in calls)
            self._reasoning_by_call[key] = {
                k: raw_message[k] for k in ("reasoning_details", "reasoning")
                if k in raw_message
            }
        usage = response["usage"]
        self.metrics.add_cost(self._episode.gateway.ledger.records[-1]["budget_charge_usd"])
        self.metrics.add_token_usage(
            prompt_tokens=usage["prompt_tokens"], completion_tokens=usage["completion_tokens"],
            cache_read_tokens=0, cache_write_tokens=0,
            context_window=self.max_input_tokens or 0, response_id=response["id"],
        )
        return self._build_completion_result(ModelResponse(**response))


class AskResearcherAction(Action):
    question: str = Field(min_length=1, max_length=4000)


class ReadContextAction(Action):
    name: str = Field(description="Exact document name from the public task", max_length=200)


class SubmitDesignAction(Action):
    design: Design


class BenchmarkObservation(Observation):
    """Concrete observation type required by the SDK's discriminated union."""


class BenchmarkExecutor(ToolExecutor):
    def __init__(self, episode, operation):
        self.episode = episode
        self.operation = operation

    def __call__(self, action, conversation=None):
        if self.episode.design is not None:
            return BenchmarkObservation.from_text("The design has already been submitted.")
        if self.operation == "ask_researcher":
            try:
                text = self.episode.researcher.ask(action.question)
            except Exception as exc:
                # SDK may turn executor exceptions into observations. Preserve the
                # terminal failure outside the agent so it cannot silently continue.
                self.episode.failure = exc
                if conversation:
                    conversation.state.execution_status = ConversationExecutionStatus.FINISHED
                raise
        elif self.operation == "read_context":
            # In-memory allowlist, not an arbitrary path read or a shell command.
            text = self.episode.task.public.documents.get(action.name,
                "Unknown document. Available: " + ", ".join(self.episode.task.public.documents))
        else:
            self.episode.submit(action.design)
            if conversation:
                conversation.state.execution_status = ConversationExecutionStatus.FINISHED
            text = "Final design accepted. This episode is complete."
        return BenchmarkObservation.from_text(text)


class AskResearcherTool(ToolDefinition):
    @classmethod
    def create(cls, conv_state=None, *, episode):
        return [cls(description="Ask the researcher for missing task facts. Each call consumes one question.",
                    action_type=AskResearcherAction, observation_type=BenchmarkObservation,
                    executor=BenchmarkExecutor(episode, "ask_researcher"))]


class ReadContextTool(ToolDefinition):
    @classmethod
    def create(cls, conv_state=None, *, episode):
        return [cls(description="Read one permitted public context document by its exact name.",
                    action_type=ReadContextAction, observation_type=BenchmarkObservation,
                    executor=BenchmarkExecutor(episode, "read_context"))]


class SubmitDesignTool(ToolDefinition):
    @classmethod
    def create(cls, conv_state=None, *, episode):
        return [cls(description="Submit the complete final experimental design. This immediately ends the episode.",
                    action_type=SubmitDesignAction, observation_type=BenchmarkObservation,
                    executor=BenchmarkExecutor(episode, "submit_design"))]


_EPISODES = {}


class ExpBenchTools(ToolDefinition):
    @classmethod
    def create(cls, conv_state, *, episode_id):
        episode = _EPISODES[episode_id]
        tool_classes = [ReadContextTool, SubmitDesignTool]
        if episode.config.limits.researcher_questions > 0:
            tool_classes.insert(1, AskResearcherTool)
        return [tool for tool_cls in tool_classes
                for tool in tool_cls.create(conv_state, episode=episode)]


register_tool("ExpBenchTools", ExpBenchTools)


def run_actor(episode):
    episode_id = str(uuid4())
    _EPISODES[episode_id] = episode
    config = episode.config
    llm = GatewayLLM(
        model="openrouter/" + config.models.actor.model, usage_id="actor",
        max_input_tokens=100_000, max_output_tokens=config.models.actor.max_output_tokens,
        native_tool_calling=True, caching_prompt=False, num_retries=1,
        log_completions=False,
    )
    llm._episode = episode
    agent = Agent(
        llm=llm, tools=[Tool(name="ExpBenchTools", params={"episode_id": episode_id})],
        include_default_tools=[], condenser=None,
        system_prompt=(prompts.ACTOR if config.limits.researcher_questions > 0
                       else prompts.ACTOR_STATIC),
        agent_context=AgentContext(load_user_skills=False, load_public_skills=False,
                                   load_project_skills=False, load_memory=False),
    )

    def on_event(event):
        value = event.model_dump(mode="json")
        append_jsonl(episode.output / "actor_events.jsonl", value)
        if value.get("kind") == "ConversationErrorEvent":
            episode.actor_error = value.get("code", "actor_error")

    try:
        # Empty temporary workspace; only in-memory public documents are exposed.
        with TemporaryDirectory(prefix="expbench-actor-") as workspace:
            conversation = LocalConversation(
                agent=agent, workspace=workspace, callbacks=[on_event], visualizer=None,
                max_iteration_per_run=config.limits.actor_steps,
                profile_store_dir=Path(workspace) / ".profiles",
            )
            try:
                conversation.send_message(json.dumps({
                    "question": episode.task.public.question,
                    "context": episode.task.public.context,
                    "documents": list(episode.task.public.documents),
                    "question_budget": config.limits.researcher_questions,
                    "actor_step_budget": config.limits.actor_steps,
                }))
                conversation.run()
                episode.actor_status = str(conversation.state.execution_status)
            finally:
                conversation.close()
    finally:
        _EPISODES.pop(episode_id, None)
