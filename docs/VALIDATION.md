# Release validation

The evaluation release was audited on Linux with Python 3.12.11. These are readiness checks, not scientific benchmark results.

## Verified

- A fresh controller virtual environment installed all locked runtime extras plus test dependencies.
- A separate actor environment installed all dependencies from `configs/actor-requirements.lock.txt` with hash verification.
- The Bubblewrap runtime probe passed on the execution host, with a separate network namespace and the configured actor interpreter.
- **30 offline tests passed**, covering frozen inputs, restoration guards, subset asset acquisition, incomplete-download failures, preparation checks before API access, and advanced CLI argument handling.
- The frozen selection has 200 distinct questions, 40 per source, with unchanged prompts for the four injected personas and persona-off as the fifth setting.
- Real restoration against already-downloaded assets verified 449 unique files, restored 1,160 metadata records, and staged 629 actor asset copies. Paths were rebased successfully and input hashes were retained. The temporary restored run was then removed.
- Python/JSON and shell syntax checks passed. Local Markdown file links resolved. A credential-pattern scan, including decompressed frozen inputs, found no matches.

## Boundaries

No paid model calls or full 1,000-episode campaign were run in this audit. Large benchmark assets were verified from existing pinned downloads rather than fetched again from scratch. Offline acquisition tests cover selection and failure handling; they do not guarantee continued availability of upstream hosts.

Each new host must still pass setup, asset restoration and runtime checks. Each provider account must support the selected model IDs and reasoning settings. Runtime code is identified by the release Git commit; the preparation bundle freezes task inputs, not historical runtime behavior or outcomes.

The source is on the `public-release` branch. Repository access remains private until a separate public distribution is created.
