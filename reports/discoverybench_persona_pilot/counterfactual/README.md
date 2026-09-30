# Counterfactual personas: gender swap and opposite attribute

Run 2026-09-29. **300/300 episodes finished (298 scored, 2 missing submissions, no infrastructure
failures)**, $1.78 at list price. Personas 148, 046 and 155 on the five pilot tasks, 5 repeats per
arm, direct OpenAI `gpt-6-luna` (reasoning `none`) for actor, researcher and judge, same settings as
the [pilot](../README.md). [Generated report](REPORT.md) · [per-episode results](results.csv) ·
[exact changes](variant_changes.json) · [config](../configs/counterfactual.json).

**Findings (descriptive):**

1. **No detectable gender-swap effect.** Changing only "Gender identity: Woman" to "Man" moved the
   pooled score by −6.8 pp (95% CI −15.1 to +1.5, p = 0.15), within the wording-noise reference:
   reordering the same profile's lines moved it by −4.7 pp (p = 0.32). The researcher did not bring
   gender into the collaboration (under one gendered word per episode in every arm, no more after the
   swap), and researcher message length, handoffs and hypothesis length did not change.
2. **No detectable pooled effect of mirroring "Speed vs accuracy":** −7.6 pp (CI −16.3 to +0.9,
   p = 0.12). Persona 155 alone dropped −19.6 pp (p = 0.025), or −15.0 pp (p = 0.04) against both of
   its unchanged runs; that is 1 of 24 comparisons at p < 0.05, about what chance predicts, and not a
   finding without replication.
3. **Wording and run-to-run noise dominate.** The same unchanged persona scored −4.4, −2.9 and
   +9.3 pp differently in the pilot and in this run; reordered twins changed plan-review counts as
   much as the real swaps (148: 1.04 → 1.80). Persona text is followed in style, but single-line
   changes did not produce effects larger than rewording on these tasks.

## Design

| Arm per persona | Change (verified to be exactly one line, or a pure reordering) |
|---|---|
| unchanged | none, re-run alongside the variants |
| `gender_swap` | line 6, `Gender identity: Woman` → `Man` (the only gender-coded line in each profile) |
| `speed_accuracy_flip` | mirror on the five-point scale: 148, 155 `Accuracy first` → `Speed first`; 046 `Speed-leaning` → `Accuracy-leaning` |
| `reordered` | bullets shuffled within sections; same content (the placebo for wording) |

Contrasts compare each variant with its own unchanged persona, task-matched; pooled rows stratify by
persona × task (75 vs 75 episodes). p values are permutation tests within strata, uncorrected for the
24 comparisons in the report.

## Gender-swap audit

| Persona | Unchanged | Gender-swapped | Δ (pp) | 95% CI | p |
|---|---:|---:|---:|---:|---:|
| 148 | 27.0 | 21.7 | −5.3 | −20.2 to +10.3 | 0.54 |
| 046 | 22.3 | 21.1 | −1.3 | −14.5 to +11.8 | 0.89 |
| 155 | 33.1 | 19.2 | −13.9 | −27.0 to −1.1 | 0.08 |
| Pooled | | | −6.8 | −15.1 to +1.5 | 0.15 |
| Reordered twins, pooled (reference) | | | −4.7 | −12.7 to +3.4 | 0.32 |

| Behavior (mean per episode) | Unchanged | Gender-swapped |
|---|---:|---:|
| Researcher characters | 1,898 | 1,901 |
| Handoffs | 2.31 | 2.28 |
| Submitted hypothesis characters | 402 | 371 |
| Numbers in hypothesis | 5.0 | 3.7 |

Persona 155's unchanged arm ran high in this run (33.1, versus 23.8 in the pilot), which inflates
all three of its contrasts; against both unchanged runs its gender-swap difference is −9.3 pp (p = 0.18).

**Scope:** all three personas are recorded as women, so this tests woman → man only, on one model,
five DiscoveryBench tasks and a reference-agreement judge. A null result here does not show the absence
of gender effects elsewhere. The man → woman direction was run next with personas recorded as men:
see [gender_reverse](../gender_reverse/README.md) (score: no detectable effect; answer length: a
possible effect, still to be confirmed).
