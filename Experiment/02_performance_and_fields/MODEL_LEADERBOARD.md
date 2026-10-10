# Model comparison figure

## Figure contract

- Question: how do the available model configurations compare on scientific performance, information acquisition, and actor repetition under a fixed persona mixture?
- Claim: model-level summaries describe complementary outcomes under four selected collaborator personas; no scalar adaptation score or causal model ranking is claimed.
- Quantitative grid: A measures task performance; B measures recovery of withheld information; C describes repeated actor text. Three aligned bar panels, consistent model colors, zero-based axes, no individual-persona bars.
- Python/Matplotlib; 183 × 82 mm before tight export; editable PDF/SVG, 300-dpi PNG preview, source CSV and saved notebook output. Main bar labels are means and whiskers are pointwise 95% CIs. Persona-off is a point reference in A only.
- Each model uses its own available eligible questions per metric, requiring all five settings within that model. There is no intersection across models. Figure estimates and intervals match the supporting model scorecard.

## Candidate caption

**Model comparison across simulator-persona conditions.** Bars show model-level means across four injected personas (155, 001, 003, 046), with pointwise 95% percentile confidence intervals from 20,000 study-cluster bootstrap samples stratified by source benchmark (seed 20261004). Each model uses its own available metric-specific question set, requiring observations for all five settings within that model; cases are not intersected across models. Available trials are averaged within question and setting, questions within source, then applicable sources and injected personas equally. All settings and observed trials of a sampled study remain together within each model's bootstrap. **A**, native performance on 101 Astra questions (ASI/Bix/Discovery/EXP/SciConv: 7/27/21/6/40; 78 study clusters) and 200 Haiku questions (40 per source; 134 study clusters). Black ticks indicate persona-off means on the corresponding model's question set; their intervals are available in source data. **B**, mean recovered fraction of withheld facts on 20 SciConv disambiguation questions per model, without success/failure conditioning. **C**, actor self-repetition on 79 Astra questions (6/27/21/6/19; 56 study clusters) and 137 Haiku questions (39/5/34/39/20; 93 study clusters): the fraction of six-word windows with at least three aligned word matches in an earlier actor message, averaged across later eligible messages. Episodes require at least two actor messages of nine or more words. Lower repetition describes less repeated text, not necessarily higher quality. The matching threshold was selected exploratorily. Coverage differs across models and metrics and is conditioned on availability. Historical evaluator differences and unequal repeats remain; intervals condition on observed rollouts and the fixed persona set. The figure is a descriptive summary of historical model configurations, not a matched or paired model comparison, a controlled actor-only ranking, or evidence of human realism.

## Reproduction and outputs

Run `code/plot_model_leaderboard.py` with the repository Python environment, or execute the final section of `performance_analysis.ipynb`. No LLM calls, new embeddings or regrading are needed.

- `data/model_leaderboard/summary.json`: model-specific available-case estimates, per-setting summaries, bootstrap specification and input/code hashes.
- `data/model_leaderboard/source_data.csv`: plotted means/CIs and off references (including supporting off intervals).
- `data/model_leaderboard/coverage.csv`: model-specific eligible counts, retained counts, exclusions and trial coverage.
- `data/model_leaderboard/question_panel.csv`: exact per-model, per-metric question/study membership.
- `figures/model_leaderboard/model_leaderboard.{pdf,svg,png}`: figure exports; QA records accompany them.

The supporting table in `data/model_scorecard/` uses the same available-case rule and remains unchanged. Mean Persona Performance is 48.82% for Astra and 33.82% for Haiku, using 101 and 200 eligible questions respectively. This supersedes the earlier figure restricted to questions shared across models.
