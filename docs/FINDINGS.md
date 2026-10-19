# Findings (living)

The team's current state of knowledge. Every entry points to the evidence that backs it. When a merged analysis changes the story, update this file in the same PR and propose the matching edit to the **Direction (living)** section of `CLAUDE.md`.

One finding so far (F-01). PROJECT.md section 7 figures are orientation only.

## Validated findings

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

From `docs/DELIVERABLE_IDEAS.md`. None of these is tested yet, and each is phrased as an association to check, not a cause.

- **H1 – Reporting-propensity gap** `[unvalidated]`. Request volume per resident may line up with who reports (income, internet access, language, rent burden) more than with need, so the highest-income districts could file the most requests per resident. Tested by Shamie's Iteration 2 piece.
- **H2 – District request signatures** `[unvalidated]`. The equity signal may sit in the *mix* of request types rather than the volume: some groups, such as Assistance Programs, may be concentrated in lower-income districts once trash containers are set aside. Planned for the final iteration.
- **H3 – Response equity against the City's own clocks** `[supported]` (type-controlled version, F-01). Raw days-to-close differ by district, but type mix may explain much of it; scoring each request against its type (and later against the City's escalation times) tests whether response is equitable. Iteration 2 tests the type-controlled version in Shenoy's Iteration 2 piece; the escalation-time version is blocked until the targets table is downloaded.
