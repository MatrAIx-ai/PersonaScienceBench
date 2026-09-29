# Persona controls

A gap between a persona run and the persona-off run is only a persona effect if it is larger than the
gap you get from rewording the prompt alone. The arms below measure that noise; the post-hoc scripts check a finished run. All are off by default;
default builds and prompts are unchanged.

## Arms (`scripts/run_persona_benchmarks.py`, fresh build only)

| Flag | Arms | Measures |
|---|---|---|
| `--control-reps N` | `persona_off`, `persona_off_r2`, … | run-to-run spread with no persona |
| `--twins N` | `<persona>__reordered` for N seeded personas | the same profile with its bullet lines shuffled within each section: noise from wording alone |
| `--neutral-arms` | `neutral_a`, `neutral_b` | an identity describing an ordinary researcher, in two paraphrases (`configs/persona_controls/`) |
| `--bound-arms` | `floor_mute`, `ceiling_oracle` | scripted researcher, no model calls. Mute gives nothing beyond the public brief; oracle gives every researcher fact in its first message. In SciConv, mute always gives the native fallback answer and oracle starts the agent from the complete requirement |
| `--truthful-history` | all arms | the researcher may not claim it already gave information it did not give |

Arm roles are in `src/personasciencebench/arms.py`. Reordered, neutral and scripted arms never enter
persona rankings. `REPORT.md` gets a **Noise floor** section per benchmark: control SD, reordered minus
source, neutral_b minus neutral_a, mute and oracle means, and how many personas fall outside the range
spanned by the reordered and neutral contrasts (the "placebo band"). The band is descriptive, not a test.

Traps:
- ExpBench builds its researcher itself: it takes `truthful_history`, rejects a scripted
  `researcher_policy`, and gets no mute/oracle jobs (`bounds_skipped` in the manifest).
- The scripted researcher stops at the first result review, unless the result failed the submission
  contract; then it asks for a revision while requests remain.

## Post-hoc scripts (read a finished run; every one needs `--budget-usd`)

```
python scripts/judge_persona_visibility.py --run runs/<run> --budget-usd 2 [--k 4] [--dry-run]
python scripts/score_sciconv_items.py      --run runs/<run> --budget-usd 2 [--dry-run]
python scripts/replay_fixed_agent.py       --run runs/<run> --budget-usd 5 [--reference persona_off] [--dry-run]
python scripts/score_sciconv_items.py      --run runs/<run> --budget-usd 2 --replay
```

- **Visibility judge**: sees only what the researcher wrote and k profiles (the episode's own plus
  k−1 seeded distractors, and "none fits better"), picks one. Hit rate vs 1/k with an exact binomial p,
  per persona and benchmark. A persona the judge cannot pick out cannot be the cause of a gap.
  Output: `<run>/persona_visibility/`.
- **SciConv per-item scores**: per missing entity, whether the agent asked for it, whether the
  researcher gave it (full or partial, verbatim evidence required), whether it was given unasked, and
  whether the final specification recovered it (from the native judge's `recovered_entities`).
  Output: `<case>/item_scores.json`, `<run>/sciconv_items/`.
- **Replay**: every arm answers the exact agent messages of one reference episode. SciConv replays the
  whole question sequence (each arm's own replies form its history); active-researcher tasks replay
  each decision point as a one-step counterfactual with the reference history. The reference arm is
  replayed too, so its self-replay is the noise baseline. ExpBench and terminal tasks are skipped.
  Output: `<run>/replay/`. `--replay` points the two scorers at it.

Budget: calls stop once the summed `usage.cost` reaches the budget; a response without cost fails
unless `--price-in/--price-out` (USD per M tokens) are given. With several workers, spend can pass the
budget by the calls already in flight. `--dry-run` counts calls and estimates tokens without calling.
