# Glendale Data Reconnaissance — 2026-09-16

## Task 1 — Email attachments

**Thread:** "FW: ASU Data Analytics Project". From Stephen Gushue, sent Fri 4 Sep 2026, 16:24 UTC. The search returned 1 message (ID `1a06d3d19e1b2041`). Nothing was downloaded.

| # | Filename | Size |
|---|----------|------|
| 1 | image001.png | 60.4 KB |
| 2 | ACS_Population_Summary_BARREL.xlsx | 51.5 KB |
| 3 | ACS_Population_Summary_CACTUS.xlsx | 53.6 KB |
| 4 | ACS_Population_Summary_CHOLLA.xlsx | 41.0 KB |
| 5 | ACS_Population_Summary_OCOTILLO.xlsx | 41.1 KB |
| 6 | ACS_Population_Summary_SAHUARO.xlsx | 137.3 KB |
| 7 | ACS_Population_Summary_YUCCA.xlsx | 136.3 KB |
| 8 | Demographic_and_Income_Profile_BARREL.xlsx | 41.8 KB |
| 9 | Demographic_and_Income_Profile_CACTUS.xlsx | 28.7 KB |
| 10 | Demographic_and_Income_Profile_CHOLLA.xlsx | 41.4 KB |
| 11 | Demographic_and_Income_Profile_OCOTILLO.xlsx | 41.7 KB |
| 12 | Demographic_and_Income_Profile_SAHUARO.xlsx | 28.6 KB |
| 13 | Demographic_and_Income_Profile_YUCCA.xlsx | 39.3 KB |

- **Missing:** none. All 12 expected .xlsx files are present, and the names match the expected pattern exactly.
- **Extra:** `image001.png` (60.4 KB). The body references it as `cid:image001.png`, so it is the inline email-signature image and not data. [inferred]
- **Size notes:** these are not errors, just things to check when opening the files.
  - ACS SAHUARO and ACS YUCCA are about 137 KB. The other four ACS files are 41–54 KB.
  - Demographic CACTUS and Demographic SAHUARO are about 29 KB. The other four are 39–42 KB.
  - [inferred] The files may have different sheet counts or contents.
- **Email body:** it lists the data sources (Open Data GlendaleOne External Requests, Code Compliance Cases – GlendaleOne, OpenBook, the GIS map gallery) and the project questions: district equity, top-N request types, per-district probabilities, similarities and disparities.

## Task 2 — OpenBook (glendaleaz.openbook.questica.com)

The site loaded without problems. It is a Questica OpenBook app, and I did not log in.

### Navigation structure
- **Header:** Glendale logo (home), Feedback (`#/Feedback`), Log In (`#/login`).
- **Home page:** an intro carousel and a "Filter by Category" control with three options: All / Operating Budgets / Capital Budgets. There is also a search box for "Spotlights and Visualizations".
- **Stories:** exactly **4** are published (`#/story/<id>`, which redirects to `#/spotlight/<id>`).

| Story | Category | Last updated | What it contains |
|---|---|---|---|
| Glendale City Sales Tax (`83fa708f…`) | Operating Budgets | 2026-09-14 | Monthly Transaction Privilege Tax (TPT) revenue: headline for FY2027 August, month and YTD figures, month-to-month collections (3 visuals) |
| Major Funds Financial Snapshot (`dcb5e4b9…`) | Operating Budgets | 2026-07-07 | 18 visuals: YTD revenue, revenue by category, and monthly expenditures by category, each for the General Fund, HURF, Transportation Sales Tax, Water Services, Solid Waste and Landfill (headings read "through May") |
| Follow Your Money – Operating (`932be221…`) | Operating Budgets | 2026-07-01 | 3 visuals (see below) |
| Follow Your Money – Capital Projects (`ab083cc7…`) | Capital Budgets | 2026-07-01 | 3 visuals (see below) |

- **Standalone views:** each visual can be opened on its own at `#/visualization/<id>` using its "Open in New Window" link.

### Data published

**Operating**

- **Operating Expenditures** (`e21f91f6…`): budget-style layout.
  - Tiles: Adopted Budget, Revised Budget, Actuals. For FY25-26: $709.8M adopted / $713.8M revised / $582.7M actuals.
  - Tabs: Amount / Percentage / Summary / History.
  - Drill-down: **Department → Fund → ORG (costing center) → Rollup (GL category) → Object (GL account)**.
  - Preset filters exclude "00-Undefined Department", "31-Debt Service" and Contingency.
- **Operating transaction detail** (`31444d31…`): Data Explorer grid with **562,730 rows**.
  - Fields: BudgetYear, Division, Fund, GLCategory, CostingCenter, GLAccount, Vendor/Item description, PostingDate, CheckNo, Warrant, Amount.
  - This is vendor-level spending, i.e. the vendor-payments data.
- **Revenue Budget vs Actuals** (`4aab6652…`): for FY25-26, $1.0B revised budget and $961.4M actuals.
  - Broken down by Fund Display Name, with about 150 funds listed.

**Capital**

- **CIP Expenditures** (`9f24d75b…`): budget-style layout, broken down by Project Type (Streets, Facility Maintenance, Public Safety, Water, etc.).
  - For FY25-26: Adopted $478.0M / Revised $392.2M / Actuals $201.6M.
  - Preset filters exclude the Finance, Economic Development, Development Impact Fee, Bridges, Risk Management, Technology and Carryover project types.
- **Detailed Capital Project Spending Report** (`95c4aa0b…`): grid with **29,561 rows**.
  - Fields: Project (e.g. "CIPAP19076 - SOUTH APRON PHASE 1 PAVEMENT RECONS"), Project Type, CIP ORG, Object (GL account), Posting Date, Check No, Vendor/Item, Warrant, Amount.
  - Posting dates run from **2018-07-18 to 2026-09-14** (I got these by sorting the date field in both directions).
  - Includes a donut chart by project type.
- **CIP Project Details – 10 Year Funding Plan** (`10063de4…`): grid with **2,525 rows**.
  - Fields: BudgetYear, Project, ProjectType, Project Phase (e.g. DESIGN), Fund Source, Original Budget, Revised Budget, ForecastYear2 through ForecastYear10, and a Grand Total.

**Not seen:** salary or payroll data. There is no dedicated vendor-payments story; vendor names only appear inside the transaction grids.

### Fiscal years
- The budget-year dropdown and the distinct-values API both return **FY20-21, FY21-22, FY22-23, FY23-24, FY24-25, FY25-26, FY26-27**.
- The capital transaction detail goes back further, to July 2018 postings.
- The grids' `dataRefreshDate` is 2026-09-16, meaning the data refreshes daily.

### Dimensions you can slice by
- **Operating:** Department, Division, Fund, ORG/Costing Center, GL Category (Rollup), GL Account (Object), Account Type, Vendor/Item, Posting Date, Budget Year.
- **Capital:** Project (the ID is embedded in the name, e.g. `CIPST22064`), Project Type, Project Phase, Fund Source, CIP ORG, GL Account, Vendor/Item, Posting Date, Budget Year.
- **Revenue:** Fund.

### Downloads and API
- **CSV export:** each standalone visualization page has a "Data Export" footer link pointing to `https://glendaleaz.openbook.questica.com/api/CSV/606b5483-0ebe-49d6-81be-1d34ca56688f/link`. I did not click it.
- **Chart export:** Highcharts `exporting.js` and `export-data.js` are loaded, and each chart has a ≡ menu. [inferred] It probably offers PNG/CSV chart export; I did not open it.
- **Undocumented JSON API** (seen in network requests; all public GETs that returned 200 without logging in):
  - `GET /api/storyviewer/{storyId}`: story metadata and markup, which contains the visualization IDs.
  - `GET /api/Layouts/DataExplorer/{vizId}/Grid?fieldFilters=[...]&sortFields=[...]&startIndex=0&pageSize=25`: paged rows plus `numberOfRecords` and `dataRefreshDate`.
  - `GET /api/Layouts/DataExplorer/{vizId}/Chart?fieldFilters=[...]`
  - `GET /api/visualizationviewer/recordcount/{vizId}`
  - `GET /api/layouts/budget/{vizId}?h=Main Breakdown&l=1&gr=<BudgetYearField>&...`: returns the drill-down hierarchy and values. It returned 500 for Grid calls on budget-type visuals.
  - `GET /api/datasetquery/distinctvalues?datasetId=...&fieldId=...`

### Geographic attributes: NONE FOUND
- **No field in any OpenBook dataset carries a Council District, address, coordinates, facility or project-location attribute.**
- Capital projects are identified only by project number and name (e.g. `CIPST22064 - TRANSPORTATION SAFETY PROGRAM`), type, phase, ORG and fund.
- Mapbox GL CSS/JS loads on every page, but none of the 4 stories displays a map. [inferred] It is part of the platform bundle, not a map of Glendale data.
- **To get locations, join on the project number to the GIS CIP layers in Task 3.** The GIS `Munis_no` / `a_project` fields look like the same Munis project IDs. [inferred]

## Task 3 — Glendale GIS map gallery (gis.glendaleaz.com/maps/)

- **How the page is built:** it is a wrapper around an iframe. The iframe is ArcGIS Experience Builder at `https://gismaps.glendaleaz.com/gisportal/apps/experiencebuilder/experience/?id=6837e95249c1479d9f0a06cdcd9e340e&page=APPS-%26-MAPS`, titled "Public GIS Portal Redesign".
- **Tabs:** All Apps, Addressing, Code Enforcement, Community Services, Engineering, Parks, Planning & Property, Public Safety, Solid Waste, Transportation, Water.
- **Rendering problem:** the gallery cards showed only `{Name}` / `{Description}` placeholders.
- **Where the list really lives:** it is backed by the public web map "GIS APPLICATIONS" (item `deb0689e209245209546990b5352b1d6`), which points to the feature layer below. I read the list from that layer's query endpoint (attributes only, no geometry):
  - **`https://gismaps.glendaleaz.com/gisserver/rest/services/GIS_Applications_Public/FeatureServer/0`** — 32 records.

### All listed apps (from GIS_Applications_Public; all are public = Y, status Active)

| Name | Tag | Platform / ID | Description (as listed) |
|---|---|---|---|
| Address Finder | Addressing | Experience Builder (AGOL) `4af15db0…` | Search and locate valid city addresses |
| Address Point Extraction | Addressing | WebApp Builder (AGOL) `c167343f…` | Extract addresses by polygon/buffer for mailers |
| Address Validation Map | Addressing | gis.glendaleaz.com/address_val | Validate an address in Glendale |
| Aerial Imagery Compare | General Maps | AGOL ImageryViewer `60ee0a71…` | Current vs historical aerials |
| City Boundary Viewer | General Maps | Portal Experience Builder `3afa5163…` | City limit map |
| Touring Downtown Glendale | General Maps | AGOL MapTour `a49a1469…` | Downtown story map |
| **My Glendale Services** | General Maps | AGOL Instant "Nearby" `207f90cc…` | Trash, recycling, police, fire and **council districts** near you |
| City Street Ownership Map Viewer | General Maps | Portal Instant `38a5aeea…` | Street ownership |
| City of Glendale, AZ Digital Twin | General Maps | gismaps/site-videos/digital-twin.html | Google 3D tiles city model |
| **Planning Interactive Map** | Planning, Property | WebApp Builder (AGOL) `096fdb68…` | Planning data, easements, **zoning**, general plan |
| Development Sites Locator | Planning, Property | AGOL Dashboard `3da6ad72…` | Development sites and their planning status |
| Road Closures Dashboard | Transportation | Portal Dashboard `c69089ec…` | Road closures, traffic cameras, planned closures |
| Rehabilitated Streets Dashboard | Transportation | Portal Dashboard `0fbe6a5d…` | Rehabilitated streets and pavement projects |
| Streetlights Public Dashboard | Transportation | Portal Dashboard `0dd5dfce…` | Streetlights, pedestrian lights, cabinets, wiring |
| ROW Maintenance Contract Areas | Transportation | Portal Dashboard `e6bfba91…` | ROW areas for contractors |
| Park Finder | Parks | AGOL Shortlist `4b0e24a7…` | Parks, amenities, details |
| Police Incidents Public Viewer (Jan 2020–Jun 2022) | Public Safety | Portal WAB `56f29275…` | Incidents by crime code; redacted to 100 block |
| Police CFS Public Viewer (Jan 2020–Jun 2022) | Public Safety | Portal WAB `0064379b…` | Calls for service; 100-block redacted |
| Police CFS Public Viewer (Jun 2022–Current) | Public Safety | AGOL Dashboard `e7a62c76…` | Calls for service by location and type |
| Glendale Police Crime Data Viewer (Public) | Public Safety | Portal Dashboard `e3544958…` | Crime by location and type; 100-block redacted |
| Bulk Trash Pickup Status | Solid Waste | Portal Experience Builder `69efe658…` | Solid waste route status |
| **City of Glendale 10-Year Capital Improvement Plan** | Engineering | Portal Dashboard `1a202474…` | Review capital improvement projects |
| Engineering Warranty Inspections Report | Engineering | Power BI (app.powerbigov.us) | Inspection counts and pass rate |
| Engineering Invoices Report | Engineering | Power BI | Invoice counts and processing time |
| ArcGIS BA Dashboard | Community Services | AGOL Dashboard `a4c4a9de…` | Business Analyst dashboards and data |
| **Code Compliance Public Dashboard** | Code Enforcement | **Power BI** (app.powerbigov.us) | Public stats on Code Compliance cases created and resolved |
| NO APPLICATIONS YET | Code Enforcement | placeholder | "This group doesn't have applications yet" |
| **GlendaleOne Public and Council Report** | Budget and Finance | **Power BI** (app.powerbigov.us) | Statistics and performance metrics on GlendaleOne requests |
| Water Conservation Rebate Survey | Water Services | Survey123 | Rebate form |
| Water Distribution Service Requests | Water Services | Survey123 | Service request form |
| Environmental Resources Service Request | Water Services | Survey123 | Service request form |
| Wastewater Collections Service Request | Water Services | Survey123 | Service request form |

### Apps relevant to this project
- **Council districts:** My Glendale Services, Planning Interactive Map, and the 10-Year CIP dashboard. All three load a Council Districts layer.
- **Code compliance:** the Code Compliance Public Dashboard. It is **Power BI**, not ArcGIS, so it has no REST service.
- **Zoning and parcels:** Planning Interactive Map.
- **Service requests:** GlendaleOne Public and Council Report (Power BI) and the three Water Services Survey123 forms. **No ArcGIS map of GlendaleOne requests is in the gallery.**
- **Capital projects:** 10-Year Capital Improvement Plan dashboard. Rehabilitated Streets may also be relevant.
- **Neighborhoods:** no app is tagged for neighborhoods. The Planning map has Special Planning Areas and Historic Districts layers.

### ArcGIS REST service URLs

**10-Year CIP Dashboard** (`gismaps.glendaleaz.com/gisportal/apps/dashboards/1a202474c5f44692b006e71eb42d259e`, page title "CIP Munis-focus map Dashboard - Public Version"). *These URLs were seen in the page's network requests.*

- `https://gismaps.glendaleaz.com/cseam/rest/services/Planning/CIP_PROJECTS_SMARTSHEET_Pv2/MapServer`
  - Capabilities: Map, Query, Data. Max record count: 2000.
  - **Layer 0 "CIP Projects":** polygons, 784 features. Fields: Project__, Munis_no, Fiscal_Year, CITY_WIDE.
  - **Layer 1 "CIP_PROJECTS_SMARTSHEET_Pv2_dashboard":** polygons, 1,135 features, 77 fields. Fields include Project_Name, Status, **Address_Start, Address_End, Street**, Citywide flag, Munis__, Department, Project_Budget, Project_Cost, FY actuals, design and construction dates, and Council_Date.
  - **Layer 2 "CIP_PROJECTS_MUNIS_POLYS_for_Dashboard":** polygons, 1,665 features. Fields: Munis_no, a_project, Fiscal_Year, CITY_WIDE, ma_project_title, ma_description, ma_justification, ProjTypeDesc, segment descriptions.
  - **Table 3 "CIP_PROJECTS_SMARTSHEET":** 427 rows. Includes Address_Start / Address_End / Street.
  - **Table 4 "CIP_PROJECTS_MUNIS":** 1,945 rows, 84 fields (the Munis project master: type, department, status, dates, % complete, etc.).
  - **Table 5 "CIP_PROJECTS_MUNIS_NOT_IN_SMARTSHEET":** 4 fields.
  - **Location field:** capital projects have real **polygon geometry** (layers 0–2). Some layers also carry **Address_Start / Address_End / Street** text and a **CITY_WIDE** flag for projects with no single location.
  - **No field stores the council district.** You would get it with a spatial join to the Council Districts layer below.
- `https://gismaps.glendaleaz.com/gisserver/rest/services/AdminAreas/Council_Districts/MapServer/0`
  - Polygons, **6 features**. Fields: DIS_NAME, MEMBER, HANSEN_DISTRICT, plus GlobalID and edit-tracking fields.
  - DIS_NAME / HANSEN_DISTRICT values: **OCOTILLO/OCO, CACTUS/CAC, BARREL/BAR, SAHUARO/SAH, CHOLLA/CHO, YUCCA/YUC**. These match the 6 attachment filename suffixes.
- `https://gismaps.glendaleaz.com/gisserver/rest/services/Infra/CITY_STREETS_L/MapServer/0`
- `https://gismaps.glendaleaz.com/gisserver/rest/services/Glendale_Services/CityBoundary/MapServer` (layer 0)

**My Glendale Services** (AGOL Nearby `207f90cc…`, web map "My Glendale Services Map")
*These URLs come from the app's web-map configuration (`cog-gis.maps.arcgis.com/sharing/rest/content/items/<id>/data`), not from network traffic. The Nearby template only queries layers after an address is searched, which I did not do.*

- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/0` — City Limits
- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/3` — **Council Districts** (a second copy of the district layer)
- `…/gisserver/rest/services/Glendale_Services/GlendaleGovernmentServices/MapServer/1` — Libraries
- `…/gisserver/rest/services/Glendale_Services/GlendaleGovernmentServices/MapServer/3` — Fire Stations
- `…/gisserver/rest/services/Glendale_Services/GlendaleGovernmentServices/MapServer/4` — Police Stations
- `…/gisserver/rest/services/Glendale_Services/GlendaleGovernmentServices/MapServer/6` — Recycling Pickup
- `…/gisserver/rest/services/Glendale_Services/ParkPoints/MapServer/0` — Parks
- Trash Pickup plus more layers (the list was cut off in my output and not captured)

**Planning Interactive Map** (AGOL WAB `096fdb68…`, web map "Planning - Transparent")
*These URLs also come from the web-map configuration.*

- `…/gisserver/rest/services/AdminAreas/General_Plan/MapServer/8` — General Plan
- `…/gisserver/rest/services/AdminAreas/Misc_Glendale_Areas/MapServer/9` — **Zoning**
- `…/gisserver/rest/services/Glendale_Services/Land/MapServer/3` — **Parcels**
- `…/gisserver/rest/services/Glendale_Services/Land/MapServer/0` — **Address Points**
- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/0` — City Limits
- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/3` — **Council Districts**
- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/5` — Historic Districts
- `…/gisserver/rest/services/Glendale_Services/CityLimits/MapServer/6` — Special Planning Areas
- `…/gisserver/rest/services/Planning/LUKE_AFB_NOISE_CONTOUR_P_fea/FeatureServer/0` — Luke AFB Noise Contours
- `…/gisserver/rest/services/Planning/PLANNING_CENTERLINE_P/MapServer/0` — Centerline
- `…/gisserver/rest/services/GIS_Land_GISADMIN_LN_EASEMENT_P/MapServer/0` — Easements
- `https://services1.arcgis.com/Ua5sjt3LWTPigjyD/ArcGIS/rest/services/School_Districts_Current/FeatureServer/0` — Unified, High School and Elementary school districts (the same layer used 3 times, presumably with different filters [inferred])

(`…` = `https://gismaps.glendaleaz.com`)

### Portal and platform notes
- **Two ArcGIS environments** are in use:
  - Enterprise portal at `gismaps.glendaleaz.com/gisportal`, with servers `/gisserver` and `/cseam`
  - ArcGIS Online org `cog-gis.maps.arcgis.com`
- **Bot protection:** `gis.glendaleaz.com` sits behind Incapsula (`_Incapsula_Resource` requests were seen).
- **Not opened:** I did not open the Code Compliance or GlendaleOne Power BI reports. They are Power BI embeds with no ArcGIS REST endpoints. [inferred]
- **Takeaway for the district question:** district-level analysis should come from spatially joining GlendaleOne and Code Compliance points (from Open Data) to `AdminAreas/Council_Districts/MapServer/0`. [inferred]
