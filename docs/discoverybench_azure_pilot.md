# DiscoveryBench persona pilot on Azure

This pilot evaluates researcher-persona variation on two DiscoveryBench studies.
The adapter supplies pinned datasets, public task exports, source-attributed
researcher context, and native discovery scoring. The OpenHands actor uses the
shared approach/result review protocol.

## Azure configuration

Copy `.env.example` to the ignored `.env` if it does not exist. Fill these fields
locally; the tracked example contains placeholders only:

```dotenv
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT=gpt-5.6-sol
```

For hidden terminal entry without putting a key in command history:

```bash
python scripts/configure_azure.py
```

The helper refuses a tracked or non-ignored `.env`, preserves the other settings,
and writes with owner-only permissions. Exported environment variables take
precedence over `.env`. No shell expansion is performed when loading it.

The Foundry project URL ending in `/api/projects/PROJECT` is not the Chat
Completions base URL. The Azure v1 endpoint uses `/openai/v1/`; `model` must be the
**deployment name**. An authenticated `/models` listing is not proof that a
particular deployment can serve requests, so the pilot also makes explicit small
JSON and function-call probes before scientific execution. There is no model
fallback or automatic inference retry. See [Microsoft's v1 API documentation](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle).

[The pilot configuration](../configs/discoverybench-azure.json) selects Azure
GPT-5.6 Sol for actor, researcher, and judge, with `reasoning_effort=none` for
compatibility with function calling on the tested Azure Chat Completions deployment. Native judge temperature,
top-p, penalties, and per-call token limits are preserved. The transport maps
`max_tokens` to Azure's `max_completion_tokens` without changing its value and
records both requested settings and provider usage. A resolved model ID is saved
for each completion. The evaluator records the configured Azure judge as a
DiscoveryBench variant. [GPT-5.6 Sol model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

The deployment environment variable overrides all three Azure role model names
for this pilot. For separate deployments per role, leave it empty and edit each
role's `model` in a copy of the configuration. Existing OpenRouter configurations
continue to work without a `provider` field. Azure support is wired into the
shared `run` and `regrade` paths; the separate EXP and SciConv launchers are outside
this pilot's scope.

## Prepare the two tasks

Use Python 3.12 with the checked-in dependency locks:

```bash
uv sync --locked --python /usr/bin/python3.12 --extra api --extra actor --extra test --extra scientific-evaluation
uv venv --python /usr/bin/python3.12 .actor-venv
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
.venv/bin/python -m personasciencebench --source-root external/sources fetch-sources --benchmarks discoverybench
.venv/bin/python -m personasciencebench --source-root external/sources prepare \
  --benchmarks discoverybench --selection configs/discoverybench-azure-selection.json \
  --output prepared/discoverybench-azure
.venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
```

The source is pinned to `c31fcf011e070f021a5f5b906896d0821f6880e8`.
The selected engineering task estimates survey proportions and bootstrap confidence
intervals; the sociology task compares wealth by incarceration history. Each has
a source-attributed researcher fact pack and a separate evaluator-private reference.
Only the question, public dataset descriptions, and approved input files reach the
actor. The upstream corpus stays under ignored `external/` with its licenses.

If preparation already exists, use it after checking its manifest or choose a
fresh output path. Preparation and run outputs refuse to overwrite earlier work.

### Host runtime requirements

The runtime check must pass before running this pilot. On hosts that restrict
unprivileged user namespaces, use a sandbox launcher approved by the host
administrator through the existing `PERSONASCIENCEBENCH_BWRAP` environment
variable. The runner requires an isolated runtime; it has no host-execution
fallback.

```bash
PERSONASCIENCEBENCH_BWRAP=/absolute/path/to/approved/bwrap-launcher \
  .venv/bin/python -m personasciencebench check-runtime --actor-python .actor-venv
```

Set the same environment variable when invoking the pilot. Its plan records and
hashes the actual launcher. The runtime check verifies a separate network
namespace, expected UID/GID, zero effective capabilities, and absence of model
credentials and private user directories. A failing check stops execution before
paid compatibility probes.

## Run the matched experiment

Preview the full plan offline:

```bash
.venv/bin/python scripts/run_discoverybench_persona_pilot.py \
  --output runs/discoverybench-plan-01
```

Execute paid calls on a working standard sandbox:

```bash
.venv/bin/python scripts/run_discoverybench_persona_pilot.py \
  --output runs/discoverybench-pilot-01 --repeats 2 --run
```

Up to two arms execute concurrently, with `--parallel 2` cases per arm. For fewer
simultaneous calls use `--parallel 1`. The complete schedule is shuffled with a recorded order seed;
that seed controls scheduling, not model determinism. Each request may incur Azure
charges. Actual token usage is retained; dollar costs require Azure billing rates.

The four arms are:

| Arm | Researcher conditioning |
| --- | --- |
| `off` | Simulator present, approved facts unchanged, no persona identity |
| `reference` | All 56 attributes at medium |
| `statistics_low` | Only statistical inference changes from medium to low |
| `statistics_high` | Only statistical inference changes from medium to high |

The three enabled profiles share role and domain. Persona is private to the
researcher simulator, not inserted into actor or judge prompts. The
approach/result review protocol, budgets, grounding policy, and scoring contract
are held fixed across conditions.

Two studies × four arms × two repetitions gives **16 executions**, with eight
unique task/condition combinations. Repetitions do not enlarge the number of
independent scientific studies. The reference-vs-off contrast tests adding the
complete neutral profile; high-vs-low isolates one attribute within that profile.

## Inspect and interpret

Each output directory contains a private frozen-input plan, resolved arm configs,
runtime and API checks, immutable case directories, `comparison.json`,
`comparison.md`, and final `integrity.json`. The plan hashes public and private
prepared inputs, execution source files, the selected sandbox launcher, lockfiles,
and actor dependency RECORDs. Keep raw records under ignored `runs/`.

The summary reports native `final_score` (0–1), scored coverage, task/repetition
matched differences from persona off, wins/ties/losses, researcher requests, and
usage tokens. Failures are **unscored**, never inserted as zeros. The same control
within a repetition is shared by three contrasts, so those contrasts are correlated.
Report per-study outcomes before interpreting a pooled mean. Two studies cannot
support a general conclusion that persona helps; repeated actor and judge samples
still include generation and grading variability.

DiscoveryBench's native evaluator measures contextual, variable, and relation
agreement with a private reference hypothesis. It is an LLM grader, not a numerical
execution verifier. Execution receipts, artifacts, interaction observations, and
scientific scores must be inspected separately. A successful process exit alone
does not validate a scientific claim.

For expansion, keep related queries from the same study grouped, freeze source
facts and runtime across persona arms, add more distinct studies, and use the
[Phase 1 planner](science_personas/experiment_plan.md) for a broader preregistered
design. Do not select only profiles or tasks that improved in this pilot.

## Validation

```bash
PERSONASCIENCEBENCH_SOURCE_ROOT=external/sources .venv/bin/python -m pytest -q -rs
.venv/bin/python scripts/check_repository.py
git check-ignore .env
```

Optional external-benchmark tests skip when their sources or dependencies are not
installed. Azure transport tests use mock HTTP responses and never paid calls.
The pilot tests check single-attribute contrasts and correct paired accounting
when a control or persona arm lacks a score.
