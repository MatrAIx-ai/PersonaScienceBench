# SciConvBench: simulator disclosure and fact recovery

**Result.** With the actor fixed, how much the researcher simulator volunteers moves the share of withheld facts the actor recovers by up to 31 points ([PR #25](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/25)). SciConvBench's simulator prompt says "Do not provide information not asked for."; PSB removes that line in every arm, persona off included. Within one model, the persona comparison keeps disclosure nearly fixed: in the Haiku-actor campaign the Opus simulator hands over 90% of the withheld values under persona off and 90 to 92% under the four profiles. Across models it does not: in the paper's model scorecard each actor is also its own researcher simulator, so a difference in fact recovery between two models can come from the actor's questions or from how much its simulator volunteers.

## 1. Disclosure with the actor fixed (GLM-5, from PR #25)

62 OpenFOAM disambiguation cases, GLM-5 as actor, simulator and judge, 6 conversations per case and condition, all conditions starting from the same first actor question. Fact recovery is the share of withheld facts the native SciConvBench judge finds in the final specification (its a/b count, as in the paper's fact-recovery definition, not the strict all-or-nothing FR), from PR #25 ([cards_analysis.txt](https://github.com/joverwiening/PersonaScienceBench/blob/report/sciconv-persona-pilots/reports/sciconv_persona_pilots/cards_analysis.txt) line 4). Values handed over is the measure of section 2, over the 60 cases with numeric withheld facts ([handover_check.txt](handover_check.txt)).

| simulator instruction | fact recovery | values handed over |
|---|---:|---:|
| none (neutral) | 0.669 | 0.627 |
| answer exactly what is asked, nothing more | 0.553 | 0.568 |
| also give the other values in the notes for the same part of the setup | 0.864 | 0.837 |

Volunteer minus terse, paired by case with case-bootstrap 95% CIs: fact recovery +31.1 points [+25.1, +37.3], values handed over +27.0 [+22.9, +31.0].

## 2. PSB's setting (Haiku actor, Opus simulator)

- `configs/full_persona_v2/shared.json` sets `volunteer_information: true`, and `full-campaign-results.json` in [`Experiment/shared/haiku_actor_opus_persona_pilot`](../../Experiment/shared/haiku_actor_opus_persona_pilot) records it for all 200 SciConvBench episodes, 40 per arm. `sciconv_runner.py` then drops the native line from every simulator prompt.
- [logs_check.py](logs_check.py) reads that campaign's traces, no model calls. For each withheld fact it takes the numbers in the fact, drops numbers already in the opening request, and counts the share found in the simulator's replies. Persona off 0.897, profiles 0.901 to 0.921 (16 disambiguation cases with numeric withheld facts, one conversation each). Profile minus persona off is 0 to +2.4 points; only profile 155's interval excludes 0. Profile 001, which favors brief replies, is at 0.901. The profiles change reply language and length much more than this share.

## For the paper

- The SciConvBench prompt template in the appendix says the simulator answers "using the intended requirement and the configured knowledge policy". It does not say that the native line is removed in every arm.
- For the scorecard's fact recovery column: one fixed simulator model across actors, as the Haiku campaign used Opus, would separate actor from simulator. Otherwise the caption can state that fact recovery includes the simulator's disclosure.

## Limits

- Section 1 uses GLM-5 in every role on one domain. Its conditions are not PSB's switch: "answer exactly what is asked" is a stronger form of the native line, and "none" is our own simulator prompt, not the native one.
- Values handed over matches numbers as strings, so a value restated in other units or words is missed, facts without numbers are skipped, and a value counts whether or not the actor asked for it. The fact cards were written by GLM-5 from the SciConvBench case files.
- Under persona off the Opus simulator already hands over all numeric values in 9 of 16 cases, so section 2 has little room upward.
- We have not measured disclosure in the scorecard runs; their conversations are not in this repository.

## Files

- [logs_check.py](logs_check.py), [logs_check.txt](logs_check.txt), [logs_check_chats.csv](logs_check_chats.csv): section 2. From the repository root: `python reports/sciconv_disclosure/logs_check.py > reports/sciconv_disclosure/logs_check.txt`.
- [fact_cards.json](fact_cards.json): fact cards for the campaign's disambiguation cases, from the [`persona-behaviour-cards`](https://github.com/joverwiening/SciConvBench/tree/persona-behaviour-cards) branch of our SciConvBench fork (`persona/fact_cards/`).
- [handover_check.py](handover_check.py), [handover_check.txt](handover_check.txt): values handed over for section 1. Its inputs (the PR #25 run directory, and the foam fact cards and dataset from the same fork branch) are not in this repository.
