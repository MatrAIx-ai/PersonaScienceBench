# Qwen3.8 27B free campaign

Submitted 2026-10-03 as job **2058780**. Initial allocation 2058574 on m001 stalled before startup and was cancelled; replacement excludes m001. Launcher: `scripts/submit_qwen_free.sh`. Run directory: `runs/qwen38-27b-free-trial-1/`.

- Exact OpenRouter model: `qwen/qwen3.8-27b:free`; actor, researcher simulator and judge.
- Low reasoning; actor 12,288 / simulator 8,192 / judge 16,384 output-token caps.
- Frozen 200 questions (40 per benchmark), off / 155 / 001 / 003 / 046, one trial: 1,000 planned episodes.
- 30 episode workers, 30 CPUs, 128 GB RAM, general partition, 12-hour allocation.
- Prepared inputs reused; no conversion inference or paid fallback.
- Tool-call access probe succeeded with `usage.cost=0`.

The account API reported 1,000 free-model requests/day, not episodes/day. Shared free-model pacing is 18 requests/minute across workers. Transient 429 responses honor cooldowns and are retried at most six times after the initial attempt. A daily-quota response writes `fatal_api.json`, halts further requests and prevents new episodes from starting inference. In-flight and skipped episodes remain visible as incomplete/infrastructure outcomes, not scientific failures. This job may not finish the full campaign within one day's quota or one scheduler allocation.

After verifying quota reset, preserve the stop record under a dated name and resume the same run with `bash scripts/submit_qwen_free.sh --retry-infrastructure`. Completed episodes are retained; incomplete episodes receive new attempts. This restarts incomplete episodes, not their exact in-memory conversation state. Do not relaunch concurrently.

Minimal compatibility changes: main launcher accepts OpenRouter and catalog prices, EXP prices allow zero, and opt-in free-model pacing is shared by both inference paths. The default paid-model paths are not paced. No prompts, benchmark scoring rules, or scientific task content were changed. Offline validation: 51 tests passed (free pricing and billing, pacing/retries/quota stop, inference policy, and frozen-cohort guards); two existing EXP integration modules skipped because their optional fixture prerequisites were unavailable.
