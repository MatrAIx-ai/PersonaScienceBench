# Current benchmark adaptations

This is the historical implementation record for the five-case-per-benchmark Luna study. The [seven-track conversion revision](design/conversion_revision_v2.md) documents the current automatic conversion and subsequent two-case trials.
The [modification standard](benchmark_standards.md) is normative; this document
records how the current subset applies it and where experimental conditions
change native execution. Earlier two-case adapter reports remain historical evidence.

## Shared collaboration protocol

The [approach and result review protocol](adapters/collaboration.md) is available across all five current tracks. It adds explicit intermediate handoffs while retaining the source task and grader. The per-benchmark records below describe the earlier passive-pilot settings unless stated otherwise.

## Common conversion contract

Every conversion separates three views: public task/input assets, private
researcher facts, and evaluator references. Export is allowlisted, not a dump of
upstream metadata. Facts retain provenance and unknowns. Public instructions keep
essential methods and deliverables; interaction is optional. Submissions are sealed
before grading. Source revisions and content hashes are recorded in
`manifests/sources.json`, EXP manifests, and controller records.

The current experiment uses `openai/gpt-6-luna`, reasoning effort `none`, for actor,
simulator, and LLM judges. Native programmatic graders remain programmatic.
Both conditions use 20 actor iterations and at most six researcher questions.
The shared simulator releases at most one approved fact per reply. These are
selected experimental budgets, not claims to reproduce every upstream agent setup.

Approved facts, selected tasks, final runtime environments, and grading contracts
are held fixed across persona conditions. Persona off still has a simulator.
Neutral enabled defaults are a different condition from disabled persona.
The comparison has one actor attempt per task/condition apart from explicitly
retained infrastructure/interruption recovery; it is not a repeated-seed study.

## DiscoveryBench

**Selection:** requirements engineering, NLS incarceration, meta regression,
NLS socioeconomic status, and World Bank education/GDP. Exact composite IDs are
in [the selection file](../configs/luna-five-selection.json).

**Preserved/public:** selected source question, dataset/column descriptions,
original CSV inputs, and required scientific objective. The actor analyzes these
inputs in the shared isolated Python runtime.

**Researcher:** explicitly reviewed domain-knowledge statements, retaining source
qualifiers. Dataset descriptions stay public; context is not hidden to force questions.

**Private:** hypotheses, workflows, intermediate/reference answers, and the answer-key
join. Test references are joined from the pinned answer key using dataset,
metadata suffix, and question ID; missing/ambiguous joins fail.

**Adaptation/evaluation:** an AST allowlist loads hash-pinned native scoring helpers
without upstream clients or reference-printing code. An injected judge preserves
native valid-response prompts, context matching, variable/relation scoring, and
aggregation. Malformed outputs become explicit errors rather than upstream
negative/undefined scores. Provider-unsupported settings are recorded under the
selected experiment policy. `final_score`, `recall_context`, and
`mean_accuracy_score` retain their 0–1 scales. Reference agreement does not by
itself verify correct execution of the analysis.

Implementation: `src/personasciencebench/adapters/discoverybench.py`.
[Native scoring details and earlier pilot](adapters/discoverybench.md).

## BixBench

**Selection:** `bix-10-q2`, `bix-8-q2`, `bix-51-q1`, `bix-54-q1`, `bix-13-q1`,
from five distinct capsules.

**Preserved/public:** exact questions, named statistical methods, and explicitly
reviewed capsule data files. Legitimate processed measurements/labels remain inputs.
Archives and extracted members are hash-checked; reference notebooks are not exported.

**Researcher:** reviewed headers, sheet names, category labels, identifier/encoding
clarifications from permitted data. No target coefficient, gold answer, or result
is derived from reference notebooks for the simulator.

**Private:** annotation answer/result fields, distractors, and executed reference
notebooks. The actor receives only allowlisted data, not the complete capsule archive.

**Adaptation/evaluation:** final submissions require an analysis artifact and
`executed_analysis=true`, a harness gate rather than proof of correctness. The
bridge loads pinned native online `OpenEndedGrader` classes and prompts with an
injected judge. It preserves native open-answer parsing (including incorrect for
malformed native responses), `grade` (0/1), `correct`, and `refusal`. This is not the
paper's separate trajectory-to-MCQ evaluation pipeline.

Implementation: `src/personasciencebench/adapters/bixbench.py`.
[Grader behavior and earlier pilot](adapters/bixbench.md).

An [active researcher collaboration pilot](adapters/bixbench_collaboration.md) now lets the researcher initiate requests and review agent handoffs in a persistent OpenHands session. Its ten-case persona-off configuration is `configs/luna-bixbench-collaboration-ten.json`; the native answer grader is retained.

## ScienceAgentBench

**Selection:** verified instances `22`, `45`, `67`, `87`, and `92`.

**Preserved/public:** native task instructions and exact reviewed data files.
Outputs retain their native paths and schemas. Provisioning requires the separately
supplied `benchmark_verified.zip`; private grader dependencies are allowlisted.

**Researcher:** selected permitted expert-guidance excerpts with provenance, not
the whole expert-guidance field. For example, the newer cases expose brief JNMF
or NetCDF background. Unknown analysis choices and reference results remain unknown.

**Private:** gold programs, solution pointers, native evaluator dependencies and
reference outputs. The actor's runtime has no access to the verified reference bundle.

**Adaptation/evaluation:** require a standalone `solution.py` and native output;
replay the sealed program with public inputs in a fresh sandbox, then run unchanged
native graders separately. Report `valid_program` independently from `success_rate`.
The current batch uses the Bubblewrap replay/grading path; the adapter also retains
a separate Docker evaluation-request interface. CodeBERTScore is not implemented.
SAB 87 uses the expanded NetCDF runtime recorded in
`configs/luna-netcdf-requirements.lock.txt`; its initial baseline dependency failure
is retained alongside the replacement. The persona run uses that same expanded
runtime; other Python cases use the original scientific environment.

Implementation: `src/personasciencebench/adapters/scienceagentbench.py`,
`scienceagentbench_provision.py`, and `scienceagentbench_runtime.py`.
[Original provisioning/interface details](adapters/scienceagentbench.md).

## Terminal-Bench-Science

**Selection:** HBV calibration, ODE law discovery, symbolic regression, traffic-flux
inversion, and spin-glass ground state. Exact native IDs are in
[the Terminal selection](../configs/luna-five-terminal-selection.json).

**Preserved/public:** original instructions, scientific constraints, submission
paths, native actor Dockerfiles, and permitted input files/public diagnostics.
Native task canaries are retained. Reviewed contextual overlays do not conceal
required criteria or imply that conversation is necessary to solve a task.

**Researcher/private boundary:** only small reviewed background/advice excerpts
are simulator-visible. Oracle solutions, hidden catchments, equations, and verifier
references stay private. Exact required native files are mirrored into workspace
paths for sealed collection; this is an artifact transport adaptation.

**Runtime changes:** the current actor has networking disabled and a 20-iteration
OpenHands cap in addition to the native wall-time ceiling. Native configured
CPU/memory allocations are used. These constraints can affect completion and are
not equivalent to the unrestricted native actor setting.

**Evaluation change:** the host cannot run Harbor's nftables-FIB-dependent network
sidecar. `--verifier-backend native-docker` instead runs the unchanged native
`tests/Dockerfile` and `tests/test.sh` in a separate Docker container with
`--network none`. The recorded variant is
`terminal-native-separate-docker-network-none-v1`. No LLM replaces the native
binary `reward`. Normal nonzero test exits with a valid reward file retain their
native score; infrastructure failures/timeouts remain distinct.

Current caveat: the persona traffic-flux submission included an extra `analysis`
artifact; the strict native artifact-set check rejected it before grading. Its
score remains missing in the snapshot until an explicit recovery is recorded.
When the actor finishes without a sealed submission, the explicit
`terminal-missing-submission-false-v1` policy counts the outcome as false
(`reward=0`). The status remains `missing_submission`, and score provenance is
`missing_submission_policy`; no native verifier grade is claimed. These zeros
enter score denominators in both conditions. Interrupted runs and infrastructure
errors remain unscored. Summary generation applies this policy to historical
records without modifying their raw attempts, and reports native grades and
policy zeros separately. Missing submissions are not automatically rerun.

Implementation: `src/personasciencebench/terminal_runner.py`, `terminal_native.py`,
and `adapters/terminal_bench_science.py`.
[Original Harbor bridge and two-case contract](adapters/terminal_bench_science.md).

## EXP-Bench

**Selection:** `neurips2024/97649/0`, `neurips2024/94328/5`,
`neurips2024/94391/7`, `iclr2024/18447/7`, and `iclr2024/18865/4`, covering
JaxMARL, QuaRot, CycleNet, MogaNet, and SineNet.

**Preserved/adapted task:** the migrated track asks for an experiment design using
curated task cards and masked, pinned code workspaces. It is intentionally
`design_only`; a plan score is not evidence of reproducing the full experiment.
Code snapshots are preparation revisions, not asserted original paper-run commits.
Acquisition and repository pins live in `manifests/expbench*.json`.

**Researcher/private boundary:** scoped approved facts are disclosed in response
to relevant questions. Private experiment references and masked solution material
are unavailable to the actor. The same `Persona` schema is rendered into the
scoped simulator's system message, but replies remain approved fact text verbatim.
Persona therefore conditions relevance/selection, not expressive paraphrasing.
EXP accepts a fixed TOML profile; shared domain/task routing is not integrated.

**Evaluation:** retain the reference-coverage judge (three judgments averaged)
and separate integrity monitor. Do not collapse these into a generic design-quality
score. The current comparison uses Luna; older Sonnet/o3-mini results are a separate
experiment. Full-workflow continuation remains an experimental extension, not the
track evaluated here.

Implementation: `src/expbench/realistic.py`, `scoped_researcher.py`, and `schema.py`.
[Preparation, masking, and historical evaluation details](adapters/expbench.md).

## Reporting and recovery

The current [seven-track report](../reports/conversion_v2/README.md) records task IDs, statuses, native scores, interaction counts and local trace locators. Earlier five-track comparisons are archived locally. Compare matched tasks and state denominators; never combine unlike metrics into one average. Record infrastructure recovery separately from scientific failure and retain every attempt.

The two-case-per-track integration trial is not a persona comparison. Establishing persona effects requires matched conditions, repeated runs, controls for available information, and persona-fidelity assessment.
