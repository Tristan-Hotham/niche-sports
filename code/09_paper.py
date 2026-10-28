"""Step 9. Paper PDF: fill code/paper_template.tex from data/results.json, write release/paper/Hotham_Signature_Sports.tex
and compile it with xelatex (figures from step 7).
Run: python3 code/09_paper.py
"""
import json, os, re, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Signature_Sports"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct": return f"{v * 100:.0f}\\%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "x": return f"{round(v)}" + "$\\times$" if v >= 10 else f"{v:.1f}".rstrip("0").rstrip(".") + "$\\times$"
    return tex(str(v))


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


xf = lambda v: (f"{round(v)}" if v >= 10 else f"{v:.1f}".rstrip("0").rstrip(".")) + "$\\times$"
rows = "".join(f"{tex(r['name'])} & {tex(r['sport'])} & {r['n']:,.0f} & {xf(r['lq'])} & {xf(r['lq_lo'])}\\\\\n" for r in R["signature"]["list"][:16])
TL = ("\\begin{table}[tbp]\\centering\\small\\caption{The largest signature-sport leads: clubs of the sport in the country, plain location quotient "
      "and cautious ratio (lower 90\\% Poisson limit), in times the world average.}\\label{tab:lead}"
      "\\begin{tabular}{llrrr}\\toprule Country & Signature sport & Clubs & Quotient & Cautious\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
U = R["uk"]; T = U["top"]
sig = [r for r in U["signature"] if r["sport"]]
def ut(s):
    return T.get(s, [None])[0] if T.get(s) else None
bits = []
for s in ["shinty", "real tennis", "fives", "Gaelic games", "croquet", "lacrosse", "curling", "polo", "korfball", "stoolball", "skittles", "bowls"]:
    a = ut(s)
    if a: bits.append(f"{tex(s)} in {tex(a['area'])} ({xf(a['lq'])}, {a['n']:,} places)")
UKR = (f"In the United Kingdom {len(sig)} of {U['areas']} counties and districts have a sport they over-index on against the UK mix of places to play "
       f"(Figure \\ref{{fig:uk}}). The largest leads are {tex(sig[0]['sport'])} in {tex(sig[0]['area'])} ({xf(sig[0]['lq'])}), "
       f"{tex(sig[1]['sport'])} in {tex(sig[1]['area'])} ({xf(sig[1]['lq'])}) and {tex(sig[2]['sport'])} in {tex(sig[2]['area'])} ({xf(sig[2]['lq'])}). "
       "For the small traditional sports the top counties are: " + "; ".join(bits) + ".")
t = open(os.path.join(HERE, "paper_template.tex")).read()
t = re.sub(r"\{\{(?!TABLE_|UK_)(.+?)\}\}", sub, t).replace("{{TABLE_LEAD}}", TL).replace("{{UK_RESULTS}}", UKR)
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
# facts stated in words
S = R["sig"]
for c, s in [("TUN", "handball"), ("ROU", "handball"), ("SVN", "handball"), ("MKD", "handball"), ("BIH", "handball"), ("MNE", "handball"),
             ("TUR", "volleyball"), ("CYP", "volleyball"), ("BGR", "volleyball"), ("AZE", "volleyball"), ("KAZ", "volleyball"), ("LBN", "volleyball"),
             ("BRA", "futsal"), ("IRN", "futsal"), ("KOR", "futsal"), ("UKR", "futsal"), ("BLR", "futsal"), ("THA", "futsal"),
             ("COL", "cycling"), ("VEN", "cycling"), ("ECU", "cycling"), ("URY", "cycling"), ("CRI", "cycling"),
             ("USA", "baseball"), ("JPN", "baseball"), ("MEX", "baseball"), ("TWN", "baseball"), ("RUS", "bandy"), ("NOR", "athletics"),
             ("LKA", "cricket"), ("PAK", "cricket"), ("BGD", "cricket"), ("IND", "cricket")]:
    assert S[c]["sport"] == s, (c, S[c]["sport"], s)
assert R["signature"]["by_sport"]["handball"] == 6 and R["signature"]["by_sport"]["volleyball"] == 6 and R["signature"]["by_sport"]["futsal"] == 6
assert R["sigw"]["NOR"]["sport"] == "athletics" and R["sigw"]["NLD"]["sport"] == "korfball" and R["sigw"]["POL"]["sport"] == "speedway"
assert R["sigw"]["RUS"]["sport"] == "bandy" and R["sigw"]["FIN"]["sport"] == "pesäpallo" and R["sigw"]["IRL"]["sport"] == "hurling and camogie"
for c, s in [("SWE", "orienteering"), ("CHE", "gymnastics"), ("HUN", "water polo"), ("FRA", "rugby union"), ("NZL", "rugby league"), ("GBR", "cricket")]:
    assert R["sigw"][c]["sport"] == s, (c, R["sigw"][c])
assert all(r["lq"] < 2 for r in R["signature"]["list"] if r["sport"] == "football")
bh = {(r["iso3"], r["sport"]) for r in R["medals"]["both_high"]}
assert {("FIN", "wrestling"), ("CAN", "curling"), ("CAN", "ice hockey"), ("NOR", "skiing"), ("NOR", "speed skating"), ("HUN", "water polo"), ("COL", "cycling")} <= bh
assert [x["region"] for x in R["region_top"]["rowing"][:3]] == ["Gipuzkoa", "Cantabria", "Biscay"]
assert [x["region"] for x in R["region_top"]["hurling and camogie"][:3]] == ["Tipperary", "Galway", "Cork"]
assert [x["region"] for x in R["region_top"]["field hockey"][:2]] == ["North Brabant", "Utrecht"]
assert [x["iso3"] for x in R["top"]["handball"][:3]] == ["TUN", "MNE", "DNK"] and [x["iso3"] for x in R["top"]["field hockey"][:3]] == ["NLD", "IND", "ARG"]
assert [x["iso3"] for x in R["top"]["water polo"][:3]] == ["MLT", "HUN", "ITA"] and [x["iso3"] for x in R["top"]["futsal"][:3]] == ["KOR", "IRN", "UKR"]
assert [x["iso3"] for x in R["top"]["cricket"][:2]] == ["LKA", "PAK"]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
if r.returncode: print(r.stdout[-3000:])
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
shutil.copy(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
print("paper written", r.returncode)
