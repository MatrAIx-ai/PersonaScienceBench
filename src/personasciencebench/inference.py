"""Optional model transports; no inference at import or preparation time."""

import json
import os
from pathlib import Path
import re
from typing import Callable


class OpenRouterClient:
    provider_name = "OpenRouter"
    key_variable = "OPENROUTER_API_KEY"

    def __init__(self, model: str, *, role: str, max_tokens: int = 2048,
                 temperature: float | None = None, reasoning_effort: str | None = None,
                 timeout: float = 180, provider: str = "openrouter",
                 unsupported_parameters: str = "reject", supported_parameters: list[str] | None = None,
                 record: Callable[[dict], None] | None = None):
        if not model or not isinstance(model, str):
            raise ValueError(f"Select a model for the {role} role before inference")
        self.model, self.role = model, role
        self.provider = provider
        if provider == "openai":
            # Records and errors name the transport actually used.
            self.provider_name, self.key_variable = "OpenAI", "OPENAI_API_KEY"
        if provider not in ("openrouter", "openai"):
            raise ValueError("Unknown API provider")
        if provider == "openai":
            from personasciencebench.openai_transport import ResponsesTransport
            self.openai = ResponsesTransport(timeout)
        self.max_tokens, self.temperature, self.timeout = max_tokens, temperature, timeout
        self.reasoning_effort = reasoning_effort
        if unsupported_parameters not in ("reject", "omit_and_record"):
            raise ValueError("Unknown parameter policy")
        self.parameter_policy = unsupported_parameters
        self.supported_parameters = supported_parameters
        self.parameter_adaptations: list[dict] = []
        self.format_adaptations: list[dict] = []
        self.record = record

    def _transport(self, key):
        return "https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {key}"}

    def _provider_payload(self, payload):
        payload["provider"] = {"require_parameters": True, "allow_fallbacks": False}
        if self.reasoning_effort is not None:
            payload["reasoning"] = {"effort": self.reasoning_effort}
        return payload

    def complete(self, messages, *, json_mode=False, settings=None):
        raw = self.completion(messages, json_mode=json_mode, settings=settings)["choices"][0]["message"]["content"]
        return self.normalize_text(raw, json_mode=json_mode)

    def complete_decision(self, messages, schema):
        """One typed researcher decision, without a generated multi-turn transcript."""
        name = "researcher_decision"
        response = self.completion(messages, tools=[{"type":"function", "function":{
            "name":name, "description":"Return the single researcher decision for the current turn.",
            "parameters":schema}}], tool_choice={"type":"function", "function":{"name":name}})
        calls = response["choices"][0]["message"].get("tool_calls", [])
        if len(calls) != 1 or calls[0]["function"]["name"] != name:
            raise ValueError("Expected exactly one researcher_decision tool call")
        return calls[0]["function"]["arguments"]

    def normalize_text(self, raw, *, json_mode=False):
        normalized = canonical_json_object(raw) if json_mode else raw
        if normalized != raw:
            self.format_adaptations.append({"normalization": "whole_json_fence_removed",
                                            "json_value_unchanged": True})
        return normalized

    def completion(self, messages, tools=None, *, json_mode=False, settings=None, tool_choice=None):
        import httpx

        key = os.environ.get(self.key_variable)
        if not key:
            raise ValueError(f"{self.key_variable} is not configured")
        allowed = {"temperature", "max_tokens", "top_p", "seed", "logprobs", "top_logprobs",
                   "frequency_penalty", "presence_penalty"}
        settings = dict(settings or {})
        if set(settings) - allowed:
            raise ValueError("Unsupported generation settings: " + ", ".join(sorted(set(settings) - allowed)))
        if self.temperature is not None and "temperature" not in settings:
            settings["temperature"] = self.temperature
        requested_settings = dict(settings)
        omitted = {}
        if self.parameter_policy == "omit_and_record" and self.supported_parameters is not None:
            omitted = {k: v for k, v in settings.items() if k not in self.supported_parameters}
            settings = {k: v for k, v in settings.items() if k in self.supported_parameters}
            if omitted:
                self.parameter_adaptations.append({"omitted_native_settings": omitted,
                                                   "replacement": "provider_defaults"})
        payload = self._provider_payload({"model": self.model, "messages": messages,
                                          "max_tokens": self.max_tokens, **settings})
        if tools:
            payload["tools"] = tools
            if tool_choice is not None:
                payload["tool_choice"] = tool_choice
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        if self.provider == "openai":
            # main's direct OpenAI Responses transport (openai_transport.ResponsesTransport).
            data = self.openai.complete(payload)
        else:
            try:
                url, headers = self._transport(key)
                response = httpx.post(url, headers=headers,
                                      json=payload, timeout=self.timeout)
            except httpx.HTTPError as exc:
                raise RuntimeError(f"{self.role}: {self.provider_name} transport failed ({type(exc).__name__})") from None
            if response.status_code != 200:
                raise RuntimeError(f"{self.role}: {self.provider_name} HTTP {response.status_code}")
            data = response.json()
        if self.record:
            self.record({"role": self.role, "model": self.model,
                         "resolved_model": data.get("model"), "provider": data.get("provider"),
                         "transport_provider": self.provider_name,
                         "request": payload, "response": data,
                         "requested_native_settings": requested_settings,
                         "omitted_native_settings": omitted,
                         "usage": data.get("usage", {}), "automatic_retries": 0})
        if data.get("error"):
            raise RuntimeError(f"{self.role}: {self.provider_name} returned an error response")
        try:
            choice = data["choices"][0]
            content = choice["message"].get("content")
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"{self.role}: response has no completion") from None
        invalid_finishes = {"length", "error", "content_filter"}
        if not tools:
            invalid_finishes.add("tool_calls")
        if choice.get("finish_reason") in invalid_finishes:
            raise RuntimeError(f"{self.role}: incomplete completion ({choice['finish_reason']})")
        if not isinstance(content, str) and not (tools and choice["message"].get("tool_calls")):
            raise RuntimeError(f"{self.role}: completion must contain text")
        return data


def azure_base_url() -> str:
    """Require the explicit v1 inference endpoint, never the Foundry project URL."""
    from urllib.parse import urlsplit
    raw = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
    url = urlsplit(raw)
    if (url.scheme != "https" or not url.hostname or url.username or url.password
            or url.query or url.fragment or url.path != "/openai/v1"):
        raise ValueError("AZURE_OPENAI_ENDPOINT must be https://<resource>.services.ai.azure.com/openai/v1/ "
                         "(or the resource's openai.azure.com host), not a project endpoint")
    if not url.hostname.endswith((".services.ai.azure.com", ".openai.azure.com")):
        raise ValueError("AZURE_OPENAI_ENDPOINT must use an Azure OpenAI resource host")
    return raw


class AzureOpenAIClient(OpenRouterClient):
    """Azure v1 chat transport with the same strict completion and audit contract."""

    provider_name = "Azure OpenAI"
    key_variable = "AZURE_OPENAI_API_KEY"

    def _transport(self, key):
        return azure_base_url() + "/chat/completions", {"api-key": key}

    def _provider_payload(self, payload):
        payload["max_completion_tokens"] = payload.pop("max_tokens")
        if self.reasoning_effort is not None:
            payload["reasoning_effort"] = self.reasoning_effort
        return payload


def model_client(*, provider="openrouter", **kwargs):
    """Explicit per-role provider selection; existing configs keep OpenRouter."""
    if provider == "openai":
        # main's direct OpenAI Responses transport, selected inside OpenRouterClient.
        return OpenRouterClient(provider="openai", **kwargs)
    clients = {"openrouter": OpenRouterClient, "azure": AzureOpenAIClient}
    if provider not in clients:
        raise ValueError(f"Unknown model provider: {provider}")
    return clients[provider](**kwargs)


def load_env(path: Path):
    """Read a local ignored dotenv file without shell evaluation or printing values."""
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key not in {"OPENROUTER_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT",
                       "AZURE_OPENAI_DEPLOYMENT", "AZURE_FOUNDRY_PROJECT_ENDPOINT"}:
            continue
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def preflight(models: dict, *, timeout=45) -> dict:
    """Check authenticated catalogs without inference; Azure deployments need a probe.

    Azure /models is not an inventory of deployed names. Record deployment access
    as unverified, rather than rejecting custom names or claiming catalog access
    proves that a particular model is deployed.
    """
    selected, router_models = {}, {}
    for role, spec in models.items():
        provider = spec.get("provider", "openrouter")
        if provider == "openrouter":
            router_models[role] = spec
        elif provider not in ("azure", "openai"):
            raise ValueError(f"Unknown model provider: {provider}")
    openai_models = {role: spec for role, spec in models.items() if spec.get("provider") == "openai"}
    if openai_models:
        from personasciencebench.openai_transport import preflight as openai_preflight
        selected.update(openai_preflight(openai_models, timeout))
    azure_models = {role: spec for role, spec in models.items() if spec.get("provider") == "azure"}
    if azure_models:
        import httpx
        key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured; no inference requested")
        endpoint = azure_base_url()
        try:
            response = httpx.get(endpoint + "/models", headers={"api-key": key}, timeout=timeout)
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Azure preflight transport failed ({type(exc).__name__})") from None
        if response.status_code != 200:
            raise RuntimeError(f"Azure preflight /models HTTP {response.status_code}")
        for role, spec in azure_models.items():
            if not isinstance(spec.get("model"), str) or not spec["model"].strip():
                raise ValueError(f"Select an exact Azure deployment for {role}")
            selected[role] = {"id": spec["model"], "provider": "azure", "endpoint": endpoint,
                              "pricing": None, "supported_parameters": None,
                              "reasoning_effort": spec.get("reasoning_effort"),
                              "deployment_verified": False, "authenticated_catalog_access": True}
    if router_models:
        selected.update(_openrouter_preflight(router_models, timeout=timeout))
    return selected


def _openrouter_preflight(models: dict, *, timeout=45) -> dict:
    """Check authenticated access and exact model names without requesting inference."""
    if all(s.get("provider") == "openai" for s in models.values()):
        from personasciencebench.openai_transport import preflight as openai_preflight
        return openai_preflight(models, timeout)
    import httpx
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is not configured; no inference requested")
    with httpx.Client(base_url="https://openrouter.ai/api/v1", timeout=timeout,
                      headers={"Authorization": f"Bearer {key}"}) as client:
        for route in ("/key", "/models"):
            response = client.get(route)
            if response.status_code != 200:
                raise RuntimeError(f"OpenRouter preflight {route} HTTP {response.status_code}")
            if route == "/models":
                catalog = {entry["id"]: entry for entry in response.json()["data"]}
    selected = {}
    for role, spec in models.items():
        model = spec.get("model")
        if model not in catalog:
            raise ValueError(f"Exact {role} model is unavailable: {model}")
        entry = catalog[model]
        parameters = entry.get("supported_parameters", [])
        if role == "actor" and "tools" not in parameters:
            raise ValueError("Actor model does not advertise tool calling")
        if spec.get("reasoning_effort") is not None and "reasoning" not in parameters:
            raise ValueError(f"{role} model does not advertise reasoning controls")
        selected[role] = {"id": model, "pricing": entry.get("pricing"),
                          "supported_parameters": parameters,
                          "reasoning_effort": spec.get("reasoning_effort")}
    return selected


def strict_json(text: str) -> dict:
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def canonical_json_object(text: str) -> str:
    """Remove only a complete JSON code fence; never repair or infer contents."""
    match = re.fullmatch(r"\s*```(?:json)?\s*\n(.*?)\n```\s*", text, re.DOTALL | re.IGNORECASE)
    if match is None:
        return text
    def reject_constant(value):
        raise ValueError("Non-finite values are not JSON constants")
    try:
        value = json.loads(match.group(1), parse_constant=reject_constant)
    except (ValueError, TypeError):
        return text
    return json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else text


class ReplayJudge:
    """Reuse exact completed requests when repairing a transport/parser issue.

    No response can be reused for changed prompts, native settings, JSON mode or
    model. New calls occur only after the ordered cached prefix is exhausted.
    The caller separately verifies that the recorded judge configuration matches.
    """

    def __init__(self, client: OpenRouterClient, source: Path, record: Callable[[dict], None]):
        self.client = client
        self.cached = [json.loads(line) for line in source.read_text().splitlines()]
        self.source, self.index, self.record = source, 0, record
        self.parameter_adaptations = client.parameter_adaptations
        self.format_adaptations = client.format_adaptations

    def complete(self, messages, *, json_mode=False, settings=None):
        if self.index >= len(self.cached):
            return self.client.complete(messages, json_mode=json_mode, settings=settings)
        entry = self.cached[self.index]
        request = entry["request"]
        same = (request["messages"] == messages and request["model"] == self.client.model
                and entry.get("requested_native_settings", {}) == (settings or {})
                and bool(request.get("response_format")) == json_mode
                and request.get("reasoning_effort", request.get("reasoning", {}).get("effort"))
                == self.client.reasoning_effort
                and entry.get("transport_provider", "OpenRouter") == self.client.provider_name)
        if not same:
            raise ValueError("Cached judge request differs; refusing to substitute a judgement")
        choice = entry["response"]["choices"][0]
        if choice.get("finish_reason") != "stop" or not isinstance(choice["message"].get("content"), str):
            raise ValueError("Only completed text judgements can be replayed")
        self.record({"source": str(self.source.resolve()), "record_index": self.index,
                     "request_identical": True, "additional_model_call": False})
        self.index += 1
        if entry.get("omitted_native_settings"):
            self.parameter_adaptations.append({"omitted_native_settings": entry["omitted_native_settings"],
                                               "replacement": "provider_defaults"})
        return self.client.normalize_text(choice["message"]["content"], json_mode=json_mode)
