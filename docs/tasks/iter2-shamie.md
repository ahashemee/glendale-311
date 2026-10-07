# Iteration 2 – Shamie

**Reviewer:** Ma'el · **Questions:** group chat, any time. Ask early.
How-to (load block, filters, chart rules): `docs/ANALYSIS_STANDARDS.md`. Outputs go in `outputs/iter2/propensity/`.

## Tasks

| # | Task | Due |
|---|---|---|
| 1 | Quick data check of the two cleaned demographic files (do the populations and columns look right? tell me anything odd), then a table of requests per 1,000 residents per year by district, using both the Esri 2026 and the ACS population. Post the table in the chat. | Thu 2026-10-01 |
| 2 | Do request counts match population shares? Chi-square goodness-of-fit with Cohen's w as the headline. A table of the district covariates (median income, renter share, no internet, Spanish with limited English, rent burden) and Spearman rho of each against the request rate. A first bar chart of rate by district. Open a draft PR. | Sun 2026-10-04 |
| 3 | Post your share-out on the PR, comment on Shenoy's PR, join the call. | Mon 10/5 · Tue 10/6 · Wed 10/7 |
| 4 | Scatter panels of rate against each covariate, `findings.md`, any change from my synthesis. PR ready for review. | **Sun 2026-10-11 (hard)** |

## What I'm looking for

- The headline of the talk: does any district file far more or less than its share of the population, and how big is the gap (Cohen's w, not the p-value, which will be tiny with 100k requests)?
- Whether the rate lines up with income, internet access, language or rent burden. With six districts this is descriptive: report rho, no p-values, "lines up with" never "causes".
- The same answer both ways: Esri vs ACS population, and with Trash/Recycle (about half of all requests) taken out. One line each in `findings.md` on whether the ranking changed.
- Window 2020-01 to 2026-07, requests with no district excluded and counted. Numbers computed by you, not taken from `PROJECT.md`.
- In the PR: the tables and charts in `outputs/iter2/propensity/`, `findings.md` with three findings that each have a number, notebook outputs cleared, a CHANGELOG line.
