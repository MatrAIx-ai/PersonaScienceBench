# Sections 5.4–5.5 revision — 2026-10-06

Restored Section 5.5 and rewrote both subsections. Section 5.3, the Introduction, Discussion, and all figure assets are unchanged by this revision.

| Result | Role and placement | Source |
|---|---|---|
| More simulator and actor output under 155/003; contrast with brief/direct 001 | Core profile-related variation, 5.4 paragraph 1 | `Experiment/01_behavioral_diversity/data/compact_behavior/comparisons.csv` |
| Recall/tool-use effect ranges and lack of pairwise Holm p < 0.05 | Necessary qualification, 5.4 paragraph 2 | Same table, all 10 pairs per metric |
| Actor repetition 003 = 8.03% [6.82, 9.30], 046 = 15.94% [14.10, 17.66] | Core interaction heterogeneity, 5.5 paragraph 1 | `Experiment/09_offline_metric_suite/figures/metric_suite_split/panel_A.source_data.json` |
| Complete-fact recovery among failed cases: 20.0–41.7% for personas, 0% Off | Core distinction between information acquisition and task outcome, 5.5 paragraph 2 | `panel_B.source_data.csv` in the same directory; setting-specific failed-case subsets |
| Later-completing episodes contribute to scientific performance | Core interaction timing, 5.5 paragraph 3, Figure 2 | `panel_C.source_data.csv`; 1,958 episodes; 003 cumulative score contribution 37.49 at iteration 2 and 48.69 at iteration 6 |

The Figure 2 interpretation explicitly retains its fixed denominator and observed completion lengths. It does not infer within-run improvement or a causal interaction-budget effect. Repetition describes wording reuse, not judged scientific novelty or interaction quality.

Figure 4's caption was corrected to match its existing stars: A/B use Holm p < 0.20, C highlights absolute differences >2 percentage points, and D >0.2 calls. The text separately reports the verified p < 0.05 comparisons. The supplied graph was not changed.

Argument chain: communication differences linked to contrasting profile preferences → reuse of earlier wording → information acquisition visible despite final failure → completion timing across full interactions. The headings introduce these claims, the prose supplies evidence and interpretation, and captions retain the reading keys. Implementation details remain in source documentation.

Removed the EXP-Bench illustrative case from Results to keep the argument based on aggregate findings and reserve detailed case analysis for Discussion. Existing Discussion case studies remain untouched. The removed paragraph is retained below for later use.

Prose word counts (whitespace-delimited, excluding floats/comments/citations/references/headings): 5.4 170 → 185; the previously unnumbered metric passage, now 5.5, 132 → 273. The new space develops profile-related interpretation and the previously undescribed Figure 2 result; it does not add new analyses.

Validation: checked stated effects, intervals, significance, and completion-score values against source data; compiled successfully with no undefined references; inspected pages 7–8 and the right-wrapped Figure 5.

## Removed case paragraph, retained for later discussion work

```latex
% Recorded example: results/astra-actor-astra-simulator-astra-judge/trial-1/candidate_155/expbench/
% expbench_neurips2024_94391_11-60ab483a5041.md (events 1--5).
Persona 155's profile specifies Mandarin output, detailed responses, and
an emphasis on accuracy (Appendix~\ref{app:persona-profile}).
In an EXP-Bench task on choosing a CycleNet~\cite{lin2024cyclenet} period, the simulator requested
an inspection and design proposal in Mandarin. The actor responded in
Mandarin, distinguished autocorrelation-based candidate generation from
validation-based period selection, and developed the approved design with
controls and evaluation criteria.
```

## Section 5.5 comment revision — 2026-10-07

Preserved the author's revised order: self-repetition (Figure 5A), completion timing (Figure 2), then information recovery among failed episodes (Figure 5B). Kept the author's removal of repeated CI bounds from the prose; Figure 5A still displays them. Compressed the estimator explanation already in the Figure 2 caption and linked completion timing to sustained communication.

The final paragraph now makes continued information-seeking concrete. Joining `Experiment/09_offline_metric_suite/data/snapshot.json` recovery records to traces by source, task, arm, and trial yields nine episodes with nonmissing recovery, FRR = 0, and facts_recovered = facts_total. All are disambiguation episodes with no recovery/trace exclusions. Their recorded interaction lengths range from four to ten; none belongs to persona off. Exact records are retained in `section_5_5_recovery_iterations.csv`. These lengths support sustained clarification in ultimately unsuccessful episodes, not attempts made after an already-observed failure or a claim about independently measured task difficulty.

All existing numerical results remain unchanged. Complete-fact recovery for persona off is exactly 0%, as in the panel source data. No inference linking repetition causally to performance is added. The main text presents the complementary behavioral observations and the concrete intermediate accomplishment of obtaining required facts. Existing figure assets and other subsections are unchanged. Prose length versus the last committed version: 273 → 228 words, excluding citation/reference commands.

## Literature supporting the self-repetition argument — 2026-10-07

Added two verified conference publications to Section 5.5's first paragraph and the bibliography. The section retains two prose paragraphs; the fact-recovery paragraph and all figures are unchanged. The new persona-off comparison (13.50%) comes from the same Panel A source JSON as the existing persona estimates.

| Reference | Verified primary source | Supported claim and role |
|---|---|---|
| Chen et al. (2026), *Diversity Collapse in Multi-Agent LLM Systems* | [Published PDF](https://aclanthology.org/2026.findings-acl.13.pdf), Introduction and Sections 4–5; DOI 10.18653/v1/2026.findings-acl.13 | Interaction structure and pressure toward agreement can restrict the diversity of scientific ideas. Motivates maintaining exploration during collaboration. |
| Liang et al. (2024), *Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate* | [Published PDF](https://aclanthology.org/2024.emnlp-main.992.pdf), Introduction and experimental analysis; DOI 10.18653/v1/2024.emnlp-main.992 | Debate introduces alternative arguments to address stalled self-reflection. Motivates substantive contributions in later interactions. |

The scientific-collaboration rationale is our interpretation: avoiding unnecessary repetition makes room for new evidence, clarification, and reasoning revisions. The manuscript reports lexical reuse and uses the literature as motivation; it does not relabel the repetition metric as a validated measure of semantic collapse, infer that every persona reduces repetition, or attribute score gains causally to lower repetition. Interaction-length results retain their original fixed-denominator interpretation.

Metadata were checked against the published papers and ACL records. For Chen et al., the PDF places Qian Wang before Qingyun Zou, whereas the Anthology export reverses their order and parses Zou's name incorrectly. The BibTeX follows the authoritative PDF. Liang et al.'s metadata agree with the publisher's BibTeX export. The Tang et al. (2026) debate-collapse paper was screened but omitted because its uncertainty/conflict intervention is less directly relevant to repetition and diversity.

Validation: Section 5.5 retains two paragraphs and grows from 228 to 270 prose words. Rebuilt `main.pdf` with Tectonic; both citations and bibliography entries resolve, with no undefined references or new overfull boxes in this section. Existing compiler rerun/font warnings remain. Verified all three repetition values against Panel A's source JSON.

## Refocus on conversational mode collapse and semantic collapse — 2026-10-07

Following the author's clarification, replaced the two preceding literature citations with sources that explicitly study mode collapse and semantic collapse in interacting LLMs. The new paragraph connects lexical repetition to this research through complementary measurements and explains why avoiding unnecessary reuse is desirable for scientific interaction. Section 5.3 is cross-referenced for semantic diversity. The fact-recovery paragraph remains separate and unchanged.

| Reference | Primary source and relevant passages | Manuscript role |
|---|---|---|
| Pandey, Yang, Liu and Jin (2026), *CORE: Measuring Multi-Agent LLM Interaction Quality under Game-Theoretic Pressures* | [EACL paper](https://aclanthology.org/2026.eacl-long.57.pdf), Sections 3.1, 4.1, 5.1 and 5.6; [publisher BibTeX](https://aclanthology.org/2026.eacl-long.57.bib) | Defines conversational mode collapse through concentration over response modes and assesses mode diversity, repetition and semantic stagnation jointly. Provides the direct connection to repetition. |
| Kong, Lai, Piao and Evans (2026), *Multi-LLM Systems Exhibit Robust Semantic Collapse* | [arXiv v2](https://arxiv.org/pdf/2605.17193v2), abstract and Results, pp. 6–7; metadata from [arXiv](https://arxiv.org/abs/2605.17193) | Documents convergence in meaning during extended closed-loop interaction, including continued variation in wording. Motivates combining lexical and semantic perspectives. Cited as a preprint, with no journal-publication claim. |

The earlier Chen/Liang bibliography additions were removed because they were used only in the superseded framing. The new paragraph does not infer that lower lexical repetition establishes mitigation of semantic collapse. The value of avoiding unnecessary reuse for clarification, interpretation and revision is the manuscript's scientific-collaboration rationale; the papers supply the documented failure modes and their diagnostic context. All empirical values, figures and other manuscript sections are unchanged.

Validation: Section 5.5 contains two paragraphs and 271 prose words. Tectonic rebuilt the 32-page PDF successfully; both new citations and bibliography entries are present, with no undefined references. The bibliography has no duplicate keys and `git diff --check` passes.
