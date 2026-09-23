# EXP-Bench dataset inspection

The local snapshot contains the complete published CSV and the richer JSON
annotations for the same 51 papers. The data provides a workable starting point
for a design-only benchmark, but the published fields need review before they
can serve as model inputs and grading references.

This inspection covers all records structurally and examines selected task
contents, all 20 question differences beyond basic formatting, and the original
grading prompts. It does not validate every annotation against its source paper
or execute experiments.

## Dataset size

| Source venue | Papers | Tasks |
| --- | ---: | ---: |
| ICLR 2024 | 24 | 199 |
| NeurIPS 2024 | 27 | 262 |
| Total | 51 | 461 |

The CSV reports 12,737 subtasks across the original full-experiment evaluation,
with 8–57 per task. These are not exclusively design criteria. Both releases
contain the same number of tasks per paper, with unique task IDs and complete
zero-based index coverage.

## What the two releases contain

The CSV has 11 columns: `conference`, `paper_id`, `paper_title`, `task_index`,
`task_type`, `subtask_count`, `question`, `agent_instructions`,
`impl_requirements`, `expected_outcome`, and `source_files`.

The CSV does **not** contain `design_complexity`. The repository's per-paper
JSON files add the reference variable groups, a separate method description,
design ambiguity, experimental constraints, and uncertainty annotations.

| Annotation | Records containing the field |
| --- | ---: |
| `design_complexity` | 461 |
| `experiment_constraints` | 461 |
| `random_uncertainty` | 461 |
| `systematic_uncertainty` | 458 |
| `design_ambiguity` | 444 |

Presence does not imply valid content. In particular, constraint and uncertainty
annotations sometimes contain suggested modifications rather than requirements
of the original task. Those suggestions should not automatically become mandatory
grading criteria.

## Task types observed in the files

| CSV type | Count | Corresponding annotation fields |
| --- | ---: | --- |
| 1 | 210 | `source` and `masked_source` |
| 2 | 123 | `source` and `mode`, without `masked_source` |
| 3 | 128 | `no_answer`, without matched `source` files |

These descriptions reflect the released fields, rather than a new classification
of scientific difficulty. Type 3's `no_answer` is an implementation-extraction
note: the extraction process did not locate a matching implementation. These
tasks still have design references and can be candidates for design-only work.

Some type 2 tasks ask for a program or demonstration, such as a Game of 24 solver
or an animation of random-agent behavior. They need reformulation or exclusion
if the target is hypothesis-driven experimental design. Other type 2 tasks
already ask for model comparisons, so type alone is insufficient for filtering.

## Structural and content issues

| Finding | Count | Handling in the local joined file |
| --- | ---: | --- |
| Design variable groups at the expected level | 419 | Preserved |
| Design nested inside another `design_complexity` | 41 | Redundant wrapper removed |
| Design field contains ambiguity notes instead of variable groups | 1 | Reference set to `null`, with a flag |
| CSV questions containing literal Unicode/hex escapes | 54 | Escapes decoded; originals preserved |
| CSV/GitHub questions identical after Unicode/whitespace normalization | 439 | Alignment recorded |
| Additional question differences explained by Markdown formatting | 2 | Alignment recorded |
| Remaining question-text differences | 20 | Both versions saved for review |
| Pairs of duplicate questions after normalization | 2 | Kept as distinct tasks; listed in the audit |
| CSV implementation-requirement fields not parseable as lists | 2 | Original text retained, with flags |

After unwrapping, **460/461 tasks have nonempty dictionaries for all three
variable groups**. This is structural coverage, not a guarantee of scientific
correctness or readiness for grading.

The unusable reference is `neurips2024/94391/4`, the CycleNet MLP-versus-Linear
comparison on Solar-Energy. Its `design_complexity` contains only
`design_ambiguity`. No replacement labels were inferred.

The two CSV implementation-requirement parsing issues occur in
`neurips2024/93638/0` and `iclr2024/17388/6`.

Other schema differences include four string-valued `experiment_constraints`
entries, three missing `systematic_uncertainty` fields, and seventeen missing
`design_ambiguity` fields. Raw annotations remain unchanged.

### Question alignment needs more than matching indices

Most of the 20 remaining differences are rewordings, including converting
assertions of results into questions. A few change what the agent is asked to
assess. For example, `neurips2024/98326/0` asks about distributed-training
accuracy in the CSV; the repository version also asks about reduced wall time.
A grader built from the repository labels could therefore expect a measurement
that the CSV question no longer requests.

The joined file uses the CSV question and records its alignment status. See
[`question_differences.json`](../../data/exp_bench/question_differences.json) for all
20 comparisons. They were not silently treated as semantically equivalent.

Two pairs have identical questions but different reference designs:
`neurips2024/93431/1` and `/2` (Trace), and `neurips2024/94391/0` and `/8`
(CycleNet). Their other task fields differ, so they were not automatically
deduplicated. A question-only adaptation needs to reconcile these references or
provide enough context to distinguish the tasks.

## Implications for design-only evaluation

**Detailed instructions often supply the design already.** In the JaxMARL
comparison (`neurips2024/97649/0`), the method specifies the algorithms, task
selection, computational controls, and metrics. Using that entire method as input
would largely test extracting and organizing an existing design.

**Some inputs disclose expected results.** The same task's agent instructions
specify an approximately sixfold MAPPO speed advantage. Trace task
`neurips2024/93431/8` supplies an approximately threefold optimization speed
advantage. MOLGEN task `iclr2024/19281/3` includes a prior numeric performance
target in the question itself. Input cleanup must therefore examine the question,
method, and instructions, not only remove `expected_outcome`.

**Some design references also contain outcome values.** For example,
`iclr2024/19292/0` embeds expected word-error rates in its dependent-variable
descriptions. A design-only grader should assess the choice and definition of
measurements, without requiring the model to predict those empirical values.

The audit includes a narrow regex screen for potential outcome hints. It flags
seven instruction fields, one question, and three design references. These are
review candidates, not validated leakage counts: there are both false positives
(such as an expected input directory structure) and omissions. The Zipformer
numeric example was found by reading the data, not by that screen.

**The original design grader is narrower than a full protocol grader.** It
compares independent, dependent, and constant variables. A richer design rubric
would need explicit criteria for controls, baselines, procedure, uncertainty,
analysis, and feasibility. The existing annotations can inform those criteria,
but require review and allowances for scientifically valid alternatives.

For an initial pilot, review comparative and ablation tasks across several papers,
retain necessary background, and separate input constraints from choices the
model must make. Keep reference designs and outcomes private to the grader.
Any development/test split should group tasks by paper, since multiple tasks
share methods and background from the same source.

## Local outputs and verification

- [`tasks.jsonl`](../../data/exp_bench/tasks.jsonl): 461 joined records with reference
  designs, flags, and provenance. Contains answers; not a model prompt export.
- [`examples.json`](../../data/exp_bench/examples.json): JaxMARL, MogaNet, and the
  malformed CycleNet reference.
- [`audit.json`](../../data/exp_bench/audit.json): Full counts, issue IDs, and review
  excerpts.
- [`papers.csv`](../../data/exp_bench/papers.csv): Counts by paper and task type.
- [`manifest.json`](../../data/exp_bench/manifest.json): Source revisions and checksums.

The examiner verifies all 59 downloaded source files against their SHA-256
checksums, validates per-paper index coverage, and rejects duplicate task IDs.
The snapshot includes upstream attribution and license notices. Downloading and
examining the dataset required no experiment execution or model API calls.
