#!/usr/bin/env python3
"""Estimate tokens, cost and safe parallelism from recorded episodes. Makes no model calls.

Samples come from published Markdown traces (`reports/*/recorded_traces`) or raw run
directories (`controller/api_calls.private.jsonl`). Estimates scale per-episode usage
by the planned episode count; they are not guarantees, because usage varies by task
and trajectory (see the p10/p90 columns).

Rate limits: many providers (e.g. OpenAI) charge a request against tokens-per-minute
as prompt tokens plus the request's max output tokens, cached or not. `counted` uses
that rule, so recommended parallelism is conservative for limiters that count less.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
CALL = re.compile(r"^### M\d+\. (\w+) call — `([^`]+)`")
EVENT_TIME = re.compile(r"^### C\d+\. `[^`]+` — (\S+)")
# Public list prices (USD per million tokens: input, output, cached input) from the
# OpenRouter model catalog, read 2026-09-29. Direct providers and Azure may differ.
PRICES = {
    "openai/gpt-6-luna": (0.10, 0.50, 0.01),
    "openai/gpt-5.6-luna": (0.20, 1.20, 0.02),
    "openai/gpt-5.6-sol": (2.00, 10.00, 0.20),
    "openai/gpt-6-sol": (2.00, 10.00, 0.20),
    "anthropic/claude-sonnet-5.5": (2.00, 10.00, 0.20),
    "anthropic/claude-opus-5.5": (4.00, 20.00, 0.20),
}
ALIASES = {"gpt-5.6-sol": "openai/gpt-5.6-sol", "gpt-6-luna": "openai/gpt-6-luna"}


def _event_time(value: str) -> float:
    """Controller events use ISO timestamps; the SciConv runner writes Unix epoch seconds."""
    try:
        return float(value)
    except ValueError:
        return datetime.fromisoformat(value).timestamp()


def _usage_blocks(lines, start):
    j = start + 1
    while not lines[j].startswith("````json"):
        j += 1
    k = j + 1
    while not lines[k].startswith("````"):
        k += 1
    return json.loads("\n".join(lines[j + 1:k])), k


def _empty_role():
    return {"calls": 0, "prompt": 0, "completion": 0, "cached": 0, "cost": 0.0}


def parse_trace(path: Path) -> dict | None:
    """One published trace -> per-role usage, recorded cost and wall-clock duration."""
    text = path.read_text(errors="replace")
    instance = re.search(r"\*\*Instance:\*\* `([^`]+)`", text)
    if not instance:
        return None
    lines = text.splitlines()
    roles, role, times = {}, None, []
    i = 0
    while i < len(lines):
        call, event = CALL.match(lines[i]), EVENT_TIME.match(lines[i])
        if call:
            role = call.group(1).lower()
            roles.setdefault(role, _empty_role())["calls"] += 1
        elif event:
            times.append(_event_time(event.group(1)))
        elif lines[i].strip() == "<summary>Usage</summary>" and role:
            usage, i = _usage_blocks(lines, i)
            _add(roles[role], usage)
            role = None
        i += 1
    return {"source": str(path), "task": instance.group(1), "roles": roles,
            "duration_s": max(times) - min(times) if len(times) > 1 else None}


def _add(bucket, usage):
    bucket["prompt"] += usage.get("prompt_tokens", 0) or 0
    bucket["completion"] += usage.get("completion_tokens", 0) or 0
    bucket["cached"] += (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
    bucket["cost"] += usage.get("cost", 0) or 0


def parse_run_case(case: Path) -> dict | None:
    """One raw run case directory -> the same record shape as parse_trace."""
    calls = case / "controller/api_calls.private.jsonl"
    if not calls.is_file():
        return None
    roles = {}
    for line in calls.read_text().splitlines():
        record = json.loads(line)
        bucket = roles.setdefault(record.get("role", "unknown"), _empty_role())
        bucket["calls"] += 1
        _add(bucket, record.get("usage") or {})
    episode = json.loads((case / "controller/episode.private.json").read_text()) \
        if (case / "controller/episode.private.json").is_file() else {}
    result = json.loads((case / "result.json").read_text()) if (case / "result.json").is_file() else {}
    return {"source": str(case), "task": episode.get("id", case.name), "roles": roles,
            "duration_s": result.get("elapsed_seconds")}


def load_samples(paths: list[Path], benchmark: str) -> list[dict]:
    samples = []
    for path in paths:
        records = ([parse_trace(p) for p in sorted(path.glob("*.md"))] +
                   [parse_run_case(p.parent.parent) for p in sorted(path.rglob("controller/api_calls.private.jsonl"))])
        samples += [r for r in records if r and r["task"].startswith(benchmark + ":") and r["roles"]]
    if not samples:
        raise ValueError(f"No recorded {benchmark} episodes with usage under {', '.join(map(str, paths))}")
    return samples


def total(sample, key):
    return sum(r[key] for r in sample["roles"].values())


def counted_tokens(sample, max_tokens: dict[str, int]) -> float:
    """Tokens a prompt+max_tokens limiter charges: every call reserves its role's output cap."""
    return sum(r["prompt"] + r["calls"] * max_tokens.get(role, 0) for role, r in sample["roles"].items())


def quantile(values, q):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def price_for(model: str, override: tuple[float, float, float] | None):
    if override:
        return override
    model = ALIASES.get(model, model)
    if model not in PRICES:
        raise ValueError(f"No list price for {model}; pass --price-in/--price-out/--price-cached")
    return PRICES[model]


def episode_cost(prompt, completion, cache_share, price, cached=True):
    rate_in, rate_out, rate_cached = price
    if not cached:
        cache_share = 0.0
    return (prompt * (1 - cache_share) * rate_in + prompt * cache_share * rate_cached + completion * rate_out) / 1e6


def summarize(samples, *, episodes: int, model: str, max_tokens: dict[str, int],
              tpm_limit: int | None = None, headroom: float = 0.6,
              price: tuple[float, float, float] | None = None) -> dict:
    """Scale measured per-episode usage to a plan; recommend parallel workers under a TPM limit."""
    price = price_for(model, price)
    prompts = [total(s, "prompt") for s in samples]
    completions = [total(s, "completion") for s in samples]
    cache_share = sum(total(s, "cached") for s in samples) / max(1, sum(prompts))
    per_episode = {}
    for label, q in (("p10", 0.10), ("mean", None), ("p90", 0.90)):
        prompt = statistics.mean(prompts) if q is None else quantile(prompts, q)
        completion = statistics.mean(completions) if q is None else quantile(completions, q)
        per_episode[label] = {"tokens": prompt + completion,
                              "cost_usd": episode_cost(prompt, completion, cache_share, price),
                              "cost_usd_no_cache": episode_cost(prompt, completion, cache_share, price, cached=False)}
    rates = [counted_tokens(s, max_tokens) / (s["duration_s"] / 60) for s in samples if s.get("duration_s")]
    worker_tpm = {"mean": statistics.mean(rates), "p90": quantile(rates, 0.9)} if rates else None
    durations = [s["duration_s"] for s in samples if s.get("duration_s")]
    result = {
        "samples": len(samples), "sample_tasks": sorted({s["task"] for s in samples}),
        "model": model, "price_usd_per_million": dict(zip(("input", "output", "cached_input"), price)),
        "cache_share_of_prompt": cache_share, "calls_per_episode": statistics.mean(total(s, "calls") for s in samples),
        "per_episode": per_episode, "episodes": episodes,
        "plan": {k: {"tokens": v["tokens"] * episodes, "cost_usd": v["cost_usd"] * episodes,
                     "cost_usd_no_cache": v["cost_usd_no_cache"] * episodes} for k, v in per_episode.items()},
        "episode_minutes": {"mean": statistics.mean(durations) / 60, "p90": quantile(durations, 0.9) / 60} if durations else None,
        "limiter_tokens_per_minute_per_worker": worker_tpm,
        "recorded_cost_usd_per_episode": statistics.mean(total(s, "cost") for s in samples),
    }
    if tpm_limit and worker_tpm:
        # Average rates hide bursts (several quick actor calls with a long prompt); size on the p90 worker
        # and keep only `headroom` of the limit so concurrent bursts rarely collide.
        result["tpm_limit"] = tpm_limit
        result["recommended_parallel"] = max(1, int(headroom * tpm_limit // worker_tpm["p90"]))
        result["tpm_headroom"] = headroom
        # Even one worker can outrun a small limit; then only rate-limit waits keep episodes alive.
        result["single_worker_exceeds_limit"] = worker_tpm["p90"] > tpm_limit
    return result


def render(summary: dict) -> str:
    lines = [f"Measured from {summary['samples']} recorded episodes ({', '.join(summary['sample_tasks'])}).",
             f"Model {summary['model']} at ${summary['price_usd_per_million']['input']}/"
             f"${summary['price_usd_per_million']['output']}/${summary['price_usd_per_million']['cached_input']} "
             f"per M input/output/cached; cache share {summary['cache_share_of_prompt']:.0%}; "
             f"{summary['calls_per_episode']:.1f} API calls per episode.", "",
             "| | tokens / episode | cost / episode | plan tokens | plan cost | plan cost, no cache |",
             "|---|---:|---:|---:|---:|---:|"]
    for label in ("p10", "mean", "p90"):
        e, p = summary["per_episode"][label], summary["plan"][label]
        lines.append(f"| {label} | {e['tokens']:,.0f} | ${e['cost_usd']:.3f} | {p['tokens']:,.0f} | "
                     f"${p['cost_usd']:.2f} | ${p['cost_usd_no_cache']:.2f} |")
    lines.append(f"\nPlanned episodes: {summary['episodes']}.")
    if summary.get("episode_minutes"):
        lines.append(f"Episode wall time: mean {summary['episode_minutes']['mean']:.1f} min, p90 {summary['episode_minutes']['p90']:.1f} min.")
    if summary.get("limiter_tokens_per_minute_per_worker"):
        w = summary["limiter_tokens_per_minute_per_worker"]
        lines.append(f"Limiter-counted tokens per minute per worker (prompt + max_tokens): mean {w['mean']:,.0f}, p90 {w['p90']:,.0f}.")
    if "recommended_parallel" in summary:
        lines.append(f"Recommended parallel workers for a {summary['tpm_limit']:,} TPM limit "
                     f"(p90 worker, {summary['tpm_headroom']:.0%} headroom): {summary['recommended_parallel']}.")
        if summary["single_worker_exceeds_limit"]:
            lines.append("WARNING: one p90 worker alone exceeds this limit. Run with parallel 1 and set "
                         "rate_limit_retries (e.g. 6) for every model role, or request a higher limit.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, nargs="+", default=[ROOT / "reports/full_persona_v2/recorded_traces"])
    parser.add_argument("--benchmark", default="discoverybench")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--model", default="openai/gpt-6-luna")
    parser.add_argument("--price-in", type=float)
    parser.add_argument("--price-out", type=float)
    parser.add_argument("--price-cached", type=float)
    parser.add_argument("--tpm-limit", type=int)
    parser.add_argument("--max-tokens", type=json.loads, default={"actor": 12288, "researcher": 8192, "judge": 4096},
                        help="JSON role -> max output tokens reserved per call")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    override = None
    if any(v is not None for v in (args.price_in, args.price_out, args.price_cached)):
        if None in (args.price_in, args.price_out):
            parser.error("--price-in and --price-out go together")
        override = (args.price_in, args.price_out, args.price_cached if args.price_cached is not None else args.price_in)
    summary = summarize(load_samples(args.samples, args.benchmark), episodes=args.episodes, model=args.model,
                        max_tokens=args.max_tokens, tpm_limit=args.tpm_limit, price=override)
    print(json.dumps(summary, indent=2) if args.json else render(summary))


if __name__ == "__main__":
    main()
