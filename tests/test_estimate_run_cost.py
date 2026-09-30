"""Offline cost/parallelism estimator over recorded usage; no model calls."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import estimate_run_cost as estimate  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/usage_traces"


def test_trace_parsing_separates_roles_and_measures_duration():
    [sample] = estimate.load_samples([FIXTURE], "discoverybench")
    assert sample["roles"]["actor"] == {"calls": 1, "prompt": 9000, "completion": 900, "cached": 4500, "cost": 0.002}
    assert sample["roles"]["researcher"]["calls"] == 1
    assert sample["duration_s"] == 120


def test_plan_scales_measured_usage_and_prices_cache():
    samples = estimate.load_samples([FIXTURE], "discoverybench")
    summary = estimate.summarize(samples, episodes=10, model="openai/gpt-6-luna",
                                 max_tokens={"actor": 1000, "researcher": 500})
    assert summary["cache_share_of_prompt"] == pytest.approx(0.5)
    assert summary["per_episode"]["mean"]["tokens"] == 11000
    # 10k prompt: half at $0.10/M, half cached at $0.01/M; 1k completion at $0.50/M.
    assert summary["per_episode"]["mean"]["cost_usd"] == pytest.approx((5000 * 0.10 + 5000 * 0.01 + 1000 * 0.50) / 1e6)
    assert summary["plan"]["mean"]["tokens"] == 110000
    assert summary["recorded_cost_usd_per_episode"] == pytest.approx(0.003)


def test_limiter_counts_prompt_plus_reserved_output_and_sizes_parallelism():
    samples = estimate.load_samples([FIXTURE], "discoverybench")
    summary = estimate.summarize(samples, episodes=1, model="openai/gpt-6-luna",
                                 max_tokens={"actor": 1000, "researcher": 500}, tpm_limit=30000)
    # (10000 prompt + 1000 + 500 reserved) over two minutes.
    assert summary["limiter_tokens_per_minute_per_worker"]["p90"] == pytest.approx(5750)
    assert summary["recommended_parallel"] == 3 and not summary["single_worker_exceeds_limit"]
    tight = estimate.summarize(samples, episodes=1, model="openai/gpt-6-luna",
                               max_tokens={"actor": 1000, "researcher": 500}, tpm_limit=5000)
    assert tight["recommended_parallel"] == 1 and tight["single_worker_exceeds_limit"]
    assert "WARNING" in estimate.render(tight)


def test_unknown_models_need_explicit_prices_and_other_benchmarks_are_ignored():
    samples = estimate.load_samples([FIXTURE], "discoverybench")
    with pytest.raises(ValueError, match="No list price"):
        estimate.summarize(samples, episodes=1, model="vendor/unknown", max_tokens={})
    assert estimate.summarize(samples, episodes=1, model="vendor/unknown", max_tokens={},
                              price=(1, 2, 1))["per_episode"]["mean"]["cost_usd"] > 0
    with pytest.raises(ValueError, match="No recorded bixbench"):
        estimate.load_samples([FIXTURE], "bixbench")


def test_published_pilot_traces_reproduce_recorded_cost():
    samples = estimate.load_samples([ROOT / "reports/full_persona_v2/recorded_traces"], "discoverybench")
    summary = estimate.summarize(samples, episodes=1, model="openai/gpt-6-luna", max_tokens={})
    assert summary["samples"] == 62
    # The modelled list-price cost stays within 25% of what OpenRouter actually billed.
    assert summary["per_episode"]["mean"]["cost_usd"] == pytest.approx(summary["recorded_cost_usd_per_episode"], rel=0.25)
