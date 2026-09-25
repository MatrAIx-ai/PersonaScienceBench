# ODE collaboration example

This directory contains the worked task adaptation, six 56-attribute profiles, the unchanged native public input package, a source lock, and controller-only verifier/control tools. Everything newly authored is in English.

Start with [the complete walkthrough](../../docs/collaboration/ODE_WORKED_EXAMPLE.md). For another task, follow [the adaptation playbook](../../docs/collaboration/TASK_ADAPTATION_PLAYBOOK.md).

| File/directory | Purpose |
|---|---|
| `public/` | Original instruction, native public data/checker, separate collaboration addendum |
| `source.lock.json` | Exact native commit and per-file checksums/visibility |
| `task_card.json` | Machine-readable adaptation contract and disclosure description |
| `personas/` | Six complete profiles; the two PI profiles differ only in delegation |
| `persona.schema.json` | Closed 56-attribute JSON Schema |
| `shared_runner_persona.json` | Opt-in science profile for the existing grounded LLM persona renderer |
| `scripted_demo/` | Reproducible protocol fixture; no scientific or model-performance claim |
| `run_live.py` | One real actor using the new session and original native verifier |
| `verifier_controls.py` | Controller-only positive/negative verifier control generation |
| `upstream.LICENSE` | License for the native public task material |

The deterministic controller and the existing grounded LLM researcher are different simulator modes. The worked live path uses the deterministic controller; the shared-runner profile overlay enables the new catalog in the existing LLM renderer without adding the worked disclosure state machine automatically.

Never mount this whole directory or the repository into an evaluated actor. The source lock names private verifier files, and controller code has access to them during preparation. Supply only the intended public files and dedicated output workspace through an isolated runtime.
