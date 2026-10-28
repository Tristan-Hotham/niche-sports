"""Step 7. Static figures for the paper (release/paper/fig_*.png) and blog (release/blog/b_*.png), drawn with
matplotlib from data/ (no web tiles). Light background, the page's sport colours.
Run: python3 code/07_figures.py
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import figlib as F
import sportmap as SM
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle

R = json.load(open(os.path.join(ROOT, "data", "results.json")))
PD = json.load(open(os.path.join(ROOT, "work", "page_data.json")))
GC = F.load("geo_countries.json"); GU = F.load("geo_uk.json")
BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
os.makedirs(BLOG, exist_ok=True); os.makedirs(PAP, exist_ok=True)
plt.rcParams.update({"font.family": F.SER, "text.color": F.FG, "axes.labelcolor": F.FG, "xtick.color": F.MUT, "ytick.color": F.MUT})
col = lambda s: SM.COLOURS.get(s, SM.NEUTRAL)
xf = lambda v: f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")


def sig_colour(c, var="all"):
    S = (R["sig"] if var == "all" else R["sigw"]).get(c)
    if not S: return F.FEW
    if S["status"] == "too few clubs": return F.FEW
    if S["status"] != "signature": return F.NODATA
    return F.mix(col(S["sport"]), F.ALPHA[F.cls(S["lq"])])


def signature_map(path, w=15.2, h=8.6, labels=True, dpi=100, legend=True):
    fig = plt.figure(figsize=(w, h), dpi=dpi, facecolor=F.BG)
    ax = fig.add_axes([0, 0.12 if legend else 0, 1, 0.88 if legend else 1]); F.world_axes(ax)
    F.draw_countries(ax, GC, lambda c: sig_colour(c))
    if labels:
        done = []
        L = sorted([r for r in R["signature"]["list"]], key=lambda r: -np.log(R["countries"][r["iso3"]]["clubs"]) * (1 + np.log(r["lq"])))
        for r in L:
            lp = PD["C"].get(r["iso3"], {}).get("lp")
            if not lp: continue
            x, y = F.pt(lp[1], lp[0])
            wbox = max(len(r["sport"]) * 1.9e5 + 3e5, 1.2e6); hb = 7.5e5
            if any(abs(x - a) < (wbox + b) / 2 and abs(y - c) < hb for a, c, b in done): continue
            if r["lq"] < 3 and R["countries"][r["iso3"]]["clubs"] < 1000: continue
            done.append((x, y, wbox))
            ax.text(x, y, r["sport"].upper().replace("HURLING AND CAMOGIE", "HURLING").replace("AUSTRALIAN RULES FOOTBALL", "AUSSIE RULES"),
                    ha="center", va="center", fontsize=8.6, family=F.MONO, weight="bold", color="white", zorder=6,
                    bbox=dict(boxstyle="square,pad=0.25", fc=col(r["sport"]), ec="white", lw=0.6))
    if legend:
        lg = fig.add_axes([0.03, 0.0, 0.94, 0.12]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
        cnt = R["signature"]["by_sport"]; items = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:15]
        SH = {"Australian rules football": "Aussie rules", "hurling and camogie": "hurling", "Canadian football": "Canadian football"}
        for i, (s, n) in enumerate(items):
            s0 = s; s = SH.get(s, s)
            cx = (i % 5) / 5; cy = 0.78 - (i // 5) * 0.3
            lg.add_patch(Rectangle((cx, cy - 0.09), 0.018, 0.18, fc=col(s0), ec="none"))
            lg.text(cx + 0.026, cy, f"{s} ({n})", va="center", fontsize=11, family=F.MONO, color=F.FG)
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


def lead_chart(path):
    rows = R["signature"]["list"][:20]
    fig, ax = plt.subplots(figsize=(15.2, 9.6), dpi=100, facecolor=F.BG); ax.set_facecolor(F.BG)
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [np.log10(r["lq"]) for r in rows], color=[col(r["sport"]) for r in rows], height=0.72)
    for yi, r in zip(y, rows):
        ax.text(-0.02, yi, r["name"], ha="right", va="center", fontsize=14, family=F.MONO)
        ax.text(np.log10(r["lq"]) + 0.02, yi, f"{r['sport']}  {xf(r['lq'])}", va="center", fontsize=13, family=F.MONO, weight="bold")
    ticks = [1, 2, 5, 10, 20, 50, 100]
    ax.set_xticks(np.log10(ticks)); ax.set_xticklabels([f"{t}x" for t in ticks], fontsize=12, family=F.MONO)
    ax.set_yticks([]); ax.set_xlim(0, np.log10(max(r["lq"] for r in rows)) + 0.55)
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis="x", color=F.RULE); ax.set_axisbelow(True)
    ax.set_xlabel("Times the world average share of clubs (log scale)", fontsize=13, family=F.MONO, color=F.MUT)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.98, bottom=0.08)
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


def sport_multiples(path, sports, ncol=3):
    nrow = int(np.ceil(len(sports) / ncol))
    fig = plt.figure(figsize=(15.2, 3.1 * nrow), dpi=100, facecolor=F.BG)
    cs = pd.read_csv(os.path.join(ROOT, "data", "country_sport.csv"))
    for i, s in enumerate(sports):
        ax = fig.add_axes([(i % ncol) / ncol + 0.005, 1 - (i // ncol + 1) / nrow + 0.01, 1 / ncol - 0.01, 1 / nrow - 0.03]); F.world_axes(ax, ylim=(-5.6e6, 9.6e6))
        g = cs[cs.sname == s].set_index("iso3")
        def cf(c):
            if c not in g.index: return F.FEW if R["countries"].get(c, {}).get("clubs", 0) < 100 else F.NODATA
            r = g.loc[c]
            if not r.eligible: return F.NODATA
            if r.lq < 1: return F.mix(col(s), 0.08)
            return F.mix(col(s), F.ALPHA[F.cls(r.lq)])
        F.draw_countries(ax, GC, cf, lw=0.2)
        t = R["top"].get(s, [])
        ax.text(0.02, 1.0, s.replace("hurling and camogie", "hurling"), transform=ax.transAxes, fontsize=16, fontproperties=F.DISP, color=col(s), va="top")
        if t: ax.text(0.02, 0.86, f"{t[0]['name']} {xf(t[0]['lq'])}" + (f", {t[1]['name']} {xf(t[1]['lq'])}" if len(t) > 1 else ""),
                      transform=ax.transAxes, fontsize=10.5, family=F.MONO, color=F.FG, va="top")
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


def uk_map(path, w=15.2, h=13):
    fig = plt.figure(figsize=(w, h), dpi=100, facecolor=F.BG)
    ax = fig.add_axes([0, 0, 0.55, 1]); ax.axis("off"); ax.set_aspect(1.65)
    A = PD["uk"]["A"]
    for f in GU["features"]:
        a = f["properties"]["area"]; g = A.get(a, {}).get("g")
        fc = F.mix(col(g[0]), F.ALPHA[F.cls(g[2])]) if g else F.NODATA
        ax.add_patch(PathPatch(F.proj_path(f["geometry"], tr=None), fc=fc, ec="white", lw=0.5))
    ax.set_xlim(-8.3, 2.0); ax.set_ylim(49.85, 60.9)
    rows = [r for r in R["uk"]["signature"] if r["sport"]][:16]
    lg = fig.add_axes([0.56, 0.06, 0.42, 0.9]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, len(rows) + 1)
    lg.text(0, len(rows) + 0.5, "Biggest county leads", fontsize=17, fontproperties=F.DISP, va="center")
    for i, r in enumerate(rows):
        yy = len(rows) - i - 0.3
        lg.add_patch(Rectangle((0, yy - 0.3), 0.04, 0.6, fc=col(r["sport"])))
        an = r["area"] if len(r["area"]) <= 26 else r["area"][:24].rstrip(" ,") + "..."
        lg.text(0.06, yy, an, fontsize=12, family=F.MONO, va="center")
        lg.text(1, yy, f"{r['sport']} {xf(r['lq'])}", fontsize=12, family=F.MONO, va="center", ha="right", weight="bold", color=col(r["sport"]))
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


def medal_scatter(path):
    P = PD["medPairs"]
    fig, ax = plt.subplots(figsize=(15.2, 9.5), dpi=100, facecolor=F.BG); ax.set_facecolor(F.BG)
    for p in P:
        ax.scatter(max(p[3], .09), max(p[2], .03), s=60, color=col(p[1]), alpha=.85, edgecolor="white", lw=.7, zorder=3)
        if p[5]:
            off = {"Norway skiing": (-8, -16), "Hungary water polo": (-10, 12), "Colombia cycling": (6, -14), "Canada curling": (6, 6), "Sweden curling": (-10, 10)}.get(f"{p[0]} {p[1]}", (6, 4))
            ax.annotate(f"{p[0]} {p[1]}", (max(p[3], .09), max(p[2], .03)), xytext=off, textcoords="offset points", fontsize=11, family=F.MONO,
                        ha="right" if off[0] < 0 else "left")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.08, 150)
    ax.axvline(1, color=F.MUT, ls=":", lw=1); ax.axhline(1, color=F.MUT, ls=":", lw=1)
    ax.set_xlabel("Clubs: times the world average", fontsize=13, family=F.MONO); ax.set_ylabel("Olympic medals: times the world average", fontsize=13, family=F.MONO)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(color=F.RULE, lw=.6); ax.set_axisbelow(True)
    ax.tick_params(labelsize=12)
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}x")); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}x"))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.1)
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


def wp_compare(path):
    fig = plt.figure(figsize=(15.2, 4.8), dpi=100, facecolor=F.BG)
    for k, var in enumerate(("all", "wp")):
        ax = fig.add_axes([k * 0.5, 0.02, 0.5, 0.86]); F.world_axes(ax, ylim=(-5.6e6, 8.4e6))
        F.draw_countries(ax, GC, lambda c: sig_colour(c, var), lw=0.2)
        ax.text(0.03, 1.07, "All clubs in Wikidata" if var == "all" else "Only clubs with a Wikipedia article", transform=ax.transAxes, fontsize=15,
                fontproperties=F.DISP, va="top")
    fig.savefig(path, facecolor=F.BG); plt.close(fig)


if __name__ == "__main__":
    signature_map(os.path.join(BLOG, "b_signature_map.png"))
    lead_chart(os.path.join(BLOG, "b_leads.png"))
    MULT = ["handball", "bandy", "field hockey", "cricket", "water polo", "futsal"]
    sport_multiples(os.path.join(BLOG, "b_six_sports.png"), MULT)
    uk_map(os.path.join(BLOG, "b_uk_counties.png"))
    medal_scatter(os.path.join(BLOG, "b_medals.png"))
    wp_compare(os.path.join(BLOG, "b_wikipedia_check.png"))
    import shutil
    for a, b in [("b_signature_map", "fig_signature_map"), ("b_leads", "fig_leads"), ("b_six_sports", "fig_six_sports"), ("b_uk_counties", "fig_uk_counties"),
                 ("b_medals", "fig_medals"), ("b_wikipedia_check", "fig_wikipedia_check")]:
        shutil.copy(os.path.join(BLOG, a + ".png"), os.path.join(PAP, b + ".png"))
    print("figures written")
