# Haiku actor / Opus simulator interaction traces

`shared-events.jsonl` contains one sanitized controller-level shared conversation record for each of the 1,000 frozen source episodes. It includes researcher decisions, actor handoffs, clarification exchanges, submissions, and termination events. `shared-events-index.csv` maps each task/persona slot to its JSONL line and source checksum.

These traces are inherited unchanged from the original campaign. The Astra regrade happened after submission and did not rerun or modify the Haiku actor or Opus researcher simulator. Raw actor command output, system prompts, private researcher state, evaluator references, and API payloads remain excluded.
