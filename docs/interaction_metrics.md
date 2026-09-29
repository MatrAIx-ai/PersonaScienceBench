# Offline interaction metrics

Use the saved-run analyzer to export DiscoveryBench outcomes and ActiveResearcher
interaction counts without model calls or regrading:

```bash
PYTHONPATH=src .venv/bin/python scripts/analyze_discoverybench_interactions.py \
  --run-root runs/example-batch --output runs/example-analysis \
  --annotation-output runs/example-annotations.private.json
```

A batch contains `CONDITION/config.json`, `summary.json`, and episode directories;
`CONDITION/repeat_01/` layouts also work. Multiple `--run-root` arguments are
supported. `--manifest` selects task IDs and analysis-family/subfield tags; its
default is the six-question ecology panel. Supply a matching manifest for other
DiscoveryBench tasks. Output paths must be new.

The utility writes `metrics.json` and `episodes.csv`. The optional separate
annotation packet contains visible messages and event IDs, excluding condition
names, native scores, private researcher evidence, tool output and submission
payloads. It makes no semantic judgments. Raw API/event logs remain local.

| Measurement | Interpretation |
|---|---|
| Handoffs/reviews | Plan and result reviews are required; extra reviews are counted separately |
| Revision requests | Result-review decisions with action `continue`; distinct from completed revisions |
| Optional questions | Researcher-question tool calls and exact-text repeats; embedded handoff questions need annotation |
| Visible length | Unicode code points including whitespace, separated by role; researcher replies exclude the initial request |
| Execution/usage | Command failures/timeouts, budget exhaustion, and reported API tokens/calls by role |
| Trace coverage | Finished, partial, absent or invalid; missing traces do not become zero interaction |
| Matched scores | Within-batch task/public-input/config matches, means and sample SD; known evaluator/model mismatches rejected |

Missing submissions receive analysis zero without inventing native grades;
infrastructure/evaluator errors remain counted but unscored. A single repeat has
undefined SD. Every attempt remains visible; no best-of selection is performed.
Questions from one study do not become independent studies.

Question usefulness, feedback uptake and persona fidelity require evidence-backed
annotation. No-question traces do not imply perfect precision. HiL-Bench's
[ASK-F1](https://arxiv.org/html/2604.09408v2) also requires a validated blocker
registry, which these native ecology tasks lack; its value remains not applicable.
Keep interaction measures separate from native reference agreement and independent
scientific verification.
