# Question-controlled semantic figure

Only two main panels: A aggregate persona-pair distances (one-third width), B two question-specific UMAP trajectories (two-thirds). Two aligned role rows: simulator above actor. No behavior categories, judge annotations or task performance. Five consistently labeled persona identities; categorical colors appear only in B. Continuous diverging scale centered at zero in A; identical role limits, symmetric matrix and masked diagonal. Numeric cells, exact 95% CIs in companion tables when cell text would be too small.

User-selected trial-1-only panel: off/155/001/004/046. Raw cosine-distance mode is required for this one-trial comparison. The colorbar and caption must say raw distance and explicitly disclaim adjustment for rollout randomness. Adjusted mode must fail if any configured condition lacks two independent rollouts. Never silently mix raw and adjusted cells.

Python/Matplotlib, 183 mm width, editable PDF/SVG, 600 dpi PNG/TIFF; minimum text 5 pt. Shared persona legend. Every trajectory uses actual nodes without point-index labels, gentle quadratic visual connectors, no directional arrows and a marked terminal node. The same question and rollout appear in both role rows. Local UMAP uses all messages for that question/role, never separate projections per persona. A is computed before projection.

Claim boundary: distances describe embedded generated content and may reflect language/style. Cases illustrate, not replicate, population evidence. Original trace selection, exclusions, question/source/round counts, model revision, preprocessing and resampling must be saved. The baseline allows comparison to off, but raw distances do not demonstrate excess diversity over baseline randomness. Existing figures remain untouched.

Latest user steering: trial 1 only, with equal weighting of the four scientific super-families. Every distance remains matched on exact question and round. Bootstrap whole questions within source × family. Preserve question-weighted outputs separately as sensitivity; family weighting does not adjust rollout randomness.


Current case studies are user-selected examples: bix-57-q1 and matToolUse/disambiguation/case_236. Exact reviewed UMAP coordinates are frozen. This supersedes the original median-case selection rule. One-round paths remain single nodes. The earlier median-case PCA figure and notebook are archived under `previous_median_pca/`. Aggregate heatmap values and CIs are unchanged.

Curved preview requested by the user: curves are visual connectors only. Their intermediate positions are not observed states; no spline fit or added semantic observations. Control offset 0.14 of the perpendicular chord in normalized axes. Straight-line outputs archived under `previous_straight_umap/`.

Directional arrows removed at user request; curved connectors, fixed nodes and final diamonds remain.


## Current Panel A: final-response domain separation

This supersedes the round-matched raw-distance heatmaps above. Select the last generated message separately for simulator and actor; retain a common question set with all five settings at trial 1. Within each family, E is cross-persona cosine distance minus the mean of two within-persona distances, using only different-question pairs in both. Give four families equal weight. The within-persona reference includes question differences, not rollout randomness. Test pairwise label exchangeability by swapping labels within questions, 10,000 times; one-sided greater alternative and Holm correction across both role heatmaps (20 tests). A single star means adjusted p<0.05. Pointwise 95% question-bootstrap intervals (20,000, source × family strata) and unadjusted/adjusted p values are reported in tables. Same-original-question pairs remain excluded when bootstrap samples contain repeated questions. The right-hand case trajectories and their coordinates remain unchanged. Previous raw heatmaps are archived in `previous_raw_heatmap/`.

Display update: show only the lower triangle of each heatmap. Upper triangle and diagonal are white/masked; all ten unique pairwise comparisons, their significance markers, and the underlying symmetric data remain unchanged.

Latest layout: 183 × 145 mm; lower-triangle heatmaps with light-gray diagonal, no heatmap spines or question-count headings. Persona/role labels remain for identification. Top subtitles and bottom explanatory text are omitted from the graphic and retained in the notebook/report. Case titles are only `bix 57` and `case 236`, close to their axes; panel headings are moved closer. Colorbar and persona legend remain.

Current persona panel: off/155/001/089/046. User-requested exploratory replacement of 004. Use all 158 common complete questions for A and refit all four selected-case UMAP maps for B. Prior 004 outputs archived; current interpretation/caption in `SEMANTIC_FIGURE_CAPTION.md` supersedes earlier panel-specific counts and coordinate-preservation statements.

Current exploratory panel: off/155/001/003/046, with 97 common questions. UMAP maps refitted for these settings. Prior 089 and 004 versions preserved. The current caption documents sparse EXP coverage and possible language contributions from 003’s Russian-output instruction.

Current endpoint markers: hollow circle at start, larger solid circle at end, small solid intermediate dots. Single-node paths use a solid dot inside a hollow circle. No changes to trajectories or statistics.
