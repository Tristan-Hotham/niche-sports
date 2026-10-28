"""Step 6. Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token
filled from data/results.json; the page tables (work/page_data.json) are embedded; outlines load from data/.
Run: python3 code/06_build_site.py
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
PD = json.load(open(os.path.join(ROOT, "work", "page_data.json"), encoding="utf-8"))


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "x": return f"{round(v)}x" if v >= 10 else f"{v:.1f}x".replace(".0x", "x")
    raise ValueError(f)


def sub(m):
    return fmt(get(m.group(1)), m.group(3))


# facts stated in words in the template
S = R["sig"]
for c, s in [("FIN", "pesäpallo"), ("CHE", "tchoukball"), ("IRL", "hurling and camogie"), ("POL", "speedway"), ("SWE", "minigolf"), ("GBR", "shooting")]:
    assert S[c]["sport"] == s, (c, S[c]["sport"])
assert R["wp"]["by_sport"].get("football", 0) >= 1 and R["sigw"]["GBR"]["sport"] == "cricket"

if __name__ == "__main__":
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", sub, tpl)
    html = html.replace("/*RESULTS*/", json.dumps({"meta": R["meta"]}, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*PD*/", json.dumps(PD, ensure_ascii=False, separators=(",", ":")))
    assert "{{" not in html
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        scr2 = re.sub(r"var\(--[\w-]+|css\(\"--[\w-]+\"\)|--c:|--[a-z]+\b", "", scr)
        for bad in ("—", "–"):
            assert bad not in scr2, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()), "bytes")
