# Results: Big Five scientist personas on SciConvBench (62 OpenFOAM cases)

This folder reports one run and its data. It adds no code to this repository.

**Result.** Three of nine Big Five traits given to SciConvBench's simulated scientist raise the share of deleted facts the agent recovers by 14–15 percentage points over a neutral scientist (0.65): anxious, outgoing and curious. They are also the three wordiest scientists, and this run cannot separate the trait from reply length. The other six traits do not pass the analysis rules fixed before the run. GLM-5 plays every role.

## Results

Effect = trait minus neutral in the share of deleted facts recovered, paired by case (+0.154 = 15.4 percentage points). A trait counts only if its Holm-corrected p is below 0.05 and a judge can tell its chats from neutral ones (Visible, see Method).

| Trait (Big Five pole) | Effect [95% CI] | Holm p | Visible | Counts | Words per reply |
|---|---:|---:|---|---|---:|
| Anxious (high neuroticism) | +0.154 [0.090, 0.217] | 0.009 | yes | **yes** | 74 |
| Outgoing (high extraversion) | +0.154 [0.092, 0.216] | 0.044 | yes | **yes** | 56 |
| Curious (high openness) | +0.136 [0.078, 0.194] | 0.031 | yes | **yes** | 48 |
| Organised (high conscientiousness) | +0.069 [0.010, 0.128] | 0.45 | no | no | 24 |
| Agreeable (high agreeableness) | +0.052 [−0.004, 0.108] | 0.57 | yes | no | 37 |
| Disorganised (low conscientiousness) | +0.034 [−0.021, 0.090] | 0.76 | yes | no | 20 |
| Conventional (low openness) | −0.027 [−0.087, 0.034] | 0.76 | incomplete¹ | no | 14 |
| Reserved (low extraversion) | −0.065 [−0.126, −0.003] | 0.45 | yes | no | 7 |
| Disagreeable (low agreeableness) | −0.087 [−0.151, −0.023] | 0.33 | yes | no | 29 |

Reference points, as absolute recovery: neutral scientist 0.65 (6 wordings, 0.60–0.72; 19 words per reply); a scripted scientist who always replies "Make a reasonable assumption based on best practices." 0.23; a scripted scientist who gives every deleted fact each turn 1.00.

59–60 cases per trait: a case enters when all 6 neutral chats and all 3 trait chats were graded. ¹ The budget cap stopped the visibility judge before most of conventional's third wording was judged (see Limits).

## What the chats show

A per-turn judge labels each deleted fact: whether the agent **asked** for it, whether the scientist **handed it over** in full or only **partly**, and whether it was **volunteered** (handed over in full before anyone asked). Rates are shares of the deleted facts, averaged over chats.

1. **The gain is in the answers, not in the questions.** For the three traits that count, the agent asks for 0.53–0.57 of the deleted facts, as with neutral (0.54). The scientist hands over 0.52–0.60 of them in full instead of 0.36, and partial answers fall from 0.23 to 0.09–0.12. Anxious also volunteers more: 0.16 of the deleted facts against 0.04 for neutral. Part of the gain replaces facts the agent would have filled in anyway: facts that reach the final spec without a full hand-over fall from 0.33 (neutral) to 0.24–0.29.
2. **Reply length and trait are not separated.** Across the 27 trait wordings, words per reply rank the effects (Spearman ρ = 0.77). A line of effect against log words per reply, fit on the other six traits and neutral, predicts 34–46% of each of the three gains, and 66–85% if disagreeable is left out of the fit. The extra words carry few deleted values: per 100 words, neutral states 7.2 deleted numeric values, anxious 2.4, outgoing and curious 3.6.
3. **The persona shows in the scientist's replies, much less on the agent's side.** A bag-of-words classifier, trained on two wordings of each trait and tested on the third wording and held-out cases, names which of the 9 traits a chat had in 88% of chats from the scientist's replies, 22% from the agent's questions and 19% from the final spec (chance 11%). A stronger decoder may find more ([decoding.json](decoding.json)).

SciConvBench scores facts recovered, so a persona can move its score by handing over more or less, or by changing what the agent asks. Traits that act on decisions, such as approving a plan or judging a result, need a task where the user makes them.

## Method

- **Task.** [SciConvBench](https://github.com/csml-rpi/SciConvBench) ([paper](https://arxiv.org/abs/2605.18630)), disambiguation mode: the agent gets a simulation request with some facts deleted. It may ask a simulated scientist, who holds the complete request, one question per turn for at most 10 turns, and then writes a final spec. Score: the share of deleted facts in the final spec, graded by the benchmark's own judge (`recovered_judge`).
- **Cases.** 62 foam (OpenFOAM) cases, none used in any pilot. Foam because there the neutral scientist is not at ceiling; in a pilot it reached 0.97 on fluids and 0.89 on materials cases.
- **Personas.** Every scientist shares one identity (a research scientist who needs the simulation for a grant report, in a busy week) and one set of rules: answer only from the complete request, never invent or change a value, say so when something is not in the notes, write like a chat. Each adds a personality paragraph, a one-sentence reaction to the situation, three example exchanges about unrelated tasks, and a one-line in-character reminder on every turn. 3 independent wordings per trait, 6 for neutral, tuned on pilot cases only ([personas.json](personas.json)). Calm (low neuroticism) failed the visibility check in two pilots and was dropped before the run.
- **Models.** GLM-5 on AWS Bedrock as agent, scientist and every judge, thinking off, temperature 0. 35 arms × 62 cases, one chat each; 2,167 of 2,170 chats ran, on September 28–29, 2026.
- **Analysis**, written before the run ([prereg.md](prereg.md)). Per trait, the effect is the mean over its 3 wordings minus the mean over the 6 neutral wordings, paired by case. The standard error includes the between-wording variance (estimated between-wording SD 0.02). Holm correction over the 9 traits at α = 0.05.
- **Visibility check.** A judge is shown the trait chat and the first neutral wording's chat on the same case. It must pick the trait chat as more like the trait (e.g. more anxious) in ≥ 75% of cases and as more like the opposite pole (e.g. more calm) in ≤ 25%, with the 95% binomial bound on the same side of 50%, pooled and for every wording.
- **Cost.** About $99: chats $47, grading $46, visibility judge $6.

## Limits

- One domain, one model family in every role, one chat per case and arm.
- Reply length is not controlled (finding 2).
- Reserved's texts and disorganised's paragraph describe how to write (clipped replies; typos and half-finished sentences), so their effects may partly be that instruction.
- Budget caps left gaps: 3 chats not run (agreeable wording 3, conventional wording 2, neutral wording 1); 46 of 62 chats with the all-facts scripted scientist not graded; for conventional wording 3, 53 of 62 visibility pairs and 58 of 62 opposite-pole pairs not judged. 1 neutral chat is ungraded because the judge's output did not parse. None changes which traits count.
- When the agent reaches the 10-turn cap it is asked for its final spec, with one retry if the output is not a spec; 12 final specs are still invalid after that.
- Finding 2 counts numeric values only. The final-spec decoding in finding 3 can also pick up the extra facts a persona gave, not only its style.

## Code and files

The harness lives on the branch [`persona-trait-study`](https://github.com/joverwiening/SciConvBench/tree/persona-trait-study) of a SciConvBench fork, not in upstream SciConvBench: commit [`4043a9af3`](https://github.com/joverwiening/SciConvBench/commit/4043a9af37c6b1591614b26724f9badf1660e006) is the code that ran, [`99cdd5578`](https://github.com/joverwiening/SciConvBench/commit/99cdd557897f3f4d658d71cea9ab9a95a36ad066) adds the analysis scripts (`persona/analysis/full1/`), and [run_commands.sh](run_commands.sh) lists the commands. Arm ids: `bf_<high|low>_<A|C|E|N|O>` (Big Five letter), `_w2`/`_w3` for wordings 2 and 3, `bf_neutral`, `bf_neutral_b`…`_f`, and `mute` / `oracle` for the two scripted scientists.

- [trait_effects.csv](trait_effects.csv): the results table, plus the finding-1 effects (`effect_asked`, `effect_delivered` = handed over in full, `effect_partial`, `effect_unasked_delivered` = volunteered).
- [arms.csv](arms.csv): all 35 arms; `grounded` / `silent` = facts in the final spec with / without a full hand-over.
- [chats.csv](chats.csv): one row per chat sent to grading (2,121; the ungraded neutral chat has an empty `recovered_judge`).
- [first_answers.csv](first_answers.csv): each scientist's first answer to the same first agent question on a case (`hg` = deleted numeric values stated).
- [decoding.json](decoding.json): the classifier in finding 3.
- [personas.json](personas.json), [cases.txt](cases.txt), [prereg.md](prereg.md): persona texts, the 62 case ids, the rules fixed before the run.

Full transcripts are not included.
