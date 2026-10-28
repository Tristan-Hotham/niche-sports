"""Step 8. header.png: 1200 x 630 social card (title and the signature sport map), drawn with matplotlib.
Run: python3 code/08_header.py   (after 05_results.py)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import figlib as F
import sportmap as SM
import matplotlib.pyplot as plt
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
PD = json.load(open(os.path.join(ROOT, "work", "page_data.json")))
GC = F.load("geo_countries.json")
col = lambda s: SM.COLOURS.get(s, SM.NEUTRAL)
xf = lambda v: f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")


def sc(c):
    S = R["sig"].get(c)
    if not S or S["status"] == "too few clubs": return F.FEW
    if S["status"] != "signature": return F.NODATA
    return F.mix(col(S["sport"]), F.ALPHA[F.cls(S["lq"])])


fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=F.BG)
ax = fig.add_axes([0.0, 0.0, 1, 0.74]); F.world_axes(ax, ylim=(-5.9e6, 8.4e6))
F.draw_countries(ax, GC, sc, lw=0.3)
for iso, short in [("FIN", "PESÄPALLO"), ("CHE", "TCHOUKBALL"), ("IRL", "HURLING"), ("POL", "SPEEDWAY"), ("NLD", "KORFBALL"), ("USA", "BASEBALL"),
                   ("IND", "CRICKET"), ("AUS", "AUSSIE RULES"), ("CAN", "CANADIAN FOOTBALL"), ("RUS", "BANDY"), ("BRA", "FUTSAL"), ("TUN", "HANDBALL"), ("COL", "CYCLING")]:
    S = R["sig"][iso]; lp = PD["C"][iso]["lp"]; x, y = F.pt(lp[1], lp[0])
    dx = {"NLD": -1.3e6, "CHE": -0.6e6, "IRL": -1.4e6, "POL": 1.1e6, "FIN": 0.9e6, "TUN": -0.3e6}.get(iso, 0)
    dy = {"NLD": 0.85e6, "CHE": -0.65e6, "IRL": 0.2e6, "POL": -0.1e6, "FIN": 0.6e6, "TUN": -0.6e6}.get(iso, 0)
    ax.text(x + dx, y + dy, short, ha="center", va="center", fontsize=7.6, family=F.MONO, weight="bold", color="white", zorder=6,
            bbox=dict(boxstyle="square,pad=0.22", fc=col(S["sport"]), ec="white", lw=0.5))
fig.text(0.04, 0.93, "Signature sports", fontproperties=F.DISP, fontsize=46, color=F.FG, va="top")
fig.text(0.04, 0.80, f"Each country coloured by the sport it plays most above the world average. {R['meta']['clubs']:,} clubs, Wikidata.",
         fontsize=13.5, family=F.SER, color=F.MUT, va="top")
fig.text(0.96, 0.93, "maps.tristanhotham.com", fontsize=11, family=F.MONO, color=F.MUT, ha="right", va="top")
fig.savefig(os.path.join(ROOT, "header.png"), facecolor=F.BG); plt.close(fig)
print("header written")
