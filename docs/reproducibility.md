# Reproducing the pipeline

Run these commands from a source checkout using Python 3.12. Editable installation
is the supported development layout: default configs and manifests live alongside
`pyproject.toml`. A standalone installed wheel is not the supported entry point.
No command below relies on the original cluster's absolute paths.

## 1. Controller environment

```bash
uv sync --locked --extra test --extra api --extra annotations
uv run --locked python -m pytest -q -rs
```

`uv.lock` locks controller dependencies and optional extras. Add `--extra actor`
to the sync command before using the OpenHands runner. To update dependencies,
edit `pyproject.toml`, run `uv lock`, and review/test the lock diff. Optional
Harbor execution is separate and is not included in this lock.

For source-backed tests, set the same source root used during acquisition:

```bash
PERSONASCIENCEBENCH_SOURCE_ROOT="$PWD/external/sources" \
  uv run --locked python -m pytest -q -rs
```

Without external sources, DiscoveryBench/BixBench source tests skip. Synthetic
ScienceAgentBench tests require the `annotations` extra. The scripted OpenHands
integration test requires the `actor` extra; its first import may be slow on
network filesystems. `-k 'not openhands_loop'` excludes that optional integration
check for a lightweight suite; record the exclusion when reporting validation.

## 2. Pinned source acquisition

```bash
uv run --locked python -m personasciencebench --source-root external/sources \
  fetch-sources --benchmarks discoverybench bixbench scienceagentbench terminal_bench_science
```

This checks out manifest-pinned commits and downloads checksum-pinned annotations
and the two small BixBench capsule archives. It neither executes upstream code
nor extracts reference notebooks into actor inputs. Repeating it verifies existing
files; it does not reset dirty/wrong-revision checkouts or replace mismatched data.
Internet/GitHub/Hugging Face access is needed for acquisition only.

DiscoveryBench and Terminal-Bench-Science pilot input files are in their source
checkouts. `prepare` extracts only allowlisted BixBench capsule data members.
ScienceAgentBench annotations are public, but its verified data/evaluator archive
must be acquired separately through the [upstream instructions](https://github.com/OSU-NLP-Group/ScienceAgentBench).
Access to that archive is a prerequisite; this repository does not bypass it.

Once you have `benchmark_verified.zip`:

```bash
uv run --locked python -m personasciencebench --source-root external/sources \
  provision-sab --archive /path/to/benchmark_verified.zip
```

This selectively extracts nine reviewed files into the private asset directory
and records their hashes. It does not deserialize pickles on the host or run
scientific code. The archive used for our pilot had SHA-256
`46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
No upstream published archive checksum was available; this is a measured local
provenance value. Different archives need renewed provenance review.

## 3. Prepare episodes

```bash
uv run --locked python -m personasciencebench --source-root external/sources \
  prepare --benchmarks discoverybench bixbench scienceagentbench \
  --output prepared/python-pilots
```

This selects exactly two reviewed tasks per requested benchmark. Omit
`scienceagentbench` if its archive is unavailable. A missing asset is a blocked
prerequisite, not a scientific failure. Preparation may report missing assets;
`run` requires every selected episode to be ready. Output directories must be new.

Each episode contains `actor/task.json`, allowlisted `actor/assets/`, and a private
`controller/` containing the complete episode and mount/hash records. The aggregate
`pilot_manifest.json` records absolute local locations. Prepared packages and run
records are local products: regenerate them after relocating the checkout or data;
do not treat copying a prepared directory to another machine as portable setup.

For the inherited workspace, `--source-root ../benchmarks` reuses already acquired
sources. The CLI retains that historical default, but these instructions always
specify the source root explicitly. Global options go before the subcommand.

## 4. Scientific execution environment

Use Linux with Bubblewrap installed as `/usr/bin/bwrap` or `/bin/bwrap` and user
and network namespaces enabled. Docker is not used by these three Python pilots.
Create the actor environment with the same base interpreter as the controller:

```bash
uv sync --locked --extra test --extra api --extra annotations --extra actor
uv run --locked python -m venv .actor-venv
uv pip sync --python .actor-venv/bin/python --require-hashes configs/actor-requirements.lock.txt
uv run --locked python -m personasciencebench check-runtime --actor-python .actor-venv
```

The last command runs an isolation probe, not a scientific task. If it fails,
resolve Bubblewrap/namespace permissions before running pilots. There is no host
execution fallback. Neither Docker nor GPUs are required for the selected
DiscoveryBench, BixBench or ScienceAgentBench tasks.

`configs/actor-requirements.txt` lists direct scientific dependencies; the adjacent
lock includes transitive versions and hashes. Regenerate it deliberately with:

```bash
uv pip compile configs/actor-requirements.txt --python-version 3.12 \
  --generate-hashes -o configs/actor-requirements.lock.txt
```

## 5. Models, credentials and personas

```bash
cp -n .env.example .env
```

Set `OPENROUTER_API_KEY` in `.env`, or export it in the controller environment.
Never place it in an actor workspace. Edit a copy of `configs/pilot.json` for your
run: its historical configuration uses `openai/gpt-6-luna`, effort `none`, for all
three model roles. Preflight checks availability; unavailable models or parameters
are errors, not silent model replacements. There are no automatic inference
retries or application dollar caps in this configuration. Native programmatic
graders do not call a judge LLM.

`configs/persona_example.json` demonstrates A–G defaults and a domain override.
See [persona configuration](personas.md) for task overrides and offline preview.
The `persona-grounded-v2` policy is a new condition relative to historical pilots.
Reproducing their broad workflow with current code does not promise identical
prompts, model outputs or scores. Preserve the code revision, resolved persona,
configuration and provider records when comparing new runs.

## 6. Execute and inspect

```bash
uv run --locked python -m personasciencebench run \
  --prepared prepared/python-pilots \
  --benchmarks discoverybench bixbench scienceagentbench \
  --actor-python .actor-venv --parallel 2 \
  --config configs/pilot.json --output runs/python-pilots-01
```

The runner supports 1–4 concurrent episodes and requires exactly two prepared
cases for each selected benchmark. This command makes paid model calls. Actor
iterations, question limits and disclosure limits are explicit in configuration.
Questions are optional; zero-question runs do not exercise persona interaction.

Inspect `summary.json` and each case's `result.json` / `evaluation.json` first.
Private controller records include `persona.private.json`, `actor_events.jsonl`,
`events.jsonl`, researcher history/audit after interaction, `submission.json`,
`submission_hashes.json`, sealed `submitted_artifacts/` and API call records.
ScienceAgentBench additionally records independent replay and native verification
under `controller/native_evaluation/`. Raw traces may contain reference answers;
keep them private and share only reviewed summaries.

To regrade saved DiscoveryBench/BixBench submissions with a changed model config:

```bash
uv run --locked python -m personasciencebench --source-root external/sources \
  regrade --run runs/discovery-bix-only \
  --config configs/pilot.json --output runs/discovery-bix-regraded
```

Use an existing run containing only those benchmarks; the generic regrade command
is not ScienceAgentBench's isolated replay pipeline. Regrading does not rerun the
actor. Native judge sampling omissions and response-format adaptations are logged
and versioned. Provider changes mean scores need not reproduce exactly.

## Terminal-Bench-Science and EXP-Bench

Terminal's two reviewed tasks can be acquired/catalogued/prepared with the same
commands, but `run` deliberately rejects Terminal: it needs an independent actor
runtime plus Harbor 0.21.0 and Docker for native verification. The bridge is
implemented but has no live validation on this host. These tasks specify zero
GPUs and retain their own native time/resource budgets. See the
[adapter contract](adapters/terminal_bench_science.md) before attempting execution.

EXP-Bench remains a separate, external design-only implementation. It is not
included in this checkout's manifest, CLI registry, lockfiles or reproduction
claims. Its migration is future work.
