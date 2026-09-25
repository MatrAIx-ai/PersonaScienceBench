# Team handoff

Use the [current conversion rules](design/conversion_revision_v2.md), [persona integration guide](science_personas/INTEGRATION_GUIDE.md), and [Phase 1 plan](science_personas/experiment_plan.md).

1. Select 50 distinct source tasks with available inputs and validated runtimes. Conversion alone does not establish runtime readiness. Keep related study IDs grouped in analysis.
2. Freeze the task, inputs, environment, actor, grader, scientific facts and interaction protocol before creating persona arms. Only the top-level persona block changes across arms.
3. Use reviewed or automatically source-validated task cards. The planner hashes both reviewed and automated eligible facts and records the actual runner and simulator policy for each case.
4. Shared execution/design tasks may use the current approach/result review protocol. SciConv uses native clarification; EXP uses its native design task card or an explicit task ID from a JSONL catalog. Do not replace either with the older optional-question workflow.
5. Generate configs and a private plan with the Phase 1 CLI. Verify the plan before and after execution. Generated JSON configs also load in EXP. Use the recorded runner and exact source task ID; the planner does not launch cases.
6. Execute independent cases concurrently, retain every attempt locally, and report native outcomes and interactions separately. Keep evaluator references and private manifests outside actor mounts.

The current [14-case trial](../reports/conversion_v2/README.md) is an integration check, not the proposed 50-task persona experiment. Obsolete standalone scope audits and validation logs are omitted from this integration.

```bash
uv run --locked python scripts/check_repository.py
uv run --locked python -m personasciencebench.science_personas.phase1 design-check --design examples/science_personas/phase1/design.proposed.json
```
