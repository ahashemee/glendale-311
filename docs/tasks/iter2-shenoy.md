# Iteration 2 – Shenoy

**Reviewer:** Ma'el · **Questions:** group chat, any time. Ask early.
How-to (load block, filters, chart rules): `docs/ANALYSIS_STANDARDS.md`. Outputs go in `outputs/iter2/time_to_close/`.

## Tasks

| # | Task | Due |
|---|---|---|
| 1 | Quick data check of `glendaleone_clean.csv` (dates, status, close dates: does it look right? tell me anything odd), then a table of days-to-close by district for closed requests (n, mean, median, p90, share closed same day). Post the table in the chat. | Thu 2026-10-01 |
| 2 | Type-corrected version: for each district, the share of requests slower than the median for their own request type; a district x request-type table of median days for the 8 biggest types; Kruskal-Wallis and chi-square with effect sizes. A first bar chart of the type-corrected share by district. Open a draft PR. | Sun 2026-10-04 |
| 3 | Post your share-out on the PR, comment on Akshara's trend PR, join the call. | Mon 10/5 · Tue 10/6 · Wed 10/7 |
| 4 | Heatmap of median days (district x request type), `findings.md`, any change from my synthesis. PR ready for review. | **Sun 2026-10-11 (hard)** |

## What I'm looking for

- Do districts really differ in how fast requests close once request type is accounted for, and how much of the raw difference was just type mix (Trash/Recycle is about half of everything)?
- Closed requests only, window 2020-01 to 2026-07, drop the one request that closes before it was opened (don't fix it). Report how many rows each filter removed.
- Say "slower than typical for its type", never "late" or "missed target": we don't have the City's targets yet.
- Each chart's title states the finding, bars start at zero. No causal wording.
- In the PR: the tables and charts in `outputs/iter2/time_to_close/`, `findings.md` with three findings that each have a number, notebook outputs cleared, a CHANGELOG line.
