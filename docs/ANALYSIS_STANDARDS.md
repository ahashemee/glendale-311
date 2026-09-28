# Analysis standards

The shared rules every analysis in this repo follows. They let several people work in parallel without asking each other how something was done: same inputs, same filters, same file names, same checks. Task cards in `docs/tasks/` copy the parts they need; when a card and this file disagree, the card wins for that task and the difference goes in its `findings.md`.

Section numbers such as "6.6" point to `docs/PROJECT.md` section 6 unless stated otherwise.

## 1. Locations

| Item | Location (relative to the repo root) |
|---|---|
| Cleaned inputs | `data/cleaned/glendaleone_clean.csv`, `data/cleaned/acs_population_summary_clean.csv`, `data/cleaned/acs_demo_income_profile_clean.csv`. The two ACS files come with the clone; download `glendaleone_clean.csv` from the team Drive (see `data/cleaned/README.md`). **Never commit `data/raw/` or `glendaleone_clean.csv`.** |
| Notebooks | `notebooks/iterN_topic_owner.ipynb`, committed with outputs cleared |
| Outputs | `outputs/iterN/<topic>/`, holding CSV tables, PNG charts and `findings.md` |
| Task cards | `docs/tasks/iterN-NN-topic.md` |
| Branch | `feature/<short-name>`, e.g. `feature/iter2-propensity` |
| PR title | `[iterN-NN] topic – Owner` |

The Code Compliance district join (6.1) is not in the repo yet. It is shared through the team Drive when a card needs it.

## 2. Standard load block

Paste this verbatim at the top of every analysis notebook that uses the requests file:

```python
from pathlib import Path
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data" / "cleaned"
DISTRICTS = ["BARREL", "CACTUS", "CHOLLA", "OCOTILLO", "SAHUARO", "YUCCA"]
START, END = "2020-01-01", "2026-07-31"      # 79 full months
YEARS = 79 / 12

req = pd.read_csv(DATA / "glendaleone_clean.csv",
                  parse_dates=["request_date", "close_date"], low_memory=False)
req["district"] = req["district"].astype("string").str.strip().str.upper()
n_raw = len(req)
req_w = req[req["request_date"].between(START, END)]
n_window = len(req_w)
req_w = req_w[req_w["district"].isin(DISTRICTS)].copy()
n_final = len(req_w)
print(n_raw, n_window, n_final, n_window - n_final)   # last number = rows without a district
```

Expected: `n_raw` is 106,795. `n_window` is smaller, because August 2026 (178 rows) drops out. About 2.2% of the window has no district. If a number is far from these, stop and post in the group chat before going on.

## 3. Cleaning and definition rules

| Rule | Value | Why |
|---|---|---|
| Analysis window | `request_date` from 2020-01-01 to 2026-07-31 | December 2019 is the launch month, August 2026 has only 5 days, and the feed stopped 2026-08-06 (6.4; CLEANING_LOG 2.1) |
| District | Uppercase, trimmed, one of the 6 names; blank rows (were `N/A` or `NONE`) excluded, and the excluded count reported | 6.6, 6.13 |
| Missing values | NULL, `''` and `'N/A'` all count as missing | 6.6, 6.10 |
| Population denominator | Primary `dip_summary_total_population_2026` (Esri 2026); sensitivity `acs_total_population` (ACS 2020–24) | 6.8 (YUCCA differs by 24%) |
| Rate | Requests per 1,000 residents per year = count / YEARS / population x 1000 | Comparable across windows |
| Type grouping | `request_type_group` (17 groups) for type-mix control | 6.12 |
| Time-to-close | `(close_date - request_date).dt.days` on rows with `status == "Closed"`, a non-null `close_date` and `flag_close_before_request == False` | Dates are date-only UTC, so a same-day close is 0 (section 9; CLEANING_LOG 2) |
| Percent scale | All `_pct` columns in the demographic files are 0–100 | CLEANING_LOG 1.2 |
| Median household income | `dip_hhinc_median_household_income_2026` only; never the `dip_trend_..._rate_` columns | 6.7 |
| n = 6 districts | District-level correlations are descriptive: report rho, not "significant". No causal verbs | Section 8 |
| Section 7 numbers | Never copied into a deliverable; recompute from code | Section 7 banner |

Decisions behind these rules are dated in `docs/DECISIONS.md`.

## 4. Output schema

- Tables are long format with snake_case columns, `district` first, one row per district or per district x category, and an `n` column wherever a statistic is computed.
- Every CSV named on a card has its exact column list on the card. Anyone should be able to build against a fake 6-row table before the real one exists.
- `findings.md` holds three findings (each with the number and the comparison), a caveats list, and the **filter log** (`n_raw`, `n_window`, `n_final`, excluded, plus any later filter such as `n_closed`).

## 5. EDA checks

Run the ones that apply and tick them in the PR:

- [ ] State the grain: one row = one GlendaleOne request (or one district, for the demographic files).
- [ ] Record row counts after each filter (the filter log). The excluded counts must add up to the difference.
- [ ] Confirm dtypes: the date columns are datetime, `district` is a string and the flags are bool.
- [ ] Count nulls in every column you use, and treat NULL, `''` and `'N/A'` alike.
- [ ] Check `request_number` is unique: `req_w["request_number"].is_unique` is True.
- [ ] Check ranges: dates fall inside the window, `days_to_close` is at least 0, and rates are positive.
- [ ] Check the category set: exactly the 6 district names, and no others.
- [ ] Report the mean alongside the median and IQR. If they disagree a lot, the median leads.
- [ ] Flag outliers (IQR fences, or anything over 365 days), but **do not delete them**. Show one result with and without them.
- [ ] Check time coverage: count rows per month and confirm there are no empty months in the window.
- [ ] Reconcile: the per-district counts sum to `n_final`.
- [ ] Keep raw and cleaned files read-only. Write only to your outputs folder.

## 6. Statistics rules

- Write the planned test in the notebook **before** running it. Changing the test after seeing the result needs a note explaining why.
- Tests used in this project:

| Question shape | Test (scipy.stats) | Effect size to report | Note |
|---|---|---|---|
| Do district counts match population shares? | `chisquare(obs, f_exp=exp)` | Cohen's w = sqrt(chi2 / N) | Also report standardized residuals (obs - exp) / sqrt(exp) per district |
| Does a yes/no outcome differ by district? | `chi2_contingency(crosstab)` | Cramér's V = sqrt(chi2 / (N x (min(rows, cols) - 1))) | 6 x 2 table |
| Does a skewed continuous measure (days) differ by district? | `kruskal(*groups)` | epsilon squared = H / (N - 1) | Days to close are heavily skewed, so ANOVA is not appropriate |
| District rate vs a district covariate | `spearmanr(x, y)` | rho itself | n = 6: report rho as descriptive and skip the p-value |

- With about 100,000 rows, nearly every p-value will be tiny. **Lead with the effect size**; the p-value only says the effect isn't zero. Report p exactly (`p < .001` below .001).
- Running more than 3 pairwise tests? Apply the Holm correction (`statsmodels.stats.multitest.multipletests(p, method="holm")`) and say so.
- Label anything you found by looking around, rather than planned, as "exploratory".
- Never use causal words (causes, drives, because of) for district patterns. Use "is associated with", "co-varies with" or "lines up with".

## 7. Chart standard

```python
import seaborn as sns, matplotlib.pyplot as plt
sns.set_theme(style="whitegrid", context="talk")        # seaborn 0.13.2
BLUE = "#2a78d6"                                        # default single hue
DISTRICT_COLORS = {"BARREL": "#2a78d6", "CACTUS": "#eb6834", "CHOLLA": "#1baf7a",
                   "OCOTILLO": "#eda100", "SAHUARO": "#e87ba4", "YUCCA": "#008300"}
```

- When district is on an axis, use one hue (`BLUE`), because color would repeat the axis. Use `DISTRICT_COLORS` only when color is the only thing identifying the district (lines on one panel). Aqua, yellow and magenta are under 3:1 contrast on white, so those charts need direct labels on the lines.
- Six districts on one line chart is too many. Use small multiples with the same y-axis instead.
- The title states the finding, not the metric: "[District A] files [x]x the requests per resident of [District B]", with the real names and numbers from your own output. The subtitle or axis label carries the window, the denominator and the units.
- Bars start at zero. There is never a dual y-axis and never 3D. Label values selectively (the extremes and the reference line), not every bar.
- Add a source note under the chart: "Source: City of Glendale GlendaleOne External Requests (extract loaded 2026-08-06); Esri 2026 population."
- Save as `fig.savefig(OUT / "name.png", dpi=200, bbox_inches="tight")` at `figsize=(12, 6.75)` (16:9, for the HTML page).
- Use keyword arguments only, and `errorbar=` instead of `ci=`. To color categories, pass `hue=` along with `legend=False`.

Chart checks:

- [ ] The title states the finding. The subtitle or axis carries the window, the denominator and the units.
- [ ] Bars start at zero, there is no dual axis and no 3D, and the grid is light.
- [ ] District on an axis gets one hue. Six districts over time go in small multiples with the same y-axis.
- [ ] Values are labeled selectively (the extremes and the reference line).
- [ ] The source note is under the chart. The PNG is 200 dpi at 12 x 6.75 in.
- [ ] Legibility test: someone who hasn't seen the notebook can say the main point in 5 seconds.

## 8. QA checklist before a PR (tick in the PR description)

- [ ] **Source and freshness:** the file names and the "extract loaded 2026-08-06" date are stated in findings.md.
- [ ] **Filters:** the window, the district filter and the closed filter match section 3 exactly.
- [ ] **Denominators:** every rate names its population column, and the sensitivity rerun is included where the card asks for one.
- [ ] **Partial periods:** December 2019 and August 2026 are excluded.
- [ ] **Sums:** the parts add up to the total, and the percentages add up to about 100.
- [ ] **Magnitude:** every rate and median is plausible (no negatives, no rate above 1,000 per 1,000 per year without a note).
- [ ] **Two ways:** one headline number was recomputed a second way (for example with `value_counts` instead of `groupby`), and the two match.
- [ ] **Charts:** the chart checks in section 7 are done.
- [ ] **Caveats:** findings.md lists the exclusions, the n = 6 limit where relevant, and "association, not cause".
- [ ] **Reproducible:** Restart and Run All works on a fresh clone plus the Drive files.

## 9. Gotcha library

| Key | Rule | Source |
|---|---|---|
| G-district | About 2.2% of requests have no district (they were `N/A` or `NONE`). Exclude them from per-district numbers and report how many you excluded. | 6.6 |
| G-window | Use requests from 2020-01-01 to 2026-07-31 only. December 2019 is the launch month and August 2026 has only 5 days. | 6.4 |
| G-stale | The City's request feed stopped updating on 2026-08-06. Say "as of the 2026-08-06 extract". | 6.4 |
| G-denominator | Esri 2026 and ACS populations disagree, most of all for YUCCA (53,147 vs 42,931). Lead with Esri 2026 and rerun with ACS. | 6.8 |
| G-income | Take median household income from `dip_hhinc_median_household_income_2026`. The `dip_trend_median_household_income_rate_*` columns are growth rates, not dollars. | 6.7 |
| G-geo | Request coordinates are rounded to the block. District is the finest reliable geography, so do not map points. | 6.2 |
| G-dates | Dates are date-only and in UTC. A same-day close is 0 days, and a late-evening request can land on the next day. | 9 |
| G-closed | 99.6% of requests are closed, so there's nothing useful to analyze about open requests. Use closed rows only for timing. | 6.11 |
| G-flags | Drop the 1 row with `flag_close_before_request` True. Do not "fix" it. | CLEANING_LOG 2.5 |
| G-types | Use `request_type_group` (17 groups) for type mix. Trash/Recycle Services is about 48% of all requests and swamps everything else, so show a version without it where totals matter. | 6.12, 7 |
| G-codecases | Code Compliance cases have no district until the spatial join is done and shared. Don't use `Code_Compliance_Cases_GlendaleOne.csv` for per-district work before then. | 6.1 |
| G-citations | Never `sum()` `CriminalCitations`, `CivilCitations` or the other citation columns. They are reference numbers. | 6.9 |
| G-2025dip | Code case volume in 2025 is probably a reporting gap, not a trend. Don't read it as one. | 6.5 |
| G-escalation | The City's response targets (the escalations table) are not downloaded yet. Don't call anything "on target" or "late vs target". | 6.12; DELIVERABLE_IDEAS 3 |
| G-section7 | Numbers in PROJECT.md section 7 are unvalidated. Never copy them; compute your own. | 7 |
| G-pct | Demographic `_pct` columns are on a 0–100 scale. | CLEANING_LOG 1.2 |
| G-lang | The ACS language columns for ages 18–64 have long nested names. Use `acs_lang_18_64_speak_spanish_speak_english_not_well_pct` and confirm its denominator before citing it. `[uncertain]` | CLEANING_LOG 1.2 |
| G-moe | ACS estimates carry margins of error (`_moe` columns). If two districts differ by less than their MOEs, call them "similar". | CLEANING_LOG 5 |
| G-pii | Never pull or publish names, emails or phone numbers from any City layer. | 6.15 |

## 10. Git flow

1. `git checkout main && git pull`, then `git checkout -b feature/<short-name>`.
2. Work in the notebook. Commit the notebook with outputs cleared (`jupyter nbconvert --clear-output --inplace notebooks/<file>.ipynb`), plus everything in `outputs/iterN/<topic>/`, plus a `CHANGELOG.md` line.
3. Open a **draft PR** by the card's draft date, fill in the template and assign the named reviewer.
4. Mark the PR ready when every definition-of-done box is ticked. Ma'el merges.

Never commit `data/raw/` or `data/cleaned/glendaleone_clean.csv`; `.gitignore` already blocks both. Full details are in `CONTRIBUTING.md`.
