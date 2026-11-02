"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, world.json) is embedded; the two map images are in img/. Facts
stated in words are checked here. The full-screen map snippet (code/fullscreen_snippet.html) is pasted before
</body>. 10.5281/zenodo.23878612 and https://blog.tristanhotham.com/2026/10/31/mappa-mundi/ stay as placeholders for the publisher."""
import json
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
KEEP = {"DOI", "BLOG_URL", "DOI_URL"}
G, C, PC = R["regions"], R["classes"], R["part_class"]

# facts stated in words (page, blog, paper, collage)
assert PC["Asia"]["Biblical"] == C["Biblical"]["n"]                                   # Asia holds every Biblical name
assert PC["Africa"]["Classical_pct"] > 85 and PC["Europe"]["Classical_pct"] > 80        # "almost all classical", "mostly Roman"
assert R["britain"]["medieval_pct"] > 85                                               # "nine names in ten"
assert R["stretch_rank"][0] == "Holy Land" and R["stretch_rank"][-1] == "India and Central Asia"
assert G["British Isles"]["stretch"] > 1 and G["India and Central Asia"]["stretch"] < 1
assert G["British Isles"]["median_abs_brg_err"] <= 10                                  # "among the best on the map"
assert 90 < R["fit"]["up_bearing"] < 110                                                # "a little south of due east"
assert R["bearing"]["within45_pct"] > 75 and R["dist"]["spearman"] > .8
assert C["Classical"]["pct"] > 50 and C["Legendary"]["pct"] < C["Biblical"]["pct"] < C["Medieval"]["pct"]
assert R["britain"]["over_x"] >= 15


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{(?!DOI\}\}|BLOG_URL\}\}|DOI_URL\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    left = set(re.findall(r"\{\{([^}]*)\}\}", html))
    assert left <= KEEP, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
