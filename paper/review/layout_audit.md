# Whole-paper formatting pass — 2026-10-07

Reviewed the original 32-page PDF and the revised 29-page PDF as rendered contact sheets, with enlarged checks of tables, captions, equations, wrapped figures, prompt frames, and the final transcript pages. The main-text font size and figure asset files are unchanged.

## Corrections

- Standardized float spacing and reduced aggressive negative spacing below displays. Kept the domain table and interaction-metric figure wrapped, with their existing widths.
- Kept the discussion figure before the Conclusion, reserved enough space for the Conclusion, and prevented isolated paragraph lines and stranded Results headings.
- Moved the algorithm caption below the pseudocode and its notation key; table, figure, and algorithm captions use italic type below their displays.
- Completed the domain-table average definition and corrected its domain-note alignment and size. Updated the generator's formatting to match.
- Removed the visible editing comment in Section 3.2 and fixed the merged words “sametime”. Scientific claims and numerical results were not revised.
- Converted prompt/profile frames to breakable boxes with continuation labels. Kept profile field headings with their descriptions and removed the unnecessary page break before the full interactions.
- Added continuation labels and consistent spacing to transcript frames. Kept each case heading with the start of its conversation. Updated the transcript generator and regenerated all 23 events and 59 fields from the archived snapshots.
- Protected proper names and acronyms in bibliography titles and used ragged-right bibliography entries to avoid stretched URL lines.
- Removed the ignored `inputenc` package and the negative listing line skip. Bundled the public-domain `placeins` 2.2 package from CTAN to preserve offline compilation of the float barrier.

## Validation

- Compiled with XeTeX through Tectonic; no compilation errors, undefined references/citations, missing glyphs, overfull boxes, or oversized floats.
- Verified six figure captions, five table captions, the algorithm caption, and Conclusion-before-Limitations ordering.
- All figure files match the pre-edit SHA-256 hashes. Performance means and confidence intervals are unchanged.
- Prompt and persona-profile contents match after removing formatting commands. Every generated conversation payload matches the previous export exactly; source snapshot hashes are checked by the generator.
- Bibliography changes add case-protection braces only; authors, titles, identifiers, URLs, and publication metadata are unchanged.
- Five minor underfull-box messages remain around narrow wrapped text/captions; the corresponding rendered pages were checked. Tectonic's pre-existing internal bibliography-rerun warning remains, with all references resolved.

The final PDF is `main.pdf`. Temporary before/after snapshots and rendered inspection pages are under `/tmp/paper-layout-before`, `/tmp/paper-layout-after`, and `/tmp/paper-layout-final`.
