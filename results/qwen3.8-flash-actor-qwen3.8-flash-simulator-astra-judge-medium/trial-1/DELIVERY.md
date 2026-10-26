# Delivery status

complete_execution_with_unresolved_slots

Actor: Qwen 3.8 Flash (medium); simulator: Qwen 3.8 Flash (medium); judge: GPT-6 Astra (low).

- Protocol caps throughout (actor 12,288 output tokens); no cap raise and no scientific-outcome rerun were applied to this cohort
- Unresolved infrastructure_error slots remain unavailable (simulator tool-call protocol failures, reasoning-only completions without text, actor cap truncation, gateway timeouts); not scored
- Retry passes were interrupted twice by an operator-side disk-full condition; interrupted attempts are recorded in provenance/attempts.csv and were re-run
- Prepared task packages and evaluator references are not copied; restore from the tracked frozen preparation bundle astra-20260929-v1

See `delivery.json`, `README.md` and `bundle_manifest.json`.
