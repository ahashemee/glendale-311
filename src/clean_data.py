"""One-time cleanup of the CIS 450 Glendale raw data -> data/cleaned/.
Run from anywhere: python src/clean_data.py
Reads data/demographics/*.xlsx and data/raw/GlendaleOne_External_Requests.csv,
writes only to data/cleaned/ (paths resolve from the repo root, whatever the cwd).
"""
import glob, hashlib, os, re, difflib, warnings
import pandas as pd, numpy as np, openpyxl
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
DEMO = os.path.join(ROOT, "data", "demographics")  # 12 Esri workbooks
RAW = os.path.join(ROOT, "data", "raw")            # request CSV from src/fetch_data.py
OUT = os.path.join(ROOT, "data", "cleaned")
os.makedirs(OUT, exist_ok=True)
REQ_FILE = "GlendaleOne_External_Requests.csv"
RUN_DATE = pd.Timestamp("2026-09-24")
L = []  # log lines
def log(*a): L.append(" ".join(str(x) for x in a))
def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
raw_files = sorted(glob.glob(os.path.join(DEMO, "*.xlsx"))) + [os.path.join(RAW, REQ_FILE)]
md5_before = {os.path.basename(p): md5(p) for p in raw_files}

def slug(s):
    s = str(s).strip().rstrip(":").lower()
    s = s.replace("$", "").replace(",", "").replace("&", " and ").replace("%", " pct ")
    s = s.replace("<", "lt ").replace("+", "plus")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")

PLACEHOLDERS = {"", "n", "(x)", "-", "**", "***", "n/a", "na"}
placeholder_hits = {}
def to_num(v, pct=False, tag=""):
    if v is None: return np.nan
    if isinstance(v, (int, float)): return round(v * 100, 6) if pct else v
    s = str(v).strip()
    if s.lower() in PLACEHOLDERS:
        placeholder_hits[tag] = placeholder_hits.get(tag, 0) + 1
        return np.nan
    is_pct_str = s.endswith("%")
    s = re.sub(r"(\+/-|±|[$,%*†‡]|\(\w\))", "", s).strip()
    x = float(s)
    return x if is_pct_str else (round(x * 100, 6) if pct else x)

colmap = []  # (file_type, clean_name, original)

# ---------------------------------------------------------------- ACS Population Summary
ACS_SECTIONS = {
    "Totals": "", "Household Size and Type": "hh_size_type",
    "Household Type by Relatives and Non-relatives": "hh_rel_type",
    "Households by Disability Status": "hh_disability",
    "Population Age 3+ by School Enrollment": "school_enroll_3plus",
    "Households by Presence of People Under 18 by Household Type": "hh_under18",
    "Households by Poverty Status": "hh_poverty",
    "Households by Public Assistance and Other Income": "hh_income_src",
    "Population by Ratio of Income to Poverty": "pop_poverty_ratio",
    "Households by Type and Size": "hh_type_size",
    "Population Age 5 to 17 by Language Spoken": "lang_5_17",
    "Population Age 18 to 64 by Language Spoken": "lang_18_64",
    "Population Age 65+ by Language Spoken": "lang_65plus",
    "Workers Age 16+ By Means of Transportation": "commute_mode",
    "Workers Age 16+ By Travel Time to Work": "commute_time",
    "Workers Age16+ by Place of Work": "work_place",
    "Sex by Class of Worker": "class_of_worker",
    "Gross Rent as a Percentage of Household Income": "rent_burden",
    "Females Age 20-64 by Age of Children": "women_20_64_children",
    "Population and Presence of a Computer": "computer",
    "Households and Internet Subscriptions": "internet",
    "Health Insurance Coverage by Age": "health_ins",
    "Civilian Population Age18+ by Vetran Status": "veteran",
}

def parse_acs(path):
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    district = str(ws["A4"].value).strip()
    rec, section, stack, reliab = {}, None, [], 0
    for r in ws.iter_rows(min_row=5):
        a = r[0]; label = a.value
        if label is None: continue
        label = str(label).strip()
        if label.startswith("Source:"): continue
        b, c, d, e = (x.value for x in r[1:5])
        if a.font.b or b == "ACS Estimate":
            section = label; stack = []; continue
        if e not in (None, ""): reliab += 1
        ind = int(a.alignment.indent or 0)
        while stack and stack[-1][0] >= ind: stack.pop()
        parents = [s for _, s, _l in stack if s != "total"]
        name = "_".join(x for x in ["acs", ACS_SECTIONS[section], *parents, slug(label)] if x)
        orig = f"{section} > " + " > ".join([lab for *_, lab in stack] + [label])
        stack.append((ind, slug(label), label))
        for suffix, val, pct, meas in [("", b, False, "ACS Estimate"), ("_pct", c, True, "Percent"), ("_moe", d, False, "MOE (±)")]:
            col = name + suffix
            if col in rec: raise ValueError(f"duplicate ACS column {col} in {path}")
            rec[col] = to_num(val, pct, tag=f"acs:{meas}")
            colmap.append(("ACS Population Summary", col, f"{orig} [{meas}]"))
    return district, rec, reliab

# ---------------------------------------------------------------- Demographic and Income Profile
DIP_SECTIONS = {"Summary": "summary", "Trends 2026 - 2031": "trend", "Population by Age": "age",
                "Households by Income": "hhinc", "Race and Ethnicity": "race"}
VINT = {"Census 2020": "2020", "2026": "2026", "2031": "2031"}
INFO_KEEP = {"2026 Total Daytime Population": "dip_total_daytime_population_2026",
             "2026 Diversity Index": "dip_diversity_index_2026", "2026 Median Net Worth": "dip_median_net_worth_2026",
             "2026 Wealth Index": "dip_wealth_index_2026", "2026 Housing Affordability Index": "dip_housing_affordability_index_2026"}

def parse_dip(path):
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    district = str(ws["A4"].value).strip()
    rows = [[c.value for c in r] + [r[0].font.b] for r in ws.iter_rows(min_row=5)]
    rec, info, section, colspec, in_info = {}, [], None, None, False
    for i, r in enumerate(rows):
        label = r[0]
        if label is None: continue
        label = str(label).strip()
        if label == "Infographic" or in_info:
            in_info = True
            if label in ("Infographic", "Variable") or label.startswith("Source:") or r[1] is None: continue
            info.append((label, r[1])); continue
        if r[-1]:  # bold section header
            section = DIP_SECTIONS[label]; hdr = r[1:7]
            if section in ("summary", "trend"):
                colspec = [(j, (VINT.get(str(h), None) if section == "summary" else "rate_" + slug(h)), False) for j, h in enumerate(hdr) if h]
            else:  # number/percent pairs under a vintage header
                # vintage label sits over either the Number or the Percent cell of its pair
                colspec, sub = [], rows[i + 1][1:7]
                for j in range(len(hdr) - 1):
                    if sub[j] == "Number" and sub[j + 1] == "Percent":
                        v = VINT[str(hdr[j] if hdr[j] is not None else hdr[j + 1])]
                        colspec += [(j, v, False), (j + 1, v + "_pct", True)]
            continue
        if label == "" or all(x is None for x in r[1:7]): continue
        lab = re.sub(r"^Age ", "", label)
        for j, suffix, pct in colspec:
            col = f"dip_{section}_{slug(lab)}_{suffix}"
            val = to_num(r[1 + j], pct=pct or section == "trend", tag=f"dip:{section}")
            if col in rec: raise ValueError(f"duplicate DIP column {col}")
            rec[col] = val
            colmap.append(("Demographic and Income Profile", col, f"{[k for k,v in DIP_SECTIONS.items() if v==section][0]} > {label} [{suffix}]"))
    for lab, val in info:
        if lab in INFO_KEEP:
            rec[INFO_KEEP[lab]] = to_num(val)
    return district, rec, info

def check_infographic(rec, info):
    """Infographic rows other than INFO_KEEP restate the main tables; count values that do not match."""
    vals = [(l, float(v)) for l, v in info if l not in INFO_KEEP]
    main = []
    main += [rec["dip_summary_total_population_2026"], rec["dip_summary_total_households_2026"],
             rec["dip_summary_average_household_size_2026"], rec["dip_summary_median_age_2026"]]
    main += [rec[f"dip_trend_{k}_rate_area"] for k in ["population", "households", "family_population", "owner_occupied_housing_units", "median_household_income"]]
    main += [rec[f"dip_trend_{k}_rate_state"] for k in ["population", "households", "family_population", "owner_occupied_housing_units", "median_household_income"]]
    main += [rec[f"dip_trend_{k}_rate_national"] for k in ["population", "households", "family_population", "owner_occupied_housing_units", "median_household_income"]]
    main += [rec[c] for v in ("2026", "2031") for c in rec if c.startswith("dip_age_") and c.endswith(f"_{v}_pct")]
    main += [rec["dip_hhinc_median_household_income_2026"]]
    main += [rec[c] for c in rec if c.startswith("dip_hhinc_") and c.endswith("_2026_pct") and not re.search(r"(median|average|per_capita)", c)]
    main += [rec[c] for v in ("2026", "2031") for c in rec if c.startswith("dip_race_") and c.endswith(f"_{v}_pct") and "hispanic" not in c]
    # infographic order: totals(4) ,trends(15), age(36), median hh income(1), income(20), race(14)
    order = [l for l, _ in vals]
    if len(main) != len(vals): return len(vals), len(main), None
    mism = [(order[k], vals[k][1], main[k]) for k in range(len(vals)) if abs(vals[k][1] - main[k]) > 0.011 * max(1, abs(main[k]) / 100)]
    return len(vals), len(main), mism

# ---------------------------------------------------------------- run ACS
log("# Cleaning log – CIS 450 Glendale data\n")
log(f"Generated by `data/cleaned/clean_data.py` on {RUN_DATE.date()}. Raw files read from `data/`; outputs written only to `data/cleaned/`.\n")
log("## 0. Inputs found vs. brief\n")
log("- The brief expected 12 ACS CSVs plus 1 glendaleOne CSV. `data/` actually holds **12 Esri .xlsx workbooks** (2 report types × 6 districts, one district per file), 2 GlendaleOne CSVs and 1 GeoJSON.")
log("- Agreed with Ma'el before building: stack the 6 district workbooks of each report type into **2 cleaned topic files** (6 rows each), and clean **only `GlendaleOne_External_Requests.csv`** as `glendaleone_clean.csv`.")
log("- Not processed: `Code_Compliance_Cases_GlendaleOne.csv` (its `District` column is 100% empty per DATA_DICTIONARY.md, so it cannot join without spatial work, which is out of scope), `council_districts.geojson` (spatial, out of scope).")
log("- Read first (not edited): `DATA_DICTIONARY.md`, `PROJECT.md`.\n")

acs_rows, dip_rows, file_log = [], [], []
acs_files = sorted(glob.glob(os.path.join(DEMO, "ACS_Population_Summary_*.xlsx")))
dip_files = sorted(glob.glob(os.path.join(DEMO, "Demographic_and_Income_Profile_*.xlsx")))
info_checks = []
for p in acs_files:
    dist, rec, reliab = parse_acs(p)
    fn_dist = re.search(r"_([A-Z]+)\.xlsx$", p).group(1)
    assert dist == fn_dist, (p, dist)
    raw_rows = pd.read_excel(p, header=None).shape[0]
    acs_rows.append({"district": dist, **rec})
    file_log.append((os.path.basename(p), "ACS Population Summary", "ACS 2020–2024 5-year estimates (Esri)", "Council district (one district per file)", dist, raw_rows, len(rec), reliab))
for p in dip_files:
    dist, rec, info = parse_dip(p)
    fn_dist = re.search(r"_([A-Z]+)\.xlsx$", p).group(1)
    assert dist == fn_dist, (p, dist)
    raw_rows = pd.read_excel(p, header=None).shape[0]
    info_checks.append((dist, *check_infographic(rec, info)))
    dip_rows.append({"district": dist, **rec})
    file_log.append((os.path.basename(p), "Demographic and Income Profile", "Census 2020 + Esri 2026 estimate + Esri 2031 projection", "Council district (one district per file)", dist, raw_rows, len(rec), 0))

def build(rows, label):
    cols = [list(r.keys()) for r in rows]
    assert all(c == cols[0] for c in cols), f"{label}: variable sets differ between districts"
    df = pd.DataFrame(rows)
    df["district"] = df["district"].str.strip()
    empty = [c for c in df.columns if c != "district" and df[c].isna().all()]
    df = df.drop(columns=empty)
    return df, empty

acs_df, acs_empty = build(acs_rows, "ACS")
dip_df, dip_empty = build(dip_rows, "DIP")
colmap = [m for m in colmap if m[1] not in acs_empty + dip_empty]
colmap = list(dict.fromkeys(colmap))

log("## 1. Demographic files (ACS / Esri)\n")
log("### 1.1 File identification\n")
log("| Raw file | Report | Vintage | Geography | District | Raw sheet rows | Values parsed | Reliability cells filled |")
log("|---|---|---|---|---|---|---|---|")
for f in file_log: log("| " + " | ".join(str(x) for x in f) + " |")
log("\nAll 12 files are at council-district level; none was flagged. Each workbook is a formatted report for one district, so there is **no citywide/total row to exclude** (the brief's step 5 does not apply). Section `Total` rows inside a report are universes for that district, not citywide totals, and were kept as variables.\n")
log("### 1.2 Reshape and conversion rules\n")
log("- Each report was parsed by section header (bold cell or `ACS Estimate` header) and by the cell indent level in column A, which encodes the label hierarchy. Variable name = `acs_` or `dip_` + section abbreviation + parent labels + label, in snake_case. Parent `Total` rows are left out of child names.")
log("- ACS Population Summary: one column per estimate, plus `_pct` (Percent) and `_moe` (MOE ±) columns. The `Reliability` column is empty in all 6 files and was not carried over.")
log("- Demographic and Income Profile: vintage suffix `_2020` = Census 2020 actual, `_2026` = Esri 2026 estimate, `_2031` = Esri 2031 projection; `_pct` = share. Trend rows are annual growth rates, named `dip_trend_<var>_rate_<area|state|national>`, in percent per year. There is no MOE in this report.")
log("- **All percentages and rates are on a 0-100 scale** (Excel stores them as fractions, e.g. 0.292 → 29.2; the `100.0%` text cells → 100).")
log("- Strings were stripped of commas, $, %, +/-, ± and footnote markers; placeholders (N, (X), -, **, blank) became empty cells. Placeholders hit: " + (", ".join(f"{k}: {v}" for k, v in placeholder_hits.items()) or "none") + " (the `-` cells are the Percent column of Median/Average/Per Capita Income).")
log(f"- Columns dropped because they were empty for all 6 districts: ACS {acs_empty}; DIP {dip_empty}. `Average Travel Time to Work` has no value in any file; `Population 65+ in Households` has no estimate (its pct/MOE are also blank).")
log("- Infographic block (DIP rows 84-219): kept only the 5 variables that exist nowhere else (" + ", ".join(INFO_KEEP.values()) + "). The rest restate the main tables and were dropped after checking they match:")
for dist, n_info, n_main, mism in info_checks:
    log(f"  - {dist}: {n_info} restated values, {n_main} main-table values compared, mismatches: {'n/a (count differs)' if mism is None else len(mism)}" + ("" if not mism else " " + str(mism[:5])))
log("  - Note: the infographic labels the first five trend rows `Trends: 2022 - 2027` and the last five `2026-2031`, but their values equal the Area and National 2026-2031 rates. Mislabel in the Esri export; no effect since the block is dropped.\n")
log("### 1.3 Output files\n")
for name, df, n_in in [("acs_population_summary_clean.csv", acs_df, len(acs_files)), ("acs_demo_income_profile_clean.csv", dip_df, len(dip_files))]:
    num = df.drop(columns="district").apply(lambda s: pd.api.types.is_numeric_dtype(s)).all()
    log(f"- `{name}`: {n_in} input files → {df.shape[0]} rows × {df.shape[1]} columns ({df.shape[1]-1} variables). All variable columns numeric: {num}. Unique districts: {df.district.is_unique}.")
    df.to_csv(os.path.join(OUT, name), index=False)

canon = sorted(acs_df["district"])
same = set(acs_df.district) == set(dip_df.district) == set(canon)
log(f"\n### 1.4 Canonical district list\n\n`{canon}` (6 districts, upper case). Every one of the 12 files uses exactly these spellings (after trimming): {same}. No standardization was needed.\n")
all_cols = list(acs_df.columns[1:]) + list(dip_df.columns[1:])
assert len(all_cols) == len(set(all_cols)), "column names collide across files"
log(f"Column names are unique across both files ({len(all_cols)} variable columns; only `district` is shared).\n")

# ---------------------------------------------------------------- glendaleOne
log("## 2. glendaleOne requests (`GlendaleOne_External_Requests.csv` → `glendaleone_clean.csv`)\n")
g = pd.read_csv(os.path.join(RAW, REQ_FILE), dtype=str, keep_default_na=False)
n0 = len(g)
log(f"- Read as text: {n0:,} rows × {g.shape[1]} columns.")
rename = {c: ("district" if c == "Council_District" else re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", re.sub(r"(?<=[a-z])(?=[A-Z])", "_", c).lower())).strip("_")) for c in g.columns}
g = g.rename(columns=rename)
log("- Column renames: " + ", ".join(f"`{k}`→`{v}`" for k, v in rename.items()))
ws_changed = {}
for c in g.columns:
    new = g[c].str.strip().str.replace(r"\s+", " ", regex=True)
    ws_changed[c] = int((new != g[c]).sum()); g[c] = new
log("- Whitespace trimmed/collapsed (cells changed): " + (", ".join(f"{k}: {v:,}" for k, v in ws_changed.items() if v) or "none"))
ph = {"", "n/a", "na", "null", "none", "-"}
ph_counts = {}
district_orig = g["district"].copy()
for c in g.columns:
    m = g[c].str.lower().isin(ph)
    nonblank = int((m & (g[c] != "")).sum())
    if nonblank: ph_counts[c] = g.loc[m & (g[c] != ""), c].value_counts().to_dict()
    g.loc[m, c] = np.nan
log("- Placeholders → empty (non-blank placeholder text only): " + str(ph_counts) + f". Already-blank cells: close_date {g['close_date'].isna().sum():,}, anon_block {g['anon_block'].isna().sum():,}, cross_streets {g['cross_streets'].isna().sum():,} (entirely empty; kept as-is).")
log("  - `NONE` is the name of a 7th GIS polygon (county/unincorporated islands, HANSEN_DISTRICT 'MC'), not a council district; it is treated as unmatched.")

# types
coerce = {}
for c in ["objectid", "request_number", "anon_block"]:
    x = pd.to_numeric(g[c], errors="coerce"); coerce[c] = int((x.isna() & g[c].notna()).sum()); g[c] = x.astype("Int64")
for c in ["latitude", "longitude"]:
    x = pd.to_numeric(g[c], errors="coerce"); coerce[c] = int((x.isna() & g[c].notna()).sum()); g[c] = x
for c in ["date_loaded", "request_date", "last_action_date", "close_date"]:
    x = pd.to_datetime(g[c], format="%Y-%m-%d %H:%M:%S", errors="coerce"); coerce[c] = int((x.isna() & g[c].notna()).sum()); g[c] = x
timeless = {c: bool((g[c].dropna().dt.normalize() == g[c].dropna()).all()) for c in ["request_date", "last_action_date", "close_date"]}
log(f"- Type conversion failures (non-empty text that would not parse): {coerce}. Date-only columns (all times 00:00:00): {timeless}. Dates are UTC per DATA_DICTIONARY.md.")

# window
log("\n### 2.1 Time window (on `request_date`, the request-created date)\n")
monthly = g["request_date"].dt.to_period("M").value_counts().sort_index()
log("Requests per month, full span:\n")
log("| Month | Requests |\n|---|---|")
for k, v in monthly.items(): log(f"| {k} | {v:,} |")
daily = g["request_date"].value_counts().sort_index()
last_day = daily.index.max()
wd = daily[(daily.index >= last_day - pd.Timedelta(days=28)) & (daily.index < last_day)]
wd_med = wd[wd.index.dayofweek == last_day.dayofweek].median()
steady = monthly[monthly.index >= pd.Period("2020-01", "M")]
steady = steady[steady.index < monthly.index.max()]
WIN_START = pd.Timestamp("2020-01-01")
WIN_END = last_day if daily[last_day] >= 0.5 * wd_med else last_day - pd.Timedelta(days=1)
log(f"\n- **Start = {WIN_START.date()}.** December 2019 is the launch month: data begins 2019-12-02 with {monthly[pd.Period('2019-12','M')]:,} requests, below every later month. From January 2020 volume is steady: full months 2020-01 through 2026-07 range {steady.min():,}–{steady.max():,} (median {int(steady.median()):,}). This widens the window beyond the 2023-01-01 floor, as the brief allows.")
log(f"- **End = {WIN_END.date()}.** The file's last request date is {last_day.date()} ({daily[last_day]} requests; median for the same weekday over the prior 4 weeks = {wd_med:.0f}), so that day looks complete. `date_loaded` is {g['date_loaded'].max()} UTC: the City feed has not refreshed since.")
log(f"- ⚠️ **Floor not met at the end:** the brief requires data through 2026-09-01, but the source stops at {last_day.date()}. There is nothing to keep past that date. August 2026 in the file is a partial month ({monthly.iloc[-1]} requests over 5 days) – exclude it from monthly trend work.")
missing_dt = int(g["request_date"].isna().sum())
before = int((g["request_date"] < WIN_START).sum())
after = int((g["request_date"] >= WIN_END + pd.Timedelta(days=1)).sum())
g = g[g["request_date"].notna() & (g["request_date"] >= WIN_START) & (g["request_date"] < WIN_END + pd.Timedelta(days=1))]
log(f"- Counts: total {n0:,} · missing/unparseable request_date (excluded) {missing_dt:,} · before window {before:,} · after window {after:,} · **kept {len(g):,}**.")

# dedupe
log("\n### 2.2 Duplicates\n")
n1 = len(g); g = g.drop_duplicates(); exact = n1 - len(g)
dup_ids = int(g["request_number"].duplicated(keep=False).sum())
g = g.sort_values(["request_number", "last_action_date"], ascending=[True, False]).drop_duplicates("request_number", keep="first").sort_values("request_number")
log(f"- Exact duplicate rows dropped: {exact:,}. Rows sharing a request_number with different content: {dup_ids:,} (kept most recent last_action_date). Rows now: {len(g):,}.")

# categoricals
log("\n### 2.3 Categorical values\n")
log("No channel field exists in this file. Variant check: values that match after lower-casing and removing spaces/punctuation would be merged; near-matches (similarity ≥ 0.9) are listed for review but only merged if they are obvious typos.\n")
for c in ["status", "request_type_group", "request_type", "responsible_department_name"]:
    vc = g[c].value_counts(dropna=False)
    key = g[c].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    merges = {}
    for k, grp in g.groupby(key)[c]:
        vs = grp.value_counts()
        if len(vs) > 1:
            for v in vs.index[1:]: merges[v] = vs.index[0]
    if merges: g[c] = g[c].replace(merges)
    vals = [v for v in vc.index if isinstance(v, str)]
    near = [(a, b) for i, a in enumerate(vals) for b in vals[i+1:] if difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.9]
    log(f"**`{c}`** – {vc.size} distinct. Merges applied: {merges or 'none'}. Near-matches reviewed, not merged (not unambiguous variants – may be renamed types): {near or 'none'}.\n")
    log("| Value | Rows |\n|---|---|")
    for v, n in vc.items(): log(f"| {v} | {n:,} |")
    log("")

# district
log("### 2.4 District → canonical ACS spelling\n")
cmap = {d: d for d in canon}
orig_counts = district_orig.loc[g.index].replace("", "(blank)").value_counts()
g["district"] = g["district"].str.upper().map(lambda v: cmap.get(v, np.nan) if isinstance(v, str) else np.nan)
log("| Original value | Canonical | Rows (in window) |\n|---|---|---|")
for v, n in orig_counts.items(): log(f"| {v} | {cmap.get(str(v).upper(), '(empty – unmatched)')} | {n:,} |")
unmatched = int(g["district"].isna().sum())
log(f"\nUnmatched/blank district rows: {unmatched:,} ({unmatched/len(g):.2%}). Not inferred from address or coordinates.\n")

# flags
log("### 2.5 Flags (added as boolean columns, nothing fixed)\n")
g["flag_close_before_request"] = g["close_date"] < g["request_date"]
g["flag_last_action_before_request"] = g["last_action_date"] < g["request_date"]
g["flag_request_date_future"] = g["request_date"] > RUN_DATE
g["flag_closed_without_close_date"] = (g["status"] == "Closed") & g["close_date"].isna()
g["flag_open_with_close_date"] = (g["status"] != "Closed") & g["close_date"].notna()
g["flag_coords_outside_glendale"] = ~(g["latitude"].between(33.45, 33.85) & g["longitude"].between(-112.45, -112.05))
for c in [c for c in g.columns if c.startswith("flag_")]:
    log(f"- `{c}`: {int(g[c].sum()):,}")
log(f"  - Of the outside-Glendale coordinate rows, {int((g.flag_coords_outside_glendale & g.district.isna()).sum()):,} have no district. Bounding box 33.45–33.85 / −112.45 – −112.05 from DATA_DICTIONARY.md. Coordinates are block-anonymized.")
log(f"- Other impossible values checked: negative request_number {int((g.request_number<0).sum())}, negative anon_block {int((g.anon_block<0).sum())}, anon_block = 0 {int((g.anon_block==0).sum()):,} (left as-is; unclear meaning).\n")

log("### 2.6 Possible personal data (left in place)\n")
log("- `full_address` – block-level street text (e.g. `7800 BLOCK W SOLANO DR`); `anon_block` – block number; `latitude`/`longitude` – block-rounded. No name, phone or email columns exist.\n")

g_out = g.copy()
for c in ["request_date", "last_action_date", "close_date"]: g_out[c] = g_out[c].dt.strftime("%Y-%m-%d")
g_out.to_csv(os.path.join(OUT, "glendaleone_clean.csv"), index=False)
chk = pd.read_csv(os.path.join(OUT, "glendaleone_clean.csv"), parse_dates=["request_date"])
log(f"- Saved `glendaleone_clean.csv`: {len(chk):,} rows × {chk.shape[1]} columns. request_date read back from file: min {chk.request_date.min().date()}, max {chk.request_date.max().date()}.\n")

# ---------------------------------------------------------------- join tests
log("## 3. Join tests\n")
a = pd.read_csv(os.path.join(OUT, "acs_population_summary_clean.csv"))
b = pd.read_csv(os.path.join(OUT, "acs_demo_income_profile_clean.csv"))
m = a.merge(b, on="district", how="outer", indicator=True)
t1 = dict(districts=len(m), missing=int(m.district.isna().sum()), duplicates=int(m.district.duplicated().sum()),
          unmatched=int((m._merge != "both").sum()))
ok1 = t1 == dict(districts=6, missing=0, duplicates=0, unmatched=0)
m = m.drop(columns="_merge")
log(f"- Test 1 – merge both demographic files on `district` (outer): {t1} → **{'PASS' if ok1 else 'FAIL'}**. Merged table: {m.shape[0]} rows × {m.shape[1]} columns.")
# full-width join done in 20k-row chunks: one pass at ~107k x 1,170 columns exceeds the laptop VM's memory
rows_after, matched = 0, 0
for k in range(0, len(chk), 20000):
    jj = chk.iloc[k:k+20000].merge(m, on="district", how="left", validate="many_to_one")
    rows_after += len(jj); matched += int(jj["acs_total_population"].notna().sum()); ncols = jj.shape[1]
    del jj
unm = chk.loc[chk.district.isna() | ~chk.district.isin(m.district), "district"].fillna("(empty)").value_counts().to_dict()
ok2 = rows_after == len(chk)
log(f"- Test 2 – left-join glendaleone_clean ({len(chk):,} rows, all columns) to the full merged table ({m.shape[1]} cols → {ncols} cols joined, run in 20k-row chunks for memory), validate many-to-one: rows after {rows_after:,} (unchanged: {ok2}) · match rate {matched/len(chk):.2%} ({matched:,}) · unmatched district values {unm} → **{'PASS' if ok2 else 'FAIL'}** (unmatched rows are the empty districts from §2.4).\n")

# ---------------------------------------------------------------- raw unchanged + summary
md5_after = {os.path.basename(p): md5(p) for p in raw_files}
log(f"## 4. Raw files unchanged\n\nMD5 of all {len(raw_files)} raw files read, before vs after: {'identical' if md5_before == md5_after else 'CHANGED'}.\n")
log("## 5. Assumptions and open issues\n")
log("- **Assumption:** `request_date` is the request-created date used for the window (unconfirmed).")
log("- **Assumption:** district spellings in the Esri/ACS workbooks are canonical (upper case, e.g. `SAHUARO`). Other city layers use title case (PROJECT.md §6.13).")
log(f"- **Open:** request data ends {last_day.date()}; the 2026-09-01 floor cannot be met until the City feed refreshes (not refreshed since 2026-08-06).")
log("- **Open:** window was widened to start 2020-01-01. The team's earlier working window is 2023-01-01 – 2026-09-01; filter `request_date` if a narrower range is wanted. 2020–2021 are COVID-era years.")
log("- **Open:** only one demographic file is true ACS (2020–2024 5-yr, with MOE). The Demographic and Income Profile is Census 2020 + Esri modelled estimates/projections without MOE; label sources accordingly.")
log("- **Open:** ACS MOEs are large for some district cells (see DATA_DICTIONARY §3.2); compare districts with the `_moe` columns in mind.")
log(f"- **Open:** {unmatched:,} in-window requests have no council district (N/A or NONE) and will drop out of per-district analysis.")
log("- **Open:** `Code_Compliance_Cases_GlendaleOne.csv` not cleaned (no district without spatial join).")
log("- `cross_streets` is entirely empty and `objectid`/`date_loaded` are ETL fields; kept so no data is silently removed.\n")
log("## Appendix A – Demographic column map (original → clean)\n")
log("| File type | Clean column | Original (section > label path [measure]) |\n|---|---|---|")
for ft, cc, orig in colmap: log(f"| {ft} | `{cc}` | {orig} |")
log(f"| both | `district` | Sheet name / cell A4 (district name) |")
log(f"| Demographic and Income Profile | " + " ".join(f"`{v}`" for v in INFO_KEEP.values()) + " | Infographic block: " + "; ".join(INFO_KEEP) + " |")

open(os.path.join(OUT, "cleaning_log.md"), "w").write("\n".join(L) + "\n")
print(f"ACS pop summary: {acs_df.shape}  DIP: {dip_df.shape}")
print(f"glendaleone: {n0} -> {len(chk)}  window {WIN_START.date()}..{WIN_END.date()}  file min/max {chk.request_date.min().date()} {chk.request_date.max().date()}")
print("Join test 1:", t1, "PASS" if ok1 else "FAIL")
print(f"Join test 2: rows {len(chk)} -> {rows_after}  match {matched/len(chk):.2%}  unmatched {unm}", "PASS" if ok2 else "FAIL")
print("infographic checks:", [(d, n1_, n2_, (None if mm is None else len(mm))) for d, n1_, n2_, mm in info_checks])
print("raw unchanged:", md5_before == md5_after, "| placeholders:", placeholder_hits, "| dropped empty:", acs_empty, dip_empty)
