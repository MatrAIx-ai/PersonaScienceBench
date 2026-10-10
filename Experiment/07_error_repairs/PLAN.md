# Error and missing-submission repair pass

> Operational provenance only. Retired launchers were moved to [the dated archive](../_archive/20261002/07_error_repairs/code/) on 2026-10-02. Status and data stay here because current offline analyses read them. Historical commands below describe their original locations.

After current job 1966129 terminates, run one repair pass with at most two concurrent jobs over the seven Astra runs already started. Prioritize trials 1–3 for personas 089/001/127, then original off/148/155 trials 1–3, then expansion group 046/003/004 trial 1. The five unstarted expansion jobs remain held until explicitly resumed.

## Implementation

`code/submit.sh` requests 128 GB, 30 CPUs, 20 workers, and a 12-hour allocation. `code/run_repair.py` locks the source coordinator during initialization, snapshots all episode states, copies frozen selection/configuration, and references prepared inputs and previous attempt directories. Each repair uses a separate `runs/repair-1-*` directory. Source trials and their original missing-submission outcomes are retained.

The coordinator's `--retry-infrastructure --retry-missing` flags rerun errors, missing submissions, and interrupted episodes. Successful outcomes, including scored zeroes, are reused without inference. Missing state files are treated as incomplete work. Each target receives one new episode attempt; existing bounded per-request 429 retries still apply. No shared rate limiter has been added. Lower concurrency reduces load but does not guarantee freedom from rate limits.

## Provenance and interpretation

`status.json` contains the actual job chain and held expansion IDs. Each repair run writes `repair_snapshot.json`, `original_results_snapshot.json`, and `repair_summary.json`, plus normal per-attempt traces. The repair target list is frozen at job start, after prior dependencies finish; live source progress files are not used to choose targets.

These are conditional additional attempts, not independent new trials. Report original first-attempt results and repair outcomes separately, especially missing-submission retries, to avoid hiding scientific failures. Runtime code/evaluator repairs present at launch can differ from early original attempts and must remain documented. Native scoring, model, reasoning, and token budgets are not changed by this submission. Judge-only errors are being rerun as whole episodes in this pass, not regraded from sealed submissions; preserve the original submissions for any later controlled regrading analysis.

## Status and results

Seven repair jobs submitted after 1966129; the user authorized two concurrent 20-worker repair jobs on 2026-09-30. Repair results are in progress. Five later expansions held. All 42 source condition/configuration combinations match the current coordinator-generated settings; Python and shell syntax checks passed. Remaining token-cap or schema errors require separate diagnosis rather than unlimited resampling.

## Runtime pin for the GitHub merge

GitHub commit `92036dd` changes scientific persona-control defaults and prompt behavior. To preserve the already queued repair protocol, those jobs use an archived runtime from local commit `de6d85f`, with only `src/personasciencebench/openai_transport.py` overlaid from `92036dd` for the requested upstream transient-error retry fixes. The runtime path and every source/configuration hash are recorded in `status.json` and the ignored runtime directory’s `runtime_manifest.json`. New main-branch work uses the merged upstream implementation. Queued repairs were temporarily held during integration and then released with their original dependencies.

## Two-job concurrency update

The two sequential lanes are `1968753 → 1968755 → 1968757 → 1968759` and `1968754 → 1968756 → 1968758`. Each job retains 20 workers, 30 CPUs, and 128 GB; at most 40 repair workers run concurrently. Job 1968754 can now start alongside 1968753. Dependencies use `afterany`. The Sol campaign waits for both lane tails (1968758 and 1968759), then runs sequentially with 30 workers per job. Existing expansion holds remain in place. Scheduler changes are recorded in `data/concurrency_two.json`.
