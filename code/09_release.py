"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23878612, https://doi.org/10.5281/zenodo.23878612 and https://blog.tristanhotham.com/2026/10/31/mappa-mundi/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Mappa_Mundi"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
G, PC = R["regions"], R["part_class"]

# numbers written in words or alt text in the blog and collage
assert [PC[p]["n"] for p in ("Asia", "Europe", "Africa", "Seas and islands", "British Isles")] == [360, 321, 114, 105, 83]
assert 4.2 < G["Holy Land"]["stretch"] < 4.8 and 1.75 < G["Egypt and Sinai"]["stretch"] < 2                        # "about four and a half", "nearly twice"
assert all(1.35 < G[k]["stretch"] < 1.7 for k in ("Mesopotamia and Persia", "Syria and Anatolia", "British Isles"))   # "about one and a half"
assert all(1 < G[k]["stretch"] < 1.45 for k in ("Italy", "Greece and Constantinople", "France", "North Africa"))     # "a little above average"
assert .85 < G["Spain"]["stretch"] < 1 and .65 < G["India and Central Asia"]["stretch"] < .75
assert G["British Isles"]["median_disp_km"] < G["North Africa"]["median_disp_km"] < G["India and Central Asia"]["median_disp_km"]   # arrows short in Britain, long in India

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "The world according to the Hereford Mappa Mundi",
        "slug": "mappa-mundi",
        "excerpt": f"I set the largest surviving medieval map of the world beside a modern one. Its directions from Jerusalem are mostly right; its scale is not: the Holy Land is drawn {G['Holy Land']['stretch']:.1f} times too big, and Britain has {R['britain']['names_pct']:.0f}% of its names.",
        "seo_description": f"The Hereford Mappa Mundi (c. 1300) beside a modern map: {R['source']['n']:,} names, where it puts real places, and what is Biblical, classical or legend.",
        "tags": ["maps", "history", "medieval", "Hereford", "mappa mundi", "data visualisation", "cartography", "Jerusalem"],
        "header_alt": "Title card reading 'Mappa Mundi' in black and red on pale parchment, beside Konrad Miller's facsimile of the Hereford map dotted with coloured markers, and a small modern map of Europe, Africa and Asia with the same places. Text: 1,025 names, Jerusalem at the centre, east at the top."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/mappa-mundi_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "img"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"mappa-mundi/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"mappa-mundi/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "mappa-mundi/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
zmeta = {"title": "The World According to the Hereford Mappa Mundi: A Medieval Map of the World Set Against a Modern One",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p><p>Sources: Bevan and Phillott (1873), Mediaeval Geography (public domain); K. Miller's 1896 facsimile and a photograph of the map (Wikimedia Commons, public domain); Pleiades (CC BY 3.0); Natural Earth.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["medieval cartography", "mappa mundi", "Hereford", "historical geography", "map distortion", "Jerusalem", "Pleiades", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": BOOK_IA, "relation": "isDerivedFrom", "resource_type": "publication"},
                                 {"identifier": "https://pleiades.stoa.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
