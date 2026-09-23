# Realistic researcher–actor benchmark (v3.1)

Historical implementation notes, migrated from the original EXP-Bench workspace.
Use [the current EXP-Bench guide](../adapters/expbench.md) for setup and paths.

This is a separate adaptation of EXP-Bench. The original pilot cards and saved
runs are preserved. It measures proposed design reference coverage separately from what
happens during implementation and execution. It does not reproduce the paper's
aggregate score or its original OpenHands deployment.

## Behavior

The actor uses OpenHands SDK 1.49.3, with inference through the existing
OpenRouter gateway. Defaults remain o3-mini for the actor and judge, Sonnet 5
for the researcher, 20 total actor steps, six researcher questions, and no dollar
caps. Models are checked against the live catalog before a live run. A configured
model's presence in a file does not establish current provider availability.

The actor receives a research question, brief context, an actual runtime
description, and a list of researcher topics. It can inspect repository files,
run commands, and ask a question about one topic. It submits its plan as natural
language in a single `plan` field; no variable-group schema is required.

The researcher retains its conversation but receives only the selected topic's
fact, plus its previous conversation. It decides relevance; the controller
publishes the approved fact verbatim or a fixed unknown answer. Generated prose
cannot introduce a new protocol or invented fact. Some source setup facts still
correspond to reference criteria, which is intentional: the study's requested
scope should be knowable. Decisions absent from the facts remain the actor's.
Actual hardware and dataset availability come from the runtime description,
not from claims about what hardware the source paper used.

In ordinary design mode, `submit_plan` saves an immutable initial checkpoint and
ends the episode. With `--continue-workflow`, that checkpoint preserves the plan,
facts disclosed so far and trace prefix. The **same OpenHands conversation** then
continues. `finish_experiment` records a final design, conclusion and optional
reproduction command. Failing to finish the workflow leaves the initial
checkpoint intact. Step exhaustion after the initial checkpoint still allows
its evaluation. API failures can leave a checkpoint saved but ungraded; they
are not silently converted to scientific failure scores.

## Evaluation

Each submitted checkpoint receives:

- **Reference coverage:** the released EXP-Bench design/conclusion prompt with
  the unmodified reference. The design is the submitted prose, without a
  generated variable-list conversion.
- **Integrity monitor:** the released prompt on the trace available at that
  checkpoint. Raw coverage and monitor-gated coverage are both retained.
- **Conclusion match:** reported only when a conclusion was submitted; this
  model judgment alone does not verify empirical validity.

Reference coverage is sampled three times by default. Each
sample and its explanation is saved, along with mean and population standard
deviation. These repeats measure observed grading variation, not a confidence
interval or a validation of the judge's accuracy. Monitor parsing has up to
three attempts; it is not independently sampled three times.

The released judge invocation now uses a system prompt followed by an empty
user message, JSON-object response mode, and up to three parsing attempts.
Transport failures are not retried. OpenRouter model deployment, medium
reasoning and the configured output allowance remain documented differences.
This fix also applies to future `original_control judge-saved` and `integrity`
runs. Previously saved scores and requests remain unchanged.

Unlike the paper's early gate, this diagnostic adaptation grades raw design
coverage even if the monitor rejects the trajectory, then reports the gated
coverage separately. No missing evaluation is silently excluded from the
reported counts: summaries show attempted, submitted, evaluated, scored and
missing counts with the averaging denominator named explicitly.

The added scientific-quality rubric was removed at the user's request in v3.1.
New runs make no quality-rubric calls and contain no quality scores. Historical
artifacts are retained as recorded. Reference prompts, grading repeats and the
integrity gate are unchanged.

`--validate-execution` replays the actor's reproduction command in a fresh
sandbox with a copy of its final workspace. It reports exit status, timeout and
output. `scientific_success` stays null: a successful command, especially a
trivial command, does not establish a scientifically valid experiment. A run
status of `completed` means the requested deliverables were submitted and
evaluated, not that the research question was successfully solved.

## Isolated runtime and repository preparation

Bubblewrap provides filesystem, PID and network isolation without Docker.
The actor sees system binaries/libraries, its writable task workspace and any
explicitly provisioned software/data mounts. It does not see the benchmark
directory, references, controller API keys, user home or Docker socket. There
is no fallback to arbitrary host execution. Network is disabled, so required
packages, datasets and model weights must be provisioned before a full run.

Exploratory commands have a maximum of 60 seconds each; implementation commands
up to 600 seconds, both within the actor episode's 40-minute soft wall-time
budget. The OpenHands iteration budget spans both stages. Reproduction
validation has a separate 40-minute timeout. These are execution bounds, not
dollar caps.

The preparation scripts select the latest default-branch commit at or before
2025-05-30 for each public repository and record its SHA. These are reproducible
snapshots, **not recovered original experiment revisions**. Code/configuration
files and licenses are staged; history, symlinks, README files, documents,
datasets, and results directories are omitted. The original task-specific
masked files are removed. Missing mask targets fail preparation. This staging
is stricter than the paper's masking and is recorded as a benchmark difference.
It does not prove every retained source/configuration file is free of answer
hints; real repository inspection remains part of the task and monitor scope.
Live runs verify the complete staged file inventory and hashes before copying it.

Provisioned environments and datasets are controlled by the operator, never
selected by the actor. In a workspace-map entry, optional `environment` is a
dedicated software environment bound read-only at `/opt/task-env`; its binaries
must function at that path. Optional `datasets` maps simple names to read-only
directories exposed as `/datasets/<name>`. Optional `gpu: true` binds NVIDIA
devices and requires `CUDA_VISIBLE_DEVICES` from a GPU allocation. GPU training
has not been validated merely by testing the CPU exploration runtime.

## Commands

Build versioned fact cards and fetch/stage repositories:

```bash
.venv/bin/python scripts/expbench/build_realistic_pilot.py
.venv/bin/python scripts/expbench/fetch_realistic_repositories.py
.venv/bin/python -m expbench.realistic prepare \
  --workspace-map data/realistic_pilot/source_repositories.json \
  --output data/realistic_pilot/staged
```

The preparer refuses to overwrite its output. The downloaded source metadata
allows completed downloads to be reused.

Run an offline integration smoke test. Model responses and scores are fixtures;
OpenHands and the isolated CPU commands are real:

```bash
.venv/bin/python -m expbench.realistic run --mode mock \
  --continue-workflow --validate-execution \
  --output runs/realistic-mock
```

Run the interactive live design benchmark with the key in the ignored `.env`:

```bash
.venv/bin/python -m expbench.realistic run --mode live --env-file .env \
  --workspace-map data/realistic_pilot/staged/workspaces.json \
  --output runs/realistic-live
```

For a matched no-simulator control, add `--input-mode original`. That supplies
the original question/method/instructions while keeping the new tools,
free-form output, resource configuration and judging the same. It is a matched
control for this adaptation, not an original-paper replication.

For the o3-mini simulator comparison, add
`--config configs/expbench/pilot-o3mini-simulator.toml`. Actor and judge settings, task
cards, prompts and step limits stay fixed. The researcher's output allowance is
4,096 tokens instead of Sonnet 5's 1,024, since o3-mini's reasoning shares that
allowance with its structured response. This compares configured model systems,
not equal token budgets. The researcher still selects the relevance of a single
approved fact; it does not generate the published answer freely. Episodes that
never ask the researcher do not test the simulator model.

The [completed o3-mini comparison](../../reports/expbench/o3mini_simulator_comparison_20260922.md)
contains all five task results and five matched answer comparisons. Four of the
five new actor episodes never queried the researcher, so the mean coverage
difference is not evidence of a simulator capability difference.

For implementation and execution, provision the runtime dependencies/data and
add `--continue-workflow --validate-execution`. Use `--task ID` for a single-task
check. `--judge-repeats`, `--seconds` and `--config` are explicit run settings.

## Artifacts

Each task records `public_input.json`, `runtime.json`, private task snapshot,
repository provenance, actor events, researcher history, API requests/responses,
execution logs, immutable `initial_design.json` and optional `final_design.json`.
Separate `initial_evaluation/` and `final_evaluation/` directories contain each
grade sample, rendered prompts, monitor response and summary. Reproduction
output, if requested and supplied, is under `reproduction/`. No judge feedback
is fed back to the actor. Private artifacts remain outside its mounted workspace.
