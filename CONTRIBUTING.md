# Contributing

Use Python 3.12 and the checked-in lockfiles. Start with the
[README](README.md), [current status](docs/status.md), and
[reproduction guide](docs/reproducibility.md). The implementation is under
`src/personasciencebench/`; upstream checkouts and generated runs are external
inputs, not code to edit or vendor into this repository.

## Development checks

```bash
uv sync --locked --extra test --extra api --extra annotations
uv run --locked python -m pytest -q -rs
uv run --locked python scripts/check_repository.py
```

Install the `actor` extra for the optional scripted OpenHands integration test.
After fetching sources, set `PERSONASCIENCEBENCH_SOURCE_ROOT` as documented to
include source-backed tests. Report skips and runtime limitations explicitly.
Tests must not call paid models or execute scientific benchmark tasks implicitly.
CI runs synthetic/offline checks with no credentials or benchmark datasets.

## Adding or extending a benchmark

1. Pin the upstream revision, annotation/data hashes and acquisition paths in
   `manifests/sources.json`; retain upstream licensing and access conditions.
2. Implement the adapter contract in `adapters/base.py` and register it in
   `registry.py`. Enumeration is not permission to convert every task: explicitly
   review the public brief, permitted researcher facts and evaluator references.
3. Follow the [benchmark standards](docs/benchmark_standards.md). Essential task
   requirements remain public; simulator facts require provenance. Persona never
   grants reference-answer access.
4. Preserve the native evaluation contract. Label environment, prompt, parser,
   sampling and scoring changes as variants. Add appropriate synthetic boundary
   tests; source-backed checks must skip clearly when inputs are unavailable.
5. Update the adapter guide and `docs/status.md`. Add a report only after measured
   runs; do not convert missing infrastructure into zero scientific scores.

The current pilot runner requires exactly two selected tasks per benchmark. A
larger release needs an explicit selection/splitting interface and corresponding
runner changes; do not silently broaden pilot manifests.

## Changing shared behavior

- Update persona schema/rendering/policy versions when behavior changes. Preserve
  resolved profiles and keep old run receipts intact.
- Keep researcher memory episode-local and controller records outside actor mounts.
  Validate malformed model output and never bypass sandbox failures.
- Keep native scores separate from execution receipts and interaction measures.
- Update the lockfiles when dependency changes are intentional. Scientific runtime
  dependencies belong in the separate actor requirements and lock.
- Update current documentation in the same change. Historical reports/proposals
  should stay labelled historical; correct obsolete current-status claims with
  links to subsequent evidence.

Do not commit `.env`, model credentials, raw archives, prepared controller state,
private traces, virtual environments or upstream checkouts. Preserve existing
local work/results during cleanup. The repository checker catches common secret
formats and local-link mistakes in distributable text; it is not a comprehensive
security scanner.

Pull requests should explain the concrete change, relevant tests and material
limitations. This repository does not require a live paid benchmark run for
ordinary documentation or offline infrastructure changes.
