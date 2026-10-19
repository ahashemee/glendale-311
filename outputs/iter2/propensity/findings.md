# Iteration 2 – Reporting propensity by Council District

Owner: Shamie (finished by Ma'el on 2026-10-18) · Reviewer: Ma'el · Notebook: `notebooks/iter2_propensity_shamie.ipynb`

**Source and freshness:** `data/cleaned/glendaleone_clean.csv` (GlendaleOne External Requests, extract loaded 2026-08-06, team Drive copy). Populations and covariates come from `data/cleaned/acs_demo_income_profile_clean.csv` (Esri 2026) and `data/cleaned/acs_population_summary_clean.csv` (ACS 2020-24 5-year estimates).

**Window:** requests opened 2020-01-01 to 2026-07-31 (79 full months).

**Grain:** one row = one GlendaleOne request. The demographic files have one row per district.

**Denominator:** Esri 2026 population (`dip_summary_total_population_2026`) is the primary denominator. ACS 2020-24 population (`acs_total_population`) is the sensitivity check.

**Rate:** requests per 1,000 residents per year = request count / (79 / 12) / population x 1,000.

**Tests (planned before the run):** chi-square goodness of fit of district counts against population shares, led by Cohen's w; Spearman rho between the district rate and five covariates (descriptive, n = 6). Both are run with each denominator, with and without Trash/Recycle Services.

## Findings

1. **District request counts do not match population shares, but the gap is small by Cohen's rule of thumb.** Against Esri 2026 population shares, chi-square(5) = 2,831.3, p < .001, Cohen's w = 0.165 (small; n = 104,274). Cholla files 22.2% more requests than its population share predicts and Sahuaro 19.9% more. Cactus files 21.6% fewer and Yucca 15.2% fewer. With the ACS population, w is almost the same at 0.166.

2. **Cholla files 1.56x the requests per resident of Cactus.** On the Esri 2026 denominator, Cholla has 72.9 requests per 1,000 residents per year and Sahuaro 71.5, against 59.7 citywide. Cactus is lowest at 46.8.

3. **Without Trash/Recycle, the income, renter and language alignment disappears and only rent burden holds.** With all requests, higher-rate districts have higher median income, fewer renters and fewer limited-English speakers (Esri rho +0.43, -0.60 and -0.66). With Trash/Recycle Services removed (they are 48.9% of analysed requests), those three drop to near zero (-0.14, -0.03 and -0.09). Only rent burden keeps its link, at +0.70 against +0.58 with all requests. This lines up with F-01, where Residential - Container Damaged is 79% of the Trash/Recycle requests from Cholla, the highest-income and highest-rate district (F-01, outputs/iter2/time_to_close/trash_recycle_mix_by_district.csv).

## Sensitivity checks

- **Esri vs ACS population:** the ranking changed. Sahuaro (75.8) passes Cholla (74.4) for first, Yucca rises from fifth to third (50.6 to 62.6) and Cactus stays lowest (45.4). The overall gap is the same size (w = 0.165 vs 0.166).
- **Trash/Recycle removed:** the ranking changed. Ocotillo moves from third to first (37.1), Cholla drops from first to third (33.8) and Cactus stays lowest (25.8). The gap narrows a little (Esri w = 0.147 vs 0.165).

## Caveats

- **Six districts.** Every rho rests on n = 6, so it is descriptive, and one district changing places moves it a lot.
- **No p-values for rho.** Rho is reported without a p-value and never called significant. Only the chi-square tests carry one; with 104,274 requests it is tiny regardless, so Cohen's w leads.
- **ACS margins of error.** Internet access, language and rent burden are ACS 2020-24 estimates with margins of error, and rho ignores those margins. Where two districts differ by less than their margins, read them as similar. The language share is small everywhere (0.1% in Cholla to 7.4% in Ocotillo); its denominator is not confirmed `[uncertain]`, and it leaves out adults who speak no English at all.
- **Yucca denominator gap.** Esri 2026 puts Yucca at 53,147 residents and ACS 2020-24 at 42,931. Yucca's rate is 50.6 on Esri and 62.6 on ACS, so its rank depends on the source more than any other district's.
- **Mixed sources and years.** Population, income and renter share are Esri 2026 estimates; internet, language and rent burden are ACS 2020-24. Requests span 2020 to 2026.
- **Ties.** Cactus and Yucca share a rent burden of 52.8%, so Spearman gives them the average rank.
- **Exclusions.** The analysis leaves out 2,343 in-window requests with no district (they were `N/A` or `NONE`) and 178 requests dated after 2026-07-31.
- **Association, not cause.** These tables show which district traits co-vary with request rates, not why one district files more than another. A rate counts requests, not residents, so a few frequent filers can lift a district's rate.

## Filter log

| Measure | Value |
|---|---|
| `n_raw` | 106,795 |
| excluded outside the window (after 2026-07-31) | 178 |
| `n_window` (2020-01-01 to 2026-07-31) | 106,617 |
| excluded (no district) | 2,343 |
| `n_final` (one of the six districts) | 104,274 |
| `n_no_trash` (`n_final` without Trash/Recycle Services) | 53,247 |
| Trash/Recycle Services share of `n_final` | 48.9% |

The same numbers are in `filter_log.csv`. None of the 79 months in the window is empty.

## Outputs

All in `outputs/iter2/propensity/`, written by the notebook. `district` values stay UPPERCASE (the join key); charts and this file use Title Case.

| File | Columns |
|---|---|
| `request_rates.csv` | One row per district: `district`, `request_count`, `esri_population_2026`, `acs_population_2020_24`, `requests_per_1000_per_year_esri`, `requests_per_1000_per_year_acs`, `request_count_no_trash`, `requests_per_1000_per_year_esri_no_trash`, `requests_per_1000_per_year_acs_no_trash`, `rank_esri`, `rank_acs`, `rank_esri_no_trash`, `rank_acs_no_trash` (1 = highest rate), `ratio_to_lowest_esri` (Esri rate / the lowest Esri rate) |
| `district_covariates.csv` | One row per district: `district`, `requests_per_1000_per_year_esri`, `requests_per_1000_per_year_acs`, `dip_hhinc_median_household_income_2026` (dollars), `renter_share_2026_pct` (renter-occupied units / households), `acs_internet_with_no_internet_access_pct`, `acs_lang_18_64_speak_spanish_speak_english_not_well_pct` (adults 18-64 who speak Spanish and speak English "not well"), `rent_burden_30plus_pct` (renter households paying 30% or more of income on rent). All `_pct` columns are 0-100 |
| `chi_square_summary.csv` | One row per scenario (`all_esri`, `all_acs`, `no_trash_esri`, `no_trash_acs`): `scenario`, `request_set`, `denominator`, `n`, `total_population`, `citywide_rate_per_1000_per_year`, `chi_square`, `df`, `p_value`, `cohens_w`, `w_size` (Cohen's rule of thumb) |
| `chi_square_district_diagnostics_esri.csv` | One row per district, all requests on Esri 2026: `district`, `observed`, `expected`, `standardized_residual` ((observed - expected) / sqrt(expected)), `pct_above_below_expected`, `population_share_pct`, `request_share_pct` |
| `spearman_rho.csv` | One row per covariate: `covariate`, `n` (districts), `rho_esri_all`, `rho_acs_all`, `rho_esri_no_trash`, `rho_acs_no_trash` |
| `filter_log.csv` | `measure`, `value`, `description`: `n_raw`, `excluded_outside_window`, `n_window`, `excluded_no_district`, `n_final`, `n_trash_recycle`, `n_no_trash`, `trash_recycle_share_of_final_pct` |
| `request_rate_by_district_esri.png` | Bar chart of the Esri rate by district with the citywide line, 200 dpi, 12 x 6.75 in |
| `scatter_panels_covariates.png` | Five panels, rate against each covariate, all requests vs Trash/Recycle removed, 200 dpi, 12 x 6.75 in |
| `findings.md` | This file |
