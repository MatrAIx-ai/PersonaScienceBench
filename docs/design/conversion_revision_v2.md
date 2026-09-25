# Automated conversion revision

This revision extends the existing five tracks with ASI-Bench and SciConvBench. Every adapter produces a public task, researcher context, evaluator mapping, provenance, and explicit preparation status. The live two-case-per-benchmark results and full traces are in [the conversion trial report](../../reports/conversion_v2/README.md).

## Implemented by benchmark

| Benchmark | Automated conversion | Researcher interaction | Preserved evaluation |
|---|---|---|---|
| BixBench | Pinned capsule acquisition, archive/member hashes, explicit data-file filtering, automatic CSV/XLSX schema facts outside the legacy curated cases; unknown input roles block readiness | Approach, executed analysis, evidence review | Native open-answer grader; existing executed-analysis submission requirement |
| EXP-Bench | Cached model classification selects exact public setup/background spans; unresolved question/reference mismatches excluded; minimal public-only design workspace generated automatically | Approach and completed-design review | Reference coverage and separate integrity gate; design-only |
| DiscoveryBench | Native question/data/reference joins; source-exact domain-knowledge spans and advice classification; native asset paths | Approach and discovery/evidence review | Native context, variable, and relation scoring |
| ScienceAgentBench | Native annotation/file/output mapping, verified archive provisioner, isolated evaluator dependencies, classified guidance, generated dependency recipes | Implementation approach and program/output review | Sealed program replay and unchanged native verifier |
| Terminal-Bench-Science | Native instructions/images/artifact declarations; section-scoped README context with solution/outcome exclusions | Approach and artifact review | Separate native Docker verifier; declared missing-submission penalty |
| ASI-Bench | Formal task catalog; pinned seed31415 prompts; B3 public, method sections of B2 researcher-only; declared inputs/outputs/runtime | Approach, execution, evidence review | Native local gates and weighted scorers in an isolated evaluator process |
| SciConvBench | Native request/specification/issue split; source ID and ontology retained; native paper prompt-length cap | Native clarification dialogue, up to ten questions plus final specification | Original judge classes/parsers and paper metric functions, with configured Luna judge |

Native full-prompt/source dumps are not used as researcher knowledge. An empty fact pack is valid and recorded. Fact extraction is automatically validated, not labeled human review. Model classification reduces ambiguous extraction but cannot prove the absence of leakage.

BixBench's generic schema facts are observable from its public inputs; they are not researcher-exclusive study knowledge. Its original five reviewed fact packs remain available for historical compatibility. The new two-case run uses questions outside that five-case list.

EXP context classification receives only the public question and public method/instruction spans, not the reference design or expected-outcome field. Every selected span retains its exact source locator and extraction cache hash. Public-source provenance was verified against the pinned release. The revision excludes task-level question/reference mismatches instead of merely attaching a warning.

For ASI, this is a **B3 plus optional B2 methodological guidance** condition, not native autonomous B3. Public seed31415 reference artifacts stay evaluator-only at runtime. Downloaded prompt catalogs do not imply every instance's data or external scientific software is installed. The two live cases use scientific Python CPU tasks. The isolated evaluator has no network or credentials; tasks requiring external judge/solver services need an explicitly supported runtime before being declared runnable.

For SciConv, the simulator's intended specification is user-owned task information, not a scientific answer key. The converted population uses source cases and the 20,000-character prompt limit; it does not reproduce the paper's exclusion based on previous models' successes. Related domain/case IDs stay grouped across perturbation types. Native conversation and final-specification metrics are retained separately from execution benchmarks. Native per-case clarification ratios are reported alongside the paper aggregator's original CR/CP values; that aggregator can produce recall above one because it uses question counts.

## Commands

Run from the repository root after fetching pinned sources and provisioning the supplied ScienceAgentBench archive. Source hashes and revisions are in `manifests/sources.json` and `manifests/expbench.json`.

```bash
# Install conversion/scoring support; use the pinned local ASI source.
uv pip install --python .venv/bin/python -e ".[conversion,scientific-evaluation]"
uv pip install --python .venv/bin/python -e external/sources/asibench

# Acquisition is cached, checked against pinned public checksums, and has no model calls.
.venv/bin/python scripts/acquire_conversion_assets.py bixbench
.venv/bin/python scripts/acquire_conversion_assets.py asibench --tasks materials.relaxation_mode_recovery math.nnls_modulus_deblur

# EXP extraction uses the configured local OPENROUTER_API_KEY and caches exact source selections.
.venv/bin/python scripts/expbench/build_full_design_catalog.py
.venv/bin/python scripts/convert_benchmark_catalogs.py

# Generate per-task dependency recipes and report missing/unmapped dependencies.
.venv/bin/python scripts/prepare_conversion_runtimes.py
# Add --install --tasks TASK_ID ... to build cached environments for selected recipes.

# Re-render and collect the declared two-case trial and all recovery attempts.
.venv/bin/python scripts/report_conversion_revision.py
```

Prepared trial selections are in `configs/conversion-v2-two-*-selection.json`, with the original three Python tracks in `configs/conversion-v2-two-selection.json`. SciConv uses its adapter's fixed two-case selection. Existing run directories are immutable attempt locations; new runs require a fresh output path.

The new adapters follow the existing `personasciencebench.cli prepare` interface. ASI executes through the shared `run` command. SciConv executes through `python -m personasciencebench.sciconv_runner --prepared ... --output ... --config configs/conversion-v2-two.json --parallel 2`. EXP uses `expbench.realistic run` and creates its own public design workspace when no repository map is supplied. Terminal retains its separate native-image runner.

## Readiness and validation

The completed catalog contains 2,280 converted cases and 24 exclusions across seven benchmarks; see [counts and asset-readiness limits](../../reports/conversion_v2/conversion_summary.md).

Generated catalogs live under ignored `data/conversion_catalog/`; EXP task cards under `data/design_catalog/`. Conversion failures, unresolved asset roles, missing dependencies, and scientific failures have separate records. Dependency recipes for ScienceAgentBench infer private evaluator imports; they do not claim to discover every dynamic dependency or package an actor may choose.

Validation consists of the requested actual benchmark runs, conversion checks, syntax checks, source hashes, and readable-trace inspection. No additional model benchmark suite was added. Successful model results were not required for accepting a conversion, and low scientific scores were not rerun.

The researcher transport was strengthened after malformed responses: an explicit current-turn request and a forced single `researcher_decision` tool call prevent treating a generated future dialogue as a real exchange. Every accepted handoff still follows the same approach/result protocol. Historical attempts retain their original prompts and transport settings; this trial is not a homogeneous scientific comparison of protocol versions.
