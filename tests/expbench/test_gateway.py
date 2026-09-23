import json
from pathlib import Path

import httpx
import pytest

import importlib.util
try:
    sdk_available = importlib.util.find_spec("openhands.sdk") is not None
except ModuleNotFoundError:
    sdk_available = False
if not sdk_available:
    pytest.skip("EXP-Bench integration tests require the actor extra", allow_module_level=True)
from expbench.paths import ROOT as EXP_ROOT
if not (EXP_ROOT / "data/realistic_pilot/tasks.jsonl").exists():
    pytest.skip("Prepare the pinned EXP-Bench task cards before running its source tests", allow_module_level=True)

from expbench.budget import Budget, Ledger
from expbench.cli import main, read_key_file
from expbench.gateway import AuthenticationRejected, Gateway, ModelError, OpenRouterTransport
from expbench.mock import MockTransport
from expbench.runner import run_episode
from expbench.schema import Config, load_tasks

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def config():
    return Config.load(ROOT / "configs/expbench/pilot.toml")


def transport_with_handler(handler):
    transport = OpenRouterTransport("test-key-not-a-secret", 10)
    transport.client.close()
    transport.client = httpx.Client(
        base_url="https://openrouter.ai/api/v1",
        headers={"Authorization": "Bearer test-key-not-a-secret"},
        transport=httpx.MockTransport(handler),
    )
    return transport


def models(config):
    return {r: getattr(config.models, r) for r in ("actor", "researcher", "judge")}


def catalog(config):
    return {"data": [
        {"id": spec.model, "pricing": {"prompt": str(spec.input_usd_per_million / 1e6),
                                      "completion": str(spec.output_usd_per_million / 1e6)},
         "supported_parameters": ["tools", "structured_outputs"]}
        for spec in models(config).values()
    ]}


def test_auth_failure_stops_before_catalog_or_inference(config):
    paths = []
    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(401, json={"error": {"message": "Invalid credentials"}})
    transport = transport_with_handler(handler)
    try:
        with pytest.raises(AuthenticationRejected, match="HTTP 401"):
            transport.preflight(models(config))
        assert paths == ["/api/v1/key"]
    finally:
        transport.close()


def test_live_http_contract_with_mock_server(tmp_path, config):
    requests = []
    mock = MockTransport()
    def handler(request):
        requests.append(request)
        assert request.headers["authorization"] == "Bearer test-key-not-a-secret"
        if request.url.path.endswith("/key"):
            return httpx.Response(200, json={"data": {}})
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=catalog(config))
        assert request.url.path == "/api/v1/chat/completions"
        payload = json.loads(request.content)
        assert payload["provider"]["allow_fallbacks"] is False
        assert payload["provider"]["require_parameters"] is True
        assert payload["max_tokens"] == config.models.judge.max_output_tokens
        assert payload["reasoning"] == {"effort": "medium"}
        return httpx.Response(200, json=mock.complete("judge", payload))
    transport = transport_with_handler(handler)
    try:
        assert set(transport.preflight(models(config))) == {"actor", "researcher", "judge"}
        gateway = Gateway(transport, models(config), Ledger(Budget(20), Budget(2)), tmp_path / "api.jsonl")
        gateway.complete("judge", [{"role": "user", "content": "Test"}])
        assert len(requests) == 3
        assert "test-key-not-a-secret" not in (tmp_path / "api.jsonl").read_text()
        assert gateway.ledger.run.charged > 0
    finally:
        transport.close()


def test_preflight_refuses_missing_model_and_price_increase(config):
    for mode in ("missing", "expensive"):
        data = catalog(config)
        if mode == "missing":
            data["data"] = []
        else:
            data["data"][0]["pricing"]["prompt"] = "1.0"
            data["data"][1]["pricing"]["prompt"] = "1.0"
        def handler(request):
            return httpx.Response(200, json={"data": {}} if request.url.path.endswith("/key") else data)
        transport = transport_with_handler(handler)
        try:
            with pytest.raises(ModelError):
                transport.preflight(models(config))
        finally:
            transport.close()


def test_auth_rejection_releases_reservation(tmp_path, config):
    transport = transport_with_handler(lambda request: httpx.Response(401, json={}))
    try:
        gateway = Gateway(transport, models(config), Ledger(Budget(20), Budget(2)), tmp_path / "api.jsonl")
        with pytest.raises(AuthenticationRejected):
            gateway.complete("judge", [])
        assert gateway.ledger.run.charged == 0
        assert gateway.ledger.records[0]["billing_status"] == "auth_rejected"
    finally:
        transport.close()


def test_budget_reason_survives_sdk_wrapping(tmp_path, config):
    class ChargedMock(MockTransport):
        mock = False
    config.limits.episode_usd = 0.00001
    task = load_tasks(ROOT / "data/design_pilot/tasks.jsonl")[0]
    transport = ChargedMock()
    result = run_episode(task, config, transport, Budget(20), tmp_path / "run")
    assert result["status"] == "budget_exceeded"
    assert not transport.requests
    assert "budget" in result["error"]


def test_truncated_output_is_not_graded(tmp_path, config):
    class Truncated(MockTransport):
        def complete(self, role, payload):
            response = super().complete(role, payload)
            response["choices"][0]["finish_reason"] = "length"
            return response
    transport = Truncated()
    task = load_tasks(ROOT / "data/design_pilot/tasks.jsonl")[0]
    result = run_episode(task, config, transport, Budget(20), tmp_path / "run")
    assert result["status"] == "actor_error"
    assert "Incomplete" in result["error"]
    assert transport.counts["judge"] == 0


def test_key_file_is_literal_and_never_saved_in_mock_manifest(tmp_path, monkeypatch):
    key_file = tmp_path / ".env"
    key_file.write_text("OPENROUTER_API_KEY='test-fixture-key'\n")
    assert read_key_file(key_file) == "test-fixture-key"
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("OPENROUTER_API_KEY", "do-not-log-test-key")
    out = tmp_path / "run"
    assert main(["run", "--mode", "mock", "--task", "iclr2024/18865/4", "--output", str(out)]) == 0
    for path in out.rglob("*.json*"):
        assert "do-not-log-test-key" not in path.read_text()
    # No shell expansion; this remains a literal string.
    key_file.write_text("OPENROUTER_API_KEY=$(touch /tmp/should-not-exist)\n")
    with pytest.raises(ValueError):
        read_key_file(key_file)


def test_default_configuration_has_no_dollar_caps(config):
    assert config.limits.actor_steps == 20
    assert config.limits.run_usd is None
    assert config.limits.episode_usd is None


def test_uncapped_gateway_logs_cost_without_price_filter_or_stop(tmp_path, config):
    class Expensive(MockTransport):
        mock = False
        def complete(self, role, payload):
            assert "max_price" not in payload["provider"]
            response = super().complete(role, payload)
            response["usage"]["cost"] = 100.0  # exceeds even the conservative reservation
            return response
    ledger = Ledger(Budget(None), Budget(None))
    gateway = Gateway(Expensive(), models(config), ledger, tmp_path / "api.jsonl")
    gateway.complete("judge", [{"role": "user", "content": "Test"}])
    assert ledger.run.charged == 100.0
    assert not gateway.failed


def test_uncapped_preflight_updates_estimates_instead_of_rejecting_price(config):
    data = catalog(config)
    for item in data["data"]:
        item["pricing"]["prompt"] = "0.00002"
    def handler(request):
        return httpx.Response(200, json={"data": {}} if request.url.path.endswith("/key") else data)
    transport = transport_with_handler(handler)
    try:
        transport.preflight(models(config), enforce_price_caps=False)
        assert config.models.actor.input_usd_per_million == 20.0
        assert config.models.judge.input_usd_per_million == 20.0
    finally:
        transport.close()
