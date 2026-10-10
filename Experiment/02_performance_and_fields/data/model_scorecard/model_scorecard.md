| Actor model | Persona-off performance | Mean Persona Performance | Fact recovery (%) | Self-repetition (%) |
|---|---|---|---|---|
| GPT-6 Astra (low) | 47.54 [39.11, 55.46] | 48.82 [40.46, 56.67] | 88.86 [76.96, 97.68] | 12.69 [11.65, 13.73] |
| Claude Haiku 4.5 | 21.97 [16.25, 27.71] | 19.72 [15.19, 24.14] | 67.95 [61.77, 74.37] | 21.43 [17.23, 24.53] |

Estimates [95% CI where available].

Haiku actor and simulator: Claude Haiku 4.5; judge: GPT-6 Astra. Performance uses 200 questions (40 per benchmark), five settings, one trial, including 120 non-submissions; 95% intervals use the benchmark-stratified study-cluster bootstrap. Haiku fact recovery (67.95%) and self-repetition (21.43%) are collaborator-reported measurements and 95% confidence intervals supplied by the author on 2026-10-07. Their underlying metric records, exact aggregation, sample counts and CI computation method are not available locally; these estimates and intervals have not been independently reproduced. They replace the incorrectly labelled older Opus-simulator values. All non-Off columns represent the four-persona mean; performance weights benchmarks and personas equally.
