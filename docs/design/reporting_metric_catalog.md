# Proposed reporting metric catalogue

Date: 2026-10-01. Specification only; this file does not change collected data, scoring, or analysis. Scope: reuse saved episodes, traces, native evaluations, embeddings and API usage. No new inference or annotation is required for the proposed core suite. New offline computations are identified. Current selected figure settings: off/155/001/003/046; do not silently restrict all existing analyses to this panel. 003/046 have one trial, off/155/001 have three. The wider repeated panel supports repeat diagnostics separately.

User constraint: additional offline extraction and recomputation are authorized; no new LLM inference. Reuse saved native judgments and cached embeddings only. New fact-level or semantic judgments remain deferred.

Status: **existing** = implemented, subject to its recorded coverage; **new offline** = data exist, computation/audit still needed; **conditional** = usable only where the necessary native definition and common coverage exist.

## Scientific outcomes

| Metric | Definition | Provenance | Status |
|---|---|---|---|
| Native scientific score | Each source's native outcome, on the existing 0–100 reporting scale; source-specific definitions below | `scripts/report_first_pass_ci.py:score`, saved native results | Existing |
| Matched score difference | Score(persona i) − score(persona j) for compatible same-task/same-trial pairs; average trials within task, then tasks | Experiment 02 `data/pairwise_selected/matched_episodes.csv`, `code/pairwise_performance.py` | Existing |
| Scored-submission rate | Scored deliverables / (scored deliverables + scientific missing submissions), excluding infrastructure failures; incorrect scored submissions still count as submitted | Experiment 02 `code/consolidate_performance.py`, native status | Existing on documented panel |
| Score conditional on submission | Native score using only scored deliverables | Same | Existing, supplementary |

Native mappings: ASI = 100 × score/max_score (judge-version filtered for matched comparisons); Bix = 100 × correct; Discovery = 100 × final_score; EXP = gated_coverage_mean from final endpoint or documented initial fallback; SciConv = 100 × FRR. A shared numerical scale does not make scientific constructs equivalent. Super-family aggregates mix source metrics and must be descriptive. Scientific missing submissions are zero in unconditional native scores; infrastructure errors remain missing. Repair endpoints are not independent trials.

## Interaction behavior (Experiment 01)

Source: `code/analyze_behavior.py`, saved `events.jsonl`, `researcher_decision` payload fields, `agent_handoff`, SciConv `researcher_question`/`researcher_reply`, termination metadata. Existing numeric artifacts include `data/behavior/` and the expanded all-persona report/snapshot.

| Metric | Definition | Scope/status |
|---|---|---|
| Interaction length | SciConv: number of researcher replies; review protocols: actor handoff count. Preserve these source-specific definitions | Existing; all sources with complete traces |
| Additional approach reviews | max(approach-review count − 1, 0) per episode | Existing; review protocols only |
| Additional result reviews | max(result-review count − 1, 0) per episode | Existing; review protocols only |
| Revision requests | Count result-review decisions whose action is `continue` | Existing; simulator requests, not verified actor revisions |
| Revision-request incidence | 100 × episodes with at least one revision request / eligible episodes | New offline aggregation of existing counts |
| Exact repeated-question rate | 100 × (Q − U)/Q, where Q is number of actor questions and U is number of unique normalized questions | Existing SciConv implementation defines only Q≥2; normalize NFKC, remove fenced code, casefold, keep alphanumerics; not semantic redundancy |
| Budget exhaustion | Percentage reaching researcher-interaction budget, actor-call budget, or SciConv ten-reply limit, separately | Existing; controller limits, not API rate/quota limits; disclose known SciConv cap-handling sensitivity |
| Dominant interaction-pattern share | Frequency of most common canonical optional event sequence / eligible episodes in a declared question/source panel | New offline; exclude forced actions/retries, preserve role and original order, represent no optional actions explicitly |
| Fixed-budget pattern coverage | Expected number of distinct canonical optional event sequences among m episodes; average over a declared sampling allocation and eligible questions | New offline; equal m, source-specific vocabulary, length sensitivity; within-question comparison primary |

The existing `optional_pattern_hash` concatenates selected phase lists and leaves empty optional patterns absent. It must not be relabeled as complete ordered-sequence coverage. Re-extract ordered native events. Counts are communication patterns, not scientific-method or actor-correction validity labels. SciConv event-type sequences alone primarily reflect questioning length and termination; do not imply content-level strategy diversity.

## Scientific information recovery (Experiment 08 / SciConv)

Source: saved `llm_judge_disambiguation_score.json`, `llm_judge_disambiguation_chat_score.json`, `llm_judge_inconsistency_chat_score.json`, `llm_judge_intent_score.json`, `evaluation.metrics`; extraction in Experiment 08 `code/analyze.py` and Experiment 01 `code/analyze_behavior.py`. These reuse saved model-based native judgments, not human ground-truth annotations.

| Metric | Definition | Scope/status |
|---|---|---|
| Fact-recovery rate | 100 × recovered deleted facts / total deleted facts; before the intent gate | Existing; disambiguation only; use full name, not acronym FRR |
| Full resolution rate (native FRR) | 100 × indicator(native full resolution AND intent preserved), averaged across cases | Existing; both modes, retaining mode-specific native resolution criteria |
| Clarification recall | 100 × native judged count of covered missing/inconsistent issues / total target issues | Existing; separate modes; use saved intended covered-issue count, not raw question count |
| Clarification precision | 100 × native judged relevant questions / all parsed actor questions | Existing; native runner encodes zero when no questions; disclose that convention and report Q=0 frequency |
| Intent preservation | 100 × native intent-capture indicator | Existing; supporting validity metric |
| Conversation-grounded resolution (CGRR) | 100 × FRR × native grounded indicator | Existing; supporting decomposition, not per-fact disclosure coverage |
| Silent resolution (SRR) | 100 × FRR × (1 − native grounded indicator) | Existing; CGRR + SRR = FRR; not evidence of guessing or leaked information by itself |

Primary graded endpoint: fact-recovery rate. Primary strict endpoint: native FRR. Clarification precision/recall are diagnostic. No composite index, no new weighting across these quantities. Existing recovery analysis is the original six-setting/three-trial disambiguation panel; selected five-setting coverage must be extracted/audited before reporting that panel. Incorrect native counts and missing judgments remain unavailable, not fabricated zeroes. Existing memory-consistency scores may remain supplementary under their native rubric; they are not a new core endpoint here.

## Semantic and resource diagnostics

| Metric | Definition | Provenance/status |
|---|---|---|
| Excess final-response cosine distance | Within each super-family, cross-persona mean distance across distinct questions minus half the sum of the two within-persona distinct-question distances; average four families equally | Existing: Experiment 01 `code/semantic/final_response.py`; frozen Qwen3-Embedding-0.6B, normalized embeddings, roles separate |
| Visible message length | Mean visible characters/message, simulator and actor separate; no prompt/history concatenation | Existing: behavior extraction; not language-neutral information quantity |
| API output tokens | Recorded completion_tokens per successful call and episode totals, by role; reasoning component reported separately when present | Existing SciConv six-setting usage analysis; `code/analyze_sciconv_tokens.py`, `data/sciconv_tokens/calls.csv`; not complete all-source cost accounting |

Current semantic analysis uses one trial and different-question distances; within-persona spread includes question variation and is NOT repeated-rollout noise. It is sensitive to language/style. UMAP paths are illustrative, not additional quantitative metrics. Selected persona primary output languages differ. Missing API usage must not become zero costs; recorded output tokens can include reasoning. Visible length and tokens measure communication/cost, not quality.

## Evaluation coverage (new offline)

For a fixed common set of questions and compatible evaluator/protocol versions, let F_s(m) be the set of questions with at least one native scientific failure under evaluation strategy s using m episodes per question. Compare repeated off with a fixed-budget persona mixture. Available off repeats limit current budgets to m≤3, and common valid coverage may be smaller.

| Metric | Definition | Provenance/status |
|---|---|---|
| Failed-task coverage | 100 × |F_s(m)| / number of eligible common questions | Saved native results; new offline, conditional on native binary success criteria |
| Additional failed-task coverage | 100 × |F_mix(m) minus F_off(m)| / eligible common questions; also report reverse set difference and net difference | Same; newly exposed tasks, not distinct failure mechanisms |
| Marginal persona contribution | Incremental distinct failed-task coverage when including a persona, averaged over declared inclusion orders/allocations; compare against adding another off episode at the same total budget | Same; new offline; not a benefit from extra compute alone |

Use scientific failures including scientifically missing submissions where the native contract supports that designation; exclude infrastructure/credit/rate-limit failures. Do not invent binary thresholds for continuous native scores. Compare at matched episode budgets first; token-budget coverage is deferred until complete actor+simulator cost is reconciled. Scientific task/fact fidelity must be retained where measurable; increased failure alone is not proof of better simulation. Outcome-selected persona sets make these exploratory comparisons. Average eligible allocations; do not choose the most favorable combination after viewing outcomes.

## Shared reporting contract

- Episode-level metrics first; available trial means within question, then equal question weights unless a figure explicitly documents another weighting. Semantic figure uses equal family weights; behavior paired heatmaps use their documented benchmark weighting.
- Report source/study/question/episode counts, valid repeated trials, evaluator and protocol versions. Use source-study cluster bootstrap for conventional behavior/performance CIs where implemented; current semantic intervals instead resample questions and have a documented different scope.
- Inapplicable metrics are NA, never zero. Preserve existing zero-question and minimum-question conventions explicitly; change a convention only with a versioned recomputation.
- Pair differences on task and trial. Paired coverage can differ from available absolute-score coverage. Behavior originals and repaired performance endpoints must be reconciled before any episode-level mechanism analysis.
- Mean ± uncertainty and distributions, not significance-cell count, describe the evidence. More revisions/questions/diversity is not automatically better. Keep the full sensitivity record.
- Required coverage fields: planned slots, evaluable/scored outcomes, complete traces, scientific missing submissions, infrastructure failures, trial counts, study counts. These are data-quality metadata rather than scientific diversity endpoints.
- Deferred: per-fact disclosure/incorporation, semantic feedback adoption, per-turn information gain, human realism/fidelity, scientific strategy categories without artifact validation, composite behavior-quality score.
