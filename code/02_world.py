"""Step 2. World analysis: clubs by sport and country, location quotients, cautious ratios, signature sports,
first-level regions, Olympic medal tables (second signal) and Wikipedia pageviews by language (third signal).

Location quotient (LQ) for sport s in place c:  LQ = (n_cs / N_c) / (N_s / N)
  n_cs clubs of sport s in c, N_c all clubs in c, N_s clubs of s everywhere, N all clubs.
  Because it compares a place with itself, how thoroughly Wikidata covers a country cancels out.
Cautious ratio: the same with n_cs replaced by the lower end of a two-sided 90% Poisson interval for n_cs,
  so a sport with a handful of clubs cannot top the list by chance.
Run: python3 code/02_world.py   (after 01_prepare.py)
"""
import gzip, json, os, re, collections, sys
import numpy as np, pandas as pd
from scipy.stats import chi2, spearmanr
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import sportmap as SM
DATA = os.environ.get("NS_DATA", "/home/claude/hist/_data18/niche-sports")
W = os.path.join(ROOT, "work"); D = os.path.join(ROOT, "data")
os.makedirs(D, exist_ok=True)


def lo_bound(n, conf=SM.CONF):
    n = np.asarray(n, float)
    a = (1 - conf) / 2
    return np.where(n > 0, chi2.ppf(a, 2 * np.maximum(n, 1e-9)) / 2, 0.0)


items = pd.read_csv(os.path.join(W, "items_raw.csv"))
sp_raw = pd.read_csv(os.path.join(W, "sports_raw.csv")).set_index("sport")
co_raw = pd.read_csv(os.path.join(W, "countries_raw.csv")).set_index("country")
R = {"meta": {}}
R["meta"]["wikidata_rows"] = int(len(items)); R["meta"]["wikidata_items_all"] = int(items.item.nunique())
R["meta"]["excluded_items"] = int(items[items.excluded].item.nunique())
it = items[~items.excluded].copy()
it["sport"] = it.sport.map(lambda q: SM.MERGE.get(q, q))
it = it[~it.sport.isin(SM.DROP)]

# country codes: fix Wikidata gaps, fold UK nations into GBR, drop former states
ISO_FIX = {"Q55": "NLD", "Q26": "GBR", "Q25": "GBR", "Q22": "GBR", "Q21": "GBR", "Q1246": "XKX", "Q29999": "NLD"}
FORMER = {"SUN", "DDR", "CSK", "YUG", "SCG", "DEU_REICH"}
def iso(q):
    if q in ISO_FIX: return ISO_FIX[q]
    v = co_raw.iso3.get(q)
    return v if isinstance(v, str) else None
it["iso3"] = it.country.map(iso)
R["meta"]["dropped_no_iso"] = int(it[it.iso3.isna()].item.nunique())
R["meta"]["dropped_former"] = int(it[it.iso3.isin(FORMER)].item.nunique())
it = it[it.iso3.notna() & ~it.iso3.isin(FORMER)]
it = it.drop_duplicates(["item", "sport", "iso3"])
# an item listed in two countries is split between them, and one with k sports counts 1/k for each
k_sp = it.groupby("item").sport.transform("nunique"); k_c = it.groupby("item").iso3.transform("nunique")
it["w"] = 1.0 / (k_sp * k_c)

labels = {q: SM.name(q, (sp_raw.label.get(q) if isinstance(sp_raw.label.get(q), str) else q)) for q in it.sport.unique()}
it["sname"] = it.sport.map(labels)
N = it.w.sum()
Ns = it.groupby("sname").w.sum()
keep_s = Ns[Ns >= SM.MIN_SPORT_WORLD].index
R["meta"]["clubs"] = int(round(N)); R["meta"]["items"] = int(it.item.nunique())
R["meta"]["sports_all"] = int(Ns.size); R["meta"]["sports_listed"] = int(len(keep_s))
R["meta"]["countries_all"] = int(it.iso3.nunique())
R["meta"]["football_share"] = float(Ns["football"] / N)

# country names (Natural Earth names are used on the page; Wikidata label as fallback)
ne = json.load(open("/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"))
ne_name = {}
for f in ne["features"]:
    p = f["properties"]
    for key in ("ADM0_A3", "ISO_A3", "ISO_A3_EH"):
        if p.get(key) and p[key] != "-99": ne_name.setdefault(p[key], p["NAME"])
wd_name = it.drop_duplicates("iso3").set_index("iso3").country.map(lambda q: co_raw.label.get(q))
cname = lambda c: ne_name.get(c) or wd_name.get(c) or c
NAMEFIX = {"USA": "United States", "GBR": "United Kingdom", "CZE": "Czechia", "BIH": "Bosnia and Herzegovina", "COD": "DR Congo",
           "CAF": "Central African Republic", "DOM": "Dominican Republic", "XKX": "Kosovo"}

cs = it.groupby(["iso3", "sname"]).w.sum().rename("n").reset_index()
Nc = it.groupby("iso3").w.sum()
cs["N_c"] = cs.iso3.map(Nc); cs["N_s"] = cs.sname.map(Ns)
cs["share"] = cs.n / cs.N_c
cs["lq"] = cs.share / (cs.N_s / N)
cs["lq_lo"] = lo_bound(np.round(cs.n)) / cs.N_c / (cs.N_s / N)
cs["eligible"] = (cs.N_c >= SM.MIN_COUNTRY_CLUBS) & (cs.n >= SM.MIN_CELL) & cs.sname.isin(keep_s)
cs["name"] = cs.iso3.map(lambda c: NAMEFIX.get(c, cname(c)))
cs.sort_values(["iso3", "lq_lo"], ascending=[True, False]).to_csv(os.path.join(D, "country_sport.csv"), index=False, float_format="%.4f")

# signature sport per country
rows = []
for c, g in cs.groupby("iso3"):
    nc = Nc[c]; e = g[g.eligible].sort_values("lq_lo", ascending=False)
    if nc < SM.MIN_COUNTRY_CLUBS:
        rows.append(dict(iso3=c, status="too few clubs", clubs=nc)); continue
    if not len(e) or e.iloc[0].lq_lo <= 1:
        rows.append(dict(iso3=c, status="no clear heartland", clubs=nc)); continue
    t = e.iloc[0]; r2 = e.iloc[1] if len(e) > 1 else None
    rows.append(dict(iso3=c, status="signature", clubs=nc, sport=t.sname, n=t.n, lq=t.lq, lq_lo=t.lq_lo, share=t.share,
                     second=(r2.sname if r2 is not None else ""), second_lq=(r2.lq if r2 is not None else np.nan),
                     top_share_sport=g.sort_values("n").iloc[-1].sname, top_share=g.n.max() / nc))
sig = pd.DataFrame(rows); sig["name"] = sig.iso3.map(lambda c: NAMEFIX.get(c, cname(c)))
sig.to_csv(os.path.join(D, "signature_sports.csv"), index=False, float_format="%.4f")
S = sig[sig.status == "signature"]
R["signature"] = dict(n_countries_mapped=int((sig.clubs >= SM.MIN_COUNTRY_CLUBS).sum()), n_signature=int(len(S)),
                      n_no_clear=int((sig.status == "no clear heartland").sum()), n_too_few=int((sig.status == "too few clubs").sum()),
                      n_sports=int(S.sport.nunique()), by_sport=S.sport.value_counts().to_dict(),
                      football_signature=int((S.sport == "football").sum()))
R["signature"]["list"] = [dict(iso3=r.iso3, name=r.name, sport=r.sport, n=round(r.n, 1), lq=round(r.lq, 2), lq_lo=round(r.lq_lo, 2),
                               share=round(r.share, 4), clubs=round(r.clubs), second=r.second) for r in S.sort_values("lq", ascending=False).itertuples()]

# per-sport league tables (eligible countries, ranked by cautious ratio)
top = {}
for s in keep_s:
    g = cs[(cs.sname == s) & cs.eligible].sort_values("lq_lo", ascending=False)
    top[s] = [dict(iso3=r.iso3, name=r.name, n=round(r.n, 1), lq=round(r.lq, 2), lq_lo=round(r.lq_lo, 2), share=round(r.share, 4)) for r in g.head(12).itertuples()]
sport_tab = pd.DataFrame(dict(sport=Ns.index, clubs=Ns.values))
sport_tab["countries"] = sport_tab.sport.map(cs[cs.n > 0].groupby("sname").iso3.nunique())
sport_tab["world_share"] = sport_tab.clubs / N
sport_tab["listed"] = sport_tab.sport.isin(keep_s)
sport_tab["top_place"] = sport_tab.sport.map(lambda s: top.get(s, [{}])[0].get("name", "") if top.get(s) else "")
sport_tab["top_lq"] = sport_tab.sport.map(lambda s: top[s][0]["lq"] if top.get(s) else np.nan)
sport_tab["colour"] = sport_tab.sport.map(lambda s: SM.COLOURS.get(s, SM.NEUTRAL))
sport_tab.sort_values("clubs", ascending=False).to_csv(os.path.join(D, "sports.csv"), index=False, float_format="%.5f")
R["sports"] = {r.sport: dict(clubs=round(r.clubs, 1), countries=int(r.countries), share=round(r.world_share, 5), colour=r.colour)
               for r in sport_tab[sport_tab.listed].itertuples()}
R["top"] = top
R["countries"] = {c: dict(name=NAMEFIX.get(c, cname(c)), clubs=round(float(Nc[c]), 1)) for c in Nc.index}

# ---------- check: only clubs with at least one Wikipedia article ----------
EXTRA = json.load(gzip.open(os.path.join(DATA, "ns_extra.json.gz"))) if os.path.exists(os.path.join(DATA, "ns_extra.json.gz")) else None
if EXTRA:
    sl = {}
    for l in EXTRA["sitelinks"].split("\n")[1:]:
        f = l.split("\t")
        if len(f) == 2:
            m = re.match(r'"?(\d+)', f[1]); sl[f[0]] = int(m.group(1)) if m else 0
    itw = it[it.item.map(lambda q: sl.get(q, 0) > 0)].copy()
    itw["w"] = 1.0 / (itw.groupby("item").sport.transform("nunique") * itw.groupby("item").iso3.transform("nunique"))
    Nw = itw.w.sum(); Nsw = itw.groupby("sname").w.sum(); Ncw = itw.groupby("iso3").w.sum()
    cw = itw.groupby(["iso3", "sname"]).w.sum().rename("n").reset_index()
    cw["N_c"] = cw.iso3.map(Ncw); cw["N_s"] = cw.sname.map(Nsw)
    cw["lq"] = (cw.n / cw.N_c) / (cw.N_s / Nw)
    cw["lq_lo"] = lo_bound(np.round(cw.n)) / cw.N_c / (cw.N_s / Nw)
    cw["eligible"] = (cw.N_c >= SM.MIN_COUNTRY_CLUBS) & (cw.n >= SM.MIN_CELL) & cw.sname.isin(keep_s)
    cw["name"] = cw.iso3.map(lambda c: NAMEFIX.get(c, cname(c)))
    cw.sort_values(["iso3", "lq_lo"], ascending=[True, False]).to_csv(os.path.join(D, "country_sport_wikipedia_only.csv"), index=False, float_format="%.4f")
    rows = []
    for c, g in cw.groupby("iso3"):
        e = g[g.eligible].sort_values("lq_lo", ascending=False)
        if Ncw[c] < SM.MIN_COUNTRY_CLUBS: st = "too few clubs"; t = None
        elif not len(e) or e.iloc[0].lq_lo <= 1: st = "no clear heartland"; t = None
        else: st = "signature"; t = e.iloc[0]
        rows.append(dict(iso3=c, status=st, clubs=Ncw[c], sport=t.sname if t is not None else "", n=t.n if t is not None else np.nan,
                         lq=t.lq if t is not None else np.nan, lq_lo=t.lq_lo if t is not None else np.nan))
    sigw = pd.DataFrame(rows); sigw["name"] = sigw.iso3.map(lambda c: NAMEFIX.get(c, cname(c)))
    sigw.to_csv(os.path.join(D, "signature_sports_wikipedia_only.csv"), index=False, float_format="%.4f")
    m = sig[sig.status == "signature"].merge(sigw[sigw.status == "signature"], on="iso3", suffixes=("", "_w"))
    R["wp"] = dict(clubs=int(round(Nw)), share=float(Nw / N), countries_mapped=int((sigw.clubs >= SM.MIN_COUNTRY_CLUBS).sum()),
                   n_signature=int((sigw.status == "signature").sum()), both=int(len(m)), same_sig=int((m.sport == m.sport_w).sum()),
                   by_sport=sigw[sigw.status == "signature"].sport.value_counts().to_dict(),
                   changed=[dict(iso3=r.iso3, name=r.name, all=r.sport, wp=r.sport_w) for r in m[m.sport != m.sport_w].itertuples()])
    CW = cw

# ---------- first-level regions (Natural Earth admin 1), clubs with coordinates ----------
A1 = json.load(open(os.path.join(DATA, "ne_admin1_s02.geojson")))
geoms = [shape(f["geometry"]) for f in A1["features"]]
props = [f["properties"] for f in A1["features"]]
tree = STRtree(geoms)
pts = it[it.lat.notna()].drop_duplicates(["item", "sport"]).copy()
R["meta"]["items_located"] = int(pts.item.nunique()); R["meta"]["located_share"] = float(pts.item.nunique() / it.item.nunique())
uniq = pts.drop_duplicates("item")[["item", "lon", "lat", "iso3"]]
reg = {}
for r in uniq.itertuples():
    p = Point(r.lon, r.lat)
    hit = None
    for i in tree.query(p):
        if geoms[i].contains(p): hit = i; break
    reg[r.item] = hit
pts["reg"] = pts.item.map(reg)
R["meta"]["located_in_region"] = float(pts.drop_duplicates("item").reg.notna().mean())
pts = pts[pts.reg.notna()].copy(); pts["reg"] = pts.reg.astype(int)
# a club placed in a region of a different country than its P17 still counts for that region (border clubs, HQ abroad)
kk = pts.groupby("item").sport.transform("nunique"); pts["w2"] = 1.0 / kk
Nr = pts.groupby("reg").w2.sum()
Nl = pts.w2.sum(); Nls = pts.groupby("sname").w2.sum()
rs = pts.groupby(["reg", "sname"]).w2.sum().rename("n").reset_index()
rs["N_r"] = rs.reg.map(Nr); rs["share"] = rs.n / rs.N_r
rs["lq"] = rs.share / rs.sname.map(Nls / Nl)
rs["lq_lo"] = lo_bound(np.round(rs.n)) / rs.N_r / rs.sname.map(Nls / Nl)
rs["eligible"] = (rs.N_r >= SM.MIN_REGION_CLUBS) & (rs.n >= SM.MIN_REGION_CELL) & rs.sname.isin(keep_s)
clean = lambda t: (t or "").replace("\u2013", "-").replace("\u2014", "-")   # Natural Earth uses en dashes in some names
rs["region"] = rs.reg.map(lambda i: clean(props[i]["name_en"] or props[i]["name"])); rs["country"] = rs.reg.map(lambda i: clean(props[i]["admin"]))
rs["adm1_code"] = rs.reg.map(lambda i: props[i]["adm1_code"])
rs.drop(columns="reg").sort_values(["adm1_code", "lq_lo"], ascending=[True, False]).to_csv(os.path.join(D, "region_sport.csv"), index=False, float_format="%.4f")
R["regions"] = dict(n_regions=int(len(Nr)), n_eligible=int((Nr >= SM.MIN_REGION_CLUBS).sum()), located_clubs=round(float(Nl)))
rtop = {}
for s in keep_s:
    g = rs[(rs.sname == s) & rs.eligible].sort_values("lq_lo", ascending=False)
    rtop[s] = [dict(code=r.adm1_code, region=r.region, country=r.country, n=round(r.n, 1), lq=round(r.lq, 2), lq_lo=round(r.lq_lo, 2)) for r in g.head(8).itertuples()]
R["region_top"] = rtop
# region signature
rsig = []
for code, g in rs.groupby("adm1_code"):
    e = g[g.eligible].sort_values("lq_lo", ascending=False)
    if len(e) and e.iloc[0].lq_lo > 1:
        t = e.iloc[0]; rsig.append(dict(adm1_code=code, region=t.region, country=t.country, sport=t.sname, n=t.n, lq=t.lq, lq_lo=t.lq_lo, clubs=t.N_r))
rsig = pd.DataFrame(rsig); rsig.to_csv(os.path.join(D, "region_signature.csv"), index=False, float_format="%.4f")
R["regions"]["n_signature"] = int(len(rsig))

# ---------- Olympic medal tables (English Wikipedia), second signal ----------
B = json.load(gzip.open(os.path.join(DATA, "ns_world_wikidata.json.gz")))
ioc = {}
for l in B["ioc"].split("\n")[1:]:
    f = l.split("\t")
    if len(f) < 3: continue
    code = f[1].strip('"'); i3 = f[2].strip('"')
    if i3: ioc.setdefault(code, i3)
WP2S = {"Fencing": "fencing", "Handball": "handball", "Field hockey": "field hockey", "Water polo": "water polo", "Judo": "judo",
        "Wrestling": "wrestling", "Weightlifting": "weightlifting", "Boxing": "boxing", "Canoeing": "canoeing", "Rowing": "rowing",
        "Sailing": "sailing", "Equestrian": "equestrian sport", "Archery": "archery", "Table tennis": "table tennis",
        "Badminton": "badminton", "Modern pentathlon": "modern pentathlon", "Shooting": "shooting", "Cycling": "cycling",
        "Gymnastics": "gymnastics", "Volleyball": "volleyball", "Basketball": "basketball", "Football": "football",
        "Athletics": "athletics", "Swimming": "swimming", "Diving": "diving", "Taekwondo": "taekwondo", "Tennis": "tennis",
        "Triathlon": "triathlon", "Golf": "golf", "Baseball": "baseball", "Softball": "softball",
        "Artistic swimming": "artistic swimming", "Beach volleyball": "beach volleyball", "Karate": "karate",
        "Curling": "curling", "Biathlon": "biathlon", "Bobsleigh": "bobsleigh", "Luge": "luge", "Skeleton": "skeleton",
        "Speed skating": "speed skating", "Short-track speed skating": "speed skating", "Figure skating": "figure skating",
        "Ice hockey": "ice hockey", "Cross-country skiing": "skiing", "Ski jumping": "skiing", "Nordic combined": "skiing",
        "Alpine skiing": "skiing", "Freestyle skiing": "skiing", "Snowboarding": "snowboarding", "Rugby sevens": "rugby union",
        "Sport climbing": "climbing"}
med = collections.defaultdict(float); med_hist = collections.defaultdict(float); med_src = []
for title, v in B["wp"].items():
    sport = WP2S.get(title.split(" at the ")[0])
    if not sport: continue
    txt = v["rev"]
    tabs = re.findall(r"\{\{\s*Medals table(.*?)\n\}\}", txt, flags=re.S | re.I)
    best = None; bt = -1
    for t in tabs:
        vals = collections.defaultdict(int)
        for kind, code, n in re.findall(r"\b(gold|silver|bronze)_([A-Z]{3})\s*=\s*(\d+)", t):
            vals[code] += int(n)
        tot = sum(vals.values())
        if tot > bt: bt, best = tot, vals
    if not best: continue
    med_src.append(dict(article=v["title"], sport=sport, medals=bt))
    for code, n in best.items():
        if code in ioc: med[(ioc[code], sport)] += n
        else: med_hist[(code, sport)] += n
md = pd.DataFrame([dict(iso3=a, sport=b, medals=n) for (a, b), n in med.items()])
M = md.medals.sum(); Mc = md.groupby("iso3").medals.sum(); Ms = md.groupby("sport").medals.sum()
md["lq"] = (md.medals / md.iso3.map(Mc)) / (md.sport.map(Ms) / M)
md["name"] = md.iso3.map(lambda c: NAMEFIX.get(c, cname(c)))
md.to_csv(os.path.join(D, "olympic_medals.csv"), index=False, float_format="%.4f")
R["medals"] = dict(articles=len(med_src), medals_current=int(M), medals_former=int(sum(med_hist.values())),
                   sports=int(md.sport.nunique()), countries=int(md.iso3.nunique()))
mj = md.merge(cs[cs.eligible][["iso3", "sname", "lq"]].rename(columns={"sname": "sport", "lq": "club_lq"}), on=["iso3", "sport"])
mj = mj[(md.medals.reindex(mj.index).fillna(0) >= 0)]
mj = mj[mj.medals >= 5]
rho = spearmanr(np.log(mj.lq), np.log(mj.club_lq))
R["medals"]["pairs"] = int(len(mj)); R["medals"]["spearman"] = float(rho.statistic); R["medals"]["p"] = float(rho.pvalue)
both = mj[(mj.lq >= 2) & (mj.club_lq >= 2)].sort_values("club_lq", ascending=False)
R["medals"]["both_high"] = [dict(iso3=r.iso3, name=r.name, sport=r.sport, medals=int(r.medals), medal_lq=round(r.lq, 2), club_lq=round(r.club_lq, 2)) for r in both.itertuples()]
R["medals"]["by_pair"] = {f"{r.iso3}|{r.sport}": [int(r.medals), round(r.lq, 2)] for r in md[md.medals >= 3].itertuples()}

# ---------- Wikipedia pageviews by language edition (optional, third signal) ----------
pvp = os.path.join(DATA, "ns_extra.json.gz")
if os.path.exists(pvp):
    PV = EXTRA
    pv = pd.DataFrame(PV["pv"], columns=["sport", "lang", "title", "views"])
    pv["sport"] = pv.sport.map(lambda q: SM.MERGE.get(q, q))
    pv = pv[~pv.sport.isin(SM.DROP)]
    pv["sname"] = pv.sport.map(lambda q: labels.get(q) or SM.NAMES.get(q) or (sp_raw.label.get(q) if isinstance(sp_raw.label.get(q), str) else q))
    pv = pv.groupby(["lang", "sname"]).views.sum().reset_index()
    # every edition is compared on the same set of sports; a sport with no article in an edition counts as 0 views there
    full_idx = pd.MultiIndex.from_product([pv.lang.unique(), pv.sname.unique()], names=["lang", "sname"])
    pv = pv.set_index(["lang", "sname"]).reindex(full_idx, fill_value=0).reset_index()
    Vl = pv.groupby("lang").views.sum()
    big = Vl[Vl >= 200000].index          # editions with at least 200,000 views a year across these articles
    pv = pv[pv.lang.isin(big)].copy()
    common = pv.sname.unique()
    pv["share"] = pv.views / pv.lang.map(Vl)
    mean_share = pv.groupby("sname").share.mean()
    pv["lq"] = pv.share / pv.sname.map(mean_share)
    pv.to_csv(os.path.join(D, "pageviews_language.csv"), index=False, float_format="%.5f")
    R["pageviews"] = dict(langs=int(pv.lang.nunique()), sports=int(len(common)), views=int(pv.views.sum()), year=2025, failed=len(PV.get("pv_failed", [])), requests=len(PV["pv"]))
    R["pageviews"]["top"] = {s: [dict(lang=r.lang, lq=round(r.lq, 2), views=int(r.views)) for r in g.sort_values("lq", ascending=False).head(5).itertuples()]
                             for s, g in pv[pv.views >= 5000].groupby("sname")}
json.dump(R, open(os.path.join(W, "world_results.json"), "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps(R["meta"], indent=1)); print(R["signature"]["by_sport"]); print(R["medals"]["spearman"], R["medals"]["pairs"])
