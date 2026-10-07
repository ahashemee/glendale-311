# Decision log

Dated record of decisions that shape how the team works and how numbers are computed. Newest first. To change a decision, add a new dated row that supersedes the old one (say which), open a PR, and update any task file or standard it affects. Never edit an old row except to mark it superseded.

| Date | Decision | Why / source | Status |
|---|---|---|---|
| 2026-09-28 | The repo `glendale-311-equity` is the team's working space: docs, tasks, code, outputs, a `CHANGELOG.md` line on every PR, and CI checks on `main`. | Every change gets notated and reviewed | Active |
| 2026-09-25 | **Iteration 2** is an in-class presentation on **Mon 2026-10-19**. Scope: the reporting-propensity gap and time-to-close by district. District request signatures and the Code Compliance comparison wait for the final iteration. | Ma'el | Active |
| 2026-09-25 | Iteration 2 measures time-to-close **controlled for request type** rather than against the City's response targets, because the targets table (GlendaleOne Escalations) is not downloaded. The talk says so. Never write "on target" or "late". | Ma'el; PROJECT.md 6.12 | Active |
| 2026-09-25 | Presentations are HTML pages from Iteration 2 on. | Ma'el | Active |
| 2026-09-25 | The repo is **private** for now; it may go public later. | Ma'el | Active |
| 2026-09-29 | Tasks are one short markdown file per person in `docs/tasks/`: tasks, due dates and what Ma'el is looking for; the how stays in `docs/ANALYSIS_STANDARDS.md`. Supersedes the 2026-09-25 task-card row. Reviews of the analysis PRs go to Ma'el; peers comment during the share-out. | Ma'el | Active |
| 2026-09-29 | Iteration 2 runs in stages with a team share-out (Mon 10/5), a short call (Wed 10/7) and Ma'el's synthesis (Thu 10/8) before the final stretch. | Ma'el | Active |
| 2026-09-25 | Task cards are markdown files in `docs/tasks/`. Ma'el posts the ping in the group chat himself. | Ma'el | Superseded 2026-09-29 |
| 2026-09-25 | Cleaned data is shared through the team Google Drive and is git-ignored (except the two small ACS tables). The raw request CSVs are **never** committed. | Ma'el | Active |
| 2026-09-25 | One branch per task (`feature/<short-name>`), a PR, and one named reviewer. Every task has exactly one owner and one reviewer. Ma'el merges. | Ma'el | Active |
| 2026-09-25 | Async check-ins every Mon and Thu in the group chat: Progress / Plans / Problems. | Ma'el | Active |
| 2026-09-25 | A missed deadline gets 24 h grace; after that the remaining work is reassigned. | Ma'el | Active |
| 2026-09-25 | **Analysis window:** requests from 2020-01-01 to 2026-07-31 (79 full months). December 2019 is the launch month and August 2026 has only 5 days. Any side-by-side volume comparison with Code Compliance is truncated to a common window, which PROJECT.md 6.4 recommends as 2020-01-01 to 2026-06-30. | PROJECT.md 6.4; ANALYSIS_STANDARDS section 3 | Active |
| 2026-09-25 | **Population denominator:** lead with Esri 2026 (`dip_summary_total_population_2026`), contemporaneous with the request data; rerun with ACS 2020–24 (`acs_total_population`) as a sensitivity check. Every per-capita claim names its denominator. | PROJECT.md 6.8 | Active |
| 2026-09-25 | **Unassigned districts:** exclude requests whose district is `'N/A'` (or NULL / `''`) or `NONE` from per-district analysis, and report the excluded count in a footnote. | PROJECT.md 6.6 | Active |
