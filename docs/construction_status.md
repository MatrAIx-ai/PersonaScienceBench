# Historical adapter construction audit

For current implementation and execution status, see [status.md](status.md).
The tables below preserve the construction-stage snapshot, not the latest run status.

This is a **construction-time audit**, generated on 2026-09-23. Subsequent live
pilot outcomes are in [the pilot report](../reports/pilot_report.md). It covers the
four retained adapters, not the existing EXP-Bench design-only pilot. Live model runs
and scientific evaluation results belong in separate run reports. Model access
is not inferred from successful conversion or schema checks.

All four retained adapters load through `registry.load_adapter` with pinned source
revisions and annotation hashes verified. All eight retained episodes convert:
exactly two per benchmark. After the user supplied the verified ScienceAgentBench
archive, all eight episodes have their declared required files locally.
**No scientific scores were produced by
this audit.** Missing or unexecuted outcomes are not assigned zero.

The measured inventory is in
[construction_inventory.json](../reports/construction_inventory.json). That
record includes the exact episode IDs, study groups, source/evaluator versions,
missing assets, and logical mount-path audit.

## Selected episodes

| Benchmark | Native task ID | Native domain | Input data | Execution and grading status |
| --- | --- | --- | --- | --- |
| DiscoveryBench | `test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0` | engineering | Ready: one input asset | First test group; native hypothesis grader constructed, live analysis/judge execution pending |
| DiscoveryBench | `test/nls_incarceration/metadata_1.json/0/0` | sociology | Ready: one input asset | First test group; native hypothesis grader constructed, live analysis/judge execution pending |
| BixBench | `bix-10-q2` | computational_biology | Ready: six input assets | First test group; native open-ended LLM grader constructed, live analysis/judge execution pending |
| BixBench | `bix-8-q2` | computational_biology | Ready: two input assets | First test group; native open-ended LLM grader constructed, live analysis/judge execution pending |
| ScienceAgentBench | `22` | Computational Chemistry | Ready: two input files | Verified native evaluator and reference provisioned; isolated replay/native grading bridge prepared |
| ScienceAgentBench | `45` | Psychology and Cognitive science | Ready: one input file | Verified native evaluator and reference provisioned; isolated replay/native grading bridge prepared |
| Terminal-Bench-Science | `earth-sciences/geosciences/hbv-calibration-1` | earth sciences | Ready: nine input files | Harbor/native separate-verifier bridge constructed; Docker/images/runtime verification pending |
| Terminal-Bench-Science | `mathematical-sciences/applied-mathematics/ode-law-discovery` | mathematical-sciences | Ready: six input files | Harbor/native separate-verifier bridge constructed; Docker/images/runtime verification pending |

DiscoveryBench and BixBench provide the **first four data-ready tests**.
Terminal-Bench-Science adds two data-ready tasks once its native execution backend
is prepared. Availability of those files does not establish scientific correctness
or a working container environment.

## Concrete blockers

- **ScienceAgentBench acquisition resolved:** the user supplied
  `benchmark_verified.zip` after the upstream endpoint returned HTTP 401. Nine
  selected files were safely extracted, hashed, and matched to the pinned task
  contracts. Three public data pickles and one private native reference pickle
  loaded successfully inside Bubblewrap. The account still cannot access Docker;
  the pilot uses an explicitly versioned Bubblewrap adaptation with unchanged
  native `eval()` functions and separate public program/private grader workspaces.
  Model-backed pilot outcomes are recorded in [the SAB report](../reports/sab_pilot_report.md).
  Both subsequent live cases completed: two valid programs, one of two native
  task successes. Those measured outcomes remain separate from this asset audit.
- **Terminal-Bench-Science:** prepare Harbor 0.21.0 and a working Docker backend,
  then build/run the native task environments and separate verifiers. Its two
  tasks retain the original 28,800-second actor budget; EXP's 20-step design limit
  is not applied. The Harbor wheel was inspected, but no native scientific trial
  was run by the construction audit.
  A subsequent host check confirmed Docker daemon access is denied, including
  outside the outer tool sandbox; no native Terminal trial could be started.

## Retained inventory and boundary audit

The verified source inventories are 264 DiscoveryBench queries, 205 BixBench
questions, 102 ScienceAgentBench verified tasks, and 70 active
Terminal-Bench-Science packages. These
are source enumeration counts, not claims that every source task has a reviewed
interactive conversion.

All eight retained episodes passed the logical actor-path audit: no duplicate paths, no
parent/child mount overlaps, and no traversal/root targets. Existing required
assets had no declared hash mismatches or rejected symlinks. Reusing `/results`
or `/data` across separate episode sandboxes is expected; the audit checks
overlap within each episode. Private references and researcher fact contents
are intentionally absent from this report.
