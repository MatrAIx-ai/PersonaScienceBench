"""NVIDIA's OpenAI-compatible Chat API; credentials never enter run records."""

from copy import deepcopy
import math
import os
from pathlib import Path
import json
import hashlib

import httpx

BASE_URL = "https://inference-api.nvidia.com/v1"
GEMINI_MODEL = "gcp/google/gemini-3.8-flash"
MINIMAX_MODEL = "nvidia/minimaxai/minimax-m3"
MINIMAX_DEPLOYMENT = "dynamo/minimaxai/minimax-m3-sglang"
MINIMAX_DOC = "https://docs.api.nvidia.com/nim/reference/minimaxai-minimax-m3-infer"


def output_limit_override(model, role, configured):
    """Load an explicit, run-bound repair policy once when a client is created.

    Existing episode processes keep their loaded settings. Judge settings and
    the original run configs are never changed by this collection repair policy.
    """
    fatal = os.environ.get('PSB_FATAL_API_FILE')
    if model != MINIMAX_MODEL or role not in ('actor', 'researcher') or not fatal:
        return configured, None
    run = Path(fatal).resolve().parent
    path = run / 'generation_limits.json'
    if not path.exists():
        return configured, None
    raw = path.read_bytes()
    policy = json.loads(raw)
    if (policy.get('model') != model or policy.get('authorization') != 'user_requested_higher_token_limits'
            or policy.get('run_manifest_sha256') != hashlib.sha256((run / 'manifest.json').read_bytes()).hexdigest()):
        raise ValueError('Output-limit repair policy does not match this run')
    cap = policy['max_output_tokens'][role]
    if type(cap) is not int or not configured <= cap <= 131072:
        raise ValueError('Invalid output-limit repair override')
    return cap, {'policy': str(path), 'policy_sha256': hashlib.sha256(raw).hexdigest(),
                 'configured_max_tokens': configured, 'effective_max_tokens': cap,
                 'policy_id': policy['id']}


def chat_payload(payload):
    """Translate the harness envelope, preserving native generation settings."""
    request = deepcopy(payload)
    request.pop("provider", None)  # OpenRouter routing directives are not Chat parameters.
    reasoning = request.pop("reasoning", None)
    if reasoning is not None:
        if set(reasoning) != {"effort"}:
            raise ValueError("NVIDIA transport requires an explicit reasoning effort")
        request["reasoning_effort"] = reasoning["effort"]
    if request.get("model") == MINIMAX_MODEL:
        effort = request.pop("reasoning_effort", None)
        if effort not in (None, "adaptive"):
            raise ValueError("MiniMax M3 requires native adaptive thinking, not an effort level")
        native = request.get("chat_template_kwargs")
        if native is not None and native != {"thinking_mode": "adaptive"}:
            raise ValueError("MiniMax M3 run requires adaptive thinking")
        request["chat_template_kwargs"] = {"thinking_mode": "adaptive"}
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
                capability_source = "catalog"
                if model == MINIMAX_MODEL:
                    if entry.get("litellm_params", {}).get("model") != MINIMAX_DEPLOYMENT:
                        raise ValueError("MiniMax deployment changed; reverify native controls")
                    if spec.get("reasoning_effort") != "adaptive":
                        raise ValueError("MiniMax M3 requires native adaptive thinking")
                    # This deployment leaves capabilities null. Native documentation
                    # and saved live tool/JSON probes establish support; retain the
                    # catalog values separately rather than inventing advertised flags.
                    capability_source = MINIMAX_DOC
                parameters = ["max_tokens", "temperature", "top_p"]
                for field, parameter in (("supports_function_calling", "tools"),
                                         ("supports_response_schema", "structured_outputs"),
                                         ("supports_reasoning", "reasoning")):
                    if info.get(field) or (model == MINIMAX_MODEL and info.get(field) is None):
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
                    "capability_source": capability_source,
                    "catalog_capabilities": {k: info.get(k) for k in (
                        "supports_function_calling", "supports_response_schema", "supports_reasoning")},
                }
                if model == MINIMAX_MODEL:
                    selected[role]["native_thinking_mode"] = "adaptive"
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"NVIDIA preflight HTTP {exc.response.status_code}") from None
    except httpx.HTTPError as exc:
        raise RuntimeError(f"NVIDIA preflight failed ({type(exc).__name__})") from None
    return selected


class ChatTransport:
    def __init__(self, timeout=600):
        self.timeout = timeout

    def complete_recorded(self, payload, record, *, role):
        """Opt-in repair of unusable early actor truncations; log every response.

        Replay the identical request at most twice. Never retry content filters,
        refusals, transport errors, substantive answers, or exhausted token caps.
        This is an explicitly recorded repair policy, disabled for normal runs.
        """
        retries = int(os.environ.get('PSB_NVIDIA_EMPTY_LENGTH_RETRIES', '0'))
        if not 0 <= retries <= 2:
            raise ValueError('PSB_NVIDIA_EMPTY_LENGTH_RETRIES must be between 0 and 2')
        for attempt in range(retries + 1):
            data = self.complete(payload)
            choices = data.get('choices') or []
            choice = choices[0] if choices else {}
            message = choice.get('message') or {}
            used = (data.get('usage') or {}).get('completion_tokens')
            cap = payload.get('max_tokens')
            eligible = (role == 'actor' and choice.get('finish_reason') == 'length'
                        and not message.get('content') and not message.get('tool_calls')
                        and not message.get('refusal')
                        and type(used) is int and type(cap) is int and 0 < used < cap)
            retry = eligible and attempt < retries
            record(data, {'request_attempt': attempt + 1,
                          'empty_length_retry_limit': retries,
                          'retry_scheduled': retry,
                          'retry_reason': 'empty_length_below_requested_limit' if retry else None})
            if not retry:
                return data

    def complete(self, payload):
        from openai import OpenAI, APIError

        fatal = os.environ.get("PSB_FATAL_API_FILE")
        if fatal and Path(fatal).exists():
            raise RuntimeError("Run stopped after a fatal API error; see fatal_api.json")
        try:
            with OpenAI(base_url=BASE_URL, api_key=api_key(), timeout=self.timeout,
                        max_retries=0) as client:
                request = chat_payload(payload)
                native = request.pop("chat_template_kwargs", None)
                if native is not None:
                    request["extra_body"] = {"chat_template_kwargs": native}
                result = client.chat.completions.create(**request)
                data = result.model_dump(exclude_none=True)
        except APIError as exc:
            status = getattr(exc, "status_code", None)
            if status in (401, 403) and fatal:
                Path(fatal).write_text(json.dumps({"provider": "nvidia", "status": status}) + "\n")
            raise RuntimeError(f"NVIDIA Chat request failed ({type(exc).__name__}, HTTP {status}); no automatic retry") from None
        data.setdefault("provider", "nvidia")
        return data
