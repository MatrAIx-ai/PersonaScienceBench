# Sonnet 5 actor comparison

Ten fresh design-only episodes: five tasks per simulator, Sonnet 5 actor and judge, at most five independent processes in parallel. OpenHands, scoped researcher facts, repository masking and CPU sandbox are retained. No GPU training or full experiment execution was requested. No validation suite was run.

| Simulator | Actor | Judge | Mean reference coverage /100 | Scored |
| --- | --- | --- | ---: | ---: |
| sonnet5 | Sonnet 5 | Sonnet 5 | 79.5 | 5/5 |
| o3mini | Sonnet 5 | Sonnet 5 | 92.7 | 5/5 |

## Per-task reference coverage

| Task | Sonnet 5 simulator | o3-mini simulator |
| --- | ---: | ---: |
| JaxMARL | 33.3 | 93.3 |
| QuaRot | 93.3 | 95.0 |
| CycleNet | 82.7 | 100.0 |
| MogaNet | 90.0 | 85.0 |
| SineNet | 98.3 | 90.0 |

Coverage is the mean of three judgments of each submitted plan. Missing evaluations remain unscored; means use the explicit scored denominator. No added design-quality rubric is used.

## Interaction and integrity

| Simulator | Total questions | Episodes consulting simulator | Integrity passed | Integrity parse errors | Gated coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| sonnet5 | 21 | 4/5 | 5/5 | 0 | 79.5 |
| o3mini | 25 | 5/5 | 5/5 | 0 | 92.7 |

## Prior actor comparison

| Simulator | Prior o3-mini actor | New Sonnet 5 actor |
| --- | ---: | ---: |
| sonnet5 | 47.5 | 79.5 |
| o3mini | 54.0 | 92.7 |

Both columns use Sonnet 5 judging with the same compatibility message. These are separate actor trajectories, one episode per task and condition, not repeated-run estimates or a causal simulator ranking. The simulator publishes approved facts verbatim or an unknown response; it does not provide free-form research advice.

## Settings and artifacts

Actor limit: 20 steps, six researcher questions, 12,288 output tokens. Sonnet 5 simulator: 1,024 output tokens; o3-mini simulator: 4,096 tokens including medium reasoning. Sonnet 5 judge: 4,096 output tokens. No dollar cap. The original coverage and monitor system prompts are retained, with the nonempty user message "Apply the evaluation instructions above." required by Claude. Strict JSON parsing and original parse-failure gating are unchanged.

API-reported cost: $9.021928; calls with unknown billing: 0. Episode wall time: 13.2 minutes, excluding initial cache preparation and final artifact persistence.

[Run manifest](../../runs/expbench/sonnet5-actor-comparison-20260922/manifest.json), [process results](../../runs/expbench/sonnet5-actor-comparison-20260922/process_status.json), [workspace archive](../../runs/expbench/sonnet5-actor-comparison-20260922/workspaces.tar.gz).

Initial actor API requests match between simulator conditions after normalizing the SDK timestamp: {'neurips2024/97649/0': True, 'neurips2024/94328/5': True, 'neurips2024/94391/7': True, 'iclr2024/18447/7': True, 'iclr2024/18865/4': True}.

The JaxMARL episodes differ substantially in researcher usage. Consult the per-episode question counts in the JSON report before attributing the aggregate score gap to simulator capability. Simulator identity is not disclosed to the actor; divergent initial choices precede any researcher response.

- JaxMARL / sonnet5: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__97649__0/neurips2024__97649__0/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__97649__0/neurips2024__97649__0/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__97649__0/neurips2024__97649__0/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__97649__0/neurips2024__97649__0/api_calls.jsonl).
- QuaRot / sonnet5: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94328__5/neurips2024__94328__5/api_calls.jsonl).
- CycleNet / sonnet5: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94391__7/neurips2024__94391__7/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94391__7/neurips2024__94391__7/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94391__7/neurips2024__94391__7/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/neurips2024__94391__7/neurips2024__94391__7/api_calls.jsonl).
- MogaNet / sonnet5: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18447__7/iclr2024__18447__7/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18447__7/iclr2024__18447__7/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18447__7/iclr2024__18447__7/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18447__7/iclr2024__18447__7/api_calls.jsonl).
- SineNet / sonnet5: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18865__4/iclr2024__18865__4/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18865__4/iclr2024__18865__4/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18865__4/iclr2024__18865__4/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/sonnet5/iclr2024__18865__4/iclr2024__18865__4/api_calls.jsonl).
- JaxMARL / o3mini: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__97649__0/neurips2024__97649__0/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__97649__0/neurips2024__97649__0/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__97649__0/neurips2024__97649__0/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__97649__0/neurips2024__97649__0/api_calls.jsonl).
- QuaRot / o3mini: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94328__5/neurips2024__94328__5/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94328__5/neurips2024__94328__5/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94328__5/neurips2024__94328__5/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94328__5/neurips2024__94328__5/api_calls.jsonl).
- CycleNet / o3mini: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94391__7/neurips2024__94391__7/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94391__7/neurips2024__94391__7/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94391__7/neurips2024__94391__7/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/neurips2024__94391__7/neurips2024__94391__7/api_calls.jsonl).
- MogaNet / o3mini: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18447__7/iclr2024__18447__7/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18447__7/iclr2024__18447__7/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18447__7/iclr2024__18447__7/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18447__7/iclr2024__18447__7/api_calls.jsonl).
- SineNet / o3mini: status `completed`; [result](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18865__4/iclr2024__18865__4/result.json), [plan](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18865__4/iclr2024__18865__4/initial_design.json), [conversation](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18865__4/iclr2024__18865__4/researcher_history.json), [API trace](../../runs/expbench/sonnet5-actor-comparison-20260922/episodes/o3mini/iclr2024__18865__4/iclr2024__18865__4/api_calls.jsonl).
