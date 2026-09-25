# Benchmark adaptations

The authoritative [conversion revision](design/conversion_revision_v2.md) describes extraction, provenance, information boundaries, runtime requirements and commands for all seven tracks. The [conversion standard](benchmark_standards.md) defines acceptance criteria. The [current trial](../reports/conversion_v2/README.md) preserves native scores and records every attempt.

## DiscoveryBench

Preserve native questions, datasets and discovery scoring. Source-exact domain knowledge becomes simulator context; advice is labeled optional. Use approach and result reviews. [Adapter guide](adapters/discoverybench.md).

## BixBench

Preserve questions and native open-answer grading. Automatically extract permissible capsule data and input schema facts; unresolved input roles block readiness. Require executed-analysis evidence. Reviewed CHIP selections retain input hashes and schema/label explanations but exclude computed aggregate findings. [Adapter guide](adapters/bixbench.md).

## ScienceAgentBench

Map native verified annotations, files and outputs automatically. Keep gold programs and references evaluator-private. Replay sealed submissions with the native verifier. [Adapter guide](adapters/scienceagentbench.md).

## Terminal-Bench-Science

Preserve native instructions, artifact contracts and Docker grading. Extract eligible scientific README context while excluding solutions and hidden tests. Missing submissions receive the declared zero reward. [Adapter guide](adapters/terminal_bench_science.md).

## EXP-Bench

Design-only: classify exact public setup spans into simulator context, exclude unresolved question/reference mismatches, and generate public-only workspaces. Retain reference coverage and a separate integrity gate. [Adapter guide](adapters/expbench.md).

## ASI-Bench

Use native B3 prompts and inputs with eligible B2 methodological guidance held by the researcher. Retain local seed31415 gates and weighted scorers. This is a collaborative adaptation, not an official autonomous B3 score. Assets and external runtime requirements remain separately tracked.

## SciConvBench

Preserve native ambiguous/inconsistent requests, intended specifications, clarification dialogue and judging. Reference annotations remain evaluator-private. This measures dialogue/specification quality, not execution success.
