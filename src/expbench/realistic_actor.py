"""OpenHands actor with natural-language plans and an isolated execution tool."""

import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from pydantic import Field

# Import establishes the isolated SDK profile store before importing SDK classes.
from expbench.actor import GatewayLLM, BenchmarkObservation
from expbench.artifacts import append_jsonl
from expbench.gateway import ModelError
from expbench import realistic_prompts as prompts
from openhands.sdk import Agent, Action, ToolDefinition
from openhands.sdk.context import AgentContext
from openhands.sdk.conversation.state import ConversationExecutionStatus
from openhands.sdk.conversation.impl.local_conversation import LocalConversation
from openhands.sdk.tool import Tool, ToolExecutor, register_tool


class InspectRepositoryAction(Action):
    path: str = Field(default=".", max_length=1000)


class ExecuteCheckAction(Action):
    command: str = Field(min_length=1, max_length=12000)
    timeout_seconds: int = Field(default=60, ge=1, le=600)


class AskScopedResearcherAction(Action):
    topic: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=4000)


class SubmitPlanAction(Action):
    plan: str = Field(min_length=1, max_length=60000, description="Your proposed research plan in natural language.")


class FinishExperimentAction(Action):
    design: str = Field(min_length=1, max_length=60000, description="Your final design, including any changes to the initial plan.")
    conclusion: str = Field(min_length=1, max_length=30000, description="What the observed evidence establishes and what remains incomplete.")
    reproduction_command: str | None = Field(default=None, max_length=12000)


class RealisticExecutor(ToolExecutor):
    def __init__(self, episode, operation):
        self.episode, self.operation = episode, operation

    def __call__(self, action, conversation=None):
        e = self.episode
        if e.design is not None:
            return BenchmarkObservation.from_text("The episode is complete.")
        if self.operation == "inspect_repository":
            text = e.inspect(action.path)
        elif self.operation == "execute_check":
            text = json.dumps(e.execute(action.command, action.timeout_seconds))
        elif self.operation == "ask_researcher":
            try:
                text = e.researcher.ask(action.topic, action.question)
            except Exception as exc:
                e.failure = exc
                if conversation:
                    conversation.state.execution_status = ConversationExecutionStatus.FINISHED
                raise
        elif self.operation == "submit_plan":
            if e.initial is not None:
                return BenchmarkObservation.from_text("The initial plan is already saved and cannot be replaced.")
            e.checkpoint("initial", action.plan)
            if e.workflow:
                text = "Initial plan saved. Continue implementing and executing; finish with finish_experiment."
            else:
                e.design = action.plan
                text = "Plan saved. The design episode is complete."
        else:
            if not e.workflow or e.initial is None:
                return BenchmarkObservation.from_text("Submit your initial plan before finishing a full workflow.")
            e.checkpoint("final", action.design, action.conclusion)
            e.reproduction_command = action.reproduction_command
            e.design = action.design
            text = "Final design and conclusion saved. Execution verification is a separate check."
        if e.design is not None and conversation:
            conversation.state.execution_status = ConversationExecutionStatus.FINISHED
        return BenchmarkObservation.from_text(text)


_EPISODES = {}


class RealisticTools(ToolDefinition):
    @classmethod
    def create(cls, conv_state, *, episode_id):
        episode = _EPISODES[episode_id]
        definitions = [
            ("inspect_repository", InspectRepositoryAction, "List a repository directory or read a text file. Paths are relative to the task workspace."),
            ("execute_check", ExecuteCheckAction, "Run a shell command in the isolated task workspace. Use small exploratory checks before submitting your plan."),
            ("submit_plan", SubmitPlanAction, "Save your initial research plan in natural language."),
        ]
        if episode.input_mode == "interactive":
            definitions.append(("ask_researcher", AskScopedResearcherAction, "Ask a focused question about one available researcher topic."))
        if episode.workflow:
            definitions.append(("finish_experiment", FinishExperimentAction, "Save the final design, evidence-based conclusion and optional reproduction command."))
        return [_TOOL_TYPES[name](description=description, action_type=action,
                    observation_type=BenchmarkObservation,
                    executor=RealisticExecutor(episode, name))
                for name, action, description in definitions]


class InspectRepositoryTool(RealisticTools):
    name = "inspect_repository"


class ExecuteCheckTool(RealisticTools):
    name = "execute_check"


class ScopedAskTool(RealisticTools):
    name = "ask_researcher"


class SubmitPlanTool(RealisticTools):
    name = "submit_plan"


class FinishExperimentTool(RealisticTools):
    name = "finish_experiment"


_TOOL_TYPES = {t.name: t for t in (InspectRepositoryTool, ExecuteCheckTool,
                                  ScopedAskTool, SubmitPlanTool, FinishExperimentTool)}


register_tool("RealisticTools", RealisticTools)


class RealisticLLM(GatewayLLM):
    def completion(self, *args, **kwargs):
        if time.monotonic() >= self._episode.deadline:
            raise ModelError("Episode reached its wall-time limit")
        return super().completion(*args, **kwargs)


def run_actor(episode):
    episode_id = str(uuid4())
    _EPISODES[episode_id] = episode
    llm = RealisticLLM(model="openrouter/" + episode.config.models.actor.model,
                       usage_id="actor", max_input_tokens=100000,
                       max_output_tokens=episode.config.models.actor.max_output_tokens,
                       native_tool_calling=True, caching_prompt=False, num_retries=1,
                       log_completions=False)
    llm._episode = episode
    agent = Agent(llm=llm, tools=[Tool(name="RealisticTools", params={"episode_id": episode_id})],
                  include_default_tools=[], condenser=None,
                  system_prompt=prompts.ACTOR + (prompts.WORKFLOW if episode.workflow else prompts.DESIGN_END),
                  agent_context=AgentContext(load_user_skills=False, load_public_skills=False,
                                             load_project_skills=False, load_memory=False))
    try:
        with TemporaryDirectory(prefix="expbench-realistic-sdk-") as state:
            conversation = LocalConversation(agent=agent, workspace=state,
                callbacks=[lambda event: append_jsonl(episode.output / "actor_events.jsonl", event.model_dump(mode="json"))],
                visualizer=None, max_iteration_per_run=episode.config.limits.actor_steps,
                profile_store_dir=Path(state) / ".profiles")
            try:
                conversation.send_message(json.dumps(episode.actor_input(), ensure_ascii=False))
                conversation.run()
                episode.actor_status = str(conversation.state.execution_status)
            finally:
                conversation.close()
    finally:
        _EPISODES.pop(episode_id, None)
