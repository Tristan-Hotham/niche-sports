"""Step 5. Assemble data/results.json (every number used in the page, paper, blog and collage) and
data/page_data.json (the compact tables the page draws from).
Run: python3 code/05_results.py   (after steps 2 to 4)
"""
import json, os, sys, gzip
import numpy as np, pandas as pd
from scipy.stats import chi2

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import sportmap as SM
W = os.path.join(ROOT, "work"); D = os.path.join(ROOT, "data")
WR = json.load(open(os.path.join(W, "world_results.json")))
U = json.load(open(os.path.join(W, "uk_results.json")))
DATA = os.environ.get("NS_DATA", "/home/claude/hist/_data18/niche-sports")
B = json.load(gzip.open(os.path.join(DATA, "ns_world_wikidata.json.gz")))
cs = pd.read_csv(os.path.join(D, "country_sport.csv"))
cw = pd.read_csv(os.path.join(D, "country_sport_wikipedia_only.csv"))
sig = pd.read_csv(os.path.join(D, "signature_sports.csv"), keep_default_na=False)
sigw = pd.read_csv(os.path.join(D, "signature_sports_wikipedia_only.csv"), keep_default_na=False)
rs = pd.read_csv(os.path.join(D, "region_sport.csv"))
md = pd.read_csv(os.path.join(D, "olympic_medals.csv"))
ucs = pd.read_csv(os.path.join(D, "uk_county_sport.csv"))
usig = pd.read_csv(os.path.join(D, "uk_signature.csv"), keep_default_na=False)
geo = json.load(open(os.path.join(D, "geo_countries.json")))
lp = {f["properties"]["iso3"]: f["properties"]["lp"] for f in geo["features"]}
georeg = json.load(open(os.path.join(D, "geo_regions.json")))
lpr = {f["properties"]["code"]: f["properties"]["lp"] for f in georeg["features"]}

R = {k: WR[k] for k in ("meta", "signature", "sports", "medals", "regions", "wp")}
R["pageviews"] = WR.get("pageviews", {})
R["meta"]["retrieved"] = B["retrieved"][:10]
lo = lambda n: float(chi2.ppf(.05, 2 * n) / 2)
R["thr"] = dict(country=SM.MIN_COUNTRY_CLUBS, cell=SM.MIN_CELL, sport=SM.MIN_SPORT_WORLD, region=SM.MIN_REGION_CLUBS,
                region_cell=SM.MIN_REGION_CELL, conf=SM.CONF, lo10=lo(10), lo100=lo(100))
g = lambda iso, s: cs[(cs.iso3 == iso) & (cs.sname == s)].iloc[0]
R["caveat"] = dict(uk_shooting=float(g("GBR", "shooting").n), nor_athletics=float(g("NOR", "athletics").n), swe_minigolf=float(g("SWE", "minigolf").n))
R["uk"] = {k: U[k] for k in ("features", "sites", "areas", "sports_listed", "sports_all", "retrieved", "signature_counts")}
R["uk"]["retrieved"] = (U.get("retrieved") or "")[:10]
R["uk"]["thr_area"] = 300; R["uk"]["thr_cell"] = 5
R["uk"]["top"] = U["top"]; R["uk"]["signature"] = U["signature"]; R["uk"]["sport_sites"] = U["sport_sites"]
R["top"] = WR["top"]; R["region_top"] = WR["region_top"]
R["countries"] = WR["countries"]
sigd = {r.iso3: r for r in sig.itertuples()}
R["sig"] = {r.iso3: dict(name=r.name, status=r.status, sport=r.sport, n=float(r.n) if r.n != "" else None,
                          lq=float(r.lq) if r.lq != "" else None, lq_lo=float(r.lq_lo) if r.lq_lo != "" else None, clubs=float(r.clubs))
            for r in sig.itertuples()}
R["sigw"] = {r.iso3: dict(sport=r.sport, lq=float(r.lq) if r.lq != "" else None, status=r.status) for r in sigw.itertuples()}

# ---------------- page data ----------------
listed = list(R["sports"].keys())
sports = {s: dict(c=SM.COLOURS.get(s, SM.NEUTRAL), n=round(v["clubs"]), k=v["countries"], sh=v["share"]) for s, v in R["sports"].items()}
C = {}
def rows_of(df, c):
    g = df[(df.iso3 == c) & df.sname.isin(listed) & (df.n >= 1)].sort_values("lq_lo", ascending=False)
    return [[r.sname, round(r.n, 1), round(r.lq, 2), round(r.lq_lo, 2), int(bool(r.eligible))] for r in g.itertuples()]
for c in cs.iso3.unique():
    s = sigd.get(c); sw = sigw[sigw.iso3 == c]
    def pack(st):
        if st is None: return None
        if st.status == "too few clubs": return ["few"]
        if st.status == "no clear heartland": return ["none"]
        return [st.sport, round(float(st.n), 1), round(float(st.lq), 2), round(float(st.lq_lo), 2)]
    C[c] = dict(nm=R["countries"][c]["name"], N=round(R["countries"][c]["clubs"]), lp=lp.get(c), g=pack(s),
                gw=pack(sw.iloc[0]) if len(sw) else ["few"], Nw=round(float(sw.iloc[0].clubs)) if len(sw) else 0,
                x=rows_of(cs, c), xw=rows_of(cw, c))
Rg = {}
for code, g2 in rs[rs.sname.isin(listed)].groupby("adm1_code"):
    e = g2[g2.eligible]
    if not len(e) and g2.N_r.iloc[0] < SM.MIN_REGION_CLUBS: 
        Rg[code] = dict(nm=g2.region.iloc[0], ct=g2.country.iloc[0], N=round(g2.N_r.iloc[0]), lp=lpr.get(code), x=[]); continue
    Rg[code] = dict(nm=g2.region.iloc[0], ct=g2.country.iloc[0], N=round(g2.N_r.iloc[0]), lp=lpr.get(code),
                    x=[[r.sname, round(r.n, 1), round(r.lq, 2), round(r.lq_lo, 2)] for r in e.itertuples()])
top = {s: [[t["iso3"], t["n"], t["lq"], t["lq_lo"]] for t in v if t["iso3"] in lp] for s, v in R["top"].items()}
rtop = {s: [[t["code"], t["region"], t["country"], t["n"], t["lq"], t["lq_lo"]] for t in v] for s, v in R["region_top"].items()}
med = {}
for r in md[(md.medals >= 5) & (md.lq >= 1.5)].sort_values("lq", ascending=False).itertuples():
    med.setdefault(r.iso3, []).append([r.sport, int(r.medals), round(r.lq, 2)])
medTop = {}
for r in md[md.medals >= 5].sort_values("lq", ascending=False).itertuples():
    medTop.setdefault(r.sport, []).append([r.iso3, int(r.medals), round(r.lq, 2)])
mj = md[md.medals >= 5].merge(cs[cs.eligible][["iso3", "sname", "lq"]].rename(columns={"sname": "sport", "lq": "club_lq"}), on=["iso3", "sport"])
LABEL_PAIRS = {("FIN", "wrestling"), ("CAN", "curling"), ("NOR", "skiing"), ("HUN", "water polo"), ("COL", "cycling"), ("IND", "field hockey"),
               ("NLD", "field hockey"), ("DEU", "table tennis"), ("USA", "baseball"), ("GBR", "shooting"), ("SWE", "curling"), ("KOR", "archery")}
medPairs = [[R["countries"][r.iso3]["name"], r.sport, round(r.lq, 3), round(r.club_lq, 3), int(r.medals), int((r.iso3, r.sport) in LABEL_PAIRS)] for r in mj.itertuples()]
pvd = {}
if R["pageviews"]:
    for s, v in R["pageviews"]["top"].items(): pvd[s] = [[x["lang"], x["lq"]] for x in v]
LANG = {"fi": "Finnish", "sv": "Swedish", "nl": "Dutch", "pl": "Polish", "hu": "Hungarian", "ga": "Irish", "eu": "Basque", "ca": "Catalan",
        "no": "Norwegian", "da": "Danish", "de": "German", "fr": "French", "it": "Italian", "es": "Spanish", "pt": "Portuguese", "en": "English",
        "ru": "Russian", "uk": "Ukrainian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "cs": "Czech", "sk": "Slovak", "sl": "Slovene",
        "hr": "Croatian", "sr": "Serbian", "bg": "Bulgarian", "ro": "Romanian", "el": "Greek", "tr": "Turkish", "et": "Estonian", "lv": "Latvian",
        "lt": "Lithuanian", "ka": "Georgian", "hy": "Armenian", "az": "Azerbaijani", "kk": "Kazakh", "he": "Hebrew", "ar": "Arabic", "fa": "Persian",
        "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay", "cy": "Welsh",
        "gl": "Galician", "be": "Belarusian", "mn": "Mongolian", "tl": "Tagalog", "ur": "Urdu", "af": "Afrikaans", "sw": "Swahili", "sq": "Albanian",
        "mk": "Macedonian", "bs": "Bosnian", "lb": "Luxembourgish", "is": "Icelandic"}
for s in pvd: pvd[s] = [[LANG.get(a, a), b] for a, b in pvd[s]]
R["lang_names"] = LANG
PV_SHOW = ["pesäpallo", "speedway", "cricket", "bandy", "floorball", "korfball", "field hockey", "baseball", "water polo", "handball", "orienteering", "curling"]
pvTable = [[s, pvd[s][:3]] for s in PV_SHOW if s in pvd]
lead = [[r["name"], r["sport"], r["lq"]] for r in R["signature"]["list"]][:24]
quick = ["handball", "bandy", "korfball", "hurling and camogie", "pesäpallo", "floorball", "field hockey", "cricket", "water polo", "curling",
         "speedway", "netball", "futsal", "orienteering", "roller hockey", "lacrosse", "tchoukball", "badminton"]
quick = [q for q in quick if q in sports]
hero = [[R["countries"][c]["name"], R["sig"][c]["sport"]] for c in ["FIN", "CHE", "IRL", "POL", "NLD", "SWE", "NZL", "CAN"] if R["sig"].get(c, {}).get("status") == "signature"]
# UK
UK = dict(A={}, list=[], n={}, top={}, pts={}, quick=[], sigTop=[])
ul = sorted(U["sport_sites"], key=lambda s: -U["sport_sites"][s])
UK["list"] = [s for s in ul if s != "multi-sport"]
UK["n"] = U["sport_sites"]
for a, g2 in ucs.groupby("area"):
    srow = usig[usig.area == a].iloc[0]
    UK["A"][a] = dict(N=int(g2.N_a.iloc[0]), g=[srow.sport, int(srow.n), round(float(srow.lq), 2), round(float(srow.lq_lo), 2)] if srow.sport else None,
                      x=[[r.sport, int(r.n), round(r.lq, 2), round(r.lq_lo, 2), int(bool(r.eligible))] for r in g2[g2.sport.isin(UK["list"])].itertuples()])
UK["top"] = {s: [[t["area"], t["n"], t["lq"], t["lq_lo"]] for t in v] for s, v in U["top"].items()}
UK["pts"] = json.load(open(os.path.join(W, "uk_points.json")))
pts = {s: v for s, v in UK["pts"].items() if s in UK["n"] and len(v) <= 3000}
json.dump(pts, open(os.path.join(D, "uk_points.json"), "w"), separators=(",", ":"))
UK["pts"] = sorted(pts)
UK["quick"] = [q for q in ["shinty", "real tennis", "fives", "croquet", "lacrosse", "korfball", "curling", "polo", "fencing", "Gaelic games",
                           "stoolball", "skittles", "rugby league", "bowls", "netball", "speedway"] if q in UK["n"]]
UK["sigTop"] = [[r["area"], r["sport"], r["lq"]] for r in U["signature"] if r["sport"]][:12]
PD = dict(sports=sports, colours=SM.COLOURS, neutral=SM.NEUTRAL, sportList=sorted(listed, key=lambda s: s.lower()), defaultSport="handball", quick=quick,
          C=C, R=Rg, top=top, rtop=rtop, med=med, medTop=medTop, medPairs=medPairs, pv=pvd, pvTable=pvTable, lead=lead, heroChips=hero,
          thr=dict(country=SM.MIN_COUNTRY_CLUBS, cell=SM.MIN_CELL, region=SM.MIN_REGION_CLUBS), uk=UK, stories=[])
# stories and UK text are added by 05b_stories.py
json.dump(R, open(os.path.join(D, "results.json"), "w"), indent=1, ensure_ascii=False, default=float)
json.dump(PD, open(os.path.join(W, "page_data.json"), "w"), ensure_ascii=False, separators=(",", ":"), default=float)
print("results", os.path.getsize(os.path.join(D, "results.json")), "page data", os.path.getsize(os.path.join(W, "page_data.json")))
