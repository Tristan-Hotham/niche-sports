"""Step 5b. The "unexpected heartlands" cards and the UK paragraph. Facts about each sport are general knowledge
written by hand; every number is read from data/results.json, and each card is checked against the data.
Run: python3 code/05b_stories.py   (after 05_results.py)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
PD = json.load(open(os.path.join(ROOT, "work", "page_data.json")))
xf = lambda v: f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")
fmt = lambda v: f"{round(v):,}"


def top(s, iso):
    for r in R["top"][s]:
        if r["iso3"] == iso: return r
    raise KeyError((s, iso))


def rtop(s, region):
    for r in R["region_top"][s]:
        if r["region"] == region: return r
    raise KeyError((s, region))


def pv(s, lang):
    for r in R["pageviews"]["top"].get(s, []):
        if r["lang"] == lang: return r
    return None


def med(iso, s):
    return R["medals"]["by_pair"].get(f"{iso}|{s}")


S = []
t = top("pesäpallo", "FIN"); p = pv("pesäpallo", "fi")
S.append(dict(sport="pesäpallo", lq=t["lq"], title="Finland: pesäpallo",
              text=f"Finland's own fast, zig-zagging cousin of baseball. All {fmt(t['n'])} pesäpallo clubs in the data are Finnish, so Finland plays it {xf(t['lq'])} as much as the world, and Finnish Wikipedia reads about it {xf(p['lq'])} as much as the average language.",
              meta=f"{fmt(t['n'])} clubs · cautious {xf(t['lq_lo'])}", ll=[63.5, 26], z=4))
t = top("tchoukball", "CHE")
S.append(dict(sport="tchoukball", lq=t["lq"], title="Switzerland: tchoukball",
              text=f"A no-contact ball game, bounced off a small rebound frame, devised in Switzerland around 1970. Swiss clubs and teams make tchoukball {xf(t['lq'])} the world average there. Most have no Wikipedia article, so with that filter on, Switzerland's signature becomes {R['sigw']['CHE']['sport']}.",
              meta=f"{fmt(t['n'])} clubs and teams · cautious {xf(t['lq_lo'])}", ll=[46.8, 8.2], z=6))
t = top("hurling and camogie", "IRL"); r = rtop("hurling and camogie", "Tipperary")
S.append(dict(sport="hurling and camogie", lq=t["lq"], title="Ireland: hurling",
              text=f"The ancient stick-and-ball game of the Gaelic Athletic Association, with camogie, its women's form. Ireland has {fmt(t['n'])} hurling and camogie clubs in the data, {xf(t['lq'])} the world average. Inside Ireland, Tipperary leads at {xf(r['lq'])}.",
              meta=f"Ireland: cautious {xf(t['lq_lo'])}", ll=[53.2, -8], z=6, region=True))
t = top("speedway", "POL"); p = pv("speedway", "pl")
S.append(dict(sport="speedway", lq=t["lq"], title="Poland: speedway",
              text=f"Motorcycles without brakes, sliding round oval shale tracks. Poland's league fills stadiums, and its clubs make speedway {xf(t['lq'])} the world average there. Polish Wikipedia reads about speedway {xf(p['lq'])} as much as the average language.",
              meta=f"{fmt(t['n'])} clubs · cautious {xf(t['lq_lo'])}", ll=[52, 19], z=5))
t = top("korfball", "NLD"); p = pv("korfball", "nl")
S.append(dict(sport="korfball", lq=t["lq"], title="The Netherlands: korfball",
              text=f"A mixed team game first played in Amsterdam in 1902, with a basket on a tall pole and men and women on every side. The Netherlands has {fmt(t['n'])} korfball clubs in the data, {xf(t['lq'])} the world average; Belgium is second.",
              meta=f"cautious {xf(t['lq_lo'])} · Dutch Wikipedia {xf(p['lq'])}", ll=[52.2, 5.3], z=6))
t = top("bandy", "SWE"); p = pv("bandy", "sv")
S.append(dict(sport="bandy", lq=t["lq"], title="Sweden: bandy",
              text=f"Hockey with a ball on an ice rink the size of a football pitch. Sweden plays it {xf(t['lq'])} the world average, Russia and Finland next. Sweden's formal signature is minigolf, but those {fmt(R['caveat']['swe_minigolf'])} clubs look like a bulk import; bandy is the sturdier finding.",
              meta=f"{fmt(t['n'])} clubs · Swedish Wikipedia {xf(p['lq'])}", ll=[61, 15], z=4))
r = rtop("rowing", "Gipuzkoa"); t = top("rowing", "ESP")
S.append(dict(sport="rowing", lq=r["lq"], title="Basque Country: rowing",
              text=f"Rowing is Spain's signature ({xf(t['lq'])}), and it is a Cantabrian coast affair: Gipuzkoa ({xf(r['lq'])}), Cantabria and Biscay top the regions. These are the traineras, fishing-boat races between coastal towns.",
              meta=f"Gipuzkoa: {fmt(r['n'])} located clubs", ll=[43.2, -2.6], z=7, region=True))
t = top("water polo", "HUN"); m = med("HUN", "water polo")
S.append(dict(sport="water polo", lq=t["lq"], title="Hungary: water polo",
              text=f"Hungary has won more Olympic water polo medals than any other country. Its clubs play water polo {xf(t['lq'])} the world average, and its medal table share is {xf(m[1])} the world's. Counting only clubs with a Wikipedia article, water polo is Hungary's signature sport.",
              meta=f"{m[0]} Olympic medals · cautious {xf(t['lq_lo'])}", ll=[47.2, 19.4], z=6))
t = top("cycling", "COL"); m = med("COL", "cycling")
S.append(dict(sport="cycling", lq=t["lq"], title="Colombia: cycling",
              text=f"The climbers of the Andes. Colombia's clubs and teams make cycling {xf(t['lq'])} the world average, the highest anywhere, and its Olympic cycling medals are {xf(m[1])} its share of all medals.",
              meta=f"{fmt(t['n'])} clubs and teams · {m[0]} Olympic medals", ll=[4.5, -74], z=5))
t = top("boxing", "UGA")
S.append(dict(sport="boxing", lq=t["lq"], title="Uganda: boxing",
              text=f"The largest lead on the map: {fmt(t['n'])} Ugandan boxing clubs, {xf(t['lq'])} the world average. Most have no Wikipedia article and share near-identical descriptions, a sign of one focused recording effort, and few other countries list their boxing gyms at all. It says as much about who records what as about boxing.",
              meta=f"cautious {xf(t['lq_lo'])} · a recording effect as much as a sport effect", ll=[1.4, 32.4], z=6))
assert R["sig"]["FIN"]["sport"] == "pesäpallo" and R["sig"]["CHE"]["sport"] == "tchoukball" and R["sig"]["IRL"]["sport"] == "hurling and camogie"
assert R["sig"]["POL"]["sport"] == "speedway" and R["sig"]["NLD"]["sport"] == "korfball" and R["sig"]["SWE"]["sport"] == "minigolf"
assert R["sig"]["ESP"]["sport"] == "rowing" and R["sigw"]["HUN"]["sport"] == "water polo" and R["sig"]["UGA"]["sport"] == "boxing"
assert R["top"]["korfball"][1]["iso3"] == "BEL" and [x["iso3"] for x in R["top"]["bandy"][:3]] == ["SWE", "RUS", "FIN"]
assert R["region_top"]["rowing"][0]["region"] == "Gipuzkoa" and R["region_top"]["hurling and camogie"][0]["region"] == "Tipperary"
import pandas as pd
_md = pd.read_csv(os.path.join(ROOT, "data", "olympic_medals.csv")); _wp = _md[_md.sport == "water polo"].sort_values("medals")
assert _wp.iloc[-1].iso3 == "HUN"
assert R["top"]["cycling"][0]["iso3"] == "COL" and abs(R["sig"]["UGA"]["lq"] - max(x["lq"] for x in R["signature"]["list"])) < 0.01

# UK paragraph, from the OSM results
U = R["uk"]; T = U["top"]
def ut(s, i=0):
    return T[s][i] if s in T and len(T[s]) > i else None
parts = []
for s, desc in [("shinty", "Shinty, the Highland stick game"), ("real tennis", "Real tennis, the indoor ancestor of lawn tennis"),
                ("fives", "Fives, a handball game played in a walled court"), ("Gaelic games", "Gaelic games"), ("croquet", "Croquet"),
                ("lacrosse", "Lacrosse"), ("curling", "Curling"), ("polo", "Polo"), ("korfball", "Korfball"), ("stoolball", "Stoolball, an old Sussex bat-and-ball game"),
                ("skittles", "Skittles")]:
    a = ut(s)
    if a: parts.append(f"{desc}: {a['area']}, {xf(a['lq'])} the UK average ({fmt(a['n'])} places)")
ukt = ("<p>Some of the UK's leads are just what you would guess, and some are not. " + "; ".join(parts[:7]) + ".</p>") if parts else ""
sigs = [r for r in U["signature"] if r["sport"]]
if sigs:
    ukt += f"<p>The county or district with the biggest lead over the UK as a whole is {sigs[0]['area']}, for {sigs[0]['sport']} ({xf(sigs[0]['lq'])}). Click a chip above the map to light up every mapped place to play.</p>"
PD["stories"] = S; PD["uk"]["text"] = ukt
R["stories"] = S; R["uk_text"] = ukt
json.dump(PD, open(os.path.join(ROOT, "work", "page_data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(R, open(os.path.join(ROOT, "data", "results.json"), "w"), indent=1, ensure_ascii=False)
print(len(S), "stories;", ukt[:400])
