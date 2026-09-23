# Terminal-Bench-Science adapter

The converter enumerates the 70 active release task packages under
`tasks/<domain>/<field>/<slug>/task.toml`. Archived tasks and deliberate CI failure
fixtures are excluded. Two reviewed researcher overlays are implemented against
repository revision `f55c14ea065243c8d094e02c0aa156d5fd22fdd4`:

| Native task | Actor work and submission | Researcher context | Local input data |
| --- | --- | --- | --- |
| `earth-sciences/geosciences/hbv-calibration-1` | Calibrate HBV and submit `/results/optimal_parameters.csv` plus reusable `/results/optimizer.R` | Motivation for difficult rainfall–runoff calibration; many local minima | Catchment CSV and HBVhelper package: nine files, approximately 1.27 MB |
| `mathematical-sciences/applied-mathematics/ode-law-discovery` | Discover compact equations and submit `/results/equations.json`, `/results/predictions.csv`, `/results/report.md` | Compact model discovery under noise; explicitly optional general advice about estimation, model complexity, and validation | Six data/metadata/checker files, approximately 0.49 MB |

The original instructions are preserved verbatim, including scientific methods,
dates, cutoffs, output schemas, and time limits. The source canary is retained.
No required criterion is concealed to force researcher questions. These tasks
have limited researcher-exclusive background; the overlay permits discussion
without claiming that dialogue is necessary for a correct solution.

## Knowledge and file boundaries

HBV context is one reviewed sentence of `task.toml`'s description. ODE context
and advice are exact reviewed sentences in the README's `Difficulty` section.
No README is exported whole. Reference-solution sections, validation evidence,
expected equations, hidden catchments, and verifier files remain private.
Each fact has a source revision, file digest, and exact section locator.

The asset manifest lists individual actor input files. The HBV package is a
permitted model implementation, not the task's optimization solution. The ODE
`check_submission.py` is the explicitly public parser/validation diagnostic. The
private native verifier remains the only source of final pass/fail. Instructions
retain every public requirement even if a researcher also discusses the topic.

## Independent actor execution and native evaluation

An external actor can use any compatible isolated runtime and the shared
researcher endpoint. Preserve the source environment's actual requirements:

| Task | Actor budget | Actor resources | Native verifier limit |
| --- | --- | --- | --- |
| HBV | 28,800 seconds | Four CPUs, 2,048 MB RAM, 10,240 MB storage, zero GPUs | 7,200 seconds; four CPUs and 2,048 MB RAM |
| ODE | 28,800 seconds | Four CPUs, 8,192 MB RAM, 10,240 MB storage, zero GPUs | 300 seconds |

Agent networking remains the native public-network setting. Both verifiers retain
the native separate-container, no-network configuration. Do not reuse EXP's
20-step design budget. A deliberately reduced budget must be labelled separately.

The controller seals all submitted files, then `evaluation_request()` writes a
private submission manifest and Harbor job configuration. Constructing this
request does not run Harbor, build an image, or call a model. The executable
`verify` bridge starts a single Harbor trial with `SealedSubmissionAgent`, which
only uploads the sealed files to their native absolute artifact paths. Harbor
then tears down that environment and invokes the original separate verifier.
The reference-solution/oracle agent is never selected.

HBV's native verifier re-executes the submitted optimizer on a private catchment
under its own unprivileged process. ODE's native verifier evaluates submitted
equations and artifacts against its protected references. Original task files,
verifier scripts, and cutoff calculations are unchanged. The adapter preserves
the native binary `reward`; it does not substitute an LLM judge or report a
successful process exit as scientific success.

The bridge requires **Harbor 0.21.0** and an importable PersonaScienceBench
installation in the same Python environment, plus working Docker. The pinned
wheel was inspected without installing/running its benchmark environments:
`harbor-0.21.0-py3-none-any.whl`, SHA-256
`c77d779a03f1a9e8ecb3c449e17f39a9728b82238832f1fd28632eb9426c0a21`.
Inspection covered `BaseAgent`, environment file uploads, job configuration, and
native trial-result fields. Runtime execution remains unverified until the
container backend and dependencies are available.

## Result integrity and limitations

The controller result directory must be outside actor/researcher mounts. Sealed
artifact hashes, native task-package digest, source revision, and runtime version
are recorded. Replay rejects changed artifacts. Verification rejects changed task
files, replaced replay-agent configurations, wrong native task names, and a
shared rather than separate verifier. Only controller-registered receipts are
accepted by `evaluate()`; score fields in an actor submission are ignored.

There is one attempt and no hidden retries. Missing submissions, absent reward
files, malformed results, and infrastructure exceptions remain explicit failures
without invented scientific scores. Results with native `reward=0` remain
scientific failures rather than infrastructure errors. Independent actor time,
resources, model usage, and researcher dialogue belong to the original episode
record; Harbor replay time is **evaluation overhead**, not a fresh actor run.

Input files are locally ready. Container images and the actual scientific
execution have not been tested during adapter construction. No external
scientific data download is needed for these two selected tasks, but image builds
still require the native package repositories.
