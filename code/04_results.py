"""Every number used anywhere (data/results.json), the reusable tables (data/names.csv, data/located.csv,
data/regions.csv) and the page data (data/site.json). Reads only data/ (raw/ is not needed from here on).

Definitions
  * name: one entry in the index of Bevan and Phillott (1873), "Index of the names of places and objects [on the]
    Hereford Mappa Mundi". Part of the map: the chapter the index sends the reader to (Asia, Africa, Europe, the
    British Isles, the seas and islands, or the frame and ocean).
  * class: Biblical, Classical, Medieval or Legendary, by the rule in code/reading.py; winds, quarters, continent
    labels and real animals and plants ('Frame') are left out of the shares.
  * placed: a name with a real-world position, either the book's identification for a located inscription
    (hand-checked) or a match in Pleiades or Natural Earth (02_geo.py). A lower bound on what can be identified.
  * map frame: positions on Miller's facsimile in pixels. Map radius R = mean distance from Jerusalem (the map's centre)
    to Paradise (the top) and to the Pillars of Hercules (the bottom), from data/control_points.csv. Map bearing: east is
    at the top of the map, so north points left, south right and west down.
  * true distance and bearing: great-circle distance from Jerusalem (31.78 N, 35.23 E) and initial bearing.
  * best fit: the rotation, scale and shift (a similarity transform, least squares) that best lays the located map
    positions onto an azimuthal equidistant projection centred on Jerusalem. The 'implied position' of a place is where
    the map puts it under that fit; the displacement is the distance from there to the real place.
  * stretch: for each region, the median over pairs of located places in it (at least 100 km apart) of map distance
    divided by true distance, relative to the same median over all pairs on the map. Above 1: drawn bigger than average."""
import itertools
import numpy as np, pandas as pd
from pyproj import Transformer, Geod
from shapely.geometry import shape
from shapely.ops import transform as stransform
from common import *
import reading, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

N = pd.DataFrame(jload(f"{DATA}/names.json"))
FIT = jload(f"{DATA}/fit.json")
CP = pd.read_csv(f"{DATA}/control_points.csv").set_index("feature")
BOOKP = jload(f"{DATA}/book_pages.json.gz")
pc = lambda a, b: round(100 * a / b, 2) if b else None
R = {}
JER = (31.7767, 35.2345)

# ---------- inventory ----------
PL = [p for p in PARTS]
inv = N.copy(); inv["places"] = inv["class"] != "Frame"
R["source"] = {"n": len(N), "n_named": int(inv.places.sum()), "n_frame": int((~inv.places).sum()),
               "first_page": int(min(min(p) for p in N.pages)), "last_page": int(max(max(p) for p in N.pages)),
               "book_year": 1873, "book_pages": 174, "pleiades_version": PLEIADES_VER}
R["parts"] = {p: {"n": int((N.part == p).sum()), "pct": pc((N.part == p).sum(), len(N))} for p in PL}
KL = ["Biblical", "Classical", "Medieval", "Legendary"]
P_ = inv[inv.places]
R["classes"] = {c: {"n": int((P_["class"] == c).sum()), "pct": pc((P_["class"] == c).sum(), len(P_))} for c in KL}
R["part_class"] = {p: {c: int(((P_.part == p) & (P_["class"] == c)).sum()) for c in KL} for p in PL if p != "Frame and ocean"}
for p in R["part_class"]:
    n = sum(R["part_class"][p].values())
    R["part_class"][p]["n"] = n
    for c in KL:
        R["part_class"][p][c + "_pct"] = pc(R["part_class"][p][c], n)
T = P_.type.replace({"mountains": "mountain", "lake": "lake", "": "place or people"})
R["types"] = {t: int(v) for t, v in T.value_counts().items()}
real = P_[P_["class"] != "Legendary"]
R["placed"] = {"n_real": len(real), "n": int(real.lat.notna().sum()), "pct": pc(real.lat.notna().sum(), len(real)),
               "book": int((real.geo_source == "book (hand-checked)").sum()), "pleiades": int(real.geo_source.str.startswith("Pleiades").sum()),
               "pleiades_close": int(real.geo_source.str.contains("close").sum()), "pleiades_rough": int(real.geo_source.str.contains("rough").sum()),
               "ne": int((real.geo_source == "Natural Earth name").sum()), "rejected": len(reading.REJECT_GAZ)}
R["placed_parts"] = {p: {"n": int((real.part == p).sum()), "placed": int(((real.part == p) & real.lat.notna()).sum()),
                         "pct": pc(((real.part == p) & real.lat.notna()).sum(), (real.part == p).sum())} for p in PL if p != "Frame and ocean"}
assert R["source"]["n"] == 1025 and R["parts"]["British Isles"]["n"] == 83

# ---------- located inscriptions ----------
L = N[N.located].copy()
L["x"] = L.x_miller.astype(float); L["y"] = L.y_miller.astype(float)
jx, jy = CP.loc["Jerusalem", ["x_miller", "y_miller"]]
RAD = float(np.mean([np.hypot(CP.loc[f, "x_miller"] - jx, CP.loc[f, "y_miller"] - jy) for f in ("Paradise", "Pillars of Hercules")]))
L["map_frac"] = np.hypot(L.x - jx, L.y - jy) / RAD
L["map_brg"] = (np.degrees(np.arctan2(-(L.y - jy), -(L.x - jx))) + 360) % 360      # east up: north = -x, east = -y
Lr = L[L.lat.notna()].copy()
Lr = Lr[~Lr.duplicated(["lat", "lon"], keep="first")]            # Babel and Babylon, Santiago and its shrine: one point each
Lr["true_km"] = gc_km(JER[0], JER[1], Lr.lat.values, Lr.lon.values)
Lr["true_brg"] = bearing(JER[0], JER[1], Lr.lat.values, Lr.lon.values)
Lr["brg_err"] = ((Lr.map_brg - Lr.true_brg + 180) % 360) - 180
Lr = Lr[Lr.true_km > 1]                                           # Jerusalem itself has no bearing

REG = {  # regions for the distortion summary, by identification keyword or part
    "British Isles": lambda r: r.part == "British Isles" or r["name"] in ("Orcades",),
    "Iceland and Norway": lambda r: r["name"] in ("Ysland", "Fareie", "Noreya"),
    "France": lambda r: r["name"] in ("Parisius", "Remis", "Rotomagum", "Carnotum", "Cenomani", "Aurelianum", "Turonis", "Limogena", "Avernis", "Augustudunum", "Tolosa", "Burdegala", "Bayona", "Narbona", "Arelas"),
    "Spain": lambda r: r["name"] in ("Compostella", "Toletum", "Corduba", "Basella", "Terracona", "Ilerda", "Ilema", "Gades", "Calpel"),
    "Italy": lambda r: r["name"] in ("Roma", "Neapolis", "Salema", "Puteolis", "Bononia", "Arimmuin", "Vercellis", "Genua", "Venicia", "Messana"),
    "Central Europe": lambda r: r["name"] in ("Braga", "Brema", "Remesburgh"),
    "Greece and Constantinople": lambda r: r["name"] in ("Constantinopolis", "Thessalonica", "Athene", "Troja", "Nicomedia", "Calcidonia"),
    "Holy Land": lambda r: r.pages[0] in range(77, 82) or r["name"] in ("Jerusalem",),
    "Syria and Anatolia": lambda r: r["name"] in ("Antiochia", "Laodiciam", "Tripolis", "Beritus", "Tarsus", "Ephesus", "Samosaka"),
    "Egypt and Sinai": lambda r: r.pages[0] in (84, 86, 88) or r["name"] in ("Sinay",),
    "North Africa": lambda r: r.part == "Africa",
    "Mesopotamia and Persia": lambda r: r["name"] in ("Ninevee", "Nisibi", "Babel Tttkris", "Babylonia", "Hur", "Persepolis", "Rages", "Carax", "Area Noe", "Caspie Portee"),
    "India and Central Asia": lambda r: r["name"] in ("Cottonare", "Patalus", "Nicea", "Bucephala", "Cassica", "Polibrota", "Zimarim", "Tapbana", "Alexandria", "Samarcan") and r.part == "Asia",
}


def region(r):
    for k, f in REG.items():
        if f(r):
            return k
    return "Other"


Lr["region"] = [region(r) for _, r in Lr.iterrows()]
Lr.loc[(Lr["name"] == "Babylonia") & (Lr.pages.map(lambda p: p[0]) == 74), "region"] = "Mesopotamia and Persia"
Lr.loc[(Lr["name"] == "Alexandria") & (Lr.pages.map(lambda p: p[0]) == 88), "region"] = "Egypt and Sinai"
Lr.loc[(Lr["name"] == "Antiochia"), "region"] = "Syria and Anatolia"
assert (Lr.region == "Other").sum() == 0, Lr[Lr.region == "Other"][["name", "pages"]].values.tolist()

# best similarity fit: map px -> azimuthal equidistant km about Jerusalem
AEQD = Transformer.from_crs(4326, f"+proj=aeqd +lat_0={JER[0]} +lon_0={JER[1]} +units=km", always_xy=True)
AINV = Transformer.from_crs(f"+proj=aeqd +lat_0={JER[0]} +lon_0={JER[1]} +units=km", 4326, always_xy=True)
ex, ny = AEQD.transform(Lr.lon.values, Lr.lat.values)
mx, my = Lr.x.values - jx, -(Lr.y.values - jy)                    # map coordinates with y up
Z = mx + 1j * my; W = ex + 1j * ny
Zc, Wc = Z - Z.mean(), W - W.mean()
a = (np.conj(Zc) @ Wc) / (np.conj(Zc) @ Zc)                        # complex scale-rotation, least squares
b = W.mean() - a * Z.mean()
Wh = a * Z + b
Lr["imp_lon"], Lr["imp_lat"] = AINV.transform(Wh.real, Wh.imag)
Lr["disp_km"] = np.abs(Wh - W)
rot = float(np.degrees(np.angle(a)))                                # rotation of the map's 'up' relative to north
R["fit"] = {"rotation_deg": round(rot, 1), "km_per_px": round(float(abs(a)), 3), "km_per_radius": round(float(abs(a)) * RAD),
            "median_disp_km": round(float(np.median(Lr.disp_km))), "mean_disp_km": round(float(Lr.disp_km.mean())),
            "r2": round(float(1 - np.sum(np.abs(Wh - W) ** 2) / np.sum(np.abs(W - W.mean()) ** 2)), 3)}
# the map's up direction in real-world terms: rotating map coordinates by 'rot' gives east-north; 'up' is +y
up_brg = (90 - (90 + rot)) % 360
R["fit"]["up_bearing"] = round(float((-rot) % 360), 1)

# distances and bearings
from scipy.stats import spearmanr
R["dist"] = {"spearman": round(float(spearmanr(Lr.true_km, Lr.map_frac).correlation), 3), "n": len(Lr),
             "max_true_km": round(float(Lr.true_km.max())), "far_name": Lr.loc[Lr.true_km.idxmax(), "identification"]}
bins = [(0, 500), (500, 1500), (1500, 3000), (3000, 6000)]
R["dist_bins"] = [{"lo": lo, "hi": hi, "n": int(((Lr.true_km >= lo) & (Lr.true_km < hi)).sum()),
                   "median_frac": round(float(Lr[(Lr.true_km >= lo) & (Lr.true_km < hi)].map_frac.median()), 3),
                   "median_km": round(float(Lr[(Lr.true_km >= lo) & (Lr.true_km < hi)].true_km.median()))} for lo, hi in bins]
db = R["dist_bins"]
R["dist"]["near_frac_pct"] = round(100 * db[0]["median_frac"]); R["dist"]["far_frac_pct"] = round(100 * db[3]["median_frac"])
R["dist"]["near_km"] = db[0]["median_km"]; R["dist"]["far_km"] = db[3]["median_km"]
R["dist"]["km_ratio"] = round(db[3]["median_km"] / db[0]["median_km"], 1); R["dist"]["frac_ratio"] = round(db[3]["median_frac"] / db[0]["median_frac"], 1)
ae = Lr.brg_err.abs()
R["bearing"] = {"median_abs_err": round(float(ae.median())), "within45_pct": pc((ae <= 45).sum(), len(Lr)), "within90_pct": pc((ae <= 90).sum(), len(Lr)),
                "n": len(Lr), "mean_err": round(float(Lr.brg_err.mean()))}


def stretch(d, allpairs_med):
    pr = []
    for (i, r1), (j, r2) in itertools.combinations(d.iterrows(), 2):
        t = gc_km(r1.lat, r1.lon, r2.lat, r2.lon)
        if t >= 100:
            pr.append(np.hypot(r1.x - r2.x, r1.y - r2.y) / t)
    return (float(np.median(pr)) / allpairs_med if pr else None), len(pr)


allp = []
for (i, r1), (j, r2) in itertools.combinations(Lr.iterrows(), 2):
    t = gc_km(r1.lat, r1.lon, r2.lat, r2.lon)
    if t >= 100:
        allp.append(np.hypot(r1.x - r2.x, r1.y - r2.y) / t)
ALLMED = float(np.median(allp))
regs = []
for k in REG:
    d = Lr[Lr.region == k]
    s, npairs = stretch(d, ALLMED)
    if len(d) < 5: s = None                                        # too few places for a stable figure
    regs.append({"region": k, "n": len(d), "stretch": round(s, 2) if s else None, "pairs": npairs,
                 "median_true_km": round(float(d.true_km.median())), "median_map_frac": round(float(d.map_frac.median()), 3),
                 "median_abs_brg_err": round(float(d.brg_err.abs().median())), "median_disp_km": round(float(d.disp_km.median())),
                 "mean_true_brg": round(float(np.degrees(np.angle(np.exp(1j * np.radians(d.true_brg)).mean())) % 360)),
                 "mean_map_brg": round(float(np.degrees(np.angle(np.exp(1j * np.radians(d.map_brg)).mean())) % 360))})
RG = pd.DataFrame(regs)
RG.to_csv(f"{DATA}/regions.csv", index=False)
R["regions"] = {r["region"]: r for r in regs}
R["stretch_all_px_per_km"] = round(ALLMED, 4)
sr = RG.dropna(subset=["stretch"]).sort_values("stretch", ascending=False)
R["stretch_rank"] = sr.region.tolist()
G = R["regions"]

# ---------- Britain: area against names ----------
W = jload(f"{DATA}/world.json")
EA = Transformer.from_crs(4326, 6933, always_xy=True)
area = {}
for f in W["features"]:
    g = stransform(EA.transform, shape(f["geometry"]))
    area[f["properties"]["iso"]] = g.area / 1e6
CONT = {"Africa": None}
afroeur = sum(v for k, v in area.items() if k not in ("USA", "CAN", "MEX", "BRA", "ARG", "AUS", "ATA", "GRL", "NZL", "CHL", "PER", "COL", "VEN", "BOL",
                                                      "ECU", "PRY", "URY", "GUY", "SUR", "CUB", "GTM", "HND", "NIC", "PAN", "CRI", "SLV", "BLZ", "DOM", "HTI",
                                                      "JAM", "PNG", "FJI", "SLB", "VUT", "NCL", "BHS", "TTO", "PRI", "FLK", "ATF", "IDN", "PHL", "JPN", "TWN",
                                                      "TLS", "BRN", "MYS", "SGP"))
bi = sum(area.get(k, 0) for k in ("GBR", "IRL", "IMN"))
R["britain"] = {"names": R["parts"]["British Isles"]["n"], "names_pct": R["parts"]["British Isles"]["pct"],
                "area_km2": round(bi), "afroeurasia_km2": round(afroeur), "area_pct": round(100 * bi / afroeur, 2),
                "over_x": round(R["parts"]["British Isles"]["pct"] / (100 * bi / afroeur)),
                "located": int((Lr.region == "British Isles").sum()), "stretch": G["British Isles"]["stretch"],
                "medieval_pct": R["part_class"]["British Isles"]["Medieval_pct"]}
# names per 100,000 km2: the British Isles against India and Central Asia's located towns is not comparable; use the chapter totals
R["britain"]["names_per_100k"] = round(R["britain"]["names"] / bi * 1e5, 1)

# ---------- facts stated in words (checked against the book and Wikipedia) ----------
bp = lambda p: BOOKP[str(p)]
assert "transferred from the southern to the northern side" in bp(170)                     # Caen put in England
assert "transposed" in bp(23) and "Jerusalem forms the centre of the circle" in bp(22)       # Africa and Europe swapped; Jerusalem centre
assert "Taprobane (Ceylon)" in bp(21)
assert "drawn on a scale out of all pro" in bp(164).replace("-", "").replace("\n", "") or "out of all proportion" in bp(164)
assert "its meaning we cannot divine" in bp(158)
WK = {"revid": None}
SRC = jload(f"{DATA}/sources.json")
R["wiki"] = {"revid": SRC["wiki_revid"], "towns": 420, "biblical_events": 15, "animals": 33, "people": 32, "myth_scenes": 5, "h_cm": 158, "w_cm": 133, "year": 1300,
             "unesco": 2007, "sale_year": 1988, "library_year": 1996}
R["fit_photo"] = {"rms_px": FIT["rms_px"], "max_px": FIT["max_px"], "n": FIT["n"], "rms_pct": round(100 * FIT["rms_px"] / (2 * RAD), 1)}
R["located"] = {"n": int(N.located.sum()), "real": int(L.lat.notna().sum()), "unique_real": len(Lr), "legend": int((N.located & (N["class"] == "Legendary")).sum()),
                "high": int((L.pos_conf == "high").sum()), "medium": int((L.pos_conf == "medium").sum()), "radius_px": round(RAD),
                "by_class": {c: int((L["class"] == c).sum()) for c in KL}}
R["meta"] = {"page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "slug": SLUG, "book_ia": BOOK_IA, "miller_ia": MILLER_IA,
             "photo_url": PHOTO_URL, "miller_url": MILLER_URL}

# notable places for the text
def row(name, page=None):
    d = Lr[(Lr["name"] == name) & ((Lr.pages.map(lambda p: p[0]) == page) if page else True)]
    r = d.iloc[0]
    return {"true_km": round(float(r.true_km)), "map_frac": round(float(r.map_frac), 3), "map_pct": round(100 * float(r.map_frac)), "true_brg": round(float(r.true_brg)),
            "map_brg": round(float(r.map_brg)), "brg_err": round(float(r.brg_err)), "disp_km": round(float(r.disp_km))}


R["places"] = {"London": row("Londonia"), "Rome": row("Roma"), "Paris": row("Parisius"), "Babylon": row("Babel Tttkris"), "Cairo": row("Babylonia", 86),
               "SriLanka": row("Tapbana"), "Samarkand": row("Samarcan"), "Iceland": row("Ysland"), "Constantinople": row("Constantinopolis"),
               "Patna": row("Polibrota"), "Bethlehem": row("Bethleem"), "Caen": row("Cadan"), "Carthage": row("Cartago"), "Santiago": row("Compostella"),
               "Hereford": row("Hreford"), "Alexandria": row("Alexandria", 88)}
pp = R["places"]
R["places"]["ratio_london_bethlehem_km"] = round(pp["London"]["true_km"] / pp["Bethlehem"]["true_km"])
R["places"]["ratio_london_bethlehem_map"] = round(pp["London"]["map_frac"] / pp["Bethlehem"]["map_frac"], 1)
R["places"]["srilanka_vs_london_km"] = round(pp["SriLanka"]["true_km"] / pp["London"]["true_km"], 2)

# ---------- tables ----------
cols = ["k", "name", "index_entry", "type", "qualifier", "pages", "part", "chapter", "class", "located", "x_miller", "y_miller", "pos_conf",
        "identification", "evidence", "lat", "lon", "geo_source", "pleiades_id", "pleiades_title", "ne_name", "book_text"]
out = N.reindex(columns=cols).copy(); out["pages"] = out.pages.map(lambda p: ";".join(map(str, p)))
out.rename(columns={"k": "index_no", "book_text": "book_text_ocr"}).to_csv(f"{DATA}/names.csv", index=False)
ax, ay = FIT["ax"], FIT["ay"]
Lc = L.copy()
Lc["x_photo"] = (ax[0] * Lc.x + ax[1] * Lc.y + ax[2]).round(); Lc["y_photo"] = (ay[0] * Lc.x + ay[1] * Lc.y + ay[2]).round()
Lc = Lc.merge(Lr[["k", "region", "true_km", "true_brg", "brg_err", "imp_lat", "imp_lon", "disp_km"]], on="k", how="left")
Lc[["k", "name", "pages", "part", "class", "region", "x_miller", "y_miller", "x_photo", "y_photo", "pos_conf", "identification", "evidence",
    "lat", "lon", "map_frac", "map_brg", "true_km", "true_brg", "brg_err", "imp_lat", "imp_lon", "disp_km"]] \
    .assign(pages=lambda d: d.pages.map(lambda p: ";".join(map(str, p)))).round(3).rename(columns={"k": "index_no"}).to_csv(f"{DATA}/located.csv", index=False)

# ---------- page data ----------
MC = FIT["miller_crop"]; MWEB = FIT["miller_web"]; sc = MWEB[0] / (MC[2] - MC[0])
CI = {c: i for i, c in enumerate(KL)}
PI = {p: i for i, p in enumerate(PL)}
loc_rows = []
for _, r in Lc.iterrows():
    loc_rows.append([int(r.k), r["name"], r.identification or "", r.evidence, CI.get(r["class"], 3), PI[r.part], round((r.x - MC[0]) * sc, 1), round((r.y - MC[1]) * sc, 1),
                     r.pos_conf, None if pd.isna(r.lat) else round(float(r.lat), 3), None if pd.isna(r.lon) else round(float(r.lon), 3),
                     None if pd.isna(r.imp_lat) else round(float(r.imp_lat), 2), None if pd.isna(r.imp_lon) else round(float(r.imp_lon), 2),
                     None if pd.isna(r.disp_km) else round(float(r.disp_km)), None if pd.isna(r.true_km) else round(float(r.true_km)),
                     r.pages[0], r.region if isinstance(r.region, str) else ""])
oth = N[(~N.located) & N.lat.notna()]
oth_rows = [[int(r.k), r["name"], CI.get(r["class"], 1), PI[r.part], round(float(r.lat), 3), round(float(r.lon), 3), r.geo_source, r.pages[0], r.get("pleiades_title") or r.get("ne_name") or ""]
            for _, r in oth.iterrows()]
allnames = [[int(r.k), r["name"], r["class"], r.part, r.pages, r.type] for _, r in N.iterrows()]
# photo frame in facsimile pixels: invert the affine fit for the photo's corners
Aff = np.array([[ax[0], ax[1]], [ay[0], ay[1]]]); bb = np.array([ax[2], ay[2]]); Ai = np.linalg.inv(Aff)
pw, ph = FIT["photo_w"], FIT["photo_h"]
corners = [Ai @ (np.array(c) - bb) for c in ((0, 0), (pw, 0), (pw, ph), (0, ph))]
corners = [[round((c[0] - MC[0]) * sc, 1), round((c[1] - MC[1]) * sc, 1)] for c in corners]
site = {"classes": [[c, CCOL[c]] for c in KL], "parts": PL, "located": loc_rows,
        "loc_cols": ["k", "name", "ident", "evidence", "cls", "part", "x", "y", "conf", "lat", "lon", "imp_lat", "imp_lon", "disp_km", "true_km", "page", "region"],
        "other": oth_rows, "other_cols": ["k", "name", "cls", "part", "lat", "lon", "src", "page", "gaz"],
        "img": {"miller": "img/miller.jpg", "w": MWEB[0], "h": MWEB[1], "photo": "img/photo.jpg", "photo_corners": corners},
        "jer_px": [round((jx - MC[0]) * sc, 1), round((jy - MC[1]) * sc, 1)], "radius_px": round(RAD * sc, 1),
        "regions": regs, "jer": list(JER)}
jsave(site, f"{DATA}/site.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("source", "classes", "placed", "fit", "dist", "bearing", "britain", "located")}, indent=0)[:3000])
print(RG.to_string())
print(R["places"])
