# Project skills

Claude Code loads every folder here that has a `SKILL.md` at its root. `CLAUDE.md` at the repo root says when to use each one. Where a library skill conflicts with `docs/ANALYSIS_STANDARDS.md` or `CLAUDE.md`, the repo's rules win.

## Written for this repo

- `work-task-card` – work a card in `docs/tasks/` end to end: branch, setup, steps, checks, outputs, findings.md, CHANGELOG line, PR.
- `log-change` – pre-commit ritual: clear notebook outputs, CHANGELOG line, findings updated, PR body filled.
- `update-findings` – fold a reviewed result into `docs/FINDINGS.md` and propose the Direction edit in `CLAUDE.md`.

## From nimrodfisher/data-analytics-skills

- `programmatic-eda` – systematic first look at a dataset: shape, types, nulls, distributions.
- `data-quality-audit` – completeness, consistency and validity checks on a table.
- `analysis-assumptions-log` – record the assumptions an analysis rests on.
- `analysis-documentation` – document an analysis so others can follow and reproduce it.
- `segmentation-analysis` – compare segments (here: districts) on a metric.
- `time-series-analysis` – trends, seasonality and breaks over time.
- `root-cause-investigation` – dig into an unexpected number before reporting it.
- `visualization-builder` – choose and build charts.
- `data-narrative-builder` – turn results into a storyline.
- `insight-synthesis` – combine several results into a few insights.
- `executive-summary-generator` – short summary for a non-technical audience.
- `analysis-qa-checklist` – self-QA before sharing results.
- `methodology-explainer` – explain methods in plain language.
- `technical-to-business-translator` – rephrase technical results for a city audience.
- `peer-review-template` – structure a review of a teammate's analysis.
- `context-packager` – package context to hand work to another person or session.

These 16 skills are copied unchanged from [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills) (the library groups them in category folders; they are flattened here so Claude Code can discover them). All credit for them goes to that project. The copy we took contained no LICENSE file `[uncertain: check the upstream repo before making this repo public]`.
