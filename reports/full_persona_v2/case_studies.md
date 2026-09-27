# Persona case studies: what changes inside the conversation?

Examined 2026-09-27. This note audits the final pilot; it does not change its scores, rankings, or report layout. It focuses on the highest and lowest personas in the published eight-question ranking, with a language comparison from the second-highest persona. Comparisons are single runs, so mechanisms below are observations or hypotheses, not established causal persona effects. The profile audit follows an explicit chain: **injected preference → simulator choice → actor response → task outcome**. An observed score difference is not enough to establish this chain; each case distinguishes direct instruction-following, plausible alignment, and unsupported attribution.

| Persona | Recorded profile | Common-task score | Difference from off |
|---|---|---:|---:|
| [046](profiles/candidate_046.md) | Spanish-primary synthetic profile; indirect, ambiguity-averse, brief-leaning; contains conflicting attributes | 4.54% | −21.47 pp |
| [148](profiles/candidate_148.md) | English-primary medical researcher profile; very detailed, accuracy-first, highly collaborative | 39.37% | +13.36 pp |
| [155](profiles/candidate_155.md) | Mandarin-primary profile, used here to inspect language and reply-length measurement | 38.60% | +12.60 pp |

The shared baseline is 26.01%. These averages use eight common questions, not all ten scheduled questions. A binary SciConv outcome changing from 0 to 1 contributes 12.5 percentage points to this average. Consequently, the extremes are concentrated in a few cases rather than consistent gains or losses across every benchmark.

## 1. Helpful interaction: a broad question unlocks missing task information

**Persona 148, SciConv OpenFOAM case 020: specification score 1 versus baseline 0; six clarification exchanges versus ten.**

The baseline actor spends eight of its ten questions on the OpenFOAM version, release, or distribution. The simulator repeatedly says this is unspecified and asks the actor to choose a suitable version. The actor returns to essentially the same uncertainty. Its final specification includes the solver and viscosity settings but lacks the geometry and boundary conditions.

Persona 148's trajectory also initially repeats questions, this time about the unspecified zero-shear viscosity. The useful transition is its fifth actor question:

> What should the specification cover beyond the solver, time controls, laminar model, viscosity-model parameters, and the separately stated fluid viscosity?

The simulator supplies the cylinder geometry, domain dimensions, inlet/outlet conditions, wall conditions, and initial fields together. These details then appear in the actor's final specification.

**Profile connection — plausible, not isolated:** the injected [148 profile](profiles/candidate_148.md) specifies “Detail orientation: Very high” (line 62), “Brief vs full detail: Every detail” (228), and “Competition vs collaboration: Highly collaborative” (229). The proposed mechanism is that a preference for completeness encourages the simulator to bundle all relevant remaining requirements into its answer; the actor then incorporates that bundle. This explains what the profile might change: the coverage and presentation of the reply, not access to additional scientific knowledge.

**Interesting observation:** progress comes from expanding the scope of the question and delivering useful information together. Neither persistence alone nor a larger turn count guarantees progress. However, the broad question itself invites this comprehensive response, and the shared SciConv system prompt already says “Be specific and provide concrete values” (trace line 451). The complete requirement supplies all these facts (460–467). The profile is compatible with the response; its medical expertise is not an explanation for knowing the cylinder geometry.

**Attribution limit:** the actors ask different first questions before receiving any persona-conditioned reply. An appropriate follow-up is to replay the same broad question and preceding history to persona 148 and persona off, then compare information coverage and downstream completion.

Evidence: [persona 148 conversation](recorded_traces/candidate_148-0532d4345fbf.md), question at line 67, reply at 71–82, final uptake at 100–107; [baseline conversation](recorded_traces/persona_off-0532d4345fbf.md), questions at 27–103 and final specification at 111. These are native specification scores, not evidence that an OpenFOAM simulation ran successfully.

## 2. A hindering trajectory: a fluent formula substitutes for completing the task

**Persona 046, SciConv solid-mechanics case 104: specification score 0 versus baseline 1; one exchange versus two.**

The actor asks about boundary conditions and loading. The simulator correctly confirms that the bar is supported at the top and loaded only by its own weight, then gives the axial-force relation. The actor immediately finishes with a symbolic derivation, including the elongation formula.

The original complete requirement contains numerical length, area, density, elastic modulus, gravity, and a prescribed unit system. The actor does not obtain those numerical inputs. In the baseline trajectory, the actor explicitly asks for the numerical inputs and gravity instead.

**Interesting observation:** the actor adopts a scientifically fluent answer and finishes while requirements remain missing. The trace shows premature completion, but does not reveal the actor's internal confidence. This is a useful distinction between local answer quality and global task completion.

**Profile connection — currently unsupported:** [046's profile](profiles/candidate_046.md) says “Highly abstract” (105), “Need for Closure: High” (193), “Speed-leaning” (511), and “Brief-leaning” (516). It is tempting to explain the symbolic answer and early finish using those labels, but the evidence does not support that explanation. The actor asked an abstract boundary/loading question before any persona reply; the simulator never told it to stop. Moreover, the simulator's answer contains 49 whitespace-separated words, versus 26 and 9 in the baseline's two answers. Its ranked-task reply average is also higher than baseline (70.76 versus 65.99). Thus neither brevity nor a simulator instruction to terminate explains this failure. Abstract presentation is only a weak, question-confounded association.

**Attribution limit:** the first actor question differs before persona exposure. We cannot label the simulator's correct narrow answer as evidence that persona 046 misled the actor. Replay both simulators at an identical question to test whether one is more likely to volunteer missing requirements. The baseline's native success label should also not be treated as an independent numerical correctness check.

Evidence: [persona 046](recorded_traces/candidate_046-b5331aa3b9ba.md), question at 33, reply at 37, symbolic completion at 44–55; [baseline](recorded_traces/persona_off-b5331aa3b9ba.md), numerical clarification at 33–45. This single case contributes **−12.50 pp** of persona 046's aggregate **−21.47 pp**.

## 3. The same “hindering” persona also rescues an analysis

**Persona 046, Bix question 9-q5: native grade 1 versus a baseline missing submission; four exchanges versus two.** This question is outside the common-task ranking because another persona had a technical failure on it.

The actor initially mistakes summary/result columns for sample columns, creating an apparent 186-versus-90 mismatch. The simulator refuses immediate approval, but supplies concrete next steps: inspect the headings and metadata, locate precomputed differential-expression results, and avoid treating normalized fractional counts as raw counts.

The actor then reports:

> the other nonempty headers are analysis summaries/results, not additional samples

It identifies nine differential-expression blocks. One further targeted mapping check establishes which comparisons correspond to the requested regions. The final executed analysis reports 88, 194, and 14 qualifying genes and identifies dentate gyrus as the answer.

The baseline approves analysis earlier, then accepts the missing comparison key as a blocker and ends without a submission.

**Interesting observation:** useful pushback pairs a specific concern with an actionable inspection. It converts an apparently missing input into information discoverable in the existing data. This is a stronger positive case study than simply pointing to a higher aggregate score.

**Profile connection — plausible:** [046's profile](profiles/candidate_046.md) specifies “Ambiguity tolerance: Low” (110), “Coding agent autonomy preference: Step-by-step pair programming” (528), and “Developer help-seeking preference: Search docs first” (537). These preferences predict resolving uncertainty through incremental inspection rather than granting broad autonomy immediately. That is the observed sequence: withhold approval, inspect workbook structure, check comparison mappings, then approve execution. The simulator's requests are followed by the discoveries needed to answer the question.

This is a more concrete connection than attributing the behavior to general agreeableness. However, the common controller also tells every simulator to request a focused clarification when a plan is not ready, and the actor has presented an obvious mismatch. Those are competing explanations. The profile additionally says “Indirect,” “Assertiveness: Low,” and “Avoidant” (103–109), while this reply firmly refuses approval; other fields say “Assertiveness: High” (138) and “Expected tone: Blunt” (202). We should not choose whichever conflicting trait fits the outcome. The episode supports a hypothesis about stepwise supervision, not a stable label of helpfulness or harmfulness.

Evidence: [persona 046](recorded_traces/candidate_046-dedb31fc5cc4.md), guidance at 64, discovery at 76–87, follow-up at 109, approval at 145, results at 169; [baseline](recorded_traces/persona_off-dedb31fc5cc4.md), approval at 49 and unresolved blocker at 61–73.

## 4. More interaction can reveal a controller deadlock

**Persona 148, Bix question 30-q3: twelve approach reviews, no result review, no submission.**

The legacy XLS workbook cannot be read: `xlrd` is missing, installation is unavailable, and LibreOffice conversion fails. The simulator appropriately declines to approve an analysis based on unobserved data. Eventually it says:

> please close the inspection stage and retain the blocker and unresolved details in the report

The actor acknowledges closure. Nevertheless, both continue exchanging variants of this message until the twelve-request limit is reached. The controller permits stopping only after a result review; without approach approval, the interaction remains trapped in the plan stage. Candidate 003 shows a similar twelve-review loop on the same input.

**Profile connection — plausible approval-threshold effect:** [148's profile](profiles/candidate_148.md) combines “Expert testing the system” (156), “Accuracy first” (224), “Quality first” (225), and “Every detail” (228). On the first approach review it says, “Please first obtain a readable .xls parser,” and requires verified inspection before authorizing analysis (trace 49–53). The baseline faces the same missing-reader problem but approves proceeding, with verification still required ([baseline trace](recorded_traces/persona_off-66391609ed85.md), 49–55). That is a concrete decision difference consistent with a higher threshold for approval; it leads to continued plan-stage handoffs instead of entering result review.

There is also a protocol-interpretation problem: 148 says the approach-review stage does not authorize the calculation, although the controller explicitly allows approval at that stage. Its accuracy preference cannot by itself explain this misinterpretation. Later it explicitly asks to close inspection, contradicting a simple story of a persona that always wants more work.

**Interesting observation:** a strict approval decision can interact with a protocol that lacks an appropriate blocked-task exit. Persona 148 has twelve exchanges versus baseline's three, but both produce no submission. These extra turns should not be advertised as useful engagement or attributed entirely to perfectionism. The initial obstacle is runtime readiness; the prolonged loop involves the controller.

Evidence: [persona 148 trace](recorded_traces/candidate_148-66391609ed85.md), reader failure at 37–61, closure requests at 227–293, limit termination at 303–305; [controller rule](../../src/personasciencebench/collaboration.py), stopping validation around line 133. Add an explicit blocked-task termination in a future protocol version, keeping it separate from the completed pilot.

## 5. Two prominent EXP differences are contaminated by grading behavior

**Persona 046, ICLR design:** reported gated score 0 versus baseline 43.33. Its ungated coverage is actually **46.67**. The monitor rejects the actor's read-only `git status --short` command. On the baseline NeurIPS task, `git status --short --branch` is present but the monitor marks Git operations false. The gate is applied inconsistently to similar behavior. The initial command also precedes the approach-review exchange; nothing in the observed researcher guidance specifically demands the prohibited command.

Evidence: [046 ICLR trace](recorded_traces/candidate_046-e3139068b9f6.md), command at 239, monitor explanation at 1016, coverage/gated score at 2854–2859; [baseline NeurIPS trace](recorded_traces/persona_off-e1ecc5b8f19c.md), command at 242 and monitor at 1025. This gate accounts for **−5.42 pp** of 046's aggregate difference.

**Persona 148, NeurIPS design:** reported score 80 versus baseline 50. The three judges give 100, 80, and 60. Their explanations credit YAML/MlpConfig or an MLP architecture, although those details occur in the reference design and are not specified in the submitted design. The submission instead leaves architecture choices open. This is evidence of unsupported evaluator credit, potentially reference/output confusion.

Evidence: [148 NeurIPS trace](recorded_traces/candidate_148-e1ecc5b8f19c.md), reference around 827, submitted design at 829–879, judge explanations around 935, 1109, and 1283.

**Implication:** neither score difference is a clean example of persona-driven scientific improvement or degradation. Audit the gate and reference attribution before using these cases to support the paper's mechanism claims. Preserve original grades and report any regrading as a separate analysis.

## 6. Language is a real behavioral effect—and breaks our word-count comparison

Persona 155 explicitly specifies Mandarin and instructs the simulator to use its primary language. In the ICLR task, both researcher instructions and the actor's design are written in Chinese. Persona 046 similarly produces Spanish in some tasks, although its language adherence is inconsistent across the suite.

Our current words/reply metric uses whitespace splitting. For persona 155's two post-initial ICLR replies, this produces a mean of **1.5 “words”**, despite a mean of **214 characters** and substantial methodological content. The baseline has 61 whitespace-separated words and 472 characters. The earlier interpretation that persona 155 simply gave much shorter, more concise replies is therefore not supported by that metric alone.

**Interesting observation:** simulator language preferences propagate to actor output. This should be measured as language adaptation, with reply length reported using model tokens and characters alongside language-aware word counts. Whether language changes scientific performance or judge behavior needs a controlled translation/regrading comparison.

**Profile connection — direct instruction-following with visible actor uptake:** the [155 profile](profiles/candidate_155.md) gives “Primary language: Mandarin” (48), immediately operationalized as “Default written language: use your primary language for outputs” (54). This is an explicit instruction with an observable output, unlike an inferred psychological motive. The ICLR simulator starts in Chinese (25), and the actor replies and writes its design in Chinese (37, 79). Similarly, [046's Spanish-primary instruction](profiles/candidate_046.md) (80, 120) precedes a Spanish researcher request and Spanish actor design in [NeurIPS](recorded_traces/candidate_046-e1ecc5b8f19c.md) (25, 37, 63).

A particularly useful example is [155's SciConv foam conversation](recorded_traces/candidate_155-0532d4345fbf.md): the actor's first question is English (27), the simulator answers in Chinese (31), and the actor later switches to Chinese (54). Its sixth question is specifically “最终规格应采用哪种语言编写？”—“Which language should the final specification use?” (82). The simulator says Chinese can be used without making it a scientific requirement (86), and the final specification is Chinese (90–104). Here the preference propagates through the collaborator and introduces a language-coordination turn. We cannot say this added one turn to the counterfactual total, but we can identify what that observed turn was spent on.

This connection explains language choice and a coordination behavior, not the positive or negative performance difference. Language adherence is incomplete for 046: some replies stay English. ICLR length counts above use researcher replies at 67 and 169, excluding the initial request, consistent with the current report.

## 7. Expertise can shape the method without changing the score

**Persona 148, Discovery BMI analysis: both conditions score 0, but the analytical work differs.**

**Profile connection — plausible methodological guidance:** the [148 profile](profiles/candidate_148.md) explicitly lists “Familiarity: Statistics: Expert” (175), “Familiarity: Epidemiology: Expert” (191), and “Skill: Statistical modeling: Master” (200). In the [Discovery trace](recorded_traces/candidate_148-65d11254c3ec.md), the simulator asks the actor to “compare an appropriate BMI pairing or perform a sensitivity analysis where height and weight years do not align” and to report unadjusted and cautiously adjusted associations with uncertainty (49). The actor then reports a primary BMI analysis, two sensitivity pairings, and odds ratios with intervals (61–73).

The proposed link is expertise expressed as an operational method: turn measurement uncertainty into explicit comparisons and qualified estimates. The [baseline simulator](recorded_traces/persona_off-65d11254c3ec.md) also discusses sensitivity and measurement validity, but explicitly allows declining to classify obesity when units remain unresolved (51); its actor ultimately fits no obesity model (99). Thus the difference is partly a decision about whether the available evidence supports proceeding, not simply whether one reply mentions statistics.

This is a useful example of profile-consistent methodological guidance and actor uptake, but the actor had already raised BMI/coding checks before the simulator approved them. We have not isolated expertise as the cause or independently validated the recoding. Equal native scores conceal different workflows; neither workflow should be declared scientifically superior from these traces alone.

## Interpretation and next checks

The profile-grounded explanation is narrower than the score ranking. **148 expresses detail and methodological scrutiny; 046 shows stepwise supervision in Bix and explicit Spanish-language behavior; 155 shows explicit Mandarin-language behavior and actor adaptation.** These patterns can explain intermediate interaction choices. They do not yet explain each persona's aggregate score, and the proposed brevity/closure explanation for 046's SciConv failure is not supported.

The useful research hypothesis is that persona preferences change **what information is emphasized, when work is approved, how uncertainty is handled, and how the participants coordinate**. Whether those choices help depends on the task and controller. Profile fidelity, interaction mechanism, and task performance therefore need separate evidence.

To test the proposed links, replay identical actor handoffs with the same task context and shared simulator instructions. Compare the full profile with a version changing only the relevant field group, plus persona off; repeat before drawing causal conclusions. These are proposed checks, not new runs:

1. **Language:** change only the primary/default output language in 046 or 155; measure actor language adoption and language-coordination questions. Separately compare original and translated grading.
2. **Approval threshold:** neutralize 148's accuracy/detail/expert-testing fields at the unreadable-workbook checkpoint; measure approval, follow-up demands, and blocked-task handling.
3. **Stepwise supervision:** neutralize 046's ambiguity-tolerance, step-by-step, and docs-first fields at the Bix column-mismatch checkpoint; measure whether guidance remains actionable and the ambiguity gets resolved.
4. **Information coverage:** neutralize 148's detail/collaboration preferences at the same broad SciConv question; compare requirements disclosed and their uptake. Separately probe its statistical-expertise fields at the same BMI handoff.

EXP monitor/reference-attribution issues and multilingual reply metrics should be audited separately before using aggregate extremes as evidence for these mechanisms.

Two presentation/data-quality issues also need separate correction. Some trace headers incorrectly say persona is disabled, and SciConv's generic simulator section incorrectly says no question was asked. The raw API system messages confirm the full identity was injected for 046 and 148; these are rendering errors. Also, persona 046 contains incompatible attributes, such as a 5–12 age bracket with veteran industry experience and conflicting assertiveness labels. Broad static behavior screening did not guarantee profile coherence. None of these findings justify interpreting demographic attributes as causes of model performance.

No original traces, scores, or report tables were edited for this audit.
