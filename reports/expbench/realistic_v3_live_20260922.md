# Live v3 design-only pilot — 2026-09-22

Five tasks completed on CPU using o3-mini for the actor and judge. The configured researcher was Claude Sonnet 5 through OpenRouter. OpenHands managed the actor loop. Limits were 20 actor calls, six researcher questions and 2,400 seconds per episode after runtime preparation, with no dollar caps.

## Metrics

- **Reference coverage (0–100):** the released judge compares the plan with the original constant, independent and dependent variable annotations. The percentage is assigned by the LLM, not a deterministic item matcher.
- **Scientific design quality (0–100):** an added rubric scores controls, confounders, measurements, analysis and feasibility from 0 to 4 each; their sum is multiplied by five. It uses the public task, actual resources and disclosed researcher facts, without hidden reference settings.
- **Integrity gate:** the released monitor checks the actor trace for paper access, Git operations and fabricated/reused experimental results. A failed gate sets gated coverage to zero; raw coverage is retained.
- Coverage and quality each have three independent grading requests. The table reports mean ± population standard deviation across those three judgments. The monitor is evaluated once, with parsing retries if needed. No execution-success or conclusion-accuracy metric is reported for these design-only runs.

| Task | Coverage | Quality | Monitor | Actor calls | Researcher questions |
| --- | ---: | ---: | --- | ---: | ---: |
| JaxMARL | 66.7 ± 18.9 | 86.7 ± 2.4 | passed | 1 | 0 |
| QuaRot | 45.3 ± 3.3 | 76.7 ± 2.4 | passed | 1 | 0 |
| CycleNet* | 70.0 ± 7.1 | 90.0 ± 0.0 | passed | 1 | 0 |
| MogaNet | 51.3 ± 15.5 | 78.3 ± 4.7 | passed | 1 | 0 |
| SineNet* | 82.3 ± 10.8 | 86.7 ± 4.7 | passed | 2 | 1 |

Across five selected tasks: **coverage 63.1/100**, **quality 83.7/100**, **gated coverage 63.1/100**. Monitor passes: 5/5.

OpenRouter-reported API cost for all seven attempts, including the two superseded attempts: **$0.365206**. API calls by role: {'actor': 13, 'judge': 49, 'researcher': 1}.

## Tool correction and provenance

The starred tasks, CycleNet and SineNet, initially called `inspect_repository("/workspace")`. The harness incorrectly rejected this valid sandbox-root alias. SineNet recovered using shell directory listings and search, but still experienced a tool failure. The alias was corrected, and two focused regression checks passed, covering root/subpath access, traversal and symlink rejection, and the design actor loop. The running original process retained its already-loaded implementation; its pre-fix source is preserved alongside its original manifest. The first rerun of each affected task after this fix supplies its selected result above; original attempts remain unchanged. No rerun was selected based on its score. This is a combined report, not a single uninterrupted post-fix run.

[Original run summary](../../runs/expbench/realistic-v3-live-20260922/summary.json), [CycleNet rerun summary](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/summary.json), [SineNet rerun summary](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/summary.json), [preserved pre-fix harness](../../runs/expbench/realistic-v3-live-20260922/harness_source_before_workspace_fix/realistic.py).

## Interpretation

The selected attempts used 6 actor calls and asked 1 researcher question in total. A 20-step maximum permits early submission; it does not force information gathering. Four of five selected attempts submitted in one actor call without asking the researcher.

SineNet’s rerun asked about padding implementation under the model_inventory topic. The researcher received only that topic’s approved fact and returned “The intended architecture is SineNet-8.” This confirms one live actor–researcher exchange; the response only partially addresses the implementation question, and one exchange does not validate sustained clarification or conversation memory across multiple questions. Fresh-plan score changes after the path fix cannot be attributed causally to the fix.

Quality grades can remain high for plans that defer important decisions; inspect the saved criterion-level reasons before interpreting them as evidence of a strong design. Repeated grading measures judge variability, not actor-run variability or scientific validity.

This is a five-task adaptation with shortened public context, scoped researcher facts, current OpenHands/OpenRouter models and CPU exploration. It is not a reproduction of the paper’s full-workflow benchmark. No GPU experiment, task training or scientific execution was performed. Task dependencies and datasets were not installed or mounted.

## Plans, traces and judgments

- **JaxMARL:** [plan](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/initial_design.json), [actor events](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/actor_events.jsonl), [researcher conversation](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/researcher_history.json), [API requests/responses](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/api_calls.jsonl), [evaluation summary](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/initial_evaluation/summary.json), [first grading pair](../../runs/expbench/realistic-v3-live-20260922/neurips2024__97649__0/initial_evaluation/sample-1.json).
- **QuaRot:** [plan](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/initial_design.json), [actor events](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/actor_events.jsonl), [researcher conversation](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/researcher_history.json), [API requests/responses](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/api_calls.jsonl), [evaluation summary](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/initial_evaluation/summary.json), [first grading pair](../../runs/expbench/realistic-v3-live-20260922/neurips2024__94328__5/initial_evaluation/sample-1.json).
- **CycleNet:** [plan](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/initial_design.json), [actor events](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/actor_events.jsonl), [researcher conversation](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/researcher_history.json), [API requests/responses](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/api_calls.jsonl), [evaluation summary](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/initial_evaluation/summary.json), [first grading pair](../../runs/expbench/realistic-v3-workspace-fix-cyclenet-20260922/neurips2024__94391__7/initial_evaluation/sample-1.json).
- **MogaNet:** [plan](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/initial_design.json), [actor events](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/actor_events.jsonl), [researcher conversation](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/researcher_history.json), [API requests/responses](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/api_calls.jsonl), [evaluation summary](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/initial_evaluation/summary.json), [first grading pair](../../runs/expbench/realistic-v3-live-20260922/iclr2024__18447__7/initial_evaluation/sample-1.json).
- **SineNet:** [plan](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/initial_design.json), [actor events](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/actor_events.jsonl), [researcher conversation](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/researcher_history.json), [API requests/responses](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/api_calls.jsonl), [evaluation summary](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/initial_evaluation/summary.json), [first grading pair](../../runs/expbench/realistic-v3-workspace-fix-sinenet-20260922/iclr2024__18865__4/initial_evaluation/sample-1.json).
