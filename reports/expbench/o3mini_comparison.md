# o3-mini actor comparison and evaluation audit

The five-task o3-mini actor run completed on September 22, 2026 UTC. Researcher:
Sonnet 5. Judge: o3-mini with the same v2 prompt used for the final Sonnet 5
grades. Actor reasoning effort: medium. Limits: at most 20 actor steps and six
researcher questions, with no dollar caps. No experiments were executed.

These are diagnostic pilot results, not validated scientific-quality scores or
a reproduction of the paper's reported design scores.

## Results

| Task | Sonnet 5 actor, v2 score | o3-mini actor, v2 score | o3-mini actor calls | Researcher questions | Cited fact-bank entries | Total API cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| JaxMARL | 95 | 95 | 2 | 1 | 2/4 | $0.019930 |
| QuaRot | 100 | 100 | 2 | 1 | 4/4 | $0.019186 |
| CycleNet | 100 | 80 | 3 | 1 | 2/5 | $0.021926 |
| MogaNet | 100 | 80 | 1 | 0 | 0/3 | $0.011595 |
| SineNet | 100 | 100 | 3 | 1 | 3/3 | $0.018474 |
| **Mean score / total cost** | **99** | **91** | | | | **$0.091110** |

Fact counts are unique cited fact IDs, not counts of atomic claims. Some entries
bundle several facts, and citations alone do not establish complete entailment.
Costs sum provider-reported usage; actor $0.0412467, researcher $0.019322,
judge $0.0305415. Per-task rounding may differ from the unrounded total.

The task and source-code hashes exactly match the v2 regrading manifest. All
five output schemas passed validation; no actor API request followed submission;
all tool observations were successful. The current run contains no API-key
pattern. Only configuration changed; no new implementation tests were needed.
The existing implementation had passed 25 tests before this run.

## Simulator disclosure concern

QuaRot's actor asked one broad question about the existing evaluation setup,
metrics, datasets, and baseline conditions. The researcher supplied all four
approved entries: model sizes, WikiText-2 and sequence length, precision settings,
and the QR-based random-matrix construction. These overlap heavily with the
reference variables that determine the score. The QR construction is particularly
questionable as unsolicited implementation guidance in response to this question.

SineNet similarly received all three approved entries in one answer. That reply
also offered to propose assumptions for the actor, although the researcher is
intended to provide facts rather than perform the design work.

This is not evidence that the hidden reference dictionary was directly exposed:
the researcher has a separately curated fact bank derived from source methods.
However, broad questions can reveal most of the information needed for the
current rubric. A stronger model ranking cannot be inferred from this setup.
No disclosure ablation has been run, so the simulator's causal contribution to
the scores is not quantified.

## Independent judge concern

MogaNet received **80/100 without any researcher interaction**. Its submitted
dataset was only "ImageNet or a standard benchmark"; its training settings were
generic labels, not the required recipe; and its feature-interaction measures
were correlation, mutual information, or attention maps rather than J(m).
The judge listed these omissions but still awarded 80. This makes simulator
disclosure an incomplete explanation for the high scores.

JaxMARL received 95 despite omitting the nine-map selection requirement. Both
examples show generous semantic matching and discretionary deductions rather
than an explicit, reproducible item tally. The adapted judge also allows
equivalent formulations without independently verifying their equivalence.

The original released judge prompt is not deterministic either: it asks for a
percentage of matching items but does not define atomic items or their weights.
Our adapted coverage score should not be presented as an objective percentage
of scientific correctness.

## Other comparison and curation issues

The released original judge sets design, implementation, and conclusion scores
to zero if its integrity monitor detects forbidden behavior or returns a parse
error. This design-only pilot omits that full-experiment gate. Therefore even
the paper's design-score column is not directly comparable with these scores.
The size of the monitor's contribution to the published averages has not been
measured here. [Pinned original judge code](https://github.com/Just-Curieous/Curie/blob/db1b1f56159b591515f77e03c55bf473d5c1c201/benchmark/exp_bench/evaluation/judge.py#L290)

The curation audit also found an omission in our JaxMARL researcher facts: the
source method explicitly requests training time to convergence, whereas our
fact card says only training time in minutes. The exact convergence threshold
is unspecified, but the requirement to use a convergence criterion should not
have been dropped. This omission can induce a design-reference mismatch even
when the actor asks a relevant question. Existing cards and results are retained
unchanged for auditability; a correction should receive a new task version.

## Recommended next changes, not yet applied

1. Separate each researcher's fixed project constraints and available resources
   from experimental choices that the actor should make. Split bundled entries
   into atomic facts with precise source locations.
2. Restrict retrieval and responses to the explicitly requested subject. Broad
   requests should lead to a focused clarification, not a complete fact-bank
   dump. The researcher should not propose the actor's experimental plan.
3. Preserve access to genuine requirements. If a requirement is removed and
   becomes an open design choice, the rubric must accept defensible alternatives;
   otherwise the actor is penalized for failing to guess a hidden setting.
4. Independently validate grading with item-level evidence and controlled missing
   or incorrect designs. Report the current score separately from any new rubric.
5. Test disclosure changes with the judge held fixed. Test judge changes on saved
   designs. Changing both together would obscure which change caused a score
   difference. Repeat runs are needed to measure stochastic variation.

## Artifacts

- [Run summary](../../runs/expbench/pilot-o3mini-20260922/summary.json)
- [Configuration](../../configs/expbench/pilot-o3mini.toml)
- [Manifest](../../runs/expbench/pilot-o3mini-20260922/manifest.json)
- [QuaRot researcher reply](../../runs/expbench/pilot-o3mini-20260922/neurips2024__94328__5/researcher_history.json)
- [MogaNet design](../../runs/expbench/pilot-o3mini-20260922/iclr2024__18447__7/design.json)
- [MogaNet judge explanation](../../runs/expbench/pilot-o3mini-20260922/iclr2024__18447__7/grade.json)

Each task directory contains the design, grade, actor events, researcher
conversation, API responses, usage, and private task snapshot. These private
artifacts must not be supplied as actor inputs.
