# Automated benchmark conversion plan

This is the historical five-track catalog plan. The [implemented seven-track revision](conversion_revision_v2.md) supersedes its remaining automation work and records the new conversion policy.

Status: implemented for catalog conversion on 2026-09-24; scientific model runs
remain separate.

This document keeps benchmark expansion separate from the research experiment
design. The current setup has five prepared cases per benchmark (25 total).
The pinned source inventories contain 1,102 task units; this is an inventory
count, not a claim that all tasks are ready to run or suitable for interaction
experiments. EXP-Bench remains design-only.

## Objective

Replace per-case pilot configuration with one automated preparation policy per
benchmark. Ordinary cases should produce runnable packages automatically;
ambiguous source records or unavailable resources should produce explicit
exceptions. Manual authoring of every case is not an inherent requirement.

## Work by benchmark

| Benchmark | Source inventory | Current limitation | Planned automation |
| --- | ---: | --- | --- |
| DiscoveryBench | 264 tasks | Five-task conversion allowlist; CSV-only asset assumptions; reference lookup tailored to test cases. | Extract attributable facts from `domain_knowledge`; preserve public questions, data and column descriptions; keep hypotheses and reference workflows private. Support TXT/Stata inputs and split-specific references. |
| ScienceAgentBench | 102 verified tasks | Context excerpts, input files, evaluator references and dependencies are configured for five tasks. | Generate manifests from native annotations and the verified archive. Use the native `domain_knowledge` field as the context source, separating background from procedural advice. Discover evaluator assets and dependencies while preserving actor/evaluator isolation. |
| BixBench | 205 questions across 59 capsules | Five capsule archives acquired; input manifests and schema facts are handwritten; no dedicated researcher-knowledge field. | Acquire each capsule once and reuse it across questions. Extract source-linked facts from permitted input metadata, schemas, sheets and encodings. Exclude reference notebooks and answer-bearing annotation fields. Flag unsupported formats or uncertain file roles. |
| Terminal-Bench-Science | 70 active tasks | Hardcoded mounts, exact output files and context excerpts; README background can be adjacent to reference solutions. | Generate preparation manifests from native task configuration and Docker assets. Support native artifact directories. Extract permitted descriptions and metadata; apply section-aware rules before using richer README material. |
| EXP-Bench | 461 tasks across 51 papers | Five handwritten context cards and repository mappings; source instructions mix background, design recipes and outcomes; some references and questions disagree. | Extract setup facts and fixed constraints with exact source spans. Keep evaluated design choices and expected results private. Reuse repository preparation by paper where applicable. Route inconsistent references, ambiguous questions and unsuitable task types to exceptions. |

DiscoveryBench and ScienceAgentBench have dedicated knowledge fields, making
context extraction more direct. ScienceAgentBench still needs broader runtime
provisioning. BixBench and Terminal-Bench-Science require more asset handling.
EXP-Bench requires the most semantic checking because supplying the method can
give away the design being evaluated.

## Shared preparation pipeline

1. **Enumerate and normalize.** Read all task records from pinned sources;
   generate stable task/study identifiers and manifests. Remove pilot-only
   restrictions, including the requirement that every selected task come from
   a different study.
2. **Separate information.** Apply benchmark-specific rules for public inputs,
   simulator knowledge and evaluator-only material. Keep essential execution
   and submission requirements public. Exclude private answer material before
   context extraction wherever the source structure permits it.
3. **Extract context.** Prefer deterministic parsing of dedicated fields and
   metadata. Use structured model extraction where semantic separation is
   necessary. Record exact source locations and distinguish background facts,
   fixed requirements and optional advice. Do not invent missing knowledge.
4. **Validate and package.** Check source hashes, required fields, asset paths,
   information boundaries and extraction provenance. Record the actual
   validation method; automated validation must not be labeled human review.
   Model-based checks do not guarantee absence of leakage.
5. **Report readiness and exceptions.** Track context preparation, asset
   availability, runtime/evaluator readiness and actual execution separately.
   A generated package is not evidence of a successful benchmark run.

## Research constraints

- Keep task content and the permitted fact pool fixed across persona conditions.
- Allow an empty fact pool when the source supplies no additional context.
  Record whether a task has meaningful researcher-exclusive information before
  using it to study interaction or expertise effects.
- Treat adopting full native guidance instead of today's selected excerpts as
  a versioned conversion-policy change. Preserve the distinction between
  background knowledge and procedural advice.
- Preserve native task objectives and scoring contracts. Separate malformed
  source records and infrastructure failures from model failures.
- Keep EXP-Bench design-only; full experiment execution and GPU provisioning
  are outside this deferred work.

## Conversion result

| Benchmark | Source tasks | Converted | Excluded | Current asset status |
| --- | ---: | ---: | ---: | --- |
| DiscoveryBench | 264 | 264 | 0 | Source assets available |
| BixBench | 205 | 205 | 0 | 32 questions currently have acquired capsule assets; other episode manifests record acquisition requirements |
| ScienceAgentBench | 102 | 102 | 0 | Full verified archive provisioned locally; evaluator runtime dependencies still require per-environment validation |
| Terminal-Bench-Science | 70 | 70 | 0 | Native task packages available; Docker/Harbor runtime validation remains separate |
| EXP-Bench | 461 | 460 | 1 | Design-only; repositories are not required |
| **Total** | **1,102** | **1,101** | **1** |  |

The excluded task is `neurips2024/94391/4`, whose source annotation lacks a
valid reference design. Automatic conversion failures are discarded from the
converted benchmark and retained in the report with their source ID and reason.
Missing assets or unavailable runtimes do not count as conversion failures.

Regenerate the catalogs with:

```bash
.venv/bin/python scripts/expbench/build_full_design_catalog.py
.venv/bin/python scripts/convert_benchmark_catalogs.py
```

Generated controller catalogs and readiness reports are stored under ignored
`data/design_catalog/` and `data/conversion_catalog/` paths.

## Existing references

- [Conversion standards](../benchmark_standards.md)
- [Current benchmark adaptations](../benchmark_adaptations.md)
- [Current adapters](../../src/personasciencebench/adapters/)
- [ScienceAgentBench archive provisioner](../../src/personasciencebench/scienceagentbench_provision.py)
- EXP-Bench source audit (historical record archived locally)
