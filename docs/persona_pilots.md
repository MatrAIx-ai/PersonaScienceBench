# Persona pilots (DiscoveryBench first)

`scripts/run_persona_pilot.py` runs small, reproducible persona experiments from one JSON
config: tasks, personas, labelled control conditions, repeats, models, budget and rate
limit. It reuses the shared runner and the scheduler's `execute()`; it adds planning,
a no-cost estimate, a budget guard and a persona × task × domain × condition report.

| Config | Purpose |
|---|---|
| [`configs/discoverybench_pilot/candidates.json`](../configs/discoverybench_pilot/candidates.json) | 12 screening candidates and their selection rationale |
| [`configs/discoverybench_pilot/screen.json`](../configs/discoverybench_pilot/screen.json) | Phase 0: persona off × 2 on the candidates (24 episodes) |
| [`configs/discoverybench_pilot/pilot.json`](../configs/discoverybench_pilot/pilot.json) | Pilot: personas 148/046/155 × 5 tasks × 2, persona off × 3, `neutral_a` × 2 (55 episodes). **Tasks are provisional** until the screen picks them. |
| [`configs/openproblems_pilot/`](../configs/openproblems_pilot) | OpenProblems denoising: smoke, screen, pilot and neutral_b configs ([adapter](adapters/openproblems_denoising.md)); they set `actor_python: .actor-venv-openproblems` |

## Why a screen first

In the 65 recorded DiscoveryBench episodes (full_persona_v2 and the ecology pilot), only 2 of 59
scored episodes were above zero, and every persona-off baseline scored 0. A pilot on unscreened
tasks would most likely score zero in every cell and could not separate personas. The screen
measures each candidate's baseline and run-to-run spread; choose pilot tasks where the baseline
is off the floor or varies, keep domains balanced, and record the reason in `pilot.json`.

## Conditions

| Condition | Arm names | What differs | Why |
|---|---|---|---|
| `persona` | `candidate_148`, … | Full published profile in the researcher system prompt | The treatment |
| `persona_off` | `persona_off` | No identity; same instructions and knowledge policy | Required by the [benchmark standards](benchmark_standards.md) §4/§8; repeats give the noise floor |
| `neutral` | `neutral_a`, `neutral_b` | An ordinary-researcher identity ([texts](../configs/persona_controls)) | Separates "any identity text" from "this persona's content" |

Deltas are task-matched: repeats are averaged within each arm × task, then over tasks.
Missing submissions count as 0 (the full_persona_v2 convention); infrastructure and
evaluator errors are excluded and listed. The report states the persona-off SD; a delta
smaller than it is indistinguishable from ordinary variation.

## Select tasks (no model calls)

```bash
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench
.venv/bin/python scripts/select_discoverybench_tasks.py --output configs/discoverybench_pilot/candidates.json
```

Selection is deterministic (seed in the file). Per domain it spreads picks over studies
(raw/processed versions count once), alternates lower/higher metadata complexity, and
prefers tasks where the adapter provides researcher facts. Earlier pilot tasks are
excluded by default. DiscoveryBench has no difficulty labels; the screen measures it.

## Estimate cost and parallelism (no model calls)

```bash
.venv/bin/python scripts/run_persona_pilot.py plan --config configs/discoverybench_pilot/pilot.json --dry-run
.venv/bin/python scripts/estimate_run_cost.py --episodes 55 --model openai/gpt-5.6-sol --tpm-limit 2000000
```

Estimates scale usage measured in recorded episodes (62 DiscoveryBench episodes by default;
add finished runs with `--samples runs/<run>/episodes`). A DiscoveryBench episode used about
250k tokens (p10 100k, p90 495k) over about 21 calls, 97% of them prompt tokens, 74% served
from cache; about $0.012 on GPT-6 Luna and $0.25 at GPT-5.6 Sol list prices.

**Tokens-per-minute limits.** One worker draws about 245k (mean) to 310k (p90) limiter-counted
tokens per minute, counting prompt plus each call's `max_tokens` as OpenAI-style limiters do.
Set `budget.tpm_limit` and leave `parallel` null to size workers from the p90 worker at 60%
headroom (see [cost estimates](cost_estimates.md)). The direct OpenAI transport
(`openai_transport.py`) retries HTTP 429, and transient 5xx responses with #14, and records the
retry count with each call; a limit below about 310k TPM can still throttle a single worker.

## Credentials

Put API keys in `.env` (ignored by Git; see `.env.example`):

| Variable | Used when |
|---|---|
| `OPENROUTER_API_KEY` | Default configs (`openai/gpt-6-luna` through OpenRouter) |
| `OPENAI_API_KEY` | Model specs with `"provider": "openai"`: the direct OpenAI Responses transport (the DiscoveryBench pilot configs use `gpt-6-luna` this way) |
| `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | Model specs with `"provider": "azure"` ([Azure setup](azure.md)) |

The runner calls provider APIs with API keys. Consumer chat subscriptions (ChatGPT Plus,
Claude Pro/Max) are not API credentials and are not supported.

## Where to run

Episodes need Linux with Bubblewrap; there is no host-execution fallback.

- **Linux workstation or cluster node:** follow [reproducibility.md](reproducibility.md)
  (`apt-get install bubblewrap`, `uv sync`, `.actor-venv`, `check-runtime`). GPUs are not
  needed for DiscoveryBench. On a scheduler (e.g. Slurm), run `plan` once, then `run` inside a
  job; `run` resumes from `finished/`, so a preempted job can be resubmitted unchanged. The
  node needs outbound HTTPS to the model provider.
- **macOS:** use the Linux container described in
  [reproducibility.md](reproducibility.md#macos-and-other-hosts-without-bubblewrap) (#13).

Run every pilot command below inside the same environment (prefix with `docker/run.sh` on macOS).
Prepared packages record absolute paths, so plan and run in the same environment.

## Run

```bash
# One persona on one task: a throwaway config with one task, one persona and no controls.
.venv/bin/python scripts/run_persona_pilot.py plan --config my-one-by-one.json --output runs/one-by-one
.venv/bin/python scripts/run_persona_pilot.py run --output runs/one-by-one --allow-provisional --yes

# Phase 0 screen (controls only), then the approved pilot.
.venv/bin/python scripts/run_persona_pilot.py plan --config configs/discoverybench_pilot/screen.json --output runs/discoverybench-screen
.venv/bin/python scripts/run_persona_pilot.py run --output runs/discoverybench-screen --allow-provisional --yes
# Edit pilot.json: set tasks from the screen and status "approved".
.venv/bin/python scripts/run_persona_pilot.py plan --config configs/discoverybench_pilot/pilot.json --output runs/discoverybench-pilot
.venv/bin/python scripts/run_persona_pilot.py run --output runs/discoverybench-pilot --yes
```

`plan` prepares task packages and per-arm configs and makes no model calls; it refuses an
existing output directory. `run` without `--yes` prints the pending work and stops. It
refuses provisional configs unless `--allow-provisional`. Before each launch it reserves a
p90 episode cost for every running job and stops scheduling once the budget would be exceeded.

Control conditions are part of the same config: set `controls.persona_off.repeats` and
`controls.neutral.arms`. To run controls alone, leave `personas.ids` empty (as in `screen.json`).

## Rerun and report

```bash
.venv/bin/python scripts/run_persona_pilot.py run --output runs/discoverybench-pilot --yes            # resume unfinished jobs
.venv/bin/python scripts/run_persona_pilot.py run --output runs/discoverybench-pilot --yes --retry-errors  # retry infrastructure failures once
.venv/bin/python scripts/run_persona_pilot.py report --output runs/discoverybench-pilot               # regenerate REPORT.md, results.csv, summary.json
```

Retries apply only to infrastructure failures, never to low scores; originals stay in
`finished/` and `results.csv`. To rerun an experiment from scratch, plan into a fresh directory.
`manifest.json` records the pilot config and its hash, Git revision, per-arm config and persona
hashes, models and the pre-run estimate; each episode keeps its full API records, events,
submission and native evaluation under `episodes/`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Bubblewrap is required; host execution is disabled` | Not on Linux or bwrap missing: install `bubblewrap` or use the container |
| `No module named personasciencebench` on macOS | Recent Python skips `.pth` files with the macOS `hidden` flag: `chflags -R nohidden .venv .actor-venv` |
| `OpenAI HTTP 429` after retries | Over the TPM limit: lower `parallel` or set `budget.tpm_limit` |
| `OPENROUTER_API_KEY is not configured` | Add the key to `.env` in the repository root |
| `Assets are not ready` during `plan` | Fetch sources first; the task's data files are missing |
| `STOPPED: N consecutive infrastructure failures` or `network: ... did not resolve` | The host lost its network (often after sleep). Fix it, then `run --retry-errors`: jobs that never started relaunch, and episodes that ran retry once |
| A native metric `killed by signal 9` | Out of memory during grading: lower `parallel`, then `regrade --output runs/<run>` re-grades the sealed submissions without model calls |
| `... exists; use a fresh output directory` | `plan` never overwrites; choose a new `--output` |
| Every score is 0 | Expected on many DiscoveryBench tasks; check the screen report before choosing tasks |

**Recorded runs.** The published DiscoveryBench pilot, replication and counterfactual runs
([reports](../reports/discoverybench_persona_pilot/README.md)) were executed on 2026-09-29 from an
earlier branch (commits 742b98b and later, recorded in each `summary.json`) whose direct-OpenAI
client used Chat Completions. The configs here reproduce the same tasks, job lists and injected
persona prompts exactly (checked by hash), but now route through `openai_transport.py`'s Responses
API; treat a rerun as the same design on a changed transport, not a byte-identical replay.
