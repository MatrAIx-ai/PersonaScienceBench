# DeepSeek cost pilot (2026-10-03)

Current live model: `deepseek/deepseek-v4.1-flash` through OpenRouter; actor, researcher simulator and judge use low reasoning. No production inference or benchmark code was changed. The local `.env` holds the credential and is Git-ignored.

Live job 2030882: `runs/deepseek-live-cost-pilot-20261003/`. The manifest records 25 episodes, full commands, source-code hashes and selection: one fixed-seed randomly selected common trial-1 question per source, each with off / 155 / 001 / 003 / 046. This is a small cost pilot, not a performance evaluation or the full 1,000-episode campaign. The five questions have complete historical records across all settings, so the sample can favor easier/completable tasks.

The existing benchmark runners receive only new run configurations. Original output caps and protocol settings from `configs/full_persona_v2` are retained. Frozen task packages are reused; task preparation does not invoke a model. EXP accounting caps use public catalog prices, but the cost report sums actual OpenRouter `usage.cost`, not the conservative internal EXP budget ledger.

Run `.venv/bin/python Experiment/shared/deepseek_cost_pilot/summarize_live.py` to refresh measured costs. For a complete, accounted 25-episode pilot, scale total and role costs by 40 for 200 questions × five settings × one trial. This is a point budget extrapolation with substantial task and trajectory uncertainty, not a confidence interval. Do not extrapolate partial or infrastructure-failed episodes as complete costs.

The initial exact `:batch` request was rejected by the synchronous endpoint (HTTP 404). A single asynchronous access probe was then submitted, but the user selected the ordinary model. A 351-request fixed-history replay was prepared locally but **never submitted**. Its payload contains private prompts under the ignored `runs/` directory. No replay output is treated as a fresh agent trajectory.

`estimate_historical.py` and `historical_projection.json` contain the earlier *batch-price* estimate based on 852 completed Astra trial-1 episodes; that estimate is not the current model's measured cost. The live access probe succeeded with a forced tool call: 296 input / 56 output tokens and reported cost $0.00006496. A one-call probe is not representative of episode cost.

## Runtime update

The first SciConv episode hit the original 4,096-token judge output cap and ended with `judge: incomplete completion (length)`. The original trace is preserved. Judge caps for future pilot processes were increased to 16,384 by configuration only; first-group processes already running retain their loaded configurations. SciConv off is retried as job 2031164 into `attempt-2/`. The cost collector reports earlier failed-attempt spend separately and requires complete native outcomes before producing the full projection. It does not classify a zero process exit code as proof of a valid native outcome.

Cost-report job 2030998 depends on both 2030882 and 2031164. No additional campaign is submitted by the reporter. Final machine-readable costs are written to `runs/deepseek-live-cost-pilot-20261003/cost_summary.json`.
