<!-- Title: [iterN-NN] topic – Owner -->

**Card:** [iterN-NN] (`docs/tasks/iterN-NN-topic.md`)
**Reviewer:** @

## What changed

-

## Why

-

## Files touched

-

## Notation

- [ ] I added a line to `CHANGELOG.md`: `- YYYY-MM-DD (Name) [iterN-NN] what changed (path) – why`
- [ ] `findings.md` for this card is written or updated (findings, caveats, filter log), and `docs/FINDINGS.md` is updated if a finding is ready
- [ ] Notebook outputs are cleared (`jupyter nbconvert --clear-output --inplace notebooks/<file>.ipynb`)
- [ ] No file from `data/raw/` and no `glendaleone_clean.csv` is in this PR

## QA checklist (`docs/ANALYSIS_STANDARDS.md` section 8)

- [ ] **Source and freshness:** the file names and the "extract loaded 2026-08-06" date are stated in findings.md.
- [ ] **Filters:** the window, the district filter and the closed filter match the standards exactly.
- [ ] **Denominators:** every rate names its population column, and the sensitivity rerun is included where the card asks for one.
- [ ] **Partial periods:** December 2019 and August 2026 are excluded.
- [ ] **Sums:** the parts add up to the total, and the percentages add up to about 100.
- [ ] **Magnitude:** every rate and median is plausible (no negatives, no rate above 1,000 per 1,000 per year without a note).
- [ ] **Two ways:** one headline number was recomputed a second way, and the two match.
- [ ] **Charts:** the chart checks are done (finding in the title, bars from zero, source note, 200 dpi).
- [ ] **Caveats:** findings.md lists the exclusions, the n = 6 limit where relevant, and "association, not cause".
- [ ] **Reproducible:** Restart and Run All works on a fresh clone plus the Drive files.
