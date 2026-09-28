### Card iter2-01 – Reporting-propensity gap – Shamie

**File:** `docs/tasks/iter2-01-propensity-gap.md`
**Owner:** Shamie · **Reviewer:** Ma'el · **Complexity:** C3 · **Estimate:** 6.3 h (4–10 h)
**Start:** Sun 2026-09-27 · **First check-in:** Thu 2026-10-01 (post `q1_rates_by_district.csv`, first 3 columns)
**Draft PR:** Thu 2026-10-08 · **Due (PR ready):** Sun 2026-10-11 23:59 · **Hard or soft:** hard (the presentation is Mon 2026-10-19)
**Questions:** Ma'el in the group chat, any time. Asking early is the right move.

**Why this matters.** The City's first question is "Are the request counts distributed equitably based on Council District populations?" Our Iteration 1 idea is that raw volume may track *who reports*, not *who needs service*. This card tests whether counts match population shares, and whether rates line up with income, renting, internet access and language. It is the headline of the Iteration 2 talk.

**Outcome.** Per-district request rates under two population sources, a goodness-of-fit test with an effect size, a covariate comparison, and 2 charts, in `outputs/iter2/propensity/`.

**Autonomy.**
- You decide and then tell Ma'el: chart styling within the rules below, and findings wording.
- Propose first: any change to the window, filters, denominators or covariates.
- Ask before doing: anything outside `outputs/iter2/propensity/`.

**Inputs** (relative to the repo root; download from Drive "City of Glendale" into `data/cleaned/`)
- `data/cleaned/glendaleone_clean.csv`: 106,795 requests x 22 columns. Uses `request_date`, `district`, `request_type_group`.
- `data/cleaned/acs_demo_income_profile_clean.csv`: 6 districts x 284 columns (Census 2020 + Esri 2026/2031).
- `data/cleaned/acs_population_summary_clean.csv`: 6 districts x 905 columns (ACS 2020–24, with `_moe` columns).

**Setup**
1. `git checkout main && git pull`, then `git checkout -b feature/iter2-propensity`.
2. `pip install pandas scipy "seaborn==0.13.2" matplotlib`
3. Create `notebooks/iter2_propensity_shamie.ipynb` and the folder `outputs/iter2/propensity/`.

**Steps**
1. **Load requests.** Paste this block:
   ```python
   from pathlib import Path
   import pandas as pd
   ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
   DATA = ROOT / "data" / "cleaned"
   OUT = ROOT / "outputs" / "iter2" / "propensity"; OUT.mkdir(parents=True, exist_ok=True)
   DISTRICTS = ["BARREL", "CACTUS", "CHOLLA", "OCOTILLO", "SAHUARO", "YUCCA"]
   START, END = "2020-01-01", "2026-07-31"; YEARS = 79 / 12
   req = pd.read_csv(DATA / "glendaleone_clean.csv", parse_dates=["request_date", "close_date"], low_memory=False)
   req["district"] = req["district"].astype("string").str.strip().str.upper()
   n_raw = len(req)
   req_w = req[req["request_date"].between(START, END)]
   n_window = len(req_w)
   req_w = req_w[req_w["district"].isin(DISTRICTS)].copy()
   n_final = len(req_w)
   print(n_raw, n_window, n_final, n_window - n_final)
   ```
   Expected: `n_raw` 106,795; `n_window` 106,617; about 2.2% of the window has no district. Also check `req_w["request_number"].is_unique` is True.
2. **Load and join the demographics.** Check it is one-to-one:
   ```python
   dip = pd.read_csv(DATA / "acs_demo_income_profile_clean.csv")
   acs = pd.read_csv(DATA / "acs_population_summary_clean.csv")
   for d in (dip, acs):
       d["district"] = d["district"].str.strip().str.upper()
   demo = (dip.merge(acs, on="district", how="inner", validate="one_to_one")
              .set_index("district").loc[DISTRICTS])
   assert len(demo) == 6
   ```
3. **Counts and rates.** Build the per-district table:
   ```python
   rates = pd.DataFrame({"n_requests": req_w["district"].value_counts().reindex(DISTRICTS)})
   rates["pop_esri_2026"] = demo["dip_summary_total_population_2026"]
   rates["pop_acs_2020_24"] = demo["acs_total_population"]
   for src in ["esri_2026", "acs_2020_24"]:
       rates[f"rate_per_1000_yr_{src}"] = rates["n_requests"] / YEARS / rates[f"pop_{src}"] * 1000
   no_trash = req_w[req_w["request_type_group"] != "Trash/Recycle Services"]
   rates["rate_per_1000_yr_esri_2026_no_trash"] = (no_trash["district"].value_counts().reindex(DISTRICTS)
                                                  / YEARS / rates["pop_esri_2026"] * 1000)
   rates["share_requests_pct"] = rates["n_requests"] / rates["n_requests"].sum() * 100
   rates["share_pop_esri_pct"] = rates["pop_esri_2026"] / rates["pop_esri_2026"].sum() * 100
   assert rates["n_requests"].sum() == n_final
   ```
   Sanity: every rate should land somewhere between about 30 and 100 requests per 1,000 residents per year. If not, re-check step 1.
4. **Goodness-of-fit test** (planned test: do counts follow population shares?). Run it for both denominators:
   ```python
   from scipy.stats import chisquare
   tests = []
   N = rates["n_requests"].sum()
   for src in ["esri_2026", "acs_2020_24"]:
       pop = rates[f"pop_{src}"]
       exp = N * pop / pop.sum()
       chi2, p = chisquare(rates["n_requests"], f_exp=exp)
       rates[f"std_resid_{src}"] = (rates["n_requests"] - exp) / exp ** 0.5
       tests.append({"denominator": src, "N": N, "chi2": chi2, "df": 5, "p_value": p,
                     "cohens_w": (chi2 / N) ** 0.5})
   rates["rank_esri_2026"] = rates["rate_per_1000_yr_esri_2026"].rank(ascending=False, method="min").astype(int)
   rates["rank_acs_2020_24"] = rates["rate_per_1000_yr_acs_2020_24"].rank(ascending=False, method="min").astype(int)
   rates.reset_index(names="district").to_csv(OUT / "q1_rates_by_district.csv", index=False)
   pd.DataFrame(tests).to_csv(OUT / "q1_chisq_tests.csv", index=False)
   ```
   With about 104,000 requests, p will be tiny. **Cohen's w is the headline** (0.1 small, 0.3 medium, 0.5 large). A positive standardized residual means the district files more than its population share.
5. **Covariates.** Build the table:
   ```python
   cov = pd.DataFrame(index=DISTRICTS)
   cov["median_hh_income_2026"] = demo["dip_hhinc_median_household_income_2026"]
   rent, own = demo["dip_summary_renter_occupied_housing_units_2026"], demo["dip_summary_owner_occupied_housing_units_2026"]
   cov["renter_share_2026_pct"] = rent / (rent + own) * 100
   cov["no_internet_pct"] = demo["acs_internet_with_no_internet_access_pct"]
   cov["no_internet_moe"] = demo["acs_internet_with_no_internet_access_moe"]
   cov["spanish_english_not_well_18_64_pct"] = demo["acs_lang_18_64_speak_spanish_speak_english_not_well_pct"]
   cov["spanish_english_not_well_18_64_moe"] = demo["acs_lang_18_64_speak_spanish_speak_english_not_well_moe"]
   cov["rent_50plus_pct"] = demo["acs_rent_burden_50plus_pct_of_income_pct"]
   cov["rent_50plus_moe"] = demo["acs_rent_burden_50plus_pct_of_income_moe"]
   cov.reset_index(names="district").to_csv(OUT / "q1_covariates.csv", index=False)
   ```
   **Denominator check (write the result in findings.md):**
   - Compute `count / pct * 100` for the language column (`acs_lang_18_64_speak_spanish_speak_english_not_well`) and for `acs_lang_18_64_speak_only_english`. If both give the same total per district, the percent is a share of residents aged 18–64.
   - Do the same for `acs_internet_with_no_internet_access` against `acs_internet_total`.
   - Note: the MOE columns are in the same units as the estimate they belong to [confirm on one row against the raw workbook if it looks odd].
6. **Rank comparison** (descriptive only, n = 6):
   ```python
   from scipy.stats import spearmanr
   rows = []
   for c in ["median_hh_income_2026", "renter_share_2026_pct", "no_internet_pct",
             "spanish_english_not_well_18_64_pct", "rent_50plus_pct"]:
       rho, _ = spearmanr(rates["rate_per_1000_yr_esri_2026"], cov[c])
       rows.append({"covariate": c, "spearman_rho": round(rho, 2), "n_districts": 6})
   pd.DataFrame(rows).to_csv(OUT / "q1_spearman.csv", index=False)
   ```
   Report rho only, with no p-values: with 6 points, a p-value says almost nothing. Use "lines up with", never "causes".
7. **Chart A – rate by district.** Paste the chart setup:
   ```python
   import seaborn as sns, matplotlib.pyplot as plt
   sns.set_theme(style="whitegrid", context="talk"); BLUE = "#2a78d6"
   plot = rates.reset_index(names="district").sort_values("rate_per_1000_yr_esri_2026", ascending=False)
   city = N / YEARS / rates["pop_esri_2026"].sum() * 1000
   fig, ax = plt.subplots(figsize=(12, 6.75))
   sns.barplot(data=plot, x="district", y="rate_per_1000_yr_esri_2026", color=BLUE, ax=ax)
   ax.axhline(city, ls="--", lw=2, color="#52514e"); ax.text(ax.get_xlim()[1], city, " Citywide", va="center")
   ax.set(xlabel="", ylabel="Requests per 1,000 residents per year", ylim=(0, None))
   ax.set_title("YOUR FINDING HERE (e.g. which district files most vs least)", loc="left")
   fig.text(0.01, -0.02, "Jan 2020 – Jul 2026. Population: Esri 2026. Source: City of Glendale GlendaleOne "
            "External Requests (extract loaded 2026-08-06).", fontsize=11)
   fig.savefig(OUT / "q1_rate_by_district.png", dpi=200, bbox_inches="tight")
   ```
   - Label only the highest and lowest bars with their values (`ax.bar_label` on those two).
   - The title must state the finding in words.
8. **Chart B – rate against each covariate.**
   - Make 5 small scatter panels in one figure: `fig, axes = plt.subplots(1, 5, figsize=(20, 5), sharey=True)`.
   - Plot each covariate on x and `rate_per_1000_yr_esri_2026` on y.
   - Write each district's name next to its dot with `ax.annotate`. Use one color (`BLUE`) and no trend lines.
   - Put rho in each panel's title, e.g. "Median income (rho = 0.xx)".
   - Save as `q1_rate_vs_covariates.png`.
9. **Write `outputs/iter2/propensity/findings.md`:**
   - 3 findings, each with a number and a comparison.
   - The ACS-vs-Esri sensitivity in one line: did the ranks change?
   - The no-trash sensitivity in one line.
   - The denominator check from step 5.
   - The filter log (`n_raw`, `n_window`, `n_final`, excluded).
   - Caveats: n = 6; association, not cause; ACS MOEs.
10. **Stretch (skip if you're over 6 h):**
    - Compute a Gini index for requests vs population across districts: sort districts by rate, compute cumulative population share X and cumulative request share Y, then `gini = 1 - sum((X[k] - X[k-1]) * (Y[k] + Y[k-1]))` with X and Y starting at 0.
    - Add the value to `q1_chisq_tests.csv` as a row with `denominator = "gini_esri_2026"`.

**Libraries and methods:** pandas (merge with `validate="one_to_one"`, `value_counts`), scipy.stats (`chisquare`, `spearmanr`), seaborn 0.13.2 (`barplot`), matplotlib (`subplots`, `annotate`, `savefig`).

**Watch out for (PROJECT.md section 6)**
- About 2.2% of requests have no district (they were `N/A` or `NONE`). They are excluded; report how many (6.6).
- Use 2020-01-01 to 2026-07-31 only. December 2019 is the launch month and August 2026 has only 5 days (6.4).
- Esri 2026 and ACS disagree most for YUCCA (53,147 vs 42,931). Lead with Esri and rerun with ACS (6.8).
- Median household income is `dip_hhinc_median_household_income_2026`. The `dip_trend_median_household_income_rate_*` columns are growth rates, not dollars (6.7).
- Trash/Recycle Services is about 48% of requests, hence the no-trash sensitivity (6.12, 7).
- `_pct` columns are on a 0–100 scale; ACS values have MOEs, so districts closer than their MOEs are "similar" (cleaning_log 1.2, 5).
- Don't copy any number from PROJECT.md section 7. Compute your own (7).
- Don't use Code Compliance data on this card. It has no district yet (6.1).

**Outputs**

| File | Columns | Rows |
|---|---|---|
| `q1_rates_by_district.csv` | `district, n_requests, pop_esri_2026, pop_acs_2020_24, rate_per_1000_yr_esri_2026, rate_per_1000_yr_acs_2020_24, rate_per_1000_yr_esri_2026_no_trash, share_requests_pct, share_pop_esri_pct, std_resid_esri_2026, std_resid_acs_2020_24, rank_esri_2026, rank_acs_2020_24` | 6 |
| `q1_chisq_tests.csv` | `denominator, N, chi2, df, p_value, cohens_w` | 2 (3 with the stretch) |
| `q1_covariates.csv` | `district, median_hh_income_2026, renter_share_2026_pct, no_internet_pct, no_internet_moe, spanish_english_not_well_18_64_pct, spanish_english_not_well_18_64_moe, rent_50plus_pct, rent_50plus_moe` | 6 |
| `q1_spearman.csv` | `covariate, spearman_rho, n_districts` | 5 |
| `q1_rate_by_district.png`, `q1_rate_vs_covariates.png` | charts | – |
| `findings.md` | findings, sensitivities, denominator check, filter log, caveats | – |

**Checks before you open the PR (tick them in the PR description)**
- [ ] EDA: the filter-log counts add up, `request_number` is unique, exactly 6 districts, and per-district counts sum to `n_final`.
- [ ] Stats: the planned test is written above the cell that runs it; Cohen's w is reported with the exact p; Spearman is reported as descriptive; no causal words anywhere.
- [ ] Charts: the title states a finding, bars start at 0, one hue, selective labels, a source note, 200 dpi.
- [ ] QA:
  - The extract date is stated, and the window and denominators are named.
  - One number was computed a second way (e.g. CHOLLA's count with `(req_w.district == "CHOLLA").sum()`).
  - Rates are in a plausible range, and caveats are listed.

**Definition of done**
- [ ] Restart the kernel and Run All works with no errors.
- [ ] All 7 output files exist with exactly the columns above.
- [ ] findings.md has 3 findings with numbers, both sensitivities, the denominator check and the filter log.
- [ ] The PR is ready for review with Ma'el as reviewer, the notebook outputs are cleared and no CSV from `data/` is committed.

**Updates:** Mon and Thu in the group chat (Progress / Plans / Problems). If you're stuck for more than 30 minutes, post it under Problems right away.
