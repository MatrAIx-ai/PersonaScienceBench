# Leaderboard figure QA — own available cases, 2026-10-05

- Re-executed the full performance notebook: five code cells, one embedded figure, no error outputs. PDF/SVG/PNG regenerated using each model's own available eligible questions.
- All six means, twelve CI limits, off references, per-setting estimates and question membership exactly match the corresponding supporting scorecard outputs. Input/code hashes verified after export.
- No cross-model intersection or exclusion is applied. Within each model and metric, the existing five-setting eligibility rule remains. Performance coverage: Astra 101 / Haiku 200; fact recovery 20 / 20; repetition 79 / 137. Question membership and availability exclusions are recorded per model in the CSV outputs.
- Alignment PASS: equal panel widths/heights and gutters at 1.5-pt tolerance. Final PDF text audit has minimum 8 pt and no below-floor text. Final collision audit PASS, with zero failures or warnings. Visual inspection confirms readable labels and complete uncertainty whiskers after the data revision.
- Source audit has zero failures. Accepted warnings: PNG is a 300-dpi preview and no TIFF is requested; PDF/SVG provide vector deliverables.
- Each panel reports four-persona means with pointwise 95% study-cluster bootstrap CIs. All bars start at zero. Panel A's black persona-off ticks are point references only, with CIs saved in source data. Panels B/C retain clearly labelled metric-specific axes. No significance tests, stars or rank claims are added.
- Caption and notebook now consistently state model-specific coverage. Historical evaluators, unequal repeats, fixed selected personas, availability conditioning and exploratory repetition matching remain documented. The obsolete 42-question matched repetition panel and its single-Bix caveat are superseded.

| Panel | Summary | Questions: Astra / Haiku | Rendered check |
|---|---|---|---|
| A | Mean Persona Performance and off reference | 101 / 200 | Both means and CI whiskers clear; off ticks distinguishable |
| B | Recovered fact fraction | 20 / 20 | Complete intervals; consistent model colors and order |
| C | Actor repeated-window fraction | 79 / 137 | Complete intervals; no unconditional quality direction implied |

No new model inference, embeddings or regrading. The main figure and supporting table now agree numerically.
