# PersonaScienceBench

**Scientific agents working with simulated researchers.**

PersonaScienceBench studies how researcher expertise and communication affect an AI agent’s scientific work. The actor inspects inputs, runs tools, consults a simulator, and submits its work. The simulator uses source-grounded context, with optional persona instructions. Each benchmark retains its own evaluation contract.

[Conversion rules](docs/design/conversion_revision_v2.md) · [Personas](docs/personas.md) · [Setup](docs/reproducibility.md) · [Results](reports/conversion_v2/README.md)

## Benchmarks and conversion

Seven benchmark tracks provide **2,280 converted cases from 2,304 source cases**. Conversion is automated; invalid cases are recorded as exclusions. Conversion and asset readiness do not establish that every runtime works.

| Benchmark | Source | Converted | Main domains | Evaluation |
|---|---:|---:|---|---|
| DiscoveryBench | 264 | 264 | Biology, humanities, sociology, economics, engineering, meta science | Native discovery scoring |
| BixBench | 205 | 205 | Computational biology | Native open-answer grading |
| ScienceAgentBench | 102 | 102 | Chemistry, GIS, bioinformatics, psychology | Program replay and native verifier |
| Terminal-Bench-Science | 70 | 70 | Earth, engineering, life, mathematical and physical sciences | Native Docker verifier |
| EXP-Bench | 461 | 440 | Machine learning research | Design coverage and integrity gate; design-only |
| ASI-Bench | 60 | 60 | Scientific computing across disciplines | Native local gates and weighted scores |
| SciConvBench | 1,142 | 1,139 | Fluids, PDEs, materials and solid mechanics | Native clarification and specification metrics |

See [asset readiness and exclusions](reports/conversion_v2/conversion_summary.md) before scheduling a larger batch. In particular, 60 BixBench cases have unresolved input-file roles, and only three ASI instances currently have all required local assets.

### Conversion checklist

The [original candidate list](docs/design/parent_benchmark_candidates.md) remains available. A check indicates an implemented conversion and live trial, not runtime validation of every case.

- [x] BixBench
- [x] DiscoveryBench
- [x] ScienceAgentBench
- [x] Terminal-Bench-Science
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

1. Preserve the scientific objective, required inputs, outputs and native scoring contract; label every adaptation.
2. Separate public task information, source-attributed simulator context and evaluator-private references. Never infer missing study facts.
3. Keep persona separate from knowledge: styling cannot alter task requirements or the fact pool.
4. Record preparation failures, unresolved assets and runtime limits explicitly.
5. Save actor–simulator interactions, submissions, evaluation results and recovery attempts locally.

Execution and design tracks use approach and result reviews; additional questions are optional. SciConvBench keeps its native clarification dialogue. BixBench’s automatically extracted schema facts are also observable from public inputs. ASI uses B3 tasks with optional B2 methodological guidance, an explicit adaptation of autonomous B3.

The [per-benchmark conversion document](docs/design/conversion_revision_v2.md) specifies extraction, access boundaries, scoring and commands. The [conversion standard](docs/benchmark_standards.md) defines acceptance criteria.

## Researcher personas

The merged [science-persona profiles](docs/science_personas/README.md) add an opt-in 56-attribute schema and deterministic renderer. The [Phase 1 planner](docs/science_personas/experiment_plan.md) creates matched persona arms for the current seven tracks; the proposed 50-task experiment has not been run. Existing profiles remain supported.

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

Use Python 3.12 and uv. Python execution requires Linux and Bubblewrap; Terminal tasks require Docker. Place credentials in the ignored `.env` file.

```bash
uv sync --locked --extra api --extra annotations --extra actor --extra conversion --extra scientific-evaluation
.venv/bin/python -m personasciencebench --help
```

Follow the [setup guide](docs/reproducibility.md), then the [conversion and runtime commands](docs/design/conversion_revision_v2.md#commands). Source revisions and checksums are pinned in `manifests/`. ScienceAgentBench requires the verified archive. Install ASI from the pinned local source as described in the conversion guide.

Run independent cases concurrently and use a fresh output directory for every attempt. Raw model/tool records and readable conversations live under ignored `runs/`; published reports contain summary outcomes and local record locators.

## Current results

**September 25, 2026: two cases per benchmark, 14 total, persona off, GPT-6 Luna for actor, simulator and LLM judges.** Independent cases ran concurrently. Thirteen cases received scores; one ScienceAgentBench case had no sealed submission. Native programmatic grading remains programmatic.

| Benchmark | Case outcomes | Average back-and-forth |
|---|---|---:|
| DiscoveryBench | 0, 0 /1 | 2.0 |
| BixBench | 1, 1 /1 | 2.5 |
| ScienceAgentBench | 1 success; 1 missing submission | 2.5 |
| Terminal-Bench-Science | 0, 1 /1 | 2.5 |
| EXP-Bench | 79.33, 30.00 coverage /100 | 2.5 |
| ASI-Bench | 14.62, 0.00 /100 | 3.0 |
| SciConvBench | Both FRR=1 and CGRR=1 | 2.5 |

A back-and-forth is an actor handoff and simulator response, including required reviews; SciConv counts native clarification Q&A. The overall average is **2.5 across 14 cases**. These small integration trials establish working paths, not persona effects or comparable scientific performance across benchmarks. Infrastructure recoveries changed researcher response formatting; the report lists all 22 attempts.

[Per-case results](reports/conversion_v2/README.md) · [Machine-readable results](reports/conversion_v2/results.json)

## Repository guide

| Path | Contents |
|---|---|
| `src/personasciencebench/` | Six adapters, simulator, runtimes and CLI |
| `src/expbench/` | EXP-Bench design pipeline |
| `configs/`, `manifests/` | Experiment settings and pinned sources |
| `docs/` | Conversion standards, setup and research plans |
| `reports/conversion_v2/` | Current result summaries and catalog readiness |
| `external/`, `data/`, `prepared/`, `runs/` | Ignored local sources, assets, task packages and raw records |

Older generated reports and local runs were archived outside the repository during cleanup. The latest raw records remain local and are not redistributed. Implementation code is MIT licensed; upstream data retain their own licenses. See [CONTRIBUTING.md](CONTRIBUTING.md).
