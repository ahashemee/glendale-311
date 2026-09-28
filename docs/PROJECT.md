# CIS 450 Group Project — City of Glendale "GlendaleOne" 311 Equity Analysis

> **Read this first, every session.** This file is the single source of truth for the
> project. It is written so a brand-new Claude Cowork chat can pick up the work without
> re-reading the raw data or re-deriving context. Load the companion files only when you
> need their detail:
> - [`DATA_DICTIONARY.md`](./DATA_DICTIONARY.md): column semantics of the two local CSVs and the 12 Esri workbooks.
>   It predates the 2026-09-16 findings; where it conflicts with §6 below, this file wins.
> - [`DATA_LANDSCAPE.md`](./DATA_LANDSCAPE.md): every other dataset the City publishes, with schemas, join keys
>   and 19 evidence-backed questions for the sponsor.
> - [`PORTAL_RECON.md`](./PORTAL_RECON.md): the email attachments check, the OpenBook budget portal and the GIS map gallery.
>
> Last updated: 2026-09-16 · Maintainer: Ma'el (Amaan) Hashemee · Update the Changelog at the bottom when you change anything.

---

## 1. At a glance

| | |
|---|---|
| **Client** | City of Glendale, Arizona — Office of Organizational Performance / Data team |
| **Client contact** | Stephen Gushue (offers a "Book time with me" scheduling link in his signature) |
| **Faculty / course contact** | Tamuchin McCreless (ASU, CIS 450) |
| **Subject** | GlendaleOne — the City's 311 service request system |
| **Core theme** | **Service equity across the six Council Districts** |
| **Deliverable** | ⚠️ **NOT ANNOUNCED YET** — see §11 |
| **Due date** | ⚠️ **NOT ANNOUNCED YET** |
| **Status** | Kickoff. Data acquired and profiled (2026-09-05). Budget portal and GIS gallery explored, and every published City dataset inventoried from metadata (2026-09-16). No analysis committed yet. |
| **Project folder** | `Desktop/ASU Courses/FA26/CIS 450/Group Project/` (this folder), data in `./data/`. The Desktop syncs to iCloud; see §4.1. |

**Client's framing, verbatim from the email:**

> GlendaleOne is the City of Glendale's 311 service where residents can provide feedback
> and requests for issues they are experiencing. It is a part of our objective of greater
> transparency and improving the lives of the people we serve every day.

Note the client's own words: *"greater transparency"* and *"improving the lives of the
people we serve."* Findings should be framed as actionable for a city audience, not as an
academic exercise.

---

## 2. The five questions (client's exact wording)

These are copied verbatim from Stephen Gushue's email. Do not paraphrase them in
deliverables without keeping the original alongside.

1. **Are the request counts distributed equitably based on Council District populations?**
2. **What are the top 10 (or n) request types differing between GlendaleOne requests and code requests?**
3. **What are the probabilities of certain request types coming from each district?**
4. **What are the similarities and disparities in requests counts, types per each district?**
5. **Other items of interest that the city may not be seeing.**

Question 5 is the open-ended one and is where the group can differentiate. Candidate
angles are listed in §8.

---

## 3. Source of the assignment

| Field | Value |
|---|---|
| Thread subject | `FW: ASU Data Analytics Project` |
| Forwarded by | Stephen Gushue → the ASU student list, **Fri 4 Sep 2026 16:24 UTC** |
| Original message | Gushue → Tamuchin McCreless, **Fri 21 Aug 2026 11:03 AM** |
| Attachments | 12 Esri `.xlsx` demographic workbooks (already downloaded to `./data/`) + 1 signature image. Re-checked 2026-09-16: all 12 present with the expected names, none missing (`PORTAL_RECON.md` Task 1). |

Gushue's cover note: *"Since only a few people showed up, here are the data and questions
related to this project for the City of Glendale."* and, to the professor, *"Please let me
know when your teams are ready to meet."* → **There is a standing offer of a client
meeting that has not been scheduled.** See §11.

---

## 4. Data inventory

The two CSVs and 12 workbooks are in `./data/`. Everything else the City publishes is
cataloged in `DATA_LANDSCAPE.md` and summarized in §4.4 and §10.

### 4.1 Primary datasets (downloaded 2026-09-05 from the ArcGIS Feature Services)

| File | Rows | Cols | Size | Date coverage |
|---|---|---|---|---|
| `GlendaleOne_External_Requests.csv` | **107,646** | 16 | 24 MB | `Request_Date` 2019-12-02 → **2026-08-05** |
| `Code_Compliance_Cases_GlendaleOne.csv` | **56,294** | 51 | 19 MB | `RequestDate` 2019-12-03 → **2026-09-03** |

These were pulled record-by-record from the live ArcGIS REST endpoints (the portal's
one-click CSV export returns an empty file). Epoch-millisecond date fields were converted
to `YYYY-MM-DD HH:MM:SS` **UTC** strings at download time.

**Live services vs the local extracts, checked 2026-09-16** (counts only, no rows downloaded):

| Dataset | Live rows | Live date coverage | Live `DateLoaded` | Extract status |
|---|---|---|---|---|
| GlendaleOne External Requests | 107,646 | `Request_Date` 2019-12-02 → 2026-08-05 | 2026-08-06 | Identical row count. The City's feed has not loaded since 2026-08-06. |
| Code Compliance Cases | **56,431** | `RequestDate` 2019-12-03 → **2026-09-09** | 2026-09-10 | **137 cases behind** |

⚠️ **The CSVs are iCloud placeholders on Ma'el's Mac.** As of 2026-09-16, macOS flags both as
`dataless`: their listed size is 24 MB and 19 MB, but 0 B is stored on disk. The first
read downloads them, so they are not usable offline until opened once.

**No refresh command works right now.** The old helper `~/dl_logs/resume.py` and the
`~/mnt/CIS 450/...` output paths are gone from this machine (checked 2026-09-16). To
refresh, a new resumable downloader has to be written into `src/` and pointed at these
endpoints:
- `https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services/GlendaleOne_External_Requests/FeatureServer/0`
- `https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services/GlendaleOne_Code_Compliance_Cases/FeatureServer/0`

Portal pages (human-readable):
- GlendaleOne External Requests — https://opendata.glendaleaz.com/datasets/37a2cb9cf728424d8c0f5c1f64621939_0/explore
- Code Compliance Cases — https://opendata.glendaleaz.com/datasets/8026de93be8147d2aa2941c3e7ceed97_0/explore

### 4.2 Demographic workbooks (email attachments, 12 files)

Two Esri Business Analyst report types, one file per Council District, six districts each:

| Family | Files | Layout | Vintage |
|---|---|---|---|
| `ACS_Population_Summary_<DISTRICT>.xlsx` | 6 | 1 sheet named after the district, 373 rows × 6 cols | ACS **2020–2024** 5-year estimates, with MOE |
| `Demographic_and_Income_Profile_<DISTRICT>.xlsx` | 6 | 1 sheet named after the district, 222 rows × 7 cols | Census 2020 actual + Esri **2026** estimate + Esri **2031** projection |

⚠️ These are **formatted reports, not tidy tables.** They have stacked section blocks,
repeated header rows, and merged-looking layouts. Never `pd.read_excel()` them naively —
see `DATA_DICTIONARY.md` §3 for the row map and a parsing recipe.

### 4.3 Not downloaded, but one command away

The **Council Districts polygon layer** is the missing piece for Question 1 on the code
compliance side (see §6.1). The hosted layer has 7 polygons: the six districts plus
`NONE`. It was last edited 2024-12-09. Run from this folder:

```bash
curl -sL "https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services/Glendale_Council_Districts/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson" -o "data/Glendale_Council_Districts.geojson"
```

The City's Enterprise server has a second copy with only the 6 districts and no `NONE`
polygon: `https://gismaps.glendaleaz.com/gisserver/rest/services/AdminAreas/Council_Districts/MapServer/0`.

**Address → district crosswalk (no GIS needed).** Two layers exist:
- **`Address_Points_By_Council_Districts` (AGOL):** the one named here before. It was last edited **2024-08-29**
  and holds 109,404 points.
- **`LN_ADDRESS_PT_APN_JOIN` (Enterprise):** newer, edited **2026-09-07**. It holds 125,686 points,
  including 12,957 tagged `NONE`, and also carries the parcel `APN`:
  `https://gismaps.glendaleaz.com/gisserver/rest/services/LN_ADDRESS_PT_APN_JOIN/MapServer/0`

### 4.4 Published-data landscape (inventoried 2026-09-16)

`src/harvest_metadata.py` read metadata only (schemas, counts and statistics; no rows) from
these sources:

- **ArcGIS Online:** 253 services in the City's AGOL org `9fVTQQSiODPjLUTa`.
- **Enterprise GIS servers:** 147 services on `gismaps.glendaleaz.com/gisserver` and 7 on `/cseam`.
  17 more folders there require a login.
- **Open Data portal:** its catalog of 34 items, used to cross-reference which AGOL items are public-facing.

104 services were set aside as noise (Survey123 forms, tests, basemaps). The rest are rated in
`DATA_LANDSCAPE.md` §1: 14 High, 14 Medium, 101 Low and 187 None.

The datasets beyond the two CSVs and the workbooks that matter most (DATA_LANDSCAPE.md
section numbers in brackets):

| Dataset | What it adds | Rows | [§] |
|---|---|---|---|
| **GlendaleOne Escalations** | The request-type catalog: department, Level-1 route and escalation time (in days for 154 types, hours for 1) for every GlendaleOne request type. See §6.12. | 155 | 2.6 |
| **Census 2020 block population points** (Enterprise `PopDensity/Census_Block_2020_pts`) | Official Census 2020 counts per block (P.L. 94-171 tables P1–P5 and H1). Blocks sum to 294,866 people, more than the six districts, so the layer extends past them. | 3,471 | 2.12 |
| **Block groups with Esri demographics + HUD QCT** (Enterprise `Community_Services/Glendale_qct_rates`) | Current-year Esri income, tenure and home value, plus HUD Qualified Census Tract flags (64 of 222 flagged) and 2016–2018 ACS poverty fields | 222 | 2.19 |
| COG child poverty tracts | Tract-level households below poverty and children under 15 (last edited 2021) | 88 | 2.20 |
| **City parcels** (Enterprise `Parcels`) | `DIS_NAME`, land use, zoning, `APN` per parcel. 237 parcels lack a district. | 88,762 | 2.17 |
| Assessor parcel view (Enterprise) | Property use code, build year, owner mailing address vs situs address | 89,001 | 2.18 |
| 100-block address points (Enterprise) | Candidate key for the requests' `FULL_ADDRESS`, but it covers only 5 street types | 2,703 | 2.15 |
| **Police Calls for Service** | District-tagged demand signal from police dispatch, 2020-01-01 → 2026-09-08; the portal says it refreshes daily | 1,138,221 | 2.25 |
| Registered neighborhoods with HOA / management company (Enterprise) | HOA flag (111 Y), management company, council district per neighborhood | 255 | 2.23 |
| Police grid (Enterprise `POLICE_GRID`) | Grid cell → beat → council district (`CC_DIST`) | 650 | 2.22 |
| Sanitation day routes / routes / inspection areas (Enterprise) | Collection day and route polygons for the trash request types | 7 / 33 / 20 | 2.24 |
| Code Compliance Sub Grid | 72 sub-zones assigned to 9 named inspectors ("Quarter 1"); its date fields are empty | 72 | 2.21 |
| **Water Distribution Service Requests** (Survey123) | Resident requests submitted outside GlendaleOne, 2019-04-29 → 2025-06-02 | 10,081 | 2.26 |
| GlendaleOne Public and Council Report; Code Compliance Public Dashboard | Power BI reports; not opened; no API | — | 2.27–2.28 |

To refresh the inventory with current counts, run `python3 src/harvest_metadata.py --refresh`,
then `python3 src/build_landscape.py`. Without `--refresh` the script reuses its cache.
Numbers typed into the prose of `DATA_LANDSCAPE.md` do not update automatically.

---

## 5. Council District reference table

Glendale has **six named districts** (not numbered). The name is the join key everywhere.

| District | Council member¹ | Census 2020 pop | Esri 2026 pop | ACS 2020–24 pop | Median HH income (2026) | Per-capita income (2026) | Esri diversity index |
|---|---|---|---|---|---|---|---|
| BARREL | Bart Turner | 41,139 | 42,736 | 42,630 | $69,507 | $34,241 | 83.2 |
| CACTUS | Ian Hugh | 43,132 | 42,913 | 44,191 | $60,854 | $27,293 | 86.8 |
| CHOLLA | Lauren Tolmachoff | 39,584 | 40,324 | 39,494 | **$118,221** | $56,254 | 58.0 |
| OCOTILLO | Leandro Baldenegro | 42,672 | 42,963 | 43,155 | **$57,269** | **$22,338** | 86.0 |
| SAHUARO | Ray Malnar | 42,122 | 43,382 | 40,956 | $90,300 | $42,932 | 67.1 |
| YUCCA | Joyce Clark | 39,994 | **53,147** | 42,931 | $104,032 | $39,179 | 87.2 |
| *(NONE)* | — | — | — | — | — | — | — |

¹ From the GIS layer's `MEMBER` field, last edited **2024-12-09**. The same six names were
still in the hosted layer on 2026-09-16, but the harvest did not re-check which name goes
with which district. **Verify on the City website before putting a council member's name
in a deliverable.**

`NONE` has `HANSEN_DISTRICT = 'MC'` and exists only in the hosted AGOL layer, not in the
Enterprise copy (§4.3).

**The income spread is the story-shaped fact here:** CHOLLA's median household income is
**2.06×** OCOTILLO's. Any equity claim should be tested against income and the diversity
index, not population alone.

---

## 6. Critical data facts and gotchas

Read this section before writing any analysis code. Each item below has already burned
time or will. Items 6.12–6.15 were added on 2026-09-16.

### 6.1 🔴 Code Compliance has **no usable district field**
The `District` column exists but is empty on every row. In the live service it holds an
**empty string (`''`) on all 56,431 rows**, not NULL. In the local CSV it reads as blank
(56,294 rows). Question 1 and Question 4 require district on both datasets. Three ways to
fill it:

- **Spatial join** (preferred, ArcGIS Pro or geopandas):
  - `Latitude`/`Longitude` are real parcel-level coordinates. In the extract **99.4% are usable** (55,971 / 56,294); in the live service 324 cases fall outside lat 33–34 / lon −113 to −111.5.
  - Run point-in-polygon against the hosted `Glendale_Council_Districts` layer (§4.3).
- **Point-in-parcel:** the City's parcel layer carries `DIS_NAME` plus land use, zoning and
  `APN` (§4.4). One join gives both the district and property context; 237 of 88,762
  parcels lack a district.
- **Address join** (no GIS needed): build `StreetNum + StreetName` and match against an
  address-point layer's `ADDRESS` → `COUNCIL`. Prefer the newer `LN_ADDRESS_PT_APN_JOIN` over
  `Address_Points_By_Council_Districts` (§4.3). In the live service 782 cases have no street
  number and 406 have an empty street name.

Do the join once, write the result to `data/derived/code_cases_with_district.csv`, and
never redo it.

### 6.2 🔴 The two datasets use **different geographic precision**
- **Requests**:
  - Coordinates are **anonymized to the block level**: only 273 distinct latitudes and 424 distinct longitudes across 107,646 rows.
  - `FULL_ADDRESS` reads like `"7800 BLOCK W SOLANO DR"`, and there is an explicit `ANON_BLOCK` field. `ANON_BLOCK` is null on 11,968 rows.
  - **You cannot do parcel-level or block-group-level analysis on requests.** District is the finest reliable geography, and it is already provided.
- **Code cases**: full-precision coordinates and real street addresses.

Do **not** compare their spatial patterns at the same resolution. Say so explicitly in the
deliverable — it is itself a finding about the City's data.

Also as of 2026-09-16:
- The City publishes a 100-block address layer, but it has only 2,703 points and 5 street
  types, so it is not a complete key for `FULL_ADDRESS` [inferred].
- Police Calls for Service is redacted to the 100 block too.

### 6.3 🔴 The two datasets look like **two slices of one GlendaleOne request stream** — but there is still no join key
*Revised 2026-09-16; the earlier reading was "separate systems."*

**What still holds:** `Request_Number` and `CodeCaseNumber` have overlapping ranges
(1,610–189,761 vs 1,670–192,176) and only **2 ID collisions**. There is **no published key**
linking a request to a case. Compare them as populations, never merge on ID.

**What changed:**
- **The City's description says so.** Its own field description for `CodeCaseNumber` reads
  "This is the GlendaleOne Request ID".
- **The type catalogs don't overlap.** The GlendaleOne escalation table (§6.12) lists 16 of
  the 24 Code Compliance request types under department "Code Compliance", covering 54,711
  of 56,431 live cases. External Requests shares **0** request types with Code Compliance.
- **Together, this points to one system split in two.** It looks like one GlendaleOne ID
  sequence and one type catalog, published as two non-overlapping datasets [inferred]. The
  tiny collision count fits that reading.
- **Consequence for Q2:** "GlendaleOne requests vs code requests" compares two partitions of
  the same catalog, not two systems.

**Confirm with the sponsor** (§11 Q8).

### 6.4 🟠 Different snapshot dates
`DateLoaded` shows requests were refreshed **2026-08-06** (data stops 2026-08-05) while
code cases were refreshed **2026-09-04** (data through 2026-09-03). Any side-by-side
volume comparison must be **truncated to a common window** — recommend
**2020-01-01 → 2026-06-30** for full-month comparability, or restate the end date if the
data is refreshed.

**Update 2026-09-16:** the live requests feed is still at `DateLoaded` 2026-08-06, with no
load in six weeks. Code cases loaded 2026-09-10 with data through 2026-09-09. The gap is
widening, and the common-window rule stands.

### 6.5 🟠 The 2025 code-compliance dip is probably an artifact
Code case volume by year: 2022 = 9,816 · 2023 = 11,543 · 2024 = 9,380 · **2025 = 3,961** ·
2026 (partial) = 10,526. Proactive cases collapse to 38 in 2025 then rebound to 4,683 in
2026. This looks like a system migration or a reporting gap, not a real change in city
activity. **Ask the client before treating 2025 as a trend.** (Counts are from the 56,294-row
extract.)

### 6.6 🟠 `Council_District` on requests is not 100% clean
105,421 rows carry one of the six district names (97.9%). The remainder is **2,225
unassigned** and **142 literal `"NONE"`**. `"NONE"` is a real polygon in the GIS layer
(`HANSEN_DISTRICT = 'MC'`, likely unincorporated Maricopa County islands).

**The unassigned rows are the string `'N/A'`, not NULL.** The live service stores them that way
(checked 2026-09-16). `DATA_DICTIONARY.md` counts them as null, most likely because pandas'
default `na_values` turns `'N/A'` into NaN [inferred]. If the CSV holds the literal string, `keep_default_na=False`
will show it. Either way, treat `'N/A'`, NULL and `''` alike.

**Diagnosis:** 2,636 request rows (2.45%) sit outside a Glendale bounding box, and
**2,225 of them are exactly the unassigned-district rows** — so these are almost certainly
requests logged from outside the city, not a data-entry failure. Recommend **excluding both
`'N/A'` and `NONE`** from per-district analysis and reporting the exclusion (2,367 rows,
2.2%) in a footnote. Decide once and document the choice.

Police Calls for Service follows the same pattern: 30,433 `NONE` and 11,902 NULL districts.

### 6.7 🟠 Esri workbooks: `"Median Household Income"` appears **twice**
Once as a *growth rate* in the Trends block (row ~22, value like `0.029`) and once as a
*dollar figure* in the Households-by-Income block (row ~68, value like `69507`). A naive
label lookup grabs the wrong one. Always anchor to the section header. Same trap for
`"Total Population"`, which appears in the Summary block and again in the Infographic
block.

### 6.8 🟠 Esri 2026 estimates vs ACS estimates disagree, badly, for YUCCA
YUCCA: Census 2020 = 39,994 · ACS 2020–24 = 42,931 · **Esri 2026 = 53,147** (+33% over
2020). North Glendale is genuinely growing, but a 33% swing changes per-capita rates
materially. **Pick one denominator, state it, and run the equity calc against the other as
a sensitivity check.** Recommendation: lead with Esri 2026 (contemporaneous with the
request data), footnote ACS.

A third, independent check now exists: the City's Census 2020 block layer (§4.4). Blocks
summed inside each district can be compared with the workbooks' Census 2020 column. The
layer reaches past the city, so clip it to the districts first.

### 6.9 🟡 Misleading column names in Code Compliance
`CriminalCitations`, `CriminalSubmittals`, `ParkingCitations` and `CivilCitations` look
like counts but hold **citation reference numbers** (e.g. `1006427`). Only 8 / 35 / 68 /
412 rows respectively are non-zero. `CourtCaseNumber` is a **0/1 flag**, not a number
(10 non-zero rows). Never `sum()` these.

### 6.10 🟡 Sparse columns to expect
- Requests: `Cross_Streets` is **100% NULL** — drop it.
- Code:
  - `NextScheduledInspectionDate` is **100% NULL** — drop it.
  - `PrimaryComplaintType` is 36% missing, `CodePropertyType` 30% missing, `Proactive` 12% missing.
  - Violation slots 2–7 fall off fast (21% → 0.2%); reshape to long format if you analyse violations.
- **Code Compliance mixes NULL and empty strings.** Treat both as missing; a non-null count
  alone overstates coverage. Live counts on 2026-09-16:

  | Column | NULL | `''` |
  |---|---|---|
  | `Proactive` | 140 | 6,353 |
  | `CodePropertyType` | 9,801 | 7,256 |
  | `PrimaryComplaintType` | 9,801 | 10,630 |
  | `SecondaryComplaintType` | 9,801 | 41,812 |
  | `StreetName` | 0 | 406 |
- **Non-Glendale cases.** The extract has **928 rows with a non-Glendale `CityName`** (Peoria 859,
  Phoenix 32, Litchfield Park 26, Waddell 9, Surprise 2) and **323 rows with zero or out-of-range
  coordinates**. Live on 2026-09-16 the figures are 929 (Litchfield Park 27) and 324. Filter both.

### 6.11 🟡 Nearly everything is closed
Requests are **99.6%** `Closed` (107,208 of 107,646). Code cases are **98.3%** `Closed`:
55,479 of 56,431 live, 55,363 of 56,294 in the extract. (This section used to say "~99.5% in
both".) Open-case analysis is not viable; **cycle time** is (see §8).

### 6.12 🟠 The City's request-type catalog (GlendaleOne Escalations) — use it, but trim first
The `GlendaleOne Escalations` table has 155 rows, one per request type. Each row carries
`Department_Name`, `Request_Group`, the Level-1 route `Route1`, and `Escalate_Time1` with its
unit in `Escalates_in_` (Days for 154 types, Hours for 1). Per the portal description, each
department sets how long a standard request of that type should take. When that time
passes, the request escalates to a supervisor, and on up to the City Manager's office.

- **Requests match it only partly.** 132 of the 155 External Requests types match by exact
  name, covering 98,586 of 107,646 requests. The 23 misses include high-volume types:
  `Roadside, Alley, or Median Landscape`, `Street or Sidewalk - Damage` and
  `Rent Assistance (Rent, Mortgage, Eviction)`. The whole `Library Services` group is missing.
- **Some misses are formatting.** Type names carry trailing spaces (`Park Maintenance `,
  `Setback/Separation `) and one has broken encoding (`Community Action Team â€“ …`). Trim
  whitespace before joining, then re-check.
- **Code types map into request groups.** The table places the 16 matching Code Compliance
  types into three of the request groups: **Neighborhood Concerns** (12 types),
  **Zoning, Permitting, & Inspections** (3) and **Vehicle Issues** (1). That is a City-defined
  crosswalk for Q2 covering 54,711 cases. The other 8 code types, such as `Repeat Offender`,
  `Code Compliance - Referral` and `Animal Complaint - Noise`, need a hand mapping.

### 6.13 🟡 District names are not spelled the same in every layer
- **Uppercase:** requests, police calls and parcels use uppercase (`BARREL`).
- **Title case:** registered neighborhoods (`CouncilDistrict`) and the police grid (`CC_DIST`) use
  title case (`Barrel`). The police grid adds `Outside Glendale` on 365 of its 650 cells.
- **Normalize before joining.** Uppercase and trim before any join (see §9).

### 6.14 🟡 The City's GIS catalog has broken and mislabeled items
- **Dead Census items.** The AGOL items "Glendale Census Block Groups / Blocks / Tracts" return
  `404 Service not found`. Use the Enterprise Census block layer and the `Glendale_qct_rates`
  block groups instead (§4.4).
- **Portal items that open the wrong layer:**

  | Item title | Layer it opens |
  |---|---|
  | Glendale Garbage Pickup | Recycling Pickup |
  | Glendale Recycling | Trash Pickup |
  | Glendale Hospitals | DMV |
  | Glendale Fire Stations | Post Offices |
  | Glendale Post Offices | Fire Stations |
  | Glendale DMV | Council District |

  Check the layer name, not the item title.
- **Empty grid attributes.** `Code_Compliance_Grids` is just six district-named polygons: `CASES`,
  `STAFF` and `ADOPTED` are empty, and its description is copied from a road-centerline layer.
  The Code Compliance Sub Grid's start/end/completed fields are empty too.
- **Empty or broken links.** Parks work requests have a `glendale_one_request` field that is empty
  on all 565 rows. The "Police Incidents" portal item opens a table with 0 rows.
  `Rental_Facilities` returns "service not started". `PopDensity/block_pop` timed out.
- **Locked folders.** 17 Enterprise folders need a login, including `SmartGov`, `Finance`,
  `Building_Safety` and `EMS`.

### 6.15 🟡 Some public layers expose personal contact fields
These layers include requester or representative contact fields in their schemas:
- **Water Distribution Service Requests (Survey123):** `requesters_name`, email.
- **Parks request layers:** `pocfirstname`, `pocphone`, `pocemail`.
- **Registered neighborhoods:** representative name, phone and email.

Nothing was downloaded. **Do not pull or publish those columns**; ask the City for anonymized
extracts if the data is needed (§11 Q15).

---

## 7. First-pass numbers (⚠️ unvalidated — recompute before citing)

Produced during the 2026-09-05 profiling pass. Treat as orientation, **not as findings.**
On 2026-09-16 the live requests service returned the same per-district counts as the Q1
table. The code-case numbers below come from the 56,294-row extract; the live service now
has 56,431.

### Q1 — Requests per 1,000 residents (Esri 2026 population, requests dataset only)

| District | Pop 2026 | Requests | Per 1,000 | % of requests | % of population |
|---|---|---|---|---|---|
| CHOLLA | 40,324 | 19,538 | **484.5** | 18.6% | 15.2% |
| SAHUARO | 43,382 | 20,648 | **476.0** | 19.6% | 16.3% |
| OCOTILLO | 42,963 | 17,923 | 417.2 | 17.0% | 16.2% |
| BARREL | 42,736 | 15,941 | 373.0 | 15.1% | 16.1% |
| YUCCA | 53,147 | 17,889 | 336.6 | 17.0% | 20.0% |
| CACTUS | 42,913 | 13,340 | **310.9** | 12.7% | 16.2% |

Spread is **1.56×** (CHOLLA vs CACTUS). Note the direction: **CHOLLA — the highest-income
district — files the most requests per capita, and OCOTILLO — the lowest-income — is
mid-pack.** That is the opposite of a naive "underserved areas complain more" story and
suggests the real question is *reporting propensity*, not need. Handle carefully; it is
the most interesting and most misinterpretable number in the project.

### Q2 — Top request types, the two systems side by side

| GlendaleOne `Request_Type` | % | Code Compliance `RequestTypeName` | % |
|---|---|---|---|
| Residential - Container Damaged | 31.7% | Property Maintenance - Private Property | 65.5% |
| Abandoned Vehicle - Roadway | 4.9% | Vehicles/Parking - Private Residence | 11.8% |
| Street Light or Pedestrian Light Issue | 4.8% | Business License Inspection | 4.1% |
| Traffic Sign - Repair | 4.2% | Code General Requests | 3.8% |
| Parking Enforcement | 4.0% | Animal Complaint | 2.2% |
| Trash/Debris in Residential Areas | 3.6% | Building Without A Permit | 1.9% |
| Residential - Missed Regular Collection | 3.3% | Signage - Advertising or Commercial | 1.7% |
| Residential - Container Missing | 3.3% | Residential Rental Violation | 1.5% |
| Graffiti | 2.8% | Home Based Business Concern | 1.5% |
| Bulk Trash - Other | 2.8% | Swimming Pool/Pond Issue - Private Property | 1.3% |

Headline contrast: GlendaleOne is dominated by **city-asset and service-delivery** issues
(a third of everything is a damaged trash container); Code Compliance is dominated by
**private-property condition** issues. Note the granularity mismatch — `RequestTypeName`
is coarse; use `PrimaryComplaintType` for a fairer comparison (Overgrown Weeds and Grass
37.6%, Vehicles/Parking 16.4%, Outside Storage 11.7%, Landscaping 10.4% of non-null).
The City's own group crosswalk for the code types is in §6.12.

### Q3/Q4 — Composition differences worth chasing

Share of a district's requests that are Trash/Recycle: CHOLLA 53.7%, BARREL 51.4%,
SAHUARO 52.3%, YUCCA 48.5%, CACTUS 44.7%, **OCOTILLO 40.9%**.
Street Lighting: **CHOLLA 8.3%** vs BARREL/CACTUS 3.7%.
Assistance Programs (rent/utility help) raw counts: **OCOTILLO 1,085** and CACTUS 715 vs
**CHOLLA 169** — a near-inverse of the income ranking, and probably the strongest genuine
equity signal in the data.

### Cycle time
Requests: median **3 days** to close, mean 8.2, max 1,552.
Code cases: median **16.7 days**, mean 52.4, max 2,247.
Median days-to-close by district (requests): CHOLLA 5 · BARREL 4 · CACTUS 4 · SAHUARO 3 ·
YUCCA 3 · **OCOTILLO 2**.

---

## 8. Proposed method, question by question

| Q | Approach | Blockers |
|---|---|---|
| **Q1** | Requests per 1,000 residents by district; Lorenz curve / Gini across districts; chi-square goodness-of-fit of observed counts vs population-proportional expectation; repeat with ACS denominator as sensitivity. Cross-check the Census 2020 column against the City's block layer summed inside each district (§6.8). Then repeat the whole thing for code cases. | Needs §6.1 district join for code cases |
| **Q2** | Rank-frequency comparison at a common granularity. Put both datasets on the City's `Request_Group` taxonomy: the escalation table already assigns 16 of the 24 code types, covering 54,711 cases (§6.12). Hand-map the remaining 8 code types, and `PrimaryComplaintType` if used. Compare share-of-total and per-capita rate. Report both "top 10 in each" and "biggest rank gaps." Frame it as two partitions of one catalog (§6.3). | Hand mapping for 8 code types; trim type names before joining |
| **Q3** | Two different readings — **compute both and label them clearly.** (a) `P(type \| district)` = within-district composition. (b) `P(district \| type)` = where a given type comes from. Bayes links them; the client's wording ("coming from each district") leans toward (b). | None |
| **Q4** | Chi-square / Cramér's V on district × type-group; standardized residuals to find over/under-represented cells; cosine or Jensen–Shannon similarity between districts' type profiles; hierarchical clustering of districts. | None |
| **Q5** | Candidates, roughly in order of expected value: see the list below. | (ii) and (iii) need type-mix controls or they mislead; (x) involves personal data (§6.15) |

**Q5 candidates**, roughly in order of expected value:

- **(i) The reporting-propensity paradox in §7.** Correlate per-capita request rate against
  median income, diversity index, % renters and % without an internet subscription (the ACS
  workbook has all of these).
- **(ii) Equity of *response*, not just volume.** Cycle time by district, controlling for type mix.
- **(iii) Response against the City's own targets.** The share of requests per district that
  closed after their type's escalation time (§6.12), which is stronger than raw cycle time.
- **(iv) Proactive vs reactive code enforcement by district.** Proactive share varies wildly by
  year and may vary by district, a fairness question the City may not have looked at. The Sub
  Grid's inspector-to-zone assignment is context.
- **(v) Seasonality:** weeds/grass vs heat vs trash.
- **(vi) Repeat-address / chronic-property analysis on code cases.** Assessor data adds use code
  and owner mailing address.
- **(vii) Police Calls for Service by district** as a second, district-tagged demand signal
  (1,138,221 calls; mind its `NONE`/NULL rows).
- **(viii) HOA and registered-neighborhood coverage vs request propensity.**
- **(ix) Block-group covariates for code cases only:** QCT flags, renter share.
- **(x) Requests that never reached GlendaleOne:** the Water Distribution Survey123 form had
  10,081 submissions through June 2025.
- **(xi) The data-governance findings themselves:** the 2025 gap, the stale requests feed, and the
  empty or mislabeled City layers (§6.14).

**Cross-cutting requirement:** every per-capita or per-district claim must state which
population denominator it used (§6.8) and which unassigned-district rule it applied (§6.6).

---

## 9. Stack and conventions

Agreed stack: **Python + Power BI, with ArcGIS Pro for the spatial work.**

```
glendale-311-equity/
├── CLAUDE.md               ← start here in any Claude Code session (living Direction section)
├── README.md · CONTRIBUTING.md · CHANGELOG.md
├── .claude/skills/         ← shared project skills for Claude Code
├── .github/                ← PR template and CI checks (CHANGELOG line, clean notebooks)
├── data/
│   ├── demographics/       (12 Esri workbooks, from the email)
│   ├── council_districts.geojson
│   ├── raw/                ← the two request CSVs (git-ignored; run src/fetch_data.py)
│   └── cleaned/            ← cleaned inputs; glendaleone_clean.csv comes from the team Drive (git-ignored)
├── docs/
│   ├── PROJECT.md          ← this file
│   ├── DATA_DICTIONARY.md  ← field-level reference for the local CSVs and workbooks
│   ├── DATA_LANDSCAPE.md   ← every other City dataset: schemas, joins, sponsor questions
│   ├── PORTAL_RECON.md     ← email attachments, OpenBook, GIS map gallery
│   ├── CLEANING_LOG.md     ← what src/clean_data.py did to each file
│   ├── ANALYSIS_STANDARDS.md · DECISIONS.md · FINDINGS.md · ROADMAP.md · DELIVERABLE_IDEAS.md
│   ├── iteration1/         ← proposal answers and the Iteration 1 HTML deck
│   └── tasks/              ← task cards, one file per iterN-NN
├── src/                    ← code
│   ├── fetch_data.py          downloads the two request CSVs into data/raw/
│   ├── clean_data.py          rebuilds data/cleaned/ and its log
│   └── landscape/             harvest_metadata.py, build_landscape.py, landscape_authored.md, field_notes.json
│                              (its .cache/ of 31 MB stays local and git-ignored)
├── notebooks/              ← iterN_topic_owner.ipynb, outputs cleared before commit
└── outputs/                ← iterN/<topic>/: tables, charts and findings.md
```

Rules:
- **`data/` is read-only.** Cleaned or joined data goes to `data/derived/` under a name
  that says what it is.
- Python: `pandas` for tabular, `geopandas` (or ArcGIS Pro) for the point-in-polygon join,
  `scipy.stats` for chi-square, `matplotlib`/`seaborn` for exploratory charts.
- Power BI is for the final visuals; feed it `data/derived/` outputs, not raw CSVs.
- Dates in the CSVs are **UTC strings**; parse with `pd.to_datetime(...)` and be aware
  Glendale is UTC-7 (MST, no DST) — a late-evening request can land on the next UTC day.
- District names are **UPPERCASE**. Uppercase and trim on read; some City layers use title case (§6.13).
- Treat `NULL`, `''` and `'N/A'` as missing (§6.6, §6.10). Trim whitespace in request-type names before joining (§6.12).
- Never pull the personal contact columns listed in §6.15.
- Any number that goes in a slide gets recomputed from a script in `src/`, not copied from
  §7 of this file.

---

## 10. Other data available (published by the City)

**Full inventory: `DATA_LANDSCAPE.md`** (checked 2026-09-16). It covers 253 AGOL services,
154 Enterprise GIS services and the Open Data portal's 34 items, with schemas, row counts,
join keys and a granularity matrix. The table below updates the list first drafted here on
2026-09-05. The earlier version called GlendaleOne Escalations "escalated 311 cases" and
listed dead Census items.

| Layer | Item ID / service | Status and why it matters |
|---|---|---|
| Glendale Council Districts (Hosted) | `887a7efe02224f0ba5f3d490e59b43ea` | **Required** for §6.1. 7 polygons including `NONE`; last edited 2024-12-09. |
| Address Points By Council Districts | `632036b8ebd34f6181b0c60a7cb9198c` | Address → district crosswalk, but stale (2024-08-29). Prefer Enterprise `LN_ADDRESS_PT_APN_JOIN` (§4.3). |
| GlendaleOne Escalations | `9f44c29d057e49709a5903a2e8aee8a7` | **Not escalated cases.** It is the 155-row request-type catalog with escalation times (§6.12). |
| Census 2020 block population | Enterprise `PopDensity/Census_Block_2020_pts` | Replaces the dead AGOL Census items. Sub-district denominators (§6.8). |
| Glendale Census Block Groups / Blocks / Tracts | `24622911ffe54431af985029081506ff` / `3d04edb172794597bb806a1e98d7fd3c` / `727bfbad45ef4df7ba1f4a3f0df6694b` | ⚠️ **Dead:** 404, service removed. |
| Block groups with Esri demographics + HUD QCT | Enterprise `Community_Services/Glendale_qct_rates` | Sub-district covariates (code cases only; requests are block-anonymized). |
| Glendale Parcels · Assessor parcel view | `dbf3db308f63471c81d28fa8d11a307d` (points at Enterprise `Land/MapServer/3`) · Enterprise `ASSESSOR_PARCEL_VIEW` | Parcel `DIS_NAME`, land use, zoning; owner mailing vs situs address. Mailing and situs address strings differ on 86,441 of 89,001 parcels, so a raw string comparison does not identify absentee owners [inferred]. |
| Glendale Zoning · Building Footprints | `793473d9bbb640ea9f463ce833c8c7a8` / `55c190ce8fd345c685ca1a8760e677dd` | Property context for code cases. |
| Glendale Neighborhoods · registered neighborhoods with HOA | `819d484e45b04f1881e85daf25a7f69f` · Enterprise `NEIGHBORHOOD_P_w_MgmtCompany` | Sub-district geography; HOA angle. The latter has personal contact fields (§6.15). |
| Police Calls for Service | `08fb381ac3664073869efb65d2cc8ac6` | 1,138,221 calls with `CouncilDistrict`, 2020-01-01 → 2026-09-08, refreshed daily. |
| Police Incidents | `c5b87660b6a745328f883d1a106822b2` | ⚠️ Opens a table with **0 rows**. |
| GPD Crime Data (Redacted) | `2565b89bed184a89aa0300c85fe14c43` | 159,507 offenses with `COUNCIL_DISTRICT_GIS`, 2022-07-01 → 2026-09-10. |
| Glendale Fire Incidents Historic | `1988a2acee844bfb874f2f70f4ebd1bf` | 518,974 incidents with `COUNCIL_DIST`, 2015-01-01 → 2026-08-03. |
| Glendale Business Licenses | `30ecfc0985e945d18bd8c1494a946c0c` | 9,879 licenses; context for Business License Inspection cases. Meaning of its `District` field unconfirmed. |
| Sanitation day routes / routes | Enterprise `Sanitation/Sanitation_Polys` | Trash is 48% of requests. The AGOL "Glendale Garbage Pickup" item (`8145fd0eeb544de7b3aa7a975b9d5a90`) opens the Recycling Pickup layer (§6.14). |
| Water Distribution Service Requests (Survey123) | `c297db43ca0244d5b273b9c4f68b9a7c` | 10,081 requests outside GlendaleOne, 2019-04-29 → 2025-06-02. Personal data (§6.15). |
| Glendale HeatRelief Locations | `57d45b10e0cc40f7af9802ea5cb56929` | Heat equity angle (12 locations). |

**How to pull a layer:**
- **AGOL hosted layers:**
  `https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services/<SERVICE_NAME>/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson`.
  Find `<SERVICE_NAME>` via `https://www.arcgis.com/sharing/rest/content/items/<ITEM_ID>?f=json`.
- **Items that point at the Enterprise server:** many AGOL items are only pointers to
  `https://gismaps.glendaleaz.com/gisserver/rest/services/<FOLDER>/<SERVICE>/MapServer/<LAYER>`.
  Query that URL instead.
- **Page large layers.** Page through them: the GlendaleOne requests layer returns at most 2,000 records per call, and other layers set their own `maxRecordCount`.

**OpenBook budget portal and GIS map gallery** — explored 2026-09-16; details in
`PORTAL_RECON.md`:
- **OpenBook** (https://glendaleaz.openbook.questica.com/):
  - **Stories:** 4 public stories covering sales tax, the major funds, and operating and capital spending.
  - **Grids:** operating transaction detail (562,730 rows), capital project spending (29,561 rows, 2018-07-18 → 2026-09-14) and a 10-year CIP plan (2,525 rows).
  - **Coverage and access:** budget years FY20-21 → FY26-27, refreshed daily. CSV export links and an undocumented JSON API.
  - **No geography at all.** Spending cannot be put on districts directly. Capital projects could be linked to the CIP polygon layers by Munis project number, then spatially joined [inferred].
- **GIS map gallery** (https://gis.glendaleaz.com/maps/): 32 apps listed in the `GIS_Applications_Public` layer.
  - **The request and code dashboards are Power BI.** The **GlendaleOne Public and Council Report** and the **Code Compliance Public Dashboard** have no API and were not opened.
  - There is no ArcGIS map of GlendaleOne requests.

---

## 11. Open questions

**For the client (Stephen Gushue) — there is a standing offer to meet.** Evidence for each
question is in `DATA_LANDSCAPE.md` §5.

1. What happened to Code Compliance data in **2025**? (§6.5) Was there a system migration?
2. Code Compliance `District` is an empty string on all 56,431 live rows (§6.1). Can the nightly load fill it with the same rule used for `Council_District` on requests, or is a spatial join the intended path?
3. Is the block-level anonymization on GlendaleOne requests intentional and permanent? Could the extract carry a Census block or block-group GEOID (no address) instead, or is a finer restricted-use extract available? Is `ADDRESS_100BLOCK` the anonymization reference?
4. Which population basis does the City use for equity reporting — Census 2020, ACS, the Esri projections it supplied, or its own Census block layer? What is `PopDensity/block_pop`?
5. What defines a "proactive" code case, and what drives the year-to-year swing?
6. Is `Escalate_Time1` in the GlendaleOne Escalations table the service target departments are measured against (§6.12)? Are levels beyond `Route1` available? Why do 23 request types have no entry?
7. What has the City already looked at, so the team doesn't re-deliver it? Can the team see the data behind the Power BI GlendaleOne Public and Council Report and the Code Compliance Public Dashboard?
8. Are External Requests and Code Compliance two filters of one GlendaleOne request stream (§6.3)? Is any request type published in neither?
9. Is `Council_District` assigned at intake against the boundaries in force then, or recomputed against the current layer (last edited 2024-12-09)? Are boundaries back to December 2019 available?
10. What do `'N/A'` (2,225) and `NONE` (142) mean on requests, and `NONE` (30,433) / NULL (11,902) on police calls (§6.6)?
11. Which layers are authoritative: the hosted district polygons (7) or the Enterprise copy (6)? And which address crosswalk (§4.3)?
12. The External Requests feed last loaded 2026-08-06, while Code Compliance loaded 2026-09-10 (§6.4). Is the requests feed paused? What refresh schedule should the team assume?
13. The Survey123 request forms (Water Distribution 10,081, Wastewater Collections 2,370, Environmental Resources 436) stop in late May or early June 2025. Were they folded into GlendaleOne, and should earlier submissions count as requests?
14. Can the team get read access to the token-secured `SmartGov` folder, or a derived extract? Is a current rental-property list available? (`Rental_Facilities` is down.)
15. Heads-up for the City: several public layers expose personal contact fields (§6.15), and several portal items are mislabeled or empty (§6.14).

**For the professor / class:**

16. What is the graded deliverable, format, and due date? (§1 is blank.)
17. Is this one team of 14 or several teams on the same brief?
18. Is there a required presentation to the City?

**For the team:**

19. Denominator decision (§6.8) and unassigned-district rule (§6.6) — decide once, early.
20. Who owns the ArcGIS Pro spatial join?
21. Refresh the local CSVs before analysis? The code extract is 137 cases behind, and no download script exists any more (§4.1).

---

## 12. Changelog

| Date | Who | What |
|---|---|---|
| 2026-09-05 | Ma'el + Claude | Created. Read the client email, downloaded both live datasets (107,646 + 56,294 rows) from the ArcGIS REST endpoints, profiled all 14 data files, inventoried the open data portal, wrote this file and `DATA_DICTIONARY.md`. No analysis code written yet. |
| 2026-09-16 | Ma'el + Claude | Wrote `PORTAL_RECON.md`. Re-checked the email attachments; explored OpenBook and the GIS map gallery without logging in or downloading. |
| 2026-09-16 | Ma'el + Claude | Wrote `DATA_LANDSCAPE.md` with `src/harvest_metadata.py` and `src/build_landscape.py`: a metadata-only inventory of 253 AGOL and 154 Enterprise services, no rows downloaded. Moved `PORTAL_RECON.md` and `.claude/` into this folder. |
| 2026-09-16 | Ma'el + Claude | Updated this file with the new findings. Added live counts and the iCloud/refresh warning (§4.1), fixed the download paths (§4.3), and added the landscape summary (§4.4). Revised §6.1, §6.3, §6.4, §6.6, §6.10 and §6.11, and added §6.12–§6.15. Added the §8 Q2 crosswalk and Q5 candidates, updated the §9 tree and rules, rewrote §10, and expanded §11. `DATA_DICTIONARY.md` was not changed. |
| 2026-09-16 | Ma'el + Claude | Wrote `DELIVERABLE_IDEAS.md`: three scoped deliverable ideas (reporting-propensity gap, district request signatures, response vs escalation targets) with data-status flags. |
| 2026-09-28 | Ma'el + Claude | Copied into the `glendale-311-equity` repo as `docs/PROJECT.md`. Rewrote the §9 folder tree to describe the repo, and removed email addresses, the Gmail thread link and the student distribution list. The rest of the text is unchanged. |
