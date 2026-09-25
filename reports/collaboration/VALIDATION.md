# Collaboration extension validation

Validation was performed on September 25, 2026 UTC. These results concern software behavior and native verifier integration, not a new LLM benchmark experiment.

## Observed results

| Check | Result |
|---|---|
| New collaboration tests plus existing persona/information-boundary tests | **62 passed** |
| Entire enhanced suite | **130 passed, 7 failed, 6 setup errors, 24 skipped** |
| Entire untouched supplied science suite, same environment | **99 passed, the same 7 failures and 6 setup errors, 24 skipped** |
| New failing tests relative to the supplied baseline | **None observed** |
| Native ODE positive oracle control | **Reward 1; 12/12 native checks passed** |
| Native ODE deliberately wrong control | **Reward 0; 9 checks passed, 3 numerical-accuracy checks failed** |
| Python wheel build | Passed; packaged wheel includes the science catalog JSON |
| Paid model calls | **0** |
| New live actor benchmark run | **Not run** |
| Human domain review and semantic-judge calibration | **Pending** |

Machine-readable evidence: [validation.json](validation.json), [positive control receipt](positive_oracle_native_receipt.json), [negative control receipt](negative_native_receipt.json), and [source provenance](provenance.json).

## What the tests establish

The tests cover the 56-field closed vocabulary, invalid-profile rejection, role/ability independence, active-attribute projection, the PI matched contrast, legacy rendering and explicit persona-off behavior, prospectively disclosed review, a reserved last-action response, question budgets, bounded unknowns, rejection of actor-injected scoring fields, blinded judge packets, invalid/early/prose-only evidence rejection, nullable N/A scores, missing evidence, immutable sealing, symlink rejection, exact native public file hashes, and disclosure-ledger consistency.

The original actor interface was exercised through the new session without making model calls: an initial final received review feedback; the revised report was sealed by the original artifact code; the judge evidence matched the sealed report hash; a later actor-side edit did not change the sealed report.

These checks do not validate a language model's semantic judgment. In particular, merely supplying a report snapshot cannot prove that its scientific claims are true. Domain review, execution evidence where applicable, independent rubric calibration, and simulator fidelity evaluation remain necessary.

## Native verifier evidence

The source revision was `f55c14ea065243c8d094e02c0aa156d5fd22fdd4`. The task instruction, data, native checker, Dockerfile, `test.sh`, and test logic were not edited. The native adapter already present in the supplied repository was reused.

The tested verifier ran on Linux/arm64 through Docker server 29.5.3. Its image ID was `sha256:f13dda6b74436823af754a7f09f31800b6c8c8549238d15d63f1ebaefd7b5d88`. Native verification used no network access.

The positive control was constructed from private native reference data solely to test the verifier. It was not created by an evaluated scientific agent and must never be counted as an agent success. The negative control deliberately supplied an incorrect dynamical model with correctly shaped artifacts. Its failed checks were the standard rollout, stress rollout, and vector-field accuracy gates.

Private native equations, clean hidden trajectories, and the oracle control artifacts are not included in the distributable actor package. Receipts contain identities, hashes, test names, and results, not the private equations.

## Existing full-suite limitations

The untouched archive reproduced the same failures/errors under the test environment:

- Two EXP-Bench tests require source prompt files absent from the supplied archive.
- One EXP-Bench test imports optional actor dependencies, including `litellm`, that were not installed for the offline validation environment.
- Six runtime tests require Linux Bubblewrap, which is unavailable on the macOS host.
- Two assertions compare macOS `/var` paths with their resolved `/private/var` equivalents.
- Two assertions are stale relative to the supplied implementation: the selected-file count in a provisioning test and an expected error-message phrase in a Terminal test.
- Twenty-four tests skip when their external assets or runtime dependencies are unavailable.

These issues were recorded rather than changing unrelated scientific code or weakening tests. The full suite is therefore not claimed to be green. The new collaboration tests passed, and the failure-name comparison against the untouched snapshot is recorded in `validation.json`.

## Setup issues retained in the audit

An initial control-generation import wrote Python bytecode into the source directory, causing the existing source-integrity guard to reject it. The control generator now disables bytecode writes; the pinned source tree was restored before verification. A Docker build initially tried to update builder state in a non-writable home cache. Builder state was moved into the allowed work directory using `BUILDX_CONFIG`, and the unchanged Docker build then completed. These were setup errors, not model scientific failures, and no native score was imputed for them.

## Reproduction

Run the commands in [the worked example](../../docs/collaboration/ODE_WORKED_EXAMPLE.md). For the targeted regression set:

```bash
uv run --locked python -m pytest tests/collaboration tests/test_persona.py tests/test_core_boundaries.py -q
```

Use fresh output directories for each control or episode. Save the source lock, actual image identity, native receipts, and all model/runtime settings alongside any future scientific results.
