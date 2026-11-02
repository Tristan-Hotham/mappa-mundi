"""Shared paths, groupings and helpers for the mappa-mundi project.

Raw inputs (raw/, read in place, never modified; steps 04 onward and the release run without raw/):
  raw/hereford_texts.json
      'medivalgeograph00unkngoog': Bevan, W.L. and Phillott, H.W. (1873) Mediaeval Geography: an essay in illustration
          of the Hereford Mappa Mundi. London: Stanford. Internet Archive OCR text (public domain, NOT_IN_COPYRIGHT).
      'bub_gb_yJzVAAAAMAAJ': Miller, K. (1903) Die Herefordkarte. Internet Archive OCR text (public domain). Cross-checks only.
      'File:...': Wikimedia Commons file information and wikitext for the map images (licence: public domain).
      'wiki:Hereford_Mappa_Mundi': English Wikipedia, parsed HTML with revision id (CC BY-SA 4.0). Facts quoted in the text.
  raw/hereford_1300.jpg         Wikimedia Commons "Hereford Mappa Mundi 1300.jpg", photograph of the map (public domain)
  raw/hereford_miller_1896.jpg  Wikimedia Commons "1896 facsimile of the Hereford Mappa Mundi by Konrad Miller.jpg" (public domain)
  raw/pleiades/places.csv, names.csv  Pleiades gazetteer of ancient places (CC BY 3.0)
  /home/claude/newdata/raw/geo/ne_*.geojson  Natural Earth (public domain)
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("MM_RAW", os.path.join(ROOT, "raw"))
GEO = os.environ.get("MM_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("MM_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.path.join(os.environ.get("MMTMP", "/dev/shm/mappamundi"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK, IMG):
    os.makedirs(d, exist_ok=True)

SLUG = "mappa-mundi"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23878612"                # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/mappa-mundi/"          # filled in by the publisher
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
PLEIADES_VER = "4.1"
BOOK = ("Bevan, W.L. and Phillott, H.W. (1873) Mediaeval Geography: an essay in illustration of the Hereford "
        "Mappa Mundi. London: E. Stanford")
BOOK_IA = "https://archive.org/details/medivalgeograph00unkngoog"
MILLER_IA = "https://archive.org/details/bub_gb_yJzVAAAAMAAJ"
PHOTO_URL = "https://commons.wikimedia.org/wiki/File:Hereford_Mappa_Mundi_1300.jpg"
MILLER_URL = "https://commons.wikimedia.org/wiki/File:1896_facsimile_of_the_Hereford_Mappa_Mundi_by_Konrad_Miller.jpg"

# The book's chapters, by page, and the part of the map each describes
CHAPTERS = [  # (first page, last page, chapter, part of the map)
    (1, 24, "I", "Frame and ocean"), (25, 44, "II", "Asia"), (45, 65, "III", "Asia"), (66, 89, "IV", "Asia"),
    (90, 110, "V", "Africa"), (111, 121, "VI", "Seas and islands"), (122, 139, "VII", "Europe"),
    (140, 162, "VIII", "Europe"), (163, 174, "IX", "British Isles")]
PARTS = ["Asia", "Africa", "Europe", "British Isles", "Seas and islands", "Frame and ocean"]


def part_of(page):
    for a, b, ch, p in CHAPTERS:
        if a <= page <= b:
            return p
    return None


def chapter_of(page):
    for a, b, ch, p in CHAPTERS:
        if a <= page <= b:
            return ch
    return None


# What each name is: places, peoples, legend and so on (see 01_parse.py for the rule)
CLASSES = [("Biblical", "#8E3B2E"), ("Classical", "#2F5FA7"), ("Medieval", "#2E8A6E"), ("Legendary", "#B07A12")]
CCOL = dict(CLASSES)


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "k": return f"{float(v) / 1000:.1f}"
    raise ValueError(f)


def gc_km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))


def bearing(lat1, lon1, lat2, lon2):
    """Initial great-circle bearing from point 1 to point 2, degrees clockwise from north."""
    import numpy as np
    p1, p2, dl = np.radians(lat1), np.radians(lat2), np.radians(lon2 - lon1)
    x = np.sin(dl) * np.cos(p2); y = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360
