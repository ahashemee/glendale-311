# data/

- `demographics/` — 12 Esri workbooks from the City, two per Council District: `Demographic_and_Income_Profile_<DISTRICT>.xlsx` and `ACS_Population_Summary_<DISTRICT>.xlsx`. Districts: Barrel, Cactus, Cholla, Ocotillo, Sahuaro, Yucca.
- `council_districts.geojson` — Council District polygons (WGS84) from the City's public ArcGIS feed. Includes the City's `NONE` polygon; drop it for district-level stats.
- `raw/` — the GlendaleOne External Requests and Code Compliance Cases extracts. Git-ignored. Run `python src/fetch_data.py` from the repo root to download them.
