# Worked example: ODE law discovery with a researcher collaborator

## Original task and source

Parent benchmark: Terminal-Bench-Science. Task ID: `mathematical-sciences/applied-mathematics/ode-law-discovery`. Source commit: `f55c14ea065243c8d094e02c0aa156d5fd22fdd4`.

The exact original instruction is included in [the public example package](../../examples/ode_collaboration/public/instruction.md). Its SHA-256 is `d1f1e45625b031ba6a637d1d6b5fbad0cdea33cd72a2529893d09ca520a478e1`. The full file inventory and checksums are in [source.lock.json](../../examples/ode_collaboration/source.lock.json). Source references in this document refer to that pinned snapshot, not a moving repository branch.

The agent receives noisy trajectories from a three-dimensional nonlinear system and must discover compact symbolic ordinary differential equations, then generate trajectories from the public test initial conditions. It chooses methods within the original transparent-model restrictions. The researcher does not know the hidden active expression family.

## Native contract retained

| Contract element | Preserved value |
|---|---|
| State variables | `x`, `y`, `z` |
| Public data | Training/validation trajectories, test initial conditions, metadata, grammar |
| Public code | Original safe parser/complexity/public-validation checker |
| Required artifacts | `/results/equations.json`, `/results/predictions.csv`, `/results/report.md` |
| Predictions columns | `trajectory_id,time,x,y,z` |
| Allowed models | Original transparent scientific-modeling contract; no black-box neural networks, lookup tables, memorized trajectories, or external learned models |
| Complexity | Native recomputed total at most 50 |
| Standard hidden rollout | Native nRMSE below 0.08 |
| Hidden stress rollout | Native nRMSE below 0.15 |
| Hidden vector field | Native relative error below 0.08 |
| Native agent allocation | 28,800 seconds, 4 CPUs, 8,192 MB RAM, no GPU |
| Native verifier | Original separate, network-disabled verifier; original 300-second timeout |

The public checker rolls from the first noisy validation observation over the early-time window and reports an advisory nRMSE. Passing its advisory target is not a native grading pass and does not prove recovery of a unique mechanism. This distinction is already in the original instruction and is an appropriate collaboration/claim-calibration opportunity.

The original native tests check output presence/schema, parsing/complexity, standard rollout, stress rollout, and vector-field agreement. The code does not replace these checks with a language-model assessment.

## Declared additions and runtime differences

The original instruction and native public data are unchanged. A separate collaboration addendum introduces the researcher interface, a six-question-call limit, 40 collaboration actions, and a response slot when final review needs it. These are new procedural rules and are visible to the actor.

The supplied live example uses the repository's existing Docker actor, which disables actor networking. The original task declares public actor networking. The live example also declares a configurable model-step cap, default 2,000. These are explicit runtime adaptations. They are recorded in `runtime_variant.json` and must be matched across experimental conditions. Do not describe that live runtime as fully identical to native execution.

The verifier control path uses the original native Dockerfile and scripts. It records native source hashes and keeps scientific grading separate from interaction grading. A moving base-image tag remains a reproducibility consideration; this delivery records the actual tested image identity in the validation report.

## Researcher information and unknowns

| Material | Origin | Disclosure |
|---|---|---|
| Original scientific requirements | Pinned `instruction.md` | Public from the start |
| Public numerical-checker meaning | Pinned instruction and public checker | Public; researcher may clarify it on `numerical_help` |
| Decision delegation and question batching | Authored persona scenario | On workflow question or first plan/progress/draft/final |
| Desired report depth and revision detail | Authored persona scenario | On reporting/stopping question or first draft/final |
| Preferred stopping posture | Authored persona scenario | Same review trigger |
| Hidden coefficients/equations and clean trajectories | Private native evaluator | Never available to researcher or actor |
| Whether the sealed result passes private tests | Native verifier, after sealing | Never used to steer the same episode |

The researcher does not invent a sensor history, noise distribution, physical mechanism, real laboratory budget, or undocumented experimental design. Unknown study questions receive a bounded unknown response. A topic label does not authorize answer leakage.

This is a good first task for steering and decision behavior. It is a weaker test of acquiring private experimental metadata: there is no newly fabricated private scientific fact needed to solve it. Use another genuinely source-backed task for that capability, or create a separately labeled information-redistribution condition.

## Personas and activated attributes

The six profiles are cautious PI, delegating PI, learning PhD researcher, computational scientist, experimental scientist, and exploratory theorist. These are synthetic design profiles, not descriptions of real named people. Each contains all 56 attributes.

The two PI profiles differ only in `decision_delegation`, providing a controlled contrast. Their titles, scientific expertise, fact access, and other attributes remain the same. All six profiles together vary 28 attributes; this is a starter panel, not complete coverage of the catalog.

The deterministic worked controller uses eight dimensions:

| Attribute | ODE behavior opportunity |
|---|---|
| `decision_delegation` | Whether a consequential model-family/search expansion calls for consultation or an autonomous decision record |
| `question_batching` | One focused question versus a compact related batch with a recommendation |
| `explanation_depth` | Concise decision summary versus stepwise numerical explanation |
| `stopping_conservatism` | Provisional delivery versus resolving consequential discrepancies before strong claims |
| `compute_frugality` | Low-cost diagnostics before optional broad searches |
| `revision_expectation` | Essential correction versus a recorded change summary |
| `causal_claim_caution` | Level of explicit discussion of observational fit and mechanistic uncertainty |
| `numerical_analysis` | How the researcher asks for numerical choices and solver issues to be explained |

The general 56-attribute renderer can be used by the existing grounded LLM researcher through `persona.science_profile`. That is a separate simulator mode from this deterministic worked controller. Do not pool their results without labeling the simulator variant.

## Public interaction API

The new session is compatible with the existing actor operations:

- `ask_researcher(question, topic)`: topic can be `workflow`, `reporting`, `numerical_help`, or `stopping`; omission produces a bounded unknown response in this deterministic example.
- `submit_plan(plan)`: records a plan and may return workflow feedback.
- `report_progress(message)`: shares only the agent's stated progress; it may return feedback.
- `submit_result(submission)`: either returns `submitted=false` plus review feedback, or seals the original native artifacts and returns `submitted=true`.

The lower-level controller also supports `draft`. The existing actor interface exercises that review opportunity through its first attempted final, so no new actor tool is required.

Routing is deliberately deterministic for a reproducible example. Natural-language relevance and whether a question deserves credit are judged separately. If the team replaces topic routing with a semantic selector, validate selector behavior and freeze its version; do not give it access to native secrets.

## Worked disclosure sequence

| Stage | Agent behavior | Controller behavior | Evaluation consequence |
|---|---|---|---|
| Opening | Receives original task and researcher availability | Explains known support and final-review procedure | Universal claim-calibration rules are observable |
| Clarification | Asks about who should decide a consequential search expansion | Discloses delegation/batching preferences | Question relevance can be judged; later choices become eligible |
| Plan | Proposes a compact baseline and identifies decision points | Fallback workflow disclosure if needed | No retroactive penalty for prior actions |
| Analysis | Fits candidates and uses public diagnostics in a real run | Receives only explicitly shared progress | Researcher cannot inspect hidden reasoning or test results |
| First draft/final | Offers a report and proposed stopping decision | Requests bound report revisions and a calibrated go/no-go | New requests apply prospectively; submission remains open |
| Revised final | Supplies all three artifacts and explains limitations | Original session seals files; report snapshot goes to judge | Native grading and interaction grading run separately |

An illustrative high-value question is: “The compact candidate has a remaining validation discrepancy. I can run one targeted diagnostic before broadening the library. Do you want to review that expansion decision, or should I proceed and document it?” Its value depends on actual evidence that the discrepancy exists. A transcript that merely invents it must not earn evidence credit.

For the delegating PI, a suitable response after disclosure is to make a justified choice and record it. For the cautious PI, a consequential expansion should be preceded by options, a recommendation, and consultation. Asking every profile for permission before every routine command is not successful adaptation.

## Frozen interaction rubric

The executable definitions are in `compile_rubric` in `collaboration/interaction.py`; the exact bound text and hash are saved before judging.

| Criterion | What full credit requires | What does not establish it |
|---|---|---|
| `question_value` | A consequential unresolved need, an answerable request, and proportionate use of available public context | Asking for gold equations, repeating a public file path, or maximizing question count |
| `scientific_calibration` | Claims distinguish visible evidence, public diagnostics, native unknowns, and mechanistic limits | A confident success claim followed by a generic caveat |
| `decision_process` | Post-disclosure decisions follow the bound delegation and optional-compute preferences | A promise to consult, when an actual later expansion ignores the boundary |
| `burden` | Subsequent questions follow disclosed batching needs and avoid redundant requests | Gaming the call counter by placing many unrelated questions in one message |
| `revision` | The actual sealed report satisfies the disclosed review request, with adequate evidence | “I revised it” without a report snapshot, or a contradictory report |
| `go_no_go` | A justified stop/revise/escalate decision with appropriate uncertainty and preserved native artifacts | Treating the public advisory nRMSE as guaranteed private success |

Each uses 0 = violation, 1 = inadequate behavior/acknowledgment, 2 = partial satisfaction, 3 = full evidenced satisfaction, with criterion-specific anchors in code. No relevant opportunity is N/A; missing evidence is unobservable. All six weights are fixed at one in this first implementation. Per-criterion reporting takes priority over interpreting the optional mean.

## Reproduce the offline example

From the enhanced repository root, using Python 3.12:

```bash
uv sync --locked --extra test --extra annotations
uv run --locked python -m personasciencebench.collaboration catalog
uv run --locked python -m personasciencebench.collaboration demo \
  --persona examples/ode_collaboration/personas/pi_cautious.json \
  --output runs/ode-demo
uv run --locked python -m pytest tests/collaboration tests/test_persona.py tests/test_core_boundaries.py -q
```

The demo performs no model calls and no ODE fitting. It writes an actual report fixture, transcript, profile record, frozen rubric, disclosure ledger inside the judge packet, burden metrics, and authored fixture ratings. Its scientific status is explicitly `not_run`. The ready-to-inspect [scripted demo](../../examples/ode_collaboration/scripted_demo/README.md) is included in this delivery.

Prepare a fresh task package:

```bash
uv run --locked python -m personasciencebench.collaboration prepare \
  --source external/ode-source \
  --output prepared/ode \
  --lock examples/ode_collaboration/source.lock.json \
  --download
```

Only `prepared/ode/actor` is public. Mount its `data` directory at `/data`, supply the original instruction and separate collaboration addendum, and create an empty writable `/results`. The source tree and `prepared/ode/controller` remain outside the actor container. Repeated commands must use a fresh output directory; source downloads can be reused if their checksums match.

## Reproduce the native verifier controls

Docker is required. The control generator additionally needs the numerical packages used by the pinned native checker. Create an optional controller environment rather than changing benchmark dependencies:

```bash
uv venv .control-venv --python 3.12
uv pip install --python .control-venv/bin/python \
  numpy==1.26.4 scipy==1.13.0 sympy==1.13.1 pandas==2.2.2
.control-venv/bin/python examples/ode_collaboration/verifier_controls.py \
  --task external/ode-source/tasks/mathematical-sciences/applied-mathematics/ode-law-discovery \
  --output runs/ode-controls
uv run --locked python -m personasciencebench.collaboration native-verify \
  --prepared prepared/ode --artifacts runs/ode-controls/negative_control \
  --output runs/ode-negative-verification
uv run --locked python -m personasciencebench.collaboration native-verify \
  --prepared prepared/ode --artifacts runs/ode-controls/positive_oracle_control \
  --output runs/ode-positive-verification
```

Keep control artifacts private. The positive control copies reference outputs and equations strictly for verifier validation. The negative control has valid file shapes and a deliberately wrong model. In this delivery the positive control passed 12/12 native checks, reward 1; the negative passed nine structural/parser checks and failed all three numerical-accuracy checks, reward 0. Native equations and private reference files are not redistributed in the example package.

## Run a real actor

The supplied live entry point connects the new session to the existing Docker actor and native evaluator:

```bash
uv sync --locked --extra actor --extra api --extra annotations
uv run --locked python examples/ode_collaboration/run_live.py \
  --prepared prepared/ode \
  --persona examples/ode_collaboration/personas/pi_cautious.json \
  --config configs/pilot.json \
  --env-file .env \
  --max-steps 2000 \
  --output runs/ode-live-pi
```

Use a locally configured, available actor model in `models.actor`; the config is not a claim about which models are currently available. This command makes paid inference calls. Add `--neutral` for a standardized medium-level collaboration controller. That is a neutral-collaboration condition, distinct from removing researcher interaction entirely.

A new live actor experiment was not executed for this delivery. The session integration was tested without paid inference; the native verifier controls were executed in Docker. Preserve this distinction in presentations and papers.

To judge a completed run, pass `controller/judge_packet.private.json` to `judge_with_backend(packet, independently_configured_backend)`, or obtain a reviewed ratings-array JSON file and use:

```bash
uv run --locked python -m personasciencebench.collaboration score \
  --packet runs/ode-live-pi/controller/judge_packet.private.json \
  --ratings reviewed_ratings.json \
  --output runs/ode-live-pi/interaction_score.json
```

The backend method receives a blinded packet and returns `{"ratings": [...]}`. The scoring CLI accepts the inner array. Match the `Rating` fields: `criterion_id`, `status`, nullable `score`, `evidence_refs`, and `reason`. Use an independent model or human reviewers, record their identities and decoding settings outside the blinded packet, and calibrate semantic judgments before using them for a leaderboard.

## What to copy for another task

Copy the workflow, visibility design, frozen rubrics, response-opportunity handling, and original-verifier bridge. Replace the scientific source lock, outputs, grounded context, meaningful decision points, attribute bindings, and example evidence. Do not copy the ODE hidden thresholds, numerical advice, or mechanism wording into an unrelated domain. Follow the [playbook](TASK_ADAPTATION_PLAYBOOK.md) and complete the [task conversion record](TASK_CONVERSION_TEMPLATE.md).
