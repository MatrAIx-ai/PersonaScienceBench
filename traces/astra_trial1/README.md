# Astra trial-1 interaction traces

**One trial per setting:** persona off, 155, 001, 003, and 046; 200 planned questions each.

These are saved historical Astra interactions, not new executions of the current SciConv protocol. All three roles use GPT-6 Astra with low reasoning. Sol and cancelled/aborted campaigns are excluded.

For each task/persona, an evaluable repaired endpoint is preferred, with the original retained when a repair is unevaluable. Endpoints are never selected by the highest score. Repairs belong to trial 1. This endpoint policy matches available-performance reporting; original-only behavioral/semantic figures can use different endpoints.

Only shared simulator–actor conversations are published. Scientific failures, zero scores, and missing submissions remain where a conversation was recorded; infrastructure-only/unusable slots have no transcript and remain visible in the [1,000-slot index](index.csv). Native scores are benchmark-specific and are not a common calibrated quality measure.

| Setting | Planned trial-1 slots | Published conversations | Unavailable |
|---|---:|---:|---:|
| [persona_off](persona_off/README.md) | 200 | 197 | 3 |
| [candidate_155](candidate_155/README.md) | 200 | 194 | 6 |
| [candidate_001](candidate_001/README.md) | 200 | 199 | 1 |
| [candidate_003](candidate_003/README.md) | 200 | 123 | 77 |
| [candidate_046](candidate_046/README.md) | 200 | 185 | 15 |

Reproduce offline from original local run artifacts with `python scripts/export_trial1_traces.py --output NEW_DIRECTORY`. The exporter refuses to overwrite an existing export. Known credential patterns are redacted from generated messages; original logs remain local and unchanged. [Export manifest](manifest.json) records input and output checksums.
