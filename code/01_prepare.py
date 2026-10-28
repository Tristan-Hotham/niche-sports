"""Step 1. Read the Wikidata bundle (sports clubs and teams) and write a clean item table.

Input: DATA/ns_world_wikidata.json.gz (gathered in a browser from the QLever Wikidata endpoint, CC0).
Output: work/items.csv (one row per club and sport, with fractional weight), work/sports.csv, work/countries.csv,
        work/excluded_classes.csv (classes that remove an item: national sides, delegations, seasons and so on).
Run: python3 code/01_prepare.py
"""
import gzip, json, os, re, collections
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
DATA = os.environ.get("NS_DATA", "/home/claude/hist/_data18/niche-sports")
W = os.path.join(ROOT, "work"); os.makedirs(W, exist_ok=True)
B = json.load(gzip.open(os.path.join(DATA, "ns_world_wikidata.json.gz")))


def tsv(text):
    rows = []
    for l in text.split("\n")[1:]:
        f = l.split("\t")
        if len(f) < 2: continue
        rows.append([re.sub(r'^"|"(@[a-z-]+)?$', "", x.strip("<>")) for x in f])
    return rows

# class labels and the classes that mark an item as something other than a club or club team
cl = {r[0]: (r[1], int(r[2])) for r in tsv(B["clslab"])}
BAD = re.compile(r"national|delegation|season|nation at| at the |world cup|uefa euro|olympic|paralympic|davis cup|fed cup|billie jean|"
                 r"golf course|reserve team|under-\d+|junior|youth|tag team|stable|esports|wikimedia|regional team|clan\b|"
                 r"college|ncaa|high school|university|school|all-star|selection|representative|cheerleading|"
                 r"formula one|racing team|rallying|auto racing|motorcycle|team season|secondary national|second national", re.I)
bad_cls = {q for q, (lab, n) in cl.items() if BAD.search(lab or "")}
pd.DataFrame([(q, cl[q][0], cl[q][1]) for q in sorted(bad_cls, key=lambda q: -cl[q][1])], columns=["class", "label", "items"]).to_csv(
    os.path.join(W, "excluded_classes.csv"), index=False)
item_cls = collections.defaultdict(set)
for r in tsv(B["cls"]): item_cls[r[0]].add(r[1])

sports = {r[0]: dict(label=r[1], n_raw=int(r[2]), enwiki=(r[3] if len(r) > 3 else "")) for r in tsv(B["sports"])}
countries = {}
for r in tsv(B["countries"]):
    countries[r[0]] = dict(label=r[1], iso3=r[2], iso2=r[3], n_raw=int(r[4]))

rows = []
seen = set()
for it, sp, c, co, hq in B["items"]:
    if c is None: continue
    key = (it, sp, c)
    if key in seen: continue
    seen.add(key)
    pt = co or hq
    rows.append(dict(item=it, sport=sp, country=c, lon=pt[0] if pt else None, lat=pt[1] if pt else None,
                     coord_src="P625" if co else ("P159" if hq else ""), excluded=bool(item_cls[it] & bad_cls)))
df = pd.DataFrame(rows)
print("rows", len(df), "items", df.item.nunique(), "excluded items", df[df.excluded].item.nunique())
df.to_csv(os.path.join(W, "items_raw.csv"), index=False)
pd.DataFrame([dict(sport=k, **v) for k, v in sports.items()]).to_csv(os.path.join(W, "sports_raw.csv"), index=False)
pd.DataFrame([dict(country=k, **v) for k, v in countries.items()]).to_csv(os.path.join(W, "countries_raw.csv"), index=False)
