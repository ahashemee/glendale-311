# Glendale 311 & Code Compliance Equity Analysis

CIS 450 capstone project (ASU, Fall 2026) with the City of Glendale, Arizona's Office of Organizational Performance / Data team. Client contact: Stephen Gushue.

**The question:** are GlendaleOne (311) and Code Compliance requests distributed across the six Council Districts in proportion to population, and do the types of requests a district generates reflect who lives there?

## Team

| Name | Role |
|---|---|
| Ma'el Hashemee | Project Manager |
| Akshara Annu | Analyst |
| Shenoy Gladwin | Analyst |
| Sammy | Analyst |

## Repo layout

```
data/
  demographics/      12 Esri workbooks, 2 per Council District (committed, ~1 MB)
  council_districts.geojson   district polygons from the City's ArcGIS feed (committed)
  raw/               the two request CSVs (git-ignored; run src/fetch_data.py)
src/                 scripts and modules
notebooks/           exploratory notebooks (clear outputs before committing)
outputs/             charts, maps, and tables that go into deliverables
docs/                write-ups, meeting notes, data dictionary
```

## Getting started

```bash
git clone <this repo>
cd glendale-311-equity
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/fetch_data.py        # downloads ~165k request rows into data/raw/
```

`fetch_data.py` pulls straight from the City's public ArcGIS FeatureServer layers, so everyone gets the same extract without emailing 40 MB CSVs around. Use `--limit 500` for a quick smoke test.

## Data sources

| Dataset | Source | Notes |
|---|---|---|
| GlendaleOne External Requests | `services1.arcgis.com/.../GlendaleOne_External_Requests/FeatureServer/0` | ~108k points, 2019 onward, has `Council_District` |
| Code Compliance Cases | `services1.arcgis.com/.../GlendaleOne_Code_Compliance_Cases/FeatureServer/0` | ~56k points, district must be derived spatially |
| Council Districts | `services1.arcgis.com/.../Glendale_Council_Districts/FeatureServer/0` | 6 districts + a `NONE` catch-all polygon |
| Demographic & Income Profile / ACS Population Summary | Esri, provided by the City | one pair per district: Barrel, Cactus, Cholla, Ocotillo, Sahuaro, Yucca |

## Iteration 1 scope

Population only. Three questions, each per Council District: requests per 1,000 residents, most repeated request types, and resolution time against the City's response targets. Income, language, and housing tenure come in later iterations.

## Working agreements

- Branch per task (`feature/<short-name>`), open a PR, one teammate reviews.
- Never commit `data/raw/`; commit derived, small tables to `outputs/` if others need them.
- Keep notebooks for exploration; anything reused goes into `src/`.
