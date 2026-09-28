# Deliverable Ideas — Glendale 311 Strategic Briefing

Companion to [`PROJECT.md`](./PROJECT.md). Written 2026-09-16 for team discussion; three
analytical deliverables, each scoped to one data pull or technique. Data status is judged
against `DATA_DICTIONARY.md`. Numbers quoted below come from `PROJECT.md` §7 and are
**unvalidated orientation**, not findings — recompute from `src/` before citing.

**Decomposition of "how can GlendaleOne serve residents more equitably":**
(a) does request *volume* track need or reporting access;
(b) which *kinds* of requests are district-specific;
(c) is *response* equitable once type mix is controlled.

---

## 1. The Reporting-Propensity Gap

- **What it answers:** Q1 directly, and Q5 candidate (i).
- **Why it matters:** First-pass numbers show CHOLLA (median income $118K) files ~485
  requests per 1,000 residents while CACTUS files ~311 — a 1.56× spread that runs *with*
  income, not against it. Raw volume is therefore measuring who knows how to use 311, not
  who needs service. The actionable insight is which districts are under-reporting relative
  to plausible need, and which access barriers (internet, language, rent burden) co-vary
  with it.
- **How to build it:**
  - Tables: `GlendaleOne_External_Requests.csv` (`Council_District`, `Request_Type_Group`);
    `Demographic_and_Income_Profile_<DISTRICT>.xlsx` (Esri 2026 Total Population, Median
    Household Income); `ACS_Population_Summary_<DISTRICT>.xlsx` (No Internet Access, Speak
    English "not well", Gross Rent 50%+).
  - Status: **confirmed.** Caveat: n=6, so covariate relationships are descriptive, not
    inferential; report ACS MOEs.
  - Method: requests per 1,000 by district × request group (excluding `'N/A'`/`NONE`), Gini
    across districts, then rank against each covariate; rerun with the ACS denominator as
    sensitivity.
  - Tools: Python (pandas, openpyxl anchored parse); Power BI.
  - Output: ranked table plus small-multiple scatter (rate vs each covariate), one panel per
    request group.

## 2. District Request Signatures

- **What it answers:** Q3 and Q4 together, one model.
- **Why it matters:** Composition, not volume, carries the equity signal. Assistance
  Programs requests are ~27% OCOTILLO and ~4% CHOLLA — a near-inverse of income — while
  Street Lighting is disproportionately CHOLLA. Trash containers dominate everywhere and
  will mask this unless removed. The insight is a per-district "signature" showing which
  service needs are geographically concentrated and where the City's mix of responders
  should follow.
- **How to build it:**
  - Tables: `GlendaleOne_External_Requests.csv` (`Council_District`, `Request_Type_Group`,
    `Request_Type`); `Demographic_and_Income_Profile_<DISTRICT>.xlsx` (Esri 2026 population
    for expected counts).
  - Status: **confirmed.**
  - Method: chi-square on district × request group with standardized residuals (cells
    over/under-represented), Cramér's V, and both conditional probabilities —
    P(type | district) and P(district | type) — labeled separately since the client's
    wording implies the latter; Jensen–Shannon distance between district profiles to
    cluster them.
  - Tools: Python (scipy.stats); Power BI heatmap.
  - Output: residual heatmap, two probability matrices, district similarity dendrogram.

## 3. Response Equity Against the City's Own Clocks

- **What it answers:** Q5 candidates (ii)–(iii): is *response*, not just volume, equitable.
- **Why it matters:** Raw median days-to-close (OCOTILLO 2, CHOLLA 5) is confounded by type
  mix — a container swap closes in a day, a sidewalk repair does not. Scoring each request
  against its type's published escalation timer controls for mix and reframes the finding
  in the City's own service-level language.
- **How to build it:**
  - Tables: `GlendaleOne_External_Requests.csv` (`Request_Type`, `Request_Date`,
    `Close_Date`, `Council_District`); `GlendaleOne_Escalations` (`Request_Type_Name`,
    `Escalate_Time1`, `Escalates_in_`).
  - Status: **likely — BLOCKER.** The escalations table is inventoried
    (`DATA_LANDSCAPE.md` §2.6) but not in the data dictionary or `data/`; it needs a
    one-command download. Only 132 of 155 request types match by name (91.6% of rows) even
    after trimming whitespace, and whether `Escalate_Time1` is the target departments are
    held to is unconfirmed (`PROJECT.md` §11 Q6). Requests are date-only, so same-day
    closes read as zero.
  - Method: flag `Close_Date − Request_Date > Escalate_Time1`, then share-past-target by
    district × request group.
  - Tools: Python; Power BI.
  - Output: district × group "past-target %" matrix.

---

## Verification notes

- Table names match `DATA_DICTIONARY.md` (`GlendaleOne_External_Requests.csv`, the two
  workbook families). `GlendaleOne_Escalations` is named from `DATA_LANDSCAPE.md` §2.6 and
  is why idea 3 is a blocker, not a plan.
- Ideas 1 and 2 rest entirely on confirmed data and can start now. Both need the
  denominator (§6.8) and unassigned-district (§6.6) decisions made once (§11 item 19).
- No idea depends on the code-compliance district join (§6.1), which remains the single
  largest unblocked prerequisite for anything on the code side (Q1/Q2/Q4 code halves).
- Each idea moves past "district X is high" to a mechanism: access barriers, need
  concentration, or type-adjusted response.

## Not chosen (for the record)

- Proactive vs reactive code enforcement by district (Q5 iv) — blocked on §6.1 district join.
- Q2 at `Request_Group` granularity — blocked on the same escalations download plus a hand
  mapping for 8 code types (§6.12).
