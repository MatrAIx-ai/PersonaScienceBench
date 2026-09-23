# Sonnet 5 judge comparison

Ten saved plans, with no actor or simulator reruns. Scores are reference coverage means over three judgments. Both coverage and integrity now use Sonnet 5, with the original system prompts and JSON-object mode. Claude rejected the original empty user message (HTTP 400), so its user message is "Apply the evaluation instructions above." This compatibility change is a protocol difference from the historical o3-mini grades. No additional quality rubric or validation suite was run.

| Task | Simulator | o3-mini judge | Sonnet 5 judge | Sonnet integrity |
| --- | --- | ---: | ---: | --- |
| JaxMARL | sonnet5_simulator | 66.7 | 46.7 | passed |
| JaxMARL | o3mini_simulator | 75.7 | 81.7 | parse_error |
| QuaRot | sonnet5_simulator | 45.3 | 31.7 | passed |
| QuaRot | o3mini_simulator | 52.3 | 40.0 | passed |
| CycleNet | sonnet5_simulator | 70.0 | 59.0 | passed |
| CycleNet | o3mini_simulator | 46.0 | 41.7 | passed |
| MogaNet | sonnet5_simulator | 51.3 | 41.7 | passed |
| MogaNet | o3mini_simulator | 54.7 | 40.0 | passed |
| SineNet | sonnet5_simulator | 82.3 | 58.3 | parse_error |
| SineNet | o3mini_simulator | 100.0 | 66.7 | passed |

## Means

- sonnet5_simulator: o3-mini judge 63.13; Sonnet 5 judge 47.47; Sonnet integrity-gated coverage 35.80.
- o3mini_simulator: o3-mini judge 65.73; Sonnet 5 judge 54.00; Sonnet integrity-gated coverage 37.67.

API-reported cost for completed regrading: $0.690528. Two earlier HTTP 400 requests returned no usage accounting; their billing is unconfirmed. The rejected attempt is preserved in `runs/sonnet5-judge-comparison-20260922`.

Eight integrity checks passed the strict parser. Two exhausted all three parse attempts because Sonnet wrapped otherwise valid JSON in Markdown fences: JaxMARL with the o3-mini simulator and SineNet with the Sonnet simulator. Inspection of all six fenced responses found all three violation flags false. The recorded monitor statuses remain `parse_error`, and the original gate assigns zero to those cases; no scores were retroactively repaired. Thus the lower gated means include format failures, not detected misconduct. Standalone reference coverage above is unaffected.

These paired grades isolate judge differences on the saved plans. They do not establish which judge is more accurate without human adjudication. The simulator conditions still have different actor trajectories; four of five episodes in each condition did not query a simulator. Sonnet uses a 4,096-output-token allowance without configured reasoning; the historical o3-mini judge used medium reasoning within the same allowance.

Artifacts: [sonnet5-judge-comparison-compatible-20260922](../../runs/expbench/sonnet5-judge-comparison-compatible-20260922/summary.json).
