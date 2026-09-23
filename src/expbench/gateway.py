"""One inference boundary for all roles; OpenHands owns the actor loop."""

import copy
import json
import math
import time
from pathlib import Path

import httpx

from expbench.artifacts import append_jsonl
from expbench.budget import BudgetExceeded, Ledger
from expbench.schema import ModelSettings


class ModelError(RuntimeError):
    """A safe-to-log error; never includes HTTP headers or credentials."""


class AuthenticationRejected(ModelError):
    """An HTTP authentication rejection, before model execution."""


class OpenRouterTransport:
    mock = False

    def __init__(self, key: str, timeout: int):
        if not key.strip():
            raise ValueError("Set OPENROUTER_API_KEY before a live run")
        self.client = httpx.Client(
            base_url="https://openrouter.ai/api/v1",
            headers={"Authorization": f"Bearer {key}"}, timeout=timeout,
            follow_redirects=False,
        )

    def preflight(self, models: dict[str, ModelSettings], *, enforce_price_caps=True) -> dict:
        # /models is public and does not establish that the key is valid.
        try:
            auth = self.client.get("/key")
            auth.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthenticationRejected(
                f"OpenRouter key check returned HTTP {exc.response.status_code}; no inference requested"
            ) from None
        except httpx.HTTPError:
            raise ModelError("OpenRouter key check failed; no inference requested") from None
        try:
            response = self.client.get("/models")
            response.raise_for_status()
            catalog = {m["id"]: m for m in response.json()["data"]}
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise ModelError("Could not validate the OpenRouter model catalog") from None
        selected = {}
        for role, spec in models.items():
            if spec.model not in catalog:
                raise ModelError(f"Configured {role} model is unavailable: {spec.model}")
            model = catalog[spec.model]
            supported = model.get("supported_parameters", [])
            required = {"tools"} if role == "actor" else {"structured_outputs"}
            if not required.issubset(supported):
                raise ModelError(f"{role} model does not advertise {sorted(required)}")
            for field, cap in (("prompt", spec.input_usd_per_million),
                               ("completion", spec.output_usd_per_million)):
                try:
                    price = float(model["pricing"][field]) * 1_000_000
                    if not math.isfinite(price) or price <= 0:
                        raise ValueError()
                    if enforce_price_caps and price > cap + 1e-9:
                        raise ValueError()
                    if not enforce_price_caps:
                        attr = "input_usd_per_million" if field == "prompt" else "output_usd_per_million"
                        setattr(spec, attr, price)
                except (KeyError, TypeError, ValueError):
                    raise ModelError(f"Review configured {role} {field} price cap before running") from None
            selected[role] = model
        return selected

    def complete(self, role: str, payload: dict) -> dict:
        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise AuthenticationRejected(
                    f"OpenRouter returned HTTP {exc.response.status_code} for {role}; no automatic retry"
                ) from None
            raise ModelError(f"OpenRouter returned HTTP {exc.response.status_code} for {role}; no automatic retry") from None
        except (httpx.HTTPError, ValueError):
            raise ModelError(f"OpenRouter request failed for {role}; billing may be unknown; no automatic retry") from None
        if not isinstance(result, dict) or "error" in result:
            raise ModelError(f"OpenRouter returned an error for {role}")
        return result

    def close(self):
        self.client.close()


class Gateway:
    def __init__(self, transport, models: dict[str, ModelSettings], ledger: Ledger,
                 log_path: Path):
        self.transport = transport
        self.models = models
        self.ledger = ledger
        self.log_path = log_path
        self.failed = False

    def complete(self, role: str, messages: list[dict], *, tools=None, schema=None,
                 json_object=False):
        if schema is not None and json_object:
            raise ValueError("Choose JSON schema or JSON object mode, not both")
        if self.failed:
            raise ModelError("Inference stopped after an earlier request failure")
        spec = self.models[role]
        bounded = self.ledger.run.limit is not None or self.ledger.episode.limit is not None
        payload = {
            "model": spec.model, "messages": copy.deepcopy(messages),
            "max_tokens": spec.max_output_tokens, "stream": False,
            "provider": {
                "require_parameters": True, "allow_fallbacks": False,
            },
        }
        if bounded:
            payload["provider"]["max_price"] = {"prompt": spec.input_usd_per_million,
                                                   "completion": spec.output_usd_per_million}
        if spec.reasoning_effort:
            payload["reasoning"] = {"effort": spec.reasoning_effort}
        if tools:
            payload["tools"] = tools
        if schema:
            payload["response_format"] = {
                "type": "json_schema", "json_schema": {
                    "name": role + "_reply", "strict": True, "schema": schema,
                },
            }
        elif json_object:
            payload["response_format"] = {"type": "json_object"}

        # Conservative guard: UTF-8 byte count plus framing allowance, rather
        # than dividing characters by four. This is not a provider billing quote.
        input_bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 2048
        reserved = (input_bound * spec.input_usd_per_million
                    + spec.max_output_tokens * spec.output_usd_per_million) / 1e6
        if self.transport.mock:
            reserved = 0.0
        self.ledger.reserve(reserved)
        call_id = len(self.ledger.records) + 1
        start = time.monotonic()
        base = {"call_id": call_id, "role": role, "requested_model": spec.model,
                "mock": self.transport.mock}
        append_jsonl(self.log_path, {**base, "phase": "request", "payload": payload,
                                     "reserved_usd": reserved})
        settled = False
        try:
            result = self.transport.complete(role, payload)
            usage = result.get("usage")
            if not isinstance(usage, dict):
                raise ModelError("Missing usage accounting; stopped to protect the budget")
            for field in ("prompt_tokens", "completion_tokens"):
                if type(usage.get(field)) is not int or usage[field] < 0:
                    raise ModelError("Invalid token accounting in model response")
            # Completion tokens already include reasoning tokens: do not add twice.
            estimate = (usage["prompt_tokens"] * spec.input_usd_per_million
                        + usage["completion_tokens"] * spec.output_usd_per_million) / 1e6
            reported_cost = usage.get("cost")
            if reported_cost is not None and (
                not isinstance(reported_cost, (int, float))
                or not math.isfinite(reported_cost) or reported_cost < 0
            ):
                raise ModelError("Invalid cost accounting in model response")
            charge = max(estimate, reported_cost or 0.0)
            if self.transport.mock:
                charge = 0.0
            record = {**base, "usage": usage, "estimated_uncached_usd": estimate,
                      "returned_model": result.get("model"),
                      "provider": result.get("provider"), "response_id": result.get("id"),
                      "billing_status": "mock" if self.transport.mock else "reported_or_estimated",
                      "elapsed_seconds": round(time.monotonic() - start, 3)}
            self.ledger.settle(reserved, charge, record)
            settled = True
            append_jsonl(self.log_path, {**base, "phase": "response", "response": result})
            if bounded and charge > reserved + 1e-9:
                raise BudgetExceeded("Provider usage exceeded the reservation; further calls stopped")
            choices = result.get("choices")
            if not choices or not isinstance(choices[0].get("message"), dict):
                raise ModelError("Missing completion message")
            if choices[0].get("finish_reason") in ("length", "content_filter"):
                raise ModelError("Incomplete or filtered response; no automatic retry")
            return result
        except Exception as exc:
            self.failed = True
            if not settled:
                rejected = isinstance(exc, AuthenticationRejected)
                self.ledger.settle(reserved, 0.0 if rejected else reserved, {
                    **base, "billing_status": "auth_rejected" if rejected else "unknown_reserved",
                    "error_type": type(exc).__name__,
                })
            append_jsonl(self.log_path, {**base, "phase": "error", "error_type": type(exc).__name__})
            raise


def response_message(response: dict) -> dict:
    return response["choices"][0]["message"]


def parse_structured(response: dict, schema):
    message = response_message(response)
    if message.get("tool_calls") or not isinstance(message.get("content"), str):
        raise ModelError("Expected a structured text response")
    try:
        return schema.model_validate_json(message["content"])
    except ValueError:
        raise ModelError(f"Invalid {schema.__name__} JSON; response retained in private API log") from None
