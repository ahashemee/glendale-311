### Card iter2-03 – Monthly request trend – Akshara

**File:** `docs/tasks/iter2-03-monthly-trend.md`
**Owner:** Akshara · **Reviewer:** Shenoy · **Complexity:** C1 · **Estimate:** 1.7 h (1–3 h)
**Start:** Sun 2026-09-27 · **First check-in:** Thu 2026-10-01 (post the chart, even as a draft) · **Due (PR ready):** Sun 2026-10-04 23:59 · **Hard or soft:** soft (it isn't on the critical path, but it frees your time for the story)
**Questions:** Ma'el in the group chat, any time.

**Why this matters.** In Iteration 1 we promised a "request trends over time" chart. This shows whether each district's volume is steady, rising or falling, which is context for the equity story.

**Outcome.** One CSV and one six-panel chart in `outputs/iter2/trend/`. The code below is complete, so you run it and check the picture.

**Steps**
1. Run `git checkout main && git pull`, then `git checkout -b feature/iter2-trend` and `pip install pandas "seaborn==0.13.2" matplotlib`.
2. Download `glendaleone_clean.csv` from Drive "City of Glendale" into `data/cleaned/`. Create `notebooks/iter2_trend_akshara.ipynb`.
3. Paste and run this. It should print `106795 106617` followed by two more numbers:
   ```python
   from pathlib import Path
   import pandas as pd
   ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
   DATA = ROOT / "data" / "cleaned"
   OUT = ROOT / "outputs" / "iter2" / "trend"; OUT.mkdir(parents=True, exist_ok=True)
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
4. Paste and run this. Both lines should print `True`:
   ```python
   monthly = (req_w.assign(month=req_w["request_date"].dt.to_period("M").dt.to_timestamp())
                .groupby(["district", "month"]).size().rename("n_requests").reset_index())
   print(monthly["n_requests"].sum() == n_final)
   print(monthly.groupby("district").size().eq(79).all())   # 79 months for every district
   monthly.to_csv(OUT / "monthly_requests_by_district.csv", index=False)
   ```
5. Paste and run this. You should get six small line charts (2 rows of 3), all in the same blue, all with the same y-axis starting at 0:
   ```python
   import seaborn as sns, matplotlib.pyplot as plt
   sns.set_theme(style="whitegrid", context="talk")
   g = sns.relplot(data=monthly, x="month", y="n_requests", col="district", col_order=DISTRICTS,
                   col_wrap=3, kind="line", color="#2a78d6", linewidth=2, height=3.2, aspect=1.6)
   g.set(ylim=(0, None)); g.set_titles("{col_name}"); g.set_axis_labels("", "Requests per month")
   g.figure.suptitle("YOUR ONE-LINE TAKEAWAY HERE", x=0.01, ha="left", y=1.04)
   g.figure.text(0.01, -0.03, "Jan 2020 – Jul 2026. Source: City of Glendale GlendaleOne External Requests "
                 "(extract loaded 2026-08-06).", fontsize=11)
   g.savefig(OUT / "monthly_requests_by_district.png", dpi=200, bbox_inches="tight")
   ```
6. Look at the chart and write `outputs/iter2/trend/findings.md` with 2–3 plain-English observations. For example: which districts rise or fall, any spike months, whether 2020–21 (COVID years) look different. Put your best observation in the chart title (step 5) and re-run. Commit (clear the notebook outputs first), push, open a PR, and assign Shenoy.

**Watch out for**
- August 2026 has only 5 days and December 2019 is the launch month; both are already left out by the dates in step 3 (PROJECT.md 6.4).
- About 2.2% of requests have no district and are left out (6.6).
- The City's feed stopped updating on 2026-08-06, so say "through July 2026" (6.4).
- Don't read any cause into a bump, like "people got angrier". Describe what you see, and note ideas as questions for the team.

**Outputs:** `monthly_requests_by_district.csv` (columns `district, month, n_requests`; 474 rows = 6 x 79), `monthly_requests_by_district.png` and `findings.md`.

**Definition of done**
- [ ] Both checks in step 4 print `True`.
- [ ] The chart has 6 panels, a shared y-axis starting at 0, your takeaway as the title, and the source note.
- [ ] findings.md has 2–3 observations.
- [ ] The PR is open with Shenoy as reviewer, and no data CSV from `data/` is committed.
