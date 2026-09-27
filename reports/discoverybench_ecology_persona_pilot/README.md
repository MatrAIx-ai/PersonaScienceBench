# DiscoveryBench ecology persona pilot

This pilot examines whether persona attributes produce meaningfully different
researcher–agent workflows on a fixed scientific task. Six of six episodes were
submitted, evaluated and scored on the urban-land-use question, covering two
single-attribute contrasts and fresh persona-off and medium-reference controls.
Sensitivity scope shows an observable difference in analysis breadth; assumption
visibility has a weaker contrast. Native scores were zero in all six conditions
and are reported separately from behavioral diversity.

## Diversity objective

The contribution is a set of reviewed task packages that supports persona-based
variants of researcher preferences, analytical choices and interaction behavior.
An increase in native score is not required for a useful variant. Low and high
are attribute settings, not rankings of researcher quality; a narrower analysis
can provide a useful contrast to a broader one.

The pilot examines which differences align with the intended attributes, whether
those differences reach the executed workflow, and which behaviors remain shared.
Source facts, scientific questions, information boundaries and acceptance rules
remain fixed. Persona diversity does not relax factual or scientific validity.
The observations below are descriptive trace annotations, not a validated diversity
metric. One episode per condition cannot distinguish a reproducible persona effect
from ordinary model variation.

## Results and traces

Each trace contains the researcher–agent conversation, recorded terminal commands
and results, final submission, and numeric native grading dimensions. Profiles
show the identity actually recorded for each episode.

| Condition and trace | Native score | Commands successful / attempted | Total tokens | Episode seconds | Identity |
|---|---:|---:|---:|---:|---|
| [off](traces/off.md) | 0 | 5 / 10 | 182,320 | 138.2 | [Profile](profiles/off.md) |
| [reference](traces/reference.md) | 0 | 5 / 8 | 148,250 | 152.2 | [Profile](profiles/reference.md) |
| [assumption visibility low](traces/assumption_visibility_low.md) | 0 | 9 / 11 | 162,541 | 139.5 | [Profile](profiles/assumption_visibility_low.md) |
| [assumption visibility high](traces/assumption_visibility_high.md) | 0 | 4 / 5 | 106,236 | 105.6 | [Profile](profiles/assumption_visibility_high.md) |
| [sensitivity scope low](traces/sensitivity_scope_low.md) | 0 | 5 / 7 | 134,063 | 114.1 | [Profile](profiles/sensitivity_scope_low.md) |
| [sensitivity scope high](traces/sensitivity_scope_high.md) | 0 | 5 / 7 | 115,813 | 103.7 | [Profile](profiles/sensitivity_scope_high.md) |

- [Machine-readable results and provenance](results.json)
- [Task selection](selection.json)
- [Reviewed ecology tasks and native evaluator](../../docs/adapters/discoverybench.md#ecology-tasks)
- [Attribute catalog](../../docs/science_personas/ATTRIBUTE_CATALOG.md)

There were 88 API calls, 48 command attempts and 33 successful commands. All 15
command failures remain visible in the traces; the actors recovered within the
fixed episode limits. There were no command timeouts or episode-level
infrastructure failures. Usage totaled 795,326 prompt and 53,897 completion tokens
(849,223 combined). Dollar cost was unavailable. These counts include actor,
researcher and judge calls; elapsed time is descriptive for this host and run.

Every episode had one plan handoff, one result handoff and three researcher
decisions, including the initial request. There were no optional questions or
result-review revision requests.

## Observed behavioral diversity

### Sensitivity scope

The [high condition](traces/sensitivity_scope_high.md) executed analyses covering
all **nine year × buffer exposure definitions**: 1956, 1993 and 2009 at 50 m,
500 m and 1000 m. Its saved `analysis_results.txt` records the full grid. The
[low condition](traces/sensitivity_scope_low.md) used **two exposure definitions**:
2009 at 500 m and a 1000 m alternative, recorded as `MODEL u500` and `MODEL u1000`
in `analysis_output.txt`. These are distinct exposure definitions, not counts of
all fitted models; the low condition also performed diagnostic refits.

The low researcher initially requested one targeted sensitivity check. The actor
proposed the 1000 m alternative and the researcher approved it. In the high
condition, the actor proposed the nine-exposure grid before researcher approval.
The traces support a difference consistent with the intended scope contrast;
they do not show the researcher uniquely originating the grid.

Both the fresh [off](traces/off.md) and [reference](traces/reference.md) controls
also covered all nine exposures. The low condition's narrower scope is the
observed departure from those controls and is useful diversity in its own right;
high need not exceed the controls for the low/high contrast to matter. Both low
and high reported the same primary
habitat-adjusted odds ratio, approximately 0.8814 per 0.10 increase in urban
fraction, but used different uncertainty estimates (model-based versus HC0).
The workflows differ in more than breadth, and the single pair cannot isolate
a causal effect. High used fewer tokens and less elapsed time in this pair;
broader scope cannot be assumed to cost more from these observations.

### Assumption visibility

The high anchor requests a maintained assumption log with verification status;
the low anchor requests a summary of the main consequential assumption. Both
[low](traces/assumption_visibility_low.md) and
[high](traces/assumption_visibility_high.md) stated consequential assumptions,
identified uncertainty about exposure definitions, and qualified the conclusion
as conditional on `n.total > 0`. A maintained verification-status log was not
clearly present in the high condition's shared handoffs or submitted artifacts.

The common interaction protocol already asks for assumptions and uncertainties,
which may limit the contrast. Both conditions covered nine exposure definitions.
The requested high behavior was not clearly expressed; an exact profile injection
is not itself evidence of persona fidelity.

### Native score interpretation

All six episodes have context recall zero. The native evaluator found no matched
reference contexts, so there are no matched variable/relation grades to compare.
The high-minus-low final-score difference is zero for both attributes. Native
reference agreement and persona-driven behavioral diversity are separate outcomes:
these equal scores leave the observed scope contrast intact, while providing no
score-based distinction between conditions.

Native grading measures agreement with an evaluator-private reference; it does
not independently validate code or statistical conclusions. These runs show a
score floor for this question and configuration. Neither the scores nor successful
command execution alone establish whether the analyses are scientifically correct.
No score, reference, threshold or grading prompt was changed, and no zero was
excluded. There were no scientific reruns or regrades.

## Experimental setup

- **Scientific task:** `test/introduction_pathways_non-native_plants/metadata_1.json/0/1`.
  One question, one study, one episode per condition. It belongs to the three
  reviewed ecology questions in the existing 264-query catalog; this study is
  outside the five DiscoveryBench studies in the full-persona cohort.
- **Conditions:** off retains the researcher without identity. Reference assigns
  all 56 attributes medium. Each low/high profile changes only its named attribute
  from reference, with role `researcher` and domain `empirical data analysis` fixed.
  `robustness_demand` stays medium.
- **Shared settings:** 60 actor steps, ActiveResearcher protocol, 12 researcher
  requests maximum, six optional questions maximum, grounded researcher mode and
  general knowledge disabled by the runner default. All conditions use identical
  source facts, public inputs and evaluator settings.
- **Models:** Azure deployment `gpt-5.6-sol` for actor, researcher and judge, each
  with reasoning effort `none`. Every recorded API call resolved to
  `gpt-5.6-sol-2026-07-09`. Native judge sampling settings were preserved under
  evaluator version
  `discoverybench-native-prompts-settings-strict-errors-v1+azure-configured-judge-v1`.
- **Execution:** sequential, concurrency one, on 2026-09-26 from 22:55:45 to
  23:08:27 UTC. The frozen order (shuffle seed 20260927) was sensitivity high,
  sensitivity low, off, assumptions low, assumptions high, reference.
- **Provenance:** code revision `ea643c8be520e103b1b854cb10c6925adbf9c5af`;
  DiscoveryBench revision `c31fcf011e070f021a5f5b906896d0821f6880e8`.
  All 104 declared frozen input files passed the end-of-run hash check. Actual
  initial researcher system payloads were equal after removing identity, actor
  public inputs were identical, and recorded identities/model settings matched
  their configurations in all six episodes.

This is a descriptive screen on one question from one study. Sensitivity scope
is the stronger candidate for expanding behavioral coverage because its intended
contrast appears in the executed workflow. Assumption visibility needs a task
where verification status becomes consequential within the existing protocol.
Further validation should test whether these attribute-aligned differences recur
across repetitions and tasks, and distinguish them from variation within a single
condition. Retain all attempts and the native scores alongside that analysis;
seeking a positive score difference is not the criterion for selecting useful
persona variants.

## Reproduce with the shared runner

Follow the [Azure and runtime setup](../../docs/azure.md), including a passing
runtime check. The configurations below make paid model calls. Use fresh output
paths and keep the native source checkout unchanged.

```bash
.venv/bin/python -m personasciencebench --source-root external/sources prepare \
  --benchmarks discoverybench \
  --selection reports/discoverybench_ecology_persona_pilot/selection.json \
  --cases-per-benchmark 1 --output prepared/discoverybench-ecology-persona

for condition in sensitivity_scope_high sensitivity_scope_low off assumption_visibility_low assumption_visibility_high reference; do
  .venv/bin/python -m personasciencebench run \
    --prepared prepared/discoverybench-ecology-persona --benchmarks discoverybench \
    --config "reports/discoverybench_ecology_persona_pilot/configs/$condition.json" \
    --output "runs/discoverybench-ecology-persona-reproduction/$condition" \
    --actor-python .actor-venv --parallel 1
done
```

These commands reproduce the configuration, not deterministic model outputs.
The recorded run used the same shared CLI and one prepared task package. Full
local operator traces and raw records, including private evaluator/model records,
are retained under
`runs/discoverybench-attribute-pilot-20260926T225545Z/`; start with
`readable_traces.private/README.md`. They are not part of this report's Git files.
The local run also holds the frozen execution plan, source snapshot, integrity
check, injection check, behavioral evidence hashes and rendering manifest.
