# Iteration 2 – Time-to-close by district

Owner: Shenoy · Reviewer: Ma'el · Notebook: `notebooks/iter2_time_to_close_shenoy.ipynb`

**Source and freshness:** `data/cleaned/glendaleone_clean.csv` (GlendaleOne External Requests, extract loaded 2026-08-06, team Drive copy). Window: requests opened 2020-01-01 to 2026-07-31. Grain: one row = one closed request. No population denominator is used here.

**Measure:** `days_to_close = close_date - request_date` in whole days (dates are date-only UTC, so a same-day close is 0). A request is *slower than typical for its type* when it took longer than the citywide median for its exact `request_type`, computed on this analysis set. That is not the City's target: the escalation targets are not downloaded, so nothing here is scored against them.

**Change from the plan:** the type control was planned as the 17 `request_type_group` values (ANALYSIS_STANDARDS section 3) and changed after the first run to the 155 exact `request_type` values, which match the task file's wording ("the median for their own request type"). The groups hide large timing differences inside them (finding 3). The group-level result is reported alongside in `type_corrected_share_by_district.csv`, `median_days_by_district_and_type_group.csv` and `stat_tests.csv`.

## Findings

1. **Before accounting for request type, district medians run from 2 days in Ocotillo to 5 days in Cholla.** The typical closed request takes 3 days citywide (mean 8.3). Even so, district lines up with only 0.7% of the variation in raw days (Kruskal-Wallis H = 769, epsilon squared = 0.007, negligible by rule of thumb, p < .001).
2. **About 78% of the raw district gap lines up with type mix.** Compared with the typical time for its exact request type, the share of requests slower than typical runs from 41.0% in Ocotillo to 44.2% in Cactus (citywide 43.0%): a 3.2-point gap, vs 14.5 points when every request is compared with the citywide median. Cramér's V is 0.023 type-corrected (negligible) vs 0.093 raw. With the 17 broad type groups instead, the gap only narrows to 12.1 points (finding 3 shows why).
3. **The broad groups hide the mix inside them.** Residential - Container Damaged (citywide median 6 days) is 79% of Cholla's Trash/Recycle Services requests but 46% of Ocotillo's, while within Residential - Container Damaged district medians run only from 6 to 7 days. Across the 8 most common exact types (61% of closed requests), the widest district spread is in Street Light or Pedestrian Light Issue: 9 days in Barrel, Cholla, Ocotillo and Yucca to 11.5 days in Cactus.

## Caveats

- Closed requests only (99.7% of the analysis set). Requests still open on the extract date are missing, so the latest months lean fast. Only 91.3% of 2026-07 requests were closed by the extract date.
- 46 requests are On Hold, In Progress or Open but carry a close date; the Closed filter drops them.
- Whole-day dates: a one-day difference is within the rounding, and a request filed in the evening can land on the next day.
- 59 request types have fewer than 30 closed requests (646 requests, 0.6%); their "typical" time rests on few cases.
- Outliers are kept: 112 requests (0.11%) took over 365 days; medians with and without them are in `outlier_check.csv`.
- With 103,939 rows nearly every p-value is tiny, so the effect sizes lead. Effect-size labels are rules of thumb (epsilon squared: Tomczak & Tomczak 2014; Cramér's V: Cohen 1988).
- Within-type Kruskal-Wallis tests are exploratory and Holm-corrected (`stat_tests.csv`).
- These are associations, not cause and effect. Nothing here says why a district is faster or slower, or why districts file different request types.
- 2,343 in-window requests with no district (were `N/A` or `NONE`) are excluded.

## Filter log

| Step | Rows after | Rows removed |
|---|---|---|
| raw file | 106,795 | 0 |
| request_date 2020-01-01 to 2026-07-31 | 106,617 | 178 |
| district is one of the 6 | 104,274 | 2,343 |
| status == Closed | 103,940 | 334 |
| close_date not null | 103,940 | 0 |
| drop flag_close_before_request (not fixed) | 103,939 | 1 |

`n_raw` = 106,795 · `n_window` = 106,617 · `n_final` = 104,274 · `n_closed` = 103,939. Outside the window: 0 before 2020-01-01 and 178 after 2026-07-31.

## Outputs

| File | What it holds |
|---|---|
| `days_to_close_by_district.csv` | Per district: `n`, `mean_days`, `median_days`, `p25_days`, `p75_days`, `p90_days`, `max_days`, `share_same_day` (closed the day it was opened), `share_over_365` |
| `type_corrected_share_by_district.csv` | Per district: `n`, `n_slower_than_type` / `share_slower_than_type` (above the citywide median for its exact type; the main measure), `share_slower_than_type_group` (same with the 17 groups), `share_slower_than_city_median` (raw yardstick), `share_trash_recycle`, `pp_vs_citywide_type` (points above or below the citywide share) |
| `type_medians_citywide.csv` | Per exact type: its group, `n`, `median_days` (the "typical" yardstick) |
| `trash_recycle_mix_by_district.csv` | The 5 most common exact types inside Trash/Recycle Services: each district's `n` and `share_of_district_trash_recycle`, and `citywide_type_median_days` |
| `median_days_by_district_and_type.csv` | District x the 8 most common exact types: `n`, `median_days`, `mean_days`, `p90_days`, `citywide_median_days`, `small_cell` (n < 30) |
| `median_days_by_district_and_type_group.csv` | The same at the 17-group level, for comparison |
| `stat_tests.csv` | Every test: `plan`, `scope`, `n`, `statistic`, `df`, `p_value`, `p_holm`, `effect_size_name`, `effect_size` |
| `chi2_residuals_by_district.csv` | Observed vs expected slower-than-typical counts and the Pearson residual per district |
| `outlier_check.csv` | Requests over the IQR fence (16 days) and over 365 days, and medians and means with and without the over-365 requests |
| `filter_log.csv` | The filter log above |
| `type_corrected_share_by_district.png`, `raw_vs_type_corrected_by_district.png`, `heatmap_median_days_district_by_type.png` | Charts, 200 dpi, 12 x 6.75 in |
