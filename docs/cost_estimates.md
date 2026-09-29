# Estimating tokens, cost and parallelism

`scripts/estimate_run_cost.py` scales per-episode usage measured in recorded episodes to a planned
number of episodes. It makes no model calls.

```bash
# Defaults: the 62 published full_persona_v2 DiscoveryBench traces and GPT-6 Luna list prices.
.venv/bin/python scripts/estimate_run_cost.py --episodes 55
.venv/bin/python scripts/estimate_run_cost.py --episodes 55 --model openai/gpt-5.6-sol --tpm-limit 2000000
# Measure your own finished runs instead (raw controller/api_calls.private.jsonl records).
.venv/bin/python scripts/estimate_run_cost.py --samples runs/<run> --episodes 300 --model gpt-6-luna
```

It reports tokens and cost per episode and for the plan at p10, mean and p90, with and without
prompt caching; episode wall time; and tokens per minute per worker. Rate-limit arithmetic counts
each call as prompt tokens plus its `max_tokens` reservation, the rule OpenAI-style limiters use,
so the recommended parallelism (p90 worker, 60% of the limit by default) is conservative. If one
worker alone exceeds the limit, it says so.

Prices are public list prices (OpenRouter catalogue, 2026-09-29) in `PRICES`; pass
`--price-in/--price-out/--price-cached` (USD per million tokens) for other models or contracts.
Estimates vary with task and trajectory, so check the p90 column against your budget.

**Reference measurements.** A full_persona_v2 DiscoveryBench episode used about 250k tokens (p10 100k,
p90 495k) over about 21 calls, 97% of them prompt tokens and 74% cached: about $0.012 on GPT-6 Luna, and
the model reproduces the billed cost within 25%. On direct OpenAI `gpt-6-luna`, 150 later DiscoveryBench
episodes averaged about 100–120k tokens and $0.006–0.007. One worker drew about 250–310k limiter-counted
tokens per minute, so a 2M TPM limit supports about four workers.
