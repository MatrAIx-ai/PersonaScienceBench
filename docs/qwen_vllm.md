# Local Qwen3.8-27B API server

## TP2 × DP2 update

Combined jobs now launch `--tensor-parallel-size 2 --data-parallel-size 2`:
two model replicas, each spanning two H200s, still four GPUs total per job.
vLLM's internal API load balancer distributes requests between the replicas;
the benchmark endpoint and request format are unchanged. The overall adapter
limit remains eight concurrent requests, and each replica permits up to eight
sequences. Model weights, precision, context, sampling and reasoning settings
are unchanged from the repair below. Each launch records TP/DP in `server.json`
and `repair_settings.json`. Completed TP4 episodes are retained, so analysis
must retain deployment provenance rather than label all episodes as TP2/DP2.
Interrupted episodes resume as new attempts. Throughput improvement must be
measured after the new server starts; it is not assumed from configuration.

Reference: [vLLM data parallel serving](https://docs.vllm.ai/en/stable/serving/data_parallel_deployment/).

## Repair applied 2026-10-04

The active combined campaign now uses **8 episode workers and 8 inference slots
per job**, replacing the failing 30-worker configuration described in the original
deployment below. Allocations remain 4 H200 / 64 CPU / 384 GiB. Context is 131,072
tokens. The client timeout is 1,900 seconds, each upstream attempt allows 800
seconds, and the adapter's total queue/retry deadline is 1,800 seconds. Up to three
attempts are allowed for transient transport errors and HTTP 408/429/5xx; HTTP
400 and malformed successful model outputs are not retried by the adapter.
The existing EXP 2,400-second episode wall budget remains unchanged; a longer
transport ceiling does not grant additional model steps or extra episode time.

Each launch validates eight concurrent moderate-length scientific prompts and
forced single-tool outputs. All must finish in under 600 seconds; otherwise no
benchmark episodes start. This is a startup load gate, not a guarantee that every
full-length episode finishes. The probe is excluded from benchmark results.

Disconnects cancel the in-flight upstream request and release its concurrency
slot. Per-request timings, errors, usage and retry count are logged in
`server/JOB-RESTART-TIME/requests.jsonl`; startup logs and validation reports share
that launch directory, so Slurm requeues no longer overwrite previous logs.
Successful responses include `local_transport` metadata. Local-only client
timeout overrides do not affect external OpenRouter requests.

Original summaries are preserved in each arm's `repair-20261004-before/`.
`--retry-infrastructure` preserves finished outcomes and creates a new attempt for
failed/interrupted episodes. Record this repair pass when reporting the results;
it uses a larger context capacity and different serving limits. The frozen
questions, personas, model, reasoning effort, sampling and output-token caps are
unchanged. The latest job IDs are in the campaign's `submissions.tsv`.

The original deployment details follow for provenance; current repair settings
above take precedence for the combined campaign.

This deployment serves the official `Qwen/Qwen3.8-27B` checkpoint through vLLM's
OpenAI-compatible API. The only client transport change is an optional
`OPENROUTER_BASE_URL`; request construction and benchmark scoring are unchanged.
The initial setup downloads packages and weights;
subsequent serving sets Hugging Face offline mode and loads local files.

## Configuration

| Setting | Value |
|---|---|
| Checkpoint revision | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` |
| vLLM | `0.30.0`, isolated `external/vllm-qwen/venv` |
| GPUs | 4 × H200, tensor parallelism 4 |
| Slurm | 30 CPU cores, 256 GiB host memory, 12-hour allocation |
| Weights / KV cache | BF16 / automatic native dtype |
| Context cap | 65,536 tokens, including prompt and generated output |
| Concurrent sequences | 32; a server capacity setting, not benchmark workers |
| Batched token budget | 8,192 |
| Reasoning | `low` server template default; `qwen3` reasoning parser |
| Tools | Automatic tool choice; `qwen3_xml` tool parser |
| Input scope | Text only (`--language-model-only`) |
| Network | Authenticated HTTP on the allocated cluster node, port 8000 |

The model's native context is larger; this deployment uses an explicit 64K cap.
Requests beyond that cap fail rather than silently truncating. Sampling settings
may be provided by callers; otherwise vLLM uses the checkpoint generation config.
This local backend is a distinct experimental deployment from OpenRouter, even
though the underlying model name matches. It has no OpenRouter request quota or
per-token bill; GPU allocation remains a resource cost.

## Setup and launch

### Combined campaign (current setup)

```bash
bash scripts/submit_qwen_local_campaign.sh
```

This submits five independent jobs: `persona_off`, `candidate_155`,
`candidate_001`, `candidate_003`, and `candidate_046`. Each requests one node,
4 H200 GPUs, 64 CPU cores, 384 GiB host RAM and 12 hours. Each runs one local
vLLM server and 30 concurrent episode workers, for 200 frozen questions (40 per
source), one trial per persona, 1,000 episodes total. All three roles use local
Qwen with low reasoning. Five simultaneous jobs require 20 H200s; jobs queue
independently. The standalone-server resource table above does not describe the
larger combined allocation.

The launcher excludes `r001`: both vLLM and an independent CUDA driver probe
failed there with `cuInit` error 3; a probe on `o001` succeeded. Each combined
job checks CUDA, waits for model readiness, verifies text/tool/JSON outputs,
then starts the benchmark. Startup failure prevents benchmark launch. Server
processes stop when the benchmark exits. Neither server nor compatibility API
is exposed beyond localhost in these jobs. Job-specific ports avoid conflicts.

`scripts/qwen_local_api.py` provides server-side compatibility with the caller's
existing `/key`, `/models`, and `/chat/completions` requests. It translates the
OpenRouter reasoning field to vLLM's reasoning-effort field and supplies local
catalog metadata. It cannot forward to an external provider. Catalog prices
and reported API cost are zero because no API invoice exists; these values do
not estimate GPU cost. The manifest's `provider=openrouter` records the existing
protocol path; deployment provenance and response `provider=local-vllm` identify
the actual backend. Do not label these as OpenRouter-hosted results.

Results are isolated in `runs/qwen38-local-trial-1/<arm>/`. The runner's new
`--standalone-arm` scheduling option permits one condition without borrowing an
off baseline. Prepared tasks are reused from the frozen main panel, and previous
OpenRouter results are not mixed into these local episodes. `submissions.tsv`
records all five job IDs. To submit just one condition, pass its arm name to
the submission script. Repeated submission resumes that condition's existing
run; use a new `CAMPAIGN_DIR` for another independent trial.

### Server only

```bash
bash scripts/setup_qwen_vllm.sh
bash scripts/submit_qwen_vllm.sh
```

The setup saves a full dependency snapshot to
`external/vllm-qwen/installed-requirements.txt`. Weights, environment, cache,
authentication key and runtime logs are Git-ignored. Submission creates a random
server key with owner-only permissions; it does not reuse an external provider key.

Logs and endpoint metadata are under `runs/vllm-qwen-server/`:

- `job_id.txt`: most recently submitted server job.
- `server.json`: endpoint, checkpoint, configuration, and validation status.
- `slurm-JOBID.out` and `.err`: startup and server logs.
- `gpus.csv`: allocated GPU names, driver and memory.
- `api_check.json`: actual text/tool responses and elapsed times after validation.

Once startup completes:

```bash
.venv/bin/python scripts/check_qwen_vllm.py
```

An OpenAI-compatible client uses the `base_url` in `server.json`, the key in
`external/vllm-qwen/api_key`, and model `Qwen/Qwen3.8-27B`. Aliases
`qwen/qwen3.8-27b` and `qwen/qwen3.8-27b:free` are also served. These aliases do
not route to OpenRouter. Supported routes include `/v1/models` and
`/v1/chat/completions`, with standard tool calls and token usage in responses.

Example from a machine that can reach the allocated cluster node:

```python
import json
from pathlib import Path
from openai import OpenAI

server = json.loads(Path('runs/vllm-qwen-server/server.json').read_text())
client = OpenAI(base_url=server['base_url'],
    api_key=Path(server['key_file']).read_text().strip())
reply = client.chat.completions.create(
    model=server['model'],
    messages=[{'role': 'user', 'content': 'Reply with ready.'}],
    reasoning_effort='low', max_tokens=1024)
print(reply.choices[0].message.content)
```

For access outside the cluster, use an SSH tunnel; this job does not publish a
public endpoint. Starting only this server does not redirect the benchmark;
the combined launcher supplies the local endpoint and starts the compatibility
API. When `OPENROUTER_BASE_URL` is unset, the caller still uses OpenRouter.

To change the context cap before submitting, set `VLLM_MAX_MODEL_LEN`.
`VLLM_PORT`, `VLLM_HOST`, `TIME_LIMIT` and `PARTITION` are also configurable.
The default validation script reads the default run directory. The endpoint
lasts only while its Slurm job runs; stop it with `scancel JOBID`.

Sources: [official checkpoint](https://huggingface.co/Qwen/Qwen3.8-27B),
[official vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-27B).

## Slow initialization allowance (2026-10-08)

The combined campaign launcher now sets `VLLM_ENGINE_READY_TIMEOUT_S=7200` (two hours) and `PSB_VLLM_STARTUP_TIMEOUT_S=10800` (three hours). These replace the 600-second internal and 1800-second outer deadlines that interrupted slow initialization. Both are configurable through the submission environment. The launcher reports elapsed initialization time every five minutes. TP2 × DP2, four H200s, eight episode workers, the 12-hour allocation, and resume/retry behavior remain unchanged. These longer startup deadlines do not change per-request inference timeouts.

## GPU allocation flexibility (2026-10-08)

Campaign submissions request four GPUs with the Slurm feature constraint
`h200|h100|a100`, allowing H200, H100 (80/94 GB), or A100 (80 GB) nodes.
The default CPU request is 32 so the 32-CPU A100 nodes are also eligible;
`CPUS_PER_TASK` and `GPU_CONSTRAINT` can override these defaults. Host memory
remains 384 GB. TP2 × DP2, eight episode workers, the context limit and extended
initialization deadlines are unchanged. The existing CUDA/API startup checks
run on the allocated hardware before benchmark execution; successful operation
on H100/A100 still needs confirmation from an actual allocation.
