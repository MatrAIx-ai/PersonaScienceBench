# Proposed evaluation and validation protocol

This is a study plan, not a report of completed model experiments. The current delivery establishes software behavior and native verifier wiring. It does not establish that simulated researchers are equivalent to real researchers or that the 56 dimensions form a validated psychological scale.

## Conditions and estimands

| Condition | Scientific input | Researcher | Main comparison |
|---|---|---|---|
| Native/no-interaction control | Original complete task | None | Cost and outcome impact of adding collaboration |
| Neutral collaboration | Same original complete task | Standardized neutral needs and same approved fact pool | Effect of persona-conditioned needs beyond dialogue alone |
| Persona collaboration | Same original complete task | Fixed persona and prospective disclosure | Adaptation to different researcher needs |
| Matched attribute contrast | Same task, same fact pool | Profiles differ in exactly one active attribute | Sensitivity to that assigned attribute under this protocol |
| Information redistribution, optional separate track | Some original context moved into reviewed researcher facts | Matched simulator | Effect of acquiring unavailable information; do not pool with unchanged-input results |

The implemented `--neutral` condition uses medium-level behavior and standard review needs. It is not a pure “no persona/no preferences” condition. The original `persona.enabled=false` option removes persona rendering in the old grounded simulator, which is another possible control; its disclosure and scoring policy must be matched and documented before comparison.

Do not interpret the six archetype bundles as isolated causal tests of individual traits. Only the two PI profiles form the included one-attribute contrast. Even that contrast identifies an effect within the chosen task/simulator protocol, not a universal property of real PIs.

## Suggested staged rollout

1. Review this one task with domain and evaluation specialists. Inspect every approved fact, disclosure, criterion, and private file boundary.
2. Calibrate semantic rubrics on adversarial examples before scoring model runs. Include successful execution, plausible false claims, valid refusal of invalid steering, no-question success, and missing evidence.
3. Run a small repeated ODE study to inspect failure modes. Do not claim cross-science generalization from one task.
4. Extend to an initial set of 12 tasks across distinct studies and domains, with two or more meaningful collaboration opportunities per task.
5. A planning example is 12 tasks × 6 personas × 3 actor seeds = 216 persona runs, plus 12 × 2 controls × 3 seeds = 72 control runs, total 288. These are proposed run counts, not a power calculation or a recommended minimum sample size.

Estimate required sample size after observing pilot variability and the smallest effect that matters. Keep compute feasibility, independent-study counts, and within-task correlation visible.

## Pairing and randomization

Use the same native data, allowed methods, environment, scientific wall-time allocation, added model-step policy, and information pool within a comparison. Pair actor seeds where the provider exposes a reproducible seed; otherwise record the lack of determinism and repeat runs. Randomize condition order and avoid systematic differences in provider load or temporal availability.

Hold researcher and judge model configurations fixed within an experiment. If testing simulator models, cross them as a declared factor. Deterministic-template and grounded-LLM researchers are distinct simulator conditions. Archive model IDs, provider routing, model versions where available, decoding parameters, tool versions, container image identity, prompt/catalog/rubric hashes, source revisions, and all exclusions.

Split related tasks by study or source repository when creating development and held-out sets. Several questions derived from the same dataset are not independent scientific studies. Prevent task-specific development traces and native reference data from entering actor training or prompt selection.

## Primary and secondary outcomes

The primary scientific outcome is the parent benchmark's native score with its original interpretation. For ODE, it is the binary native reward. Report the number of scientifically graded runs and distinguish zero reward from missing or invalid grading.

Interaction outcomes are per-criterion 0–3 scores, applicable opportunities, evidence coverage, and the optional conditional mean. Report preference adaptation and scientific claim calibration separately. Do not publish a combined “science plus collaboration” score that allows conversation quality to offset scientific error.

Researcher effort includes question calls, atomic requests, repeated requests, reply length, and, where measured with real people, time and perceived interruption burden. Automated character/call counts are proxies only. Predefine what constitutes a redundant question and annotate it against the information already available at that turn.

Useful exploratory views include scientific reward versus researcher effort, revision compliance among runs with a valid review opportunity, calibrated go/no-go among scientifically failed runs, and persona-conditioned behavior under a matched attribute contrast. Always show denominators.

## Semantic rubric calibration set

Construct at least these cases for each applicable criterion. Expected labels are authored calibration targets; have independent reviewers validate them before evaluating a model judge.

| Case | Intended distinction |
|---|---|
| Correct action with traceable evidence | Full satisfaction, not just a pleasant answer |
| Explicitly violated communicated need | Zero or low score with a post-disclosure citation |
| Acknowledgment with no change | Does not earn implementation credit |
| Artifact exists but contradicts the claim | Reference validity alone cannot establish satisfaction |
| Need never communicated or no relevant decision occurred | N/A, not failure or automatic success |
| Relevant opportunity but missing artifact/trace | Unobservable |
| Invalid researcher steering conflicts with original requirements | Evidence-based disagreement can be the correct collaboration behavior |
| Reviewer request arrives after termination without a response slot | Scheduling invalidity, not agent noncompliance |

For example, a report claiming “public validation passed, therefore the hidden tests pass and the mechanism is causal” should fail claim calibration even if it is polished. A report that accurately states no scientific execution was performed may be well calibrated but cannot earn native scientific success. The included demo illustrates that separation.

Use at least two independent reviewers on a stratified subset covering profiles, outcomes, and low/high rubric scores. Measure agreement on applicability separately from score agreement, inspect disagreements rather than averaging them away, and publish an adjudication rule. A project may preregister a target agreement threshold, but this release does not claim any threshold has been achieved.

## Simulator validation

Evaluate factual fidelity, knowledge-boundary compliance, persona consistency, opportunity coverage, repetition, and sensitivity to actor phrasing. Include requests for hidden answers, unsupported laboratory details, and contradictory preferences. Assess style variation without changing approved facts.

Ask actual researchers to review whether the simulated decisions and replies are plausible for the assigned profile, then compare with human collaboration on a small held-out subset if feasible. A model judge agreeing that a persona sounds like a PI is not sufficient evidence of realism. Avoid using the same model's self-assessment as the primary validation of its own simulation.

If a scientist simulator leaks a fact, invents study knowledge, or fails its disclosure schedule, record the invalid episode and report native scientific output separately. Do not silently drop invalid episodes from all denominators. Predefine whether and how a rerun is permitted; retain the original attempt and reason.

## Analysis and reporting

Report paired task-level differences where the design supports them. For uncertainty estimates, resample at the independent task/study level and preserve matched conditions within a resample; turns and repeated messages should not be treated as independent samples. Use stratified analyses for domain, task type, and applicability. Treat a large collection of attribute tests as exploratory unless hypotheses and multiplicity handling were specified beforehand.

Do not extrapolate all 56 attribute effects from the six starter profiles. Inspect whether dimensions are distinguishable in practice; merge, refine, or retire redundant dimensions based on evidence. Keep the catalog version fixed for a reported experiment, and rerun comparability checks when anchors or activation policies change.

Publish successes and failures, infrastructure/actor/simulator/judge status counts, missing-score reasons, native and interaction denominators, and the source/runtime changes relative to the parent benchmark. The new implementation is ready for this staged validation process; completed psychometric, human-realism, and model-performance results are not implied.
