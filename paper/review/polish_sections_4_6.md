# Language polish: Sections 4–6

Applied nature-polishing to an English research manuscript, covering Methods, Results and Discussion with generic journal conventions. Existing section order and scientific argument are retained. Section 5.1 received wording edits only; no model results were added.

## Revision notes

- Replaced abstract framing and repeated conclusions with direct descriptions. Removed phrases such as “provide a common axis”, “establish the performance context”, “expose additional dimensions” and “providing a basis”.
- Split dense metric and sampling descriptions into shorter sentences. Preserved eligibility thresholds, aggregation order, original versus repaired runs, and uncertainty definitions.
- Shortened Results by removing repeated explanations of what each plot or metric reveals. Retained numerical ranges, effect sizes, confidence intervals, significance levels, sample sizes and analysis families.
- Kept Discussion centered on workflow revision and clarification. Translated excerpts, highlighting, omission marks and appendix references are unchanged.
- Corrected one prose–table mismatch: persona 003 has the highest available mean in all four domains. The previous sentence incorrectly credited persona 155 in social sciences and humanities. Verified against `tables/performance_panel.tex` and `data/domain_performance.csv`; no table values changed.

## Main-text discipline audit

| Evidence | Function | Treatment |
|---|---|---|
| Domain score ranges and persona ordering | Domain variation | Retained; corrected ordering statement |
| Semantic separation and permutation tests | Main result and inference | Retained; compressed repeated interpretation |
| Token differences, clarification and tool-use ranges | Behavioral results | Retained, including Holm family |
| Self-repetition means/CIs and failure-conditioned recovery | Behavioral results and scope | Retained, including distinct eligible samples |
| Embedding and aggregation details | Method provenance | Compressed in place |
| C2 and C1 conversations | Discussion interpretation | Retained; full source conversations remain in Appendix C |
| Generic transitions and repeated broad implications | Redundant framing | Deleted or replaced |

No evidence was moved to the appendix or removed from a figure caption. Methods gained explicit sentence structure while Results and Discussion lost redundant prose.

## Terminology and verification

Retained canonical terms: PersonaScienceBench, persona off, actor, researcher simulator, Mean Persona Performance, fact recovery, self-repetition, native benchmark score, and study-cluster confidence intervals. The scorecard, available-case domain table and failure-conditioned recovery remain distinct analyses.

- Results decimal values were checked against the pre-edit text and retained exactly.
- All figure blocks, including captions and Discussion excerpts, remain unchanged.
- Figure assets and table source files were verified unchanged by SHA-256.
- The current metric-suite notebook confirms the six-word/three-position repetition definition and reported intervals; older standalone metric reports describe earlier figure versions.
- Tectonic compilation resolved all cross-references with complete glyph coverage. Rendered pages covering Sections 4–6 were inspected. The only overfull-box warning is in the existing Introduction.

## Prose word counts

Approximate whitespace-delimited counts exclude headings, figure blocks and captions, table inputs, TODO notes and cross-reference commands. Hyphenated expressions count as one word.

| Section | Before | After |
|---|---:|---:|
| 4. Experimental Setup | 428 | 469 |
| 5. Results | 828 | 587 |
| 6. Discussion | 268 | 240 |

| Results subsection | Before | After |
|---|---:|---:|
| Model-Level Scientific Collaboration | 60 | 41 |
| Performance across Scientific Domains | 133 | 77 |
| Persona Diversity Extends to Agent Responses | 203 | 164 |
| Behavioral Adaptation to Researcher Context | 432 | 305 |
