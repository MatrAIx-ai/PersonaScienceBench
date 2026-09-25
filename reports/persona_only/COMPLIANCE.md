# Phase 1 requirement audit

This audit describes the corrected release, not the superseded persona-only
package. Test results and limits are in [VALIDATION.md](VALIDATION.md).

| Requirement | Implementation and evidence | Boundary |
|---|---|---|
| Simulate a human researcher | 56 science behavior anchors are rendered by the researcher profile | Human realism is not established by code tests |
| Persona only in a private system prompt | Reply generation uses `system.identity`; grounding gets no profile; actor input is unchanged | Private config/logs must stay outside actor mounts |
| Off retains the same simulator and facts | Same common instructions, model, fact filtering, grounding and call sequence; only identity omitted | Off is not a no-researcher baseline |
| Same task/data/environment/budget | All original task/runtime/runner/config files remain byte-identical; arm configs differ only in persona; planner fingerprints declared inputs | Live runtime and complete dependency coverage still need receipts |
| Same scientific facts and gold | Episode/fact pool/evaluator and declared private references are frozen | Naturally selected/disclosed facts can differ as an interaction outcome |
| Same original scientific evaluation | Original adapters, native scoring bridges and schema are protected by the 83-file scope audit | No new native run is claimed; inherited benchmark limitations remain |
| One persona dimension at a time | Each contrast is generated from a common reference by one level or field change; unknown/extra/no-op/duplicate changes fail validation | Broad expertise labels are explicit narrow operational proxies |
| Same 50 tasks, approximately 600 episodes | Planner requires exactly 50 unique reviewed source tasks and crosses each with all arms; proposed 12-arm design yields 600 | Actual 50-task list is absent; template is intentionally unfilled |
| Observe behavior and original score | Existing events plus read-only counts; native evaluation JSON retained unchanged | Counts alone do not establish quality, causal dependence or adaptation |
| Keep Phase 2 separate | No new gates, tasks, forced questions, negotiation/revision controller or interaction score | Subsequent protocol extensions require a separate version and evidence |
| Retain zero-question/null effects | Original first-valid-final behavior and budget remain; no consultation is required | Persona may be unobservable in an episode |

## Corrected gaps

1. The previous off path replaced the common response instruction string. It now
   removes only identity and shares policy version `persona-conditioning-only-v3`.
2. The previous grounding request received a separate persona-preferences payload.
   It now performs the same persona-independent factual-support check in all arms.
3. Whole-profile examples were insufficient for a one-dimension experiment. They
   are now separated from the explicit reference/contrast design and planner.
4. The previous ODE preview read an old prepared Episode with collaboration
   metadata. Current evidence is regenerated from the unchanged original adapter;
   known superseded collaboration markers are rejected by the planner.
5. Team instructions now specify cohort invariants, comparison estimands, private
   file placement, launcher checks, raw native results and the Phase 2 boundary.

## Still required before the actual experiment

Register the actual 50-task cohort and chosen arm matrix; provision its native
inputs/runtimes; verify that each launcher uses the intended simulator and settings;
run the episodes under the original evaluation protocol; then analyze matched
outcomes and independently inspect simulator fidelity. The separate EXP runners
are not integrated with this planner and must not be silently treated as covered.

The 12-arm allocation is a clearly labeled proposal. The synthetic 50-task test
fixture validates software bookkeeping, not 50 scientific tasks or 600 model runs.
There were no live model calls, native scientific executions or human calibration
for this revision. These limits cannot be converted into guarantees by passing
unit tests or checking file hashes.
