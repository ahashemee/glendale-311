### Card iter2-02 – Time-to-close by district – Shenoy

**File:** `docs/tasks/iter2-02-time-to-close.md`
**Owner:** Shenoy · **Reviewer:** Shamie · **Complexity:** C2 · **Estimate:** 6.3 h (4–10 h)
**Start:** Sun 2026-09-27 · **First check-in:** Thu 2026-10-01 (post your step-4 filter counts and the step-6 table)
**Draft PR:** Thu 2026-10-08 · **Due (PR ready):** Sun 2026-10-11 23:59 · **Hard or soft:** hard (the presentation is Mon 2026-10-19)
**Questions:** Ma'el in the group chat, any time.

**Why this matters.** The City wants to know about fairness. Iteration 1 promised to check "how quickly requests are resolved per district". Some request types close in a day and others take weeks, so a district with more slow types would look slow for no real reason. This card measures time-to-close by district, then corrects for request type.

**Outcome.** Two tables, one test file and 2 charts in `outputs/iter2/time_to_close/` showing whether districts differ in how fast requests close once type is accounted for.

**Autonomy.** Follow the steps exactly. If a result doesn't match the expected range in a step, stop and post in the group chat before going on.

**Inputs:** `data/cleaned/glendaleone_clean.csv` (106,795 rows x 22 columns; download from Drive "City of Glendale" into `data/cleaned/`). Columns used: `request_date`, `close_date`, `status`, `district`, `request_type_group`, `request_number`, `flag_close_before_request`.

**Steps**
1. Run `git checkout main && git pull`, then `git checkout -b feature/iter2-time-to-close`.
2. Run `pip install pandas scipy "seaborn==0.13.2" matplotlib`. Create `notebooks/iter2_time_to_close_shenoy.ipynb`.
3. In the first cell, paste and run this. You should see `106795 106617` followed by two more numbers:
   ```python
   from pathlib import Path
   import pandas as pd
   ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
   DATA = ROOT / "data" / "cleaned"
   OUT = ROOT / "outputs" / "iter2" / "time_to_close"; OUT.mkdir(parents=True, exist_ok=True)
   DISTRICTS = ["BARREL", "CACTUS", "CHOLLA", "OCOTILLO", "SAHUARO", "YUCCA"]
   START, END = "2020-01-01", "2026-07-31"
   req = pd.read_csv(DATA / "glendaleone_clean.csv", parse_dates=["request_date", "close_date"], low_memory=False)
   req["district"] = req["district"].astype("string").str.strip().str.upper()
   n_raw = len(req)
   req_w = req[req["request_date"].between(START, END)]
   n_window = len(req_w)
   req_w = req_w[req_w["district"].isin(DISTRICTS)].copy()
   n_final = len(req_w)
   print(n_raw, n_window, n_final, n_window - n_final)
   ```
4. Keep only closed requests with a valid close date, then print the counts. The last number should be under 1% of `n_final`:
   ```python
   bad_flag = req_w["flag_close_before_request"].astype(str).str.lower() == "true"
   ttc = req_w[(req_w["status"] == "Closed") & req_w["close_date"].notna() & ~bad_flag].copy()
   n_closed = len(ttc)
   print(n_final, n_closed, n_final - n_closed)
   ```
5. Compute days to close and check none are negative. It should print `True`:
   ```python
   ttc["days_to_close"] = (ttc["close_date"] - ttc["request_date"]).dt.days
   print(ttc["days_to_close"].min() >= 0)
   print(ttc["days_to_close"].describe(percentiles=[.25, .5, .75, .9]))
   print("same day %:", round((ttc["days_to_close"] == 0).mean() * 100, 1),
         "| over 365 days %:", round((ttc["days_to_close"] > 365).mean() * 100, 2))
   ```
   Expect the mean to be much larger than the median, because a few requests take years. That's why we use medians.
6. Build the district table:
   ```python
   g = ttc.groupby("district")["days_to_close"]
   by_d = pd.DataFrame({
       "n": g.size(), "mean_days": g.mean(), "median_days": g.median(),
       "p25_days": g.quantile(.25), "p75_days": g.quantile(.75), "p90_days": g.quantile(.9),
       "pct_same_day": g.apply(lambda s: (s == 0).mean() * 100),
       "pct_over_365": g.apply(lambda s: (s > 365).mean() * 100),
       "median_days_excl_over_365": ttc[ttc["days_to_close"] <= 365].groupby("district")["days_to_close"].median(),
   }).reindex(DISTRICTS)
   print(by_d["n"].sum() == n_closed)   # must be True
   ```
7. Correct for request type. Each request is compared with the typical (median) time for *its own* request group:
   ```python
   ttc["type_median_days"] = ttc.groupby("request_type_group")["days_to_close"].transform("median")
   ttc["slower_than_type_median"] = ttc["days_to_close"] > ttc["type_median_days"]
   by_d["pct_slower_than_type_median"] = ttc.groupby("district")["slower_than_type_median"].mean().reindex(DISTRICTS) * 100
   city_pct = ttc["slower_than_type_median"].mean() * 100
   print(round(city_pct, 1))
   by_d.reset_index(names="district").to_csv(OUT / "ttc_by_district.csv", index=False)
   ```
   Many requests close in exactly the median time, so `city_pct` will be **below 50%**. That's expected. Compare each district with `city_pct`, not with 50.
8. Build the district x request-group table for the 8 biggest groups:
   ```python
   top8 = ttc["request_type_group"].value_counts().index[:8]
   by_dg = (ttc[ttc["request_type_group"].isin(top8)]
              .groupby(["district", "request_type_group"])["days_to_close"]
              .agg(n="size", median_days="median").reset_index())
   by_dg.to_csv(OUT / "ttc_by_district_group.csv", index=False)
   ```
9. Run the two planned tests. Write this sentence in a markdown cell **above** the code: "Planned tests: Kruskal-Wallis on days to close across 6 districts; chi-square on district x slower-than-type-median."
   ```python
   from scipy.stats import kruskal, chi2_contingency
   N = len(ttc)
   H, p_kw = kruskal(*[ttc.loc[ttc["district"] == d, "days_to_close"] for d in DISTRICTS])
   ct = pd.crosstab(ttc["district"], ttc["slower_than_type_median"]).reindex(DISTRICTS)
   chi2, p_chi, dof, _ = chi2_contingency(ct)
   tests = pd.DataFrame([
       {"test": "kruskal_days_to_close", "statistic": H, "df": 5, "p_value": p_kw,
        "effect_size_name": "epsilon_squared", "effect_size": H / (N - 1), "N": N},
       {"test": "chi2_slower_than_type_median", "statistic": chi2, "df": dof, "p_value": p_chi,
        "effect_size_name": "cramers_v", "effect_size": (chi2 / N) ** 0.5, "N": N},
   ])
   tests.to_csv(OUT / "ttc_tests.csv", index=False)
   print(tests)
   ```
   How to read it: the p-values will be tiny because N is about 100,000, so focus on the effect sizes. For epsilon squared, 0.01 is small, 0.06 medium and 0.14 large. For Cramér's V, 0.1 is small, 0.3 medium and 0.5 large.
10. Chart A: paste this and change only the title text:
    ```python
    import seaborn as sns, matplotlib.pyplot as plt
    sns.set_theme(style="whitegrid", context="talk")
    plot = by_d.reset_index(names="district")
    fig, ax = plt.subplots(figsize=(12, 6.75))
    sns.barplot(data=plot, x="district", y="pct_slower_than_type_median", color="#2a78d6", ax=ax)
    ax.axhline(city_pct, ls="--", lw=2, color="#52514e"); ax.text(ax.get_xlim()[1], city_pct, " Citywide", va="center")
    ax.set(xlabel="", ylabel="% slower than typical for type", ylim=(0, None))
    ax.set_title("YOUR FINDING HERE (which districts wait longer than typical)", loc="left")
    fig.text(0.01, -0.02, "Closed requests, Jan 2020 – Jul 2026. 'Typical' = citywide median days for the "
             "request group. Source: City of Glendale GlendaleOne External Requests (extract loaded 2026-08-06).", fontsize=11)
    fig.savefig(OUT / "ttc_pct_slower_by_district.png", dpi=200, bbox_inches="tight")
    ```
11. Chart B, a heatmap of median days. Paste this and change only the title:
    ```python
    heat = by_dg.pivot(index="request_type_group", columns="district", values="median_days")[DISTRICTS]
    fig, ax = plt.subplots(figsize=(12, 6.75))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="Blues", cbar_kws={"label": "Median days to close"}, ax=ax)
    ax.set(xlabel="", ylabel="")
    ax.set_title("YOUR FINDING HERE", loc="left")
    fig.savefig(OUT / "ttc_median_heatmap.png", dpi=200, bbox_inches="tight")
    ```
12. Write `outputs/iter2/time_to_close/findings.md` with these parts:
    - **3 findings**, each with a number and a comparison. Example format: "[District] requests were slower than typical X% of the time vs Y% citywide."
    - **Sensitivity**: does excluding the over-365-day requests change the district medians? (compare `median_days` with `median_days_excl_over_365`)
    - **Filter log**: `n_raw`, `n_window`, `n_final`, `n_closed`.
    - **Caveats**: dates are date-only; City targets are not used yet; association, not cause.
13. Commit the notebook (clear outputs first: Kernel → Restart & Clear Output), plus everything in `outputs/iter2/time_to_close/`. Push, and open a **draft PR** by Thu 10-08 with Shamie as reviewer. Mark it ready by Sun 10-11.

**Libraries and methods:** pandas (`groupby`, `transform`, `crosstab`, `pivot`), scipy.stats (`kruskal`, `chi2_contingency`), seaborn 0.13.2 (`barplot`, `heatmap`), matplotlib (`savefig`).

**Watch out for (PROJECT.md section 6)**
- Dates are date-only and in UTC. A same-day close is 0 days, and a late-evening request can land on the next day (section 9).
- 99.6% of requests are closed; use closed rows only (6.11). Drop the 1 row where close is before request, and don't "fix" it (cleaning_log 2.5).
- About 2.2% of requests have no district and are excluded (6.6).
- Use 2020-01-01 to 2026-07-31 only (6.4).
- The City's response targets aren't downloaded yet. Don't write "late", "missed target" or "on target"; write "slower than typical for its type" (6.12).
- Trash/Recycle is about half of all requests, which is why every comparison is made within request group (6.12).
- Don't copy the "median days" numbers from PROJECT.md section 7. Compute your own (7).

**Outputs**

| File | Columns | Rows |
|---|---|---|
| `ttc_by_district.csv` | `district, n, mean_days, median_days, p25_days, p75_days, p90_days, pct_same_day, pct_over_365, median_days_excl_over_365, pct_slower_than_type_median` | 6 |
| `ttc_by_district_group.csv` | `district, request_type_group, n, median_days` | up to 48 |
| `ttc_tests.csv` | `test, statistic, df, p_value, effect_size_name, effect_size, N` | 2 |
| `ttc_pct_slower_by_district.png`, `ttc_median_heatmap.png` | charts | – |
| `findings.md` | 3 findings, sensitivity, filter log, caveats | – |

**Checks before you open the PR (tick them in the PR description)**
- [ ] Filter counts printed at steps 3 and 4, and `by_d["n"].sum() == n_closed` is True.
- [ ] No negative days; the mean and median are both reported.
- [ ] The planned-tests sentence is written above the test cell; effect sizes are reported along with the p-values.
- [ ] Both charts have a finding in the title, the bar chart starts at 0, and the source note is present.
- [ ] One number checked a second way: `ttc.loc[ttc.district == "BARREL", "days_to_close"].median()` equals the BARREL row in `ttc_by_district.csv`.
- [ ] Caveats are listed in findings.md.

**Definition of done**
- [ ] Restart and Run All works with no errors.
- [ ] All 6 output files exist with exactly the columns above.
- [ ] findings.md is complete.
- [ ] The PR is ready with Shamie as reviewer, notebook outputs are cleared and no data CSV is committed.

**Updates:** post Progress / Plans / Problems every Mon and Thu in the group chat.
