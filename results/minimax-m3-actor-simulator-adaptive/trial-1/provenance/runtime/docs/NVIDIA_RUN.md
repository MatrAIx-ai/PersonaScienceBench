# Gemini 3.8 Flash through NVIDIA

This campaign uses `gcp/google/gemini-3.8-flash` for actor and researcher simulator,
both requesting `reasoning_effort="medium"`, through
`https://inference-api.nvidia.com/v1/chat/completions`. It collects one trial of
the frozen 200 questions under off / 155 / 001 / 003 / 046: 1,000 episodes.
Final grading is deferred to the receiving team's Astra / low pass.

## Setup and validation

Run `bash scripts/setup_main.sh` on a Linux host with working Bubblewrap isolation.
Use managed Python 3.12 if the system Python's library links fail the runtime's
trusted-path check. Both `.venv` and `.actor-venv` must use the same resolved base
interpreter. The setup script acquires pinned public source/data assets without
LLM calls. The tracked reference preparation is restored separately below.

Provide `NVIDIA_API_KEY` in an ignored `.env` file or the environment. The loader
reads literal assignments and does not evaluate shell expressions; existing
environment values take precedence. An explicit external dotenv path is supported,
so no credential copy is needed.

```bash
.venv/bin/python scripts/check_main.py
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
.venv/bin/python scripts/check_nvidia.py --env-file /path/to/.env
```

The last command reads authenticated `/models` and `/model/info` metadata without
inference. Add `--live --output runs/gemini-nvidia-validation/api-check.json` for
small paid checks of medium reasoning, forced tools, tool-result continuation,
typed researcher decisions, JSON output and token accounting. This is an API
compatibility check, not an executed scientific episode or a claim of complete
benchmark compatibility.

## Frozen inputs and launch

The repository now ships the reference preparation at
[`configs/main_run/frozen/astra-20260929-v1`](../configs/main_run/frozen/astra-20260929-v1/README.md).
Restore it once into a fresh run directory after public asset acquisition. The
restorer verifies metadata and asset hashes, rebases paths, and saves
`preparation_receipt.json`. The final EXP cards are included, so no separate
extraction cache or new extraction inference is required.

```bash
.venv/bin/python scripts/restore_main_preparation.py \
  --run-dir runs/main/gemini-3.8-flash-nvidia-medium/trial-1
ENV_FILE=/path/to/.env bash scripts/run_gemini_nvidia.sh
```

`RUN_DIR` and `WORKERS` override the defaults (the path above and four workers).
The launcher supplies `--provider nvidia --model gcp/google/gemini-3.8-flash
--reasoning-effort medium --collect-only --require-prepared`. The main runner
checks isolation and the existence of every required prepared package before API
preflight or episode execution. Frozen selection/persona hashes remain enforced.

Resume with the same command/directory; append `--retry-infrastructure` for
technical repairs. Do not use `--retry-missing` as a default repair policy.
Changing grading mode requires a new run directory. Credentials are inherited by
controller subprocesses but excluded from the actor sandbox and exported records.

## Collection and accounting

`--collect-only` excludes the judge from API preflight and execution across the
shared, SciConv and EXP runners. It records Astra / low as the intended final
judge. Saved final submissions, original events, task/evaluator inputs, artifacts
and usage records remain available for later grading. Pending evaluation records
contain `status="grading_pending"`, empty metrics and `score=null`; no Gemini
judge scores are presented as Astra results. Scientific missing submissions and
execution failures retain their separate statuses.

NVIDIA requests use the OpenAI SDK's Chat Completions interface. The transport
converts the harness reasoning field to `reasoning_effort`, removes OpenRouter
routing fields, and preserves Gemini tool-call metadata across SDK turns. The
serialized wire payload and returned usage are recorded without authentication
headers. Failed model requests are not automatically retried; 401/403 errors
write the main runner's fatal-API marker and stop later requests.

EXP cost estimates use the selected deployment's advertised per-token prices
from `/model/info`, not hard-coded OpenAI prices. The metadata snapshot preserves
both deployment identity and accounting base model. On 2026-10-14 the gateway
reported deployment `vertex_ai/gemini-3.8-flash` but accounting base model
`vertex_ai/gemini-3.7-flash`, with input/output estimates of $0.75/$3.75 per million
tokens. These are gateway-advertised accounting estimates, not independently
verified billing rates or proof of the upstream model version. Preserve the
discrepancy in campaign provenance.

Deliver the complete tracked bundle under `results/<model-slug>/trial-1/` according
to [TEAM_HANDOFF.md](TEAM_HANDOFF.md), with explicit pending-grading records and
hashes. Ignored `runs/` output alone does not constitute delivery. No collection
bundle should be marked complete until all 1,000 slots and required artifacts are
verified and the export is pushed.

## Response repair and export

The initial trial and first repair exposed some actor responses whose finish
reason was `length` but whose reported output was below the requested cap and
contained neither text nor a tool call. The opt-in
`PSB_NVIDIA_EMPTY_LENGTH_RETRIES=2` policy permits at most two identical-request
replays for that specific case. It is disabled by default. It never changes the
model, prompts, medium effort, token cap, or safety settings; content filters,
refusals, partial answers, exhausted caps and transport exceptions are not
automatically replayed. Every returned response and its usage are recorded with
`response_repair` metadata. Record this policy as a repair, not an original run.

Once the coordinator stops, create the collection export without inference:

```bash
.venv/bin/python scripts/export_collection_bundle.py \
  --run-dir runs/main/gemini-3.8-flash-nvidia-medium/trial-1 \
  --output results/gemini-3.8-flash-actor-simulator-nvidia-medium/trial-1 \
  --env-file /path/to/.env
.venv/bin/python scripts/validate_collection_bundle.py \
  results/gemini-3.8-flash-actor-simulator-nvidia-medium/trial-1
```

The exporter refuses to overwrite an existing destination, export running slots,
or declare completion with unresolved execution failures. `--allow-partial`
permits an explicitly labeled partial checkpoint; `--endpoint-snapshot` can
select an immutable earlier results snapshot only for such a checkpoint.
All attempts and their submissions remain available, with original attempt 1
separate from the latest authorized repair. Missing submissions are scientific
outcomes, including the EXP non-submissions previously misclassified by the
coordinator's exit-code rule. No favorable-score selection is performed.

Validation checks every file hash, 1,000 slot identities, event-line mappings,
selected/original attempts, submission artifact paths, grading-input paths and
pending-score disposition. Export scans for configured credentials and common
token patterns, including decompressed payloads. Public shared conversations
exclude private context; controller grading inputs stay separate for the team.
These commands prepare and validate files only; commit/push and remote-commit
verification remain separate delivery steps. Final grading stays deferred.

## Current machine readiness (2026-10-17)

Both previously identified blockers are resolved. The maintainer's portable
bundle arrived in upstream revision `d672e19`. All 200 selected tasks have been
restored into `runs/main/gemini-3.8-flash-nvidia-medium/trial-1/prepared`, with
629 actor asset copies and 449 unique source files verified. The receipt records
bundle and restored-metadata hashes; no preparation inference was performed.

The administrator installed and loaded the application-specific AppArmor policy.
The benchmark's real runtime check now reports `isolation_ok: true`, managed
Python 3.12.11 and a separate network namespace. The 22 runtime, frozen-input
and NVIDIA integration tests pass. NVIDIA model catalog access was rechecked
successfully; the earlier live API compatibility probes also passed.
These checks establish readiness, not completion of any scientific episode.

### AppArmor policy installed on this host

[configs/apparmor/personasciencebench-bwrap](../configs/apparmor/personasciencebench-bwrap)
uses Ubuntu's documented application-specific `userns` permission. It applies to
the system `/usr/bin/bwrap` for all users, not only this benchmark. The
`unconfined` flag leaves other AppArmor operations unrestricted for that
application; Bubblewrap's own isolation still applies. It does not change the
global sysctl, grant host capabilities, or remove any benchmark sandbox checks.
See [Ubuntu's policy design](https://discourse.ubuntu.com/t/spec-unprivileged-user-namespace-restrictions-via-apparmor-in-ubuntu-23-10/37626).

The following installation commands are retained for another host; this host
already has the profile loaded. Review existing policy before installing, and
do not overwrite a local profile or add a competing `/usr/bin/bwrap` profile.

```bash
# Validate syntax without loading policy or writing the parser cache.
apparmor_parser --skip-kernel-load --skip-cache configs/apparmor/personasciencebench-bwrap
sudo install -o root -g root -m 0644 configs/apparmor/personasciencebench-bwrap /etc/apparmor.d/personasciencebench-bwrap
sudo apparmor_parser --add /etc/apparmor.d/personasciencebench-bwrap

# Run as the ordinary user, after the administrator loads the profile.
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_runtime.py
```

The runtime check must pass before launching episodes. If loading succeeds but
the check still fails, inspect the administrator-visible AppArmor denial logs;
do not assume this proposal resolves every possible host restriction. To undo
only this newly installed profile:

```bash
sudo apparmor_parser --remove /etc/apparmor.d/personasciencebench-bwrap
sudo rm /etc/apparmor.d/personasciencebench-bwrap
```
