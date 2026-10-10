# Figure contract

Question: How does per-call generated output differ between persona conditions and between actor and simulator?
Claim: Describe role-separated token use without treating verbosity as performance or causal persona influence.
Archetype: quantitative grid; two complementary panels, actor output and simulator output.
Backend: Python, using the existing nature-figure workflow. Style-only adaptation of the preceding two-panel renderer, with new units and both panels using the same per-call estimator.
Mapping: summary roles.actor/researcher, output_tokens_per_call, mean and ci95 in raw tokens; all six conditions in fixed order. No percentage transformation. Actor panel includes final specifications, explicitly disclosed.
Statistics: episode call mean, trial mean per case, then equal cases; pointwise study-cluster bootstrap CIs within SciConv mode. All available original scored episodes; one technical failure excluded, no repairs pooled.
Exports: 183 × 100 mm PDF/SVG with editable text; PNG/TIFF at 600 dpi. Minimum 5.5 pt. Comparable axes use shared final plot-area height and width, 1.5 pt tolerance. Numeric labels preserve CIs.
QA: source, alignment, text-size and collision audits followed by visual inspection. No journal-specific submission-compliance claim.
