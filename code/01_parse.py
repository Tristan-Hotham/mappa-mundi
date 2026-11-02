"""Read Bevan and Phillott (1873): split the OCR text into book pages, parse the index of names on the map, find where
each name is discussed and pull out the book's identification and the authorities it cites there.

Method
  * Pages: the OCR marks each scanned page with a 'Digitized by' line; the running head that follows gives the page
    number (ASIA. 27, 170 THE BRITISH ISLES.). Where the head is unreadable the count simply continues.
  * Inventory: the book's own "Index of the names of places and objects [on the] Hereford Mappa Mundi" (pp. 175 to
    182). Each entry is one name on the map with its type (Fl. river, I. island, Ms. mountain...) and the page(s)
    where the book discusses it. The index is the inventory: one entry, one inscription or labelled feature.
  * Where it is discussed: the book prints the map's own words in black-letter type, which the OCR turns into garbage
    ('ColcegtriH', 'I^foti'). These garbled runs are found on the page and each index entry is matched to the most
    similar run (similarity of the cleaned name with the garbled run and with the plain text that follows it). The
    plain words after the run are the book's gloss: usually the identification ('ColcegtriH, Colchester, already
    noticed...'), sometimes a description.
  * Identification: taken from the gloss by simple patterns (a capitalised place name, 'intended for X', 'now X',
    'the modern X'), then every entry was checked by hand against the page text (code/reading.py), which also records
    the book's own verdict where it calls a name unknown.
  * Citations: books of the Bible and classical or late antique authors cited between this run and the next one.
Output: WORK/entries.json (all index entries with page, gloss, context, citations) and WORK/review.tsv."""
import difflib
import numpy as np
from scipy.optimize import linear_sum_assignment
from common import *

T = jload(f"{RAW}/hereford_texts.json")["medivalgeograph00unkngoog"]["text"]
lines = T.split("\n")

# ---------- pages ----------
start = [i for i, l in enumerate(lines) if l.strip().startswith("CHAPTER I.")][1]
idx0 = [i for i, l in enumerate(lines) if l.strip().startswith("INDEX")][0]
head_re = re.compile(r"^\s*(\d{1,3})\s+[A-Z][A-Z .,'\-]+\.?\s*$|^\s*[A-Z][A-Z .,'\-]+\.?\s+(\d{1,3})\s*$")
pages, cur, buf, expect = {}, 1, [], False
for l in lines[start:idx0]:
    s = l.strip()
    if s.startswith("Digitized by"):
        pages.setdefault(cur, []).extend(buf); buf = []; cur += 1; expect = True; continue
    if expect and s:
        expect = False
        m = head_re.match(s)
        if m:
            n = int(m.group(1) or m.group(2))
            if abs(n - cur) <= 3:
                cur = n
            continue
    buf.append(l)
pages.setdefault(cur, []).extend(buf)


def flat(t):
    t = re.sub(r"-\s*\n\s*", "", t)            # join words hyphenated across lines
    return re.sub(r"\s+", " ", t).strip()


PG = {p: flat("\n".join(v)) for p, v in pages.items() if p <= 174}
jsave({str(p): t for p, t in sorted(PG.items())}, f"{DATA}/book_pages.json.gz")     # public domain text, for checking

# ---------- index ----------
i0 = [i for i, l in enumerate(lines) if l.strip().startswith("Ms. = Mons")][0] + 1
raw = [l.strip() for l in lines[i0:] if l.strip() and not l.strip().startswith("Digitized")
       and not re.fullmatch(r"INDEX\.?|\d{3}|1Y9|THE END\.|.{0,2}|Printed.*", l.strip())]
ents, cur = [], ""
for l in raw:
    cur = (cur + " " + l).strip()
    if re.search(r"(\d|S\(k|seq)[.\-^,]?\s*[.\-]?\s*[■'.]?$", cur) and not re.search(r",\s*$", cur):
        ents.append(cur); cur = ""
    elif cur.startswith("Miles Maris"):
        ents.append(cur + ", 146."); cur = ""          # index omits the page: the legend is on p. 146 (Mont St Michel)
# a few lines end in a comma or a stray mark although the entry is complete: split where a page number is followed by a new name
ents = [p for e in ents for p in re.split(r"(?<=\d)[.,]\^?\s+(?=[A-Z][A-Za-z'^]+(?: [A-Za-z]+)?, (?:[A-Z][a-z]*\.,? )?\d)", e)]
ents = [e.replace("(Cyren).", "(Cyren.)") for e in ents]
ents = [x for e in ents for x in (["Gangines, 35.", "Gangines Ethiopes, 100, 108."] if e.startswith("Gangines, 35, Gangines") else [e])]
TYPES = {"Fl": "river", "FL": "river", "F1": "river", "fl": "river", "I": "island", "L": "island", "M": "sea", "Ms": "mountain",
         "M8": "mountain", "M&": "mountain", "Mts": "mountains", "Pr": "promontory", "S": "gulf", "Prov": "province", "It": "island", "1": "island"}
rx = re.compile(r"^(?P<name>.+?)(?:,\s*(?P<type>Fl|FL|F1|fl|I|L|M|Ms|M8|M&|Mts|Pr|S|Prov|It|1)\s*[.,;^']*)?(?:\s*(?:et\s+\w+\.?)?\s*\((?P<q>[^)]*)\))?,\s*(?P<pages>[\dS(k ,.\-']+?(?:,?\s*seq)?)[.\-^■' ]*$")
PAGEFIX = {"Duracium": [132], "Elicon": [133], "Gazan": [81], "Gelboe": [80], "Insula": [133], "Thelea": [134], "Tubalum": [135],
           "Lech": [153], "Carimaspi": [61], "Wltumns": [19]}
# the index's 'L' after a name is 'I.' (Insula) misread, except for the few lakes, fixed below by name
LAKES = {"Calearsus", "Aretusa", "Benacus", "Fialus", "Salinarum", "Salinamm", "Triton", "Madus"}
NAMEFIX = {"Hibemia": "Hibernia", "Comubia": "Cornubia", "Jenisalem": "Jerusalem", "lope": "Iope", "luda": "Iuda", "lacobi Templum": "Iacobi Templum",
           "lUiricus": "Illiricus", "lira": "Ilra", "lor": "Ior", "Iaboth": "Iaboth", "NHus": "Nilus", "Kumidia": "Numidia", "Koreya": "Noreya",
           "Koricus": "Noricus", "Kisa": "Nisa", "Katabres": "Natabres", "Kibie": "Nibie", "Bale": "Eale", "Eecia Minor": "Recia Minor",
           "Becordanonim": "Recordanorum", "Graramantes": "Garamantes", "Cannania": "Carmania", "Canuelum": "Carmelum", "Cam": "Carn",
           "Camotuin": "Carnotum", "Camder": "Carnder", "Samus": "Sarnus", "Mama": "Marna", "Ama Blanca": "Arna Blanca",
           "Avemia": "Avernia", "Avemis": "Avernis", "Hfoid": "Hreford", "ETmochi": "Eniochi", "Enzaree": "Euzaree", "GaUlee": "Galilee",
           "Ipims": "Ipirus", "Tracia": "Tracia", "TripMcia": "Triphicia", "TJgolopes": "Ugolopes", "TJrsus": "Ursus", "Tnstrum": "Tustrum",
           "Wadtjs": "Wadus", "Zabtjlon": "Zabulon", "Pactaltjs": "Pactalus", "\"Wormacia": "Wormacia", "Ti:aceas": "Traceas",
           "Wltumns": "Vulturnus", "Femus": "Fernus", "Ptbolomaida": "Ptholomaida", "Ptbolomayda": "Ptholomayda", "Sepbar": "Sephar",
           "Sitbe": "Sithe", "Sitbe palme": "Sithe palme", "Sitipbi": "Sitiphi", "Spbinx": "Sphinx", "Socbotb": "Sochoth",
           "Snotingbam": "Snotingham", "Scobesbiri": "Scobesbiri", "Partbia": "Parthia", "Antropopbagi": "Antropophagi",
           "Sarmatbarum Rupes": "Sarmatharum Rupes", "Carpatlias": "Carpathas", "LeodiiUD": "Leodium", "EudemoD": "Eudemon",
           "CincinDus": "Cincinnus", "HUta": "Hilta", "I<5aya": "Icaya", "Riisadden": "Rusadden", "Paretoninm": "Paretonium",
           "Patavinm": "Patavium", "Sirinmn": "Sirinum", "Siracnsa": "Siracusa", "Subsolanns": "Subsolanus", "Piscinns": "Piscinus",
           "Ranandufl": "Ranandus", "Spitacns": "Spitacus", "Salodanim": "Salodanum", "Salinamm": "Salinarum", "Ycnsia": "Ycusia",
           "Yppns Diart": "Yppus Diart", "Minoi^ga": "Minorga", "Eonee": "Eonee", "Laybumia": "Layburnia", "Libumia": "Liburnia",
           "Libomice": "Liburnice", "Britannia^": "Britannia", "Cathinna^": "Cathinna", "Caucasus^": "Caucasus", "Terracona»": "Terracona",
           "DecapoUs": "Decapolis", "DiospoUs": "Diospolis", "ApoUonia": "Apollonia", "AppoUonis": "Appollonis", "AchiUea": "Achillea",
           "Eurus-Nothus": "Eurus-Nothus", "Thiberia": "Thiberia", "Etfraim": "Effraim", "S. Job'": "S. Joh", "S. Andr": "S. Andr",
           "UCARIA": "Ucaria", "OCCIDENS": "Occidens", "Cotomare": "Cottonare", "Pobbrota": "Polibrota", "Ilema": "Ilerda"}
inv, bad = [], []
for k, e in enumerate(ents):
    e = re.sub(r"[\^»]\s+(\d)", r", \1", e).replace(", '61.", ", 61.")
    m = rx.match(e)
    if not m:
        bad.append(e); continue
    name = m.group("name").strip(" ,'\"")
    pg = [int(x) for x in re.findall(r"\d+", m.group("pages")) if 0 < int(x) < 175]
    base = name.split(",")[0]
    if base in PAGEFIX or name in PAGEFIX:
        pg = PAGEFIX.get(base) or PAGEFIX[name]
    tp = TYPES.get(m.group("type"), "")
    clean = NAMEFIX.get(name, name)
    if tp == "island" and m.group("type") == "L" and base in LAKES: tp = "lake"
    if "L." in e and base in LAKES: tp = "lake"
    inv.append({"k": len(inv), "index": e, "name": clean, "type": tp, "qual": (m.group("q") or "").strip(), "pages": pg, "seq": "seq" in e})
assert not bad, bad
assert all(x["pages"] for x in inv), [x for x in inv if not x["pages"]]
print("index entries", len(inv))

# ---------- garbled black-letter runs and their glosses ----------
BIBN = r"Gen|Exod|Ex|Lev|Numb|Num|Deut|Josh|Judg|Ruth|Sam|Kings|Chron|Chr|Ezra|Neh|Esth|Job|Ps|Prov|Eccl|Cant|Is|Isa|Jer|Lam|Ezek|Ezck|Dan|Hos|Joel|Amos|Obad|Jon|Mic|Nah|Hab|Zeph|Hag|Zech|Mal|Matt|Mark|Luke|John|Acts|Rom|Cor|Gal|Eph|Phil|Col|Thess|Tim|Tit|Heb|Rev|Mac|Macc|Tob|Judith|Jud"
CLA = r"\b(?:Plin|PHn|Pliny|Solin|Sol|Solinus|Mela|Ptol|Ptolemy|Strabo|Herod|Oros|Orosius|Isid|Isidore|Itin|Itinerary|Anton|Antonin|Mart\. Cap|Martianus|Priscian|Dionys|Arr|Arrian|Curt|Justin|Virg|Hor|Ovid|Lucan|Caes|Tac|Liv|Steph|Amm|Peut|Peutinger|Aethic|Æthic|iEthic|^thic|Macrob|Procop|Xen|Polyb|Diod|Paus|Hom|Thuc|Joseph|Euseb|Hieron|Jerome|Geog\. Rav|Ravenna|Cassiod|Jornand|Avien|Sall|Cic)\b"
MED = r"\b(?:Higden|Hoveden|Adam of Bremen|Adam\. Brem|Giraldus|Gervase|Gerv|Matthew Paris|Dicuil|Langtoft|Bede|Paulus Diaconus|Paul\. Diac|Mandeville|Marco Polo|Sanuto|Roger Bacon|Bacon|Imago Mundi|Rubruquis|Carpini|Joinville|Vinsauf|Jac\. de Vitr|Jacques de Vitry|Brocardus|Burchard|Fulcher|William of Tyre|Will\. Tyr|Robert of Gloucester|Henry of Huntingdon|Ordericus|Helmold|Saxo)\b"


def garbled(tok):
    w = tok.strip(".,;:()[]\"'*")
    if len(w) < 2: return False
    if re.search(r"[\^%$@#|!&{}<>\\~©®■•«»]", w) and re.search(r"[A-Za-z]", w): return True
    if re.search(r"[a-z][A-Z]", w) and not re.fullmatch(r"(Mc|Mac|De|St|La|Le|Du|Van|Von|Ii)[A-Z][a-z]+", w): return True
    if re.search(r"[A-Za-z]\d|\d[A-Za-z]", w) and not re.fullmatch(r"\d+(st|nd|rd|th|s|d)", w): return True
    if re.fullmatch(r"[A-Z]{2,}[a-z]+", w): return True
    return False


def runs(text):
    toks = list(re.finditer(r"\S+", text)); out = []; i = 0
    while i < len(toks):
        if garbled(toks[i].group()):
            j = i
            while j + 1 < len(toks) and (garbled(toks[j + 1].group()) or (re.fullmatch(r"[a-z]{1,12}[,.;:]?", toks[j + 1].group())
                                                                        and j + 2 < len(toks) and garbled(toks[j + 2].group()))):
                j += 1
            out.append({"s": toks[i].start(), "e": toks[j].end(), "g": text[toks[i].start():toks[j].end()]}); i = j + 1
        else:
            i += 1
    for a, b in zip(out, out[1:] + [None]):
        a["next"] = b["s"] if b else len(text)
    return out


SUB = [("tt", "n"), ("j5", "s"), ("jS", "s"), ("0", "o"), ("5", "s"), ("6", "b"), ("&", "v"), ("@", "g"), ("1", "l"), ("lr", "d"), ("Ir", "d"), ("3", "i"), ("©", "o")]


def gnorm(g):
    for a, b in SUB:
        g = g.replace(a, b)
    return re.sub(r"[^a-z]", "", g.lower())


def nnorm(n):
    return re.sub(r"[^a-z]", "", n.lower())


def sim(a, b):
    if not a or not b: return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


RUNS = {p: runs(t) for p, t in PG.items()}
by_page = {}
for x in inv:
    by_page.setdefault(x["pages"][0], []).append(x)
for p, xs in by_page.items():
    cand = []
    for q in (p, p - 1, p + 1):
        for r in RUNS.get(q, []):
            cand.append((q, r))
    if not cand:
        continue
    M = np.zeros((len(xs), len(cand)))
    for i, x in enumerate(xs):
        nn = nnorm(x["name"])
        for j, (q, r) in enumerate(cand):
            t = PG[q]; gl = t[r["e"]:r["e"] + 60]
            s1 = sim(nn, gnorm(r["g"])[-max(len(nn) + 4, 6):])           # the run ends with the name, often after 'mons', 'fluvius'
            s2 = max([sim(nn, nnorm(w)) for w in re.findall(r"[A-Za-z]+", gl)[:4]] + [0])
            s3 = 1.0 if re.search(r"\b" + re.escape(x["name"].split()[0]) + r"\b", t[r["s"]:r["e"] + 40]) else 0
            M[i, j] = max(s1, .9 * s2, s3) - (.08 if q != p else 0)
    ri, ci = linear_sum_assignment(-M)
    for i, j in zip(ri, ci):
        q, r = cand[j]; t = PG[q]
        xs[i]["run"] = {"page": q, "g": r["g"], "score": round(float(M[i, j]), 2), "gloss": t[r["e"]:r["e"] + 160].strip(),
                        "ctx": t[r["s"]:min(r["next"], r["e"] + 500)]}

# plain-text occurrence (for names the book prints in roman type, e.g. in lists)
for x in inv:
    p = x["pages"][0]
    t = PG.get(p, "")
    m = re.search(r"\b" + re.escape(x["name"]) + r"\b", t)
    x["plain"] = t[max(0, m.start() - 60):m.end() + 160] if m else ""


def citations(ctx):
    return {"bible": sorted(set(re.findall(r"\b(" + BIBN + r")\.?,?\s+[ivxlc\d]", ctx))),
            "classical": len(re.findall(CLA, ctx)) > 0, "medieval": len(re.findall(MED, ctx)) > 0}


ID_PAT = [r"intended for ([A-Z][\w'\- ]+)", r"\bnow ([A-Z][\w'\- ]+)", r"the modern ([A-Z][\w'\- ]+)", r"answer(?:s|ing) to ([A-Z][\w'\- ]+)",
          r"(?:original|earlier|older) form of ([A-Z][\w'\- ]+)", r"\bi\.\s?e\.\s?([A-Z][\w'\- ]+)", r"represents? ([A-Z][\w'\- ]+)"]
for x in inv:
    r = x.get("run")
    cid = ""
    if r:
        gl = r["gloss"]
        m = re.match(r"\(?(?:=\s*)?((?:(?:the|The|Mount|mount|Mt\.|St\.|S\.|river|River|Lake|lake|Cape|cape|Isle of|isle of|brook|Gulf of|city of|town|the town|the river|the city of)\s+)*[A-Z][A-Za-z'\-]+(?:[ \-](?:on|upon|de|of|the|[A-Z][A-Za-z'\-]+))*)", gl)
        if m and len(m.group(1)) > 2:
            cid = m.group(1)
        else:
            for pt in ID_PAT:
                mm = re.search(pt, gl[:120])
                if mm:
                    cid = mm.group(1).strip(); break
        x["cit"] = citations(r["ctx"])
    else:
        x["cit"] = citations(x["plain"])
    x["auto_id"] = re.sub(r"\s+(and|or|which|who|is|was|in|on|at|a|an|the)$", "", cid.strip(" ,;.:"))
    x["part"] = part_of(x["pages"][0]); x["chapter"] = chapter_of(x["pages"][0])

jsave(inv, f"{WORK}/entries.json", indent=1)
with open(f"{WORK}/review.tsv", "w", encoding="utf-8") as f:
    for x in inv:
        r = x.get("run") or {}
        f.write("\t".join([str(x["k"]), x["name"], x["type"], x["qual"], ",".join(map(str, x["pages"])), x["auto_id"],
                           str(r.get("score", "")), (r.get("g", "") + " || " + r.get("gloss", "")[:110]).replace("\t", " ")]) + "\n")
sc = np.array([x["run"]["score"] for x in inv if x.get("run")])
print("matched to a run", len(sc), "score>=.6", int((sc >= .6).sum()), "auto ids", sum(1 for x in inv if x["auto_id"]))
print("parts", {p: sum(1 for x in inv if x["part"] == p) for p in PARTS})
