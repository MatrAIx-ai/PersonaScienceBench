# Azure inference for task validation

The shared `personasciencebench run` and `regrade` commands support Azure Chat
Completions through the existing model-client interface. Task adapters and native
graders remain independent of the inference provider. Separate EXP and SciConv
launchers retain their own provider setup.

## Credentials and model configuration

Copy `.env.example` to the ignored `.env` if needed, then enter credentials locally:

```bash
python scripts/configure_azure.py
```

The helper uses hidden key entry, refuses a tracked or non-ignored `.env`, and
writes with owner-only permissions. Exported environment variables take precedence;
loading `.env` does not perform shell expansion.

```dotenv
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT=gpt-5.6-sol
```

The project endpoint ending in `/api/projects/PROJECT` is a provenance field;
Chat Completions uses the resource endpoint ending in `/openai/v1/`.

[The example configuration](../configs/discoverybench-azure.json) sets Azure
GPT-5.6 Sol for actor, researcher and judge. Each role's `model` must match its
Azure deployment name. **The shared runner reads model names from the config;
`AZURE_OPENAI_DEPLOYMENT` does not override them.** For a different deployment,
edit the three `models` entries in an ignored `configs/*.local.json` copy.

The tested configuration uses `reasoning_effort=none` for function calling.
Native judge temperature, top-p, penalties and per-call token limits are
preserved. The transport maps `max_tokens` to `max_completion_tokens`, records
the resolved model and usage, and labels the Azure judge variant. It does not
silently substitute a model or retry a failed inference call. An authenticated
`/models` listing alone does not verify that a deployment can serve requests.

## Runtime and execution

Use Python 3.12 and the checked-in dependency locks:

```bash
uv sync --locked --python /usr/bin/python3.12 --extra api --extra actor --extra test --extra scientific-evaluation
uv venv --python /usr/bin/python3.12 .actor-venv
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
```

The runtime check must pass before a scientific run. On hosts that restrict
unprivileged user namespaces, an administrator-provisioned launcher can be
selected with `PERSONASCIENCEBENCH_BWRAP`. Use the same launcher for the check and
the run. Do not run the benchmark process with `sudo`. The actor check verifies
network isolation, the expected user/group, zero effective capabilities, and
absence of API credentials and private user directories.

Prepare the [ecology task selection](adapters/discoverybench.md#ecology-tasks),
then run one validation episode per task:

```bash
.venv/bin/python -m personasciencebench run \
  --prepared prepared/discoverybench-ecology --benchmarks discoverybench \
  --output runs/discoverybench-ecology-validation-01 \
  --actor-python .actor-venv --config configs/discoverybench-azure.json --parallel 2
```

This makes paid Azure calls. The config selects three cases and persona off;
the researcher still participates in the standard approach/result reviews.
Use a fresh output path for each attempt. Raw API receipts, evaluator references,
interaction logs and submissions remain under ignored `runs/`. Token usage is
recorded; Azure billing rates are needed to calculate monetary cost.

Existing science profiles attach through the [shared helper](science_personas/INTEGRATION_GUIDE.md):

```bash
.venv/bin/python -m personasciencebench.science_personas attach \
  --profile examples/science_personas/profiles/pi_cautious.json \
  --config configs/discoverybench-azure.json \
  --output configs/discoverybench-ecology-persona.local.json
```

This changes only the private researcher identity. It creates a config and does
not start a run. Full-profile `persona.system_prompt` configurations are also
supported by the shared runner. Hold the task package, model settings, knowledge
policy, review budget and grader fixed within any persona comparison.
