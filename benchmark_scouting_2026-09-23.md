# PersonaScienceBench: benchmark scouting (2026-09-23)

## Relation to `benchmark_candidates.md`

This report complements `benchmark_candidates.md` rather than replacing it. The two documents rank the same benchmarks through different lenses:
- `benchmark_candidates.md` asks how well a benchmark supports a **simulated researcher steering a multi-turn collaboration**.
- This report asks how **measurably a persona changes the correct outcome**, preferably under a deterministic verifier.

Some ratings therefore differ. BixBench3 and AstaBench E2E rate very high there, but lower here because of cost, licensing and judge-only grading. Which lens matters more depends on the persona-placement decision at the end of this report.

## How this was made

- Three web-research agents read papers, READMEs and dataset cards. Nothing was cloned or downloaded.
- I spot-checked the core facts of the top candidates against the primary pages:
  - TB-Science: 70 tasks, Apache-2.0.
  - DiscoveryBench: 264 real tasks (25/239), ODC-BY, not gated.
  - BixBench: 205 Qs / 60 capsules, Apache-2.0, 24-48 h full agentic run.
  - BioML-bench: MIT, 5 domains, submission-file grading.
- All confirmed. SOTA numbers and costs come from the agents' reads and are **not** independently re-checked. Treat them as approximate.

## Scoring

- **Persona sensitivity (Sens., 1-5):** does the task leave choices open that persona attributes (A-H, plus any attributes added later) would pin, so the correct artifact changes?
- **Measurability (Meas., 1-5):** can the persona-pinned choice be checked deterministically, and can a persona-blind agent be made to fail?
- **Headroom:** is SOTA far from both 0% and 100%?

## Master table

| Benchmark | Domain | Size | License | Harness | Grading | SOTA (approx., not re-checked) | Sens. | Meas. | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Terminal-Bench-Science** | Life / phys / math / eng / earth | 70 (→100+) | Apache-2.0 | **Harbor-native** | Deterministic pytest | 5-66% by model | 3 | **5** | **Core** |
| **DiscoveryBench** | Soc / bio / econ / humanities / eng / meta-sci | 264 real + 903 synth | ODC-BY | CSV + JSON, light | LLM judge (HMS) | ~15-25% (2024) | **5** | 3→4* | **Core** |
| **BixBench** | Comp. bio | 205 Q / 60 capsules | Apache-2.0 | Docker notebook | LLM + exact / range | 17% orig; 84-98% on Verified-50 | 4 | 4 | **Core (life sci)** |
| **BioML-bench** | Protein / drug / sc-omics / imaging / clinical | ~24 [unverified] | MIT | MLE-bench fork | Deterministic metric → human percentile | < human median | **5** | 4 | Strong add |
| ScienceAgentBench | Bioinf / chem / GIS / psych | 102 | CC-BY data, **password zip, no redistribution** | Docker | Success scripts (+ GPT-4o for figures) | 33-42% | 3 | 4 | Strong add, if the license allows derived tasks |
| LABBench2 (mol-bio subset) | Mol. bio | 414 of 1,912 | CC BY-SA | HF + GitHub | Programmatic (primers, cloning) | lower than LAB-Bench | 4 | 4 | Add for narrow, deterministic items |
| SciAgentArena | Biomedical | ~200 | CC BY-NC-SA [unverified] | Web platform | Deterministic stepwise | Mixed, some saturated | 3 | 4 | Maybe; NC license, new |
| LLM-SRBench | Equation discovery | 239 | [unverified] | Light | Numeric + symbolic | ~30% | 4 | 4 | Maybe; weakly agentic |
| sc-HeurekaBench | Single-cell | 50 OEQ + 50 MCQ | MIT | conda | GPT-4o judge | 2.58/5 | 4 | 1-2 | Judge-only, deprioritize |
| AstaBench E2E-Hard | AI / NLP research | 50 | **Gated, no redistribution** | Inspect + Docker | Claude judge, rubric | 62-82% | **5** | 2 | Blocked by license |
| EXP-Bench | AI research | 461 | [unverified] | Docker | o3-mini judge | 0.5% full | 5 | 2 | Judge-only, v0.1 |
| MLRC-Bench | ML | 7 | MIT | conda, 48 GB GPU | Objective metric | ~9% | 4 | 3 | Too small |
| FrontierChallenge | Chemistry / materials | 97 released | [unverified] | [unverified] | pass + partial | 20.6% | 4 | ? | Watch |
| BixBench3 | Comp. bio | 20 | CC BY-SA | GCP + Cell Ranger | Artifact F1 vs published | ~0.5 | 2-3 | 3 | Too expensive; plan is fixed |
| ScienceBoard | 6 app domains | 169 | MIT | VMware GUI VM | State checks | 0-15% | 3 | 4 | GUI stack, avoid |
| PaperBench | ML replication | 20 | MIT | Docker + GPU | o3-mini judge | 21-26% | 1 | 2 | No |
| CORE-Bench / SciCode / MLE-bench | — | — | — | — | — | Saturated or defective | — | — | No |

\* DiscoveryBench is judge-graded as shipped. It becomes deterministic if we re-run its recorded gold workflows under each persona's settings. Examples of what that would make checkable: the test used, the α level, the variable set, and claim vs no-claim. DB-SYNTH can plant effects just above or below a persona's threshold, which defeats the blind control by construction.

## Key finding

The benchmarks where a persona matters most (AstaBench E2E-Hard, EXP-Bench, sc-HeurekaBench) are exactly the ones graded only by an LLM judge. The deterministic ones (TB-Science, BixBench, BioML-bench) mostly have well-specified tasks. So in every case the persona dependence has to be designed in: take a real open decision in the task, let a persona attribute pin it, and extend the verifier to check it.

No existing science benchmark combines a researcher persona with a deterministic verifier. None of the persona precedents (τ-bench, UserBench, PrefEval, PersonaGym, PersonaLens) reports a persona-blind control arm either. This is an open gap, based on the searches run, not an exhaustive review.

## Answer to "one benchmark or several?"

**Recommendation: a mix of three sources behind one harness, rather than a single benchmark.**

**Single benchmark.** The only credible single-benchmark option is TB-Science.
- It already spans five domains, so a domain distribution is possible within it.
- It has only 70 tasks, and most of them are deliberately well specified. Persona sensitivity would be low without heavy rewriting.

**Suggested mix.**

| Source | Role in the mix | Share |
|---|---|---|
| **TB-Science** | Deterministic spine across domains (physical / math / engineering / earth), Harbor-native | ~40% |
| **DiscoveryBench** | Evidence-threshold and method-choice tasks (D, C, H); social science and bio; cheap | ~30% |
| **BixBench, then BioML-bench** | Life-science block (C, D, F: thresholds, normalization, compute budget) | ~30% |

- This mix yields roughly **life science 30-40%, social/economic 15-20%, physical/math/engineering 40%**.
- Port everything to Harbor so there is one eval harness and the final comparison stays clean.

**Pilot before committing.** Take about 5 tasks from each of TB-Science, DiscoveryBench and BixBench, and run each under four arms:
1. no persona;
2. persona P;
3. opposite persona ¬P;
4. persona-blind control.

Keep a source only if the P vs ¬P outcomes actually diverge.
- DiscoveryBench is the cheapest place to start: small CSVs, no GPU.

## Precedents to copy for the persona layer

1. **τ-bench / UserBench: hidden persona plus a deterministic final-state check.** This is the model for the "persona as user simulator" design. For the v1 system-prompt design, keep the same deterministic check.
2. **P / ¬P / blind triples.** Every persona task gets an opposite-persona twin and a blind arm that has to fail. In a persona-blind control, the agent never sees the persona. If that arm still passes, the task is not measuring persona adaptation.
3. **Score axes split, not one judged total.** Report three separate axes, since K-Bench shows judges reward communication over accuracy:
   - task competence: the existing verifier;
   - persona adherence: deterministic;
   - communication fit for E and G: an ensembled LLM judge, reported separately.
4. **Watch simulator over-compliance.** If we use a researcher simulator, assistant-tuned models play users who are too cooperative (arXiv 2609.00608). This matters most for personas that hold firm to a prior hypothesis.

## Open decisions for the group

- **Persona placement:** in the agent's system prompt (v1, Persona8B style), in a user simulator (τ-bench style), or both.
- **Whether AstaBench-style judge-only tasks count at all.** Recommendation: no, for the headline metric.
- **License checks** for ScienceAgentBench (redistribution) and SciAgentArena (NC) before investing in either.
