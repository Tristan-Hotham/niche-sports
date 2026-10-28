"""Step 4. Light outlines for the page and figures: countries (Natural Earth 1:50m), first-level regions
(Natural Earth 1:10m admin 1, pre-simplified) and UK counties (ONS boundaries via onsvisual/uk-topojson, as built
for the how-roman-is-your-road project, plus Northern Ireland's 11 districts).
Writes data/geo_countries.json, data/geo_regions.json, data/geo_uk.json (GeoJSON, coordinates rounded).
Run: python3 code/04_geometry.py
"""
import json, os
from shapely.geometry import shape, mapping

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
D = os.path.join(ROOT, "data")
DATA = os.environ.get("NS_DATA", "/home/claude/hist/_data18/niche-sports")
NE = "/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"
UKC = "/home/claude/hist/how-roman-is-your-road/data/counties.geojson"
LTLA = "/home/claude/hist/how-roman-is-your-road/data/ons/ltla.geojson"


def polys(g):
    from shapely.geometry import MultiPolygon, Polygon
    if g.geom_type in ("Polygon", "MultiPolygon"): return g
    ps = [x for x in getattr(g, "geoms", []) if x.geom_type in ("Polygon", "MultiPolygon")]
    out = []
    for x in ps: out += list(x.geoms) if x.geom_type == "MultiPolygon" else [x]
    return MultiPolygon(out)


def rnd(g, nd):
    g = polys(g)
    def r(c):
        if isinstance(c[0], (int, float)): return [round(c[0], nd), round(c[1], nd)]
        return [r(x) for x in c]
    m = mapping(g); return {"type": m["type"], "coordinates": r(m["coordinates"])}


def label_pt(g):
    g = polys(g)
    parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    big = max(parts, key=lambda x: x.area)
    c = big.centroid
    if not big.contains(c): c = big.representative_point()
    return [round(c.y, 2), round(c.x, 2)]


def write(path, feats):
    json.dump({"type": "FeatureCollection", "features": feats}, open(path, "w"), separators=(",", ":"))
    print(path, os.path.getsize(path))


def iso_of(p):
    for k in ("ISO_A3", "ADM0_A3"):
        v = p.get(k)
        if v and v != "-99": return v
    return None


# hand-set label points where the largest polygon's centre is a poor place for a label
LP_FIX = {"USA": [39.5, -98.5], "CAN": [56.0, -106.0], "RUS": [61.0, 96.0], "NOR": [61.5, 9.0], "FRA": [46.6, 2.4],
          "CHL": [-33.0, -70.8], "NZL": [-41.8, 172.8], "GBR": [53.0, -1.6], "IDN": [-1.0, 114.0], "MYS": [3.8, 102.2]}

if __name__ == "__main__":
    W = json.load(open(os.path.join(ROOT, "work", "world_results.json")))
    feats = []
    for f in json.load(open(NE))["features"]:
        p = f["properties"]; c = iso_of(p)
        if p.get("ADM0_A3") == "KOS": c = "XKX"
        if p.get("ADM0_A3") in ("FRA", "NOR"): c = p["ADM0_A3"]
        if c == "ATA": continue
        g = shape(f["geometry"]).simplify(0.05, preserve_topology=True)
        if g.is_empty: continue
        feats.append({"type": "Feature", "properties": {"iso3": c, "name": p["NAME"], "lp": LP_FIX.get(c) or label_pt(g)}, "geometry": rnd(g, 2)})
    write(os.path.join(D, "geo_countries.json"), feats)
    # regions: only those that have any located clubs, to keep the file small
    import pandas as pd
    rs = pd.read_csv(os.path.join(D, "region_sport.csv"))
    used = set(rs.adm1_code)
    feats = []
    for f in json.load(open(os.path.join(DATA, "ne_admin1_s02.geojson")))["features"]:
        p = f["properties"]
        if p["adm1_code"] not in used: continue
        g = shape(f["geometry"]).simplify(0.04, preserve_topology=True)
        if g.is_empty: continue
        feats.append({"type": "Feature", "properties": {"code": p["adm1_code"], "name": (p["name_en"] or p["name"]).replace("\u2013", "-").replace("\u2014", "-"), "country": p["admin"].replace("\u2013", "-"), "lp": label_pt(g)}, "geometry": rnd(g, 2)})
    write(os.path.join(D, "geo_regions.json"), feats)
    feats = []
    for f in json.load(open(UKC))["features"]:
        g = shape(f["geometry"]).simplify(0.006, preserve_topology=True)
        feats.append({"type": "Feature", "properties": {"area": f["properties"]["county"], "nation": f["properties"]["nation"], "lp": label_pt(g)}, "geometry": rnd(g, 3)})
    for f in json.load(open(LTLA))["features"]:
        p = f["properties"]
        if not p["areacd"].startswith("N") or p.get("end"): continue
        g = shape(f["geometry"]).simplify(0.006, preserve_topology=True)
        feats.append({"type": "Feature", "properties": {"area": p["areanm"], "nation": "Northern Ireland", "lp": label_pt(g)}, "geometry": rnd(g, 3)})
    write(os.path.join(D, "geo_uk.json"), feats)
