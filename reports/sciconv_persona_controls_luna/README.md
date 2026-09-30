# SciConv persona controls on GPT-6 Luna

This report tests whether researcher identities change how many deleted specification facts a SciConvBench agent recovers. It reports four linked studies, **759 scored episodes** run on September 28–29, 2026.

**Scope:**
- all runs use GPT-6 Luna in every role, under the `full_persona_v2` researcher settings;
- the primary outcome is the native judge's share of deleted facts recovered;
- infrastructure failures were retried once; no episode was rerun because of its score.

**Summary.**

1. **The v2 SciConv persona pattern does not replicate.**
   - In `full_persona_v2`, six personas passed both SciConv cases.
   - In 78 fresh episodes they did no better than personas that passed neither: +2.8 pp, persona-level permutation p = 1.00, 95% CI [−8.3, +13.9] pp.
2. **SciConv has usable mid-difficulty cases, but most sampled cases are at the ceiling.**
   - Of 40 newly sampled disambiguation cases, 17 recover over 90% of facts with persona off, and 11 single-fact cases can only pass or fail.
   - 11 multi-fact cases recover 36–69% of facts across 8 persona-off runs, and were confirmed as a test panel.
3. **No identity effect on the 11 confirmed cases.**
   - Personas 148 and 155 match persona off (−2.0 pp, p = 0.70).
   - Two neutral "ordinary researcher" identities do not lower recovery (+6.5 pp, p = 0.11).
4. **A pre-registered test found no effect of the neutral wording.**
   - `neutral_a`'s +10.7 pp lead over persona off (p = 0.027, post hoc) did not replicate in fresh runs (+2.1 pp, p = 0.66).
   - Removing its trait sentence ("…warm, organised, calm, sociable and open to new ideas…") changed nothing (−3.0 pp, p = 0.43).
   - Identical identity text scored 0.667 and 0.587 in two batches of 66 episodes. **Arm-level differences below roughly ±9 pp are within run-to-run noise at this size.**

## Relation to other work

- **`full_persona_v2`:** its 8-question ranking was largely determined by two binary SciConv outcomes. Study 1 tests the only between-persona pattern in it.
- **#12 (Big Five traits on SciConv `foam`, GLM-5):**
  - reports +14–15 pp recovery for anxious, outgoing and curious scientists against six neutral wordings;
  - that is larger than the noise band measured here;
  - it was not tested under Luna in this report.
- **#16 (DiscoveryBench):** found `neutral_a` +21.9 pp and `neutral_b` +3.0 pp. Study 4 tests the same pattern on SciConv with fresh episodes.
- **#9 (BixBench CHIP pilot):** also found no persona separable from run-to-run variation.

## Common setup

- **Code:** `75e3f08` for every run, before #6 (`fb2d8c1`).
  - `configs/full_persona_v2/shared.json` at that commit sets `unrestricted_knowledge: true`. SciConv's native simulated-user prompt then receives v2's five edits in every arm, persona off included.
  - After #6, those edits are the three separate switches `unrestricted_knowledge`, `embody_identity` and `volunteer_information`, and identity arms also receive `PERSONA_BOUNDARY`.
  - **Exact reproduction of the identity arms therefore requires `75e3f08`.** Persona-off arms reproduce on current `main`.
- **Models:** `openai/gpt-6-luna`, reasoning effort `none`, for actor, simulated researcher and judge.
- **Injection:** identity text reaches the simulated researcher only. This was verified in the recorded API requests of all 759 episodes:
  - no actor or judge request contains identity text (534/534 identity-arm episodes);
  - no persona-off request contains identity text (225/225);
  - in 530 identity-arm episodes the researcher's requests carry the identity;
  - in the remaining 4 the actor submitted without asking, so the researcher was never called. These are kept as scored episodes.
- **Profiles:** personas 148 and 155 use the exact published `full_persona_v2` profiles, hash-checked. Neutral identities are in [identities/](identities/).
- **Source:** SciConvBench at `8d1528e`.
- **Retries:** 8 of 78 Study 1 episodes failed on the OpenAI tokens-per-minute limit at parallel 4 and were rerun once at parallel 2. No other study needed retries.
- **Cost:** GPT-6 Luna cost **$1.60** across all attempts.

| Study | Runs | Cost |
|---|---:|---:|
| 1 | 78 | $0.29 |
| 2 | 120 | $0.16 |
| 3 confirmation | 55 | $0.11 |
| 3 neutral arms | 198 | $0.44 |
| 4 | 308 | $0.61 |

## Study 1: does the v2 SciConv pattern replicate?

**Design.**
- **Arms:**
  - persona off;
  - the six personas that passed both v2 SciConv cases (050, 055, 148, 155, 228, 259);
  - six drawn with seed `20260928` from the thirteen that passed neither (224, 132, 039, 001, 026, 003).
- **Runs:** `solMech/disambiguation/case_104` and `foam/disambiguation/case_020`, 3 fresh episodes per arm and case (78 total).
- **Outcome:** native pass/fail FRR, as in v2.

| Case | Persona off | v2 both-pass | v2 neither-pass | v2 single run |
|---|---:|---:|---:|---|
| `solMech` 104 | 3/3 | 15/18 | 15/18 | personas 16/30; off 1/1 |
| `foam` 020 | 2/3 | 1/18 | 0/18 | personas 7/30; off 0/1 |

**Results.**
- **The groups do not differ:**
  - both-pass minus neither-pass: +0.028 (persona-level permutation p = 1.00; bootstrap 95% CI [−0.083, +0.139]);
  - question-limit hits: 5 vs 6;
  - the SciConv code path is unchanged from the v2 run.
- **Post hoc:** on `foam`, persona off passed 2/3 and all personas together 1/36 (Fisher p = 0.012).
  - Of the 35 persona `foam` failures, 34 lost specification facts (`FR = 0`) and 34 failed the intent gate; 33 failed both.
  - Study 3 shows this contrast does not generalise.

## Study 2: difficulty screen

**Design.** 40 disambiguation cases, 8 per domain (fluids, PDE, matSci, solMech, foam).
- **Sampling:** seed `20260929-<domain>`; the Astra campaign's 40 tasks and the two Study 1 cases were excluded.
- **Runs:** persona off × 3 each (120 episodes).

| Pass/fail band | Cases | Recovery-share band | Cases |
|---|---:|---|---:|
| Ceiling (3/3) | 22 | Near ceiling (> 0.9) | 17 |
| Mid (1–2/3) | 9 | **Multi-fact, 0.3–0.9** | **11** |
| Floor (0/3) | 9 | Single fact | 11 |
| | | Low (< 0.3) | 1 |

- **Why recovery share is the measure to use:** pass/fail undersells multi-fact cases. Six `foam` candidates never pass yet recover 33–73% of facts.
- **Candidates:** the 11 multi-fact cases in the 0.3–0.9 band.
- **Question limit:** 4 of 120 episodes hit it: `foam/039` (2), `foam/032` (1) and `foam/023` (1). The first two are candidates.
- **Overlap with #12:** five of our eight `foam` cases are in #12's 62. On the four overlapping multi-fact cases, Luna persona off recovers 0.48–0.73 and #12's GLM-5 neutral arms 0.69–0.87, so both models put these cases in the mid range.

## Study 3: confirmation and neutral arms

**Confirmation.**
- **Runs:** 5 more persona-off episodes per candidate, 8 per case in total.
- **Rule:** keep a case if its mean recovery is within [0.25, 0.90].
- **Result:** all 11 were kept, with means from 0.36 (`foam/077`) to 0.69 (`fluids/016`, `matSci/031`), and every case varies between runs.
- **Cases:** foam 009, 030, 032, 039, 048, 070, 077; matSci 031, 071; fluids 016; solMech 036.

**Neutral arms.**
- **Runs per case:** `neutral_a` × 6, `neutral_b` × 6, persona 148 × 3, persona 155 × 3 (198 episodes), against the 8 persona-off runs.
- **Neutral texts:** written for #8 and reused unchanged in #16. They describe an ordinary researcher with no distinctive traits.
- **Test:** case-stratified permutation, each case weighted equally, 20,000 permutations, two-sided.

| Arm | Mean recovery | Episodes |
|---|---:|---:|
| Persona off | 0.559 | 88 |
| `neutral_a` | 0.667 | 66 |
| `neutral_b` | 0.582 | 66 |
| Persona 148 | 0.541 | 33 |
| Persona 155 | 0.538 | 33 |

| Contrast | Difference | p |
|---|---:|---:|
| Neutral (a+b) − persona off | +0.065 | 0.109 |
| Personas (148+155) − persona off | −0.020 | 0.698 |
| `neutral_b` − `neutral_a` | −0.085 | 0.086 |
| Personas − neutral | −0.085 | 0.052 |
| 148 − persona off | −0.018 | 0.771 |
| 155 − persona off | −0.021 | 0.741 |
| `neutral_a` − persona off (post hoc) | +0.107 | 0.027 |
| `neutral_b` − persona off (post hoc) | +0.022 | 0.652 |

Nothing survives correction for these eight comparisons.

**Question-limit hits.** The native loop drops the 10th answer, which could bias arm comparisons.
- **How often:** 9–33% of panel episodes per arm hit the 10-question limit (persona 148 9%, persona 155 33%, all other arms 15–21%).
- **Sensitivity check:** excluding them leaves the conclusions unchanged. Neutral − persona off is +0.057 (p = 0.163), and personas − persona off is −0.022 (p = 0.695).

## Study 4: pre-registered paraphrase test

The [pre-registration](prereg_paraphrase.md) was written before this run. It tests whether `neutral_a`'s trait sentence explains its lead.

**Design.**
- **Arms:** two wordings, each with the trait sentence and with it replaced by a length-matched non-trait filler:
  - `neutral_a` / `neutral_a_swap`, 334 and 332 characters;
  - `neutral_c` / `neutral_d`, 316 and 289 characters.
- **Runs per case:** 6 of each arm, plus 4 fresh persona-off runs (12 in total per case). 308 episodes.
- **Freshness:** earlier `neutral_a` episodes are excluded, so H2 is a fresh replication.

| Arm | Mean recovery | Episodes |
|---|---:|---:|
| Persona off | 0.566 | 132 |
| `neutral_a` (fresh) | 0.587 | 66 |
| `neutral_a_swap` | 0.599 | 66 |
| `neutral_c` | 0.579 | 66 |
| `neutral_d` | 0.627 | 66 |

| Pre-registered test (each needs p < 0.025) | Difference | p | Verdict |
|---|---:|---:|---|
| H1: trait sentence (a, c) − filler (a_swap, d) | −0.030 | 0.430 | not supported |
| H2: fresh `neutral_a` − persona off | +0.021 | 0.657 | not supported |

- **Secondary contrasts:** all have |difference| ≤ 0.061 and p ≥ 0.19.
- **Question-limit sensitivity:** excluding limit-hit episodes gives H1 −0.052 (p = 0.186) and H2 +0.028 (p = 0.525). Neither is supported.
- **Noise across batches:** `neutral_a` scored 0.667 in Study 3 and 0.587 here with the same text and 66 episodes each. Six bland-identity arm means across the two studies span 0.579–0.667.

## What can we learn?

1. **Single-run persona labels are not reliable on SciConv.** The v2 both-pass/neither-pass split carries no information in fresh runs.
2. **Choose SciConv cases by recovery share and screen them first.**
   - Most sampled cases recover almost all facts with persona off.
   - Pass/fail hides mid-range multi-fact cases, which are where an identity could change what is disclosed.
3. **Neither full profiles nor neutral identities moved recovery on the confirmed panel.** An identity per se does not degrade the v2 simulator. The `foam/020` contrast in Study 1 was case-specific or chance.
4. **Wording and sampling noise is about ±9 pp per arm at 66 episodes.**
   - Persona claims need several neutral paraphrases as a reference band and fresh replication.
   - A single neutral control, or combined post hoc results, can mislead. That is how the `neutral_a` lead arose here and, possibly, in #16.

## Limitations

- **Model:** GPT-6 Luna only, at reasoning `none`. The Astra campaign and #12 (GLM-5) use other models.
- **Scope:**
  - Only SciConv disambiguation cases.
  - The panel has 11 cases, 7 of them from `foam`.
  - Personas 148 and 155 have 3 episodes per case.
- **Grading:** the outcome comes from the native LLM judge. Judge variation is part of the measured noise.
- **Settings:** the v2 simulator prompt edits apply in every arm. Results under native SciConv settings (all #6 switches off) or with #6's `PERSONA_BOUNDARY` may differ.

## Reproduce

These commands need a checkout of `75e3f08` for the identity arms, the pinned SciConvBench source and an `.env` with `OPENROUTER_API_KEY`. Run at parallel 2–5, depending on the provider's tokens-per-minute limit.

```bash
.venv/bin/python -m personasciencebench --source-root <sources> prepare --selection <cases.json> \
  --benchmarks sciconvbench --cases-per-benchmark <N> --output prepared/<name>
.venv/bin/python scripts/run_sciconv_persona_rerun.py --output runs/<study1>              # Study 1
.venv/bin/python scripts/run_sciconv_difficulty_screen.py --output runs/<study2>          # Study 2
.venv/bin/python scripts/run_sciconv_arms.py --output runs/<study3> --prepared prepared/<11 cases>/pilot_manifest.json \
  --arms persona_off=5 --neutral-dir reports/sciconv_persona_controls_luna/identities                      # confirmation
.venv/bin/python scripts/run_sciconv_arms.py --output runs/<study3b> --prepared prepared/<11 cases>/pilot_manifest.json \
  --arms neutral_a=6 neutral_b=6 candidate_148=3 candidate_155=3 --neutral-dir reports/sciconv_persona_controls_luna/identities
.venv/bin/python scripts/run_sciconv_arms.py --output runs/<study4> --prepared prepared/<11 cases>/pilot_manifest.json \
  --arms neutral_a=6 neutral_a_swap=6 neutral_c=6 neutral_d=6 persona_off=4 --neutral-dir reports/sciconv_persona_controls_luna/identities
python3 scripts/report_sciconv_persona_controls.py --rerun runs/<study1> --screen runs/<study2> \
  --confirm runs/<study3> --neutral runs/<study3b> --paraphrase runs/<study4> --output reports/sciconv_persona_controls_luna
```

- **Case lists:** the case IDs of Studies 2–4 are in `summary.json`.
- **Prepared-manifest paths:** Study 1 and Study 2 read theirs from fixed paths (`prepared/sciconv-persona-rerun`, `prepared/sciconv-difficulty-screen`).

## Files

- [results.json](results.json) and [results.csv](results.csv): all 759 episodes. Each row has study, arm, case, repeat, status, whether it was a retry, FRR, FR, intent capture, facts recovered and total, recovery share, researcher replies, question-limit hit, tokens and cost.
- [summary.json](summary.json): per-study status counts, retries, costs, question-limit hits by arm, the limit-hit sensitivity analysis and every statistic in this README, regenerated deterministically from fixed seeds.
- [runtime_config.json](runtime_config.json): code revision, config, models, identity hashes, seeds, driver hashes and source pin.
- [prereg_paraphrase.md](prereg_paraphrase.md): the Study 4 pre-registration.
- [identities/](identities/): `neutral_a` and `neutral_b` (from #8/#16), and `neutral_a_swap`, `neutral_c` and `neutral_d` (written for Study 4).
- Scripts:
  - [`scripts/run_sciconv_persona_rerun.py`](../../scripts/run_sciconv_persona_rerun.py)
  - [`scripts/run_sciconv_difficulty_screen.py`](../../scripts/run_sciconv_difficulty_screen.py)
  - [`scripts/run_sciconv_arms.py`](../../scripts/run_sciconv_arms.py)
  - [`scripts/report_sciconv_persona_controls.py`](../../scripts/report_sciconv_persona_controls.py)

Raw API records, conversations and native evaluator references are not included; SciConv conversations contain the reference specification.

## Sources

- [SciConvBench](https://github.com/csml-rpi/SciConvBench) at `8d1528ed86b54cb4437f8f921e0f396511acd104`, as pinned in `manifests/sources.json`.
- Persona profiles: the published `full_persona_v2` identities (`configs/full_persona_v2/cohort.json`).
