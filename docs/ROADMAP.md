# Roadmap

Where the team is going and when. Only the class date is firm; everything else is a planning estimate. Changes to dates go through a PR, with a `CHANGELOG.md` line and, where a decision changes, a row in `docs/DECISIONS.md`.

## Iteration 2 – in-class presentation, Mon 2026-10-19

**Scope:** the reporting-propensity gap (Q1) and time-to-close by district, controlled for request type. Cards are in [`docs/tasks/`](tasks/README.md).

| Date | Milestone |
|---|---|
| Sun 2026-09-27 | Cards start |
| Thu 2026-10-01 | First check-in with first artifacts |
| Sun 2026-10-04 | iter2-03 PR ready |
| Thu 2026-10-08 | Draft PRs for iter2-01 and iter2-02; storyline outline posted |
| Sun 2026-10-11 | iter2-01 and iter2-02 PRs ready |
| Mon 2026-10-12 | Grace day |
| Tue 2026-10-13 | Chart review |
| Wed 2026-10-14 | Section copy done |
| Fri 2026-10-16 | Content freeze; run sheet |
| Sun 2026-10-18 | Rehearsal, 18:00 |
| Mon 2026-10-19 | Present in class |

## Gantt

```mermaid
gantt
    title Iteration 2 – present Mon 10-19 (crit = critical path)
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    section Setup
    M0 setup and data share (Ma'el)        :crit, m0, 2026-09-26, 1d
    section Analysts
    iter2-01 propensity gap (Shamie)       :crit, t1, 2026-09-27, 15d
    iter2-02 time-to-close (Shenoy)        :t2, 2026-09-27, 15d
    iter2-03 monthly trend (Akshara)       :t3, 2026-09-27, 8d
    Review iter2-03 (Shenoy)               :r3, 2026-10-05, 2d
    Review iter2-01 (Ma'el)                :crit, r1, 2026-10-09, 2d
    Review iter2-02 (Shamie)               :r2, 2026-10-09, 2d
    section Story
    iter2-04 storyline outline (Akshara)   :s1, 2026-09-27, 12d
    iter2-04 section copy (Akshara)        :s2, 2026-10-09, 6d
    iter2-05 chart review (Akshara)        :s3, 2026-10-13, 1d
    iter2-05 run sheet (Akshara)           :s4, 2026-10-15, 2d
    section Ma'el
    M1 spatial join                        :m1, 2026-09-27, 15d
    Grace day                              :crit, g, 2026-10-12, 1d
    M3 integration QA                      :crit, m3, 2026-10-13, 2d
    M4 HTML build                          :crit, m4, 2026-10-15, 2d
    section Class
    Content freeze                         :milestone, crit, 2026-10-16, 0d
    Rehearsal 18:00                        :milestone, crit, 2026-10-18, 0d
    Present                                :milestone, crit, 2026-10-19, 0d
```

- **Critical path:** M0 → iter2-01 (Shamie) → Ma'el's review → grace day → M3 → M4 → freeze → rehearsal → present. iter2-01 is on it because it is the longest card and feeds the headline finding.
- **Buffer:** Mon 10-12 (grace) and Sat 10-17 (float), plus 20% of everyone's hours.
- **Estimates vs firm dates:** only 10-19 (class) is firm. The 18:00 rehearsal repeats the Iteration 1 pattern [confirm with the team]. Everything else is a planning estimate.

## Check-in calendar

Check-ins are async in the group chat every Mon and Thu (Progress / Plans / Problems; see `CONTRIBUTING.md`).

| Date | What Ma'el looks for |
|---|---|
| Mon 09-28 | Everyone has the data downloaded and the load block printing the expected counts |
| Thu 10-01 | First artifacts: Shamie's rates table, Shenoy's filter counts and district table, Akshara's draft chart |
| Mon 10-05 | Akshara's trend PR in review; Shamie's and Shenoy's tests run |
| Thu 10-08 | Draft PRs open for iter2-01 and iter2-02; storyline outline posted |
| Mon 10-12 | Grace day: everything merged or in the missed-deadline protocol |
| Thu 10-15 | Integration QA done; chart flags fixed; HTML build in progress |

## Risks (top 5)

| ID | Risk | L | I | Owner | Mitigation | Early signal / review |
|---|---|---|---|---|---|---|
| R1 | iter2-01 runs long (C3, on the critical path) | 3 | 4 | Ma'el | Stretch step (Gini) is cut first; first-artifact check on 10-01 | No rates table by Thu 10-01 |
| R2 | Setup friction (Drive download, pip, paths) | 3 | 3 | Ma'el | Exact paths and expected counts on every card | Load block counts not posted by Mon 09-28 |
| R3 | Only Ma'el can do the HTML build and the spatial join | 2 | 4 | Ma'el | README beside the join output; storyline makes the HTML build mechanical | M1 not done by Sun 10-11 |
| R4 | A slide implies causation from 6 districts | 3 | 3 | Ma'el | Wording rules on cards 01, 02 and 04; M3 wording pass | Causal verbs in any findings.md |
| R5 | The scope change reads as "no progress" | 2 | 3 | Akshara | Scope-change paragraph required in iter2-04 | Missing from the 10-08 outline |
