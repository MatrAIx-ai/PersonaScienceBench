# Exploratory choice of four personas plus off

**Recommendation for a reduced future campaign: off + 155, 001, 004, 046.** This is a coverage-constrained descriptive selection from observed summaries, not proof of a uniquely most diverse population subset. No settings or jobs were changed.

## Data and experimental unit

Eight candidates have at least one completed Astra trial job. 148/155/089/001/127 have three trials; 003/004/046 have one. Behavior uses original complete traces; performance uses the available repaired endpoint within each trial and evaluator-compatible matching. These policies differ and the resulting feature blocks do not describe identical episode sets. Repeats average within task; uncertainty in the input summaries resamples studies within benchmark. Trials, metrics and persona pairs are not independent experimental units.

## Transparent selection rule

1. Force persona-off into every five-setting set. Exhaustively evaluate all four-persona combinations.
2. Performance features are paired changes on Bix, Discovery, EXP and SciConv. Exclude ASI from the primary selection because the new personas have only 2–5 matched cases under a compatible judge. Require at least 20 of the planned 40 distinct matched tasks on each remaining benchmark: 003 fails with six EXP cases. This is an analyst-chosen half-coverage guard, not a power calculation or preregistered rule. Threshold sensitivities from 10 to 30 are saved.
3. Behavior features are the six existing heatmap metrics: reply characters, exchanges, extra approach reviews, revision requests, clarification recall and precision. Use their existing equal-benchmark means. Features are correlated; equal feature weighting is a stated design choice. Do not duplicate benchmark performance by also adding super-family summaries of the same outcomes.
4. Divide each feature by a fixed persona-off task-level SD. Within each block, compute mean squared feature differences and normalize to unit average pairwise squared distance over eligible profiles including off. Combine behavior and performance with 50:50 weights, then take square roots. Off has a zero paired-effect vector.
5. Maximize the smallest of the ten pairwise distances among the five selected settings. This avoids spending slots on nearly overlapping profiles. Mean pairwise distance breaks ties. This objective describes separation of estimated mean profiles, not within-persona dispersion, semantic diversity or a validated latent trait.

The primary search compared 35 eligible subsets; the unrestricted search compared 70. With the baseline required, 148 can be partially redundant despite its clearly longer replies. The maximin rule deliberately values complementarity, rather than selecting the largest four individual changes from off.

## Sensitivity results

| Change | Winning four personas |
|---|---|
| behavior_weight_0.25 | 155, 001, 004, 046 |
| language_features_weight_0.25 | 155, 001, 004, 046 |
| behavior_weight_0.5 | 155, 001, 004, 046 |
| language_features_weight_0.5 | 155, 001, 004, 046 |
| behavior_weight_0.75 | 155, 001, 004, 046 |
| language_features_weight_0.75 | 155, 001, 004, 046 |
| omit_source_bixbench | 155, 001, 004, 046 |
| omit_source_discoverybench | 155, 001, 004, 046 |
| omit_source_expbench | 155, 001, 004, 046 |
| omit_source_sciconvbench | 155, 089, 004, 046 |
| omit_behavior_simulator_chars | 089, 001, 004, 046 |
| omit_behavior_exchanges | 155, 001, 004, 046 |
| omit_behavior_extra_plan_reviews | 155, 001, 004, 046 |
| omit_behavior_revision_requests | 155, 001, 004, 046 |
| omit_behavior_clarification_recall | 155, 001, 004, 046 |
| omit_behavior_clarification_precision | 155, 001, 004, 046 |
| minimum_matched_tasks_10 | 155, 001, 004, 046 |
| minimum_matched_tasks_16 | 155, 001, 004, 046 |
| minimum_matched_tasks_20 | 155, 001, 004, 046 |
| minimum_matched_tasks_24 | 155, 001, 004, 046 |
| minimum_matched_tasks_30 | 155, 001, 004, 046 |
| include_sparse_003 | 155, 001, 003, 046 |
| include_ASI | 155, 001, 004, 046 |
| three_trial_settings_only | 155, 089, 001, 127 |

Maximizing mean distance instead of minimum distance selects 155, 127, 004, 046. Thus “biggest diversity” depends on the stated objective. Weight and leave-one-feature checks are deterministic sensitivity analyses, not bootstrap selection probabilities.

## Selected profiles: observed changes

| Persona | Trials | Reply characters: Δ [95% CI] | SciConv performance: Δ pp [95% CI] |
|---|---:|---|---|
| 155 | 3 | -515.9 [-536.9, -496.4] | +0.0 [-6.7, 7.5] |
| 001 | 3 | -175.6 [-189.9, -162.1] | +5.0 [0.0, 10.8] |
| 004 | 1 | -59.0 [-79.9, -37.7] | +2.5 [-5.0, 12.5] |
| 046 | 1 | -109.3 [-129.2, -90.9] | -7.5 [-20.0, 5.0] |

All intervals above are pointwise, conditional on observed trials and based on studies/tasks, not a comparison of four independent persona populations. Character differences are language-dependent. 004’s revision-request change is −0.113 [−0.307, 0.018], so its apparent interaction difference is not established separately. 046’s SciConv change is −7.5 [−20.0, 5.0] pp; the negative estimate is not evidence of a confirmed decrease. Its Discovery estimate is +6.76 [2.43, 12.64] pp over 39 matched tasks clustered in studies. Full cell denominators remain in the source summaries.

## Statistical reporting boundary

The selection uses observed outcomes and analyst-chosen scaling, endpoints and weighting; it is exploratory and post hoc. Input pointwise CIs are not selection-adjusted. Subtracting different persona-minus-off summaries is a descriptive profile distance on differing observed task panels, not a direct matched pairwise treatment-effect estimate. Missingness, conditional repair and single-trial noise can change rankings. No p values or claims of statistical distinguishability are attached to the selection. A further common-task-panel analysis and joint study bootstrap of the entire selection pipeline would be needed to estimate selection stability.

For a future experiment, freeze this subset and rule before collecting fresh comparable trials, and complete trials 2–3 for 004/046 if repeat variation is part of the claim. Independent tasks/studies are needed to assess selection generalization; additional runs on the same tasks measure stochastic repeatability only. Keep the all-persona exploratory table in the paper/supplement so the selection is visible. Human realism and semantic collapse are not inferred.

Reproduce: `.venv/bin/python Experiment/shared/select_diverse_personas.py`. [Selection JSON](data/persona_selection/selection.json) · [All eligible subsets](data/persona_selection/ranked_subsets.csv).
