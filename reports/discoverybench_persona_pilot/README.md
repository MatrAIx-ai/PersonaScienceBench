# DiscoveryBench persona pilot

Run 2026-09-29. **125/125 pilot episodes plus a 25-episode replication finished (124 scored, 1 missing submission, no infrastructure
failures)**; three full-profile personas, persona off and a neutral identity, five repeats each,
on five screened DiscoveryBench tasks. Actor, researcher and judge were direct OpenAI `gpt-6-luna`
(reasoning `none`). Cost $0.76 at list price (the provider reports tokens, not cost).

**Main findings (descriptive; the neutral result was then tested by a replication):**

1. **No persona differed detectably from persona off.** 148: +10.3 pp (95% CI −4.7 to +25.0);
   046: +4.1 pp; 155: +2.6 pp; all permutation p ≥ 0.23.
2. **The neutral-identity score gain did not replicate.** `neutral_a` scored +21.9 pp over persona
   off (CI +6.2 to +36.2, p = 0.015, uncorrected). Its paraphrase `neutral_b`, run afterwards on the
   same tasks and settings ([replication](#replication-neutral_b)), scored +3.0 pp (CI −12.2 to +18.4,
   p = 0.72), and **−18.9 pp below `neutral_a` (p = 0.042)**. Two wordings of the same ordinary
   identity differ by as much as the original "effect", so the `neutral_a` result is best read as
   wording-specific or chance, and ~20 pp is the practical placebo band for single-arm contrasts here.
4. **One behavioral effect is robust: any identity shortens the submitted hypothesis.** All four
   identity arms (three personas, two neutral texts) submitted hypotheses of 326–408 characters with
   2–5 numbers, versus 654 characters and 11 numbers under persona off. This changed the answers, not
   the collaboration structure, and it did not reliably change the score.
3. **Scores are noisy.** The persona-off run-to-run SD averages 21.5 pp per task; the same
   condition scores 0 in one run and 100 in the next on the biology tasks.

The [generated report](REPORT.md) has every table (by arm, task, domain, condition, behavior,
uncertainty); [results.csv](results.csv) has one row per episode; [summary.json](summary.json)
records code revision, configs, persona and config hashes, models and statuses.

## Where the neutral difference comes from

| Measure (mean per episode) | persona off | neutral_a | 148 | 046 | 155 |
|---|---:|---:|---:|---:|---:|
| Native score | 0.21 | 0.43 | 0.31 | 0.25 | 0.24 |
| Context recall (native sub-score) | 0.64 | 0.92 | 0.76 | 0.64 | 0.64 |
| Submitted hypothesis, characters | 654 | 367 | 408 | 374 | 326 |
| Numbers in the hypothesis | 11.3 | 4.3 | 5.4 | 3.5 | 2.2 |
| Actor commands | 4.8 | 4.9 | 4.9 | 4.8 | 4.7 |
| Result-review revision requests | 0 | 0 | 0 | 0 | 0 |

The neutral gain is almost entirely **context recall**: whether the judged hypothesis states the
reference's population and conditions. Every identity arm led to much shorter, less numeric
hypotheses than persona off, but the personas did not gain recall, so brevity alone does not
explain it. Researchers never requested a revision in any arm; the workflow was almost always
inspect → approve → result → stop, so the arms differ in the wording of two or three researcher
messages, not in the structure of the collaboration.

**The instruction text is not a confound:** with `embody_identity` the "embody the supplied
identity, if any" instruction is present in every arm, including persona off; only the identity
block differs. Whether the effect belongs to *an ordinary identity* or to *this wording* is
untested: `neutral_b` (a paraphrase, `configs/persona_controls/neutral_b.txt`) is the direct check.

## Replication: neutral_b

Run 2026-09-29 after the pilot: `neutral_b` × the same 5 tasks × 5 repeats, same code path, models,
knowledge policy and seed ([config](configs/neutral_b.json), [report](neutral_b/REPORT.md),
[results](neutral_b/results.csv)); 25/25 scored, $0.13. Compared with the pilot's own persona off
and `neutral_a` arms.

| Task | neutral_b | neutral_a | persona off |
|---|---:|---:|---:|
| introduction_pathways / metadata_0 | 52 | 73 | 52 |
| introduction_pathways / metadata_2 | 21 | 76 | 28 |
| nls_incarceration / metadata_11 | 23 | 31 | 26 |
| nls_raw / metadata_7 | 11 | 25 | 0 |
| immigration_offshoring / metadata_0 | 13 | 10 | 0 |

| Contrast | Δ (pp) | 95% CI | Permutation p |
|---|---:|---:|---:|
| neutral_b − persona off | +3.0 | −12.2 to +18.4 | 0.720 |
| neutral_a − persona off | +21.9 | +6.2 to +36.2 | 0.015 |
| neutral_b − neutral_a | −18.9 | −33.5 to −3.3 | 0.042 |
| both neutral texts pooled − persona off | +12.5 | −1.3 to +25.8 | 0.105 |

`neutral_b` kept the short-hypothesis behavior (341 characters, 2.9 numbers) but not the context
recall gain (0.68 vs 0.92 for `neutral_a` and 0.64 for persona off).

## Counterfactual follow-up: gender swap and opposite attribute

[300 more episodes](counterfactual/README.md) (2026-09-29, $1.78) varied single profile lines of
personas 148, 046 and 155. Gender swap (Woman → Man): pooled −6.8 pp (p = 0.15); mirroring
"Speed vs accuracy": −7.6 pp (p = 0.12); reordering the same lines (placebo): −4.7 pp (p = 0.32).
No single-line change produced an effect distinguishable from rewording, and the researcher never
raised gender. See the [gender-swap audit](counterfactual/README.md#gender-swap-audit).

The reverse direction, [man → woman](gender_reverse/README.md) (personas 089, 026, 147; 225 more
episodes, 2026-09-30, $1.54), also showed no score effect (woman − man over both directions:
+5.2 pp, p = 0.13). It did show a possible answer-length effect: +136 characters with the woman
label (p = 0.014), carried by occasional very long hypotheses. This is exploratory and not yet
confirmed.

## Design

- **Task screen** ([screen/REPORT.md](screen/REPORT.md)): persona off × 2 on 12 deterministic
  candidates ([selection rationale](configs/candidates.json)) across biology, humanities,
  sociology and economics. Seven scored 0 in both runs, including all three archaeology tasks, so
  the pilot uses the five with off-floor baselines: biology 2, sociology 2, economics 1.
  **Humanities has no usable task** in this screen; conclusions do not extend to it.
- **Conditions:** `persona` (published full_persona_v2 profiles 148, 046, 155, injected
  verbatim), `persona_off` (no identity) and `neutral` (`neutral_a`, an ordinary-researcher
  identity). Everything else (tasks, models, budgets, knowledge policy, instructions) is shared.
- **Analysis:** repeats averaged within arm × task, then over tasks; missing submissions count as
  0; task-stratified permutation tests and bootstrap intervals.
- **Reproduce:** `scripts/run_persona_pilot.py plan --config configs/pilot.json …` then `run`;
  see [docs/persona_pilots.md](../../docs/persona_pilots.md). Raw API records, events, submissions
  and evaluator records are retained locally under the ignored `runs/discoverybench-pilot/`.

## Limitations

Five tasks from three domains, one model for all three roles, and the native DiscoveryBench
LLM judge (reference agreement, not verified analysis). No correction for multiple comparisons.
The screen and pilot used different repeats of persona off; the pilot's own 25 are used for all
comparisons here.

## Next checks

1. Done: `neutral_b` did not reproduce the `neutral_a` gain (see above).
2. Treat wording noise as the reference for persona claims: include both neutral texts and
   reordered twins (PR #8) in future pilots, and more tasks per domain, before any claim about
   persona effects on score.
3. A behavior-focused comparison (language, pushback, approval), which this protocol barely
   exercised: no revision requests occurred in any arm.
