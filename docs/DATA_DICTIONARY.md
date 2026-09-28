# Data Dictionary — CIS 450 Glendale Group Project

Companion to [`PROJECT.md`](./PROJECT.md). Load this when you need column semantics;
`PROJECT.md` alone is enough for context and direction.

All row counts, null rates and cardinalities were measured on the **2026-09-05** extract.
All date columns in the CSVs are **UTC** strings, `YYYY-MM-DD HH:MM:SS`, converted from
ArcGIS epoch-milliseconds at download time. Glendale local time is **UTC-7 (MST, no DST)**.

---

## 1. `data/GlendaleOne_External_Requests.csv`

**107,646 rows × 16 columns.** Source: ArcGIS Feature Service
`GlendaleOne_External_Requests` (item `37a2cb9cf728424d8c0f5c1f64621939`, City of Glendale
Arizona). Portal description: *"GlendaleOne is the application that allows residents of
Glendale to make requests about their service needs and issues they are experiencing."*

| # | Column | Type | Non-null | Distinct | Notes |
|---|---|---|---|---|---|
| 1 | `OBJECTID` | int | 100% | 107,646 | ArcGIS internal row id. Not a business key. Drop. |
| 2 | `DateLoaded` | datetime | 100% | 4 | ETL timestamp. All four values are **2026-08-06 02:00:12–15**, i.e. one nightly load. Use to detect refresh staleness. |
| 3 | `Request_Number` | int | 100% | 107,646 | **Primary key.** Range 1,610 – 189,761. Sequential-ish; gaps exist (internal/withheld requests). Not comparable to `CodeCaseNumber`. |
| 4 | `Status` | string | 100% | 4 | `Closed` 107,208 · `On Hold` 253 · `In Progress` 116 · `Open` 69. **99.6% closed** — no meaningful backlog analysis. |
| 5 | `Request_Date` | datetime | 100% | 2,428 | Date opened. **2019-12-02 → 2026-08-05.** Time component is always 00:00:00 — **date-only, no time-of-day analysis possible.** |
| 6 | `Last_Action_Date` | datetime | 100% | 2,036 | Most recent action. Date-only. |
| 7 | `Close_Date` | datetime | 99.6% | 2,031 | Date closed; 392 nulls (the open/in-progress/on-hold cases). Date-only, so same-day close = 0 days. |
| 8 | `Request_Type_Group` | string | 100% | **17** | Coarse category. See §1.1. Use this for cross-district comparison; `Request_Type` is too sparse. |
| 9 | `Request_Type` | string | 100% | **155** | Fine category. Heavy long tail — top type alone is 31.7%. |
| 10 | `Latitude` | float | 100% | **273** | ⚠️ **Block-anonymized.** Only 273 distinct values across 107k rows. Range **33.25 – 33.82**. **2,636 rows (2.45%) fall outside a Glendale bounding box** (33.45–33.85 / −112.45 – −112.05) — and **2,225 of those are exactly the null-`Council_District` rows**, so the nulls are almost certainly out-of-city requests. No zero coordinates. Do not treat as a point location. |
| 11 | `Longitude` | float | 100% | **424** | ⚠️ Same. Range **−112.93 – −111.34**. |
| 12 | `Cross_Streets` | — | **0%** | 0 | Entirely null. **Drop.** |
| 13 | `Council_District` | string | 97.9% | 7 | `SAHUARO` 20,648 · `CHOLLA` 19,538 · `OCOTILLO` 17,923 · `YUCCA` 17,889 · `BARREL` 15,941 · `CACTUS` 13,340 · `NONE` 142 · **null 2,225**. See PROJECT.md §6.6. |
| 14 | `Responsible_Department_Name` | string | 100% | 14 | See §1.2. Useful as an operational (rather than geographic) cut. |
| 15 | `ANON_BLOCK` | float | 88.9% | 230 | The anonymized block number (e.g. `7800`, `19000`). `0` appears as a value. Explains the coordinate rounding. |
| 16 | `FULL_ADDRESS` | string | 100% | 9,448 | Block-level text, e.g. `"7800 BLOCK W SOLANO DR"`. Some rows are street-only, e.g. `"W CHOLLA ST"`. Not geocodable to a parcel. |

### 1.1 `Request_Type_Group` — all 17 values

| Group | Count | Share |
|---|---|---|
| Trash/Recycle Services | 51,717 | 48.0% |
| Streets/Sidewalks/Medians/Corners | 10,936 | 10.2% |
| Vehicle Issues | 9,660 | 9.0% |
| Traffic Signals/Signs | 7,473 | 6.9% |
| Water/Sewer Services | 6,458 | 6.0% |
| Street Lighting | 5,217 | 4.8% |
| Assistance Programs | 4,088 | 3.8% |
| Park & Recreation Facilities | 3,862 | 3.6% |
| Neighborhood Concerns | 3,299 | 3.1% |
| Traffic Safety | 2,481 | 2.3% |
| Zoning, Permitting, & Inspections | 1,052 | 1.0% |
| Miscellaneous | 744 | 0.7% |
| Public Transportation | 243 | 0.2% |
| Website | 210 | 0.2% |
| Community Programs | 145 | 0.1% |
| Library Services | 38 | <0.1% |
| Americans with Disabilities Act (ADA) | 23 | <0.1% |

### 1.2 `Responsible_Department_Name` — all 14 values

Field Operations 53,439 · Transportation 25,241 · Police Department 12,866 ·
Customer Service Center 4,279 · Community Services 4,229 ·
Public Facilities, Recreation & Special Events 3,187 · Water Services 2,576 ·
Development Services 942 · Engineering Department 211 · Public Affairs 210 ·
Budget & Finance 176 · Human Resources & Risk Mgmt 150 · Fire Department 103 ·
Economic Development 37.

### 1.3 Top 15 `Request_Type` values

Residential - Container Damaged 34,129 · Abandoned Vehicle - Roadway 5,303 ·
Street Light or Pedestrian Light Issue 5,217 · Traffic Sign - Repair 4,571 ·
Parking Enforcement 4,346 · Trash/Debris in Residential Areas 3,884 ·
Residential - Missed Regular Collection 3,575 · Residential - Container Missing 3,555 ·
Graffiti 3,047 · Bulk Trash - Other 3,039 · Roadside, Alley, or Median Landscape 3,001 ·
Street or Sidewalk - Damage 2,432 · Rent Assistance (Rent, Mortgage, Eviction) 1,849 ·
Traffic Enforcement - Public Property 1,717 · Commercial - Missed Regular Collection 1,544.

*(140 more types in the tail.)*

### 1.4 Volume by year

2019: 851 (partial, Dec only) · 2020: 16,694 · 2021: 17,132 · 2022: 16,493 · 2023: 17,315 ·
2024: 14,802 · 2025: 15,302 · 2026: 9,057 (through Aug 5).

---

## 2. `data/Code_Compliance_Cases_GlendaleOne.csv`

**56,294 rows × 51 columns.** Source: ArcGIS Feature Service
`GlendaleOne_Code_Compliance_Cases` (item `8026de93be8147d2aa2941c3e7ceed97`).
Portal description: *"This dataset shows the cases that are worked by the Code Compliance
Division in the City of Glendale. Each case either stems from a resident providing
information about a potential code violation or a code inspector observing a violation.
This data shows how Glendale is pro-actively working to reduce blight and improve our
community."*

### 2.1 Identity and lifecycle

| Column | Type | Non-null | Distinct | Notes |
|---|---|---|---|---|
| `ObjectID` | int | 100% | 56,294 | ArcGIS row id. Drop. |
| `DateLoaded` | datetime | 100% | 83 | **2026-09-04 01:05–01:06.** One load, batched. |
| `CodeCaseNumber` | int | 100% | 56,294 | **Primary key.** Range 1,670 – 192,176. **Unrelated to `Request_Number`** despite the overlapping range. |
| `RequestDate` | datetime | 100% | 52,219 | Case opened. **2019-12-03 09:08 → 2026-09-03 17:57.** Has a real **time component** (unlike the requests dataset) — time-of-day analysis is possible here. |
| `CloseDate` | datetime | 98.5% | 46,563 | 848 nulls. |
| `FirstInspectionDate` | datetime | 67.6% | 1,343 | Date-only. Max value is **2026-11-24 — in the future**, i.e. scheduled inspections leak in. Filter future dates before computing durations. |
| `NextScheduledInspectionDate` | — | **0%** | 0 | Entirely null. **Drop.** |
| `LastActionDate` | datetime | 100% | 46,804 | Has a time component. |
| `RequestStatus` | string | 100% | 4 | `Closed` 55,363 · `On Hold` 780 · `In Progress` 139 · `Open` 12. |
| `Proactive` | string | 88.5% | 3 | `No` 31,210 (resident-reported) · `Yes` 17,949 (inspector-observed) · `Expanded Audit` 652 · **null 6,483**. See PROJECT.md §6.5 — the yes/no mix swings wildly by year. |

### 2.2 Location

| Column | Type | Non-null | Distinct | Notes |
|---|---|---|---|---|
| `Latitude` | float | 100% | 37,482 | **Full precision** (unlike requests). 323 rows are `0` or out of range — filter to lat 33.0–34.0. |
| `Longitude` | float | 100% | 24,826 | Same; filter to −113.0 – −111.5. |
| `StreetNum` | string | 98.6% | 6,027 | Stored as text. |
| `StreetName` | string | 99.3% | 814 | e.g. `"N 77th Dr"`. Mixed case. |
| `CityName` | string | 100% | 6 | Glendale 55,366 · **Peoria 859 · Phoenix 32 · Litchfield Park 26 · Waddell 9 · Surprise 2**. 928 non-Glendale rows — filter them out. |
| `CrossStreetName` | string | **0.9%** | 192 | Nearly empty. Drop. |
| `District` | — | **0%** | 0 | ⚠️ **Entirely null.** The field exists but was never populated. Must be derived — see PROJECT.md §6.1. |

### 2.3 Classification

| Column | Type | Non-null | Distinct | Notes |
|---|---|---|---|---|
| `CodePropertyType` | string | 69.7% | 2 | `Residential` 36,731 · `Commercial/Business` 2,520 · null 17,043. |
| `RequestTypeName` | string | 100% | **24** | Coarse intake category. Dominated by `Property Maintenance - Private Property` (65.5%). See §2.6. |
| `PrimaryComplaintType` | string | 63.7% | 25 | The **more informative** classification. 20,416 nulls. See §2.6. |
| `SecondaryComplaintType` | string | 8.5% | 24 | Only 4,811 rows. Top: Outside Storage 1,595 · Overgrown Weeds and Grass 920 · Vehicles/Parking 773. |

### 2.4 Violations (repeating group, slots 1–7)

Each slot has `Violation<N>` (code + description), `Violation<N>Start`, `Violation<N>End`.

| Slot | Non-null | Distinct codes |
|---|---|---|
| 1 | 64.4% (36,259) | 312 |
| 2 | 21.5% (12,093) | 260 |
| 3 | 7.9% (4,464) | 202 |
| 4 | 2.9% (1,635) | 167 |
| 5 | 1.1% (638) | 123 |
| 6 | 0.5% (255) | 84 |
| 7 | 0.2% (102) | 57 |

**Format:** `"CC 25-21.G\tOVERGROWN WEEDS AND GRASS"` — the ordinance code and the
description are separated by a **literal tab character**. Split on `\t` to get a clean
code and label. Prefixes seen: `CC` (City Code), `UDC` (Unified Development Code),
`IBC` (International Building Code), `C-NOVIO` (= *no violation found*, 3,179 cases —
**exclude these from violation analysis, they are cleared cases**).

Top codes: `CC 25-21.G` Overgrown Weeds and Grass 12,098 · `C-NOVIO` No Violation 3,179 ·
`CC 25-21.E` Rubbish/Trash/Debris 2,781 · `CC 25-20.D` PM Landscaping 2,702 ·
`CC 25-21.F` Items Stored in Public View 1,501 · `CC 21-132` City Business License Required
1,378 · `CC 24-68.E.2` Storing/Manoeuvring in Landscaped Area 1,017.

**Recommended reshape:** melt slots 1–7 into a long table
(`CodeCaseNumber, slot, code, description, start, end`), drop nulls and `C-NOVIO`, then
analyse.

### 2.5 Enforcement / citation fields — ⚠️ read the note

| Column | Type | Non-zero rows | What it actually is |
|---|---|---|---|
| `CleanandLien` | datetime | 223 | Date the City abated and liened the property. Rare but high-severity — a good "worst cases" filter. |
| `CriminalCitations` | int | **8** | ⚠️ A **citation reference number** (e.g. `1006427`), not a count. **Never sum.** |
| `CriminalCitationsDate` | datetime | 54 | |
| `CivilCitations` | float | 412 | ⚠️ Reference number. |
| `CivilCitationsDate` | datetime | 442 | |
| `CourtCaseNumber` | int | **10** | ⚠️ A **0/1 flag**, not a number. |
| `CriminalSubmittals` | int | **35** | ⚠️ Mixed — some rows hold small counts (1–3), others reference numbers (e.g. `113022`). Treat as unreliable. |
| `ParkingCitations` | int | **68** | ⚠️ Reference number. |

Practical takeaway: **formal enforcement is vanishingly rare** (<1% of cases reach any
citation). The interesting enforcement variable is `CleanandLien` and cycle time, not
citation counts.

### 2.6 Classification value lists

**`RequestTypeName`, all 24:** Property Maintenance - Private Property 36,868 ·
Vehicles/Parking - Private Residence 6,657 · Business License Inspection 2,290 ·
Code General Requests 2,145 · Animal Complaint 1,247 · Building Without A Permit 1,060 ·
Signage - Advertising or Commercial 978 · Residential Rental Violation 856 ·
Home Based Business Concern 820 · Swimming Pool/Pond Issue - Private Property 744 ·
Animal Complaint - Noise 507 · Code Compliance - Referral 494 ·
Discharging Material in Roadway 385 · Animal Complaint - Other 359 ·
Graffiti - Refer to Code Compliance 247 · Noise Complaint 246 ·
Yard or Garage Sale Concern 147 · Repeat Offender 67 · Setback/Separation 66 ·
Unsecured Refrigerator/Freezer 42 · Mobile Vendor Complaint 25 · ADA - Code Compliance 22 ·
Red Flag - Code Compliance 21 · Code Compliance - ADA 1.

*(Note the near-duplicate pair `ADA - Code Compliance` / `Code Compliance - ADA` — evidence
of inconsistent intake coding.)*

**`PrimaryComplaintType`, all 25 (excluding 20,416 nulls):** Overgrown Weeds and Grass
13,507 · Vehicles/Parking 5,878 · Outside Storage 4,208 · Landscaping 3,747 · Other 1,583 ·
Rental Concern 1,085 · Animal Noises 843 · Illegal Signs or Banners 795 ·
Building without a permit 680 · Home based business concerns 502 · Swimming Pool/Pond issue
501 · Abandoned or Inoperable Vehicles 374 · General Nuisance 323 · Fences and Walls 300 ·
Discharging Material in Roadway 292 · Graffiti 273 · Illegal Land Use 186 · Noise 159 ·
No Permit 151 · Painted Surfaces 115 · Animal Smells 112 · Yard or Garage Sale Concern 99 ·
Unsecured Refrigerator 98 · Roof 53 · Vendor Concerns 14.

### 2.7 Volume by year and proactive mix

| Year | Total | Reactive (`No`) | Proactive (`Yes`) | Expanded Audit | Null |
|---|---|---|---|---|---|
| 2019 | 125 | 106 | 17 | 0 | 2 |
| 2020 | 4,926 | 3,455 | 9 | 0 | 1,462 |
| 2021 | 6,017 | 5,216 | 82 | 0 | 719 |
| 2022 | 9,816 | 5,452 | 3,790 | 144 | 430 |
| 2023 | 11,543 | 5,596 | 5,256 | 372 | 319 |
| 2024 | 9,380 | 4,862 | 4,074 | 133 | 311 |
| **2025** | **3,961** | 3,401 | **38** | 0 | 522 |
| 2026 | 10,526 | 3,122 | 4,683 | 3 | 2,718 |

⚠️ The 2025 row is almost certainly a data artifact. See PROJECT.md §6.5.

---

## 3. The 12 Esri demographic workbooks

One sheet per file, named after the district (`BARREL`, `CACTUS`, `CHOLLA`, `OCOTILLO`,
`SAHUARO`, `YUCCA`). **These are formatted reports, not tables.** Column A holds a label
that is sometimes a section header, sometimes a data row, and sometimes repeated in a
different section with a different meaning.

### 3.1 `Demographic_and_Income_Profile_<DISTRICT>.xlsx` — 222 rows × 7 cols

Vintage: **Census 2020 actual + Esri 2026 estimate + Esri 2031 projection.**

| Rows | Section | Layout |
|---|---|---|
| 2–4 | Title block | `"Demographic and Income Profile"` / `"Prepared by Esri"` / district name |
| 6–14 | **Summary** | Col A label; **B = Census 2020, C = 2026, D = 2031**. Rows: Total Population, Total Households, Family Households, Average Household Size, Owner Occupied Housing Units, Renter Occupied Housing Units, Median Age |
| 16–22 | **Trends 2026–2031 (annual rates)** | B = Area, C = State, D = National. ⚠️ Contains a row literally labelled `Median Household Income` holding a **rate** (e.g. `0.029`) |
| 24–43 | **Population by Age** | B/C = Census 2020 number/percent, D/E = 2026, F/G = 2031. 18 age bands, `0-4` … `Age 85+` |
| 45–66 | **Households by Income** | B/C = 2026 number/percent, D/E = 2031. 20 income bands, `<$10,000` … `$500,000+` |
| **68–70** | **Income summary** | ⚠️ **This is where the dollar figures live.** B = 2026, D = 2031. Rows: Median Household Income, Average Household Income, Per Capita Income |
| 72–82 | **Race and Ethnicity** | Same 3-vintage number/percent layout. 7 race categories + a separate `Hispanic (Any Race)` row |
| 84–219 | **Infographic blocks** | Repeated `Infographic` / `Variable` / value triplets, plus flattened restatements of the age, income and race percentages. **Redundant with the above** — includes the only home for `2026 Diversity Index`, `2026 Median Net Worth`, `2026 Wealth Index`, `2026 Housing Affordability Index`, `2026 Total Daytime Population` |
| 221 | Source note | U.S. Census Bureau + Esri |

**Unique-to-the-infographic-block variables** (not available anywhere else):
`2026 Total Daytime Population`, `2026 Diversity Index`, `2026 Median Net Worth`,
`2026 Wealth Index`, `2026 Housing Affordability Index`.

**Parsing recipe** — anchor to section headers, never to bare labels:

```python
import openpyxl
def read_profile(path):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    out = {}
    for i, r in enumerate(rows):
        if r[0] == "Households by Income":           # anchor
            for r2 in rows[i:i+30]:
                if r2[0] in ("Median Household Income",
                             "Average Household Income",
                             "Per Capita Income"):
                    out[r2[0]] = {"2026": r2[1], "2031": r2[3]}
            break
    return out
```

### 3.2 `ACS_Population_Summary_<DISTRICT>.xlsx` — 373 rows × 6 cols

Vintage: **ACS 2020–2024 five-year estimates.** Columns: A = label,
**B = ACS Estimate, C = Percent, D = MOE (±), E = Reliability.**
The `2020 - 2024` / `ACS Estimate | Percent | MOE (±) | Reliability` header pair repeats at
the top of most sections — skip rows where col A is blank or equals `"Total"`
without context.

Sections, in order, with their approximate row ranges:

| Rows | Section |
|---|---|
| 8–10 | **Totals** — Total Population, Total Households, Total Housing Units |
| 12–20 | Household Size and Type (split by presence of 65+) |
| 22–34 | Household Type by Relatives and Non-relatives |
| 36–39 | **Households by Disability Status** |
| 42–66 | Population Age 3+ by School Enrollment (public/private by grade band) |
| 68–78 | Households by Presence of People Under 18 |
| 81–95 | **Households by Poverty Status** — ends with a scalar `Poverty Index` |
| 97–106 | **Households by Public Assistance and Other Income** — public assistance, **SNAP**, Social Security, retirement |
| 108–116 | Population by Ratio of Income to Poverty (`Under .50` … `2.00 and over`) |
| 119–134 | Households by Type and Size |
| 136–153 | Population Age 5–17 by Language Spoken |
| 156–173 | **Population Age 18–64 by Language Spoken** (incl. English proficiency) |
| 175–192 | Population Age 65+ by Language Spoken |
| 194–209 | **Workers 16+ by Means of Transportation** (incl. Worked at home) |
| 211–225 | Workers 16+ by Travel Time to Work |
| 228–232 | Workers 16+ by Place of Work |
| 234–253 | Sex by Class of Worker |
| 255–265 | **Gross Rent as a Percentage of Household Income** (cost-burden: 30%+, 50%+) |
| 268–281 | Females Age 20–64 by Age of Children |
| 283–293 | **Population and Presence of a Computer** (by age band) |
| 295–303 | **Households and Internet Subscriptions** (broadband, satellite, none) |
| 306–359 | Health Insurance Coverage by Age (four blocks: <19, 19–34, 35–64, 65+) |
| 361–370 | Civilian Population 18+ by Veteran Status |
| 372 | Source note |

**Highest-value variables for the equity story** (these are the covariates that make Q5
work): `Poverty Index`, `With Food Stamps/SNAP`, `With No Internet Access`,
`Households with 1+ Persons w/Disability`, `Speak English "not well"/"not at all"`,
`Gross Rent 50+% of Income`, `Have No Computer`, `Worked at home`.

⚠️ Every estimate has a **margin of error** in column D. Several district-level cells have
MOEs of 20–50% of the estimate. When comparing districts on an ACS variable, check whether
the intervals overlap before calling it a difference.

### 3.3 District-level values already extracted

See `PROJECT.md` §5 for the assembled cross-district table (population by three vintages,
income, diversity index).

---

## 4. Reference: Council Districts GIS layer

Service: `https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services/Glendale_Council_Districts/FeatureServer/0`
Geometry: polygon. **7 features** — the six districts plus a `NONE` polygon
(`HANSEN_DISTRICT = 'MC'`, ~4× the area of any district; likely county/unincorporated
context rather than a service area).

| Field | Notes |
|---|---|
| `DIS_NAME` | **The join key.** `OCOTILLO`, `CACTUS`, `BARREL`, `SAHUARO`, `CHOLLA`, `YUCCA`, `NONE` — matches `Council_District` in the requests CSV and the workbook filenames exactly. |
| `MEMBER` | Council member name. Layer last edited **2024-12-09** — ⚠️ verify before publishing. |
| `HANSEN_DISTRICT` | 3-letter code: `OCO`, `CAC`, `BAR`, `SAH`, `CHO`, `YUC`, `MC`. |
| `Shape__Area`, `Shape__Length` | Useful for requests-per-square-mile as an alternative to per-capita. |

Companion layer `Address_Points_By_Council_Districts` (service
`Address_Points_By_Council_Districts`) provides `ADDRESS` → `COUNCIL` for a non-spatial
join, plus `ZIP_CODE`, `ZONE`, `LAT`, `LONGITUDE`.

---

*Measured 2026-09-05. If the underlying data is refreshed, re-run the profiling before
trusting the counts above.*
