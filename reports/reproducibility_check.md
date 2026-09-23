# Reproduction and repository cleanup validation

Date: 2026-09-23. This is infrastructure/developer validation, not a new scientific
benchmark run. No paid model calls or scientific task executions were made.

## Verified from fresh environments

- Resolved `uv.lock` using uv 0.11.26 and installed the project editable into a
  fresh Python 3.12.11 controller environment, initially with test/API/annotation
  extras and then with the pinned OpenHands 1.49.3 extra.
- Installed a separate scientific environment using
  `configs/actor-requirements.lock.txt` with required package hashes.
- Downloaded new DiscoveryBench/BixBench checkouts and public assets using
  `fetch-sources`, with pinned commit and checksum validation.
- Prepared four episodes from those fresh downloads: **4/4 assets ready** and no
  scientific runs started. Their 19 source-backed adapter tests passed.
- Verified existing pins/annotations for all four retained adapters and enumerated
  source inventories of 264, 205, 102 and 70 units respectively. These counts are
  not counts of reviewed interactive conversions.
- Ran the final suite in the locked controller environment with acquired sources:
  **129 tests passed, zero skipped**. Five warnings come from the pinned upstream
  BixBench Pydantic configuration, which is intentionally unchanged.
- The scripted OpenHands integration test passed; its model responses are fixtures.
- The newly installed actor environment passed the actual Bubblewrap isolation
  probe and imported numpy, pandas, scipy, statsmodels, openpyxl and patsy inside
  the sandbox. No scientific analysis was executed.
- Local documentation links and common credential patterns passed the repository
  checker. The check deliberately excludes ignored credentials and private runs.

## Fix discovered during validation

A virtual environment under `/tmp` was hidden by the sandbox's later temporary
filesystem mount. The runtime now creates its isolated temporary filesystem
before mounting the read-only Python environment. A regression test and a real
fresh-environment isolation probe passed after the change.

The outer execution-tool sandbox denies network-namespace initialization. The
host-level probe succeeded outside that outer wrapper; a developer still needs
OS permission to create the namespaces required by Bubblewrap.

## Scope and remaining prerequisites

The README now points to current status, reproduction, persona, protocol and
adapter documentation. Historical selection/implementation proposals live under
`docs/design/`. Prior scientific reports and private local artifacts are retained.
The offline CI workflow is added, but remote GitHub Actions execution has not
been observed during this local validation. These checks were completed before publication.

ScienceAgentBench still requires a separately obtained verified archive. Its
existing live pilot evidence is in [the SAB report](sab_pilot_report.md); this
cleanup did not rerun it. Terminal's Docker/Harbor execution is still unvalidated
on this host. At the time of this check EXP-Bench was external; it has subsequently been
migrated. See [the EXP-Bench guide](../docs/adapters/expbench.md). Live persona effects
and future provider/model availability are not established by these checks.

Dependency locks describe the current reproducible development/runtime setup;
they do not retroactively freeze the environments or prompts of earlier model
runs, or guarantee deterministic model output.
