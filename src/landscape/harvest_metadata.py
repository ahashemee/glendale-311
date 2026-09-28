#!/usr/bin/env python3
"""
harvest_metadata.py -- inventory the datasets the City of Glendale publishes, WITHOUT
downloading any rows.

Sources
  agol       ArcGIS Online org 9fVTQQSiODPjLUTa (a.k.a. cog-gis.maps.arcgis.com),
             Feature Services + Map Services
  hub        opendata.glendaleaz.com catalog API (which AGOL items the portal lists)
  gisserver  gismaps.glendaleaz.com/gisserver  ArcGIS Enterprise server directory
  cseam      gismaps.glendaleaz.com/cseam      ArcGIS Enterprise server directory

Guarantees (enforced in fetch(), not by convention)
  * Any /query call must carry returnCountOnly=true, outStatistics, or
    resultRecordCount<=10. Replica/extract/export/item-data endpoints are refused.
  * No response over 5 MB is read; the run stops instead.
  * Every raw response body is cached under src/.cache/raw/, and every network hit is
    appended to src/.cache/fetch_log.jsonl. Reruns only touch the network for new URLs.

Usage
  python3 src/harvest_metadata.py                 # full run
  python3 src/harvest_metadata.py --catalog-only  # enumerate + triage, no schemas
  python3 src/harvest_metadata.py --offline       # cache only; a cache miss is an error
  python3 src/harvest_metadata.py --refresh       # ignore cache, refetch everything

Inputs
  src/field_notes.json   [inferred] field descriptions and '#quirk' notes for High/Medium fields

Outputs (src/.cache/)
  raw/                     raw response bodies; *.transient.json = saved timeouts/server errors
  fetch_log.jsonl          one line per network fetch (URL, bytes, time)
  index.tsv                cache file -> URL -> first fetched_at
  catalog.json             every service found, with source, triage tier and reason
  harvest.json             probes (schemas, row counts) and deep statistics (non-null, empty-string,
                           date range, value counts, sums) with the cache file behind each number
  join_checks.json         key-overlap and count checks used by the relationship map
  landscape_fragments.md   rendered Section 1 table, Section 2 field tables, join checks
  missing_field_notes.tsv  High/Medium fields that still lack any description

Then run src/build_landscape.py to merge the fragments into DATA_LANDSCAPE.md.
"""

import argparse
import hashlib
import json
import re
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
RAW = CACHE / "raw"
FETCH_LOG = CACHE / "fetch_log.jsonl"

AGOL_ORG = "9fVTQQSiODPjLUTa"
AGOL_SEARCH = "https://www.arcgis.com/sharing/rest/search"
AGOL_ITEM = "https://www.arcgis.com/sharing/rest/content/items/{id}?f=json"
HUB_ITEMS = "https://opendata.glendaleaz.com/api/search/v1/collections/{collection}/items"
ENTERPRISE_ROOTS = {
    "gisserver": "https://gismaps.glendaleaz.com/gisserver/rest/services",
    "cseam": "https://gismaps.glendaleaz.com/cseam/rest/services",
}

MAX_BYTES = 5 * 1024 * 1024
PAUSE_S = 0.15
UA = "ASU-CIS450-metadata-harvest/1.0 (metadata only; no row downloads)"

OFFLINE = False
REFRESH = False


# --------------------------------------------------------------------------------------
# HTTP + cache
# --------------------------------------------------------------------------------------

class BulkFetchRefused(RuntimeError):
    pass


class CacheMiss(RuntimeError):
    pass


class ArcGISError(RuntimeError):
    def __init__(self, url, err):
        super().__init__(f"{err.get('code')} {err.get('message')} <- {url}")
        self.code = err.get("code")
        self.url = url


REFUSED_PATH = re.compile(
    r"/(createReplica|replicas|extractData|export\w*|queryRelatedRecords|queryAttachments"
    r"|queryTopFeatures|generateRenderer)\b|/content/items/[0-9a-f]{32}/data\b",
    re.I,
)


def check_metadata_only(url):
    """Raise unless the URL is a metadata/count/statistics call."""
    p = urlparse(url)
    if REFUSED_PATH.search(p.path):
        raise BulkFetchRefused(f"refused endpoint: {url}")
    if not re.search(r"/query/?$", p.path, re.I):
        return
    qs = {k.lower(): v[-1] for k, v in parse_qs(p.query).items()}
    if qs.get("returncountonly", "").lower() == "true":
        return
    if qs.get("outstatistics"):
        return
    rrc = qs.get("resultrecordcount", "")
    if rrc.isdigit() and int(rrc) <= 10:
        return
    raise BulkFetchRefused(f"/query without count/statistics/<=10 limit: {url}")


def cache_path(url, ext="json"):
    p = urlparse(url)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", p.path).strip("_")[-110:]
    digest = hashlib.sha1(url.encode()).hexdigest()[:12]
    return RAW / p.netloc / f"{slug}__{digest}.{ext}"


def rel(path):
    return str(path.relative_to(HERE.parent))


def _download(url):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    last = None
    for attempt in range(3):
        try:
            try:
                resp = urlopen(req, timeout=90)
                status = resp.status
            except HTTPError as e:
                resp, status = e, e.code
            chunks, total = [], 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    raise RuntimeError(f"response exceeds 5 MB, stopping (ask first): {url}")
                chunks.append(chunk)
            return status, b"".join(chunks)
        except (URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"network failure after 3 tries: {url}: {last}")


def norm_url(url):
    p = urlparse(url)
    return p._replace(path=quote(p.path, safe="/%:@")).geturl()


def fetch(url, allow_error=False):
    """GET a JSON metadata URL through the guard and cache. Returns (data, cache_file)."""
    url = norm_url(url)
    check_metadata_only(url)
    path = cache_path(url)
    transient = path.with_suffix(".transient.json")
    if path.exists() and not REFRESH:
        body = path.read_bytes()
    elif transient.exists() and not REFRESH:
        # A saved transient error (e.g. a server timeout) is reused so reruns do not keep
        # hammering a failing service; pass --refresh to try it again.
        body, path = transient.read_bytes(), transient
    else:
        if OFFLINE:
            raise CacheMiss(url)
        status, body = _download(url)
        try:
            data = json.loads(body)
        except ValueError:  # e.g. an HTML 404 page: keep it as a JSON error record
            data = {"error": {"code": status, "message": f"non-JSON response (HTTP {status})",
                              "details": [body[:300].decode(errors="replace")]}}
            body = json.dumps(data).encode()
            status = -1  # forces the transient path below
        err = data.get("error") if isinstance(data, dict) else None
        if not (status == 200 and (not err or err.get("code") in (400, 403, 404, 498, 499))):
            path = transient
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        with FETCH_LOG.open("a") as log:
            log.write(json.dumps({
                "file": rel(path), "url": url, "http": status, "bytes": len(body),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }) + "\n")
        time.sleep(PAUSE_S)
    data = json.loads(body)
    if isinstance(data, dict) and isinstance(data.get("error"), dict) and not allow_error:
        raise ArcGISError(url, data["error"])
    return data, rel(path)


def fetch_xml(url):
    """GET an XML metadata document through the same guard and cache. Returns (text|None, file)."""
    url = norm_url(url)
    check_metadata_only(url)
    path = cache_path(url, ext="xml")
    miss = path.with_suffix(".miss")
    if not REFRESH and path.exists():
        return path.read_text(errors="replace"), rel(path)
    if not REFRESH and miss.exists():
        return None, rel(miss)
    if OFFLINE:
        raise CacheMiss(url)
    status, body = _download(url)
    ok = status == 200 and body.lstrip()[:1] == b"<"
    target = path if ok else miss
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body if ok else f"HTTP {status}\n".encode() + body[:2000])
    with FETCH_LOG.open("a") as log:
        log.write(json.dumps({"file": rel(target), "url": url, "http": status, "bytes": len(body),
                              "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
    time.sleep(PAUSE_S)
    return (body.decode(errors="replace") if ok else None), rel(target)


def qurl(base, **params):
    return f"{base}?{urlencode(params, quote_via=quote)}"


# --------------------------------------------------------------------------------------
# Catalog
# --------------------------------------------------------------------------------------

def catalog_agol():
    q = f'orgid:{AGOL_ORG} (type:"Feature Service" OR type:"Map Service")'
    items, start, total, pages = {}, 1, None, []
    while start and start > 0:
        data, src = fetch(qurl(AGOL_SEARCH, q=q, num=100, start=start,
                               sortField="created", sortOrder="asc", f="json"))
        total = data["total"]
        pages.append(src)
        for r in data["results"]:
            items[r["id"]] = r
        start = data.get("nextStart", -1)
    if total != len(items):
        print(f"  note: AGOL search total={total} but {len(items)} unique ids", file=sys.stderr)
    out = []
    for r in items.values():
        out.append({
            "source": "agol", "key": r["id"], "item_id": r["id"], "title": r["title"],
            "name": r.get("name") or "", "type": r["type"], "url": r.get("url") or "",
            "owner": r.get("owner"), "access": r.get("access"),
            "created": r.get("created"), "modified": r.get("modified"),
            "snippet": r.get("snippet") or "", "tags": r.get("tags") or [],
            "categories": r.get("categories") or [], "size": r.get("size"),
            "typeKeywords": r.get("typeKeywords") or [],
        })
    return out, {"total": total, "pages": pages}


def catalog_hub():
    """Items the open-data portal surfaces. Returns {collection: {item_id: title}}."""
    listed, provenance = {}, {}
    for collection in ("dataset", "all"):
        ids, start, matched = {}, 1, None
        while True:
            data, src = fetch(qurl(HUB_ITEMS.format(collection=collection),
                                   limit=100, startindex=start))
            matched = data.get("numberMatched", matched)
            provenance.setdefault(collection, []).append(src)
            for feat in data.get("features", []):
                p = feat.get("properties", {})
                ids[feat["id"]] = {"title": p.get("title"), "type": p.get("type"),
                                   "orgId": p.get("orgId"), "url": p.get("url")}
            got = data.get("numberReturned", len(data.get("features", [])))
            if got == 0 or len(ids) >= (matched or 0):
                break
            start += got
        listed[collection] = {"numberMatched": matched, "items": ids}
    return listed, provenance


DATA_SERVICE_TYPES = ("FeatureServer", "MapServer")


def catalog_enterprise(label, root):
    """One record per service name; FeatureServer and MapServer twins are collapsed."""
    top, src = fetch(f"{root}?f=json")
    provenance, folders = [src], {"(root)": {"services": len(top.get("services", [])), "src": src}}
    services = list(top.get("services", []))
    for folder in top.get("folders", []):
        sub, s = fetch(f"{root}/{quote(folder)}?f=json", allow_error=True)
        provenance.append(s)
        if isinstance(sub.get("error"), dict):
            folders[folder] = {"error": f"{sub['error'].get('code')} {sub['error'].get('message')}", "src": s}
            continue
        folders[folder] = {"services": len(sub.get("services", [])), "src": s}
        services.extend(sub.get("services", []))
    by_name, other_types = {}, []
    for svc in services:
        if svc["type"] not in DATA_SERVICE_TYPES:
            other_types.append(svc)
            continue
        by_name.setdefault(svc["name"], set()).add(svc["type"])
    out = []
    for name, types in sorted(by_name.items()):
        primary = "FeatureServer" if "FeatureServer" in types else "MapServer"
        out.append({
            "source": label, "key": f"{label}:{name}", "item_id": None,
            "title": name.split("/")[-1], "name": name,
            "folder": name.split("/")[0] if "/" in name else "",
            "type": primary, "types": sorted(types), "url": f"{root}/{name}/{primary}",
        })
    return out, {"folders": folders, "pages": provenance, "currentVersion": top.get("currentVersion"),
                 "non_data_services": other_types}


# --------------------------------------------------------------------------------------
# Triage
# --------------------------------------------------------------------------------------

# Services that are never datasets for this project, by name pattern.
NOISE_PATTERNS = [
    (re.compile(r"_(form|fieldworker|stakeholder|results?)(_|$)", re.I), "Survey123 artifact"),
    (re.compile(r"^survey123_", re.I), "Survey123 artifact"),
    (re.compile(r"(^|[_\s])test([_\s\d]|$)|testing|_copy$|\bcopy\b", re.I), "test/copy layer"),
    (re.compile(r"basemap|hillshade|imagery|aerial|ortho|_tiles?$|vector ?tile|labels?$", re.I),
     "cartographic/basemap service"),
    (re.compile(r"^(Utilities/Geometry|Utilities/PrintingTools|SampleWorldCities|"
                r"System/|Hosted/.*_test)", re.I), "platform utility service"),
]

def T(tier, theme, why, **kw):
    """One curated triage entry.

    tier   High   needed to answer Q1-Q4 directly (request populations, districts, denominators)
           Medium a join key, covariate or finer geography that Q1-Q5 can use
           Low    tangential context, or a duplicate/broken copy of a relevant dataset
           None   unrelated (default for anything not listed here)
    kw     q, label, layers, date_field, value_fields, sum_fields, field_groups,
           mirror_of, district, notes
    """
    return dict(tier=tier, theme=theme, why=why, **kw)


SR, GEO, DEM, PROP, SAFE, INFRA = ("service requests", "geography", "demographics", "property",
                                   "public safety", "infrastructure")
PL94 = [(r"^P001\d{4}$", "Census 2020 P.L. 94-171 table P1: race (total population and race combinations)"),
        (r"^P002\d{4}$", "Table P2: Hispanic or Latino, and not Hispanic or Latino by race"),
        (r"^P003\d{4}$", "Table P3: race for the population 18 years and over"),
        (r"^P004\d{4}$", "Table P4: Hispanic or Latino by race, 18 years and over"),
        (r"^P005\d{4}$", "Table P5: group quarters population by major group quarters type"),
        (r"^H001\d{4}$", "Table H1: housing units (total, occupied, vacant)"),
        (r"^PCT_", "Derived percentage of a P2/P3/H1 cell"),
        (r"^(SUMLEV|REGION|DIVISION|STATE|STATENS|COUNTY|COUNTYCC|COUNTYNS|COUSUB\w*|SUBMCD\w*|ESTATE\w*|CONCIT\w*|"
         r"PLACE\w*|AIANHH\w*|AIHHTLI|AITS\w*|TTRACT|TBLKGRP|ANRC\w*|CBSA\w*|MEMI|CSA|METDIV|NECTA\w*|NMEMI|CNECTA|"
         r"UA|UATYPE|UR|CD116|SLDU18|SLDL18|VTD|VTDI|ZCTA|SDELM|SDSEC|SDUNI|PUMA|AREALAND|AREAWATR|SUFFIX|BASENAME|"
         r"FUNCSTAT|GCUNI|PARTFLAG|UGA|INTPTLAT|INTPTLON)$",
         "P.L. 94-171 geographic header codes (summary level, state/county/place, districts, urban/rural, land area, "
         "internal point)")]

GL1, CODE, ESC, CD_HOSTED, ADDR_CD = ("37a2cb9cf728424d8c0f5c1f64621939", "8026de93be8147d2aa2941c3e7ceed97",
                                      "9f44c29d057e49709a5903a2e8aee8a7", "887a7efe02224f0ba5f3d490e59b43ea",
                                      "632036b8ebd34f6181b0c60a7cb9198c")

# Insertion order sets the order of the Section 2 detail entries.
TRIAGE = {
    # ---- High ------------------------------------------------------------------------
    GL1: T("High", SR, "The GlendaleOne 311 request population and the only request source that already carries "
           "Council District.", q="Q1–Q5", date_field="Request_Date",
           value_fields=["Council_District", "Status", "Request_Type_Group", "Responsible_Department_Name",
                         "Request_Type"]),
    CODE: T("High", SR, "The Code Compliance case population; district must be derived because `District` is empty.",
            q="Q1–Q5", date_field="RequestDate",
            value_fields=["District", "RequestStatus", "Proactive", "CodePropertyType", "RequestTypeName", "CityName"],
            district="N (`District` is an empty string on every row); derivable (spatial or address)"),
    ESC: T("High", SR, "Per-request-type department, route and escalation timer: the closest published thing to a "
           "service-level target for GlendaleOne request types.", q="Q2, Q5", layers=[1], date_field="DateLoaded",
           value_fields=["Department_Name", "Request_Group", "Request_Type_Name", "Route1", "Escalate_Time1",
                         "Escalates_in_", "Is_Private1"],
           district="N/A (lookup keyed by request type)"),
    CD_HOSTED: T("High", GEO, "The district polygons; `DIS_NAME` is the join key to requests and to the workbook "
                 "filenames.", q="Q1, Q3, Q4", date_field="last_edited_date",
                 value_fields=["DIS_NAME", "HANSEN_DISTRICT", "MEMBER"], district="Y (`DIS_NAME`; is the district layer)"),
    ADDR_CD: T("High", GEO, "Address → `COUNCIL` crosswalk: the non-spatial route to put code cases in a district.",
               q="Q1, Q4", date_field="last_edited_date", value_fields=["COUNCIL", "CITY", "ADDRESS_TYPE", "ADD_LEVEL"]),
    "gisserver:PopDensity/Census_Block_2020_pts": T(
        "High", DEM, "Census 2020 P.L. 94-171 counts by block: an official population denominator below district "
        "level that can be aggregated to districts independently of the Esri workbooks.", q="Q1",
        label="Census 2020 block population points", field_groups=PL94,
        sum_fields=["P0010001", "H0010001", "H0010002"], value_fields=[], vintage="Census 2020 (P.L. 94-171)",
        district="Derivable (spatial; block centroid points)"),
    "gisserver:OpenData/GLENDALEONE_EXTERNAL_REQUESTS_PTS": T(
        "High", SR, "Enterprise layer that the AGOL hosted requests service carries the name of.", q="Q1–Q5",
        label="GlendaleOne External Requests (Enterprise layer)", mirror_of=GL1, date_field="DateLoaded",
        district="Y (`Council_District`)"),
    "gisserver:OpenData/GlendaleOne_Escalations": T(
        "High", SR, "Enterprise copy of the escalation table.", q="Q2, Q5", layers=[1], mirror_of=ESC,
        label="GlendaleOne Escalations (Enterprise layer)", date_field="DateLoaded",
        district="N/A (lookup keyed by request type)"),
    "8a440beae0c94eb8b91df341ec02fe04": T(
        "High", SR, "Second portal item for the escalation table, registered against the Enterprise layer.",
        q="Q2, Q5", mirror_of=ESC, label="GlendaleOne Escalations (portal item → Enterprise)",
        date_field="DateLoaded", district="N/A (lookup keyed by request type)"),
    "gisserver:AdminAreas/Council_Districts": T(
        "High", GEO, "Enterprise district layer used by the CIP dashboard.", q="Q1, Q3, Q4", mirror_of=CD_HOSTED,
        label="Council Districts (Enterprise AdminAreas)", date_field="last_edited_date",
        district="Y (`DIS_NAME`; is the district layer)"),
    # ---- Medium ----------------------------------------------------------------------
    "gisserver:ADDRESS_100BLOCK": T(
        "Medium", GEO, "One point per 100-block, the unit GlendaleOne anonymizes to; the candidate key for request "
        "`FULL_ADDRESS` / `ANON_BLOCK`.", q="Q1, Q4", label="100-block address points",
        date_field="last_edited_date", value_fields=["CITY", "STREET_TYP"]),
    "gisserver:LN_ADDRESS_PT_APN_JOIN": T(
        "Medium", PROP, "Address points carrying both `COUNCIL` and `APN`, bridging code-case addresses to assessor "
        "parcels.", q="Q4, Q5", label="Address points joined to APN", date_field="last_edited_date",
        value_fields=["COUNCIL", "CITY", "ADDRESS_TYPE"]),
    "gisserver:Parcels": T(
        "Medium", PROP, "Parcels carrying `DIS_NAME`, land-use code and zoning; a point-in-parcel join assigns district "
        "and land use to code cases.", q="Q4, Q5", layers=[6], label="Parcels (city)", date_field="last_edited_date",
        value_fields=["DIS_NAME", "CITYJUR", "COG_OWN", "LUCODE"]),
    "gisserver:ASSESSOR_PARCEL_VIEW": T(
        "Medium", PROP, "Maricopa County Assessor attributes per parcel (use code, owner mailing vs situs address, "
        "build year, exemptions): the only published proxy for rental or absentee ownership.", q="Q5",
        label="Assessor parcel view", date_field="SALE_DATE",
        value_fields=["JURISDICTION", "PUC_DESC", "PHYSICAL_CITY", "EXEMPT_TYPE_CUR", "PSC", "TAX_YR_CUR"]),
    "gisserver:Community_Services/Glendale_qct_rates": T(
        "Medium", DEM, "Block groups with current-year Esri income, tenure and wealth plus tract-level HUD Qualified "
        "Census Tract and ACS poverty fields: equity covariates finer than district.", q="Q1, Q5",
        label="Block groups with Esri demographics and HUD QCT fields", value_fields=["qct", "metro20"]),
    "79ae505f4eb04f33b17efe01d88bff3b": T(
        "Medium", DEM, "Esri-enriched polygons with population, households below poverty, children under 15 and "
        "median household income.", q="Q5", sum_fields=["POPULATION", "TOTPOP_CY", "ACSHHBPOV", "POPU14_CY"],
        value_fields=["COUNTY", "aggregationMethod", "HasData"]),
    "gisserver:Code_Compliance/Code_Compliance_Grids": T(
        "Low", SR, "Six Code Compliance grids named after the council districts; the `CASES`, `STAFF` and "
        "`ADOPTED` fields are empty (see Section 1 evidence).", q="Q4, Q5", layers=[2], label="Code Compliance Grids", date_field="last_edited_date",
        value_fields=["GRID", "STAFF", "ADOPTED"]),
    "a4ba51c9e57548aabc261b3e2e3d9cb3": T(
        "Medium", SR, "72 sub-zones, each assigned to a named inspector (`STAFF`) under `QUARTER` = 'Quarter 1'; "
        "the start/end date and completed fields exist but are empty. The only published inspector-to-area "
        "assignment.", q="Q5", date_field="last_edited_date",
        value_fields=["GRID", "QUARTER", "COMPLETED", "STAFF"]),
    "gisserver:POLICE_GRID": T(
        "Medium", GEO, "650 grid cells each carrying police `BEAT`/`SECTOR` and `CC_DIST`, whose values are council "
        "district names (title case) or 'Outside Glendale': a published grid → beat → council district crosswalk.",
        q="Q4, Q5", label="Police grid with council district (`CC_DIST`)",
        date_field="last_edited_date", value_fields=["CC_DIST", "BEAT", "SECTOR", "CAT_TEAMS"]),
    "gisserver:NEIGHBORHOOD_P_w_MgmtCompany": T(
        "Medium", GEO, "Registered neighborhood organizations with council district, HOA flag and management company; "
        "HOA coverage is a candidate explanation for who reports to the City.", q="Q5",
        label="Registered neighborhoods with HOA / management company", date_field="DateEntered",
        value_fields=["CouncilDistrict", "HOA_1", "Status_1", "MgmtCompany", "BlockWatch", "SchoolDistrict"],
        notes="Carries organization representative names, phone and email fields. Only counts and statistics "
              "were queried."),
    "gisserver:Sanitation/Sanitation_Polys": T(
        "Medium", INFRA, "Trash/Recycle is the largest request group; these polygons give collection day, route and "
        "section to compare missed-collection and container requests against.", q="Q3, Q4",
        label="Sanitation day routes, routes and inspection areas", date_field="last_edited_date",
        value_fields=["DAY_ROUTE", "SECTION", "ROUTE", "STAFF_NAME", "INSPECT_ID"]),
    "08fb381ac3664073869efb65d2cc8ac6": T(
        "Medium", SAFE, "Dispatched police calls already tagged with council district: a second district-keyed demand "
        "signal next to GlendaleOne (Police Department receives GlendaleOne parking and vehicle requests).",
        q="Q5", layers=[1], date_field="CallDatetime",
        value_fields=["CouncilDistrict", "CallPriority", "PatrolDivision", "DayofWeek"]),
    "c297db43ca0244d5b273b9c4f68b9a7c": T(
        "Medium", SR, "Resident service requests submitted through a Survey123 form instead of GlendaleOne: a "
        "request stream in neither sponsor dataset.", q="Q2, Q5", layers=[0], date_field="CreationDate",
        label="Water Distribution Service Requests (Survey123)", value_fields=["service_request_details"],
        district="Derivable (spatial, if survey points are placed) [unverified]",
        notes="Fields hold requester name and email. Only counts and statistics were queried. Sibling Survey123 "
              "forms for Wastewater Collections and Environmental Resources are listed as Low."),
    "cseam:Parks/Park_Work_Request_Points": T(
        "Low", SR, "Parks work requests with a `glendale_one_request` field that is empty on every row (see join "
        "checks).", q="Q2, Q5", label="Parks work requests (CentralSquare EAM)",
        date_field="created_date",
        value_fields=["reqcategory", "reqtype", "status", "source", "region", "type", "esritask_status", "parktype"],
        notes="Carries requester contact fields (`pocfirstname`, `pocphone`, `pocemail`). Only counts and statistics "
              "were queried."),
    # ---- Low: duplicates / registrations of the datasets above -----------------------
    "gisserver:OpenData/Police_Calls_for_Service": T("Low", SAFE, "Enterprise copy of Police Calls for Service.",
                                                     layers=[1], label="Police Calls for Service (Enterprise layer)"),
    "gisserver:AdminAreas/Council_Districts_fea": T("Low", GEO, "Another copy of the district polygons."),
    "gisserver:Glendale_Services/Council_Districts": T("Low", GEO, "Another copy of the district polygons."),
    "27fc18be7f0a4f5eb3054edd8881ddf0": T("Low", GEO, "Another copy of the district polygons."),
    "fa232710a27e4a999fe144affa158b4b": T("Low", GEO, "Portal item for CityLimits layer 3 (districts)."),
    "e91ae56785e84b888c488238808b70d5": T("Low", GEO, "Layers behind Power BI maps: districts, beats and the grid "
                                          "crosswalk also in POLICE_GRID."),
    "gisserver:Glendale_Services/CityLimits": T("Low", GEO, "City limits, annexations, districts, ZIPs, historic and "
                                                 "school districts in one service."),
    "gisserver:AdminAreas/Misc_Glendale_Areas": T("Low", GEO, "Planning map service including districts, parcel land "
                                                   "use and zoning."),
    "gisserver:Code_Compliance/Senior_Code_Compliance_Grids": T("Low", SR, "Senior-inspector grid variant."),
    "gisserver:CODE_COMPLIANCE_SR_SUB_GRID_P": T("Low", SR, "Senior-inspector sub-grid variant."),
    "gisserver:CODE_COMPLIANCE_SUB_GRID_P": T("Low", SR, "Enterprise copy of the sub-grid (fewer zones than hosted)."),
    "4df1066e23f54c60aa1c818084fb56f7": T("Low", SR, "Copy of the sub-grid."),
    "b501907963d144f0ad446c1c319005e0": T("Low", SR, "Copy of the sub-grid."),
    "b97115abf9774943951f0415d880dc72": T("Low", SR, "Temporary copy of the sub-grid."),
    "gisserver:Land/CODE_COMPLIANCE_TERRITORIES_P": T("Low", SR, "Inspector territories (older or parallel scheme "
                                                      "to the grids) [inferred]."),
    "929f8dbbce824668897c923e72a230ce": T("Low", PROP, "Address points without the district field focus.",
                                          date_field="last_edited_date"),
    "gisserver:OpenData/Address_Points": T("Low", PROP, "Enterprise copy of the address points."),
    "d46fe5ea104c4d0784af730c3b34444c": T("Low", PROP, "Copy of the address points."),
    "46c809cf75344922b5396c7f00cbaaa3": T("Low", PROP, "Portal item for Land layer 0 (address points)."),
    "d8fdd961fdb14c5dbf581e9f606c9148": T("Low", PROP, "Portal item for Land layer 0 (address points)."),
    "gisserver:ADDRESS_ZIP_CHECK": T("Low", PROP, "Address points with ZIP validation fields."),
    "gisserver:NG911_Glendale": T("Low", PROP, "NG911 address points, road centerlines and ESN/ZIP boundaries."),
    "gisserver:Glendale_Services/Land": T("Low", PROP, "Address points, streets, footprints and parcels in one "
                                          "service."),
    "gisserver:PopDensity/PopDensity": T("Low", PROP, "Address points and city boundary behind the population "
                                         "density map."),
    "gisserver:PopDensity/block_pop": T("Low", DEM, "Block population service; its metadata request timed out, so "
                                        "contents are [unverified]."),
    "dbf3db308f63471c81d28fa8d11a307d": T("Low", PROP, "Portal item for Land layer 3 (parcels)."),
    "gisserver:Report_Tools/LN_PARCEL_P": T("Low", PROP, "Copy of the city parcels."),
    "24622911ffe54431af985029081506ff": T("Low", DEM, "Portal item whose Census service was removed.",
                                          label="Glendale Census Block Groups (service removed)"),
    "3d04edb172794597bb806a1e98d7fd3c": T("Low", DEM, "Portal item whose Census service was removed.",
                                          label="Glendale Census Blocks (service removed)"),
    "727bfbad45ef4df7ba1f4a3f0df6694b": T("Low", DEM, "Portal item whose Census service was removed.",
                                          label="Glendale Census Tracts (service removed)"),
    "819d484e45b04f1881e85daf25a7f69f": T("Low", GEO, "Portal item for the neighborhood polygons."),
    "gisserver:Glendale_Services/Neighborhood": T("Low", GEO, "Neighborhood polygons with `CNCL_DIST` and HOA."),
    "ece86f675b32418b8ff7546b74337906": T("Low", GEO, "2021 join of neighborhoods to organizations."),
    "997abf68397d454aaac6b76b5fd2aaef": T("Low", GEO, "2022 join of neighborhoods."),
    "91551d78bd9a4a37ac4626b9fa54e59d": T("Low", GEO, "Neighborhood service now token-secured."),
    # ---- Low: context ----------------------------------------------------------------
    "2565b89bed184a89aa0300c85fe14c43": T("Low", SAFE, "NIBRS offenses tagged with council district.", layers=[2],
                                          date_field="Occurred_On_Date"),
    "gisserver:OpenData/GPD_Crime_Data": T("Low", SAFE, "Enterprise copy of GPD crime data."),
    "1988a2acee844bfb874f2f70f4ebd1bf": T("Low", SAFE, "Fire incidents tagged with council district and tract.",
                                          date_field="INCIDENT_DATE"),
    "c5b87660b6a745328f883d1a106822b2": T("Low", SAFE, "Portal item for an Enterprise incidents table that has 0 rows."),
    "gisserver:OpenData/Police_Incidents_1": T("Low", SAFE, "Incidents table with 0 rows.", layers=[1]),
    "gisserver:Public_Safety/Police_Public_Mapping_Layers": T("Low", SAFE, "Redacted incident and CFS points."),
    "gisserver:Public_Safety/Police_Public_Export_Layers": T("Low", SAFE, "Redacted incident and CFS points."),
    "6267a217bcc74b849c948b497ce9b08d": T("Low", SAFE, "Redacted call-for-service points tagged with "
                                          "`Council_District_GIS`; copies and views of it are listed as None.",
                                          date_field="last_edited_date"),
    "5f561718f6854de992aae37b17477b11": T("Low", SAFE, "Police response-time records, no district field.",
                                          date_field="incident_date"),
    "gisserver:Fire_SOC_Dashboard": T("Low", SAFE, "Fire standards-of-cover goals vs actuals."),
    "gisserver:Fire/FireFirstDue_4min": T("Low", SAFE, "Fire first-due 4-minute coverage areas."),
    "1565c794fee649f78cfe938f82b92c34": T("Low", SAFE, "Police beats and grids."),
    "gisserver:POLICE_BEATS": T("Low", SAFE, "Police beats."),
    "gisserver:Public_Safety/Police_Polys": T("Low", SAFE, "Police beats, patrol zones and divisions."),
    "099c0fc42b1e42dfbd1d68b434a7a4ce": T("Low", SAFE, "Law enforcement district template, 0 rows."),
    "fd105ecd5b854227a3e94a62bc5a3363": T("Low", SR, "Survey123 service-request channel (Wastewater Collections).",
                                          layers=[0], date_field="CreationDate"),
    "be5da2e2f22b4750ac414253564290de": T("Low", SR, "Survey123 service-request channel (Environmental Resources).",
                                          layers=[0], date_field="CreationDate"),
    "e51d453394844523b51487b778512b1f": T("Low", SR, "Parks and grounds request form results.", layers=[0],
                                          date_field="created_date"),
    "11946bf814c14120b396035d3c3a2299": T("Low", SR, "Parks request app layer.", layers=[0], date_field="created_date"),
    "ffe11522aae94316a65079f963a841c0": T("Low", SR, "Parks request submission view (query disabled)."),
    "7d3c81add1df44dc907f82e306487438": T("Low", SR, "Portal item for the parks work request layer."),
    "16633ca2e7dd4398935bfb4eec5192a4": T("Low", SR, "Proxied portal item for the parks work request layer."),
    "64caa0fdf46248859c3c8a152603800a": T("Low", SR, "Proxied portal item for the parks work request layer."),
    "fe6f30f2b72f425fabeb37960beeb391": T("Low", SR, "Parks work assignments (proxied)."),
    "c3a919d72e3b4fb5a77d7652767d4eb5": T("Low", SR, "GlendaleOne customer feedback survey view (query disabled)."),
    "4b73972209974186a770aa442731ec2b": T("Low", SR, "Code compliance assistance request form view (query disabled)."),
    "ac8af0f71beb4cbe8d1cf4d3a36f8aad": T("Low", SR, "Vision Zero public comment points."),
    "eaefcc1fcb244199ade46337fa5973bc": T("Low", SR, "Escalation-levels layer; service not found."),
    "bfc147e0204a48dc80717693a1600d7c": T("Low", SR, "Escalation-levels service; token required."),
    "85270a1ac636476c9dbafc9c8d6e055d": T("Low", PROP, "Rental facilities; Enterprise service not started."),
    "30ecfc0985e945d18bd8c1494a946c0c": T("Low", PROP, "Business licenses with a `District` field.",
                                          date_field="IssuedOn",
                                          district="Unclear (`District` field; meaning [unverified])"),
    "gisserver:OpenData/Business_Licenses": T("Low", PROP, "Enterprise copy of business licenses.", layers=[1],
                                              district="Unclear (`District` field; meaning [unverified])"),
    "gisserver:Community_Services/Homeless_PIT_Zone": T("Low", DEM, "Homeless point-in-time count zones."),
    "gisserver:Community_Services/Homeless_Encampmentsv1": T("Low", DEM, "Homeless encampments; token required."),
    "57d45b10e0cc40f7af9802ea5cb56929": T("Low", DEM, "Heat relief locations."),
    "8145fd0eeb544de7b3aa7a975b9d5a90": T("Low", INFRA, "Collection-area polygons; the item title does not match the "
                                          "layer it registers (MapServer layer 6)."),
    "86175c665b2e46bd93c31fca8c3a015d": T("Low", INFRA, "Collection-area polygons; the item title does not match the "
                                          "layer it registers (MapServer layer 7)."),
    "857deac48fe249829472770caa11a510": T("Low", GEO, "Titled DMV but registers a council-district layer "
                                          "(MapServer layer 5)."),
    "bcf1e735b9c54057b6a4f055f0bbf235": T("Low", INFRA, "Portal item for sanitation sections."),
    "gisserver:Sanitation/SANITATION_SECTION_P": T("Low", INFRA, "Sanitation sections."),
    "gisserver:Recycling_Routes": T("Low", INFRA, "Recycling routes."),
    "gisserver:Sanitation/Sanitation_Bulk_Trash_Streets_Coverage": T("Low", INFRA, "Bulk trash street coverage."),
    "gisserver:Glendale_Services/GlendaleGovernmentServices": T("Low", INFRA, "Facility points (DMV, libraries, "
                                                                "stations, hospitals)."),
    "gisserver:Streetlights/Streetlight_Data_For_WebApps": T("Low", INFRA, "Streetlight and pedestrian light "
                                                             "inventory (Street Lighting request group)."),
    "gisserver:Transportation/Completed_Pavement_Activities": T("Low", INFRA, "Completed pavement work by segment."),
    "gisserver:Planning/CIP_PROJECTS_SMARTSHEET_Pv2": T("Low", INFRA, "CIP project polygons (see PORTAL_RECON.md)."),
    "cseam:Planning/CIP_PROJECTS_SMARTSHEET_Pv2": T("Low", INFRA, "cseam copy of the CIP project service."),
    "gisserver:ROW_Maintenance_Contract_Areas": T("Low", INFRA, "Right-of-way maintenance contract areas."),
    "gisserver:Transportation/ROW_MAINT_CONT_AREAS_CONTRACTOR_DOWNLOAD": T("Low", INFRA, "ROW contract areas "
                                                                           "(contractor copy)."),
    "cseam:Parks/CentralSquare_EAM_Production_Parks_FeatureService": T("Low", INFRA, "Parks asset inventory."),
    "8654b72ae84445c8a27d8d4dff9b5bdd": T("Low", INFRA, "Contract spend by department; joins OpenBook by Munis "
                                          "contract [inferred].", date_field="ContractStartDate"),
    "gisserver:OpenData/Glendale_Contract_Spend_Report": T("Low", INFRA, "Enterprise copy of contract spend.",
                                                           layers=[2]),
    "793473d9bbb640ea9f463ce833c8c7a8": T("Low", PROP, "Zoning polygons."),
    "gisserver:Glendale_Services/Glendale_Zoning": T("Low", PROP, "Enterprise zoning polygons."),
    "ea92cbb5af114072ab2a2af63be4ca2e": T("Low", GEO, "City limits (filter for out-of-city points)."),
    "268eb580e2f34995885fa5efe01b2d4c": T("Low", GEO, "Annexation history."),
    "df3321db8b1c495d9dca1144d3fef6d2": T("Low", GEO, "ZIP code polygons."),
    "gisserver:ZIPCODE_P": T("Low", GEO, "ZIP code polygons."),
    "4ed235f9e67e44339897713ad7a0b6a2": T("Low", GEO, "Single Maricopa County polygon (2018)."),
}

# Sources with no ArcGIS REST endpoint. Nothing here is fetched by this script; the numbers
# are carried from PORTAL_RECON.md (browser session) and DATA_DICTIONARY.md (local extract)
# and are therefore tagged [unverified] in the rendered table.
# Cells: dataset, host, access method, row count, date range, Council District, relevance.
NON_REST_ROWS = [
    ["Local extract `data/GlendaleOne_External_Requests.csv`", "local `data/`",
     "CSV pulled 2026-09-05 from AGOL item 37a2cb9c", "107,646 [unverified: DATA_DICTIONARY.md]",
     "`Request_Date` 2019-12-02 → 2026-08-05 [unverified: DATA_DICTIONARY.md]", "Y (`Council_District`)", "High"],
    ["Local extract `data/Code_Compliance_Cases_GlendaleOne.csv`", "local `data/`",
     "CSV pulled 2026-09-05 from AGOL item 8026de93", "56,294 [unverified: DATA_DICTIONARY.md]",
     "`RequestDate` 2019-12-03 → 2026-09-03 [unverified: DATA_DICTIONARY.md]", "N (`District` 100% null)", "High"],
    ["Esri BA `ACS_Population_Summary_<DISTRICT>.xlsx` (×6)", "local `data/` (sponsor email)",
     "Email attachment, formatted report", "373 rows × 6 cols each [unverified: DATA_DICTIONARY.md]",
     "ACS 2020–2024 5-yr [unverified: DATA_DICTIONARY.md]", "Y (one file per district)", "High"],
    ["Esri BA `Demographic_and_Income_Profile_<DISTRICT>.xlsx` (×6)", "local `data/` (sponsor email)",
     "Email attachment, formatted report", "222 rows × 7 cols each [unverified: DATA_DICTIONARY.md]",
     "Census 2020 / Esri 2026 / 2031 [unverified: DATA_DICTIONARY.md]", "Y (one file per district)", "High"],
    ["GlendaleOne Public and Council Report", "Power BI `app.powerbigov.us`",
     "Power BI embed; no API; not opened", "— [unverified]", "— [unverified]", "— [unverified]", "Medium"],
    ["Code Compliance Public Dashboard", "Power BI `app.powerbigov.us`",
     "Power BI embed; no API; not opened", "— [unverified]", "— [unverified]", "— [unverified]", "Medium"],
    ["OpenBook — Operating transaction detail (vendor spend)", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; undocumented JSON API; CSV export link", "562,730 [unverified: PORTAL_RECON.md]",
     "FY20-21 → FY26-27; refresh date 2026-09-16 [unverified: PORTAL_RECON.md]", "N", "Low"],
    ["OpenBook — Detailed Capital Project Spending Report", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; undocumented JSON API; CSV export link", "29,561 [unverified: PORTAL_RECON.md]",
     "Posting 2018-07-18 → 2026-09-14 [unverified: PORTAL_RECON.md]",
     "Derivable (project no. → CIP polygons, spatial) [unverified]", "Low"],
    ["OpenBook — CIP Project Details, 10-Year Funding Plan", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; undocumented JSON API", "2,525 [unverified: PORTAL_RECON.md]",
     "FY20-21 → FY26-27 [unverified: PORTAL_RECON.md]",
     "Derivable (project no. → CIP polygons, spatial) [unverified]", "Low"],
    ["OpenBook — Operating Expenditures (budget hierarchy)", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; budget drill-down API", "— (hierarchy, no grid)", "FY20-21 → FY26-27 [unverified: PORTAL_RECON.md]",
     "N", "Low"],
    ["OpenBook — CIP Expenditures (budget hierarchy)", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; budget drill-down API", "— (hierarchy, no grid)", "FY20-21 → FY26-27 [unverified: PORTAL_RECON.md]",
     "N", "Low"],
    ["OpenBook — Revenue Budget vs Actuals", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; budget API", "~150 funds [unverified: PORTAL_RECON.md]", "FY20-21 → FY26-27 [unverified: PORTAL_RECON.md]",
     "N", "None"],
    ["OpenBook — City Sales Tax / Major Funds Snapshot stories", "OpenBook `glendaleaz.openbook.questica.com`",
     "JS app; story visuals", "— (charts)", "updated 2026-07-07 / 2026-09-14 [unverified: PORTAL_RECON.md]", "N", "None"],
]

THEME_RULES = [
    ("service requests", r"glendaleone|311|service.?request|code.?compl|code.?enforce|escalat|lucity|work.?order|smartgov"),
    ("geography", r"council|district|boundar|city.?limit|neighborhood|census|tract|block.?group|\bblocks?\b|zip|precinct|beat|village|planning.?area"),
    ("demographics", r"popul|demograph|acs\b|income|poverty|housing|density|equity|heat.?relief"),
    ("property", r"parcel|zoning|address|building|footprint|land.?use|general.?plan|permit|licen|rental|historic"),
    ("public safety", r"police|fire|crime|incident|calls?.?for.?service|ems|emergency|hydrant"),
    ("infrastructure", r"street|road|pavement|sidewalk|light|signal|sign|traffic|water|sewer|storm|sanitation|garbage|trash|solid.?waste|recycl|bulk|cip|capital|park|trail|library|facilit|transit|bus|bike|utility"),
]


def infer_theme(rec):
    text = " ".join([rec.get("title", ""), rec.get("name", ""), rec.get("snippet", ""),
                     " ".join(rec.get("tags", []))])
    for theme, pat in THEME_RULES:
        if re.search(pat, text, re.I):
            return theme
    return "other"


# Survey123 services whose names match NOISE_PATTERNS but which are resident request-intake
# channels running parallel to GlendaleOne, so they are probed rather than discarded.
NOT_NOISE = {
    "c297db43ca0244d5b273b9c4f68b9a7c",  # Water Distribution Service Requests
    "fd105ecd5b854227a3e94a62bc5a3363",  # Wastewater Collections Service Request
    "be5da2e2f22b4750ac414253564290de",  # Environmental Resources Service Request
    "c3a919d72e3b4fb5a77d7652767d4eb5",  # GlendaleOne Customer Feedback Survey_fieldworker
    "e51d453394844523b51487b778512b1f",  # Parks and Grounds Request_results
    "4b73972209974186a770aa442731ec2b",  # Code Compliance Assistance Request Survey_form
}


def triage(rec):
    name = rec.get("name") or rec.get("title") or ""
    if rec["key"] in NOT_NOISE and rec["key"] not in TRIAGE:
        return {"tier": "None", "theme": "service requests", "why": "Survey123 intake channel", "noise": False}
    if rec["key"] in TRIAGE:
        cfg = TRIAGE[rec["key"]]
        return {"tier": cfg["tier"], "theme": cfg["theme"], "why": cfg["why"],
                "questions": cfg.get("q", ""), "noise": False}
    for pat, why in NOISE_PATTERNS:
        if pat.search(name) or pat.search(rec.get("title", "")):
            return {"tier": "None", "theme": "noise", "why": why, "noise": True}
    return {"tier": "None", "theme": infer_theme(rec), "why": "not curated", "noise": False}


# --------------------------------------------------------------------------------------
# Probe: service + layer schema + row count (metadata only)
# --------------------------------------------------------------------------------------

MAX_LAYERS_PER_SERVICE = 60
SKIP_LAYER_TYPES = {"Group Layer", "Raster Layer", "Annotation Layer", "Annotation SubLayer",
                    "Mosaic Layer", "Raster Catalog Layer"}


def err_text(d):
    e = d.get("error") if isinstance(d, dict) else None
    return f"{e.get('code')} {e.get('message')}" if isinstance(e, dict) else None


def probe_layer(base, lid):
    lj, lsrc = fetch(f"{base}/{lid}?f=json", allow_error=True)
    if err_text(lj):
        return {"id": lid, "error": err_text(lj), "src": lsrc}
    info = {
        "id": lid, "name": lj.get("name"), "layer_type": lj.get("type"),
        "geometryType": lj.get("geometryType"), "description": lj.get("description") or "",
        "copyrightText": lj.get("copyrightText") or "", "src": lsrc,
        "editingInfo": lj.get("editingInfo"), "maxRecordCount": lj.get("maxRecordCount"),
        "capabilities": lj.get("capabilities"),
        "supportsStatistics": bool((lj.get("advancedQueryCapabilities") or {}).get("supportsStatistics")
                                   or lj.get("supportsStatistics")),
        "fields": [{"name": f["name"], "type": f["type"].replace("esriFieldType", ""),
                    "alias": f.get("alias"), "length": f.get("length"),
                    "domain": (f.get("domain") or {}).get("type"),
                    "domain_values": [c.get("name") for c in (f.get("domain") or {}).get("codedValues", [])][:40],
                    "description": f.get("description")}
                   for f in (lj.get("fields") or [])],
    }
    if info["layer_type"] in SKIP_LAYER_TYPES or not info["fields"]:
        return info
    cnt, csrc = fetch(qurl(f"{base}/{lid}/query", where="1=1", returnCountOnly="true", f="json"),
                      allow_error=True)
    info["count"] = cnt.get("count") if not err_text(cnt) else None
    info["count_error"] = err_text(cnt)
    info["count_src"] = csrc
    return info


LAYER_URL = re.compile(r"^(.*/(?:MapServer|FeatureServer))/(\d+)/?$", re.I)


def probe_service(rec):
    m = LAYER_URL.match(rec["url"])
    if m:  # AGOL item registered against one layer of a (usually Enterprise) service
        base, lid = m.group(1), int(m.group(2))
        layer = probe_layer(base, lid)
        return {"base": base, "layer_item": True, "layers": [layer], "src": layer.get("src"),
                "error": layer.get("error")}
    svc, src = fetch(f"{rec['url']}?f=json", allow_error=True)
    out = {"src": src, "error": err_text(svc), "base": rec["url"]}
    if out["error"]:
        return out
    out["serviceDescription"] = svc.get("serviceDescription") or svc.get("description") or ""
    out["copyrightText"] = svc.get("copyrightText") or ""
    out["editingInfo"] = svc.get("editingInfo")
    sublayers = [(l["id"], l.get("name"), bool(l.get("subLayerIds"))) for l in svc.get("layers", [])]
    tables = [(t["id"], t.get("name"), False) for t in svc.get("tables", [])]
    out["layers"] = []
    for lid, name, is_group in (sublayers + tables)[:MAX_LAYERS_PER_SERVICE]:
        if is_group:
            out["layers"].append({"id": lid, "name": name, "layer_type": "Group Layer"})
            continue
        out["layers"].append(probe_layer(rec["url"], lid))
    out["truncated_layers"] = max(0, len(sublayers) + len(tables) - MAX_LAYERS_PER_SERVICE)
    return out


# --------------------------------------------------------------------------------------
# Deep: statistics for High/Medium layers (outStatistics / returnCountOnly only)
# --------------------------------------------------------------------------------------

NO_STATS_TYPES = {"OID", "Geometry", "Blob", "Raster", "XML", "GlobalID", "GUID"}
DEFAULT_VALUE_FIELDS = re.compile(
    r"status|type|group|categor|depart|council|district|dis_name|hansen|priority|proactive|escalat|level|member",
    re.I)
MAX_GROUPS_KEPT = 40


def epoch_to_date(v):
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    return v


def stats_query(base, lid, stats, **extra):
    def run(b):
        return fetch(qurl(f"{b}/{lid}/query", where="1=1",
                          outStatistics=json.dumps(stats, separators=(",", ":")), f="json", **extra),
                     allow_error=True)
    data, src = run(base)
    # Some Enterprise FeatureServers refuse statistics that their MapServer twin answers.
    if err_text(data) and "gismaps.glendaleaz.com" in base and base.endswith("/FeatureServer"):
        alt, alt_src = run(base[: -len("FeatureServer")] + "MapServer")
        if not err_text(alt):
            return alt, alt_src
    return data, src


def non_null_counts(base, lid, fields):
    """count(field) ignores nulls, so one statistics call per chunk gives non-null counts."""
    out, cols = {}, [f for f in fields if f["type"] not in NO_STATS_TYPES]
    for i in range(0, len(cols), 15):
        chunk = cols[i:i + 15]
        stats = [{"statisticType": "count", "onStatisticField": f["name"], "outStatisticFieldName": f"n{j}"}
                 for j, f in enumerate(chunk)]
        data, src = stats_query(base, lid, stats)
        if not err_text(data) and data.get("features"):
            attrs = data["features"][0]["attributes"]
            for j, f in enumerate(chunk):
                val = attrs.get(f"n{j}", attrs.get(f"N{j}"))
                out[f["name"]] = {"n": val, "src": src}
            continue
        for f in chunk:  # fall back to one field at a time so one bad column doesn't hide the rest
            d1, s1 = stats_query(base, lid, [{"statisticType": "count", "onStatisticField": f["name"],
                                              "outStatisticFieldName": "n0"}])
            if err_text(d1) or not d1.get("features"):
                out[f["name"]] = {"n": None, "error": err_text(d1) or "no features", "src": s1}
            else:
                a = d1["features"][0]["attributes"]
                out[f["name"]] = {"n": a.get("n0", a.get("N0")), "src": s1}
    return out


def blank_counts(base, lid, fields):
    """count(field) treats '' as a value, so count empty strings separately (returnCountOnly)."""
    out = {}
    for f in fields:
        if f["type"] != "String":
            continue
        url = qurl(f"{base}/{lid}/query", where=f"{f['name']} = ''", returnCountOnly="true", f="json")
        data, src = fetch(url, allow_error=True)
        if err_text(data) and "gismaps.glendaleaz.com" in base and base.endswith("/FeatureServer"):
            alt_base = base[: -len("FeatureServer")] + "MapServer"
            data, src = fetch(qurl(f"{alt_base}/{lid}/query", where=f"{f['name']} = ''",
                                   returnCountOnly="true", f="json"), allow_error=True)
        out[f["name"]] = {"n": None if err_text(data) else data.get("count"), "error": err_text(data), "src": src}
    return out


def date_ranges(base, lid, fields):
    out = {}
    for f in fields:
        if f["type"] != "Date":
            continue
        stats = [{"statisticType": "min", "onStatisticField": f["name"], "outStatisticFieldName": "mn"},
                 {"statisticType": "max", "onStatisticField": f["name"], "outStatisticFieldName": "mx"}]
        data, src = stats_query(base, lid, stats)
        if err_text(data) or not data.get("features"):
            out[f["name"]] = {"error": err_text(data) or "no features", "src": src}
            continue
        a = {k.lower(): v for k, v in data["features"][0]["attributes"].items()}
        out[f["name"]] = {"min": epoch_to_date(a.get("mn")), "max": epoch_to_date(a.get("mx")), "src": src}
    return out


def value_counts(base, lid, field, oid_field):
    stats = [{"statisticType": "count", "onStatisticField": oid_field or field, "outStatisticFieldName": "n"}]
    data, src = stats_query(base, lid, stats, groupByFieldsForStatistics=field)
    if err_text(data):
        return {"error": err_text(data), "src": src}
    groups = []
    for feat in data.get("features", []):
        a = feat["attributes"]
        key = next((v for k, v in a.items() if k.lower() == field.lower()), None)
        n = next((v for k, v in a.items() if k.lower() == "n"), None)
        groups.append([key, n])
    groups.sort(key=lambda g: -(g[1] or 0))
    return {"n_groups": len(groups), "top": groups[:MAX_GROUPS_KEPT],
            "truncated": len(groups) > MAX_GROUPS_KEPT, "src": src}


ISO_MAINT = {"001": "continual", "002": "daily", "003": "weekly", "004": "fortnightly", "005": "monthly",
             "006": "quarterly", "007": "biannually", "008": "annually", "009": "as needed",
             "010": "irregular", "011": "not planned", "998": "unknown"}


def parse_metadata_xml(text):
    """Pull publisher-written field definitions and maintenance frequency from item metadata."""
    if not text:
        return {}
    out = {"field_defs": {}}
    for block in re.findall(r"<attr>(.*?)</attr>", text, re.S):
        label = re.search(r"<attrlabl[^>]*>(.*?)</attrlabl>", block, re.S)
        definition = re.search(r"<attrdef[^>]*>(.*?)</attrdef>", block, re.S)
        source = re.search(r"<attrdefs[^>]*>(.*?)</attrdefs>", block, re.S)
        if label and definition and (not source or source.group(1).strip() != "Esri"):
            out["field_defs"][label.group(1).strip()] = re.sub(r"\s+", " ", definition.group(1)).strip()
    m = re.search(r'<MaintFreqCd[^>]*value="(\d+)"', text)
    if m:
        out["maintenance"] = ISO_MAINT.get(m.group(1), m.group(1))
    m = re.search(r"<update[^>]*>(.*?)</update>", text, re.S)
    if m:
        out["fgdc_update"] = m.group(1).strip()
    return out


def sums(base, lid, fields):
    stats = [{"statisticType": "sum", "onStatisticField": f, "outStatisticFieldName": f"s{i}"}
             for i, f in enumerate(fields)]
    data, src = stats_query(base, lid, stats)
    if err_text(data) or not data.get("features"):
        return {"error": err_text(data) or "no features", "src": src}
    a = {k.lower(): v for k, v in data["features"][0]["attributes"].items()}
    out = {f: a.get(f"s{i}") for i, f in enumerate(fields)}
    out["src"] = src
    return out


def deepen_light(rec):
    """Low tier: only the configured date field, so the summary row gets a real date range."""
    cfg = TRIAGE.get(rec["key"], {})
    base = rec.get("probe", {}).get("base") or rec["url"]
    deep = {"layers": {}}
    for layer in primary_layers(rec):
        fields = [f for f in layer["fields"] if f["name"] == cfg.get("date_field")]
        if fields and layer.get("count"):
            deep["layers"][str(layer["id"])] = {"dates": date_ranges(base, layer["id"], fields)}
    return deep


def deepen(rec):
    cfg = TRIAGE.get(rec["key"], {})
    base = rec.get("probe", {}).get("base") or rec["url"]
    deep = {"layers": {}}
    if cfg.get("mirror_of"):
        light = deepen_light(rec)
        for lid, d in light["layers"].items():
            deep["layers"][lid] = d
        return deep
    if rec["item_id"]:
        item, isrc = fetch(AGOL_ITEM.format(id=rec["item_id"]), allow_error=True)
        deep["item"] = {k: item.get(k) for k in ("description", "snippet", "accessInformation",
                                                  "licenseInfo", "modified", "created", "tags", "url")}
        deep["item_src"] = isrc
        xml, xsrc = fetch_xml(f"https://www.arcgis.com/sharing/rest/content/items/{rec['item_id']}"
                              "/info/metadata/metadata.xml")
        deep["metadata"] = parse_metadata_xml(xml)
        deep["metadata_src"] = xsrc
    wanted = cfg.get("layers")
    for layer in rec.get("probe", {}).get("layers", []):
        if "fields" not in layer or not layer["fields"] or layer.get("count") is None:
            continue
        if wanted is not None and layer["id"] not in wanted:
            continue
        lid, fields = layer["id"], layer["fields"]
        d = {}
        if layer.get("supportsStatistics") or rec["source"] == "agol":
            d["non_null"] = non_null_counts(base, lid, fields)
            d["blank"] = blank_counts(base, lid, fields)
            d["dates"] = date_ranges(base, lid, fields)
            oid = next((f["name"] for f in fields if f["type"] == "OID"), None)
            vfields = cfg.get("value_fields")
            if vfields is None:
                vfields = [f["name"] for f in fields
                           if f["type"] in ("String", "SmallInteger", "Integer")
                           and DEFAULT_VALUE_FIELDS.search(f["name"])
                           and (f.get("length") or 0) <= 255]
            d["values"] = {v: value_counts(base, lid, v, oid) for v in vfields
                           if any(f["name"] == v for f in fields)}
            present = [s for s in cfg.get("sum_fields", []) if any(f["name"] == s for f in fields)]
            if present:
                d["sums"] = sums(base, lid, present)
        else:
            d["error"] = "layer does not advertise statistics support"
        if rec["source"] != "agol":
            xml, xsrc = fetch_xml(f"{base}/{lid}/metadata")
            d["metadata"] = parse_metadata_xml(xml)
            d["metadata_src"] = xsrc
        deep["layers"][str(lid)] = d
    return deep


# --------------------------------------------------------------------------------------
# Join checks: evidence for the relationship map (counts and cached value lists only)
# --------------------------------------------------------------------------------------

AGOL_SVC = "https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services"
GIS = "https://gismaps.glendaleaz.com/gisserver/rest/services"
CSEAM = "https://gismaps.glendaleaz.com/cseam/rest/services"
REQ_L = f"{AGOL_SVC}/GlendaleOne_External_Requests/FeatureServer/0"
CODE_L = f"{AGOL_SVC}/GlendaleOne_Code_Compliance_Cases/FeatureServer/0"
ESC_L = f"{AGOL_SVC}/GlendaleOne_Escalations/FeatureServer/1"

# (id, description, layer URL, where clause) -> returnCountOnly
COUNT_CHECKS = [
    ("code_coords_outside", "Code cases with coordinates outside lat 33–34 / lon −113 – −111.5", CODE_L,
     "Latitude < 33 OR Latitude > 34 OR Longitude < -113 OR Longitude > -111.5"),
    ("code_streetnum_blank", "Code cases with no street number (null or empty)", CODE_L,
     "StreetNum IS NULL OR StreetNum = ''"),
    ("req_anon_block_null", "Requests with ANON_BLOCK null", REQ_L, "ANON_BLOCK IS NULL"),
    ("req_full_address_block", "Requests whose FULL_ADDRESS contains ' BLOCK '", REQ_L, "FULL_ADDRESS LIKE '% BLOCK %'"),
    ("parks_g1_linked", "Parks work requests with glendale_one_request populated",
     f"{CSEAM}/Parks/Park_Work_Request_Points/FeatureServer/0",
     "glendale_one_request IS NOT NULL AND glendale_one_request <> ''"),
    ("blocks_geoid15", "Census block points whose GEOID is 15 characters",
     f"{GIS}/PopDensity/Census_Block_2020_pts/FeatureServer/0", "CHAR_LENGTH(GEOID) = 15"),
    ("qct_geoid12", "qct_rates polygons whose GEOID is 12 characters (block group)",
     f"{GIS}/Community_Services/Glendale_qct_rates/MapServer/0", "CHAR_LENGTH(GEOID) = 12"),
    ("childpov_fips11", "Child-poverty polygons whose FIPS is 11 characters (tract)",
     f"{AGOL_SVC}/COG_Child_Poverty_Analysis/FeatureServer/0", "CHAR_LENGTH(FIPS) = 11"),
    ("childpov_fips12", "Child-poverty polygons whose FIPS is 12 characters (block group)",
     f"{AGOL_SVC}/COG_Child_Poverty_Analysis/FeatureServer/0", "CHAR_LENGTH(FIPS) = 12"),
    ("assessor_mail_differs", "Assessor parcels whose MAIL_ADDRESS differs from PHYSICAL_ADDRESS",
     f"{GIS}/ASSESSOR_PARCEL_VIEW/MapServer/0", "MAIL_ADDRESS <> PHYSICAL_ADDRESS"),
    ("ccgrids_cases", "Code Compliance Grids with CASES populated",
     f"{GIS}/Code_Compliance/Code_Compliance_Grids/FeatureServer/2", "CASES IS NOT NULL"),
    ("ccgrids_staff", "Code Compliance Grids with STAFF populated",
     f"{GIS}/Code_Compliance/Code_Compliance_Grids/FeatureServer/2", "STAFF IS NOT NULL AND STAFF <> ''"),
    ("ccgrids_adopted", "Code Compliance Grids with ADOPTED populated",
     f"{GIS}/Code_Compliance/Code_Compliance_Grids/FeatureServer/2", "ADOPTED IS NOT NULL"),
    ("parcels_dis_name_blank", "City parcels with DIS_NAME null or empty",
     f"{GIS}/Parcels/MapServer/6", "DIS_NAME IS NULL OR DIS_NAME = ''"),
]

# (id, description, (layer URL, field), (layer URL, field)) -> compare full grouped value lists
VOCAB_CHECKS = [
    ("group_vocab", "Request_Type_Group vs escalation Request_Group", (REQ_L, "Request_Type_Group"),
     (ESC_L, "Request_Group")),
    ("type_vocab", "Request_Type vs escalation Request_Type_Name", (REQ_L, "Request_Type"),
     (ESC_L, "Request_Type_Name")),
    ("dept_vocab", "Responsible_Department_Name vs escalation Department_Name",
     (REQ_L, "Responsible_Department_Name"), (ESC_L, "Department_Name")),
    ("district_vocab_cfs", "Council_District (requests) vs CouncilDistrict (police calls)",
     (REQ_L, "Council_District"), (f"{AGOL_SVC}/Police_Calls_for_Service/FeatureServer/1", "CouncilDistrict")),
    ("district_vocab_nbhd", "DIS_NAME (hosted districts) vs CouncilDistrict (neighborhoods)",
     (f"{AGOL_SVC}/Glendale_Council_Districts/FeatureServer/0", "DIS_NAME"),
     (f"{GIS}/NEIGHBORHOOD_P_w_MgmtCompany/FeatureServer/0", "CouncilDistrict")),
    ("district_vocab_parcels", "DIS_NAME (hosted districts) vs DIS_NAME (city parcels)",
     (f"{AGOL_SVC}/Glendale_Council_Districts/FeatureServer/0", "DIS_NAME"), (f"{GIS}/Parcels/MapServer/6", "DIS_NAME")),
    ("code_type_vs_esc", "Code case RequestTypeName vs escalation Request_Type_Name", (CODE_L, "RequestTypeName"),
     (ESC_L, "Request_Type_Name")),
    ("code_type_vs_req_type", "Code case RequestTypeName vs request Request_Type", (CODE_L, "RequestTypeName"),
     (REQ_L, "Request_Type")),
    ("grid_vocab", "Code_Compliance_Grids GRID vs Sub Grid GRID",
     (f"{GIS}/Code_Compliance/Code_Compliance_Grids/FeatureServer/2", "GRID"),
     (f"{AGOL_SVC}/Glendale_Code_Compliance_Sub_Grid/FeatureServer/0", "GRID")),
    ("ccdist_vs_grid", "POLICE_GRID CC_DIST vs Code_Compliance_Grids GRID (case-sensitive)",
     (f"{GIS}/POLICE_GRID/MapServer/0", "CC_DIST"), (f"{GIS}/Code_Compliance/Code_Compliance_Grids/FeatureServer/2", "GRID")),
]


def grouped_values(layer, field):
    base, lid = layer.rsplit("/", 1)
    stats = [{"statisticType": "count", "onStatisticField": field, "outStatisticFieldName": "n"}]
    data, src = stats_query(base, lid, stats, groupByFieldsForStatistics=field)
    if err_text(data):
        return None, src, err_text(data)
    vals = {}
    for feat in data.get("features", []):
        a = feat["attributes"]
        key = next((v for k, v in a.items() if k.lower() == field.lower()), None)
        vals[key] = next((v for k, v in a.items() if k.lower() == "n"), None)
    return vals, src, None


def run_join_checks():
    out = {"counts": [], "vocab": []}
    for cid, desc, layer, where in COUNT_CHECKS:
        data, src = fetch(qurl(f"{layer}/query", where=where, returnCountOnly="true", f="json"), allow_error=True)
        out["counts"].append({"id": cid, "desc": desc, "where": where, "count": data.get("count"),
                              "error": err_text(data), "src": src})
    for cid, desc, (la, fa), (lb, fb) in VOCAB_CHECKS:
        a, sa, ea = grouped_values(la, fa)
        b, sb, eb = grouped_values(lb, fb)
        row = {"id": cid, "desc": desc, "src_a": sa, "src_b": sb, "error": ea or eb}
        if a is not None and b is not None:
            ka = {k for k in a if k not in (None, "")}
            kb = {k for k in b if k not in (None, "")}
            row.update({"n_a": len(ka), "n_b": len(kb), "shared": len(ka & kb),
                        "only_a": sorted(map(str, ka - kb))[:25], "only_b": sorted(map(str, kb - ka))[:25],
                        "rows_a_matched": sum(v or 0 for k, v in a.items() if k in kb),
                        "rows_a_total": sum(v or 0 for v in a.values())})
        out["vocab"].append(row)
    return out


def render_join_checks(checks):
    lines = ["| Check | Result | Evidence |", "|---|---|---|"]
    for c in checks["counts"]:
        result = fmt_n(c["count"]) if c["count"] is not None else f"refused ({c['error']})"
        lines.append(f"| {md_escape(c['desc'])} (`{md_escape(c['where'])}`) | {result} | `{c['src']}` |")
    for v in checks["vocab"]:
        if v.get("error") or "shared" not in v:
            lines.append(f"| {md_escape(v['desc'])} | refused ({v.get('error')}) | `{v['src_a']}` |")
            continue
        result = (f"{v['shared']} shared of {v['n_a']} / {v['n_b']} distinct; "
                  f"{fmt_n(v['rows_a_matched'])} of {fmt_n(v['rows_a_total'])} left-side rows match")
        extra = []
        if v["only_a"]:
            extra.append("left only: " + ", ".join(v["only_a"][:8]) + (" …" if len(v["only_a"]) > 8 else ""))
        if v["only_b"]:
            extra.append("right only: " + ", ".join(v["only_b"][:8]) + (" …" if len(v["only_b"]) > 8 else ""))
        if extra:
            result += "; " + "; ".join(md_escape(e) for e in extra)
        lines.append(f"| {md_escape(v['desc'])} | {result} | `{v['src_a']}`, `{v['src_b']}` |")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Render: markdown fragments for DATA_LANDSCAPE.md (sections 1 and 2)
# --------------------------------------------------------------------------------------

TIER_ORDER = {"High": 0, "Medium": 1, "Low": 2, "None": 3}
DISTRICT_FIELD = re.compile(r"^(council|dis_name|cncl_dist)$|council_?dist", re.I)
ADDRESS_FIELD = re.compile(r"address|street_?nam|streetname|full_address|^location$", re.I)

SYSTEM_FIELDS = {
    "OBJECTID": "ArcGIS row id; not stable across reloads",
    "ObjectID": "ArcGIS row id; not stable across reloads",
    "ObjectId": "ArcGIS row id; not stable across reloads",
    "objectid": "ArcGIS row id; not stable across reloads",
    "OBJECTID_1": "Secondary ArcGIS row id left over from a join/export",
    "OBJECTID_12": "ArcGIS row id left over from a join/export",
    "ORIG_FID": "Source feature id from the feature-to-point conversion",
    "ESRI_OID": "ArcGIS row id",
    "FID": "Shapefile row id left over from import",
    "GlobalID": "ArcGIS global unique id",
    "GlobalID_1": "Second GlobalID left over from a join/export",
    "globalid": "ArcGIS global unique id",
    "Shape": "Geometry column",
    "SHAPE": "Geometry column",
    "Shape__Area": "Polygon area in the service's spatial reference units",
    "Shape__Length": "Perimeter/length in the service's spatial reference units",
    "Shape.STArea()": "Polygon area (SQL Server geometry), spatial reference units",
    "Shape.STLength()": "Perimeter/length (SQL Server geometry), spatial reference units",
    "SHAPE.STArea()": "Polygon area (SQL Server geometry), spatial reference units",
    "SHAPE.STLength()": "Perimeter/length (SQL Server geometry), spatial reference units",
    "Shape_Area": "Area carried over from a source shapefile",
    "Shape_Leng": "Length carried over from a source shapefile",
    "created_user": "Editor tracking: account that created the row",
    "created_date": "Editor tracking: row creation timestamp",
    "last_edited_user": "Editor tracking: account that last edited the row",
    "last_edited_date": "Editor tracking: last edit timestamp",
    "CreationDate": "Editor tracking: row creation timestamp",
    "Creator": "Editor tracking: creating account",
    "EditDate": "Editor tracking: last edit timestamp",
    "Editor": "Editor tracking: last editing account",
    "DateLoaded": "ETL timestamp of the nightly load that wrote the row",
}


def fmt_n(n):
    if isinstance(n, float) and n.is_integer():
        n = int(n)
    return f"{n:,}" if isinstance(n, (int, float)) else ("—" if n is None else str(n))


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"&nbsp;|&#160;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    return re.sub(r"\s+", " ", s).strip()


def base_url(rec):
    return rec.get("probe", {}).get("base") or rec["url"]


def data_layers(rec):
    return [l for l in rec.get("probe", {}).get("layers", []) if l.get("fields") and "count" in l]


def primary_layers(rec):
    wanted = TRIAGE.get(rec["key"], {}).get("layers")
    return [l for l in data_layers(rec) if wanted is None or l["id"] in wanted]


def layer_url(rec, layer):
    return f"{base_url(rec)}/{layer['id']}"


def host_label(rec):
    url = rec["url"]
    via = " (via AGOL item)" if rec["source"] == "agol" else ""
    if "services1.arcgis.com" in url:
        return "AGOL hosted `services1.arcgis.com`"
    if "/cseam/" in url:
        return "Enterprise `gismaps…/cseam`" + via
    if "gismaps.glendaleaz.com/gisserver" in url:
        return "Enterprise `gismaps…/gisserver`" + via
    if "gisapps.glendaleaz.com" in url:
        return "Enterprise `gisapps.glendaleaz.com`" + via
    if "utility.arcgis.com" in url:
        return "AGOL proxy `utility.arcgis.com` → Enterprise"
    return f"`{urlparse(url).netloc}`" + via


def service_key(url):
    m = LAYER_URL.match(url)
    base = m.group(1) if m else url
    return re.sub(r"/(MapServer|FeatureServer)/?$", "", base.rstrip("/"), flags=re.I).lower()


def cross_refs(records):
    """Map each Enterprise service to the AGOL items that register one of its layers."""
    refs = {}
    for r in records:
        if r["source"] == "agol" and "gismaps.glendaleaz.com" in r["url"]:
            refs.setdefault(service_key(r["url"]), []).append(r)
    return refs


def last_edit(rec):
    stamps = []
    for l in data_layers(rec):
        ei = l.get("editingInfo") or {}
        v = ei.get("dataLastEditDate") or ei.get("lastEditDate")
        if v:
            stamps.append(v)
    if stamps:
        return f"data last edited {epoch_to_date(max(stamps))}"
    if rec.get("modified"):
        return f"item modified {epoch_to_date(rec['modified'])}"
    return "not published"


def district_status(rec):
    cfg = TRIAGE.get(rec["key"], {})
    if cfg.get("district"):
        return cfg["district"]
    layers = primary_layers(rec)
    if not layers:
        return "—"
    deep = rec.get("deep", {}).get("layers", {})
    for l in layers:
        for f in l["fields"]:
            if DISTRICT_FIELD.search(f["name"]):
                nn = deep.get(str(l["id"]), {}).get("non_null", {}).get(f["name"], {}).get("n")
                where = f" in layer “{md_escape(l['name'])}”" if len(layers) > 1 else ""
                if nn == 0:
                    return f"N (`{f['name']}`{where} 100% null)"
                return f"Y (`{f['name']}`{where})"
    if any(l.get("geometryType") for l in layers):
        return "Derivable (spatial)"
    if any(ADDRESS_FIELD.search(f["name"]) for l in layers for f in l["fields"]):
        return "Derivable (address match)"
    return "N"


def row_count_cell(rec):
    probe = rec.get("probe", {})
    if probe.get("error"):
        return f"— ({md_escape(probe['error'])[:60]})"
    layers = primary_layers(rec)
    if not layers:
        return "— (no queryable layer)"
    if len(layers) == 1:
        l = layers[0]
        return fmt_n(l.get("count")) if l.get("count") is not None else f"— (count refused: {l.get('count_error')})"
    if len(layers) <= 3:
        return "; ".join(f"{md_escape(l['name'])}: {fmt_n(l.get('count'))}" for l in layers)
    total = sum(l.get("count") or 0 for l in layers)
    return f"{len(layers)} layers, {fmt_n(total)} rows total"


def date_cell(rec):
    if TRIAGE.get(rec["key"], {}).get("vintage"):
        return TRIAGE[rec["key"]]["vintage"]
    df = TRIAGE.get(rec["key"], {}).get("date_field")
    if df:
        for d in rec.get("deep", {}).get("layers", {}).values():
            r = d.get("dates", {}).get(df)
            if r and r.get("min"):
                return f"`{df}` {r['min']} → {r['max']}"
    return last_edit(rec)


def access_cell(rec):
    probe = rec.get("probe", {})
    kind = "FeatureServer" if "FeatureServer" in rec["url"] else "MapServer"
    if rec.get("types"):
        kind = "+".join(rec["types"])
    if rec["source"] == "agol":
        where = "on Open Data portal" if rec.get("on_open_data_portal") else "not on portal"
        base = f"REST {kind}, {rec.get('access')}, {where}"
    else:
        base = f"REST {kind}, anonymous"
    if probe.get("error"):
        base += f" — **{md_escape(probe['error'])[:48]}**"
    return base


def name_cell(rec, refs):
    cfg = TRIAGE.get(rec["key"], {})
    name = md_escape(cfg.get("label") or rec["title"])
    if rec["source"] != "agol":
        name += f" (`{rec['name']}`)"
        agol = refs.get(service_key(rec["url"]), [])
        if agol:
            name += " · also AGOL item " + ", ".join(f"`{r['item_id'][:8]}`" for r in agol[:4])
    elif rec.get("probe", {}).get("layer_item"):
        m = LAYER_URL.match(rec["url"])
        target = (rec["probe"].get("layers") or [{}])[0].get("name")
        name += (f" (registers `…/{'/'.join(m.group(1).split('/')[-2:])}/{m.group(2)}`"
                 + (f", layer named “{md_escape(target)}”)" if target else ")"))
    if cfg.get("mirror_of"):
        name += " · mirror"
    return name


def render_summary(records, extra_rows):
    refs = cross_refs(records)
    rows = []
    for rec in records:
        if rec["noise"]:
            continue
        rows.append((TIER_ORDER[rec["tier"]], rec["theme"], (TRIAGE.get(rec["key"], {}).get("label") or rec["title"]).lower(), [
            name_cell(rec, refs), host_label(rec), access_cell(rec), row_count_cell(rec),
            date_cell(rec), district_status(rec), rec["tier"]]))
    for r in extra_rows:
        rows.append((TIER_ORDER[r[-1]], "~", r[0].lower(), r))
    rows.sort(key=lambda x: (x[0], x[1], x[2]))
    out = ["| # | Dataset | Host | Access method | Row count | Date range / vintage | Council District | Relevance |",
           "|---|---|---|---|---|---|---|---|"]
    for i, (_, _, _, cells) in enumerate(rows, 1):
        out.append(f"| {i} | " + " | ".join(cells) + " |")
    return "\n".join(out), len(rows)


def render_noise(records):
    groups = {}
    for r in records:
        if r["noise"]:
            groups.setdefault((r["source"], r["why"]), []).append(r)
    lines = []
    for (source, why), recs in sorted(groups.items()):
        names = ", ".join(f"{md_escape(r['title'])}" for r in sorted(recs, key=lambda r: r["title"].lower()))
        lines.append(f"- **{source} — {why} ({len(recs)}):** {names}")
    return "\n".join(lines)


def portal_field_description(field, deep_layer, deep):
    portal = field.get("description")
    if isinstance(portal, str) and portal.strip().startswith("{"):
        try:
            portal = json.loads(portal).get("value")
        except ValueError:
            pass
    return portal or deep_layer.get("metadata", {}).get("field_defs", {}).get(field["name"]) \
        or deep.get("metadata", {}).get("field_defs", {}).get(field["name"])


def field_description(field, notes, deep_layer, deep):
    portal = portal_field_description(field, deep_layer, deep)
    if portal:
        return md_escape(strip_html(portal))
    text = notes.get(field["name"]) or SYSTEM_FIELDS.get(field["name"])
    return md_escape(text) + " [inferred]" if text else ""


def field_quirks(field, count, deep_layer, notes):
    bits = []
    nn = deep_layer.get("non_null", {}).get(field["name"], {})
    blank = deep_layer.get("blank", {}).get(field["name"], {}).get("n") or 0
    if count and nn.get("n") is not None:
        nulls, filled = count - nn["n"], nn["n"] - blank
        if nn["n"] == 0:
            bits.append("**100% null**")
        elif filled == 0:
            bits.append(f"**0% populated** ({fmt_n(nulls)} null, {fmt_n(blank)} empty string)")
        elif filled < count:
            detail = f"{fmt_n(nulls)} null" + (f", {fmt_n(blank)} empty string" if blank else "")
            bits.append(f"{100 * filled / count:.1f}% populated ({detail})")
    elif nn.get("error"):
        bits.append(f"non-null count refused ({nn['error']})")
    dr = deep_layer.get("dates", {}).get(field["name"])
    if dr and dr.get("min"):
        bits.append(f"{dr['min']} → {dr['max']}")
    vc = deep_layer.get("values", {}).get(field["name"])
    if vc and "top" in vc:
        shown = vc["top"][:8]
        top = ", ".join(f"{'NULL' if k is None else ('(empty string)' if k == '' else k)} {fmt_n(n)}"
                        for k, n in shown)
        if vc["n_groups"] <= 8:
            bits.append(f"{vc['n_groups']} values: {md_escape(top)}")
        else:
            bits.append(f"{vc['n_groups']} distinct; top: {md_escape(top)} …")
    sm = deep_layer.get("sums", {})
    if field["name"] in sm and sm[field["name"]] is not None:
        bits.append(f"sum = {fmt_n(sm[field['name']])}")
    dv = field.get("domain_values") or []
    if dv:
        bits.append("coded domain: " + (md_escape(", ".join(dv)) if len(dv) <= 12 else f"{len(dv)}+ coded values"))
    q = notes.get(f"{field['name']}#quirk")
    if q:
        bits.append(md_escape(q))
    return "; ".join(bits)


def grouped_fields(fields, groups):
    """Collapse runs of fields matching a configured regex into one row each."""
    rows, used = [], set()
    for pattern, label in groups:
        rx = re.compile(pattern)
        members = [f for f in fields if rx.search(f["name"])]
        if members:
            used.update(f["name"] for f in members)
            rows.append(("group", members, label))
    singles = [("field", f, None) for f in fields if f["name"] not in used]
    # keep original field order: place each group where its first member appeared
    order = {f["name"]: i for i, f in enumerate(fields)}
    items = singles + rows
    items.sort(key=lambda it: order[it[1]["name"]] if it[0] == "field" else order[it[1][0]["name"]])
    return items


def render_layer_table(rec, layer, notes, deep, cfg):
    dl = deep.get("layers", {}).get(str(layer["id"]), {})
    count = layer.get("count")
    lines = ["| Field | Type | Alias | Description | Nulls / range / values |", "|---|---|---|---|---|"]
    documented = 0
    for kind, obj, label in grouped_fields(layer["fields"], cfg.get("field_groups", [])):
        if kind == "group":
            members = obj
            types = sorted({f["type"] for f in members})
            nn = [dl.get("non_null", {}).get(f["name"], {}).get("n") for f in members]
            nn = [n for n in nn if n is not None]
            null_note = ""
            if count and nn:
                null_note = "all 100% non-null" if min(nn) == count else f"min non-null {100 * min(nn) / count:.1f}%"
            first_alias = members[0].get("alias") or ""
            lines.append(f"| `{members[0]['name']}` … `{members[-1]['name']}` ({len(members)} fields) | "
                         f"{'/'.join(types)} | e.g. {md_escape(first_alias)} | {md_escape(label)} [inferred] | {null_note} |")
            documented += len(members)
            continue
        f = obj
        alias = f.get("alias") if f.get("alias") and f.get("alias") != f["name"] else ""
        lines.append(f"| `{f['name']}` | {f['type']} | {md_escape(alias)} | {field_description(f, notes, dl, deep)} | "
                     f"{field_quirks(f, count, dl, notes)} |")
        documented += 1
    srcs = sorted({v["src"] for k in ("non_null", "dates", "values") for v in dl.get(k, {}).values()
                   if isinstance(v, dict) and v.get("src")} | ({dl["sums"]["src"]} if dl.get("sums", {}).get("src") else set()))
    if srcs:
        lines.append("")
        lines.append(f"<sub>Nulls/ranges/values from {len(srcs)} cached statistics responses "
                     f"(e.g. `{srcs[0]}`); schema `{layer.get('src')}`.</sub>")
    return lines, documented


def render_detail(rec, field_notes, n, by_key):
    cfg = TRIAGE[rec["key"]]
    deep = rec.get("deep", {})
    notes = field_notes.get(rec["key"], {})
    title = cfg.get("label") or rec["title"]
    lines = [f"### 2.{n} {md_escape(title)} — {rec['tier']}", ""]
    if rec["item_id"]:
        lines.append(f"- **Item:** `{rec['item_id']}` (https://www.arcgis.com/home/item.html?id={rec['item_id']}), "
                     f"on Open Data portal: {'yes' if rec.get('on_open_data_portal') else 'no'}")
    lines.append(f"- **Host / access:** {host_label(rec)}; {access_cell(rec)}")
    lines.append(f"- **Relevance:** {rec['tier']} ({cfg.get('q', '')}). {cfg['why']}")
    lines.append(f"- **Council District:** {district_status(rec)}")
    if cfg.get("notes"):
        lines.append(f"- **Notes:** {cfg['notes']}")
    documented = 0
    mirror = by_key.get(cfg.get("mirror_of"))
    if mirror:
        lines.append(f"- **Mirror of:** {md_escape(TRIAGE[mirror['key']].get('label') or mirror['title'])} "
                     f"(`{mirror['key']}`); the full field list is documented there.")
        mine, theirs = primary_layers(rec), primary_layers(mirror)
        for layer in mine:
            other = theirs[0] if theirs else None
            a = {f["name"] for f in layer["fields"]}
            b = {f["name"] for f in (other["fields"] if other else [])}
            lines.append("")
            lines.append(f"**Layer {layer['id']} `{layer['name']}`** · rows: {fmt_n(layer.get('count'))} "
                         f"(`{layer.get('count_src')}`) vs {fmt_n(other.get('count') if other else None)} in the primary · "
                         f"{date_cell(rec)}")
            lines.append("")
            lines.append(f"Access URL: `{layer_url(rec, layer)}`")
            lines.append("")
            lines.append(f"Fields only here: {', '.join(f'`{x}`' for x in sorted(a - b)) or 'none'} · "
                         f"fields only in primary: {', '.join(f'`{x}`' for x in sorted(b - a)) or 'none'}")
            documented += len(a)
        lines.append("")
        return "\n".join(lines), documented
    maint = deep.get("metadata", {}).get("maintenance")
    edit = last_edit(rec)
    lines.append("- **Update frequency:** " + (f"published as '{maint}'" if maint else
                 "not published in item metadata [unverified]") + (f"; {edit}" if edit != "not published" else ""))
    item = deep.get("item") or {}
    desc = strip_html(item.get("description") or rec.get("probe", {}).get("serviceDescription") or "")
    lines.append(f"- **Portal description:** " + (f"\"{md_escape(desc[:500])}{'…' if len(desc) > 500 else ''}\""
                                                   if desc else "none published"))
    lines.append("")
    for layer in primary_layers(rec):
        geom = (layer.get("geometryType") or "table").replace("esriGeometry", "").lower()
        lines.append(f"**Layer {layer['id']} `{layer['name']}`** · {geom} · rows: {fmt_n(layer.get('count'))} "
                     f"(`{layer.get('count_src')}`)")
        lines.append("")
        lines.append(f"Access URL: `{layer_url(rec, layer)}`")
        lines.append("")
        sm = deep.get("layers", {}).get(str(layer["id"]), {}).get("sums") or {}
        if sm and not sm.get("error"):
            lines.append("Sums across all rows: " + "; ".join(f"`{k}` = {fmt_n(v)}" for k, v in sm.items() if k != "src")
                         + f" (`{sm['src']}`)")
            lines.append("")
        table, m = render_layer_table(rec, layer, notes, deep, cfg)
        lines.extend(table)
        documented += m
        lines.append("")
    return "\n".join(lines), documented


def missing_field_notes(records, field_notes):
    missing = []
    for rec in records:
        cfg = TRIAGE.get(rec["key"], {})
        if rec.get("tier") not in ("High", "Medium") or cfg.get("mirror_of"):
            continue
        notes = field_notes.get(rec["key"], {})
        deep = rec.get("deep", {})
        for layer in primary_layers(rec):
            dl = deep.get("layers", {}).get(str(layer["id"]), {})
            grouped = set()
            for pattern, _ in cfg.get("field_groups", []):
                grouped.update(f["name"] for f in layer["fields"] if re.search(pattern, f["name"]))
            for f in layer["fields"]:
                if f["name"] not in grouped and not field_description(f, notes, dl, deep):
                    missing.append((rec["key"], layer["id"], f["name"], f.get("alias") or ""))
    return missing


def write_index():
    seen = {}
    if FETCH_LOG.exists():
        for line in FETCH_LOG.read_text().splitlines():
            e = json.loads(line)
            seen.setdefault(e["file"], e)
    with (CACHE / "index.tsv").open("w") as out:
        out.write("file\turl\thttp\tbytes\tfetched_at\n")
        for f, e in sorted(seen.items()):
            out.write(f"{f}\t{e['url']}\t{e['http']}\t{e['bytes']}\t{e['fetched_at']}\n")
    return len(seen)


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def progress(ok, source, detail):
    print(f"{'✅' if ok else '⚠️'} {source} — {detail}", flush=True)


def main():
    global OFFLINE, REFRESH
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog-only", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    OFFLINE, REFRESH = args.offline, args.refresh
    RAW.mkdir(parents=True, exist_ok=True)

    records, prov = [], {}
    for label, fn in [("agol", catalog_agol), ("hub", catalog_hub),
                      ("gisserver", lambda: catalog_enterprise("gisserver", ENTERPRISE_ROOTS["gisserver"])),
                      ("cseam", lambda: catalog_enterprise("cseam", ENTERPRISE_ROOTS["cseam"]))]:
        try:
            result, p = fn()
            prov[label] = p
            if label == "hub":
                hub = result
                print(f"  hub: dataset collection {hub['dataset']['numberMatched']}, all {hub['all']['numberMatched']}")
            else:
                records.extend(result)
                print(f"  {label}: {len(result)} services enumerated")
        except Exception as e:  # noqa: BLE001 -- a blocked source must not stop the others
            prov[label] = {"blocked": str(e)}
            progress(False, label, f"blocked: {e}")

    hub_ids = set(hub["all"]["items"]) if "hub" in locals() else set()
    for rec in records:
        rec.update(triage(rec))
        rec["on_open_data_portal"] = (rec["item_id"] in hub_ids) if rec["item_id"] else False

    (CACHE / "catalog.json").write_text(json.dumps(
        {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "provenance": prov, "hub": hub if "hub" in locals() else None,
         "records": records}, indent=1))
    if args.catalog_only:
        return

    targets = [r for r in records if not r["noise"]]
    print(f"  probing {len(targets)} non-noise services (schema + row count)")
    for i, rec in enumerate(targets, 1):
        try:
            rec["probe"] = probe_service(rec)
        except BulkFetchRefused:
            raise
        except Exception as e:  # noqa: BLE001 -- record and move on; one bad service is not a blocked source
            rec["probe"] = {"error": f"{type(e).__name__}: {e}"}
        if i % 25 == 0:
            print(f"    {i}/{len(targets)}", flush=True)

    unknown = [k for k in TRIAGE if k not in {r["key"] for r in records}]
    if unknown:
        print(f"  note: {len(unknown)} TRIAGE keys not found in this catalog: {unknown}", file=sys.stderr)
    tiered = sorted((r for r in targets if r["tier"] in ("High", "Medium")),
                    key=lambda r: (TIER_ORDER[r["tier"]], list(TRIAGE).index(r["key"])))
    print(f"  deep statistics for {len(tiered)} High/Medium datasets")
    for rec in tiered:
        try:
            rec["deep"] = deepen(rec)
        except BulkFetchRefused:
            raise
        except Exception as e:  # noqa: BLE001
            rec["deep"] = {"error": f"{type(e).__name__}: {e}"}
            print(f"    deep failed for {rec['key']}: {e}", file=sys.stderr)
    for rec in targets:
        if rec["tier"] in ("Low", "None") and TRIAGE.get(rec["key"], {}).get("date_field"):
            try:
                rec["deep"] = deepen_light(rec)
            except BulkFetchRefused:
                raise
            except Exception as e:  # noqa: BLE001
                rec["deep"] = {"error": f"{type(e).__name__}: {e}"}

    print("  join checks")
    checks = run_join_checks()
    (CACHE / "join_checks.json").write_text(json.dumps(checks, indent=1))

    notes_path = HERE / "field_notes.json"
    field_notes = json.loads(notes_path.read_text()) if notes_path.exists() else {}
    by_key = {r["key"]: r for r in records}
    details, documented = [], {}
    for n, rec in enumerate(tiered, 1):
        text, m = render_detail(rec, field_notes, n, by_key)
        details.append(text)
        documented[rec["source"]] = documented.get(rec["source"], 0) + m
    summary, n_rows = render_summary(records, NON_REST_ROWS)
    secured = [f"`{label}/{folder}`" for label in ("gisserver", "cseam")
               for folder, v in prov.get(label, {}).get("folders", {}).items() if "error" in v]
    (CACHE / "landscape_fragments.md").write_text(
        "<!-- generated by src/harvest_metadata.py; do not hand-edit -->\n\n"
        f"## Section 1 table ({n_rows} rows)\n\n" + summary +
        "\n\n## Excluded as noise\n\n" + render_noise(records) +
        "\n\n## Token-secured Enterprise folders\n\n" + ", ".join(secured) +
        "\n\n## Join checks\n\n" + render_join_checks(checks) +
        "\n\n## Section 2 details\n\n" + "\n".join(details))
    missing = missing_field_notes(tiered, field_notes)
    with (CACHE / "missing_field_notes.tsv").open("w") as fh:
        fh.write("key\tlayer\tfield\talias\n")
        for row in missing:
            fh.write("\t".join(str(x) for x in row) + "\n")
    (CACHE / "harvest.json").write_text(json.dumps(
        {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "provenance": prov, "records": targets,
         "noise": [{k: r.get(k) for k in ("source", "key", "title", "name", "why")}
                   for r in records if r["noise"]]}, indent=1))
    n_files = write_index()

    print(f"  {len(missing)} High/Medium fields still lack a description; {n_files} cached responses indexed")
    names = {"agol": "ArcGIS Online org 9fVTQQSiODPjLUTa", "hub": "Open Data Hub opendata.glendaleaz.com",
             "gisserver": "Enterprise gismaps.glendaleaz.com/gisserver",
             "cseam": "Enterprise gismaps.glendaleaz.com/cseam"}
    for label in ("agol", "hub", "gisserver", "cseam"):
        p = prov.get(label, {})
        if "blocked" in p:
            progress(False, names[label], f"blocked: {p['blocked']}")
            continue
        if label == "hub":
            progress(True, names[label], f"{hub['all']['numberMatched']} datasets cataloged, "
                                         "0 fields documented (cross-reference only)")
            continue
        recs = [r for r in records if r["source"] == label]
        locked = [f for f, v in p.get("folders", {}).items() if "error" in v]
        extra = f"; {len(locked)} folders token-secured" if locked else ""
        progress(True, names[label], f"{len(recs)} datasets cataloged, "
                                     f"{documented.get(label, 0)} fields documented{extra}")


if __name__ == "__main__":
    main()
