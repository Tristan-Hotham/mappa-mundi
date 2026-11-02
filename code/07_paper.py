"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them). The DOI stays as the 10.5281/zenodo.23878612 placeholder."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Mappa_Mundi"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# statements made in words in the paper only
assert R["bearing"]["within90_pct"] == 100                                  # "all are within 90"
assert R["places"]["SriLanka"]["map_frac"] > .97                            # "sits on the rim"
assert R["regions"]["Iceland and Norway"]["median_map_frac"] > .95 and R["regions"]["Iceland and Norway"]["stretch"] is None
assert R["regions"]["North Africa"]["median_abs_brg_err"] > 45 and R["regions"]["Egypt and Sinai"]["median_abs_brg_err"] > 45


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "pc1": return f"{float(v):.1f}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


KL = ["Biblical", "Classical", "Medieval", "Legendary"]
rows = "".join(f"{p} & {R['part_class'][p]['n']} & " + " & ".join(str(R['part_class'][p][k]) for k in KL) + "\\\\\n" for p in R["part_class"])
tot = " & ".join(str(R["classes"][k]["n"]) for k in KL)
TP = ("\\begin{table}[tbp]\\centering\\small\\caption{Names in Bevan and Phillott's index by part of the map and class (frame and natural history left out).}\\label{tab:parts}"
      "\\begin{tabular}{lrrrrr}\\toprule Part of the map & Names & Biblical & Classical & Medieval & Legendary\\\\\\midrule\n" + rows +
      f"\\midrule All & {R['source']['n_named']} & {tot}\\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
G = pd.read_csv(f"{DATA}/regions.csv")
rows = "".join(f"{tex(r.region)} & {r.n} & {r.median_true_km:,} & {round(100 * r.median_map_frac)}\\% & {r.median_abs_brg_err} & {('%.2f' % r.stretch) if pd.notna(r.stretch) else 'too few'} & {r.median_disp_km:,}\\\\\n" for r in G.itertuples())
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Located real places by region: number, median true distance from Jerusalem, median distance on the map as a share of the radius, median absolute bearing error (degrees), relative scale, and median displacement from the best-fitting position (km).}\\label{tab:regions}"
      "\\begin{tabular}{lrrrrrr}\\toprule Region & Places & km & Map & Error & Scale & Shift\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
L = pd.read_csv(f"{DATA}/located.csv")
L = L.sort_values(["part", "name"])
rows = "".join(f"{tex(r['name'])} & {tex(str(r.pages).split(';')[0])} & {tex(r['class'])} & {tex(r.identification) if isinstance(r.identification, str) else '(no real place)'} & {r.pos_conf}\\\\\n" for _, r in L.iterrows())
TL = ("{\\footnotesize\\setlength{\\tabcolsep}{4pt}\\begin{longtable}{p{3.2cm}rlp{6.6cm}l}\\caption{The " + str(len(L)) + " inscriptions located on Miller's facsimile, with the 1873 book's page, the class, the identification and my confidence in the position.}\\label{tab:located}\\\\"
      "\\toprule Name (index) & Page & Class & Identification (Bevan and Phillott) & Position\\\\\\midrule\\endfirsthead\\toprule Name (index) & Page & Class & Identification & Position\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|meta\.doi)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("PARTS", TP), ("REGIONS", TR), ("LOCATED", TL)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = t.replace("\\href{https://doi.org/{{meta.doi}}}{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
assert "{{" not in t and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
