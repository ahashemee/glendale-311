# Monthly request trends by Council District – findings

Iteration 2 · Task 1 in `docs/tasks/iter2-akshara.md` · Owner: Akshara Annu (finished by Ma'el Hashemee on 2026-10-18) · Reviewer: Ma'el Hashemee

| | |
|---|---|
| Source | `data/cleaned/glendaleone_clean.csv`: City of Glendale GlendaleOne External Requests, extract loaded 2026-08-06 (the `date_loaded` value on every row) |
| Window | `request_date` from 2020-01-01 to 2026-07-31 (79 full months) |
| Grain | One input row is one request. One output row is one district-month. |
| Coverage | 474 district-months (6 districts x 79 months), none of them empty |
| Denominator | None. Every figure here is a raw request count, not a rate per resident. |
| Notebook | `notebooks/iter2_trend_akshara.ipynb` |

## Observations

1. **Every district filed fewer requests in 2024 than in 2023.** The citywide count went from 16,778 to 14,336 (-14.6%). Cactus had the largest drop, -22.4% (2,258 to 1,753), followed by Sahuaro -17.3% (3,214 to 2,659), Ocotillo -15.2% (3,153 to 2,674), Barrel -13.2% (2,471 to 2,146), Cholla -12.3% (2,839 to 2,490) and Yucca -8.1% (2,843 to 2,614). Akshara's write-up said all six districts declined, and the notebook confirms it.
2. **May 2023 holds both the highest district-month and the highest citywide month.** Cactus filed 408 requests that month, the most of any of the 474 district-months. Across the six districts, May 2023 had 1,926 requests, more than any other month in the window.
3. **From January to July, four districts filed more requests in 2026 than in 2025, and two filed fewer.** The increases were Yucca +17.5% (1,464 to 1,720), Barrel +15.3% (1,239 to 1,429), Cactus +6.4% (1,025 to 1,091) and Ocotillo +6.4% (1,438 to 1,530). The decreases were Cholla -11.2% (1,659 to 1,473) and Sahuaro -11.6% (1,713 to 1,514). Citywide, the total rose 2.6% (8,538 to 8,757).

## Two months that stand out

These notes describe the counts only. This analysis does not test why either month looks the way it does.

- **Cactus, May 2023: a one-month spike.** Cactus went from 149 requests in April 2023 to 408 in May, then 218 in June and 168 in July. Its next-highest month in the window is 263 (August 2021), and its median month is 163.
- **November 2024: the citywide low.** The six districts together filed 819 requests, the lowest of all 79 months in the window. February 2025 comes next, with 918. November 2024 is also the low point of the window for four districts: Barrel (98, the smallest of all 474 district-months), Ocotillo (142), Yucca (152) and Sahuaro (153). The other two had their lows in other months: Cactus 102 in February 2025 (114 in November 2024) and Cholla 153 in December 2024 (160 in November 2024).

## Caveats

- **Raw counts, not per resident.** The districts have different populations, so a higher count does not mean more requests per person. Shamie's propensity analysis covers rates per resident.
- **2026 is a partial year.** The window ends on 2026-07-31, so 2026 is compared like-for-like: January to July 2026 against January to July 2025. Full calendar years are compared only for 2023 and 2024, which are both complete.
- **Exclusions.** 178 requests dated after 2026-07-31 (August 2026) and 2,343 in-window requests with no district (2.2% of the window) are left out. The file has no requests before 2020-01-01 and none without a date.
- **Month boundaries.** Dates are date-only and in UTC, so a request filed on the evening of a month's last day (Arizona time) can be dated to the next month (`docs/ANALYSIS_STANDARDS.md` G-dates).
- **Association, not cause.** The counts show when and where request volume changed, not why.

## Filter log

| Step | Rows | Note |
|---|---|---|
| `n_raw` | 106,795 | Rows in `glendaleone_clean.csv` |
| Excluded: outside the window | 178 | All dated after 2026-07-31 (August 2026). None before 2020-01-01; no missing dates. |
| `n_window` | 106,617 | `request_date` from 2020-01-01 to 2026-07-31 |
| Excluded: no district | 2,343 | 2.2% of `n_window`; these rows were `N/A` or `NONE` in the source |
| `n_final` | 104,274 | In the window and in one of the six districts |
| District-months | 474 | 6 x 79, none empty. Smallest 98, largest 408. They sum to `n_final`. |

The excluded rows add up: 106,795 - 178 - 2,343 = 104,274.

Per-district totals for the window (`n_total` in `change_by_district.csv`): Barrel 15,812, Cactus 13,209, Cholla 19,354, Ocotillo 17,766, Sahuaro 20,433, Yucca 17,700. They sum to 104,274, and a second count (`value_counts` on the filtered rows) gives the same six numbers. These totals match `request_count` in `outputs/iter2/propensity/request_rates.csv` for every district.

## Outputs

All files are in `outputs/iter2/trend/`. The notebook writes every file except this one.

| File | What it holds |
|---|---|
| `monthly_counts_by_district.csv` | 474 rows, one per district-month, sorted by district and month |
| `change_by_district.csv` | 7 rows: the six districts plus a `CITYWIDE` row (the sum of the six, month by month). Drop `CITYWIDE` before joining on `district`. |
| `monthly_trend_by_district.png` | Six panels, one per district, on a shared 0 to 500 y-axis, saved at 200 dpi from a 12 x 6.75 in figure. |
| `trend_charts.html` | Akshara's interactive page. On every run the notebook rewrites its embedded `rows` from `monthly_counts_by_district.csv` and fills each marked text spot, so every number on the page comes from the notebook. |
| `findings.md` | This file, written by hand from the notebook's printed results |

Column definitions:

| Column | File | Definition |
|---|---|---|
| `district` | both CSVs | Council District name in UPPERCASE (the join key used across the repo); `CITYWIDE` in `change_by_district.csv` only |
| `month` | `monthly_counts_by_district.csv` | Calendar month of `request_date`, `YYYY-MM` |
| `n` | `monthly_counts_by_district.csv` | Requests filed in that district in that month |
| `n_total` | `change_by_district.csv` | Requests from 2020-01 to 2026-07 |
| `n_2023`, `n_2024` | `change_by_district.csv` | Requests in calendar year 2023 and 2024 |
| `pct_change_2023_2024` | `change_by_district.csv` | (`n_2024` / `n_2023` - 1) x 100, rounded to one decimal |
| `n_jan_jul_2025`, `n_jan_jul_2026` | `change_by_district.csv` | Requests from January to July of 2025 and of 2026 |
| `pct_change_jan_jul_2025_2026` | `change_by_district.csv` | (`n_jan_jul_2026` / `n_jan_jul_2025` - 1) x 100, rounded to one decimal |
| `peak_month`, `peak_n` | `change_by_district.csv` | The month with the most requests in the window, and its count |
| `low_month`, `low_n` | `change_by_district.csv` | The month with the fewest requests in the window, and its count |
