"""Download the project's raw datasets from the City of Glendale's public ArcGIS feeds.

Usage:
    python src/fetch_data.py            # everything into data/raw/ and data/
    python src/fetch_data.py --limit 500  # quick smoke test (first 500 rows per layer)

Writes:
    data/raw/GlendaleOne_External_Requests.csv   (~108k rows)
    data/raw/Code_Compliance_Cases_GlendaleOne.csv (~56k rows)
    data/council_districts.geojson               (6 districts + the City's NONE polygon)

The two request CSVs are git-ignored because of their size; run this script after cloning.
"""
import argparse, csv, json, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://services1.arcgis.com/9fVTQQSiODPjLUTa/arcgis/rest/services"
LAYERS = {
    "GlendaleOne_External_Requests.csv": f"{BASE}/GlendaleOne_External_Requests/FeatureServer/0",
    "Code_Compliance_Cases_GlendaleOne.csv": f"{BASE}/GlendaleOne_Code_Compliance_Cases/FeatureServer/0",
}
DISTRICTS = f"{BASE}/Glendale_Council_Districts/FeatureServer/0"
PAGE = 2000


def get_json(url, params):
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=120) as r:
        data = json.load(r)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def fetch_layer(url, out_path, limit=None):
    offset, header, n = 0, None, 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = None
        while True:
            count = PAGE if limit is None else min(PAGE, limit - n)
            if count <= 0:
                break
            data = get_json(url + "/query", {
                "where": "1=1", "outFields": "*", "outSR": 4326, "f": "json",
                "resultOffset": offset, "resultRecordCount": count, "returnGeometry": "true",
            })
            feats = data.get("features", [])
            if not feats:
                break
            for f in feats:
                row = dict(f["attributes"])
                g = f.get("geometry") or {}
                row["lon"], row["lat"] = g.get("x"), g.get("y")
                if writer is None:
                    header = list(row.keys())
                    writer = csv.DictWriter(fh, fieldnames=header)
                    writer.writeheader()
                writer.writerow(row)
            n += len(feats)
            offset += len(feats)
            print(f"  {out_path.name}: {n} rows", file=sys.stderr)
            if not data.get("exceededTransferLimit", False) and len(feats) < count:
                break
    return n


def fetch_districts(out_path):
    data = get_json(DISTRICTS + "/query", {"where": "1=1", "outFields": "DIS_NAME", "outSR": 4326, "f": "geojson"})
    out_path.write_text(json.dumps(data))
    return len(data["features"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="max rows per layer (smoke test)")
    args = ap.parse_args()
    for name, url in LAYERS.items():
        n = fetch_layer(url, ROOT / "data" / "raw" / name, args.limit)
        print(f"{name}: {n} rows")
    n = fetch_districts(ROOT / "data" / "council_districts.geojson")
    print(f"council_districts.geojson: {n} features")


if __name__ == "__main__":
    main()
