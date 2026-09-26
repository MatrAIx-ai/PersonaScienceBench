# PersonaScienceBench

**Scientific agents working with simulated researchers.**

PersonaScienceBench studies how researcher expertise and communication affect an AI agent’s scientific work. The actor inspects inputs, runs tools, consults a simulator, and submits its work. The simulator uses source-grounded context, with optional persona instructions. Each benchmark retains its own evaluation contract.

[Conversion rules](docs/design/conversion_revision_v2.md) · [Personas](docs/personas.md) · [Setup](docs/reproducibility.md) · [Results](reports/persona_action_case_study/benchmark_score_ranking.md) · [Conversion history](reports/conversion_v2/README.md)

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

1. Preserve the scientific objective, required inputs, outputs and native scoring contract; label every adaptation.
2. Separate public task information, source-attributed simulator context and evaluator-private references. Never infer missing study facts.
3. Keep persona separate from knowledge: styling cannot alter task requirements or the fact pool.
4. Record preparation failures, unresolved assets and runtime limits explicitly.
5. Save actor–simulator interactions, submissions, evaluation results and recovery attempts locally.

Execution and design tracks use approach and result reviews; additional questions are optional. SciConvBench keeps its native clarification dialogue. BixBench’s automatically extracted schema facts are also observable from public inputs. ASI uses B3 tasks with optional B2 methodological guidance, an explicit adaptation of autonomous B3.

The [per-benchmark conversion document](docs/design/conversion_revision_v2.md) specifies extraction, access boundaries, scoring and commands. The [conversion standard](docs/benchmark_standards.md) defines acceptance criteria.

## Researcher personas

The merged [science-persona profiles](docs/science_personas/README.md) add an opt-in 56-attribute schema and deterministic renderer. The [Phase 1 planner](docs/science_personas/experiment_plan.md) creates matched persona arms for the five retained tracks; the proposed 50-task experiment has not been run. Existing profiles remain supported. A separate [action-persona case study](reports/persona_action_case_study/README.md) screens a reproducible sample of 300 MatrAIx records using three static rules, then measures whether the selected action instructions visibly change one controlled model response.

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

For a matched DiscoveryBench experiment using Azure GPT-5.6 Sol, see the [Azure persona pilot](docs/discoverybench_azure_pilot.md) and its [16-run results](reports/discoverybench_azure_pilot/README.md).

Follow the [setup guide](docs/reproducibility.md), then the [conversion and runtime commands](docs/design/conversion_revision_v2.md#commands). Source revisions and checksums are pinned in `manifests/`. Install ASI from the pinned local source as described in the conversion guide. The setup guide retains historical instructions for the two discarded tracks.

Run independent cases concurrently and use a fresh output directory for every attempt. Raw model/tool records and readable conversations live under ignored `runs/`; published reports contain summary outcomes and local record locators.

## Current results

**September 26, 2026: 30 action personas and persona off were run on two fixed
cases from each of the five retained benchmarks, using GPT-6 Luna for actor,
simulator, and LLM judges.** This leaves 310 final experiment records. Independent
episodes ran concurrently and each task reused one persona-off result across its
30 paired comparisons.

Nine of ten retained control tasks had a native score. Their normalized persona-
off average was **0.4685**. Among the 24 personas with complete 9-task score
coverage, deviations ranged from **+0.1911** (`candidate_259`) to **-0.1432**
(`candidate_019`). These are descriptive single-run differences from an enriched
profile sample, without uncertainty estimates; they do not establish general
persona effects.

[Persona score ranking](reports/persona_action_case_study/benchmark_score_ranking.md) · [Selected extreme profiles](reports/persona_action_case_study/extreme_personas.md) · [Conversion pilot history](reports/conversion_v2/README.md)

A separate [DiscoveryBench Azure pilot](reports/discoverybench_azure_pilot/README.md)
ran two studies across persona off, a neutral profile, and low/high statistical
expertise, with two repetitions (**16 scored runs**). Using GPT-5.6 Sol for all
three roles, mean native scores were **0.500, 0.250, 0.500, and 0.833**, respectively.
The high-expertise gains occurred in the engineering study in both repetitions.
The small study count and observed native-grader context sensitivity limit these
results to exploratory evidence; they do not establish a general persona benefit.

## Repository guide

| Path | Contents |
|---|---|
| `src/personasciencebench/` | Six adapters, simulator, runtimes and CLI |
| `src/expbench/` | EXP-Bench design pipeline |
| `configs/`, `manifests/` | Experiment settings and pinned sources |
| `docs/` | Conversion standards, setup and research plans |
| `reports/conversion_v2/` | Current result summaries and catalog readiness |
| `reports/persona_action_case_study/` | Persona selection, retained-benchmark ranking and extreme profiles |
| `reports/discoverybench_azure_pilot/` | Matched Azure DiscoveryBench pilot outcomes and limitations |
| `external/`, `data/`, `prepared/`, `runs/` | Ignored local sources, assets, task packages and raw records |

Older generated reports and local runs were archived outside the repository during cleanup. The latest raw records remain local and are not redistributed. Implementation code is MIT licensed; upstream data retain their own licenses. See [CONTRIBUTING.md](CONTRIBUTING.md).
