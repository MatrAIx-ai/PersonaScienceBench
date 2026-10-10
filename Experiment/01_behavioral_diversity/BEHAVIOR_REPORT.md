> Expanded eight-persona analysis: [all completed-trial personas](ALL_PERSONAS_BEHAVIOR.md). This report preserves the original six-setting results.

# Experiment 01 — Behavioral diversity without semantic trajectories

[Executed notebook](behavioral_analysis.ipynb) · [Separate SciConv API-token analysis](SCICONV_TOKENS.md)

Original Astra-low panel: off/148/155/089/001/127 × 200 frozen tasks × three trials. Analyses use complete saved episodes, including completed scientific missing submissions; infrastructure-truncated traces are excluded. Repairs, Sol and the post-PR6 failed baseline are not pooled. No model calls or semantic embeddings.

## Principal observations

- Communication length separates the selected personas beyond repeat variation: excess between-persona absolute reply-length difference is 196.10 [185.64, 207.81] characters (n=111 tasks). Restricting to English-primary personas with Latin-script replies retains an excess of 44.48 [37.08, 53.08] characters (n=136 tasks).
- Extra approach reviews, revision requests and post-reply SciConv question counts show much smaller excess variation; all three excess-distance intervals include zero. Required-review workflows leave little optional review variation in the complete panel.
- Exact 40-character opening collisions are lower between personas than within persona-off by 8.95 [4.30, 14.05] percentage points (n=102 tasks). This is a script-matched lexical diagnostic, not evidence about semantic collapse.
- Character counts and API tokens can move differently across languages. In particular, Mandarin-primary 155 has shorter character strings despite its larger SciConv token usage in the separate token report. Neither measures information quality.

## Coverage

| Persona | Complete analyzed episodes | Excluded slots |
|---|---|---|
| Off | 565 | 35 |
| 148 | 559 | 41 |
| 155 | 545 | 55 |
| 089 | 572 | 28 |
| 001 | 568 | 32 |
| 127 | 573 | 27 |

## Definitions and uncertainty

An observation is an episode-level summary; repeats average within task, then sources receive equal weights for all-source summaries. Within a source tasks have equal weight. Pointwise 95% intervals use 20,000 study-cluster bootstrap draws within source, conditional on the observed trials. Paired changes match task and trial before averaging. The same trial number is a run block, not a shared random seed. No multiplicity-corrected significance claim is made.

Simulator length counts visible reply characters, excluding initial requests and private evidence. Actor length counts shared handoff answers or SciConv questions; tool calls and final SciConv specifications are excluded. Additional reviews subtract the required first review in each phase. Revision requests are simulator requests to continue during result review, not proof that a revision was completed. Absent opportunities remain missing rather than zero.

Script agreement compares actor text with the preceding noninitial simulator reply. Unicode script labels (Latin, CJK, Devanagari, Other) require at least 20 letters and 60% dominance; they are not language identification. Code fences are excluded for script/repetition analysis. Length and script differences do not establish information quality.

SciConv first questions precede persona-conditioned replies, so post-reply questions exclude the first. Exact repeated-question percentage requires at least two questions. Native clarification/grounding/memory fields are retained only inside [0,1], then displayed as percentages; invalid values are missing, not clipped. Ten-reply cap hits remain a proxy for the historical last-answer issue.

Native-metric validation flagged 0 episodes with at least one invalid field.

## Behavioral patterns

![Matched behavioral changes](figures/behavior/behavior_effects.png)

Colors show paired differences divided by the matched baseline task-level standard deviation, solely for display. Cell text gives the raw change and its 95% CI. Negative and positive changes are not intrinsically bad or good. See the tables below for all units and denominators.

![Task-level reply-length changes](figures/behavior/reply_length_distribution.png)

All matched task-level reply-length differences are shown, with no point subsampling. The teal estimates use equal source weights; raw points display individual tasks. Language and workflow affect character counts.

### Simulator characters/reply

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 844.00 [817.24, 873.72]; n=196, e=557 | reference |
| 148 | 905.21 [873.60, 940.61]; n=196, e=551 | +60.44 [48.01, 73.48]; n=193, e=538 |
| 155 | 327.56 [317.77, 338.39]; n=197, e=536 | -515.95 [-536.85, -496.43]; n=196, e=524 |
| 089 | 751.68 [725.51, 779.10]; n=199, e=569 | -93.42 [-107.49, -80.30]; n=195, e=535 |
| 001 | 672.24 [653.29, 693.24]; n=199, e=561 | -175.59 [-189.95, -162.06]; n=195, e=528 |
| 127 | 868.78 [839.83, 899.69]; n=197, e=566 | +25.53 [12.37, 38.37]; n=193, e=537 |

### Actor characters/handoff or question

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 5222.67 [4930.08, 5550.57]; n=196, e=557 | reference |
| 148 | 5619.42 [5261.93, 6018.66]; n=196, e=551 | +380.50 [242.74, 515.27]; n=193, e=538 |
| 155 | 2232.16 [2118.00, 2374.76]; n=197, e=536 | -2993.28 [-3205.11, -2787.95]; n=196, e=524 |
| 089 | 4840.59 [4531.25, 5141.80]; n=199, e=569 | -338.11 [-517.96, -189.34]; n=195, e=535 |
| 001 | 4314.61 [4117.08, 4509.70]; n=199, e=561 | -894.59 [-1097.40, -738.80]; n=195, e=528 |
| 127 | 5411.51 [5130.00, 5730.22]; n=197, e=566 | +241.82 [125.16, 355.36]; n=193, e=537 |

### Completed handoffs or clarification replies

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 2.36 [2.18, 2.56]; n=198, e=565 | reference |
| 148 | 2.29 [2.13, 2.46]; n=198, e=559 | -0.07 [-0.14, -0.02]; n=195, e=546 |
| 155 | 2.36 [2.18, 2.54]; n=199, e=545 | -0.01 [-0.08, 0.06]; n=198, e=533 |
| 089 | 2.39 [2.21, 2.58]; n=200, e=572 | +0.01 [-0.04, 0.07]; n=197, e=543 |
| 001 | 2.35 [2.19, 2.53]; n=200, e=568 | -0.01 [-0.08, 0.05]; n=198, e=537 |
| 127 | 2.35 [2.18, 2.52]; n=198, e=573 | -0.02 [-0.10, 0.07]; n=195, e=545 |

### Additional approach reviews

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.01 [0.00, 0.02]; n=158, e=445 | reference |
| 148 | 0.00 [0.00, 0.01]; n=158, e=439 | -0.00 [-0.02, 0.01]; n=155, e=426 |
| 155 | 0.01 [0.00, 0.02]; n=159, e=425 | +0.00 [-0.02, 0.02]; n=158, e=413 |
| 089 | 0.01 [0.00, 0.03]; n=160, e=453 | +0.00 [0.00, 0.01]; n=157, e=424 |
| 001 | 0.00 [0.00, 0.01]; n=160, e=448 | -0.00 [-0.01, 0.00]; n=158, e=417 |
| 127 | 0.00 [0.00, 0.01]; n=158, e=453 | -0.00 [-0.01, 0.00]; n=155, e=425 |

### Additional result reviews

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.07 [0.03, 0.13]; n=158, e=445 | reference |
| 148 | 0.05 [0.03, 0.08]; n=158, e=439 | -0.02 [-0.07, 0.03]; n=155, e=426 |
| 155 | 0.08 [0.04, 0.11]; n=159, e=425 | +0.00 [-0.05, 0.05]; n=158, e=413 |
| 089 | 0.07 [0.04, 0.12]; n=160, e=453 | -0.02 [-0.06, 0.02]; n=157, e=424 |
| 001 | 0.11 [0.07, 0.16]; n=160, e=448 | +0.04 [-0.01, 0.09]; n=158, e=417 |
| 127 | 0.08 [0.04, 0.14]; n=158, e=453 | +0.01 [-0.06, 0.08]; n=155, e=425 |

### Result-review requests to continue

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.08 [0.03, 0.14]; n=158, e=445 | reference |
| 148 | 0.05 [0.03, 0.08]; n=158, e=439 | -0.02 [-0.08, 0.02]; n=155, e=426 |
| 155 | 0.08 [0.05, 0.12]; n=159, e=425 | +0.00 [-0.05, 0.05]; n=158, e=413 |
| 089 | 0.07 [0.04, 0.12]; n=160, e=453 | -0.02 [-0.07, 0.02]; n=157, e=424 |
| 001 | 0.11 [0.07, 0.16]; n=160, e=448 | +0.03 [-0.02, 0.08]; n=158, e=417 |
| 127 | 0.08 [0.04, 0.15]; n=158, e=453 | +0.01 [-0.06, 0.09]; n=155, e=425 |

### Researcher budget reached (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.21 [0.00, 0.68]; n=158, e=445 | reference |
| 148 | 0.00 [0.00, 0.00]; n=158, e=439 | -0.21 [-0.68, 0.00]; n=155, e=426 |
| 155 | 0.00 [0.00, 0.00]; n=159, e=425 | -0.21 [-0.68, 0.00]; n=158, e=413 |
| 089 | 0.00 [0.00, 0.00]; n=160, e=453 | -0.21 [-0.68, 0.00]; n=157, e=424 |
| 001 | 0.00 [0.00, 0.00]; n=160, e=448 | -0.21 [-0.68, 0.00]; n=158, e=417 |
| 127 | 0.21 [0.00, 0.69]; n=158, e=453 | +0.00 [-0.58, 0.62]; n=155, e=425 |

### Actor call budget reached (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.00 [0.00, 0.00]; n=158, e=445 | reference |
| 148 | 0.00 [0.00, 0.00]; n=158, e=439 | +0.00 [0.00, 0.00]; n=155, e=426 |
| 155 | 0.00 [0.00, 0.00]; n=159, e=425 | +0.00 [0.00, 0.00]; n=158, e=413 |
| 089 | 0.00 [0.00, 0.00]; n=160, e=453 | +0.00 [0.00, 0.00]; n=157, e=424 |
| 001 | 0.00 [0.00, 0.00]; n=160, e=448 | +0.00 [0.00, 0.00]; n=158, e=417 |
| 127 | 0.00 [0.00, 0.00]; n=158, e=453 | +0.00 [0.00, 0.00]; n=155, e=425 |

### Actor/simulator dominant-script agreement (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 100.00 [100.00, 100.00]; n=185, e=515 | reference |
| 148 | 100.00 [100.00, 100.00]; n=185, e=506 | +0.00 [0.00, 0.00]; n=178, e=489 |
| 155 | 93.27 [90.43, 95.64]; n=182, e=449 | -6.68 [-9.58, -4.28]; n=179, e=433 |
| 089 | 100.00 [100.00, 100.00]; n=187, e=526 | +0.00 [0.00, 0.00]; n=181, e=489 |
| 001 | 93.72 [91.27, 95.98]; n=156, e=383 | -6.15 [-8.63, -3.86]; n=153, e=352 |
| 127 | 100.00 [100.00, 100.00]; n=186, e=525 | +0.00 [0.00, 0.00]; n=179, e=490 |

### Simulator CJK letters (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.00 [0.00, 0.00]; n=196, e=557 | reference |
| 148 | 0.00 [0.00, 0.00]; n=196, e=551 | +0.00 [0.00, 0.00]; n=193, e=538 |
| 155 | 79.50 [78.20, 80.63]; n=197, e=536 | +79.47 [78.17, 80.60]; n=196, e=524 |
| 089 | 0.00 [0.00, 0.00]; n=199, e=569 | +0.00 [0.00, 0.00]; n=195, e=535 |
| 001 | 0.00 [0.00, 0.00]; n=199, e=561 | +0.00 [0.00, 0.00]; n=195, e=528 |
| 127 | 0.00 [0.00, 0.00]; n=197, e=566 | +0.00 [0.00, 0.00]; n=193, e=537 |

### Simulator Devanagari letters (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.00 [0.00, 0.00]; n=196, e=557 | reference |
| 148 | 0.00 [0.00, 0.00]; n=196, e=551 | +0.00 [0.00, 0.00]; n=193, e=538 |
| 155 | 0.00 [0.00, 0.00]; n=197, e=536 | +0.00 [0.00, 0.00]; n=196, e=524 |
| 089 | 0.00 [0.00, 0.00]; n=199, e=569 | +0.00 [0.00, 0.00]; n=195, e=535 |
| 001 | 43.08 [41.60, 44.53]; n=199, e=561 | +43.31 [41.78, 44.79]; n=195, e=528 |
| 127 | 0.00 [0.00, 0.00]; n=197, e=566 | +0.00 [0.00, 0.00]; n=193, e=537 |

### Exact repeated SciConv questions (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.00 [0.00, 0.00]; n=27, e=72 | reference |
| 148 | 0.00 [0.00, 0.00]; n=27, e=69 | +0.00 [0.00, 0.00]; n=24, e=66 |
| 155 | 0.00 [0.00, 0.00]; n=28, e=77 | +0.00 [0.00, 0.00]; n=25, e=68 |
| 089 | 0.00 [0.00, 0.00]; n=28, e=76 | +0.00 [0.00, 0.00]; n=25, e=68 |
| 001 | 0.00 [0.00, 0.00]; n=27, e=73 | +0.00 [0.00, 0.00]; n=25, e=68 |
| 127 | 0.00 [0.00, 0.00]; n=28, e=74 | +0.00 [0.00, 0.00]; n=25, e=68 |

### SciConv questions after first simulator reply

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 2.58 [1.70, 3.52]; n=40, e=120 | reference |
| 148 | 2.28 [1.52, 3.12]; n=40, e=120 | -0.29 [-0.56, -0.07]; n=40, e=120 |
| 155 | 2.54 [1.72, 3.42]; n=40, e=120 | -0.03 [-0.33, 0.25]; n=40, e=120 |
| 089 | 2.65 [1.80, 3.59]; n=40, e=119 | +0.08 [-0.14, 0.30]; n=40, e=119 |
| 001 | 2.36 [1.58, 3.21]; n=40, e=120 | -0.22 [-0.47, 0.01]; n=40, e=120 |
| 127 | 2.45 [1.68, 3.27]; n=40, e=120 | -0.12 [-0.45, 0.19]; n=40, e=120 |

### Ten-reply limit reached (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 10.00 [2.50, 19.19]; n=40, e=120 | reference |
| 148 | 5.83 [0.83, 12.50]; n=40, e=120 | -4.17 [-9.17, -0.83]; n=40, e=120 |
| 155 | 7.50 [1.67, 15.00]; n=40, e=120 | -2.50 [-7.50, 1.67]; n=40, e=120 |
| 089 | 11.67 [3.33, 21.67]; n=40, e=119 | +1.67 [-3.33, 6.67]; n=40, e=119 |
| 001 | 6.67 [0.83, 15.00]; n=40, e=120 | -3.33 [-9.17, 0.00]; n=40, e=120 |
| 127 | 6.67 [1.67, 13.33]; n=40, e=120 | -3.33 [-8.33, 0.83]; n=40, e=120 |

### Clarification recall (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 70.28 [58.06, 81.76]; n=40, e=120 | reference |
| 148 | 68.46 [56.59, 79.64]; n=40, e=120 | -1.82 [-8.92, 4.58]; n=40, e=120 |
| 155 | 72.82 [61.66, 83.25]; n=40, e=120 | +2.53 [-1.84, 7.67]; n=40, e=120 |
| 089 | 75.49 [64.88, 85.25]; n=40, e=119 | +5.20 [0.28, 10.87]; n=40, e=119 |
| 001 | 72.54 [60.66, 83.78]; n=40, e=120 | +2.26 [-2.12, 7.50]; n=40, e=120 |
| 127 | 72.36 [61.07, 82.96]; n=40, e=120 | +2.08 [-5.80, 9.64]; n=40, e=120 |

### Clarification precision (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 54.39 [42.74, 66.02]; n=40, e=120 | reference |
| 148 | 55.64 [44.15, 67.03]; n=40, e=120 | +1.25 [-3.60, 6.10]; n=40, e=120 |
| 155 | 55.19 [44.07, 66.16]; n=40, e=120 | +0.80 [-2.29, 4.32]; n=40, e=120 |
| 089 | 55.94 [44.90, 67.02]; n=40, e=119 | +1.48 [-2.33, 5.61]; n=40, e=119 |
| 001 | 53.63 [42.60, 64.63]; n=40, e=120 | -0.76 [-7.62, 5.38]; n=40, e=120 |
| 127 | 54.67 [43.50, 65.81]; n=40, e=120 | +0.28 [-3.04, 3.87]; n=40, e=120 |

### Conversation-grounded resolution (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 81.67 [70.00, 91.67]; n=40, e=120 | reference |
| 148 | 82.50 [72.50, 91.67]; n=40, e=120 | +0.83 [-5.00, 7.50]; n=40, e=120 |
| 155 | 77.50 [65.83, 88.33]; n=40, e=120 | -4.17 [-12.50, 4.17]; n=40, e=120 |
| 089 | 82.50 [71.67, 92.50]; n=40, e=119 | +0.83 [-5.00, 7.50]; n=40, e=119 |
| 001 | 82.50 [71.67, 91.67]; n=40, e=120 | +0.83 [-4.17, 5.83]; n=40, e=120 |
| 127 | 82.50 [71.67, 91.67]; n=40, e=120 | +0.83 [-5.00, 7.50]; n=40, e=120 |

### Silent resolution (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 3.33 [0.00, 8.33]; n=40, e=120 | reference |
| 148 | 3.33 [0.00, 7.50]; n=40, e=120 | +0.00 [-4.17, 3.33]; n=40, e=120 |
| 155 | 7.50 [1.67, 15.00]; n=40, e=120 | +4.17 [-1.67, 10.83]; n=40, e=120 |
| 089 | 5.00 [0.00, 11.67]; n=40, e=119 | +1.67 [0.00, 4.17]; n=40, e=119 |
| 001 | 7.50 [0.83, 15.83]; n=40, e=120 | +4.17 [0.00, 10.00]; n=40, e=120 |
| 127 | 6.67 [1.67, 13.33]; n=40, e=120 | +3.33 [0.83, 6.67]; n=40, e=120 |

### Memory consistency (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 87.50 [77.50, 95.83]; n=40, e=120 | reference |
| 148 | 88.33 [79.17, 95.83]; n=40, e=120 | +0.83 [-1.67, 4.17]; n=40, e=120 |
| 155 | 85.83 [75.83, 94.17]; n=40, e=120 | -1.67 [-5.00, 1.67]; n=40, e=120 |
| 089 | 86.67 [75.83, 95.83]; n=40, e=119 | -0.83 [-9.17, 8.33]; n=40, e=119 |
| 001 | 90.00 [80.83, 97.50]; n=40, e=120 | +2.50 [-0.83, 7.50]; n=40, e=120 |
| 127 | 91.67 [84.17, 97.50]; n=40, e=120 | +4.17 [-0.83, 10.00]; n=40, e=120 |

### Intent capture (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 89.17 [80.00, 96.67]; n=40, e=120 | reference |
| 148 | 88.33 [80.00, 95.83]; n=40, e=120 | -0.83 [-5.00, 4.17]; n=40, e=120 |
| 155 | 88.33 [80.83, 95.00]; n=40, e=120 | -0.83 [-5.83, 5.00]; n=40, e=120 |
| 089 | 90.00 [81.67, 96.67]; n=40, e=119 | +0.83 [-4.17, 5.83]; n=40, e=119 |
| 001 | 92.50 [85.00, 98.33]; n=40, e=120 | +3.33 [-0.83, 8.33]; n=40, e=120 |
| 127 | 92.50 [85.83, 98.33]; n=40, e=120 | +3.33 [-1.67, 10.00]; n=40, e=120 |

### Repeated reply openings within episode (%)

| Persona | Mean [95% CI]; tasks/episodes | Paired change vs off [95% CI]; tasks/pairs |
|---|---|---|
| Off | 0.00 [0.00, 0.00]; n=184, e=515 | reference |
| 148 | 0.00 [0.00, 0.00]; n=185, e=508 | +0.00 [0.00, 0.00]; n=179, e=491 |
| 155 | 0.00 [0.00, 0.00]; n=185, e=494 | +0.00 [0.00, 0.00]; n=182, e=474 |
| 089 | 0.00 [0.00, 0.00]; n=188, e=529 | +0.00 [0.00, 0.00]; n=181, e=490 |
| 001 | 0.00 [0.00, 0.00]; n=187, e=520 | +0.00 [0.00, 0.00]; n=182, e=482 |
| 127 | 0.04 [0.00, 0.10]; n=186, e=527 | +0.04 [0.00, 0.11]; n=179, e=491 |

## Repeat variation

![Within- and between-persona variation](figures/behavior/repeat_variation.png)

Each metric uses tasks with all three eligible values in every one of the six conditions. Within-condition distance is mean absolute difference over the three run pairs. Between-persona distance averages all nine episode pairs for each of the ten pairs among the five personas. Personas and persona pairs have equal weights. Pair combinations are not independent samples: distances are summarized once per task before the study bootstrap. Excess is between-persona minus within-persona distance; it describes these selected conditions rather than isolating a personality trait.

| Metric | Within off | Within personas | Between personas | Excess between − within |
|---|---|---|---|---|
| Simulator characters/reply | 89.30 [77.26, 102.07]; n=111 tasks | 77.47 [70.23, 84.80]; n=111 tasks | 273.58 [261.30, 286.76]; n=111 tasks | 196.10 [185.64, 207.81]; n=111 tasks |
| Additional approach reviews | 0.03 [0.00, 0.07]; n=75 tasks | 0.01 [0.00, 0.04]; n=75 tasks | 0.02 [0.00, 0.04]; n=75 tasks | 0.00 [-0.00, 0.01]; n=75 tasks |
| Result-review requests to continue | 0.14 [0.03, 0.29]; n=75 tasks | 0.09 [0.05, 0.15]; n=75 tasks | 0.10 [0.05, 0.15]; n=75 tasks | 0.00 [-0.00, 0.01]; n=75 tasks |
| SciConv questions after first simulator reply | 0.56 [0.34, 0.82]; n=39 tasks | 0.74 [0.51, 0.98]; n=39 tasks | 0.77 [0.53, 1.03]; n=39 tasks | 0.03 [-0.05, 0.12]; n=39 tasks |

### English-primary length sensitivity

Restrict to off/148/089/127, selected by their explicit English-primary profile instruction, and require Latin-script first replies in all three runs. This removes the Mandarin/Hindi-primary personas; it is a sensitivity on a different complete task panel, not a controlled language intervention.

| Comparison | Absolute reply-length difference [95% CI] |
|---|---|
| persona within | 93.56 [85.05, 102.21]; n=136 tasks |
| between personas | 138.05 [128.41, 148.90]; n=136 tasks |
| excess | 44.48 [37.08, 53.08]; n=136 tasks |

## Exploratory template concentration

Openings are the first 40 alphanumeric Unicode characters after NFKC normalization, case folding and code-fence removal. Only replies with at least 40 such characters qualify. Initial requests and required controller/schema text are excluded; only researcher message content is used. First-reply collisions require the full repeated panel, one consistent baseline script across its three runs, and at least two personas sharing that script in all three runs. The same eligible personas enter within- and between-persona comparisons; persona pairs receive equal weights. Eligible personas can vary by task and are recorded. Fixed prefix length limits sample-length artifacts, but does not make this a semantic or language-normalized measure. The within-episode opening-repeat metric is separate and conditions on at least two eligible replies. Neither measure proves semantic collapse.

| Comparison | Opening collision % or reduction (pp) [95% CI]; tasks |
|---|---|
| baseline within | 13.65 [8.96, 18.69]; n=102 tasks |
| persona within | 15.65 [12.01, 19.24]; n=102 tasks |
| between personas | 4.69 [3.49, 5.92]; n=102 tasks |
| reduction vs off | 8.95 [4.30, 14.05]; n=102 tasks |
| reduction vs within | 10.96 [8.08, 13.80]; n=102 tasks |

## Scope remaining

Semantic trajectories and embedding-based distances are deliberately deferred. Disagreement, feedback adoption, and per-fact volunteering need content annotation and are not inferred from character counts or decision actions. No human realism evaluation is planned. The selected profiles were chosen using prior performance, and missing complete traces can change coverage. All-source summaries mix workflows; per-benchmark values and full denominators are in the numeric summary.

[Numeric summary](data/behavior/summary.json) · [Episode features](data/behavior/episodes.csv) · [Paired effects](data/behavior/paired_effects.csv) · [Frozen provenance](data/behavior/snapshot.json)

Reproduce: `.venv/bin/python Experiment/01_behavioral_diversity/code/analyze_behavior.py`; use `--refresh` only to re-extract saved event logs. Plot with `code/plot_behavior.py`.
