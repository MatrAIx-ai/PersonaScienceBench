# UMAP review gallery contract

- Purpose: inspect question-controlled examples of five persona interaction paths; no inferential claim based on projected cluster gaps or path lengths.
- Evidence: two equal panels per question, simulator and actor separately. Same trial-1 interactions and fixed persona colors; full observed paths and message access.
- Archetype: exploratory quantitative grid, not final manuscript artwork.
- Backend/export: Python Matplotlib, 11.7 × 6.5 inches, editable SVG and multipage PDF, minimum annotation font 7 pt. Numeric coordinates and projection provenance saved separately.
- Projection: Qwen3-Embedding-0.6B cached normalized embeddings; cosine UMAP jointly fit across five settings within each question and role. n_neighbors=min(15,N−1), min_dist=.1, 500 epochs, spectral init, random_state=42, transform_seed=42, n_jobs=1. No seed selection based on appearance.
- Coverage: 22 length-enriched cases and 110 complete interaction traces, replacing the preceding review gallery. Length selection requires ≥4 paired exchanges in at least one persona, prioritizing more qualifying personas. No model calls, trajectory truncation or persona exclusion within selected questions.
- Interpretation: trajectories connect observed rounds in time; connecting segments do not represent observed intermediate semantic states. UMAP coordinates and scales are local. No explained-variance or distance-effect-size claim.
- Validation: panel alignment at export, PDF geometry review, finite coordinates and exact node-message coverage. Main aggregate artifact hashes checked separately.
- Replacement scope: only the prior review gallery plots, projection records, coordinates and notebook previews. Raw traces, embeddings and main manuscript figures remain preserved.
