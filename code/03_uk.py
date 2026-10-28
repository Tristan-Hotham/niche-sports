"""Step 3. UK detail from OpenStreetMap: every feature tagged sport=* (pitches, courts, sports centres, clubs),
gathered through the Overpass API in tiles, assigned to UK counties (ceremonial counties in England, preserved
counties in Wales, council areas in Scotland, districts in Northern Ireland).

To avoid counting the four pitches of one playing field four times, features of the same sport are merged into
"sites": one per sport per grid cell of 0.002 degrees of latitude by 0.003 of longitude (roughly 220 m by 200 m).
Location quotients compare each county's mix of sites with the UK mix, with the same cautious ratio as the world.
Run: python3 code/03_uk.py
"""
import gzip, json, os, re, collections, sys, io, csv
import numpy as np, pandas as pd
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from scipy.stats import chi2

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
DATA = os.environ.get("NS_DATA", "/home/claude/hist/_data18/niche-sports")
W = os.path.join(ROOT, "work"); D = os.path.join(ROOT, "data")
MIN_AREA_SITES = 300; MIN_CELL = 5; MIN_SPORT_UK = 30; MIN_SPORT_LIST = 8
NOT_SPORT = {"clubhouse", "q", "laser tag", "fitness", "pilates", "multi-sport", "yes", "gymnasium", "calisthenics", "dance", "yoga", "obstacle course"}

# OSM sport values merged into one name; anything else keeps its own tag value
NORM = {"soccer": "football", "association_football": "football", "football": "football", "5-a-side": "football", "five-a-side": "football", "miniature_golf": "minigolf", "minigolf": "minigolf", "gym": "fitness", "crossfit": "fitness", "exercise": "fitness", "table_soccer": "table football", "mma": "martial arts", "jiu-jitsu": "martial arts", "muay_thai": "martial arts", "kickboxing": "martial arts",
        "rugby": "rugby union", "rugby_union": "rugby union", "rugby_league": "rugby league",
        "american_football": "American football", "gaelic_games": "Gaelic games", "gaelic_football": "Gaelic games",
        "hurling": "Gaelic games", "camogie": "Gaelic games", "gaelic_handball": "Gaelic games",
        "bowls": "bowls", "lawn_bowls": "bowls", "bowling": "bowls", "crown_green_bowls": "bowls", "indoor_bowls": "bowls",
        "10pin": "ten-pin bowling", "9pin": "nine-pin bowling",
        "real_tennis": "real tennis", "table_tennis": "table tennis", "field_hockey": "field hockey", "hockey": "field hockey",
        "ice_hockey": "ice hockey", "rc_car": "RC cars", "model_aerodrome": "model flying", "horse_racing": "horse racing",
        "equestrian": "equestrian", "horse_riding": "equestrian", "dog_racing": "greyhound racing", "greyhound_racing": "greyhound racing",
        "climbing": "climbing", "bouldering": "climbing", "climbing_adventure": "climbing", "skateboard": "skateboarding",
        "fives": "fives", "eton_fives": "fives", "rugby_fives": "fives", "racquet": "racquet sports", "racquets": "rackets", "angling": "fishing", "ski": "skiing", "kayaking": "canoeing", "shooting_range": "shooting", "ice_skating": "ice skating", "mini_tennis": "tennis",
        "shooting": "shooting", "clay_pigeon_shooting": "shooting", "archery": "archery", "multi": "multi-sport",
        "motor": "motorsport", "motocross": "motorsport", "karting": "karting", "speedway": "speedway",
        "beachvolleyball": "beach volleyball", "beach_volleyball": "beach volleyball", "basketball": "basketball", "netball": "netball",
        "running": "athletics", "athletics": "athletics", "canoe": "canoeing", "kayak": "canoeing", "sailing": "sailing",
        "rowing": "rowing", "swimming": "swimming", "diving": "diving", "scuba_diving": "diving", "padel": "padel",
        "pickleball": "pickleball", "petanque": "pétanque", "boules": "pétanque", "skittles": "skittles", "korfball": "korfball",
        "handball": "handball", "lacrosse": "lacrosse", "shinty": "shinty", "curling": "curling", "croquet": "croquet",
        "polo": "polo", "fencing": "fencing", "cricket": "cricket", "cricket_nets": "cricket", "golf": "golf", "tennis": "tennis",
        "squash": "squash", "badminton": "badminton", "volleyball": "volleyball", "baseball": "baseball", "softball": "softball",
        "gymnastics": "gymnastics", "boxing": "boxing", "judo": "judo", "karate": "karate", "martial_arts": "martial arts",
        "taekwondo": "martial arts", "fitness": "fitness", "yoga": "fitness", "cycling": "cycling", "bmx": "cycling",
        "mtb": "cycling", "trampoline": "trampolining", "darts": "darts", "billiards": "cue sports", "snooker": "cue sports",
        "pool": "cue sports", "chess": "chess", "orienteering": "orienteering", "ultimate": "ultimate", "quidditch": "quidditch",
        "rounders": "rounders", "stoolball": "stoolball", "tchoukball": "tchoukball", "ice_skating": "ice skating",
        "skiing": "skiing", "dog_agility": "dog agility", "paddle_tennis": "padel", "water_polo": "water polo",
        "wakeboarding": "water sports", "water_ski": "water sports", "surfing": "surfing", "free_flying": "free flying",
        "gliding": "gliding", "parachuting": "parachuting", "model_railway": "", "horseshoes": "horseshoes", "boules;petanque": "pétanque"}
NICHE = ["real tennis", "fives", "rackets", "shinty", "curling", "croquet", "lacrosse", "korfball", "handball", "polo",
         "fencing", "Gaelic games", "stoolball", "rounders", "skittles", "pétanque", "bowls", "netball", "rugby league",
         "American football", "baseball", "softball", "ice hockey", "speedway", "greyhound racing", "padel", "pickleball",
         "beach volleyball", "archery", "shooting", "rowing", "canoeing", "sailing", "climbing", "equestrian", "orienteering",
         "field hockey", "squash", "badminton", "basketball", "volleyball", "cricket", "golf", "rugby union", "tennis",
         "skateboarding", "ultimate", "water polo", "quidditch", "tchoukball", "ice skating", "skiing", "horse racing", "karting",
         "motorsport", "gliding", "surfing", "trampolining", "gymnastics", "boxing", "judo", "darts", "cue sports", "chess"]


def lo_bound(n, conf=0.90):
    n = np.asarray(n, float); a = (1 - conf) / 2
    return np.where(n > 0, chi2.ppf(a, 2 * np.maximum(n, 1e-9)) / 2, 0.0)


B = json.load(gzip.open(os.path.join(DATA, "ns_uk_osm.json.gz")))
seen = set(); rows = []
for key, text in B["rows"].items():
    for rec in csv.reader(io.StringIO(text), delimiter="\t"):
        if len(rec) < 5 or not rec[2]: continue
        t, i, lat, lon, sport = rec[:5]
        if (t, i) in seen: continue
        seen.add((t, i))
        rows.append(dict(type=t, id=i, lat=float(lat), lon=float(lon), sport=sport, leisure=rec[5] if len(rec) > 5 else "",
                         club=rec[6] if len(rec) > 6 else "", name=rec[8] if len(rec) > 8 else ""))
df = pd.DataFrame(rows)
print("features", len(df))
# assign to areas
geo = json.load(open(os.path.join(D, "geo_uk.json")))
# use the unsimplified ONS-derived outlines for assignment
full = []
for f in json.load(open("/home/claude/hist/how-roman-is-your-road/data/counties.geojson"))["features"]:
    full.append((f["properties"]["county"], f["properties"]["nation"], shape(f["geometry"]).buffer(0)))
for f in json.load(open("/home/claude/hist/how-roman-is-your-road/data/ons/ltla.geojson"))["features"]:
    p = f["properties"]
    if p["areacd"].startswith("N") and not p.get("end"): full.append((p["areanm"], "Northern Ireland", shape(f["geometry"]).buffer(0)))
geoms = [g for _, _, g in full]; tree = STRtree(geoms)
def where(lon, lat):
    p = Point(lon, lat)
    for i in tree.query(p):
        if geoms[i].contains(p): return i
    # within 300 m of the coast (piers, lidos, marinas)
    for i in tree.query(p.buffer(0.004)):
        if geoms[i].distance(p) < 0.004: return i
    return -1
df["ai"] = [where(a, b) for a, b in zip(df.lon, df.lat)]
df = df[df.ai >= 0].copy()
df["area"] = df.ai.map(lambda i: full[i][0]); df["nation"] = df.ai.map(lambda i: full[i][1])
print("in UK", len(df))
# split multi-valued sport tags
ex = []
for r in df.itertuples():
    vals = [v.strip().lower() for v in re.split(r"[;,]", r.sport) if v.strip()]
    names = []
    for v in vals:
        nm = NORM.get(v, v.replace("_", " "))
        if nm and nm not in names: names.append(nm)
    for nm in names:
        ex.append((r.area, r.nation, nm, r.lat, r.lon, 1.0 / len(names), r.name, r.type + "/" + r.id))
ex = pd.DataFrame(ex, columns=["area", "nation", "sport", "lat", "lon", "w", "name", "osm"])
ex["cell"] = (np.floor(ex.lat / 0.002)).astype(int).astype(str) + "_" + (np.floor(ex.lon / 0.003)).astype(int).astype(str)
sites = ex.sort_values("name", ascending=False).groupby(["sport", "cell"], as_index=False).agg(
    area=("area", "first"), nation=("nation", "first"), lat=("lat", "mean"), lon=("lon", "mean"), features=("osm", "size"),
    name=("name", "first"))
print("sites", len(sites))
sites.to_csv(os.path.join(W, "uk_sites.csv"), index=False)
U = {"features": int(len(df)), "feature_sport_rows": int(len(ex)), "sites": int(len(sites)), "areas": int(sites.area.nunique()),
     "tiles": len(B["rows"]), "retrieved": B.get("retrieved", "")}
Ns = sites.groupby("sport").size(); N = len(sites); Na = sites.groupby("area").size()
keep = Ns[(Ns >= MIN_SPORT_LIST) & ~Ns.index.isin(NOT_SPORT)].index        # listed on the page
keep_sig = Ns[(Ns >= MIN_SPORT_UK) & ~Ns.index.isin(NOT_SPORT)].index   # can be a county's signature sport
U["sports_listed"] = int(len(keep)); U["sports_all"] = int(Ns.size); U["sports_sig"] = int(len(keep_sig))
U["top_sports"] = {k: int(v) for k, v in Ns.sort_values(ascending=False).head(25).items()}
cs = sites.groupby(["area", "nation", "sport"]).size().rename("n").reset_index()
cs["N_a"] = cs.area.map(Na); cs["N_s"] = cs.sport.map(Ns)
cs["lq"] = (cs.n / cs.N_a) / (cs.N_s / N)
cs["lq_lo"] = lo_bound(cs.n) / cs.N_a / (cs.N_s / N)
cs["eligible"] = (cs.N_a >= MIN_AREA_SITES) & (cs.n >= MIN_CELL) & cs.sport.isin(keep)
cs.sort_values(["area", "lq_lo"], ascending=[True, False]).to_csv(os.path.join(D, "uk_county_sport.csv"), index=False, float_format="%.4f")
sig = []
for a, g in cs.groupby("area"):
    e = g[g.eligible & g.sport.isin(keep_sig)].sort_values("lq_lo", ascending=False)
    if len(e) and e.iloc[0].lq_lo > 1:
        t = e.iloc[0]; sig.append(dict(area=a, nation=t.nation, sport=t.sport, n=int(t.n), lq=float(t.lq), lq_lo=float(t.lq_lo), sites=int(t.N_a),
                                        second=e.iloc[1].sport if len(e) > 1 else ""))
    else:
        sig.append(dict(area=a, nation=g.nation.iloc[0], sport="", n=0, lq=np.nan, lq_lo=np.nan, sites=int(Na[a]), second=""))
sig = pd.DataFrame(sig); sig.to_csv(os.path.join(D, "uk_signature.csv"), index=False, float_format="%.4f")
U["signature"] = sig.sort_values("lq", ascending=False).fillna("").to_dict("records")
U["signature_counts"] = sig[sig.sport != ""].sport.value_counts().to_dict()
U["top"] = {}
for s in keep:
    g = cs[(cs.sport == s) & cs.eligible].sort_values("lq_lo", ascending=False)
    U["top"][s] = [dict(area=r.area, nation=r.nation, n=int(r.n), lq=round(r.lq, 2), lq_lo=round(r.lq_lo, 2)) for r in g.head(8).itertuples()]
U["sport_sites"] = {s: int(Ns[s]) for s in keep}
# points for the page: niche sports only (one per site)
pts = {}
for s in NICHE:
    if s not in Ns.index: continue
    g = sites[sites.sport == s]
    pts[s] = [[round(r.lat, 4), round(r.lon, 4)] for r in g.itertuples()]
json.dump(pts, open(os.path.join(W, "uk_points.json"), "w"), separators=(",", ":"))
sites[sites.sport.isin(NICHE)][["sport", "area", "nation", "lat", "lon", "features", "name"]].to_csv(
    os.path.join(D, "uk_sites_niche.csv"), index=False, float_format="%.5f")
json.dump(U, open(os.path.join(W, "uk_results.json"), "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: U[k] for k in ("features", "sites", "areas", "sports_listed")}), U["signature_counts"])
