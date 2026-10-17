# Pre-registration: neutral paraphrase / trait-clause test (written before the run, 2026-09-29)

## Motivation

`neutral_a` exceeded persona off on SciConv (+10.7 pp recovery, p = 0.027, post hoc; 9/11 cases) and on DiscoveryBench in PR #16 (+21.9 pp). `neutral_b` did not in either. `neutral_a` contains an explicit trait sentence: "You are about as warm, organised, calm, sociable and open to new ideas as most people, and you communicate the way most colleagues do."

## Hypotheses

- **H1, primary (trait clause):** identities with the trait sentence (`neutral_a`, `neutral_c`) recover more deleted facts than the same identities with the sentence replaced by a length-matched non-trait filler (`neutral_a_swap`, `neutral_d`).
- **H2, replication:** fresh `neutral_a` episodes exceed persona off.

## Arms (identity texts in [identities/](identities/), SHA-256 recorded in the run manifest)

| Arm | Text | Trait sentence | Characters |
|---|---|---|---:|
| `neutral_a` | PR #8/#16 original | yes | 334 |
| `neutral_a_swap` | `neutral_a` with the trait sentence replaced by filler | no | 332 |
| `neutral_c` | new wording; trait sentence "Like most researchers, you are moderately friendly, organised, even-tempered, outgoing and curious, and you talk with collaborators the way most colleagues do." | yes | 316 |
| `neutral_d` | `neutral_c` with the trait sentence replaced by the same filler | no | 289 |
| `persona_off` | none | — | — |

Filler sentence: "You work on the kinds of problems that are standard in your area and use the same methods, tools and routines as most of your peers."

## Design

- **Cases:** the same 11 confirmed SciConv disambiguation cases.
- **Runs per case:** `neutral_a`, `neutral_a_swap`, `neutral_c` and `neutral_d` × 6 each; persona off × 4 fresh. The 8 existing persona-off runs per case are pooled for the persona-off baseline; the earlier `neutral_a` runs are *not* pooled, so H2 is a fresh replication.
- **Total:** 308 episodes.
- **Settings:** frozen v2 settings, GPT-6 Luna, reasoning `none`, parallel 5. Infrastructure failures get one logged retry; there are no score-based reruns.
- **Outcome:** share of deleted facts recovered (native judge).
- **Tests:** case-stratified permutation, each case weighted equally, 20,000 permutations, two-sided.
  - **H1:** mean of (`neutral_a`, `neutral_c`) minus mean of (`neutral_a_swap`, `neutral_d`), pooled within case.
  - **H2:** fresh `neutral_a` minus persona off (all 12 runs per case).
  - **Secondary (descriptive):** each arm vs persona off; `neutral_a` − `neutral_a_swap`; `neutral_c` − `neutral_d`.
- **Decision rule:** with two primary tests, each needs p < 0.025 (Bonferroni) to be called supported.

> Publication note: this is the pre-registration as written before the run; only the identity-file location above was changed for publication. Results are in the [README](README.md), Study 4.
