# Five-persona pilot on the BixBench CHIP questions

This pilot asks whether researcher personas that looked helpful, neutral or harmful in [`full_persona_v2`](../full_persona_v2/README.md) change the outcome on two reviewed BixBench questions. On these questions the researcher holds data-coding facts that the actor needs.

- **Design:** 2 questions × 6 conditions (5 personas plus persona off) × 3 independent episodes = **36 scheduled episodes**.
- **Run:** September 28, 2026. **35 were scored**; one could not be completed because of repeated transport errors.

**Summary.**

- **No persona is separable from run-to-run variation.** Persona off answered correctly in 4 of 6 episodes. The personas ranged from 0/6 to 4/6. The only large gap, candidate 148 at 0/6, partly reflects two correct answers that the native judge graded incorrect.
- **The `full_persona_v2` labels do not carry over.** The "positive" candidate 148 has the lowest score here, and the "negative" candidates 089 (3/6) and 003 (2/5) are within one or two correct answers of persona off.
- **Personas did not change the information supplied.** In 32 of 35 episodes the researcher disclosed every approved fact it would use in its first message, in every condition.

## Persona selection

The profiles are the exact published identities from [`full_persona_v2`](../full_persona_v2/profiles/). Each prompt is checked against its published SHA-256 before use.

- **How they were chosen:** for diversity of observed outcome on that study's 8-question ranking. They are **selection labels from single runs**, dominated by two binary SciConv outcomes, not established persona effects.
- **Excluded:** candidate 046, the most negative profile, because its attributes contradict each other (aged 5–12 with a "Veteran" food-and-beverage industry rating).

| Persona | `full_persona_v2` label (8-question change) | Salient recorded attributes |
|---|---|---|
| [148](../full_persona_v2/profiles/candidate_148.md) | Positive (+13.36 pp) | 65–74; doctorate; medicine, clinical; statistics expert; detail orientation very high; "every detail" |
| [155](../full_persona_v2/profiles/candidate_155.md) | Positive (+12.60 pp) | 85+; no formal education; manager; primary language Mandarin, "use your primary language for outputs" |
| [251](../full_persona_v2/profiles/candidate_251.md) | No impact (−0.43 pp) | 25–34; vocational certificate; entry-level engineering; short profile (2,498-character prompt) |
| [089](../full_persona_v2/profiles/candidate_089.md) | Negative (−16.22 pp) | 75–84; bachelor's; retired, engineering; evasive; consensus-driven; warm tone |
| [003](../full_persona_v2/profiles/candidate_003.md) | Negative (−19.87 pp) | 25–34; secondary education; senior product role; primary language Russian; blunt; analytical |

## Tasks and protocol

| Question | Asks for | What the researcher's reviewed facts cover |
|---|---|---|
| `bix-7-q2` | Mean number of CHIP variants per sample after excluding intronic, intergenic and UTR variants | Workbook layout, zygosity coding (reference calls), annotation terms |
| `bix-2-q2` | Percentage of CHIP variants in the Control Children cohort with VAF between 0.3 and 0.7 | Workbook layout, zygosity coding, trio status sheet, VAF summary workbook |

Both questions were added in [#3](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/3). On 2026-09-25, under the earlier protocol, `bix-7-q2` scored 0/3 researcher-only and 3/3 when the same facts were public. The facts are therefore answer-changing.

- **Protocol:** the current shared `researcher-review-v2` controller. Inspection, then approach review with explicit approval, then execution, then result review. At most 12 researcher requests and 60 actor steps.
- **Knowledge:** the researcher answers from the public brief, approved facts and shared handoffs only. `unrestricted_knowledge` is unset (the repository default), unlike `full_persona_v2`, which enabled general knowledge and the "embody the supplied identity" instruction.
- **Injection:** the persona profile is added only to the researcher's system prompt. The actor and judge never receive it, which was verified in the recorded API requests.
- **Models:** actor, researcher and judge all use `openai/gpt-6-luna`, reasoning effort `none`.
- **Grading:** the native BixBench open-answer judge prompt and parser, unchanged. The judge model is set at run time (`configured_at_run_time` in the evaluator record), and here it is `openai/gpt-6-luna` at reasoning effort `none`. Grades therefore depend on that configured judge; the judge model is recorded per episode in the evaluation details.
- **Runs:** each episode is a fresh, independent run in its own subprocess with a Bubblewrap sandbox. Job order was shuffled with seed `20260928`.
- **Retries were for infrastructure failures only:**
  - 17 episodes failed in the first pass. 13 failed with OpenRouter HTTP 402 after calls routed outside the configured provider key exhausted a zero credit balance; 4 failed with transport `ReadError`.
  - All 17 were rerun, and 14 were scored.
  - A second rerun scored 2 of the remaining 3.
  - `candidate_003` / `bix-2-q2` / repeat 2 failed with `ReadError` on all three attempts and is excluded, not counted as zero.
  - Scored episodes were never rerun.

## Results

**Native grade** is the benchmark's own judge.

**Range check** is a secondary, deterministic analysis. It extracts the headline value (the first percentage for `bix-2-q2`, the first bold number for `bix-7-q2`) and compares it with the private reference range. It does not replace the native grade.

| Condition | `bix-7-q2` native | `bix-2-q2` native | **Native, both** | Range check, both | Mean researcher requests | Mean facts disclosed |
|---|---:|---:|---:|---:|---:|---:|
| Persona off | 2/3 | 2/3 | **4/6** | 4/6 | 2.2 | 3.3 |
| 148 | 0/3 | 0/3 | **0/6** | 2/6 | 2.8 | 3.5 |
| 155 | 2/3 | 2/3 | **4/6** | 4/6 | 3.8 | 3.5 |
| 251 | 1/3 | 3/3 | **4/6** | 3/6 | 2.5 | 3.5 |
| 089 | 1/3 | 2/3 | **3/6** | 3/6 | 3.0 | 3.5 |
| 003 | 1/3 | 1/2 | **2/5** | 2/5 | 2.6 | 3.4 |

- **All personas pooled:** 13/29 native and 14/29 by range check, against persona off at 4/6.
- **Statistical test:** a two-sided Fisher exact test against persona off gives p ≥ 0.57 for every persona except 148. For 148, p = 0.06 on the native grade and p = 0.57 on the range check.
- **Cost:** GPT-6 Luna cost **$0.655** across the 35 scored episodes, reported by the API including provider-key usage. Mean 291k prompt tokens per episode, including repeated history.

Token use and time, per scored episode. Tokens include input and output, including repeatedly sent history:

| Condition | Profile characters | Mean actor tokens (range) | Mean researcher tokens | Researcher prompt tokens per call | Median elapsed (s) |
|---|---:|---:|---:|---:|---:|
| Persona off | — | 258,823 (121k–604k) | 15,974 | 4,792 | 129 |
| 148 | 7,218 | 307,737 (97k–741k) | 28,487 | 7,143 | 179 |
| 155 | 4,720 | 427,747 (101k–747k) | 33,703 | 6,716 | 144 |
| 251 | 2,498 | 169,254 (110k–261k) | 21,161 | 5,775 | 100 |
| 089 | 17,954 | 236,645 (108k–369k) | 40,472 | 9,843 | 99 |
| 003 | 18,692 | 204,564 (89k–426k) | 36,229 | 9,791 | 110 |

Actor tokens vary 2–8× within every condition (max/min 2.4× for 251 up to 7.6× for 148), so the condition means are not informative about persona.
Researcher tokens rise with profile length because the full profile is resent on every researcher call. Prompt tokens per call rise from 4.8k (no profile) to about 9.8k (the two ~18k-character profiles), so this difference is mechanical, not behavioural.
Median elapsed time is shown because one persona-off episode took 905 s with only two researcher requests, which points to API waiting rather than extra work.

Submitted headline values (per-episode detail in [results.json](results.json)):

| Condition | `bix-7-q2` | `bix-2-q2` |
|---|---|---|
| Persona off | 52.33, 300.94, 52.33 | 59.27, 61.57, 61.57 |
| 148 | 613.47, 310.5, 52.33 | 61.57, 97.49, 59.32 |
| 155 | 291.94, 52.33, 48.28 | 61.57, 61.57, "not calculable" (0) |
| 251 | 48.5, 1.05, 300.94 | 59.2, 61.57, 61.6 |
| 089 | 52.33, 7.22, 23.94 | 61.57, 59.36, 61.57 |
| 003 | 7.22, 300.94, 58.16 | 61.57, *(unresolved)*, "not calculable" |

## What can we learn about persona?

**1. Outcome variation is dominated by the actor, not the researcher.**

- Within every condition, `bix-7-q2` answers vary several-fold: 52.33 alongside 300.94 in persona off, 1.05 to 300.94 for 251.
- The same wrong values recur across conditions: 300.94 in persona off, 251 and 003, and 7.22 in 089 and 003. Examples of the underlying actor readings:
  - none of the three 300.94 answers mentions excluding reference calls, and one states that "no zygosity filter was applied";
  - 148's 310.5 averages over only two workbooks it judged populated.
- Two `bix-2-q2` failures ("not calculable") came from the actor concluding the workbooks held no usable VAF values. One said they were placeholder sheets; the other found a zero denominator. Its reading of the files failed; nothing the researcher said caused this.

**2. The personas did not change what information was supplied.**

- In 32 of 35 scored episodes, the researcher's first message already disclosed every approved fact it used in the episode. Typically that was all 3 facts for `bix-7-q2` and all 4 for `bix-2-q2`.
- This held in every condition, including persona off.
- Under the fact-restricted protocol, the controller front-loads the facts, leaving little room for persona-dependent disclosure.
- This likely explains why persona off now solves `bix-7-q2` (2/3), where the earlier researcher-only protocol scored 0/3.

**3. Persona expression was weak.**

- No researcher reply in any episode contained Chinese or Cyrillic characters (`reply_cjk_chars` and `reply_cyrillic_chars` are 0 throughout). That includes 155 (Mandarin, "use your primary language for outputs") and 003 (Russian).
- In `full_persona_v2`, 155's researcher wrote Chinese and the actor switched language. That study also enabled "Embody the supplied identity naturally", which this run keeps off.
- **Language adoption appears to depend on that instruction, not on the profile alone.** This is an inference from the two configurations, not a controlled comparison.
- Reply length varied little across conditions: per-episode mean 447–790 characters.

**4. The 148 gap is partly a grading artifact, and its one real error was not caused by the persona.**

- Two of 148's six episodes submitted in-range answers that the native judge graded incorrect: 61.57% on `bix-2-q2` and 52.33 on `bix-7-q2`. Persona off's identical 61.57 and 52.33 answers were graded correct.
- In the other direction, the judge accepted 251's 59.2% on `bix-2-q2`, which is outside the reference range.
- The judge runs at reasoning effort `none`. Its errors here include a value well inside the range (52.33), not only values near a boundary.
- 148's 97.49% on `bix-2-q2` came from the **actor** adding a "heterozygous only" filter. 148's researcher restated and accepted the result without challenging the restriction. That is a missed check, not a persona-driven instruction.

**5. One controller loop was observed.**

- In 155's third `bix-7-q2` episode the researcher used 11 of its 12 requests.
- For three consecutive decisions its message said the audit-only plan had been approved while the structured `approve_approach` flag stayed `false`, so the controller kept the actor in the plan stage. The fourth such message set the flag.
- The episode still finished correctly (48.28).
- Like the plan-stage loop in the `full_persona_v2` [case studies](../full_persona_v2/case_studies.md) §4, the actor was held in the plan stage. The cause differs: there the researcher withheld approval, while here its prose and flag disagreed. The controller could reconcile the two.

## Limitations

- **Sample size:** three episodes per cell. Differences of one or two correct answers per condition are within the observed persona-off variation. No condition-level claim is made.
- **Grader:** the native judge misgraded 3 of 35 episodes according to the deterministic range check. Grades are reported unchanged.
- **Scope:** two questions from the same CHIP study, so the results do not generalize to BixBench as a whole or to other benchmarks. The persona selection labels come from a different protocol (general knowledge on), so this pilot tests transfer across both tasks and protocol.
- **No actor questions:** the actor never asked the researcher a question (0 in all 35 scored episodes); the researcher drove every exchange. A HiL-Bench-style Ask-F1 (precision and recall of actor questions against known blockers) is therefore undefined here. An adaptation would score the uncertainties the actor lists in its handoffs against the reviewed facts, which needs a separate matching step.
- **Missing episode:** one scheduled episode is missing (`candidate_003`, `bix-2-q2`, repeat 2).

## Reproduce

Requires the pinned BixBench source and assets, the actor runtime and an `.env` with `OPENROUTER_API_KEY`.

```bash
.venv/bin/python -m personasciencebench --source-root <sources> prepare \
  --selection configs/bixbench-chip-selection.json --benchmarks bixbench \
  --cases-per-benchmark 2 --output prepared/bixbench-chip-persona
.venv/bin/python scripts/run_bixbench_chip_persona_pilot.py \
  --output runs/bixchip-persona-YYYYMMDD --env-file .env --parallel 2
.venv/bin/python scripts/report_bixbench_chip_persona_pilot.py \
  --run runs/bixchip-persona-YYYYMMDD --output <analysis-dir>
```

Consider running at most two episodes in parallel when calls go through a provider key. In this run, the fallback routing described above occurred with four parallel episodes.

## Files

- [results.json](results.json): all 36 scheduled episodes, with status, native grade, extracted value, range check, researcher requests, approach and result reviews, disclosed fact IDs, reply length, Chinese and Cyrillic character counts, per-role and total tokens, elapsed time, cost and an answer excerpt. Reference ranges are omitted.
- [results.csv](results.csv): the same per-episode metrics as a flat table. Answer excerpts are omitted, and fact IDs are joined with `;`.
- [case_evidence.json](case_evidence.json): the episodes cited in this README, with short researcher-decision and actor-handoff excerpts in sequence order:
  - the three native-judge disagreements and the persona-off runs with the same answers;
  - 148's accepted heterozygous-only filter;
  - 155's approval-flag loop;
  - the two actor reading failures;
  - the per-episode first-message fact counts behind the 32/35 figure.
  Judge prompts are excluded because they contain the reference.
- [summary.json](summary.json): per-condition and per-question aggregates, status counts, retry record and unresolved episode.
- [runtime_config.json](runtime_config.json): models, protocol, knowledge setting, persona prompt hashes, tasks, repeats and source hashes.
- Scripts: [`scripts/run_bixbench_chip_persona_pilot.py`](../../scripts/run_bixbench_chip_persona_pilot.py) and [`scripts/report_bixbench_chip_persona_pilot.py`](../../scripts/report_bixbench_chip_persona_pilot.py).

Raw API records, full transcripts, private evaluator references and local paths are not included.

## Sources

- [BixBench](https://github.com/Future-House/BixBench) at `49311180bdacb324c596f2e07596c126f2004008`, dataset revision `f8cc3bdcc6357c88b8c3648306522b9c422dc95a`, as pinned in `manifests/sources.json`. Questions and reviewed facts come from the adapter added in [#3](https://github.com/MatrAIx-ai/PersonaScienceBench/pull/3).
- The persona profiles are the exact published `full_persona_v2` identities. They were rendered from `MatrAIx2026/MatrAIx_Persona_1M` sample revision `8b1073ab23d0c0ba0928386a041bac55e5365ddc`; see `configs/full_persona_v2/cohort.json`.
- Repository base: upstream `main` at `75e3f08`.
