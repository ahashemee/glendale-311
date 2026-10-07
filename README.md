# Glendale 311 & Code Compliance Equity Analysis

CIS 450 capstone project (ASU, Fall 2026) with the City of Glendale, Arizona's Office of Organizational Performance / Data team. Client contact: Stephen Gushue.

**The question:** are GlendaleOne (311) and Code Compliance requests distributed across the six Council Districts in proportion to population, and do the types of requests a district generates reflect who lives there?

## Team

| Name | Role |
|---|---|
| Ma'el Hashemee | Project Manager |
| Akshara Annu | Analyst |
| Shenoy Gladwin | Analyst |
| Shamie Reyes | Analyst |

## Where we are

**Iteration 2** – in-class presentation on **Mon 2026-10-19** (HTML page). Scope: the reporting-propensity gap (are request counts in line with each district's population, and what do the rates line up with?) and time-to-close by district, controlled for request type. Code Compliance and district request signatures come in the final iteration.

- Dates: [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Your tasks, due dates and what's expected: [`docs/tasks/`](docs/tasks/README.md)

## Start here

- [`CLAUDE.md`](CLAUDE.md) – the brief every Claude Code session reads first (questions, current direction, rules, data gotchas, skills).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) – branch, PR and review flow, Mon/Thu check-ins, how to notate a change.
- [`CHANGELOG.md`](CHANGELOG.md) – one line per change; every PR adds one.
- [`docs/`](docs/) – `PROJECT.md` (source of truth), `DATA_DICTIONARY.md`, `ANALYSIS_STANDARDS.md`, `DECISIONS.md`, `FINDINGS.md` and the rest.

## Repo layout

```
CLAUDE.md, CONTRIBUTING.md, CHANGELOG.md
.claude/skills/      project skills for Claude Code
.github/             PR template and CI checks (CHANGELOG line, clean notebooks)
data/
  demographics/      12 Esri workbooks, 2 per Council District (committed, ~1 MB)
  council_districts.geojson   district polygons from the City's ArcGIS feed (committed)
  raw/               the two request CSVs (git-ignored; run src/fetch_data.py)
  cleaned/           cleaned inputs; glendaleone_clean.csv comes from the team Drive (git-ignored)
src/                 fetch_data.py, clean_data.py, landscape/ (data-landscape harvest)
notebooks/           iterN_topic_owner.ipynb (clear outputs before committing)
outputs/             iterN/<topic>/: charts, tables and findings.md for deliverables
docs/                project brief, standards, decisions, findings, roadmap, task files
```

## Getting started

```bash
git clone <this repo>
cd glendale-311-equity
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then download `glendaleone_clean.csv` from the team Drive folder [DRIVE_FOLDER_LINK] into `data/cleaned/` (details in [`data/cleaned/README.md`](data/cleaned/README.md)). The two small ACS tables are already in the repo. That is all a task needs.

To rebuild the raw data and the cleaned files yourself instead:

```bash
python src/fetch_data.py        # downloads ~165k request rows into data/raw/
python src/clean_data.py        # rebuilds data/cleaned/ from data/raw/ and data/demographics/
```

`fetch_data.py` pulls straight from the City's public ArcGIS FeatureServer layers, so everyone gets the same extract without emailing 40 MB CSVs around. Use `--limit 500` for a quick smoke test. The live feed may differ from the 2026-08-06 extract the docs were written against, so use the Drive copy for task work.

## Data sources

| Dataset | Source | Notes |
|---|---|---|
| GlendaleOne External Requests | `services1.arcgis.com/.../GlendaleOne_External_Requests/FeatureServer/0` | ~108k points, 2019 onward, has `Council_District` |
| Code Compliance Cases | `services1.arcgis.com/.../GlendaleOne_Code_Compliance_Cases/FeatureServer/0` | ~56k points, district must be derived spatially |
| Council Districts | `services1.arcgis.com/.../Glendale_Council_Districts/FeatureServer/0` | 6 districts + a `NONE` catch-all polygon |
| Demographic & Income Profile / ACS Population Summary | Esri, provided by the City | one pair per district: Barrel, Cactus, Cholla, Ocotillo, Sahuaro, Yucca |

## Working agreements

- Branch per task (`feature/<short-name>`), open a PR, one named reviewer; Ma'el merges. Full flow in [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Never commit `data/raw/` or `glendaleone_clean.csv`; commit derived, small tables to `outputs/` if others need them.
- Keep notebooks for exploration; anything reused goes into `src/`.
- Questions go to Ma'el in the group chat.
