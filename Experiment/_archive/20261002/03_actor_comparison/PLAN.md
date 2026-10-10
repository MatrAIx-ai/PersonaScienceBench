# Model comparison: actor and simulator

> Withdrawn on 2026-10-01 at the user’s request. The incomplete Sol campaign is excluded from current results and public traces; raw runs are retained in `runs/_archive/20261001-incomplete-campaigns/`. Plans and counts below are historical.

## Question and confirmed scope

Compare the collaborating model pair while keeping the evaluator model fixed. The user selected GPT-5.6 Sol with low reasoning for both actor and researcher simulator, GPT-6 Astra low for the model judge, and the five personas that have three original Astra trial jobs ended: 148, 155, 089, 001, and 127, plus persona-off. This estimates the joint actor-and-simulator change, not the isolated actor effect proposed in the original paper plan.

## Design

Reuse the same 200 frozen tasks (40 per source) and profile text. Run three independent complete episodes for each of six conditions: 3,600 fresh episodes. Each trial comprises two 600-episode jobs: off/148/155, then 089/001/127. Every trial gets a new Sol-pair persona-off baseline; expansion conditions reference that matching baseline. No Astra trajectories are reused as Sol outcomes. Prepared task inputs, native score contracts, protocol limits, and token budgets are retained.

The scientific implementation is pinned to the same archived pre-merge protocol used by the queued Astra repairs, with the merged transient transport retry fixes. The Sol runtime additionally uses the role-aware coordinator and fixes native result collection to read only the exact harness-owned result file, avoiding actor-created files named `result.json`. This prevents the list-shaped artifact failure that interrupted an Astra coordinator. No scientific prompts or scoring formulas are changed for this fix. Historical ASI evaluator differences still require version-aware comparisons.

## Implementation and validation

- `code/prepare_sol.py` prepares isolated runtimes, frozen input references, manifests, and optionally submits the chain.
- `code/submit_sol.sh` requests 128 GB / 30 CPUs / 12 hours; each job uses 30 episode workers and one BLAS/OpenMP thread.
- `scripts/run_openai_first_pass.py` accepts separate actor and researcher model/reasoning overrides, checks all role models against the paired baseline, and can require existing prepared inputs.
- EXP accounting uses GPT-5.6 Sol input/output prices of $4/$20 per million tokens and retains Astra judge pricing. This is conservative accounting that does not apply cached-token discounts.
- Read-only model catalog access verified both exact model IDs. No paid smoke episodes were run.
- 23 offline tests passed, covering role isolation, native-result selection, and bounded transport retries. All six jobs' role arguments, selection hashes, and three-per-condition trial counts were checked.

## Status and schedule

Submitted jobs `1970253`–`1970258` sequentially after both Astra repair lane tails `1968758` and `1968759`. The five user-held Astra expansion jobs remain held. [Campaign manifest](data/gpt56sol-actor-simulator-low-prioritized.json) records commands, dependencies, profile hashes, runtime identity, and run directories. Results are pending.

Do not interpret a finished coordinator status as scientific correctness. Preserve infrastructure failures separately from missing submissions and scored zeroes. Compare matched tasks and report missingness and first-pass versus repair results separately. Cross-model statistical analysis is not yet implemented.

## Rate limits and sources

The official GPT-5.6 Sol page lists Tier 2 at 1M TPM, Tier 3 at 2M, Tier 4 at 4M, and Tier 5 at 40M. The current account's Sol-specific inference limit has not been measured; model catalog access does not establish that limit or independent capacity across model groups. Sol scheduling remains sequential and starts only after both repair lanes end to avoid overlapping Sol judge traffic with Astra repairs.

- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/guides/rate-limits

The user corrected concurrency to 30 workers before execution. The six original 20-worker submissions were cancelled and replaced; CPU and memory requests remain 30 CPUs and 128 GB. See [replacement audit](data/workers30_resubmission.json).
