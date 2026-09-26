# PersonaScienceBench

**Scientific agents working with simulated researchers.**

PersonaScienceBench studies how researcher expertise and communication affect an AI agent’s scientific work. The actor inspects inputs, runs tools, consults a simulator, and submits its work. The simulator uses source-grounded context, with optional persona instructions. Each benchmark retains its own evaluation contract.

[Conversion rules](docs/design/conversion_revision_v2.md) · [Personas](docs/personas.md) · [Setup](docs/reproducibility.md) · [Experiment status](reports/persona_action_case_study/README.md) · [Conversion history](reports/conversion_v2/README.md)

## Benchmarks and conversion

Five retained benchmark tracks provide **2,108 converted cases from 2,132 source cases**. Conversion is automated; invalid cases are recorded as exclusions. Conversion and asset readiness do not establish that every runtime works.

| Benchmark | Source | Converted | Main domains | Evaluation |
|---|---:|---:|---|---|
| DiscoveryBench | 264 | 264 | Biology, humanities, sociology, economics, engineering, meta science | Native discovery scoring |
| BixBench | 205 | 205 | Computational biology | Native open-answer grading |
| EXP-Bench | 461 | 440 | Machine learning research | Design coverage and integrity gate; design-only |
| ASI-Bench | 60 | 60 | Scientific computing across disciplines | Native local gates and weighted scores |
| SciConvBench | 1,142 | 1,139 | Fluids, PDEs, materials and solid mechanics | Native clarification and specification metrics |

See [asset readiness and exclusions](reports/conversion_v2/conversion_summary.md) before scheduling a larger batch. In particular, 60 BixBench cases have unresolved input-file roles, and only three ASI instances currently have all required local assets.

ScienceAgentBench and Terminal-Bench-Science were converted and piloted, then
discarded from the active benchmark set. ScienceAgentBench required a multi-GB
verified archive and duplicated evaluator workspaces in each run. Terminal-Bench-
Science required large source assets, Docker images, and long-lived containers.
Their adapters remain as historical conversion records, but current persona
experiments do not schedule them and their local assets and traces are not kept.

### Conversion checklist

The [original candidate list](docs/design/parent_benchmark_candidates.md) remains available. A check indicates an implemented conversion and live trial, not runtime validation of every case.

- [x] BixBench
- [x] DiscoveryBench
- [x] ScienceAgentBench — converted and piloted; discarded as too heavy
- [x] Terminal-Bench-Science — converted and piloted; discarded as too heavy
- [x] EXP-Bench — added later; design-only
- [x] ASI-Bench — added later
- [x] SciConvBench — added later
- [ ] BixBench3
- [ ] sc-HeurekaBench
- [ ] AstaBench: E2E-Bench / E2E-Bench-Hard
- [ ] PaperBench
- [ ] MLRC-Bench
- [ ] SciAgentArena

## How conversion works

The rules below describe the existing implementation. Persona injection and the simulator knowledge policy are under redesign.

1. Preserve the scientific objective, required inputs, outputs and native scoring contract; label every adaptation.
2. Separate public task information, source-attributed simulator context and evaluator-private references. Never infer missing study facts.
3. Keep persona separate from knowledge: styling cannot alter task requirements or the fact pool.
4. Record preparation failures, unresolved assets and runtime limits explicitly.
5. Save actor–simulator interactions, submissions, evaluation results and recovery attempts locally.

Execution and design tracks use approach and result reviews; additional questions are optional. SciConvBench keeps its native clarification dialogue. BixBench’s automatically extracted schema facts are also observable from public inputs. ASI uses B3 tasks with optional B2 methodological guidance, an explicit adaptation of autonomous B3.

The [per-benchmark conversion document](docs/design/conversion_revision_v2.md) specifies extraction, access boundaries, scoring and commands. The [conversion standard](docs/benchmark_standards.md) defines acceptance criteria.

## Researcher personas

The merged [science-persona profiles](docs/science_personas/README.md) add an opt-in 56-attribute schema and deterministic renderer. The [Phase 1 planner](docs/science_personas/experiment_plan.md) creates matched persona arms for the five retained tracks; the proposed 50-task experiment has not been run. Existing profiles remain supported. The [action-persona case study](reports/persona_action_case_study/README.md) has been retired pending a redesign using broader original profiles.

Persona is injected into the **simulator's private system prompt**. The actor
experiences it through researcher replies; the profile is not added to actor or
judge prompts. Approved knowledge stays fixed across conditions.

An example configuration uses a **computer-science novice** profile, with novice
domain knowledge, statistics, and coding. Computer science remains the configured
domain for every task; other persona fields use neutral defaults.

```json
{
  "persona": {
    "enabled": true,
    "id": "computer-science-novice",
    "version": "1",
    "expertise": {
      "domain": "computer science",
      "domain_level": "novice",
      "statistics": "novice",
      "coding": "novice"
    }
  }
}
```

For the control condition, set `"persona": {"enabled": false}`. **The simulator
stays available**, with the same approved facts and no persona instructions.
Omitting `persona` in the shared runner instead selects an enabled neutral profile.

<details>
<summary>Schema and injection behavior</summary>

| Field group | Controls |
| --- | --- |
| `enabled`, `id`, `version` | Activation and profile identity |
| `role` | Title and seniority |
| `expertise` | Domain; independent domain, statistics, and coding levels |
| `research_style` | Research approach and method preference |
| `evidence` | Evidence standard and risk tolerance |
| `communication` | Verbosity, technical level, and tone |
| `workflow` | Speed/thoroughness and compute preference |
| `interaction` | Initiative within replies and feedback style |

Shared adapters resolve overrides in order: base profile → router defaults →
exact domain → full episode ID. In grounded mode, styled replies undergo a
model-based grounding check; rejected prose falls back to approved fact text or
an unknown response.

EXP-Bench accepts the same fixed profile through TOML, without the shared router.
It publishes approved fact text verbatim, so persona can influence fact selection
and relevance but cannot produce freely styled replies. Low expertise never
removes approved facts or permits invented study information.

</details>

See the [persona guide](docs/personas.md) for allowed values, routing, prompt
rendering, and audit records. Complete experiment configs are available for the
[shared runners](configs/conversion-v2-two.json) and
[EXP-Bench](configs/expbench/conversion-v2-two.toml).

## Get started

Use Python 3.12 and uv. Python execution requires Linux and Bubblewrap. Place credentials in the ignored `.env` file.

```bash
uv sync --locked --extra api --extra annotations --extra actor --extra conversion --extra scientific-evaluation
.venv/bin/python -m personasciencebench --help
```

Follow the [setup guide](docs/reproducibility.md), then the [conversion and runtime commands](docs/design/conversion_revision_v2.md#commands). Source revisions and checksums are pinned in `manifests/`. Install ASI from the pinned local source as described in the conversion guide. The setup guide retains historical instructions for the two discarded tracks.

Run independent cases concurrently and use a fresh output directory for every attempt. Raw model/tool records and readable conversations live under ignored `runs/`; published reports contain summary outcomes and local record locators.

## Experiment status

The replacement full-persona experiment has completed locally in
[runs/full-persona-v2-two-20260926](runs/full-persona-v2-two-20260926): 30 personas
plus a fresh persona-off baseline, two fixed questions per retained benchmark
(**310 episodes**). All model roles use GPT-6 Luna with reasoning effort `none`.
The batch began with eight episode slots and three Python workers; Python concurrency later increased to six.
Full persona text is injected into the simulator system prompt only. Both arms
can use general knowledge; native scoring references remain private. Exact
configs, API traces, readable episode traces, and completion records are retained.


The previous action-rule persona experiment has been withdrawn. Its injection
used a narrow subset of the original profiles, so its results do not answer the
intended full-persona research question. Raw runs, score tables, rankings, and
generated displays have been removed from the current worktree.

Original persona data and benchmark inputs are retained. We are redesigning the
persona injection and simulator interaction; preserving the old approved-facts
boundary is not a requirement. The replacement runtime now supports full-profile system injection and general
knowledge in the simulator. All 310 episodes have finished; the final tables distinguish scored outcomes, missing submissions, and errors.

The original 300 profiles have been rescreened: **180 are eligible**, including
the previous 131 and 49 additional profiles. The three static rules require at
least four concrete behavioral attributes, three directional preferences or
habits, and evidence across two behavioral areas. Communication, interaction,
decisions, workflow, and tool collaboration count; there is no domain filter
or model-score selection. Eligibility does not guarantee a behavioral effect.

Inspect the local [pool and all 300 decisions](data/persona_case_study/full_profile_selection_v2/README.md),
generated by `scripts/reselect_persona_pool.py`. The earlier 30-profile sample
from the old pool is superseded. The [replacement 30 and full prompts](data/persona_case_study/full_persona_v2/README.md)
are now ready: 8 synthetic, 8 Wikipedia-derived, 8 Stack Overflow, 4 survey,
1 PRISM, and 1 Amazon profile. Selection balances available sources and greedily
covers different directional behavioral preferences across the five areas;
it uses no model scores. This is a diversity-oriented sample, not a population
estimate. `scripts/build_full_persona_cohort.py` records the selection method,
coverage, original profiles, exact prompts, and field audits.
The planned injection uses the broader profile with the pinned MatrAIx renderer,
without domain or knowledge-boundary restrictions. Selection evidence does not
limit which persona attributes are injected. These artifacts are local and
ignored by Git; the updated runners now consume these prompts.

[Retirement record](reports/persona_action_case_study/README.md)

<!-- FULL_PERSONA_RESULTS_START -->

## Current persona results

Final results: **310/310 episodes finished**. [Benchmark results, all 30 profiles, and interaction traces](reports/full_persona_v2/README.md).

Top deviations below use the same **8 completed questions** for every persona; questions with infrastructure or evaluator errors are excluded for every persona. Differences are normalized score percentage points.

**Shared baseline: 26.01%.** All personas are compared on the same 8 questions. Sorted by absolute score change; positive means higher performance. Profile links show the exact injected identity.

| Rank | Persona | Score | Change vs off | Traces |
|---:|---|---:|---:|---|
| 1 | [046](reports/full_persona_v2/profiles/candidate_046.md) | 4.54% | **-21.47 pp** | [Read](reports/full_persona_v2/traces/candidate_046.md) |
| 2 | [003](reports/full_persona_v2/profiles/candidate_003.md) | 6.14% | **-19.87 pp** | [Read](reports/full_persona_v2/traces/candidate_003.md) |
| 3 | [004](reports/full_persona_v2/profiles/candidate_004.md) | 9.33% | **-16.68 pp** | [Read](reports/full_persona_v2/traces/candidate_004.md) |
| 4 | [089](reports/full_persona_v2/profiles/candidate_089.md) | 9.79% | **-16.22 pp** | [Read](reports/full_persona_v2/traces/candidate_089.md) |
| 5 | [001](reports/full_persona_v2/profiles/candidate_001.md) | 9.91% | **-16.10 pp** | [Read](reports/full_persona_v2/traces/candidate_001.md) |
| 6 | [127](reports/full_persona_v2/profiles/candidate_127.md) | 10.51% | **-15.50 pp** | [Read](reports/full_persona_v2/traces/candidate_127.md) |
| 7 | [262](reports/full_persona_v2/profiles/candidate_262.md) | 11.33% | **-14.68 pp** | [Read](reports/full_persona_v2/traces/candidate_262.md) |
| 8 | [224](reports/full_persona_v2/profiles/candidate_224.md) | 12.20% | **-13.81 pp** | [Read](reports/full_persona_v2/traces/candidate_224.md) |
| 9 | [148](reports/full_persona_v2/profiles/candidate_148.md) | 39.37% | **+13.36 pp** | [Read](reports/full_persona_v2/traces/candidate_148.md) |
| 10 | [026](reports/full_persona_v2/profiles/candidate_026.md) | 12.66% | **-13.35 pp** | [Read](reports/full_persona_v2/traces/candidate_026.md) |

**Behavior on the same questions**

Each cell shows **persona on / baseline**. Rows follow the performance ranking.

| Persona | Turns per question | Words per simulator reply | Revisions per question¹ |
|---|---:|---:|---:|
| [046](reports/full_persona_v2/profiles/candidate_046.md) | 2.38 / 3.38 | 70.76 / 65.99 | 0.17 / 0.33 |
| [003](reports/full_persona_v2/profiles/candidate_003.md) | 3.88 / 3.38 | 66.73 / 65.99 | 0.00 / 0.33 |
| [004](reports/full_persona_v2/profiles/candidate_004.md) | 3.88 / 3.38 | 69.05 / 65.99 | 0.00 / 0.33 |
| [089](reports/full_persona_v2/profiles/candidate_089.md) | 4.25 / 3.38 | 69.53 / 65.99 | 0.00 / 0.33 |
| [001](reports/full_persona_v2/profiles/candidate_001.md) | 4.25 / 3.38 | 70.60 / 65.99 | 0.00 / 0.33 |
| [127](reports/full_persona_v2/profiles/candidate_127.md) | 4.50 / 3.38 | 70.49 / 65.99 | 0.50 / 0.33 |
| [262](reports/full_persona_v2/profiles/candidate_262.md) | 2.25 / 3.38 | 68.95 / 65.99 | 0.00 / 0.33 |
| [224](reports/full_persona_v2/profiles/candidate_224.md) | 4.38 / 3.38 | 65.12 / 65.99 | 0.00 / 0.33 |
| [148](reports/full_persona_v2/profiles/candidate_148.md) | 3.88 / 3.38 | 72.61 / 65.99 | 0.00 / 0.33 |
| [026](reports/full_persona_v2/profiles/candidate_026.md) | 3.50 / 3.38 | 74.09 / 65.99 | 0.33 / 0.33 |

Turns exclude tool calls. Reply lengths exclude initial requests and private evidence. ¹ Revisions cover result-review benchmarks only; SciConv has no such stage. Trace indexes list all ten scheduled questions, while the tables use only the shared completed questions.


<!-- FULL_PERSONA_RESULTS_END -->

## Repository guide

| Path | Contents |
|---|---|
| `src/personasciencebench/` | Six adapters, simulator, runtimes and CLI |
| `src/expbench/` | EXP-Bench design pipeline |
| `configs/`, `manifests/` | Experiment settings and pinned sources |
| `docs/` | Conversion standards, setup and research plans |
| `reports/conversion_v2/` | Current result summaries and catalog readiness |
| `reports/persona_action_case_study/` | Retirement record and redesign status |
| `external/`, `data/`, `prepared/`, `runs/` | Ignored local sources, assets, task packages and raw records |

Old raw runs and persona comparison outputs were deleted during cleanup. Previously committed summaries remain in Git history. Implementation code is MIT licensed; upstream data retain their own licenses. See [CONTRIBUTING.md](CONTRIBUTING.md).
