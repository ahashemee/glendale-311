# Findings (living)

The team's current state of knowledge. Every entry points to the evidence that backs it. When a merged analysis changes the story, update this file in the same PR and propose the matching edit to the **Direction (living)** section of `CLAUDE.md`.

Three findings so far (F-01 to F-03). PROJECT.md section 7 figures are orientation only.

## Validated findings

### F-03 – Every district filed fewer requests in 2024 than in 2023 (citywide -14.6%, Cactus -22.4%), and from January to July 2026 the districts moved in different directions
- Finding: citywide requests went from 16,778 in 2023 to 14,336 in 2024 (-14.6%), and every district declined, from Yucca (-8.1%) to Cactus (-22.4%). May 2023 holds both the highest district-month (Cactus, 408) and the highest citywide month (1,926); November 2024 is the lowest citywide month in the window (819). January to July 2026 vs the same months of 2025: Yucca +17.5%, Barrel +15.3%, Cactus +6.4%, Ocotillo +6.4%, Cholla -11.2%, Sahuaro -11.6% (citywide +2.6%).
- Evidence: outputs/iter2/trend/findings.md, monthly_counts_by_district.csv, change_by_district.csv, monthly_trend_by_district.png, trend_charts.html
- Owner: Akshara (finished by Ma'el) · Merged: 2026-10-18 · Window and denominator: GlendaleOne requests opened 2020-01-01 to 2026-07-31, 474 district-months summing to n = 104,274 (2,343 with no district excluded); raw counts, no population denominator
- Caveats: raw counts, not per resident. 2026 is compared January to July only. Descriptive: nothing here tests why a month stands out. Associations only.
- Hypothesis it bears on: none directly (unclear). Context for H1 and H2: a rate over the whole window averages over volume that moves by year and by month.

### F-02 – Cholla files 1.56x the requests per resident of Cactus, and the rate's alignment with income, renters and limited English nearly disappears without Trash/Recycle
- Finding: district request counts do not match population shares (chi-square(5) = 2,831.3, Cohen's w = 0.165, small). Cholla files 72.9 requests per 1,000 residents per year and Cactus 46.8, against 59.7 citywide. With all requests, higher-rate districts have higher median income, fewer renters and fewer limited-English speakers (Spearman rho +0.43, -0.60, -0.66). With Trash/Recycle Services removed (48.9% of requests), those drop to -0.14, -0.03 and -0.09, and only rent burden holds (+0.70).
- Evidence: outputs/iter2/propensity/findings.md, chi_square_summary.csv, request_rates.csv, spearman_rho.csv, scatter_panels_covariates.png
- Owner: Shamie (finished by Ma'el) · Merged: 2026-10-18 · Window and denominator: GlendaleOne requests opened 2020-01-01 to 2026-07-31, n = 104,274 (2,343 with no district excluded); Esri 2026 population, with ACS 2020-24 as the sensitivity (w = 0.166)
- Caveats: n = 6 districts, so rho is descriptive and carries no p-value. ACS estimates have margins of error. Yucca's population differs most between Esri (53,147) and ACS (42,931), and its rank moves from fifth to third on ACS. The language column's denominator is not confirmed `[uncertain]`. The pattern lines up with F-01: Residential - Container Damaged is 79% of Cholla's Trash/Recycle requests. Associations only.
- Hypothesis it bears on: H1 (weakens: the income, renter and language alignment tracks Trash/Recycle, not total volume), H2 (supports)

### F-01 – About 78% of the raw district gap in time-to-close lines up with request-type mix
- Finding: the share of closed requests slower than the citywide median runs from 40.5% (Ocotillo) to 55.0% (Cholla), a 14.5-point gap; against the typical time for each request's exact type, the range is 41.0% (Ocotillo) to 44.2% (Cactus), a 3.2-point gap (Cramér's V 0.093 raw vs 0.023 type-corrected, both negligible). Raw district medians run from 2 days (Ocotillo) to 5 days (Cholla).
- Evidence: outputs/iter2/time_to_close/findings.md, type_corrected_share_by_district.csv, stat_tests.csv
- Owner: Shenoy (finished by Ma'el) · Merged: 2026-10-18 · Window and denominator: GlendaleOne requests opened 2020-01-01 to 2026-07-31, closed only, n = 103,939 (2,343 with no district excluded)
- Caveats: "typical" is the citywide median for the exact `request_type` (155 types), not the City's escalation targets, which are not downloaded. With the 17 type groups the gap only narrows to 12.1 points: groups such as Trash/Recycle hide different type mixes. Closed-only timing leans fast in the latest months (91.3% of 2026-07 requests closed). 59 types have under 30 requests. Associations only.
- Hypothesis it bears on: H3 (supports)

Add entries in this format, newest first:

```
### F-NN – one-sentence finding with its number and comparison
- Evidence: outputs/iterN/<topic>/findings.md (and the CSV or chart)
- Owner: name · Merged: YYYY-MM-DD · Window and denominator: ...
- Caveats: ... `[uncertain]` where a fact is not verified
- Hypothesis it bears on: H1 / H2 / H3 (supports, weakens, unclear)
```

## Working hypotheses

From `docs/DELIVERABLE_IDEAS.md`. Each is phrased as an association to check, not a cause; the tag shows where the evidence stands after Iteration 2.

- **H1 – Reporting-propensity gap** `[weakened]` (F-02). Request volume per resident may line up with who reports (income, internet access, language, rent burden) more than with need, so the highest-income districts could file the most requests per resident. Shamie's Iteration 2 piece: with all requests the rate lines up with higher income, fewer renters and fewer limited-English speakers, but those alignments drop to near zero once Trash/Recycle is removed, and only rent burden holds.
- **H2 – District request signatures** `[supported]` (first evidence, F-01 and F-02). The equity signal may sit in the *mix* of request types rather than the volume: some groups, such as Assistance Programs, may be concentrated in lower-income districts once trash containers are set aside. In Iteration 2 the income alignment in F-02 and most of the time-to-close gap in F-01 track the type mix: both sit in Trash/Recycle, where Residential - Container Damaged is 79% of Cholla's Trash/Recycle requests (F-01). The Assistance Programs part is untested and stays planned for the final iteration.
- **H3 – Response equity against the City's own clocks** `[supported]` (type-controlled version, F-01). Raw days-to-close differ by district, but type mix may line up with much of it; scoring each request against its type (and later against the City's escalation times) tests whether response is equitable. Iteration 2 tests the type-controlled version in Shenoy's Iteration 2 piece; the escalation-time version is blocked until the targets table is downloaded.
