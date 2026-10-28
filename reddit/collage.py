"""r/dataisbeautiful collage: reddit/signature_sports.png (2400 x 3000), light paper with one bold colour per sport.
Hero: the signature sport map. Below: four big numbers and six "unexpected heartland" cards, each with a small locator map.
Every number comes from ../data/results.json; outlines from ../data/geo_*.json.
Fonts: FONT_DIR (Fraunces, Source Serif 4, IBM Plex Mono).
Run: python3 reddit/collage.py
"""
import json, os, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "code"))
import figlib as F
import sportmap as SM
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
PD = json.load(open(os.path.join(ROOT, "work", "page_data.json")))
GC = F.load("geo_countries.json"); GR = F.load("geo_regions.json"); GU = F.load("geo_uk.json")
BG, FG, MUT = "#F7F5F0", F.FG, F.MUT
col = lambda s: SM.COLOURS.get(s, SM.NEUTRAL)
xf = lambda v: f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")
DISP, SER, MONO = F.DISP, F.SER, F.MONO


def sc(c):
    S = R["sig"].get(c)
    if not S or S["status"] == "too few clubs": return "#ECE9E2"
    if S["status"] != "signature": return "#D6D1C8"
    return F.mix(col(S["sport"]), F.ALPHA[F.cls(S["lq"])], bg=BG)


fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
# title
fig.text(0.045, 0.978, "Every country's", fontproperties=DISP, fontsize=52, color=FG, va="top")
rend = fig.canvas.get_renderer(); x = 0.045
for word, c in (("signature ", "#E0362C"), ("sport", "#1F6FD6")):
    t = fig.text(x, 0.928, word, fontproperties=DISP, fontsize=52, color=c, va="top")
    x += t.get_window_extent(rend).width / fig.bbox.width
fig.text(0.045, 0.872, f"Not the sport each country plays most (that is football almost everywhere) but the one it plays most\n"
         f"above the world average: its share of the country's clubs over its share of all {R['meta']['clubs']:,} clubs in Wikidata.\n"
         f"Deeper colour, bigger lead. A sport needs {R['thr']['cell']} clubs in a country to count.",
         family=SER, fontsize=14.5, color=FG, va="top", linespacing=1.2)

# hero map
ax = fig.add_axes([0.0, 0.47, 1.0, 0.33]); F.world_axes(ax, ylim=(-5.8e6, 8.3e6), xlim=(-1.45e7, 1.72e7))
F.draw_countries(ax, GC, sc, edge=BG, lw=0.45)
LAB = [("FIN", "PESÄPALLO", 1.9e6, 1.1e6), ("SWE", "MINIGOLF*", -1.7e6, 1.6e6), ("RUS", "BANDY", 0, 0), ("CHE", "TCHOUKBALL", 1.0e6, -2.7e6),
       ("IRL", "HURLING", -2.4e6, 0.5e6), ("GBR", "SHOOTING*", -3.0e6, -0.5e6), ("POL", "SPEEDWAY", 1.9e6, 0.25e6), ("NLD", "KORFBALL", -2.9e6, -1.0e6),
       ("ESP", "ROWING", -2.4e6, -1.3e6), ("USA", "BASEBALL", 0, 0), ("CAN", "CANADIAN FOOTBALL", 0, 0), ("BRA", "FUTSAL", 0, 0), ("IND", "CRICKET", 0, 0),
       ("AUS", "AUSSIE RULES", 0, 0), ("TUN", "HANDBALL", -1.5e6, -2.0e6), ("TUR", "VOLLEYBALL", 0.8e6, -1.2e6), ("COL", "CYCLING", -0.6e6, 0),
       ("ARG", "RUGBY UNION", 0, 0), ("JPN", "BASEBALL", 1.0e6, 0.4e6), ("NZL", "NETBALL", -1.6e6, 0.7e6), ("KAZ", "VOLLEYBALL", 0, 0),
       ("UGA", "BOXING", 1.0e6, -0.4e6), ("ZAF", "CRICKET", 0, 0)]
for iso, txt, dx, dy in LAB:
    if not txt: continue
    S = R["sig"][iso]
    if S["status"] != "signature": continue
    lp = PD["C"][iso]["lp"]; px, py = F.pt(lp[1], lp[0])
    if dx or dy: ax.plot([px, px + dx * 0.85], [py, py + dy * 0.85], color=FG, lw=0.6, zorder=5)
    ax.text(px + dx, py + dy, txt, ha="center", va="center", fontsize=8.8, family=MONO, weight="bold", color="white", zorder=6,
            bbox=dict(boxstyle="square,pad=0.25", fc=col(S["sport"]), ec="white", lw=0.7))
# strength key
kx = fig.add_axes([0.045, 0.462, 0.42, 0.03]); kx.axis("off"); kx.set_xlim(0, 7.6); kx.set_ylim(0, 1)
for i, (a, t) in enumerate(zip(F.ALPHA[1:], ["1.5x", "2x", "4x", "8x", "16x+"])):
    kx.add_patch(Rectangle((i, 0.45), 0.94, 0.5, fc=F.mix(FG, a, bg=BG), ec="none")); kx.text(i + 0.47, 0.02, t, ha="center", fontsize=9.5, family=MONO, color=MUT)
kx.text(5.25, 0.68, "times the world average", fontsize=10, family=MONO, color=MUT, va="center")
fig.text(0.56, 0.478, "Mid grey: no sport stands out.  Pale: under 100 clubs.", fontsize=10, family=MONO, color=MUT, va="center")

# big numbers
nums = [("FIN", "pesäpallo", "Finland plays pesäpallo, its own\nfast cousin of baseball. Every\npesäpallo club in the data is Finnish."),
        ("CHE", "tchoukball", "Switzerland's tchoukball, a no-\ncontact game played off a rebound\nframe, devised there around 1970."),
        ("IRL", "hurling and camogie", "Ireland's hurling and camogie,\nthe ancient Gaelic stick game.\nTipperary leads within Ireland."),
        ("POL", "speedway", "Poland's speedway: motorbikes\nwith no brakes on shale ovals.\nPolish Wikipedia: {pv}.")]
for k, (iso, s, txt) in enumerate(nums):
    xx = 0.045 + k * 0.237; S = R["sig"][iso]
    fig.text(xx, 0.437, xf(S["lq"]), fontproperties=DISP, fontsize=46, color=col(s), va="top")
    pv = R["pageviews"]["top"]["speedway"][0]["lq"]
    fig.text(xx, 0.385, txt.format(pv=xf(pv) + " the average"), family=SER, fontsize=11.6, color=FG, va="top", linespacing=1.18)

# unexpected heartlands cards
fig.text(0.045, 0.326, "UNEXPECTED HEARTLANDS: ZOOM IN AND THE LEADS GET SHARPER", family=MONO, fontsize=11.5, color=MUT, va="top", weight="medium")
geo_c = {f["properties"]["iso3"]: f for f in GC["features"]}
geo_r = {f["properties"]["code"]: f for f in GR["features"]}
rt = lambda s, i=0: R["region_top"][s][i]
cards = []
r = rt("rowing"); cards.append(dict(s="rowing", big=xf(r["lq"]), head="Rowing, Gipuzkoa", txt="Basque trainera crews: Spain's\nsignature sport is a coastal one.",
                                    iso="ESP", code=r["code"], box=(-9.8, 35.5, 4.5, 44.2)))
r = rt("roller hockey"); cards.append(dict(s="roller hockey", big=xf(r["lq"]), head="Roller hockey, Barcelona", txt="Rink hockey on quad skates;\nPortugal leads among countries.",
                                           iso="ESP", code=r["code"], box=(-9.8, 35.5, 4.5, 44.2)))
r = rt("hurling and camogie"); cards.append(dict(s="hurling and camogie", big=xf(r["lq"]), head="Hurling, Tipperary", txt="Galway and Cork next.\nIreland overall: " + xf(R["sig"]["IRL"]["lq"]) + ".",
                                                 iso="IRL", code=r["code"], box=(-10.7, 51.3, -5.8, 55.5)))
t = R["top"]["water polo"]; m = R["medals"]["by_pair"]["HUN|water polo"]
cards.append(dict(s="water polo", big=xf(t[1]["lq"]), head="Water polo, Hungary", txt=f"Most Olympic water polo medals\nof any country ({m[0]}). Malta {xf(t[0]['lq'])}.",
                  iso="HUN", code=None, box=(12, 43.5, 26.5, 50.5)))
t = R["top"]["cycling"][0]; cards.append(dict(s="cycling", big=xf(t["lq"]), head="Cycling, Colombia", txt="The Andes' climbers: the biggest\ncycling lead of any country.",
                                              iso="COL", code=None, box=(-82, -5, -66, 13.5)))
UT = R["uk"]["top"]
uk_s = next(s for s in ["shinty", "real tennis", "fives", "curling", "croquet"] if UT.get(s))
u = UT[uk_s][0]
cards.append(dict(s=uk_s, big=xf(u["lq"]), head=f"{uk_s.capitalize()}, {u['area']}", txt=f"{u['n']} of the UK's {R['uk']['sport_sites'][uk_s]} mapped {uk_s}\nplaces are here (OpenStreetMap).", uk=u["area"]))
for k, c in enumerate(cards):
    cx = 0.045 + (k % 3) * 0.31; cy = 0.302 - (k // 3) * 0.110
    fig.patches.append(FancyBboxPatch((cx, cy - 0.102), 0.29, 0.098, boxstyle="square,pad=0", transform=fig.transFigure, fc="white", ec="#DDD7CC", lw=0.8))
    fig.patches.append(Rectangle((cx, cy - 0.006), 0.29, 0.006, transform=fig.transFigure, fc=col(c["s"]), ec="none"))
    fig.text(cx + 0.012, cy - 0.014, c["big"], fontproperties=DISP, fontsize=30, color=col(c["s"]), va="top")
    fig.text(cx + 0.012, cy - 0.054, c["head"], family=MONO, fontsize=10.5, weight="bold", color=FG, va="top")
    fig.text(cx + 0.012, cy - 0.072, c["txt"], family=SER, fontsize=10.8, color=FG, va="top", linespacing=1.15)
    a = fig.add_axes([cx + 0.185, cy - 0.098, 0.1, 0.088]); a.axis("off")
    if c.get("uk"):
        for f in GU["features"]:
            fc = col(c["s"]) if f["properties"]["area"] == c["uk"] else "#E4DFD6"
            a.add_patch(PathPatch(F.proj_path(f["geometry"], tr=None), fc=fc, ec="white", lw=0.3))
        a.set_xlim(-8.3, 2); a.set_ylim(49.9, 60.9); a.set_aspect(1.7)
    else:
        x0, y0, x1, y1 = c["box"]
        for f in GC["features"]:
            fc = "#CFC9BF" if f["properties"]["iso3"] == c["iso"] else "#ECE8E1"
            if not c["code"] and f["properties"]["iso3"] == c["iso"]: fc = col(c["s"])
            a.add_patch(PathPatch(F.proj_path(f["geometry"], tr=None), fc=fc, ec="white", lw=0.3))
        if c["code"]:
            a.add_patch(PathPatch(F.proj_path(geo_r[c["code"]]["geometry"], tr=None), fc=col(c["s"]), ec="white", lw=0.3))
        a.set_xlim(x0, x1); a.set_ylim(y0, y1); a.set_aspect(1 / np.cos(np.radians((y0 + y1) / 2)))

fig.text(0.045, 0.084, f"Clubs: Wikidata sports clubs and teams (CC0), via QLever, {R['meta']['retrieved']}; national sides, delegations, seasons and\n"
         f"school teams removed. Ranked by a cautious ratio (lower 90% Poisson limit). *Likely bulk imports: Sweden's {R['caveat']['swe_minigolf']:.0f}\n"
         f"minigolf and the UK's {R['caveat']['uk_shooting']:.0f} target shooting clubs; bandy ({xf(R['top']['bandy'][0]['lq'])}) is the sturdier Swedish heartland. With only clubs that\n"
         f"have a Wikipedia article, {R['wp']['same_sig']} of {R['wp']['both']} countries keep the same signature (the UK's becomes cricket). Medals: English Wikipedia.\n"
         "UK: OpenStreetMap contributors (ODbL). Outlines: Natural Earth, ONS.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib.   maps.tristanhotham.com/niche-sports",
         family=MONO, fontsize=9.2, color=MUT, va="top", linespacing=1.22)
fig.savefig(os.path.join(HERE, "signature_sports.png"), dpi=200, facecolor=BG)
print("collage written")
