# Named-method citation audit

Scope: main.tex and its section/table inputs, including appendix prompts and full interaction cases. Added citations use `\cite`, as requested. Existing benchmark/persona and related-work citations were retained; this pass does not reverify every existing bibliography entry.

| Method | Citation key | Location | Verified source |
|---|---|---|---|
| Qwen3-Embedding-0.6B | zhang2025qwen3embedding | Semantic analysis | https://arxiv.org/abs/2506.05176 ; official checkpoint https://huggingface.co/Qwen/Qwen3-Embedding-0.6B |
| UMAP | mcinnes2018umap | Trajectory visualization | https://arxiv.org/abs/1802.03426 |
| Study-cluster bootstrap | field2007bootstrap | Sampling and Statistical Analysis | https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9868.2007.00593.x ; original paper https://bemlar.ism.ac.jp/zhuang/Refs/Refs/field2007jrssb.pdf |
| Monte Carlo permutation add-one correction | phipson2010permutation | Semantic inference | https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf |
| Holm multiple-testing correction | holm1979sequential | Semantic inference; editorial appendix note | https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf |
| CycleNet | lin2024cyclenet | EXP-Bench behavioral example | https://proceedings.neurips.cc/paper_files/paper/2024/hash/bfe7998398779dde03cad7a73b1f81b6-Abstract-Conference.html |
| limma | ritchie2015limma | Discussion workflow case; editorial appendix note | https://bioinf.wehi.edu.au/limma/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4402510/ |
| Benjamini–Hochberg correction | benjamini1995fdr | Editorial note preceding full transcripts | https://www.math.tau.ac.il/~yekutiel/eBayes/bh_1995.pdf |

Checks and placement decisions:

- The semantic implementation in `Experiment/01_behavioral_diversity/code/semantic/final_response.py` uses `(1 + exceedances)/(permutations + 1)`, matching the newly cited Monte Carlo correction.
- Field and Welsh supports cluster resampling in general; the study's benchmark stratification and exact weighting remain its own documented implementation.
- Qwen citation replaces the author's inline citation reminder. UMAP citation is in prose rather than lengthening the caption.
- limma is cited as a method mentioned in the workflow, not as a successfully executed analysis. The recorded replacement analysis remains ordinary least squares.
- Full interaction-event blocks are byte-for-byte unchanged. References for named transcript methods appear in editorial prose, also added to the transcript generator.
- Basic operations (cosine distance, L2 normalization, averaging, ordinary least squares, F1) were not assigned arbitrary new citations. General-purpose language names R/Python and profile attributes are not new methods introduced by this study. Persona attributes remain attributed to MatrAIx.
- OpenHands was searched as a potential framework reference, but does not appear in the manuscript prose; no unsupported framework description was added.
- Preserved existing source-benchmark citations and existing agent-system citations. Official model-card references were added in the Section 4.1 update below; exact runtime identifiers and remaining configuration details retain a TODO.
- Removed an orphaned duplicate Wang-author/year field block outside a BibTeX entry. The complete `wang2023userbehavior` entry remains.

## Section 4.1 model-card update — 2026-10-07

Rewrote Section 4.1 as three paragraphs covering model roles, persona settings, and a concise trial-coverage statement. All seven Table 2 models are cited through six official cards. GPT-5 mini and GPT-5 nano share their family system card, which explicitly covers the API thinking mini/nano variants. No model specifications, capabilities, or benchmark results were inferred from unrelated versions.

| Model(s) | Citation key | Verified official source | Document date |
|---|---|---|---|
| Claude Opus 5.5 | `anthropic2026opus55` | [System card](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf) | 22 September 2026, verified from the downloaded PDF cover |
| Claude Haiku 4.5 | `anthropic2025haiku45` | [System card](https://assets.anthropic.com/m/99128ddd009bdcb/original/Claude-Haiku-4-5-System-Card.pdf) | October 2025 |
| Gemini 3.7 Flash | `deepmind2026gemini37flash` | [Model card](https://deepmind.google/models/model-cards/gemini-3-7-flash/) | 13 August 2026 |
| Gemini 3 Flash | `deepmind2025gemini3flash` | [Model card](https://deepmind.google/models/model-cards/gemini-3-flash/) | December 2025; publisher index specifies 17 December |
| GPT-6 Astra | `openai2026astra` | [System card](https://deploymentsafety.openai.com/gpt-6-astra) | 3 September 2026; living document with subsequent updates |
| GPT-5 mini and GPT-5 nano | `openai2025gpt5` | [System card](https://cdn.openai.com/gpt-5-system-card.pdf) | 13 August 2025 on the PDF; original announcement dated 7 August |

The actor/simulator pairing and Astra judge statements describe this study's configuration, as specified by the author and Table 2, rather than properties established by the model cards. Detailed persona analyses are identified with the Astra campaign. The third paragraph states the current single-trial design and points to Section 4.3 for historical coverage and eligibility. Sections 4.2 and 4.3, the scorecard values, and all figure assets are unchanged.

Validation: three prose paragraphs, approximately 221 words excluding citation/reference commands; the coverage paragraph contains two sentences. Rebuilt the 33-page PDF and verified all six card citations and bibliography entries. No undefined references, duplicate citation keys, or whitespace errors were found. Existing minor box warnings remain.

## Merge of Sections 4.1 and 4.3 — 2026-10-07

Merged the statistical-analysis essentials into Section 4.1, now titled “Models, Persona Settings, and Evaluation Protocol.” Section 4.2 retains the metric definitions. The `sec:statistical-protocol` label now resolves to Section 4.1, and the old self-reference and separate Section 4.3 heading are removed.

The compact coverage paragraph distinguishes the current single-trial design from historical analyses that average available repeats within tasks. It retains analysis-specific coverage and the domain table's use of valid repaired outputs. The 20,000-resample study-cluster bootstrap statement is explicitly limited to the Astra scorecard, as verified in `Experiment/02_performance_and_fields/data/model_scorecard/summary.json`; it is not generalized to all seven model rows or to collaborator-reported Haiku behavioral intervals. Table 2's existing source qualification remains unchanged.

Removed duplicated profile-selection language from this methods passage; the corresponding statement remains in the Abstract. Figure 5B's failure-conditioned complete-fact recovery remains explicitly described in its caption and Section 5.5, while Section 4.2 defines the recovered-fact fraction used by the scorecard. Historical evaluator configuration details remain in source records and the pending audit; no new claim of identical historical evaluator versions is introduced. Consolidated the two unfinished configuration/coverage audit TODOs into one note rather than marking them complete. Model-card citations, recorded estimates, and figure assets are unchanged.
