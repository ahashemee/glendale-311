# data/cleaned/

Cleaned inputs for every analysis card. Load them with the standard load block in `docs/ANALYSIS_STANDARDS.md`; never edit them in place.

| File | What it is | Shape | In git? |
|---|---|---|---|
| `glendaleone_clean.csv` | GlendaleOne External Requests, cleaned: snake_case columns, request dates 2020-01-02 to 2026-08-05, district uppercase (blank where the City had `N/A` or `NONE`), `request_type_group` and quality flags added | 106,795 rows x 22 columns (24 MB) | **No** – download it (below) |
| `acs_demo_income_profile_clean.csv` | Esri Demographic and Income Profile, one row per Council District: Census 2020, Esri 2026 estimate and Esri 2031 projection | 6 rows x 284 columns | Yes |
| `acs_population_summary_clean.csv` | Esri ACS Population Summary, one row per Council District: ACS 2020–24 5-year estimates with `_moe` columns | 6 rows x 905 columns | Yes |
| `cleaning_log.md` | Written here by `src/clean_data.py` on every run | – | No – the reference copy is `docs/CLEANING_LOG.md` |

## Get `glendaleone_clean.csv`

Download it from the team Drive folder [DRIVE_FOLDER_LINK] into this folder, so the path is `data/cleaned/glendaleone_clean.csv`. It is git-ignored; never commit it.

## Regenerate everything instead

From the repo root:

```bash
python src/fetch_data.py && python src/clean_data.py
```

`fetch_data.py` downloads the two request CSVs into `data/raw/` from the City's live ArcGIS feed, and `clean_data.py` rebuilds all three files and the log here.

**Warning:** the live feed may differ from the 2026-08-06 extract that `docs/CLEANING_LOG.md` describes (the City keeps loading new rows, and Code Compliance was already 137 cases ahead by 2026-09-16). If your row counts differ from the log, use the Drive copy for card work so everyone's numbers match, and tell Ma'el.
