# Five-case Luna baseline

This run uses five distinct task IDs per benchmark, GPT-6 Luna
(`openai/gpt-6-luna`, reasoning effort `none`) for actor, simulator, and
model-based judges, with no persona styling. The simulator remains available
for approved study facts. ScienceAgentBench and Terminal-Bench-Science retain
native programmatic grading; EXP-Bench remains a design-only track.

Configurations:

- `configs/luna-no-persona-five.json`: Python and Terminal cases.
- `configs/expbench/luna-no-persona.toml`: EXP-Bench cases.
- `configs/luna-five-selection.json`: five reviewed cases each from
  DiscoveryBench, BixBench, and ScienceAgentBench.
- `configs/luna-five-terminal-selection.json`: five reviewed Terminal cases.

The original two-case defaults remain available. Explicit selection does not
allow conversion of unreviewed task IDs. The additional BixBench archives are
pinned by dataset revision and content hash in `manifests/sources.json`.
ScienceAgentBench's additional private evaluator dependencies are explicitly
allowlisted in `scienceagentbench_provision.py`.

## Execution

After pinned source acquisition, archive provisioning, and environment setup:

```bash
python -m personasciencebench --source-root external/sources prepare \
  --benchmarks discoverybench bixbench scienceagentbench \
  --selection configs/luna-five-selection.json --cases-per-benchmark 5 \
  --output prepared/luna-five-python
python -m personasciencebench run \
  --prepared prepared/luna-five-python \
  --benchmarks discoverybench bixbench scienceagentbench \
  --actor-python .actor-venv --config configs/luna-no-persona-five.json \
  --env-file .env --parallel 15 --output runs/luna-baseline/python

python -m expbench.realistic run --mode live \
  --config configs/expbench/luna-no-persona.toml \
  --workspace-map data/realistic_pilot/staged-luna/workspaces.json \
  --env-file .env --parallel 5 --output runs/luna-baseline/expbench

python -m personasciencebench --source-root external/sources prepare \
  --benchmarks terminal_bench_science \
  --selection configs/luna-five-terminal-selection.json --cases-per-benchmark 5 \
  --output prepared/luna-five-terminal
python -m personasciencebench.terminal_runner \
  --prepared prepared/luna-five-terminal --config configs/luna-no-persona-five.json \
  --env-file .env --parallel 5 --verifier-backend native-docker \
  --output runs/luna-baseline/terminal
```

Run the three independent commands concurrently when all inputs are ready.
Each runner schedules its cases concurrently. Actor, simulator, and grader calls
within an individual episode retain their necessary causal ordering.

Terminal requires Docker. The default Harbor backend additionally requires Harbor
0.21.0 and Docker Compose. On this host, use `--verifier-backend native-docker`:
Harbor’s network sidecar requires nftables FIB support absent from the kernel.
The explicit alternative runs the unchanged native `tests/Dockerfile` and
`tests/test.sh` in a separate Docker container with `--network none`, recording
`terminal-native-separate-docker-network-none-v1`. The runner builds
the unchanged native actor images from the public environment directories and
seals submissions before passing them to the selected verifier. The actor network
is disabled and its OpenHands loop has the configured 20-step limit; both are
recorded adaptations. Native container CPU/memory allocations and the native
actor wall-time ceiling are retained. Exact native artifact paths are copied to
workspace-relative files for sealed submission; grader references never enter
actor containers.

For a local Bubblewrap installation, set `PERSONASCIENCEBENCH_BWRAP` to its
executable path for Python cases, and add its directory to `PATH` for EXP-Bench.
The scientific environment must include NetCDF/HDF5 readers for SAB instance 87;
the original two-case scientific lock does not supply these dependencies.
`configs/luna-netcdf-requirements.lock.txt` records the expanded environment used
for the replacement climate case.

## Persona-disabled condition

`"persona": {"enabled": false}` bypasses persona routing and emits no identity
or style prompt. The grounding check receives no persona preferences. Each
controller records the disabled condition and `no-persona-grounded-v1` policy.
The EXP-Bench scoped simulator publishes only approved fact text. Its optional
shared persona renderer is inactive in this condition, and the run manifest
records `persona_enabled: false`.

No additional test suite is required for this requested batch. The live case
records are the validation evidence. Infrastructure attempts and replacements
must remain visible; do not turn unavailable execution into a scientific zero.
