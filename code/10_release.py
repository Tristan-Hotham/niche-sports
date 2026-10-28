"""Step 10. Blog post (release/blog/post.html from code/blog_template.html), blog and Zenodo meta files, and the
Zenodo folder (paper, key CSVs, results.json and a code-and-data zip).
Image placeholders {{IMG|file|alt|caption}} are left for the uploader.
Run: python3 code/10_release.py
"""
import importlib.util, json, os, re, shutil, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "06_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
xf = lambda v: f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")
fmt = lambda v: f"{round(v):,}"
U = R["uk"]; T = U["top"]
sig = [r for r in U["signature"] if r["sport"]]
bits = []
for s, d in [("shinty", "shinty, the Highland stick game, peaks in"), ("real tennis", "real tennis, the indoor ancestor of lawn tennis, in"),
             ("fives", "fives, handball in a walled court, in"), ("croquet", "croquet in"), ("lacrosse", "lacrosse in"),
             ("curling", "curling in"), ("Gaelic games", "Gaelic games in"), ("stoolball", "stoolball, an old Sussex bat-and-ball game, in")]:
    if T.get(s): a = T[s][0]; bits.append(f"{d} {a['area']} ({xf(a['lq'])})")
UKP = ("<!-- wp:paragraph -->\n<p>Some county leads are what you would expect and some are not. The biggest is "
       f"{sig[0]['sport']} in {sig[0]['area']} ({xf(sig[0]['lq'])} the UK average), then {sig[1]['sport']} in {sig[1]['area']} ({xf(sig[1]['lq'])}). "
       "Among the small traditional games, " + "; ".join(bits) + ".</p>\n<!-- /wp:paragraph -->")
t = open(os.path.join(HERE, "blog_template.html")).read()
t = re.sub(r"\{\{(?!IMG\|)(?!UK_PARA)([^}|]+)(\|(\w+))?\}\}", b.sub, t).replace("{{UK_PARA}}", UKP)
assert "{{" not in t.replace("{{IMG|", "")
vis = re.sub(r"<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--"): assert bad not in vis, bad
L = R["signature"]["list"]
assert [r["iso3"] for r in L[:6]] == ["UGA", "CHE", "FIN", "IRL", "LKA", "PAK"], [r["iso3"] for r in L[:6]]
os.makedirs(os.path.join(ROOT, "release", "blog"), exist_ok=True)
open(os.path.join(ROOT, "release", "blog", "post.html"), "w").write(t)
for m in re.findall(r"\{\{IMG\|([^|]+)\|", t):
    assert os.path.exists(os.path.join(ROOT, "release", "blog", m)), m
meta = dict(
    title="Signature sports: where the world's niche games are unusually popular",
    slug="niche-sports",
    excerpt=(f"Every country plays football, but which sport does each country play far more than the world? From {fmt(R['meta']['clubs'])} clubs: "
             f"pesäpallo in Finland ({xf(R['sig']['FIN']['lq'])} the world average), tchoukball in Switzerland, hurling in Ireland, speedway in Poland."),
    seo_description="Each country coloured by the sport it over-indexes on most, from Wikidata sports clubs, with a pick-a-sport map and a UK county map.",
    tags=["sport", "maps", "Wikidata", "OpenStreetMap", "location quotient", "data visualisation", "Olympics", "data"],
    header_alt=("Title card reading 'Signature sports' on pale paper above a world map in which each country is coloured by its signature sport: "
                "hurling green in Ireland, pesäpallo blue in Finland, korfball orange in the Netherlands, handball red in north Africa and the Balkans, "
                "cricket green in South Asia, baseball red in the United States, with labels naming the sports."))
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
for v in meta.values():
    for bad in ("—", "–", "--"): assert bad not in str(v)
json.dump(meta, open(os.path.join(ROOT, "release", "blog", "meta.json"), "w"), indent=2, ensure_ascii=False)

NAME = "Hotham_Signature_Sports"
pt = open(os.path.join(ROOT, "release", "paper", NAME + ".tex")).read()
ab = pt.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("$\\rho$", "rho").replace("$\\times$", "x")
assert "\\" not in ab and "$" not in ab, ab
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
zmeta = dict(
    title="Signature Sports: Where the World's Niche Games Are Unusually Popular. Location Quotients of Sports Clubs in Wikidata and OpenStreetMap, by Country, Region and UK County",
    description_html=f"<p>{ab}</p><p>Interactive version: https://maps.tristanhotham.com/niche-sports/. Data and code: https://github.com/Tristan-Hotham/niche-sports. Blog post: to follow.</p>"
                     "<p>Text, figures and derived data: CC BY 4.0, except tables derived from OpenStreetMap (ODbL 1.0: uk_county_sport.csv, uk_signature.csv, uk_sites_niche.csv) "
                     "and from Wikipedia medal tables (CC BY-SA 4.0: olympic_medals.csv). Code: MIT. Wikidata and Wikimedia pageview data are CC0. "
                     "Boundaries: Natural Earth (public domain) and Office for National Statistics (Open Government Licence v3).</p>",
    keywords=["sport geography", "location quotient", "Wikidata", "OpenStreetMap", "sports clubs", "regional specialisation", "Olympic medals",
              "Wikipedia pageviews", "United Kingdom", "data visualisation"],
    licence="cc-by-4.0",
    related=[
        dict(identifier="https://github.com/Tristan-Hotham/niche-sports", relation="issupplementedby", resource_type="software"),
        dict(identifier="https://maps.tristanhotham.com/niche-sports/", relation="issupplementedby", resource_type="other"),
        dict(identifier="https://www.wikidata.org", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://qlever.cs.uni-freiburg.de", relation="isderivedfrom", resource_type="other"),
        dict(identifier="https://www.openstreetmap.org", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://en.wikipedia.org", relation="isderivedfrom", resource_type="other"),
        dict(identifier="https://wikimedia.org/api/rest_v1/", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://www.naturalearthdata.com", relation="isderivedfrom", resource_type="dataset"),
        dict(identifier="https://github.com/onsvisual/uk-topojson", relation="isderivedfrom", resource_type="dataset"),
    ])
json.dump(zmeta, open(os.path.join(Z, "meta.json"), "w"), indent=2, ensure_ascii=False)
rd = open(os.path.join(HERE, "readme_template.md")).read()
rd = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", b.sub, rd)
assert "{{" not in rd
for bad in ("\u2014", "\u2013", "--"): assert bad not in re.sub(r"(?m)^\|[-|]+\|$", "", rd), bad
open(os.path.join(ROOT, "README.md"), "w").write(rd)
shutil.copy(os.path.join(ROOT, "release", NAME + ".pdf"), Z)
for f in ["country_sport.csv", "signature_sports.csv", "signature_sports_wikipedia_only.csv", "region_sport.csv", "olympic_medals.csv",
          "pageviews_language.csv", "uk_county_sport.csv", "uk_signature.csv", "sports.csv", "results.json"]:
    shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, "niche-sports_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for sub in ("code", "data"):
        for f in sorted(os.listdir(os.path.join(ROOT, sub))):
            p = os.path.join(ROOT, sub, f)
            if os.path.isfile(p) and not f.endswith(".pyc"): zf.write(p, f"niche-sports/{sub}/{f}")
    for f in ("README.md", "LICENSE"): zf.write(os.path.join(ROOT, f), f"niche-sports/{f}")
words = len(re.sub(r"<[^>]+>", " ", re.sub(r"\{\{IMG\|.*?\}\}", "", t)).split())
print("release files written; post words:", words, "abstract words:", len(ab.split()))
