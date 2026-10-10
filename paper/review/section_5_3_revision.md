# Section 5.3 revision — 2026-10-06

Replaced the commented semantic-results passage with three result-led paragraphs. Retained the subsequent behavioral and offline-metric findings and the author’s merged subsection structure. Repaired the Discussion pointer to the merged section. Figure assets are unchanged.

| Result | Function and location | Evidence |
|---|---|---|
| Distinct final responses in both roles | Core result, paragraph 1 | `Experiment/01_behavioral_diversity/data/semantic_final/heatmap_cells.csv`: all 20 comparisons positive, Holm-adjusted p < 0.05, 97 questions |
| Different intermediate paths despite nearby endpoints | Illustrative heterogeneity, paragraph 2 | Existing `figures/semantic.pdf`, BixBench panel; describes projection geometry without claiming identical conclusions or disjoint behavior |
| Additional clarification exchanges | Illustrative heterogeneity, paragraph 3 | SciConvBench case 236: Off/001 = 1, 155/003 = 3, 046 = 4; figure trajectory source data and saved trial-1 traces |
| Domain control and test | Necessary support, compressed in paragraph 1 | Within-domain comparison against within-persona cross-question variation; equal domain weights; question-wise label permutations and Holm correction |
| Normalization, add-one formula, projection parameters | Provenance detail, retained in existing source report | `Experiment/01_behavioral_diversity/SEMANTIC_REPORT.md` and `SEMANTIC_FIGURE_CAPTION.md`; method citations retained in manuscript |

Evidence chain: final-response differences → different interaction paths → concrete extended clarification sequence. The heading introduces the scope; the heatmap supplies aggregate evidence; the trajectories illustrate process differences; the Discussion connects those results to separate case studies. No claim of uniformly longer interactions, improved accuracy, or measured human realism is added.

The three rewritten semantic paragraphs contain 237 whitespace-delimited words, excluding citation/reference commands, versus 136 in the last committed semantic prose. The added space develops the requested trajectory interpretation and concrete exchange counts; statistical implementation prose is compressed. Subsequent results prose is unchanged.

Validation: checked all 20 heatmap rows, inspected the existing semantic figure, verified the case-236 transcript, compiled the paper, and inspected page 7. No undefined references. Existing minor layout warnings remain outside the rewritten paragraphs.

## Author-directed trajectory rewrite

Replaced only the two trajectory paragraphs after clarification of the intended argument. The author has restored Section 5.4; its structure is preserved.

- Diversity: BixBench shows distinct paths with similar overall movement and partial convergence in both roles; SciConvBench shows different overall trajectory patterns for both roles. This is an interpretation of the existing projection, not a claim of identical scientific conclusions.
- Participation: the plotted BixBench persona-off path contains two actor messages and three simulator messages; the persona paths contain three or four actor messages and four or five simulator messages. The single-exchange baseline belongs to SciConvBench, where 155/003/046 have three/three/four exchanges and 001 also has one. The prose names the three profiles with longer interactions.
- Meaning: the saved case-236 trace supports sequential, specific actor questions. The value of surfacing implicit assumptions and incorporating feedback is presented as the rationale for evaluating these interactions, not as a new measured performance gain.
- Evidence allocation: trajectory observations and one concrete sequence of questions stay in the main text; exact plotting counts and the correction to the recalled baseline are retained here and in source data. Figure contents and subsequent findings are unchanged.
- Two-paragraph word count: 162 → 223 (whitespace-delimited, excluding citation/reference commands).
