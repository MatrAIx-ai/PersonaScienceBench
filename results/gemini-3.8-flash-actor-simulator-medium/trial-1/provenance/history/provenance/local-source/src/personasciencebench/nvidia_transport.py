"""NVIDIA's OpenAI-compatible Chat API; credentials never enter run records."""

from copy import deepcopy
import math
import os
from pathlib import Path
import json

import httpx

BASE_URL = "https://inference-api.nvidia.com/v1"
GEMINI_MODEL = "gcp/google/gemini-3.8-flash"


def chat_payload(payload):
    """Translate the harness envelope, preserving native generation settings."""
    request = deepcopy(payload)
    request.pop("provider", None)  # OpenRouter routing directives are not Chat parameters.
    reasoning = request.pop("reasoning", None)
    if reasoning is not None:
        if set(reasoning) != {"effort"}:
            raise ValueError("NVIDIA transport requires an explicit reasoning effort")
        request["reasoning_effort"] = reasoning["effort"]
    return request


def api_key():
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise ValueError("NVIDIA_API_KEY is not configured")
    return key


def preflight(models, timeout=45):
    """Read authenticated model/deployment metadata; never invoke a model."""
    selected = {}
    try:
        with httpx.Client(base_url=BASE_URL, timeout=timeout,
                          headers={"Authorization": "Bearer " + api_key()}) as client:
            response = client.get("/models")
            response.raise_for_status()
            available = {entry["id"] for entry in response.json()["data"]}
            metadata = {}
            for role, spec in models.items():
                model = spec["model"]
                if model not in available:
                    raise ValueError(f"Exact {role} NVIDIA model unavailable: {model}")
                if model not in metadata:
                    response = client.get("/model/info", params={"model": model})
                    response.raise_for_status()
                    matches = [m for m in response.json()["data"] if m.get("model_name") == model]
                    if len(matches) != 1:
                        raise ValueError(f"Ambiguous NVIDIA deployment metadata: {model}")
                    metadata[model] = matches[0]
                entry = metadata[model]
                info = entry["model_info"]
                parameters = ["max_tokens", "temperature", "top_p"]
                for field, parameter in (("supports_function_calling", "tools"),
                                         ("supports_response_schema", "structured_outputs"),
                                         ("supports_reasoning", "reasoning")):
                    if info.get(field):
                        parameters.append(parameter)
                if role in ("actor", "researcher") and "tools" not in parameters:
                    raise ValueError(f"{role} model does not advertise tool calling")
                if spec.get("reasoning_effort") and "reasoning" not in parameters:
                    raise ValueError(f"{role} model does not advertise reasoning controls")
                prices = {}
                for field, name in (("input_cost_per_token", "prompt"),
                                    ("output_cost_per_token", "completion")):
                    value = info.get(field)
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                        raise ValueError(f"Missing/invalid NVIDIA accounting metadata: {field}")
                    prices[name] = value
                # Never retain litellm_params wholesale: deployments may contain secrets.
                selected[role] = {
                    "id": model, "provider": "nvidia", "base_url": BASE_URL,
                    "deployment_model": entry.get("litellm_params", {}).get("model"),
                    "accounting_base_model": info.get("base_model"),
                    "pricing": prices, "pricing_source": BASE_URL + "/model/info",
                    "supported_parameters": parameters,
                    "reasoning_effort": spec.get("reasoning_effort"),
                }
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"NVIDIA preflight HTTP {exc.response.status_code}") from None
    except httpx.HTTPError as exc:
        raise RuntimeError(f"NVIDIA preflight failed ({type(exc).__name__})") from None
    return selected


class ChatTransport:
    def __init__(self, timeout=600):
        self.timeout = timeout

    def complete(self, payload):
        from openai import OpenAI, APIError

        fatal = os.environ.get("PSB_FATAL_API_FILE")
        if fatal and Path(fatal).exists():
            raise RuntimeError("Run stopped after a fatal API error; see fatal_api.json")
        try:
            with OpenAI(base_url=BASE_URL, api_key=api_key(), timeout=self.timeout,
                        max_retries=0) as client:
                result = client.chat.completions.create(**chat_payload(payload))
                data = result.model_dump(exclude_none=True)
        except APIError as exc:
            status = getattr(exc, "status_code", None)
            if status in (401, 403) and fatal:
                Path(fatal).write_text(json.dumps({"provider": "nvidia", "status": status}) + "\n")
            raise RuntimeError(f"NVIDIA Chat request failed ({type(exc).__name__}, HTTP {status}); no automatic retry") from None
        data.setdefault("provider", "nvidia")
        return data
