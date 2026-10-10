# Local Qwen campaign failure audit — 2026-10-04

The two available 200-episode result files contain 39 finished episodes and 361
infrastructure errors. Finished means a recorded terminal benchmark outcome,
not a correct answer. Counts below classify each episode once from saved native
errors; opaque wrappers may conceal additional timeout failures.

| Final classification | Persona 155 | Persona 001 |
|---|---:|---:|
| Finished | 19 | 20 |
| HTTP 500 / timeout / transport failure | 171 | 163 |
| Opaque wrapped error | 8 | 14 |
| HTTP 400 | 1 | 2 |
| Researcher decision tool-count mismatch | 1 | 1 |

## Confirmed primary failure chain

1. The benchmark has 30 simultaneous episode workers per model server. Requests
   are non-streaming and permit 12,288 actor, 8,192 researcher, and 16,384 judge
   output tokens, including reasoning.
2. Both the benchmark request settings and the local adapter use a 600-second
   HTTP timeout. These timeouts race: the client can time out directly, or the
   adapter can time out first.
3. The adapter does not catch `httpx.ReadTimeout`. FastAPI therefore emits an
   HTTP 500 instead of a structured upstream timeout. Persona 155's adapter log
   contains 179 such exceptions. This counts requests, not failed episodes.
4. The caller does not retry these failures; affected episodes become
   infrastructure errors. The median failed episode duration is approximately
   632 seconds for 155 and 636 seconds for 001, consistent with the 600-second
   boundary plus startup/other work.
5. `run_main.py` returns exit code 1 if any episode is an infrastructure error.
   Thus persona 155's Slurm FAILED state does not mean the server crashed at the
   end: its coordinator processed all 200 slots and reported incomplete coverage.

For persona 155, 604 server log intervals with at least 20 active requests had
a median aggregate generation throughput of 39.2 tokens/s. This is a median of
logged intervals, not per-request decode speed or total-run token throughput.
It supports a concurrency/latency mismatch; it does not identify the underlying
GPU/kernel bottleneck. The logs also show an all-reduce fallback on a GPU topology
without NVSwitch multicast and a first-use Triton compilation. Neither is proven
to explain the sustained slowness. Small API readiness checks did not validate
performance under 30 simultaneous scientific-agent requests.

## Other confirmed issues and limits

- The initial `r001` deployment failed CUDA initialization even in a standalone
  driver probe. Another node passed; later servers loaded and served requests.
  That earlier node failure is separate from the episode timeout failures.
- Slurm preempted persona-off and persona-001 jobs and requeued them. Off's saved
  30 running episode states were interrupted, not still-active workers.
- Automatic requeue overwrites `server/stdout.log`, `stderr.log`, and
  `adapter.log`. Persona 001's current logs cover a subsequent launch, so their
  timeout counts cannot be compared with its full accumulated result table.
- At least one researcher response returned **two** tool calls, while the
  protocol requires exactly one `researcher_decision`. The recorded response
  finished with `stop`, not a token-limit termination. Do not silently accept or
  merge these calls.
- Three episodes report HTTP 400. The client did not retain the response error
  body, so their exact causes are unconfirmed. A 155 example had already reached
  51,880 prompt tokens before its failing later request, against a 65,536 context
  cap with 12,288 requested output tokens. Context exhaustion is plausible, not
  established from the available error log.
- No evidence here identifies an external API quota as the cause. The word
  OpenRouter persists in error messages because the existing protocol client is
  reused; the actual inference endpoint is local.

## Recommended repair before resubmission

Keep model/persona settings fixed. Measure representative requests at lower
inference concurrency, then choose concurrency and an end-to-end timeout budget
from observed latency. Coordinate benchmark, adapter and episode deadlines;
raising only one HTTP timeout is insufficient. Return structured timeout/error
responses, preserve their bodies, and cancel abandoned upstream work. Retry only
eligible infrastructure failures with bounded backoff and preserved attempts.
Preserve per-launch logs across Slurm requeues. Investigate context-limit and
tool-format cases separately. Do not treat incomplete infrastructure episodes
as model score zeros or blindly rerun the unchanged configuration.

Evidence: `runs/qwen38-local-trial-1/{candidate_155,candidate_001}/results.json`,
persona 155 `server/adapter.log` and `server/stdout.log`, saved role configs,
Slurm stderr logs, `scripts/qwen_local_api.py`, and `scripts/run_main.py`.
Machine-readable episode classification: `reports/local_vllm/failure_audit.json`.
This audit does not change or resubmit the queued jobs.
