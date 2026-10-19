# Iteration 2 storyline – Glendale 311 equity

Owner: Akshara (storyline and readability pass; finished by Ma'el on 2026-10-18) · Reviewer: Ma'el · Run sheet: `outputs/iter2/story/run_sheet.md`

Every number below comes from one of the three merged findings files. The list at the end says which file and line.

**So what:** Cholla's high request rate and the rate's link to income track Trash/Recycle requests, and the type mix inside Trash/Recycle (79% of Cholla's Trash/Recycle requests are Residential - Container Damaged) lines up with most of the district gap in time-to-close, so the equity signal sits in which requests a district files more than in how many it files or how fast they close.

---

## 1. Summary of the problem

**Speaker:** Ma'el · **Chart:** none

The City of Glendale's lead question is whether GlendaleOne request counts are distributed equitably based on Council District populations. For Iteration 2 we took that question and added another: does time-to-close differ by district once request type is taken into account? Both analyses start from 104,274 requests in the six Council Districts, opened from January 2020 to July 2026 (79 months), as of the City's 2026-08-06 extract.

**Transition:** "Shamie starts there: how many requests each district files per resident, and what that rate lines up with."

## 2. Preliminary analysis

### 2a. Reporting propensity (F-02)

**Speaker:** Shamie · **Charts:** `outputs/iter2/propensity/request_rate_by_district_esri.png`, then `outputs/iter2/propensity/scatter_panels_covariates.png`

Request counts do not match population shares, though the gap is small by Cohen's rule of thumb (w = 0.165). Cholla, the highest-income and highest-rate district, files 72.9 requests per 1,000 residents per year, 1.56x Cactus at 46.8, against 59.7 citywide. With all requests, higher-rate districts have higher median income, fewer renters and fewer limited-English speakers (Spearman rho +0.43, -0.60 and -0.66). Take out Trash/Recycle Services, 48.9% of requests, and those fall to -0.14, -0.03 and -0.09, Cholla drops from first to third, and only rent burden keeps its link (+0.70).

**Limit to name:** with n = 6 districts, rho is descriptive and carries no p-value.

**Transition:** "So the income pattern tracks Trash/Recycle. Shenoy shows which Trash/Recycle requests those are, and how the same mix lines up with time-to-close."

### 2b. Time-to-close (F-01)

**Speaker:** Shenoy · **Chart:** `outputs/iter2/time_to_close/raw_vs_type_corrected_by_district.png` (backup for questions: `outputs/iter2/time_to_close/type_corrected_share_by_district.png`, `outputs/iter2/time_to_close/heatmap_median_days_district_by_type.png`)

Before accounting for request type, the median closed request takes 2 days in Ocotillo and 5 in Cholla, and the share of requests slower than the citywide median is 14.5 points apart from the highest district to the lowest. Since the City's escalation targets are not downloaded yet, we compare each request with the typical time for its own exact type (the citywide median across 155 types), and the gap shrinks to 3.2 points, from 41.0% in Ocotillo to 44.2% in Cactus. That means about 78% of the raw gap lines up with type mix. The 17 broad type groups only narrow it to 12.1 points, since they hide the mix inside them: Residential - Container Damaged, a type that typically takes 6 days, is 79% of Cholla's Trash/Recycle requests but 46% of Ocotillo's, while within that type district medians run only from 6 to 7 days.

**Limit to name:** closed requests only, so the most recent months lean fast (91.3% of 2026-07 requests were closed by the extract date).

### The connecting thread (Shenoy closes the analysis with it)

Both analyses come back to the same requests. Without Trash/Recycle, Cholla drops from first to third and the rate's link to income, renters and language fades to near zero (F-02). Inside Trash/Recycle, Residential - Container Damaged dominates Cholla's requests (79%, against 46% in Ocotillo), and it is the clearest piece of the type mix associated with about 78% of the time-to-close gap (F-01). We have not run the income correlation on Container Damaged alone, so we do not claim that link.

**Transition:** "These are rates and shares over all 79 months. Akshara shows how the raw monthly counts moved inside that window."

## 3. Data visualization

**Speaker:** Akshara · **Charts:** `outputs/iter2/trend/monthly_trend_by_district.png`, with `outputs/iter2/trend/trend_charts.html` open for hover

Six panels, one per district, on the same 0 to 500 scale, show raw monthly request counts from January 2020 to July 2026. Every district filed fewer requests in 2024 than in 2023 (citywide 16,778 to 14,336, -14.6%; Cactus -22.4%), Cactus spiked to 408 in May 2023, and November 2024 was the citywide low at 819. From January to July 2026, against the same months of 2025, the districts split: Yucca (+17.5%) and Barrel (+15.3%) rose while Cholla (-11.2%) and Sahuaro (-11.6%) fell, so any rate over the full window blends years with different volume.

**Limit to name:** raw counts, not per resident, and descriptive only; nothing here tests why a month stands out.

**Transition:** "Every chart on the page follows the same rules as this one, and so does the page as a whole."

## 4. Presentation style

**Speaker:** Akshara · **Chart:** none (the page itself)

The page tells one story in order, from the problem through the two analyses and the thread that joins them, then the trend and what changed since Iteration 1. Every chart title states its finding, district names are in Title Case, and the wording stays associative ("lines up with", "tracks"), since six districts can show a pattern but not why it exists. Before the talk we checked every chart for what is unclear at a glance, and each of us presents the piece we built.

**Transition:** "Ma'el closes with what changed since Iteration 1, including one change to the plan."

## 5. Progress since Iteration 1

**Speaker:** Ma'el · **Chart:** none

In Iteration 1 we proposed requests per 1,000 residents, the most repeated request types by district, and time-to-close against the City's response targets. This round delivers that rate with a chi-square test and five district traits, measures time-to-close against each request's own type and adds the monthly trend, while the Code Compliance comparison and district request signatures move to the final iteration. Our open challenge last time was that data can show a pattern but not why, so now effect sizes lead and every correlation is labelled descriptive. All of it runs from a shared repo with written standards and a decision log, and every number on the page traces to a merged findings file there.

### Scope change (Ma'el says this plainly)

In Iteration 1 we planned to score time-to-close against the City's own response targets. Those targets sit in the GlendaleOne Escalations table, which is not downloaded yet, so Iteration 2 compares each closed request with the typical time for its own exact request type: the citywide median for that type, across 155 types. Nothing in this talk is scored against the City's targets, and no request is called fast or slow against them. That is a limit of the data we hold so far, and the page says so. The target-based version waits until the table is downloaded.

### Challenges (data and method limits)

- **n = 6 districts.** Each rho is descriptive with no p-value, and one district changing places moves it a lot.
- **Raw counts vs per resident.** The trend chart counts requests; only the rate chart divides by population (Esri 2026).
- **Closed-only timing.** Requests still open on the extract date are missing, so the most recent months lean fast (91.3% of 2026-07 requests were closed).
- **No City targets.** Nothing is scored against them (see the scope change above).
- **ACS margins of error.** Internet access, language and rent burden are ACS 2020-24 estimates; districts that differ by less than their margins read as similar.
- **Yucca's denominator gap.** Esri 2026 counts 53,147 residents and ACS 2020-24 counts 42,931, which moves Yucca's rate from 50.6 to 62.6 and its rank from fifth to third.

**Close:** back to the so-what line, then questions.

---

## Chart readability pass

- `request_rate_by_district_esri.png`: the point lands at a glance. Keep as is.
- `scatter_panels_covariates.png`: the densest chart (five panels, each with and without Trash/Recycle). Shamie points at the income and rent burden panels only, and quotes only the rho values in the findings file.
- `raw_vs_type_corrected_by_district.png`: bar labels are rounded to whole percents, so say the gaps (14.5 and 3.2 points) rather than reading labels. Ocotillo's share edges up slightly after the type control; expect a question on it.
- `heatmap_median_days_district_by_type.png`: the Trash & debris column shows 0, which is a same-day close, not missing data. Say so if the chart comes up.
- `monthly_trend_by_district.png`: only Barrel and Cactus carry labels; the hover in `trend_charts.html` covers the other panels.

## Number sources

TTC = `outputs/iter2/time_to_close/findings.md` (F-01) · PROP = `outputs/iter2/propensity/findings.md` (F-02) · TREND = `outputs/iter2/trend/findings.md` (F-03)

| Number on the page | Source (file, line) |
|---|---|
| 104,274 requests; six districts | PROP line 19 (n = 104,274); TREND lines 10 and 43 |
| January 2020 to July 2026, 79 months | PROP line 7; TREND line 8 |
| 2026-08-06 extract | PROP line 5; TTC line 5; TREND line 7 |
| Cohen's w = 0.165; chi-square test | PROP lines 15 and 19 |
| Cholla 72.9 per 1,000 residents per year; 1.56x; Cactus 46.8; citywide 59.7 | PROP line 21 (per 1,000 also line 13) |
| Cholla the highest-income and highest-rate district | PROP line 23 |
| rho +0.43, -0.60, -0.66 | PROP line 23 |
| Trash/Recycle Services 48.9% of requests | PROP lines 23 and 51 |
| rho -0.14, -0.03, -0.09 without Trash/Recycle; rent burden +0.70 | PROP line 23 |
| Cholla first to third without Trash/Recycle | PROP line 28 |
| n = 6 districts | PROP line 32 |
| five district traits | PROP line 15 (five covariates) |
| Yucca 53,147 (Esri 2026) vs 42,931 (ACS 2020-24); 50.6 to 62.6; fifth to third | PROP lines 27 and 35 |
| Median 2 days Ocotillo, 5 days Cholla | TTC line 13 |
| 14.5-point raw gap; 3.2 points; 41.0% Ocotillo; 44.2% Cactus; about 78% | TTC line 14 |
| 155 exact types; 17 type groups; 12.1 points | TTC lines 9 and 14 |
| Container Damaged citywide median 6 days; 79% of Cholla's vs 46% of Ocotillo's Trash/Recycle requests; district medians 6 to 7 days | TTC line 15 |
| 91.3% of 2026-07 requests closed | TTC line 19 |
| 0 = same-day close (heatmap note) | TTC line 7 |
| Six panels on a 0 to 500 scale | TREND line 58 |
| 16,778 (2023) to 14,336 (2024), -14.6%; Cactus -22.4% | TREND line 16 |
| Cactus 408 in May 2023 | TREND line 17 |
| November 2024 citywide low, 819 | TREND line 25 |
| Jan-Jul 2026 vs 2025: Yucca +17.5%, Barrel +15.3%, Cholla -11.2%, Sahuaro -11.6% | TREND line 18 |
| Five panels (scatter chart note) | PROP line 68 |

Nothing is left to fill: every number above is in a merged findings file.
