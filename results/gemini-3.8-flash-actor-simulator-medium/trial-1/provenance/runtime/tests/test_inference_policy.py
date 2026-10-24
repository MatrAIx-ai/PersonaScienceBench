"""OpenRouter policy checks with an in-memory transport; no API calls."""

from copy import deepcopy
import json
from types import SimpleNamespace
import sys

import pytest

from personasciencebench.inference import OpenRouterClient
from personasciencebench.researcher import Researcher
from personasciencebench.schema import Episode, EvaluatorSpec, PublicContext, Submission
from personasciencebench.session import EpisodeSession


def response(content="synthetic completion", finish_reason="stop"):
    return {
        "id": "synthetic-response", "model": "resolved-synthetic-model",
        "provider": "synthetic-provider", "usage": {"prompt_tokens": 7, "completion_tokens": 3, "cost": 0.0001},
        "choices": [{"finish_reason": finish_reason, "message": {"content": content}}],
    }


@pytest.fixture
def transport(monkeypatch):
    class TransportError(Exception):
        pass
    state = SimpleNamespace(calls=[], data=response(), status_code=200)
    def post(url, **kwargs):
        state.calls.append({"url": url, **deepcopy(kwargs)})
        return SimpleNamespace(status_code=state.status_code, json=lambda: deepcopy(state.data))
    monkeypatch.setitem(sys.modules, "httpx", SimpleNamespace(post=post, HTTPError=TransportError))
    monkeypatch.setenv("OPENROUTER_API_KEY", "NONSECRET_UNIT_TEST_KEY")
    return state


def test_reasoning_none_is_forwarded_verbatim_and_constructor_is_lazy(transport):
    client = OpenRouterClient("synthetic-model", role="actor", reasoning_effort="none")
    assert transport.calls == []
    assert client.complete([{"role": "user", "content": "Synthetic question"}]) == "synthetic completion"
    request = transport.calls[0]["json"]
    assert request["reasoning"] == {"effort": "none"}
    assert request["provider"] == {"require_parameters": True, "allow_fallbacks": False}
    assert "temperature" not in request


def test_tool_completion_can_have_null_content(transport):
    transport.data = response(None, "tool_calls")
    tool_calls = [{"id": "call-test", "type": "function", "function": {
        "name": "ask_researcher", "arguments": '{"question":"Synthetic question"}',
    }}]
    transport.data["choices"][0]["message"]["tool_calls"] = tool_calls
    tools = [{"type": "function", "function": {"name": "ask_researcher", "parameters": {"type": "object"}}}]
    client = OpenRouterClient("synthetic-model", role="actor", reasoning_effort="none")
    completion = client.completion([{"role": "user", "content": "Synthetic question"}], tools=tools)
    assert completion["choices"][0]["message"]["content"] is None
    assert completion["choices"][0]["message"]["tool_calls"] == tool_calls
    assert transport.calls[0]["json"]["tools"] == tools
    # The plain-text judge/researcher interface must still reject this response.
    with pytest.raises(RuntimeError):
        client.complete([{"role": "user", "content": "Synthetic question"}])


@pytest.mark.parametrize("policy,catalog", [
    ("reject", ["max_tokens"]),
    ("omit_and_record", None),
])
def test_native_settings_are_preserved_without_both_opt_in_and_catalog(transport, policy, catalog):
    settings = {"temperature": 0.9, "max_tokens": 91, "frequency_penalty": 0.4,
                "presence_penalty": 0.2, "seed": 22}
    records = []
    client = OpenRouterClient("synthetic-model", role="judge", record=records.append,
                              unsupported_parameters=policy, supported_parameters=catalog)
    client.complete([{"role": "user", "content": "Synthetic grade"}], settings=settings)
    assert all(transport.calls[0]["json"][key] == value for key, value in settings.items())
    assert records[0]["requested_native_settings"] == settings
    assert records[0]["omitted_native_settings"] == {}
    assert client.parameter_adaptations == []


def test_explicit_omit_policy_uses_catalog_and_logs_exact_native_changes(transport):
    settings = {"temperature": 0.9, "max_tokens": 91, "frequency_penalty": 0.4,
                "presence_penalty": 0.2, "seed": 22}
    records = []
    client = OpenRouterClient("synthetic-model", role="judge", record=records.append,
                              unsupported_parameters="omit_and_record",
                              supported_parameters=["max_tokens", "seed"])
    client.complete([{"role": "user", "content": "Synthetic grade"}], settings=settings)
    omitted = {"temperature": 0.9, "frequency_penalty": 0.4, "presence_penalty": 0.2}
    request = transport.calls[0]["json"]
    assert all(key not in request for key in omitted)
    assert request["max_tokens"] == 91 and request["seed"] == 22
    assert records[0]["requested_native_settings"] == settings
    assert records[0]["omitted_native_settings"] == omitted
    assert client.parameter_adaptations[0]["omitted_native_settings"] == omitted
    assert client.parameter_adaptations[0]["replacement"] == "provider_defaults"
    assert records[0]["automatic_retries"] == 0
    assert "NONSECRET_UNIT_TEST_KEY" not in json.dumps(records)


def test_omitted_native_temperature_is_not_reintroduced_from_client_default(transport):
    records = []
    client = OpenRouterClient("synthetic-model", role="judge", temperature=0.3,
                              unsupported_parameters="omit_and_record",
                              supported_parameters=["max_tokens"], record=records.append)
    client.complete([{"role": "user", "content": "Synthetic grade"}], settings={"temperature": 0.9})
    assert "temperature" not in transport.calls[0]["json"]
    assert records[0]["omitted_native_settings"]["temperature"] == 0.9


@pytest.mark.parametrize("finish_reason", ["length", "error", "content_filter"])
def test_paid_incomplete_completion_records_usage_before_raising(transport, finish_reason):
    transport.data = response("Partial synthetic completion", finish_reason)
    records = []
    client = OpenRouterClient("synthetic-model", role="judge", record=records.append)
    with pytest.raises(RuntimeError, match="incomplete"):
        client.complete([{"role": "user", "content": "Synthetic grade"}])
    assert len(transport.calls) == 1 and len(records) == 1
    assert records[0]["usage"] == transport.data["usage"]
    assert records[0]["response"]["choices"][0]["finish_reason"] == finish_reason
    assert records[0]["automatic_retries"] == 0


def test_error_response_with_usage_remains_logged_and_unscored(transport):
    transport.data = {"error": {"message": "synthetic provider-side error"},
                      "usage": {"total_tokens": 9, "cost": 0.0001}}
    records = []
    client = OpenRouterClient("synthetic-model", role="researcher", record=records.append)
    with pytest.raises(RuntimeError, match="error response"):
        client.complete([{"role": "user", "content": "Synthetic question"}])
    assert len(transport.calls) == len(records) == 1
    assert records[0]["usage"]["total_tokens"] == 9


def test_unknown_settings_are_rejected_before_transport(transport):
    client = OpenRouterClient("synthetic-model", role="judge")
    with pytest.raises(ValueError, match="Unsupported generation settings"):
        client.complete([{"role": "user", "content": "Synthetic question"}], settings={"stream": True})
    assert transport.calls == []


def test_actor_cannot_forge_controller_execution_receipt(tmp_path):
    episode = Episode(id="synthetic:one", benchmark="synthetic", source_task_id="one",
                      study_id="synthetic-study", domain="synthetic", source_revision="v1",
                      public=PublicContext(question="Synthetic task"),
                      evaluator=EvaluatorSpec(kind="synthetic", version="v1"))
    class UnusedBackend:
        def complete(self, *args, **kwargs):
            pytest.fail("Receipt validation must not call a model")
    session = EpisodeSession(episode, Researcher(episode, UnusedBackend()), tmp_path / "controller")
    with pytest.raises(ValueError, match="controller execution receipts"):
        session.submit_result(Submission(episode_id=episode.id, answer="Synthetic answer",
                                         payload={"controller_execution_receipt": {"verified": True}}))
    assert session.closed is False and session.submission is None
    assert not (session.output / "submission.json").exists()


@pytest.mark.parametrize("prefix,suffix", [("", ""), (" \n", "\n\t ")])
def test_canonical_json_object_unwraps_only_a_complete_valid_object(prefix, suffix):
    from personasciencebench.inference import canonical_json_object
    payload = '{"score": 0.0100, "exponent": 1e2, "text": "inside ``` is data", "flag": false, "nested": {"items": [null, 2]}}'
    wrapped = prefix + "```json\n" + payload + "\n```" + suffix
    normalized = canonical_json_object(wrapped)
    assert not normalized.lstrip().startswith("```")
    assert json.loads(normalized) == json.loads(payload)
    assert json.loads(normalized)["text"] == "inside ``` is data"


@pytest.mark.parametrize("original", [
    '```json\n{"score": }\n```',
    '```json\n{"score": 1,}\n```',
    '```json\n{"score": NaN}\n```',
    '```json\n{"score": Infinity}\n```',
    '```json\n[1, 2]\n```',
    '```json\n"a string"\n```',
    '```json\n42\n```',
    '```json\nnull\n```',
    'Here is the grade:\n```json\n{"score": 1}\n```',
    '```json\n{"score": 1}\n```\nAdditional explanation.',
    '```json\n{"score": 1}\n```\n```json\n{"score": 0}\n```',
    '```json\n{"score": 1}',
    ' \n{"score": 1}\n ',
    '```python\n{"score": 1}\n```',
])
def test_canonical_json_object_does_not_repair_invalid_or_nonobject_outputs(original):
    from personasciencebench.inference import canonical_json_object
    assert canonical_json_object(original) == original


def test_json_mode_normalization_preserves_raw_api_response_and_records(transport):
    payload = '{"score": 1, "explanation": "Synthetic reference comparison"}'
    raw = "```json\n" + payload + "\n```"
    transport.data = response(raw)
    records = []
    client = OpenRouterClient("synthetic-model", role="judge", record=records.append)
    result = client.complete([{"role": "user", "content": "Synthetic grade"}], json_mode=True)
    assert json.loads(result) == json.loads(payload)
    assert records[0]["response"]["choices"][0]["message"]["content"] == raw
    assert transport.data["choices"][0]["message"]["content"] == raw
    assert len(client.format_adaptations) == 1
    native_completion = client.completion([{"role": "user", "content": "Synthetic grade"}], json_mode=True)
    assert native_completion["choices"][0]["message"]["content"] == raw
    assert records[1]["response"]["choices"][0]["message"]["content"] == raw
    assert len(client.format_adaptations) == 1


def test_non_json_mode_never_unwraps_model_output(transport):
    raw = '```json\n{"score": 1}\n```'
    transport.data = response(raw)
    client = OpenRouterClient("synthetic-model", role="judge")
    assert client.complete([{"role": "user", "content": "Synthetic grade"}], json_mode=False) == raw
    assert client.format_adaptations == []


def _cached_judge_entry(messages, content="cached synthetic judgement", *, json_mode=False,
                        settings=None, finish_reason="stop"):
    request = {"messages": messages, "model": "synthetic-model", "max_tokens": 2048,
               "reasoning": {"effort": "none"}}
    if json_mode:
        request["response_format"] = {"type": "json_object"}
    request.update(settings or {})
    data = response(content, finish_reason)
    return {"request": request, "response": data,
            "requested_native_settings": settings or {}, "omitted_native_settings": {},
            "usage": data["usage"]}


def test_replay_exact_completed_prefix_uses_no_api_and_preserves_raw_cache(transport, tmp_path):
    from personasciencebench.inference import ReplayJudge
    messages = [{"role": "user", "content": "Synthetic cached request"}]
    raw = '```json\n{"score": 1}\n```'
    entry = _cached_judge_entry(messages, raw, json_mode=True)
    source = tmp_path / "cached.jsonl"
    source.write_text(json.dumps(entry) + "\n")
    before = source.read_bytes()
    api_records, replay_records = [], []
    client = OpenRouterClient("synthetic-model", role="judge", reasoning_effort="none", record=api_records.append)
    replay = ReplayJudge(client, source, replay_records.append)
    assert json.loads(replay.complete(messages, json_mode=True)) == {"score": 1}
    assert transport.calls == [] and api_records == []
    assert source.read_bytes() == before
    assert replay.index == 1 and len(replay_records) == 1
    assert replay_records[0]["request_identical"] is True
    assert replay_records[0]["additional_model_call"] is False
    assert replay_records[0]["record_index"] == 0
    assert "usage" not in replay_records[0] and "cost" not in replay_records[0]
    assert len(client.format_adaptations) == 1


@pytest.mark.parametrize("changed", ["prompt", "model", "json_mode", "effort", "settings"])
def test_replay_rejects_changed_request_instead_of_substituting_a_judgement(transport, tmp_path, changed):
    from personasciencebench.inference import ReplayJudge
    messages = [{"role": "user", "content": "Original synthetic request"}]
    source = tmp_path / "cached.jsonl"
    source.write_text(json.dumps(_cached_judge_entry(messages)) + "\n")
    client = OpenRouterClient("changed-model" if changed == "model" else "synthetic-model",
                              role="judge", reasoning_effort="low" if changed == "effort" else "none")
    events = []
    replay = ReplayJudge(client, source, events.append)
    call_messages = [{"role": "user", "content": "Different synthetic request"}] if changed == "prompt" else messages
    with pytest.raises(ValueError, match="Cached judge request differs"):
        replay.complete(call_messages, json_mode=changed == "json_mode",
                        settings={"temperature": 0.2} if changed == "settings" else None)
    assert transport.calls == [] and events == [] and replay.index == 0


@pytest.mark.parametrize("finish_reason", ["length", "error", "tool_calls"])
def test_replay_rejects_incomplete_cached_judgements(transport, tmp_path, finish_reason):
    from personasciencebench.inference import ReplayJudge
    messages = [{"role": "user", "content": "Synthetic request"}]
    source = tmp_path / "cached.jsonl"
    source.write_text(json.dumps(_cached_judge_entry(messages, finish_reason=finish_reason)) + "\n")
    client = OpenRouterClient("synthetic-model", role="judge", reasoning_effort="none")
    events = []
    replay = ReplayJudge(client, source, events.append)
    with pytest.raises(ValueError, match="Only completed text judgements"):
        replay.complete(messages)
    assert transport.calls == [] and events == [] and replay.index == 0


def test_replay_invokes_client_only_after_cached_prefix_without_double_charging(transport, tmp_path):
    from personasciencebench.inference import ReplayJudge
    cached_messages = [{"role": "user", "content": "First synthetic request"}]
    new_messages = [{"role": "user", "content": "Second synthetic request"}]
    entry = _cached_judge_entry(cached_messages)
    source = tmp_path / "cached.jsonl"
    source.write_text(json.dumps(entry) + "\n")
    api_records, replay_records = [], []
    client = OpenRouterClient("synthetic-model", role="judge", reasoning_effort="none", record=api_records.append)
    replay = ReplayJudge(client, source, replay_records.append)
    assert replay.complete(cached_messages) == "cached synthetic judgement"
    assert transport.calls == []
    assert replay.complete(new_messages) == "synthetic completion"
    assert len(transport.calls) == len(api_records) == len(replay_records) == 1
    assert transport.calls[0]["json"]["messages"] == new_messages
    assert api_records[0]["usage"] == transport.data["usage"]
    assert replay_records[0]["additional_model_call"] is False
    assert "usage" not in replay_records[0]
    assert sum(item["usage"]["cost"] for item in api_records) == transport.data["usage"]["cost"]
