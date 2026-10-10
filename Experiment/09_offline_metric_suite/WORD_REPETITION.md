# Word-based within-conversation repetition

Current panel A uses exact four-word sequences separately for simulator and actor. This revision was requested after viewing the character-based results; it is exploratory. The 40-character analysis remains available in SELF_REPETITION.md and the prior figure is archived under revisions/v5_character_matching/. No new model calls or embeddings.

## Definition

For every later length-eligible message, slide a four-token window one token at a time. A window matches if its ordered token tuple occurred in an earlier message of the same role and conversation. Divide matched windows by all current-message windows, then average eligible later turns. The first eligible message only provides history; within-current-message repetition alone is not counted. Exact token equality is required: no stemming, synonym matching or semantic comparison. Short phrases can match despite surrounding edits.

Tokens: remove code fences and Markdown blockquote lines; Unicode NFKC and casefold. Han-script spans use jieba 0.42.1 dictionary segmentation with HMM=False; other spans use Unicode letter/mark/number runs with internal apostrophes retained. Punctuation/whitespace separate words, so word boundaries are preserved. Hindi combining marks and Cyrillic letters are retained. Stopwords and numbers are retained. No tokenizer model inference or translation. Tokenization and language differences still affect comparability; Chinese dictionary words are approximations, not guaranteed linguistic segmentation.

## Aggregation and interpretation

Average turns within episode, eligible trials within question, questions within benchmark, then benchmarks equally. Retain a common five-setting question panel separately for each role/window size. Require at least two messages containing enough tokens; unavailable is not zero. CIs use 20,000 source-study bootstrap draws conditional on saved trials. Paired contrasts compare question means; available repeat counts differ. The four-word choice was fixed before this extraction; two- and three-word results are sensitivities. Unigram reuse is provided as vocabulary reuse, which naturally includes recurring scientific terms and function words and should not be called conversational stagnation.

| Role | Words/window | Common questions | Sources |
|---|---|---|---|
| simulator | 1 | 81 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| simulator | 2 | 81 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| simulator | 3 | 81 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| simulator | 4 | 81 | {"asibench": 7, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| actor | 1 | 80 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| actor | 2 | 80 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| actor | 3 | 80 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |
| actor | 4 | 80 | {"asibench": 6, "bixbench": 27, "discoverybench": 21, "expbench": 6, "sciconvbench": 20} |

## Simulator — four-word repetition

| Setting | Repeated word windows % [95% CI] | Paired Δ vs off (pp) |
|---|---|---|
| Off | 2.03 [1.60, 2.51]; n=81, g=58 | Reference |
| 155 | 2.54 [2.04, 3.11]; n=81, g=58 | 0.51 [0.03, 1.01]; n=81, g=58 |
| 001 | 2.24 [1.77, 2.70]; n=81, g=58 | 0.21 [-0.30, 0.61]; n=81, g=58 |
| 003 | 2.14 [1.47, 2.91]; n=81, g=58 | 0.11 [-0.51, 0.74]; n=81, g=58 |
| 046 | 3.21 [2.26, 4.19]; n=81, g=58 | 1.18 [0.24, 2.12]; n=81, g=58 |

## Actor — four-word repetition

| Setting | Repeated word windows % [95% CI] | Paired Δ vs off (pp) |
|---|---|---|
| Off | 1.63 [1.31, 1.99]; n=80, g=57 | Reference |
| 155 | 1.89 [1.53, 2.30]; n=80, g=57 | 0.27 [-0.16, 0.69]; n=80, g=57 |
| 001 | 1.56 [1.31, 1.87]; n=80, g=57 | -0.07 [-0.51, 0.38]; n=80, g=57 |
| 003 | 0.87 [0.59, 1.14]; n=80, g=57 | -0.76 [-1.17, -0.39]; n=80, g=57 |
| 046 | 1.99 [1.66, 2.35]; n=80, g=57 | 0.36 [-0.13, 0.84]; n=80, g=57 |

## Window-size sensitivity

| Role | Words/window | Off | 155 | 001 | 003 | 046 |
|---|---|---|---|---|---|---|
| simulator | 1 | 55.876 | 61.338 | 57.586 | 41.192 | 58.812 |
| simulator | 2 | 14.153 | 14.695 | 13.972 | 12.203 | 17.595 |
| simulator | 3 | 4.950 | 5.409 | 5.291 | 5.062 | 6.686 |
| simulator | 4 | 2.032 | 2.544 | 2.241 | 2.141 | 3.211 |
| actor | 1 | 60.884 | 58.756 | 57.113 | 42.250 | 56.719 |
| actor | 2 | 14.131 | 14.133 | 13.309 | 8.484 | 15.399 |
| actor | 3 | 4.421 | 4.578 | 3.920 | 2.373 | 5.148 |
| actor | 4 | 1.628 | 1.894 | 1.556 | 0.865 | 1.986 |

These are different definitions and can have different eligible turns/questions. Four-word and 40-character rates are not interchangeable. Higher measured overlap under shorter phrases does not imply more mode collapse. Required scientific vocabulary, stock politeness and legitimate fact restatement can contribute; paraphrases remain undetected. Persona language, output length and dialogue duration can confound comparisons. Intervals are pointwise; no new significance claims or persona ranking are selected from the sensitivities.

[Figure](figures/metric_suite.pdf) · [Notebook](metric_suite.ipynb). Source tables are data/word_repetition_{episodes,turns,cases,cells,contrasts}.csv. Snapshots contain numeric values and hashes, not transcripts or word strings.

Reproduce with `OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/word_repetition.py`. Dictionary/version provenance is in data/word_repetition_summary.json.
