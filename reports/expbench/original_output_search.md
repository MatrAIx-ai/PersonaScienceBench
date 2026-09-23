# Search for original paper outputs

Date: 2026-09-22

Purpose: obtain the paper's original OpenHands + o3-mini outputs and per-task scores for our five pilot tasks, then regrade the identical outputs with the released judge. This separates changes in grading from changes in generated designs. No paid inference was performed for this search.

## Result

No matching original outputs were found in the public sources inspected. This is a bounded search, not proof that the artifacts have never been released. The exact matched comparison has not been run.

## Sources inspected

- [Curie](https://github.com/Just-Curieous/Curie), main commit `db1b1f56159b591515f77e03c55bf473d5c1c201`: complete recursive tree, releases, and available issue metadata. Also inspected trees of `expbench`, `exp_bench_int`, `dataset`, `bench_misc`, `evaluate-curie`, `anonymous`, `pat_backup`, `pat_backup_2`, `pat_backup_3`, and `better_log`.
- The `evaluate-curie` branch contains evaluation artifacts for Curie + Azure GPT-4o on NeurIPS paper 93022. These do not match the requested agent, model, or tasks and cannot serve as the matched control.
- [Separate EXP-Bench repository](https://github.com/Just-Curieous/EXP-Bench), main commit `401573342845fe24963d4384e6849d53f046dd23`: complete recursive tree (1,234 files), branch/release/issue metadata. Evaluation code and dataset construction artifacts are present; no matching o3-mini evaluation output files were identified.
- [Hugging Face dataset](https://huggingface.co/datasets/Just-Curieous/EXP-Bench), commit `5b35c4c717a9f7ddd6a255b94a462f8ca51b0668`: repository contains the dataset CSV, README and attributes; the dataset card says the leaderboard is to be released. Community metadata did not provide a matching run archive.
- Official website, EXP-Bench blog, organization repository listing, and the `visualize-log-tool` repository tree; no matching artifact download identified.

Public API responses, source URLs, and status codes are retained in `data/original_output_search/`. GitHub issues and public web searches were not an exhaustive audit of every historical commit or external archive.

## Required matched tasks

| Task | Dataset identifier |
| --- | --- |
| JaxMARL | `neurips2024/97649/0` |
| QuaRot | `neurips2024/94328/5` |
| CycleNet | `neurips2024/94391/7` |
| MogaNet | `iclr2024/18447/7` |
| SineNet | `iclr2024/18865/4` |

## Comparison once artifacts are available

1. Match dataset revision, task identity, run iteration, and model configuration to the original paper.
2. Preserve the original extracted design and conclusion exactly; do not regenerate or reserialize them through our design schema.
3. Replay the released joint judge on those outputs with the original reference and record raw design scores separately from integrity-gated scores.
4. Replay the integrity monitor when the original trajectory is available. Otherwise compare against the saved monitor decision and label that limitation.
5. Compare per-task original and replayed grades; use repeated grading to measure judge variability if discrepancies appear.

Saved-output judging needs API access and artifacts, not GPU experiment execution. Matching a model name alone does not establish identical model deployment or inference settings. Our five selected tasks also cannot be compared directly with a paper-wide aggregate as though they were the same sample.

## Draft artifact request — not sent

Hello EXP-Bench authors,

We are validating the experiment-design evaluation against the original results reported for OpenHands with o3-mini in arXiv:2505.24785. Could you share the original outputs and per-task grades for `neurips2024/97649/0`, `neurips2024/94328/5`, `neurips2024/94391/7`, `iclr2024/18447/7`, and `iclr2024/18865/4`, if these tasks were included in that evaluation?

Ideally we would need the original `eval_gen.json` files (including extracted designs and conclusions), `eval_judge.json` files, integrity-monitor decisions and input trajectories, and the dataset revision and evaluation configuration. Please include run iterations, judge/actor model identifiers, provider, reasoning settings, and decoding parameters where available. An existing archive link would be sufficient.

We want to regrade the identical saved outputs to distinguish grading differences from differences in agent behavior. Thank you.
