"""Geography: outlines for the page and the figures (Natural Earth 1:50m), and a real-world position for every name
in the book's index that can be matched to a place.

Matching, in order of preference:
  1. The book's own identification, for the inscriptions I located by eye on the facsimile (code/reading.py). The
     coordinates I give there are checked against Natural Earth (towns) and Pleiades (ancient places): where a gazetteer
     point for the same place lies more than 30 km away, the gazetteer point is used.
  2. Pleiades: the map's name (as the book's index spells it) equals an attested or romanised name in Pleiades, allowing
     for simple medieval spellings (y for i, f for ph, e for ae), and the place lies in the part of the world the book
     discusses it under. Rough Pleiades locations are kept but flagged.
  3. Natural Earth populated places: the map's name equals a modern town name in the same part of the world (this
     catches medieval names that are still in use, such as Lincoln and Ely).
Names that match nothing are left without a position. Outputs: data/world.json, data/names.json (every index name with its part of the map, class, position on the facsimile
where located, real-world position and source, and the OCR text of the book where it is discussed)."""
import difflib
import numpy as np, pandas as pd
from shapely.geometry import shape, mapping
from common import *
import reading

iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]


def rnd(c, k=2):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], k), round(c[1], k)]
    return [rnd(x, k) for x in c]


W50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
feats = []
for f in W50["features"]:
    gs = shape(f["geometry"]).simplify(0.04, preserve_topology=True)
    if gs.is_empty: continue
    gm = mapping(gs)
    feats.append({"type": "Feature", "properties": {"iso": iso_of(f["properties"]), "name": f["properties"].get("NAME_EN") or f["properties"]["NAME"]},
                  "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")

E = jload(f"{WORK}/entries.json")
K = {e["k"]: e for e in E}
assert K[513]["name"] == "Jerusalem" and K[802]["name"] == "Roma" and K[434]["name"] == "Gangines" and K[1023]["name"] == "Zimarim"

# ---------- Pleiades ----------
pl = pd.read_csv(f"{RAW}/pleiades/places.csv", dtype=str, keep_default_na=False)
nm = pd.read_csv(f"{RAW}/pleiades/names.csv", dtype=str, keep_default_na=False)
pl = pl[(pl.representative_latitude != "") & (pl.representative_longitude != "")]
PL = {r.id: (r.title, float(r.representative_latitude), float(r.representative_longitude), r.location_precision) for r in pl.itertuples()}
nnames = nm.groupby("place_id").size().to_dict()
KEYS = {}


def addkey(k, pid):
    if k and pid in PL:
        KEYS.setdefault(k, set()).add(pid)


for r in nm.itertuples():
    for f in (r.attested_form, r.romanized_form_1, r.romanized_form_2, r.romanized_form_3):
        for v in re.split(r"[,/;]", f):
            addkey(norm(v), r.place_id)
for pid, (t, *_ ) in PL.items():
    for v in re.split(r"[,/;]", re.sub(r"\([^)]*\)", "", t)):
        addkey(norm(v), pid)
KEYLIST = sorted(KEYS)

BOX = {  # lon0, lat0, lon1, lat1 for the parts of the map
    "Asia": (24, 5, 110, 56), "Africa": (-18, 0, 34, 38), "Europe": (-11, 34, 45, 72), "British Isles": (-11, 49.5, 2.5, 61.5),
    "Seas and islands": (-19, 26, 43, 48), "Frame and ocean": (-180, -90, 180, 90)}
QBOX = {"Eg.": (24, 20, 36, 32), "Ind.": (55, 5, 100, 40), "Syr.": (33, 30, 40, 38), "Pisid.": (28, 36, 34, 40), "Cyren.": (17, 29, 26, 34),
        "Cyren": (17, 29, 26, 34), "Maced.": (19, 39, 25, 42.5), "Mys.": (25, 38, 31, 41), "Ital.": (6, 36, 19, 47), "ItaL": (6, 36, 19, 47),
        "Gall.": (-5, 42, 8, 51.5), "GalL": (-5, 42, 8, 51.5), "Germ.": (5, 46, 20, 56), "Genn.": (5, 46, 20, 56), "Rset": (8, 45, 14, 49),
        "Maurit.": (-10, 30, 10, 37.5), "Cappad.": (33, 37, 39, 41), "Pisid": (28, 36, 34, 40)}


def inbox(lat, lon, b):
    return b[0] <= lon <= b[2] and b[1] <= lat <= b[3]


def variants(n):
    n = norm(n)
    out = {n, n.replace("y", "i"), n.replace("ph", "f"), n.replace("f", "ph"), n.replace("ae", "e"), n.replace("th", "t"),
           re.sub(r"^y", "i", n), n.replace("c", "k"), n.replace("ch", "c")}
    if n.endswith("um"): out.add(n[:-2] + "us")
    if n.endswith("is"): out.add(n[:-2] + "ae")      # ablative forms in the Itinerary style: Vercellis, Turonis
    return {v for v in out if len(v) >= 3}


def pleiades(e):
    if e["name"] in reading.REJECT_GAZ:
        return None
    box = QBOX.get(e["qual"]) or BOX[e["part"]]
    best, how = None, None
    for v in variants(e["name"]):
        for pid in KEYS.get(v, ()):
            t, la, lo, pr = PL[pid]
            if inbox(la, lo, box):
                sc = (pr == "precise", nnames.get(pid, 0), norm(t) == norm(e["name"]))
                if best is None or sc > best[0]:
                    best, how = (sc, pid), "exact"
    if best is None and len(norm(e["name"])) >= 5:      # close spelling, same first two letters, in the right part of the world
        n = norm(e["name"])
        for k in difflib.get_close_matches(n, [x for x in KEYLIST if x[:2] == n[:2]], n=6, cutoff=.86):
            for pid in KEYS[k]:
                t, la, lo, pr = PL[pid]
                if inbox(la, lo, box):
                    sc = (pr == "precise", nnames.get(pid, 0), 0)
                    if best is None or sc > best[0]:
                        best, how = (sc, pid), "close"
    if best is None:
        return None
    pid = best[1]; t, la, lo, pr = PL[pid]
    return {"pid": pid, "title": t, "lat": round(la, 4), "lon": round(lo, 4), "precision": pr, "how": how}


# ---------- Natural Earth towns ----------
NE = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
NEI = {}
for f in NE:
    p = f["properties"]
    for v in {norm(p["name"]), norm(p.get("nameascii") or ""), norm(p.get("namealt") or "")}:
        if v: NEI.setdefault(v, []).append((p["name"], p["latitude"], p["longitude"], p.get("pop_max") or 0, p.get("adm0name")))


def naturalearth(name, box):
    c = [x for x in NEI.get(norm(name), []) if inbox(x[1], x[2], box)]
    return max(c, key=lambda x: x[3]) if c else None


# ---------- located inscriptions: the book's identification ----------
pos = pd.read_csv(f"{DATA}/map_positions.csv")
LOC, notes = {}, []
for r in pos.itertuples():
    c = [e for e in E if (e["name"] == r.name or e["index"].startswith(r.name)) and r.page in e["pages"]]
    assert len(c) == 1, (r.name, r.page, [x["index"] for x in c])
    e = c[0]
    key = (e["name"], r.page) if (e["name"], r.page) in reading.LOCATED else (r.name, r.page)
    ident, ev, la, lo = reading.LOCATED[key]
    src = "book" if ident else None
    if ident:
        nep = naturalearth(ident.split(" (")[0], BOX[e["part"]] if e["part"] != "Frame and ocean" else BOX["Europe"])
        if nep and gc_km(la, lo, nep[1], nep[2]) > 30:
            notes.append(f"{e['name']}: hand position {la},{lo} vs Natural Earth {nep[0]} {nep[1]:.2f},{nep[2]:.2f}; using Natural Earth")
            la, lo = round(nep[1], 4), round(nep[2], 4)
    LOC[e["k"]] = {"x": int(r.x), "y": int(r.y), "conf": r.conf, "identification": ident, "evidence": ev, "lat": la, "lon": lo, "src": src}
print("located", len(LOC), "with a real place", sum(1 for v in LOC.values() if v["lat"] is not None)); print("\n".join(notes) or "no gazetteer disagreements")

# ---------- class (see reading.py for the rule) ----------


def klass(e, pm):
    k = e["k"]; p = e["pages"][0]
    if k in reading.FRAME_NAT: return "Frame"
    if k in reading.LEGEND: return "Legendary"
    if k not in reading.NOT_BIBLE and (k in reading.BIBLE or any(a <= p <= b for a, b in reading.BIBLE_PAGES)): return "Biblical"
    if k in reading.MEDIEVAL_X or k in reading.MEDIEVAL_EU: return "Medieval"
    if e["part"] == "British Isles" and k not in reading.CLASSICAL_BRIT: return "Medieval"
    return "Classical"


# Some names are indexed only under the frame chapter's pages but sit elsewhere (Clee Hill, p. 6 and 165)
for e in E:
    if e["part"] == "Frame and ocean" and len(e["pages"]) > 1 and part_of(max(e["pages"])) not in (None, "Frame and ocean"):
        e["part"] = part_of(max(e["pages"])); e["chapter"] = chapter_of(max(e["pages"]))

out = []
for e in E:
    pm = pleiades(e) if e["part"] != "Frame and ocean" else None
    cls = klass(e, pm)
    rec = {"k": e["k"], "index_entry": e["index"], "name": e["name"], "type": e["type"], "qualifier": e["qual"], "pages": e["pages"],
           "part": e["part"], "chapter": e["chapter"], "class": cls, "located": e["k"] in LOC}
    L = LOC.get(e["k"])
    if L:
        rec.update({"x_miller": L["x"], "y_miller": L["y"], "pos_conf": L["conf"], "identification": L["identification"], "evidence": L["evidence"]})
    lat = lon = None; src = ""
    if L and L["lat"] is not None:
        lat, lon, src = L["lat"], L["lon"], "book (hand-checked)"
    elif cls not in ("Legendary", "Frame") and not (L and L["identification"] is None):
        if pm:
            lat, lon, src = pm["lat"], pm["lon"], "Pleiades " + pm["how"] + (" (rough)" if pm["precision"] == "rough" else "")
            rec.update({"pleiades_id": pm["pid"], "pleiades_title": pm["title"]})
        elif e["part"] in ("Europe", "British Isles", "Seas and islands"):
            ne = naturalearth(e["name"], BOX[e["part"]]) if e["name"] not in reading.REJECT_GAZ else None
            if ne:
                lat, lon, src = round(ne[1], 4), round(ne[2], 4), "Natural Earth name"
                rec["ne_name"] = ne[0]
    rec.update({"lat": lat, "lon": lon, "geo_source": src})
    r = e.get("run") or {}
    rec["book_text"] = (r.get("g", "") + " " + r.get("gloss", "")[:140]).strip()
    out.append(rec)
jsave(out, f"{DATA}/names.json", indent=0)
df = pd.DataFrame(out)
print(df["class"].value_counts().to_dict())
print(df.groupby("part").apply(lambda d: f"{len(d)} names, {d.lat.notna().sum()} placed").to_dict())
print(df.geo_source.value_counts().to_dict())

# ---------- source facts carried forward (raw/ is not needed after this step) ----------
T = jload(f"{RAW}/hereford_texts.json")
wk = T["wiki:Hereford_Mappa_Mundi"]
import html as _html
wtxt = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>|<sup.*?</sup>", "", wk["html"], flags=re.S))).replace("\xa0", " "))
for s_ in ("420 towns, 15 Biblical events, 33 animals and plants, 32 people, and five scenes from classical mythology", "158 cm by 133 cm",
           "largest medieval map known still to exist", "Hereford has nearly disappeared from it", "UNESCO Memory of the World International Register in 2007"):
    assert s_ in wtxt, s_
lic = {k: T[k]["info"]["extmetadata"]["LicenseShortName"]["value"] for k in ("File:Hereford Mappa Mundi 1300.jpg", "File:1896 facsimile of the Hereford Mappa Mundi by Konrad Miller.jpg")}
assert all(v == "Public domain" for v in lic.values()), lic
jsave({"wiki_revid": wk["revid"], "image_licences": lic, "book_ia_status": T["medivalgeograph00unkngoog"]["meta"].get("possible_copyright_status"),
       "miller_licence": T["bub_gb_yJzVAAAAMAAJ"]["meta"].get("licenseurl")}, f"{DATA}/sources.json", indent=1)
