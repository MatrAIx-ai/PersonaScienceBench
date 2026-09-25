# Phase 1 correction: validation

Measured on September 25, 2026 UTC. These results belong to the corrected
private-system-only simulator release. They supersede the previous persona-only
validation counts and ODE preview. See the [requirement audit](COMPLIANCE.md).

## Measured checks

| Check | Result |
|---|---|
| Full Linux suite with locked lightweight CI dependencies | **177 passed, 27 skipped, 0 failures/errors** |
| Separate real OpenHands SDK smoke job | **2 passed, 0 skipped** |
| Targeted macOS persona/Phase 1/boundary tests | **94 passed** |
| New Phase 1 cases within the full suite | **32 passed** |
| Existing science-persona regression cases | **31 passed** |
| Original protected task/eval/runtime/configuration files | **83 byte-identical files** |
| Researcher file | **Matches the explicitly reviewed Phase 1 simulator correction** |
| ODE source integrity | **Original instruction and 20 native source/license file hashes verified** |
| ODE injection preview | **12 arms including off: equal non-persona inputs; identity differs** |
| Wheel build and isolated package import | **Passed; 56 attributes, Phase 1 planner and observations included** |
| Model calls / native scientific executions | **0 / 0** |
| Actual 50-task cohort / 600 executed episodes | **Not supplied / not executed** |
| Hosted GitHub Actions rerun / human calibration | **Not performed** |

Evidence: [machine-readable results](validation.json), [scope audit](scope_audit.json),
[ODE comparison](ode_injection_comparison.json), [provenance](provenance.json),
[Linux test log](offline-pytest.log), [SDK log](sdk-smoke.log), and
[macOS test log](targeted-macos.log).

## What is established

The shared simulator now uses the same base response policy and policy version
for on/off. Off removes only the private system identity. The grounding checker
receives no extra persona payload. Matched scripted requests verify identical
facts, common messages, support checks, question limits and call sequence after
identity removal. Existing actor boundary and first-valid-final tests still pass.
No original task adapter, evaluator, actor, session, runtime or runner is edited.

The Phase 1 planner generates each treatment from a common reference by one
field/level change and rejects malformed, duplicate, unknown and unchanged
contrasts. A synthetic 50-task fixture yields 600 manifest entries, all with
matched per-task fingerprints and persona-only config differences. Tests detect
drift in task, data, environment, execution settings, scientific facts, gold,
verifier, Episode, config, generated configs and the manifest. They reject an
incomplete/oversized cohort, duplicate source tasks, unsupported EXP runners,
and the superseded collaboration metadata. The source hashes and identity hashes
also record the implementation used to build a private plan.

The observations helper leaves the native evaluation file unchanged and exports
its result values without rescaling or recomputing a pass/fail decision. It counts
existing interaction events and preserves zero-question cases. These descriptive
counts are not an interaction quality score or a scientific grader.

The ODE evidence uses a fresh Episode from the unchanged original adapter, with
no prior collaboration addendum. Source files are checked against the previously
recorded native source lock. The actual Researcher request is captured before
inference for every example arm, including off. The task is neither solved nor
scientifically re-evaluated by this check.

## What is not established

Tests ran in Linux/arm64 containers with Python 3.12.14 and uv 0.11.26, using the
existing lockfile. The two test jobs had networking disabled after dependency
setup. The SDK job uses OpenHands SDK 1.49.3 with scripted responses; it is not a
live model experiment. The 27 skips cover unavailable external benchmark assets
and optional SDK integration in the lightweight job. Skips are not scientific
passes. Runtime tests do not establish a full native scientific execution.

A file fingerprint proves only equality of the declared local artifacts. It
cannot certify unlisted dependencies, runtime hardware/container identity, remote
model stability, effective launcher settings or the semantic truth of model prose.
The actual cohort, native assets/runtimes and launch receipts remain necessary.
Separate EXP simulator implementations are deliberately not claimed as covered.

No human fidelity calibration, population validity, statistical effect or robust
scientific-performance change has been demonstrated. The catalog's behavior
anchors are authored operational choices. The 12-arm allocation is a proposal;
the empty cohort template is not a completed 50-task dataset. A null effect is
valid and does not justify adding Phase 2 interactions to this experiment.

## Reproduce

Follow [the CI setup](../../docs/reproducibility.md). Run the full Linux suite and
scope audit; the SDK job separately installs the existing actor extra.

```bash
uv run --locked python -m pytest -q -rs
uv run --locked python scripts/check_persona_scope.py
uv run --locked python scripts/check_repository.py
```

The scope audit pins 83 original files and the reviewed simulator correction
[diff](../../manifests/researcher_phase1.patch). It is not TaskEval. No test result
in this report changes the scientific benchmark's answer or pass/fail rule.
