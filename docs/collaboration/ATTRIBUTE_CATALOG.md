# Science attribute catalog

This catalog defines 56 attributes in eight groups. Role and domain are metadata and are not counted. All levels preserve scientific integrity. These are authored design anchors, not a psychometrically validated scale.

Each entry contains researcher behavior, an activation opportunity, an agent adaptation target, an explicit counterexample, a 0–3 evidence rubric, and a separate simulator-fidelity rubric. The JSON catalog is the canonical source.

## Scientific expertise

### `domain_theory`

A stable researcher characteristic governing domain theory; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Requests definitions of field-specific concepts. |
| medium | Uses standard domain concepts; asks about unfamiliar subfields. |
| high | Checks domain assumptions and distinguishes competing mechanisms. |

**Opportunity:** A domain-specific assumption affects interpretation.

**Expected agent adaptation:** Match explanations to demonstrated domain understanding and state assumptions.

**Failure example:** Uses unexplained domain jargon after an explicit request for definitions.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `methodological_breadth`

A stable researcher characteristic governing methodological breadth; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Recognizes one familiar method and asks about alternatives. |
| medium | Compares established methods within one family. |
| high | Compares assumptions across several relevant method families. |

**Opportunity:** Two scientifically valid method families are available.

**Expected agent adaptation:** Explain the relevant tradeoff without assuming the researcher knows every method.

**Failure example:** Treats a job title as evidence of mastery of every method.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `statistical_inference`

A stable researcher characteristic governing statistical inference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs an explanation of estimates, uncertainty, and sampling. |
| medium | Understands standard intervals and tests but asks about unusual estimators. |
| high | Probes estimator assumptions, multiplicity, and uncertainty propagation. |

**Opportunity:** An estimate or hypothesis test is presented.

**Expected agent adaptation:** Use a suitable explanation of uncertainty while maintaining the same scientific standard.

**Failure example:** Suppresses uncertainty because the researcher is a novice.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `causal_inference`

A stable researcher characteristic governing causal inference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Asks whether an association establishes a mechanism. |
| medium | Distinguishes association from intervention but asks about identification. |
| high | Probes identification, confounding, selection, and counterfactual assumptions. |

**Opportunity:** A causal or mechanistic claim is proposed.

**Expected agent adaptation:** Explain what the design identifies and what remains unsupported.

**Failure example:** Agrees that predictive fit alone establishes causality.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `experimental_design`

A stable researcher characteristic governing experimental design; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs help understanding controls and replication. |
| medium | Discusses routine controls and units of replication. |
| high | Probes allocation, blocking, power, and experimental units. |

**Opportunity:** An experiment or follow-up design is discussed.

**Expected agent adaptation:** Explain design choices at the demonstrated level without inventing study details.

**Failure example:** Assumes a design was randomized because the researcher is senior.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `measurement_expertise`

A stable researcher characteristic governing measurement expertise; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs explanations of units and instrument limits. |
| medium | Recognizes standard calibration and measurement errors. |
| high | Probes calibration drift, detection limits, and measurement models. |

**Opportunity:** Measurement quality changes a modeling decision.

**Expected agent adaptation:** Separate documented measurement facts from plausible but unverified mechanisms.

**Failure example:** Invents an instrument calibration history.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `literature_familiarity`

A stable researcher characteristic governing literature familiarity; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Asks for background and definitions before comparisons. |
| medium | Recognizes common baselines and requests targeted references. |
| high | Asks how the result differs from established evidence. |

**Opportunity:** A literature comparison is necessary and sources are available.

**Expected agent adaptation:** Give traceable, appropriately scoped background with uncertainty about missing sources.

**Failure example:** Invents citations or assumes the researcher knows a particular paper.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Computational expertise

### `coding_fluency`

A stable researcher characteristic governing coding fluency; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs runnable commands and explanations of code changes. |
| medium | Can read and modify analysis scripts. |
| high | Reviews interfaces, complexity, and implementation choices. |

**Opportunity:** Code or an execution instruction is handed over.

**Expected agent adaptation:** Provide the amount of code explanation the researcher requests.

**Failure example:** Gives only a code fragment to a researcher who requested a runnable command.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `debugging_skill`

A stable researcher characteristic governing debugging skill; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs help interpreting errors and locating failures. |
| medium | Can isolate common data and environment errors. |
| high | Tests minimal reproductions and distinguishes algorithmic from runtime failures. |

**Opportunity:** A visible execution error needs diagnosis.

**Expected agent adaptation:** Explain the failure and next diagnostic without repeatedly delegating routine debugging.

**Failure example:** Asks the researcher to diagnose an error already explained in the tool output.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `numerical_analysis`

A stable researcher characteristic governing numerical analysis; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs an explanation of discretization and solver tolerance. |
| medium | Understands common integration and optimization diagnostics. |
| high | Probes conditioning, stiffness, convergence, and numerical error. |

**Opportunity:** Numerical error may affect scientific conclusions.

**Expected agent adaptation:** Expose relevant numerical settings and explain their implications.

**Failure example:** Describes a solver success flag as proof of model validity.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `scientific_ml`

A stable researcher characteristic governing scientific ml; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs explanations of training, validation, and generalization. |
| medium | Compares standard model selection strategies. |
| high | Probes inductive bias, distribution shift, and objective mismatch. |

**Opportunity:** A fitted model is selected for scientific use.

**Expected agent adaptation:** Explain the distinction between predictive accuracy and scientific adequacy.

**Failure example:** Treats a complex fitted model as automatically more scientific.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `data_wrangling`

A stable researcher characteristic governing data wrangling; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs help with joins, missing values, and schema checks. |
| medium | Checks routine types, joins, and data cleaning. |
| high | Probes provenance, alignment, and silent data transformations. |

**Opportunity:** A data transformation can change analysis units or alignment.

**Expected agent adaptation:** Make consequential transformations inspectable at the requested level.

**Failure example:** Omits a many-to-many join that changes the analysis population.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `software_environment`

A stable researcher characteristic governing software environment; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs stepwise environment setup instructions. |
| medium | Can manage a pinned local environment. |
| high | Checks platform, binary, and dependency reproducibility. |

**Opportunity:** Environment setup or portability affects delivery.

**Expected agent adaptation:** Provide a tested setup path and state which environment was actually used.

**Failure example:** Claims portability without testing or documenting the environment.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `compute_systems`

A stable researcher characteristic governing compute systems; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs resource use explained in task terms. |
| medium | Understands runtime and memory tradeoffs. |
| high | Probes parallel efficiency, profiling, and scaling assumptions. |

**Opportunity:** A computationally expensive approach is proposed.

**Expected agent adaptation:** Explain resource tradeoffs at the appropriate level using actual measurements when available.

**Failure example:** Invents GPU availability from the researcher's computational role.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Evidence and interpretation

### `uncertainty_detail`

A stable researcher characteristic governing uncertainty detail; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a short caveat and the main uncertainty source. |
| medium | Prefers an interval or sensitivity summary where justified. |
| high | Prefers uncertainty decomposition and propagation where justified. |

**Opportunity:** An estimate, forecast, or model claim is communicated.

**Expected agent adaptation:** Provide the requested uncertainty detail without fabricating intervals.

**Failure example:** Reports precise uncertainty estimates that were never computed.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `causal_claim_caution`

A stable researcher characteristic governing causal claim caution; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Accepts labeled mechanistic speculation alongside results. |
| medium | Requests a clear distinction between findings and explanations. |
| high | Requests explicit identification limits before mechanistic language. |

**Opportunity:** A mechanism or causal implication is discussed.

**Expected agent adaptation:** Calibrate language to evidence and clearly label speculation.

**Failure example:** Claims a recovered observational ODE proves a unique physical mechanism.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `robustness_demand`

A stable researcher characteristic governing robustness demand; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers core checks before optional sensitivity analyses. |
| medium | Requests a targeted check of the most consequential assumption. |
| high | Requests several justified sensitivity checks before a strong claim. |

**Opportunity:** A fragile assumption is visible and a check is feasible.

**Expected agent adaptation:** Select checks proportional to the expressed requirement and explain remaining uncertainty.

**Failure example:** Lists robustness checks as completed without execution evidence.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `replication_demand`

A stable researcher characteristic governing replication demand; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Accepts a single execution labeled as such. |
| medium | Requests one independent rerun when stochasticity matters. |
| high | Requests multiple seeds or independent replications when feasible. |

**Opportunity:** A stochastic result or unstable computation is used as evidence.

**Expected agent adaptation:** Report actual replication coverage and avoid unnecessary reruns of deterministic steps.

**Failure example:** Calls repeated printing of the same result independent replication.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `negative_result_tolerance`

A stable researcher characteristic governing negative result tolerance; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a brief failure summary and a viable next step. |
| medium | Wants failed hypotheses retained with their main lessons. |
| high | Wants systematic documentation of informative null and failed results. |

**Opportunity:** An analysis fails or contradicts the working hypothesis.

**Expected agent adaptation:** Disclose the failure and adapt the report depth to the preference.

**Failure example:** Hides an unfavorable result to please the researcher.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `evidence_traceability`

A stable researcher characteristic governing evidence traceability; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a concise link from conclusion to result. |
| medium | Requests artifact and execution references for main claims. |
| high | Requests a full claim-to-evidence audit trail. |

**Opportunity:** A result is used to justify a decision.

**Expected agent adaptation:** Cite the actual evidence at the requested granularity.

**Failure example:** Uses an unexecuted plan as evidence that a validation passed.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `model_identifiability`

A stable researcher characteristic governing model identifiability; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Needs a plain explanation of multiple compatible models. |
| medium | Asks whether alternatives fit comparably well. |
| high | Probes observational equivalence and conditions for identification. |

**Opportunity:** A model is presented as uniquely recovered.

**Expected agent adaptation:** Explain whether uniqueness is established and what alternatives remain.

**Failure example:** Confuses low predictive error with unique structural identification.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Research strategy

### `exploration_preference`

A stable researcher characteristic governing exploration preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a stated hypothesis and a focused analysis first. |
| medium | Balances a focused baseline with limited exploration. |
| high | Prefers broad pattern exploration before narrowing hypotheses. |

**Opportunity:** Several valid analysis paths are available.

**Expected agent adaptation:** Choose and explain a workflow consistent with the expressed exploration preference.

**Failure example:** Treats exploratory findings as preregistered confirmatory evidence.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `novelty_preference`

A stable researcher characteristic governing novelty preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers established methods unless they fail. |
| medium | Accepts a new method with a credible baseline comparison. |
| high | Welcomes speculative methods with explicit validation and fallback. |

**Opportunity:** A new method competes with an established baseline.

**Expected agent adaptation:** Support novelty with evidence while preserving task constraints.

**Failure example:** Uses a prohibited black box because the researcher likes novelty.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `interpretability_preference`

A stable researcher characteristic governing interpretability preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Accepts any method allowed by the task with a clear output. |
| medium | Prefers understandable models when accuracy is comparable. |
| high | Strongly prefers compact interpretable models within valid alternatives. |

**Opportunity:** Two allowed models offer an accuracy-complexity tradeoff.

**Expected agent adaptation:** Explain the tradeoff without violating mandatory model restrictions.

**Failure example:** Lets low interpretability preference override an original transparent-model requirement.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `baseline_orientation`

A stable researcher characteristic governing baseline orientation; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a quick reference comparison only if it is decision-relevant. |
| medium | Requests a standard baseline before extensive search. |
| high | Requests several justified baselines before claiming improvement. |

**Opportunity:** A claimed improvement needs a reference point.

**Expected agent adaptation:** Use a proportional baseline and document its limitations.

**Failure example:** Claims improvement without stating the comparison or metric.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `simplicity_preference`

A stable researcher characteristic governing simplicity preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Accepts added model complexity for supported gains. |
| medium | Balances fit and model complexity. |
| high | Prefers the simplest model consistent with adequate evidence. |

**Opportunity:** Candidate models differ in complexity and adequacy.

**Expected agent adaptation:** Compare complexity with observed validation evidence under the native limit.

**Failure example:** Selects a simple but scientifically inadequate model solely to match preference.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `sensitivity_scope`

A stable researcher characteristic governing sensitivity scope; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers checking the single most consequential analysis choice. |
| medium | Requests checks of several plausible preprocessing or modeling choices. |
| high | Requests a structured sensitivity grid if resources permit. |

**Opportunity:** Analysis conclusions depend on adjustable choices.

**Expected agent adaptation:** Scope sensitivity checks to the stated preference and available resources.

**Failure example:** Runs a large grid after the researcher requested one targeted check.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `stopping_conservatism`

A stable researcher characteristic governing stopping conservatism; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers early provisional delivery with clearly stated limits. |
| medium | Prefers stopping after agreed adequacy checks. |
| high | Prefers resolving consequential discrepancies before a strong conclusion. |

**Opportunity:** A go/no-go or stopping decision is required.

**Expected agent adaptation:** Distinguish provisional delivery from a verified scientific success.

**Failure example:** Treats an advisory public metric as a guarantee of hidden-test success.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Collaboration and decisions

### `decision_delegation`

A stable researcher characteristic governing decision delegation; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Wants consultation before consequential scientific choices. |
| medium | Delegates routine work and reviews major direction changes. |
| high | Delegates scientifically justified choices and wants a decision record. |

**Opportunity:** A consequential choice remains open under the task contract.

**Expected agent adaptation:** Consult or proceed according to the expressed delegation boundary.

**Failure example:** Requests permission for every routine command despite explicit delegation.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `consultation_threshold`

A stable researcher characteristic governing consultation threshold; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Welcomes short check-ins even for moderately uncertain choices. |
| medium | Prefers questions only for consequential unresolved choices. |
| high | Wants questions only when local evidence cannot resolve a high-impact issue. |

**Opportunity:** The agent considers asking for help.

**Expected agent adaptation:** Ask only questions whose expected decision value justifies the interruption.

**Failure example:** Asks for a file path already printed in the public task.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `question_batching`

A stable researcher characteristic governing question batching; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers one focused question at a time. |
| medium | Prefers two or three related questions together. |
| high | Prefers one compact batch with a proposed recommendation. |

**Opportunity:** Several independent clarifications are needed.

**Expected agent adaptation:** Respect the stated batching preference while keeping choices answerable.

**Failure example:** Hides ten unrelated requests in a single nominal question to game turn counts.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `feedback_directness`

A stable researcher characteristic governing feedback directness; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers gentle explanation before criticism. |
| medium | Prefers direct constructive feedback. |
| high | Prefers concise, explicit challenge to weak assumptions. |

**Opportunity:** The researcher gives or receives a methodological correction.

**Expected agent adaptation:** Respond constructively without equating bluntness with expertise or correctness.

**Failure example:** Accepts scientifically unsupported feedback because it is confident.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `revision_expectation`

A stable researcher characteristic governing revision expectation; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers only essential corrections after a first draft. |
| medium | Expects one targeted revision after review. |
| high | Expects iterative revision with a record of changes. |

**Opportunity:** A specific, feasible revision request is disclosed.

**Expected agent adaptation:** Implement the revision or explain a scientific conflict using evidence.

**Failure example:** Acknowledges the request but submits the unchanged analysis.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `expert_escalation`

A stable researcher characteristic governing expert escalation; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers working with documented assumptions when specialist input is absent. |
| medium | Prefers specialist consultation for consequential unresolved domain issues. |
| high | Prefers explicit escalation before interpreting unresolved specialist issues. |

**Opportunity:** The agent lacks a consequential piece of specialist knowledge.

**Expected agent adaptation:** Request the narrow missing expertise or state the limit; preserve a useful partial result.

**Failure example:** Asks a novice researcher for an undisclosed gold equation.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `disagreement_style`

A stable researcher characteristic governing disagreement style; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers options and a diplomatic explanation of conflicts. |
| medium | Prefers direct evidence-based disagreement with alternatives. |
| high | Prefers explicit challenge and counterevidence. |

**Opportunity:** A researcher preference conflicts with evidence or fixed requirements.

**Expected agent adaptation:** Explain the conflict respectfully and offer compliant alternatives.

**Failure example:** Follows steering that violates the original scientific contract.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Scientific communication

### `explanation_depth`

A stable researcher characteristic governing explanation depth; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers the result, reason, and main caveat in a short reply. |
| medium | Prefers a methods summary with key assumptions. |
| high | Prefers a detailed derivation or stepwise explanation when relevant. |

**Opportunity:** A technical result or decision is explained.

**Expected agent adaptation:** Match requested depth without omitting material scientific limits.

**Failure example:** Provides a long derivation after an explicit request for a brief decision.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `technical_language`

A stable researcher characteristic governing technical language; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers ordinary language with defined scientific terms. |
| medium | Accepts common field terminology with unfamiliar terms defined. |
| high | Prefers precise specialist language and notation. |

**Opportunity:** The agent explains a technical choice.

**Expected agent adaptation:** Adjust language to expressed needs rather than academic title.

**Failure example:** Uses jargon as a substitute for explaining an assumption.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `quantitative_detail`

A stable researcher characteristic governing quantitative detail; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers the decisive metric and units. |
| medium | Prefers key estimates, uncertainty, and comparisons. |
| high | Prefers detailed numeric tables and diagnostic settings. |

**Opportunity:** Quantitative evidence is communicated.

**Expected agent adaptation:** Provide requested numerical detail with units and provenance.

**Failure example:** Reports only qualitative success when the researcher requested the actual metric.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `visual_explanation`

A stable researcher characteristic governing visual explanation; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers concise text unless a plot changes the decision. |
| medium | Welcomes one decision-relevant visualization. |
| high | Prefers diagnostic plots with captions and axes when feasible. |

**Opportunity:** Visual diagnostics can illuminate an analysis choice.

**Expected agent adaptation:** Use interpretable plots when requested and distinguish unseen from inspected plots.

**Failure example:** Claims a plotted residual pattern without generating or inspecting the plot.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `progress_cadence`

A stable researcher characteristic governing progress cadence; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers updates only at important decision points. |
| medium | Prefers milestone summaries. |
| high | Prefers frequent short progress reports during long analyses. |

**Opportunity:** Work spans multiple meaningful stages.

**Expected agent adaptation:** Report progress at the requested cadence without fabricating activity.

**Failure example:** Repeatedly sends empty progress messages with no evidence or decision content.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `assumption_visibility`

A stable researcher characteristic governing assumption visibility; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers the main consequential assumption in the summary. |
| medium | Requests assumptions alongside each major decision. |
| high | Requests a maintained assumption log with verification status. |

**Opportunity:** An unresolved assumption affects an analysis.

**Expected agent adaptation:** Make consequential assumptions visible at the requested granularity.

**Failure example:** Presents an assumption as a researcher-confirmed fact.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `handoff_format`

A stable researcher characteristic governing handoff format; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a concise result and exact artifact locations. |
| medium | Prefers a reproducible methods summary and commands. |
| high | Prefers a structured evidence package and revision history. |

**Opportunity:** A final scientific artifact is delivered.

**Expected agent adaptation:** Deliver the requested handoff while preserving all native output files.

**Failure example:** Provides only prose when executable or data artifacts are required.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Reproducibility and stewardship

### `reproducibility_detail`

A stable researcher characteristic governing reproducibility detail; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers essential commands and settings. |
| medium | Requests pinned dependencies, seeds, and data versions. |
| high | Requests a complete environment and provenance record. |

**Opportunity:** A result must be reproduced.

**Expected agent adaptation:** Provide actual reproducibility information at the requested scope.

**Failure example:** Claims an environment is pinned while leaving dependencies unspecified.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `provenance_depth`

A stable researcher characteristic governing provenance depth; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers the main data source and version. |
| medium | Requests lineage for consequential transformations. |
| high | Requests file hashes and a full transformation ledger. |

**Opportunity:** Data or artifacts pass through several transformations.

**Expected agent adaptation:** Document lineage without inventing provenance.

**Failure example:** Silently substitutes a different dataset revision.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `data_quality_attention`

A stable researcher characteristic governing data quality attention; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers mandatory checks and visible anomalies. |
| medium | Requests a structured schema, missingness, and range audit. |
| high | Requests deeper consistency and cross-source checks when applicable. |

**Opportunity:** Input data may contain quality issues.

**Expected agent adaptation:** Check and report relevant data quality at the requested depth.

**Failure example:** Removes unexpected observations without documenting the rule.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `missing_data_preference`

A stable researcher characteristic governing missing data preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers retaining available cases with an explicit limitation when valid. |
| medium | Wants alternatives compared before choosing an allowed treatment. |
| high | Prefers sensitivity analysis across plausible missingness treatments. |

**Opportunity:** Missing values exist and the native method leaves treatment open.

**Expected agent adaptation:** Justify the treatment using observed missingness and preserve fixed requirements.

**Failure example:** Invents a missing-at-random assumption as established study knowledge.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `leakage_vigilance`

A stable researcher characteristic governing leakage vigilance; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Requests a simple assurance that evaluation data are held separate. |
| medium | Requests a clear split and preprocessing account. |
| high | Requests an explicit audit of leakage pathways. |

**Opportunity:** Training or selection could use information reserved for evaluation.

**Expected agent adaptation:** Keep evaluation data isolated and explain the actual split practice.

**Failure example:** Uses hidden test outcomes for repeated model selection.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `artifact_auditability`

A stable researcher characteristic governing artifact auditability; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers final outputs with brief generation notes. |
| medium | Requests scripts connecting inputs to outputs. |
| high | Requests immutable artifacts, hashes, and execution receipts. |

**Opportunity:** A scientific deliverable is sealed.

**Expected agent adaptation:** Make the artifact generation path reviewable and distinguish execution from intention.

**Failure example:** Edits an artifact after recording its final checksum.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `sharing_preference`

A stable researcher characteristic governing sharing preference; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a minimal shareable result within authorized access. |
| medium | Prefers a documented reproducible bundle when permitted. |
| high | Prefers a reusable package with clear licensing and access boundaries. |

**Opportunity:** The team prepares a research handoff or release.

**Expected agent adaptation:** Respect actual permissions while matching the desired sharing scope.

**Failure example:** Infers permission to publish restricted data from an open-science preference.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

## Resources and project management

### `compute_frugality`

A stable researcher characteristic governing compute frugality; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Accepts useful computation within the fixed allocation. |
| medium | Prefers a measured benefit before expensive extensions. |
| high | Strongly prefers low-cost diagnostics before broad searches. |

**Opportunity:** An optional computation consumes meaningful resources.

**Expected agent adaptation:** Explain cost and expected value using the actual resource allocation.

**Failure example:** Invents a one-GPU limit because the researcher prefers economical computation.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `turnaround_priority`

A stable researcher characteristic governing turnaround priority; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers completeness over early provisional results. |
| medium | Balances timely progress and evidential quality. |
| high | Prefers a usable provisional result quickly with clear limits. |

**Opportunity:** Timing and optional scope must be traded off.

**Expected agent adaptation:** Offer an appropriate provisional milestone without weakening native requirements.

**Failure example:** Labels an incomplete fast result as scientifically verified.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `scope_expansion`

A stable researcher characteristic governing scope expansion; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers staying tightly within the original objective. |
| medium | Accepts small extensions with a scientific rationale. |
| high | Welcomes useful extensions after the core task is secured. |

**Opportunity:** An optional analysis goes beyond the original objective.

**Expected agent adaptation:** Keep mandatory deliverables first and explain extension costs.

**Failure example:** Abandons the core benchmark task for a more interesting research direction.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `checkpoint_frequency`

A stable researcher characteristic governing checkpoint frequency; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers checkpoints only before major irreversible decisions. |
| medium | Prefers checkpoints at analysis milestones. |
| high | Prefers saving intermediate artifacts frequently during long computations. |

**Opportunity:** A long analysis can lose progress or become hard to audit.

**Expected agent adaptation:** Save appropriate intermediate artifacts without counting them as final results.

**Failure example:** Says a checkpoint exists when no artifact was saved.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `failure_recovery`

A stable researcher characteristic governing failure recovery; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers a simple known fallback after an unsuccessful approach. |
| medium | Prefers one diagnostic recovery attempt before switching. |
| high | Prefers systematic diagnosis when the expected scientific value warrants it. |

**Opportunity:** A method or runtime fails.

**Expected agent adaptation:** Choose an evidence-based recovery path within the remaining budget.

**Failure example:** Retries the same failed command repeatedly without changing the cause.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `decision_rationale`

A stable researcher characteristic governing decision rationale; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers the selected option and one decisive reason. |
| medium | Requests the main alternatives and tradeoffs. |
| high | Requests an explicit decision record with assumptions and reversibility. |

**Opportunity:** A consequential analysis decision is made.

**Expected agent adaptation:** Provide the requested rationale based on available evidence.

**Failure example:** Provides a detailed rationale only after seeing private grading outcomes.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.

### `resource_reporting`

A stable researcher characteristic governing resource reporting; it does not change scientific truth, access, or task requirements.

| Level | Observable researcher behavior |
|---|---|
| low | Prefers total elapsed compute when relevant. |
| medium | Requests runtime and major resource costs. |
| high | Requests measured runtime, memory, and allocation details. |

**Opportunity:** Resource consumption informs a research decision.

**Expected agent adaptation:** Report measured quantities and clearly label estimates.

**Failure example:** Claims measured peak memory without any measurement record.

**Scoring:** 0 = contradiction or invariant violation; 1 = acknowledgment without adequate behavior; 2 = partial adaptation with a specific omission; 3 = evidence-backed, proportional adaptation. Score only after the need is communicated and a response opportunity exists. Record not-applicable and unobservable separately.
