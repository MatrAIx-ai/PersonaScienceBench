# BixBench active researcher collaboration

**Current implementation:** [shared approach and result review (`researcher-review-v2`)](collaboration.md). The existing BixBench configuration now selects this protocol. The description and ten-case results below record the earlier v1 pilot; its traces have not been rerun or relabeled.

The researcher initiates the analysis, reads the agent's progress, requests follow-up work, and decides when to stop. Persona styling is disabled in the pilot; actor, researcher, and model judge use `openai/gpt-6-luna` with reasoning effort `none`.

Each question has one persistent OpenHands conversation and scientific workspace. The agent executes commands and yields through `end_researcher_turn`, sharing its findings, uncertainties, and any final answer/artifact candidate. The researcher replies with the next request or a stop decision. The actor cannot independently submit. When the researcher stops, the controller seals the latest complete candidate and passes it to the existing native BixBench open-answer grader. Missing candidates remain `missing_submission`.

The researcher sees the public task, eligible approved facts, and shared handoffs. It never receives evaluator references, reference notebooks, hidden results, or private actor reasoning. It can propose analytical steps and critique reported work; factual grounding of free-form suggestions is a model instruction, not a deterministic guarantee. Its structured decision records the interaction type, evidence, unresolved objectives, and disclosed fact IDs. One formatting-only retry is allowed and logged if the decision is malformed.

The pilot uses the same ten questions as the previous persona-off run, independently rather than grouping questions from one capsule. This isolates the protocol integration from changes to task packaging. It permits at most 12 researcher requests and 60 total actor calls per question. At budget exhaustion, the controller records the reason and seals the latest complete candidate if available; this is distinct from researcher-selected stopping. The previous passive run allowed 20 actor calls, so accuracy differences are descriptive, not a controlled estimate of collaboration's effect.

## Run

```bash
PERSONASCIENCEBENCH_BWRAP="$PWD/external/runtime/bubblewrap/root/usr/bin/bwrap" \
.venv/bin/python -m personasciencebench.cli run \
  --prepared prepared/luna-ten-python --benchmarks bixbench \
  --output runs/bixbench-collaboration-new \
  --actor-python .actor-venv \
  --config configs/luna-bixbench-collaboration-ten.json --parallel 10

.venv/bin/python scripts/render_run_traces.py runs/bixbench-collaboration-new
```

The existing `.env` supplies the API credential. Use a fresh output directory. `TRACE_INDEX.md` links complete readable traces; each begins with the chronological researcher–agent conversation. Raw controller events and API calls retain the full record, including grader calls.

Researcher request counts measure participation. To assess useful involvement, inspect whether follow-ups respond to findings, correct errors, or resolve uncertainty; a higher turn count alone does not establish better collaboration.

## Activation check

Earlier activation and ten-case records are archived locally. See the [current seven-track trial](../../reports/conversion_v2/README.md) for the retained results.
