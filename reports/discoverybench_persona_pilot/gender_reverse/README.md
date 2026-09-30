# Gender swap, man → woman (and both directions combined)

Run 2026-09-30. **225/225 cells have an outcome (220 scored, 5 missing submissions)** after
one logged retry of 4 episodes whose actor or judge lost its connection
(`RemoteProtocolError`; originals kept as attempt 1). $1.54 at list price. Personas 089 (English),
026 (Spanish) and 147 (Japanese): the three profiles recorded as men whose only gender-coded line
is `Gender identity: Man` (001 and 039 also carry a "Traditional gender roles" attitude line and were
excluded). Their languages mirror the woman → man set (148 English, 046 Spanish, 155 Mandarin). Same
five tasks, 5 repeats, direct `gpt-6-luna` (reasoning `none`). [Generated report](REPORT.md) ·
[results](results.csv) · [exact changes](variant_changes.json) · [config](../configs/gender_reverse.json).

**Findings (exploratory):**

1. **No detectable gender effect on score.** Man → woman: +3.5 pp pooled (95% CI −5.2 to +11.8,
   p = 0.47). Both directions combined, woman − man: +5.2 pp (CI −0.8 to +11.0, p = 0.13). The
   placebo (same lines reordered) moved the score +11.3 pp here (p = 0.017), so single-run
   references remain noisy.
2. **A possible effect on answer length, not yet established.** With the gender line set to
   "Woman", actors submitted longer hypotheses: +239 characters in this run (p = 0.017), and +136
   characters combining both directions (CI +42 to +235, p = 0.014), in the same direction in both
   runs (woman → man: the man version −32 characters, p = 0.60). The placebo barely moved length
   (−3.5 characters, p = 0.95). **The difference is a tail, not a shift:** median length hardly
   changed (350 → 369), but 10 of 73 swapped episodes exceeded 1,000 characters against 3 of 74
   unchanged and 2 of 73 reordered (one-sided Fisher p = 0.037). The tail appears for all three
   personas (4, 3, 3), half on the immigration task, and those long answers scored lower (5 vs 26).
3. **The researcher's visible behavior did not change.** Gendered words stayed under 0.3 per
   episode in every arm; researcher message length (2,073 vs 2,095 characters), handoffs (2.75 vs
   2.75) and requests for detailed results were unchanged. How a one-word identity change would
   lengthen the actor's answers is therefore unexplained.

Treat finding 2 as a lead: it is one of many comparisons across these runs, rests on a minority of
long answers, and the two directions ran on different personas and different transports (below).
A confirmatory test would fix the measure in advance (share of hypotheses above 1,000 characters),
use new tasks, and run both directions on one transport.

## Both directions

| Measure (woman − man) | Woman → man run (148, 046, 155) | Man → woman run (089, 026, 147) | Combined (30 persona × task strata) |
|---|---:|---:|---:|
| Score | +6.8 pp (p = 0.15) | +3.5 pp (p = 0.47) | +5.2 pp, CI −0.8 to +11.0, p = 0.13 |
| Hypothesis characters | +32 (p = 0.60) | +239 (p = 0.017) | +136, CI +42 to +235, p = 0.014 |

Signs are shown as woman − man in both columns, so the woman → man run's reported "man − woman"
deltas (−6.8 pp, −32) are reversed here.

| Man → woman run (mean per episode) | Unchanged (man) | Gender-swapped (woman) | Reordered |
|---|---:|---:|---:|
| Native score | 19.3 | 22.8 | 30.5 |
| Hypothesis characters (median) | 408 (350) | 617 (369) | 397 (347) |
| Numbers in hypothesis | 4.1 | 8.8 | 5.3 |
| Hypotheses > 1,000 characters | 3 / 74 | 10 / 73 | 2 / 73 |
| Researcher characters | 2,076 | 2,092 | 2,010 |

## Differences between the two runs

- **Personas:** different people (all recorded women vs all recorded men); the combined estimate
  asks whether the gender line matters on average, not how one persona changes in both directions.
- **Transport:** the woman → man run used an earlier Chat Completions client; this run used
  `main`'s `openai_transport.py` (Responses API) on the rebased #16 code (commit `92a22ca`).
  Within-run contrasts share a transport; the cross-run comparison does not.
- **Retries:** this run's four connection failures were retried once with the dropped-connection
  retry added to #14; `--retry-errors` retries only infrastructure failures and judge errors whose
  recorded cause is transport, never low or missing outcomes.
