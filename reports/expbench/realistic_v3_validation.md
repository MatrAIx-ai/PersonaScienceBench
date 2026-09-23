# Realistic benchmark implementation and validation

Implemented as a separate v3 mode, now updated to v3.1 reference-only evaluation. See the [usage documentation](../../docs/expbench/realistic-benchmark.md).

## Implemented

- Researcher queries select one topic; only its approved fact is available for a new answer. Published answers cannot add generated facts. Conversation memory is retained.
- Actor tools support repository inspection and isolated CPU commands. Plans are free-form, without required variable groups.
- Initial and final plans are immutable separate checkpoints. Workflow continuation retains the same OpenHands conversation.
- Released judge system/user roles, JSON-object mode and three-attempt parsing are implemented, including for future original-control and monitor replays. Historical scores remain unchanged.
- Reference coverage is sampled three times by default. The added scientific-quality rubric was removed in v3.1 at the user's request. Monitor decisions, gated coverage and execution status are separately recorded.
- Runtime failures and missing evaluations remain visible in summary counts. A successful reproduction command does not set scientific success.
- A matched no-simulator mode supplies original question/method/instructions with the same new actor tools and judging.

## Repositories prepared

Each public snapshot uses a recorded commit dated at or before 2025-05-30; these are not claimed to be the paper's exact run revisions. Missing mask targets would fail preparation. All required targets were found.

| Task | Commit prefix | Staged files | Masked files |
| --- | --- | ---: | ---: |
| JaxMARL | `dff30486a7cd` | 179 | 2 |
| QuaRot | `5008669b08c1` | 46 | 1 |
| CycleNet | `af6e06ccf838` | 90 | 5 |
| MogaNet | `386b548c5f0b` | 269 | 0 |
| SineNet | `8fa3b18f8e88` | 605 | 2 |

MogaNet's selected task is type 3 and has no source mask in the released annotation; zero is intentional. Staging omits history, hidden files, symlinks, README files, documents/data and results directories. This stricter staging is an adaptation. Every retained file is hashed and checked before a live run.

[Prepared workspace mapping](../../data/realistic_pilot/staged/workspaces.json) and [source revisions](../../data/realistic_pilot/source_repositories.json).

## Verification

**47 tests passed**, including regression tests for the earlier pilot and tests of researcher boundaries, conversation continuity, immutable checkpoints, missing-evaluation accounting and original judge request roles/retries. The real Bubblewrap test verifies that a private host file and API-key environment variable cannot be accessed, the network namespace has only loopback, public workspace files are readable, and a timed-out command is stopped. There is one existing harmless Pydantic `ReadOnly` warning.

The [five-task smoke run](../../runs/expbench/realistic-v3-five-task-smoke/summary.json) used real OpenHands orchestration, actual masked repositories and real isolated CPU execution, with **scripted model responses**. It completed all five tasks with six actor calls and one researcher query each. It saved ten plan checkpoints, thirty pairs of coverage/quality sample fixtures, ten monitor fixtures and five successful command replays.

The executed checks were trivial arithmetic smoke tests. They do not constitute the scientific experiments. Summary benchmark scores remain null, `scientific_success` remains null, and the paid API cost was **$0**.

An earlier smoke attempt was interrupted because three Python processes stalled reading the same bytecode file on the shared filesystem. Using a local `PYTHONPYCACHEPREFIX` resolved the validation stall; the interrupted attempt is marked separately in its run directory. No inference was made in that attempt.

## Live-run status

The five-task live CPU design pilot is complete; see the [live report, metric definitions and traces](realistic_v3_live_20260922.md). It used o3-mini for the actor and judge and Claude Sonnet 5 for the researcher, with three grading repeats and no dollar caps. CycleNet and SineNet exposed a valid `/workspace` path being rejected by the repository-inspection tool. The alias was fixed, two focused regression checks passed, and both affected tasks were rerun. Original attempts remain preserved; the live report explicitly identifies the replacements.

No GPU training or full scientific experiment was performed. Task-specific ML dependencies, datasets and model weights are not preinstalled or mounted. Full experiment execution requires those assets and a GPU allocation when appropriate. The GPU visibility check is implemented but has not been exercised on an allocated GPU in this version.

With credentials available, another live design run can use the following command with a new output directory:

```bash
PYTHONPYCACHEPREFIX=/tmp/expbench-validation-pycache .venv/bin/python -m expbench.realistic run \
  --mode live --env-file .env \
  --workspace-map data/realistic_pilot/staged/workspaces.json \
  --output runs/realistic-v3-live
```

Defaults remain 20 actor steps, six questions, and no dollar caps. Add `--input-mode original` for the matched no-simulator control. Full workflow execution is explicitly enabled with `--continue-workflow --validate-execution` after provisioning its runtime assets.
