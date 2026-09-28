# Findings (living)

The team's current state of knowledge. Every entry points to the evidence that backs it. When a merged analysis changes the story, update this file in the same PR and propose the matching edit to the **Direction (living)** section of `CLAUDE.md`.

No validated findings yet. PROJECT.md section 7 figures are orientation only.

## Validated findings

*None yet.* Add entries in this format, newest first:

```
### F-NN – one-sentence finding with its number and comparison
- Evidence: outputs/iterN/<topic>/findings.md (and the CSV or chart)
- Card: [iterN-NN] · Merged: YYYY-MM-DD · Window and denominator: ...
- Caveats: ... `[uncertain]` where a fact is not verified
- Hypothesis it bears on: H1 / H2 / H3 (supports, weakens, unclear)
```

## Working hypotheses

From `docs/DELIVERABLE_IDEAS.md`. None of these is tested yet, and each is phrased as an association to check, not a cause.

- **H1 – Reporting-propensity gap** `[unvalidated]`. Request volume per resident may line up with who reports (income, internet access, language, rent burden) more than with need, so the highest-income districts could file the most requests per resident. Tested by `[iter2-01]`.
- **H2 – District request signatures** `[unvalidated]`. The equity signal may sit in the *mix* of request types rather than the volume: some groups, such as Assistance Programs, may be concentrated in lower-income districts once trash containers are set aside. Planned for the final iteration.
- **H3 – Response equity against the City's own clocks** `[unvalidated]`. Raw days-to-close differ by district, but type mix may explain much of it; scoring each request against its type (and later against the City's escalation times) tests whether response is equitable. Iteration 2 tests the type-controlled version in `[iter2-02]`; the escalation-time version is blocked until the targets table is downloaded.
