# IdeaGene: opt-in IG-Arena Question pilot

Status: adapter and offline-tested text-only runner. Full native PES evaluation is
**not verified** by this change. This is integration and protocol validation, not a
formal persona-effect experiment. No conversation is published as empirical evidence.

## Scientific task and provenance

Source: [VisionXLab/IdeasHaveGenomes](https://github.com/VisionXLab/IdeasHaveGenomes),
revision `938fa9edfe54bee9a78359b42810b9c20857e432`, pinned in
`manifests/sources.json`. The upstream README currently says License TBD. Acquire
the source externally; this PR does not redistribute the task corpus or references.
For archive acquisition, native preflight also accepts the exact Git root tree
`61507ee2964f6dd4fb365c5875505939b1cb1641`; this is the tree addressed by the
pinned commit, not a looser per-file version check. Tracked modifications still block.

The adapter enumerates `gene_arena/task/*.json` automatically. The pilot explicitly
selects ten tasks whose upstream records have `verified=true`; it does not expand
the current paper plan or other benchmark defaults. The reviewed allowlist is fixed
in code; smaller reviewed subsets may be used for connectivity checks.
Source trace IDs define study groups; potential cross-trace literature overlap
still needs review before larger dataset splitting.

| Boundary | Export |
| --- | --- |
| Actor | Exact `open_question`, `domain`, `subfield`, public proposal contract and text-only runtime |
| Researcher | Same public brief, empty source fact pack, explicit unknowns, exact selected full identity, actual shared handoffs |
| Evaluator | Pinned original task and literature/lineage metadata, optional native genome database, final proposal |
| Controller | Source revision/hashes, conversion record, persona hash, role configurations, API/event logs, sealed submission |

Source locators are `/open_question`, `/domain`, `/subfield`. No wholesale source row
is exported. Nested papers, edges, genomes, frontier evidence and unexpected answer
fields stay excluded. The empty fact pack is valid under the conversion standard;
we do not remove essential information to manufacture clarification questions.
Hardware, data availability and research budgets remain unknown. General knowledge
is permitted equally with and without persona; suggestions do not become fixed facts.
The upstream `verified` flag is retained as provenance, not an independent scientific audit.

## Interaction and runtime

The runner reuses `ActiveResearcher`, `CollaborationHandoff`, `EpisodeSession`,
`OpenRouterClient` and the `researcher-review-v2` protocol. The researcher makes one
typed decision per request. The actor has exactly one tool, `end_researcher_turn`;
it has no filesystem, shell, retrieval or network tools. This is a text-only design
track, not a fallback that executes scientific code outside the existing sandbox.
Bubblewrap execution policies in other runners are unchanged.

An initial researcher request is followed by plan review, approach approval and
result review. Revisions are optional. Each handoff is recorded with timestamp,
trace sequence and then-disclosed context. A result cannot precede approval.
Only researcher acceptance seals a submission. Budget exhaustion is missing
submission, never a fabricated answer or zero scientific score.

The actor puts the complete proposal in `payload.proposal` as a typed JSON object.
The controller serializes it once into `Submission.answer`; that exact string becomes
native `content`. The contract requires the six fields already consumed by the PES
`idea_genome` parser, plus an evolution rationale, validation plan and known unknowns.
This is a generation-side compatibility check, not a change to the native evaluator:
without it, plausible free-form answers can all hit the evaluator's 40-point format
cap and make the persona comparison uninformative. The controller also enforces a
20,000-character serialized limit. Clarification-only result handoffs retain the
previously shared candidate; the reviewer is shown that retained candidate.

This is explicitly a **collaborative Question generation variant**: extra discussion
and a bounded number of turns differ from native one-shot generation. There is no
added Chinese-language restriction and no claimed leaderboard comparability. The
native scientific question, proposal content reader and PES scoring are preserved.

## Personas and pilot controls

`configs/ideagene/pilot.json` schedules ten upstream-verified tasks with persona off,
candidate 148 and candidate 046, for 30 episodes. The task set spans biology,
chemistry, climate, computer science, energy, mathematics, medicine and physics.
Both profiles belong to the proposed follow-up panel. Selection
precedes IdeaGene outcomes and is not a claim of domain matching or population
representation. The exact identity blocks are read from published profile Markdown
and checked against the frozen cohort manifest SHA-256 values. No identity is
summarized, projected to a task domain or passed to the actor/native judge.

Off keeps the same researcher, general-knowledge permissions and review budget.
One repetition yields 30 episodes. It is a workflow screening pilot, not a
statistical estimate of persona effects. Profiles vary in multiple attributes;
differences cannot be attributed to a single preference. Use more repetitions and
the team's calibration controls for claims of a stable effect. This change does not
merge or depend on unmerged PR #6/#8 switches.

## Acquisition and preparation

Use the repository environment from CONTRIBUTING.md. From its root:

```bash
uv run --locked python -m personasciencebench --source-root external/sources fetch-sources --benchmarks ideagene
uv run --locked python -m personasciencebench --source-root external/sources catalog --benchmarks ideagene
uv run --locked python -m personasciencebench --source-root external/sources prepare --benchmarks ideagene --selection configs/ideagene/selection.json --output data/ideagene-pilot
uv run --locked python -m personasciencebench --source-root external/sources run-ideagene --dry-run --output runs/ideagene-plan-001
```

Preparation and dry-run make no model calls. Outputs are public/controller packages
and a 30-episode manifest with exact question/profile hashes. Conversion or asset
readiness is not proof of runtime or scientific success. Use a new output directory
for every run; existing runs are never overwritten.

## Actual actor/researcher run

Set `OPENROUTER_API_KEY` in the local environment or ignored `.env`. The checked-in
actor/researcher model IDs mirror the team's existing full-profile config. Preflight
must validate availability and tool support; adjust model configuration explicitly
if your provider lacks these IDs. No silent model fallback is used.

```bash
uv run --locked python -m personasciencebench --source-root external/sources run-ideagene --output runs/ideagene-live-001
```

This requests paid model calls. Maximum researcher requests are 12 per episode,
including the initial request; actor handoffs are at most 11. The shared researcher
may make its existing format-repair retry, recorded in API/events. Resource usage,
reported cost (or null when absent), elapsed time, errors and denominator counts
are retained. Native grading is not enabled implicitly. Actor/researcher instances
and histories are recreated for every task, persona and repetition.

## Native PES evaluation

PES uses the source's separate `API_KEY` and its configured API endpoint, not the
actor's OpenRouter credential. Install the pinned upstream requirements into an
evaluator environment. Supply that environment's Python with `--native-python`.
The original three judges are `judge-gpt4o`, `judge-gpt4o-mini`, `judge-gpt4.1-mini`;
their native temperatures, prompts, parsing, caps and aggregation are preserved.
Native defaults include evaluator retries; they are not replaced by best-of-run selection.

```bash
uv run --locked python -m personasciencebench --source-root external/sources run-ideagene --output runs/ideagene-live-scored-001 --evaluate-native --native-python /path/to/evaluator/python
```

Each accepted proposal produces `controller/native_request.json` and a fresh
native directory. Constructing the request does not execute the evaluator.
`--evaluate-native` runs the pinned `gene_arena/run_arena.py pes` on that directory
after sealing; otherwise operators can inspect and execute the recorded argv later.
The native process never receives identity blocks or conversations. Raw upstream
sources and genome reference data are never available to actor tools.

The adapter preserves `pes`, `heredity_score`, `variation_score`, `selection_score`
on their native 0–100 scale, plus the original detailed record and aggregate output.
The upstream `gene_arena/genome_db/paper_gene_cards.json` is optional. When present,
its hash and use are recorded; when absent, the request records
`missing_task_json_fallback` and native PES uses the gene cards embedded in the
pinned task JSON, matching the upstream implementation. Its absence does not block
native execution.
Incomplete judges, missing score files, malformed metrics, process failure and
timeouts remain distinct from a valid zero score. No proxy LLM judge is substituted.
Native `GENE_*` overrides are rejected in this default track rather than silently
changing judge fallback, sampling or reference settings. Missing dependencies or
credentials leave evaluation blocked/error, with no numerical score.

The submission/reference hashes, consumed native code hashes and judge IDs are
saved alongside the request; complete upstream judge records are retained. Actual
native API costs may not be reported by the upstream scorer and are not inferred
from actor usage. Review native records and provider billing before cost comparisons.

## Tests and review status

```bash
uv run --locked python -m pytest tests/test_ideagene.py tests/test_persona.py -q -rs
```

Synthetic tests use hand-written test fixtures only, never paid models. They cover
automatic conversion, nested reference exclusion, exact identity recovery, stage
ordering, private reasoning isolation, candidate retention, immutable submission,
budget exhaustion, source mutation, native export/score parsing and 30-episode
scheduling. They are not scientific or persona-effect results.

Optional source-backed conversion: set `PERSONASCIENCEBENCH_SOURCE_ROOT` to a root
containing the verified IdeaGene checkout. If only exact copies of the smoke task JSONs
are available, set `PERSONASCIENCEBENCH_IDEAGENE_TASK_DIR`; the test verifies their
pinned SHA-256 values before conversion. That narrower test verifies task conversion
only, not native source acquisition or PES execution. Sources remain external.

Before publishing a pilot report, run real episodes and native PES, inspect all 30
traces, verify user knowledge/identity behavior and retain all missing outcomes.
This patch does not change the 200-question paper plan or historical study records.
