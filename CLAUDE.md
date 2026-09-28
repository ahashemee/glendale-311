# CLAUDE.md – glendale-311-equity

Brief for any Claude Code session in this repo. Read it in full before doing anything.

## What this repo is

CIS 450 capstone (ASU, Fall 2026) for the City of Glendale, Arizona. We analyse GlendaleOne (311) and Code Compliance requests across the six Council Districts (BARREL, CACTUS, CHOLLA, OCOTILLO, SAHUARO, YUCCA). Team: Ma'el Hashemee (PM), Akshara Annu, Shenoy Gladwin, Shamie Reyes. The client's five questions, verbatim (`docs/PROJECT.md` section 2):

1. **Are the request counts distributed equitably based on Council District populations?**
2. **What are the top 10 (or n) request types differing between GlendaleOne requests and code requests?**
3. **What are the probabilities of certain request types coming from each district?**
4. **What are the similarities and disparities in requests counts, types per each district?**
5. **Other items of interest that the city may not be seeing.**

## Direction (living)

*Last updated: 2026-09-28.* This section is changed by PR whenever a finding shifts the story; it is never treated as fixed. Use the `update-findings` skill to propose the edit.

- **Current iteration:** Iteration 2, in-class presentation **Mon 2026-10-19** (HTML page).
- **Scope:** the reporting-propensity gap (Q1: requests per resident vs population share and district covariates) and time-to-close by district, controlled for request type. Code Compliance and district request signatures wait for the final iteration.
- **Working hypotheses** (from `docs/FINDINGS.md`; none validated yet):
  - H1 `[unvalidated]` Request volume per resident may line up with who reports (income, internet, language, rent burden) more than with need.
  - H2 `[unvalidated]` The equity signal may sit in the mix of request types, not the volume.
  - H3 `[unvalidated]` District gaps in days-to-close may shrink once request type is controlled.
- **Validated findings:** none yet. `docs/PROJECT.md` section 7 figures are orientation only.

## Read first, in this order

1. `CLAUDE.md` (this file).
2. `docs/PROJECT.md` sections 2 (questions), 6 (data gotchas) and 9 (conventions).
3. `docs/DATA_DICTIONARY.md` (where it conflicts with PROJECT.md section 6, PROJECT.md wins).
4. `docs/ANALYSIS_STANDARDS.md` (load block, rules, checks, chart standard).
5. The card in `docs/tasks/` you are working on.

Never re-profile raw data that the docs already describe. If the docs answer it, use the docs.

## Repo map

| Path | What |
|---|---|
| `docs/PROJECT.md` | Source of truth: client, questions, data inventory, gotchas, methods |
| `docs/ANALYSIS_STANDARDS.md` | Load block, definitions, EDA / stats / chart / QA checks, gotcha library |
| `docs/DECISIONS.md` · `docs/FINDINGS.md` · `docs/ROADMAP.md` | Dated decisions · living findings · dates, Gantt, check-ins, risks |
| `docs/tasks/` | Task cards and their status table |
| `docs/CLEANING_LOG.md` · `docs/DATA_LANDSCAPE.md` · `docs/iteration1/` | What cleaning did · every other City dataset · Iteration 1 proposal and deck |
| `data/cleaned/` | Cleaned inputs; `glendaleone_clean.csv` comes from the team Drive (git-ignored) |
| `data/raw/` | Raw request CSVs from `src/fetch_data.py` (git-ignored) |
| `data/demographics/`, `data/council_districts.geojson` | Esri workbooks and district polygons |
| `src/` | `fetch_data.py`, `clean_data.py`, `landscape/` (data-landscape harvest) |
| `notebooks/` | `iterN_topic_owner.ipynb` |
| `outputs/iterN/<topic>/` | CSV tables, PNG charts, `findings.md` |
| `.claude/skills/` | Project skills (below) |

## How work flows

1. One card, one owner, one reviewer. Branch `feature/<short-name>` off an up-to-date `main`.
2. Work in `notebooks/` and write only to your card's `outputs/iterN/<topic>/`.
3. Open a draft PR by the card's draft date using `.github/PULL_REQUEST_TEMPLATE.md`, and assign the named reviewer. CI checks the CHANGELOG line and clean notebooks. Ma'el merges.
4. Check-ins every Mon and Thu in the group chat: Progress / Plans / Problems. A missed deadline gets 24 h grace, then the work is reassigned. Details: `CONTRIBUTING.md`.

## Notation rules (MUST)

- Every PR MUST add a `CHANGELOG.md` line: `- YYYY-MM-DD (Name) [iterN-NN] what changed (path) – why`.
- Every analysis MUST write `outputs/iterN/<topic>/findings.md` with its findings, caveats and a filter log (`n_raw`, `n_window`, `n_final`, excluded).
- Notebook outputs MUST be cleared before commit: `jupyter nbconvert --clear-output --inplace notebooks/<file>.ipynb`.
- Any number that reaches a slide MUST be recomputed from code in this repo, never copied from `docs/PROJECT.md` section 7.
- Unverified facts MUST carry `[uncertain]`.
- Language MUST be associative ("is associated with", "lines up with"), never causal ("causes", "drives", "because of").
- In anything written for this repo, an en dash (–) goes where an em dash would; everywhere else use a plain hyphen. No em dashes.
- MUST NOT commit `data/raw/` or the 24 MB `data/cleaned/glendaleone_clean.csv`.
- MUST NOT pull or publish the personal contact columns in `docs/PROJECT.md` 6.15: Water Distribution Survey123 `requesters_name` and email; Parks `pocfirstname`, `pocphone`, `pocemail`; registered-neighborhood representative name, phone and email.

## Top data gotchas (`docs/PROJECT.md` section numbers)

- 6.1 Code Compliance `District` is empty on every row; no per-district code work until the spatial join is shared.
- 6.2 Request coordinates are block-anonymized; district is the finest reliable geography.
- 6.3 Requests and code cases share no join key; compare them as populations, never merge on ID.
- 6.4 Feeds stop on different dates; use 2020-01-01 to 2026-07-31 for requests and a common window for side-by-side comparisons.
- 6.5 The 2025 code-case dip is probably a reporting gap, not a trend.
- 6.6 About 2.2% of requests have no district (`'N/A'` or `NONE`); exclude and report the count.
- 6.7 "Median Household Income" appears twice in the Esri workbooks; use `dip_hhinc_median_household_income_2026`.
- 6.8 Esri 2026 and ACS populations disagree (YUCCA most); lead with Esri 2026, rerun with ACS.
- 6.9 Code citation columns hold reference numbers; never `sum()` them.
- 6.10 NULL, `''` and `'N/A'` all mean missing; filter non-Glendale code cases.
- 6.11 99.6% of requests are closed; analyse cycle time, not open cases.
- 6.12 Trim request-type names before joining; the escalation targets are not downloaded, so never say "on target" or "late".
- 6.13 District names are UPPERCASE here; uppercase and trim before any join.

## Skills in `.claude/skills/`

Project skills:
- `work-task-card` – start or resume a card in `docs/tasks/`: branch, setup, steps, checks, outputs, PR.
- `log-change` – before every commit or PR: clear notebooks, CHANGELOG line, findings, PR body.
- `update-findings` – fold a merged result into `docs/FINDINGS.md` and propose the Direction edit above.

Analytics skills (from nimrodfisher/data-analytics-skills):
- `programmatic-eda`, `data-quality-audit` – first look at a table, null and range checks (only where the docs don't already cover it).
- `analysis-assumptions-log`, `analysis-documentation`, `methodology-explainer` – record assumptions, write up methods for `findings.md`.
- `segmentation-analysis`, `time-series-analysis`, `root-cause-investigation` – district comparisons, monthly trends, digging into an odd number.
- `visualization-builder` – charts (always within the chart standard in `docs/ANALYSIS_STANDARDS.md`).
- `data-narrative-builder`, `insight-synthesis`, `executive-summary-generator`, `technical-to-business-translator` – storyline and slide copy for a city audience.
- `analysis-qa-checklist`, `peer-review-template` – self-QA before a PR, and reviewing a teammate's PR.
- `context-packager` – hand work to another person or session.

Where a library skill conflicts with `docs/ANALYSIS_STANDARDS.md` or this file, this repo's rules win.

## Questions

Questions go to Ma'el in the group chat. Asking early is the right move.
