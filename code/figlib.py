"""Shared drawing helpers for the static figures, header and collage: Robinson projection of the page outlines,
fonts and the sport palette."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
HAVE_FONTS = os.path.exists(os.path.join(FD, "FrauncesVar.ttf"))
if HAVE_FONTS:
    for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf"]:
        fm.fontManager.addfont(os.path.join(FD, f))
    DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
    SER, MONO = "Source Serif 4", "IBM Plex Mono"
else:
    DISP = fm.FontProperties(family="DejaVu Serif", weight="bold"); SER, MONO = "DejaVu Serif", "DejaVu Sans Mono"
BG, FG, MUT, RULE = "#F6F4EF", "#1D1B22", "#66616E", "#DCD6CB"
NODATA, FEW = "#D9D4CB", "#ECE9E3"
BR = [1.5, 2, 4, 8, 16]; ALPHA = [.16, .34, .52, .7, .86, .97]
TR = Transformer.from_crs("EPSG:4326", "+proj=robin +lon_0=0 +datum=WGS84", always_xy=True)


def cls(v):
    k = 0
    while k < len(BR) and v >= BR[k]: k += 1
    return k


def mix(hexc, a, bg=BG):
    c = np.array(matplotlib.colors.to_rgb(hexc)); b = np.array(matplotlib.colors.to_rgb(bg))
    return tuple(b + (c - b) * a)


def rings(geom):
    t = geom["type"]; cs = geom["coordinates"]
    polys = [cs] if t == "Polygon" else cs
    return polys


def proj_path(geom, tr=TR, lonwrap=None):
    verts, codes = [], []
    for poly in rings(geom):
        for ring in poly:
            a = np.array(ring, float)
            if lonwrap is not None: a[:, 0] = np.where(a[:, 0] < lonwrap, a[:, 0] + 360, a[:, 0])
            x, y = tr.transform(a[:, 0], a[:, 1]) if tr else (a[:, 0], a[:, 1])
            verts += list(zip(x, y)); codes += [Path.MOVETO] + [Path.LINETO] * (len(a) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes)


def load(name):
    return json.load(open(os.path.join(ROOT, "data", name)))


def world_axes(ax, ylim=(-6.0e6, 8.4e6), xlim=(-1.45e7, 1.70e7)):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect(1); ax.axis("off")


def draw_countries(ax, gc, colour_of, edge="#FFFFFF", lw=0.35, z=2):
    for f in gc["features"]:
        if f["properties"]["iso3"] == "ATA": continue
        fc = colour_of(f["properties"]["iso3"])
        ax.add_patch(PathPatch(proj_path(f["geometry"]), facecolor=fc, edgecolor=edge, lw=lw, zorder=z))


def pt(lon, lat, tr=TR):
    return tr.transform(lon, lat)
