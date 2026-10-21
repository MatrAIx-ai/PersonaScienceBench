# Delivery status

complete_execution_with_unresolved_slots

Actor: Qwen 3.8 27B (medium); simulator: Qwen 3.8 27B (medium); judge: GPT-6 Astra (low).

- Mixed actor output cap: 12,288 tokens for slots finished before the repair passes, 16,384 for slots recovered afterwards (per-attempt cap in provenance/attempts.csv)
- Scientific-outcome repair: one --retry-missing pass re-ran every slot that finished without a submission; earlier attempts are retained in provenance/attempts.csv and the rerun is disclosed in README campaign notes
- Unresolved infrastructure_error slots remain unavailable (actor cap truncation, simulator schema failures, non-retryable gateway 400s); not scored
- Prepared task packages and evaluator references are not copied; restore from the tracked frozen preparation bundle astra-20260929-v1

See `delivery.json`, `README.md` and `bundle_manifest.json`.
